from sqlalchemy import select
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
