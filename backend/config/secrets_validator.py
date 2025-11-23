"""Secrets validation module for production and development environments."""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class SecretValidationError(Exception):
    """Raised when a secret fails validation in production."""
    pass


# Weak default secrets that should NEVER be used in production
WEAK_DEFAULTS = {
    "your-jwt-secret-key-here",
    "your-api-key-secret-here",
    "dev-secret-change-in-production",
    "changeme",
    "your-secure-postgres-password-here",
    "your-secure-neo4j-password-here",
    "optional-redis-password",
    "your-google-client-id",
    "your-google-client-secret",
    "your-github-client-id",
    "your-github-client-secret",
    "your-domain.com",
    "https://your-domain.com",
    "",
}

MIN_SECRET_LENGTH = 32  # 32 hex chars = 128 bits


def is_valid_secret(secret: Optional[str], min_length: int = MIN_SECRET_LENGTH) -> bool:
    """
    Check if a secret is strong enough.

    Args:
        secret: The secret to validate
        min_length: Minimum length (default 32 for 128-bit entropy)

    Returns:
        True if secret is valid, False otherwise
    """
    if not secret:
        return False

    if secret in WEAK_DEFAULTS:
        return False

    if len(secret) < min_length:
        return False

    return True


def validate_secrets(strict: bool = True) -> None:
    """
    Validate all required secrets for the application.

    Args:
        strict: If True, raise exception on weak secrets (production mode).
               If False, only log warnings (development mode).

    Raises:
        SecretValidationError: In production mode if any secret is weak.

    Environment variables checked:
        - DATABASE_URL: PostgreSQL connection string (must not be SQLite)
        - JWT_SECRET: JWT signing key (min 32 chars)
        - API_KEY_SECRET: API key HMAC secret (min 32 chars)
        - REDIS_PASSWORD: Redis authentication (optional, but if set must be strong)
        - NEO4J_PASSWORD: Neo4j authentication (min 32 chars recommended)
    """
    environment = os.getenv("ENVIRONMENT", "development").lower()

    # List of validations: (env_var, required, description)
    secrets_to_check = [
        ("JWT_SECRET", True, "JWT signing secret"),
        ("API_KEY_SECRET", True, "API key HMAC secret"),
        ("DATABASE_URL", True, "Database connection string"),
        ("NEO4J_PASSWORD", False, "Neo4j authentication password (optional - deferred)"),
        ("REDIS_PASSWORD", False, "Redis password (optional)"),
    ]

    errors = []
    warnings = []

    for env_var, required, description in secrets_to_check:
        secret = os.getenv(env_var)

        # Check if required and missing
        if required and not secret:
            error_msg = f"Missing required secret: {env_var} ({description})"
            errors.append(error_msg)
            logger.error(error_msg)
            continue

        # Skip optional secrets if not set
        if not required and not secret:
            logger.info(f"Optional secret not set: {env_var}")
            continue

        # Check for weak defaults or short length
        if secret and not is_valid_secret(secret):
            msg = f"Weak or default secret: {env_var} ({description})"
            if strict or environment == "production":
                errors.append(msg)
                logger.error(msg)
            else:
                warnings.append(msg)
                logger.warning(msg)

    # Special validation for DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        if database_url.startswith("sqlite"):
            error_msg = "SQLite database NOT allowed in production. Configure proper PostgreSQL via DATABASE_URL (postgresql://...)"
            errors.append(error_msg)
            logger.error(error_msg)

    # Raise error if in production mode or strict mode and errors exist
    if errors:
        if strict or environment == "production":
            error_summary = "\n".join(errors)
            raise SecretValidationError(
                f"Secret validation failed. Fix the following issues:\n{error_summary}"
            )
        else:
            # In dev mode without strict, just warn
            for msg in errors:
                logger.warning(msg)

    if warnings:
        for msg in warnings:
            logger.warning(msg)

    if not errors and not warnings:
        logger.info("✓ All secrets validated successfully")
    elif warnings and not errors:
        logger.info(f"✓ Secrets validated (with {len(warnings)} warnings)")


def get_environment_mode() -> str:
    """
    Get current environment mode.

    Returns:
        'production', 'staging', or 'development'
    """
    return os.getenv("ENVIRONMENT", "development").lower()


def is_production() -> bool:
    """Check if running in production mode."""
    return get_environment_mode() == "production"


def is_development() -> bool:
    """Check if running in development mode."""
    return get_environment_mode() == "development"
