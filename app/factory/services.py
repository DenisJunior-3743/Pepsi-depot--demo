from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.admin.models import Product, Quantity
from app.factory.models import FactoryCurrentStock, ProductionRecord, SupplyHistory
from app.factory.schemas import ProductionCreate, SupplyCreate


def record_production(db: Session, data: ProductionCreate) -> ProductionRecord:
    if db.get(Product, data.product_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    stock = db.scalar(select(FactoryCurrentStock).where(FactoryCurrentStock.product_id == data.product_id).with_for_update())
    if stock is None:
        stock = FactoryCurrentStock(product_id=data.product_id, available_quantity=0)
        db.add(stock)
        db.flush()
    stock.available_quantity += data.quantity_produced
    record = ProductionRecord(**data.model_dump(exclude_none=True))
    try:
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    except Exception:
        db.rollback()
        raise


def create_supply(db: Session, data: SupplyCreate) -> SupplyHistory:
    if db.get(Product, data.product_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    if db.get(Quantity, data.quantity_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quantity not found")
    stock = db.scalar(select(FactoryCurrentStock).where(FactoryCurrentStock.product_id == data.product_id).with_for_update())
    if stock is None or stock.available_quantity < data.amount:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Insufficient factory stock")
    history = SupplyHistory(**data.model_dump())
    try:
        stock.available_quantity -= data.amount
        db.add(history)
        db.commit()
        db.refresh(history)
        return history
    except Exception:
        db.rollback()
        raise


def get_supply(db: Session, supply_id: int) -> SupplyHistory:
    supply = db.scalar(select(SupplyHistory).options(selectinload(SupplyHistory.product), selectinload(SupplyHistory.quantity_record)).where(SupplyHistory.id == supply_id))
    if supply is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supply not found")
    return supply


def get_production(db: Session, production_id: int) -> ProductionRecord:
    record = db.scalar(select(ProductionRecord).options(selectinload(ProductionRecord.product)).where(ProductionRecord.id == production_id))
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Production record not found")
    return record


def get_stock(db: Session, product_id: int) -> FactoryCurrentStock:
    stock = db.scalar(select(FactoryCurrentStock).options(selectinload(FactoryCurrentStock.product)).where(FactoryCurrentStock.product_id == product_id))
    if stock is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Factory stock not found")
    return stock


def list_production(db: Session) -> list[ProductionRecord]:
    return list(db.scalars(select(ProductionRecord).options(selectinload(ProductionRecord.product)).order_by(ProductionRecord.production_date.desc())))


def list_supplies(db: Session) -> list[SupplyHistory]:
    return list(db.scalars(select(SupplyHistory).options(selectinload(SupplyHistory.product), selectinload(SupplyHistory.quantity_record)).order_by(SupplyHistory.id.desc())))