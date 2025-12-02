"""
Rate limiting configuration using SlowAPI (FastAPI + limits)

Limits applied:
- Auth endpoints: 5 requests/minute (brute force protection)
- API endpoints: 100 requests/minute (authenticated users)
- Public endpoints: 1000 requests/minute (general public)
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import HTTPException, status

# Create limiter instance with get_remote_address key function
limiter = Limiter(key_func=get_remote_address)

# Rate limit keys (for use in @limiter.limit() decorators)
RATE_LIMIT_AUTH = "5/minute"        # Brute force protection
RATE_LIMIT_API = "100/minute"       # Authenticated API users
RATE_LIMIT_PUBLIC = "1000/minute"   # Public endpoints (search, etc.)


def rate_limit_handler(request, exc: RateLimitExceeded):
    """
    Custom rate limit error handler.
    Returns structured JSON response instead of plain text.
    """
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail={
            "code": "RATE_LIMIT_EXCEEDED",
            "message": f"Too many requests. {exc.detail}",
        }
    )
