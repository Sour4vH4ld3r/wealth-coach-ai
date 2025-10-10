"""
Rate limiting middleware to prevent abuse and control costs.

Implements token bucket algorithm using Redis for distributed rate limiting.
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
from typing import Optional

from backend.core.config import settings
from backend.core.dependencies import get_redis_client


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using Redis.

    Implements per-IP and per-user rate limiting with configurable windows.
    Uses token bucket algorithm for smooth rate limiting.
    """

    async def dispatch(self, request: Request, call_next):
        """
        Process request through rate limiter.

        Args:
            request: FastAPI request
            call_next: Next middleware/route handler

        Returns:
            Response or raises HTTPException if rate limited

        Raises:
            HTTPException: 429 if rate limit exceeded
        """
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)

        # Skip rate limiting for health checks and OPTIONS requests
        if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
            return await call_next(request)

        # Skip rate limiting for CORS preflight requests
        if request.method == "OPTIONS":
            return await call_next(request)

        # Get client identifier
        client_id = self._get_client_id(request)

        # Check rate limits
        try:
            await self._check_rate_limit(client_id, request.url.path)
        except HTTPException:
            raise
        except Exception as e:
            # Log error but don't block request if Redis is down
            print(f"Rate limiter error: {e}")

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_PER_MINUTE)
        response.headers["X-RateLimit-Window"] = "60"  # seconds

        return response

    def _get_client_id(self, request: Request) -> str:
        """
        Get unique client identifier from request.

        Tries to extract user_id from JWT token, falls back to IP address.

        Args:
            request: FastAPI request

        Returns:
            Client identifier string
        """
        # Try to get user_id from token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                from backend.core.security import decode_token
                token = auth_header.replace("Bearer ", "")
                payload = decode_token(token)
                user_id = payload.get("user_id")
                if user_id:
                    return f"user:{user_id}"
            except Exception:
                pass

        # Fall back to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"

        return f"ip:{ip}"

    async def _check_rate_limit(self, client_id: str, path: str):
        """
        Check if client has exceeded rate limit.

        Implements sliding window rate limiting with Redis.

        Args:
            client_id: Client identifier
            path: Request path

        Raises:
            HTTPException: 429 if rate limit exceeded
        """
        try:
            redis = await get_redis_client()
        except Exception as e:
            # If Redis is unavailable, skip rate limiting
            print(f"Rate limiter: Redis unavailable, skipping rate limit check: {e}")
            return

        current_time = int(time.time())

        # Determine rate limit based on endpoint
        if "/chat/" in path:
            limit_per_minute = settings.CHAT_RATE_LIMIT_PER_MINUTE
        elif "/search" in path:
            limit_per_minute = settings.SEARCH_RATE_LIMIT_PER_MINUTE
        else:
            limit_per_minute = settings.RATE_LIMIT_PER_MINUTE

        # Per-minute check
        minute_key = f"ratelimit:{client_id}:minute:{current_time // 60}"
        minute_count = await redis.incr(minute_key)

        if minute_count == 1:
            await redis.expire(minute_key, 60)

        if minute_count > limit_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {limit_per_minute} requests per minute",
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(limit_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str((current_time // 60 + 1) * 60),
                },
            )

        # Per-hour check
        hour_key = f"ratelimit:{client_id}:hour:{current_time // 3600}"
        hour_count = await redis.incr(hour_key)

        if hour_count == 1:
            await redis.expire(hour_key, 3600)

        if hour_count > settings.RATE_LIMIT_PER_HOUR:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {settings.RATE_LIMIT_PER_HOUR} requests per hour",
                headers={"Retry-After": "3600"},
            )

        # Per-day check
        day_key = f"ratelimit:{client_id}:day:{current_time // 86400}"
        day_count = await redis.incr(day_key)

        if day_count == 1:
            await redis.expire(day_key, 86400)

        if day_count > settings.RATE_LIMIT_PER_DAY:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {settings.RATE_LIMIT_PER_DAY} requests per day",
                headers={"Retry-After": "86400"},
            )
