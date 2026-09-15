from datetime import date, timedelta

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.depot.models import CurrentSales, CurrentStock, RestockHistory, RestockStatus, SalesHistory
from app.depot.schemas import PagedResponse, RestockConfirm, RestockReject, RestockUpdate, SaleCreate, SaleUpdate
from app.factory.models import FactoryCurrentStock, SupplyHistory, SupplyStatus
from app.modules.admin.models import Price, Product, Quantity

_RESTOCK_OPTIONS = (
    selectinload(RestockHistory.depot),
    selectinload(RestockHistory.product),
    selectinload(RestockHistory.quantity_record),
)
_SALE_OPTIONS = (
    selectinload(SalesHistory.depot),
    selectinload(SalesHistory.product),
    selectinload(SalesHistory.quantity_record),
)
_STOCK_OPTIONS = (
    selectinload(CurrentStock.depot),
    selectinload(CurrentStock.product),
    selectinload(CurrentStock.quantity_record),
)
_CURRENT_SALES_OPTIONS = (
    selectinload(CurrentSales.depot),
    selectinload(CurrentSales.product),
    selectinload(CurrentSales.quantity_record),
)


def _is_insufficient_stock(exc: DBAPIError) -> bool:
    return "insufficient_stock" in str(exc.orig).lower()


def _paginate(db: Session, stmt, page: int, page_size: int) -> PagedResponse:
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = list(db.scalars(stmt.offset((page - 1) * page_size).limit(page_size)))
    total_pages = (total + page_size - 1) // page_size if total else 0
    return PagedResponse(items=items, total=total, page=page, page_size=page_size, total_pages=total_pages)


def _get_supply(db: Session, supply_history_id: int) -> SupplyHistory:
    supply = db.get(SupplyHistory, supply_history_id)
    if supply is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supply record not found")
    return supply


def _require_pending(supply: SupplyHistory) -> None:
    if supply.status != SupplyStatus.pending:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Supply {supply.id} is already {supply.status.value}, cannot decide it again",
        )


def _restore_factory_stock(db: Session, supply: SupplyHistory) -> None:
    stock = db.scalar(
        select(FactoryCurrentStock)
        .where(FactoryCurrentStock.product_id == supply.product_id, FactoryCurrentStock.quantity_id == supply.quantity_id)
        .with_for_update()
    )
    if stock is not None:
        stock.available_quantity += supply.amount


def _deduct_factory_stock(db: Session, supply: SupplyHistory) -> None:
    stock = db.scalar(
        select(FactoryCurrentStock)
        .where(FactoryCurrentStock.product_id == supply.product_id, FactoryCurrentStock.quantity_id == supply.quantity_id)
        .with_for_update()
    )
    if stock is not None:
        stock.available_quantity -= supply.amount


def confirm_restock(db: Session, supply_history_id: int, data: RestockConfirm) -> RestockHistory:
    supply = _get_supply(db, supply_history_id)
    _require_pending(supply)
    matched = data.quantity_received == supply.amount
    entry = RestockHistory(
        supply_history_id=supply.id,
        depot_id=data.depot_id,
        product_id=supply.product_id,
        quantity_id=supply.quantity_id,
        quantity_delivered=data.quantity_received,
        supplier_id=data.supplier_id,
        confirmed_by_id=data.confirmed_by_id,
        status=RestockStatus.confirmed if matched else RestockStatus.rejected,
        rejection_reason=None if matched else f"Quantity mismatch: expected {supply.amount}, received {data.quantity_received}",
    )
    if matched:
        supply.status = SupplyStatus.received
        supply.rejection_reason = None
    else:
        supply.status = SupplyStatus.rejected
        supply.rejection_reason = entry.rejection_reason
        _restore_factory_stock(db, supply)
    try:
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid depot, supplier, or confirming personnel reference")


def reject_restock(db: Session, supply_history_id: int, data: RestockReject) -> RestockHistory:
    supply = _get_supply(db, supply_history_id)
    _require_pending(supply)
    entry = RestockHistory(
        supply_history_id=supply.id,
        depot_id=data.depot_id,
        product_id=supply.product_id,
        quantity_id=supply.quantity_id,
        quantity_delivered=data.quantity_received or 0,
        supplier_id=data.supplier_id,
        confirmed_by_id=data.confirmed_by_id,
        status=RestockStatus.rejected,
        rejection_reason=data.reason,
    )
    supply.status = SupplyStatus.rejected
    supply.rejection_reason = data.reason
    _restore_factory_stock(db, supply)
    try:
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid depot, supplier, or confirming personnel reference")


def list_restock_history(
    db: Session,
    depot_id: int | None = None,
    status_filter: RestockStatus | None = None,
    product_name: str | None = None,
    quantity: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    page: int = 1,
    page_size: int = 10,
) -> PagedResponse:
    stmt = select(RestockHistory).options(*_RESTOCK_OPTIONS)
    if depot_id is not None:
        stmt = stmt.where(RestockHistory.depot_id == depot_id)
    if status_filter is not None:
        stmt = stmt.where(RestockHistory.status == status_filter)
    if product_name is not None:
        stmt = stmt.join(Product, RestockHistory.product_id == Product.id).where(Product.name.ilike(f"%{product_name}%"))
    if quantity is not None:
        stmt = stmt.join(Quantity, RestockHistory.quantity_id == Quantity.id).where(Quantity.quantity.ilike(f"%{quantity}%"))
    if date_from is not None:
        stmt = stmt.where(RestockHistory.restock_date >= date_from)
    if date_to is not None:
        stmt = stmt.where(RestockHistory.restock_date < date_to + timedelta(days=1))
    stmt = stmt.order_by(RestockHistory.id.desc())
    return _paginate(db, stmt, page, page_size)


def get_restock_entry(db: Session, entry_id: int) -> RestockHistory:
    entry = db.scalar(select(RestockHistory).options(*_RESTOCK_OPTIONS).where(RestockHistory.id == entry_id))
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restock entry not found")
    return entry


def update_restock_entry(db: Session, entry_id: int, data: RestockUpdate) -> RestockHistory:
    entry = db.get(RestockHistory, entry_id)
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restock entry not found")
    entry.quantity_delivered = data.quantity_delivered
    db.commit()
    db.refresh(entry)
    return get_restock_entry(db, entry_id)


def delete_restock_entry(db: Session, entry_id: int) -> None:
    entry = db.get(RestockHistory, entry_id)
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restock entry not found")
    supply = db.get(SupplyHistory, entry.supply_history_id)
    if supply is not None and supply.status != SupplyStatus.pending:
        if supply.status == SupplyStatus.rejected:
            _deduct_factory_stock(db, supply)
        supply.status = SupplyStatus.pending
        supply.rejection_reason = None
    db.delete(entry)
    db.commit()


def record_sale(db: Session, data: SaleCreate) -> SalesHistory:
    amount_sold = data.amount_sold
    if amount_sold is None:
        price = db.scalar(select(Price).where(Price.quantity_id == data.quantity_id))
        if price is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No price set for this quantity; provide amount_sold explicitly")
        amount_sold = float(price.amount) * data.quantity_sold

    entry = SalesHistory(
        depot_id=data.depot_id,
        product_id=data.product_id,
        quantity_id=data.quantity_id,
        quantity_sold=data.quantity_sold,
        amount_sold=amount_sold,
        sold_by_id=data.sold_by_id,
    )
    try:
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry
    except DBAPIError as exc:
        db.rollback()
        if _is_insufficient_stock(exc):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Insufficient stock at this depot for the requested sale")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid depot, product, or quantity reference")


def list_sales_history(
    db: Session,
    depot_id: int | None = None,
    product_name: str | None = None,
    quantity: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    page: int = 1,
    page_size: int = 10,
) -> PagedResponse:
    stmt = select(SalesHistory).options(*_SALE_OPTIONS)
    if depot_id is not None:
        stmt = stmt.where(SalesHistory.depot_id == depot_id)
    if product_name is not None:
        stmt = stmt.join(Product, SalesHistory.product_id == Product.id).where(Product.name.ilike(f"%{product_name}%"))
    if quantity is not None:
        stmt = stmt.join(Quantity, SalesHistory.quantity_id == Quantity.id).where(Quantity.quantity.ilike(f"%{quantity}%"))
    if date_from is not None:
        stmt = stmt.where(SalesHistory.sale_date >= date_from)
    if date_to is not None:
        stmt = stmt.where(SalesHistory.sale_date <= date_to)
    stmt = stmt.order_by(SalesHistory.id.desc())
    return _paginate(db, stmt, page, page_size)


def get_sale(db: Session, sale_id: int) -> SalesHistory:
    sale = db.scalar(select(SalesHistory).options(*_SALE_OPTIONS).where(SalesHistory.id == sale_id))
    if sale is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")
    return sale


def update_sale(db: Session, sale_id: int, data: SaleUpdate) -> SalesHistory:
    sale = db.get(SalesHistory, sale_id)
    if sale is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")
    sale.quantity_sold = data.quantity_sold
    sale.amount_sold = data.amount_sold
    try:
        db.commit()
    except DBAPIError as exc:
        db.rollback()
        if _is_insufficient_stock(exc):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Insufficient stock at this depot for the requested update")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid update")
    return get_sale(db, sale_id)


def delete_sale(db: Session, sale_id: int) -> None:
    sale = db.get(SalesHistory, sale_id)
    if sale is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")
    db.delete(sale)
    db.commit()


def list_current_stock(db: Session, depot_id: int | None = None) -> list[CurrentStock]:
    stmt = select(CurrentStock).options(*_STOCK_OPTIONS)
    if depot_id is not None:
        stmt = stmt.where(CurrentStock.depot_id == depot_id)
    return list(db.scalars(stmt.order_by(CurrentStock.depot_id, CurrentStock.product_id)))


def list_current_sales(db: Session, depot_id: int | None = None) -> list[CurrentSales]:
    stmt = select(CurrentSales).options(*_CURRENT_SALES_OPTIONS).where(CurrentSales.sale_date == date.today())
    if depot_id is not None:
        stmt = stmt.where(CurrentSales.depot_id == depot_id)
    return list(db.scalars(stmt.order_by(CurrentSales.depot_id, CurrentSales.product_id)))
