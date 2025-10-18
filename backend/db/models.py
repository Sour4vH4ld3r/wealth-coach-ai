"""
SQLAlchemy database models for user management and chat history.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey, Boolean, Numeric, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import uuid

Base = declarative_base()


def generate_uuid():
    """Generate a UUID string for primary keys."""
    return str(uuid.uuid4())


class User(Base):
    """User account model."""

    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    mobile_number = Column(String(10), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    hashed_password = Column(String(255), nullable=True)
    full_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, mobile={self.mobile_number}, email={self.email})>"


class ChatSession(Base):
    """Chat session model to group related messages."""

    __tablename__ = "chat_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=True)  # Optional session title
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ChatSession(id={self.id}, user_id={self.user_id})>"


class ChatMessage(Base):
    """Individual chat message model."""

    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("chat_sessions.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False, index=True)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    tokens_used = Column(Integer, nullable=True)  # Track token usage
    cost = Column(String(20), nullable=True)  # Track cost
    sources_count = Column(Integer, default=0)  # Number of RAG sources used
    cached = Column(Boolean, default=False)  # Whether response was cached
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, role={self.role})>"


class UserPreferences(Base):
    """User preferences and settings."""

    __tablename__ = "user_preferences"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, unique=True, index=True)

    # Preferences
    use_rag = Column(Boolean, default=True)  # Enable/disable RAG by default
    theme = Column(String(20), default="light")  # UI theme preference
    language = Column(String(10), default="en")  # Language preference

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<UserPreferences(user_id={self.user_id})>"


class UserProfile(Base):
    """User profile and onboarding data for personalized AI responses."""

    __tablename__ = "user_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, unique=True, index=True)

    # Onboarding Questions
    age_range = Column(String(20), nullable=True)  # e.g., "25-34", "35-44"
    occupation = Column(String(100), nullable=True)  # User's job/profession
    income_range = Column(String(30), nullable=True)  # e.g., "$50k-$75k"
    financial_goals = Column(Text, nullable=True)  # Comma-separated goals
    investment_experience = Column(String(30), nullable=True)  # beginner/intermediate/advanced
    risk_tolerance = Column(String(20), nullable=True)  # low/medium/high
    current_investments = Column(Text, nullable=True)  # What they currently invest in
    debt_status = Column(String(30), nullable=True)  # none/some/significant
    retirement_planning = Column(Boolean, default=False)  # Interested in retirement planning
    interests = Column(Text, nullable=True)  # Other financial interests

    # Onboarding Status
    onboarding_completed = Column(Boolean, default=False, nullable=False)
    onboarding_completed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<UserProfile(user_id={self.user_id}, completed={self.onboarding_completed})>"


class Document(Base):
    """Document model for vector embeddings and semantic search."""

    __tablename__ = "documents"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(Text, nullable=False)
    meta = Column("metadata", JSONB, nullable=True)  # Renamed to avoid SQLAlchemy conflict
    embedding = Column(Vector(384), nullable=True)  # 384 dimensions for all-MiniLM-L6-v2
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Document(id={self.id}, content_length={len(self.content) if self.content else 0})>"


class AllocationCategory(Base):
    """Main allocation categories (Freedom, Health, Spending, Learning, Entertainment, Contribution)."""

    __tablename__ = "allocation_categories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(50), unique=True, nullable=False)  # freedom, health, spending, etc.
    label = Column(String(100), nullable=False)  # Display name
    icon = Column(String(50), nullable=False)  # Icon identifier
    icon_color = Column(String(20), nullable=False)  # Color code
    description = Column(Text, nullable=True)
    target_percentage = Column(Numeric(5, 2), nullable=False)  # e.g., 10.00 for 10%
    sort_order = Column(Integer, nullable=False)  # Display order
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    allocation_types = relationship("AllocationType", back_populates="category", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<AllocationCategory(id={self.id}, name={self.name})>"


class AllocationType(Base):
    """Investment types under each allocation category."""

    __tablename__ = "allocation_types"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    category_id = Column(String(36), ForeignKey("allocation_categories.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)  # e.g., "Bank Deposits", "Mutual Funds"
    description = Column(Text, nullable=True)
    purpose = Column(String(200), nullable=True)  # e.g., "Secure, low-risk savings"
    sort_order = Column(Integer, nullable=False)  # Display order within category
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    category = relationship("AllocationCategory", back_populates="allocation_types")
    user_allocations = relationship("UserAllocation", back_populates="allocation_type", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<AllocationType(id={self.id}, name={self.name})>"


class UserAllocation(Base):
    """User's budget and actual spending for each allocation type."""

    __tablename__ = "user_allocations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    allocation_type_id = Column(String(36), ForeignKey("allocation_types.id"), nullable=False, index=True)

    # Financial data
    budget_amount = Column(Numeric(15, 2), default=0.00, nullable=False)  # Budgeted amount
    actual_amount = Column(Numeric(15, 2), default=0.00, nullable=False)  # Actual spent/invested

    # Metadata
    month = Column(Integer, nullable=False, index=True)  # 1-12
    year = Column(Integer, nullable=False, index=True)  # e.g., 2025
    notes = Column(Text, nullable=True)  # Optional user notes

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    allocation_type = relationship("AllocationType", back_populates="user_allocations")

    def __repr__(self):
        return f"<UserAllocation(id={self.id}, user_id={self.user_id}, type_id={self.allocation_type_id})>"


class MonthlyBudget(Base):
    """User's monthly budget summary - tracks current balance."""
    __tablename__ = "monthly_budgets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    current_balance = Column(Numeric(15, 2), default=0.00, nullable=False)  # Current balance (income - expenses)
    total_income = Column(Numeric(15, 2), default=0.00, nullable=False)  # Sum of all income
    total_expense = Column(Numeric(15, 2), default=0.00, nullable=False)  # Sum of all expenses
    month = Column(Integer, nullable=False, index=True)  # 1-12
    year = Column(Integer, nullable=False, index=True)  # e.g., 2025

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Unique constraint: one budget per user per month
    __table_args__ = (
        Index('idx_user_month_year', 'user_id', 'month', 'year', unique=True),
    )

    def __repr__(self):
        return f"<MonthlyBudget(id={self.id}, user_id={self.user_id}, balance={self.current_balance})>"


class Transaction(Base):
    """Income and expense transactions."""
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    type = Column(String(10), nullable=False)  # 'income' or 'expense'
    category = Column(String(50), nullable=False)  # e.g., 'salary', 'food', 'rent'
    amount = Column(Numeric(15, 2), nullable=False)
    label = Column(String(200), nullable=False)  # Description
    transaction_date = Column(DateTime, nullable=False, index=True)  # When transaction occurred
    month = Column(Integer, nullable=False, index=True)  # 1-12
    year = Column(Integer, nullable=False, index=True)  # e.g., 2025

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Transaction(id={self.id}, type={self.type}, category={self.category}, amount={self.amount})>"
