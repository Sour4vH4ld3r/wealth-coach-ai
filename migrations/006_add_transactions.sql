-- Migration: Add transactions table and update monthly_budgets structure
-- This changes from budget planning to transaction tracking

-- Step 1: Backup existing monthly_budgets data (optional - comment out if not needed)
-- CREATE TABLE monthly_budgets_backup AS SELECT * FROM monthly_budgets;

-- Step 2: Drop old columns from monthly_budgets
ALTER TABLE monthly_budgets DROP COLUMN IF EXISTS total_amount;
ALTER TABLE monthly_budgets DROP COLUMN IF EXISTS income_sources;
ALTER TABLE monthly_budgets DROP COLUMN IF EXISTS notes;

-- Step 3: Add new columns to monthly_budgets
ALTER TABLE monthly_budgets ADD COLUMN IF NOT EXISTS current_balance DECIMAL(15, 2) DEFAULT 0.00 NOT NULL;
ALTER TABLE monthly_budgets ADD COLUMN IF NOT EXISTS total_income DECIMAL(15, 2) DEFAULT 0.00 NOT NULL;
ALTER TABLE monthly_budgets ADD COLUMN IF NOT EXISTS total_expense DECIMAL(15, 2) DEFAULT 0.00 NOT NULL;

-- Step 4: Create transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense')),
    category VARCHAR(50) NOT NULL,
    amount DECIMAL(15, 2) NOT NULL CHECK (amount > 0),
    label VARCHAR(200) NOT NULL,
    transaction_date TIMESTAMP NOT NULL,
    month INTEGER NOT NULL CHECK (month >= 1 AND month <= 12),
    year INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Step 5: Create indexes for transactions
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_transactions_month_year ON transactions(month, year);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type);

-- Step 6: Add comments
COMMENT ON TABLE transactions IS 'Income and expense transactions for budget tracking';
COMMENT ON COLUMN transactions.type IS 'Transaction type: income or expense';
COMMENT ON COLUMN transactions.transaction_date IS 'When the transaction occurred';
COMMENT ON COLUMN monthly_budgets.current_balance IS 'Current balance (total_income - total_expense)';
