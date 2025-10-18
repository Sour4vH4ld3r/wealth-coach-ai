"""
Authentication endpoints for user registration, login, and token management.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import timedelta
from sqlalchemy.orm import Session
import httpx
import random
import string

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
    mobile_number: str = Field(pattern=r"^\d{10}$", description="10-digit mobile number")
    email: Optional[EmailStr] = None
    password: str = Field(min_length=settings.PASSWORD_MIN_LENGTH)
    full_name: str = Field(min_length=2, max_length=100)


class UserLogin(BaseModel):
    """User login request model."""
    mobile_number: str = Field(pattern=r"^\d{10}$", description="10-digit mobile number")
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


class SendOTPRequest(BaseModel):
    """Send OTP request model."""
    mobile_number: str = Field(pattern=r"^\d{10}$", description="10-digit mobile number")


class VerifyOTPRequest(BaseModel):
    """Verify OTP request model."""
    mobile_number: str = Field(pattern=r"^\d{10}$", description="10-digit mobile number")
    otp: str = Field(min_length=6, max_length=6, description="6-digit OTP")


class OTPResponse(BaseModel):
    """OTP response model."""
    success: bool
    message: str


# =============================================================================
# AUTHENTICATION ENDPOINTS
# =============================================================================

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegistration, db: Session = Depends(get_db)):
    """
    Register a new user account.

    Creates a new user with hashed password and returns authentication tokens.

    Args:
        user_data: User registration data (mobile_number required, email optional)
        db: Database session

    Returns:
        Access and refresh tokens

    Raises:
        HTTPException: If mobile number/email already exists or password is weak
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

    # Check if mobile number already exists
    existing_mobile = db.query(User).filter(User.mobile_number == user_data.mobile_number).first()
    if existing_mobile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mobile number already registered",
        )

    # Check if email already exists (if provided)
    if user_data.email:
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    # Hash password
    hashed_password = hash_password(user_data.password)

    # Create new user
    new_user = User(
        mobile_number=user_data.mobile_number,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate tokens
    token_data = {
        "user_id": new_user.id,
        "mobile_number": new_user.mobile_number,
        "email": new_user.email
    }
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
    Authenticate user with mobile number and password.

    Validates mobile_number/password and returns access and refresh tokens.

    Args:
        credentials: User login credentials (mobile_number + password)
        db: Database session
        redis: Redis client for rate limiting

    Returns:
        Access and refresh tokens

    Raises:
        HTTPException: If credentials are invalid or account is locked
    """
    # Check for account lockout
    lockout_key = f"login_attempts:{credentials.mobile_number}"

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

    # Fetch user from database by mobile number
    user = db.query(User).filter(User.mobile_number == credentials.mobile_number).first()

    if not user:
        # Increment failed attempts
        try:
            await redis.incr(lockout_key)
            await redis.expire(lockout_key, 900)  # 15 minute lockout
        except Exception:
            pass

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid mobile number or password",
        )

    # Verify password
    if not user.hashed_password or not verify_password(credentials.password, user.hashed_password):
        # Increment failed attempts
        try:
            await redis.incr(lockout_key)
            await redis.expire(lockout_key, 900)  # 15 minute lockout
        except Exception:
            pass

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid mobile number or password",
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
    token_data = {
        "user_id": user.id,
        "mobile_number": user.mobile_number,
        "email": user.email
    }
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/login-otp", response_model=TokenResponse)
async def login_otp(
    request: VerifyOTPRequest,
    db: Session = Depends(get_db),
    redis: RedisClient = Depends(get_redis_client)
):
    """
    Authenticate user with mobile number and OTP.

    Validates OTP from Redis and returns access and refresh tokens.

    Args:
        request: Mobile number and OTP
        db: Database session
        redis: Redis client for OTP verification

    Returns:
        Access and refresh tokens

    Raises:
        HTTPException: If OTP is invalid, expired, or user doesn't exist
    """
    try:
        # Check if user exists in database
        user = db.query(User).filter(User.mobile_number == request.mobile_number).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found. Please register first.",
            )

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account has been deactivated",
            )

        # Retrieve OTP from Redis
        redis_key = f"otp:{request.mobile_number}"
        stored_otp = await redis.get(redis_key)

        logger.info(f"🔍 [Login-OTP] Verifying OTP for {request.mobile_number}")

        if not stored_otp:
            logger.warning(f"❌ [Login-OTP] OTP not found or expired for {request.mobile_number}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="OTP expired or not found. Please request a new OTP.",
            )

        # Verify OTP - handle both bytes and string from Redis
        if isinstance(stored_otp, bytes):
            stored_otp_str = stored_otp.decode('utf-8')
        else:
            stored_otp_str = str(stored_otp)

        logger.info(f"🔐 [Login-OTP] Comparing OTP - Entered: {request.otp}, Stored: {stored_otp_str}")

        if stored_otp_str != request.otp:
            logger.warning(f"❌ [Login-OTP] Invalid OTP for {request.mobile_number}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid OTP. Please check and try again.",
            )

        # OTP verified successfully - delete from Redis
        await redis.delete(redis_key)

        logger.info(f"✅ [Login-OTP] OTP verified successfully for {request.mobile_number}")

        # Generate tokens
        token_data = {
            "user_id": user.id,
            "mobile_number": user.mobile_number,
            "email": user.email
        }
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"❌ [Login-OTP] Error during OTP login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify OTP. Please try again.",
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


# =============================================================================
# MOBILE NUMBER & PASSWORD UTILITIES
# =============================================================================

class CheckMobileRequest(BaseModel):
    """Check mobile number request model."""
    mobile_number: str = Field(pattern=r"^\d{10}$", description="10-digit mobile number")


class CheckMobileResponse(BaseModel):
    """Check mobile number response model."""
    exists: bool
    message: str


class PasswordRequirements(BaseModel):
    """Password requirements response model."""
    min_length: int
    requires_uppercase: bool
    requires_lowercase: bool
    requires_digit: bool
    requires_special: bool
    special_characters: str


@router.post("/check-mobile", response_model=CheckMobileResponse)
async def check_mobile(request: CheckMobileRequest, db: Session = Depends(get_db)):
    """
    Check if mobile number exists in database.

    Used by login and registration flows to validate mobile number existence.

    Args:
        request: Mobile number to check
        db: Database session

    Returns:
        exists status and message
    """
    user = db.query(User).filter(User.mobile_number == request.mobile_number).first()

    if user:
        return CheckMobileResponse(
            exists=True,
            message=f"Mobile number {request.mobile_number} is registered"
        )
    else:
        return CheckMobileResponse(
            exists=False,
            message=f"Mobile number {request.mobile_number} is not registered"
        )


@router.get("/password-requirements", response_model=PasswordRequirements)
async def get_password_requirements():
    """
    Get password strength requirements.

    Returns:
        Password requirements including minimum length and character requirements
    """
    return PasswordRequirements(
        min_length=settings.PASSWORD_MIN_LENGTH,
        requires_uppercase=True,
        requires_lowercase=True,
        requires_digit=True,
        requires_special=True,
        special_characters="!@#$%^&*()_+-=[]{}|;:,.<>?"
    )


# =============================================================================
# OTP ENDPOINTS
# =============================================================================

def generate_otp(length: int = 6) -> str:
    """Generate a random numeric OTP."""
    return ''.join(random.choices(string.digits, k=length))


@router.post("/send-otp", response_model=OTPResponse)
async def send_otp(
    request: SendOTPRequest,
    redis: RedisClient = Depends(get_redis_client)
):
    """
    Send OTP to mobile number via BulkSMS gateway.

    Args:
        request: Mobile number to send OTP to
        redis: Redis client for storing OTP

    Returns:
        Success status and message

    Raises:
        HTTPException: If SMS sending fails
    """
    try:
        # Generate 6-digit OTP
        otp = generate_otp(6)

        # BulkSMS API configuration
        sms_url = "http://sms.bulksmsind.in/v2/sendSMS"
        sms_params = {
            "username": "myfighters",
            "message": f"{otp} is your WealthwarriorsHub verification code .SUBVRF",
            "sendername": "SUBVRF",
            "smstype": "TRANS",
            "numbers": request.mobile_number,
            "apikey": "4ea8c19a-1dea-4b9a-b559-bbecbe99d0b4",
            "peid": "1501465730000042566",
            "templateid": "1507165519281578180"
        }

        # Send SMS via BulkSMS gateway
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(sms_url, params=sms_params)

        if response.status_code != 200:
            logger.error(f"SMS gateway error: {response.status_code} - {response.text}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send OTP. Please try again."
            )

        # Store OTP in Redis with 5 minute expiry
        redis_key = f"otp:{request.mobile_number}"
        await redis.set(redis_key, otp, ex=300)  # 5 minutes

        # Log OTP only in development mode (NEVER in production)
        if settings.DEBUG:
            logger.info(f"✅ [DEV] OTP sent to {request.mobile_number} | OTP: {otp}")
        else:
            logger.info(f"✅ OTP sent to {request.mobile_number}")

        return OTPResponse(
            success=True,
            message=f"OTP sent successfully to {request.mobile_number}. Valid for 5 minutes."
        )

    except httpx.TimeoutException:
        logger.error("SMS gateway timeout")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="SMS gateway timeout. Please try again."
        )
    except Exception as e:
        logger.error(f"Error sending OTP: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP. Please try again."
        )


@router.post("/verify-otp", response_model=OTPResponse)
async def verify_otp(
    request: VerifyOTPRequest,
    redis: RedisClient = Depends(get_redis_client)
):
    """
    Verify OTP for mobile number.

    Args:
        request: Mobile number and OTP to verify
        redis: Redis client for retrieving stored OTP

    Returns:
        Success status and message

    Raises:
        HTTPException: If OTP is invalid or expired
    """
    try:
        # Retrieve OTP from Redis
        redis_key = f"otp:{request.mobile_number}"
        stored_otp = await redis.get(redis_key)

        logger.info(f"🔍 Verifying OTP for {request.mobile_number}")

        if not stored_otp:
            logger.warning(f"❌ OTP not found or expired for {request.mobile_number}")
            return OTPResponse(
                success=False,
                message="OTP expired or not found. Please request a new OTP."
            )

        # Verify OTP - handle both bytes and string from Redis
        if isinstance(stored_otp, bytes):
            stored_otp_str = stored_otp.decode('utf-8')
        else:
            stored_otp_str = str(stored_otp)

        logger.info(f"🔐 Comparing OTP - Entered: {request.otp}, Stored: {stored_otp_str}")

        if stored_otp_str != request.otp:
            logger.warning(f"❌ Invalid OTP for {request.mobile_number}")
            return OTPResponse(
                success=False,
                message="Invalid OTP. Please check and try again."
            )

        # OTP verified successfully - delete from Redis
        await redis.delete(redis_key)

        logger.info(f"✅ OTP verified successfully for {request.mobile_number}")

        return OTPResponse(
            success=True,
            message=f"Mobile number {request.mobile_number} verified successfully!"
        )

    except Exception as e:
        logger.error(f"❌ Error verifying OTP: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify OTP. Please try again."
        )
