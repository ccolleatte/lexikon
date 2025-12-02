"""
Rate limiting configuration using SlowAPI (FastAPI + limits)

Limits applied by tier:
- Auth endpoints: 5 requests/minute (brute force protection)
- quick-project: 100 requests/minute
- research-project: 500 requests/minute
- production-api: 2000 requests/minute
- Public endpoints: 1000 requests/minute (general public)

Returns HTTP 429 with rate limit headers (X-RateLimit-*) for client visibility.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import HTTPException, status, Response, Request
import re
from typing import Optional

# Create limiter instance with get_remote_address key function
limiter = Limiter(key_func=get_remote_address)

# Rate limit keys (for use in @limiter.limit() decorators)
RATE_LIMIT_AUTH = "5/minute"        # Brute force protection
RATE_LIMIT_API = "100/minute"       # Authenticated API users (default)
RATE_LIMIT_PUBLIC = "1000/minute"   # Public endpoints (search, etc.)

# Tier-based rate limits
TIER_LIMITS = {
    "quick-project": "100/minute",
    "research-project": "500/minute",
    "production-api": "2000/minute",
}

# Map limit strings to request counts for header calculation
LIMIT_MAP = {
    "5/minute": 5,
    "100/minute": 100,
    "500/minute": 500,
    "1000/minute": 1000,
    "2000/minute": 2000,
}


def get_tier_rate_limit(adoption_level: Optional[str]) -> str:
    """
    Get rate limit based on adoption level (tier).

    Args:
        adoption_level: User's adoption level (quick-project, research-project, production-api)

    Returns:
        Rate limit string (e.g., "100/minute")
    """
    return TIER_LIMITS.get(adoption_level, RATE_LIMIT_API)


def rate_limit_handler(request, exc: RateLimitExceeded):
    """
    Custom rate limit error handler with HTTP headers.
    Returns 429 with X-RateLimit-* headers for client visibility.
    """
    # Extract limit from exception detail (e.g., "5 per 1 minute")
    limit_value = 5  # Default fallback
    if exc.detail:
        match = re.search(r"(\d+)\s+per", exc.detail)
        if match:
            limit_value = int(match.group(1))

    error_response = HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail={
            "code": "RATE_LIMIT_EXCEEDED",
            "message": f"Too many requests. {exc.detail}",
        }
    )

    # Add rate limit headers to response
    error_response.headers = {
        "X-RateLimit-Limit": str(limit_value),
        "X-RateLimit-Remaining": "0",
        "X-RateLimit-Reset": "60",  # Seconds until limit resets
        "Retry-After": "60",  # Standard HTTP retry-after header
    }

    return error_response
