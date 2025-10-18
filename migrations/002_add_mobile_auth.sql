-- Mobile Authentication Migration
-- Adds mobile_number support and makes email/password optional
-- Run this on existing databases to update users table

-- Step 1: Add mobile_number column (temporarily nullable for existing users)
ALTER TABLE users ADD COLUMN IF NOT EXISTS mobile_number VARCHAR(10);

-- Step 2: Add unique index on mobile_number
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_mobile_number ON users(mobile_number);

-- Step 3: Make email nullable (for mobile-only users)
ALTER TABLE users ALTER COLUMN email DROP NOT NULL;

-- Step 4: Make hashed_password nullable (for OTP-only authentication)
ALTER TABLE users ALTER COLUMN hashed_password DROP NOT NULL;

-- Note: For existing users, you'll need to manually populate mobile_number
-- Then run: ALTER TABLE users ALTER COLUMN mobile_number SET NOT NULL;

-- Verify changes
SELECT column_name, is_nullable, data_type
FROM information_schema.columns
WHERE table_name = 'users'
  AND column_name IN ('mobile_number', 'email', 'hashed_password')
ORDER BY column_name;
