-- Performance Optimization: Add indexes for fast queries
-- This will improve API response times from 400-1100ms to < 50ms

-- Transactions table: Composite index for user queries
-- Used by: GET /transactions, GET /transactions/balance
CREATE INDEX IF NOT EXISTS idx_transactions_user_month_year 
ON transactions(user_id, month, year, transaction_date DESC);

-- Monthly budgets table: Composite index
-- Used by: GET /transactions/balance, GET /monthly-budget
CREATE INDEX IF NOT EXISTS idx_monthly_budget_user_month_year 
ON monthly_budgets(user_id, month, year);

-- User allocations table: Composite index
-- Used by: GET /monthly-budget, GET /allocations
CREATE INDEX IF NOT EXISTS idx_user_allocations_user_month_year 
ON user_allocations(user_id, month, year);

-- User allocations: Index for allocation_type_id lookups
-- Used by: POST /allocations/budget, POST /allocations/actual
CREATE INDEX IF NOT EXISTS idx_user_allocations_allocation_type 
ON user_allocations(allocation_type_id);

-- Verify indexes created
SELECT 
    tablename,
    indexname,
    indexdef
FROM pg_indexes 
WHERE schemaname = 'public' 
    AND indexname LIKE 'idx_%'
ORDER BY tablename, indexname;
