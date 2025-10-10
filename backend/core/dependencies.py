"""
FastAPI dependency injection utilities.

Provides reusable dependencies for database connections, caching,
authentication, and service initialization.
"""

from typing import AsyncGenerator, Optional
from functools import lru_cache
import redis.asyncio as redis

from backend.core.config import settings
from backend.services.vector_store.pgvector_store import get_vector_store, PGVectorStore
from backend.services.cache.redis_client import RedisClient
from backend.services.llm.client import LLMClient
from backend.services.rag.retriever import RAGRetriever


# =============================================================================
# REDIS CLIENT
# =============================================================================

_redis_client: Optional[RedisClient] = None


async def get_redis_client() -> RedisClient:
    """
    Get or create Redis client singleton.

    Returns:
        RedisClient instance
    """
    global _redis_client

    if _redis_client is None:
        _redis_client = RedisClient(
            url=settings.REDIS_URL,
            password=settings.REDIS_PASSWORD,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
        )
        await _redis_client.connect()

    return _redis_client


# =============================================================================
# VECTOR DATABASE
# =============================================================================

@lru_cache()
def get_vector_db() -> PGVectorStore:
    """
    Get or create PGVectorStore singleton.

    Uses LRU cache to ensure single instance per process.

    Returns:
        PGVectorStore instance
    """
    return get_vector_store()


# =============================================================================
# LLM CLIENT
# =============================================================================

_llm_client: Optional[LLMClient] = None


@lru_cache()
def get_llm_client() -> LLMClient:
    """
    Get or create LLM client singleton.

    Returns:
        LLMClient instance configured with settings
    """
    global _llm_client

    if _llm_client is None:
        _llm_client = LLMClient(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL,
            max_tokens=settings.OPENAI_MAX_TOKENS,
            temperature=settings.OPENAI_TEMPERATURE,
            timeout=settings.OPENAI_TIMEOUT,
        )

    return _llm_client


# =============================================================================
# RAG RETRIEVER
# =============================================================================

_rag_retriever: Optional[RAGRetriever] = None


@lru_cache()
def get_rag_retriever() -> RAGRetriever:
    """
    Get or create RAG retriever singleton.

    Returns:
        RAGRetriever instance
    """
    global _rag_retriever

    if _rag_retriever is None:
        vector_db = get_vector_db()
        _rag_retriever = RAGRetriever(
            vector_db=vector_db,
            top_k=settings.RAG_TOP_K,
            similarity_threshold=settings.RAG_SIMILARITY_THRESHOLD,
        )

    return _rag_retriever


# =============================================================================
# CLEANUP UTILITIES
# =============================================================================

async def close_redis_connection():
    """
    Close Redis connection pool.

    Should be called on application shutdown.
    """
    global _redis_client

    if _redis_client:
        await _redis_client.close()
        _redis_client = None


def persist_vector_db():
    """
    Persist vector database (pgvector auto-persists to PostgreSQL).

    Kept for backward compatibility but does nothing as pgvector
    automatically persists all data to PostgreSQL.
    """
    # pgvector automatically persists to PostgreSQL - no action needed
    pass
