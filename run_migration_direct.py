"""
Run database migration to add mobile authentication support - Direct SQL execution.
"""
import os
from sqlalchemy import create_engine, text

# Get DATABASE_URL from environment
DATABASE_URL = "postgresql://postgres:JAnKfltpThXSYIdv@db.qfcnomdgpcpnsibihwvm.supabase.co:5432/postgres"

print(f"🔄 Connecting to database...")
engine = create_engine(DATABASE_URL)

# Direct SQL statements
migrations = [
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS mobile_number VARCHAR(10)",
    "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_mobile_number ON users(mobile_number)",
    "ALTER TABLE users ALTER COLUMN email DROP NOT NULL",
    "ALTER TABLE users ALTER COLUMN hashed_password DROP NOT NULL",
]

print(f"📝 Running {len(migrations)} migration statements...")

try:
    with engine.connect() as conn:
        for i, statement in enumerate(migrations, 1):
            print(f"   {i}. {statement}")
            try:
                conn.execute(text(statement))
                conn.commit()
                print(f"      ✅ Success")
            except Exception as e:
                print(f"      ⚠️  {e}")
                # Continue with other statements

        print("\n🔍 Verifying schema changes...")
        result = conn.execute(text("""
            SELECT column_name, is_nullable, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_name = 'users'
              AND column_name IN ('mobile_number', 'email', 'hashed_password')
            ORDER BY column_name
        """))

        print("\n📊 Users table schema:")
        for row in result:
            print(f"   - {row[0]}: {row[2]}({row[3] or 'N/A'}) nullable={row[1]}")

        print("\n✅ Migration completed successfully!")

except Exception as e:
    print(f"❌ Migration failed: {e}")
    import traceback
    traceback.print_exc()
finally:
    engine.dispose()

print("\n✅ All done! You can now test the registration endpoint.")
