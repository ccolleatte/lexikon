# Testing Strategy - Frontend Authentication Integration

## Overview

This document outlines the comprehensive testing strategy for the frontend authentication integration completed in Sprint 2.

## Test Pyramid

```
       E2E Tests (Manual)
           /\
          /  \
         /    \
        /------\
       / Inte- \
      / gration \
     /----------\
    /   Unit     \
   /--------------\
```

## 1. Unit Tests

### Auth Store (`src/lib/stores/auth.ts`)

**What to test:**
- ✅ Initial state (unauthenticated)
- ✅ `login()` - sets user and tokens
- ✅ `logout()` - clears state
- ✅ `updateUser()` - updates user info
- ✅ `updateAccessToken()` - updates token
- ✅ localStorage persistence
- ✅ Derived stores (isAuthenticated, user, accessToken)
- ✅ `hasAdoptionLevel()` - level checking logic

**Test cases:**
```typescript
describe('authStore', () => {
  beforeEach(() => {
    localStorage.clear();
    authStore.reset();
  });

  it('should initialize with unauthenticated state')
  it('should login and set auth state')
  it('should logout and clear state')
  it('should update user information')
  it('should update access token')
  it('should persist to localStorage')
  it('should restore from localStorage')
  it('should compute isAuthenticated correctly')
  it('should check adoption level correctly')
});
```

### Auth Utilities (`src/lib/utils/auth.ts`)

**What to test:**
- ✅ `login()` - calls API and updates store
- ✅ `register()` - calls API and updates store
- ✅ `logout()` - calls API and clears store
- ✅ `changePassword()` - calls API with correct data
- ✅ OAuth URL generation
- ✅ Error handling

**Test cases:**
```typescript
describe('auth utilities', () => {
  it('should call login API and update store')
  it('should call register API with correct data')
  it('should logout and clear store')
  it('should change password with validation')
  it('should handle API errors gracefully')
  it('should generate OAuth URLs correctly')
});
```

### API Client (`src/lib/utils/api.ts`)

**What to test:**
- ✅ JWT token injection in headers
- ✅ 401 error detection
- ✅ Error handling
- ✅ Request/response transformation

**Test cases:**
```typescript
describe('API client', () => {
  it('should inject JWT token when authenticated')
  it('should not inject token when not authenticated')
  it('should handle 401 errors')
  it('should handle network errors')
  it('should transform API responses correctly')
});
```

## 2. Component Tests

### Login Page (`src/routes/login/+page.svelte`)

**What to test:**
- ✅ Renders form correctly
- ✅ Form validation (email, password)
- ✅ Submit calls login()
- ✅ Displays errors
- ✅ OAuth buttons present
- ✅ Redirect when authenticated

**Test cases:**
```typescript
describe('Login Page', () => {
  it('should render login form')
  it('should validate email format')
  it('should require password')
  it('should call login on submit')
  it('should display API errors')
  it('should show loading state')
  it('should redirect if already authenticated')
});
```

### Register Page (`src/routes/register/+page.svelte`)

**What to test:**
- ✅ Renders form correctly
- ✅ Password confirmation validation
- ✅ Password strength validation
- ✅ Submit calls register()
- ✅ Displays errors
- ✅ Language selection

**Test cases:**
```typescript
describe('Register Page', () => {
  it('should render registration form')
  it('should validate password match')
  it('should validate password strength (8+ chars)')
  it('should call register on submit')
  it('should display validation errors')
  it('should show loading state')
});
```

### NavBar Component (`src/lib/components/NavBar.svelte`)

**What to test:**
- ✅ Shows guest buttons when not authenticated
- ✅ Shows user menu when authenticated
- ✅ User menu toggle
- ✅ Logout functionality
- ✅ User initials display

**Test cases:**
```typescript
describe('NavBar', () => {
  it('should show Sign in/Get started for guests')
  it('should show user menu when authenticated')
  it('should toggle user menu on click')
  it('should display user initials')
  it('should call logout on sign out')
  it('should close menu on outside click')
});
```

### Profile Page (`src/routes/profile/+page.svelte`)

**What to test:**
- ✅ Displays user information
- ✅ Change password form
- ✅ Password validation
- ✅ Submit calls changePassword()
- ✅ Success/error messages

**Test cases:**
```typescript
describe('Profile Page', () => {
  it('should display user information')
  it('should show change password form')
  it('should validate password match')
  it('should call changePassword on submit')
  it('should display success message')
  it('should display error messages')
});
```

## 3. Integration Tests

### Authentication Flow

**Test scenarios:**
1. **Complete registration flow**
   - Fill registration form
   - Submit
   - Verify store updated
   - Verify redirect to /terms

2. **Complete login flow**
   - Fill login form
   - Submit
   - Verify store updated
   - Verify redirect to /terms

3. **Protected route access**
   - Try to access /terms unauthenticated
   - Verify redirect to /login
   - Login
   - Verify redirect back to /terms

4. **Logout flow**
   - Authenticated user
   - Click logout
   - Verify store cleared
   - Verify redirect to homepage

5. **Session persistence**
   - Login
   - Reload page
   - Verify still authenticated

## 4. Manual E2E Tests

### Test Suite 1: Registration & Login

**TC-001: New User Registration**
- [ ] Navigate to homepage
- [ ] Click "Commencer Gratuitement"
- [ ] Fill registration form with valid data
- [ ] Submit form
- [ ] Verify redirect to /terms
- [ ] Verify NavBar shows user name
- [ ] Verify user menu works

**TC-002: Email/Password Login**
- [ ] Logout if authenticated
- [ ] Click "Se Connecter"
- [ ] Fill login form
- [ ] Submit
- [ ] Verify redirect to /terms
- [ ] Verify NavBar shows user

**TC-003: Login with Invalid Credentials**
- [ ] Go to /login
- [ ] Enter wrong email/password
- [ ] Submit
- [ ] Verify error message displayed
- [ ] Verify not authenticated

**TC-004: Registration Validation**
- [ ] Go to /register
- [ ] Enter mismatched passwords
- [ ] Verify error shown
- [ ] Enter password < 8 chars
- [ ] Verify error shown
- [ ] Enter invalid email
- [ ] Verify error shown

### Test Suite 2: Protected Routes

**TC-005: Access Protected Route When Not Authenticated**
- [ ] Logout
- [ ] Try to access /terms directly
- [ ] Verify redirect to /login
- [ ] Verify return URL preserved

**TC-006: Guest-Only Routes When Authenticated**
- [ ] Login
- [ ] Try to access /login
- [ ] Verify redirect to /terms
- [ ] Try to access /register
- [ ] Verify redirect to /terms

### Test Suite 3: User Profile

**TC-007: View Profile**
- [ ] Login
- [ ] Click user menu
- [ ] Click "My Profile"
- [ ] Verify profile page shows correct info
- [ ] Verify all fields displayed

**TC-008: Change Password**
- [ ] Go to /profile
- [ ] Click "Change password"
- [ ] Enter current password
- [ ] Enter new password
- [ ] Confirm new password
- [ ] Submit
- [ ] Verify success message
- [ ] Logout and login with new password

**TC-009: Change Password Validation**
- [ ] Go to /profile
- [ ] Click "Change password"
- [ ] Enter mismatched new passwords
- [ ] Verify error shown
- [ ] Enter weak password
- [ ] Verify error shown

### Test Suite 4: Session Management

**TC-010: Session Persistence**
- [ ] Login
- [ ] Verify authenticated
- [ ] Refresh page (F5)
- [ ] Verify still authenticated
- [ ] Verify user data intact

**TC-011: Logout**
- [ ] Login
- [ ] Click user menu
- [ ] Click "Sign out"
- [ ] Verify redirect to homepage
- [ ] Verify NavBar shows guest buttons
- [ ] Try to access /terms
- [ ] Verify redirect to /login

**TC-012: Session Expiry (Manual)**
- [ ] Login
- [ ] Wait for token expiry (60 min)
- [ ] Try API call
- [ ] Verify 401 error
- [ ] Verify redirect to login

### Test Suite 5: Navigation & UI

**TC-013: NavBar Guest State**
- [ ] Logout
- [ ] Verify "Sign in" button visible
- [ ] Verify "Get started" button visible
- [ ] Click each button
- [ ] Verify correct navigation

**TC-014: NavBar Authenticated State**
- [ ] Login
- [ ] Verify user avatar visible
- [ ] Verify user name visible
- [ ] Click avatar/name
- [ ] Verify menu opens
- [ ] Verify menu items present
- [ ] Click outside menu
- [ ] Verify menu closes

**TC-015: Homepage Auth Awareness**
- [ ] Visit homepage as guest
- [ ] Verify "Commencer Gratuitement" visible
- [ ] Login
- [ ] Visit homepage
- [ ] Verify "Mes Ontologies" visible
- [ ] Verify welcome message with name

### Test Suite 6: Error Handling

**TC-016: Network Error During Login**
- [ ] Stop backend server
- [ ] Try to login
- [ ] Verify error message displayed
- [ ] Verify not authenticated

**TC-017: Malformed API Response**
- [ ] (Requires backend mock)
- [ ] Trigger malformed response
- [ ] Verify graceful error handling

**TC-018: LocalStorage Unavailable**
- [ ] Disable localStorage in browser
- [ ] Try to login
- [ ] Verify warning or degraded mode
- [ ] Enable localStorage
- [ ] Verify normal operation

### Test Suite 7: OAuth (Requires Backend Setup)

**TC-019: Google OAuth Login**
- [ ] Click "Google" button
- [ ] Verify redirect to Google
- [ ] Complete Google auth
- [ ] Verify redirect back to app
- [ ] Verify authenticated
- [ ] Verify user info from Google

**TC-020: GitHub OAuth Login**
- [ ] Click "GitHub" button
- [ ] Verify redirect to GitHub
- [ ] Complete GitHub auth
- [ ] Verify redirect back
- [ ] Verify authenticated
- [ ] Verify user info from GitHub

**TC-021: OAuth Cancellation**
- [ ] Click OAuth button
- [ ] Cancel on provider page
- [ ] Verify return to login
- [ ] Verify error message
- [ ] Verify not authenticated

## 5. Cross-Browser Testing

Test on:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile Chrome
- [ ] Mobile Safari

## 6. Accessibility Testing

- [ ] Keyboard navigation works
- [ ] Tab order is logical
- [ ] Focus indicators visible
- [ ] Form labels present
- [ ] Error messages announced
- [ ] ARIA attributes correct

## 7. Performance Testing

- [ ] Initial page load < 2s
- [ ] Auth state restoration < 100ms
- [ ] Login/register response < 1s
- [ ] Token injection overhead < 10ms
- [ ] localStorage read/write < 50ms

## Test Execution Plan

### Phase 1: Unit Tests (Automated)
**Duration:** 2-3 hours
- Setup Vitest + Testing Library
- Write unit tests for stores
- Write unit tests for utilities
- Achieve 80%+ coverage

### Phase 2: Component Tests (Automated)
**Duration:** 3-4 hours
- Write component tests
- Test user interactions
- Test error states
- Achieve 70%+ coverage

### Phase 3: Manual E2E Tests
**Duration:** 1-2 hours
- Execute all test suites
- Document results
- Log bugs

### Phase 4: Cross-Browser Testing
**Duration:** 1 hour
- Test on all browsers
- Document browser-specific issues

## Success Criteria

- ✅ 80%+ unit test coverage
- ✅ 70%+ component test coverage
- ✅ All critical paths tested (login, register, logout, profile)
- ✅ 0 critical bugs
- ✅ All test suites pass
- ✅ Documentation complete

## Test Environment Setup

```bash
# Install dependencies
npm install -D vitest @testing-library/svelte @testing-library/jest-dom
npm install -D @testing-library/user-event jsdom

# Run tests
npm run test

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode
npm run test:watch
```

## Bug Tracking

Use GitHub Issues with labels:
- `bug` - Functionality broken
- `test-failure` - Test found issue
- `auth` - Authentication related
- `critical` - Blocks usage
- `minor` - Cosmetic/UX issue

## Regression Testing

After any auth-related changes:
- [ ] Re-run full unit test suite
- [ ] Re-run component tests
- [ ] Execute TC-001 through TC-015 minimum
- [ ] Verify no regressions

## Metrics to Track

- Test execution time
- Coverage percentage
- Number of bugs found
- Bug severity distribution
- Time to fix bugs
- Regression rate

---

**Last Updated:** 2025-11-15
**Next Review:** After test implementation
**Status:** Planning Complete, Ready for Execution
