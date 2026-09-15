from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.admin import models, schemas


def _count(db: Session, model) -> int:
    return db.scalar(select(func.count()).select_from(model)) or 0


def create_roles_batch(db: Session, roles_in: list[schemas.RoleCreate]) -> list[models.Role]:
    roles = [models.Role(name=r.name) for r in roles_in]
    db.add_all(roles)
    db.commit()
    for role in roles:
        db.refresh(role)
    return roles


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


def count_personnel_with_depot(db: Session, depot_id: int) -> int:
    return db.scalar(select(func.count()).select_from(models.Personnel).where(models.Personnel.depot_id == depot_id)) or 0


def create_personnel_batch(db: Session, personnel_in: list[schemas.PersonnelCreate]) -> list[models.Personnel]:
    records = [
        models.Personnel(
            role_id=p.role_id,
            depot_id=p.depot_id,
            name=p.name,
            email=p.email,
            gender=p.gender,
            contact=p.contact,
            salary=p.salary,
        )
        for p in personnel_in
    ]
    db.add_all(records)
    db.commit()
    for record in records:
        db.refresh(record)
    return records


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
    personnel.depot_id = personnel_in.depot_id
    personnel.name = personnel_in.name
    personnel.email = personnel_in.email
    personnel.gender = personnel_in.gender
    personnel.contact = personnel_in.contact
    personnel.salary = personnel_in.salary
    db.commit()
    db.refresh(personnel)
    return personnel


def delete_personnel(db: Session, personnel: models.Personnel) -> None:
    db.delete(personnel)
    db.commit()


def assign_personnel_depot(db: Session, personnel: models.Personnel, depot_id: int) -> models.Personnel:
    personnel.depot_id = depot_id
    db.commit()
    db.refresh(personnel)
    return personnel


def assign_personnel_role(db: Session, personnel: models.Personnel, role_id: int) -> models.Personnel:
    personnel.role_id = role_id
    db.commit()
    db.refresh(personnel)
    return personnel


def create_products_batch(db: Session, products_in: list[schemas.ProductCreate]) -> list[models.Product]:
    products = [models.Product(name=p.name) for p in products_in]
    db.add_all(products)
    db.commit()
    for product in products:
        db.refresh(product)
    return products


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


def create_quantities_batch(db: Session, quantities_in: list[schemas.QuantityCreate]) -> list[models.Quantity]:
    quantities = [models.Quantity(quantity=q.quantity) for q in quantities_in]
    db.add_all(quantities)
    db.commit()
    for quantity in quantities:
        db.refresh(quantity)
    return quantities


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


def create_depots_batch(db: Session, depots_in: list[schemas.DepotCreate]) -> list[models.Depot]:
    depots = [models.Depot(name=d.name, location=d.location) for d in depots_in]
    db.add_all(depots)
    db.commit()
    for depot in depots:
        db.refresh(depot)
    return depots


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


def update_depot(db: Session, depot: models.Depot, depot_in: schemas.DepotCreate) -> models.Depot:
    depot.name = depot_in.name
    depot.location = depot_in.location
    db.commit()
    db.refresh(depot)
    return depot


def delete_depot(db: Session, depot: models.Depot) -> None:
    db.delete(depot)
    db.commit()


def create_prices_batch(db: Session, prices_in: list[schemas.PriceCreate]) -> list[models.Price]:
    prices = [models.Price(quantity_id=p.quantity_id, amount=p.amount) for p in prices_in]
    db.add_all(prices)
    db.commit()
    for price in prices:
        db.refresh(price)
    return prices


def get_price(db: Session, quantity_id: int) -> models.Price | None:
    return db.scalar(select(models.Price).where(models.Price.quantity_id == quantity_id))


def list_prices(db: Session, page: int = 1, page_size: int = 10) -> list[models.Price]:
    return list(
        db.scalars(
            select(models.Price).order_by(models.Price.quantity_id).offset((page - 1) * page_size).limit(page_size)
        )
    )


def count_prices(db: Session) -> int:
    return _count(db, models.Price)


def update_price(db: Session, price: models.Price, price_in: schemas.PriceUpdate) -> models.Price:
    price.amount = price_in.amount
    db.commit()
    db.refresh(price)
    return price


def delete_price(db: Session, price: models.Price) -> None:
    db.delete(price)
    db.commit()
