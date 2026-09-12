from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.admin import models, schemas


def _count(db: Session, model) -> int:
    return db.scalar(select(func.count()).select_from(model)) or 0


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


def list_roles(db: Session, page: int = 1, page_size: int = 10) -> list[models.Role]:
    return list(
        db.scalars(
            select(models.Role).order_by(models.Role.id).offset((page - 1) * page_size).limit(page_size)
        )
    )


def count_roles(db: Session) -> int:
    return _count(db, models.Role)


def update_role(db: Session, role: models.Role, role_in: schemas.RoleCreate) -> models.Role:
    role.name = role_in.name
    db.commit()
    db.refresh(role)
    return role


def delete_role(db: Session, role: models.Role) -> None:
    db.delete(role)
    db.commit()


def count_personnel_with_role(db: Session, role_id: int) -> int:
    return db.scalar(select(func.count()).select_from(models.Personnel).where(models.Personnel.role_id == role_id)) or 0


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


def paged_list_personnel(db: Session, page: int = 1, page_size: int = 10) -> list[models.Personnel]:
    return list(
        db.scalars(
            select(models.Personnel).order_by(models.Personnel.id).offset((page - 1) * page_size).limit(page_size)
        )
    )


def count_personnel(db: Session) -> int:
    return _count(db, models.Personnel)


def update_personnel(db: Session, personnel: models.Personnel, personnel_in: schemas.PersonnelCreate) -> models.Personnel:
    personnel.role_id = personnel_in.role_id
    personnel.name = personnel_in.name
    personnel.gender = personnel_in.gender
    personnel.contact = personnel_in.contact
    personnel.salary = personnel_in.salary
    db.commit()
    db.refresh(personnel)
    return personnel


def delete_personnel(db: Session, personnel: models.Personnel) -> None:
    db.delete(personnel)
    db.commit()


def assign_personnel_role(db: Session, personnel: models.Personnel, role_id: int) -> models.Personnel:
    personnel.role_id = role_id
    db.commit()
    db.refresh(personnel)
    return personnel


def create_product(db: Session, product_in: schemas.ProductCreate) -> models.Product:
    product = models.Product(name=product_in.name)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def get_product(db: Session, product_id: int) -> models.Product | None:
    return db.get(models.Product, product_id)


def get_product_by_name(db: Session, name: str) -> models.Product | None:
    return db.scalar(select(models.Product).where(models.Product.name == name))


def list_products(db: Session, page: int = 1, page_size: int = 10) -> list[models.Product]:
    return list(
        db.scalars(
            select(models.Product).order_by(models.Product.id).offset((page - 1) * page_size).limit(page_size)
        )
    )


def count_products(db: Session) -> int:
    return _count(db, models.Product)


def create_quantity(db: Session, quantity_in: schemas.QuantityCreate) -> models.Quantity:
    quantity = models.Quantity(quantity=quantity_in.quantity)
    db.add(quantity)
    db.commit()
    db.refresh(quantity)
    return quantity


def get_quantity(db: Session, quantity_id: int) -> models.Quantity | None:
    return db.get(models.Quantity, quantity_id)


def get_quantity_by_value(db: Session, value: str) -> models.Quantity | None:
    return db.scalar(select(models.Quantity).where(models.Quantity.quantity == value))


def list_quantities(db: Session, page: int = 1, page_size: int = 10) -> list[models.Quantity]:
    return list(
        db.scalars(
            select(models.Quantity).order_by(models.Quantity.id).offset((page - 1) * page_size).limit(page_size)
        )
    )


def count_quantities(db: Session) -> int:
    return _count(db, models.Quantity)


def create_depot(db: Session, depot_in: schemas.DepotCreate) -> models.Depot:
    depot = models.Depot(name=depot_in.name, location=depot_in.location)
    db.add(depot)
    db.commit()
    db.refresh(depot)
    return depot


def get_depot(db: Session, depot_id: int) -> models.Depot | None:
    return db.get(models.Depot, depot_id)


def get_depot_by_name(db: Session, name: str) -> models.Depot | None:
    return db.scalar(select(models.Depot).where(models.Depot.name == name))


def list_depots(db: Session, page: int = 1, page_size: int = 10) -> list[models.Depot]:
    return list(
        db.scalars(
            select(models.Depot).order_by(models.Depot.id).offset((page - 1) * page_size).limit(page_size)
        )
    )


def count_depots(db: Session) -> int:
    return _count(db, models.Depot)


def create_price(db: Session, price_in: schemas.PriceCreate) -> models.Price:
    price = models.Price(
        quantity_id=price_in.quantity_id,
        amount=price_in.amount,
    )
    db.add(price)
    db.commit()
    db.refresh(price)
    return price


def get_price(db: Session, quantity_id: int) -> models.Price | None:
    return db.get(models.Price, quantity_id)


def list_prices(db: Session, page: int = 1, page_size: int = 10) -> list[models.Price]:
    return list(
        db.scalars(
            select(models.Price).order_by(models.Price.quantity_id).offset((page - 1) * page_size).limit(page_size)
        )
    )


def count_prices(db: Session) -> int:
    return _count(db, models.Price)
