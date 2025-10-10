"""
WebSocket handler for real-time chat functionality.

Provides bi-directional communication for streaming AI responses.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Set
import json
import asyncio
from datetime import datetime

from backend.core.security import decode_token
from backend.core.config import settings
from backend.utils.logger import setup_logger

router = APIRouter()
logger = setup_logger(__name__)

# Active WebSocket connections per user
active_connections: Dict[str, Set[WebSocket]] = {}


class ConnectionManager:
    """Manages WebSocket connections."""

    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept and register WebSocket connection."""
        await websocket.accept()

        if user_id not in active_connections:
            active_connections[user_id] = set()

        # Check max connections per user
        if len(active_connections[user_id]) >= settings.WS_MAX_CONNECTIONS_PER_USER:
            await websocket.close(code=1008, reason="Max connections reached")
            return False

        active_connections[user_id].add(websocket)
        logger.info(f"WebSocket connected: user={user_id}, total={len(active_connections[user_id])}")
        return True

    async def disconnect(self, websocket: WebSocket, user_id: str):
        """Unregister WebSocket connection."""
        if user_id in active_connections:
            active_connections[user_id].discard(websocket)
            if not active_connections[user_id]:
                del active_connections[user_id]
        logger.info(f"WebSocket disconnected: user={user_id}")

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


@router.websocket("/chat")
async def websocket_chat(websocket: WebSocket, token: str = None):
    """
    WebSocket endpoint for real-time chat.

    Flow:
    1. Authenticate via token parameter
    2. Accept connection
    3. Listen for messages
    4. Stream AI responses back
    5. Handle disconnection

    Args:
        websocket: WebSocket connection
        token: JWT authentication token

    Message Format (Client -> Server):
    {
        "type": "message",
        "content": "User question here",
        "conversation_id": "optional-id"
    }

    Message Format (Server -> Client):
    {
        "type": "response",
        "content": "AI response",
        "done": false,
        "timestamp": "ISO-8601"
    }
    """
    # Authenticate
    if not token:
        await websocket.close(code=1008, reason="Authentication required")
        return

    try:
        payload = decode_token(token)
        user_id = payload.get("user_id")
        if not user_id:
            await websocket.close(code=1008, reason="Invalid token")
            return
    except Exception:
        await websocket.close(code=1008, reason="Authentication failed")
        return

    # Connect
    connected = await manager.connect(websocket, user_id)
    if not connected:
        return

    # Send welcome message
    await manager.send_message({
        "type": "connected",
        "message": "Connected to Wealth Coach AI",
        "timestamp": datetime.utcnow().isoformat(),
    }, websocket)

    try:
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
                # Process chat message
                await handle_chat_message(websocket, user_id, message)

            elif message_type == "ping":
                # Heartbeat
                await manager.send_message({"type": "pong"}, websocket)

            else:
                await manager.send_message({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}",
                }, websocket)

    except WebSocketDisconnect:
        await manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        await manager.disconnect(websocket, user_id)


async def handle_chat_message(websocket: WebSocket, user_id: str, message: dict):
    """
    Process chat message and stream response.

    Args:
        websocket: WebSocket connection
        user_id: Authenticated user ID
        message: Message payload
    """
    user_message = message.get("content", "").strip()

    if not user_message:
        await manager.send_message({
            "type": "error",
            "message": "Empty message",
        }, websocket)
        return

    # TODO: Integrate with LLM service for streaming
    # For now, send mock streaming response

    # Simulate streaming response
    mock_response = "I'm here to help with your financial questions. This is a placeholder response that will be replaced with actual AI-generated content."

    words = mock_response.split()
    accumulated = ""

    for word in words:
        accumulated += word + " "
        await manager.send_message({
            "type": "response",
            "content": accumulated,
            "done": False,
            "timestamp": datetime.utcnow().isoformat(),
        }, websocket)
        await asyncio.sleep(0.1)  # Simulate streaming delay

    # Final message
    await manager.send_message({
        "type": "response",
        "content": accumulated.strip(),
        "done": True,
        "timestamp": datetime.utcnow().isoformat(),
    }, websocket)


@router.websocket("/notifications")
async def websocket_notifications(websocket: WebSocket, token: str = None):
    """
    WebSocket endpoint for push notifications.

    Sends:
    - Cost alerts
    - Usage limits
    - System notifications
    """
    # Similar authentication as chat endpoint
    if not token:
        await websocket.close(code=1008, reason="Authentication required")
        return

    try:
        payload = decode_token(token)
        user_id = payload.get("user_id")
    except Exception:
        await websocket.close(code=1008, reason="Authentication failed")
        return

    await websocket.accept()

    try:
        while True:
            # Keep connection alive
            await asyncio.sleep(settings.WS_HEARTBEAT_INTERVAL)
            await websocket.send_json({"type": "heartbeat"})
    except WebSocketDisconnect:
        pass
