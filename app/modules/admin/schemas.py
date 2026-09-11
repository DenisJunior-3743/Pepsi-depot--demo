from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class RoleCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)


class RoleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class PersonnelCreate(BaseModel):
    role_id: int
    name: str = Field(min_length=2, max_length=150)
    gender: str = Field(min_length=1, max_length=10)
    contact: str = Field(min_length=7, max_length=20)
    salary: Decimal = Field(gt=0)


class PersonnelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role_id: int
    name: str
    gender: str
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
    quantity: int = Field(gt=0)


class QuantityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    quantity: int


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
