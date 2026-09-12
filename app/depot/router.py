from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.depot import schemas, services
from app.depot.models import RestockStatus

router = APIRouter(prefix="/depot", tags=["depot"])


@router.post("/restock/{supply_history_id}/confirm", response_model=schemas.RestockResponse, status_code=status.HTTP_201_CREATED)
def confirm_restock(supply_history_id: int, data: schemas.RestockConfirm, db: Session = Depends(get_db)):
    return services.confirm_restock(db, supply_history_id, data)


@router.post("/restock/{supply_history_id}/reject", response_model=schemas.RestockResponse, status_code=status.HTTP_201_CREATED)
def reject_restock(supply_history_id: int, data: schemas.RestockReject, db: Session = Depends(get_db)):
    return services.reject_restock(db, supply_history_id, data)


@router.get("/restock", response_model=list[schemas.RestockResponse])
def list_restock_history(depot_id: int | None = None, status_filter: RestockStatus | None = Query(default=None, alias="status"), db: Session = Depends(get_db)):
    return services.list_restock_history(db, depot_id, status_filter)


@router.get("/restock/{entry_id}", response_model=schemas.RestockResponse)
def get_restock_entry(entry_id: int, db: Session = Depends(get_db)):
    return services.get_restock_entry(db, entry_id)


@router.put("/restock/{entry_id}", response_model=schemas.RestockResponse)
def update_restock_entry(entry_id: int, data: schemas.RestockUpdate, db: Session = Depends(get_db)):
    return services.update_restock_entry(db, entry_id, data)


@router.delete("/restock/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_restock_entry(entry_id: int, db: Session = Depends(get_db)):
    services.delete_restock_entry(db, entry_id)


@router.get("/stock", response_model=list[schemas.CurrentStockResponse])
def list_current_stock(depot_id: int | None = None, db: Session = Depends(get_db)):
    return services.list_current_stock(db, depot_id)


@router.post("/sales", response_model=schemas.SaleResponse, status_code=status.HTTP_201_CREATED)
def record_sale(data: schemas.SaleCreate, db: Session = Depends(get_db)):
    return services.record_sale(db, data)


@router.get("/sales", response_model=list[schemas.SaleResponse])
def list_sales_history(depot_id: int | None = None, db: Session = Depends(get_db)):
    return services.list_sales_history(db, depot_id)


@router.get("/sales/{sale_id}", response_model=schemas.SaleResponse)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    return services.get_sale(db, sale_id)


@router.put("/sales/{sale_id}", response_model=schemas.SaleResponse)
def update_sale(sale_id: int, data: schemas.SaleUpdate, db: Session = Depends(get_db)):
    return services.update_sale(db, sale_id, data)


@router.delete("/sales/{sale_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sale(sale_id: int, db: Session = Depends(get_db)):
    services.delete_sale(db, sale_id)


@router.get("/sales-current", response_model=list[schemas.CurrentSalesResponse])
def list_current_sales(depot_id: int | None = None, db: Session = Depends(get_db)):
    return services.list_current_sales(db, depot_id)
