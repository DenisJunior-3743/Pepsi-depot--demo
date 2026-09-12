from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.factory.models import SupplyStatus

class ProductionCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity_produced: int = Field(gt=0)
    production_date: datetime | None = None


class ProductionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    product_name: str
    quantity_produced: int
    production_date: datetime
    created_date: datetime


class FactoryStockResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    product_name: str
    available_quantity: int
    updated_date: datetime


class SupplyCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity_id: int = Field(gt=0)
    amount: int = Field(gt=0)


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
    status: SupplyStatus
    rejection_reason: str | None
    created_date: datetime