from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_permission
from app.auth.models import PermissionAction
from app.db.session import get_db
from app.modules.admin import crud, schemas

router = APIRouter(prefix="/admin", tags=["admin"])


def _reject_batch_duplicates(values: list[str], label: str) -> None:
    seen = set()
    for value in values:
        key = value.lower()
        if key in seen:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Duplicate {label} in request: {value}")
        seen.add(key)


@router.post(
    "/roles",
    response_model=list[schemas.RoleRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("admin.roles", PermissionAction.create))],
)
def create_roles(roles_in: list[schemas.RoleCreate] = Body(..., min_length=1), db: Session = Depends(get_db)):
    _reject_batch_duplicates([r.name for r in roles_in], "role name")
    for role_in in roles_in:
        if crud.get_role_by_name(db, role_in.name):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Role already exists: {role_in.name}")
    return crud.create_roles_batch(db, roles_in)


@router.get(
    "/roles",
    response_model=schemas.Page[schemas.RoleRead],
    dependencies=[Depends(require_permission("admin.roles", PermissionAction.read))],
)
def list_roles(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items = crud.list_roles(db, page=page, page_size=page_size)
    return schemas.Page(items=items, total=crud.count_roles(db), page=page, page_size=page_size)


@router.get(
    "/roles/{role_id}",
    response_model=schemas.RoleRead,
    dependencies=[Depends(require_permission("admin.roles", PermissionAction.read))],
)
def get_role(role_id: int, db: Session = Depends(get_db)):
    role = crud.get_role(db, role_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return role


@router.put(
    "/roles/{role_id}",
    response_model=schemas.RoleRead,
    dependencies=[Depends(require_permission("admin.roles", PermissionAction.update))],
)
def update_role(role_id: int, role_in: schemas.RoleCreate, db: Session = Depends(get_db)):
    role = crud.get_role(db, role_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    existing = crud.get_role_by_name(db, role_in.name)
    if existing and existing.id != role_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Role already exists")
    return crud.update_role(db, role, role_in)


@router.delete(
    "/roles/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("admin.roles", PermissionAction.delete))],
)
def delete_role(role_id: int, db: Session = Depends(get_db)):
    role = crud.get_role(db, role_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    if crud.count_personnel_with_role(db, role_id) > 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Role is assigned to existing personnel")
    crud.delete_role(db, role)


@router.post(
    "/personnel",
    response_model=list[schemas.PersonnelRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("admin.personnel", PermissionAction.create))],
)
def register_personnel(personnel_in: list[schemas.PersonnelCreate] = Body(..., min_length=1), db: Session = Depends(get_db)):
    for entry in personnel_in:
        if entry.role_id is not None and crud.get_role(db, entry.role_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Role not found: {entry.role_id}")
        if entry.depot_id is not None and crud.get_depot(db, entry.depot_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Depot not found: {entry.depot_id}")
    return crud.create_personnel_batch(db, personnel_in)


@router.get(
    "/personnel",
    response_model=schemas.Page[schemas.PersonnelRead],
    dependencies=[Depends(require_permission("admin.personnel", PermissionAction.read))],
)
def paged_list_personnel(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    role_id: int | None = Query(None, gt=0),
    depot_id: int | None = Query(None, gt=0),
    db: Session = Depends(get_db),
):
    items = crud.paged_list_personnel(db, page=page, page_size=page_size, role_id=role_id, depot_id=depot_id)
    return schemas.Page(items=items, total=crud.count_personnel(db, role_id=role_id, depot_id=depot_id), page=page, page_size=page_size)


@router.get(
    "/personnel/{personnel_id}",
    response_model=schemas.PersonnelRead,
    dependencies=[Depends(require_permission("admin.personnel", PermissionAction.read))],
)
def get_personnel(personnel_id: int, db: Session = Depends(get_db)):
    personnel = crud.get_personnel(db, personnel_id)
    if personnel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Personnel not found")
    return personnel


@router.put(
    "/personnel/{personnel_id}",
    response_model=schemas.PersonnelRead,
    dependencies=[Depends(require_permission("admin.personnel", PermissionAction.update))],
)
def update_personnel(personnel_id: int, personnel_in: schemas.PersonnelCreate, db: Session = Depends(get_db)):
    personnel = crud.get_personnel(db, personnel_id)
    if personnel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Personnel not found")
    if personnel_in.role_id is not None and crud.get_role(db, personnel_in.role_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    if personnel_in.depot_id is not None and crud.get_depot(db, personnel_in.depot_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Depot not found")
    return crud.update_personnel(db, personnel, personnel_in)


@router.delete(
    "/personnel/{personnel_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("admin.personnel", PermissionAction.delete))],
)
def delete_personnel(personnel_id: int, db: Session = Depends(get_db)):
    personnel = crud.get_personnel(db, personnel_id)
    if personnel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Personnel not found")
    crud.delete_personnel(db, personnel)


@router.patch(
    "/personnel/{personnel_id}/role",
    response_model=schemas.PersonnelRead,
    dependencies=[Depends(require_permission("admin.personnel", PermissionAction.update))],
)
def assign_personnel_role(personnel_id: int, role_in: schemas.PersonnelRoleAssign, db: Session = Depends(get_db)):
    personnel = crud.get_personnel(db, personnel_id)
    if personnel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Personnel not found")
    if crud.get_role(db, role_in.role_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return crud.assign_personnel_role(db, personnel, role_in.role_id)


@router.patch(
    "/personnel/{personnel_id}/depot",
    response_model=schemas.PersonnelRead,
    dependencies=[Depends(require_permission("admin.personnel", PermissionAction.update))],
)
def assign_personnel_depot(personnel_id: int, depot_in: schemas.PersonnelDepotAssign, db: Session = Depends(get_db)):
    personnel = crud.get_personnel(db, personnel_id)
    if personnel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Personnel not found")
    if crud.get_depot(db, depot_in.depot_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Depot not found")
    return crud.assign_personnel_depot(db, personnel, depot_in.depot_id)


@router.post(
    "/products",
    response_model=list[schemas.ProductRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("admin.products", PermissionAction.create))],
)
def create_products(products_in: list[schemas.ProductCreate] = Body(..., min_length=1), db: Session = Depends(get_db)):
    _reject_batch_duplicates([p.name for p in products_in], "product name")
    for product_in in products_in:
        if crud.get_product_by_name(db, product_in.name):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Product already exists: {product_in.name}")
    return crud.create_products_batch(db, products_in)


@router.get(
    "/products",
    response_model=schemas.Page[schemas.ProductRead],
    dependencies=[Depends(require_permission("admin.products", PermissionAction.read))],
)
def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items = crud.list_products(db, page=page, page_size=page_size)
    return schemas.Page(items=items, total=crud.count_products(db), page=page, page_size=page_size)


@router.get(
    "/products/{product_id}",
    response_model=schemas.ProductRead,
    dependencies=[Depends(require_permission("admin.products", PermissionAction.read))],
)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.post(
    "/quantities",
    response_model=list[schemas.QuantityRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("admin.quantities", PermissionAction.create))],
)
def create_quantities(quantities_in: list[schemas.QuantityCreate] = Body(..., min_length=1), db: Session = Depends(get_db)):
    _reject_batch_duplicates([q.quantity for q in quantities_in], "quantity value")
    for quantity_in in quantities_in:
        if crud.get_quantity_by_value(db, quantity_in.quantity):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Quantity already exists: {quantity_in.quantity}")
    return crud.create_quantities_batch(db, quantities_in)


@router.get(
    "/quantities",
    response_model=schemas.Page[schemas.QuantityRead],
    dependencies=[Depends(require_permission("admin.quantities", PermissionAction.read))],
)
def list_quantities(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items = crud.list_quantities(db, page=page, page_size=page_size)
    return schemas.Page(items=items, total=crud.count_quantities(db), page=page, page_size=page_size)


@router.get(
    "/quantities/{quantity_id}",
    response_model=schemas.QuantityRead,
    dependencies=[Depends(require_permission("admin.quantities", PermissionAction.read))],
)
def get_quantity(quantity_id: int, db: Session = Depends(get_db)):
    quantity = crud.get_quantity(db, quantity_id)
    if quantity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quantity not found")
    return quantity


@router.post(
    "/depots",
    response_model=list[schemas.DepotRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("admin.depots", PermissionAction.create))],
)
def create_depots(depots_in: list[schemas.DepotCreate] = Body(..., min_length=1), db: Session = Depends(get_db)):
    _reject_batch_duplicates([d.name for d in depots_in], "depot name")
    for depot_in in depots_in:
        if crud.get_depot_by_name(db, depot_in.name):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Depot already exists: {depot_in.name}")
    return crud.create_depots_batch(db, depots_in)


@router.get(
    "/depots",
    response_model=schemas.Page[schemas.DepotRead],
    dependencies=[Depends(require_permission("admin.depots", PermissionAction.read))],
)
def list_depots(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items = crud.list_depots(db, page=page, page_size=page_size)
    return schemas.Page(items=items, total=crud.count_depots(db), page=page, page_size=page_size)


@router.get(
    "/depots/{depot_id}",
    response_model=schemas.DepotRead,
    dependencies=[Depends(require_permission("admin.depots", PermissionAction.read))],
)
def get_depot(depot_id: int, db: Session = Depends(get_db)):
    depot = crud.get_depot(db, depot_id)
    if depot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Depot not found")
    return depot


@router.put(
    "/depots/{depot_id}",
    response_model=schemas.DepotRead,
    dependencies=[Depends(require_permission("admin.depots", PermissionAction.update))],
)
def update_depot(depot_id: int, depot_in: schemas.DepotCreate, db: Session = Depends(get_db)):
    depot = crud.get_depot(db, depot_id)
    if depot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Depot not found")
    existing = crud.get_depot_by_name(db, depot_in.name)
    if existing and existing.id != depot_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Depot already exists")
    return crud.update_depot(db, depot, depot_in)


@router.delete(
    "/depots/{depot_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("admin.depots", PermissionAction.delete))],
)
def delete_depot(depot_id: int, db: Session = Depends(get_db)):
    depot = crud.get_depot(db, depot_id)
    if depot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Depot not found")
    if crud.count_personnel_with_depot(db, depot_id) > 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Depot is assigned to existing personnel")
    crud.delete_depot(db, depot)


@router.post(
    "/prices",
    response_model=list[schemas.PriceRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("admin.prices", PermissionAction.create))],
)
def create_prices(prices_in: list[schemas.PriceCreate] = Body(..., min_length=1), db: Session = Depends(get_db)):
    seen_quantity_ids = set()
    for price_in in prices_in:
        if price_in.quantity_id in seen_quantity_ids:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Duplicate quantity_id in request: {price_in.quantity_id}")
        seen_quantity_ids.add(price_in.quantity_id)
        if crud.get_quantity(db, price_in.quantity_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Quantity not found: {price_in.quantity_id}")
        if crud.get_price(db, price_in.quantity_id) is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Price already exists for quantity: {price_in.quantity_id}")
    return crud.create_prices_batch(db, prices_in)


@router.get(
    "/prices",
    response_model=schemas.Page[schemas.PriceRead],
    dependencies=[Depends(require_permission("admin.prices", PermissionAction.read))],
)
def list_prices(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items = crud.list_prices(db, page=page, page_size=page_size)
    return schemas.Page(items=items, total=crud.count_prices(db), page=page, page_size=page_size)


@router.get(
    "/prices/{quantity_id}",
    response_model=schemas.PriceRead,
    dependencies=[Depends(require_permission("admin.prices", PermissionAction.read))],
)
def get_price(quantity_id: int, db: Session = Depends(get_db)):
    price = crud.get_price(db, quantity_id)
    if price is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Price not found")
    return price


@router.put(
    "/prices/{quantity_id}",
    response_model=schemas.PriceRead,
    dependencies=[Depends(require_permission("admin.prices", PermissionAction.update))],
)
def update_price(quantity_id: int, price_in: schemas.PriceUpdate, db: Session = Depends(get_db)):
    price = crud.get_price(db, quantity_id)
    if price is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Price not found")
    return crud.update_price(db, price, price_in)


@router.delete(
    "/prices/{quantity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("admin.prices", PermissionAction.delete))],
)
def delete_price(quantity_id: int, db: Session = Depends(get_db)):
    price = crud.get_price(db, quantity_id)
    if price is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Price not found")
    crud.delete_price(db, price)
