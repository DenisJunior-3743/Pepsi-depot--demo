import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth.models import PermissionAction, User
from app.auth.security import decode_access_token
from app.auth.services import get_current_user_by_id, get_permission_strings_for_role
from app.db.session import get_db

_bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        user_id = decode_access_token(credentials.credentials)
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    user = get_current_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_permission(module_key: str, action: PermissionAction):
    def _check(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
        role_id = current_user.personnel.role_id
        granted = get_permission_strings_for_role(db, role_id)
        needed = f"{module_key}:{action.value}"
        if needed not in granted:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Missing permission: {needed}")
        return current_user

    return _check
