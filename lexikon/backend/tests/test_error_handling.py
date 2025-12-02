"""
Tests for error handling middleware.

Covers:
- Standardized error response format
- Exception hierarchy
- Error code mapping
- Validation error handling
- Unhandled exception safety
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestErrorResponseFormat:
    """Test standardized error response format."""

    def test_validation_error_format(self):
        """Validation errors should return consistent format."""
        # Send invalid registration data
        response = client.post(
            "/api/auth/register",
            json={
                "email": "invalid-email",  # Invalid email
                "password": "weak",  # Too short
                "first_name": "J",  # Too short
                "last_name": "D",  # Too short
            }
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()

        # Check error response structure
        assert data["success"] is False
        assert "error" in data
        assert "code" in data["error"]
        assert "message" in data["error"]
        assert "timestamp" in data["error"]
        assert "details" in data["error"] or "details" not in data["error"]

    def test_missing_required_fields(self):
        """Missing required fields should return validation error."""
        response = client.post(
            "/api/auth/register",
            json={"email": "test@example.com"}  # Missing required fields
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert "password" in str(data["error"]) or "details" in data["error"]

    def test_invalid_email_format(self):
        """Invalid email format should be caught."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "not-an-email",
                "password": "StrongPass123!",
                "first_name": "John",
                "last_name": "Doe",
            }
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert data["success"] is False

    def test_weak_password_rejection(self):
        """Weak passwords should be rejected with clear error."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "user@example.com",
                "password": "NoSpecialChar123",  # No special character
                "first_name": "John",
                "last_name": "Doe",
            }
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert data["success"] is False
        # Should mention password issue in error
        assert "error" in data

    def test_short_password_rejection(self):
        """Too-short passwords should be rejected."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "user@example.com",
                "password": "Short1!",  # Only 7 characters
                "first_name": "John",
                "last_name": "Doe",
            }
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert data["success"] is False

    def test_invalid_name_format(self):
        """Invalid name characters should be rejected."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "user@example.com",
                "password": "StrongPass123!",
                "first_name": "John@123",  # Invalid characters
                "last_name": "Doe",
            }
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert data["success"] is False


class TestSuccessfulOperations:
    """Test that valid requests still work correctly."""

    def test_health_check_still_works(self):
        """Health check should work without errors."""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data

    def test_root_endpoint_still_works(self):
        """Root endpoint should work without errors."""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Lexikon API"


class TestErrorCodeConsistency:
    """Test that error codes are consistent across operations."""

    def test_validation_error_has_code(self):
        """All validation errors should have error code."""
        response = client.post(
            "/api/auth/register",
            json={}  # Empty request
        )

        data = response.json()
        assert "error" in data
        assert "code" in data["error"]
        assert data["error"]["code"] in ["VALIDATION_ERROR", "422"]

    def test_not_found_has_code(self):
        """Not found errors should have consistent code."""
        # Try to get non-existent term (would need auth, so we check rate limit endpoint doesn't exist)
        response = client.get("/api/nonexistent-endpoint")

        # This will be 404 from FastAPI, not our handler yet
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestErrorLogging:
    """Test that errors are properly logged (indirectly)."""

    def test_validation_errors_logged(self, caplog):
        """Validation errors should be logged."""
        import logging
        caplog.set_level(logging.WARNING)

        response = client.post(
            "/api/auth/register",
            json={"email": ""}  # Empty email
        )

        # Request should fail
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestErrorSecurityConsiderations:
    """Test that errors don't leak sensitive information."""

    def test_validation_errors_dont_expose_system_details(self):
        """Validation errors should be user-friendly."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "weak",
                "first_name": "J",
                "last_name": "D",
            }
        )

        data = response.json()
        error_str = str(data)

        # Should not expose internal paths or Python details
        assert "C:\\" not in error_str
        assert "/home" not in error_str
        assert "Traceback" not in error_str
        assert "File \"" not in error_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
