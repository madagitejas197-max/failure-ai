from datetime import datetime, timedelta
from typing import Any, Optional, Union
from jose import jwt
from passlib.context import CryptContext

from app.config import get_settings

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def create_jwt_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
    token_type: str = "access",
) -> str:
    """Create JWT token with expiration and subject."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    elif token_type == "access":
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.refresh_token_expire_days
        )

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": token_type,
    }
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def decode_jwt_token(token: str) -> dict:
    """Decode JWT token and return claims. Raises jwt.JWTError if invalid."""
    return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
