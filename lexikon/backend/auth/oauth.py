"""
OAuth2 authentication with Google and GitHub.
"""

import os
import uuid
from typing import Optional, Dict, Any
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.orm import Session

from db.postgres import User, OAuthAccount
from auth.jwt import create_token_pair


# OAuth configuration from environment
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv(
    "GOOGLE_REDIRECT_URI", "http://localhost:5173/oauth/callback/google"
)

# GitHub OAuth removed (2025-11-27) - GitHub not in target providers


# Initialize OAuth client
oauth = OAuth()


def register_oauth_providers():
    """Register OAuth providers with Authlib"""

    # Google OAuth2
    if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
        oauth.register(
            name="google",
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={"scope": "openid email profile"},
        )

    # GitHub OAuth removed (2025-11-27)


# Call during app startup
register_oauth_providers()


class OAuthProviderError(Exception):
    """OAuth provider error"""
    pass


def get_or_create_oauth_user(
    db: Session,
    provider: str,
    provider_user_id: str,
    email: str,
    first_name: str,
    last_name: str,
    access_token: Optional[str] = None,
    refresh_token: Optional[str] = None,
    expires_at: Optional[int] = None,
) -> User:
    """
    Get or create a user from OAuth provider data.

    Args:
        db: Database session
        provider: OAuth provider name ('google', 'github')
        provider_user_id: User ID from provider
        email: User email
        first_name: User first name
        last_name: User last name
        access_token: OAuth access token
        refresh_token: OAuth refresh token
        expires_at: Token expiration timestamp

    Returns:
        User model
    """
    from datetime import datetime

    # Check if OAuth account exists
    oauth_account = (
        db.query(OAuthAccount)
        .filter(
            OAuthAccount.provider == provider,
            OAuthAccount.provider_user_id == provider_user_id,
        )
        .first()
    )

    if oauth_account:
        # Update tokens
        oauth_account.access_token = access_token
        oauth_account.refresh_token = refresh_token
        if expires_at:
            oauth_account.expires_at = datetime.fromtimestamp(expires_at)
        oauth_account.updated_at = datetime.now()

        db.commit()
        db.refresh(oauth_account)

        # Get associated user
        user = db.query(User).filter(User.id == oauth_account.user_id).first()
        return user

    # Check if user with email exists
    user = db.query(User).filter(User.email == email).first()

    if not user:
        # Create new user
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            first_name=first_name,
            last_name=last_name,
            password_hash=None,  # OAuth-only users don't have passwords
            adoption_level="quick-project",
            language="fr",
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Create OAuth account link
    oauth_account = OAuthAccount(
        id=str(uuid.uuid4()),
        user_id=user.id,
        provider=provider,
        provider_user_id=provider_user_id,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=datetime.fromtimestamp(expires_at) if expires_at else None,
    )

    db.add(oauth_account)
    db.commit()
    db.refresh(oauth_account)

    return user


def extract_user_info_from_google(user_info: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract user information from Google OAuth response.

    Args:
        user_info: User info from Google

    Returns:
        Dictionary with email, first_name, last_name, provider_user_id
    """
    email = user_info.get("email")
    given_name = user_info.get("given_name", "")
    family_name = user_info.get("family_name", "")
    provider_user_id = user_info.get("sub") or user_info.get("id")

    if not email or not provider_user_id:
        raise OAuthProviderError("Missing required fields from Google")

    return {
        "email": email,
        "first_name": given_name or email.split("@")[0],
        "last_name": family_name or "",
        "provider_user_id": provider_user_id,
    }


def extract_user_info_from_github(user_info: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract user information from GitHub OAuth response.

    Args:
        user_info: User info from GitHub

    Returns:
        Dictionary with email, first_name, last_name, provider_user_id
    """
    email = user_info.get("email")
    name = user_info.get("name", "")
    login = user_info.get("login", "")
    provider_user_id = str(user_info.get("id"))

    if not provider_user_id:
        raise OAuthProviderError("Missing required fields from GitHub")

    # GitHub doesn't always provide email in user info
    # In production, you'd need to make a separate API call to /user/emails
    if not email:
        email = f"{login}@github-users.noreply.github.com"

    # Parse name into first/last
    if name:
        name_parts = name.split(maxsplit=1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""
    else:
        first_name = login
        last_name = ""

    return {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "provider_user_id": provider_user_id,
    }


async def handle_oauth_callback(
    db: Session,
    provider: str,
    user_info: Dict[str, Any],
    token: Optional[Dict[str, Any]] = None,
) -> Dict[str, str]:
    """
    Handle OAuth callback and create/login user.

    Args:
        db: Database session
        provider: OAuth provider name
        user_info: User info from provider
        token: OAuth token info (access_token, refresh_token, etc.)

    Returns:
        Dictionary with access_token, refresh_token, user info
    """
    # Extract user info based on provider
    if provider == "google":
        extracted_info = extract_user_info_from_google(user_info)
    elif provider == "github":
        extracted_info = extract_user_info_from_github(user_info)
    else:
        raise OAuthProviderError(f"Unsupported provider: {provider}")

    # Extract token info
    access_token = None
    refresh_token = None
    expires_at = None

    if token:
        access_token = token.get("access_token")
        refresh_token = token.get("refresh_token")
        expires_in = token.get("expires_in")
        if expires_in:
            from datetime import datetime
            expires_at = int((datetime.now().timestamp() + expires_in))

    # Get or create user
    user = get_or_create_oauth_user(
        db=db,
        provider=provider,
        provider_user_id=extracted_info["provider_user_id"],
        email=extracted_info["email"],
        first_name=extracted_info["first_name"],
        last_name=extracted_info["last_name"],
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=expires_at,
    )

    # Generate JWT tokens for our system
    tokens = create_token_pair(
        user_id=user.id,
        email=user.email,
        extra_data={"provider": provider},
    )

    return {
        **tokens,
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "adoption_level": user.adoption_level,
        },
    }


def unlink_oauth_account(db: Session, user_id: str, provider: str) -> bool:
    """
    Unlink an OAuth account from a user.

    Args:
        db: Database session
        user_id: User ID
        provider: OAuth provider to unlink

    Returns:
        True if unlinked, False if not found
    """
    oauth_account = (
        db.query(OAuthAccount)
        .filter(OAuthAccount.user_id == user_id, OAuthAccount.provider == provider)
        .first()
    )

    if not oauth_account:
        return False

    db.delete(oauth_account)
    db.commit()

    return True


def list_oauth_accounts(db: Session, user_id: str) -> list[OAuthAccount]:
    """
    List all OAuth accounts for a user.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        List of OAuthAccount models
    """
    return (
        db.query(OAuthAccount)
        .filter(OAuthAccount.user_id == user_id)
        .order_by(OAuthAccount.created_at.desc())
        .all()
    )
