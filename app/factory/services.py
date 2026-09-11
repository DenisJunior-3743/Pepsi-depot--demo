from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.admin.models import Depot, Personnel, Product
from app.factory.models import FactoryStock, ProductionRecord, Supply, SupplyItem
from app.factory.schemas import ProductionCreate, SupplyCreate


def record_production(db: Session, data: ProductionCreate) -> ProductionRecord:
    if db.get(Product, data.product_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    if data.recorded_by_user_id is not None and db.get(Personnel, data.recorded_by_user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Personnel record not found")
    stock = db.scalar(select(FactoryStock).where(FactoryStock.product_id == data.product_id).with_for_update())
    if stock is None:
        stock = FactoryStock(product_id=data.product_id, available_quantity=0)
        db.add(stock)
        db.flush()
    stock.available_quantity += data.quantity_produced
    record = ProductionRecord(**data.model_dump(exclude_none=True))
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def create_supply(db: Session, data: SupplyCreate) -> Supply:
    if db.get(Depot, data.destination_depot_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Depot not found")
    if data.dispatched_by_user_id is not None and db.get(Personnel, data.dispatched_by_user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Personnel record not found")
    product_ids = [item.product_id for item in data.items]
    if len(product_ids) != len(set(product_ids)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A product may appear only once per supply")

    stocks = {}
    for item in data.items:
        if db.get(Product, item.product_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product {item.product_id} not found")
        stock = db.scalar(select(FactoryStock).where(FactoryStock.product_id == item.product_id).with_for_update())
        if stock is None or stock.available_quantity < item.quantity_supplied:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Insufficient stock for product {item.product_id}")
        stocks[item.product_id] = stock

    supply = Supply(**data.model_dump(exclude={"items"}, exclude_none=True))
    db.add(supply)
    db.flush()
    for item in data.items:
        stocks[item.product_id].available_quantity -= item.quantity_supplied
        supply.items.append(SupplyItem(**item.model_dump()))
    db.commit()
    db.refresh(supply)
    return supply


def get_supply(db: Session, supply_id: int) -> Supply:
    supply = db.scalar(select(Supply).options(selectinload(Supply.items).selectinload(SupplyItem.product), selectinload(Supply.depot)).where(Supply.id == supply_id))
    if supply is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supply not found")
    return supply


def get_production(db: Session, production_id: int) -> ProductionRecord:
    record = db.scalar(select(ProductionRecord).options(selectinload(ProductionRecord.product)).where(ProductionRecord.id == production_id))
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Production record not found")
    return record


def get_stock(db: Session, product_id: int) -> FactoryStock:
    stock = db.scalar(select(FactoryStock).options(selectinload(FactoryStock.product)).where(FactoryStock.product_id == product_id))
    if stock is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Factory stock not found")
    return stock


def list_production(db: Session) -> list[ProductionRecord]:
    return list(db.scalars(select(ProductionRecord).options(selectinload(ProductionRecord.product)).order_by(ProductionRecord.production_date.desc())))


def list_supplies(db: Session) -> list[Supply]:
    return list(db.scalars(select(Supply).options(selectinload(Supply.items).selectinload(SupplyItem.product), selectinload(Supply.depot)).order_by(Supply.supply_date.desc())))