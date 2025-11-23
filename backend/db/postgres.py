"""
PostgreSQL database models and connection using SQLAlchemy.
"""

from sqlalchemy import (
    create_engine,
    Column,
    String,
    Text,
    DateTime,
    ForeignKey,
    Table,
    Boolean,
    Integer,
    Enum as SQLEnum,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime
import os
import enum

# Database URL from environment
# Use SQLite for development, PostgreSQL for production
DATABASE_URL = os.getenv(
    "DATABASE_URL", "sqlite:///./lexikon.db"
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Enums
class AdoptionLevelEnum(str, enum.Enum):
    QUICK_PROJECT = "quick-project"
    RESEARCH_PROJECT = "research-project"
    PRODUCTION_API = "production-api"


class TermLevelEnum(str, enum.Enum):
    QUICK_DRAFT = "quick-draft"
    READY = "ready"
    EXPERT = "expert"


class TermStatusEnum(str, enum.Enum):
    DRAFT = "draft"
    READY = "ready"
    VALIDATED = "validated"


class ProjectRoleEnum(str, enum.Enum):
    OWNER = "owner"
    EDITOR = "editor"
    REVIEWER = "reviewer"
    VIEWER = "viewer"


# Association table for project members
project_members = Table(
    "project_members",
    Base.metadata,
    Column("project_id", String, ForeignKey("projects.id"), primary_key=True),
    Column("user_id", String, ForeignKey("users.id"), primary_key=True),
    Column("role", SQLEnum(ProjectRoleEnum), nullable=False, default=ProjectRoleEnum.VIEWER),
    Column("joined_at", DateTime, server_default=func.now()),
)


# Models
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=True)  # Nullable for OAuth-only users
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    institution = Column(String, nullable=True)
    primary_domain = Column(String, nullable=True)
    language = Column(String, nullable=False, default="fr")
    country = Column(String(2), nullable=True)
    adoption_level = Column(
        SQLEnum(AdoptionLevelEnum),
        nullable=False,
        default=AdoptionLevelEnum.QUICK_PROJECT,
    )
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    oauth_accounts = relationship("OAuthAccount", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("ApiKey", back_populates="user", cascade="all, delete-orphan")
    owned_projects = relationship("Project", back_populates="owner", foreign_keys="Project.owner_id")
    project_memberships = relationship("Project", secondary=project_members, back_populates="members")
    created_terms = relationship("Term", back_populates="creator")


class OAuthAccount(Base):
    __tablename__ = "oauth_accounts"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    provider = Column(String, nullable=False)  # google, github
    provider_user_id = Column(String, nullable=False)
    access_token = Column(String, nullable=True)
    refresh_token = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="oauth_accounts")


class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    key_hash = Column(String, nullable=False, unique=True, index=True)
    name = Column(String, nullable=False)
    scopes = Column(String, nullable=False, default="read")  # Comma-separated: read,write
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="api_keys")


class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    language = Column(String, nullable=False, default="fr")
    primary_domain = Column(String, nullable=True)
    is_public = Column(Boolean, default=False)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    archived_at = Column(DateTime, nullable=True)

    # Relationships
    owner = relationship("User", back_populates="owned_projects", foreign_keys=[owner_id])
    members = relationship("User", secondary=project_members, back_populates="project_memberships")
    terms = relationship("Term", back_populates="project", cascade="all, delete-orphan")


class Term(Base):
    __tablename__ = "terms"

    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=True)  # TODO: Make non-nullable in future versions
    name = Column(String, nullable=False, index=True)
    definition = Column(Text, nullable=False)
    domain = Column(String, nullable=True)
    level = Column(
        SQLEnum(TermLevelEnum), nullable=False, default=TermLevelEnum.QUICK_DRAFT
    )
    status = Column(SQLEnum(TermStatusEnum), nullable=False, default=TermStatusEnum.DRAFT)

    # Extended fields for Level 2 (Ready) and Level 3 (Expert)
    examples = Column(Text, nullable=True)  # JSON array
    synonyms = Column(Text, nullable=True)  # JSON array
    formal_definition = Column(Text, nullable=True)
    citations = Column(Text, nullable=True)  # JSON array
    term_metadata = Column(Text, nullable=True)  # JSON object

    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="terms")
    creator = relationship("User", back_populates="created_terms")


class OnboardingSession(Base):
    __tablename__ = "onboarding_sessions"

    id = Column(String, primary_key=True)  # session_id
    adoption_level = Column(SQLEnum(AdoptionLevelEnum), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)  # Set when user registers
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)


class LLMConfig(Base):
    """User's LLM configuration for AI features (BYOK - Bring Your Own Key)"""
    __tablename__ = "llm_configs"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True)
    provider = Column(String, nullable=False)  # openai, anthropic, mistral, ollama
    api_key_encrypted = Column(String, nullable=True)  # Encrypted API key
    model_name = Column(String, nullable=True)  # e.g., gpt-4, claude-3-opus
    base_url = Column(String, nullable=True)  # For Ollama or custom endpoints
    max_tokens = Column(Integer, default=1000)
    temperature = Column(Integer, default=70)  # Stored as int (0.7 → 70)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Webhook(Base):
    """Webhook configuration for event delivery."""
    __tablename__ = "webhooks"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    url = Column(String, nullable=False)
    events = Column(String, nullable=False)  # Comma-separated: "term_created,term_updated"
    secret = Column(String, nullable=False)  # HMAC-SHA256 secret for signature
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    max_retries = Column(Integer, default=5)
    retry_delay_seconds = Column(Integer, default=60)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_triggered_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="webhooks")
    deliveries = relationship("WebhookDelivery", back_populates="webhook", cascade="all, delete-orphan")

    def get_event_list(self) -> list:
        """Parse comma-separated events into list."""
        return [e.strip() for e in self.events.split(",")]

    def should_handle_event(self, event_type: str) -> bool:
        """Check if webhook handles this event type."""
        return event_type in self.get_event_list()


class WebhookDelivery(Base):
    """Webhook delivery attempt tracking."""
    __tablename__ = "webhook_deliveries"

    id = Column(String, primary_key=True)
    webhook_id = Column(String, ForeignKey("webhooks.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String, nullable=False)  # e.g., "term_created"
    payload = Column(Text, nullable=False)  # JSON payload
    status = Column(String, nullable=False)  # "pending", "success", "failed"
    response_status = Column(Integer, nullable=True)  # HTTP status code
    response_body = Column(Text, nullable=True)  # Response from webhook
    attempt_count = Column(Integer, default=0)
    max_attempts = Column(Integer, default=5)
    next_retry_at = Column(DateTime, nullable=True)
    last_error = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    delivered_at = Column(DateTime, nullable=True)

    # Relationships
    webhook = relationship("Webhook", back_populates="deliveries")

    def is_successful(self) -> bool:
        """Check if delivery was successful."""
        return self.status == "success"

    def is_failed(self) -> bool:
        """Check if delivery permanently failed."""
        return self.status == "failed"

    def should_retry(self) -> bool:
        """Check if delivery should be retried."""
        return self.status == "pending" and self.attempt_count < self.max_attempts


# Add relationships to User model
User.webhooks = relationship("Webhook", back_populates="user", cascade="all, delete-orphan")


# Database helper functions
def get_db():
    """Dependency for FastAPI routes"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine, checkfirst=True)


def drop_db():
    """Drop all tables (use with caution!)"""
    Base.metadata.drop_all(bind=engine)
