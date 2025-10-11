"""
Chat endpoint tests.

Tests for chat message sending, history retrieval, and session management.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime

from backend.db.models import User, ChatSession, ChatMessage


# =============================================================================
# CHAT MESSAGE TESTS
# =============================================================================

def test_send_message_authenticated(client: TestClient, auth_headers: dict):
    """Test sending a chat message as authenticated user."""
    response = client.post(
        "/api/v1/chat/message",
        headers=auth_headers,
        json={
            "message": "What is a Roth IRA?",
            "use_rag": True,
            "stream": False
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Check response structure
    assert "response" in data
    assert "sources" in data
    assert "timestamp" in data
    assert "conversation_id" in data

    # Check response content
    assert len(data["response"]) > 0
    assert isinstance(data["sources"], list)
    assert data["cached"] is False


def test_send_message_unauthenticated(client: TestClient):
    """Test that unauthenticated requests are rejected."""
    response = client.post(
        "/api/v1/chat/message",
        json={
            "message": "What is a Roth IRA?",
            "use_rag": True
        }
    )

    assert response.status_code == 403  # Forbidden - no auth header


def test_send_message_invalid_token(client: TestClient):
    """Test that requests with invalid token are rejected."""
    response = client.post(
        "/api/v1/chat/message",
        headers={"Authorization": "Bearer invalid.token.here"},
        json={
            "message": "What is a Roth IRA?",
            "use_rag": True
        }
    )

    assert response.status_code == 401


def test_send_message_with_conversation_history(client: TestClient, auth_headers: dict):
    """Test sending a message with conversation history."""
    response = client.post(
        "/api/v1/chat/message",
        headers=auth_headers,
        json={
            "message": "Tell me more about that",
            "conversation_history": [
                {
                    "role": "user",
                    "content": "What is a Roth IRA?"
                },
                {
                    "role": "assistant",
                    "content": "A Roth IRA is a retirement account..."
                }
            ],
            "use_rag": True
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "response" in data


def test_send_message_without_rag(client: TestClient, auth_headers: dict):
    """Test sending a message without RAG context retrieval."""
    response = client.post(
        "/api/v1/chat/message",
        headers=auth_headers,
        json={
            "message": "Hello, how are you?",
            "use_rag": False
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    # Sources should be empty when RAG is disabled
    assert len(data["sources"]) == 0


def test_send_message_empty_message(client: TestClient, auth_headers: dict):
    """Test that empty messages are rejected."""
    response = client.post(
        "/api/v1/chat/message",
        headers=auth_headers,
        json={
            "message": "",
            "use_rag": True
        }
    )

    assert response.status_code == 422  # Validation error


def test_send_message_too_long(client: TestClient, auth_headers: dict):
    """Test that messages exceeding max length are rejected."""
    long_message = "x" * 2001  # Max is 2000

    response = client.post(
        "/api/v1/chat/message",
        headers=auth_headers,
        json={
            "message": long_message,
            "use_rag": True
        }
    )

    assert response.status_code == 422  # Validation error


def test_send_message_creates_session(client: TestClient, auth_headers: dict, db: Session, test_user: User):
    """Test that sending a message creates a chat session."""
    response = client.post(
        "/api/v1/chat/message",
        headers=auth_headers,
        json={
            "message": "What is a Roth IRA?",
            "use_rag": True
        }
    )

    assert response.status_code == 200
    conversation_id = response.json()["conversation_id"]

    # Verify session was created in database
    session = db.query(ChatSession).filter(ChatSession.id == conversation_id).first()
    assert session is not None
    assert session.user_id == test_user.id


def test_send_message_saves_to_database(client: TestClient, auth_headers: dict, db: Session):
    """Test that messages are saved to database."""
    user_message = "What is compound interest?"

    response = client.post(
        "/api/v1/chat/message",
        headers=auth_headers,
        json={
            "message": user_message,
            "use_rag": True
        }
    )

    assert response.status_code == 200
    conversation_id = response.json()["conversation_id"]

    # Verify messages were saved
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == conversation_id
    ).all()

    assert len(messages) == 2  # User message + assistant response

    # Check user message
    user_msg = [m for m in messages if m.role == "user"][0]
    assert user_msg.content == user_message

    # Check assistant message
    assistant_msg = [m for m in messages if m.role == "assistant"][0]
    assert len(assistant_msg.content) > 0


def test_send_message_with_session_id(client: TestClient, auth_headers: dict, db: Session, test_user: User):
    """Test sending a message to an existing session."""
    # Create initial session
    session = ChatSession(user_id=test_user.id)
    db.add(session)
    db.commit()
    db.refresh(session)

    # Send message to existing session
    response = client.post(
        "/api/v1/chat/message",
        headers=auth_headers,
        json={
            "message": "What is a Roth IRA?",
            "session_id": session.id,
            "use_rag": True
        }
    )

    assert response.status_code == 200
    assert response.json()["conversation_id"] == session.id


# =============================================================================
# CHAT SESSION TESTS
# =============================================================================

def test_get_chat_sessions(client: TestClient, auth_headers: dict, db: Session, test_user: User):
    """Test retrieving user's chat sessions."""
    # Create test sessions
    session1 = ChatSession(user_id=test_user.id)
    session2 = ChatSession(user_id=test_user.id)
    db.add_all([session1, session2])
    db.commit()

    # Add messages to sessions
    message1 = ChatMessage(
        session_id=session1.id,
        role="user",
        content="First question about investing"
    )
    message2 = ChatMessage(
        session_id=session2.id,
        role="user",
        content="Second question about retirement"
    )
    db.add_all([message1, message2])
    db.commit()

    # Get sessions
    response = client.get(
        "/api/v1/chat/sessions",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert "sessions" in data
    assert len(data["sessions"]) == 2

    # Check session structure
    session = data["sessions"][0]
    assert "session_id" in session
    assert "preview" in session
    assert "message_count" in session
    assert "created_at" in session
    assert "updated_at" in session


def test_get_chat_sessions_pagination(client: TestClient, auth_headers: dict, db: Session, test_user: User):
    """Test chat session pagination."""
    # Create 25 test sessions
    sessions = [ChatSession(user_id=test_user.id) for _ in range(25)]
    db.add_all(sessions)
    db.commit()

    # Get first page (default limit is 20)
    response = client.get(
        "/api/v1/chat/sessions?skip=0&limit=20",
        headers=auth_headers
    )

    assert response.status_code == 200
    assert len(response.json()["sessions"]) == 20

    # Get second page
    response = client.get(
        "/api/v1/chat/sessions?skip=20&limit=20",
        headers=auth_headers
    )

    assert response.status_code == 200
    assert len(response.json()["sessions"]) == 5


def test_get_chat_sessions_empty(client: TestClient, auth_headers: dict):
    """Test getting sessions when user has no sessions."""
    response = client.get(
        "/api/v1/chat/sessions",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert "sessions" in data
    assert len(data["sessions"]) == 0


def test_get_chat_sessions_unauthenticated(client: TestClient):
    """Test that unauthenticated requests are rejected."""
    response = client.get("/api/v1/chat/sessions")

    assert response.status_code == 403


# =============================================================================
# CHAT HISTORY TESTS
# =============================================================================

def test_get_session_messages(client: TestClient, auth_headers: dict, db: Session, test_user: User):
    """Test retrieving messages from a specific session."""
    # Create session with messages
    session = ChatSession(user_id=test_user.id)
    db.add(session)
    db.commit()
    db.refresh(session)

    messages = [
        ChatMessage(session_id=session.id, role="user", content="Question 1"),
        ChatMessage(session_id=session.id, role="assistant", content="Answer 1"),
        ChatMessage(session_id=session.id, role="user", content="Question 2"),
        ChatMessage(session_id=session.id, role="assistant", content="Answer 2"),
    ]
    db.add_all(messages)
    db.commit()

    # Get session messages
    response = client.get(
        f"/api/v1/chat/sessions/{session.id}/messages",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert "messages" in data
    assert len(data["messages"]) == 4
    assert data["session_id"] == session.id
    assert data["total"] == 4
    assert data["has_more"] is False


def test_get_session_messages_pagination(client: TestClient, auth_headers: dict, db: Session, test_user: User):
    """Test message pagination within a session."""
    # Create session with 60 messages
    session = ChatSession(user_id=test_user.id)
    db.add(session)
    db.commit()
    db.refresh(session)

    messages = []
    for i in range(30):
        messages.append(ChatMessage(session_id=session.id, role="user", content=f"Question {i}"))
        messages.append(ChatMessage(session_id=session.id, role="assistant", content=f"Answer {i}"))
    db.add_all(messages)
    db.commit()

    # Get first page
    response = client.get(
        f"/api/v1/chat/sessions/{session.id}/messages?skip=0&limit=50",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["messages"]) == 50
    assert data["total"] == 60
    assert data["has_more"] is True


def test_get_session_messages_invalid_session(client: TestClient, auth_headers: dict):
    """Test getting messages from non-existent session."""
    response = client.get(
        "/api/v1/chat/sessions/invalid-session-id/messages",
        headers=auth_headers
    )

    assert response.status_code == 404


def test_get_session_messages_wrong_user(client: TestClient, auth_headers: dict, db: Session):
    """Test that users cannot access other users' sessions."""
    # Create another user's session
    other_user = User(
        email="other@example.com",
        hashed_password="hash",
        full_name="Other User"
    )
    db.add(other_user)
    db.commit()

    session = ChatSession(user_id=other_user.id)
    db.add(session)
    db.commit()
    db.refresh(session)

    # Try to access other user's session
    response = client.get(
        f"/api/v1/chat/sessions/{session.id}/messages",
        headers=auth_headers
    )

    assert response.status_code == 404


# =============================================================================
# CACHE TESTS
# =============================================================================

def test_chat_response_caching(client: TestClient, auth_headers: dict, mock_redis):
    """Test that identical queries return cached responses."""
    message = "What is diversification?"

    # First request
    response1 = client.post(
        "/api/v1/chat/message",
        headers=auth_headers,
        json={
            "message": message,
            "use_rag": True
        }
    )

    assert response1.status_code == 200
    assert response1.json()["cached"] is False

    # Second identical request should be cached
    response2 = client.post(
        "/api/v1/chat/message",
        headers=auth_headers,
        json={
            "message": message,
            "use_rag": True
        }
    )

    assert response2.status_code == 200
    assert response2.json()["cached"] is True


# =============================================================================
# STREAMING TESTS
# =============================================================================

def test_send_message_stream_endpoint_exists(client: TestClient, auth_headers: dict):
    """Test that streaming endpoint exists and responds."""
    response = client.post(
        "/api/v1/chat/message/stream",
        headers=auth_headers,
        json={
            "message": "What is a Roth IRA?",
            "use_rag": True
        }
    )

    # Should return streaming response
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream"
