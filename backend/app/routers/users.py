from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.schemas import UserResponse, UserUpdate
from app.core.dependencies import get_current_user
from app.core.security import hash_password

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
)
async def get_me(current_user: User = Depends(get_current_user)) -> User:
    """Return the profile data of the currently authenticated user."""
    return current_user


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user profile",
)
async def update_me(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Update profile information for the authenticated user."""
    # Update fields
    if user_in.display_name is not None:
        current_user.display_name = user_in.display_name
    if user_in.avatar_url is not None:
        current_user.avatar_url = user_in.avatar_url
    if user_in.bio is not None:
        current_user.bio = user_in.bio
    if user_in.password is not None:
        current_user.password_hash = hash_password(user_in.password)

    db.add(current_user)
    await db.flush()
    return current_user
