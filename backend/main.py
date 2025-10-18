"""
Wealth Coach AI Assistant - Main Application Entry Point

This module initializes the FastAPI application with all necessary middleware,
routers, and lifecycle events for the wealth coaching AI assistant.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import logging

from backend.core.config import settings
from backend.core.dependencies import get_redis_client, get_vector_db
from backend.middleware.rate_limiter import RateLimiterMiddleware
from backend.middleware.logging import LoggingMiddleware
from backend.api.v1 import chat, auth, user, health, onboarding, allocations, transactions
from backend.api.websocket import chat_ws
from backend.utils.logger import setup_logger

# Initialize logger
logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager - handles startup and shutdown events.

    Startup:
    - Initialize Redis connection pool
    - Load vector database
    - Warm up embedding model

    Shutdown:
    - Close Redis connections
    - Persist vector database
    - Cleanup resources
    """
    logger.info("Starting Wealth Coach AI Assistant...")

    # Startup tasks
    try:
        # Initialize Redis (optional - continue without it)
        try:
            redis_client = await get_redis_client()
            await redis_client.ping()
            logger.info("✓ Redis connection established")
        except Exception as redis_error:
            logger.warning(f"⚠️  Redis not available: {redis_error}. Caching disabled.")
            logger.warning("   Install Redis: brew install redis && redis-server")

        # Initialize Vector DB
        vector_db = get_vector_db()
        logger.info("✓ Vector database loaded")

        # Warm up embedding model (first load is slow)
        logger.info("Loading embedding model (this may take a moment)...")
        from backend.services.rag.embeddings import EmbeddingService
        embedding_service = EmbeddingService()
        _ = embedding_service.embed_query("warmup query")
        logger.info("✓ Embedding model warmed up")

        logger.info(f"🚀 Server ready on {settings.HOST}:{settings.PORT}")
        logger.info(f"📚 API Docs: http://{settings.HOST}:{settings.PORT}/docs")

    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

    yield

    # Shutdown tasks
    logger.info("Shutting down Wealth Coach AI Assistant...")
    try:
        # Close Redis connections (Redis client is synchronous, no async close needed)
        try:
            redis_client = get_redis_client()
            if hasattr(redis_client, 'close'):
                redis_client.close()
            logger.info("✓ Redis connections closed")
        except Exception as redis_err:
            logger.warning(f"Redis cleanup skipped: {redis_err}")

        # Persist vector database
        try:
            vector_db.persist()
            logger.info("✓ Vector database persisted")
        except Exception as vdb_err:
            logger.warning(f"Vector DB persist skipped: {vdb_err}")

    except Exception as e:
        logger.error(f"Shutdown error: {e}")


# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered financial coaching assistant with RAG-based knowledge retrieval",
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.ENABLE_SWAGGER_UI else None,
    redoc_url="/redoc" if settings.ENABLE_REDOC else None,
    lifespan=lifespan,
)


# =============================================================================
# MIDDLEWARE CONFIGURATION
# =============================================================================
# Note: Middleware is applied in reverse order - last added executes first

# Request/response logging (executes first)
app.add_middleware(LoggingMiddleware)

# Rate limiting middleware
if settings.RATE_LIMIT_ENABLED:
    app.add_middleware(RateLimiterMiddleware)

# GZip compression for response payloads
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS - Must be last to wrap all responses (executes last)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# EXCEPTION HANDLERS
# =============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.
    Logs errors and returns sanitized response to client.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "request_id": request.state.request_id if hasattr(request.state, "request_id") else None,
        }
    )


@app.exception_handler(ValueError)
async def validation_exception_handler(request: Request, exc: ValueError):
    """Handle validation errors with 400 Bad Request."""
    return JSONResponse(
        status_code=400,
        content={
            "error": "Validation error",
            "message": str(exc),
        }
    )


# =============================================================================
# ROUTERS
# =============================================================================

# API v1 routes
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(user.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(onboarding.router, prefix="/api/v1/onboarding", tags=["Onboarding"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(allocations.router, prefix="/api/v1", tags=["Allocations"])
app.include_router(transactions.router, prefix="/api/v1", tags=["Transactions"])

# WebSocket routes
if settings.WS_ENABLED:
    app.include_router(chat_ws.router, prefix="/ws", tags=["WebSocket"])


# =============================================================================
# ROOT ENDPOINTS
# =============================================================================

@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": "/docs" if settings.ENABLE_SWAGGER_UI else "disabled",
        "health": "/api/v1/health",
    }


@app.get("/health")
async def health_check():
    """Quick health check endpoint for load balancers."""
    return {"status": "healthy"}


# =============================================================================
# STARTUP MESSAGE
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=settings.WORKERS if not settings.DEBUG else 1,
        log_level=settings.LOG_LEVEL.lower(),
    )
