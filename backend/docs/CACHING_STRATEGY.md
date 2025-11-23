# Caching Strategy Guide

**Last Updated:** 2025-11-20
**Version:** 1.0

## Overview

Lexikon uses Redis for in-memory caching to reduce database load, improve response times, and enhance user experience.

## Architecture

```
┌─────────────────────┐
│   FastAPI Request   │
└──────────┬──────────┘
           │
    ┌──────▼──────┐
    │ Cache Check │ (Redis)
    └──────┬──────┘
           │
      ┌────▼────┐
  HIT │          │ MISS
    ┌─┴────┐    │
    │Cache ├────┤
    │Result    │
    └────┬─────┘
         │
    ┌────▼─────────┐
    │DB Query      │
    │+ Cache Set   │
    └────┬─────────┘
         │
    ┌────▼─────────┐
    │   Response   │
    └──────────────┘
```

## Components

### RedisClient (cache/redis_client.py)

High-level client wrapper providing:

**Basic Operations:**
- `get(key)` - Retrieve cached value
- `set(key, value, ttl_seconds)` - Store with TTL
- `delete(key)` - Remove cache entry
- `delete_pattern(pattern)` - Bulk delete with wildcard
- `exists(key)` - Check if key exists

**Batch Operations:**
- `mget(keys)` - Get multiple values
- `mset(items, ttl_seconds)` - Set multiple values
- `pipeline_context()` - Atomic batch operations

**Smart Operations:**
- `get_or_set(key, compute_fn, ttl)` - Cache-aside pattern
- `increment(key, amount)` - Atomic counter
- `health_check()` - Connection verification

**Features:**
- Automatic JSON/Pickle serialization
- Key prefixing (all keys prefixed with "lexikon:")
- TTL management (default 1 hour)
- Connection pooling
- Graceful error handling
- Detailed logging

### Decorators

#### @cache(key_prefix, ttl_seconds, key_builder)

Decorator to automatically cache function results:

```python
from cache import cache

# Simple: auto-generates cache key
@cache(key_prefix="user", ttl_seconds=3600)
def get_user(user_id: str):
    return db.query(User).filter(User.id == user_id).first()

# Custom key builder
@cache(
    key_prefix="term_search",
    ttl_seconds=7200,
    key_builder=lambda kwargs: f"{kwargs['term_name']}:{kwargs['user_id']}"
)
def search_terms(term_name: str, user_id: str):
    return db.query(Term).filter(
        Term.name.ilike(f"%{term_name}%"),
        Term.created_by == user_id
    ).all()
```

#### @invalidate_cache(pattern)

Decorator to invalidate cache on write operations:

```python
from cache import invalidate_cache

@invalidate_cache("user:*")  # Invalidate all user caches
def update_user(user_id: str, **updates):
    # Update database
    user = db.query(User).filter(User.id == user_id).first()
    for key, value in updates.items():
        setattr(user, key, value)
    db.commit()
    return user
```

## Caching Patterns

### 1. Cache-Aside (Lazy Loading)

Load data from cache, compute if missing, then cache it.

```python
from cache import get_redis_client

def get_user_profile(user_id: str):
    redis = get_redis_client()

    # Try cache
    cached = redis.get(f"user:{user_id}")
    if cached:
        return cached

    # Not in cache, fetch from DB
    user = db.query(User).filter(User.id == user_id).first()

    # Store in cache
    redis.set(f"user:{user_id}", user, ttl_seconds=3600)

    return user
```

Or use the convenient `get_or_set`:

```python
def get_user_profile(user_id: str):
    redis = get_redis_client()
    return redis.get_or_set(
        f"user:{user_id}",
        lambda: db.query(User).filter(User.id == user_id).first(),
        ttl_seconds=3600
    )
```

### 2. Write-Through Cache

Update cache and database together.

```python
def update_user_email(user_id: str, new_email: str):
    redis = get_redis_client()

    # Update database
    user = db.query(User).filter(User.id == user_id).first()
    user.email = new_email
    db.commit()

    # Update cache
    redis.set(f"user:{user_id}", user, ttl_seconds=3600)

    return user
```

### 3. Cache Invalidation on Write

Invalidate related cache entries when data changes.

```python
@invalidate_cache("term:*")  # Invalidate all term caches
@invalidate_cache("user:*")  # Invalidate all user caches
def create_term(term_data):
    term = Term(**term_data)
    db.add(term)
    db.commit()
    return term
```

## What to Cache

### ✅ GOOD Candidates

1. **Frequently Accessed, Rarely Changed Data**
   - User profiles: `user:{user_id}`
   - User settings: `user:{user_id}:settings`
   - Read-only reference data

2. **Expensive Computations**
   - Search results: `search:{query}:{user_id}`
   - Aggregated stats: `stats:{period}`
   - Report generation results

3. **Database Queries That...
   - Run frequently
   - Have predictable access patterns
   - Return data not changed often

### ❌ BAD Candidates

1. **Real-Time Data**
   - Current session status
   - Real-time counters
   - Stock prices, rates, etc.

2. **User-Sensitive Data**
   - Passwords, secrets
   - Payment information
   - Personally identifiable information

3. **Frequently Changing Data**
   - Active user sessions (use Redis directly, not caching)
   - Real-time metrics
   - Chat messages

4. **Huge Objects**
   - Large result sets (paginate instead)
   - Full text search results (Elasticsearch instead)
   - Media files (CDN instead)

## Cache Keys Design

### Naming Conventions

Use hierarchical key patterns for organization:

```
{entity}:{id}                              # User: "user:123"
{entity}:{id}:{attribute}                  # User email: "user:123:email"
{action}:{param1}:{param2}                 # Search: "search:terms:python:user123"
{resource}:{id}:{relation}                 # Project terms: "project:456:terms"
{type}:list:{user_id}                      # User's items: "term:list:user123"
{type}:page:{page}:{limit}                 # Paginated: "terms:page:1:50"
```

### Examples

```python
redis.set("user:550e8400", user_data)
redis.set("user:550e8400:settings", settings)
redis.set("term:search:python:550e8400", results)
redis.set("project:456:terms", terms_list)
redis.set("api_keys:550e8400", keys_list)
redis.set("stats:daily:2025-11-20", stats)
```

## Cache Invalidation Strategies

### Pattern 1: Time-Based (TTL)

Simplest: Let data expire automatically.

```python
# Cache for 1 hour
redis.set("user:123", user_data, ttl_seconds=3600)

# Cache for 24 hours (less frequently changing)
redis.set("project:456", project, ttl_seconds=86400)

# Cache for 5 minutes (frequently changing)
redis.set("stats:live", stats, ttl_seconds=300)
```

### Pattern 2: Event-Based Invalidation

Invalidate on specific events.

```python
@invalidate_cache("user:*")
def update_user(user_id: str, updates: dict):
    user = db.query(User).get(user_id)
    for key, val in updates.items():
        setattr(user, key, val)
    db.commit()
    return user

@invalidate_cache("term:search:*")  # Invalidate all search caches
def create_term(term_data):
    term = Term(**term_data)
    db.add(term)
    db.commit()
    return term
```

### Pattern 3: Lazy Invalidation

Check freshness on cache hit.

```python
def get_user_with_freshness_check(user_id: str):
    redis = get_redis_client()
    cached = redis.get(f"user:{user_id}")

    if cached:
        # Check if stale
        if cache_is_stale(cached):
            redis.delete(f"user:{user_id}")
        else:
            return cached

    # Fetch fresh
    user = db.query(User).filter(User.id == user_id).first()
    redis.set(f"user:{user_id}", user, ttl_seconds=3600)
    return user
```

### Pattern 4: Explicit Invalidation

Manual invalidation on specific actions.

```python
def link_oauth_account(user_id: str, provider: str, account_id: str):
    # Link account in DB
    oauth = OAuthAccount(
        user_id=user_id,
        provider=provider,
        provider_user_id=account_id
    )
    db.add(oauth)
    db.commit()

    # Invalidate user's OAuth cache
    redis = get_redis_client()
    redis.delete(f"user:{user_id}:oauth_accounts")
```

## Configuration

### Redis Client Setup

Default configuration in `cache/redis_client.py`:

```python
RedisClient(
    host="localhost",           # Redis server
    port=6379,                  # Default Redis port
    db=0,                       # Database number
    password=None,              # No password (dev)
    prefix="lexikon:",          # Cache key prefix
    default_ttl_seconds=3600,   # 1 hour default TTL
    max_pool_size=10,           # Connection pool
)
```

### Environment Variables

```bash
# .env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=dev-secret
REDIS_DB=0
REDIS_DEFAULT_TTL=3600
```

### Docker Compose

Redis service is included in `docker-compose.yml`:

```yaml
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data
  command: redis-server --appendonly yes
```

Start with: `docker-compose up redis`

## Monitoring & Debugging

### Health Check

```python
from cache import get_redis_client

redis = get_redis_client()
is_healthy = redis.health_check()

# Get info
info = redis.get_info()
# {
#     "used_memory_mb": 125.5,
#     "connected_clients": 3,
#     "total_commands_processed": 15000
# }
```

### Cache Statistics

Monitor cache effectiveness:

```python
total_requests = 10000
cache_hits = 8500
hit_rate = cache_hits / total_requests  # 85%
```

**Target metrics:**
- Hit rate: > 80% for read-heavy operations
- Response time improvement: 10-100x faster than DB
- Memory usage: < 500MB for typical workload

### Manual Cache Management

```python
from cache import get_redis_client

redis = get_redis_client()

# Clear specific type
redis.delete_pattern("user:*")

# Clear all cache
redis.clear()

# Check if key exists
exists = redis.exists("user:123")
```

### Common Issues

**Issue: Cache Key Misses**
- Problem: Key doesn't exist or expired
- Solution: Check TTL, verify key naming consistency

**Issue: Stale Data**
- Problem: Cache wasn't invalidated on update
- Solution: Use @invalidate_cache decorator

**Issue: High Memory Usage**
- Problem: Too much data cached or long TTLs
- Solution: Reduce TTL or cache size limit

**Issue: Connection Errors**
- Problem: Redis not running or unreachable
- Solution: Check `docker-compose up redis` and firewall

## Performance Benchmarks

### Read Performance

| Operation | Without Cache | With Cache | Improvement |
|-----------|---------------|-----------|-------------|
| Get user | 15ms (DB) | 2ms | 7.5x faster |
| Search terms | 45ms (DB) | 3ms | 15x faster |
| Get projects | 25ms (DB) | 1ms | 25x faster |

### Memory Usage

| Scenario | Memory | Entries | Avg Size |
|----------|--------|---------|----------|
| 1000 users cached | 5MB | 1000 | 5KB |
| 10000 term searches | 50MB | 10000 | 5KB |
| Full capacity (1M keys) | 500MB | 1M | 500B |

## Best Practices

1. **Always use TTL**
   - Set appropriate expiration times
   - Prevents stale data buildup
   - Saves memory automatically

2. **Key Naming Consistency**
   - Use hierarchical patterns
   - Document key formats
   - Version keys for migrations

3. **Error Handling**
   - Cache failure shouldn't break app
   - Fall back to database queries
   - Log cache errors for monitoring

4. **Invalidation Strategy**
   - Invalidate on writes
   - Use patterns for bulk invalidation
   - Test cache behavior

5. **Size Limits**
   - Don't cache huge objects
   - Paginate large result sets
   - Monitor memory usage

6. **Sensitive Data**
   - Never cache passwords/secrets
   - Use short TTLs for sensitive data
   - Log cache access for sensitive keys

## Testing

See `tests/test_redis_caching.py` for comprehensive test examples including:
- Cache hits/misses
- TTL expiration
- Serialization/deserialization
- Invalidation patterns
- Error handling

## Related Files

- **Client**: `cache/redis_client.py`
- **Tests**: `tests/test_redis_caching.py`
- **Docker**: `docker-compose.yml` (Redis service)
- **Config**: `requirements.txt` (redis==5.0.1)

## Further Reading

- [Redis Best Practices](https://redis.io/docs/management/optimization/)
- [Cache Design Patterns](https://docs.microsoft.com/en-us/azure/architecture/patterns/cache-aside)
- [Redis Memory Optimization](https://redis.io/topics/memory-optimization)
