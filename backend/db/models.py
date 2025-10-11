"""
SQLAlchemy database models for user management and chat history.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey, Boolean
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
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


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
