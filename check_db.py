#!/usr/bin/env python3
"""Check database contents"""

import sys
sys.path.insert(0, ".")

from backend.db.database import SessionLocal
from backend.db.models import User

def main():
    db = SessionLocal()

    print("=" * 70)
    print("Database Contents")
    print("=" * 70)
    print()

    users = db.query(User).all()

    print(f"Total users: {len(users)}")
    print()

    for user in users:
        print(f"ID: {user.id}")
        print(f"Email: {user.email}")
        print(f"Name: {user.full_name}")
        print(f"Active: {user.is_active}")
        print(f"Created: {user.created_at}")
        print("-" * 70)

    db.close()

if __name__ == "__main__":
    main()
