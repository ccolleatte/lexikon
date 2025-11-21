# Monitoring & Logging Guide

**Last Updated:** 2025-11-20
**Version:** 1.0

## Overview

Lexikon uses structured JSON logging with context tracking and built-in metrics for comprehensive observability.

## Architecture

```
┌─────────────────────┐
│   FastAPI Request   │
└──────────┬──────────┘
           │
    ┌──────▼───────┐
    │ Logging      │
    │ Middleware   │ ←→ JSON Formatter
    └──────┬───────┘
           │
    ┌──────▼──────────┐
    │ Request Handler │
    └──────┬──────────┘
           │
    ┌──────▼──────────┐
    │ Metrics Counter │ ←→ /metrics endpoint
    └──────┬──────────┘
           │
    ┌──────▼──────────┐
    │    Response     │
    └─────────────────┘
```

## Structured Logging

### JSON Format

All logs are JSON-formatted in production for easy parsing:

```json
{
  "timestamp": "2025-11-20T12:00:00.000000",
  "level": "INFO",
  "logger": "lexikon.api",
  "module": "terms",
  "function": "create_term",
  "line": 45,
  "environment": "production",
  "message": "Term created successfully",
  "request_id": "req_abc123",
  "user_id": "user_550e8400",
  "duration_ms": 125.5,
  "query_count": 3
}
```

### Text Format (Development)

Human-readable format for local development:

```
2025-11-20 12:00:00 [INFO] lexikon.api:create_term:45 - Term created successfully
```

## Configuration

### Environment Variables

```bash
# .env
ENVIRONMENT=production          # development or production
LOG_LEVEL=INFO                 # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=json                # json or text
```

### Setup in main.py

```python
from logging_config import configure_logging, get_logger

# Configure logging on startup
configure_logging()

# Get logger
logger = get_logger("lexikon.api")
```

## Usage

### Basic Logging

```python
from logging_config import get_logger

logger = get_logger("lexikon.api")

# Simple log
logger.info("User registered", extra={"user_id": "user_123"})

# Log with context
logger.set_context(user_id="user_123", request_id="req_abc")
logger.info("Term created")
logger.clear_context()

# Structured data
logger.warning(
    "Slow query detected",
    extra={
        "query": "SELECT * FROM terms...",
        "duration_ms": 850,
        "threshold_ms": 100,
    }
)

# Error with exception
try:
    perform_operation()
except Exception as e:
    logger.error("Operation failed", exc_info=True)
```

### Logger Adapters

```python
from logging_config import auth_logger, db_logger, api_logger, webhook_logger, cache_logger

# Use specialized loggers
auth_logger.info("Login successful", extra={"user_id": "user_123"})
db_logger.warning("N+1 query detected")
api_logger.error("Rate limit exceeded")
webhook_logger.info("Webhook delivered")
cache_logger.debug("Cache hit")
```

### Context Tracking

```python
def handle_request(user_id: str, request_id: str):
    logger = get_logger(__name__)

    # Set context
    logger.set_context(user_id=user_id, request_id=request_id)

    try:
        # All logs will include user_id and request_id
        logger.info("Processing request")
        result = process()
        logger.info("Request successful", extra={"duration_ms": 125})
        return result
    finally:
        logger.clear_context()
```

## Metrics

### Endpoints

**GET** `/metrics` - Application metrics

```json
{
  "success": true,
  "data": {
    "requests": {
      "total": 1250,
      "successful": 1205,
      "failed": 45,
      "error_rate": 3.6
    },
    "authentication": {
      "failures": 12
    },
    "cache": {
      "hits": 890,
      "misses": 110,
      "hit_rate": 89.0
    },
    "database": {
      "queries": 2150
    },
    "webhooks": {
      "deliveries": 125
    }
  }
}
```

**GET** `/status` - Detailed system status

```json
{
  "success": true,
  "data": {
    "timestamp": "2025-11-20T12:00:00",
    "version": "0.1.0",
    "environment": "production",
    "database": {
      "status": "healthy",
      "connection": "ok"
    },
    "cache": {
      "status": "healthy",
      "connection": "ok",
      "memory_mb": 125.5,
      "clients": 3
    },
    "metrics": { /* same as /metrics */ }
  }
}
```

**GET** `/health` - Liveness probe

```json
{
  "status": "healthy",
  "timestamp": "2025-11-20T12:00:00"
}
```

### Metrics Collection

```python
from logging_config import metrics

# Increment counters
metrics.increment_request()
metrics.increment_success()
metrics.increment_cache_hit()

# Get current metrics
current_metrics = metrics.get_metrics()

# Reset metrics (e.g., daily)
metrics.reset()
```

## Monitoring Best Practices

### 1. Use Request IDs

Track requests end-to-end:

```python
import uuid
from fastapi import Request

async def middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    # Log middleware
    logger.set_context(request_id=request_id)

    response = await call_next(request)
    return response
```

### 2. Log Slow Operations

```python
import time
from logging_config import logger

start = time.time()
result = expensive_operation()
duration_ms = (time.time() - start) * 1000

logger.info(
    "Operation completed",
    extra={"duration_ms": duration_ms}
)

if duration_ms > 1000:
    logger.warning(
        "Slow operation detected",
        extra={"duration_ms": duration_ms, "threshold_ms": 1000}
    )
```

### 3. Track Performance Metrics

```python
from logging_config import metrics

def endpoint():
    metrics.increment_request()

    try:
        result = process()
        metrics.increment_success()
        return result
    except Exception as e:
        metrics.increment_failure()
        raise
```

### 4. Monitor Cache Effectiveness

```python
from logging_config import metrics

def get_cached_user(user_id: str):
    cached = cache.get(f"user:{user_id}")
    if cached:
        metrics.increment_cache_hit()
        return cached
    else:
        metrics.increment_cache_miss()
        return fetch_from_db()
```

### 5. Structured Data in Logs

```python
# Good - structured context
logger.info(
    "User action",
    extra={
        "action": "create_term",
        "user_id": "user_123",
        "term_count": 45,
        "duration_ms": 125,
    }
)

# Bad - unstructured
logger.info(f"User user_123 created term 45 in 125ms")
```

## Deployment

### Production Setup

1. **Enable JSON logging:**
   ```bash
   export LOG_FORMAT=json
   export LOG_LEVEL=INFO
   export ENVIRONMENT=production
   ```

2. **Log aggregation:**
   - Collect logs to ELK, Datadog, CloudWatch, etc.
   - Parse JSON format automatically
   - Create dashboards from structured fields

3. **Alerting:**
   - Error rate > 5%
   - Response time > 1000ms (P95)
   - Cache hit rate < 80%
   - Database query time > 500ms

### Local Development

```bash
export LOG_FORMAT=text
export LOG_LEVEL=DEBUG
export ENVIRONMENT=development
```

## Log Files

### Recommended Structure

```
logs/
├── application.log       # All logs
├── errors.log           # ERROR and CRITICAL only
├── performance.log      # Slow queries, requests > 500ms
└── security.log         # Auth failures, unauthorized access
```

### Log Rotation

```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'logs/application.log',
    maxBytes=10_000_000,  # 10MB
    backupCount=10        # Keep 10 files
)
```

## Analyzing Logs

### Common Queries

```bash
# Find errors
grep '"level": "ERROR"' logs/application.log

# Find slow queries
jq 'select(.duration_ms > 1000)' logs/application.log

# Find user activity
jq "select(.user_id == \"user_123\")" logs/application.log

# Count by level
jq '.level' logs/application.log | sort | uniq -c
```

## Related Files

- **Config**: `logging_config.py`
- **Middleware**: `middleware/performance.py`
- **Health**: `api/health.py`

## Further Reading

- [Structured Logging Best Practices](https://www.kartar.net/2015/12/structured-logging/)
- [JSON Logging Standards](https://www.w3.org/TR/json-ld/)
- [Observability in Python](https://opentelemetry.io/docs/reference/specification/logs/)
