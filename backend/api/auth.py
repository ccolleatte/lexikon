"""
Authentication API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from typing import Optional
import uuid
import logging

logger = logging.getLogger(__name__)

from db.postgres import get_db, User
from auth.jwt import (
    create_token_pair,
    hash_password,
    verify_password,
    verify_token,
    refresh_access_token,
)
from auth.middleware import get_current_user, AuthenticationError
from auth.api_keys import create_api_key, list_api_keys, revoke_api_key
from models import ApiResponse
from middleware.rate_limit import limiter, RATE_LIMIT_AUTH, RATE_LIMIT_API


router = APIRouter(prefix="/auth", tags=["authentication"])


# Request/Response Models
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=2, max_length=100)
    language: str = Field(default="fr", pattern="^(fr|en|es|de|it)$")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: dict


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


class CreateApiKeyRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    scopes: str = Field(default="read", pattern="^(read|write|admin|read,write)$")
    expires_in_days: Optional[int] = Field(None, ge=1, le=365)


class ApiKeyResponse(BaseModel):
    id: str
    name: str
    key: Optional[str] = None  # Only present when creating
    scopes: str
    is_active: bool
    created_at: str
    expires_at: Optional[str] = None
    last_used_at: Optional[str] = None


# Endpoints
@router.post("/register", status_code=201)
@limiter.limit(RATE_LIMIT_AUTH)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user account."""
    try:
        logger.info(f"Register: Starting for {request.email}")

        # Check if email already exists
        existing = db.query(User).filter(User.email == request.email).first()
        if existing:
            logger.warning(f"Register: Email {request.email} already exists")
            return ApiResponse(
                success=False,
                error={
                    "code": "EMAIL_EXISTS",
                    "message": "This email is already registered",
                    "details": {"email": request.email},
                },
            )

        logger.info(f"Register: Hashing password for {request.email}")
        # Hash password
        password_hash = hash_password(request.password)
        logger.info(f"Register: Password hashed successfully")

        # Create user
        user = User(
            id=str(uuid.uuid4()),
            email=request.email,
            password_hash=password_hash,
            first_name=request.first_name,
            last_name=request.last_name,
            language=request.language,
            adoption_level="quick-project",
            is_active=True,
        )
        logger.info(f"Register: User object created, saving to DB")

        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Register: User {request.email} saved to database")

        # Generate tokens
        logger.info(f"Register: Generating tokens")
        tokens = create_token_pair(user.id, user.email)
        logger.info(f"Register: Tokens generated: {list(tokens.keys())}")

        response_data = LoginResponse(
            **tokens,
            user={
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "language": user.language,
                "adoption_level": user.adoption_level,
            },
        )
        logger.info(f"Register: Response data prepared")

        return ApiResponse(success=True, data=response_data.model_dump())

    except Exception as e:
        logger.error(f"Register: Error - {type(e).__name__}: {str(e)}", exc_info=True)
        raise


@router.post("/login")
@limiter.limit(RATE_LIMIT_AUTH)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login with email and password."""

    # Find user
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        return ApiResponse(
            success=False,
            error={
                "code": "INVALID_CREDENTIALS",
                "message": "Invalid email or password",
            },
        )

    # Check if user has a password (OAuth-only users don't)
    if not user.password_hash:
        return ApiResponse(
            success=False,
            error={
                "code": "OAUTH_ONLY",
                "message": "This account uses OAuth. Please login with Google or GitHub.",
            },
        )

    # Verify password
    if not verify_password(request.password, user.password_hash):
        return ApiResponse(
            success=False,
            error={
                "code": "INVALID_CREDENTIALS",
                "message": "Invalid email or password",
            },
        )

    # Check if account is active
    if not user.is_active:
        return ApiResponse(
            success=False,
            error={
                "code": "ACCOUNT_DISABLED",
                "message": "Your account has been disabled",
            },
        )

    # Generate tokens
    tokens = create_token_pair(user.id, user.email)

    response_data = LoginResponse(
        **tokens,
        user={
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "language": user.language,
            "adoption_level": user.adoption_level,
        },
    )

    return ApiResponse(success=True, data=response_data.model_dump())


@router.post("/refresh")
async def refresh_token(request: RefreshTokenRequest):
    """Refresh access token using refresh token."""

    new_access_token = refresh_access_token(request.refresh_token)

    if not new_access_token:
        return ApiResponse(
            success=False,
            error={
                "code": "INVALID_REFRESH_TOKEN",
                "message": "Invalid or expired refresh token",
            },
        )

    return ApiResponse(
        success=True,
        data={
            "access_token": new_access_token,
            "token_type": "bearer",
        },
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout (client should discard tokens).
    In a production system, you'd maintain a token blacklist.
    """
    return ApiResponse(
        success=True,
        data={"message": "Logged out successfully"},
    )


@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information."""

    return ApiResponse(
        success=True,
        data={
            "id": current_user.id,
            "email": current_user.email,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "institution": current_user.institution,
            "primary_domain": current_user.primary_domain,
            "language": current_user.language,
            "country": current_user.country,
            "adoption_level": current_user.adoption_level,
            "is_active": current_user.is_active,
            "created_at": current_user.created_at.isoformat(),
        },
    )


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change user password."""

    # Check if user has a password (OAuth-only users don't)
    if not current_user.password_hash:
        return ApiResponse(
            success=False,
            error={
                "code": "OAUTH_ONLY",
                "message": "This account uses OAuth and doesn't have a password.",
            },
        )

    # Verify current password
    if not verify_password(request.current_password, current_user.password_hash):
        return ApiResponse(
            success=False,
            error={
                "code": "INVALID_PASSWORD",
                "message": "Current password is incorrect",
            },
        )

    # Hash new password
    new_password_hash = hash_password(request.new_password)

    # Update password
    current_user.password_hash = new_password_hash
    db.commit()

    return ApiResponse(
        success=True,
        data={"message": "Password changed successfully"},
    )


# API Key Management
@router.post("/api-keys", status_code=201)
async def create_new_api_key(
    request: CreateApiKeyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new API key (production-api tier only)."""

    # Check adoption level
    if current_user.adoption_level != "production-api":
        return ApiResponse(
            success=False,
            error={
                "code": "INSUFFICIENT_TIER",
                "message": "API keys are only available for production-api tier",
            },
        )

    try:
        api_key, plain_key = create_api_key(
            db=db,
            user_id=current_user.id,
            name=request.name,
            scopes=request.scopes,
            expires_in_days=request.expires_in_days,
        )

        response_data = ApiKeyResponse(
            id=api_key.id,
            name=api_key.name,
            key=plain_key,  # Only shown once!
            scopes=api_key.scopes,
            is_active=api_key.is_active,
            created_at=api_key.created_at.isoformat(),
            expires_at=api_key.expires_at.isoformat() if api_key.expires_at else None,
        )

        return ApiResponse(success=True, data=response_data.model_dump())

    except Exception as e:
        return ApiResponse(
            success=False,
            error={
                "code": "API_KEY_ERROR",
                "message": str(e),
            },
        )


@router.get("/api-keys")
async def list_user_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all API keys for current user."""

    api_keys = list_api_keys(db, current_user.id)

    keys_data = [
        ApiKeyResponse(
            id=key.id,
            name=key.name,
            scopes=key.scopes,
            is_active=key.is_active,
            created_at=key.created_at.isoformat(),
            expires_at=key.expires_at.isoformat() if key.expires_at else None,
            last_used_at=key.last_used_at.isoformat() if key.last_used_at else None,
        ).model_dump()
        for key in api_keys
    ]

    return ApiResponse(success=True, data=keys_data)


@router.delete("/api-keys/{key_id}")
async def revoke_user_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Revoke an API key."""

    success = revoke_api_key(db, key_id, current_user.id)

    if not success:
        return ApiResponse(
            success=False,
            error={
                "code": "KEY_NOT_FOUND",
                "message": "API key not found",
            },
        )

    return ApiResponse(
        success=True,
        data={"message": "API key revoked successfully"},
    )
