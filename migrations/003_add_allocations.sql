-- Investment Allocation Tables Migration
-- Creates tables for allocation categories, types, and user allocations
-- Includes seed data for 6 categories and 34 investment types

-- ============================================================================
-- Step 1: Create allocation_categories table
-- ============================================================================
CREATE TABLE IF NOT EXISTS allocation_categories (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    label VARCHAR(100) NOT NULL,
    icon VARCHAR(50) NOT NULL,
    icon_color VARCHAR(20) NOT NULL,
    description TEXT,
    target_percentage NUMERIC(5, 2) NOT NULL,
    sort_order INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create index on name for faster lookups
CREATE INDEX IF NOT EXISTS idx_allocation_categories_name ON allocation_categories(name);

-- ============================================================================
-- Step 2: Create allocation_types table
-- ============================================================================
CREATE TABLE IF NOT EXISTS allocation_types (
    id VARCHAR(36) PRIMARY KEY,
    category_id VARCHAR(36) NOT NULL REFERENCES allocation_categories(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    purpose VARCHAR(200),
    sort_order INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_allocation_types_category_id ON allocation_types(category_id);
CREATE INDEX IF NOT EXISTS idx_allocation_types_sort_order ON allocation_types(category_id, sort_order);

-- ============================================================================
-- Step 3: Create user_allocations table
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_allocations (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    allocation_type_id VARCHAR(36) NOT NULL REFERENCES allocation_types(id) ON DELETE CASCADE,
    budget_amount NUMERIC(15, 2) DEFAULT 0.00 NOT NULL,
    actual_amount NUMERIC(15, 2) DEFAULT 0.00 NOT NULL,
    month INTEGER NOT NULL CHECK (month >= 1 AND month <= 12),
    year INTEGER NOT NULL CHECK (year >= 2020 AND year <= 2100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE (user_id, allocation_type_id, month, year)
);

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_user_allocations_user_id ON user_allocations(user_id);
CREATE INDEX IF NOT EXISTS idx_user_allocations_type_id ON user_allocations(allocation_type_id);
CREATE INDEX IF NOT EXISTS idx_user_allocations_month_year ON user_allocations(month, year);
CREATE INDEX IF NOT EXISTS idx_user_allocations_user_month_year ON user_allocations(user_id, month, year);

-- ============================================================================
-- Step 4: Seed Allocation Categories (6 categories)
-- ============================================================================
INSERT INTO allocation_categories (id, name, label, icon, icon_color, description, target_percentage, sort_order)
VALUES
    (gen_random_uuid()::text, 'freedom', 'FREEDOM (Financial Independence)', '🏦', 'blue', 'Build your financial freedom fund for long-term wealth', 10.00, 1),
    (gen_random_uuid()::text, 'health', 'HEALTH (Healthcare & Wellness)', '❤️', 'red', 'Provision for Emergencies', 10.00, 2),
    (gen_random_uuid()::text, 'spending', 'SPENDING (Lifestyle)', '🛍️', 'green', 'Spending for Life Style', 50.00, 3),
    (gen_random_uuid()::text, 'learning', 'LEARNING (Education & Development)', '🎓', 'gold', 'Invest in education and skill development', 10.00, 4),
    (gen_random_uuid()::text, 'entertainment', 'ENTERTAINMENT (Fun & Leisure)', '🎮', 'red', 'Enjoy life with fun activities and entertainment', 5.00, 5),
    (gen_random_uuid()::text, 'contribution', 'CONTRIBUTION (Charity & Giving)', '🤲', 'blue', 'Give back to society and make a difference', 5.00, 6)
ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- Step 5: Seed Allocation Types (34 investment types)
-- ============================================================================

-- 5.1: FREEDOM Category (5 types)
INSERT INTO allocation_types (id, category_id, name, description, purpose, sort_order)
SELECT
    gen_random_uuid()::text,
    (SELECT id FROM allocation_categories WHERE name = 'freedom'),
    unnest(ARRAY['Bank Deposits', 'Mutual Funds', 'Shares & Stock', 'Real Estate', 'Capital in New Business']),
    unnest(ARRAY[
        'Fixed deposits, savings accounts',
        'Equity, debt, hybrid funds',
        'Direct equity investments',
        'Property investments',
        'Entrepreneurial investments'
    ]),
    unnest(ARRAY[
        'Secure, low-risk savings',
        'Diversified investments',
        'High-growth potential',
        'Long-term asset building',
        'Business ventures'
    ]),
    unnest(ARRAY[1, 2, 3, 4, 5]);

-- 5.2: HEALTH Category (5 types)
INSERT INTO allocation_types (id, category_id, name, description, purpose, sort_order)
SELECT
    gen_random_uuid()::text,
    (SELECT id FROM allocation_categories WHERE name = 'health'),
    unnest(ARRAY[
        'Mediclaim/Accident Policies',
        'Dr. Consultation/Medicines',
        'Hospitalization',
        'Elderly People Care Exp. With Treatment',
        'Repairs of House Hold & Disinfection'
    ]),
    unnest(ARRAY[
        'Health insurance premiums',
        'Regular medical expenses',
        'Emergency medical care costs',
        'Senior care expenses',
        'Home safety & hygiene'
    ]),
    unnest(ARRAY[
        'Medical coverage',
        'Routine healthcare',
        'Critical care fund',
        'Elder healthcare',
        'Preventive care'
    ]),
    unnest(ARRAY[1, 2, 3, 4, 5]);

-- 5.3: SPENDING Category (6 types)
INSERT INTO allocation_types (id, category_id, name, description, purpose, sort_order)
SELECT
    gen_random_uuid()::text,
    (SELECT id FROM allocation_categories WHERE name = 'spending'),
    unnest(ARRAY[
        'Marriage/Social Event Expenses',
        'College Education Fees',
        'LIC Premiums for Future Events',
        'Consumer Durables/Gym Exp.',
        'Gold Jewellery/Mobile/Laptop/Computer',
        'Vacation/Holidays'
    ]),
    unnest(ARRAY[
        'Celebrations & ceremonies',
        'Higher education costs',
        'Life insurance',
        'Appliances & fitness',
        'Electronics & jewelry',
        'Travel & tourism'
    ]),
    unnest(ARRAY[
        'Major life events',
        'Educational investment',
        'Future security',
        'Quality of life',
        'Assets & tools',
        'Life experiences'
    ]),
    unnest(ARRAY[1, 2, 3, 4, 5, 6]);

-- 5.4: LEARNING Category (8 types)
INSERT INTO allocation_types (id, category_id, name, description, purpose, sort_order)
SELECT
    gen_random_uuid()::text,
    (SELECT id FROM allocation_categories WHERE name = 'learning'),
    unnest(ARRAY[
        'School Fees',
        'College Fees',
        'Books for Personal/Professional/Buss. Dev.',
        'Hobby Classes for Any Member',
        'Seminars, Conference, Workshop',
        'Spiritual Retreat, Yoga',
        'Tuition Class, Personal Tutor/Coach',
        'Gym Fees'
    ]),
    unnest(ARRAY[
        'Primary/secondary education',
        'Higher education',
        'Learning materials',
        'Skill development',
        'Professional development',
        'Wellness education',
        'Private coaching',
        'Physical fitness'
    ]),
    unnest(ARRAY[
        'Basic education',
        'Degree programs',
        'Knowledge building',
        'Personal growth',
        'Career advancement',
        'Mental health',
        'Targeted learning',
        'Health & wellness'
    ]),
    unnest(ARRAY[1, 2, 3, 4, 5, 6, 7, 8]);

-- 5.5: ENTERTAINMENT Category (5 types)
INSERT INTO allocation_types (id, category_id, name, description, purpose, sort_order)
SELECT
    gen_random_uuid()::text,
    (SELECT id FROM allocation_categories WHERE name = 'entertainment'),
    unnest(ARRAY[
        'Cinema, Drama, Opera',
        'Outing, Picnic, Restaurant Bills',
        'Body Treatment /Spa/ Massage /Skin Treat',
        'Partying with Friends',
        'Ice Cream, Coffee House, Fast Foods, etc.'
    ]),
    unnest(ARRAY[
        'Entertainment shows',
        'Dining & outdoor activities',
        'Self-care',
        'Social gatherings',
        'Casual dining'
    ]),
    unnest(ARRAY[
        'Cultural experiences',
        'Social bonding',
        'Relaxation & wellness',
        'Social connections',
        'Simple pleasures'
    ]),
    unnest(ARRAY[1, 2, 3, 4, 5]);

-- 5.6: CONTRIBUTION Category (5 types)
INSERT INTO allocation_types (id, category_id, name, description, purpose, sort_order)
SELECT
    gen_random_uuid()::text,
    (SELECT id FROM allocation_categories WHERE name = 'contribution'),
    unnest(ARRAY[
        'Charity Donations',
        'Community Support',
        'NGO Contributions',
        'Social Causes',
        'Volunteering Expenses'
    ]),
    unnest(ARRAY[
        'Monetary donations',
        'Local community help',
        'Non-profit organizations',
        'Social welfare initiatives',
        'Cost of volunteering activities'
    ]),
    unnest(ARRAY[
        'Direct financial support',
        'Neighborhood assistance',
        'Organized social work',
        'Systemic change support',
        'Active participation'
    ]),
    unnest(ARRAY[1, 2, 3, 4, 5]);

-- ============================================================================
-- Step 6: Verification Queries
-- ============================================================================

-- Verify categories
SELECT 'Categories Created:' as check_type, COUNT(*) as count FROM allocation_categories;

-- Verify types per category
SELECT
    ac.label as category,
    COUNT(at.id) as types_count
FROM allocation_categories ac
LEFT JOIN allocation_types at ON ac.id = at.category_id
GROUP BY ac.label, ac.sort_order
ORDER BY ac.sort_order;

-- Total types
SELECT 'Total Investment Types:' as check_type, COUNT(*) as count FROM allocation_types;

-- ============================================================================
-- Step 7: Create trigger for updated_at timestamp
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to all allocation tables
DROP TRIGGER IF EXISTS update_allocation_categories_updated_at ON allocation_categories;
CREATE TRIGGER update_allocation_categories_updated_at
    BEFORE UPDATE ON allocation_categories
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_allocation_types_updated_at ON allocation_types;
CREATE TRIGGER update_allocation_types_updated_at
    BEFORE UPDATE ON allocation_types
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_user_allocations_updated_at ON user_allocations;
CREATE TRIGGER update_user_allocations_updated_at
    BEFORE UPDATE ON user_allocations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Migration Complete
-- ============================================================================
-- Summary:
-- ✅ Created 3 tables: allocation_categories, allocation_types, user_allocations
-- ✅ Seeded 6 allocation categories
-- ✅ Seeded 34 investment types
-- ✅ Created indexes for performance
-- ✅ Created triggers for updated_at timestamps
-- ✅ Ready for API endpoints
-- ============================================================================
