"""Investment allocation endpoints for budget and spending tracking."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import and_
from datetime import datetime
from decimal import Decimal
import json
from backend.core.security import get_current_user_id
from backend.db.database import get_db
from backend.db.models import AllocationCategory, AllocationType, UserAllocation, MonthlyBudget, Transaction
from backend.core.dependencies import get_redis_client

router = APIRouter()

# Cache TTL in seconds (2 minutes)
CACHE_TTL = 120


class AllocationTypeResponse(BaseModel):
    """Investment type response model."""
    id: str
    name: str
    description: Optional[str] = None
    purpose: Optional[str] = None
    sort_order: int
    budget_amount: Decimal = Field(default=Decimal("0.00"))
    actual_amount: Decimal = Field(default=Decimal("0.00"))
    difference: Decimal = Field(default=Decimal("0.00"))

    class Config:
        from_attributes = True


class AllocationCategoryResponse(BaseModel):
    """Allocation category response model."""
    id: str
    name: str
    label: str
    icon: str
    icon_color: str
    description: Optional[str] = None
    target_percentage: Decimal
    sort_order: int
    total_budget: Decimal = Field(default=Decimal("0.00"))
    total_actual: Decimal = Field(default=Decimal("0.00"))
    total_difference: Decimal = Field(default=Decimal("0.00"))
    allocation_types: List[AllocationTypeResponse] = []

    class Config:
        from_attributes = True


class AllocationSummaryResponse(BaseModel):
    """Summary of all allocations."""
    month: int
    year: int
    total_budget: Decimal
    total_actual: Decimal
    total_difference: Decimal
    target_allocation_percentage: Decimal
    categories: List[AllocationCategoryResponse]


@router.get("/allocations", response_model=AllocationSummaryResponse)
async def get_all_allocations(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get all allocation categories with their investment types and user's budget/actual data.

    Returns complete allocation breakdown for current month:
    - All 6 categories (Freedom, Health, Spending, Learning, Entertainment, Contribution)
    - Investment types under each category
    - User's budget and actual amounts
    - Calculated differences and totals

    ⚡ Cached for 2 minutes for better performance
    """
    # Use current month/year
    now = datetime.utcnow()
    month = now.month
    year = now.year

    # Try to get from cache first
    cache_key = f"allocations:{user_id}:{year}:{month}"
    redis_client = get_redis_client()

    try:
        cached_data = redis_client.get(cache_key)
        if cached_data:
            # Return cached response
            return AllocationSummaryResponse(**json.loads(cached_data))
    except Exception:
        # If Redis fails, continue with database query
        pass

    # Fetch all categories with their types
    categories = db.query(AllocationCategory).order_by(AllocationCategory.sort_order).all()

    if not categories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No allocation categories found. Please seed the database."
        )

    # Build response
    category_responses = []
    grand_total_budget = Decimal("0.00")
    grand_total_actual = Decimal("0.00")
    total_target_percentage = Decimal("0.00")

    for category in categories:
        # Fetch allocation types for this category
        allocation_types = db.query(AllocationType).filter(
            AllocationType.category_id == category.id
        ).order_by(AllocationType.sort_order).all()

        type_responses = []
        category_total_budget = Decimal("0.00")
        category_total_actual = Decimal("0.00")

        for alloc_type in allocation_types:
            # Fetch user's allocation data for this type
            user_alloc = db.query(UserAllocation).filter(
                and_(
                    UserAllocation.user_id == user_id,
                    UserAllocation.allocation_type_id == alloc_type.id,
                    UserAllocation.month == month,
                    UserAllocation.year == year
                )
            ).first()

            budget = user_alloc.budget_amount if user_alloc else Decimal("0.00")
            actual = user_alloc.actual_amount if user_alloc else Decimal("0.00")
            difference = budget - actual

            type_responses.append(AllocationTypeResponse(
                id=alloc_type.id,
                name=alloc_type.name,
                description=alloc_type.description,
                purpose=alloc_type.purpose,
                sort_order=alloc_type.sort_order,
                budget_amount=budget,
                actual_amount=actual,
                difference=difference
            ))

            category_total_budget += budget
            category_total_actual += actual

        category_difference = category_total_budget - category_total_actual

        category_responses.append(AllocationCategoryResponse(
            id=category.id,
            name=category.name,
            label=category.label,
            icon=category.icon,
            icon_color=category.icon_color,
            description=category.description,
            target_percentage=category.target_percentage,
            sort_order=category.sort_order,
            total_budget=category_total_budget,
            total_actual=category_total_actual,
            total_difference=category_difference,
            allocation_types=type_responses
        ))

        grand_total_budget += category_total_budget
        grand_total_actual += category_total_actual
        total_target_percentage += category.target_percentage

    grand_total_difference = grand_total_budget - grand_total_actual

    response = AllocationSummaryResponse(
        month=month,
        year=year,
        total_budget=grand_total_budget,
        total_actual=grand_total_actual,
        total_difference=grand_total_difference,
        target_allocation_percentage=total_target_percentage,
        categories=category_responses
    )

    # Cache the response for future requests
    try:
        redis_client.setex(
            cache_key,
            CACHE_TTL,
            response.model_dump_json()
        )
    except Exception:
        # If caching fails, still return the response
        pass

    return response


@router.get("/allocations/summary")
async def get_summary(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get monthly summary with analytics."""
    now = datetime.utcnow()

    allocations = db.query(UserAllocation).filter(
        and_(
            UserAllocation.user_id == user_id,
            UserAllocation.month == now.month,
            UserAllocation.year == now.year
        )
    ).all()

    total_budget = sum(a.budget_amount for a in allocations)
    total_actual = sum(a.actual_amount for a in allocations)

    return {
        "month": now.month,
        "year": now.year,
        "total_budget": total_budget,
        "total_actual": total_actual,
        "difference": total_budget - total_actual,
        "on_track": total_actual <= total_budget,
        "utilization_percentage": float(total_actual / total_budget * 100) if total_budget > 0 else 0
    }


@router.get("/allocations/history")
async def get_history(
    months: int = Query(6, ge=1, le=12),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get historical allocation data."""
    now = datetime.utcnow()
    history = []

    for i in range(months):
        month = now.month - i
        year = now.year

        if month <= 0:
            month += 12
            year -= 1

        allocations = db.query(UserAllocation).filter(
            and_(
                UserAllocation.user_id == user_id,
                UserAllocation.month == month,
                UserAllocation.year == year
            )
        ).all()

        total_budget = sum(a.budget_amount for a in allocations)
        total_actual = sum(a.actual_amount for a in allocations)

        history.append({
            "month": month,
            "year": year,
            "total_budget": total_budget,
            "total_actual": total_actual,
            "difference": total_budget - total_actual
        })

    return {"history": history}


@router.get("/allocations/{allocation_id}", response_model=AllocationCategoryResponse)
async def get_allocation_by_id(
    allocation_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get a specific allocation category by ID with all investment types and user data.

    Path Parameters:
        - allocation_id: Category ID (UUID from database)

    Returns:
        - Category details
        - All investment types under the category
        - User's budget and actual amounts for each type (current month)
        - Calculated totals and differences
    """
    # Use current month/year
    now = datetime.utcnow()
    month = now.month
    year = now.year

    # Fetch the category
    category = db.query(AllocationCategory).filter(AllocationCategory.id == allocation_id).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Allocation category with id '{allocation_id}' not found"
        )

    # Fetch allocation types for this category
    allocation_types = db.query(AllocationType).filter(
        AllocationType.category_id == category.id
    ).order_by(AllocationType.sort_order).all()

    type_responses = []
    category_total_budget = Decimal("0.00")
    category_total_actual = Decimal("0.00")

    for alloc_type in allocation_types:
        # Fetch user's allocation data for this type
        user_alloc = db.query(UserAllocation).filter(
            and_(
                UserAllocation.user_id == user_id,
                UserAllocation.allocation_type_id == alloc_type.id,
                UserAllocation.month == month,
                UserAllocation.year == year
            )
        ).first()

        budget = user_alloc.budget_amount if user_alloc else Decimal("0.00")
        actual = user_alloc.actual_amount if user_alloc else Decimal("0.00")
        difference = budget - actual

        type_responses.append(AllocationTypeResponse(
            id=alloc_type.id,
            name=alloc_type.name,
            description=alloc_type.description,
            purpose=alloc_type.purpose,
            sort_order=alloc_type.sort_order,
            budget_amount=budget,
            actual_amount=actual,
            difference=difference
        ))

        category_total_budget += budget
        category_total_actual += actual

    category_difference = category_total_budget - category_total_actual

    return AllocationCategoryResponse(
        id=category.id,
        name=category.name,
        label=category.label,
        icon=category.icon,
        icon_color=category.icon_color,
        description=category.description,
        target_percentage=category.target_percentage,
        sort_order=category.sort_order,
        total_budget=category_total_budget,
        total_actual=category_total_actual,
        total_difference=category_difference,
        allocation_types=type_responses
    )


class SetBudgetRequest(BaseModel):
    """Request to set budget for allocation type."""
    allocation_type_id: str
    budget_amount: Decimal


class SetActualRequest(BaseModel):
    """Request to record actual spending/investment."""
    allocation_type_id: str
    actual_amount: Decimal
    notes: Optional[str] = None


@router.post("/allocations/budget")
async def set_budget(
    request: SetBudgetRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Set budget amount for an allocation type."""
    now = datetime.utcnow()

    user_alloc = db.query(UserAllocation).filter(
        and_(
            UserAllocation.user_id == user_id,
            UserAllocation.allocation_type_id == request.allocation_type_id,
            UserAllocation.month == now.month,
            UserAllocation.year == now.year
        )
    ).first()

    if user_alloc:
        user_alloc.budget_amount = request.budget_amount
    else:
        user_alloc = UserAllocation(
            user_id=user_id,
            allocation_type_id=request.allocation_type_id,
            budget_amount=request.budget_amount,
            actual_amount=Decimal("0.00"),
            month=now.month,
            year=now.year
        )
        db.add(user_alloc)

    db.commit()
    return {"message": "Budget set successfully"}


@router.post("/allocations/actual")
async def set_actual(
    request: SetActualRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Record actual spending/investment."""
    now = datetime.utcnow()

    user_alloc = db.query(UserAllocation).filter(
        and_(
            UserAllocation.user_id == user_id,
            UserAllocation.allocation_type_id == request.allocation_type_id,
            UserAllocation.month == now.month,
            UserAllocation.year == now.year
        )
    ).first()

    if user_alloc:
        user_alloc.actual_amount = request.actual_amount
        if request.notes:
            user_alloc.notes = request.notes
    else:
        user_alloc = UserAllocation(
            user_id=user_id,
            allocation_type_id=request.allocation_type_id,
            budget_amount=Decimal("0.00"),
            actual_amount=request.actual_amount,
            month=now.month,
            year=now.year,
            notes=request.notes
        )
        db.add(user_alloc)

    db.commit()
    return {"message": "Actual amount recorded successfully"}


@router.put("/allocations/{allocation_id}")
async def update_allocation(
    allocation_id: str,
    budget_amount: Optional[Decimal] = None,
    actual_amount: Optional[Decimal] = None,
    notes: Optional[str] = None,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update existing allocation entry."""
    user_alloc = db.query(UserAllocation).filter(
        and_(
            UserAllocation.id == allocation_id,
            UserAllocation.user_id == user_id
        )
    ).first()

    if not user_alloc:
        raise HTTPException(status_code=404, detail="Allocation not found")

    if budget_amount is not None:
        user_alloc.budget_amount = budget_amount
    if actual_amount is not None:
        user_alloc.actual_amount = actual_amount
    if notes is not None:
        user_alloc.notes = notes

    db.commit()
    return {"message": "Allocation updated successfully"}


@router.delete("/allocations/{allocation_id}")
async def delete_allocation(
    allocation_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete allocation entry."""
    user_alloc = db.query(UserAllocation).filter(
        and_(
            UserAllocation.id == allocation_id,
            UserAllocation.user_id == user_id
        )
    ).first()

    if not user_alloc:
        raise HTTPException(status_code=404, detail="Allocation not found")

    db.delete(user_alloc)
    db.commit()
    return {"message": "Allocation deleted successfully"}


# ==================== MONTHLY BUDGET ENDPOINTS ====================

class IncomeSource(BaseModel):
    """Income source model."""
    category: str  # e.g., "salary", "freelance", "business"
    amount: Decimal
    label: str  # e.g., "Monthly Salary", "Freelance Projects"


class MonthlyBudgetRequest(BaseModel):
    """Request to set monthly budget."""
    total_amount: Decimal
    income_sources: Optional[List[IncomeSource]] = None
    notes: Optional[str] = None


class MonthlyBudgetResponse(BaseModel):
    """Monthly budget response model."""
    id: str
    total_amount: Decimal
    income_sources: Optional[List[IncomeSource]] = None
    month: int
    year: int
    notes: Optional[str] = None
    category_breakdown: dict

    class Config:
        from_attributes = True


@router.post("/monthly-budget")
async def set_monthly_budget(
    request: MonthlyBudgetRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Set total monthly budget. System auto-calculates category allocations.

    Example: Set ₹10,000 → System calculates:
    - FREEDOM: ₹1,000 (10%)
    - HEALTH: ₹1,000 (10%)
    - SPENDING: ₹5,000 (50%)
    - etc.
    """
    now = datetime.utcnow()

    # Check if budget already exists for this month
    existing_budget = db.query(MonthlyBudget).filter(
        and_(
            MonthlyBudget.user_id == user_id,
            MonthlyBudget.month == now.month,
            MonthlyBudget.year == now.year
        )
    ).first()

    if existing_budget:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Monthly budget already exists for {now.month}/{now.year}. Use PUT to update."
        )

    # Convert income_sources to dict format for JSONB storage
    income_sources_data = None
    if request.income_sources:
        income_sources_data = [
            {
                "category": source.category,
                "amount": float(source.amount),
                "label": source.label
            }
            for source in request.income_sources
        ]

    # Create new monthly budget
    monthly_budget = MonthlyBudget(
        user_id=user_id,
        total_amount=request.total_amount,
        income_sources=income_sources_data,
        month=now.month,
        year=now.year,
        notes=request.notes
    )

    db.add(monthly_budget)
    if income_sources_data:
        flag_modified(monthly_budget, "income_sources")
    db.commit()
    db.refresh(monthly_budget)

    # Calculate category breakdown
    categories = db.query(AllocationCategory).all()
    breakdown = {}
    for cat in categories:
        amount = (request.total_amount * cat.target_percentage) / 100
        breakdown[cat.name] = {
            "label": cat.label,
            "percentage": float(cat.target_percentage),
            "amount": float(amount)
        }

    return {
        "id": monthly_budget.id,
        "total_amount": monthly_budget.total_amount,
        "income_sources": monthly_budget.income_sources,
        "month": monthly_budget.month,
        "year": monthly_budget.year,
        "notes": monthly_budget.notes,
        "category_breakdown": breakdown,
        "message": "Monthly budget set successfully"
    }


@router.put("/monthly-budget")
async def update_monthly_budget(
    request: MonthlyBudgetRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Update total monthly budget for current month.
    System recalculates category allocations automatically.
    """
    now = datetime.utcnow()

    # Find existing budget
    monthly_budget = db.query(MonthlyBudget).filter(
        and_(
            MonthlyBudget.user_id == user_id,
            MonthlyBudget.month == now.month,
            MonthlyBudget.year == now.year
        )
    ).first()

    if not monthly_budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No monthly budget found for {now.month}/{now.year}. Use POST to create."
        )

    # Update budget
    monthly_budget.total_amount = request.total_amount
    if request.notes:
        monthly_budget.notes = request.notes

    # Update income sources
    if request.income_sources:
        monthly_budget.income_sources = [
            {
                "category": source.category,
                "amount": float(source.amount),
                "label": source.label
            }
            for source in request.income_sources
        ]
        flag_modified(monthly_budget, "income_sources")

    db.commit()
    db.refresh(monthly_budget)

    # Calculate category breakdown
    categories = db.query(AllocationCategory).all()
    breakdown = {}
    for cat in categories:
        amount = (request.total_amount * cat.target_percentage) / 100
        breakdown[cat.name] = {
            "label": cat.label,
            "percentage": float(cat.target_percentage),
            "amount": float(amount)
        }

    return {
        "id": monthly_budget.id,
        "total_amount": monthly_budget.total_amount,
        "income_sources": monthly_budget.income_sources,
        "month": monthly_budget.month,
        "year": monthly_budget.year,
        "notes": monthly_budget.notes,
        "category_breakdown": breakdown,
        "message": "Monthly budget updated successfully"
    }


@router.get("/monthly-budget")
async def get_monthly_budget(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get current month's budget with auto-calculated category allocations.

    Flow:
    1. Get current_balance from transactions
    2. Auto-calculate allocated_amount = current_balance × target_%
    3. Compare with actual_invested from user_allocations
    4. Show status (under/perfect/over)
    """
    now = datetime.utcnow()
    month = now.month
    year = now.year

    # Get monthly budget (from transactions)
    monthly_budget = db.query(MonthlyBudget).filter(
        and_(
            MonthlyBudget.user_id == user_id,
            MonthlyBudget.month == month,
            MonthlyBudget.year == year
        )
    ).first()

    if not monthly_budget:
        return {
            "month": month,
            "year": year,
            "current_balance": 0.00,
            "total_income": 0.00,
            "total_expense": 0.00,
            "categories": [],
            "message": "No transactions yet for this month"
        }

    # Get all allocation categories
    categories = db.query(AllocationCategory).order_by(AllocationCategory.sort_order).all()

    # Optimized: Single JOIN query to get all user allocations with their types
    # This replaces N+1 queries with 1 efficient query
    user_allocations = db.query(
        UserAllocation,
        AllocationType.category_id
    ).join(
        AllocationType,
        UserAllocation.allocation_type_id == AllocationType.id
    ).filter(
        and_(
            UserAllocation.user_id == user_id,
            UserAllocation.month == month,
            UserAllocation.year == year
        )
    ).all()

    # Build a dictionary of actual_invested per category
    category_investments = {}
    for user_alloc, category_id in user_allocations:
        if category_id not in category_investments:
            category_investments[category_id] = Decimal("0.00")
        category_investments[category_id] += user_alloc.actual_amount

    category_list = []
    for cat in categories:
        # Auto-calculate allocated amount based on current balance
        allocated_amount = (monthly_budget.current_balance * cat.target_percentage) / Decimal("100")

        # Get actual invested from pre-built dictionary
        actual_invested = category_investments.get(cat.id, Decimal("0.00"))

        # Calculate difference
        difference = actual_invested - allocated_amount

        # Determine status
        if difference == 0:
            status = "perfect"
        elif difference < 0:
            status = "under"
        else:
            status = "over"

        category_list.append({
            "name": cat.name,
            "label": cat.label,
            "icon": cat.icon,
            "icon_color": cat.icon_color,
            "target_percentage": float(cat.target_percentage),
            "allocated_amount": float(allocated_amount),
            "actual_invested": float(actual_invested),
            "difference": float(difference),
            "status": status
        })

    return {
        "month": month,
        "year": year,
        "current_balance": float(monthly_budget.current_balance),
        "total_income": float(monthly_budget.total_income),
        "total_expense": float(monthly_budget.total_expense),
        "categories": category_list
    }
