# Lexikon User Journey Testing Plan

## Overview

After deploying to VPS, validate that all user journeys work according to specification.

## Prerequisites

- Application deployed and healthy (`docker-compose ps`)
- Access to: `https://your-domain.com`
- Test user can be created

## Test Environment

- **Frontend URL**: `https://your-domain.com`
- **API URL**: `https://your-domain.com/api`
- **Backend Direct**: `http://localhost:8000` (VPS only)

## Test Cases

---

## Journey 1: Registration & Email/Password Authentication

**Specification**: US-002, Auth Flow
**Estimated Time**: 5 minutes
**Status**: [ ] PASS [ ] FAIL

### Setup

Create a test account with unique email:

```bash
TEST_EMAIL="test_$(date +%s)@example.com"
echo "Using email: $TEST_EMAIL"
```

### Steps

1. Navigate to `https://your-domain.com/register`
2. Fill registration form:
   - First Name: `Test`
   - Last Name: `User`
   - Email: `$TEST_EMAIL`
   - Password: `SecurePassword123!`
   - Terms: Check box
3. Click "Create Account"

### Expected Results

| Step | Expected | Actual | Status |
|------|----------|--------|--------|
| Form validation | Password strength validated | | [ ] |
| API call | POST /api/auth/register succeeds (201) | | [ ] |
| Response | Receives access_token + refresh_token | | [ ] |
| Redirect | Redirects to /onboarding | | [ ] |
| User record | New row in users table (psql verify) | | [ ] |

### Verification (Backend)

```bash
# SSH to VPS
docker exec -it lexikon-postgres psql -U lexikon -d lexikon

# Check user was created
SELECT id, email, first_name, created_at FROM users WHERE email = 'test_...' LIMIT 1;

# Verify password hash exists
SELECT password_hash IS NOT NULL FROM users WHERE email = 'test_...' LIMIT 1;
```

---

## Journey 2: Onboarding - Adoption Level Selection

**Specification**: US-001
**Estimated Time**: 3 minutes
**Status**: [ ] PASS [ ] FAIL

### Setup

- Logged in user from Journey 1
- Already on `/onboarding` page

### Steps

1. See 3 adoption level options:
   - [ ] Quick Project (fast, temporary)
   - [ ] Research Project (periodic, validation)
   - [ ] Production API (continuous, integration)
2. Select **Quick Project**
3. Click "Continue →"

### Expected Results

| Step | Expected | Actual | Status |
|------|----------|--------|--------|
| Page load | 3 radio cards visible | | [ ] |
| Selection | Can select any option | | [ ] |
| API call | POST /api/onboarding/adoption-level (200) | | [ ] |
| Database | users.adoption_level = "quick-project" | | [ ] |
| Redirect | Redirects to /onboarding/profile | | [ ] |
| Progress | Stepper shows "2/3" | | [ ] |

### Verification (Backend)

```bash
docker exec -it lexikon-postgres psql -U lexikon -d lexikon

SELECT adoption_level FROM users WHERE email = 'test_...' LIMIT 1;
# Expected: quick-project
```

---

## Journey 3: Onboarding - Profile Setup

**Specification**: US-003
**Estimated Time**: 3 minutes
**Status**: [ ] PASS [ ] FAIL

### Setup

- User on `/onboarding/profile` page
- Stepper showing "2/3"

### Steps

1. Fill profile form:
   - First Name: `Test` (auto-filled)
   - Last Name: `User` (auto-filled)
   - Email: `test_...@example.com` (auto-filled)
   - Institution: `University of Test` (optional)
   - Primary Domain: `Computer Science`
   - Language: `English`
   - Country: `France`
2. Click "Continue →"

### Expected Results

| Step | Expected | Actual | Status |
|------|----------|--------|--------|
| Form loads | 8 fields visible, some pre-filled | | [ ] |
| Validation | Required fields enforced | | [ ] |
| API call | POST /api/users/profile (200) | | [ ] |
| Database | users record updated | | [ ] |
| Redirect | Redirects to /terms | | [ ] |
| Progress | Stepper shows "3/3" | | [ ] |

### Verification (Backend)

```bash
docker exec -it lexikon-postgres psql -U lexikon -d lexikon

SELECT institution, primary_domain, language, country FROM users WHERE email = 'test_...' LIMIT 1;
# Expected: University of Test | Computer Science | en | FR
```

---

## Journey 4: Term Creation (Quick Mode)

**Specification**: US-002
**Estimated Time**: 5 minutes
**Status**: [ ] PASS [ ] FAIL

### Setup

- User on `/terms` (empty list)
- Click "Create Term" button

### Steps

1. Navigate to `/terms/new`
2. Should see badge "⚡ Mode Rapide" (Quick Mode)
3. Fill 3 fields:
   - **Term Name**: `Artificial Intelligence` (50 chars)
   - **Definition**: `The simulation of human intelligence processes by digital computers` (70 chars)
   - **Domain**: `Computer Science` (optional)
4. Watch progress bar:
   - After name (50+ chars): +40%
   - After definition (50+ chars): +50%
   - After domain: +10%
5. Should reach 100% (all 3 fields)
6. Click "Créer le terme →"

### Expected Results

| Step | Expected | Actual | Status |
|------|----------|--------|--------|
| Page load | 3-field form, auto-save enabled | | [ ] |
| Char counter | "50/100" shown under name | | [ ] |
| Progress calc | 40% after name, 90% after def | | [ ] |
| Auto-save | "Sauvegardé ✓" appears after 1s | | [ ] |
| Validation | Button disabled until 3 chars + 50 chars | | [ ] |
| API call | POST /api/terms (201) | | [ ] |
| Response | Returns term ID | | [ ] |
| Database | New row in terms table | | [ ] |
| Redirect | Redirects to /terms | | [ ] |
| List | Term appears in list | | [ ] |

### Verification (Backend)

```bash
docker exec -it lexikon-postgres psql -U lexikon -d lexikon

SELECT id, name, definition, domain, level FROM terms ORDER BY created_at DESC LIMIT 1;
# Expected: artificial-intelligence | ... | Computer Science | quick-draft
```

---

## Journey 5: Term List View

**Specification**: Search/List functionality
**Estimated Time**: 2 minutes
**Status**: [ ] PASS [ ] FAIL

### Setup

- User on `/terms` page
- At least 1 term created from Journey 4

### Steps

1. Should see created term in list
2. Term card should show:
   - [ ] Name: "Artificial Intelligence"
   - [ ] Definition: First 100 chars
   - [ ] Domain: "Computer Science"
   - [ ] Created date
   - [ ] Delete button
3. Try filtering by domain (if available)
4. Try searching if search box exists

### Expected Results

| Step | Expected | Actual | Status |
|------|----------|--------|--------|
| List load | GET /api/terms (200) | | [ ] |
| Display | Term visible in list | | [ ] |
| Card info | All fields displayed | | [ ] |
| Delete button | Can delete term | | [ ] |
| Pagination | Works if >10 terms | | [ ] |

### Verification (Backend)

```bash
docker exec -it lexikon-postgres psql -U lexikon -d lexikon

SELECT COUNT(*) FROM terms WHERE created_by = (SELECT id FROM users WHERE email = 'test_...' LIMIT 1);
# Expected: >= 1
```

---

## Journey 6: Login (Return User)

**Specification**: Auth Flow
**Estimated Time**: 3 minutes
**Status**: [ ] PASS [ ] FAIL

### Setup

- Logged out user
- Have test credentials from Journey 1

### Steps

1. Navigate to `/login`
2. Fill form:
   - Email: `test_...@example.com`
   - Password: `SecurePassword123!`
3. Click "Sign In"

### Expected Results

| Step | Expected | Actual | Status |
|------|----------|--------|--------|
| Form | Email + password fields | | [ ] |
| Validation | Email format validated | | [ ] |
| API call | POST /api/auth/login (200) | | [ ] |
| Response | Receives access_token | | [ ] |
| Token store | JWT stored in localStorage | | [ ] |
| Redirect | Redirects to /terms | | [ ] |
| Permissions | Can see user's own terms | | [ ] |

### Verification (Frontend - Browser Dev Tools)

```javascript
// In browser console
localStorage.getItem('lexikon-auth')
// Expected: {"access_token": "eyJ...", "user": {...}}
```

---

## Journey 7: Refresh Token Renewal

**Specification**: JWT token lifecycle
**Estimated Time**: 5 minutes (after 60+ min or manual)
**Status**: [ ] PASS [ ] FAIL

### Setup

- Logged in user
- Note current access_token expiry

### Steps

1. Wait ~60 minutes OR manually trigger refresh
2. Make API call (GET /api/terms)
3. Should transparently refresh token

### Expected Results

| Step | Expected | Actual | Status |
|------|----------|--------|--------|
| API call | Works with expired access_token | | [ ] |
| Refresh | POST /api/auth/refresh automatically called | | [ ] |
| New token | access_token rotated in localStorage | | [ ] |
| Session | User remains logged in | | [ ] |

---

## Journey 8: Logout

**Specification**: Session termination
**Estimated Time**: 2 minutes
**Status**: [ ] PASS [ ] FAIL

### Setup

- Logged in user

### Steps

1. Click user menu (top-right)
2. Click "Logout"
3. Navigate to `/terms` (protected route)

### Expected Results

| Step | Expected | Actual | Status |
|------|----------|--------|--------|
| Logout | JWT removed from localStorage | | [ ] |
| Redirect | Redirected to /login | | [ ] |
| Access | Cannot access /terms without login | | [ ] |
| Session | New login required | | [ ] |

---

## Performance Benchmarks

**Specification**: Appendix in user journey docs

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Registration API | <500ms | | [ ] |
| Term creation | <500ms | | [ ] |
| Term list GET | <200ms (10 terms) | | [ ] |
| Login | <500ms | | [ ] |
| Page load | <2s | | [ ] |
| Auto-save latency | ~1s (configurable) | | [ ] |

### Measurement

```bash
# Test API response times
time curl -X POST https://your-domain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'
```

---

## Error Handling Tests

**Specification**: Error codes and messages

### Test Cases

| Scenario | Expected Behavior | Status |
|----------|-------------------|--------|
| **Wrong password** | POST /api/auth/login returns 401, message "Invalid credentials" | [ ] |
| **Duplicate email** | POST /api/auth/register returns 409, message "Email already exists" | [ ] |
| **Missing required field** | Returns 422 with validation error | [ ] |
| **Weak password** | Frontend validation + 400 from backend | [ ] |
| **Network timeout** | Graceful error message, retry option | [ ] |
| **Server error** | 500 error with generic message (no stack trace) | [ ] |

---

## Security Tests

**Specification**: Security requirements

| Test | Expected | Status |
|------|----------|--------|
| **Password hashing** | Passwords never sent in plain text | [ ] |
| **JWT validation** | Invalid token rejected (401) | [ ] |
| **CORS** | Cross-origin requests blocked if not whitelisted | [ ] |
| **SQL injection** | Parameterized queries prevent injection | [ ] |
| **XSS protection** | HTML entities escaped in responses | [ ] |
| **Rate limiting** | /api/auth endpoints limited to 5 req/min | [ ] |
| **HTTPS** | All traffic encrypted (no HTTP redirect loops) | [ ] |

---

## Accessibility Tests

| Component | Expected | Status |
|-----------|----------|--------|
| Form labels | Associated with inputs (for attribute) | [ ] |
| Focus management | Tab order logical | [ ] |
| Error messages | Associated with fields (aria-describedby) | [ ] |
| Button text | Descriptive, not just "Submit" | [ ] |
| Color contrast | WCAG AA minimum | [ ] |

---

## Cross-Browser Testing

| Browser | Registration | Login | Term Creation | Notes |
|---------|--------------|-------|----------------|-------|
| Chrome 120+ | [ ] | [ ] | [ ] | |
| Firefox 121+ | [ ] | [ ] | [ ] | |
| Safari 17+ | [ ] | [ ] | [ ] | |
| Edge 120+ | [ ] | [ ] | [ ] | |
| Mobile Safari | [ ] | [ ] | [ ] | |
| Chrome Mobile | [ ] | [ ] | [ ] | |

---

## Regression Tests (After Each Deploy)

Run these to ensure nothing broke:

```bash
# 1. Check all services healthy
docker-compose -f docker-compose.prod.yml ps

# 2. Test API endpoint
curl https://your-domain.com/api/health

# 3. Test frontend loads
curl -I https://your-domain.com

# 4. Check logs for errors
docker-compose -f docker-compose.prod.yml logs --tail=100 | grep ERROR

# 5. Quick user flow test (API level)
./test-user-flows.sh
```

---

## Known Issues & Workarounds

### Issue Template

```
**Title**: [Brief description]

**Severity**: [ ] Critical [ ] High [ ] Medium [ ] Low

**Affected Journey**: [Which journey]

**Steps to Reproduce**:
1. ...
2. ...

**Expected Behavior**: ...

**Actual Behavior**: ...

**Workaround** (if any): ...

**Environment**:
- Domain: your-domain.com
- Date: YYYY-MM-DD HH:MM:SS
- Browser: Chrome 120
- User Email: test@example.com
```

---

## Test Report Template

Date: YYYY-MM-DD
Tester: [Name]
Environment: Production

### Summary

- Total test cases: 8
- Passed: [ ]
- Failed: [ ]
- Blocked: [ ]

### Failed Tests

| Journey | Issue | Severity | Action |
|---------|-------|----------|--------|
| | | | |

### Notes

[Any additional observations, performance issues, etc.]

### Sign-off

- [ ] All critical tests passed
- [ ] No blockers
- [ ] Ready for user access

Tester: ______________________  Date: ____________
