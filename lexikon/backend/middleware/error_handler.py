"""
Centralized error handling middleware for FastAPI.

Provides:
- Standardized JSON error responses
- Error classification (validation, authentication, authorization, business logic, server)
- Structured logging with context
- Security (doesn't leak sensitive information to clients)
- HTTP status code mapping
"""

import logging
import traceback
from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

logger = logging.getLogger(__name__)


class AppException(Exception):
    """
    Base application exception with structured error information.

    All application-specific errors should inherit from this class.
    """

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None,
    ):
        """
        Initialize application exception.

        Args:
            code: Machine-readable error code (e.g., "INVALID_EMAIL")
            message: Internal error message (logged)
            status_code: HTTP status code (default 500)
            details: Additional error details (not sent to user unless safe)
            user_message: User-friendly message (optional, uses message if not provided)
        """
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        self.user_message = user_message or message
        super().__init__(self.message)


class ValidationException(AppException):
    """Exception for invalid request data."""

    def __init__(
        self,
        message: str,
        code: str = "VALIDATION_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class AuthenticationException(AppException):
    """Exception for authentication failures."""

    def __init__(
        self,
        message: str = "Authentication required",
        code: str = "UNAUTHORIZED",
    ):
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class AuthorizationException(AppException):
    """Exception for authorization failures."""

    def __init__(
        self,
        message: str = "Insufficient permissions",
        code: str = "FORBIDDEN",
    ):
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class NotFoundException(AppException):
    """Exception for resource not found."""

    def __init__(
        self,
        resource: str,
        code: str = "NOT_FOUND",
    ):
        message = f"{resource} not found"
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            user_message=message,
        )


class ConflictException(AppException):
    """Exception for resource conflicts (e.g., duplicate)."""

    def __init__(
        self,
        message: str,
        code: str = "CONFLICT",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            details=details,
        )


class RateLimitException(AppException):
    """Exception for rate limit exceeded."""

    def __init__(self):
        super().__init__(
            code="RATE_LIMIT_EXCEEDED",
            message="Too many requests",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            user_message="Too many requests. Please try again later.",
        )


class ServerException(AppException):
    """Exception for server errors."""

    def __init__(
        self,
        message: str = "Internal server error",
        code: str = "INTERNAL_ERROR",
    ):
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            user_message="An unexpected error occurred. Please try again later.",
        )


def format_error_response(
    code: str,
    message: str,
    status_code: int,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Format standardized error response.

    Returns:
        Dict with error information in consistent format
    """
    response = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
        }
    }

    if details and len(details) > 0:
        response["error"]["details"] = details

    if request_id:
        response["error"]["request_id"] = request_id

    response["error"]["timestamp"] = datetime.utcnow().isoformat()

    return response


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle application exceptions."""

    # Log the error
    logger.warning(
        f"Application exception: {exc.code}",
        extra={
            "error_code": exc.code,
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method,
            "message": exc.message,
        }
    )

    # Format response
    error_response = format_error_response(
        code=exc.code,
        message=exc.user_message,
        status_code=exc.status_code,
        details=exc.details,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response,
    )


async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle Pydantic validation errors."""

    # Extract field-level errors
    errors = {}
    for error in exc.errors():
        field = ".".join(str(x) for x in error["loc"][1:])  # Skip request class name
        errors[field] = error["msg"]

    logger.warning(
        "Validation error",
        extra={
            "path": request.url.path,
            "method": request.method,
            "validation_errors": errors,
        }
    )

    error_response = format_error_response(
        code="VALIDATION_ERROR",
        message="Request validation failed",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        details={"fields": errors},
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response,
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected server errors."""

    # Log full traceback for debugging
    logger.error(
        f"Unhandled exception: {type(exc).__name__}",
        exc_info=True,
        extra={
            "path": request.url.path,
            "method": request.method,
            "exception_type": type(exc).__name__,
        }
    )

    # Don't expose internal error details to client
    error_response = format_error_response(
        code="INTERNAL_ERROR",
        message="An unexpected error occurred. Please try again later.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response,
    )


def setup_error_handlers(app) -> None:
    """
    Register error handlers with FastAPI app.

    Must be called after app initialization but before adding routes.
    """
    from fastapi.exceptions import RequestValidationError

    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
