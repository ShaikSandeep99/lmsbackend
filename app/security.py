from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext

from app.config import settings

# Password hashing context (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ------------------------
# Password helpers
# ------------------------
def hash_password(plain_password: str) -> str:
    """Hash a plain text password using bcrypt."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against the hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


# ------------------------
# JWT helpers
# ------------------------
def create_access_token(subject: str) -> str:
    """Create an access JWT token (short-lived)."""
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")


def create_refresh_token(subject: str) -> str:
    """Create a refresh JWT token (long-lived)."""
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"sub": subject, "exp": expire, "type": "refresh"}
    return jwt.encode(to_encode, settings.JWT_REFRESH_SECRET, algorithm="HS256")


def decode_access(token: str) -> dict:
    """Decode & verify an access token."""
    return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])


def decode_refresh(token: str) -> dict:
    """Decode & verify a refresh token."""
    return jwt.decode(token, settings.JWT_REFRESH_SECRET, algorithms=["HS256"])
