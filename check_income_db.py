"""Check if income sources are in database."""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT id, total_amount, income_sources, month, year, notes
        FROM monthly_budgets
        ORDER BY created_at DESC
        LIMIT 1
    """))

    row = result.fetchone()
    if row:
        print("📊 Latest Monthly Budget:")
        print(f"   ID: {row[0]}")
        print(f"   Total Amount: ₹{row[1]}")
        print(f"   Income Sources: {row[2]}")
        print(f"   Month/Year: {row[3]}/{row[4]}")
        print(f"   Notes: {row[5]}")
    else:
        print("❌ No monthly budget found")

engine.dispose()
