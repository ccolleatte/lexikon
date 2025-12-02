# ADR-0002: JWT Authentication Strategy

**Date**: 2025-11-16
**Status**: Accepted (partial implementation)
**Deciders**: [Lead Dev], [Security Lead]
**Consulted**: OAuth specialist, frontend lead
**Informed**: Full dev team

## Context

Lexikon requires user authentication for:
- Securing API endpoints
- Tracking who creates/modifies terms
- Implementing role-based access (free/paid tiers)
- OAuth integration (GitHub, Google)

**Current state**:
- JWT infrastructure implemented in `backend/auth/jwt.py` (90% complete)
- But not integrated into API endpoints (fake tokens used in Sprint 1)
- OAuth skeleton present but not working
- Frontend stores tokens in localStorage
- No refresh token flow implemented

**Problem**: Fake tokens mean:
- Cannot actually validate authentication
- Security is theater, not real
- Frontend not testing real auth flows
- Cannot go to production with current state

## Decision

**Implement production-grade JWT authentication with:**
1. Real JWT generation + validation (not fake tokens)
2. Bearer token in Authorization header
3. Access tokens (1h) + refresh tokens (7d)
4. Middleware enforcement (reject unauthenticated requests)
5. OAuth integration (Phase 2)

### Rationale

**Why JWT (vs alternatives)**:
- **vs sessions**: Stateless, scales to load balancer
- **vs API keys**: Better for user-facing apps, shorter lived
- **vs OAuth-only**: Need fallback for email/password flow
- **vs JWTs alone**: Refresh tokens enable secure rotation

**Why this specific design**:
- Access tokens (short-lived) reduce harm if compromised
- Refresh tokens in HTTP-only cookies (if browser) vs localStorage (if SPA)
- Middleware enforcement ensures no endpoint leaks
- Standard OpenID Connect patterns (easier to audit)

## Consequences

### Positives
✅ Industry-standard authentication
✅ Scales horizontally (stateless)
✅ Can integrate with OAuth providers
✅ Front-end can implement conditional rendering (logged-in vs guest)
✅ Audit trail: tokens linked to user IDs

### Negatives
❌ Token revocation requires extra logic (token blacklist)
❌ Front-end complexity: Store/refresh tokens properly
❌ Logout not instant (token valid until expiration)
❌ Requires HTTPS in production (token in header exposed otherwise)

### Mitigations
- Token blacklist service for immediate logout (Phase 2)
- Refresh token rotation policy (each use issues new refresh token)
- Short expiration times (1h access, 7d refresh)
- HTTPS everywhere (not in dev, required in prod)
- Secure refresh endpoint (same-origin only)

## Alternatives Considered

### Alternative A: OAuth-only (no email/password)
**Pros**:
- No password management burden
- Simpler auth server
- Users prefer OAuth

**Cons**:
- GitHub/Google outage = users blocked
- No fallback if provider removed token
- Complex multi-provider logic
- Requires working OAuth setup (not in v0.1)

**Rejection**: Valid for future, but MVP needs email/password fallback.

### Alternative B: Session-based (server-side sessions)
**Pros**:
- Easy logout (delete session immediately)
- Can revoke anytime
- More secure (token not exposed to frontend)

**Cons**:
- Requires session store (Redis, database)
- Doesn't scale well across multiple servers
- Heavier on server (memory)
- Conflicts with deployment (serverless, load balancers)

**Rejection**: Harder to scale. Lexikon may need horizontal scaling soon.

### Alternative C: API Keys only
**Pros**:
- Simple, works for machine-to-machine

**Cons**:
- Not suitable for user-facing apps
- Long-lived = higher compromise risk
- Rotation harder

**Rejection**: Viable as tier 2, but JWT better for MVP.

## Activation Criteria

### Requirement 1: Token Validation (CRITICAL)
**Must-have for v0.1 release**:
- Every endpoint validates Authorization header
- Invalid/expired tokens → 401 Unauthorized
- No endpoint accepts fake tokens

### Requirement 2: Frontend Integration
**Must-have for v0.1 release**:
- Frontend stores real JWT tokens
- Frontend sends tokens in Authorization header
- Frontend handles 401 responses (logout + redirect to login)

### Requirement 3: Refresh Flow
**Nice-to-have for v0.2**:
- POST /api/auth/refresh exchanges old token for new
- Reduces window of vulnerability
- Enables token rotation

### Requirement 4: OAuth Integration
**Phase 2 (v0.2+)**:
- GitHub provider working
- Google provider working
- Single sign-on working

## Rollback Plan

### Scenario: JWT security vulnerability discovered

**If vulnerability in library** (e.g., python-jose):
1. Upgrade to patched version
2. Force re-authentication for all users (invalidate all issued tokens)
3. **Time**: 1-2 hours

**If JWT design flaw** (e.g., need to revoke tokens immediately):
1. Implement token blacklist service:
   - Redis set: `revoked_tokens:{jti}`
   - Every validation checks blacklist
2. Alternative: Switch to session-based (1 week refactor)
3. **Time**: 4-8 hours to blacklist, 1 week to sessions

## Related Decisions
- ADR-0005-postgres-primary: User auth data in PostgreSQL
- ADR-0003-svelte-framework: Frontend token storage
- ADR-0004-fastapi-backend: Backend token generation

## Implementation Roadmap

### Phase 1: JWT Core (TIER-1 BLOCKER, Week 1)
**Sprint completion**: < 3 hours
- [x] `backend/auth/jwt.py` - Implemented
- [ ] Integrate into `api/users.py` - Generate real tokens on signup
- [ ] `auth/middleware.py` - Validate tokens on protected endpoints
- [ ] Frontend: Update auth store to use real tokens
- [ ] E2E test: Full auth flow

### Phase 2: Refresh Tokens (TIER-2, Week 2-3)
**Sprint completion**: 4-6 hours
- [ ] `api/auth.py` - Implement refresh endpoint
- [ ] Frontend: Implement refresh token logic
- [ ] Tests: Refresh flow + token rotation

### Phase 3: Token Revocation (v0.2+)
**Time**: 8 hours
- [ ] Redis blacklist service
- [ ] Logout immediately invalidates token
- [ ] Tests: Revocation

### Phase 4: OAuth Integration (v0.2+)
**Time**: 3-5 days
- [ ] GitHub OAuth integration
- [ ] Google OAuth integration
- [ ] Frontend: OAuth buttons
- [ ] Tests: OAuth flow

## Security Checklist

Before shipping:
- [ ] JWT secret is > 32 chars (currently "dev-jwt-secret-change-in-production")
- [ ] Tokens never logged (avoid leaking in logs)
- [ ] HTTPS enforced in production
- [ ] Token expiration tested (1h access, 7d refresh)
- [ ] Invalid signatures rejected
- [ ] Expired tokens rejected
- [ ] Malformed tokens rejected
- [ ] Authorization header required (no body tokens)

## Testing Strategy

### Unit Tests
```
test_jwt_generation()
test_jwt_validation()
test_jwt_expiration()
test_token_refresh()
test_invalid_signature_rejected()
test_expired_token_rejected()
```

### Integration Tests
```
test_login_endpoint_returns_token()
test_protected_endpoint_requires_token()
test_protected_endpoint_401_without_token()
test_protected_endpoint_401_with_invalid_token()
```

### E2E Tests
```
test_signup_login_get_terms_flow()
test_logout_invalidates_access()
test_token_expiration_forces_refresh()
```

## Approval

- Technical Review: ______ (date)
- Security Review: ______ (date)
- PM Sign-off: ______ (date)

---

**Next Review Date**: After Phase 1 implementation (v0.1 release)
**Last Updated**: 2025-11-16
