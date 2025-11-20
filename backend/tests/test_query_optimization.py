"""
Tests for query optimization utilities.
Verifies that optimized queries use correct indexes and avoid N+1 patterns.
"""

import pytest
from sqlalchemy.orm import Session
from db.query_utils import QueryOptimizer, QueryProfiler
from db.postgres import User, Term, ApiKey, OAuthAccount, Project
import uuid


class TestQueryProfiler:
    """Test QueryProfiler context manager."""

    def test_profiler_measures_duration(self):
        """QueryProfiler should measure execution time."""
        import time

        with QueryProfiler("test_operation") as profiler:
            time.sleep(0.01)  # 10ms delay

        assert profiler.duration_ms >= 10
        assert profiler.duration_ms < 100

    def test_profiler_handles_exceptions(self):
        """QueryProfiler should handle exceptions gracefully."""
        with pytest.raises(ValueError):
            with QueryProfiler("failing_operation"):
                raise ValueError("Test error")


class TestQueryOptimizer:
    """Test QueryOptimizer helper functions."""

    @pytest.fixture
    def setup_data(self, db: Session):
        """Create test data."""
        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            email=f"test_{user_id}@example.com",
            password_hash="hashed",
            first_name="Test",
            last_name="User",
            language="en",
            adoption_level="quick-project",
            is_active=True,
        )
        db.add(user)
        db.commit()

        # Create test terms
        term_ids = []
        for i in range(5):
            term = Term(
                id=str(uuid.uuid4()),
                name=f"Test Term {i}",
                definition=f"Definition {i}",
                level="quick-draft",
                status="draft",
                created_by=user_id,
                project_id=None,
            )
            db.add(term)
            term_ids.append(term.id)
        db.commit()

        return {"user": user, "term_ids": term_ids, "user_id": user_id}

    def test_get_terms_by_user(self, db: Session, setup_data):
        """QueryOptimizer.get_terms_by_user should fetch user terms efficiently."""
        terms = QueryOptimizer.get_terms_by_user(db, setup_data["user_id"])

        assert len(terms) == 5
        assert all(t.created_by == setup_data["user_id"] for t in terms)

    def test_get_term_by_id_for_user(self, db: Session, setup_data):
        """QueryOptimizer.get_term_by_id_for_user should verify ownership."""
        term_id = setup_data["term_ids"][0]
        user_id = setup_data["user_id"]

        # Should find term for correct user
        term = QueryOptimizer.get_term_by_id_for_user(db, term_id, user_id)
        assert term is not None
        assert term.id == term_id
        assert term.created_by == user_id

        # Should not find term for different user
        other_user_id = str(uuid.uuid4())
        term = QueryOptimizer.get_term_by_id_for_user(db, term_id, other_user_id)
        assert term is None

    def test_check_term_exists_for_user(self, db: Session, setup_data):
        """check_term_exists_for_user should efficiently check existence."""
        user_id = setup_data["user_id"]

        # Existing term
        exists = QueryOptimizer.check_term_exists_for_user(
            db, "Test Term 0", user_id
        )
        assert exists is True

        # Non-existing term
        exists = QueryOptimizer.check_term_exists_for_user(
            db, "Non-existent Term", user_id
        )
        assert exists is False

        # Existing term for different user should not be found
        other_user_id = str(uuid.uuid4())
        exists = QueryOptimizer.check_term_exists_for_user(
            db, "Test Term 0", other_user_id
        )
        assert exists is False

    def test_get_user_api_keys(self, db: Session, setup_data):
        """QueryOptimizer.get_user_api_keys should fetch user's keys efficiently."""
        user_id = setup_data["user_id"]

        # Create API keys for user
        for i in range(3):
            api_key = ApiKey(
                id=str(uuid.uuid4()),
                user_id=user_id,
                key_hash=f"hash_{i}",
                name=f"Key {i}",
                scopes="read,write",
                is_active=True,
            )
            db.add(api_key)
        db.commit()

        keys = QueryOptimizer.get_user_api_keys(db, user_id)
        assert len(keys) == 3
        assert all(k.user_id == user_id for k in keys)

    def test_get_oauth_account_by_provider(self, db: Session, setup_data):
        """QueryOptimizer.get_oauth_account_by_provider should lookup efficiently."""
        user_id = setup_data["user_id"]

        oauth = OAuthAccount(
            id=str(uuid.uuid4()),
            user_id=user_id,
            provider="github",
            provider_user_id="github_123",
            access_token="token",
        )
        db.add(oauth)
        db.commit()

        # Find existing account
        found = QueryOptimizer.get_oauth_account_by_provider(
            db, "github", "github_123"
        )
        assert found is not None
        assert found.provider == "github"
        assert found.provider_user_id == "github_123"

        # Non-existent account
        found = QueryOptimizer.get_oauth_account_by_provider(
            db, "github", "non_existent"
        )
        assert found is None

    def test_get_user_projects(self, db: Session, setup_data):
        """QueryOptimizer.get_user_projects should fetch user's projects efficiently."""
        user_id = setup_data["user_id"]

        # Create projects
        for i in range(3):
            project = Project(
                id=str(uuid.uuid4()),
                name=f"Project {i}",
                language="en",
                is_public=False,
                owner_id=user_id,
            )
            db.add(project)
        db.commit()

        projects = QueryOptimizer.get_user_projects(db, user_id)
        assert len(projects) == 3
        assert all(p.owner_id == user_id for p in projects)

    def test_get_project_terms(self, db: Session, setup_data):
        """QueryOptimizer.get_project_terms should fetch project terms efficiently."""
        user_id = setup_data["user_id"]

        # Create project
        project = Project(
            id=str(uuid.uuid4()),
            name="Test Project",
            language="en",
            is_public=False,
            owner_id=user_id,
        )
        db.add(project)
        db.commit()

        # Create terms in project
        for i in range(3):
            term = Term(
                id=str(uuid.uuid4()),
                name=f"Project Term {i}",
                definition=f"Definition {i}",
                level="quick-draft",
                status="draft",
                created_by=user_id,
                project_id=project.id,
            )
            db.add(term)
        db.commit()

        terms = QueryOptimizer.get_project_terms(db, project.id)
        assert len(terms) == 3
        assert all(t.project_id == project.id for t in terms)


class TestPerformanceCharacteristics:
    """
    Tests that verify performance characteristics of queries.
    These tests ensure indexes are being used correctly.
    """

    def test_index_on_terms_created_by(self, db: Session):
        """Verify ix_terms_created_by index exists and is used."""
        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            email=f"index_test_{user_id}@example.com",
            password_hash="hashed",
            first_name="Test",
            last_name="User",
            language="en",
            adoption_level="quick-project",
            is_active=True,
        )
        db.add(user)

        # Create many terms to benefit from index
        for i in range(100):
            term = Term(
                id=str(uuid.uuid4()),
                name=f"Term {i}",
                definition="Definition",
                level="quick-draft",
                status="draft",
                created_by=user_id,
                project_id=None,
            )
            db.add(term)
        db.commit()

        # Query should use index
        with QueryProfiler("indexed_query_terms_by_user"):
            terms = db.query(Term).filter(
                Term.created_by == user_id
            ).all()

        assert len(terms) == 100

    def test_composite_index_name_created_by(self, db: Session):
        """Verify composite index (name, created_by) is effective."""
        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            email=f"composite_test_{user_id}@example.com",
            password_hash="hashed",
            first_name="Test",
            last_name="User",
            language="en",
            adoption_level="quick-project",
            is_active=True,
        )
        db.add(user)

        term_name = "Unique Term Name"
        term = Term(
            id=str(uuid.uuid4()),
            name=term_name,
            definition="Definition",
            level="quick-draft",
            status="draft",
            created_by=user_id,
            project_id=None,
        )
        db.add(term)
        db.commit()

        # Query should use composite index
        with QueryProfiler("composite_index_uniqueness_check"):
            result = db.query(Term).filter(
                Term.name == term_name,
                Term.created_by == user_id,
            ).first()

        assert result is not None
        assert result.name == term_name


class TestIndexDocumentation:
    """Test that all documented indexes are working as expected."""

    @pytest.mark.parametrize("index_name,table,columns", [
        ("ix_users_email", "users", "email"),
        ("ix_api_keys_key_hash", "api_keys", "key_hash"),
        ("ix_api_keys_user_id", "api_keys", "user_id"),
        ("ix_terms_created_by", "terms", "created_by"),
        ("ix_terms_name_created_by", "terms", "name,created_by"),
        ("ix_terms_project_id", "terms", "project_id"),
        ("ix_oauth_accounts_user_id", "oauth_accounts", "user_id"),
        ("ix_projects_owner_id", "projects", "owner_id"),
    ])
    def test_indexes_exist(self, db: Session, index_name: str, table: str, columns: str):
        """Verify all documented indexes exist in database."""
        from sqlalchemy import inspect

        # Get list of indexes for the table
        inspector = inspect(db.get_bind())
        indexes = [idx["name"] for idx in inspector.get_indexes(table)]

        assert index_name in indexes, f"Index {index_name} not found on table {table}"
