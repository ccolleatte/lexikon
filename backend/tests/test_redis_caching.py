"""
Tests for Redis caching layer.
Verifies cache operations, serialization, and invalidation patterns.
"""

import pytest
import time
from cache import RedisClient, cache, invalidate_cache
from cache.redis_client import get_redis_client


class TestRedisClient:
    """Test RedisClient basic operations."""

    @pytest.fixture
    def redis(self):
        """Create test Redis client."""
        client = RedisClient(
            host="localhost",
            port=6379,
            prefix="test:",
            default_ttl_seconds=3600,
        )
        # Clean before test
        client.clear()
        yield client
        # Clean after test
        client.clear()

    def test_set_and_get_string(self, redis):
        """Test storing and retrieving string values."""
        redis.set("key1", "value1")
        assert redis.get("key1") == "value1"

    def test_set_and_get_dict(self, redis):
        """Test storing and retrieving dict values."""
        data = {"name": "John", "age": 30}
        redis.set("user:123", data)
        assert redis.get("user:123") == data

    def test_set_and_get_list(self, redis):
        """Test storing and retrieving list values."""
        items = ["term1", "term2", "term3"]
        redis.set("terms:search", items)
        assert redis.get("terms:search") == items

    def test_set_with_ttl(self, redis):
        """Test that TTL causes key expiration."""
        redis.set("temp_key", "temp_value", ttl_seconds=1)
        assert redis.get("temp_key") == "temp_value"

        # Wait for expiration
        time.sleep(1.1)
        assert redis.get("temp_key") is None

    def test_delete_key(self, redis):
        """Test deleting a key."""
        redis.set("key1", "value1")
        assert redis.exists("key1") is True

        redis.delete("key1")
        assert redis.exists("key1") is False

    def test_delete_nonexistent_key(self, redis):
        """Test deleting non-existent key."""
        result = redis.delete("nonexistent")
        assert result is False

    def test_delete_pattern(self, redis):
        """Test deleting keys by pattern."""
        redis.set("user:1:profile", {"id": 1})
        redis.set("user:1:settings", {"theme": "dark"})
        redis.set("user:2:profile", {"id": 2})

        # Delete all user:1 cache
        deleted = redis.delete_pattern("user:1:*")
        assert deleted == 2

        assert redis.exists("user:1:profile") is False
        assert redis.exists("user:1:settings") is False
        assert redis.exists("user:2:profile") is True

    def test_exists(self, redis):
        """Test checking if key exists."""
        redis.set("existing_key", "value")

        assert redis.exists("existing_key") is True
        assert redis.exists("nonexistent") is False

    def test_mget_multiple_keys(self, redis):
        """Test getting multiple values at once."""
        redis.set("key1", "value1")
        redis.set("key2", "value2")
        redis.set("key3", "value3")

        result = redis.mget(["key1", "key2", "key3", "nonexistent"])

        assert result["key1"] == "value1"
        assert result["key2"] == "value2"
        assert result["key3"] == "value3"
        assert result["nonexistent"] is None

    def test_mset_multiple_values(self, redis):
        """Test setting multiple values at once."""
        items = {
            "key1": "value1",
            "key2": {"nested": "dict"},
            "key3": [1, 2, 3],
        }
        redis.mset(items)

        assert redis.get("key1") == "value1"
        assert redis.get("key2") == {"nested": "dict"}
        assert redis.get("key3") == [1, 2, 3]

    def test_get_or_set_cache_hit(self, redis):
        """Test get_or_set returns cached value."""
        redis.set("computed", "cached_result")

        # compute_fn should not be called
        compute_count = 0

        def compute():
            nonlocal compute_count
            compute_count += 1
            return "fresh_result"

        result = redis.get_or_set("computed", compute)

        assert result == "cached_result"
        assert compute_count == 0

    def test_get_or_set_cache_miss(self, redis):
        """Test get_or_set computes and caches."""
        compute_count = 0

        def compute():
            nonlocal compute_count
            compute_count += 1
            return {"id": 123, "name": "Test"}

        result = redis.get_or_set("new_key", compute, ttl_seconds=3600)

        assert result == {"id": 123, "name": "Test"}
        assert compute_count == 1

        # Second call should hit cache
        result2 = redis.get_or_set("new_key", compute)
        assert result2 == {"id": 123, "name": "Test"}
        assert compute_count == 1  # Not called again

    def test_increment_counter(self, redis):
        """Test incrementing numeric values."""
        redis.set("counter", 10)
        result = redis.increment("counter", 5)
        assert result == 15

        result = redis.increment("counter", 1)
        assert result == 16

    def test_clear_all_cache(self, redis):
        """Test clearing all cached entries."""
        redis.set("key1", "value1")
        redis.set("key2", "value2")
        redis.set("key3", "value3")

        deleted = redis.clear()
        assert deleted == 3

        assert redis.get("key1") is None
        assert redis.get("key2") is None
        assert redis.get("key3") is None

    def test_health_check(self, redis):
        """Test health check."""
        is_healthy = redis.health_check()
        assert is_healthy is True

    def test_get_info(self, redis):
        """Test getting Redis server info."""
        info = redis.get_info()

        assert "used_memory_mb" in info
        assert "connected_clients" in info
        assert "total_commands_processed" in info
        assert info["used_memory_mb"] > 0


class TestSerialization:
    """Test serialization/deserialization of various types."""

    @pytest.fixture
    def redis(self):
        """Create test Redis client."""
        client = RedisClient(host="localhost", port=6379, prefix="test:")
        client.clear()
        yield client
        client.clear()

    def test_serialize_json_compatible_types(self, redis):
        """Test JSON serialization for standard types."""
        values = [
            ("string", "test_string"),
            ("integer", 42),
            ("float", 3.14),
            ("bool", True),
            ("null", None),
            ("list", [1, 2, 3]),
            ("dict", {"key": "value", "nested": {"inner": "data"}}),
        ]

        for key, value in values:
            redis.set(key, value)
            retrieved = redis.get(key)
            assert retrieved == value, f"Failed for {key}: {value}"

    def test_serialize_complex_nested_structure(self, redis):
        """Test serialization of complex nested structures."""
        complex_data = {
            "users": [
                {"id": 1, "name": "Alice", "tags": ["admin", "user"]},
                {"id": 2, "name": "Bob", "tags": ["user"]},
            ],
            "metadata": {
                "total": 2,
                "timestamp": "2025-11-20T12:00:00Z",
                "flags": {"verified": True, "active": True},
            },
        }

        redis.set("complex", complex_data)
        retrieved = redis.get("complex")
        assert retrieved == complex_data

    def test_serialize_user_object_with_datetime(self, redis):
        """Test serialization of object-like structures."""
        from datetime import datetime

        # Simulate a user object (as dict since we can't use actual objects)
        user_dict = {
            "id": "550e8400",
            "email": "user@example.com",
            "created_at": datetime(2025, 11, 20, 12, 0, 0).isoformat(),
            "attributes": {"verified": True, "tier": "premium"},
        }

        redis.set("user:550e8400", user_dict)
        retrieved = redis.get("user:550e8400")
        assert retrieved == user_dict


class TestCacheDecorator:
    """Test @cache decorator functionality."""

    @pytest.fixture
    def redis(self):
        """Clear cache before each test."""
        client = get_redis_client()
        client.clear()
        yield client
        client.clear()

    def test_cache_decorator_caches_result(self, redis):
        """Test that @cache decorator caches function results."""
        call_count = 0

        @cache(key_prefix="test_func", ttl_seconds=3600)
        def expensive_function(user_id: str):
            nonlocal call_count
            call_count += 1
            return {"id": user_id, "name": f"User {user_id}"}

        # First call - executes function
        result1 = expensive_function("123")
        assert result1 == {"id": "123", "name": "User 123"}
        assert call_count == 1

        # Second call - uses cache
        result2 = expensive_function("123")
        assert result2 == {"id": "123", "name": "User 123"}
        assert call_count == 1  # Not called again

    def test_cache_decorator_with_different_arguments(self, redis):
        """Test that different arguments create different cache entries."""
        call_count = 0

        @cache(key_prefix="user_data")
        def get_user_data(user_id: str):
            nonlocal call_count
            call_count += 1
            return {"id": user_id}

        # Different user IDs should create different cache entries
        result1 = get_user_data("user1")
        assert result1 == {"id": "user1"}
        assert call_count == 1

        result2 = get_user_data("user2")
        assert result2 == {"id": "user2"}
        assert call_count == 2

    def test_cache_decorator_with_custom_key_builder(self, redis):
        """Test @cache with custom key builder."""
        call_count = 0

        @cache(
            key_prefix="search",
            key_builder=lambda kwargs: f"{kwargs['query']}:{kwargs['user_id']}"
        )
        def search_terms(query: str, user_id: str):
            nonlocal call_count
            call_count += 1
            return {"results": [query, user_id]}

        result1 = search_terms(query="python", user_id="user123")
        assert call_count == 1

        # Same query and user - cache hit
        result2 = search_terms(query="python", user_id="user123")
        assert call_count == 1

        # Different query - cache miss
        result3 = search_terms(query="javascript", user_id="user123")
        assert call_count == 2


class TestInvalidationDecorator:
    """Test @invalidate_cache decorator."""

    @pytest.fixture
    def redis(self):
        """Clear cache before each test."""
        client = get_redis_client()
        client.clear()
        yield client
        client.clear()

    def test_invalidate_cache_removes_pattern(self, redis):
        """Test that @invalidate_cache removes matching patterns."""
        # Pre-populate cache
        redis.set("user:123:profile", {"id": 123})
        redis.set("user:123:settings", {"theme": "dark"})

        # Function that invalidates on execution
        @invalidate_cache("user:123:*")
        def update_user(user_id: str):
            return f"Updated user {user_id}"

        # Before invalidation, keys exist
        assert redis.exists("user:123:profile") is True

        # Execute function
        update_user("123")

        # After function execution, cache is invalidated
        assert redis.exists("user:123:profile") is False
        assert redis.exists("user:123:settings") is False

    def test_invalidate_multiple_patterns(self, redis):
        """Test invalidating multiple patterns."""
        redis.set("term:search:python", ["term1", "term2"])
        redis.set("term:recent", ["term3"])

        @invalidate_cache("term:search:*")
        @invalidate_cache("term:recent")
        def create_new_term():
            return "Created"

        create_new_term()

        assert redis.exists("term:search:python") is False
        assert redis.exists("term:recent") is False


class TestCacheInvalidationPatterns:
    """Test different cache invalidation strategies."""

    @pytest.fixture
    def redis(self):
        """Clear cache before each test."""
        client = get_redis_client()
        client.clear()
        yield client
        client.clear()

    def test_ttl_based_expiration(self, redis):
        """Test automatic expiration via TTL."""
        redis.set("temp", "value", ttl_seconds=1)
        assert redis.get("temp") == "value"

        time.sleep(1.1)
        assert redis.get("temp") is None

    def test_event_based_invalidation(self, redis):
        """Test invalidation on specific events."""
        # Cache user data
        redis.set("user:456:profile", {"name": "Alice"})
        redis.set("user:456:settings", {"notifications": True})

        # Simulate update event
        redis.delete_pattern("user:456:*")

        # Cache invalidated
        assert redis.exists("user:456:profile") is False
        assert redis.exists("user:456:settings") is False

    def test_cascade_invalidation(self, redis):
        """Test invalidating related caches together."""
        # Cache multiple related entries
        redis.set("term:123", {"name": "Python"})
        redis.set("term:123:relations", ["java", "rust"])
        redis.set("term:search:python", {"results": []})

        # Invalidate term and its relations
        redis.delete_pattern("term:123*")
        redis.delete_pattern("term:search:*")

        assert redis.exists("term:123") is False
        assert redis.exists("term:123:relations") is False
        assert redis.exists("term:search:python") is False


class TestErrorHandling:
    """Test error handling in cache operations."""

    @pytest.fixture
    def redis(self):
        """Create test Redis client."""
        client = RedisClient(host="localhost", port=6379, prefix="test:")
        client.clear()
        yield client
        client.clear()

    def test_get_nonexistent_key_returns_none(self, redis):
        """Test that getting non-existent key returns None gracefully."""
        result = redis.get("nonexistent")
        assert result is None

    def test_delete_nonexistent_key_returns_false(self, redis):
        """Test that deleting non-existent key returns False."""
        result = redis.delete("nonexistent")
        assert result is False

    def test_mget_with_mix_of_existing_and_missing(self, redis):
        """Test mget with some missing keys."""
        redis.set("key1", "value1")
        redis.set("key3", "value3")

        result = redis.mget(["key1", "key2", "key3"])

        assert result["key1"] == "value1"
        assert result["key2"] is None
        assert result["key3"] == "value3"
