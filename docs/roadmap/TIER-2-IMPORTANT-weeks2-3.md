# TIER 2 - IMPORTANT (Semaines 2-3)

**Status**: Feature-complete pour MVP
**Effort**: ~80 hours
**Prerequisites**: TIER-1 completed
**Timeline**: 2-3 weeks (Weeks 2-3)

---

## Overview

6 fonctionnalités qui transforment MVP "technically works" en "users can actually use this".

**Without TIER-2**:
- No proper authentication (only registration onboarding)
- No persistent data (everything lost on restart)
- No security throttling (vulnerable to abuse)
- No OAuth (friction on signup)

**With TIER-2**:
- Full auth flow (login/register)
- Data persists across deploys
- Protected against basic attacks
- Social login options (reduced friction)

---

## Task 1: Implémenter login/register backend (3-5 days, 24h)

**Priority**: 🟡 IMPORTANT
**Owner**: Lead Dev + Frontend Dev
**Blocker**: Only onboarding works currently; true auth missing

### Current State
- Registration (onboarding → profile setup) works
- Login page exists (stub, no backend)
- Register page exists (stub, no backend)
- Password hashing ready (`passlib + bcrypt`)
- JWT generation ready (integrated in TIER-1)

### What to implement

#### 1.1 Backend: `api/auth.py` (2-3 days)

**POST /api/auth/login**
```python
@app.post("/api/auth/login")
async def login(creds: LoginRequest):
    """
    Expected: { email, password }
    Return: { access_token, refresh_token, user_id }
    Errors: 401 (invalid), 404 (not found), 400 (validation)
    """
```

**POST /api/auth/register**
```python
@app.post("/api/auth/register")
async def register(req: RegisterRequest):
    """
    Expected: { email, password, firstName, lastName }
    Return: { user_id, access_token }
    Errors: 409 (duplicate email), 400 (validation)
    """
```

**POST /api/auth/logout**
```python
@app.post("/api/auth/logout")
async def logout(current_user = Depends(get_current_user)):
    """
    Logout user (invalidate refresh token for TIER-3)
    Return: { success: true }
    """
```

**POST /api/auth/refresh**
```python
@app.post("/api/auth/refresh")
async def refresh(req: RefreshRequest):
    """
    Exchange refresh token for new access token
    Expected: { refresh_token }
    Return: { access_token, token_type }
    """
```

**Tasks**:
- [ ] Create models: `LoginRequest`, `RegisterRequest`, `RefreshRequest`
- [ ] Implement password hashing + verification (passlib)
- [ ] Implement all 4 endpoints
- [ ] Add error handling (duplicate email, invalid password, etc.)
- [ ] Write unit tests
- **Time**: 2-3 days

#### 1.2 Frontend: Complete auth forms (1-2 days)

**login/+page.svelte**
- [ ] Email + password inputs
- [ ] Form validation
- [ ] Submit handler
- [ ] Error display
- [ ] Loading state
- [ ] Redirect on success

**register/+page.svelte**
- [ ] All onboarding fields
- [ ] Password strength indicator
- [ ] Password confirmation field
- [ ] Form validation
- [ ] Duplicate email check
- [ ] Submit handler

**Tasks**:
- [ ] Component scaffolding
- [ ] Form binding + validation
- [ ] API integration
- [ ] Tests (input.test.ts already covers)
- **Time**: 1-2 days

#### 1.3 Integration tests (1 day)

**E2E scenarios**:
- [ ] Register new user → verify email stored
- [ ] Login with correct password → get JWT
- [ ] Login with wrong password → error
- [ ] Login with non-existent email → 404
- [ ] Session persists across page reload
- [ ] Logout → cannot access protected routes

**Time**: 1 day

### Success Criteria
- ✅ All 4 auth endpoints working
- ✅ Passwords hashed (bcrypt)
- ✅ Frontend forms complete
- ✅ E2E test: register → login → logout flow
- ✅ 0 fake tokens or weak auth remaining

---

## Task 2: Implémenter OAuth (3-5 days, 24h)

**Priority**: 🟡 IMPORTANT
**Owner**: Lead Dev
**Driver**: Reduce signup friction (OAuth signup = 2 clicks vs form fill)

### Current State
- OAuth skeleton exists (`backend/auth/oauth.py`)
- Frontend OAuth buttons stubbed
- No provider configuration

### Providers
1. **GitHub**: Easier setup, good for technical users
2. **Google**: Broader audience, most users have account

### Implementation per provider (2-3 days each)

#### 2.1 GitHub OAuth

**Setup**:
1. Register app on https://github.com/settings/developers
2. Get Client ID + Secret
3. Add to `.env`

**Backend flow**:
```
1. Frontend redirects to GitHub
2. GitHub redirect back with code
3. Backend exchanges code for access token
4. Backend gets user info (email, name)
5. Create/update user in DB
6. Return JWT
```

**Frontend flow**:
- "Login with GitHub" button on login/register pages
- Redirect to `/oauth/callback/github?code=XXX`
- Handler validates code, stores token, redirects to dashboard

#### 2.2 Google OAuth

**Setup**:
1. Register app on https://console.cloud.google.com
2. Get Client ID + Client Secret
3. Add to `.env`

**Flow**: Same as GitHub

#### 2.3 Testing OAuth

- [ ] Mock OAuth provider in tests
- [ ] Test happy path (user created, token returned)
- [ ] Test error path (invalid code)
- [ ] Test existing user login (no duplicate)

### Success Criteria
- ✅ GitHub OAuth fully working
- ✅ Google OAuth fully working
- ✅ User created/updated correctly
- ✅ JWT issued on successful OAuth
- ✅ Frontend buttons route correctly
- ✅ E2E test: OAuth flow end-to-end

---

## Task 3: Persistance DB complète - PostgreSQL (1 week, 40h)

**Priority**: 🟡 IMPORTANT
**Owner**: Lead Dev
**Blocker**: Data in-memory currently (lost on restart)

### Current State
- PostgreSQL service running in docker-compose
- SQLAlchemy models mostly defined
- Alembic migration framework ready
- In-memory dict-based storage still used

### What to implement

#### 3.1 Replace in-memory storage with SQLAlchemy ORM (2-3 days)

**Current**: `database.py` uses dicts
```python
users_db = {}
terms_db = {}
```

**Target**: SQLAlchemy models + database
```python
from sqlalchemy.orm import Session
from models import User, Term

def get_user(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()
```

**Tasks**:
- [ ] Verify SQLAlchemy models in `models.py`
- [ ] Create database session management
- [ ] Update all CRUD operations to use ORM
- [ ] Add proper error handling (IntegrityError, etc.)
- [ ] Implement soft deletes where needed

#### 3.2 Alembic migrations (1-2 days)

**Current**: Initial migration exists (`20251115_0001_initial_schema.py`)

**Tasks**:
- [ ] Test initial migration on clean DB
- [ ] Create rollback test
- [ ] Document migration strategy
- [ ] Add migration to CI/CD (auto-run on deploy)
- [ ] Plan for data migrations (if needed later)

#### 3.3 Data integrity + testing (1-2 days)

**Tasks**:
- [ ] Test concurrent user operations
- [ ] Test transaction rollback
- [ ] Test foreign key constraints
- [ ] Test unique constraints
- [ ] Load test (1000 terms)

### Success Criteria
- ✅ All data persists across server restart
- ✅ Initial migration runs successfully
- ✅ Foreign keys enforced
- ✅ Concurrent access works
- ✅ No data loss on errors

---

## Task 4: Ajouter rate limiting (2-3h)

**Priority**: 🟡 IMPORTANT
**Owner**: Lead Dev
**Blocker**: Vulnerable to brute force / DDoS

### Implementation

**Tool**: `SlowAPI` (FastAPI wrapper around ratelimit)

```bash
pip install slowapi
```

**Code**:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/auth/login")
@limiter.limit("5/minute")  # 5 attempts per minute per IP
async def login(creds: LoginRequest):
    ...

@app.post("/api/terms")
@limiter.limit("100/hour")  # 100 new terms per hour per user
async def create_term(term: TermRequest, current_user = Depends(get_current_user)):
    ...
```

**Rates to set**:
- Login endpoint: 5 attempts/minute (prevent brute force)
- Register: 3 new accounts/hour per IP
- Term creation: 100/hour per user (freemium limit)
- Term listing: 1000/hour per user

**Tasks**:
- [ ] Install + configure slowapi
- [ ] Apply to all auth endpoints
- [ ] Apply to term endpoints
- [ ] Handle rate limit responses (429)
- [ ] Document rate limits in API docs
- [ ] Test rate limiting behavior

### Success Criteria
- ✅ Exceeding limits returns 429
- ✅ Limits configurable via env
- ✅ Logs show rate limit hits
- ✅ Tests verify limits enforced

---

## Task 5: Input validation amélioration (1-2h)

**Priority**: 🟡 IMPORTANT
**Issue**: Current regex rejects international names (Ç, ñ, ü, etc.)

### Problem
```python
# Current (too restrictive)
pattern = r"^[a-zA-ZÀ-ÿ\s\-]{2,100}$"

# Rejects: Ångström (å), Peña (ñ), José (é as second char)
```

### Solution
Use `unicodedata` for proper Unicode handling:

```python
import unicodedata

def validate_name(name: str) -> bool:
    # Normalize to NFC (decompose accents)
    name = unicodedata.normalize('NFC', name)

    # Allow letters, spaces, hyphens, apostrophes
    allowed = lambda c: c.isalpha() or c in " -',"

    return all(allowed(c) for c in name) and 2 <= len(name) <= 100
```

**Test cases**:
- ✅ François
- ✅ Peña
- ✅ O'Brien
- ✅ María-José
- ✅ 田中 (Japanese)
- ❌ user@domain (email chars rejected)
- ❌ <script> (HTML rejected)

### Success Criteria
- ✅ All international names accepted
- ✅ Control characters rejected
- ✅ XSS payloads rejected
- ✅ Tests pass for all cases

---

## Task 6: Setup CI/CD complet (4-5h)

**Priority**: 🟡 IMPORTANT
**Owner**: Lead Dev
**Blocker**: No automated testing

### GitHub Actions workflow

Create `.github/workflows/ci.yml`:

```yaml
name: CI/CD

on:
  push:
    branches: [master, develop]
  pull_request:
    branches: [master, develop]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: lexikon_test
          POSTGRES_PASSWORD: password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Frontend lint + test
        run: |
          npm install
          npm run lint
          npm run test -- --run
          npm run test:coverage

      - name: Backend lint + test
        run: |
          pip install -r backend/requirements.txt
          ruff check backend
          black --check backend
          pytest backend/ -v --cov

      - name: Build frontend
        run: npm run build

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/coverage-final.json

  e2e:
    runs-on: ubuntu-latest
    needs: test

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Run E2E tests
        run: |
          npm install
          npm run test:e2e

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/

  build:
    runs-on: ubuntu-latest
    needs: [test, e2e]

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - uses: actions/setup-python@v4

      - name: Build Docker images
        run: |
          docker build -f Dockerfile.frontend -t lexikon-frontend:latest .
          docker build -f Dockerfile.backend -t lexikon-backend:latest backend/

      - name: Publish artifacts
        if: github.ref == 'refs/heads/master'
        run: |
          # Push to registry (ECR, Docker Hub, etc.)
          echo "TODO: Push to production registry"
```

**Tasks**:
- [ ] Create `.github/workflows/ci.yml`
- [ ] Protect master branch (require checks pass)
- [ ] Require reviews before merge
- [ ] Add status badges to README
- [ ] Document deployment process

### Success Criteria
- ✅ CI runs on every PR
- ✅ Tests must pass before merge
- ✅ Coverage tracked + displayed
- ✅ E2E tests run in CI
- ✅ Build succeeds on master

---

## Summary

| Task | Hours | Effort | Owner |
|------|-------|--------|-------|
| 1. Login/register | 24 | 3-5 days | Lead Dev |
| 2. OAuth integration | 24 | 3-5 days | Lead Dev |
| 3. PostgreSQL persistence | 40 | 1 week | Lead Dev |
| 4. Rate limiting | 3 | 0.5 day | Lead Dev |
| 5. Input validation | 2 | 2-3 hours | Lead Dev |
| 6. CI/CD setup | 5 | 4-5 hours | Lead Dev |
| **TOTAL** | **98** | **2-3 weeks** | - |

### Timeline
Assuming 2 developers at 40h/week:
- Week 2: Tasks 1 + 4 + 5 (auth foundation + rate limiting)
- Week 3: Tasks 2 + 3 + 6 (OAuth + DB + CI/CD)

### Next Steps
→ Proceed to [TIER-3-POLISH-weeks4-6.md](TIER-3-POLISH-weeks4-6.md)
