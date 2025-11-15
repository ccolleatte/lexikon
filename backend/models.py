from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Literal, Any
from datetime import datetime
import re


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

    @validator("firstName", "lastName")
    def validate_name(cls, v):
        if not re.match(r"^[a-zA-ZÀ-ÿ\s\-]{2,100}$", v):
            raise ValueError("Invalid name format")
        return v


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

    @validator("name")
    def validate_name(cls, v):
        v = v.strip()
        if not re.match(r"^[a-zA-ZÀ-ÿ0-9\s\-]+$", v):
            raise ValueError("Invalid characters in name")
        return v


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


# API Response Wrapper
class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[dict] = None
    metadata: Optional[dict] = None
