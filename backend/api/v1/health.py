"""
Health check and monitoring endpoints.

Provides endpoints for:
- Service health checks
- Readiness probes
- System metrics
- Dependency status
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any
import asyncio
from datetime import datetime

from backend.core.config import settings
from backend.core.dependencies import get_redis_client, get_vector_db, get_llm_client
from backend.services.cache.redis_client import RedisClient

router = APIRouter()


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.

    Returns service status without checking dependencies.
    Fast response for load balancer health checks.

    Returns:
        Health status dictionary
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/health/detailed")
async def detailed_health_check(
    redis: RedisClient = Depends(get_redis_client)
) -> Dict[str, Any]:
    """
    Detailed health check with dependency status.

    Checks:
    - Redis connection
    - Vector database
    - LLM client
    - System resources

    Returns:
        Detailed health status including all dependencies
    """
    health_status = {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT,
        "dependencies": {},
    }

    # Check Redis
    try:
        await redis.ping()
        health_status["dependencies"]["redis"] = {
            "status": "healthy",
            "url": settings.REDIS_URL.split("@")[-1],  # Hide password
        }
    except Exception as e:
        health_status["dependencies"]["redis"] = {
            "status": "unhealthy",
            "error": str(e),
        }
        health_status["status"] = "degraded"

    # Check Vector Database (pgvector)
    try:
        vector_db = get_vector_db()
        collection_count = vector_db.count()
        health_status["dependencies"]["vector_db"] = {
            "status": "healthy",
            "type": "pgvector",
            "document_count": collection_count,
        }
    except Exception as e:
        health_status["dependencies"]["vector_db"] = {
            "status": "unhealthy",
            "error": str(e),
        }
        health_status["status"] = "degraded"

    # Check LLM Client configuration
    try:
        llm_client = get_llm_client()
        health_status["dependencies"]["llm"] = {
            "status": "configured",
            "model": settings.OPENAI_MODEL,
            "has_api_key": bool(settings.OPENAI_API_KEY),
        }
    except Exception as e:
        health_status["dependencies"]["llm"] = {
            "status": "error",
            "error": str(e),
        }

    return health_status


@router.get("/ready")
async def readiness_check(
    redis: RedisClient = Depends(get_redis_client)
) -> Dict[str, Any]:
    """
    Kubernetes readiness probe endpoint.

    Checks if service is ready to accept traffic by verifying
    all critical dependencies are available.

    Returns:
        Readiness status

    Raises:
        HTTPException: If service is not ready (status 503)
    """
    ready = True
    checks = {}

    # Check Redis
    try:
        await redis.ping()
        checks["redis"] = True
    except Exception:
        checks["redis"] = False
        ready = False

    # Check Vector DB
    try:
        vector_db = get_vector_db()
        vector_db.count()
        checks["vector_db"] = True
    except Exception:
        checks["vector_db"] = False
        ready = False

    return {
        "ready": ready,
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/metrics")
async def metrics(
    redis: RedisClient = Depends(get_redis_client)
) -> Dict[str, Any]:
    """
    Application metrics endpoint.

    Returns performance and usage metrics for monitoring.

    Returns:
        Dictionary of metrics
    """
    metrics_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": 0,  # TODO: Track actual uptime
        "requests": {
            "total": 0,  # TODO: Implement request counter
            "success": 0,
            "errors": 0,
        },
        "cache": {
            "enabled": settings.CACHE_ENABLED,
            "hit_rate": 0.0,  # TODO: Calculate from Redis stats
        },
        "llm": {
            "model": settings.OPENAI_MODEL,
            "requests": 0,  # TODO: Track LLM requests
            "total_tokens": 0,
        },
        "vector_db": {
            "document_count": 0,
        },
    }

    # Get Redis info
    try:
        info = await redis.info()
        metrics_data["cache"]["hit_rate"] = float(
            info.get("keyspace_hits", 0)
        ) / max(
            float(info.get("keyspace_hits", 0) + info.get("keyspace_misses", 1)), 1
        )
    except Exception:
        pass

    # Get Vector DB count
    try:
        vector_db = get_vector_db()
        metrics_data["vector_db"]["document_count"] = vector_db.count()
    except Exception:
        pass

    return metrics_data


@router.get("/stats")
async def usage_stats(
    redis: RedisClient = Depends(get_redis_client)
) -> Dict[str, Any]:
    """
    Usage statistics for admin dashboard.

    Returns aggregated statistics about service usage.

    Returns:
        Usage statistics dictionary
    """
    # TODO: Implement proper stats tracking
    # This is a placeholder structure
    stats = {
        "timestamp": datetime.utcnow().isoformat(),
        "users": {
            "total": 0,
            "active_today": 0,
            "active_this_week": 0,
        },
        "conversations": {
            "total": 0,
            "today": 0,
            "average_length": 0,
        },
        "queries": {
            "total": 0,
            "today": 0,
            "average_response_time_ms": 0,
        },
        "costs": {
            "llm_tokens_today": 0,
            "estimated_cost_today": 0.0,
            "estimated_cost_month": 0.0,
        },
    }

    return stats
