from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uuid

from app.config import get_settings
from app.database import get_db
from app.models import User, UserRole
from app.core.security import ALGORITHM

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    """Dependency to retrieve the currently authenticated user from a JWT access token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        user_id_str: Optional[str] = payload.get("sub")
        token_type: Optional[str] = payload.get("type")

        if user_id_str is None or token_type != "access":
            raise credentials_exception

        user_id = uuid.UUID(user_id_str)
    except (jwt.JWTError, ValueError):
        raise credentials_exception

    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()

    if user is None:
        raise credentials_exception

    return user


class RoleChecker:
    """Helper class to enforce minimum role authorization requirements."""

    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        # If admin, let them pass everything
        if current_user.role == UserRole.admin:
            return current_user

        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return current_user


# Role-based dependency shortcuts
get_moderator_user = RoleChecker([UserRole.moderator, UserRole.admin])
get_admin_user = RoleChecker([UserRole.admin])
