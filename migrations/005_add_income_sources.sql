-- Add income_sources column to monthly_budgets table
ALTER TABLE monthly_budgets
ADD COLUMN IF NOT EXISTS income_sources JSONB;

-- Add comment for documentation
COMMENT ON COLUMN monthly_budgets.income_sources IS 'Array of income source objects with category, amount, and label fields';
