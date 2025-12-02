# Lexikon API - Backend

FastAPI backend for Lexikon Sprint 1 MVP.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python main.py
```

Server will start at `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

## Endpoints

### Onboarding

- **POST `/api/onboarding/adoption-level`** - Save adoption level selection
  - Body: `{ "adoptionLevel": "quick-project", "sessionId": "uuid" }`

### Users

- **POST `/api/users/profile`** - Create user profile
  - Body: `{ "firstName": "Marie", "lastName": "Dupont", "email": "marie@example.com", ... }`

### Terms

- **POST `/api/terms`** - Create new term
  - Body: `{ "name": "Épistémologie", "definition": "...", "domain": "Philosophie" }`
- **GET `/api/terms`** - List user terms

## Architecture

- **Framework**: FastAPI 0.104+
- **Validation**: Pydantic v2
- **Database**: In-memory (Sprint 1) → PostgreSQL + Neo4j (Sprint 2)

## Sprint 1 Simplifications

- No authentication (fake JWT tokens)
- In-memory database (data lost on restart)
- No rate limiting
- No avatar upload

These will be implemented in Sprint 2.
