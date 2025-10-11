"""
Security function tests.

Tests for password hashing, JWT token creation/validation, and security utilities.
"""

import pytest
from datetime import timedelta, datetime

from backend.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_access_token,
    verify_refresh_token,
    validate_password_strength,
    generate_api_key,
)
from fastapi import HTTPException


# =============================================================================
# PASSWORD HASHING TESTS
# =============================================================================

def test_hash_password():
    """Test password hashing produces different hashes for same password."""
    password = "TestPassword123!"

    hash1 = hash_password(password)
    hash2 = hash_password(password)

    # Hashes should be different due to random salt
    assert hash1 != hash2
    assert hash1 != password
    assert len(hash1) > 0


def test_verify_password_correct():
    """Test password verification with correct password."""
    password = "SecurePass123!"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_verify_password_incorrect():
    """Test password verification with incorrect password."""
    password = "SecurePass123!"
    wrong_password = "WrongPass123!"
    hashed = hash_password(password)

    assert verify_password(wrong_password, hashed) is False


def test_hash_password_long_password():
    """Test password hashing with long password (bcrypt 72-byte limit)."""
    # Bcrypt has a 72-byte limit, should handle gracefully
    long_password = "A" * 100 + "123!"

    hashed = hash_password(long_password)
    assert verify_password(long_password, hashed) is True


def test_hash_password_unicode():
    """Test password hashing with unicode characters."""
    password = "Pässwörd123!🔐"

    hashed = hash_password(password)
    assert verify_password(password, hashed) is True


# =============================================================================
# PASSWORD STRENGTH VALIDATION TESTS
# =============================================================================

def test_validate_password_strength_valid(valid_passwords: list):
    """Test password strength validation with valid passwords."""
    for password in valid_passwords:
        # Should not raise exception
        result = validate_password_strength(password)
        assert result is True


def test_validate_password_too_short():
    """Test password validation rejects too short passwords."""
    with pytest.raises(ValueError, match="at least .* characters"):
        validate_password_strength("Short1!")


def test_validate_password_no_uppercase():
    """Test password validation rejects passwords without uppercase."""
    with pytest.raises(ValueError, match="uppercase"):
        validate_password_strength("alllowercase123!")


def test_validate_password_no_lowercase():
    """Test password validation rejects passwords without lowercase."""
    with pytest.raises(ValueError, match="lowercase"):
        validate_password_strength("ALLUPPERCASE123!")


def test_validate_password_no_digit():
    """Test password validation rejects passwords without digits."""
    with pytest.raises(ValueError, match="digit"):
        validate_password_strength("NoNumbersHere!")


def test_validate_password_no_special_char():
    """Test password validation rejects passwords without special characters."""
    with pytest.raises(ValueError, match="special character"):
        validate_password_strength("NoSpecialChars123")


def test_validate_password_all_requirements():
    """Test that password must meet all requirements."""
    # Valid password with all requirements
    assert validate_password_strength("Valid123!Pass") is True

    # Missing each requirement
    test_cases = [
        ("short1!", "at least"),           # Too short
        ("alllower123!", "uppercase"),     # No uppercase
        ("ALLUPPER123!", "lowercase"),     # No lowercase
        ("NoDigits!", "digit"),            # No digit
        ("NoSpecial123", "special"),       # No special char
    ]

    for password, expected_error in test_cases:
        with pytest.raises(ValueError, match=expected_error):
            validate_password_strength(password)


# =============================================================================
# JWT TOKEN CREATION TESTS
# =============================================================================

def test_create_access_token():
    """Test JWT access token creation."""
    data = {"user_id": "123", "email": "test@example.com"}

    token = create_access_token(data)

    assert isinstance(token, str)
    assert len(token) > 0

    # Decode and verify
    payload = decode_token(token)
    assert payload["user_id"] == "123"
    assert payload["email"] == "test@example.com"
    assert payload["type"] == "access"
    assert "exp" in payload
    assert "iat" in payload


def test_create_access_token_custom_expiration():
    """Test JWT access token with custom expiration."""
    data = {"user_id": "123"}
    expires_delta = timedelta(minutes=5)

    token = create_access_token(data, expires_delta=expires_delta)

    payload = decode_token(token)
    assert "exp" in payload
    assert "iat" in payload

    # Check that exp is roughly 5 minutes after iat
    exp = datetime.fromtimestamp(payload["exp"])
    iat = datetime.fromtimestamp(payload["iat"])
    actual_delta = (exp - iat).total_seconds()

    # Should be close to 5 minutes (300 seconds)
    expected_seconds = expires_delta.total_seconds()
    assert abs(actual_delta - expected_seconds) < 5  # Within 5 seconds


def test_create_refresh_token():
    """Test JWT refresh token creation."""
    data = {"user_id": "123", "email": "test@example.com"}

    token = create_refresh_token(data)

    assert isinstance(token, str)
    assert len(token) > 0

    # Decode and verify
    payload = decode_token(token)
    assert payload["user_id"] == "123"
    assert payload["email"] == "test@example.com"
    assert payload["type"] == "refresh"
    assert "exp" in payload


def test_tokens_are_different():
    """Test that access and refresh tokens are different for same data."""
    data = {"user_id": "123"}

    access_token = create_access_token(data)
    refresh_token = create_refresh_token(data)

    assert access_token != refresh_token


# =============================================================================
# JWT TOKEN DECODING TESTS
# =============================================================================

def test_decode_token_valid():
    """Test decoding valid JWT token."""
    data = {"user_id": "123", "email": "test@example.com"}
    token = create_access_token(data)

    payload = decode_token(token)

    assert payload["user_id"] == "123"
    assert payload["email"] == "test@example.com"


def test_decode_token_invalid():
    """Test decoding invalid JWT token raises exception."""
    invalid_token = "invalid.token.here"

    with pytest.raises(HTTPException) as exc_info:
        decode_token(invalid_token)

    assert exc_info.value.status_code == 401


def test_decode_token_expired():
    """Test decoding expired JWT token raises exception."""
    data = {"user_id": "123"}
    # Create token that expired 10 seconds ago
    token = create_access_token(data, expires_delta=timedelta(seconds=-10))

    with pytest.raises(HTTPException) as exc_info:
        decode_token(token)

    assert exc_info.value.status_code == 401


def test_decode_token_wrong_secret():
    """Test that token signed with wrong secret fails validation."""
    from jose import jwt

    data = {"user_id": "123"}
    # Sign with wrong secret
    token = jwt.encode(data, "wrong-secret", algorithm="HS256")

    with pytest.raises(HTTPException) as exc_info:
        decode_token(token)

    assert exc_info.value.status_code == 401


# =============================================================================
# TOKEN VERIFICATION TESTS
# =============================================================================

def test_verify_access_token_valid():
    """Test verifying valid access token."""
    data = {"user_id": "123", "email": "test@example.com"}
    token = create_access_token(data)

    payload = verify_access_token(token)

    assert payload["user_id"] == "123"
    assert payload["type"] == "access"


def test_verify_access_token_with_refresh_token():
    """Test that refresh token fails access token verification."""
    data = {"user_id": "123"}
    refresh_token = create_refresh_token(data)

    with pytest.raises(HTTPException) as exc_info:
        verify_access_token(refresh_token)

    assert exc_info.value.status_code == 401
    assert "Invalid token type" in str(exc_info.value.detail)


def test_verify_refresh_token_valid():
    """Test verifying valid refresh token."""
    data = {"user_id": "123", "email": "test@example.com"}
    token = create_refresh_token(data)

    payload = verify_refresh_token(token)

    assert payload["user_id"] == "123"
    assert payload["type"] == "refresh"


def test_verify_refresh_token_with_access_token():
    """Test that access token fails refresh token verification."""
    data = {"user_id": "123"}
    access_token = create_access_token(data)

    with pytest.raises(HTTPException) as exc_info:
        verify_refresh_token(access_token)

    assert exc_info.value.status_code == 401
    assert "Invalid token type" in str(exc_info.value.detail)


# =============================================================================
# TOKEN PAYLOAD TESTS
# =============================================================================

def test_token_contains_issued_at():
    """Test that tokens contain issued at (iat) timestamp."""
    data = {"user_id": "123"}
    token = create_access_token(data)

    payload = decode_token(token)

    assert "iat" in payload
    # Just verify that iat exists and is a valid timestamp
    # Don't compare times directly due to potential timezone issues
    assert isinstance(payload["iat"], int)
    assert payload["iat"] > 0


def test_token_contains_expiration():
    """Test that tokens contain expiration (exp) timestamp."""
    data = {"user_id": "123"}
    token = create_access_token(data)

    payload = decode_token(token)

    assert "exp" in payload
    # Should be in the future
    exp = datetime.fromtimestamp(payload["exp"])
    now = datetime.utcnow()
    assert exp > now


def test_token_preserves_custom_data():
    """Test that tokens preserve all custom data in payload."""
    data = {
        "user_id": "123",
        "email": "test@example.com",
        "role": "admin",
        "custom_field": "custom_value"
    }

    token = create_access_token(data)
    payload = decode_token(token)

    assert payload["user_id"] == "123"
    assert payload["email"] == "test@example.com"
    assert payload["role"] == "admin"
    assert payload["custom_field"] == "custom_value"


# =============================================================================
# API KEY TESTS
# =============================================================================

def test_generate_api_key():
    """Test API key generation."""
    key1 = generate_api_key()
    key2 = generate_api_key()

    # Keys should be different
    assert key1 != key2

    # Keys should be 64 characters (32 bytes hex)
    assert len(key1) == 64
    assert len(key2) == 64

    # Keys should be hexadecimal
    assert all(c in "0123456789abcdef" for c in key1)
    assert all(c in "0123456789abcdef" for c in key2)


# =============================================================================
# SECURITY EDGE CASES
# =============================================================================

def test_empty_password():
    """Test handling of empty password."""
    with pytest.raises(ValueError):
        validate_password_strength("")


def test_whitespace_only_password():
    """Test that whitespace-only passwords are rejected."""
    with pytest.raises(ValueError):
        validate_password_strength("        ")


def test_password_with_spaces():
    """Test that passwords with spaces are allowed if they meet requirements."""
    password = "Valid Password 123!"

    # Should be valid
    assert validate_password_strength(password) is True

    # Should hash and verify correctly
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True


def test_token_without_type_field():
    """Test handling of tokens without type field (legacy tokens)."""
    from jose import jwt
    from backend.core.config import settings

    # Create token without type field
    data = {"user_id": "123", "exp": datetime.utcnow() + timedelta(minutes=30)}
    token = jwt.encode(data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    # decode_token should work
    payload = decode_token(token)
    assert payload["user_id"] == "123"

    # But verify_access_token should fail (no type field)
    with pytest.raises(HTTPException):
        verify_access_token(token)


def test_multiple_password_hashing_rounds():
    """Test that hashing the same password multiple times produces different hashes."""
    password = "TestPassword123!"

    hashes = [hash_password(password) for _ in range(5)]

    # All hashes should be unique
    assert len(set(hashes)) == 5

    # But all should verify correctly
    for hashed in hashes:
        assert verify_password(password, hashed) is True
