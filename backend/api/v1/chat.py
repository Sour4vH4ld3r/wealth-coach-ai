"""
Chat API endpoints for conversational financial advice.

Handles synchronous chat requests with RAG-enhanced responses.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import json

from backend.core.security import get_current_user_id
from backend.core.dependencies import get_llm_client, get_rag_retriever, get_redis_client
from backend.services.llm.client import LLMClient
from backend.services.rag.retriever import RAGRetriever
from backend.services.cache.redis_client import RedisClient
from backend.core.config import settings
from backend.db.database import get_db
from backend.db.models import UserProfile, ChatSession, ChatMessage
import hashlib
import json
import uuid

router = APIRouter()


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class Message(BaseModel):
    """Single chat message."""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., min_length=1, max_length=5000)
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    """Chat request with conversation history."""
    message: str = Field(..., min_length=1, max_length=2000, description="User's question")
    conversation_history: List[Message] = Field(default=[], max_length=20)
    use_rag: bool = Field(default=True, description="Enable RAG context retrieval")
    stream: bool = Field(default=False, description="Stream response (not yet implemented)")
    session_id: Optional[str] = Field(None, description="Chat session ID for continuing conversation")


class ChatResponse(BaseModel):
    """Chat response from AI assistant."""
    response: str
    sources: List[dict] = Field(default=[], description="Source documents used")
    conversation_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    cached: bool = Field(default=False, description="Response from cache")
    tokens_used: Optional[int] = None


class ConversationHistory(BaseModel):
    """Conversation history response."""
    conversation_id: str
    messages: List[Message]
    created_at: datetime
    updated_at: datetime


# =============================================================================
# CHAT ENDPOINTS
# =============================================================================

@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id),
    llm: LLMClient = Depends(get_llm_client),
    rag: RAGRetriever = Depends(get_rag_retriever),
    redis: RedisClient = Depends(get_redis_client),
    db: Session = Depends(get_db),
):
    """
    Send a message and receive AI-powered financial advice.

    Flow:
    1. Check cache for similar query
    2. If RAG enabled, retrieve relevant context
    3. Generate response using LLM
    4. Cache response
    5. Return response with sources

    Args:
        request: Chat request with message and history
        user_id: Authenticated user ID
        llm: LLM client instance
        rag: RAG retriever instance
        redis: Redis client for caching

    Returns:
        AI-generated response with sources

    Raises:
        HTTPException: On LLM or RAG failure
    """
    # Generate cache key from message + history
    cache_key = _generate_cache_key(request.message, request.conversation_history)

    # Check cache first
    if settings.CACHE_ENABLED:
        try:
            cached_response = await redis.get(cache_key)
            if cached_response:
                return ChatResponse(**json.loads(cached_response), cached=True)
        except Exception as e:
            # Redis unavailable, continue without cache
            print(f"Cache check failed (Redis unavailable): {e}")

    # Fetch user profile for personalized context
    user_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    # Load recent conversation history from database for AI context
    # If session_id provided, load from that session; otherwise load from most recent session
    db_conversation_history = []
    if request.session_id:
        # Load last 10 messages from this session for context
        recent_messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == request.session_id
        ).order_by(
            ChatMessage.created_at.desc()
        ).limit(10).all()

        # Reverse to get chronological order
        for msg in reversed(recent_messages):
            db_conversation_history.append(Message(
                role=msg.role,
                content=msg.content,
                timestamp=msg.created_at
            ))

    # Retrieve relevant context if RAG enabled
    context_documents = []
    sources = []

    if request.use_rag:
        try:
            retrieval_results = await rag.retrieve(
                query=request.message,
                top_k=settings.RAG_TOP_K,
            )
            context_documents = retrieval_results.documents
            sources = retrieval_results.sources
        except Exception as e:
            # Log error but continue without RAG context
            print(f"RAG retrieval failed: {e}")

    # Build prompt with context and user profile
    system_prompt = _build_system_prompt(context_documents, user_profile)

    # Merge database history with request history (prefer database history)
    combined_history = db_conversation_history if db_conversation_history else request.conversation_history

    messages = _build_conversation_messages(
        system_prompt=system_prompt,
        conversation_history=combined_history,
        user_message=request.message,
    )

    # Generate response
    try:
        llm_response = await llm.chat(
            messages=messages,
            max_tokens=settings.MAX_TOKENS_PER_REQUEST,
        )

        response_text = llm_response.content
        tokens_used = llm_response.usage.total_tokens if llm_response.usage else None

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate response: {str(e)}",
        )

    # Get or create chat session
    if request.session_id:
        session = db.query(ChatSession).filter(
            ChatSession.id == request.session_id,
            ChatSession.user_id == user_id
        ).first()
        if not session:
            # Invalid session_id, create new session
            session = ChatSession(id=str(uuid.uuid4()), user_id=user_id)
            db.add(session)
    else:
        # Create new session
        session = ChatSession(id=str(uuid.uuid4()), user_id=user_id)
        db.add(session)

    db.flush()  # Get session ID without committing

    # Save user message to database
    user_message_db = ChatMessage(
        session_id=session.id,
        role="user",
        content=request.message,
        created_at=datetime.utcnow()
    )
    db.add(user_message_db)

    # Save assistant response to database
    assistant_message_db = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=response_text,
        tokens_used=tokens_used,
        sources_count=len(sources),
        cached=False,
        created_at=datetime.utcnow()
    )
    db.add(assistant_message_db)

    # Update session timestamp
    session.updated_at = datetime.utcnow()

    db.commit()

    # Prepare response
    chat_response = ChatResponse(
        response=response_text,
        sources=sources,
        tokens_used=tokens_used,
        timestamp=datetime.utcnow(),
        conversation_id=session.id,
    )

    # Cache response (convert datetime to ISO string for JSON serialization)
    if settings.CACHE_ENABLED:
        try:
            cache_data = chat_response.dict()
            if 'timestamp' in cache_data and isinstance(cache_data['timestamp'], datetime):
                cache_data['timestamp'] = cache_data['timestamp'].isoformat()
            await redis.set(
                cache_key,
                json.dumps(cache_data),
                ex=settings.QUERY_CACHE_TTL,
            )
        except Exception as e:
            # Redis unavailable, continue without caching
            print(f"Cache set failed (Redis unavailable): {e}")

    return chat_response


@router.post("/message/stream")
async def send_message_stream(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id),
    llm: LLMClient = Depends(get_llm_client),
    rag: RAGRetriever = Depends(get_rag_retriever),
    db: Session = Depends(get_db),
):
    """
    Send a message and receive streaming AI response (token by token).

    Flow:
    1. If RAG enabled, retrieve relevant context
    2. Generate streaming response using LLM
    3. Save to database after streaming completes
    4. Return tokens as Server-Sent Events (SSE)

    Args:
        request: Chat request with message and history
        user_id: Authenticated user ID
        llm: LLM client instance
        rag: RAG retriever instance
        db: Database session

    Returns:
        Streaming response with tokens
    """
    # Fetch user profile for personalized context
    user_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    # Load recent conversation history from database
    db_conversation_history = []
    if request.session_id:
        recent_messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == request.session_id
        ).order_by(
            ChatMessage.created_at.desc()
        ).limit(10).all()

        for msg in reversed(recent_messages):
            db_conversation_history.append(Message(
                role=msg.role,
                content=msg.content,
                timestamp=msg.created_at
            ))

    # Retrieve relevant context if RAG enabled
    context_documents = []
    sources = []

    if request.use_rag:
        try:
            retrieval_results = await rag.retrieve(
                query=request.message,
                top_k=settings.RAG_TOP_K,
            )
            context_documents = retrieval_results.documents
            sources = retrieval_results.sources
        except Exception as e:
            print(f"RAG retrieval failed: {e}")

    # Build prompt with context and user profile
    system_prompt = _build_system_prompt(context_documents, user_profile)

    # Merge database history with request history
    combined_history = db_conversation_history if db_conversation_history else request.conversation_history

    messages = _build_conversation_messages(
        system_prompt=system_prompt,
        conversation_history=combined_history,
        user_message=request.message,
    )

    # Get or create chat session
    if request.session_id:
        session = db.query(ChatSession).filter(
            ChatSession.id == request.session_id,
            ChatSession.user_id == user_id
        ).first()
        if not session:
            session = ChatSession(id=str(uuid.uuid4()), user_id=user_id)
            db.add(session)
    else:
        session = ChatSession(id=str(uuid.uuid4()), user_id=user_id)
        db.add(session)

    db.flush()

    # Save user message to database
    try:
        print(f"[DEBUG] Saving user message for session {session.id}")
        user_message_db = ChatMessage(
            session_id=session.id,
            role="user",
            content=request.message,
            created_at=datetime.utcnow()
        )
        db.add(user_message_db)
        db.commit()
        print(f"[DEBUG] Successfully saved user message to database")
    except Exception as user_save_error:
        print(f"[ERROR] Failed to save user message: {user_save_error}")
        db.rollback()
        raise

    # Extract session_id before generator (avoid detached instance error)
    session_id = session.id

    # Stream generator function
    async def generate_stream():
        full_response = ""
        try:
            # Send session_id first
            yield f"data: {json.dumps({'type': 'session_id', 'session_id': session_id})}\n\n"

            # Send sources if available
            if sources:
                yield f"data: {json.dumps({'type': 'sources', 'sources': sources})}\n\n"

            # Stream tokens
            async for token in llm.chat_stream(messages=messages, max_tokens=settings.MAX_TOKENS_PER_REQUEST):
                full_response += token
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

            # Send completion signal
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

            # Save assistant response to database using a new session
            try:
                from backend.db.database import get_db
                from sqlalchemy.orm import Session as DBSession

                new_db_gen = get_db()
                new_db: DBSession = next(new_db_gen)

                try:
                    print(f"[DEBUG] Saving assistant message for session {session_id}, content length: {len(full_response)}")

                    assistant_message_db = ChatMessage(
                        session_id=session_id,
                        role="assistant",
                        content=full_response,
                        tokens_used=None,  # We don't track tokens for streaming
                        sources_count=len(sources),
                        cached=False,
                        created_at=datetime.utcnow()
                    )
                    new_db.add(assistant_message_db)

                    # Update session timestamp
                    chat_session = new_db.query(ChatSession).filter(ChatSession.id == session_id).first()
                    if chat_session:
                        chat_session.updated_at = datetime.utcnow()

                    new_db.commit()
                    print(f"[DEBUG] Successfully saved assistant message to database")

                except Exception as save_error:
                    print(f"[ERROR] Failed to save assistant message: {save_error}")
                    new_db.rollback()
                    raise
                finally:
                    new_db.close()

            except Exception as db_error:
                print(f"[ERROR] Database session error: {db_error}")

        except Exception as e:
            print(f"[ERROR] Stream generation error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.get("/sessions")
async def get_chat_sessions(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 20,
):
    """
    Get user's chat sessions with pagination.

    Returns list of sessions with their latest message preview.
    Frontend can load messages for specific session separately.

    Performance optimized: Uses SQL aggregation to avoid N+1 queries.
    """
    from sqlalchemy import func, case
    from sqlalchemy.orm import aliased

    # Subquery for first user message (preview)
    FirstMessage = aliased(ChatMessage)
    first_msg_subq = db.query(
        FirstMessage.session_id,
        func.min(FirstMessage.created_at).label('min_created')
    ).filter(
        FirstMessage.role == "user"
    ).group_by(FirstMessage.session_id).subquery()

    # Subquery for message count
    msg_count_subq = db.query(
        ChatMessage.session_id,
        func.count(ChatMessage.id).label('message_count')
    ).group_by(ChatMessage.session_id).subquery()

    # Main query with left joins
    query = db.query(
        ChatSession,
        ChatMessage.content.label('preview_content'),
        msg_count_subq.c.message_count
    ).outerjoin(
        first_msg_subq,
        ChatSession.id == first_msg_subq.c.session_id
    ).outerjoin(
        ChatMessage,
        (ChatSession.id == ChatMessage.session_id) &
        (ChatMessage.created_at == first_msg_subq.c.min_created) &
        (ChatMessage.role == "user")
    ).outerjoin(
        msg_count_subq,
        ChatSession.id == msg_count_subq.c.session_id
    ).filter(
        ChatSession.user_id == user_id
    ).order_by(
        ChatSession.updated_at.desc()
    ).offset(skip).limit(limit)

    result = []
    for session, preview_content, message_count in query:
        result.append({
            "session_id": session.id,
            "preview": preview_content[:100] if preview_content else "New conversation",
            "message_count": message_count or 0,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
        })

    return {"sessions": result, "total": len(result)}


@router.get("/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50,
):
    """
    Get messages for a specific session with pagination.

    This endpoint supports infinite scrolling. Load older messages by
    increasing the skip parameter.

    Args:
        session_id: Session ID
        skip: Number of messages to skip (for pagination)
        limit: Maximum messages to return (default 50)

    Returns:
        Paginated list of messages
    """
    # Verify session belongs to user
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == user_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # Get messages with pagination (newest first)
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(
        ChatMessage.created_at.desc()
    ).offset(skip).limit(limit).all()

    # Get total count
    total = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).count()

    # Convert to response format (reverse to show oldest first)
    message_list = []
    for msg in reversed(messages):
        message_list.append({
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.created_at.isoformat(),
            "tokens_used": msg.tokens_used,
            "sources_count": msg.sources_count,
            "cached": msg.cached,
        })

    return {
        "session_id": session_id,
        "messages": message_list,
        "total": total,
        "has_more": (skip + limit) < total
    }


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """
    Delete a conversation.

    Args:
        conversation_id: Conversation ID to delete
        user_id: Authenticated user ID

    Returns:
        Success message
    """
    # TODO: Implement database deletion
    return {"message": "Conversation deleted successfully"}


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def _generate_cache_key(message: str, history: List[Message]) -> str:
    """Generate deterministic cache key from message and history."""
    # Include last 3 messages in cache key for context-aware caching
    history_text = " ".join([m.content for m in history[-3:]])
    cache_input = f"{history_text}|{message}"
    return f"chat:response:{hashlib.sha256(cache_input.encode()).hexdigest()}"


def _build_system_prompt(context_documents: List[str], user_profile: Optional[UserProfile] = None) -> str:
    """Build system prompt with RAG context and user profile."""
    base_prompt = f"""You are WealthWarriors AI, a knowledgeable financial advisor assistant created by the WealthWarriors development team.

ABOUT YOU:
- You are WealthWarriors AI, an intelligent financial coaching assistant
- You were created by the WealthWarriors team to help people achieve financial freedom
- Your mission is to empower individuals with financial knowledge and guidance
- You provide personalized, educational financial advice based on each user's profile and goals

{settings.FINANCIAL_DISCLAIMER}

IMPORTANT GUIDELINES:
- Provide educational information, not personalized investment advice
- Explain financial concepts clearly in simple terms
- Cite sources when using specific information
- Recommend consulting a licensed financial advisor for personalized advice
- Be honest when you don't know something
- When asked about who created you, mention you were built by the WealthWarriors team
- Maintain a friendly, supportive, and empowering tone
"""

    # Add user profile context for personalized responses
    if user_profile and user_profile.onboarding_completed:
        profile_context = "\n\nUSER PROFILE:\n"
        if user_profile.age_range:
            profile_context += f"- Age range: {user_profile.age_range}\n"
        if user_profile.occupation:
            profile_context += f"- Occupation: {user_profile.occupation}\n"
        if user_profile.income_range:
            profile_context += f"- Income range: {user_profile.income_range}\n"
        if user_profile.financial_goals:
            profile_context += f"- Financial goals: {user_profile.financial_goals}\n"
        if user_profile.investment_experience:
            profile_context += f"- Investment experience: {user_profile.investment_experience}\n"
        if user_profile.risk_tolerance:
            profile_context += f"- Risk tolerance: {user_profile.risk_tolerance}\n"
        if user_profile.current_investments:
            profile_context += f"- Current investments: {user_profile.current_investments}\n"
        if user_profile.debt_status:
            profile_context += f"- Debt status: {user_profile.debt_status}\n"
        if user_profile.retirement_planning:
            profile_context += f"- Interested in retirement planning: Yes\n"
        if user_profile.interests:
            profile_context += f"- Interests: {user_profile.interests}\n"

        profile_context += "\nUse this information to provide more relevant and personalized guidance while maintaining educational focus.\n"
        base_prompt += profile_context

    if context_documents:
        context_text = "\n\n".join([f"Source {i+1}:\n{doc}" for i, doc in enumerate(context_documents)])
        base_prompt += f"\n\nRELEVANT INFORMATION:\n{context_text}\n\n"

    return base_prompt


def _build_conversation_messages(
    system_prompt: str,
    conversation_history: List[Message],
    user_message: str,
) -> List[dict]:
    """Build message array for LLM API."""
    messages = [{"role": "system", "content": system_prompt}]

    # Add conversation history
    for msg in conversation_history[-10:]:  # Last 10 messages only
        messages.append({
            "role": msg.role,
            "content": msg.content,
        })

    # Add current user message
    messages.append({
        "role": "user",
        "content": user_message,
    })

    return messages
