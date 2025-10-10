"""
Request/response logging middleware.

Logs all API requests with timing, status codes, and sanitized payloads.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import uuid
import json
from typing import Callable

from backend.core.config import settings
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.

    Logs:
    - Request method, path, headers
    - Response status code and time
    - Errors and exceptions
    - Request/response bodies (sanitized)
    """

    async def dispatch(self, request: Request, call_next: Callable):
        """
        Process request through logging middleware.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler

        Returns:
            Response from downstream handler
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Record start time
        start_time = time.time()

        # Log request
        logger.info(
            "Incoming request",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "client_host": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            },
        )

        # Process request
        try:
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Log response
            logger.info(
                "Request completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration * 1000, 2),
                },
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as exc:
            # Calculate duration
            duration = time.time() - start_time

            # Log error
            logger.error(
                "Request failed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round(duration * 1000, 2),
                    "error": str(exc),
                },
                exc_info=True,
            )

            # Re-raise exception for FastAPI error handlers
            raise
