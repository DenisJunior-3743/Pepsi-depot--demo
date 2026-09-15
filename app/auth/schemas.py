from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.auth.models import PermissionAction


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)


class CurrentUserResponse(BaseModel):
    id: int
    username: str
    personnel_id: int
    personnel_name: str
    role_id: int | None
    role_name: str | None
    permissions: list[str]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: CurrentUserResponse


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=6, max_length=72)
    personnel_id: int = Field(gt=0)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    personnel_id: int
    created_at: datetime


class ModuleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    key: str
    name: str
    description: str | None


class PermissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    module_id: int
    module_key: str
    module_name: str
    action: PermissionAction


class RolePermissionsAssign(BaseModel):
    permission_ids: list[int] = Field(min_length=1)
