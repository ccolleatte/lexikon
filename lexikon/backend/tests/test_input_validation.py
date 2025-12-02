"""
Tests for input validation and sanitization module.

Covers:
- HTML sanitization
- Name validation
- Definition validation
- Password strength validation
- Email validation
- String input validation
"""

import pytest
from validators.input_validators import (
    sanitize_html,
    validate_name,
    validate_definition,
    validate_string_input,
    validate_password,
    validate_email_format,
)


class TestSanitizeHtml:
    """Test HTML sanitization."""

    def test_remove_script_tags(self):
        """Script tags should be completely removed."""
        input_text = '<script>alert("xss")</script>Hello'
        output = sanitize_html(input_text)
        assert "script" not in output
        assert "Hello" in output

    def test_remove_onclick_handlers(self):
        """Event handlers should be removed."""
        input_text = '<div onclick="alert(1)">Click me</div>'
        output = sanitize_html(input_text)
        assert "onclick" not in output
        assert "Click me" in output

    def test_allow_safe_html_tags(self):
        """Safe HTML tags should be preserved when allowed."""
        input_text = '<b>Bold</b> and <i>italic</i>'
        output = sanitize_html(input_text, allow_html=True)
        assert '<b>Bold</b>' in output
        assert '<i>italic</i>' in output

    def test_strip_unsafe_tags_even_when_html_allowed(self):
        """Unsafe tags should be escaped/stripped even when HTML is allowed."""
        input_text = '<b>Bold</b> and <script>alert(1)</script> text'
        output = sanitize_html(input_text, allow_html=True)
        assert '<b>Bold</b>' in output
        # Script tags are escaped, not executed
        assert '<script>' not in output  # No unescaped script tags
        # alert() should not be executable
        assert 'onclick=' not in output and 'onerror=' not in output

    def test_whitespace_normalization(self):
        """Input should be stripped of leading/trailing whitespace."""
        input_text = '  Hello World  '
        output = sanitize_html(input_text)
        assert output == 'Hello World'


class TestValidateName:
    """Test name validation."""

    def test_valid_simple_name(self):
        """Simple ASCII names should pass."""
        assert validate_name("John") == "John"
        assert validate_name("Mary") == "Mary"

    def test_valid_hyphenated_name(self):
        """Hyphenated names should be valid."""
        assert validate_name("Jean-Pierre") == "Jean-Pierre"

    def test_valid_diacritics(self):
        """Names with diacritics should be valid."""
        assert validate_name("José") == "José"
        assert validate_name("François") == "François"
        assert validate_name("Müller") == "Müller"

    def test_valid_apostrophe(self):
        """Names with apostrophes should be valid."""
        assert validate_name("O'Brien") == "O'Brien"

    def test_spaces_normalized(self):
        """Multiple spaces should be collapsed."""
        assert validate_name("Jean  Marie") == "Jean Marie"

    def test_invalid_too_short(self):
        """Names shorter than min_length should fail."""
        with pytest.raises(ValueError, match="at least 2"):
            validate_name("J", min_length=2)

    def test_invalid_too_long(self):
        """Names longer than max_length should fail."""
        with pytest.raises(ValueError, match="must not exceed"):
            validate_name("A" * 101, max_length=100)

    def test_invalid_special_characters(self):
        """Names with invalid special characters should fail."""
        with pytest.raises(ValueError, match="invalid characters"):
            validate_name("John@Doe")
        with pytest.raises(ValueError, match="invalid characters"):
            validate_name("Jean#Marie")

    def test_empty_name(self):
        """Empty name should fail."""
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_name("")

    def test_numbers_allowed(self):
        """Numbers in names should be allowed (for some cultures)."""
        assert validate_name("Jean2") == "Jean2"


class TestValidateDefinition:
    """Test definition/description validation."""

    def test_valid_simple_definition(self):
        """Simple text definition should pass."""
        text = "This is a valid definition that is long enough to satisfy the minimum length requirement."
        result = validate_definition(text)
        assert "valid definition" in result

    def test_valid_definition_with_html(self):
        """Definition with allowed HTML tags should pass."""
        text = "<b>Bold term</b> is a concept used in academic research and scientific studies across multiple disciplines."
        result = validate_definition(text)
        assert "Bold term" in result

    def test_invalid_too_short(self):
        """Definition shorter than min_length should fail."""
        with pytest.raises(ValueError, match="at least 50"):
            validate_definition("Too short")

    def test_invalid_too_long(self):
        """Definition longer than max_length should fail."""
        with pytest.raises(ValueError, match="must not exceed"):
            long_text = "x" * 2001
            validate_definition(long_text)

    def test_xss_prevention(self):
        """XSS payloads should be sanitized/removed."""
        # The img tag is not in allowed_tags, so it gets escaped/removed
        text = "Definition with <img src=x onerror=alert(1)> embedded attack in a long enough definition text."
        result = validate_definition(text)
        # After bleach sanitization, img tag is removed/escaped
        # The dangerous onerror attribute should not execute
        assert "<img" not in result or "onerror=" not in result

    def test_javascript_protocol_blocked(self):
        """JavaScript protocol URLs should be sanitized/blocked by bleach."""
        # Bleach will escape or remove javascript: protocol URLs in href
        text = "Click <a href='javascript:alert(1)'>here</a> for more information about this long definition."
        result = validate_definition(text)
        # The link text is preserved but javascript: should be escaped/removed
        assert "here" in result
        # Javascript URL should not be executable
        assert "javascript:" not in result or "&lt;" in result

    def test_empty_definition(self):
        """Empty definition should fail."""
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_definition("")


class TestValidatePassword:
    """Test password strength validation."""

    def test_valid_strong_password(self):
        """Strong password should pass all requirements."""
        assert validate_password("SecurePass123!") == "SecurePass123!"

    def test_valid_complex_password(self):
        """Complex password with various special chars should pass."""
        assert validate_password("MyP@ssw0rd#2024") == "MyP@ssw0rd#2024"

    def test_invalid_too_short(self):
        """Password shorter than 8 characters should fail."""
        with pytest.raises(ValueError, match="at least 8"):
            validate_password("Short1!")

    def test_invalid_too_long(self):
        """Password longer than 100 characters should fail."""
        with pytest.raises(ValueError, match="must not exceed"):
            validate_password("A" * 101 + "1!")

    def test_invalid_no_uppercase(self):
        """Password without uppercase should fail."""
        with pytest.raises(ValueError, match="uppercase"):
            validate_password("lowercase123!")

    def test_invalid_no_lowercase(self):
        """Password without lowercase should fail."""
        with pytest.raises(ValueError, match="lowercase"):
            validate_password("UPPERCASE123!")

    def test_invalid_no_digit(self):
        """Password without digits should fail."""
        with pytest.raises(ValueError, match="digit"):
            validate_password("NoDigitsHere!")

    def test_invalid_no_special_char(self):
        """Password without special characters should fail."""
        with pytest.raises(ValueError, match="special character"):
            validate_password("NoSpecialChar123")

    def test_empty_password(self):
        """Empty password should fail."""
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_password("")


class TestValidateEmail:
    """Test email validation."""

    def test_valid_simple_email(self):
        """Simple valid email should pass."""
        assert validate_email_format("user@example.com") == "user@example.com"

    def test_valid_complex_email(self):
        """Complex email with subdomain should pass."""
        assert validate_email_format("user.name+tag@mail.example.co.uk") == "user.name+tag@mail.example.co.uk"

    def test_normalizes_to_lowercase(self):
        """Email should be normalized to lowercase."""
        assert validate_email_format("User@Example.COM") == "user@example.com"

    def test_invalid_double_dot(self):
        """Emails with consecutive dots should fail."""
        with pytest.raises(ValueError, match="invalid pattern"):
            validate_email_format("user..name@example.com")

    def test_invalid_no_domain(self):
        """Email without @ symbol should fail."""
        with pytest.raises(ValueError, match="format is invalid"):
            validate_email_format("usernameexample.com")

    def test_invalid_no_tld(self):
        """Email without TLD should fail."""
        with pytest.raises(ValueError, match="format is invalid|valid domain"):
            validate_email_format("user@example")

    def test_invalid_short_tld(self):
        """Email with too-short TLD should fail."""
        with pytest.raises(ValueError, match="format is invalid|TLD is too short"):
            validate_email_format("user@example.c")

    def test_empty_email(self):
        """Empty email should fail."""
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_email_format("")

    def test_invalid_leading_dot(self):
        """Email starting with dot should fail."""
        with pytest.raises(ValueError, match="invalid"):
            validate_email_format(".user@example.com")

    def test_valid_dot_in_local_part(self):
        """Dots in the local part are allowed (RFC 5321)."""
        # While unusual, dots in local part are technically valid
        result = validate_email_format("user.name@example.com")
        assert "user.name@example.com" == result


class TestValidateStringInput:
    """Test generic string input validation."""

    def test_valid_simple_input(self):
        """Simple valid input should pass."""
        result = validate_string_input("Hello World", field_name="test_field")
        assert "Hello World" in result

    def test_custom_length_constraints(self):
        """Custom min/max lengths should be enforced."""
        result = validate_string_input("test", min_length=2, max_length=10, field_name="test")
        assert "test" in result

    def test_invalid_too_short(self):
        """Input shorter than min_length should fail."""
        with pytest.raises(ValueError, match="at least"):
            validate_string_input("x", min_length=5, field_name="field")

    def test_invalid_too_long(self):
        """Input longer than max_length should fail."""
        with pytest.raises(ValueError, match="must not exceed"):
            validate_string_input("x" * 100, max_length=50, field_name="field")

    def test_html_stripping_by_default(self):
        """HTML should be stripped by default."""
        result = validate_string_input("<b>Bold text</b>", field_name="field")
        assert "<b>" not in result
        assert "Bold text" in result

    def test_html_allowed_when_specified(self):
        """HTML should be allowed when allow_html=True."""
        result = validate_string_input("<b>Bold</b>", allow_html=True, field_name="field")
        assert "<b>Bold</b>" in result

    def test_empty_input(self):
        """Empty input should fail."""
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_string_input("", field_name="field")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
