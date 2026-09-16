from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.factory.models import SupplyStatus

class ProductionCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity_id: int = Field(gt=0)
    quantity_produced: int = Field(gt=0)
    production_date: datetime | None = None


class ProductionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    product_name: str
    quantity_id: int | None
    quantity_value: str | None
    quantity_produced: int
    production_date: datetime
    created_date: datetime


class FactoryStockResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    product_name: str
    quantity_id: int | None
    quantity_value: str | None
    available_quantity: int
    updated_date: datetime


class SupplyCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity_id: int = Field(gt=0)
    amount: int = Field(gt=0)
    depot_id: int = Field(gt=0)
    supplier_id: int = Field(gt=0)


class SupplyUpdate(BaseModel):
    status: SupplyStatus
    rejection_reason: str | None = Field(default=None, min_length=1)


class SupplyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    quantity_id: int
    amount: int
    product_name: str
    quantity_value: str
    depot_id: int | None
    depot_name: str | None
    supplier_id: int | None
    supplier_name: str | None
    status: SupplyStatus
    rejection_reason: str | None
    created_date: datetime