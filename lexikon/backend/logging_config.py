"""
Structured logging configuration for Lexikon.
Sets up JSON logging with context tracking and performance metrics.
"""

import logging
import logging.config
import json
from pythonjsonlogger import jsonlogger
import os
from typing import Optional, Dict, Any

# Environment-based configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = os.getenv("LOG_FORMAT", "json")  # json or text


class ContextJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with context support."""

    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, str]):
        """Add fields to JSON log record."""
        super().add_fields(log_record, record, message_dict)

        # Add standard fields
        log_record["timestamp"] = self.formatTime(record)
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record["module"] = record.module
        log_record["function"] = record.funcName
        log_record["line"] = record.lineno
        log_record["environment"] = ENVIRONMENT

        # Add context if available
        if hasattr(record, "request_id"):
            log_record["request_id"] = record.request_id
        if hasattr(record, "user_id"):
            log_record["user_id"] = record.user_id
        if hasattr(record, "duration_ms"):
            log_record["duration_ms"] = record.duration_ms
        if hasattr(record, "query_count"):
            log_record["query_count"] = record.query_count

        # Add exception info if present
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)


def configure_logging():
    """Configure logging based on environment."""

    if LOG_FORMAT == "json":
        handler_formatter = ContextJsonFormatter(
            fmt="%(timestamp)s %(level)s %(name)s %(message)s"
        )
    else:
        # Text format for development
        handler_formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s:%(funcName)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(handler_formatter)
    root_logger.addHandler(console_handler)

    # Suppress noisy libraries in production
    if ENVIRONMENT == "production":
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
        logging.getLogger("asyncio").setLevel(logging.WARNING)

    # Log startup
    logger = logging.getLogger(__name__)
    logger.info(
        "Logging configured",
        extra={
            "environment": ENVIRONMENT,
            "log_level": LOG_LEVEL,
            "log_format": LOG_FORMAT,
        },
    )


def get_logger(name: str) -> logging.LoggerAdapter:
    """Get logger with context support."""
    logger = logging.getLogger(name)
    return LoggerAdapter(logger)


class LoggerAdapter(logging.LoggerAdapter):
    """Custom logger adapter for context tracking."""

    def __init__(self, logger: logging.Logger, extra: Optional[Dict[str, Any]] = None):
        super().__init__(logger, extra or {})
        self.context = {}

    def set_context(self, **kwargs):
        """Set logging context variables."""
        self.context.update(kwargs)

    def clear_context(self):
        """Clear logging context."""
        self.context.clear()

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=None):
        """Override to add context to every log."""
        if extra is None:
            extra = {}

        # Merge context into extra
        extra.update(self.context)

        super()._log(level, msg, args, exc_info, extra, stack_info)


# Common loggers
logger = get_logger(__name__)
auth_logger = get_logger("lexikon.auth")
db_logger = get_logger("lexikon.db")
api_logger = get_logger("lexikon.api")
webhook_logger = get_logger("lexikon.webhooks")
cache_logger = get_logger("lexikon.cache")


# Counters for monitoring
class MetricsCounter:
    """Simple metrics counter."""

    def __init__(self):
        self.requests_total = 0
        self.requests_successful = 0
        self.requests_failed = 0
        self.auth_failures = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.db_queries = 0
        self.webhook_deliveries = 0

    def increment_request(self):
        self.requests_total += 1

    def increment_success(self):
        self.requests_successful += 1

    def increment_failure(self):
        self.requests_failed += 1

    def increment_auth_failure(self):
        self.auth_failures += 1

    def increment_cache_hit(self):
        self.cache_hits += 1

    def increment_cache_miss(self):
        self.cache_misses += 1

    def increment_db_query(self):
        self.db_queries += 1

    def increment_webhook_delivery(self):
        self.webhook_deliveries += 1

    def get_metrics(self) -> Dict[str, Any]:
        """Get all metrics."""
        total_cache = self.cache_hits + self.cache_misses
        hit_rate = (
            (self.cache_hits / total_cache * 100) if total_cache > 0 else 0
        )

        return {
            "requests": {
                "total": self.requests_total,
                "successful": self.requests_successful,
                "failed": self.requests_failed,
                "error_rate": (
                    self.requests_failed / self.requests_total * 100
                    if self.requests_total > 0
                    else 0
                ),
            },
            "authentication": {
                "failures": self.auth_failures,
            },
            "cache": {
                "hits": self.cache_hits,
                "misses": self.cache_misses,
                "hit_rate": hit_rate,
            },
            "database": {
                "queries": self.db_queries,
            },
            "webhooks": {
                "deliveries": self.webhook_deliveries,
            },
        }

    def reset(self):
        """Reset all counters."""
        self.__init__()


# Global metrics instance
metrics = MetricsCounter()


def get_metrics() -> Dict[str, Any]:
    """Get current metrics."""
    return metrics.get_metrics()
