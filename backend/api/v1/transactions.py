"""Transaction endpoints for income and expense tracking."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from datetime import datetime
from decimal import Decimal

from backend.core.security import get_current_user_id
from backend.db.database import get_db
from backend.db.models import Transaction, MonthlyBudget

router = APIRouter()


class TransactionRequest(BaseModel):
    """Request to create a transaction."""
    type: str = Field(..., description="Transaction type: 'income' or 'expense'")
    category: str = Field(..., description="Category like 'salary', 'food', 'rent'")
    amount: Decimal = Field(..., gt=0, description="Transaction amount (must be positive)")
    label: str = Field(..., min_length=1, max_length=200, description="Description")
    transaction_date: datetime = Field(..., description="When transaction occurred")


class TransactionResponse(BaseModel):
    """Transaction response model."""
    id: str
    type: str
    category: str
    amount: Decimal
    label: str
    transaction_date: datetime
    month: int
    year: int
    created_at: datetime

    class Config:
        from_attributes = True


class MonthlyBalanceResponse(BaseModel):
    """Monthly balance summary."""
    month: int
    year: int
    current_balance: Decimal
    total_income: Decimal
    total_expense: Decimal
    transaction_count: int


@router.post("/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    request: TransactionRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Add income or expense transaction.

    - **type**: "income" adds to balance, "expense" subtracts
    - **category**: e.g., "salary", "freelance", "food", "rent"
    - **amount**: Transaction amount (always positive)
    - **label**: Description of the transaction
    - **transaction_date**: When the transaction occurred

    Example:
    ```json
    {
        "type": "income",
        "category": "salary",
        "amount": 50000,
        "label": "Monthly Salary",
        "transaction_date": "2025-10-16T10:00:00"
    }
    ```
    """
    # Validate type
    if request.type not in ['income', 'expense']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Type must be 'income' or 'expense'"
        )

    # Extract month/year from transaction date
    month = request.transaction_date.month
    year = request.transaction_date.year

    # Create transaction
    transaction = Transaction(
        user_id=user_id,
        type=request.type,
        category=request.category,
        amount=request.amount,
        label=request.label,
        transaction_date=request.transaction_date,
        month=month,
        year=year
    )

    db.add(transaction)

    # Update or create monthly budget
    monthly_budget = db.query(MonthlyBudget).filter(
        and_(
            MonthlyBudget.user_id == user_id,
            MonthlyBudget.month == month,
            MonthlyBudget.year == year
        )
    ).first()

    if not monthly_budget:
        # Create new monthly budget starting from 0
        monthly_budget = MonthlyBudget(
            user_id=user_id,
            month=month,
            year=year,
            current_balance=Decimal("0.00"),
            total_income=Decimal("0.00"),
            total_expense=Decimal("0.00")
        )
        db.add(monthly_budget)

    # Update totals
    if request.type == 'income':
        monthly_budget.total_income += request.amount
        monthly_budget.current_balance += request.amount
    else:  # expense
        monthly_budget.total_expense += request.amount
        monthly_budget.current_balance -= request.amount

    db.commit()
    db.refresh(transaction)

    return transaction


@router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    month: Optional[int] = None,
    year: Optional[int] = None,
    type: Optional[str] = None,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get all transactions for the user.

    Query parameters:
    - **month**: Filter by month (1-12). Defaults to current month.
    - **year**: Filter by year. Defaults to current year.
    - **type**: Filter by type ('income' or 'expense')
    """
    now = datetime.utcnow()
    if month is None:
        month = now.month
    if year is None:
        year = now.year

    query = db.query(Transaction).filter(
        and_(
            Transaction.user_id == user_id,
            Transaction.month == month,
            Transaction.year == year
        )
    )

    if type:
        if type not in ['income', 'expense']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Type must be 'income' or 'expense'"
            )
        query = query.filter(Transaction.type == type)

    transactions = query.order_by(desc(Transaction.transaction_date)).all()
    return transactions


@router.get("/transactions/balance", response_model=MonthlyBalanceResponse)
async def get_monthly_balance(
    month: Optional[int] = None,
    year: Optional[int] = None,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get current balance for the month.

    Returns:
    - **current_balance**: Total income - Total expenses
    - **total_income**: Sum of all income transactions
    - **total_expense**: Sum of all expense transactions
    - **transaction_count**: Number of transactions
    """
    now = datetime.utcnow()
    if month is None:
        month = now.month
    if year is None:
        year = now.year

    # Get or create monthly budget
    monthly_budget = db.query(MonthlyBudget).filter(
        and_(
            MonthlyBudget.user_id == user_id,
            MonthlyBudget.month == month,
            MonthlyBudget.year == year
        )
    ).first()

    if not monthly_budget:
        # No transactions yet, return zero balance
        return {
            "month": month,
            "year": year,
            "current_balance": Decimal("0.00"),
            "total_income": Decimal("0.00"),
            "total_expense": Decimal("0.00"),
            "transaction_count": 0
        }

    # Count transactions
    transaction_count = db.query(Transaction).filter(
        and_(
            Transaction.user_id == user_id,
            Transaction.month == month,
            Transaction.year == year
        )
    ).count()

    return {
        "month": monthly_budget.month,
        "year": monthly_budget.year,
        "current_balance": monthly_budget.current_balance,
        "total_income": monthly_budget.total_income,
        "total_expense": monthly_budget.total_expense,
        "transaction_count": transaction_count
    }


@router.delete("/transactions/{transaction_id}")
async def delete_transaction(
    transaction_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Delete a transaction and update monthly balance.

    This will:
    1. Remove the transaction
    2. Update the monthly balance accordingly
    """
    # Find transaction
    transaction = db.query(Transaction).filter(
        and_(
            Transaction.id == transaction_id,
            Transaction.user_id == user_id
        )
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    # Get monthly budget
    monthly_budget = db.query(MonthlyBudget).filter(
        and_(
            MonthlyBudget.user_id == user_id,
            MonthlyBudget.month == transaction.month,
            MonthlyBudget.year == transaction.year
        )
    ).first()

    if monthly_budget:
        # Reverse the transaction
        if transaction.type == 'income':
            monthly_budget.total_income -= transaction.amount
            monthly_budget.current_balance -= transaction.amount
        else:  # expense
            monthly_budget.total_expense -= transaction.amount
            monthly_budget.current_balance += transaction.amount

    # Delete transaction
    db.delete(transaction)
    db.commit()

    return {
        "message": "Transaction deleted successfully",
        "transaction_id": transaction_id
    }
