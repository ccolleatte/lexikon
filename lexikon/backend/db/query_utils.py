"""
Query optimization utilities for common database patterns.
Provides helpers for eager loading, lazy loading, and performance logging.
"""

import logging
import time
from functools import wraps
from typing import Callable, List, TypeVar, Optional, Any

from sqlalchemy.orm import Session, selectinload, joinedload, contains_eager
from sqlalchemy import inspect

logger = logging.getLogger(__name__)

T = TypeVar("T")


class QueryProfiler:
    """Utility for measuring and logging query performance."""

    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        self.duration_ms = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.duration_ms = (time.perf_counter() - self.start_time) * 1000

        if exc_type is None:
            # Log successful queries
            if self.duration_ms > 100:  # Warn on slow queries (> 100ms)
                logger.warning(
                    f"Slow query detected: {self.operation_name} took {self.duration_ms:.2f}ms"
                )
            else:
                logger.debug(
                    f"Query: {self.operation_name} completed in {self.duration_ms:.2f}ms"
                )
        else:
            logger.error(
                f"Query error: {self.operation_name} failed after {self.duration_ms:.2f}ms - {exc_type.__name__}"
            )


def profile_query(operation_name: str) -> Callable:
    """
    Decorator for profiling individual query operations.

    Usage:
        @profile_query("get_user_by_email")
        def get_user_by_email(db: Session, email: str):
            return db.query(User).filter(User.email == email).first()
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            with QueryProfiler(f"{operation_name}"):
                return func(*args, **kwargs)
        return wrapper
    return decorator


class QueryOptimizer:
    """Helper class for building optimized queries."""

    @staticmethod
    def get_user_with_relationships(db: Session, user_id: str):
        """
        Get user with all relationships eagerly loaded.
        Prevents N+1 queries when accessing related data.
        """
        from db.postgres import User

        with QueryProfiler(f"get_user_with_relationships[{user_id}]"):
            return db.query(User).options(
                selectinload(User.oauth_accounts),
                selectinload(User.api_keys),
                selectinload(User.owned_projects),
                selectinload(User.created_terms),
            ).filter(User.id == user_id).first()

    @staticmethod
    def get_terms_by_user(db: Session, user_id: str) -> List[Any]:
        """
        Get all terms created by user with optimized loading.
        Leverages index on (created_by, name).
        """
        from db.postgres import Term

        with QueryProfiler(f"get_terms_by_user[{user_id}]"):
            # Uses index: ix_terms_created_by
            return db.query(Term).filter(
                Term.created_by == user_id
            ).order_by(Term.created_at.desc()).all()

    @staticmethod
    def get_term_by_id_for_user(db: Session, term_id: str, user_id: str) -> Optional[Any]:
        """
        Get a specific term with ownership verification.
        Uses primary key index for fast lookup.
        """
        from db.postgres import Term

        with QueryProfiler(f"get_term_by_id_for_user[{term_id}]"):
            # Uses: Primary key index on id + ix_terms_created_by
            return db.query(Term).filter(
                Term.id == term_id,
                Term.created_by == user_id
            ).first()

    @staticmethod
    def check_term_exists_for_user(db: Session, term_name: str, user_id: str) -> bool:
        """
        Lightweight check for term existence.
        Uses composite index (name, created_by).
        """
        from db.postgres import Term

        with QueryProfiler(f"check_term_exists[{term_name}]"):
            # Uses index: ix_terms_name_created_by
            # Returns 1 or 0 instead of full object for efficiency
            exists = db.query(
                db.func.count(Term.id)
            ).filter(
                Term.name == term_name,
                Term.created_by == user_id
            ).scalar()
            return exists > 0

    @staticmethod
    def get_user_api_keys(db: Session, user_id: str) -> List[Any]:
        """
        Get all API keys for a user.
        Uses index on user_id.
        """
        from db.postgres import ApiKey

        with QueryProfiler(f"get_user_api_keys[{user_id}]"):
            # Uses index: ix_api_keys_user_id
            return db.query(ApiKey).filter(
                ApiKey.user_id == user_id,
                ApiKey.is_active == True
            ).order_by(ApiKey.created_at.desc()).all()

    @staticmethod
    def get_user_oauth_accounts(db: Session, user_id: str) -> List[Any]:
        """
        Get all OAuth accounts linked to a user.
        Uses index on user_id.
        """
        from db.postgres import OAuthAccount

        with QueryProfiler(f"get_user_oauth_accounts[{user_id}]"):
            # Uses index: ix_oauth_accounts_user_id
            return db.query(OAuthAccount).filter(
                OAuthAccount.user_id == user_id
            ).all()

    @staticmethod
    def get_oauth_account_by_provider(
        db: Session, provider: str, provider_user_id: str
    ) -> Optional[Any]:
        """
        Get OAuth account by provider and provider_user_id.
        Uses composite index (provider, provider_user_id).
        """
        from db.postgres import OAuthAccount

        with QueryProfiler(f"get_oauth_account_by_provider[{provider}]"):
            # Uses index: ix_oauth_accounts_provider_user_id
            return db.query(OAuthAccount).filter(
                OAuthAccount.provider == provider,
                OAuthAccount.provider_user_id == provider_user_id
            ).first()

    @staticmethod
    def get_user_projects(db: Session, user_id: str) -> List[Any]:
        """
        Get all projects owned by a user.
        Uses index on owner_id.
        """
        from db.postgres import Project

        with QueryProfiler(f"get_user_projects[{user_id}]"):
            # Uses index: ix_projects_owner_id
            return db.query(Project).filter(
                Project.owner_id == user_id
            ).order_by(Project.created_at.desc()).all()

    @staticmethod
    def get_project_terms(db: Session, project_id: str) -> List[Any]:
        """
        Get all terms in a project.
        Uses index on project_id.
        """
        from db.postgres import Term

        with QueryProfiler(f"get_project_terms[{project_id}]"):
            # Uses index: ix_terms_project_id
            return db.query(Term).filter(
                Term.project_id == project_id
            ).order_by(Term.created_at.desc()).all()


# Query profiling middleware - logs all database queries for analysis
class QueryLoggingConfig:
    """Configuration for query logging."""

    SLOW_QUERY_THRESHOLD_MS = 100  # Warn on queries slower than 100ms
    LOG_LEVEL = logging.DEBUG
    ENABLE_SQL_LOGGING = False  # Set to True to log actual SQL statements


def enable_query_logging(engine):
    """
    Enable detailed SQL query logging on SQLAlchemy engine.
    Use in development to detect N+1 queries and slow queries.
    """
    if QueryLoggingConfig.ENABLE_SQL_LOGGING:
        import logging
        logging.basicConfig()
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
        logger.info("SQL query logging enabled")


# Anti-patterns to avoid (documented here for reference)
"""
⚠️ ANTI-PATTERNS TO AVOID:

1. N+1 QUERIES (Very Common)
   ❌ Bad:
        user = db.query(User).first()
        for term in user.created_terms:  # ← Triggers query per term
            print(term.name)

   ✅ Good:
        user = db.query(User).options(
            selectinload(User.created_terms)
        ).first()
        for term in user.created_terms:  # ← Already loaded
            print(term.name)

2. UNBOUNDED QUERIES (Memory issues)
   ❌ Bad:
        all_terms = db.query(Term).all()  # Could load millions!

   ✅ Good:
        paginated = db.query(Term).limit(100).offset(0).all()

3. MISSING INDEXES (Slow queries)
   ❌ Bad:
        db.query(Term).filter(Term.created_by == user_id).all()
        # Without index on created_by

   ✅ Good:
        # With ix_terms_created_by index created by migration

4. INEFFICIENT EXISTENCE CHECKS
   ❌ Bad:
        term = db.query(Term).filter(...).first()
        if term:
            # Loads full object

   ✅ Good:
        exists = db.query(db.func.count(Term.id)).filter(...).scalar() > 0

5. SELECTING COLUMNS NOT NEEDED
   ❌ Bad:
        users = db.query(User).all()  # Loads all columns

   ✅ Good:
        users = db.query(User.id, User.email).all()  # Only needed columns
"""
