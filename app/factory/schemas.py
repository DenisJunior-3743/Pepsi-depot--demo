from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.factory.models import SupplyStatus


class ProductionCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity_produced: int = Field(gt=0)
    production_date: datetime | None = None
    recorded_by_user_id: int | None = Field(default=None, gt=0)


class ProductionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    product_name: str
    quantity_produced: int
    production_date: datetime
    created_date: datetime
    recorded_by_user_id: int | None


class FactoryStockResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    product_name: str
    available_quantity: int
    updated_date: datetime


class SupplyItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity_supplied: int = Field(gt=0)


class SupplyCreate(BaseModel):
    destination_depot_id: int = Field(gt=0)
    items: list[SupplyItemCreate] = Field(min_length=1)
    dispatched_by_user_id: int | None = Field(default=None, gt=0)
    supply_date: datetime | None = None


class SupplyItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    product_name: str
    quantity_supplied: int
    quantity_received: int | None


class SupplyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    destination_depot_id: int
    destination_depot_name: str
    dispatched_by_user_id: int | None
    status: SupplyStatus
    supply_date: datetime
    created_date: datetime
    items: list[SupplyItemResponse]