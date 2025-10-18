"""Run performance optimization migration."""
from sqlalchemy import create_engine, text

# Use the correct DATABASE_URL
DATABASE_URL = "postgresql://postgres:JAnKfltpThXSYIdv@db.qfcnomdgpcpnsibihwvm.supabase.co:5432/postgres"

print("🔧 Running Performance Optimization Migration...")
print("=" * 70)

# Create engine with AUTOCOMMIT
engine = create_engine(DATABASE_URL, isolation_level="AUTOCOMMIT")

try:
    with engine.connect() as conn:
        # Read migration file
        with open('migrations/007_add_performance_indexes.sql', 'r') as f:
            sql = f.read()
        
        # Split by semicolon and execute each statement
        statements = [s.strip() for s in sql.split(';') if s.strip() and not s.strip().startswith('--')]
        
        for i, statement in enumerate(statements, 1):
            if statement:
                print(f"\n{i}. Executing: {statement[:60]}...")
                result = conn.execute(text(statement))
                
                # If it's the verification query, print results
                if 'SELECT' in statement.upper():
                    rows = result.fetchall()
                    print(f"\n   ✅ Found {len(rows)} indexes:")
                    for row in rows:
                        print(f"      - {row[0]}.{row[1]}")
                else:
                    print("   ✅ Done")
        
        print("\n" + "=" * 70)
        print("✅ Performance indexes created successfully!")
        print("\nExpected improvements:")
        print("  - GET /transactions: 455ms → < 35ms (92% faster)")
        print("  - GET /transactions/balance: 1122ms → < 40ms (96% faster)")
        print("  - GET /monthly-budget: 44ms → < 30ms (30% faster)")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    raise
finally:
    engine.dispose()
