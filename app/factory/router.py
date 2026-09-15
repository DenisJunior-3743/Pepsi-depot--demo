from datetime import date, datetime

from fastapi import APIRouter, Body, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.auth.dependencies import require_permission
from app.auth.models import PermissionAction
from app.db.session import get_db
from app.factory.models import FactoryCurrentStock, SupplyStatus
from app.factory.schemas import FactoryStockResponse, ProductionCreate, ProductionResponse, SupplyCreate, SupplyResponse
from app.factory.schemas import SupplyUpdate
from app.factory.services import create_supplies_batch, delete_production, delete_supply, get_production, get_stock, get_supply, list_production, list_supplies, record_production_batch, update_production, update_supply

router = APIRouter(prefix="/factory", tags=["Factory"])


@router.post(
    "/production",
    response_model=list[ProductionResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("factory.production", PermissionAction.create))],
)
def create_production(data: list[ProductionCreate] = Body(..., min_length=1), db: Session = Depends(get_db)):
    return record_production_batch(db, data)


@router.get(
    "/production",
    response_model=list[ProductionResponse],
    dependencies=[Depends(require_permission("factory.production", PermissionAction.read))],
)
def read_production_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=10),
    history_date: date | None = Query(None, alias="date"),
    product_id: int | None = Query(None, gt=0),
    product_name: str | None = None,
    quantity: int | None = Query(None, gt=0),
    db: Session = Depends(get_db),
):
    history_datetime = datetime.combine(history_date, datetime.min.time()) if history_date else None
    return list_production(db, skip, limit, history_datetime, product_id, product_name, quantity)


@router.get(
    "/production/{production_id}",
    response_model=ProductionResponse,
    dependencies=[Depends(require_permission("factory.production", PermissionAction.read))],
)
def read_production(production_id: int, db: Session = Depends(get_db)):
    return get_production(db, production_id)


@router.put(
    "/production/{production_id}",
    response_model=ProductionResponse,
    dependencies=[Depends(require_permission("factory.production", PermissionAction.update))],
)
def update_factory_production(production_id: int, data: ProductionCreate, db: Session = Depends(get_db)):
    return update_production(db, get_production(db, production_id), data)


@router.delete(
    "/production/{production_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("factory.production", PermissionAction.delete))],
)
def delete_factory_production(production_id: int, db: Session = Depends(get_db)):
    delete_production(db, get_production(db, production_id))


@router.post(
    "/supplies",
    response_model=list[SupplyResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("factory.supplies", PermissionAction.create))],
)
def create_factory_supply(data: list[SupplyCreate] = Body(..., min_length=1), db: Session = Depends(get_db)):
    return create_supplies_batch(db, data)


@router.get(
    "/supplies",
    response_model=list[SupplyResponse],
    dependencies=[Depends(require_permission("factory.supplies", PermissionAction.read))],
)
def read_supply_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=10),
    history_date: date | None = Query(None, alias="date"),
    product_id: int | None = Query(None, gt=0),
    product_name: str | None = None,
    quantity: int | None = Query(None, gt=0),
    status_filter: SupplyStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
):
    history_datetime = datetime.combine(history_date, datetime.min.time()) if history_date else None
    return list_supplies(db, skip, limit, history_datetime, product_id, product_name, quantity, status_filter)


@router.get(
    "/supplies/{supply_id}",
    response_model=SupplyResponse,
    dependencies=[Depends(require_permission("factory.supplies", PermissionAction.read))],
)
def read_factory_supply(supply_id: int, db: Session = Depends(get_db)):
    return get_supply(db, supply_id)


@router.put(
    "/supplies/{supply_id}",
    response_model=SupplyResponse,
    dependencies=[Depends(require_permission("factory.supplies", PermissionAction.update))],
)
def update_factory_supply(supply_id: int, data: SupplyUpdate, db: Session = Depends(get_db)):
    return update_supply(db, get_supply(db, supply_id), data)


@router.delete(
    "/supplies/{supply_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("factory.supplies", PermissionAction.delete))],
)
def delete_factory_supply(supply_id: int, db: Session = Depends(get_db)):
    delete_supply(db, get_supply(db, supply_id))


@router.get(
    "/stock",
    response_model=list[FactoryStockResponse],
    dependencies=[Depends(require_permission("factory.production", PermissionAction.read))],
)
def list_factory_stock(product_id: int | None = Query(None, gt=0), db: Session = Depends(get_db)):
    query = select(FactoryCurrentStock).options(selectinload(FactoryCurrentStock.product), selectinload(FactoryCurrentStock.quantity_record))
    if product_id is not None:
        query = query.where(FactoryCurrentStock.product_id == product_id)
    return list(db.scalars(query.order_by(FactoryCurrentStock.product_id, FactoryCurrentStock.quantity_id)))


@router.get(
    "/stock/{product_id}/{quantity_id}",
    response_model=FactoryStockResponse,
    dependencies=[Depends(require_permission("factory.production", PermissionAction.read))],
)
def read_factory_stock(product_id: int, quantity_id: int, db: Session = Depends(get_db)):
    return get_stock(db, product_id, quantity_id)
