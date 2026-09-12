from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.admin.models import Product, Quantity
from app.factory.models import FactoryCurrentStock, ProductionRecord, SupplyHistory, SupplyStatus
from app.factory.schemas import ProductionCreate, SupplyCreate, SupplyUpdate


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


def update_production(db: Session, record: ProductionRecord, data: ProductionCreate) -> ProductionRecord:
    if db.get(Product, data.product_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    stock = db.scalar(select(FactoryCurrentStock).where(FactoryCurrentStock.product_id == record.product_id).with_for_update())
    if record.product_id != data.product_id:
        if stock is None or stock.available_quantity < record.quantity_produced:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Insufficient stock for production update")
        target_stock = db.scalar(select(FactoryCurrentStock).where(FactoryCurrentStock.product_id == data.product_id).with_for_update())
        if target_stock is None:
            target_stock = FactoryCurrentStock(product_id=data.product_id, available_quantity=0)
            db.add(target_stock)
            db.flush()
        stock.available_quantity -= record.quantity_produced
        target_stock.available_quantity += data.quantity_produced
    else:
        if stock is None or stock.available_quantity - record.quantity_produced + data.quantity_produced < 0:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Insufficient stock for production update")
        stock.available_quantity += data.quantity_produced - record.quantity_produced
    record.product_id = data.product_id
    record.quantity_produced = data.quantity_produced
    if data.production_date is not None:
        record.production_date = data.production_date
    try:
        db.commit()
        db.refresh(record)
        return record
    except Exception:
        db.rollback()
        raise


def delete_production(db: Session, record: ProductionRecord) -> None:
    stock = db.scalar(select(FactoryCurrentStock).where(FactoryCurrentStock.product_id == record.product_id).with_for_update())
    if stock is None or stock.available_quantity < record.quantity_produced:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Insufficient stock to delete production record")
    stock.available_quantity -= record.quantity_produced
    db.delete(record)
    db.commit()


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


def update_supply(db: Session, supply: SupplyHistory, data: SupplyUpdate) -> SupplyHistory:
    if data.status == SupplyStatus.rejected and not data.rejection_reason:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Rejection reason is required")
    if data.status != SupplyStatus.rejected:
        data.rejection_reason = None
    if supply.status == SupplyStatus.pending and data.status == SupplyStatus.rejected:
        stock = db.scalar(select(FactoryCurrentStock).where(FactoryCurrentStock.product_id == supply.product_id).with_for_update())
        if stock is not None:
            stock.available_quantity += supply.amount
    supply.status = data.status
    supply.rejection_reason = data.rejection_reason
    try:
        db.commit()
        db.refresh(supply)
        return supply
    except Exception:
        db.rollback()
        raise


def delete_supply(db: Session, supply: SupplyHistory) -> None:
    if supply.status == SupplyStatus.pending:
        stock = db.scalar(select(FactoryCurrentStock).where(FactoryCurrentStock.product_id == supply.product_id).with_for_update())
        if stock is not None:
            stock.available_quantity += supply.amount
    db.delete(supply)
    db.commit()


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


def list_production(db: Session, skip: int = 0, limit: int = 10, history_date=None, product_id: int | None = None, product_name: str | None = None, quantity: int | None = None) -> list[ProductionRecord]:
    query = select(ProductionRecord).join(ProductionRecord.product).options(selectinload(ProductionRecord.product))
    if history_date is not None:
        query = query.where(ProductionRecord.production_date >= history_date, ProductionRecord.production_date < history_date.replace(hour=23, minute=59, second=59, microsecond=999999))
    if product_id is not None:
        query = query.where(ProductionRecord.product_id == product_id)
    if product_name is not None:
        query = query.where(Product.name.ilike(f"%{product_name}%"))
    if quantity is not None:
        query = query.where(ProductionRecord.quantity_produced == quantity)
    return list(db.scalars(query.order_by(ProductionRecord.production_date.desc()).offset(skip).limit(limit)))


def list_supplies(db: Session, skip: int = 0, limit: int = 10, history_date=None, product_id: int | None = None, product_name: str | None = None, quantity: int | None = None) -> list[SupplyHistory]:
    query = select(SupplyHistory).join(SupplyHistory.product).options(selectinload(SupplyHistory.product), selectinload(SupplyHistory.quantity_record))
    if history_date is not None:
        query = query.where(SupplyHistory.created_date >= history_date, SupplyHistory.created_date < history_date.replace(hour=23, minute=59, second=59, microsecond=999999))
    if product_id is not None:
        query = query.where(SupplyHistory.product_id == product_id)
    if product_name is not None:
        query = query.where(Product.name.ilike(f"%{product_name}%"))
    if quantity is not None:
        query = query.where(SupplyHistory.amount == quantity)
    return list(db.scalars(query.order_by(SupplyHistory.created_date.desc()).offset(skip).limit(limit)))