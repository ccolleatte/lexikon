# TIER 1 - BLOCKER (Semaine 1)

**Status**: Critical path pour launch MVP
**Effort Total**: 66-74 hours
**Team**: Lead Dev + QA Eng + PM
**Timeline**: 1 semaine (5 working days)

---

## 🚨 Overview

5 activités qui **bloquent absolument** la mise en production de v0.1.0.

Sans ces éléments, l'application n'est pas deployable, sécurisable, ou testable.

### Deliverables Semaine 1
- ✅ JWT réels en production (pas de fake tokens)
- ✅ CORS paramétrable via env vars
- ✅ Tests couverture 80%+ (pas de stubs)
- ✅ Linting + formatting automatisé
- ✅ Audit sécurité passé

### DRI (Directly Responsible Individual)
| Task | Owner | +1 |
|------|-------|-----|
| JWT Integration | Lead Dev | Architect |
| CORS Setup | Lead Dev | PM |
| Tests Completion | QA Eng | Lead Dev |
| Linting Config | Lead Dev | QA Eng |
| Security Audit | QA Eng | Sec Lead |

---

## Task 1: Intégrer JWT réel dans API (2-3h)

**Priority**: 🔴 CRITIQUE
**Owner**: Lead Dev
**Time**: 2-3 heures
**Status**: Not started

### Problème actuel
```python
# backend/api/users.py (Sprint 1 code - WRONG)
def create_profile(req: UserProfileRequest):
    user_id = generate_id()
    return {
        "token": f"fake-jwt-token-{user_id}"  # ← FAKE!
    }
```

**Impact sécurité**: Le backend accepte n'importe quel bearer token. Validation zéro.

### Qu'est-ce qui existe déjà
✅ `backend/auth/jwt.py` : Complet et testé (token generation, verification)
✅ `backend/models.py` : User + Auth models
✅ Frontend auth store: Prêt à stocker vrais tokens

### Que faire

#### 1.1 Modifier `api/users.py` (30 min)

Remplacer le fake token par du JWT réel:

```python
# backend/api/users.py (FIXED)
from auth.jwt import generate_access_token, generate_refresh_token

def create_profile(req: UserProfileRequest) -> dict:
    """Create user profile and return JWT tokens"""
    user_id = generate_id()

    # Store user in DB (will be implemented in Task 3)
    # For now: in-memory (Sprint 1)

    # Generate REAL tokens
    access_token = generate_access_token(
        subject=str(user_id),
        user_data={"email": req.email, "firstName": req.firstName}
    )
    refresh_token = generate_refresh_token(subject=str(user_id))

    return {
        "success": True,
        "data": {
            "user_id": user_id,
            "access_token": access_token,
            "refresh_token": refresh_token,  # Send to secure storage
            "token_type": "Bearer"
        }
    }
```

**Time**: 30 minutes
**Files touched**: `backend/api/users.py`
**Tests needed**: Manual test with Postman

#### 1.2 Implémenter middleware auth (1h)

Créer `backend/auth/middleware.py` pour valider tokens:

```python
# backend/auth/middleware.py (NEW)
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthCredentialsError
from jwt import PyJWTError
from auth.jwt import verify_access_token

security = HTTPBearer()

async def get_current_user(credentials = Depends(security)):
    """Middleware that validates JWT token from Authorization header"""
    try:
        token = credentials.credentials
        payload = verify_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    return {"user_id": user_id, "payload": payload}


def protect_endpoint(func):
    """Decorator to protect endpoints with JWT"""
    async def wrapper(*args, current_user = Depends(get_current_user), **kwargs):
        # current_user is guaranteed non-null here
        return await func(*args, current_user=current_user, **kwargs)
    return wrapper
```

Apply to endpoints:
```python
# backend/api/terms.py
@app.get("/api/terms")
async def list_terms(current_user = Depends(get_current_user)):
    """List terms for authenticated user"""
    user_id = current_user["user_id"]
    # Filter terms by user_id
    return {terms: [...]}
```

**Time**: 1 hour
**Files touched**: Create `backend/auth/middleware.py`, update `backend/api/*.py`
**Tests needed**: Unit test middleware

#### 1.3 Tester intégration (30 min)

Manual test suite:

```bash
# 1. GET user profile (create + get token)
curl -X POST http://localhost:8000/api/users/profile \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "Jean",
    "lastName": "Dupont",
    "email": "jean@example.com",
    "sessionId": "session-123"
  }'

# Response:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "token_type": "Bearer"
# }

# 2. USE token to get terms
curl -X GET http://localhost:8000/api/terms \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Expected: 200 OK + terms

# 3. Try WITHOUT token
curl -X GET http://localhost:8000/api/terms

# Expected: 401 Unauthorized

# 4. Try with INVALID token
curl -X GET http://localhost:8000/api/terms \
  -H "Authorization: Bearer fake-token"

# Expected: 401 Unauthorized
```

**Time**: 30 minutes
**Files touched**: None (testing only)
**Tools**: Postman or curl

#### 1.4 Décommenter E2E tests (30 min)

**File**: `e2e/auth.spec.ts`

Currently has 7 test cases commented out:
```typescript
// These will now pass:
test('login with valid credentials', async ({ page }) => { ... })
test('reject invalid credentials', async ({ page }) => { ... })
test('token refresh works', async ({ page }) => { ... })
// etc.
```

Décommenter et vérifier 7/7 pass.

**Time**: 30 minutes
**Files touched**: `e2e/auth.spec.ts`
**Run**: `npm run test:e2e -- auth.spec.ts`

### Success Criteria (Task 1)
- ✅ POST /api/users/profile returns real JWT (verified with jwt.io)
- ✅ GET /api/terms with valid JWT → 200 OK
- ✅ GET /api/terms without JWT → 401 Unauthorized
- ✅ GET /api/terms with invalid JWT → 401 Unauthorized
- ✅ E2E auth.spec.ts: 7/7 tests PASS
- ✅ Fake tokens completely removed

### Risks & Mitigations
| Risk | Impact | Mitigation |
|------|--------|-----------|
| Frontend doesn't update auth headers | Major | Coordinate with frontend dev, have them test with Postman first |
| Token validation too strict (rejects valid) | Major | Test manually before deploying |
| Middleware breaks other endpoints | Major | Apply only to protected routes first, test incrementally |

---

## Task 2: Paramétrer CORS pour production (1h)

**Priority**: 🔴 CRITIQUE
**Owner**: Lead Dev
**Time**: 1 heure
**Status**: Not started

### Problème actuel
```python
# backend/main.py (Sprint 1 - HARDCODED)
app.add_middleware(CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # ← HARDCODED!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
```

**Impact**: Can't deploy to different domain without code change.

### Que faire

#### 2.1 Créer `backend/config.py` (20 min)

```python
# backend/config.py (NEW)
import os
from typing import List

class Settings:
    """Configuration management"""

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///lexikon.db"  # Dev default
    )

    # Neo4j
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "password")

    # Security
    JWT_SECRET: str = os.getenv(
        "JWT_SECRET",
        "dev-secret-change-in-production"
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 1
    REFRESH_TOKEN_EXPIRATION_DAYS: int = 7

    # CORS (critical!)
    ALLOWED_ORIGINS: List[str] = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://localhost:3000"
    ).split(",")

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"

settings = Settings()
```

**Time**: 20 minutes

#### 2.2 Modifier `backend/main.py` (10 min)

```python
# backend/main.py (UPDATED)
from fastapi.middleware.cors import CORSMiddleware
from config import settings

app = FastAPI()

# Use dynamic origins from config
app.add_middleware(CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
```

**Time**: 10 minutes

#### 2.3 Créer `.env.example` complet (20 min)

```bash
# backend/.env.example
# Copy to .env.local and fill with real values

# Environment
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/lexikon

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Authentication
JWT_SECRET=your-secret-key-here-min-32-chars-for-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=1
REFRESH_TOKEN_EXPIRATION_DAYS=7

# CORS (comma-separated, no spaces)
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:8000

# LLM Keys (if using)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

**Time**: 20 minutes

#### 2.4 Mettre à jour README (20 min)

Add section:
```markdown
## Configuration

### Environment Variables

Copy `.env.example` to `.env.local`:
```bash
cp backend/.env.example backend/.env.local
```

Edit `.env.local` with your values. **Never commit `.env`.**

### Production Setup

For production deployment:
```
ENVIRONMENT=production
ALLOWED_ORIGINS=https://app.lexikon.ai,https://api.lexikon.ai
JWT_SECRET=<your-32-char-secret-from-password-manager>
DATABASE_URL=postgresql://<prod-rds-url>
```
```

**Time**: 20 minutes

### Success Criteria (Task 2)
- ✅ ALLOWED_ORIGINS loaded from env var
- ✅ `.env.example` is complete
- ✅ Default dev origins work (localhost:5173, 3000)
- ✅ README documents how to configure
- ✅ Deployment can override origins without code change

---

## Task 3: Compléter tests (3-5 days)

**Priority**: 🔴 CRITIQUE
**Owner**: QA Eng + Lead Dev
**Time**: 3-5 jours (40 hours)
**Status**: Not started

### Problème actuel
- `page.test.ts` files are stubs with 0 real assertions
- Components (Input, Select, Button, etc.) untested
- Coverage is ~70% actual vs claimed 85%+

### Current test files
```
✅ src/lib/stores/auth.test.ts          (complete, 30+ assertions)
✅ src/lib/utils/api.test.ts            (complete, 40+ assertions)
✅ src/lib/utils/auth.test.ts           (complete, 20+ assertions)
⚠️  src/lib/components/NavBar.test.ts   (minimal, 5 assertions)
❌ src/routes/login/page.test.ts        (stub, 0 assertions)
❌ src/routes/register/page.test.ts     (stub, 0 assertions)
❌ src/routes/profile/page.test.ts      (stub, 0 assertions)
❌ src/routes/onboarding/...test.ts     (missing)
✅ e2e/auth.spec.ts                     (7 scenarios)
✅ e2e/user-journey.spec.ts             (complete flow)
```

### Plan de test

#### Phase 1: Routes (2-3 days, 24 hours)

**1.3a: login/page.test.ts** (6-8 hours)
```typescript
// Should test:
describe('Login Page', () => {
  test('renders login form', async ({ render }) => {
    // Assert: email input, password input, submit button visible
  })

  test('submits with valid credentials', async ({ render }) => {
    // Assert: API called, token stored, redirect to /terms
  })

  test('shows error on invalid credentials', async ({ render }) => {
    // Assert: Error message displayed
  })

  test('password field is type=password', async ({ render }) => {
    // Assert: Input masked
  })

  test('submit disabled while loading', async ({ render }) => {
    // Assert: Button disabled, spinner shown
  })
})
```

**1.3b: register/page.test.ts** (6-8 hours)
```typescript
// Should test:
test('validates password match')
test('validates min password length')
test('checks duplicate email')
test('shows password strength indicator')
test('form resets after success')
```

**1.3c: profile/page.test.ts** (6-8 hours)
```typescript
// Should test:
test('loads and displays user data')
test('edits profile successfully')
test('validates name length')
test('handles API errors gracefully')
test('shows confirmation on save')
```

**1.3d: terms/+page.test.ts** (4-6 hours)
```typescript
// Should test:
test('displays list of terms')
test('filters by domain')
test('creates new term')
test('validation errors handled')
```

#### Phase 2: Composants (1-2 days, 12 hours)

Each component needs minimum 3-4 tests:

**1.3e: Input.test.ts** (2-3 hours)
```typescript
test('renders with placeholder')
test('accepts input and emits change')
test('shows error state')
test('shows char counter')
test('is disabled when prop set')
test('has focus ring on focus')
```

**1.3f: Select.test.ts** (2-3 hours)
```typescript
test('renders options')
test('selects option')
test('shows error state')
test('is disabled when prop set')
```

**1.3g: Textarea.test.ts** (1-2 hours)
```typescript
test('auto-resizes')
test('shows error')
test('is disabled')
```

**1.3h: Button.test.ts** (1-2 hours)
```typescript
test('renders all variants')
test('shows loading spinner')
test('is disabled when prop set')
test('emits click event')
```

**1.3i: Alert.test.ts** (1-2 hours)
```typescript
test('renders all variants')
test('shows icon')
test('is dismissible')
```

#### Phase 3: Coverage Check (4 hours)

```bash
npm run test:coverage
# Target: 80%+ line coverage
# Review report: coverage/index.html
# Fix gaps: missing branches, edge cases
```

### Success Criteria (Task 3)
- ✅ page.test.ts: Each has >3 real test cases (not stubs)
- ✅ Composants: Input, Select, Button, Textarea, Alert each have tests
- ✅ Coverage report: 80%+ global coverage
- ✅ All tests pass: `npm run test -- --run` = 0 failures
- ✅ No console errors/warnings during test run

---

## Task 4: Linting + Formatting + Pre-commit (8-10h)

**Priority**: 🔴 CRITIQUE
**Owner**: Lead Dev
**Time**: 8-10 heures (2 days)
**Status**: Not started

### Pourquoi critique
- Code quality drift without automation
- Future devs commit bad code
- Technical debt accumulates
- Hard to review PRs with formatting noise

### Qu'à faire

#### 4.1: Frontend (TypeScript/Svelte)

**Create `.eslintrc.json`** (30 min)
```json
{
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:svelte/recommended"
  ],
  "rules": {
    "no-console": "warn",
    "no-unused-vars": "off",
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/strict-boolean-expressions": "warn"
  },
  "parserOptions": {
    "ecmaVersion": 2020,
    "sourceType": "module"
  }
}
```

**Create `.prettierrc`** (15 min)
```json
{
  "semi": true,
  "singleQuote": true,
  "trailingComma": "es5",
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false
}
```

**Install packages** (5 min)
```bash
npm install -D \
  eslint \
  eslint-plugin-svelte \
  @typescript-eslint/eslint-plugin \
  prettier
```

**Add scripts to package.json** (10 min)
```json
{
  "scripts": {
    "lint": "eslint src",
    "lint:fix": "eslint src --fix",
    "format": "prettier --write .",
    "format:check": "prettier --check ."
  }
}
```

**Run auto-fix** (30 min)
```bash
npm run lint:fix 2>&1 | head -20  # See issues
npm run format
```

#### 4.2: Backend (Python)

**Create `pyproject.toml`** (20 min)
```toml
[tool.ruff]
line-length = 100
target-version = "py311"
select = ["E", "F", "W", "I", "N", "UP", "B", "A", "C4", "T20"]
ignore = ["E501"]  # Line too long (black handles)

[tool.black]
line-length = 100
target-version = ["py311"]
```

**Install packages** (5 min)
```bash
pip install ruff black isort
```

**Add Makefile** (10 min)
```makefile
.PHONY: lint format format-check

lint:
	ruff check backend && isort --check backend && black --check backend

format:
	ruff check backend --fix && isort backend && black backend

format-check:
	ruff check backend && isort --check backend && black --check backend
```

**Run auto-fix** (30 min)
```bash
make format
```

#### 4.3: Pre-commit Hooks

**Create `.pre-commit-config.yaml`** (30 min)
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json

  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.5
    hooks:
      - id: ruff
        args: [--fix]

  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.1.0
    hooks:
      - id: prettier
        types_or: [typescript, tsx, jsx, json, markdown, yaml, toml]
```

**Install hooks** (15 min)
```bash
pre-commit install
pre-commit run --all-files
```

### Success Criteria (Task 4)
- ✅ ESLint config created + all rules pass
- ✅ Prettier config created + format applied
- ✅ Ruff + Black config created for Python
- ✅ Pre-commit hooks block bad commits
- ✅ npm run lint, make format-check both pass
- ✅ Documentation updated in README

---

## Task 5: Audit sécurité (15-20h)

**Priority**: 🔴 CRITIQUE
**Owner**: QA Eng
**Time**: 15-20 heures
**Status**: Not started

### Checklist sécurité

#### 5.1: Token Validation (4-6h)

| Test | Expected | Status |
|------|----------|--------|
| POST /api/users/profile → JWT | Valid JWT returned | [ ] |
| GET /api/terms + valid JWT | 200 OK | [ ] |
| GET /api/terms + invalid JWT | 401 Unauthorized | [ ] |
| GET /api/terms + expired JWT | 401 Unauthorized | [ ] |
| GET /api/terms (no header) | 401 Unauthorized | [ ] |
| GET /api/terms + malformed header | 401 Unauthorized | [ ] |

#### 5.2: CORS Enforcement (2-3h)

| Test | Expected | Status |
|------|----------|--------|
| Request from allowed origin | 200 OK | [ ] |
| Request from disallowed origin | CORS blocked | [ ] |
| Preflight OPTIONS request | 200 OK | [ ] |

#### 5.3: Input Validation (3-4h)

| Test | Expected | Status |
|------|----------|--------|
| Name too short (< 2 chars) | Validation error | [ ] |
| Name too long (> 100 chars) | Validation error | [ ] |
| Email invalid format | Validation error | [ ] |
| Duplicate email | 409 Conflict | [ ] |
| Special chars (é, ñ, Ç) | Accepted | [ ] |
| SQL injection attempt | Rejected | [ ] |
| XSS payload in name | Escaped | [ ] |

#### 5.4: Rate Limiting (2-3h)

**Note**: Not implemented yet, document for Task 2.1

| Test | Expected | Status |
|------|----------|--------|
| >10 requests/min (anon) | 429 Too Many Requests | [❌] Not yet |
| >100 requests/min (auth) | 429 Too Many Requests | [❌] Not yet |

#### 5.5: Documentation

Create `SECURITY-AUDIT-WEEK1.md`:
```markdown
# Security Audit - Week 1

## Passing Checks ✅
- Token validation: PASS
- CORS enforcement: PASS
- Input validation: PASS

## Failing Checks ❌
- Rate limiting: NOT IMPLEMENTED (TIER-2)

## Blockers for Release
- None (all critical items pass)

## Warnings ⚠️
- JWT secret in `.env.example` is placeholder (CHANGE IN PRODUCTION)
- HTTPS not enforced in dev (required in production)
```

### Success Criteria (Task 5)
- ✅ Token validation: All tests pass
- ✅ CORS: Properly enforced
- ✅ Input: All validation works
- ✅ SECURITY-AUDIT.md: Complete
- ✅ All blockers cleared for v0.1 release

---

## Summary & Timeline

### Effort Breakdown
| Task | Hours | Owner | Week |
|------|-------|-------|------|
| 1. JWT integration | 2-3 | Lead Dev | Mon-Tue |
| 2. CORS setup | 1 | Lead Dev | Tue |
| 3. Tests completion | 40 | QA + Dev | Tue-Fri |
| 4. Linting + formatting | 8-10 | Lead Dev | Mon-Wed |
| 5. Security audit | 15-20 | QA | Thu-Fri |
| **TOTAL** | **66-74** | - | **All week** |

### Critical Path
1. **Monday AM**: Start JWT integration + linting setup (can parallelize)
2. **Monday PM**: Tests infrastructure ready
3. **Tuesday-Wednesday**: Bulk of tests + JWT verification
4. **Thursday**: Security audit + polish
5. **Friday**: Final verification + sign-off

### Dependencies
- Task 1 (JWT) unblocks Tasks 3 (E2E tests) + 5 (security audit)
- Task 2 (CORS) independent
- Task 4 (linting) independent
- **No hard blockers**, can parallelize aggressively

### Risk & Contingency
| Risk | Probability | Mitigation |
|------|------------|-----------|
| Tests take longer than estimated | HIGH | Start early, parallelize |
| JWT integration breaks frontend | MEDIUM | Coordinate closely, test with Postman first |
| Pre-commit hooks too strict | LOW | Adjust rules if needed |
| Security audit finds issues | MEDIUM | Have contingency time Friday |

### Sign-off Template

```
✋ TIER-1 BLOCKER SIGN-OFF (Semaine 1)

PM Approval:        [ ] Agree timeline + deliverables
Lead Dev Approval:  [ ] Agree technical approach
QA Approval:        [ ] Agree test strategy
Security Lead:      [ ] Security review OK
CTO/Architect:      [ ] Architecture review OK

All boxes checked = Ready for v0.1 release candidate
```

---

## Next Steps

Once TIER-1 complete:
→ Proceed to [TIER-2-IMPORTANT-weeks2-3.md](TIER-2-IMPORTANT-weeks2-3.md)
