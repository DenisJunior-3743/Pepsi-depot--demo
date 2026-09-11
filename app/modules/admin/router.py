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
    if crud.count_users_with_role(db, role_id) > 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Role is assigned to existing users")
    crud.delete_role(db, role)


@router.post("/users", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def register_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_role(db, user_in.role_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
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


@router.put("/users/{user_id}", response_model=schemas.UserRead)
def update_user(user_id: int, user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if crud.get_role(db, user_in.role_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return crud.update_user(db, user, user_in)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    crud.delete_user(db, user)
