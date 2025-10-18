# API Response Format - Investment Breakdown

**Version:** 1.0.0
**Last Updated:** October 15, 2025
**Backend:** Python FastAPI
**API Framework:** FastAPI 0.104+
**Python Version:** 3.11+

---

## Table of Contents

1. [Overview](#overview)
2. [Base URL](#base-url)
3. [Authentication](#authentication)
4. [FastAPI Features](#fastapi-features)
5. [Endpoints](#endpoints)
6. [Pydantic Models](#pydantic-models)
7. [Example Responses](#example-responses)
8. [Error Responses](#error-responses)
9. [Validation](#validation)

---

## Overview

This document defines the API response format for the WealthWarriorsHub investment breakdown and allocation system built with **Python FastAPI**. All responses follow REST principles with automatic validation using Pydantic models.

### Technology Stack

- **Framework:** FastAPI 0.104+
- **Python:** 3.11+
- **Validation:** Pydantic v2
- **Authentication:** OAuth2 with JWT Bearer tokens
- **Database ORM:** SQLAlchemy 2.0
- **Migration:** Alembic

---

## Base URL

```
Production: https://api.wealthwarriorshub.com/api/v1
Staging: https://staging-api.wealthwarriorshub.com/api/v1
Development: http://localhost:8000/api/v1
```

### Interactive Documentation

FastAPI provides automatic interactive API documentation:

```
Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc
OpenAPI JSON: http://localhost:8000/openapi.json
```

---

## Authentication

All protected endpoints require OAuth2 Bearer token authentication:

```http
Authorization: Bearer <access_token>
```

### FastAPI Dependency

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    # Token verification logic
    pass
```

---

## FastAPI Features

### Automatic Validation

All request/response data is validated using Pydantic models with automatic error messages.

### Async Support

All endpoints support async operations for better performance:

```python
@router.get("/allocations")
async def get_allocations(current_user: User = Depends(get_current_user)):
    return await allocation_service.get_all_allocations(current_user.id)
```

### Type Hints

FastAPI uses Python type hints for automatic documentation and validation.

### Dependency Injection

Common dependencies (auth, database) are injected automatically.

---

## Endpoints

### 1. Get All Allocations Summary

**Endpoint:** `GET /api/v1/allocations`

**Description:** Returns summary of all 6 wealth allocation categories with current status.

**FastAPI Route:**

```python
@router.get(
    "/allocations",
    response_model=AllocationsResponse,
    status_code=status.HTTP_200_OK,
    tags=["Allocations"]
)
async def get_all_allocations(
    current_user: User = Depends(get_current_user)
) -> AllocationsResponse:
    """
    Retrieve all wealth allocation categories for the current user.

    Returns summary of 6 allocation categories with budget tracking.
    """
    return await allocation_service.get_all_allocations(current_user.id)
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "allocations": [
      {
        "id": "freedom",
        "label": "Freedom",
        "description": "Build your financial freedom fund for long-term wealth",
        "icon": "bank",
        "iconColor": "#3b82f6",
        "targetPercentage": 10,
        "currentPercentage": 15,
        "totalBudget": 1180.0,
        "totalActual": 1135.0,
        "difference": 45.0,
        "status": "under_budget",
        "categoryCount": 5
      },
      {
        "id": "health",
        "label": "Health",
        "description": "Provision for Emergencies",
        "icon": "heart-pulse",
        "iconColor": "#ef4444",
        "targetPercentage": 10,
        "currentPercentage": 7,
        "totalBudget": 1180.0,
        "totalActual": 1135.0,
        "difference": 45.0,
        "status": "under_budget",
        "categoryCount": 5
      },
      {
        "id": "spending",
        "label": "Spending",
        "description": "Spending for Life Style",
        "icon": "cart",
        "iconColor": "#10b981",
        "targetPercentage": 50,
        "currentPercentage": 50,
        "totalBudget": 1400.0,
        "totalActual": 1365.0,
        "difference": 35.0,
        "status": "under_budget",
        "categoryCount": 6
      },
      {
        "id": "learning",
        "label": "Learning",
        "description": "Invest in education and skill development",
        "icon": "school",
        "iconColor": "#fbbf24",
        "targetPercentage": 10,
        "currentPercentage": 10,
        "totalBudget": 1830.0,
        "totalActual": 1785.0,
        "difference": 45.0,
        "status": "under_budget",
        "categoryCount": 8
      },
      {
        "id": "entertainment",
        "label": "Entertainment",
        "description": "Enjoy life with fun activities and entertainment",
        "icon": "gamepad-variant",
        "iconColor": "#ef4444",
        "targetPercentage": 5,
        "currentPercentage": 5,
        "totalBudget": 1180.0,
        "totalActual": 1135.0,
        "difference": 45.0,
        "status": "under_budget",
        "categoryCount": 5
      },
      {
        "id": "contribution",
        "label": "Contribution",
        "description": "Give back to society and make a difference",
        "icon": "hand-heart",
        "iconColor": "#3b82f6",
        "targetPercentage": 5,
        "currentPercentage": 5,
        "totalBudget": 1180.0,
        "totalActual": 1135.0,
        "difference": 45.0,
        "status": "under_budget",
        "categoryCount": 5
      }
    ],
    "summary": {
      "totalBudget": 7950.0,
      "totalActual": 7690.0,
      "totalDifference": 260.0,
      "totalCategories": 34,
      "allocatedPercentage": 95,
      "unallocatedPercentage": 5,
      "overallStatus": "excellent"
    }
  },
  "timestamp": "2025-10-15T10:30:00Z"
}
```

---

### 2. Get Allocation Detail

**Endpoint:** `GET /api/v1/allocations/{allocation_id}`

**Description:** Returns detailed breakdown of a specific allocation category with all investment subcategories.

**FastAPI Route:**

```python
@router.get(
    "/allocations/{allocation_id}",
    response_model=AllocationDetailResponse,
    status_code=status.HTTP_200_OK,
    tags=["Allocations"]
)
async def get_allocation_detail(
    allocation_id: str = Path(
        ...,
        description="Allocation ID",
        regex="^(freedom|health|spending|learning|entertainment|contribution)$"
    ),
    current_user: User = Depends(get_current_user)
) -> AllocationDetailResponse:
    """
    Retrieve detailed breakdown for a specific allocation category.

    Args:
        allocation_id: One of freedom, health, spending, learning, entertainment, contribution

    Returns:
        Detailed allocation with all investment subcategories
    """
    return await allocation_service.get_allocation_detail(current_user.id, allocation_id)
```

**Path Parameters:**

- `allocation_id` (string): One of `freedom`, `health`, `spending`, `learning`, `entertainment`, `contribution`

**Response:**

```json
{
  "status": "success",
  "data": {
    "allocation": {
      "id": "freedom",
      "label": "Freedom",
      "description": "Build your financial freedom fund for long-term wealth",
      "icon": "bank",
      "iconColor": "#3b82f6",
      "targetPercentage": 10,
      "currentPercentage": 15,
      "totalBudget": 1180.0,
      "totalActual": 1135.0,
      "difference": 45.0,
      "status": "under_budget"
    },
    "investmentCategories": [
      {
        "id": "bank_deposits",
        "name": "Bank Deposits",
        "description": "Fixed deposits, savings accounts",
        "purpose": "Secure, low-risk savings",
        "budget": 250.0,
        "actual": 200.0,
        "difference": 50.0,
        "status": "under_budget",
        "transactionCount": 3,
        "lastTransactionDate": "2025-10-10T14:20:00Z"
      },
      {
        "id": "mutual_funds",
        "name": "Mutual Funds",
        "description": "Equity, debt, hybrid funds",
        "purpose": "Diversified investments",
        "budget": 180.0,
        "actual": 195.0,
        "difference": -15.0,
        "status": "over_budget",
        "transactionCount": 2,
        "lastTransactionDate": "2025-10-12T09:15:00Z"
      },
      {
        "id": "shares_stock",
        "name": "Shares & Stock",
        "description": "Direct equity investments",
        "purpose": "High-growth potential",
        "budget": 320.0,
        "actual": 310.0,
        "difference": 10.0,
        "status": "under_budget",
        "transactionCount": 5,
        "lastTransactionDate": "2025-10-14T16:45:00Z"
      },
      {
        "id": "real_estate",
        "name": "Real Estate",
        "description": "Property investments",
        "purpose": "Long-term asset building",
        "budget": 150.0,
        "actual": 160.0,
        "difference": -10.0,
        "status": "over_budget",
        "transactionCount": 1,
        "lastTransactionDate": "2025-10-08T11:30:00Z"
      },
      {
        "id": "capital_new_business",
        "name": "Capital in New Business",
        "description": "Entrepreneurial investments",
        "purpose": "Business ventures",
        "budget": 280.0,
        "actual": 270.0,
        "difference": 10.0,
        "status": "under_budget",
        "transactionCount": 2,
        "lastTransactionDate": "2025-10-05T13:00:00Z"
      }
    ],
    "summary": {
      "categoryCount": 5,
      "totalBudget": 1180.0,
      "totalActual": 1135.0,
      "totalDifference": 45.0,
      "totalTransactions": 13,
      "underBudgetCount": 3,
      "overBudgetCount": 2,
      "onBudgetCount": 0
    }
  },
  "timestamp": "2025-10-15T10:30:00Z"
}
```

---

### 3. Get Investment Category Transactions

**Endpoint:** `GET /api/v1/allocations/{allocation_id}/categories/{category_id}/transactions`

**Description:** Returns transaction history for a specific investment category.

**FastAPI Route:**

```python
@router.get(
    "/allocations/{allocation_id}/categories/{category_id}/transactions",
    response_model=TransactionsResponse,
    status_code=status.HTTP_200_OK,
    tags=["Transactions"]
)
async def get_transactions(
    allocation_id: str = Path(..., description="Allocation ID"),
    category_id: str = Path(..., description="Category ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    start_date: Optional[datetime] = Query(None, description="Filter from date"),
    end_date: Optional[datetime] = Query(None, description="Filter to date"),
    current_user: User = Depends(get_current_user)
) -> TransactionsResponse:
    """
    Retrieve transaction history for a specific investment category.

    Supports pagination and date filtering.
    """
    return await transaction_service.get_transactions(
        user_id=current_user.id,
        allocation_id=allocation_id,
        category_id=category_id,
        page=page,
        limit=limit,
        start_date=start_date,
        end_date=end_date
    )
```

**Path Parameters:**

- `allocation_id` (string): Allocation identifier
- `category_id` (string): Investment category identifier

**Query Parameters:**

- `page` (integer, optional): Page number (default: 1, min: 1)
- `limit` (integer, optional): Items per page (default: 20, min: 1, max: 100)
- `start_date` (datetime, optional): Filter from date (ISO 8601)
- `end_date` (datetime, optional): Filter to date (ISO 8601)

**Response:**

```json
{
  "status": "success",
  "data": {
    "transactions": [
      {
        "id": "txn_001",
        "allocationId": "freedom",
        "categoryId": "bank_deposits",
        "categoryName": "Bank Deposits",
        "type": "investment",
        "amount": 100.0,
        "currency": "INR",
        "description": "Fixed Deposit - HDFC Bank",
        "notes": "5 year FD at 7.5% interest",
        "transactionDate": "2025-10-10T14:20:00Z",
        "createdAt": "2025-10-10T14:20:00Z",
        "updatedAt": "2025-10-10T14:20:00Z"
      },
      {
        "id": "txn_002",
        "allocationId": "freedom",
        "categoryId": "bank_deposits",
        "categoryName": "Bank Deposits",
        "type": "investment",
        "amount": 50.0,
        "currency": "INR",
        "description": "Savings Account Deposit",
        "notes": "Monthly savings",
        "transactionDate": "2025-10-05T10:00:00Z",
        "createdAt": "2025-10-05T10:00:00Z",
        "updatedAt": "2025-10-05T10:00:00Z"
      },
      {
        "id": "txn_003",
        "allocationId": "freedom",
        "categoryId": "bank_deposits",
        "categoryName": "Bank Deposits",
        "type": "investment",
        "amount": 50.0,
        "currency": "INR",
        "description": "Recurring Deposit",
        "notes": "RD installment",
        "transactionDate": "2025-10-01T09:30:00Z",
        "createdAt": "2025-10-01T09:30:00Z",
        "updatedAt": "2025-10-01T09:30:00Z"
      }
    ],
    "pagination": {
      "currentPage": 1,
      "totalPages": 1,
      "totalItems": 3,
      "itemsPerPage": 20,
      "hasNextPage": false,
      "hasPreviousPage": false
    },
    "summary": {
      "totalAmount": 200.0,
      "transactionCount": 3,
      "budgetAmount": 250.0,
      "remainingBudget": 50.0,
      "utilizationPercentage": 80.0
    }
  },
  "timestamp": "2025-10-15T10:30:00Z"
}
```

---

### 4. Create Investment Transaction

**Endpoint:** `POST /api/v1/allocations/{allocation_id}/categories/{category_id}/transactions`

**Description:** Create a new investment transaction.

**FastAPI Route:**

```python
@router.post(
    "/allocations/{allocation_id}/categories/{category_id}/transactions",
    response_model=TransactionCreateResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Transactions"]
)
async def create_transaction(
    allocation_id: str = Path(..., description="Allocation ID"),
    category_id: str = Path(..., description="Category ID"),
    transaction_data: TransactionCreate = Body(...),
    current_user: User = Depends(get_current_user)
) -> TransactionCreateResponse:
    """
    Create a new investment transaction.

    Validates budget availability and updates category totals.
    """
    return await transaction_service.create_transaction(
        user_id=current_user.id,
        allocation_id=allocation_id,
        category_id=category_id,
        transaction_data=transaction_data
    )
```

**Request Body (Pydantic Model):**

```python
class TransactionCreate(BaseModel):
    type: TransactionType = Field(..., description="Transaction type")
    amount: Decimal = Field(..., gt=0, description="Transaction amount")
    currency: str = Field(default="INR", max_length=3, description="Currency code")
    description: str = Field(..., min_length=1, max_length=200)
    notes: Optional[str] = Field(None, max_length=500)
    transaction_date: datetime = Field(..., description="Transaction date")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "investment",
                "amount": 100.00,
                "currency": "INR",
                "description": "Fixed Deposit - HDFC Bank",
                "notes": "5 year FD at 7.5% interest",
                "transaction_date": "2025-10-10T14:20:00Z"
            }
        }
```

**Request Body Example:**

```json
{
  "type": "investment",
  "amount": 100.0,
  "currency": "INR",
  "description": "Fixed Deposit - HDFC Bank",
  "notes": "5 year FD at 7.5% interest",
  "transaction_date": "2025-10-10T14:20:00Z"
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Transaction created successfully",
  "data": {
    "transaction": {
      "id": "txn_001",
      "allocationId": "freedom",
      "categoryId": "bank_deposits",
      "categoryName": "Bank Deposits",
      "type": "investment",
      "amount": 100.0,
      "currency": "INR",
      "description": "Fixed Deposit - HDFC Bank",
      "notes": "5 year FD at 7.5% interest",
      "transactionDate": "2025-10-10T14:20:00Z",
      "createdAt": "2025-10-10T14:20:00Z",
      "updatedAt": "2025-10-10T14:20:00Z"
    },
    "updatedCategory": {
      "id": "bank_deposits",
      "name": "Bank Deposits",
      "budget": 250.0,
      "actual": 200.0,
      "difference": 50.0,
      "status": "under_budget",
      "utilizationPercentage": 80.0
    }
  },
  "timestamp": "2025-10-15T10:30:00Z"
}
```

---

### 5. Update Investment Budget

**Endpoint:** `PUT /api/v1/allocations/{allocation_id}/categories/{category_id}/budget`

**Description:** Update budget for a specific investment category.

**FastAPI Route:**

```python
@router.put(
    "/allocations/{allocation_id}/categories/{category_id}/budget",
    response_model=BudgetUpdateResponse,
    status_code=status.HTTP_200_OK,
    tags=["Budget"]
)
async def update_budget(
    allocation_id: str = Path(..., description="Allocation ID"),
    category_id: str = Path(..., description="Category ID"),
    budget_data: BudgetUpdate = Body(...),
    current_user: User = Depends(get_current_user)
) -> BudgetUpdateResponse:
    """
    Update budget for a specific investment category.

    Recalculates allocation totals and status.
    """
    return await budget_service.update_budget(
        user_id=current_user.id,
        allocation_id=allocation_id,
        category_id=category_id,
        budget_data=budget_data
    )
```

**Request Body (Pydantic Model):**

```python
class BudgetUpdate(BaseModel):
    budget: Decimal = Field(..., gt=0, description="New budget amount")

    class Config:
        json_schema_extra = {
            "example": {
                "budget": 300.00
            }
        }
```

**Request Body Example:**

```json
{
  "budget": 300.0
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Budget updated successfully",
  "data": {
    "category": {
      "id": "bank_deposits",
      "name": "Bank Deposits",
      "budget": 300.0,
      "actual": 200.0,
      "difference": 100.0,
      "status": "under_budget",
      "utilizationPercentage": 66.67
    },
    "allocationSummary": {
      "id": "freedom",
      "label": "Freedom",
      "totalBudget": 1230.0,
      "totalActual": 1135.0,
      "difference": 95.0,
      "status": "under_budget"
    }
  },
  "timestamp": "2025-10-15T10:30:00Z"
}
```

---

### 6. Get Analytics Dashboard

**Endpoint:** `GET /api/v1/allocations/analytics`

**Description:** Returns comprehensive analytics and insights across all allocations.

**FastAPI Route:**

```python
@router.get(
    "/allocations/analytics",
    response_model=AnalyticsResponse,
    status_code=status.HTTP_200_OK,
    tags=["Analytics"]
)
async def get_analytics(
    period: Period = Query(Period.MONTHLY, description="Analysis period"),
    start_date: Optional[datetime] = Query(None, description="Filter from date"),
    end_date: Optional[datetime] = Query(None, description="Filter to date"),
    current_user: User = Depends(get_current_user)
) -> AnalyticsResponse:
    """
    Retrieve comprehensive analytics and insights across all allocations.

    Provides overview, breakdowns, trends, and top categories.
    """
    return await analytics_service.get_analytics(
        user_id=current_user.id,
        period=period,
        start_date=start_date,
        end_date=end_date
    )
```

**Query Parameters:**

- `period` (enum, optional): `monthly`, `quarterly`, `yearly` (default: `monthly`)
- `start_date` (datetime, optional): Filter from date (ISO 8601)
- `end_date` (datetime, optional): Filter to date (ISO 8601)

**Response:**

```json
{
  "status": "success",
  "data": {
    "overview": {
      "totalBudget": 7950.0,
      "totalActual": 7690.0,
      "totalDifference": 260.0,
      "utilizationPercentage": 96.73,
      "overallStatus": "excellent"
    },
    "allocationBreakdown": [
      {
        "id": "freedom",
        "label": "Freedom",
        "targetPercentage": 10,
        "currentPercentage": 15,
        "budget": 1180.0,
        "actual": 1135.0,
        "difference": 45.0
      },
      {
        "id": "health",
        "label": "Health",
        "targetPercentage": 10,
        "currentPercentage": 7,
        "budget": 1180.0,
        "actual": 1135.0,
        "difference": 45.0
      },
      {
        "id": "spending",
        "label": "Spending",
        "targetPercentage": 50,
        "currentPercentage": 50,
        "budget": 1400.0,
        "actual": 1365.0,
        "difference": 35.0
      },
      {
        "id": "learning",
        "label": "Learning",
        "targetPercentage": 10,
        "currentPercentage": 10,
        "budget": 1830.0,
        "actual": 1785.0,
        "difference": 45.0
      },
      {
        "id": "entertainment",
        "label": "Entertainment",
        "targetPercentage": 5,
        "currentPercentage": 5,
        "budget": 1180.0,
        "actual": 1135.0,
        "difference": 45.0
      },
      {
        "id": "contribution",
        "label": "Contribution",
        "targetPercentage": 5,
        "currentPercentage": 5,
        "budget": 1180.0,
        "actual": 1135.0,
        "difference": 45.0
      }
    ],
    "topCategories": {
      "mostInvested": [
        {
          "allocationId": "learning",
          "categoryId": "college_fees",
          "categoryName": "College Fees",
          "actual": 320.0,
          "budget": 300.0,
          "utilizationPercentage": 106.67
        },
        {
          "allocationId": "freedom",
          "categoryId": "shares_stock",
          "categoryName": "Shares & Stock",
          "actual": 310.0,
          "budget": 320.0,
          "utilizationPercentage": 96.88
        }
      ],
      "mostUnderBudget": [
        {
          "allocationId": "health",
          "categoryId": "hospitalization",
          "categoryName": "Hospitalization",
          "actual": 0.0,
          "budget": 320.0,
          "difference": 320.0
        }
      ]
    },
    "trends": {
      "monthlyGrowth": 5.2,
      "averageMonthlyInvestment": 7690.0,
      "projectedYearEnd": 92280.0
    }
  },
  "timestamp": "2025-10-15T10:30:00Z"
}
```

---

## Pydantic Models

### Base Configuration

```python
from pydantic import BaseModel, Field, validator
from decimal import Decimal
from datetime import datetime
from typing import Optional, List
from enum import Enum
```

### Enums

```python
class AllocationStatus(str, Enum):
    """Allocation budget status"""
    UNDER_BUDGET = "under_budget"
    ON_BUDGET = "on_budget"
    OVER_BUDGET = "over_budget"


class CategoryStatus(str, Enum):
    """Investment category budget status"""
    UNDER_BUDGET = "under_budget"
    ON_BUDGET = "on_budget"
    OVER_BUDGET = "over_budget"


class TransactionType(str, Enum):
    """Transaction type enumeration"""
    INVESTMENT = "investment"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    RETURN = "return"


class Period(str, Enum):
    """Analytics period enumeration"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
```

### Allocation Models

```python
class Allocation(BaseModel):
    """Wealth allocation category model"""
    id: str = Field(..., description="Unique identifier")
    label: str = Field(..., min_length=1, max_length=50, description="Display name")
    description: str = Field(..., max_length=200, description="Purpose description")
    icon: str = Field(..., description="Material icon name")
    icon_color: str = Field(..., regex="^#[0-9A-Fa-f]{6}$", description="Hex color code")
    target_percentage: Decimal = Field(..., ge=0, le=100, description="Target allocation")
    current_percentage: Decimal = Field(..., ge=0, le=100, description="Current allocation")
    total_budget: Decimal = Field(..., ge=0, description="Total budget amount")
    total_actual: Decimal = Field(..., ge=0, description="Total actual investment")
    difference: Decimal = Field(..., description="Budget - Actual")
    status: AllocationStatus = Field(..., description="Status indicator")
    category_count: int = Field(..., ge=0, description="Number of subcategories")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "freedom",
                "label": "Freedom",
                "description": "Build your financial freedom fund",
                "icon": "bank",
                "icon_color": "#3b82f6",
                "target_percentage": 10,
                "current_percentage": 15,
                "total_budget": 1180.00,
                "total_actual": 1135.00,
                "difference": 45.00,
                "status": "under_budget",
                "category_count": 5
            }
        }
```

### Investment Category Models

```python
class InvestmentCategory(BaseModel):
    """Investment subcategory model"""
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., min_length=1, max_length=100, description="Display name")
    description: str = Field(..., max_length=200, description="Category description")
    purpose: str = Field(..., max_length=200, description="Investment purpose")
    budget: Decimal = Field(..., ge=0, description="Budget amount")
    actual: Decimal = Field(..., ge=0, description="Actual invested amount")
    difference: Decimal = Field(..., description="Budget - Actual")
    status: CategoryStatus = Field(..., description="Status indicator")
    transaction_count: int = Field(..., ge=0, description="Number of transactions")
    last_transaction_date: Optional[datetime] = Field(None, description="Last transaction")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "bank_deposits",
                "name": "Bank Deposits",
                "description": "Fixed deposits, savings accounts",
                "purpose": "Secure, low-risk savings",
                "budget": 250.00,
                "actual": 200.00,
                "difference": 50.00,
                "status": "under_budget",
                "transaction_count": 3,
                "last_transaction_date": "2025-10-10T14:20:00Z"
            }
        }
```

### Transaction Models

```python
class Transaction(BaseModel):
    """Investment transaction model"""
    id: str = Field(..., description="Unique identifier")
    allocation_id: str = Field(..., description="Parent allocation ID")
    category_id: str = Field(..., description="Investment category ID")
    category_name: str = Field(..., description="Category display name")
    type: TransactionType = Field(..., description="Transaction type")
    amount: Decimal = Field(..., gt=0, description="Transaction amount")
    currency: str = Field(default="INR", max_length=3, description="Currency code")
    description: str = Field(..., min_length=1, max_length=200)
    notes: Optional[str] = Field(None, max_length=500)
    transaction_date: datetime = Field(..., description="Transaction date")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "txn_001",
                "allocation_id": "freedom",
                "category_id": "bank_deposits",
                "category_name": "Bank Deposits",
                "type": "investment",
                "amount": 100.00,
                "currency": "INR",
                "description": "Fixed Deposit - HDFC Bank",
                "notes": "5 year FD at 7.5% interest",
                "transaction_date": "2025-10-10T14:20:00Z",
                "created_at": "2025-10-10T14:20:00Z",
                "updated_at": "2025-10-10T14:20:00Z"
            }
        }


class TransactionCreate(BaseModel):
    """Create transaction request model"""
    type: TransactionType = Field(..., description="Transaction type")
    amount: Decimal = Field(..., gt=0, description="Transaction amount")
    currency: str = Field(default="INR", max_length=3, description="Currency code")
    description: str = Field(..., min_length=1, max_length=200)
    notes: Optional[str] = Field(None, max_length=500)
    transaction_date: datetime = Field(..., description="Transaction date")

    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v
```

### Response Models

```python
class AllocationsResponse(BaseModel):
    """Response model for get all allocations"""
    status: str = Field(default="success")
    data: dict
    timestamp: datetime


class AllocationDetailResponse(BaseModel):
    """Response model for allocation detail"""
    status: str = Field(default="success")
    data: dict
    timestamp: datetime


class TransactionsResponse(BaseModel):
    """Response model for transactions list"""
    status: str = Field(default="success")
    data: dict
    timestamp: datetime


class TransactionCreateResponse(BaseModel):
    """Response model for transaction creation"""
    status: str = Field(default="success")
    message: str
    data: dict
    timestamp: datetime


class BudgetUpdateResponse(BaseModel):
    """Response model for budget update"""
    status: str = Field(default="success")
    message: str
    data: dict
    timestamp: datetime


class AnalyticsResponse(BaseModel):
    """Response model for analytics"""
    status: str = Field(default="success")
    data: dict
    timestamp: datetime
```

---

## Error Responses

### FastAPI Error Handling

```python
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

class CustomException(Exception):
    """Base custom exception"""
    def __init__(self, code: str, message: str, status_code: int, details: dict = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


@app.exception_handler(CustomException)
async def custom_exception_handler(request, exc: CustomException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    )
```

### Standard Error Format

```json
{
  "status": "error",
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Allocation with ID 'invalid_id' not found",
    "details": {
      "allocation_id": "invalid_id"
    }
  },
  "timestamp": "2025-10-15T10:30:00Z"
}
```

### Error Codes

| Code                 | HTTP Status | Description                             |
| -------------------- | ----------- | --------------------------------------- |
| `UNAUTHORIZED`       | 401         | Invalid or missing authentication token |
| `FORBIDDEN`          | 403         | Insufficient permissions                |
| `RESOURCE_NOT_FOUND` | 404         | Requested resource not found            |
| `VALIDATION_ERROR`   | 422         | Request validation failed (Pydantic)    |
| `BUDGET_EXCEEDED`    | 400         | Transaction exceeds available budget    |
| `INVALID_AMOUNT`     | 400         | Amount must be positive number          |
| `INVALID_DATE`       | 400         | Invalid date format                     |
| `INTERNAL_ERROR`     | 500         | Internal server error                   |

### Example Error Responses

**Unauthorized:**

```json
{
  "status": "error",
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication token is missing or invalid"
  },
  "timestamp": "2025-10-15T10:30:00Z"
}
```

**Pydantic Validation Error (422):**

```json
{
  "detail": [
    {
      "loc": ["body", "amount"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt",
      "ctx": { "limit_value": 0 }
    },
    {
      "loc": ["body", "description"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Custom Validation Error (400):**

```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "fields": {
        "amount": "Amount must be a positive number",
        "description": "Description is required"
      }
    }
  },
  "timestamp": "2025-10-15T10:30:00Z"
}
```

**Budget Exceeded:**

```json
{
  "status": "error",
  "error": {
    "code": "BUDGET_EXCEEDED",
    "message": "Transaction amount exceeds available budget",
    "details": {
      "requestedAmount": 500.0,
      "availableBudget": 50.0,
      "currentActual": 200.0,
      "totalBudget": 250.0
    }
  },
  "timestamp": "2025-10-15T10:30:00Z"
}
```

---

## Validation

### Pydantic Validators

FastAPI uses Pydantic for automatic request validation:

```python
from pydantic import BaseModel, Field, validator, root_validator
from decimal import Decimal
from datetime import datetime

class TransactionCreate(BaseModel):
    amount: Decimal = Field(..., gt=0, description="Transaction amount")
    description: str = Field(..., min_length=1, max_length=200)
    transaction_date: datetime

    @validator('amount')
    def validate_amount(cls, v):
        """Validate amount is positive and reasonable"""
        if v <= 0:
            raise ValueError('Amount must be positive')
        if v > 1000000:
            raise ValueError('Amount exceeds maximum limit')
        return v

    @validator('transaction_date')
    def validate_date(cls, v):
        """Validate transaction date is not in future"""
        if v > datetime.utcnow():
            raise ValueError('Transaction date cannot be in future')
        return v

    @root_validator
    def validate_transaction(cls, values):
        """Cross-field validation"""
        amount = values.get('amount')
        description = values.get('description')

        if amount and amount > 10000 and not description:
            raise ValueError('Large transactions require description')

        return values
```

### Custom Validators

```python
from typing import Any
from pydantic import validator

class AllocationBudget(BaseModel):
    budget: Decimal = Field(..., gt=0)

    @validator('budget')
    def validate_budget(cls, v: Decimal) -> Decimal:
        """Ensure budget is reasonable"""
        if v < 100:
            raise ValueError('Budget must be at least 100')
        if v > 100000:
            raise ValueError('Budget exceeds maximum allowed')
        # Round to 2 decimal places
        return round(v, 2)
```

### Validation Error Handling

```python
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom handler for Pydantic validation errors"""
    errors = {}
    for error in exc.errors():
        field = error['loc'][-1]
        errors[field] = error['msg']

    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": {"fields": errors}
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    )
```

---

## Database Models (SQLAlchemy)

### Base Configuration

```python
from sqlalchemy import Column, String, Numeric, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()
```

### Allocation Table

```python
class AllocationDB(Base):
    """SQLAlchemy model for allocations"""
    __tablename__ = "allocations"

    id = Column(String(50), primary_key=True)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, index=True)
    label = Column(String(50), nullable=False)
    description = Column(String(200), nullable=False)
    icon = Column(String(50), nullable=False)
    icon_color = Column(String(7), nullable=False)
    target_percentage = Column(Numeric(5, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    categories = relationship("InvestmentCategoryDB", back_populates="allocation", cascade="all, delete-orphan")
    user = relationship("UserDB", back_populates="allocations")
```

### Investment Category Table

```python
class InvestmentCategoryDB(Base):
    """SQLAlchemy model for investment categories"""
    __tablename__ = "investment_categories"

    id = Column(String(50), primary_key=True)
    allocation_id = Column(String(50), ForeignKey("allocations.id"), nullable=False, index=True)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(200), nullable=False)
    purpose = Column(String(200), nullable=False)
    budget = Column(Numeric(12, 2), nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    allocation = relationship("AllocationDB", back_populates="categories")
    transactions = relationship("TransactionDB", back_populates="category", cascade="all, delete-orphan")
    user = relationship("UserDB", back_populates="categories")
```

### Transaction Table

```python
class TransactionDB(Base):
    """SQLAlchemy model for transactions"""
    __tablename__ = "transactions"

    id = Column(String(50), primary_key=True)
    allocation_id = Column(String(50), ForeignKey("allocations.id"), nullable=False, index=True)
    category_id = Column(String(50), ForeignKey("investment_categories.id"), nullable=False, index=True)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, index=True)
    type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="INR")
    description = Column(String(200), nullable=False)
    notes = Column(String(500), nullable=True)
    transaction_date = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    category = relationship("InvestmentCategoryDB", back_populates="transactions")
    user = relationship("UserDB", back_populates="transactions")
```

---

## Middleware & CORS

### CORS Configuration

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="WealthWarriorsHub API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://wealthwarriorshub.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Request Logging Middleware

```python
import time
from fastapi import Request

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing"""
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    print(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")

    return response
```

### Authentication Middleware

```python
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """Validate JWT token for protected routes"""
    if request.url.path.startswith("/api/v1/allocations"):
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authentication token"
            )

    response = await call_next(request)
    return response
```

---

## Status Calculation Rules

### Allocation Status

```
if (actual < budget): status = "under_budget"
if (actual == budget): status = "on_budget"
if (actual > budget): status = "over_budget"
```

### Overall Status

```
if (totalDifference >= 200): overallStatus = "excellent"
if (totalDifference >= 100): overallStatus = "good"
if (totalDifference >= 0): overallStatus = "fair"
if (totalDifference < 0): overallStatus = "needs_attention"
```

---

## Rate Limiting

- **Rate Limit:** 1000 requests per hour per user
- **Rate Limit Headers:**
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Unix timestamp when limit resets

**Example:**

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1697368800
```

---

## Versioning

API version is specified in the URL path:

- Current version: `v1`
- Format: `/v{version}/{endpoint}`

---

## Project Structure

### Recommended FastAPI Project Layout

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database connection
│   ├── dependencies.py         # Shared dependencies
│   │
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── allocation.py
│   │   ├── category.py
│   │   ├── transaction.py
│   │   └── user.py
│   │
│   ├── schemas/                # Pydantic models
│   │   ├── __init__.py
│   │   ├── allocation.py
│   │   ├── category.py
│   │   ├── transaction.py
│   │   └── response.py
│   │
│   ├── routers/                # API routes
│   │   ├── __init__.py
│   │   ├── allocations.py
│   │   ├── transactions.py
│   │   ├── analytics.py
│   │   └── auth.py
│   │
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── allocation_service.py
│   │   ├── transaction_service.py
│   │   └── analytics_service.py
│   │
│   └── utils/                  # Utilities
│       ├── __init__.py
│       ├── security.py
│       └── validators.py
│
├── alembic/                    # Database migrations
│   ├── versions/
│   └── env.py
│
├── tests/                      # Unit tests
│   ├── test_allocations.py
│   ├── test_transactions.py
│   └── test_analytics.py
│
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
└── alembic.ini                 # Alembic configuration
```

---

## Dependencies (requirements.txt)

```txt
# FastAPI Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Pydantic
pydantic==2.5.0
pydantic-settings==2.1.0

# Database
sqlalchemy==2.0.23
alembic==1.13.0
psycopg2-binary==2.9.9
asyncpg==0.29.0

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-decouple==3.8

# Utilities
python-dotenv==1.0.0
```

---

## Environment Variables

```bash
# .env file
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/wealthwarriors
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://wealthwarriorshub.com

# API Settings
API_V1_PREFIX=/api/v1
PROJECT_NAME=WealthWarriorsHub API
```

---

## Running the Application

### Development Mode

```bash
# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
# Using Gunicorn with Uvicorn workers
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

---

## Notes

### Technical Standards

1. **Decimal Precision:** All monetary amounts use Python `Decimal` type with 2 decimal places
2. **Timestamps:** ISO 8601 format with UTC timezone (`datetime.utcnow()`)
3. **Currency Codes:** ISO 4217 standard (default: INR)
4. **Content Type:** All endpoints return `application/json`
5. **Snake Case:** Use snake_case for field names (FastAPI converts to camelCase if needed)
6. **Async/Await:** All database operations use async patterns
7. **Type Hints:** All functions use Python type hints for automatic validation

### Best Practices

1. **Use dependency injection** for database sessions and authentication
2. **Separate business logic** into service layer
3. **Keep routers thin** - delegate to services
4. **Use Pydantic validators** for custom validation rules
5. **Write comprehensive tests** for all endpoints
6. **Document all endpoints** with docstrings and examples
7. **Use Alembic** for database migrations
8. **Implement proper logging** at all levels
9. **Handle exceptions** with custom exception handlers
10. **Use environment variables** for configuration

### Performance

- **Connection Pooling:** SQLAlchemy connection pool (default: 5-20 connections)
- **Async Database:** Use asyncpg for PostgreSQL async operations
- **Response Caching:** Implement Redis caching for frequently accessed data
- **Query Optimization:** Use SQLAlchemy eager loading to prevent N+1 queries
- **Pagination:** Always paginate list endpoints (default: 20 items per page)

---

**Last Updated:** October 15, 2025
**Version:** 1.0.0
**Backend:** Python FastAPI
**Contact:** api-support@wealthwarriorshub.com
