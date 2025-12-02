"""Configuration module for Lexikon application."""
from .secrets_validator import validate_secrets, SecretValidationError

__all__ = ["validate_secrets", "SecretValidationError"]
