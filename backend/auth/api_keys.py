"""
API Key management for production-api tier users.
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from db.postgres import ApiKey


def generate_api_key() -> Tuple[str, str]:
    """
    Generate a new API key and its hash.

    Returns:
        Tuple of (plain_key, key_hash)
        plain_key: The actual key to give to user (only shown once)
        key_hash: Hashed version to store in database
    """
    # Generate random key (32 bytes = 64 hex characters)
    plain_key = "lxk_" + secrets.token_urlsafe(32)

    # Hash the key for storage
    key_hash = hashlib.sha256(plain_key.encode()).hexdigest()

    return plain_key, key_hash


def create_api_key(
    db: Session,
    user_id: str,
    name: str,
    scopes: str = "read",
    expires_in_days: Optional[int] = None,
) -> Tuple[ApiKey, str]:
    """
    Create a new API key for a user.

    Args:
        db: Database session
        user_id: User ID
        name: Friendly name for the key
        scopes: Comma-separated scopes (e.g., 'read', 'read,write', 'admin')
        expires_in_days: Optional expiration in days

    Returns:
        Tuple of (ApiKey model, plain_key string)
    """
    from db.postgres import User
    import uuid

    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User not found")

    # Generate key
    plain_key, key_hash = generate_api_key()

    # Calculate expiration
    expires_at = None
    if expires_in_days:
        expires_at = datetime.now() + timedelta(days=expires_in_days)

    # Create API key record
    api_key = ApiKey(
        id=str(uuid.uuid4()),
        user_id=user_id,
        key_hash=key_hash,
        name=name,
        scopes=scopes,
        is_active=True,
        expires_at=expires_at,
    )

    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    return api_key, plain_key


def verify_api_key(plain_key: str, db: Session) -> Optional[Tuple[str, str]]:
    """
    Verify an API key and return associated user ID and scopes.

    Args:
        plain_key: The API key to verify
        db: Database session

    Returns:
        Tuple of (user_id, scopes) if valid, None otherwise
    """
    # Hash the provided key
    key_hash = hashlib.sha256(plain_key.encode()).hexdigest()

    # Find API key in database
    api_key = db.query(ApiKey).filter(ApiKey.key_hash == key_hash).first()

    if not api_key:
        return None

    # Check if key is active
    if not api_key.is_active:
        return None

    # Check if key has expired
    if api_key.expires_at and api_key.expires_at < datetime.now():
        return None

    # Update last used timestamp
    api_key.last_used_at = datetime.now()
    db.commit()

    return api_key.user_id, api_key.scopes


def revoke_api_key(db: Session, key_id: str, user_id: str) -> bool:
    """
    Revoke (deactivate) an API key.

    Args:
        db: Database session
        key_id: API key ID
        user_id: User ID (for authorization check)

    Returns:
        True if revoked, False if not found or not authorized
    """
    api_key = (
        db.query(ApiKey)
        .filter(ApiKey.id == key_id, ApiKey.user_id == user_id)
        .first()
    )

    if not api_key:
        return False

    api_key.is_active = False
    db.commit()

    return True


def list_api_keys(db: Session, user_id: str) -> list[ApiKey]:
    """
    List all API keys for a user.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        List of ApiKey models
    """
    return (
        db.query(ApiKey)
        .filter(ApiKey.user_id == user_id)
        .order_by(ApiKey.created_at.desc())
        .all()
    )


def get_api_key(db: Session, key_id: str, user_id: str) -> Optional[ApiKey]:
    """
    Get a specific API key for a user.

    Args:
        db: Database session
        key_id: API key ID
        user_id: User ID

    Returns:
        ApiKey model or None
    """
    return (
        db.query(ApiKey)
        .filter(ApiKey.id == key_id, ApiKey.user_id == user_id)
        .first()
    )


def cleanup_expired_keys(db: Session) -> int:
    """
    Cleanup expired API keys (deactivate them).

    Args:
        db: Database session

    Returns:
        Number of keys deactivated
    """
    now = datetime.now()

    expired_keys = (
        db.query(ApiKey)
        .filter(ApiKey.expires_at < now, ApiKey.is_active == True)
        .all()
    )

    count = 0
    for key in expired_keys:
        key.is_active = False
        count += 1

    db.commit()

    return count
