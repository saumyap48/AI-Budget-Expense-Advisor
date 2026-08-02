from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import decode_access_token
from backend.app.models.user import User
from backend.app.repositories.user_repository import UserRepository
from backend.app.core.exceptions import AuthenticationException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    FastAPI dependency to extract and validate JWT access token from Authorization header.
    Returns authenticated User model or raises HTTP 401.
    """
    if not token:
        raise AuthenticationException("Authentication required. Please log in.")

    payload = decode_access_token(token)
    if not payload:
        raise AuthenticationException("Invalid or expired authentication token.")

    user_id_str = payload.get("sub")
    if not user_id_str or not user_id_str.isdigit():
        raise AuthenticationException("Invalid token payload format.")

    user_id = int(user_id_str)
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)

    if not user:
        raise AuthenticationException("User account associated with token no longer exists.")

    return user
