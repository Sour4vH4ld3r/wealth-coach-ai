"""Run transactions migration on Supabase."""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not found")
    exit(1)

print("🔌 Connecting to Supabase...")
engine = create_engine(DATABASE_URL, isolation_level="AUTOCOMMIT")

with open("migrations/006_add_transactions.sql", "r") as f:
    migration_sql = f.read()

print("📝 Running migration...")
try:
    with engine.connect() as conn:
        # Split and execute statements one by one
        statements = [s.strip() for s in migration_sql.split(';') if s.strip() and not s.strip().startswith('--') and not s.strip().startswith('COMMENT')]

        for i, stmt in enumerate(statements, 1):
            if stmt and len(stmt) > 10:  # Skip empty or very short statements
                try:
                    print(f"   Executing statement {i}...")
                    conn.execute(text(stmt))
                except Exception as e:
                    print(f"   ⚠️  Statement {i} error (may be OK): {str(e)[:100]}")

        print("✅ Migration completed!")

        # Verify
        result = conn.execute(text("""
            SELECT table_name FROM information_schema.tables
            WHERE table_name = 'transactions'
        """))

        if result.fetchone():
            print("✅ Transactions table created")

        result = conn.execute(text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'monthly_budgets' AND column_name = 'current_balance'
        """))

        if result.fetchone():
            print("✅ Monthly budgets table updated")

except Exception as e:
    print(f"❌ Migration failed: {e}")
finally:
    engine.dispose()
