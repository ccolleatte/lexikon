"""
Performance monitoring middleware.
Logs request processing time, database queries, and identifies bottlenecks.
"""

import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from contextvars import ContextVar

logger = logging.getLogger(__name__)

# Context variable for tracking request processing time
request_start_time: ContextVar[float] = ContextVar("request_start_time")
request_operation: ContextVar[str] = ContextVar("request_operation", default="unknown")


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """
    Middleware to monitor and log request processing performance.

    Logs:
    - Total request processing time
    - Response time from database
    - Slow requests (> 500ms)
    - Request size and response size
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request and measure performance."""

        # Record start time
        start_time = time.perf_counter()
        request_start_time.set(start_time)

        # Identify operation for logging
        operation = f"{request.method} {request.url.path}"
        request_operation.set(operation)

        # Get request size
        request_size_bytes = len(await request.body()) if request.method != "GET" else 0

        try:
            # Process request
            response = await call_next(request)

            # Calculate timing
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Add timing headers
            response.headers["X-Process-Time"] = f"{duration_ms:.2f}ms"

            # Log based on duration
            log_level = logging.INFO
            message_prefix = "Request"

            if duration_ms > 500:
                log_level = logging.WARNING
                message_prefix = "⚠️ SLOW REQUEST"
            elif duration_ms > 1000:
                log_level = logging.ERROR
                message_prefix = "🔴 VERY SLOW REQUEST"

            logger.log(
                log_level,
                f"{message_prefix}: {operation} completed in {duration_ms:.2f}ms "
                f"[status={response.status_code}, req_size={request_size_bytes}bytes]"
            )

            return response

        except Exception as e:
            # Log errors with timing
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                f"❌ Request error: {operation} failed after {duration_ms:.2f}ms - {type(e).__name__}: {str(e)}"
            )
            raise


class QueryCounterMiddleware(BaseHTTPMiddleware):
    """
    Middleware to count database queries per request.
    Use with SQLAlchemy echo=True or logging to identify N+1 queries.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """Track query count during request."""

        # In a real implementation, this would integrate with SQLAlchemy's
        # event system to count queries. For now, it's a placeholder.
        response = await call_next(request)

        # TODO: Integrate with SQLAlchemy events
        # response.headers["X-Query-Count"] = str(query_count)

        return response


def log_slow_query_warning(operation: str, duration_ms: float):
    """Log warning for slow queries to aid performance debugging."""
    if duration_ms > 100:
        logger.warning(
            f"⚠️ Slow query detected: {operation} took {duration_ms:.2f}ms - "
            f"Consider adding indexes or optimizing query"
        )


def get_request_processing_time() -> float:
    """Get current request processing time in milliseconds."""
    try:
        start = request_start_time.get()
        current_ms = (time.perf_counter() - start) * 1000
        return current_ms
    except LookupError:
        return 0.0


def get_request_operation() -> str:
    """Get current request operation name."""
    try:
        return request_operation.get()
    except LookupError:
        return "unknown"
