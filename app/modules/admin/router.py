from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.admin import crud, schemas

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/roles", response_model=schemas.RoleRead, status_code=status.HTTP_201_CREATED)
def create_role(role_in: schemas.RoleCreate, db: Session = Depends(get_db)):
    if crud.get_role_by_name(db, role_in.name):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Role already exists")
    return crud.create_role(db, role_in)


@router.get("/roles", response_model=list[schemas.RoleRead])
def list_roles(db: Session = Depends(get_db)):
    return crud.list_roles(db)


@router.get("/roles/{role_id}", response_model=schemas.RoleRead)
def get_role(role_id: int, db: Session = Depends(get_db)):
    role = crud.get_role(db, role_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return role


@router.post("/users", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def register_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_role(db, user_in.role_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    if crud.get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    return crud.create_user(db, user_in)


@router.get("/users", response_model=list[schemas.UserRead])
def list_users(db: Session = Depends(get_db)):
    return crud.list_users(db)


@router.get("/users/{user_id}", response_model=schemas.UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("/personnel", response_model=schemas.PersonnelRead, status_code=status.HTTP_201_CREATED)
def register_personnel(personnel_in: schemas.PersonnelCreate, db: Session = Depends(get_db)):
    if crud.get_role(db, personnel_in.role_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return crud.create_personnel(db, personnel_in)


@router.get("/personnel", response_model=list[schemas.PersonnelRead])
def list_personnel(db: Session = Depends(get_db)):
    return crud.list_personnel(db)


@router.get("/personnel/{personnel_id}", response_model=schemas.PersonnelRead)
def get_personnel(personnel_id: int, db: Session = Depends(get_db)):
    personnel = crud.get_personnel(db, personnel_id)
    if personnel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Personnel not found")
    return personnel
