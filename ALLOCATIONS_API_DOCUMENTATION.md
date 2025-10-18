# 💰 WealthWarriors - Budget & Allocations API Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
All endpoints require JWT Bearer token in header:
```
Authorization: Bearer {your_access_token}
```

---

## 🔄 Transaction-Based Budget Flow

### New System Overview
Starting from ₹0 each month, track all income and expenses as transactions:

1. **Add Income Transactions** → Balance increases
2. **Add Expense Transactions** → Balance decreases
3. **View Current Balance** → See total income - total expenses

**Example:**
```
Start: ₹0
+ Income (Salary): ₹50,000 → Balance: ₹50,000
- Expense (Food): ₹1,000 → Balance: ₹49,000
+ Income (Freelance): ₹2,000 → Balance: ₹51,000
```

---

## 📋 API Endpoints

**Total Endpoints: 13**
- **Transaction Tracking:** 4 endpoints (POST, GET balance, GET list, DELETE)
- **Monthly Budget:** 1 endpoint (GET with auto-allocation)
- **Allocation Tracking:** 8 endpoints (GET all, GET by ID, POST budget, POST actual, PUT, DELETE, GET summary, GET history)

---

## 💳 TRANSACTION ENDPOINTS (Budget Tracking)

### 1. POST /transactions
**Add Income or Expense Transaction**

**Request:**
```json
{
  "type": "income",        // or "expense"
  "category": "salary",    // e.g., "salary", "food", "rent", "freelance"
  "amount": 50000,
  "label": "Monthly Salary",
  "transaction_date": "2025-10-16T10:00:00"
}
```

**Response (201):**
```json
{
  "id": "txn-uuid",
  "type": "income",
  "category": "salary",
  "amount": 50000.00,
  "label": "Monthly Salary",
  "transaction_date": "2025-10-16T10:00:00",
  "month": 10,
  "year": 2025,
  "created_at": "2025-10-16T10:00:00"
}
```

**Common Categories:**
- **Income:** salary, freelance, business, investment, rental
- **Expense:** food, rent, utilities, transport, entertainment, health

---

### 2. GET /transactions/balance
**Get Current Month Balance**

**Query Parameters:**
- `month` (optional): Month (1-12), defaults to current
- `year` (optional): Year, defaults to current

**Response (200):**
```json
{
  "month": 10,
  "year": 2025,
  "current_balance": 51000.00,
  "total_income": 52000.00,
  "total_expense": 1000.00,
  "transaction_count": 3
}
```

**Calculation:**
```
current_balance = total_income - total_expense
```

---

### 3. GET /transactions
**List All Transactions**

**Query Parameters:**
- `month` (optional): Filter by month (1-12), defaults to current
- `year` (optional): Filter by year, defaults to current
- `type` (optional): Filter by type ("income" or "expense")

**Response (200):**
```json
[
  {
    "id": "txn-3",
    "type": "income",
    "category": "freelance",
    "amount": 2000.00,
    "label": "Freelance project payment",
    "transaction_date": "2025-10-16T15:00:00",
    "month": 10,
    "year": 2025,
    "created_at": "2025-10-16T15:00:00"
  },
  {
    "id": "txn-2",
    "type": "expense",
    "category": "food",
    "amount": 1000.00,
    "label": "Groceries",
    "transaction_date": "2025-10-16T12:00:00",
    "month": 10,
    "year": 2025,
    "created_at": "2025-10-16T12:00:00"
  },
  {
    "id": "txn-1",
    "type": "income",
    "category": "salary",
    "amount": 50000.00,
    "label": "Monthly Salary",
    "transaction_date": "2025-10-16T10:00:00",
    "month": 10,
    "year": 2025,
    "created_at": "2025-10-16T10:00:00"
  }
]
```

**Note:** Transactions are ordered by date (newest first)

---

### 4. DELETE /transactions/{transaction_id}
**Delete a Transaction**

**Response (200):**
```json
{
  "message": "Transaction deleted successfully",
  "transaction_id": "txn-uuid"
}
```

**Note:** Deleting a transaction automatically updates the monthly balance:
- Income deleted → Balance decreases
- Expense deleted → Balance increases

---

### 5. GET /monthly-budget
**Get Monthly Budget with Auto-Calculated Category Allocations**

This endpoint combines transaction data with allocation categories to show:
- Current balance from transactions
- Auto-calculated allocation amounts per category
- Actual invested amounts from user allocations
- Status of each category (under/perfect/over)

**Response (200):**
```json
{
  "month": 10,
  "year": 2025,
  "current_balance": 51000.00,
  "total_income": 52000.00,
  "total_expense": 1000.00,
  "categories": [
    {
      "name": "freedom",
      "label": "FREEDOM (Financial Independence)",
      "icon": "🏦",
      "icon_color": "blue",
      "target_percentage": 10.0,
      "allocated_amount": 5100.00,     // Auto-calculated: current_balance × 10%
      "actual_invested": 750.00,       // From user allocations
      "difference": -4350.00,          // actual_invested - allocated_amount
      "status": "under"                // "under" | "perfect" | "over"
    },
    {
      "name": "health",
      "label": "HEALTH (Healthcare & Wellness)",
      "icon": "❤️",
      "icon_color": "red",
      "target_percentage": 10.0,
      "allocated_amount": 5100.00,
      "actual_invested": 0.00,
      "difference": -5100.00,
      "status": "under"
    },
    {
      "name": "spending",
      "label": "SPENDING (Lifestyle)",
      "icon": "🛍️",
      "icon_color": "green",
      "target_percentage": 50.0,
      "allocated_amount": 25500.00,
      "actual_invested": 0.00,
      "difference": -25500.00,
      "status": "under"
    },
    {
      "name": "learning",
      "label": "LEARNING (Education & Development)",
      "icon": "🎓",
      "icon_color": "gold",
      "target_percentage": 10.0,
      "allocated_amount": 5100.00,
      "actual_invested": 0.00,
      "difference": -5100.00,
      "status": "under"
    },
    {
      "name": "entertainment",
      "label": "ENTERTAINMENT (Fun & Leisure)",
      "icon": "🎮",
      "icon_color": "red",
      "target_percentage": 5.0,
      "allocated_amount": 2550.00,
      "actual_invested": 0.00,
      "difference": -2550.00,
      "status": "under"
    },
    {
      "name": "contribution",
      "label": "CONTRIBUTION (Charity & Giving)",
      "icon": "🤲",
      "icon_color": "blue",
      "target_percentage": 5.0,
      "allocated_amount": 2550.00,
      "actual_invested": 0.00,
      "difference": -2550.00,
      "status": "under"
    }
  ]
}
```

**How It Works:**
1. **Gets current_balance** from transactions (income - expense)
2. **Auto-calculates allocated_amount** = current_balance × target_percentage
   - FREEDOM (10%): ₹5,100 from ₹51,000
   - HEALTH (10%): ₹5,100
   - SPENDING (50%): ₹25,500
   - LEARNING (10%): ₹5,100
   - ENTERTAINMENT (5%): ₹2,550
   - CONTRIBUTION (5%): ₹2,550
3. **Compares with actual_invested** (sum of user allocations in category)
4. **Shows status**:
   - `"under"` - Invested less than allocated (difference < 0)
   - `"perfect"` - Invested exactly as allocated (difference = 0)
   - `"over"` - Invested more than allocated (difference > 0)

**Example Use Case:**
```
Current Balance: ₹51,000
FREEDOM allocation: ₹5,100 (10%)
User invested: ₹750 in Bank Deposits
Status: "under" by ₹4,350
```

---

## 📊 ALLOCATION TRACKING ENDPOINTS

These endpoints help track how you plan to allocate your income across 6 life categories.

### System Overview
The system uses a 6-category allocation framework:

| Category | Percentage | Description |
|----------|------------|-------------|
| 🏦 FREEDOM | 10% | Financial Independence (Savings, Investments) |
| ❤️ HEALTH | 10% | Healthcare & Wellness |
| 🛍️ SPENDING | 50% | Lifestyle & Daily Expenses |
| 🎓 LEARNING | 10% | Education & Development |
| 🎮 ENTERTAINMENT | 5% | Fun & Leisure |
| 🤲 CONTRIBUTION | 5% | Charity & Giving |

---

### 6. GET /allocations
**Get All Allocation Categories with Investment Types**

**Response (200):**
```json
{
  "month": 10,
  "year": 2025,
  "total_budget": 0.00,
  "total_actual": 0.00,
  "total_difference": 0.00,
  "target_allocation_percentage": 100.00,
  "categories": [
    {
      "id": "cat-freedom",
      "name": "FREEDOM",
      "label": "FREEDOM (Financial Independence)",
      "icon": "🏦",
      "icon_color": "blue",
      "description": "Financial Independence through savings and investments",
      "target_percentage": 10.00,
      "sort_order": 1,
      "total_budget": 0.00,
      "total_actual": 0.00,
      "total_difference": 0.00,
      "allocation_types": [
        {
          "id": "type-bank-deposits",
          "name": "Bank Deposits",
          "description": "Fixed Deposits, Savings Accounts",
          "purpose": "Secure, low-risk savings",
          "sort_order": 1,
          "budget_amount": 0.00,
          "actual_amount": 0.00,
          "difference": 0.00
        },
        {
          "id": "type-stocks",
          "name": "Stocks",
          "description": "Direct equity investments",
          "purpose": "High growth potential",
          "sort_order": 2,
          "budget_amount": 0.00,
          "actual_amount": 0.00,
          "difference": 0.00
        }
        // ... more investment types
      ]
    }
    // ... 5 more categories
  ]
}
```

---

### 7. GET /allocations/{allocation_id}
**Get Specific Investment Type**

**Response (200):**
```json
{
  "id": "type-bank-deposits",
  "category_id": "cat-freedom",
  "category_name": "FREEDOM",
  "name": "Bank Deposits",
  "description": "Fixed Deposits, Savings Accounts",
  "purpose": "Secure, low-risk savings",
  "budget_amount": 0.00,
  "actual_amount": 0.00,
  "difference": 0.00,
  "month": 10,
  "year": 2025
}
```

---

### 8. POST /allocations/budget
**Set Budget for Investment Type**

**Request:**
```json
{
  "allocation_type_id": "type-bank-deposits",
  "budget_amount": 400
}
```

**Response (200):**
```json
{
  "id": "user-alloc-uuid",
  "allocation_type_id": "type-bank-deposits",
  "allocation_type_name": "Bank Deposits",
  "category_name": "FREEDOM",
  "budget_amount": 400.00,
  "actual_amount": 0.00,
  "difference": -400.00,
  "month": 10,
  "year": 2025
}
```

---

### 9. POST /allocations/actual
**Record Actual Investment Amount**

**Request:**
```json
{
  "allocation_type_id": "type-bank-deposits",
  "actual_amount": 400,
  "notes": "FD opened at 7% interest"
}
```

**Response (200):**
```json
{
  "id": "user-alloc-uuid",
  "allocation_type_id": "type-bank-deposits",
  "allocation_type_name": "Bank Deposits",
  "category_name": "FREEDOM",
  "budget_amount": 400.00,
  "actual_amount": 400.00,
  "difference": 0.00,
  "notes": "FD opened at 7% interest",
  "month": 10,
  "year": 2025
}
```

---

### 10. PUT /allocations/{allocation_id}
**Update Budget or Actual Amount**

**Request:**
```json
{
  "budget_amount": 500,
  "actual_amount": 450,
  "notes": "Increased allocation"
}
```

**Response (200):**
```json
{
  "id": "alloc-uuid",
  "allocation_type_name": "Bank Deposits",
  "category_name": "FREEDOM",
  "budget_amount": 500.00,
  "actual_amount": 450.00,
  "difference": -50.00,
  "notes": "Increased allocation"
}
```

---

### 11. DELETE /allocations/{allocation_id}
**Delete User Allocation**

**Response (200):**
```json
{
  "message": "Allocation deleted successfully"
}
```

---

### 12. GET /allocations/summary
**Get Monthly Allocation Summary**

**Response (200):**
```json
{
  "month": 10,
  "year": 2025,
  "total_budget": 1000.00,
  "total_actual": 900.00,
  "total_difference": -100.00,
  "categories": [
    {
      "name": "FREEDOM",
      "label": "FREEDOM (Financial Independence)",
      "icon": "🏦",
      "target_percentage": 10.00,
      "total_budget": 1000.00,
      "total_actual": 900.00,
      "total_difference": -100.00,
      "allocation_types_count": 5
    }
    // ... other categories
  ]
}
```

---

### 13. GET /allocations/history
**Get Historical Allocation Data**

**Query Parameters:**
- `months` (optional): Number of past months (default: 6)

**Response (200):**
```json
[
  {
    "month": 10,
    "year": 2025,
    "total_budget": 1000.00,
    "total_actual": 900.00,
    "difference": -100.00
  },
  {
    "month": 9,
    "year": 2025,
    "total_budget": 950.00,
    "total_actual": 950.00,
    "difference": 0.00
  }
  // ... previous months
]
```

---

## 🔄 Complete Workflow Example

### Month Start (October 2025)

**1. Check Initial Balance**
```bash
GET /transactions/balance
# Response: balance = ₹0
```

**2. Add Income - Salary**
```bash
POST /transactions
{
  "type": "income",
  "category": "salary",
  "amount": 50000,
  "label": "Monthly Salary",
  "transaction_date": "2025-10-01T09:00:00"
}
# Balance now: ₹50,000
```

**3. Check Auto-Calculated Allocations**
```bash
GET /monthly-budget
# Response shows:
# - Current Balance: ₹50,000
# - FREEDOM allocated: ₹5,000 (10%)
# - HEALTH allocated: ₹5,000 (10%)
# - SPENDING allocated: ₹25,000 (50%)
# - etc.
```

**4. Invest in Freedom Category**
```bash
POST /allocations/actual
{
  "allocation_type_id": "type-bank-deposits",
  "actual_amount": 5000,
  "notes": "Fixed Deposit opened"
}
```

**5. Track Daily Expenses**
```bash
POST /transactions
{
  "type": "expense",
  "category": "food",
  "amount": 500,
  "label": "Grocery shopping",
  "transaction_date": "2025-10-02T18:00:00"
}
# Balance now: ₹49,500
```

**6. Add Freelance Income**
```bash
POST /transactions
{
  "type": "income",
  "category": "freelance",
  "amount": 5000,
  "label": "Website project",
  "transaction_date": "2025-10-15T14:00:00"
}
# Balance now: ₹54,500
```

**7. Month-End Review**
```bash
# View auto-calculated allocations with status
GET /monthly-budget
# See: current_balance, allocated amounts, actual_invested, status

# View detailed transactions
GET /transactions/balance
# See: total_income, total_expense, current_balance

# Review all expenses
GET /transactions?type=expense
# Review all expenses for the month
```

---

## 📱 Mobile App Integration

### Key Features to Implement:

1. **Dashboard Screen**
   - Current balance (from `/transactions/balance`)
   - Quick add income/expense buttons
   - Recent transactions list

2. **Add Transaction Screen**
   - Type selector: Income / Expense
   - Category dropdown (customizable)
   - Amount input
   - Label/description
   - Date picker (default: today)

3. **Transactions List Screen**
   - Filter by type, category, date range
   - Pull to refresh
   - Swipe to delete

4. **Allocations Screen**
   - 6 categories with percentages
   - Budget vs Actual progress bars
   - Drill down to investment types

5. **Reports Screen**
   - Monthly balance chart
   - Income vs Expense pie chart
   - Category allocation breakdown
   - Historical trends

---

## 🔐 Error Handling

All endpoints return consistent error formats:

**401 Unauthorized:**
```json
{
  "detail": "Could not validate credentials"
}
```

**400 Bad Request:**
```json
{
  "detail": "Type must be 'income' or 'expense'"
}
```

**404 Not Found:**
```json
{
  "detail": "Transaction not found"
}
```

**422 Validation Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "amount"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

---

## 🎯 Best Practices

1. **Transaction Dates:** Always use ISO 8601 format with timezone
2. **Amount Validation:** Amounts must always be positive (use type field for direction)
3. **Categories:** Keep consistent category names across transactions
4. **Labels:** Provide meaningful descriptions for better tracking
5. **Monthly Reset:** System automatically starts each month at ₹0
6. **Balance Calculation:** Always server-calculated, never client-side

---

## 📊 Category & Investment Types Reference

### FREEDOM (Financial Independence) - 10%
- Bank Deposits (FD, Savings)
- Stocks
- Mutual Funds
- Real Estate
- Gold/Precious Metals

### HEALTH (Healthcare & Wellness) - 10%
- Health Insurance
- Medical Expenses
- Fitness & Wellness
- Preventive Healthcare
- Emergency Medical Fund

### SPENDING (Lifestyle) - 50%
- Daily Essentials
- Utilities & Bills
- Transportation
- Dining & Entertainment
- Shopping

### LEARNING (Education) - 10%
- Books & Courses
- Professional Development
- Certifications
- Workshops & Seminars
- Educational Tools

### ENTERTAINMENT (Fun & Leisure) - 5%
- Hobbies
- Travel & Vacations
- Movies & Events
- Gaming
- Social Activities

### CONTRIBUTION (Giving Back) - 5%
- Charity & Donations
- Community Service
- Religious Contributions
- Supporting Causes
- Helping Others

---

## 🚀 Quick Start Checklist

- [ ] Get JWT token from login
- [ ] Check initial balance (`GET /transactions/balance`)
- [ ] Add first income transaction (`POST /transactions`)
- [ ] Verify balance updated
- [ ] Check auto-calculated allocations (`GET /monthly-budget`)
- [ ] Add expense transaction
- [ ] View transaction list
- [ ] Record actual investments (`POST /allocations/actual`)
- [ ] Review monthly budget with status (`GET /monthly-budget`)

---

## 📞 Support

For API issues or questions:
- Check server logs for detailed error messages
- Verify JWT token is valid and not expired
- Ensure all required fields are provided
- Validate date formats are correct

**Server:** Running at `http://192.168.1.10:8000`
**API Docs:** `http://192.168.1.10:8000/docs`
