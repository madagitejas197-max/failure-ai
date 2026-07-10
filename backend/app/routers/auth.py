from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import User, UserRole
from app.schemas import Token, UserCreate, UserResponse, LoginRequest, RefreshRequest
from app.core.security import hash_password, verify_password, create_jwt_token, decode_jwt_token
from app.core.dependencies import get_current_user
from jose import jwt

router = APIRouter(prefix="/auth")


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    """Create a new user account with hashed password."""
    # Check if email is already taken
    result = await db.execute(select(User).filter(User.email == user_in.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )

    # Hash the password and save
    hashed_pwd = hash_password(user_in.password)
    user = User(
        email=user_in.email,
        password_hash=hashed_pwd,
        display_name=user_in.display_name,
        role=UserRole.user,
    )
    db.add(user)
    await db.flush()  # get generated UUID
    return user


@router.post(
    "/login",
    response_model=Token,
    summary="Log in user",
)
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """
    Log in user and issue access and refresh tokens.
    Accepts LoginRequest in the JSON request body.
    """
    email = credentials.email
    password = credentials.password

    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalars().first()

    if not user or not user.password_hash or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Issue JWTs
    access_token = create_jwt_token(subject=user.id, token_type="access")
    refresh_token = create_jwt_token(subject=user.id, token_type="refresh")

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post(
    "/refresh",
    response_model=Token,
    summary="Exchange refresh token for a new access token",
)
async def refresh(refresh_in: RefreshRequest, db: AsyncSession = Depends(get_db)) -> Token:
    """Verify refresh token and issue new access & refresh tokens."""
    try:
        payload = decode_jwt_token(refresh_in.refresh_token)
        user_id_str = payload.get("sub")
        token_type = payload.get("type")

        if not user_id_str or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Get user
    result = await db.execute(select(User).filter(User.id == user_id_str))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Issue new token pair
    access_token = create_jwt_token(subject=user.id, token_type="access")
    new_refresh_token = create_jwt_token(subject=user.id, token_type="refresh")

    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
    )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Log out / invalidate tokens",
)
async def logout(current_user: User = Depends(get_current_user)):
    """Log out the current user (stateless logout confirmation)."""
    return {"message": "Successfully logged out"}
