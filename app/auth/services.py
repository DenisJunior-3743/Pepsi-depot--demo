from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.auth.models import Module, Permission, RolePermission, User
from app.auth.schemas import CurrentUserResponse, LoginRequest, UserCreate
from app.auth.security import create_access_token, hash_password, verify_password
from app.modules.admin.models import Personnel, Role


def get_permission_strings_for_role(db: Session, role_id: int | None) -> list[str]:
    if role_id is None:
        return []
    rows = db.execute(
        select(Module.key, Permission.action)
        .select_from(RolePermission)
        .join(Permission, RolePermission.permission_id == Permission.id)
        .join(Module, Permission.module_id == Module.id)
        .where(RolePermission.role_id == role_id)
    ).all()
    return sorted(f"{module_key}:{action.value}" for module_key, action in rows)


def login(db: Session, data: LoginRequest) -> tuple[User, str]:
    personnel = db.scalar(select(Personnel).where(Personnel.email == data.email))
    if personnel is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    user = db.scalar(select(User).where(User.personnel_id == personnel.id))
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    token = create_access_token(user.id)
    return user, token


def create_users_batch(db: Session, users_in: list[UserCreate]) -> list[User]:
    personnel_ids = [u.personnel_id for u in users_in]
    if len(personnel_ids) != len(set(personnel_ids)):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Duplicate personnel_id in request")
    usernames = [u.username for u in users_in]
    if len(usernames) != len(set(usernames)):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Duplicate username in request")
    for data in users_in:
        if db.get(Personnel, data.personnel_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Personnel not found: {data.personnel_id}")

    users = [
        User(username=data.username, password_hash=hash_password(data.password), personnel_id=data.personnel_id)
        for data in users_in
    ]
    try:
        db.add_all(users)
        db.commit()
        for user in users:
            db.refresh(user)
        return users
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A username is already taken, or a personnel record already has a login account")


def get_current_user_by_id(db: Session, user_id: int) -> User | None:
    return db.scalar(
        select(User).options(selectinload(User.personnel)).where(User.id == user_id)
    )


def to_current_user_response(db: Session, user: User) -> CurrentUserResponse:
    personnel = user.personnel
    role = db.get(Role, personnel.role_id) if personnel.role_id is not None else None
    return CurrentUserResponse(
        id=user.id,
        username=user.username,
        personnel_id=personnel.id,
        personnel_name=personnel.name,
        role_id=role.id if role else None,
        role_name=role.name if role else None,
        permissions=get_permission_strings_for_role(db, personnel.role_id),
    )


def list_modules(db: Session) -> list[Module]:
    return list(db.scalars(select(Module).order_by(Module.key)))


def list_permissions(db: Session) -> list[Permission]:
    return list(db.scalars(select(Permission).options(selectinload(Permission.module)).join(Module).order_by(Module.key, Permission.action)))


def list_role_permissions(db: Session, role_id: int) -> list[Permission]:
    return list(
        db.scalars(
            select(Permission)
            .options(selectinload(Permission.module))
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(Module, Permission.module_id == Module.id)
            .where(RolePermission.role_id == role_id)
            .order_by(Module.key, Permission.action)
        )
    )


def assign_permissions_to_role(db: Session, role_id: int, permission_ids: list[int]) -> list[Permission]:
    if db.get(Role, role_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    valid_ids = set(db.scalars(select(Permission.id).where(Permission.id.in_(permission_ids))))
    missing = set(permission_ids) - valid_ids
    if missing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unknown permission id(s): {sorted(missing)}")
    already_granted = set(
        db.scalars(select(RolePermission.permission_id).where(RolePermission.role_id == role_id))
    )
    for permission_id in valid_ids - already_granted:
        db.add(RolePermission(role_id=role_id, permission_id=permission_id))
    db.commit()
    return list_role_permissions(db, role_id)


def revoke_permission_from_role(db: Session, role_id: int, permission_id: int) -> None:
    row = db.get(RolePermission, (role_id, permission_id))
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role does not have this permission")
    db.delete(row)
    db.commit()
