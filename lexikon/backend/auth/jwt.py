"""
JWT token generation and validation.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

# Configuration from environment
JWT_SECRET = os.getenv("JWT_SECRET", "dev-jwt-secret-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenData:
    """Token payload data structure"""

    def __init__(
        self,
        user_id: str,
        email: str,
        token_type: str = "access",
        **extra_fields
    ):
        self.user_id = user_id
        self.email = email
        self.token_type = token_type
        self.extra_fields = extra_fields

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JWT payload"""
        return {
            "sub": self.user_id,
            "email": self.email,
            "type": self.token_type,
            **self.extra_fields,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TokenData":
        """Create TokenData from JWT payload"""
        user_id = data.get("sub")
        email = data.get("email")
        token_type = data.get("type", "access")

        # Extract extra fields
        extra = {k: v for k, v in data.items() if k not in ["sub", "email", "type", "exp", "iat"]}

        return cls(user_id=user_id, email=email, token_type=token_type, **extra)


def create_access_token(
    user_id: str,
    email: str,
    extra_data: Optional[Dict[str, Any]] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a new JWT access token.

    Args:
        user_id: User ID (will be stored in 'sub' claim)
        email: User email
        extra_data: Optional additional claims to include
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    token_data = TokenData(
        user_id=user_id,
        email=email,
        token_type="access",
        **(extra_data or {})
    )

    to_encode = token_data.to_dict()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    user_id: str,
    email: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a new JWT refresh token.

    Args:
        user_id: User ID
        email: User email
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT refresh token string
    """
    if expires_delta is None:
        expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    token_data = TokenData(
        user_id=user_id,
        email=email,
        token_type="refresh"
    )

    to_encode = token_data.to_dict()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str, expected_type: str = "access") -> Optional[TokenData]:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token string
        expected_type: Expected token type ('access' or 'refresh')

    Returns:
        TokenData if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        # Verify token type
        token_type = payload.get("type")
        if token_type != expected_type:
            return None

        return TokenData.from_dict(payload)

    except JWTError:
        return None


def decode_token_unsafe(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode token without verification (for debugging only).

    Args:
        token: JWT token string

    Returns:
        Decoded payload or None
    """
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM], options={"verify_signature": False})
    except Exception:
        return None


# Password utilities
def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password: Plain text password to check
        hashed_password: Hashed password to verify against

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_token_pair(user_id: str, email: str, extra_data: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
    """
    Create both access and refresh tokens.

    Args:
        user_id: User ID
        email: User email
        extra_data: Optional additional claims for access token

    Returns:
        Dictionary with 'access_token' and 'refresh_token' keys
    """
    access_token = create_access_token(user_id, email, extra_data)
    refresh_token = create_refresh_token(user_id, email)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # seconds
    }


def refresh_access_token(refresh_token: str) -> Optional[str]:
    """
    Generate a new access token from a refresh token.

    Args:
        refresh_token: Valid refresh token

    Returns:
        New access token or None if refresh token is invalid
    """
    token_data = verify_token(refresh_token, expected_type="refresh")

    if token_data is None:
        return None

    # Create new access token
    return create_access_token(token_data.user_id, token_data.email)
