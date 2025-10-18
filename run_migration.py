"""
Run database migration to add mobile authentication support.
"""
import os
import sys
from sqlalchemy import create_engine, text

# Get DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:JAnKfltpThXSYIdv@db.qfcnomdgpcpnsibihwvm.supabase.co:5432/postgres")

print(f"🔄 Connecting to database...")
engine = create_engine(DATABASE_URL)

# Read migration file
with open("migrations/002_add_mobile_auth.sql", "r") as f:
    migration_sql = f.read()

# Split by statements (simple split by semicolon)
statements = [stmt.strip() for stmt in migration_sql.split(";") if stmt.strip() and not stmt.strip().startswith("--")]

print(f"📝 Running migration with {len(statements)} statements...")

try:
    with engine.connect() as conn:
        for i, statement in enumerate(statements, 1):
            if statement:
                print(f"   {i}. Executing: {statement[:60]}...")
                conn.execute(text(statement))
                conn.commit()

        print("✅ Migration completed successfully!")

        # Verify changes
        print("\n🔍 Verifying schema changes...")
        result = conn.execute(text("""
            SELECT column_name, is_nullable, data_type
            FROM information_schema.columns
            WHERE table_name = 'users'
              AND column_name IN ('mobile_number', 'email', 'hashed_password')
            ORDER BY column_name
        """))

        print("\n📊 Users table schema:")
        for row in result:
            print(f"   - {row[0]}: {row[2]} (nullable: {row[1]})")

except Exception as e:
    print(f"❌ Migration failed: {e}")
    sys.exit(1)
finally:
    engine.dispose()

print("\n✅ All done! You can now test the registration endpoint.")
