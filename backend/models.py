from pydantic import BaseModel, EmailStr, Field, validator, field_validator
from typing import Optional, Literal, Any
from datetime import datetime
import re
from validators.input_validators import (
    validate_name,
    validate_definition,
    validate_string_input,
    validate_password,
    validate_email_format,
)


# Enums
AdoptionLevel = Literal["quick-project", "research-project", "production-api"]
PrimaryDomain = Literal[
    "philosophie",
    "sciences-education",
    "sociologie",
    "psychologie",
    "linguistique",
    "histoire",
    "informatique",
    "data-science",
    "autre",
]
TermLevel = Literal["quick-draft", "ready", "expert"]
TermStatus = Literal["draft", "ready", "validated"]


# Onboarding Models
class AdoptionLevelRequest(BaseModel):
    adoptionLevel: AdoptionLevel
    sessionId: str = Field(..., pattern=r"^[0-9a-f-]{36}$")


class AdoptionLevelResponse(BaseModel):
    adoptionLevel: AdoptionLevel
    sessionId: str
    nextStep: str
    recommendedTier: str
    features: list[str]


# User Profile Models
class UserProfileRequest(BaseModel):
    firstName: str = Field(..., min_length=2, max_length=100)
    lastName: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    institution: Optional[str] = Field(None, max_length=200)
    primaryDomain: Optional[PrimaryDomain] = None
    language: str = Field(default="fr", pattern="^(fr|en|es|de|it)$")
    country: Optional[str] = Field(None, pattern="^[A-Z]{2}$")
    sessionId: str

    @validator("firstName", "lastName", pre=True)
    def validate_user_name(cls, v):
        """Validate and normalize user names."""
        if not v:
            raise ValueError("Name cannot be empty")
        return validate_name(v, min_length=2, max_length=100)

    @validator("institution", pre=True)
    def validate_institution(cls, v):
        """Validate and sanitize institution name."""
        if v is None:
            return v
        return validate_string_input(v, min_length=1, max_length=200, field_name="Institution")

    @validator("email", pre=True)
    def validate_user_email(cls, v):
        """Validate email format."""
        if not v:
            raise ValueError("Email cannot be empty")
        return validate_email_format(v)


class UserProfileResponse(BaseModel):
    id: str
    firstName: str
    lastName: str
    email: str
    institution: Optional[str] = None
    primaryDomain: Optional[str] = None
    language: str
    country: Optional[str] = None
    adoptionLevel: AdoptionLevel
    createdAt: str
    accessToken: str
    nextStep: str


# Term Models
class CreateTermRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    definition: str = Field(..., min_length=50, max_length=500)
    domain: Optional[str] = Field(None, max_length=100)
    level: TermLevel = "quick-draft"
    status: TermStatus = "draft"

    @validator("name", pre=True)
    def validate_term_name(cls, v):
        """Validate and normalize term name."""
        if not v:
            raise ValueError("Term name cannot be empty")
        return validate_name(v, min_length=3, max_length=100)

    @validator("definition", pre=True)
    def validate_term_definition(cls, v):
        """Validate and sanitize term definition (allow HTML)."""
        if not v:
            raise ValueError("Definition cannot be empty")
        return validate_definition(v, min_length=50, max_length=500)

    @validator("domain", pre=True)
    def validate_term_domain(cls, v):
        """Validate and sanitize domain field."""
        if v is None:
            return v
        return validate_string_input(v, min_length=1, max_length=100, field_name="Domain")


class TermResponse(BaseModel):
    id: str
    name: str
    definition: str
    domain: Optional[str] = None
    level: TermLevel
    status: TermStatus
    createdBy: str
    createdAt: str
    updatedAt: str
    nextSteps: dict[str, str]


# Semantic Search Models
class SearchTermRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    top_k: int = Field(default=5, ge=1, le=50)

    @validator("query", pre=True)
    def validate_search_query(cls, v):
        """Validate and normalize search query."""
        if not v:
            raise ValueError("Search query cannot be empty")
        return validate_string_input(v, min_length=1, max_length=500, field_name="Search query")


class SearchResult(BaseModel):
    term_id: str
    term_name: str
    definition: str
    similarity_score: float = Field(..., ge=0.0, le=1.0)
    domain: Optional[str] = None
    level: TermLevel


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
    total: int
    threshold_used: float
    execution_time_ms: Optional[float] = None


# API Response Wrapper
class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[dict] = None
    metadata: Optional[dict] = None
