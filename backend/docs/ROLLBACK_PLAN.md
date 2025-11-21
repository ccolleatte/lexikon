# Security Hardening Rollback Plan

**Last Updated:** 2025-11-21
**Version:** 1.0
**Status:** Production-Ready

## Overview

This document describes the step-by-step procedure to rollback the security hardening changes if critical issues occur in production.

**Related Commits to Rollback:**
- `daf8663` - Security hardening implementation (cache, auth, API keys)
- `75ef432` - Integration tests
- `0ff1345` - Security hardening test suite
- Plus subsequent commits (Redis auth, benchmarks, security.md)

---

## Pre-Rollback Checklist

Before initiating rollback:

- [ ] Confirm the issue is production-critical (not just test/dev)
- [ ] Check if issue is configuration-related (can be fixed without code rollback)
- [ ] Verify database backups exist (API keys, user data intact)
- [ ] Notify team that rollback is starting
- [ ] Take screenshot of error state for post-mortem

---

## Rollback Scenarios

### Scenario 1: Cache System Failures

**Symptoms:**
- `SCAN` operations timing out or hanging
- Memory exhaustion (SCAN not working as expected)
- Cache hit/miss ratio degradation > 50%

**Rollback Steps:**

```bash
# 1. Identify problematic commit
git log --oneline | head -20

# 2. Revert cache-related changes (if isolated)
git revert daf8663  # Security hardening
git revert 75ef432  # Integration tests
git revert 0ff1345  # Security tests

# 3. Clear problematic cache
redis-cli FLUSHDB   # WARNING: Clears ALL cache

# 4. Verify system
python -m pytest tests/test_redis_caching.py -v

# 5. Deploy rolled-back version
# (Follow standard deploy procedure)
```

**Why this works:**
- Reverts SCAN implementation back to KEYS (original)
- TTL validation removed (reverts to any TTL)
- Memory limits removed

**Post-Rollback:**
- [ ] Monitor cache hit rate
- [ ] Check KEYS performance vs SCAN regression
- [ ] Review original code for why KEYS was problematic

---

### Scenario 2: Authentication Failures

**Symptoms:**
- Login always fails with "Invalid credentials"
- API key authentication broken for all keys
- 100% auth failure rate in logs

**Rollback Steps:**

```bash
# 1. Check auth logs for specific error
tail -100 logs/application.log | grep -i auth

# 2. Verify current API_KEY_SECRET
echo $API_KEY_SECRET  # Should be set

# 3. If HMAC issue, revert API key hashing
git revert daf8663

# 4. Clear API key cache if any
redis-cli DEL "api_key:*"

# 5. For login timing attack fix, revert:
git revert daf8663  # Reverts dummy hash logic

# 6. Test auth
python -m pytest tests/test_security_hardening.py::TestAPIKeyHMACHashing -v

# 7. Deploy
```

**Why this works:**
- Reverts HMAC-SHA256 back to plain SHA256
- Removes dummy hash for non-existent users
- Removes timing attack mitigation

**Post-Rollback:**
- [ ] Re-issue all API keys (HMAC hashes won't work with old keys)
- [ ] Update clients with new API keys
- [ ] Review why HMAC migration failed

---

### Scenario 3: Memory Issues

**Symptoms:**
- Memory exhaustion alerts
- Redis memory > 100MB (even on cleared cache)
- OOM killer triggering
- Application rejected requests (set() returning False)

**Rollback Steps:**

```bash
# 1. Check current memory usage
redis-cli INFO memory

# 2. Revert memory limit enforcement
git revert daf8663

# 3. Clear and reset Redis
redis-cli FLUSHDB
redis-cli CONFIG RESETSTAT

# 4. Restart Redis to clear memory
sudo systemctl restart redis-server  # or equivalent for your OS

# 5. Verify memory
redis-cli INFO memory | grep used_memory_mb

# 6. Deploy rolled-back version
```

**Why this works:**
- Removes 10MB per-value and 100MB total limits
- No more rejection of oversized values
- Memory checks disabled

**Post-Rollback:**
- [ ] Implement proper Redis memory policies in config
- [ ] Add external rate limiting for cache size
- [ ] Review what was causing memory pressure

---

### Scenario 4: Performance Degradation

**Symptoms:**
- P99 latency > 2s (was < 500ms)
- SCAN operations much slower than KEYS
- Cache operations taking > 100ms each

**Rollback Steps:**

```bash
# 1. Confirm SCAN is causing issue
redis-cli --latency 30  # 30 second sample

# 2. Revert to KEYS (less blocking but faster)
git revert 75ef432  # Integration tests
git revert daf8663  # Main changes

# 3. Clear cache to start fresh
redis-cli FLUSHDB

# 4. Run performance tests
python tests/benchmark_cache_performance.py

# 5. Deploy
```

**Why this works:**
- KEYS is O(N) but faster than SCAN for small datasets
- SCAN is more correct but potentially slower

**Post-Rollback:**
- [ ] Implement performance benchmarking in CI/CD
- [ ] Document SCAN vs KEYS tradeoffs
- [ ] Optimize SCAN implementation

---

### Scenario 5: General System Instability

**Symptoms:**
- Multiple unrelated failures
- Cannot identify specific cause
- System unreliable

**Full Rollback Steps:**

```bash
# 1. Identify all security hardening commits
git log --oneline | grep -E "security|hardening"

# 2. Create a rollback branch
git checkout -b rollback/emergency-`date +%Y%m%d-%H%M%S`

# 3. Revert all commits in reverse order
git revert --no-edit HEAD~6..HEAD  # Adjust range as needed

# 4. Verify nothing is broken
python -m pytest tests/test_redis_caching.py tests/test_security_hardening.py -v

# 5. Push to production branch if safe
git checkout master
git merge --no-ff rollback/emergency-xxxxx

# 6. Clear all caches
redis-cli FLUSHDB

# 7. Deploy
```

**Post-Rollback:**
- [ ] Full system test
- [ ] Monitor all metrics for 24+ hours
- [ ] Schedule post-mortem meeting
- [ ] Review what went wrong

---

## Database Considerations

### API Keys

**Before Rollback:**
- HMAC hashes stored in database (commitment code `daf8663`)
- Old keys (SHA256) no longer work

**After Rollback:**
- HMAC hashes become invalid
- Must invalidate all API keys or re-hash

**Recovery:**
```bash
# Option 1: Invalidate and re-issue
UPDATE api_keys SET is_active = FALSE;

# Option 2: Re-hash to old format (if keys in plaintext somewhere)
# This is not recommended - issuere new keys instead
```

### Cache Data

**Before Rollback:**
- Serialized as JSON only (no pickle)
- TTL validation enforced (1s - 24h)
- Memory limits enforced

**After Rollback:**
- Can cache non-JSON objects (if code supports)
- TTL validation disabled
- No size limits

**Recovery:**
- Clearing cache is safe: `redis-cli FLUSHDB`
- No data loss (cache is ephemeral)

---

## Monitoring During Rollback

### Key Metrics to Watch

```bash
# Cache health
redis-cli INFO stats | grep hits
redis-cli INFO stats | grep misses

# Memory
redis-cli INFO memory | grep used_memory_mb

# Auth success rate
grep "INVALID_CREDENTIALS" logs/application.log | wc -l

# Performance (latency)
redis-cli --latency-histogram 30
```

### Alerts to Silence

During rollback, silence these alerts temporarily:
- TTL validation violations (will appear on rollback)
- Large cache value rejections (will work again)
- API key HMAC failures (expected during rollback)

---

## Verification Checklist

After rollback completes:

- [ ] Redis is accepting connections
- [ ] Cache operations working (set/get/delete)
- [ ] Auth system operational
- [ ] All tests passing (`pytest tests/ -v`)
- [ ] No errors in application logs
- [ ] Metrics look normal
- [ ] Performance acceptable

### Smoke Tests

```bash
# Cache operations
curl -X GET http://localhost:8000/api/health

# Auth flow (if exposed)
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

---

## Post-Rollback Actions

### Immediate (Day 1)

1. **Document the issue**
   - What failed?
   - When did it start?
   - What was the user impact?

2. **Root cause analysis**
   - Was it code issue or deployment issue?
   - Configuration problem?
   - Environment incompatibility?

3. **Notify stakeholders**
   - Team that rollback is complete
   - Status of investigation
   - ETA for fix

### Short-term (Week 1)

4. **Fix the issue**
   - Address root cause
   - Add regression tests
   - Implement monitoring

5. **Improve process**
   - Why wasn't this caught in staging?
   - Add better integration tests?
   - Improve monitoring?

### Long-term (Ongoing)

6. **Schedule re-deployment**
   - Plan with full team
   - More extensive testing
   - Better monitoring

7. **Post-mortem meeting**
   - Document lessons learned
   - Update procedures
   - Improve playbooks

---

## Contact & Escalation

**In case of issues:**

1. Slack #incidents channel
2. On-call engineer (@oncall)
3. Tech lead for authorization
4. Follow incident response protocol

**Estimated Rollback Time:** 15-30 minutes (including verification)

**Expected Downtime:** 2-5 minutes (during redis flush and redeployment)

---

## Appendix: Commit Details

### Rollback Commits

```
daf8663 - refactor(security): Implement comprehensive security hardening
          └─ Cache: Pickle RCE fix, KEYS→SCAN, TTL validation, memory limits
          └─ Auth: API key HMAC upgrade
          └─ Login: Timing attack fix
          └─ Cache decorator: Key hashing

0ff1345 - test(security): Add comprehensive security hardening test suite
          └─ 26 unit tests for all 7 security fixes

75ef432 - test(integration): Add end-to-end security integration tests
          └─ 16 integration tests (caching + auth flows)
```

### Revert Command

```bash
# All at once
git revert --no-edit daf8663 0ff1345 75ef432 [other commits...]

# Or one by one
git revert daf8663
git revert 0ff1345
git revert 75ef432
```

---

**Last tested:** 2025-11-21
**Testing frequency:** Before every production deployment
**Next review:** 2025-12-21
