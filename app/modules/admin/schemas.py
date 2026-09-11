from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RoleCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)


class RoleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class UserCreate(BaseModel):
    role_id: int
    name: str = Field(min_length=2, max_length=150)
    contact: str = Field(min_length=7, max_length=20)
    email: EmailStr


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role_id: int
    name: str
    contact: str
    email: EmailStr
    created_at: datetime


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
