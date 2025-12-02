# Frontend Authentication Integration - Manual Testing Guide

**Version:** 1.0
**Date:** 2025-11-15
**Estimated Time:** 30-45 minutes
**Prerequisites:** Backend running on http://localhost:8000

---

## Quick Start

```bash
# Terminal 1 - Start Backend
cd backend
python main.py

# Terminal 2 - Start Frontend
npm run dev

# Terminal 3 - Open Browser
open http://localhost:5173
```

---

## Test Environment Checklist

Before starting tests, verify:

- [ ] Backend API running (http://localhost:8000)
- [ ] Frontend dev server running (http://localhost:5173)
- [ ] PostgreSQL database running (docker-compose up -d)
- [ ] Browser DevTools open (F12)
- [ ] Network tab visible
- [ ] Console tab visible
- [ ] localStorage cleared (`localStorage.clear()`)

---

## Phase 1: Registration Flow (10 minutes)

### Test 1.1: New User Registration - Happy Path ✅

**Steps:**
1. Navigate to http://localhost:5173
2. Click **"Commencer Gratuitement"** button
3. Verify redirect to `/register`
4. Fill the registration form:
   - **First name:** `Test`
   - **Last name:** `User`
   - **Email:** `test@lexikon.com`
   - **Password:** `password123`
   - **Confirm password:** `password123`
   - **Language:** `Français`
5. Check **"I agree to Terms"** checkbox
6. Click **"Create account"** button

**Expected Results:**
- ✅ Loading state appears ("Creating account...")
- ✅ Button disabled during loading
- ✅ Network request to `POST /api/auth/register` (check Network tab)
- ✅ Response includes `access_token`, `refresh_token`, `user`
- ✅ Redirect to `/terms` page
- ✅ NavBar shows user initials "TU" in avatar
- ✅ NavBar shows "Test" as first name
- ✅ localStorage has `lexikon-auth` key (check Application tab)
- ✅ No errors in Console

**Actual Results:**
```
[Record any differences from expected]
```

---

### Test 1.2: Registration Validation - Password Mismatch ❌

**Steps:**
1. Go to `/register`
2. Fill form with:
   - First name: `Jane`
   - Last name: `Doe`
   - Email: `jane@example.com`
   - Password: `password123`
   - Confirm password: `different456` ← Intentionally different
3. Try to submit

**Expected Results:**
- ✅ Red error message below "Confirm password" field
- ✅ Error text: "Passwords do not match"
- ✅ Submit button disabled
- ✅ No API call made
- ✅ Form not submitted

**Actual Results:**
```
[Record results]
```

---

### Test 1.3: Registration Validation - Weak Password ❌

**Steps:**
1. Go to `/register`
2. Fill form with:
   - Password: `abc123` ← Only 6 characters
   - Confirm password: `abc123`
3. Try to submit

**Expected Results:**
- ✅ Error message: "Password must be at least 8 characters long"
- ✅ Form not submitted

**Actual Results:**
```
[Record results]
```

---

### Test 1.4: Registration - Duplicate Email ❌

**Steps:**
1. Go to `/register`
2. Try to register with email `test@lexikon.com` (already used in Test 1.1)
3. Use valid password: `password123`
4. Submit

**Expected Results:**
- ✅ API returns error
- ✅ Error alert displayed: "This email is already registered"
- ✅ User stays on `/register` page
- ✅ Form remains filled
- ✅ User not authenticated

**Actual Results:**
```
[Record results]
```

---

## Phase 2: Login Flow (10 minutes)

### Test 2.1: Logout First

**Steps:**
1. If authenticated, click user avatar in NavBar
2. Click **"Sign out"**

**Expected Results:**
- ✅ Redirect to homepage `/`
- ✅ NavBar shows "Sign in" and "Get started" buttons
- ✅ localStorage `lexikon-auth` cleared
- ✅ Homepage shows guest CTAs

---

### Test 2.2: Login - Happy Path ✅

**Steps:**
1. From homepage, click **"Se Connecter"**
2. Verify at `/login`
3. Fill login form:
   - Email: `test@lexikon.com`
   - Password: `password123`
4. Check "Remember me" (optional)
5. Click **"Sign in"**

**Expected Results:**
- ✅ Loading state ("Signing in...")
- ✅ Network request to `POST /api/auth/login`
- ✅ Response includes tokens and user
- ✅ Redirect to `/terms`
- ✅ NavBar shows user "Test"
- ✅ localStorage updated
- ✅ No errors

**Actual Results:**
```
[Record results]
```

---

### Test 2.3: Login - Invalid Credentials ❌

**Steps:**
1. Go to `/login`
2. Enter:
   - Email: `test@lexikon.com`
   - Password: `wrongpassword` ← Incorrect
3. Submit

**Expected Results:**
- ✅ Error alert displayed: "Invalid email or password"
- ✅ Form stays at `/login`
- ✅ User not authenticated
- ✅ localStorage not updated

**Actual Results:**
```
[Record results]
```

---

### Test 2.4: Login - Nonexistent User ❌

**Steps:**
1. Go to `/login`
2. Enter:
   - Email: `doesnotexist@example.com`
   - Password: `anypassword`
3. Submit

**Expected Results:**
- ✅ Error alert: "Invalid email or password"
- ✅ User not authenticated

**Actual Results:**
```
[Record results]
```

---

## Phase 3: Protected Routes (5 minutes)

### Test 3.1: Access Protected Route When Not Authenticated

**Steps:**
1. Logout if authenticated
2. Manually navigate to http://localhost:5173/terms
3. Press Enter

**Expected Results:**
- ✅ Redirect to `/login`
- ✅ URL includes `?redirect=/terms` (return URL)
- ✅ Not shown `/terms` page content

**Actual Results:**
```
[Record results]
```

---

### Test 3.2: Access Guest-Only Route When Authenticated

**Steps:**
1. Login first (use Test 2.2)
2. Manually navigate to http://localhost:5173/login
3. Press Enter

**Expected Results:**
- ✅ Redirect to `/terms` (can't access login when already logged in)
- ✅ Not shown login form

**Actual Results:**
```
[Record results]
```

---

### Test 3.3: Return URL After Login

**Steps:**
1. Logout
2. Try to access `/profile`
3. Verify redirect to `/login?redirect=/profile`
4. Login with valid credentials
5. After login completes

**Expected Results:**
- ✅ Redirect to `/profile` (the original destination)
- ✅ Not redirect to `/terms`

**Note:** This test currently may not work (return URL not implemented). Expected behavior for future.

**Actual Results:**
```
[Record results]
```

---

## Phase 4: User Profile (10 minutes)

### Test 4.1: View Profile

**Steps:**
1. Login if not authenticated
2. Click user avatar in NavBar
3. Click **"My Profile"**

**Expected Results:**
- ✅ Navigate to `/profile`
- ✅ Personal Information section shows:
  - Full name: "Test User"
  - Email: "test@lexikon.com"
  - Language: "FR"
  - Member since: [date]
  - Account status: "Active" (green badge)
- ✅ Subscription section shows "Quick Project"
- ✅ Security section has "Change password" button

**Actual Results:**
```
[Record results]
```

---

### Test 4.2: Change Password - Happy Path ✅

**Steps:**
1. On `/profile` page
2. Click **"Change password"** button
3. Fill form:
   - Current password: `password123`
   - New password: `newpassword123`
   - Confirm new password: `newpassword123`
4. Click **"Save new password"**

**Expected Results:**
- ✅ Network request to `POST /api/auth/change-password`
- ✅ Success alert: "Password changed successfully"
- ✅ Form hidden
- ✅ Button returns to "Change password"

**Verify New Password:**
5. Logout
6. Login with:
   - Email: `test@lexikon.com`
   - Password: `newpassword123` ← New password
7. Should login successfully

**Actual Results:**
```
[Record results]
```

---

### Test 4.3: Change Password - Validation ❌

**Steps:**
1. On `/profile`, click "Change password"
2. Fill with mismatched passwords:
   - Current password: `newpassword123`
   - New password: `another123`
   - Confirm: `different123` ← Mismatch
3. Try to submit

**Expected Results:**
- ✅ Error shown: "Passwords do not match"
- ✅ Button disabled
- ✅ No API call

**Actual Results:**
```
[Record results]
```

---

### Test 4.4: Change Password - Wrong Current Password ❌

**Steps:**
1. Click "Change password"
2. Fill:
   - Current password: `wrongpassword` ← Incorrect
   - New password: `validpass123`
   - Confirm: `validpass123`
3. Submit

**Expected Results:**
- ✅ API error returned
- ✅ Error alert: "Current password is incorrect"
- ✅ Password not changed

**Actual Results:**
```
[Record results]
```

---

## Phase 5: Session Persistence (5 minutes)

### Test 5.1: Session Survives Page Reload

**Steps:**
1. Login (if not authenticated)
2. Verify at `/terms` and NavBar shows user
3. Press F5 (hard reload)
4. Wait for page load

**Expected Results:**
- ✅ Still authenticated after reload
- ✅ NavBar still shows user
- ✅ Can access protected routes
- ✅ localStorage still has auth data

**Actual Results:**
```
[Record results]
```

---

### Test 5.2: Session Survives Browser Close/Reopen

**Steps:**
1. Login
2. Close browser completely
3. Reopen browser
4. Navigate to http://localhost:5173

**Expected Results:**
- ✅ Still authenticated
- ✅ Homepage shows "Bienvenue, Test!"
- ✅ NavBar shows user

**Actual Results:**
```
[Record results]
```

---

### Test 5.3: Logout Clears Session

**Steps:**
1. Login
2. Note localStorage has `lexikon-auth`
3. Click user menu → "Sign out"
4. Check localStorage

**Expected Results:**
- ✅ Redirect to homepage
- ✅ localStorage `lexikon-auth` removed
- ✅ NavBar shows guest buttons
- ✅ Can't access `/terms` without redirect to login

**Actual Results:**
```
[Record results]
```

---

## Phase 6: Navigation & UI (5 minutes)

### Test 6.1: NavBar - Guest State

**Steps:**
1. Logout
2. Observe NavBar

**Expected Results:**
- ✅ Logo "Lexikon" visible (links to `/`)
- ✅ "Sign in" button visible
- ✅ "Get started" button visible (primary style)
- ✅ No user menu visible
- ✅ No "My Terms" / "Create Term" links

**Actual Results:**
```
[Record results]
```

---

### Test 6.2: NavBar - Authenticated State

**Steps:**
1. Login
2. Observe NavBar

**Expected Results:**
- ✅ Logo visible
- ✅ "My Terms" link visible
- ✅ "Create Term" link visible
- ✅ User avatar visible (initials "TU")
- ✅ User first name visible ("Test")
- ✅ Dropdown arrow visible
- ✅ No "Sign in" / "Get started" buttons

**Actual Results:**
```
[Record results]
```

---

### Test 6.3: User Menu Dropdown

**Steps:**
1. Login
2. Click user avatar/name in NavBar
3. Observe dropdown menu

**Expected Results:**
- ✅ Menu opens below avatar
- ✅ Header shows:
  - Full name: "Test User"
  - Email: "test@lexikon.com"
- ✅ Menu items:
  - 👤 My Profile
  - 📚 My Terms
  - [divider]
  - 🚪 Sign out (red text)
- ✅ Clicking "My Profile" navigates to `/profile`
- ✅ Clicking "My Terms" navigates to `/terms`
- ✅ Clicking "Sign out" logs out

**Actual Results:**
```
[Record results]
```

---

### Test 6.4: User Menu Close on Outside Click

**Steps:**
1. Login
2. Click user avatar to open menu
3. Click anywhere on the page (outside menu)

**Expected Results:**
- ✅ Menu closes
- ✅ Arrow returns to down position

**Actual Results:**
```
[Record results]
```

---

### Test 6.5: Homepage Auth Awareness

**Steps:**
1. Logout, go to homepage
2. Observe CTAs

**Guest State:**
- ✅ "Commencer Gratuitement" button (primary)
- ✅ "Se Connecter" button (outline)
- ✅ No welcome message

**Steps (continued):**
3. Login
4. Go to homepage

**Authenticated State:**
- ✅ "Mes Ontologies →" button (primary)
- ✅ "Mon Profil" button (outline)
- ✅ Welcome message: "Bienvenue, Test! 👋"

**Actual Results:**
```
[Record results]
```

---

## Phase 7: Error Handling (5 minutes)

### Test 7.1: Network Error - Backend Down

**Steps:**
1. Logout
2. Stop backend server (Ctrl+C in Terminal 1)
3. Try to login with any credentials
4. Submit

**Expected Results:**
- ✅ Error alert: "Failed to connect to server" or "Network error"
- ✅ User not authenticated
- ✅ Form remains on `/login`

**Cleanup:**
- Restart backend: `python main.py`

**Actual Results:**
```
[Record results]
```

---

### Test 7.2: API Error Handling

**Steps:**
1. Ensure backend running
2. Try to register with existing email `test@lexikon.com`
3. Observe error handling

**Expected Results:**
- ✅ Error displayed in Alert component
- ✅ Error message from API shown
- ✅ User can retry
- ✅ No crash or blank page

**Actual Results:**
```
[Record results]
```

---

## Phase 8: Browser Compatibility (Optional, 15 minutes)

Test the following flows in each browser:
- Registration
- Login
- Profile view
- Logout

### Browsers to Test:

**Chrome (latest):**
- [ ] Registration works
- [ ] Login works
- [ ] Session persists
- [ ] UI displays correctly

**Firefox (latest):**
- [ ] Registration works
- [ ] Login works
- [ ] Session persists
- [ ] UI displays correctly

**Safari (latest):**
- [ ] Registration works
- [ ] Login works
- [ ] Session persists
- [ ] UI displays correctly

**Edge (latest):**
- [ ] Registration works
- [ ] Login works
- [ ] Session persists
- [ ] UI displays correctly

---

## Phase 9: Accessibility (Optional, 10 minutes)

### Test 9.1: Keyboard Navigation

**Steps:**
1. Go to `/login`
2. Use only Tab key to navigate
3. Try to complete login using only keyboard

**Expected Results:**
- ✅ Can tab through all form fields
- ✅ Can tab to buttons
- ✅ Can submit with Enter key
- ✅ Focus indicators visible
- ✅ Tab order logical (email → password → buttons)

**Actual Results:**
```
[Record results]
```

---

### Test 9.2: Screen Reader (Optional)

With screen reader enabled (NVDA, JAWS, VoiceOver):

**Expected Results:**
- ✅ Form labels announced
- ✅ Error messages announced
- ✅ Button states announced
- ✅ Navigation accessible

**Actual Results:**
```
[Record results]
```

---

## Summary & Sign-Off

### Test Execution Summary

**Date Tested:** ________________
**Tester:** ________________
**Environment:**
- Backend version: ________________
- Frontend commit: ________________
- Browser: ________________

### Results Overview

| Phase | Tests Passed | Tests Failed | Critical Bugs |
|-------|-------------|--------------|---------------|
| Phase 1: Registration | __/4 | __/4 | __ |
| Phase 2: Login | __/4 | __/4 | __ |
| Phase 3: Protected Routes | __/3 | __/3 | __ |
| Phase 4: User Profile | __/4 | __/4 | __ |
| Phase 5: Session Persistence | __/3 | __/3 | __ |
| Phase 6: Navigation & UI | __/5 | __/5 | __ |
| Phase 7: Error Handling | __/2 | __/2 | __ |
| **TOTAL** | __/29 | __/29 | __ |

### Bugs Found

**Bug #1:**
- **Severity:** [Critical / Major / Minor]
- **Test:** [Test number]
- **Description:**
- **Steps to Reproduce:**
- **Expected:**
- **Actual:**

**Bug #2:**
[...]

### Sign-Off

**Status:** [ ] PASS / [ ] FAIL / [ ] PASS WITH ISSUES

**Tester Signature:** ________________
**Date:** ________________

**Notes:**
```
[Additional comments, observations, or recommendations]
```

---

## Troubleshooting

### Common Issues

**Issue:** Can't login, getting 401 error
- **Solution:** Check backend is running, database initialized

**Issue:** localStorage not persisting
- **Solution:** Check browser privacy settings, try incognito mode

**Issue:** OAuth buttons don't work
- **Solution:** OAuth not fully implemented, expected behavior

**Issue:** Network errors
- **Solution:** Verify backend URL is http://localhost:8000

**Issue:** Tokens expired
- **Solution:** Logout and login again

---

## Next Steps After Testing

1. Log all bugs in GitHub Issues
2. Prioritize critical bugs
3. Fix P0/P1 bugs
4. Re-test failed scenarios
5. Update documentation with findings
6. Plan automated tests for regression prevention

---

**End of Manual Testing Guide**
