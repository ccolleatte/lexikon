"""
Authentication middleware and dependencies for FastAPI routes.
"""

from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Callable
from sqlalchemy.orm import Session

from db.postgres import get_db, User
from auth.jwt import verify_token, TokenData
from auth.api_keys import verify_api_key


# Security scheme for Swagger UI
security = HTTPBearer(auto_error=False)


class AuthenticationError(HTTPException):
    """Custom authentication error"""

    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthorizationError(HTTPException):
    """Custom authorization error"""

    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


def get_token_from_header(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """
    Extract token from Authorization header.

    Args:
        authorization: Authorization header value

    Returns:
        Token string or None
    """
    if not authorization:
        return None

    # Handle "Bearer <token>" format
    if authorization.startswith("Bearer "):
        return authorization[7:]

    # Handle plain token
    return authorization


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    authorization: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> User:
    """
    Get current authenticated user from JWT token or API key.

    Supports multiple authentication methods:
    1. JWT Bearer token (Authorization: Bearer <token>)
    2. API Key (X-API-Key: <key>)

    Args:
        credentials: HTTP Bearer credentials from security scheme
        authorization: Raw Authorization header
        x_api_key: API key header
        db: Database session

    Returns:
        User object if authenticated

    Raises:
        AuthenticationError: If authentication fails
    """
    token = None

    # Try to get token from HTTPBearer
    if credentials:
        token = credentials.credentials
    # Try to get token from Authorization header
    elif authorization:
        token = get_token_from_header(authorization)

    # If token provided, verify JWT
    if token:
        token_data = verify_token(token, expected_type="access")
        if token_data is None:
            raise AuthenticationError("Invalid or expired token")

        # Get user from database
        user = db.query(User).filter(User.id == token_data.user_id).first()
        if not user:
            raise AuthenticationError("User not found")

        if not user.is_active:
            raise AuthenticationError("User account is disabled")

        return user

    # Try API key authentication
    if x_api_key:
        api_key_data = verify_api_key(x_api_key, db)
        if api_key_data is None:
            raise AuthenticationError("Invalid API key")

        user_id, scopes = api_key_data

        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise AuthenticationError("User not found")

        if not user.is_active:
            raise AuthenticationError("User account is disabled")

        # Attach scopes to user for authorization checks
        user.api_scopes = scopes
        return user

    # No authentication provided
    raise AuthenticationError("No authentication credentials provided")


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user (convenience dependency).

    Args:
        current_user: User from get_current_user

    Returns:
        User object if active

    Raises:
        AuthenticationError: If user is not active
    """
    if not current_user.is_active:
        raise AuthenticationError("User account is disabled")

    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    Get current user if authenticated, None otherwise.
    Useful for optional authentication on public endpoints.

    Args:
        credentials: HTTP Bearer credentials
        authorization: Authorization header
        db: Database session

    Returns:
        User object if authenticated, None otherwise
    """
    try:
        return await get_current_user(credentials, authorization, None, db)
    except AuthenticationError:
        return None


def require_scope(required_scope: str) -> Callable:
    """
    Create a dependency that requires a specific API scope.

    Args:
        required_scope: Required scope (e.g., 'write', 'admin')

    Returns:
        Dependency function
    """
    async def check_scope(current_user: User = Depends(get_current_user)):
        # If authenticated via JWT (not API key), allow all
        if not hasattr(current_user, "api_scopes"):
            return current_user

        # Check if user has required scope
        scopes = current_user.api_scopes.split(",")
        if required_scope not in scopes and "admin" not in scopes:
            raise AuthorizationError(
                f"This operation requires '{required_scope}' scope"
            )

        return current_user

    return check_scope


def require_adoption_level(minimum_level: str) -> Callable:
    """
    Create a dependency that requires a minimum adoption level.

    Args:
        minimum_level: Minimum adoption level required

    Returns:
        Dependency function
    """
    level_hierarchy = {
        "quick-project": 1,
        "research-project": 2,
        "production-api": 3,
    }

    async def check_adoption_level(current_user: User = Depends(get_current_user)):
        user_level = level_hierarchy.get(current_user.adoption_level, 0)
        required_level = level_hierarchy.get(minimum_level, 999)

        if user_level < required_level:
            raise AuthorizationError(
                f"This feature requires '{minimum_level}' adoption level or higher"
            )

        return current_user

    return check_adoption_level


# Convenience dependencies
RequireAuth = Depends(get_current_user)
RequireActiveUser = Depends(get_current_active_user)
OptionalAuth = Depends(get_optional_user)
RequireWriteScope = Depends(require_scope("write"))
RequireAdminScope = Depends(require_scope("admin"))
RequireProductionAPI = Depends(require_adoption_level("production-api"))
