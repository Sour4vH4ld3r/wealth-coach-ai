#!/usr/bin/env python3
"""
Database Initialization Script

Creates all database tables and optionally seeds initial data.
Run this script to set up the database before starting the application.
"""

import sys
sys.path.insert(0, ".")

from backend.db.database import init_db, reset_database
from backend.core.config import settings
import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Initialize the database."""
    parser = argparse.ArgumentParser(description="Initialize the Wealth Coach database")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset database (WARNING: Deletes all existing data!)"
    )
    args = parser.parse_args()

    print("=" * 70)
    print("Wealth Coach AI - Database Initialization")
    print("=" * 70)
    print()

    print(f"Database URL: {settings.DATABASE_URL}")
    print()

    if args.reset:
        response = input("⚠️  WARNING: This will DELETE ALL DATA! Continue? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            return

        print("\nResetting database...")
        reset_database()
        print("✓ Database reset complete")
    else:
        print("Creating database tables...")
        init_db()
        print("✓ Database initialized successfully")

    print()
    print("=" * 70)
    print("Database is ready!")
    print("=" * 70)


if __name__ == "__main__":
    main()
