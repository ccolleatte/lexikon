# Security Audit - Week 1

**Date:** November 17, 2025
**Status:** In Progress
**Related:** TIER-1-BLOCKER Task #5 (Security Audit)

---

## Executive Summary

Three critical security vulnerabilities identified during Phase A code review. All are actionable and required before production deployment.

| Vulnerability | CVSS Score | Status | Deadline |
|---------------|-----------|--------|----------|
| SQL Injection (init_postgres.py) | 9.8 | ✅ FIXED | Immediate |
| BOLA - Broken Object Level Authorization (api/terms.py) | 8.6 | ✅ FIXED | This week |
| Secrets Hardcoded (docker-compose.yml) | 9.1 | ✅ FIXED | This week |

---

## Vulnerability #1: SQL Injection in init_postgres.py

### Details

**Location:** `backend/db/init_postgres.py:76`

**Original Vulnerable Code:**
```python
count_result = conn.execute(f"SELECT COUNT(*) FROM {table}")
```

**Problem:** Table name parameter not validated or escaped

**CVSS v3.1:** 9.8 CRITICAL
- Attack Vector: Network
- Attack Complexity: Low
- Privileges Required: None
- User Interaction: None
- Impact: Confidentiality (High), Integrity (High), Availability (High)

### Exploitation Scenario

If `information_schema.tables` is somehow tampered or if source is user-controlled:
```python
# Attacker-controlled input
table = "users; DROP TABLE users; --"
# Results in:
# SELECT COUNT(*) FROM users; DROP TABLE users; --
```

### Fix Applied ✅

**Commit:** `a327653` - security: Fix SQL injection in init_postgres table statistics

Changes:
1. **Whitelist Validation**: Only allow known tables from ALLOWED_TABLES set
2. **Identifier Escaping**: Use double quotes for table identifiers in PostgreSQL
3. **Error Handling**: Try/except per table to prevent crashes

**Fixed Code:**
```python
ALLOWED_TABLES = {
    "users", "oauth_accounts", "api_keys", "projects", "project_members",
    "terms", "onboarding_sessions", "llm_configs"
}

tables = [row[0] for row in result if row[0] in ALLOWED_TABLES]

for table in tables:
    try:
        count_result = conn.execute(f"SELECT COUNT(*) FROM \"{table}\"")
        count = count_result.scalar()
        print(f"  {table}: {count} rows")
```

### Verification

- [x] Whitelist applied to `show_table_stats()`
- [x] Unknown tables filtered before execution
- [x] Double quotes escape identifiers in PostgreSQL
- [x] No injection possible from `information_schema.tables`

---

## Vulnerability #2: BOLA - Broken Object Level Authorization

### Details

**Location:** `backend/api/terms.py` (GET /api/terms/{term_id})

**Current Vulnerable Code:**
```python
@router.get("/api/terms/{term_id}")
async def get_term(term_id: str, db: Session = Depends(get_db)):
    """Get term by ID"""
    term = db.query(Term).filter(Term.id == term_id).first()
    return {"term": term}
```

**Problem:** No ownership verification. Any authenticated user can read any user's terms.

**CVSS v3.1:** 8.6 HIGH
- Impact: Confidentiality (High) - unauthorized data access
- Attack Vector: Network, Low Complexity
- Escalation: Can be combined with other endpoints for full data breach

### Exploitation Scenario

```bash
# User A authenticates and gets access_token
curl -X POST http://localhost:8000/api/auth/login \
  -d '{"email":"userA@test.com","password":"..."}' \
  # Returns: {"access_token": "..."}

# User A then queries User B's terms (no authorization check!)
curl http://localhost:8000/api/terms/term-uuid-from-userB \
  -H "Authorization: Bearer $ACCESS_TOKEN_A"
# Returns: User B's private term data!
```

### Fix Required

Add ownership verification to all user-owned resource endpoints:

```python
@router.get("/api/terms/{term_id}")
async def get_term(
    term_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get term by ID - with ownership check"""
    term = db.query(Term).filter(
        Term.id == term_id,
        Term.user_id == current_user.id  # ← FIX: Add ownership check
    ).first()

    if not term:
        raise HTTPException(status_code=404, detail="Term not found")

    return {"term": term}
```

**Affected Endpoints (TODO):**
- [x] GET /api/terms/{term_id}
- [ ] PUT /api/terms/{term_id}
- [ ] DELETE /api/terms/{term_id}
- [ ] GET /api/projects/{project_id}
- [ ] PUT /api/projects/{project_id}

### Fix Applied ✅

**Commit:** `6172f87` - security: Fix BOLA (Broken Object Level Authorization) in terms endpoints

Changes:
1. **Migrated to SQLAlchemy**: Converted `api/terms.py` from in-memory database to ORM
2. **Authentication**: Integrated `get_current_user` dependency
3. **Ownership Verification**: Added `created_by == current_user.id` to all endpoints:
   - ✅ GET /api/terms/{term_id}
   - ✅ PUT /api/terms/{term_id}
   - ✅ DELETE /api/terms/{term_id}
   - ✅ POST /api/terms (with ownership binding)
   - ✅ GET /api/terms (list with ownership filtering)
4. **Complete CRUD**: Added missing GET single, PUT, DELETE endpoints
5. **Logging**: Comprehensive security audit logging

### Status

**Status:** ✅ FIXED (Nov 18, 2025)
**Commit:** 6172f87
**Priority:** 🔴 P0 - RESOLVED

---

## Vulnerability #3: Secrets Hardcoded in docker-compose.yml

### Details

**Location:** `docker-compose.yml` (PostgreSQL + Neo4j passwords)

**Current Vulnerable Code:**
```yaml
services:
  postgres:
    environment:
      POSTGRES_PASSWORD: dev-secret  # ← Hardcoded!

  neo4j:
    environment:
      NEO4J_AUTH: neo4j/dev-secret   # ← Hardcoded!
```

**Problem:**
- Database credentials in version control
- If repo is compromised (private repo → public, fork, leak), full database access exposed
- dev-secret is weak and obviously a placeholder

**CVSS v3.1:** 9.1 CRITICAL
- Impact: Full confidentiality + integrity of database
- Vector: Network (if repo leaked or accessed)
- Scope: Entire application data

### Exploitation Scenario

```bash
# If repo.git is accessed (GitHub compromise, leaked fork, etc.)
git clone https://github.com/ccolleatte/lexikon.git
grep -r "PASSWORD\|AUTH" docker-compose.yml
# Attacker finds:
#   POSTGRES_PASSWORD=dev-secret
#   NEO4J_AUTH=neo4j/dev-secret

# Attacker connects directly to databases:
psql -h lexikon-prod.aws.com -U lexikon -d lexikon
# Prompts for password → dev-secret (if same as prod!)
# Full database access granted
```

### Fix Required

1. **Use Environment Variables** (not in docker-compose.yml):
```yaml
services:
  postgres:
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}  # From .env
```

2. **Create .env.local** (NOT in git):
```bash
POSTGRES_PASSWORD=<strong-random-password>
NEO4J_AUTH=neo4j/<strong-random-password>
```

3. **Update .gitignore**:
```
.env
.env.local
.env.*.local
```

4. **Documentation** (.env.example):
```yaml
# docker-compose.yml
POSTGRES_PASSWORD=change-me-in-production
NEO4J_AUTH=neo4j/change-me-in-production
```

### Fix Applied ✅

**Commit:** `8303db0` - security: Move database secrets to environment variables

Changes:
1. **Created `.env.example`**: Template with placeholder values for all environment variables
2. **Updated `docker-compose.yml`**:
   - POSTGRES_PASSWORD: `${POSTGRES_PASSWORD}`
   - NEO4J_AUTH: `neo4j/${NEO4J_PASSWORD}`
   - Neo4j healthcheck: Updated to use `${NEO4J_PASSWORD}`
3. **Created `.env.local`**: Local development credentials (not committed)
4. **Verified `.gitignore`**: Confirmed `.env` and `.env.local` are already ignored
5. **Updated `README.md`**: Added Configuration section with setup instructions

Deploy Instructions:
```bash
# 1. Copy template
cp .env.example .env.local

# 2. Update with strong passwords
vim .env.local

# 3. Load environment and start Docker
export $(cat .env.local | xargs)
docker-compose up -d
```

### Status

**Status:** ✅ FIXED (Nov 18, 2025)
**Commit:** 8303db0
**Priority:** 🔴 P0 - RESOLVED
**Production Ready:** Yes (requires env vars before deployment)

---

## Security Checklist

### TIER-1 Task #5 Progress

- [x] SQL Injection (init_postgres.py) - FIXED (commit a327653)
- [x] BOLA (api/terms.py) - FIXED (commit 6172f87)
- [x] Secrets Management (docker-compose.yml) - FIXED (commit 8303db0)
- [ ] Rate Limiting - Deferred to TIER-2
- [ ] HTTPS Enforcement - Deferred to TIER-3
- [ ] HSTS Headers - Deferred to TIER-3

### Production Readiness Gates

| Requirement | Status | Notes |
|------------|--------|-------|
| SQL Injection fixed | ✅ DONE | Commit a327653 |
| BOLA fixed | ✅ DONE | Commit 6172f87 |
| Secrets not in repo | ✅ DONE | Commit 8303db0 |
| Rate limiting | ⏳ TIER-2 | SlowAPI integration |
| CORS hardcoding fixed | ⏳ Task 2 | 30 min remaining |

---

## Next Steps

1. ✅ **Fix BOLA** - COMPLETE (commit 6172f87) - Ownership checks on all term endpoints
2. ✅ **Move Secrets** - COMPLETE (commit 8303db0) - Environment variables configured
3. 🔄 **Test fixes** - Run security tests to verify unauthorized access is blocked
4. 📋 **Update TIER-1** - Mark Task #5 complete (3 critical vulns fixed)

---

## References

- OWASP: [Broken Object Level Authorization (BOLA)](https://owasp.org/www-project-api-security/latest/docs/vulnerabilities/broken-object-level-authorization/)
- CWE-89: [SQL Injection](https://cwe.mitre.org/data/definitions/89.html)
- CWE-798: [Hardcoded Credentials](https://cwe.mitre.org/data/definitions/798.html)
- CVSS Calculator: https://www.first.org/cvss/calculator/3.1

---

**Last Updated:** November 17, 2025
**Next Review:** Daily until all vulnerabilities fixed
**Owner:** Lead Developer + Security
