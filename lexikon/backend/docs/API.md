# Lexikon API Documentation

**Version:** 0.1.0
**Base URL:** `http://localhost:8000` (development) | `https://api.lexikon.app` (production)
**Content-Type:** `application/json`

## Table of Contents

- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
  - [Auth Endpoints](#auth-endpoints)
  - [Terms Endpoints](#terms-endpoints)
  - [Health Check](#health-check)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Examples](#examples)

## Authentication

The API uses JWT (JSON Web Token) for authentication.

### Token Types

- **Access Token:** Short-lived token (1 hour) for API requests
- **Refresh Token:** Long-lived token for obtaining new access tokens

### Authorization Header

Include the access token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

## API Endpoints

### Auth Endpoints

#### POST /api/auth/register

Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "language": "en"
}
```

**Parameters:**
- `email` (string, required): Valid email address
- `password` (string, required): Strong password
  - Minimum 8 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one digit
  - At least one special character (!@#$%^&*()_+-=[]{}';:",.<>?/)
- `first_name` (string, required): 2-100 characters, letters and diacritics only
- `last_name` (string, required): 2-100 characters, letters and diacritics only
- `language` (string, optional): Default "fr". Options: fr, en, es, de, it

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "language": "en",
      "adoption_level": "quick-project"
    }
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "success": false,
  "error": {
    "code": "EMAIL_EXISTS",
    "message": "This email is already registered",
    "details": {
      "email": "user@example.com"
    },
    "timestamp": "2024-11-19T10:30:00.000Z"
  }
}
```

**Rate Limit:** 5 requests per minute per IP
**Status Codes:**
- `201`: User created successfully
- `400`: Email already exists
- `422`: Validation error
- `429`: Too many requests

---

#### POST /api/auth/login

Authenticate user with email and password.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "language": "en",
      "adoption_level": "quick-project"
    }
  }
}
```

**Error Response (200 OK with failure):**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid email or password",
    "timestamp": "2024-11-19T10:30:00.000Z"
  }
}
```

**Rate Limit:** 5 requests per minute per IP
**Status Codes:**
- `200`: Success or authentication failure (check `success` field)
- `422`: Validation error
- `429`: Too many requests

**Note:** Returns 200 regardless of authentication success/failure to prevent user enumeration.

---

#### POST /api/auth/refresh

Get a new access token using a refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
}
```

**Status Codes:**
- `200`: Token refreshed successfully
- `401`: Invalid or expired refresh token
- `422`: Validation error

---

#### POST /api/auth/logout

Logout the current user (invalidate tokens).

**Headers Required:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "message": "Logged out successfully"
  }
}
```

**Status Codes:**
- `200`: Logout successful
- `401`: Unauthorized

---

#### GET /api/auth/me

Get current authenticated user information.

**Headers Required:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "institution": "University of Example",
    "primary_domain": "informatique",
    "language": "en",
    "country": "FR",
    "adoption_level": "quick-project",
    "is_active": true,
    "created_at": "2024-11-19T10:00:00.000Z"
  }
}
```

**Status Codes:**
- `200`: Success
- `401`: Unauthorized

---

#### POST /api/auth/change-password

Change the current user's password.

**Headers Required:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "current_password": "OldPass123!",
  "new_password": "NewPass456!"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "message": "Password changed successfully"
  }
}
```

**Status Codes:**
- `200`: Success or error (check `success` field)
- `401`: Unauthorized
- `422`: Validation error

---

### Terms Endpoints

#### POST /api/terms (Create Term)

Create a new ontology term.

**Headers Required:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "name": "Machine Learning",
  "definition": "Machine learning is a subset of artificial intelligence that focuses on developing algorithms and statistical models...",
  "domain": "informatique",
  "level": "quick-draft",
  "status": "draft"
}
```

**Parameters:**
- `name` (string, required): 3-100 characters, alphanumeric + diacritics
- `definition` (string, required): 50-500 characters (allows safe HTML)
- `domain` (string, optional): Max 100 characters
- `level` (string, optional): "quick-draft", "ready", "expert" (default: "quick-draft")
- `status` (string, optional): "draft", "ready", "validated" (default: "draft")

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Machine Learning",
    "definition": "Machine learning is a subset...",
    "domain": "informatique",
    "level": "quick-draft",
    "status": "draft",
    "createdBy": "user-id",
    "createdAt": "2024-11-19T10:00:00.000Z",
    "updatedAt": "2024-11-19T10:00:00.000Z",
    "nextSteps": {
      "addRelations": "/terms/550e8400-e29b-41d4-a716-446655440000/relations",
      "upgradeLevel": "/terms/550e8400-e29b-41d4-a716-446655440000/edit?mode=ready",
      "view": "/terms/550e8400-e29b-41d4-a716-446655440000"
    }
  }
}
```

**Status Codes:**
- `201`: Term created
- `400`: Duplicate term name
- `401`: Unauthorized
- `422`: Validation error

---

#### GET /api/terms

List all terms for the current user.

**Headers Required:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Machine Learning",
      "definition": "Machine learning is...",
      "domain": "informatique",
      "level": "quick-draft",
      "status": "draft",
      "createdBy": "user-id",
      "createdAt": "2024-11-19T10:00:00.000Z",
      "updatedAt": "2024-11-19T10:00:00.000Z"
    }
  ],
  "metadata": {
    "total": 1
  }
}
```

**Status Codes:**
- `200`: Success
- `401`: Unauthorized

---

#### GET /api/terms/{term_id}

Get a specific term by ID.

**Headers Required:**
```
Authorization: Bearer <access_token>
```

**Parameters:**
- `term_id` (path parameter): UUID of the term

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Machine Learning",
    "definition": "Machine learning is...",
    "domain": "informatique",
    "level": "quick-draft",
    "status": "draft",
    "createdBy": "user-id",
    "createdAt": "2024-11-19T10:00:00.000Z",
    "updatedAt": "2024-11-19T10:00:00.000Z"
  }
}
```

**Status Codes:**
- `200`: Success
- `401`: Unauthorized
- `404`: Term not found or not authorized

---

#### PUT /api/terms/{term_id}

Update a term.

**Headers Required:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "name": "Machine Learning (Updated)",
  "definition": "Updated definition...",
  "domain": "informatique",
  "level": "ready",
  "status": "ready"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Machine Learning (Updated)",
    "definition": "Updated definition...",
    "domain": "informatique",
    "level": "ready",
    "status": "ready",
    "createdBy": "user-id",
    "createdAt": "2024-11-19T10:00:00.000Z",
    "updatedAt": "2024-11-19T11:00:00.000Z"
  }
}
```

**Status Codes:**
- `200`: Success
- `401`: Unauthorized
- `404`: Term not found or not authorized
- `422`: Validation error

---

#### DELETE /api/terms/{term_id}

Delete a term.

**Headers Required:**
```
Authorization: Bearer <access_token>
```

**Parameters:**
- `term_id` (path parameter): UUID of the term

**Response (204 No Content):**
Empty response body.

**Status Codes:**
- `204`: Successfully deleted
- `401`: Unauthorized
- `404`: Term not found or not authorized

---

### Health Check

#### GET /health

Check API health status.

**Response (200 OK):**
```json
{
  "status": "healthy"
}
```

**Status Codes:**
- `200`: API is healthy

---

#### GET /

Get API information.

**Response (200 OK):**
```json
{
  "name": "Lexikon API",
  "version": "0.1.0",
  "status": "running",
  "docs": "/docs"
}
```

## Error Handling

All error responses follow a standardized format:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "additional": "information"
    },
    "request_id": "unique-request-id",
    "timestamp": "2024-11-19T10:30:00.000Z"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 422 | Request data validation failed |
| `INVALID_EMAIL` | 422 | Email format is invalid |
| `WEAK_PASSWORD` | 422 | Password doesn't meet strength requirements |
| `INVALID_CREDENTIALS` | 200 | Email or password is incorrect |
| `UNAUTHORIZED` | 401 | Authentication required |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource already exists (duplicate) |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

## Rate Limiting

The API implements rate limiting to prevent abuse.

### Rate Limit Tiers

| Endpoint | Limit | Window |
|----------|-------|--------|
| Auth (register, login) | 5 requests | 1 minute |
| API (authenticated) | 100 requests | 1 minute |
| Public (health, docs) | 1000 requests | 1 minute |

### Rate Limit Headers

Responses include rate limit information:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1634567890
```

When limit is exceeded, the API returns `429 Too Many Requests`:

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again later.",
    "timestamp": "2024-11-19T10:30:00.000Z"
  }
}
```

## Examples

### Register and Login

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe",
    "language": "en"
  }'

# Response: Save the access_token

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "SecurePass123!"
  }'
```

### Create and Retrieve a Term

```bash
# Create a term
curl -X POST http://localhost:8000/api/terms \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Artificial Intelligence",
    "definition": "Artificial Intelligence refers to computer systems designed to simulate human intelligence...",
    "domain": "informatique",
    "level": "quick-draft",
    "status": "draft"
  }'

# Response: Save the term ID

# Get the term
curl -X GET http://localhost:8000/api/terms/TERM_ID \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### List All Terms

```bash
curl -X GET http://localhost:8000/api/terms \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## API Documentation

The API includes interactive documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Contact & Support

For issues, questions, or feature requests, please contact the development team.
