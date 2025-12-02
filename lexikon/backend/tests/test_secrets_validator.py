"""Tests for secrets validation module."""

import os
import pytest
from config.secrets_validator import (
    validate_secrets,
    is_valid_secret,
    SecretValidationError,
    is_production,
    is_development,
)


class TestSecretValidation:
    """Test secret validation logic."""

    def test_valid_secret_32_hex_chars(self):
        """Test that 32 hex characters is valid."""
        secret = "a" * 32
        assert is_valid_secret(secret) is True

    def test_weak_secret_too_short(self):
        """Test that secrets < 32 chars are rejected."""
        assert is_valid_secret("short") is False
        assert is_valid_secret("1234567890123456789012345678901") is False  # 31 chars

    def test_weak_secret_default_values(self):
        """Test that known weak defaults are rejected."""
        assert is_valid_secret("your-jwt-secret-key-here") is False
        assert is_valid_secret("your-api-key-secret-here") is False
        assert is_valid_secret("dev-secret-change-in-production") is False
        assert is_valid_secret("changeme") is False
        assert is_valid_secret("") is False

    def test_weak_secret_none(self):
        """Test that None is rejected."""
        assert is_valid_secret(None) is False

    def test_valid_secret_openssl_format(self):
        """Test that openssl rand -hex 32 output is valid."""
        # Example: openssl rand -hex 32 produces 64 hex chars (32 bytes)
        secret = "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2"
        assert is_valid_secret(secret) is True

    def test_validate_secrets_missing_required_strict(self):
        """Test that missing required secrets raise error in strict mode."""
        # Save original env
        orig_jwt = os.getenv("JWT_SECRET")
        orig_api = os.getenv("API_KEY_SECRET")

        try:
            os.environ["ENVIRONMENT"] = "production"
            os.environ.pop("JWT_SECRET", None)
            os.environ["API_KEY_SECRET"] = "a" * 32
            os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost/db"
            os.environ["NEO4J_PASSWORD"] = "a" * 32

            with pytest.raises(SecretValidationError, match="Missing required secret"):
                validate_secrets(strict=True)

        finally:
            # Restore
            if orig_jwt:
                os.environ["JWT_SECRET"] = orig_jwt
            else:
                os.environ.pop("JWT_SECRET", None)
            if orig_api:
                os.environ["API_KEY_SECRET"] = orig_api
            else:
                os.environ.pop("API_KEY_SECRET", None)

    def test_validate_secrets_weak_in_production(self):
        """Test that weak secrets raise error in production."""
        orig_jwt = os.getenv("JWT_SECRET")

        try:
            os.environ["ENVIRONMENT"] = "production"
            os.environ["JWT_SECRET"] = "your-jwt-secret-key-here"
            os.environ["API_KEY_SECRET"] = "a" * 32
            os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost/db"
            os.environ["NEO4J_PASSWORD"] = "a" * 32

            with pytest.raises(SecretValidationError, match="Weak or default secret"):
                validate_secrets(strict=True)

        finally:
            if orig_jwt:
                os.environ["JWT_SECRET"] = orig_jwt
            else:
                os.environ.pop("JWT_SECRET", None)

    def test_validate_secrets_sqlite_in_production(self):
        """Test that SQLite in production raises error."""
        orig_db = os.getenv("DATABASE_URL")

        try:
            os.environ["ENVIRONMENT"] = "production"
            os.environ["JWT_SECRET"] = "a" * 32
            os.environ["API_KEY_SECRET"] = "a" * 32
            os.environ["DATABASE_URL"] = "sqlite:///./lexikon.db"
            os.environ["NEO4J_PASSWORD"] = "a" * 32

            with pytest.raises(SecretValidationError, match="SQLite database NOT allowed"):
                validate_secrets(strict=True)

        finally:
            if orig_db:
                os.environ["DATABASE_URL"] = orig_db
            else:
                os.environ.pop("DATABASE_URL", None)

    def test_validate_secrets_all_valid_production(self):
        """Test that all valid secrets pass in production."""
        # Save originals
        orig_env = os.getenv("ENVIRONMENT")
        orig_jwt = os.getenv("JWT_SECRET")
        orig_api = os.getenv("API_KEY_SECRET")
        orig_db = os.getenv("DATABASE_URL")
        orig_neo4j = os.getenv("NEO4J_PASSWORD")

        try:
            os.environ["ENVIRONMENT"] = "production"
            os.environ["JWT_SECRET"] = "a" * 32
            os.environ["API_KEY_SECRET"] = "b" * 32
            os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost/db"
            os.environ["NEO4J_PASSWORD"] = "c" * 32

            # Should not raise
            validate_secrets(strict=True)

        finally:
            # Restore
            if orig_env:
                os.environ["ENVIRONMENT"] = orig_env
            else:
                os.environ.pop("ENVIRONMENT", None)
            if orig_jwt:
                os.environ["JWT_SECRET"] = orig_jwt
            else:
                os.environ.pop("JWT_SECRET", None)
            if orig_api:
                os.environ["API_KEY_SECRET"] = orig_api
            else:
                os.environ.pop("API_KEY_SECRET", None)
            if orig_db:
                os.environ["DATABASE_URL"] = orig_db
            else:
                os.environ.pop("DATABASE_URL", None)
            if orig_neo4j:
                os.environ["NEO4J_PASSWORD"] = orig_neo4j
            else:
                os.environ.pop("NEO4J_PASSWORD", None)

    def test_environment_helpers(self):
        """Test environment detection helpers."""
        orig = os.getenv("ENVIRONMENT")

        try:
            os.environ["ENVIRONMENT"] = "production"
            assert is_production() is True
            assert is_development() is False

            os.environ["ENVIRONMENT"] = "development"
            assert is_production() is False
            assert is_development() is True

        finally:
            if orig:
                os.environ["ENVIRONMENT"] = orig
            else:
                os.environ.pop("ENVIRONMENT", None)
