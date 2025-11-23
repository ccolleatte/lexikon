"""
Redis caching client for Lexikon.
Provides high-level caching operations with automatic serialization and TTL management.
"""

import redis
import json
import logging
import os
from typing import Optional, Any, Dict, List, Callable
from contextlib import contextmanager
from functools import wraps
import hashlib

logger = logging.getLogger(__name__)


class RedisClient:
    """
    High-level Redis client wrapper.

    Features:
    - Automatic serialization/deserialization (JSON only, no pickle)
    - TTL management with min/max validation
    - Key prefix namespacing
    - Connection pooling
    - Health checks
    - Cache invalidation
    """

    # TTL validation limits
    MIN_TTL_SECONDS = 1  # Minimum 1 second
    MAX_TTL_SECONDS = 86400  # Maximum 24 hours

    # Memory protection limits
    MAX_VALUE_SIZE_BYTES = 10 * 1024 * 1024  # Maximum 10MB per value
    MAX_TOTAL_MEMORY_MB = 100  # Maximum 100MB total cache usage

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        prefix: str = "lexikon:",
        default_ttl_seconds: int = 3600,
        max_pool_size: int = 10,
        socket_connect_timeout: int = 5,
        socket_keepalive: bool = True,
        decode_responses: bool = False,
    ):
        """
        Initialize Redis client.

        Args:
            host: Redis server hostname
            port: Redis server port
            db: Redis database number
            password: Redis password (if authentication required)
            prefix: Key prefix for all cache entries
            default_ttl_seconds: Default TTL for cached values (1 hour)
            max_pool_size: Maximum connection pool size
            socket_connect_timeout: Socket connection timeout in seconds
            socket_keepalive: Enable TCP keepalive
            decode_responses: Automatically decode responses as strings
        """
        self.prefix = prefix
        self.default_ttl_seconds = default_ttl_seconds

        try:
            self.client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=decode_responses,
                socket_connect_timeout=socket_connect_timeout,
                socket_keepalive=socket_keepalive,
                max_connections=max_pool_size,
                health_check_interval=30,
            )
            # Test connection
            self.client.ping()
            logger.info(f"✅ Connected to Redis at {host}:{port}")
        except redis.ConnectionError as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            raise

    def _make_key(self, key: str) -> str:
        """Create prefixed cache key."""
        return f"{self.prefix}{key}"

    def _serialize(self, value: Any) -> bytes:
        """Serialize value for storage using JSON only (no pickle for security)."""
        # Only allow JSON-serializable types (prevents RCE via pickle)
        if not isinstance(value, (dict, list, str, int, float, bool, type(None))):
            raise ValueError(
                f"Cannot cache non-JSON-serializable type: {type(value).__name__}. "
                f"Please convert to dict/list/str/int/float/bool/None before caching."
            )

        try:
            return json.dumps(value).encode("utf-8")
        except (TypeError, ValueError) as e:
            logger.error(f"Failed to serialize cache value: {e}")
            raise

    def _deserialize(self, data: bytes) -> Any:
        """Deserialize value from storage using JSON only."""
        if data is None:
            return None

        try:
            return json.loads(data.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.error(f"Failed to deserialize cached value: {e}")
            return None

    def _validate_ttl(self, ttl: int) -> int:
        """
        Validate and enforce TTL bounds.

        Args:
            ttl: TTL in seconds

        Returns:
            Validated TTL value (clamped to min/max bounds)

        Raises:
            ValueError: If TTL is outside acceptable range
        """
        if ttl < self.MIN_TTL_SECONDS:
            raise ValueError(
                f"TTL must be at least {self.MIN_TTL_SECONDS} second(s), "
                f"got {ttl}s. Set to None or use default_ttl_seconds to avoid this."
            )

        if ttl > self.MAX_TTL_SECONDS:
            # Log warning but clamp to max instead of failing
            logger.warning(
                f"TTL {ttl}s exceeds maximum {self.MAX_TTL_SECONDS}s (24h), "
                f"clamping to maximum."
            )
            return self.MAX_TTL_SECONDS

        return ttl

    def _validate_value_size(self, value_bytes: bytes) -> None:
        """
        Validate that value size doesn't exceed limits.

        Args:
            value_bytes: Serialized value

        Raises:
            ValueError: If value exceeds maximum size
        """
        size_mb = len(value_bytes) / (1024 * 1024)

        if len(value_bytes) > self.MAX_VALUE_SIZE_BYTES:
            raise ValueError(
                f"Cached value size {size_mb:.2f}MB exceeds maximum {self.MAX_VALUE_SIZE_BYTES / (1024 * 1024):.0f}MB. "
                f"Consider compressing or splitting the data."
            )

    def _check_memory_usage(self) -> None:
        """
        Check current cache memory usage against limits.
        Logs warning if exceeding threshold.
        """
        try:
            info = self.client.info()
            used_memory_mb = info.get("used_memory", 0) / (1024 * 1024)

            if used_memory_mb > self.MAX_TOTAL_MEMORY_MB:
                logger.warning(
                    f"Cache memory usage {used_memory_mb:.2f}MB exceeds "
                    f"maximum {self.MAX_TOTAL_MEMORY_MB}MB. "
                    f"Consider clearing old entries or increasing max memory."
                )
        except redis.RedisError:
            # Silently fail memory checks to avoid blocking operations
            pass

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key (without prefix)

        Returns:
            Cached value or None if not found
        """
        try:
            full_key = self._make_key(key)
            data = self.client.get(full_key)
            if data is None:
                return None

            value = self._deserialize(data)
            logger.debug(f"Cache hit: {key}")
            return value
        except redis.RedisError as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None

    def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
    ) -> bool:
        """
        Set value in cache with TTL and memory validation.

        Args:
            key: Cache key (without prefix)
            value: Value to cache
            ttl_seconds: Time to live in seconds (uses default if None)
                        Must be between MIN_TTL_SECONDS and MAX_TTL_SECONDS

        Returns:
            True if successful, False if validation fails or error occurs
        """
        try:
            full_key = self._make_key(key)
            ttl = ttl_seconds or self.default_ttl_seconds

            # Validate TTL (min 1 second, max 24 hours)
            ttl = self._validate_ttl(ttl)

            serialized = self._serialize(value)

            # Validate value size (max 10MB per value)
            self._validate_value_size(serialized)

            # Check total memory usage (warn if exceeding 100MB)
            self._check_memory_usage()

            self.client.setex(full_key, ttl, serialized)
            logger.debug(f"Cache set: {key} (size: {len(serialized) / 1024:.1f}KB, TTL: {ttl}s)")
            return True
        except (redis.RedisError, ValueError) as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete value from cache.

        Args:
            key: Cache key (without prefix)

        Returns:
            True if deleted, False if not found
        """
        try:
            full_key = self._make_key(key)
            deleted = self.client.delete(full_key)
            if deleted:
                logger.debug(f"Cache invalidated: {key}")
            return deleted > 0
        except redis.RedisError as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern using SCAN (non-blocking).

        Args:
            pattern: Pattern with wildcards (e.g., "user:123:*")

        Returns:
            Number of keys deleted
        """
        try:
            full_pattern = self._make_key(pattern)
            deleted = 0
            cursor = 0

            # Use SCAN instead of KEYS (non-blocking operation)
            while True:
                cursor, keys = self.client.scan(cursor, match=full_pattern, count=100)
                if keys:
                    deleted += self.client.delete(*keys)
                if cursor == 0:
                    break

            logger.debug(f"Cache invalidated {deleted} keys matching {pattern}")
            return deleted
        except redis.RedisError as e:
            logger.error(f"Error deleting pattern {pattern}: {e}")
            return 0

    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            full_key = self._make_key(key)
            return self.client.exists(full_key) > 0
        except redis.RedisError:
            return False

    def clear(self) -> int:
        """
        Clear all cached entries with our prefix using SCAN (non-blocking).

        Returns:
            Number of keys deleted
        """
        try:
            pattern = f"{self.prefix}*"
            deleted = 0
            cursor = 0

            # Use SCAN instead of KEYS (non-blocking operation)
            while True:
                cursor, keys = self.client.scan(cursor, match=pattern, count=100)
                if keys:
                    deleted += self.client.delete(*keys)
                if cursor == 0:
                    break

            logger.info(f"Cache cleared: {deleted} entries removed")
            return deleted
        except redis.RedisError as e:
            logger.error(f"Error clearing cache: {e}")
            return 0

    def get_or_set(
        self,
        key: str,
        compute_fn: Callable[[], Any],
        ttl_seconds: Optional[int] = None,
    ) -> Any:
        """
        Get value from cache or compute and cache if missing.

        Args:
            key: Cache key
            compute_fn: Function to call if cache miss
            ttl_seconds: TTL for cached value

        Returns:
            Cached or computed value
        """
        # Try cache first
        value = self.get(key)
        if value is not None:
            return value

        # Compute value
        value = compute_fn()

        # Cache it
        self.set(key, value, ttl_seconds)

        return value

    def mget(self, keys: List[str]) -> Dict[str, Optional[Any]]:
        """
        Get multiple values from cache.

        Args:
            keys: List of cache keys

        Returns:
            Dictionary mapping key -> value (value None if not found)
        """
        try:
            full_keys = [self._make_key(k) for k in keys]
            values = self.client.mget(full_keys)

            result = {}
            for key, value in zip(keys, values):
                result[key] = self._deserialize(value) if value else None

            logger.debug(f"Cache mget: {len(keys)} keys")
            return result
        except redis.RedisError as e:
            logger.error(f"Error in mget: {e}")
            return {k: None for k in keys}

    def mset(
        self,
        items: Dict[str, Any],
        ttl_seconds: Optional[int] = None,
    ) -> bool:
        """
        Set multiple values in cache with TTL and memory validation.

        Args:
            items: Dictionary of key -> value pairs
            ttl_seconds: TTL for all values (validated for bounds)

        Returns:
            True if successful, False if validation fails or error occurs
        """
        try:
            ttl = ttl_seconds or self.default_ttl_seconds

            # Validate TTL (min 1 second, max 24 hours)
            ttl = self._validate_ttl(ttl)

            # Pre-validate all values before pipeline execution
            total_size = 0
            serialized_items = {}
            for key, value in items.items():
                serialized = self._serialize(value)
                # Validate each value size (max 10MB per value)
                self._validate_value_size(serialized)
                total_size += len(serialized)
                serialized_items[key] = serialized

            # Check total memory usage
            self._check_memory_usage()

            # Execute pipeline with pre-validated data
            pipeline = self.client.pipeline()
            for key, serialized in serialized_items.items():
                full_key = self._make_key(key)
                pipeline.setex(full_key, ttl, serialized)

            pipeline.execute()
            logger.debug(f"Cache mset: {len(items)} keys (total: {total_size / 1024:.1f}KB, TTL: {ttl}s)")
            return True
        except (redis.RedisError, ValueError) as e:
            logger.error(f"Error in mset: {e}")
            return False

    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Increment integer value in cache.

        Args:
            key: Cache key
            amount: Amount to increment by

        Returns:
            New value or None on error
        """
        try:
            full_key = self._make_key(key)
            return self.client.incrby(full_key, amount)
        except redis.RedisError as e:
            logger.error(f"Error incrementing {key}: {e}")
            return None

    def health_check(self) -> bool:
        """Check if Redis connection is healthy."""
        try:
            self.client.ping()
            return True
        except redis.RedisError:
            return False

    def get_info(self) -> Dict[str, Any]:
        """Get Redis server info."""
        try:
            info = self.client.info()
            return {
                "used_memory_mb": info.get("used_memory", 0) / (1024 * 1024),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
            }
        except redis.RedisError:
            return {}

    @contextmanager
    def pipeline_context(self):
        """Context manager for Redis pipelined operations."""
        pipe = self.client.pipeline()
        try:
            yield pipe
            pipe.execute()
        except Exception as e:
            logger.error(f"Error in pipeline: {e}")
            pipe.reset()
            raise


# Global Redis instance (lazy initialization)
_redis_client: Optional[RedisClient] = None


def get_redis_client() -> RedisClient:
    """
    Get or create global Redis client with environment variable configuration.

    Environment Variables:
    - REDIS_HOST: Redis server hostname (default: localhost)
    - REDIS_PORT: Redis server port (default: 6379)
    - REDIS_DB: Redis database number (default: 0)
    - REDIS_PASSWORD: Redis password for authentication (optional)
    - REDIS_PREFIX: Key prefix for all cache entries (default: lexikon:)

    Example:
        export REDIS_HOST=redis.example.com
        export REDIS_PORT=6379
        export REDIS_PASSWORD=your-secure-password
        python app.py
    """
    global _redis_client
    if _redis_client is None:
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", 6379))
        redis_db = int(os.getenv("REDIS_DB", 0))
        redis_password = os.getenv("REDIS_PASSWORD")
        redis_prefix = os.getenv("REDIS_PREFIX", "lexikon:")

        _redis_client = RedisClient(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            password=redis_password,
            prefix=redis_prefix,
        )

        logger.info(
            f"Redis client initialized: {redis_host}:{redis_port}/db{redis_db}"
            + (" (password-protected)" if redis_password else " (no password)")
        )
    return _redis_client


def cache(
    key_prefix: str,
    ttl_seconds: int = 3600,
    key_builder: Optional[Callable] = None,
):
    """
    Decorator to cache function results with secure key generation.

    Usage:
        @cache(key_prefix="user", ttl_seconds=3600)
        def get_user(user_id: str):
            return db.query(User).filter(User.id == user_id).first()

        # Customize cache key
        @cache(
            key_prefix="term_search",
            key_builder=lambda kwargs: (kwargs['term_name'], kwargs['user_id'])
        )
        def search_terms(term_name: str, user_id: str):
            ...

    Args:
        key_prefix: Prefix for cache key
        ttl_seconds: Time to live in seconds
        key_builder: Optional function to build cache key from args/kwargs.
                     Should return tuple of parameters to be hashed for security.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            redis_client = get_redis_client()

            # Build cache key with secure hashing
            if key_builder:
                # key_builder should return tuple/list of parameters to hash
                params = key_builder(kwargs)
                if not isinstance(params, (tuple, list)):
                    params = (params,)
                # Hash parameters to prevent cache key injection
                params_str = ":".join(str(p) for p in params)
                params_hash = hashlib.sha256(params_str.encode()).hexdigest()[:16]
                cache_key = f"{key_prefix}:{params_hash}"
            else:
                # Default: hash first arg and all kwargs for security
                key_parts = []
                if args:
                    key_parts.append(str(args[0]))
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))

                # Hash to prevent injection attacks
                params_str = "|".join(key_parts) if key_parts else ""
                if params_str:
                    params_hash = hashlib.sha256(params_str.encode()).hexdigest()[:16]
                    cache_key = f"{key_prefix}:{params_hash}"
                else:
                    cache_key = key_prefix

            # Try cache
            cached = redis_client.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached

            # Compute and cache
            result = func(*args, **kwargs)
            redis_client.set(cache_key, result, ttl_seconds)
            return result

        return wrapper
    return decorator


def invalidate_cache(pattern: str):
    """
    Decorator to invalidate cache on function execution.

    Usage:
        @invalidate_cache("user:*")
        def update_user(user_id: str):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            result = func(*args, **kwargs)
            redis_client = get_redis_client()
            redis_client.delete_pattern(pattern)
            logger.debug(f"Invalidated cache pattern: {pattern}")
            return result
        return wrapper
    return decorator
