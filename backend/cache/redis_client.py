"""
Redis caching client for Lexikon.
Provides high-level caching operations with automatic serialization and TTL management.
"""

import redis
import json
import logging
from typing import Optional, Any, Dict, List, Callable
from contextlib import contextmanager
from functools import wraps
import hashlib
import pickle

logger = logging.getLogger(__name__)


class RedisClient:
    """
    High-level Redis client wrapper.

    Features:
    - Automatic serialization/deserialization (JSON + pickle)
    - TTL management
    - Key prefix namespacing
    - Connection pooling
    - Health checks
    - Cache invalidation
    """

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
        """Serialize value for storage."""
        try:
            # Try JSON first (human-readable, smaller)
            if isinstance(value, (dict, list, str, int, float, bool, type(None))):
                return json.dumps(value).encode("utf-8")
        except (TypeError, ValueError):
            pass

        # Fall back to pickle for complex objects
        return pickle.dumps(value)

    def _deserialize(self, data: bytes) -> Any:
        """Deserialize value from storage."""
        if data is None:
            return None

        # Try JSON first
        try:
            return json.loads(data.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass

        # Fall back to pickle
        try:
            return pickle.loads(data)
        except (pickle.UnpicklingError, EOFError):
            logger.error(f"Failed to deserialize cached value")
            return None

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
        Set value in cache.

        Args:
            key: Cache key (without prefix)
            value: Value to cache
            ttl_seconds: Time to live in seconds (uses default if None)

        Returns:
            True if successful
        """
        try:
            full_key = self._make_key(key)
            ttl = ttl_seconds or self.default_ttl_seconds
            serialized = self._serialize(value)

            self.client.setex(full_key, ttl, serialized)
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
            return True
        except redis.RedisError as e:
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
        Delete all keys matching a pattern.

        Args:
            pattern: Pattern with wildcards (e.g., "user:123:*")

        Returns:
            Number of keys deleted
        """
        try:
            full_pattern = self._make_key(pattern)
            keys = self.client.keys(full_pattern)
            if not keys:
                return 0

            deleted = self.client.delete(*keys)
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
        Clear all cached entries with our prefix.

        Returns:
            Number of keys deleted
        """
        try:
            pattern = f"{self.prefix}*"
            keys = self.client.keys(pattern)
            if not keys:
                return 0

            deleted = self.client.delete(*keys)
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
        Set multiple values in cache.

        Args:
            items: Dictionary of key -> value pairs
            ttl_seconds: TTL for all values

        Returns:
            True if successful
        """
        try:
            ttl = ttl_seconds or self.default_ttl_seconds

            pipeline = self.client.pipeline()
            for key, value in items.items():
                full_key = self._make_key(key)
                serialized = self._serialize(value)
                pipeline.setex(full_key, ttl, serialized)

            pipeline.execute()
            logger.debug(f"Cache mset: {len(items)} keys (TTL: {ttl}s)")
            return True
        except redis.RedisError as e:
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
    """Get or create global Redis client."""
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient()
    return _redis_client


def cache(
    key_prefix: str,
    ttl_seconds: int = 3600,
    key_builder: Optional[Callable] = None,
):
    """
    Decorator to cache function results.

    Usage:
        @cache(key_prefix="user", ttl_seconds=3600)
        def get_user(user_id: str):
            return db.query(User).filter(User.id == user_id).first()

        # Customize cache key
        @cache(
            key_prefix="term_search",
            key_builder=lambda kwargs: f"{kwargs['term_name']}:{kwargs['user_id']}"
        )
        def search_terms(term_name: str, user_id: str):
            ...

    Args:
        key_prefix: Prefix for cache key
        ttl_seconds: Time to live in seconds
        key_builder: Optional function to build cache key from args/kwargs
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            redis_client = get_redis_client()

            # Build cache key
            if key_builder:
                cache_key = key_builder(kwargs)
            else:
                # Default: use function name and first argument
                arg_str = "_".join(str(arg) for arg in args[:1]) if args else ""
                kwarg_str = "_".join(f"{k}={v}" for k, v in kwargs.items())
                key_part = f"{arg_str}_{kwarg_str}".strip("_")
                cache_key = f"{key_prefix}:{key_part}" if key_part else key_prefix

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
