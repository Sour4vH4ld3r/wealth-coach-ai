"""Run monthly budget migration on Supabase."""
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
with open("migrations/004_add_monthly_budgets.sql", "r") as f:
    migration_sql = f.read()

print("📝 Running migration...")
try:
    with engine.connect() as conn:
        # Execute migration
        conn.execute(text(migration_sql))
        conn.commit()
        print("✅ Migration completed successfully!")

        # Verify table creation
        result = conn.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_name = 'monthly_budgets'
        """))

        if result.fetchone():
            print("✅ Table 'monthly_budgets' created successfully")
        else:
            print("❌ Table creation failed")

except Exception as e:
    print(f"❌ Migration failed: {e}")
finally:
    engine.dispose()
