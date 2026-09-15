from fastapi import APIRouter, Body, Depends, status
from sqlalchemy.orm import Session

from app.auth import schemas, services
from app.auth.dependencies import get_current_user, require_permission
from app.auth.models import PermissionAction, User
from app.db.session import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=schemas.TokenResponse)
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    user, token = services.login(db, data)
    return schemas.TokenResponse(access_token=token, user=services.to_current_user_response(db, user))


@router.get("/me", response_model=schemas.CurrentUserResponse)
def read_current_user(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return services.to_current_user_response(db, current_user)


@router.post(
    "/users",
    response_model=list[schemas.UserRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("auth.users", PermissionAction.create))],
)
def create_users(users_in: list[schemas.UserCreate] = Body(..., min_length=1), db: Session = Depends(get_db)):
    return services.create_users_batch(db, users_in)


@router.get(
    "/modules",
    response_model=list[schemas.ModuleRead],
    dependencies=[Depends(require_permission("auth.permissions", PermissionAction.read))],
)
def list_modules(db: Session = Depends(get_db)):
    return services.list_modules(db)


@router.get(
    "/permissions",
    response_model=list[schemas.PermissionRead],
    dependencies=[Depends(require_permission("auth.permissions", PermissionAction.read))],
)
def list_permissions(db: Session = Depends(get_db)):
    return services.list_permissions(db)


@router.get(
    "/roles/{role_id}/permissions",
    response_model=list[schemas.PermissionRead],
    dependencies=[Depends(require_permission("auth.permissions", PermissionAction.read))],
)
def list_role_permissions(role_id: int, db: Session = Depends(get_db)):
    return services.list_role_permissions(db, role_id)


@router.post(
    "/roles/{role_id}/permissions",
    response_model=list[schemas.PermissionRead],
    dependencies=[Depends(require_permission("auth.permissions", PermissionAction.update))],
)
def assign_role_permissions(role_id: int, data: schemas.RolePermissionsAssign, db: Session = Depends(get_db)):
    return services.assign_permissions_to_role(db, role_id, data.permission_ids)


@router.delete(
    "/roles/{role_id}/permissions/{permission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("auth.permissions", PermissionAction.update))],
)
def revoke_role_permission(role_id: int, permission_id: int, db: Session = Depends(get_db)):
    services.revoke_permission_from_role(db, role_id, permission_id)
