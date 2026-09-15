from datetime import date, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.dashboard.schemas import SummaryCard, SummaryResponse
from app.depot.models import CurrentSales, CurrentStock, RestockHistory, RestockStatus
from app.factory.models import FactoryCurrentStock, ProductionRecord, SupplyHistory, SupplyStatus
from app.modules.admin import crud as admin_crud


def _today_range() -> tuple[datetime, datetime]:
    today = date.today()
    return datetime.combine(today, datetime.min.time()), datetime.combine(today, datetime.max.time())


def build_summary(db: Session) -> SummaryResponse:
    start, end = _today_range()
    today_iso = date.today().isoformat()
    cards: list[SummaryCard] = []

    cards.append(SummaryCard(key="products", title="Products", value=admin_crud.count_products(db), link="/admin/products"))
    cards.append(SummaryCard(key="depots", title="Depots", value=admin_crud.count_depots(db), link="/admin/depots"))
    cards.append(SummaryCard(key="personnel", title="Personnel", value=admin_crud.count_personnel(db), link="/admin/personnel"))

    produced_today = db.scalar(
        select(func.coalesce(func.sum(ProductionRecord.quantity_produced), 0))
        .where(ProductionRecord.production_date >= start, ProductionRecord.production_date <= end)
    )
    batches_today = db.scalar(
        select(func.count()).select_from(ProductionRecord)
        .where(ProductionRecord.production_date >= start, ProductionRecord.production_date <= end)
    )
    cards.append(SummaryCard(
        key="production_today",
        title="Produced Today",
        value=produced_today or 0,
        subtitle=f"{batches_today or 0} batch(es)",
        link=f"/factory/production?date={today_iso}",
    ))

    factory_stock_total = db.scalar(select(func.coalesce(func.sum(FactoryCurrentStock.available_quantity), 0)))
    factory_lines = db.scalar(select(func.count()).select_from(FactoryCurrentStock))
    cards.append(SummaryCard(
        key="factory_stock",
        title="Factory Stock",
        value=factory_stock_total or 0,
        subtitle=f"across {factory_lines or 0} product/pack line(s)",
        link="/factory/stock",
    ))

    pending_supplies = db.scalar(
        select(func.count()).select_from(SupplyHistory).where(SupplyHistory.status == SupplyStatus.pending)
    )
    cards.append(SummaryCard(
        key="pending_supplies",
        title="Pending Supplies",
        value=pending_supplies or 0,
        subtitle="awaiting depot confirmation",
        link="/factory/supplies?status=pending",
    ))

    confirmed_today = db.scalar(
        select(func.count()).select_from(RestockHistory)
        .where(RestockHistory.restock_date >= start, RestockHistory.restock_date <= end, RestockHistory.status == RestockStatus.confirmed)
    )
    rejected_today = db.scalar(
        select(func.count()).select_from(RestockHistory)
        .where(RestockHistory.restock_date >= start, RestockHistory.restock_date <= end, RestockHistory.status == RestockStatus.rejected)
    )
    cards.append(SummaryCard(
        key="restocks_today",
        title="Restocks Today",
        value=(confirmed_today or 0) + (rejected_today or 0),
        subtitle=f"{confirmed_today or 0} confirmed, {rejected_today or 0} rejected",
        link="/depot/restock",
    ))

    depot_stock_total = db.scalar(select(func.coalesce(func.sum(CurrentStock.current_amount), 0)))
    depot_lines = db.scalar(select(func.count()).select_from(CurrentStock))
    cards.append(SummaryCard(
        key="depot_stock",
        title="Depot Stock",
        value=depot_stock_total or 0,
        subtitle=f"across {depot_lines or 0} depot/product line(s)",
        link="/depot/stock",
    ))

    sales_qty_today = db.scalar(
        select(func.coalesce(func.sum(CurrentSales.quantity_sold), 0)).where(CurrentSales.sale_date == date.today())
    )
    sales_amount_today = db.scalar(
        select(func.coalesce(func.sum(CurrentSales.sold_amount), 0)).where(CurrentSales.sale_date == date.today())
    )
    cards.append(SummaryCard(
        key="sales_today",
        title="Sales Today",
        value=float(sales_amount_today or 0),
        subtitle=f"{sales_qty_today or 0} unit(s) sold",
        link="/depot/sales",
    ))

    return SummaryResponse(generated_at=datetime.utcnow(), cards=cards)
