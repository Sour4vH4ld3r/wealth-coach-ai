# 💰 WealthWarriors - Investment Allocation System

## 📱 Home Screen
**Dashboard:** Total Income | Total Expenses | Net Balance | 6 Category Progress Bars

## 🔄 User Flow

### Step 1: Add Transaction
Type: [Expense/Income] | Category: [Food/Transport/Others] | Amount: ₹___ | Date: 📅 | Description
**API:** `POST /api/v1/transactions`

### Step 2: Set Monthly Budget
User enters total income → System auto-calculates allocation breakdown
**API:** `POST /api/v1/budget`

### Step 3: Allocation Dashboard (Auto-Generated)

| Category | Icon | % | Amount | Status |
|----------|------|---|--------|--------|
| FREEDOM | 🏦 | 10% | ₹1,000 | 🟢 |
| HEALTH | ❤️ | 10% | ₹1,000 | 🟢 |
| SPENDING | 🛍️ | 50% | ₹5,000 | 🟡 |
| LEARNING | 🎓 | 10% | ₹1,000 | 🟢 |
| ENTERTAINMENT | 🎮 | 5% | ₹500 | 🟢 |
| CONTRIBUTION | 🤲 | 5% | ₹500 | 🟢 |

**API:** `GET /api/v1/allocations`

### Step 4: Category Detail (e.g., FREEDOM)
**Screen shows:**
- Target: 10% (₹1,000) | Budgeted: ₹950 | Actual: ₹800 | Remaining: ₹150
- **Investment Types:** Bank Deposits, Mutual Funds, Shares, Real Estate, Business Capital
- Each type shows: Budget | Actual | Difference (color-coded 🟢🔴)

**Button:** [Invest Now] → Opens modal

### Step 5: Investment Entry Modal
Select Type | Budget Amount | Actual Amount 
**API:** `POST /api/v1/allocations/actual`

## 🛠️ API Endpoints

### ✅ Built:
- `GET /api/v1/allocations` - All categories with user data
- `GET /api/v1/allocations/{id}` - Specific category details

### 🔨 To Build:
1. `POST /api/v1/allocations/budget` - Set budget breakdown
2. `POST /api/v1/allocations/actual` - Record actual spending/investment
3. `PUT /api/v1/allocations/{id}` - Update allocation entry
4. `DELETE /api/v1/allocations/{id}` - Remove entry
5. `GET /api/v1/allocations/summary` - Monthly analytics with insights
6. `GET /api/v1/allocations/history?months=6` - Historical data for charts

## 📊 Example Flow
User sets ₹10K budget → System: FREEDOM=₹1K → User clicks FREEDOM → Sees 5 investment types →
Clicks [Invest Now] → Enters: Bank₹250, Mutual₹180, Shares₹320 → Records actual throughout month →
Dashboard shows real-time progress with color indicators (🟢 Under budget, 🔴 Over budget)

## 🎯 Key Features
- **Auto-calculation:** Budget automatically distributed by category percentages
- **Real-time tracking:** Budget vs Actual with visual indicators
- **34 Investment types** across 6 categories
- **Monthly snapshots:** Historical data for trend analysis
- **Color-coded status:** Instant visual feedback on spending/investment patterns

if my monthly budget 10 thousend , then is devided into all catagory like freedom
  have 10% then 10k - 10% = 1000 rupees is the actuall amount for freedom . then i am
  desided 10 rupee or 100 rupee diposit bank , 100 rupee stocks etc. change the logic
  . and  