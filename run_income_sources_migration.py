"""Run income sources migration on Supabase."""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not found in environment variables")
    exit(1)

print("🔌 Connecting to Supabase...")
engine = create_engine(DATABASE_URL)

# Read migration file
with open("migrations/005_add_income_sources.sql", "r") as f:
    migration_sql = f.read()

print("📝 Running migration...")
try:
    with engine.connect() as conn:
        # Execute migration
        conn.execute(text(migration_sql))
        conn.commit()
        print("✅ Migration completed successfully!")

        # Verify column addition
        result = conn.execute(text("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'monthly_budgets'
            AND column_name = 'income_sources'
        """))

        if result.fetchone():
            print("✅ Column 'income_sources' added successfully")
        else:
            print("❌ Column addition failed")

except Exception as e:
    print(f"❌ Migration failed: {e}")
finally:
    engine.dispose()
