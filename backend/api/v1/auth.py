"""
Authentication endpoints for user registration, login, and token management.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import timedelta
from sqlalchemy.orm import Session

from backend.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    validate_password_strength,
)
from backend.core.config import settings
from backend.db.database import get_db
from backend.db.models import User
from backend.services.cache.redis_client import RedisClient
from backend.core.dependencies import get_redis_client
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class UserRegistration(BaseModel):
    """User registration request model."""
    email: EmailStr
    password: str = Field(min_length=settings.PASSWORD_MIN_LENGTH)
    full_name: str = Field(min_length=2, max_length=100)


class UserLogin(BaseModel):
    """User login request model."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Authentication token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class RefreshTokenRequest(BaseModel):
    """Refresh token request model."""
    refresh_token: str


# =============================================================================
# AUTHENTICATION ENDPOINTS
# =============================================================================

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegistration, db: Session = Depends(get_db)):
    """
    Register a new user account.

    Creates a new user with hashed password and returns authentication tokens.

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        Access and refresh tokens

    Raises:
        HTTPException: If email already exists or password is weak
    """
    if not settings.ENABLE_USER_REGISTRATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User registration is currently disabled",
        )

    # Validate password strength
    try:
        validate_password_strength(user_data.password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Hash password
    hashed_password = hash_password(user_data.password)

    # Create new user
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate tokens
    token_data = {"user_id": new_user.id, "email": new_user.email}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
    redis: RedisClient = Depends(get_redis_client)
):
    """
    Authenticate user and return tokens.

    Validates email/password and returns access and refresh tokens.

    Args:
        credentials: User login credentials
        db: Database session
        redis: Redis client for rate limiting

    Returns:
        Access and refresh tokens

    Raises:
        HTTPException: If credentials are invalid or account is locked
    """
    # Check for account lockout
    lockout_key = f"login_attempts:{credentials.email}"

    try:
        attempts_str = await redis.get(lockout_key)
        attempts = int(attempts_str) if attempts_str else 0

        if attempts >= 5:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Account temporarily locked due to too many failed login attempts. Try again in 15 minutes.",
            )
    except Exception as e:
        # Continue if Redis is unavailable
        logger.warning(f"Redis unavailable for lockout check: {e}")

    # Fetch user from database by email
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user:
        # Increment failed attempts
        try:
            await redis.incr(lockout_key)
            await redis.expire(lockout_key, 900)  # 15 minute lockout
        except Exception:
            pass

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        # Increment failed attempts
        try:
            await redis.incr(lockout_key)
            await redis.expire(lockout_key, 900)  # 15 minute lockout
        except Exception:
            pass

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been deactivated",
        )

    # Successful login - clear failed attempts
    try:
        await redis.delete(lockout_key)
    except Exception:
        pass

    # Generate tokens
    token_data = {"user_id": user.id, "email": user.email}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token.

    Validates refresh token and issues new access token.

    Args:
        request: Refresh token request

    Returns:
        New access and refresh tokens

    Raises:
        HTTPException: If refresh token is invalid
    """
    # Verify refresh token
    payload = verify_refresh_token(request.refresh_token)

    # Extract user data
    user_id = payload.get("user_id")
    email = payload.get("email")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token payload",
        )

    # Generate new tokens
    token_data = {"user_id": user_id, "email": email}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout")
async def logout():
    """
    Logout user (placeholder for token blacklisting).

    In a production system, this would:
    1. Add token to blacklist in Redis
    2. Clear user session data
    3. Revoke refresh token

    Returns:
        Success message
    """
    # TODO: Implement token blacklisting in Redis
    # await redis.sadd(f"blacklist:tokens", token)

    return {"message": "Successfully logged out"}
