from datetime import date

from fastapi import APIRouter, Body, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_permission
from app.auth.models import PermissionAction
from app.db.session import get_db
from app.depot import schemas, services
from app.depot.models import RestockStatus

router = APIRouter(prefix="/depot", tags=["depot"])


@router.post(
    "/restock/{supply_history_id}/confirm",
    response_model=schemas.RestockResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("depot.restock", PermissionAction.create))],
)
def confirm_restock(supply_history_id: int, data: schemas.RestockConfirm, db: Session = Depends(get_db)):
    return services.confirm_restock(db, supply_history_id, data)


@router.post(
    "/restock/{supply_history_id}/reject",
    response_model=schemas.RestockResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("depot.restock", PermissionAction.create))],
)
def reject_restock(supply_history_id: int, data: schemas.RestockReject, db: Session = Depends(get_db)):
    return services.reject_restock(db, supply_history_id, data)


@router.get(
    "/restock",
    response_model=schemas.PagedResponse[schemas.RestockResponse],
    dependencies=[Depends(require_permission("depot.restock", PermissionAction.read))],
)
def list_restock_history(
    depot_id: int | None = None,
    status_filter: RestockStatus | None = Query(default=None, alias="status"),
    product_name: str | None = None,
    quantity: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return services.list_restock_history(db, depot_id, status_filter, product_name, quantity, date_from, date_to, page, page_size)


@router.get(
    "/restock/{entry_id}",
    response_model=schemas.RestockResponse,
    dependencies=[Depends(require_permission("depot.restock", PermissionAction.read))],
)
def get_restock_entry(entry_id: int, db: Session = Depends(get_db)):
    return services.get_restock_entry(db, entry_id)


@router.put(
    "/restock/{entry_id}",
    response_model=schemas.RestockResponse,
    dependencies=[Depends(require_permission("depot.restock", PermissionAction.update))],
)
def update_restock_entry(entry_id: int, data: schemas.RestockUpdate, db: Session = Depends(get_db)):
    return services.update_restock_entry(db, entry_id, data)


@router.delete(
    "/restock/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("depot.restock", PermissionAction.delete))],
)
def delete_restock_entry(entry_id: int, db: Session = Depends(get_db)):
    services.delete_restock_entry(db, entry_id)


@router.get(
    "/stock",
    response_model=list[schemas.CurrentStockResponse],
    dependencies=[Depends(require_permission("depot.restock", PermissionAction.read))],
)
def list_current_stock(depot_id: int | None = None, db: Session = Depends(get_db)):
    return services.list_current_stock(db, depot_id)


@router.post(
    "/sales",
    response_model=list[schemas.SaleResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("depot.sales", PermissionAction.create))],
)
def record_sale(data: list[schemas.SaleCreate] = Body(..., min_length=1), db: Session = Depends(get_db)):
    return services.record_sales_batch(db, data)


@router.get(
    "/sales",
    response_model=schemas.PagedResponse[schemas.SaleResponse],
    dependencies=[Depends(require_permission("depot.sales", PermissionAction.read))],
)
def list_sales_history(
    depot_id: int | None = None,
    product_name: str | None = None,
    quantity: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return services.list_sales_history(db, depot_id, product_name, quantity, date_from, date_to, page, page_size)


@router.get(
    "/sales/{sale_id}",
    response_model=schemas.SaleResponse,
    dependencies=[Depends(require_permission("depot.sales", PermissionAction.read))],
)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    return services.get_sale(db, sale_id)


@router.put(
    "/sales/{sale_id}",
    response_model=schemas.SaleResponse,
    dependencies=[Depends(require_permission("depot.sales", PermissionAction.update))],
)
def update_sale(sale_id: int, data: schemas.SaleUpdate, db: Session = Depends(get_db)):
    return services.update_sale(db, sale_id, data)


@router.delete(
    "/sales/{sale_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("depot.sales", PermissionAction.delete))],
)
def delete_sale(sale_id: int, db: Session = Depends(get_db)):
    services.delete_sale(db, sale_id)


@router.get(
    "/sales-current",
    response_model=list[schemas.CurrentSalesResponse],
    dependencies=[Depends(require_permission("depot.sales", PermissionAction.read))],
)
def list_current_sales(depot_id: int | None = None, db: Session = Depends(get_db)):
    return services.list_current_sales(db, depot_id)
