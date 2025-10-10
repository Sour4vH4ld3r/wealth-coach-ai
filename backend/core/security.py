"""
Security utilities for authentication, encryption, and token management.

Implements JWT token generation/validation and password hashing using industry
best practices (bcrypt with secure defaults).
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
import bcrypt
from fastapi import HTTPException, status, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.core.config import settings

# Note: Using bcrypt directly instead of passlib to avoid initialization issues
# with password length validation during library setup

# HTTP Bearer token scheme for OpenAPI docs
security_scheme = HTTPBearer()


# =============================================================================
# PASSWORD HASHING
# =============================================================================

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Automatically truncates passwords longer than 72 bytes to comply with bcrypt limitations.

    Args:
        password: Plain text password

    Returns:
        Hashed password string (bcrypt hash)
    """
    # Bcrypt has a strict 72 byte password limit
    # Always truncate to 72 bytes to prevent errors
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]

    # Generate salt and hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)

    # Return as string (decode bytes to string)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Applies same truncation as hash_password for consistency.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Previously hashed password (bcrypt hash)

    Returns:
        True if password matches, False otherwise
    """
    # Apply same 72-byte truncation as in hash_password
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]

    # Convert hashed password to bytes if it's a string
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')

    # Verify using bcrypt
    return bcrypt.checkpw(password_bytes, hashed_password)


# =============================================================================
# JWT TOKEN MANAGEMENT
# =============================================================================

def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.

    Args:
        data: Payload data to encode in token (e.g., user_id, email)
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT refresh token with longer expiration.

    Args:
        data: Payload data to encode in token

    Returns:
        Encoded JWT refresh token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token string to decode

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_access_token(token: str) -> Dict[str, Any]:
    """
    Verify that a token is a valid access token.

    Args:
        token: JWT token to verify

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid, expired, or not an access token
    """
    payload = decode_token(token)

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    return payload


def verify_refresh_token(token: str) -> Dict[str, Any]:
    """
    Verify that a token is a valid refresh token.

    Args:
        token: JWT token to verify

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid, expired, or not a refresh token
    """
    payload = decode_token(token)

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    return payload


# =============================================================================
# API KEY AUTHENTICATION
# =============================================================================

def verify_api_key(x_api_key: str = Header(None)) -> str:
    """
    Verify API key from request header.

    Args:
        x_api_key: API key from X-API-Key header

    Returns:
        Validated API key

    Raises:
        HTTPException: If API key is missing or invalid
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key missing",
        )

    if x_api_key not in settings.VALID_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    return x_api_key


# =============================================================================
# FASTAPI DEPENDENCIES
# =============================================================================

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme)
) -> str:
    """
    FastAPI dependency to extract user ID from JWT token.

    Usage:
        @app.get("/protected")
        async def protected_route(user_id: str = Depends(get_current_user_id)):
            return {"user_id": user_id}

    Args:
        credentials: JWT credentials from Authorization header

    Returns:
        User ID from token payload

    Raises:
        HTTPException: If token is invalid or user_id is missing
    """
    token = credentials.credentials
    payload = verify_access_token(token)

    user_id: str = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    return user_id


async def get_optional_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)
) -> Optional[str]:
    """
    FastAPI dependency for optional authentication.

    Returns user_id if valid token provided, None otherwise.
    Useful for endpoints that work with or without authentication.

    Args:
        credentials: Optional JWT credentials

    Returns:
        User ID if authenticated, None otherwise
    """
    if not credentials:
        return None

    try:
        token = credentials.credentials
        payload = verify_access_token(token)
        return payload.get("user_id")
    except HTTPException:
        return None


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def validate_password_strength(password: str) -> bool:
    """
    Validate password meets minimum security requirements.

    Requirements:
    - Minimum length (configurable)
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character

    Note: The 72-byte bcrypt limitation is automatically handled by hash_password()

    Args:
        password: Password to validate

    Returns:
        True if valid, raises ValueError otherwise
    """
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        raise ValueError(
            f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters"
        )

    # Note: Removed 72-byte check - now handled automatically in hash_password()

    if not any(c.isupper() for c in password):
        raise ValueError("Password must contain at least one uppercase letter")

    if not any(c.islower() for c in password):
        raise ValueError("Password must contain at least one lowercase letter")

    if not any(c.isdigit() for c in password):
        raise ValueError("Password must contain at least one digit")

    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        raise ValueError("Password must contain at least one special character")

    return True


def generate_api_key() -> str:
    """
    Generate a secure random API key.

    Returns:
        32-character hexadecimal API key
    """
    import secrets
    return secrets.token_hex(32)
