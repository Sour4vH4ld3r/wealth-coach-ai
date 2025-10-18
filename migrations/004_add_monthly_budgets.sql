-- Migration: Add monthly budgets table
-- Purpose: Store user's total monthly budget for auto-calculating category allocations
-- Date: 2025-10-16

-- Create monthly_budgets table
CREATE TABLE IF NOT EXISTS monthly_budgets (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    total_amount DECIMAL(15, 2) NOT NULL,
    month INTEGER NOT NULL CHECK (month >= 1 AND month <= 12),
    year INTEGER NOT NULL,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create unique index for one budget per user per month
CREATE UNIQUE INDEX IF NOT EXISTS idx_user_month_year
ON monthly_budgets(user_id, month, year);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_monthly_budgets_user_id ON monthly_budgets(user_id);
CREATE INDEX IF NOT EXISTS idx_monthly_budgets_month ON monthly_budgets(month);
CREATE INDEX IF NOT EXISTS idx_monthly_budgets_year ON monthly_budgets(year);

-- Comments
COMMENT ON TABLE monthly_budgets IS 'User total monthly budget for allocation calculations';
COMMENT ON COLUMN monthly_budgets.total_amount IS 'Total monthly budget in rupees';
COMMENT ON COLUMN monthly_budgets.month IS 'Month (1-12)';
COMMENT ON COLUMN monthly_budgets.year IS 'Year (e.g., 2025)';
