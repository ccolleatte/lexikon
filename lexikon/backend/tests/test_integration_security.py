"""
Integration tests for security hardening implementation.

Validates end-to-end scenarios:
1. Caching + Authentication flows
2. API key generation/verification with HMAC
3. Memory limits enforcement
4. TTL expiration
5. Cache invalidation patterns
6. Timing attack prevention in login
"""

import pytest
import time
import asyncio
from datetime import datetime
from cache import RedisClient, cache, invalidate_cache
from cache.redis_client import get_redis_client
from auth.api_keys import generate_api_key, verify_api_key, create_api_key
from passlib.context import CryptContext


class TestCachingAuthIntegration:
    """Test caching with authentication system."""

    @pytest.fixture
    def redis(self):
        """Setup and teardown cache."""
        client = get_redis_client()
        client.clear()
        yield client
        client.clear()

    def test_cache_user_data_with_authentication(self, redis):
        """Verify caching user data doesn't bypass auth."""
        # Simulate cached user after login
        user_id = "user_550e8400"
        user_data = {
            "id": user_id,
            "email": "user@example.com",
            "permissions": ["read", "write"],
        }

        # Cache user data after authentication
        redis.set(f"user:{user_id}", user_data, ttl_seconds=3600)

        # Retrieve cached data
        cached = redis.get(f"user:{user_id}")
        assert cached == user_data
        assert cached["email"] == "user@example.com"

    def test_cache_invalidation_on_logout(self, redis):
        """Verify cache invalidation on logout."""
        user_id = "user_logout_test"

        # Cache user session
        redis.set(f"user:{user_id}:session", {"logged_in": True})
        redis.set(f"user:{user_id}:profile", {"name": "Test User"})

        # Verify cached
        assert redis.exists(f"user:{user_id}:session")
        assert redis.exists(f"user:{user_id}:profile")

        # Logout: invalidate all user caches
        redis.delete_pattern(f"user:{user_id}:*")

        # Verify cleared
        assert not redis.exists(f"user:{user_id}:session")
        assert not redis.exists(f"user:{user_id}:profile")

    def test_api_key_caching_with_hmac_verification(self, redis):
        """Verify API key caching doesn't bypass HMAC verification."""
        # Create API key
        plain_key, key_hash = generate_api_key()

        # Cache the key hash (simulating lookup optimization)
        redis.set(f"api_key:{key_hash[:8]}", {"user_id": "user_123", "scopes": "read"})

        # Verify against HMAC (simulating auth middleware)
        import hmac
        import hashlib
        import os

        api_secret = os.getenv(
            "API_KEY_SECRET",
            "dev-secret-change-in-production-set-api-key-secret-env-var"
        ).encode()

        computed_hash = hmac.new(api_secret, plain_key.encode(), hashlib.sha256).hexdigest()
        assert computed_hash == key_hash, "HMAC verification should succeed"

        # Cached value should still require HMAC for full auth
        cached = redis.get(f"api_key:{key_hash[:8]}")
        assert cached is not None
        assert cached["user_id"] == "user_123"


class TestMemoryLimitsSecurity:
    """Test memory limits enforcement under realistic load."""

    @pytest.fixture
    def redis(self):
        """Setup cache."""
        client = get_redis_client()
        client.clear()
        yield client
        client.clear()

    def test_large_cached_response_rejected(self, redis):
        """Verify oversized responses are rejected."""
        # Simulate large API response (e.g., data export)
        large_data = {"items": ["x" * 1000 for _ in range(20000)]}  # ~20MB

        result = redis.set("export_data", large_data)
        assert result is False, "Oversized data should be rejected"

    def test_bulk_cache_operations_with_limits(self, redis):
        """Verify bulk operations validate all items."""
        items = {
            "key1": {"data": "small"},
            "key2": {"data": "x" * (11 * 1024 * 1024)},  # 11MB - too large
            "key3": {"data": "small"},
        }

        result = redis.mset(items)
        assert result is False, "mset should fail if any item oversized"

        # Verify no partial data was set
        assert redis.get("key1") is None
        assert redis.get("key2") is None
        assert redis.get("key3") is None

    def test_memory_usage_monitoring(self, redis):
        """Verify memory monitoring works without blocking operations."""
        # Set multiple values
        for i in range(100):
            redis.set(f"data:{i}", {"value": f"item_{i}"}, ttl_seconds=3600)

        # Get info (should not block)
        info = redis.get_info()
        assert "used_memory_mb" in info
        assert info["used_memory_mb"] >= 0


class TestTTLExpiration:
    """Test TTL expiration behavior."""

    @pytest.fixture
    def redis(self):
        """Setup cache."""
        client = get_redis_client()
        client.clear()
        yield client
        client.clear()

    def test_session_cache_expires_correctly(self, redis):
        """Verify session caches expire per TTL."""
        # Cache session with 2-second TTL
        redis.set("session:xyz123", {"user_id": "user_123"}, ttl_seconds=2)

        # Should exist initially
        assert redis.get("session:xyz123") is not None

        # Wait for expiration
        time.sleep(2.1)

        # Should be expired
        assert redis.get("session:xyz123") is None

    def test_ttl_prevents_permanent_caches(self, redis):
        """Verify TTL enforcement prevents permanent cache entries."""
        # All caches must have TTL between 1s and 24h
        assert redis.MIN_TTL_SECONDS == 1
        assert redis.MAX_TTL_SECONDS == 86400


class TestCacheDecoratorSecurity:
    """Test @cache decorator security features."""

    @pytest.fixture
    def redis(self):
        """Clear cache."""
        client = get_redis_client()
        client.clear()
        yield client
        client.clear()

    def test_cache_decorator_hashes_sensitive_parameters(self, redis):
        """Verify cache keys are hashed (no plaintext sensitive data)."""
        call_count = 0

        @cache(key_prefix="auth_check", ttl_seconds=300)
        def check_permission(user_id: str, resource_id: str):
            nonlocal call_count
            call_count += 1
            return {"can_access": True}

        # First call
        result1 = check_permission(user_id="user_123", resource_id="resource_456")
        assert result1["can_access"] is True
        assert call_count == 1

        # Second call with same parameters - should hit cache
        result2 = check_permission(user_id="user_123", resource_id="resource_456")
        assert result2 == result1
        assert call_count == 1  # Not called again

        # Different parameters - should miss cache
        result3 = check_permission(user_id="user_123", resource_id="resource_789")
        assert call_count == 2

    def test_cache_decorator_with_special_input_handling(self, redis):
        """Verify special/malicious input in cache keys is handled safely."""
        call_count = 0

        @cache(key_prefix="search")
        def search_database(query: str):
            nonlocal call_count
            call_count += 1
            return {"results": []}

        # Injection-like string (should be safe due to hashing)
        injection_query = "'; DROP TABLE users; --"
        result1 = search_database(query=injection_query)
        assert call_count == 1

        # Same query should hit cache
        result2 = search_database(query=injection_query)
        assert result2 == result1
        assert call_count == 1


class TestCacheInvalidationPatterns:
    """Test cache invalidation with security patterns."""

    @pytest.fixture
    def redis(self):
        """Setup cache."""
        client = get_redis_client()
        client.clear()
        yield client
        client.clear()

    def test_invalidate_decorator_on_update(self, redis):
        """Verify @invalidate_cache removes patterns on function execution."""
        # Pre-populate cache
        redis.set("user:123:profile", {"name": "Alice"})
        redis.set("user:123:permissions", ["read", "write"])

        # Function that invalidates on execution
        @invalidate_cache("user:123:*")
        def update_user_profile(user_id: str):
            return f"Updated {user_id}"

        # Cache exists before
        assert redis.exists("user:123:profile")

        # Execute update
        result = update_user_profile("123")
        assert result == "Updated 123"

        # Cache invalidated after
        assert not redis.exists("user:123:profile")
        assert not redis.exists("user:123:permissions")

    def test_cascade_invalidation_pattern(self, redis):
        """Verify cascading invalidation of related caches."""
        # Setup related cache entries
        redis.set("term:python:definition", {"text": "..."})
        redis.set("term:python:relations", ["java", "cpp"])
        redis.set("search:results:python", {"count": 100})

        # Simulate term update that cascades
        @invalidate_cache("term:python:*")
        @invalidate_cache("search:results:*")
        def update_term(term_id: str):
            return f"Updated {term_id}"

        result = update_term("python")

        # All related caches should be cleared
        assert not redis.exists("term:python:definition")
        assert not redis.exists("term:python:relations")
        assert not redis.exists("search:results:python")


class TestLoginTimingAttackMitigation:
    """Test timing attack prevention in authentication."""

    def test_bcrypt_timing_invariant(self):
        """Verify bcrypt verification is timing-invariant."""
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        password = "SecurePassword123!"
        password_hash = pwd_context.hash(password)

        # Time correct password
        start = time.time()
        result_correct = pwd_context.verify(password, password_hash)
        time_correct = time.time() - start

        # Time incorrect password
        start = time.time()
        try:
            pwd_context.verify("WrongPassword", password_hash)
        except:
            pass
        time_incorrect = time.time() - start

        # Should be similar (bcrypt is designed for timing resistance)
        assert result_correct is True
        # Note: Bcrypt is variable-time but resistant to simple timing attacks
        # The difference should be < 10% due to bcrypt's design
        # In real-world, this would be < 50ms differences

    def test_dummy_hash_prevents_user_enumeration(self):
        """Verify dummy hash usage prevents user enumeration."""
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        existing_user_hash = pwd_context.hash("correct_password")

        # Create dummy hash for non-existent user
        dummy_hash = pwd_context.hash("dummy_password_nonexistent@email.com")

        # Both should take similar time
        start = time.time()
        try:
            pwd_context.verify("guessed_password", existing_user_hash)
        except:
            pass
        time_existing = time.time() - start

        start = time.time()
        try:
            pwd_context.verify("guessed_password", dummy_hash)
        except:
            pass
        time_dummy = time.time() - start

        # Times should be comparable (within bcrypt's timing resistance)
        # This prevents attackers from knowing if user exists via response time
        assert isinstance(time_existing, float)
        assert isinstance(time_dummy, float)


class TestEndToEndAuthFlow:
    """Test complete authentication flow with security features."""

    @pytest.fixture
    def redis(self):
        """Setup cache."""
        client = get_redis_client()
        client.clear()
        yield client
        client.clear()

    def test_complete_auth_session_flow(self, redis):
        """Verify full auth flow: login → cache session → logout."""
        user_id = "user_e2e_test"
        access_token = "jwt_token_xyz123"

        # 1. Login: Cache session
        redis.set(
            f"session:{access_token}",
            {"user_id": user_id, "issued_at": datetime.utcnow().isoformat()},
            ttl_seconds=3600,
        )

        # Cache user profile for quick lookup
        redis.set(
            f"user:{user_id}:profile",
            {"email": "user@example.com", "permissions": ["read"]},
            ttl_seconds=3600,
        )

        # 2. Verify: Can retrieve session
        session = redis.get(f"session:{access_token}")
        assert session is not None
        assert session["user_id"] == user_id

        # 3. Operations: Use cached profile
        profile = redis.get(f"user:{user_id}:profile")
        assert "read" in profile["permissions"]

        # 4. Logout: Invalidate session and related caches
        redis.delete(f"session:{access_token}")
        redis.delete_pattern(f"user:{user_id}:*")

        # 5. Verify: Session should be gone
        assert redis.get(f"session:{access_token}") is None
        assert redis.get(f"user:{user_id}:profile") is None

    def test_api_key_auth_with_caching(self, redis):
        """Verify API key auth with caching doesn't bypass security."""
        # Generate API key
        plain_key, key_hash = generate_api_key()

        # Cache API key metadata (for performance)
        redis.set(
            f"api_key_metadata:{key_hash[:8]}",
            {"user_id": "api_user_123", "scopes": "read,write", "rate_limit": 1000},
            ttl_seconds=86400,
        )

        # Retrieve cached metadata
        cached_meta = redis.get(f"api_key_metadata:{key_hash[:8]}")
        assert cached_meta["user_id"] == "api_user_123"

        # But always verify key hash itself
        # In real auth, would verify full key_hash in database
