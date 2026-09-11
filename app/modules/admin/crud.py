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
        contact=user_in.contact,
        email=user_in.email,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, user_id: int) -> models.User | None:
    return db.get(models.User, user_id)


def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.scalar(select(models.User).where(models.User.email == email))


def list_users(db: Session) -> list[models.User]:
    return list(db.scalars(select(models.User).order_by(models.User.id)))


def create_personnel(db: Session, personnel_in: schemas.PersonnelCreate) -> models.Personnel:
    personnel = models.Personnel(
        role_id=personnel_in.role_id,
        name=personnel_in.name,
        gender=personnel_in.gender,
        contact=personnel_in.contact,
        salary=personnel_in.salary,
    )
    db.add(personnel)
    db.commit()
    db.refresh(personnel)
    return personnel


def get_personnel(db: Session, personnel_id: int) -> models.Personnel | None:
    return db.get(models.Personnel, personnel_id)


def list_personnel(db: Session) -> list[models.Personnel]:
    return list(db.scalars(select(models.Personnel).order_by(models.Personnel.id)))
