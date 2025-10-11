"""
Pytest configuration and shared fixtures for all tests.

This file provides common test fixtures including:
- Test database setup/teardown
- Test client fixture
- Authenticated user fixture
- Mock Redis client
- Mock LLM client
"""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator, AsyncGenerator
from unittest.mock import AsyncMock, MagicMock
import asyncio

from backend.main import app
from backend.db.models import Base, User, UserProfile, ChatSession, ChatMessage, UserPreferences
from backend.db.database import get_db
from backend.core.security import hash_password, create_access_token
from backend.core.dependencies import get_redis_client, get_llm_client, get_rag_retriever


# =============================================================================
# TEST DATABASE SETUP
# =============================================================================

# Use in-memory SQLite for tests (fast and isolated)
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

# Create test session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """
    Create a fresh database for each test.

    This fixture:
    1. Creates all tables before the test (excluding Document table for SQLite compatibility)
    2. Yields a database session
    3. Drops all tables after the test

    This ensures complete isolation between tests.

    Note: Document table uses PostgreSQL-specific types (JSONB, Vector) that are not
    compatible with SQLite, so we exclude it from test database.
    """
    # Create only the tables we need for testing (exclude Document table)
    # Document table uses JSONB and Vector types which are PostgreSQL-specific
    from backend.db.models import Document
    tables_to_create = [table for table in Base.metadata.sorted_tables
                       if table.name != 'documents']

    for table in tables_to_create:
        table.create(bind=test_engine, checkfirst=True)

    # Create a new session
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        for table in reversed(tables_to_create):
            table.drop(bind=test_engine, checkfirst=True)


def override_get_db():
    """Override database dependency for testing."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


# =============================================================================
# MOCK REDIS CLIENT
# =============================================================================

class MockRedis:
    """Mock Redis client for testing without Redis server."""

    def __init__(self):
        self.data = {}
        self.expirations = {}

    async def get(self, key: str) -> str | None:
        """Get value from mock Redis."""
        return self.data.get(key)

    async def set(self, key: str, value: str, ex: int = None) -> bool:
        """Set value in mock Redis."""
        self.data[key] = value
        if ex:
            self.expirations[key] = ex
        return True

    async def delete(self, key: str) -> int:
        """Delete key from mock Redis."""
        if key in self.data:
            del self.data[key]
            return 1
        return 0

    async def incr(self, key: str) -> int:
        """Increment value in mock Redis."""
        current = int(self.data.get(key, 0))
        self.data[key] = str(current + 1)
        return current + 1

    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on key."""
        self.expirations[key] = seconds
        return True

    async def ping(self) -> bool:
        """Ping mock Redis."""
        return True

    async def close(self):
        """Close mock Redis connection."""
        pass


@pytest.fixture
def mock_redis():
    """Provide a mock Redis client for testing."""
    return MockRedis()


async def override_get_redis_client():
    """Override Redis dependency for testing."""
    return MockRedis()


# =============================================================================
# MOCK LLM CLIENT
# =============================================================================

class MockLLMResponse:
    """Mock LLM response object."""

    def __init__(self, content: str, tokens: int = 100):
        self.content = content
        self.usage = MagicMock()
        self.usage.total_tokens = tokens


class MockLLMClient:
    """Mock LLM client for testing without OpenAI API."""

    async def chat(self, messages: list, max_tokens: int = 500) -> MockLLMResponse:
        """Mock chat response."""
        return MockLLMResponse(
            content="This is a mock financial advice response from the AI assistant.",
            tokens=50
        )

    async def chat_stream(self, messages: list, max_tokens: int = 500):
        """Mock streaming chat response."""
        mock_response = "This is a mock streaming response."
        for word in mock_response.split():
            yield word + " "
            await asyncio.sleep(0.01)


@pytest.fixture
def mock_llm_client():
    """Provide a mock LLM client for testing."""
    return MockLLMClient()


async def override_get_llm_client():
    """Override LLM client dependency for testing."""
    return MockLLMClient()


# =============================================================================
# MOCK RAG RETRIEVER
# =============================================================================

class MockRAGResult:
    """Mock RAG retrieval result."""

    def __init__(self):
        self.documents = [
            "Investment diversification is a risk management strategy.",
            "A Roth IRA allows for tax-free growth and withdrawals in retirement."
        ]
        self.sources = [
            {"source": "financial_basics.pdf", "page": 12},
            {"source": "retirement_planning.pdf", "page": 5}
        ]


class MockRAGRetriever:
    """Mock RAG retriever for testing without vector database."""

    async def retrieve(self, query: str, top_k: int = 5) -> MockRAGResult:
        """Mock RAG retrieval."""
        return MockRAGResult()


@pytest.fixture
def mock_rag_retriever():
    """Provide a mock RAG retriever for testing."""
    return MockRAGRetriever()


async def override_get_rag_retriever():
    """Override RAG retriever dependency for testing."""
    return MockRAGRetriever()


# =============================================================================
# TEST CLIENT
# =============================================================================

@pytest.fixture
def client(db: Session, mock_redis, mock_llm_client, mock_rag_retriever) -> TestClient:
    """
    Create a test client with all dependencies mocked.

    This client uses:
    - In-memory SQLite database
    - Mock Redis client
    - Mock LLM client
    - Mock RAG retriever
    """
    # Override dependencies
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis_client] = override_get_redis_client
    app.dependency_overrides[get_llm_client] = override_get_llm_client
    app.dependency_overrides[get_rag_retriever] = override_get_rag_retriever

    # Create test client
    with TestClient(app) as test_client:
        yield test_client

    # Clear overrides after test
    app.dependency_overrides.clear()


# =============================================================================
# TEST USER FIXTURES
# =============================================================================

@pytest.fixture
def test_user(db: Session) -> User:
    """
    Create a test user in the database.

    Returns:
        User object with known credentials
    """
    user = User(
        email="test@example.com",
        hashed_password=hash_password("TestPassword123!"),
        full_name="Test User",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_user_token(test_user: User) -> str:
    """
    Create a valid JWT token for the test user.

    Returns:
        JWT access token string
    """
    token_data = {"user_id": test_user.id, "email": test_user.email}
    return create_access_token(token_data)


@pytest.fixture
def auth_headers(test_user_token: str) -> dict:
    """
    Create authentication headers with Bearer token.

    Returns:
        Dictionary with Authorization header
    """
    return {"Authorization": f"Bearer {test_user_token}"}


# =============================================================================
# ASYNC FIXTURES
# =============================================================================

@pytest_asyncio.fixture
async def async_client(db: Session, mock_redis, mock_llm_client, mock_rag_retriever):
    """
    Async test client for testing async endpoints.

    Note: FastAPI TestClient is actually synchronous, but this fixture
    is provided for consistency with async test patterns.
    """
    # Override dependencies
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis_client] = override_get_redis_client
    app.dependency_overrides[get_llm_client] = override_get_llm_client
    app.dependency_overrides[get_rag_retriever] = override_get_rag_retriever

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# =============================================================================
# UTILITY FIXTURES
# =============================================================================

@pytest.fixture
def weak_passwords():
    """List of passwords that should fail validation."""
    return [
        "short",              # Too short
        "alllowercase123!",   # No uppercase
        "ALLUPPERCASE123!",   # No lowercase
        "NoNumbers!",         # No digits
        "NoSpecialChars123",  # No special characters
    ]


@pytest.fixture
def valid_passwords():
    """List of passwords that should pass validation."""
    return [
        "ValidPass123!",
        "SecurePassword456#",
        "Complex@Password789",
    ]
