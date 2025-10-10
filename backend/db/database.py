"""
Database connection and session management for PostgreSQL.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from typing import Generator
import logging

from backend.core.config import settings
from backend.db.models import Base

logger = logging.getLogger(__name__)

# Create database engine
# For local development with SQLite (if PostgreSQL not available):
# DATABASE_URL = "sqlite:///./wealth_coach.db"
# For PostgreSQL:
# DATABASE_URL = "postgresql://user:password@localhost/wealth_coach"

# Use the DATABASE_URL from settings
DATABASE_URL = settings.DATABASE_URL

# Create engine with appropriate settings
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # Needed for SQLite
        echo=settings.DATABASE_ECHO,
    )
else:
    # PostgreSQL or other database
    engine = create_engine(
        DATABASE_URL,
        poolclass=NullPool if settings.DEBUG else None,
        echo=settings.DATABASE_ECHO,
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """
    Initialize database by creating all tables.

    This should be called on application startup.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Database tables created successfully")
    except Exception as e:
        logger.error(f"✗ Failed to create database tables: {e}")
        raise


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.

    Usage in FastAPI endpoints:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()

    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_db_async() -> Generator[Session, None, None]:
    """
    Async version of get_db for async endpoints.

    Usage in FastAPI async endpoints:
        @app.get("/users")
        async def get_users(db: Session = Depends(get_db_async)):
            return db.query(User).all()

    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def drop_all_tables() -> None:
    """
    Drop all database tables.

    WARNING: This will delete all data! Use only for development/testing.
    """
    logger.warning("⚠️  Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    logger.info("✓ All tables dropped")


def reset_database() -> None:
    """
    Reset database by dropping and recreating all tables.

    WARNING: This will delete all data! Use only for development/testing.
    """
    drop_all_tables()
    init_db()
    logger.info("✓ Database reset complete")
