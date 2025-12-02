# API Specifications - Sprint 1

**Version**: 1.0.0
**Date**: 2025-11-14
**Tech Stack**: FastAPI (Python), PostgreSQL, Neo4j
**Target Audience**: Backend Developers

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Authentication & Authorization](#authentication--authorization)
3. [Common Patterns](#common-patterns)
4. [Endpoints by Feature](#endpoints-by-feature)
5. [Data Models](#data-models)
6. [Error Handling](#error-handling)
7. [Rate Limiting](#rate-limiting)
8. [Testing](#testing)

---

## Overview

### Scope

This document covers the **minimum backend API** required for **Sprint 1** (Weeks 1-2):

- **US-001**: Onboarding - Adoption Level Selection
- **US-002**: Quick Draft - Term Creation
- **US-003**: Onboarding - Profile Setup

### Technology Stack

```yaml
framework: FastAPI 0.104+
database:
  relational: PostgreSQL 15+
  graph: Neo4j 5+
orm: SQLAlchemy 2.0
validation: Pydantic v2
auth: JWT (future: OAuth2)
file_storage: Local filesystem (future: S3/R2)
```

### Base URL

```
Development: http://localhost:8000/api
Production: https://api.lexikon.app/api
```

### API Versioning

```
Current: /api/v1/{resource}
Future: /api/v2/{resource}
```

---

## Authentication & Authorization

### Current State (Sprint 1)

For Sprint 1, authentication is **simplified**:
- No login required for onboarding flow
- User created on profile submission (US-003)
- Session stored in cookie/localStorage

### Future State (Sprint 2+)

```yaml
auth_methods:
  - email_password
  - google_oauth
  - github_oauth

token_type: JWT
token_expiry: 7 days
refresh_token: 30 days
```

### Headers

**Required for authenticated requests**:
```http
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Optional**:
```http
X-Request-ID: {uuid}  # For request tracing
Accept-Language: fr   # For i18n
```

---

## Common Patterns

### Request Format

```json
{
  "data": { /* request payload */ },
  "metadata": {
    "requestId": "uuid",
    "timestamp": "2025-11-14T10:00:00Z"
  }
}
```

### Response Format

**Success (200-299)**:
```json
{
  "success": true,
  "data": { /* response payload */ },
  "metadata": {
    "requestId": "uuid",
    "timestamp": "2025-11-14T10:00:01Z",
    "version": "1.0.0"
  }
}
```

**Error (400-599)**:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {
      "email": ["Invalid email format"],
      "firstName": ["Minimum 2 characters required"]
    }
  },
  "metadata": {
    "requestId": "uuid",
    "timestamp": "2025-11-14T10:00:01Z"
  }
}
```

### Pagination

```http
GET /api/terms?page=1&limit=20&sort=createdAt&order=desc
```

**Response**:
```json
{
  "data": [ /* items */ ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "totalPages": 8,
    "hasNext": true,
    "hasPrev": false
  }
}
```

---

## Endpoints by Feature

### 1. Onboarding - Adoption Level (US-001)

#### POST `/api/onboarding/adoption-level`

**Description**: Save the user's selected adoption level during onboarding.

**Request**:
```http
POST /api/onboarding/adoption-level
Content-Type: application/json

{
  "adoptionLevel": "quick-project",
  "sessionId": "temp-session-uuid"
}
```

**Request Body Schema**:
```typescript
{
  adoptionLevel: "quick-project" | "research-project" | "production-api";
  sessionId: string;  // Temporary session ID (before user creation)
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "adoptionLevel": "quick-project",
    "sessionId": "temp-session-uuid",
    "nextStep": "/onboarding/profile",
    "recommendedTier": "free",
    "features": [
      "Setup en 30 minutes",
      "Export quand terminé",
      "Gratuit, pas de validation obligatoire"
    ]
  }
}
```

**Validation Rules**:
- `adoptionLevel` must be one of: `quick-project`, `research-project`, `production-api`
- `sessionId` must be a valid UUID

**Database**:
```sql
-- Temporary session storage (Redis or PostgreSQL)
CREATE TABLE onboarding_sessions (
  session_id UUID PRIMARY KEY,
  adoption_level VARCHAR(50) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  expires_at TIMESTAMP DEFAULT NOW() + INTERVAL '1 hour'
);
```

**Implementation Notes**:
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from enum import Enum

class AdoptionLevel(str, Enum):
    QUICK_PROJECT = "quick-project"
    RESEARCH_PROJECT = "research-project"
    PRODUCTION_API = "production-api"

class AdoptionLevelRequest(BaseModel):
    adoptionLevel: AdoptionLevel
    sessionId: str = Field(..., pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')

router = APIRouter(prefix="/api/onboarding")

@router.post("/adoption-level")
async def save_adoption_level(request: AdoptionLevelRequest):
    # Save to Redis/PostgreSQL with TTL
    # Return next step
    pass
```

---

### 2. User Profile Setup (US-003)

#### POST `/api/users/profile`

**Description**: Create or update user profile during onboarding.

**Request**:
```http
POST /api/users/profile
Content-Type: application/json

{
  "firstName": "Marie",
  "lastName": "Dupont",
  "email": "marie.dupont@universite.fr",
  "institution": "Université Paris-Sorbonne",
  "primaryDomain": "philosophie",
  "language": "fr",
  "country": "FR",
  "sessionId": "temp-session-uuid"
}
```

**Request Body Schema**:
```typescript
{
  // Required
  firstName: string;      // Min 2, max 100 chars
  lastName: string;       // Min 2, max 100 chars
  email: string;          // Valid email format

  // Optional
  avatar?: string;        // Base64 data URI (max 2MB)
  institution?: string;   // Max 200 chars
  primaryDomain?: string; // Enum: see list below
  language: string;       // Default "fr", options: fr, en, es, de, it
  country?: string;       // ISO 3166-1 alpha-2

  // From onboarding flow
  sessionId: string;      // Links to adoption level
}
```

**primaryDomain Options**:
```typescript
type PrimaryDomain =
  | "philosophie"
  | "sciences-education"
  | "sociologie"
  | "psychologie"
  | "linguistique"
  | "histoire"
  | "informatique"
  | "data-science"
  | "autre";
```

**Response** (201 Created):
```json
{
  "success": true,
  "data": {
    "id": "user-550e8400-e29b-41d4-a716-446655440000",
    "firstName": "Marie",
    "lastName": "Dupont",
    "email": "marie.dupont@universite.fr",
    "avatar": null,
    "institution": "Université Paris-Sorbonne",
    "primaryDomain": "philosophie",
    "language": "fr",
    "country": "FR",
    "adoptionLevel": "quick-project",
    "createdAt": "2025-11-14T11:00:00Z",
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "nextStep": "/onboarding/preferences"
  }
}
```

**Validation Rules**:
- `firstName`: 2-100 chars, letters + spaces + hyphens + accents (regex: `^[a-zA-ZÀ-ÿ\s\-]{2,100}$`)
- `lastName`: same as firstName
- `email`: valid email format, unique in database
- `avatar`: if provided, must be valid base64 data URI, max decoded size 2MB
- `institution`: max 200 chars
- `primaryDomain`: must be from predefined enum
- `language`: must be one of: fr, en, es, de, it
- `country`: must be valid ISO 3166-1 alpha-2 code

**Error Response** (400 Bad Request):
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {
      "email": ["Email already exists"],
      "firstName": ["Minimum 2 characters required"]
    }
  }
}
```

**Error Response** (409 Conflict):
```json
{
  "success": false,
  "error": {
    "code": "EMAIL_EXISTS",
    "message": "Cette adresse email est déjà utilisée",
    "details": {
      "email": "marie.dupont@universite.fr"
    }
  }
}
```

**Database Schema**:
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  first_name VARCHAR(100) NOT NULL,
  last_name VARCHAR(100) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  avatar_url TEXT,
  institution VARCHAR(200),
  primary_domain VARCHAR(50),
  language VARCHAR(5) DEFAULT 'fr',
  country VARCHAR(2),
  adoption_level VARCHAR(50) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  deleted_at TIMESTAMP NULL
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_adoption_level ON users(adoption_level);
```

**Implementation Notes**:
```python
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
import re

class UserProfileRequest(BaseModel):
    firstName: str = Field(..., min_length=2, max_length=100)
    lastName: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    avatar: Optional[str] = None
    institution: Optional[str] = Field(None, max_length=200)
    primaryDomain: Optional[str] = None
    language: str = Field(default="fr", pattern="^(fr|en|es|de|it)$")
    country: Optional[str] = Field(None, pattern="^[A-Z]{2}$")
    sessionId: str

    @validator('firstName', 'lastName')
    def validate_name(cls, v):
        if not re.match(r'^[a-zA-ZÀ-ÿ\s\-]{2,100}$', v):
            raise ValueError('Invalid name format')
        return v

    @validator('avatar')
    def validate_avatar(cls, v):
        if v:
            # Decode base64 and check size
            # Check if valid image format
            pass
        return v

@router.post("/users/profile", status_code=201)
async def create_user_profile(request: UserProfileRequest, db: Session):
    # Check email uniqueness
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already exists")

    # Get adoption level from session
    session_data = get_onboarding_session(request.sessionId)

    # Create user
    user = User(
        first_name=request.firstName,
        last_name=request.lastName,
        email=request.email,
        # ... other fields
        adoption_level=session_data.adoptionLevel
    )
    db.add(user)
    db.commit()

    # Generate JWT token
    access_token = create_access_token(user.id)

    return {
        "success": True,
        "data": {
            "id": str(user.id),
            # ... user fields
            "accessToken": access_token,
            "nextStep": "/onboarding/preferences"
        }
    }
```

---

#### POST `/api/users/avatar`

**Description**: Upload avatar image as multipart/form-data (alternative to base64).

**Request**:
```http
POST /api/users/avatar
Content-Type: multipart/form-data

avatar: File (image/jpeg, image/png, image/gif)
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "avatarUrl": "https://cdn.lexikon.app/avatars/user-550e8400.jpg",
    "size": 245678,
    "format": "jpeg"
  }
}
```

**Validation**:
- Max file size: 2MB
- Allowed formats: JPEG, PNG, GIF
- Image dimensions: Min 100x100, max 2000x2000
- Virus scan before storage

**Implementation Notes**:
```python
from fastapi import File, UploadFile
from PIL import Image
import io

@router.post("/users/avatar")
async def upload_avatar(avatar: UploadFile = File(...)):
    # Validate file size
    contents = await avatar.read()
    if len(contents) > 2 * 1024 * 1024:  # 2MB
        raise HTTPException(400, "File too large")

    # Validate image format
    try:
        image = Image.open(io.BytesIO(contents))
        image.verify()
    except:
        raise HTTPException(400, "Invalid image format")

    # Save to storage (local or S3)
    filename = f"avatars/{uuid4()}.jpg"
    # ... save logic

    return {
        "success": True,
        "data": {
            "avatarUrl": f"https://cdn.lexikon.app/{filename}",
            "size": len(contents),
            "format": image.format.lower()
        }
    }
```

---

### 3. Term Creation (US-002)

#### POST `/api/terms`

**Description**: Create a new term in Quick Draft mode.

**Request**:
```http
POST /api/terms
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Épistémologie",
  "definition": "Étude critique des sciences, destinée à déterminer leur origine logique, leur valeur et leur portée.",
  "domain": "Philosophie",
  "level": "quick-draft",
  "status": "draft"
}
```

**Request Body Schema**:
```typescript
{
  name: string;          // Required, 3-100 chars, unique per user
  definition: string;    // Required, 50-500 chars
  domain?: string;       // Optional, max 100 chars
  level: "quick-draft" | "ready" | "expert";  // Default: "quick-draft"
  status: "draft" | "ready" | "validated";    // Default: "draft"
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "data": {
    "id": "term-7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "name": "Épistémologie",
    "definition": "Étude critique des sciences, destinée à déterminer leur origine logique, leur valeur et leur portée.",
    "domain": "Philosophie",
    "level": "quick-draft",
    "status": "draft",
    "createdBy": "user-550e8400-e29b-41d4-a716-446655440000",
    "createdAt": "2025-11-14T11:30:00Z",
    "updatedAt": "2025-11-14T11:30:00Z",
    "nextSteps": {
      "addRelations": "/terms/term-7c9e6679/relations",
      "upgradeLevel": "/terms/term-7c9e6679/edit?mode=ready",
      "view": "/terms/term-7c9e6679"
    }
  }
}
```

**Validation Rules**:
- `name`: 3-100 chars, must be unique per user (case-insensitive)
- `definition`: 50-500 chars
- `domain`: optional, max 100 chars
- `level`: must be one of: quick-draft, ready, expert
- `status`: must be one of: draft, ready, validated

**Error Response** (400 Bad Request):
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {
      "name": ["Minimum 3 characters required"],
      "definition": ["Minimum 50 characters required"]
    }
  }
}
```

**Error Response** (409 Conflict):
```json
{
  "success": false,
  "error": {
    "code": "TERM_EXISTS",
    "message": "Un terme avec ce nom existe déjà dans votre ontologie",
    "details": {
      "name": "Épistémologie",
      "existingTermId": "term-abc123"
    }
  }
}
```

**Database Schema**:
```sql
CREATE TABLE terms (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL,
  definition TEXT NOT NULL CHECK (char_length(definition) >= 50 AND char_length(definition) <= 500),
  domain VARCHAR(100),
  level VARCHAR(20) NOT NULL DEFAULT 'quick-draft',
  status VARCHAR(20) NOT NULL DEFAULT 'draft',
  created_by UUID NOT NULL REFERENCES users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  deleted_at TIMESTAMP NULL,

  UNIQUE(created_by, LOWER(name))  -- Unique name per user
);

CREATE INDEX idx_terms_created_by ON terms(created_by);
CREATE INDEX idx_terms_status ON terms(status);
CREATE INDEX idx_terms_level ON terms(level);
```

**Neo4j Graph Node**:
```cypher
// Create term node
CREATE (t:Term {
  id: 'term-7c9e6679',
  name: 'Épistémologie',
  definition: '...',
  domain: 'Philosophie',
  level: 'quick-draft',
  status: 'draft',
  createdBy: 'user-550e8400',
  createdAt: datetime()
})
RETURN t
```

**Implementation Notes**:
```python
from pydantic import BaseModel, Field, validator

class TermLevel(str, Enum):
    QUICK_DRAFT = "quick-draft"
    READY = "ready"
    EXPERT = "expert"

class TermStatus(str, Enum):
    DRAFT = "draft"
    READY = "ready"
    VALIDATED = "validated"

class CreateTermRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    definition: str = Field(..., min_length=50, max_length=500)
    domain: Optional[str] = Field(None, max_length=100)
    level: TermLevel = TermLevel.QUICK_DRAFT
    status: TermStatus = TermStatus.DRAFT

    @validator('name')
    def validate_name(cls, v):
        # No leading/trailing spaces
        v = v.strip()
        # No special chars except accents, hyphens, spaces
        if not re.match(r'^[a-zA-ZÀ-ÿ0-9\s\-]+$', v):
            raise ValueError('Invalid characters in name')
        return v

@router.post("/terms", status_code=201)
async def create_term(
    request: CreateTermRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    neo4j: Neo4jDriver = Depends(get_neo4j)
):
    # Check duplicate name
    existing = db.query(Term).filter(
        Term.created_by == current_user.id,
        func.lower(Term.name) == request.name.lower()
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "TERM_EXISTS",
                "message": "Un terme avec ce nom existe déjà",
                "details": {"name": request.name, "existingTermId": str(existing.id)}
            }
        )

    # Create in PostgreSQL
    term = Term(
        name=request.name,
        definition=request.definition,
        domain=request.domain,
        level=request.level,
        status=request.status,
        created_by=current_user.id
    )
    db.add(term)
    db.commit()
    db.refresh(term)

    # Create in Neo4j
    with neo4j.session() as session:
        session.run("""
            CREATE (t:Term {
                id: $id,
                name: $name,
                definition: $definition,
                domain: $domain,
                level: $level,
                status: $status,
                createdBy: $createdBy,
                createdAt: datetime()
            })
        """, {
            "id": str(term.id),
            "name": term.name,
            "definition": term.definition,
            "domain": term.domain,
            "level": term.level,
            "status": term.status,
            "createdBy": str(current_user.id)
        })

    return {
        "success": True,
        "data": {
            "id": str(term.id),
            # ... term fields
            "nextSteps": {
                "addRelations": f"/terms/{term.id}/relations",
                "upgradeLevel": f"/terms/{term.id}/edit?mode=ready",
                "view": f"/terms/{term.id}"
            }
        }
    }
```

---

#### GET `/api/terms`

**Description**: List all terms for the current user.

**Request**:
```http
GET /api/terms?page=1&limit=20&status=draft&sort=createdAt&order=desc
Authorization: Bearer {token}
```

**Query Parameters**:
- `page` (int, default: 1): Page number
- `limit` (int, default: 20, max: 100): Items per page
- `status` (string, optional): Filter by status (draft, ready, validated)
- `level` (string, optional): Filter by level (quick-draft, ready, expert)
- `domain` (string, optional): Filter by domain
- `search` (string, optional): Search in name and definition
- `sort` (string, default: createdAt): Sort field
- `order` (string, default: desc): Sort order (asc, desc)

**Response** (200 OK):
```json
{
  "success": true,
  "data": [
    {
      "id": "term-7c9e6679",
      "name": "Épistémologie",
      "definition": "Étude critique des sciences...",
      "domain": "Philosophie",
      "level": "quick-draft",
      "status": "draft",
      "createdAt": "2025-11-14T11:30:00Z",
      "updatedAt": "2025-11-14T11:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45,
    "totalPages": 3,
    "hasNext": true,
    "hasPrev": false
  }
}
```

---

#### POST `/api/drafts` (Auto-Save Endpoint)

**Description**: Save form draft (for auto-save functionality).

**Request**:
```http
POST /api/drafts
Authorization: Bearer {token}
Content-Type: application/json

{
  "draftType": "term",
  "data": {
    "name": "Épist",
    "definition": "Étude...",
    "domain": ""
  }
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "draftId": "draft-abc123",
    "savedAt": "2025-11-14T11:29:45Z",
    "ttl": 604800
  }
}
```

**Database**:
```sql
-- Use Redis for ephemeral draft storage
-- Key: draft:{userId}:{draftType}
-- TTL: 7 days
```

---

## Data Models

### User

```typescript
interface User {
  id: UUID;
  firstName: string;
  lastName: string;
  email: string;
  avatar?: string;
  institution?: string;
  primaryDomain?: string;
  language: string;
  country?: string;
  adoptionLevel: "quick-project" | "research-project" | "production-api";
  createdAt: DateTime;
  updatedAt: DateTime;
  deletedAt?: DateTime;
}
```

### Term

```typescript
interface Term {
  id: UUID;
  name: string;
  definition: string;
  domain?: string;
  level: "quick-draft" | "ready" | "expert";
  status: "draft" | "ready" | "validated";
  createdBy: UUID;  // User ID
  createdAt: DateTime;
  updatedAt: DateTime;
  deletedAt?: DateTime;

  // Relations (added in Sprint 2)
  relations?: Relation[];
  examples?: Example[];
  synonyms?: string[];
}
```

### OnboardingSession (Temporary)

```typescript
interface OnboardingSession {
  sessionId: UUID;
  adoptionLevel: "quick-project" | "research-project" | "production-api";
  createdAt: DateTime;
  expiresAt: DateTime;  // 1 hour from creation
}
```

---

## Error Handling

### Error Codes

```typescript
enum ErrorCode {
  // Validation (400)
  VALIDATION_ERROR = "VALIDATION_ERROR",
  INVALID_INPUT = "INVALID_INPUT",

  // Authentication (401)
  UNAUTHORIZED = "UNAUTHORIZED",
  INVALID_TOKEN = "INVALID_TOKEN",
  TOKEN_EXPIRED = "TOKEN_EXPIRED",

  // Authorization (403)
  FORBIDDEN = "FORBIDDEN",
  INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS",

  // Not Found (404)
  NOT_FOUND = "NOT_FOUND",
  USER_NOT_FOUND = "USER_NOT_FOUND",
  TERM_NOT_FOUND = "TERM_NOT_FOUND",

  // Conflict (409)
  EMAIL_EXISTS = "EMAIL_EXISTS",
  TERM_EXISTS = "TERM_EXISTS",

  // Rate Limiting (429)
  RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED",

  // Server Error (500)
  INTERNAL_ERROR = "INTERNAL_ERROR",
  DATABASE_ERROR = "DATABASE_ERROR",
}
```

### HTTP Status Codes

```yaml
200: OK - Request successful
201: Created - Resource created
204: No Content - Successful deletion
400: Bad Request - Validation error
401: Unauthorized - Authentication required
403: Forbidden - Insufficient permissions
404: Not Found - Resource not found
409: Conflict - Resource already exists
422: Unprocessable Entity - Semantic error
429: Too Many Requests - Rate limit exceeded
500: Internal Server Error - Unexpected error
503: Service Unavailable - Temporary outage
```

---

## Rate Limiting

### Limits by Tier

```yaml
free:
  requests_per_minute: 60
  requests_per_hour: 1000
  requests_per_day: 10000

pro:
  requests_per_minute: 300
  requests_per_hour: 10000
  requests_per_day: 100000

team:
  requests_per_minute: 1000
  requests_per_hour: 50000
  requests_per_day: unlimited
```

### Rate Limit Headers

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1699972800
```

### Rate Limit Exceeded Response

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again in 30 seconds.",
    "details": {
      "limit": 60,
      "remaining": 0,
      "resetAt": "2025-11-14T11:30:00Z"
    }
  }
}
```

---

## Testing

### Unit Tests

```python
# tests/test_users.py
def test_create_user_profile_success():
    # Given: Valid user data
    # When: POST /api/users/profile
    # Then: Returns 201 with user data

def test_create_user_profile_duplicate_email():
    # Given: Email already exists
    # When: POST /api/users/profile
    # Then: Returns 409 with error

def test_create_user_profile_invalid_email():
    # Given: Invalid email format
    # When: POST /api/users/profile
    # Then: Returns 400 with validation error
```

### Integration Tests

```python
# tests/integration/test_onboarding_flow.py
def test_complete_onboarding_flow():
    # Step 1: Save adoption level
    response1 = client.post("/api/onboarding/adoption-level", json={
        "adoptionLevel": "quick-project",
        "sessionId": session_id
    })
    assert response1.status_code == 200

    # Step 2: Create profile
    response2 = client.post("/api/users/profile", json={
        "firstName": "Test",
        "lastName": "User",
        "email": "test@example.com",
        "sessionId": session_id
    })
    assert response2.status_code == 201
    assert "accessToken" in response2.json()["data"]
```

### API Testing Tools

```bash
# Using pytest
pytest tests/ -v

# Using curl
curl -X POST http://localhost:8000/api/users/profile \
  -H "Content-Type: application/json" \
  -d '{"firstName":"Test","lastName":"User","email":"test@example.com"}'

# Using HTTPie
http POST localhost:8000/api/users/profile \
  firstName=Test lastName=User email=test@example.com
```

---

## Next Steps

### Sprint 2 Endpoints (Future)

- **POST `/api/terms/{id}/relations`** - Add relation between terms
- **GET `/api/terms/{id}/suggestions`** - AI relation suggestions
- **POST `/api/llm/configure`** - Configure LLM provider (BYOK)
- **POST `/api/import/csv`** - Import terms from CSV
- **GET `/api/graph/visualize`** - Get graph data for visualization

### Additional Features

- **WebSocket** for real-time collaboration
- **GraphQL** endpoint for complex queries
- **Bulk operations** for batch term creation
- **Export endpoints** (CSV, JSON, RDF)

---

## Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Pydantic v2**: https://docs.pydantic.dev/latest/
- **SQLAlchemy 2.0**: https://docs.sqlalchemy.org/en/20/
- **Neo4j Python Driver**: https://neo4j.com/docs/api/python-driver/current/

---

**Last Updated**: 2025-11-14
**Version**: 1.0.0
**Status**: ✅ Ready for Implementation
