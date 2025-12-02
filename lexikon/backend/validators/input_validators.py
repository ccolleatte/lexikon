"""
Input validation and sanitization utilities.

Provides functions to validate and sanitize user input for:
- Names (alphanumeric + diacritics + hyphens/spaces)
- Definitions (text with allowed HTML)
- Passwords (complexity requirements)
- General string input (XSS prevention)
- Email format validation
"""

import re
import bleach
from typing import Optional


# Allowed HTML tags for rich text fields (definitions, descriptions)
ALLOWED_TAGS = ['b', 'i', 'em', 'strong', 'p', 'br', 'ul', 'ol', 'li', 'a']
ALLOWED_ATTRIBUTES = {'a': ['href', 'title']}


def sanitize_html(text: str, allow_html: bool = False) -> str:
    """
    Sanitize HTML input to prevent XSS attacks.

    Args:
        text: Input text to sanitize
        allow_html: If True, allow specified HTML tags. If False, strip all HTML.

    Returns:
        Sanitized text

    Examples:
        >>> sanitize_html('<script>alert("xss")</script>Hello')
        'Hello'
        >>> sanitize_html('<b>Bold</b> text', allow_html=True)
        '<b>Bold</b> text'
    """
    if not text:
        return text

    text = text.strip()

    if allow_html:
        # Allow only safe HTML tags
        return bleach.clean(
            text,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            strip=False
        )
    else:
        # Strip all HTML tags
        return bleach.clean(text, tags=[], strip=True)


def validate_name(value: str, min_length: int = 2, max_length: int = 100) -> str:
    """
    Validate and normalize a name field.

    Allows:
    - Letters (a-z, A-Z, diacritics À-ÿ)
    - Numbers (0-9)
    - Hyphens and spaces
    - Apostrophes (for names like O'Brien)

    Args:
        value: Name to validate
        min_length: Minimum length (default 2)
        max_length: Maximum length (default 100)

    Returns:
        Normalized name

    Raises:
        ValueError: If name is invalid

    Examples:
        >>> validate_name('Jean-Pierre')
        'Jean-Pierre'
        >>> validate_name('José María')
        'José María'
    """
    if not value:
        raise ValueError("Name cannot be empty")

    # Strip whitespace
    value = value.strip()

    # Check length
    if len(value) < min_length:
        raise ValueError(f"Name must be at least {min_length} characters")
    if len(value) > max_length:
        raise ValueError(f"Name must not exceed {max_length} characters")

    # Validate characters (letters, numbers, hyphens, spaces, apostrophes)
    if not re.match(r"^[a-zA-ZÀ-ÿ0-9\s\-']+$", value):
        raise ValueError("Name contains invalid characters. Use letters, numbers, hyphens, spaces, and apostrophes only")

    # Normalize whitespace (collapse multiple spaces)
    value = re.sub(r'\s+', ' ', value)

    # Prevent leading/trailing spaces or hyphens
    value = value.strip()
    value = value.strip('-')

    return value


def validate_definition(value: str, min_length: int = 50, max_length: int = 2000) -> str:
    """
    Validate and sanitize a definition/description field.

    Allows:
    - Basic text
    - Limited HTML formatting (bold, italic, lists, links)
    - Line breaks

    Args:
        value: Definition text to validate
        min_length: Minimum length (default 50)
        max_length: Maximum length (default 2000)

    Returns:
        Sanitized definition

    Raises:
        ValueError: If definition is invalid
    """
    if not value:
        raise ValueError("Definition cannot be empty")

    value = value.strip()

    # Check length before sanitization
    if len(value) < min_length:
        raise ValueError(f"Definition must be at least {min_length} characters")
    if len(value) > max_length:
        raise ValueError(f"Definition must not exceed {max_length} characters")

    # Sanitize HTML (allow safe tags)
    # Bleach removes dangerous tags and escapes unsafe attributes
    value = sanitize_html(value, allow_html=True)

    return value


def validate_string_input(
    value: str,
    min_length: int = 1,
    max_length: int = 500,
    allow_html: bool = False,
    field_name: str = "field"
) -> str:
    """
    Generic string input validator with optional HTML sanitization.

    Args:
        value: Input string to validate
        min_length: Minimum length
        max_length: Maximum length
        allow_html: Whether to allow safe HTML tags
        field_name: Field name for error messages

    Returns:
        Validated and sanitized string

    Raises:
        ValueError: If input is invalid
    """
    if not value:
        raise ValueError(f"{field_name} cannot be empty")

    value = value.strip()

    if len(value) < min_length:
        raise ValueError(f"{field_name} must be at least {min_length} characters")
    if len(value) > max_length:
        raise ValueError(f"{field_name} must not exceed {max_length} characters")

    # Sanitize HTML
    value = sanitize_html(value, allow_html=allow_html)

    return value


def validate_password(value: str) -> str:
    """
    Validate password strength.

    Requirements:
    - Minimum 8 characters
    - Maximum 100 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character

    Args:
        value: Password to validate

    Returns:
        Password (unchanged if valid)

    Raises:
        ValueError: If password doesn't meet requirements
    """
    if not value:
        raise ValueError("Password cannot be empty")

    if len(value) < 8:
        raise ValueError("Password must be at least 8 characters")
    if len(value) > 100:
        raise ValueError("Password must not exceed 100 characters")

    if not re.search(r'[A-Z]', value):
        raise ValueError("Password must contain at least one uppercase letter")

    if not re.search(r'[a-z]', value):
        raise ValueError("Password must contain at least one lowercase letter")

    if not re.search(r'\d', value):
        raise ValueError("Password must contain at least one digit")

    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/]', value):
        raise ValueError("Password must contain at least one special character")

    return value


def validate_email_format(value: str) -> str:
    """
    Validate email format (complements Pydantic's EmailStr).

    Also checks for:
    - Suspicious patterns (e.g., multiple consecutive dots)
    - Invalid TLD

    Args:
        value: Email to validate

    Returns:
        Email (normalized to lowercase)

    Raises:
        ValueError: If email is invalid
    """
    if not value:
        raise ValueError("Email cannot be empty")

    value = value.strip().lower()

    # Check for suspicious patterns
    if '..' in value:
        raise ValueError("Email contains invalid pattern")

    if value.startswith('.') or value.endswith('.'):
        raise ValueError("Email is invalid")

    # Basic email pattern validation
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
        raise ValueError("Email format is invalid")

    # Check domain has valid TLD (at least 2 characters)
    domain_part = value.split('@')[1]
    if '.' not in domain_part:
        raise ValueError("Email must have valid domain")

    tld = domain_part.split('.')[-1]
    if len(tld) < 2:
        raise ValueError("Email TLD is too short")

    return value
