# Technical Debt Tracker

**Last Updated:** November 18, 2025
**Total Items:** 12
**Critical Debt:** 2 items

---

## 📊 Executive Summary

| Status | Count | Impact |
|--------|-------|--------|
| ✅ Resolved | 1 | CVSS 9.8 (SQL Injection) |
| 🔄 In Progress | 0 | - |
| ⏳ Backlog (TIER-2) | 9 | ~40 hours effort |
| 📋 Post-v0.1 | 2 | ~2 hours effort |
| **Total Effort** | **~42 hours** | - |

---

## 🔴 Critical Debt (Blocking Production)

### 1. ✅ SQL Injection in Database Initialization (RESOLVED)
- **CVSS:** 9.8 CRITICAL
- **Status:** ✅ RESOLVED (Commit a327653)
- **TIER:** TIER-1
- **Priority:** P0
- **Effort:** 1h
- **Details:** Table name validation missing in init_postgres.py show_table_stats()
- **Fix:** Whitelist validation + identifier escaping

### 2. ✅ BOLA - Broken Object Level Authorization (RESOLVED)
- **CVSS:** 8.6 HIGH
- **Status:** ✅ RESOLVED (Commit 6172f87)
- **TIER:** TIER-1
- **Priority:** P0
- **Effort:** 2-3h
- **Details:** Missing ownership checks on /api/terms endpoints
- **Fix:** Migrated to SQLAlchemy, added get_current_user dependency, ownership verification

### 3. ✅ Hardcoded Secrets in Version Control (RESOLVED)
- **CVSS:** 9.1 CRITICAL
- **Status:** ✅ RESOLVED (Commit 8303db0)
- **TIER:** TIER-1
- **Priority:** P0
- **Effort:** 1-2h
- **Details:** Database passwords hardcoded in docker-compose.yml
- **Fix:** Environment variables, .env.example, .env.local template

---

## 🟡 Backlog Debt (TIER-2 & TIER-3)

### 4. ⏳ Neo4j Integration & Migration
- **CVSS:** N/A (Data Integrity)
- **Status:** ⏳ TODO
- **TIER:** TIER-2
- **Priority:** P1 (Graph queries)
- **Effort:** 8-10h
- **Details:** Neo4j driver not integrated; graph relationships not persisted
- **Blockers:** None
- **Dependencies:** PostgreSQL stable (✅ done)
- **Next Steps:** Install py2neo, design graph schema, implement relationship queries
- **Impacts:** Term relationships, knowledge graph features

### 5. ⏳ Rate Limiting Implementation
- **CVSS:** N/A (DoS Prevention)
- **Status:** ⏳ TODO
- **TIER:** TIER-2
- **Priority:** P1 (Production requirement)
- **Effort:** 3-4h
- **Details:** No rate limiting on API endpoints; vulnerable to brute force/DoS
- **Library:** SlowAPI (FastAPI-native)
- **Scope:**
  - Auth endpoints: 5 req/min per IP
  - API endpoints: 100 req/min per user
  - Public endpoints: 1000 req/min per IP
- **Next Steps:** Install slowapi, configure limits, add monitoring

### 6. ⏳ Input Validation & Sanitization
- **CVSS:** N/A (XSS/Injection Prevention)
- **Status:** ⏳ TODO
- **TIER:** TIER-2
- **Priority:** P1 (Security)
- **Effort:** 4-5h
- **Details:** Minimal input validation on create_term, register endpoints
- **Current:** Pydantic models only
- **Missing:**
  - Length limits (term.definition max 5000 chars)
  - HTML/Script injection checks
  - Reserved keyword validation
  - Null byte sanitization
- **Next Steps:** Enhanced Pydantic validators, bleach library for HTML

### 7. ⏳ HTTPS Enforcement & TLS
- **CVSS:** N/A (Transport Security)
- **Status:** ⏳ TODO
- **TIER:** TIER-3
- **Priority:** P1 (Production)
- **Effort:** 2h
- **Details:** No HTTPS enforcement; cleartext communication possible
- **Current:** HTTP only (localhost dev)
- **Production:** Requires TLS certificates + middleware
- **Next Steps:** Add https_only middleware, configure nginx reverse proxy

### 8. ⏳ HSTS & Security Headers
- **CVSS:** N/A (Protocol Security)
- **Status:** ⏳ TODO
- **TIER:** TIER-3
- **Priority:** P2 (Hardening)
- **Effort:** 1h
- **Details:** Missing security headers (HSTS, CSP, X-Frame-Options, etc.)
- **Headers Needed:**
  - Strict-Transport-Security (31536000s)
  - Content-Security-Policy (restrict sources)
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
  - X-XSS-Protection: 1; mode=block
- **Next Steps:** FastAPI middleware

### 9. ⏳ CORS Hardcoding Removal
- **CVSS:** N/A (Configuration)
- **Status:** ⏳ TODO (Partial - hardcoded origins in main.py:21)
- **TIER:** TIER-2
- **Priority:** P1 (Flexibility)
- **Effort:** 0.5h
- **Details:** CORS origins hardcoded; should use env vars
- **Current:** `["http://localhost:5173", "http://localhost:5174", ...]`
- **Fix:** Load from CORS_ORIGINS env var
- **Next Steps:** Update main.py, .env.example

### 10. ⏳ Error Handling & Logging Standardization
- **CVSS:** N/A (Maintainability)
- **Status:** ⏳ TODO
- **TIER:** TIER-2
- **Priority:** P2 (Observability)
- **Effort:** 3h
- **Details:** Inconsistent error responses; minimal centralized logging
- **Current:** Ad-hoc try/except in endpoints
- **Missing:**
  - Centralized error handler middleware
  - Structured JSON logging
  - Request/response logging
  - Error tracking (Sentry integration)
- **Next Steps:** FastAPI ExceptionHandler, python-json-logger

### 11. ⏳ Testing Coverage Gaps
- **CVSS:** N/A (Quality)
- **Status:** ⏳ TODO
- **TIER:** TIER-2
- **Priority:** P2 (Reliability)
- **Effort:** 5-6h
- **Details:** Frontend tests missing; backend coverage = 85% (need 90%+)
- **Current:** 85% backend coverage (pytest)
- **Missing:**
  - BOLA security tests (User B access prevention)
  - Auth endpoint tests (login/register edge cases)
  - Frontend component tests (SvelteKit + Vitest)
  - Integration tests (end-to-end flows)
- **Next Steps:** pytest parametrization, Vitest setup for frontend

### 12. ⏳ Documentation & API Docs
- **CVSS:** N/A (Maintainability)
- **Status:** ⏳ TODO
- **TIER:** TIER-2
- **Priority:** P2 (Developer Experience)
- **Effort:** 2-3h
- **Details:** Missing OpenAPI/Swagger documentation; unclear API contract
- **Current:** FastAPI auto-docs at /docs (basic)
- **Missing:**
  - API endpoint descriptions & examples
  - Error response documentation
  - Authentication flow diagrams
  - Database schema documentation
  - Deployment guide
- **Next Steps:** Enhanced docstrings, AsyncAPI for events, Architecture Decision Records (ADRs)

---

## 📋 Post-v0.1 Debt (TIER-4)

### 13. 📦 Database Hardening Guide
- **Status:** ⏳ TODO
- **TIER:** Post-v0.1
- **Priority:** P2 (Operations)
- **Effort:** 0.5h
- **Details:** Extract from security audit (7k lines)
- **File:** docs/infrastructure/db-hardening.md
- **Content:** Backup strategy, disaster recovery, access control

### 14. 📊 ELK Alerting & Monitoring
- **Status:** ⏳ TODO
- **TIER:** Post-v0.1
- **Priority:** P2 (Operations)
- **Effort:** 1h
- **Details:** Extract from security audit
- **File:** docs/infrastructure/elk-alerting.md
- **Content:** Alert rules, dashboards, log ingestion

---

## 🔄 Resolution Strategy

### Phase 1: Critical Fixes (TIER-1) ✅ COMPLETE
- ✅ SQL Injection: Whitelist validation
- ✅ BOLA: Ownership checks
- ✅ Secrets: Environment variables

**Timeline:** Complete before production
**Status:** All 3 critical items resolved

### Phase 2: Core Security & Stability (TIER-2)
- **Timeline:** Weeks 1-2 after TIER-1
- **Effort:** 20 hours
- **Items:**
  - Rate limiting (SlowAPI)
  - Input validation (bleach + validators)
  - CORS environment configuration
  - Error handling standardization
  - Testing coverage (security + integration)
  - Neo4j integration

### Phase 3: Hardening & Documentation (TIER-3)
- **Timeline:** Weeks 3-4 after TIER-1
- **Effort:** 5 hours
- **Items:**
  - HTTPS enforcement
  - Security headers (HSTS, CSP)
  - API documentation (Swagger enhancements)
  - Deployment guides

### Phase 4: Operations & Monitoring (Post-v0.1)
- **Timeline:** After v0.1 release
- **Effort:** 1.5 hours
- **Items:**
  - Database hardening guide
  - ELK alerting rules
  - Branch archival & cleanup

---

## 🎯 Completion Criteria

| TIER | Must Complete | Target Date | Blocker |
|------|--------------|-------------|---------|
| TIER-1 | 3/3 items ✅ | Nov 18 | v0.1 release |
| TIER-2 | 6/6 items | Dec 2 | TIER-1 complete |
| TIER-3 | 2/2 items | Dec 16 | Prod deployment |
| Post-v0.1 | 2/2 items | Jan 2026 | v1.0 release |

---

## 📞 Maintenance

**Last Review:** Nov 18, 2025
**Next Review:** Dec 2, 2025 (TIER-2 checkpoint)
**Owner:** Development Team
**Link to Security Audit:** [SECURITY-AUDIT-WEEK1.md](../security/SECURITY-AUDIT-WEEK1.md)
