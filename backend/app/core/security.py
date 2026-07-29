from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import html

from passlib.context import CryptContext
from jose import jwt, JWTError, ExpiredSignatureError

from app.core.config import settings
from app.core.logging import logger, error_logger

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------
# We use Argon2 (winner of the Password Hashing Competition) instead of bcrypt.
#
# Why not bcrypt?
#   passlib 1.7.4 (last release: 2020, unmaintained) uses the __about__ module
#   to detect the bcrypt library version.  bcrypt 4.x→5.0 removed __about__,
#   causing passlib to raise:
#       ValueError: password cannot be longer than 72 bytes
#   on EVERY password — even short ones — because the backend detection fails.
#
# Why Argon2?
#   • No 72-byte input limit (handles passwords of any length)
#   • Memory-hard: resistant to GPU / ASIC brute-force attacks
#   • Actively maintained (argon2-cffi)
#   • passlib has first-class Argon2 support via CryptContext
#
# The `deprecated="auto"` setting means any hash produced with an old scheme
# will be transparently re-hashed to argon2 on next successful login, making
# future algorithm migrations seamless.
# ---------------------------------------------------------------------------
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a raw password using Argon2id."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a raw password against its Argon2 (or legacy) hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta if expires_delta
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT access token. Returns None on any failure."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except ExpiredSignatureError:
        logger.warning("Attempted use of expired JWT token.")
        return None
    except JWTError as e:
        error_logger.warning(f"Invalid JWT token: {str(e)}")
        return None


# ---------------------------------------------------------------------------
# Input sanitisation
# ---------------------------------------------------------------------------

def sanitize_input(text: Optional[str]) -> Optional[str]:
    """Sanitize HTML and whitespace from user input strings."""
    if not text:
        return text
    return html.escape(text.strip())
