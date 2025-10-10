#!/usr/bin/env python3
"""
Check pgvector Setup Status
Verifies pgvector is enabled and configured in Supabase
"""

import sys
sys.path.insert(0, ".")

from backend.core.config import settings
from backend.db.database import engine
from sqlalchemy import text


def main():
    print("=" * 70)
    print("pgvector Setup Status Check")
    print("=" * 70)
    print()

    try:
        with engine.connect() as conn:
            # Check 1: pgvector extension
            print("1️⃣  Checking pgvector extension...")
            result = conn.execute(text(
                "SELECT * FROM pg_extension WHERE extname = 'vector'"
            ))
            extension = result.fetchone()

            if extension:
                print("   ✅ pgvector extension is ENABLED")
            else:
                print("   ❌ pgvector extension is NOT enabled")
                print()
                print("   💡 To enable:")
                print("      1. Go to https://supabase.com/dashboard")
                print("      2. Select your project")
                print("      3. Database → Extensions")
                print("      4. Search 'vector' and click Enable")
                print()
                print("   Or run this SQL:")
                print("      CREATE EXTENSION IF NOT EXISTS vector;")
                print()
                return
            print()

            # Check 2: documents table
            print("2️⃣  Checking documents table...")
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'documents'
                )
            """))
            table_exists = result.scalar()

            if table_exists:
                print("   ✅ documents table EXISTS")

                # Check column structure
                result = conn.execute(text("""
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_name = 'documents'
                    ORDER BY ordinal_position
                """))
                columns = result.fetchall()
                print("   📊 Columns:")
                for col in columns:
                    print(f"      - {col[0]}: {col[1]}")

                # Count documents
                result = conn.execute(text("SELECT COUNT(*) FROM documents"))
                count = result.scalar()
                print(f"   📄 Document count: {count}")

            else:
                print("   ❌ documents table NOT found")
                print()
                print("   💡 To create:")
                print("      Run this SQL file in Supabase SQL Editor:")
                print("      /Users/souravhalder/Downloads/wealthWarriors/setup_pgvector.sql")
                print()
                return
            print()

            # Check 3: Indexes
            print("3️⃣  Checking indexes...")
            result = conn.execute(text("""
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = 'documents'
            """))
            indexes = result.fetchall()

            if indexes:
                print(f"   ✅ Found {len(indexes)} indexes:")
                for idx in indexes:
                    print(f"      - {idx[0]}")
            else:
                print("   ⚠️  No indexes found")
                print("   💡 Indexes improve search performance")
            print()

            # Check 4: Functions
            print("4️⃣  Checking helper functions...")
            result = conn.execute(text("""
                SELECT routine_name, routine_type
                FROM information_schema.routines
                WHERE routine_name IN ('match_documents', 'count_documents', 'delete_all_documents')
                AND routine_schema = 'public'
            """))
            functions = result.fetchall()

            if functions:
                print(f"   ✅ Found {len(functions)} functions:")
                for func in functions:
                    print(f"      - {func[0]}() [{func[1]}]")
            else:
                print("   ⚠️  Helper functions not found")
                print("   💡 Run setup_pgvector.sql to create them")
            print()

            print("=" * 70)
            print("✅ pgvector is ready to use!")
            print("=" * 70)
            print()
            print("Next steps:")
            print("   1. Install pgvector package: pip install pgvector")
            print("   2. Load knowledge base: python scripts/load_knowledge_pgvector.py")
            print("   3. Update .env: Set USE_PGVECTOR=true")
            print()

    except Exception as e:
        print(f"❌ Error checking pgvector setup:")
        print(f"   {str(e)}")
        print()
        print("Make sure:")
        print("   - Supabase database is accessible")
        print("   - DATABASE_URL in .env is correct")
        print("   - pgvector extension is enabled")
        sys.exit(1)


if __name__ == "__main__":
    main()
