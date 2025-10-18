"""
Run database migration to add investment allocation tables and seed data.
Creates allocation_categories, allocation_types, and user_allocations tables.
"""
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:JAnKfltpThXSYIdv@db.qfcnomdgpcpnsibihwvm.supabase.co:5432/postgres")

print(f"🔄 Connecting to Supabase database...")
engine = create_engine(DATABASE_URL)

# Read migration file
migration_file = "migrations/003_add_allocations.sql"
print(f"📝 Reading migration file: {migration_file}")

try:
    with open(migration_file, "r") as f:
        migration_sql = f.read()
except FileNotFoundError:
    print(f"❌ Migration file not found: {migration_file}")
    sys.exit(1)

print(f"📝 Running migration...")

try:
    with engine.connect() as conn:
        # Execute the entire migration as a single transaction
        conn.execute(text(migration_sql))
        conn.commit()

        print("\n✅ Migration completed successfully!")

        # Verify categories created
        print("\n🔍 Verifying allocation categories...")
        result = conn.execute(text("""
            SELECT name, label, target_percentage
            FROM allocation_categories
            ORDER BY sort_order
        """))

        print("\n📊 Allocation Categories:")
        for row in result:
            print(f"   - {row[1]}: {row[2]}%")

        # Count types
        print("\n🔍 Verifying allocation types...")
        result = conn.execute(text("""
            SELECT
                ac.label as category,
                COUNT(at.id) as types_count
            FROM allocation_categories ac
            LEFT JOIN allocation_types at ON ac.id = at.category_id
            GROUP BY ac.label, ac.sort_order
            ORDER BY ac.sort_order
        """))

        print("\n📊 Investment Types per Category:")
        total_types = 0
        for row in result:
            print(f"   - {row[0]}: {row[1]} types")
            total_types += row[1]

        print(f"\n   Total Investment Types: {total_types}")

        # Verify tables exist
        print("\n🔍 Verifying tables created...")
        result = conn.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name IN ('allocation_categories', 'allocation_types', 'user_allocations')
            ORDER BY table_name
        """))

        print("\n📊 Tables created:")
        for row in result:
            print(f"   ✓ {row[0]}")

except Exception as e:
    print(f"\n❌ Migration failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    engine.dispose()

print("\n✅ All done! Allocation tables are ready.")
print("\n🚀 You can now use the API endpoints:")
print("   - GET /api/v1/allocations")
print("   - GET /api/v1/allocations/{allocation_id}")
