from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.factory.models import FactoryCurrentStock
from app.factory.schemas import FactoryStockResponse, ProductionCreate, ProductionResponse, SupplyCreate, SupplyResponse
from app.factory.services import create_supply, get_production, get_stock, get_supply, list_production, list_supplies, record_production

router = APIRouter(prefix="/factory", tags=["Factory"])


@router.post("/production", response_model=ProductionResponse, status_code=status.HTTP_201_CREATED)
def create_production(data: ProductionCreate, db: Session = Depends(get_db)):
    return record_production(db, data)


@router.get("/production", response_model=list[ProductionResponse])
def read_production_history(db: Session = Depends(get_db)):
    return list_production(db)


@router.get("/production/{production_id}", response_model=ProductionResponse)
def read_production(production_id: int, db: Session = Depends(get_db)):
    return get_production(db, production_id)


@router.post("/supplies", response_model=SupplyResponse, status_code=status.HTTP_201_CREATED)
def create_factory_supply(data: SupplyCreate, db: Session = Depends(get_db)):
    return create_supply(db, data)


@router.get("/supplies", response_model=list[SupplyResponse])
def read_supply_history(db: Session = Depends(get_db)):
    return list_supplies(db)


@router.get("/supplies/{supply_id}", response_model=SupplyResponse)
def read_factory_supply(supply_id: int, db: Session = Depends(get_db)):
    return get_supply(db, supply_id)


@router.get("/stock", response_model=list[FactoryStockResponse])
def list_factory_stock(db: Session = Depends(get_db)):
    return list(db.scalars(select(FactoryCurrentStock).options(selectinload(FactoryCurrentStock.product)).order_by(FactoryCurrentStock.product_id)))


@router.get("/stock/{product_id}", response_model=FactoryStockResponse)
def read_factory_stock(product_id: int, db: Session = Depends(get_db)):
    return get_stock(db, product_id)