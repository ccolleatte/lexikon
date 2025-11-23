"""
Health check and status endpoints.
Provides system health, metrics, and diagnostics.
"""

import logging
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from db.postgres import get_db
from logging_config import get_metrics
from cache import get_redis_client
from models import ApiResponse

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Basic health check (liveness probe)."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@router.get("/ready")
async def readiness_probe(db: Session = Depends(get_db)):
    """
    Readiness probe - returns 200 only if application can accept traffic.

    Checks:
    - Database connectivity (must be able to execute queries)
    - Redis connectivity (cache layer must be available)

    Returns:
    - 200: Ready to accept traffic (all dependencies healthy)
    - 503: Not ready (missing critical dependencies)

    Used by Docker/Kubernetes for traffic routing decisions.
    Different from /health (liveness) - readiness is stricter.
    """
    ready_status = {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "dependencies": {}
    }

    # Check database connectivity
    try:
        db.execute(text("SELECT 1"))
        ready_status["dependencies"]["database"] = "ok"
    except Exception as e:
        logger.error(f"Database readiness check failed: {e}")
        ready_status["status"] = "not_ready"
        ready_status["dependencies"]["database"] = f"error: {str(e)}"
        return ready_status, 503

    # Check Redis connectivity
    try:
        redis_client = get_redis_client()
        if redis_client.health_check():
            ready_status["dependencies"]["cache"] = "ok"
        else:
            logger.error("Redis health check failed in readiness probe")
            ready_status["status"] = "not_ready"
            ready_status["dependencies"]["cache"] = "error: health check failed"
            return ready_status, 503
    except Exception as e:
        logger.error(f"Redis readiness check failed: {e}")
        ready_status["status"] = "not_ready"
        ready_status["dependencies"]["cache"] = f"error: {str(e)}"
        return ready_status, 503

    return ready_status, 200


@router.get("/status")
async def status(db: Session = Depends(get_db)):
    """
    Detailed status endpoint.
    Returns system health, database status, cache status, and metrics.
    """
    status_info = {
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0",
        "environment": "development",  # Would be from env var
    }

    # Database status
    try:
        db.execute(text("SELECT 1"))
        status_info["database"] = {
            "status": "healthy",
            "connection": "ok",
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        status_info["database"] = {
            "status": "unhealthy",
            "error": str(e),
        }

    # Redis status
    try:
        redis_client = get_redis_client()
        is_healthy = redis_client.health_check()
        if is_healthy:
            info = redis_client.get_info()
            status_info["cache"] = {
                "status": "healthy",
                "connection": "ok",
                "memory_mb": info.get("used_memory_mb", 0),
                "clients": info.get("connected_clients", 0),
            }
        else:
            status_info["cache"] = {
                "status": "unhealthy",
                "error": "Health check failed",
            }
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        status_info["cache"] = {
            "status": "unhealthy",
            "error": str(e),
        }

    # Metrics
    status_info["metrics"] = get_metrics()

    return ApiResponse(success=True, data=status_info)


@router.get("/metrics")
async def metrics():
    """
    Get application metrics.

    Returns:
        - Requests: total, successful, failed, error_rate
        - Authentication: failures
        - Cache: hits, misses, hit_rate
        - Database: query count
        - Webhooks: deliveries
    """
    return ApiResponse(success=True, data=get_metrics())


@router.get("/")
async def root():
    """API root information."""
    return {
        "name": "Lexikon API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "ready": "/ready",
        "status": "/status",
        "metrics": "/metrics",
    }
