from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.admin import models, schemas


def create_role(db: Session, role_in: schemas.RoleCreate) -> models.Role:
    role = models.Role(name=role_in.name)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def get_role(db: Session, role_id: int) -> models.Role | None:
    return db.get(models.Role, role_id)


def get_role_by_name(db: Session, name: str) -> models.Role | None:
    return db.scalar(select(models.Role).where(models.Role.name == name))


def list_roles(db: Session) -> list[models.Role]:
    return list(db.scalars(select(models.Role).order_by(models.Role.id)))


def update_role(db: Session, role: models.Role, role_in: schemas.RoleCreate) -> models.Role:
    role.name = role_in.name
    db.commit()
    db.refresh(role)
    return role


def delete_role(db: Session, role: models.Role) -> None:
    db.delete(role)
    db.commit()


def count_users_with_role(db: Session, role_id: int) -> int:
    return db.scalar(select(func.count()).select_from(models.User).where(models.User.role_id == role_id)) or 0


def create_user(db: Session, user_in: schemas.UserCreate) -> models.User:
    user = models.User(
        role_id=user_in.role_id,
        name=user_in.name,
        gender=user_in.gender,
        contact=user_in.contact,
        salary=user_in.salary,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, user_id: int) -> models.User | None:
    return db.get(models.User, user_id)


def list_users(db: Session) -> list[models.User]:
    return list(db.scalars(select(models.User).order_by(models.User.id)))


def update_user(db: Session, user: models.User, user_in: schemas.UserCreate) -> models.User:
    user.role_id = user_in.role_id
    user.name = user_in.name
    user.gender = user_in.gender
    user.contact = user_in.contact
    user.salary = user_in.salary
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: models.User) -> None:
    db.delete(user)
    db.commit()
