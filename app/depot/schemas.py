from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field

from app.depot.models import RestockStatus


class RestockConfirm(BaseModel):
    depot_id: int = Field(gt=0)
    quantity_received: int = Field(gt=0)
    supplier_id: int | None = None
    confirmed_by_id: int | None = None


class RestockReject(BaseModel):
    depot_id: int = Field(gt=0)
    reason: str = Field(min_length=3)
    quantity_received: int | None = Field(default=None, ge=0)
    supplier_id: int | None = None
    confirmed_by_id: int | None = None


class RestockUpdate(BaseModel):
    quantity_delivered: int = Field(gt=0)


class RestockResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    supply_history_id: int
    depot_id: int
    depot_name: str
    product_id: int
    product_name: str
    quantity_id: int
    quantity_value: str
    quantity_delivered: int
    supplier_id: int | None
    confirmed_by_id: int | None
    status: RestockStatus
    rejection_reason: str | None
    restock_date: datetime


class CurrentStockResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    depot_id: int
    depot_name: str
    product_id: int
    product_name: str
    quantity_id: int
    quantity_value: str
    current_amount: int
    updated_at: datetime


class SaleCreate(BaseModel):
    depot_id: int = Field(gt=0)
    product_id: int = Field(gt=0)
    quantity_id: int = Field(gt=0)
    quantity_sold: int = Field(gt=0)
    amount_sold: float | None = Field(default=None, gt=0)
    sold_by_id: int | None = None


class SaleUpdate(BaseModel):
    quantity_sold: int = Field(gt=0)
    amount_sold: float = Field(gt=0)


class SaleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    depot_id: int
    depot_name: str
    product_id: int
    product_name: str
    quantity_id: int
    quantity_value: str
    quantity_sold: int
    amount_sold: float
    sold_by_id: int | None
    sale_date: date
    sale_time: time


class CurrentSalesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    depot_id: int
    depot_name: str
    product_id: int
    product_name: str
    quantity_id: int
    quantity_value: str
    sale_date: date
    quantity_sold: int
    sold_amount: float
