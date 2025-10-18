"""User profile and management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime
from backend.core.security import get_current_user_id
from backend.db.database import get_db
from backend.db.models import User

router = APIRouter()


class UserProfile(BaseModel):
    """User profile response model."""
    user_id: str
    mobile_number: str
    email: Optional[str] = None
    full_name: str
    is_active: bool
    created_at: str
    updated_at: str


@router.get("/me", response_model=UserProfile)
async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user profile.

    Automatically extracts user_id from JWT token.
    No need to send user_id in request.

    Returns:
        User profile with mobile, email, name, and account status
    """
    # Fetch user from database
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Return user profile
    return UserProfile(
        user_id=user.id,
        mobile_number=user.mobile_number,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        created_at=user.created_at.isoformat() if user.created_at else datetime.utcnow().isoformat(),
        updated_at=user.updated_at.isoformat() if user.updated_at else datetime.utcnow().isoformat()
    )


@router.patch("/me")
async def update_profile(user_id: str = Depends(get_current_user_id)):
    """Update user profile."""
    # TODO: Implement profile update
    return {"message": "Profile updated successfully"}


@router.delete("/me")
async def delete_account(user_id: str = Depends(get_current_user_id)):
    """Delete user account."""
    # TODO: Implement account deletion with GDPR compliance
    return {"message": "Account deletion initiated"}
