from typing import Tuple
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin
from app.repositories.user_repository import UserRepository
from app.core.security import hash_password, verify_password, create_access_token
from app.core.exceptions import ValidationException, AuthenticationException
from app.core.logging import logger


class AuthService:

    @staticmethod
    def register_user(db: Session, data: UserRegister) -> Tuple[User, str]:
        """Register a new user, hash password, and issue JWT access token."""
        user_repo = UserRepository(db)

        # Check if email is already registered
        existing_user = user_repo.get_by_email(data.email)
        if existing_user:
            logger.warning(f"Registration failed: Email '{data.email}' already registered.")
            raise ValidationException("An account with this email address already exists.")

        # Hash password and create user
        pw_hash = hash_password(data.password)
        user = user_repo.create_user(
            full_name=data.full_name,
            email=data.email,
            password_hash=pw_hash
        )

        # Generate JWT access token
        access_token = create_access_token({"sub": str(user.id), "email": user.email})
        logger.info(f"User registered successfully: ID {user.id} ({user.email})")

        return user, access_token

    @staticmethod
    def authenticate_user(db: Session, data: UserLogin) -> Tuple[User, str]:
        """Authenticate user credentials and issue JWT access token."""
        user_repo = UserRepository(db)

        user = user_repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.password_hash):
            logger.warning(f"Login failed for email '{data.email}': Invalid credentials.")
            raise AuthenticationException("Invalid email or password.")

        access_token = create_access_token({"sub": str(user.id), "email": user.email})
        logger.info(f"User authenticated successfully: ID {user.id} ({user.email})")

        return user, access_token
