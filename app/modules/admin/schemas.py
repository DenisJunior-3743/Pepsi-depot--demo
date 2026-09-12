from datetime import datetime
from decimal import Decimal
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from app.modules.admin.models import Gender

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


class RoleCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)


class RoleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class PersonnelCreate(BaseModel):
    role_id: int | None = None
    name: str = Field(min_length=2, max_length=150)
    gender: Gender
    contact: str = Field(min_length=7, max_length=20)
    salary: Decimal | None = Field(default=None, gt=0)


class PersonnelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role_id: int | None
    name: str
    gender: Gender
    contact: str
    salary: Decimal | None
    created_at: datetime


class PersonnelRoleAssign(BaseModel):
    role_id: int


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
