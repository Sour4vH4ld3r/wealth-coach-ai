"""User profile and management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from backend.core.security import get_current_user_id

router = APIRouter()


class UserProfile(BaseModel):
    """User profile model."""
    user_id: str
    email: EmailStr
    full_name: str
    created_at: Optional[str] = None


@router.get("/me", response_model=UserProfile)
async def get_current_user(user_id: str = Depends(get_current_user_id)):
    """Get current user profile."""
    # TODO: Fetch from database
    return UserProfile(
        user_id=user_id,
        email=f"{user_id}@example.com",
        full_name="Demo User",
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
