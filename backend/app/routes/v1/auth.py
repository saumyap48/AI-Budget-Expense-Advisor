from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.schemas.user import UserRegister, UserLogin, UserResponse, Token
from backend.app.schemas.common import ApiResponse
from backend.app.services.auth_service import AuthService
from backend.app.dependencies.auth import get_current_user
from backend.app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=ApiResponse[Token], status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user account and issue an access token."""
    user, access_token = AuthService.register_user(db, data)
    user_response = UserResponse.from_orm(user)
    token_obj = Token(access_token=access_token, token_type="bearer", user=user_response)
    return ApiResponse(success=True, data=token_obj, message="User registered successfully")


@router.post("/login", response_model=ApiResponse[Token])
def login(data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user credentials and issue an access token."""
    user, access_token = AuthService.authenticate_user(db, data)
    user_response = UserResponse.from_orm(user)
    token_obj = Token(access_token=access_token, token_type="bearer", user=user_response)
    return ApiResponse(success=True, data=token_obj, message="Login successful")


@router.get("/me", response_model=ApiResponse[UserResponse])
def get_me(current_user: User = Depends(get_current_user)):
    """Get authenticated user details."""
    user_response = UserResponse.from_orm(current_user)
    return ApiResponse(success=True, data=user_response, message="User profile retrieved")
