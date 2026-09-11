from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.modules.admin.models import Gender


class RoleCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)


class RoleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class PersonnelCreate(BaseModel):
    role_id: int
    name: str = Field(min_length=2, max_length=150)
    gender: Gender
    contact: str = Field(min_length=7, max_length=20)
    salary: Decimal = Field(gt=0)


class PersonnelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role_id: int
    name: str
    gender: Gender
    contact: str
    salary: Decimal
    created_at: datetime


class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class QuantityCreate(BaseModel):
    quantity: str = Field(min_length=1, max_length=50)


class QuantityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    quantity: str


class DepotCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    location: str = Field(min_length=2, max_length=255)


class DepotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    location: str


class PriceCreate(BaseModel):
    quantity_id: int
    amount: Decimal = Field(gt=0)


class PriceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    quantity_id: int
    amount: Decimal
