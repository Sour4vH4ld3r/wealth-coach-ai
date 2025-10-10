"""
Onboarding API endpoints for collecting user profile information.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from backend.db.database import get_db
from backend.db.models import UserProfile
from backend.core.security import get_current_user_id

router = APIRouter()


class OnboardingData(BaseModel):
    """Onboarding questionnaire data."""

    age_range: Optional[str] = Field(None, description="Age range (e.g., '25-34')")
    occupation: Optional[str] = Field(None, description="Job/profession")
    income_range: Optional[str] = Field(None, description="Income range (e.g., '$50k-$75k')")
    financial_goals: Optional[str] = Field(None, description="Comma-separated financial goals")
    investment_experience: Optional[str] = Field(None, description="beginner/intermediate/advanced")
    risk_tolerance: Optional[str] = Field(None, description="low/medium/high")
    current_investments: Optional[str] = Field(None, description="Current investments")
    debt_status: Optional[str] = Field(None, description="none/some/significant")
    retirement_planning: Optional[bool] = Field(False, description="Interested in retirement planning")
    interests: Optional[str] = Field(None, description="Other financial interests")


class OnboardingResponse(BaseModel):
    """Response after onboarding submission."""

    message: str
    profile_completed: bool
    user_id: str


@router.post("/submit", response_model=OnboardingResponse)
async def submit_onboarding(
    data: OnboardingData,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Submit user onboarding data.

    This endpoint saves the user's profile information collected during onboarding.
    This data will be used to personalize AI responses.
    """

    # Check if profile already exists
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    if profile:
        # Update existing profile
        profile.age_range = data.age_range
        profile.occupation = data.occupation
        profile.income_range = data.income_range
        profile.financial_goals = data.financial_goals
        profile.investment_experience = data.investment_experience
        profile.risk_tolerance = data.risk_tolerance
        profile.current_investments = data.current_investments
        profile.debt_status = data.debt_status
        profile.retirement_planning = data.retirement_planning
        profile.interests = data.interests
        profile.onboarding_completed = True
        profile.onboarding_completed_at = datetime.utcnow()
        profile.updated_at = datetime.utcnow()
    else:
        # Create new profile
        profile = UserProfile(
            user_id=user_id,
            age_range=data.age_range,
            occupation=data.occupation,
            income_range=data.income_range,
            financial_goals=data.financial_goals,
            investment_experience=data.investment_experience,
            risk_tolerance=data.risk_tolerance,
            current_investments=data.current_investments,
            debt_status=data.debt_status,
            retirement_planning=data.retirement_planning,
            interests=data.interests,
            onboarding_completed=True,
            onboarding_completed_at=datetime.utcnow()
        )
        db.add(profile)

    db.commit()
    db.refresh(profile)

    return OnboardingResponse(
        message="Onboarding completed successfully! Your profile will help me provide better financial advice.",
        profile_completed=True,
        user_id=user_id
    )


@router.get("/status")
async def get_onboarding_status(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Check if user has completed onboarding.

    Returns whether the user needs to complete onboarding.
    """

    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    if not profile:
        return {
            "onboarding_completed": False,
            "message": "Please complete your profile to get personalized financial advice"
        }

    return {
        "onboarding_completed": profile.onboarding_completed,
        "completed_at": profile.onboarding_completed_at.isoformat() if profile.onboarding_completed_at else None
    }


@router.get("/profile")
async def get_user_profile(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get user's profile data.

    Returns the user's onboarding information.
    """

    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please complete onboarding first."
        )

    return {
        "age_range": profile.age_range,
        "occupation": profile.occupation,
        "income_range": profile.income_range,
        "financial_goals": profile.financial_goals,
        "investment_experience": profile.investment_experience,
        "risk_tolerance": profile.risk_tolerance,
        "current_investments": profile.current_investments,
        "debt_status": profile.debt_status,
        "retirement_planning": profile.retirement_planning,
        "interests": profile.interests,
        "onboarding_completed": profile.onboarding_completed,
        "completed_at": profile.onboarding_completed_at.isoformat() if profile.onboarding_completed_at else None
    }
