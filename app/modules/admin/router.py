from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.admin import crud, schemas

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/roles", response_model=schemas.RoleRead, status_code=status.HTTP_201_CREATED)
def create_role(role_in: schemas.RoleCreate, db: Session = Depends(get_db)):
    if crud.get_role_by_name(db, role_in.name):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Role already exists")
    return crud.create_role(db, role_in)


@router.get("/roles", response_model=schemas.Page[schemas.RoleRead])
def list_roles(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items = crud.list_roles(db, page=page, page_size=page_size)
    return schemas.Page(items=items, total=crud.count_roles(db), page=page, page_size=page_size)


@router.get("/roles/{role_id}", response_model=schemas.RoleRead)
def get_role(role_id: int, db: Session = Depends(get_db)):
    role = crud.get_role(db, role_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return role


@router.put("/roles/{role_id}", response_model=schemas.RoleRead)
def update_role(role_id: int, role_in: schemas.RoleCreate, db: Session = Depends(get_db)):
    role = crud.get_role(db, role_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    existing = crud.get_role_by_name(db, role_in.name)
    if existing and existing.id != role_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Role already exists")
    return crud.update_role(db, role, role_in)


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(role_id: int, db: Session = Depends(get_db)):
    role = crud.get_role(db, role_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    if crud.count_personnel_with_role(db, role_id) > 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Role is assigned to existing personnel")
    crud.delete_role(db, role)


@router.post("/personnel", response_model=schemas.PersonnelRead, status_code=status.HTTP_201_CREATED)
def register_personnel(personnel_in: schemas.PersonnelCreate, db: Session = Depends(get_db)):
    if personnel_in.role_id is not None and crud.get_role(db, personnel_in.role_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return crud.create_personnel(db, personnel_in)


@router.get("/personnel", response_model=schemas.Page[schemas.PersonnelRead])
def paged_list_personnel(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items = crud.paged_list_personnel(db, page=page, page_size=page_size)
    return schemas.Page(items=items, total=crud.count_personnel(db), page=page, page_size=page_size)


@router.get("/personnel/{personnel_id}", response_model=schemas.PersonnelRead)
def get_personnel(personnel_id: int, db: Session = Depends(get_db)):
    personnel = crud.get_personnel(db, personnel_id)
    if personnel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Personnel not found")
    return personnel


@router.put("/personnel/{personnel_id}", response_model=schemas.PersonnelRead)
def update_personnel(personnel_id: int, personnel_in: schemas.PersonnelCreate, db: Session = Depends(get_db)):
    personnel = crud.get_personnel(db, personnel_id)
    if personnel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Personnel not found")
    if personnel_in.role_id is not None and crud.get_role(db, personnel_in.role_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return crud.update_personnel(db, personnel, personnel_in)


@router.delete("/personnel/{personnel_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_personnel(personnel_id: int, db: Session = Depends(get_db)):
    personnel = crud.get_personnel(db, personnel_id)
    if personnel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Personnel not found")
    crud.delete_personnel(db, personnel)


@router.patch("/personnel/{personnel_id}/role", response_model=schemas.PersonnelRead)
def assign_personnel_role(personnel_id: int, role_in: schemas.PersonnelRoleAssign, db: Session = Depends(get_db)):
    personnel = crud.get_personnel(db, personnel_id)
    if personnel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Personnel not found")
    if crud.get_role(db, role_in.role_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return crud.assign_personnel_role(db, personnel, role_in.role_id)


@router.post("/products", response_model=schemas.ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(product_in: schemas.ProductCreate, db: Session = Depends(get_db)):
    if crud.get_product_by_name(db, product_in.name):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Product already exists")
    return crud.create_product(db, product_in)


@router.get("/products", response_model=schemas.Page[schemas.ProductRead])
def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items = crud.list_products(db, page=page, page_size=page_size)
    return schemas.Page(items=items, total=crud.count_products(db), page=page, page_size=page_size)


@router.get("/products/{product_id}", response_model=schemas.ProductRead)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.post("/quantities", response_model=schemas.QuantityRead, status_code=status.HTTP_201_CREATED)
def create_quantity(quantity_in: schemas.QuantityCreate, db: Session = Depends(get_db)):
    if crud.get_quantity_by_value(db, quantity_in.quantity):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Quantity already exists")
    return crud.create_quantity(db, quantity_in)


@router.get("/quantities", response_model=schemas.Page[schemas.QuantityRead])
def list_quantities(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items = crud.list_quantities(db, page=page, page_size=page_size)
    return schemas.Page(items=items, total=crud.count_quantities(db), page=page, page_size=page_size)


@router.get("/quantities/{quantity_id}", response_model=schemas.QuantityRead)
def get_quantity(quantity_id: int, db: Session = Depends(get_db)):
    quantity = crud.get_quantity(db, quantity_id)
    if quantity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quantity not found")
    return quantity


@router.post("/depots", response_model=schemas.DepotRead, status_code=status.HTTP_201_CREATED)
def create_depot(depot_in: schemas.DepotCreate, db: Session = Depends(get_db)):
    if crud.get_depot_by_name(db, depot_in.name):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Depot already exists")
    return crud.create_depot(db, depot_in)


@router.get("/depots", response_model=schemas.Page[schemas.DepotRead])
def list_depots(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items = crud.list_depots(db, page=page, page_size=page_size)
    return schemas.Page(items=items, total=crud.count_depots(db), page=page, page_size=page_size)


@router.get("/depots/{depot_id}", response_model=schemas.DepotRead)
def get_depot(depot_id: int, db: Session = Depends(get_db)):
    depot = crud.get_depot(db, depot_id)
    if depot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Depot not found")
    return depot


@router.post("/prices", response_model=schemas.PriceRead, status_code=status.HTTP_201_CREATED)
def create_price(price_in: schemas.PriceCreate, db: Session = Depends(get_db)):
    if crud.get_quantity(db, price_in.quantity_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quantity not found")
    if crud.get_price(db, price_in.quantity_id) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Price already exists for this quantity")
    return crud.create_price(db, price_in)


@router.get("/prices", response_model=schemas.Page[schemas.PriceRead])
def list_prices(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items = crud.list_prices(db, page=page, page_size=page_size)
    return schemas.Page(items=items, total=crud.count_prices(db), page=page, page_size=page_size)


@router.get("/prices/{quantity_id}", response_model=schemas.PriceRead)
def get_price(quantity_id: int, db: Session = Depends(get_db)):
    price = crud.get_price(db, quantity_id)
    if price is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Price not found")
    return price
