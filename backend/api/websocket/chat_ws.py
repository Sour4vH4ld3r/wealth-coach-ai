"""
WebSocket handler for real-time chat functionality.

Provides bi-directional communication for streaming AI responses.
Optimizations:
- Message-based authentication (token not in URL)
- In-memory user profile caching
- Conversation history management
- Context-aware caching
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Set, List, Optional
import json
import asyncio
import hashlib
from datetime import datetime
from sqlalchemy import text

from backend.core.security import decode_token
from backend.core.config import settings
from backend.utils.logger import setup_logger
from backend.services.llm.client import LLMClient
from backend.core.dependencies import get_redis_client
from backend.db.database import get_db

router = APIRouter()
logger = setup_logger(__name__)

# Initialize LLM client
llm_client = LLMClient(cache_client=get_redis_client())

# Active WebSocket connections per user
active_connections: Dict[str, Set[WebSocket]] = {}


class SessionData:
    """Stores session-specific data for each WebSocket connection."""
    def __init__(self, user_id: str, user_profile: dict):
        self.user_id = user_id
        self.user_profile = user_profile
        self.conversation_history: List[dict] = []
        self.connected_at = datetime.utcnow()
        self.message_count = 0

    def add_message(self, role: str, content: str):
        """Add message to conversation history (keep last 10)."""
        self.conversation_history.append({
            "role": role,
            "content": content
        })
        # Keep only last 10 messages (5 exchanges)
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
        self.message_count += 1

    def get_conversation_hash(self) -> str:
        """Generate hash of conversation for caching."""
        conversation_str = json.dumps(self.conversation_history)
        return hashlib.md5(conversation_str.encode()).hexdigest()


class ConnectionManager:
    """Manages WebSocket connections with session data."""

    def __init__(self):
        self.sessions: Dict[WebSocket, SessionData] = {}

    async def connect(self, websocket: WebSocket, user_id: str, user_profile: dict):
        """Register WebSocket connection with session data (connection already accepted)."""
        if user_id not in active_connections:
            active_connections[user_id] = set()

        # Check max connections per user
        if len(active_connections[user_id]) >= settings.WS_MAX_CONNECTIONS_PER_USER:
            await websocket.close(code=1008, reason="Max connections reached")
            return False

        active_connections[user_id].add(websocket)

        # Create session with cached user data
        self.sessions[websocket] = SessionData(user_id, user_profile)

        logger.info(f"WebSocket connected: user={user_id}, total={len(active_connections[user_id])}")
        return True

    async def disconnect(self, websocket: WebSocket):
        """Unregister WebSocket connection and clean up session."""
        session = self.sessions.get(websocket)
        if session:
            user_id = session.user_id
            if user_id in active_connections:
                active_connections[user_id].discard(websocket)
                if not active_connections[user_id]:
                    del active_connections[user_id]

            # Clean up session data
            del self.sessions[websocket]
            logger.info(f"WebSocket disconnected: user={user_id}, messages={session.message_count}")

    def get_session(self, websocket: WebSocket) -> Optional[SessionData]:
        """Get session data for WebSocket."""
        return self.sessions.get(websocket)

    async def send_message(self, message: dict, websocket: WebSocket):
        """Send message to specific WebSocket."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send message: {e}")

    async def broadcast_to_user(self, message: dict, user_id: str):
        """Send message to all user's connections."""
        if user_id in active_connections:
            disconnected = set()
            for ws in active_connections[user_id]:
                try:
                    await ws.send_json(message)
                except Exception:
                    disconnected.add(ws)

            # Clean up disconnected sockets
            active_connections[user_id] -= disconnected


manager = ConnectionManager()


async def load_user_profile(user_id: str) -> dict:
    """
    Load user profile from database (called ONCE on connection).

    Returns:
        dict: User profile data with context string
    """
    try:
        db = next(get_db())
        result = db.execute(text("""
            SELECT
                u.full_name,
                up.age_range,
                up.occupation,
                up.income_range,
                up.financial_goals,
                up.investment_experience,
                up.risk_tolerance,
                up.current_investments,
                up.debt_status,
                up.retirement_planning
            FROM users u
            LEFT JOIN user_profiles up ON u.id = up.user_id
            WHERE u.id = :user_id
        """), {"user_id": user_id})

        user = result.fetchone()

        if not user or not user[1]:  # No profile data
            return {"context": "", "has_profile": False}

        # Build personalized context
        context_parts = []

        if user[0]:  # full_name
            context_parts.append(f"User: {user[0]}")
        if user[1]:  # age_range
            context_parts.append(f"Age: {user[1]}")
        if user[2]:  # occupation
            context_parts.append(f"Occupation: {user[2]}")
        if user[3]:  # income_range
            context_parts.append(f"Income: {user[3]}")
        if user[4]:  # financial_goals
            context_parts.append(f"Goals: {user[4]}")
        if user[5]:  # investment_experience
            context_parts.append(f"Investment Experience: {user[5]}")
        if user[6]:  # risk_tolerance
            context_parts.append(f"Risk Tolerance: {user[6]}")
        if user[7]:  # current_investments
            context_parts.append(f"Current Investments: {user[7]}")
        if user[8]:  # debt_status
            context_parts.append(f"Debt: {user[8]}")
        if user[9]:  # retirement_planning
            retirement_status = "planning for retirement" if user[9] else "not yet planning retirement"
            context_parts.append(f"Retirement: {retirement_status}")

        context = ""
        if context_parts:
            context = "\n\nUser Profile:\n" + "\n".join(f"- {part}" for part in context_parts)

        return {
            "context": context,
            "has_profile": True,
            "full_name": user[0],
            "age_range": user[1],
            "occupation": user[2]
        }

    except Exception as e:
        logger.error(f"Error loading user profile: {e}")
        return {"context": "", "has_profile": False}


@router.websocket("/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for real-time chat with message-based authentication.

    Flow:
    1. Accept connection
    2. Wait for authentication message
    3. Verify token and load user profile (ONCE)
    4. Listen for messages with conversation history
    5. Stream AI responses back
    6. Handle disconnection

    Authentication Message (Client -> Server):
    {
        "type": "authenticate",
        "token": "JWT_TOKEN_HERE"
    }

    Chat Message (Client -> Server):
    {
        "type": "message",
        "content": "User question here"
    }

    Response Message (Server -> Client):
    {
        "type": "response",
        "content": "AI response",
        "done": false,
        "timestamp": "ISO-8601"
    }
    """
    # Accept connection without authentication
    await websocket.accept()

    authenticated = False
    user_id = None

    try:
        # Wait for authentication message (30 second timeout)
        auth_data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)

        try:
            auth_message = json.loads(auth_data)
        except json.JSONDecodeError:
            await websocket.close(code=1008, reason="Invalid JSON")
            return

        # Verify authentication message
        if auth_message.get("type") != "authenticate":
            await websocket.close(code=1008, reason="Authentication required")
            return

        token = auth_message.get("token")
        if not token:
            await websocket.close(code=1008, reason="Token missing")
            return

        # Decode and verify token
        try:
            payload = decode_token(token)
            user_id = payload.get("user_id")
            if not user_id:
                await websocket.close(code=1008, reason="Invalid token")
                return
        except Exception as e:
            logger.warning(f"Authentication failed: {e}")
            await websocket.close(code=1008, reason="Authentication failed")
            return

        # Load user profile ONCE (cached in session)
        user_profile = await load_user_profile(user_id)

        # Register connection with session data
        connected = await manager.connect(websocket, user_id, user_profile)
        if not connected:
            return

        authenticated = True

        # Send connection confirmation
        await manager.send_message({
            "type": "connected",
            "message": "Connected to Wealth Coach AI",
            "timestamp": datetime.utcnow().isoformat(),
        }, websocket)

        # Main message loop
        while True:
            # Receive message
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                await manager.send_message({
                    "type": "error",
                    "message": "Invalid JSON format",
                }, websocket)
                continue

            # Handle different message types
            message_type = message.get("type")

            if message_type == "message":
                # Process chat message with conversation history
                await handle_chat_message(websocket, message)

            elif message_type == "ping":
                # Heartbeat
                await manager.send_message({"type": "pong"}, websocket)

            else:
                await manager.send_message({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}",
                }, websocket)

    except asyncio.TimeoutError:
        logger.warning("Authentication timeout")
        await websocket.close(code=1008, reason="Authentication timeout")
    except WebSocketDisconnect:
        if authenticated:
            await manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        if authenticated:
            await manager.disconnect(websocket)


async def handle_chat_message(websocket: WebSocket, message: dict):
    """
    Process chat message with conversation history and context-aware caching.

    Args:
        websocket: WebSocket connection
        message: Message payload
    """
    # Get session data (user profile already cached)
    session = manager.get_session(websocket)
    if not session:
        await manager.send_message({
            "type": "error",
            "message": "Session not found",
        }, websocket)
        return

    user_message = message.get("content", "").strip()

    if not user_message:
        await manager.send_message({
            "type": "error",
            "message": "Empty message",
        }, websocket)
        return

    try:
        # Build system prompt with cached user context
        base_prompt = (
            "You are a helpful financial assistant for Wealth Warriors Hub. "
            "Provide clear, concise, and actionable financial advice. "
            "Keep responses brief and focused. "
            "If you need more information to give accurate advice, ask clarifying questions."
        )

        # Add user context from cached profile
        system_prompt = base_prompt + session.user_profile.get("context", "")

        # Build messages with conversation history
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            *session.conversation_history,  # Include conversation history
            {
                "role": "user",
                "content": user_message
            }
        ]

        # Context-aware cache key (includes user + conversation context)
        conversation_hash = session.get_conversation_hash()
        message_hash = hashlib.md5(user_message.encode()).hexdigest()
        cache_key = f"ai_chat:{session.user_id}:{conversation_hash}:{message_hash}"

        # Check cache
        redis_client = await get_redis_client()
        cached_response = await redis_client.get(cache_key)

        if cached_response:
            # Return cached response
            logger.info(f"Cache hit for user {session.user_id}")
            cached_text = cached_response.decode('utf-8')

            await manager.send_message({
                "type": "response",
                "content": cached_text,
                "done": True,
                "cached": True,
                "timestamp": datetime.utcnow().isoformat(),
            }, websocket)

            # Add to conversation history
            session.add_message("user", user_message)
            session.add_message("assistant", cached_text)
            return

        # Stream response from LLM
        accumulated = ""
        async for chunk in llm_client.chat_stream(messages, max_tokens=300, temperature=0.7):
            accumulated += chunk
            await manager.send_message({
                "type": "response",
                "content": accumulated,
                "done": False,
                "timestamp": datetime.utcnow().isoformat(),
            }, websocket)

        # Final message
        final_response = accumulated.strip()
        await manager.send_message({
            "type": "response",
            "content": final_response,
            "done": True,
            "cached": False,
            "timestamp": datetime.utcnow().isoformat(),
        }, websocket)

        # Cache the response (120 seconds TTL)
        await redis_client.set(cache_key, final_response, ex=120)

        # Add to conversation history
        session.add_message("user", user_message)
        session.add_message("assistant", final_response)

    except Exception as e:
        logger.error(f"Error streaming AI response: {e}", exc_info=True)
        await manager.send_message({
            "type": "error",
            "message": "Failed to generate response. Please try again.",
        }, websocket)


@router.websocket("/notifications")
async def websocket_notifications(websocket: WebSocket):
    """
    WebSocket endpoint for push notifications with message-based auth.

    Sends:
    - Cost alerts
    - Usage limits
    - System notifications
    """
    # Accept connection
    await websocket.accept()

    try:
        # Wait for authentication
        auth_data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
        auth_message = json.loads(auth_data)

        if auth_message.get("type") != "authenticate":
            await websocket.close(code=1008, reason="Authentication required")
            return

        token = auth_message.get("token")
        payload = decode_token(token)
        user_id = payload.get("user_id")

        if not user_id:
            await websocket.close(code=1008, reason="Invalid token")
            return

        # Connection successful
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to notifications",
        })

        # Keep connection alive
        while True:
            await asyncio.sleep(settings.WS_HEARTBEAT_INTERVAL)
            await websocket.send_json({"type": "heartbeat"})

    except (asyncio.TimeoutError, Exception):
        await websocket.close(code=1008, reason="Connection error")
