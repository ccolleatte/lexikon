# Production Deployment Checklist

**Version:** 1.0
**Date:** 2025-11-21
**Type:** Security Hardening Release

## Pre-Deployment (24h before)

### Infrastructure
- [ ] Redis instance up and healthy (`redis-cli ping`)
- [ ] Database backups created (API keys table specifically)
- [ ] Backup procedure tested (can restore in < 5 min)
- [ ] Disk space available: at least 10GB free
- [ ] Memory available: at least 2GB free
- [ ] Network connectivity verified (Redis, DB, monitoring)

### Team & Communication
- [ ] Notify #incidents channel: "Security hardening deployment in 24h"
- [ ] Assign incident commander
- [ ] Assign monitoring watcher (first 4h post-deploy)
- [ ] Assign rollback executor (standby)
- [ ] Verify on-call engineer available

### Code Verification
- [ ] All tests passing: `pytest tests/ -v` (26 + 16 tests)
- [ ] Code review completed (daf8663, 75ef432, 0ff1345 commits)
- [ ] Security scan clean: `semgrep --config p/ci`
- [ ] No blocking issues in git status
- [ ] Recent commits documented

### Staging Validation
- [ ] Deploy to staging environment
- [ ] Run full test suite against staging (1 hour)
- [ ] Load test: 100 concurrent users (30 min)
- [ ] API key migration tested (old + new format)
- [ ] Cache behavior verified under load
- [ ] Memory limits tested (attempt oversized values)
- [ ] SCAN performance measured (< 50ms P95)
- [ ] Monitoring alerts tested (verify they fire)

---

## Deployment Strategy

### Option A: Canary (Recommended for this release)

**Timeline:** 1-2 hours total

```
T+0:00    Deploy to canary (10% traffic)
T+0:10    Monitor metrics, no errors expected
T+0:20    Increment to 25% traffic
T+0:30    Increment to 50% traffic
T+1:00    Full rollout (100% traffic)
T+1:30    Monitor stabilization
T+2:00    Declare success, team standby for 24h
```

### Option B: Blue-Green (Most conservative)

**Timeline:** 30 minutes

```
T+0:00    Deploy to green environment (parallel)
T+0:10    Run smoke tests against green
T+0:15    Switch load balancer from blue → green
T+0:20    Monitor for issues
T+0:30    Celebrate ✅
```

### Option C: Rolling (Standard)

**Timeline:** 15 minutes

```
T+0:00    Deploy to first instance
T+0:05    Verify health check passing
T+0:07    Deploy to remaining instances (parallel)
T+0:15    All instances updated, monitor
```

**Recommendation:** Use Option A (Canary) for this security release

---

## Deployment Steps

### Phase 1: Pre-Flight Checks (5 min)

```bash
# 1. Verify commit hashes
git log --oneline | head -15

# 2. Verify no uncommitted changes
git status  # Should be clean

# 3. Verify API_KEY_SECRET is set
[ -z "$API_KEY_SECRET" ] && echo "ERROR: API_KEY_SECRET not set" && exit 1

# 4. Verify Redis connectivity
redis-cli ping

# 5. Verify database connectivity
python -c "from db.postgres import SessionLocal; s = SessionLocal(); print('DB OK')"

# 6. Run quick sanity test
pytest tests/test_redis_caching.py::TestRedisClient::test_set_and_get_string -v
```

### Phase 2: Canary Deployment (60 min)

```bash
# 1. Build container/package
docker build -t lexikon-api:security-v1.0 .

# 2. Deploy to canary instance (10% traffic)
kubectl set image deployment/lexikon-api \
  api=lexikon-api:security-v1.0 \
  --record \
  --replicas=1

# 3. Verify canary is healthy (wait 2 min for startup)
sleep 120
kubectl get pods | grep lexikon

# 4. Check logs for errors
kubectl logs deployment/lexikon-api | tail -20

# 5. Monitor metrics (5 min of data)
# Should see NO errors in:
#   - Cache rejection rate
#   - Auth failure rate
#   - Memory usage
#   - SCAN latency
```

### Phase 3: Progressive Rollout (45 min)

```bash
# 1. Increment to 25% traffic
kubectl set image deployment/lexikon-api \
  api=lexikon-api:security-v1.0 \
  --replicas=3

sleep 60
# Monitor for 5 minutes

# 2. Increment to 50% traffic
kubectl set image deployment/lexikon-api \
  api=lexikon-api:security-v1.0 \
  --replicas=5

sleep 300  # Monitor 5 minutes
# Check: No error spikes, memory stable, latency OK

# 3. Increment to 100% traffic
kubectl set image deployment/lexikon-api \
  api=lexikon-api:security-v1.0 \
  --replicas=10

sleep 300  # Monitor 5 minutes
```

### Phase 4: Verification (15 min)

```bash
# 1. All instances healthy
kubectl get pods -l app=lexikon-api

# 2. No errors in logs
kubectl logs -l app=lexikon-api --tail=100 | grep -i error

# 3. Smoke tests passing
# Test endpoints:
curl -X GET http://localhost:8000/api/health
curl -X GET http://localhost:8000/api/status
curl -X GET http://localhost:8000/api/metrics

# 4. Metrics normal
# Check Datadog/ELK dashboard for:
#   ✓ Cache hit rate > 80%
#   ✓ Error rate = 0
#   ✓ P95 latency < 500ms
#   ✓ Memory stable
```

---

## API Key Migration Strategy

### Old Format (Pre-deployment)
- Format: `lxk_[random]`
- Hash algorithm: `SHA256(plain_key)` (VULNERABLE)
- Database field: `api_keys.key_hash`

### New Format (Post-deployment)
- Format: `lxk_[random]` (same)
- Hash algorithm: `HMAC-SHA256(secret, plain_key)` (SECURE)
- Database field: `api_keys.key_hash` (same location)

### Migration Approach

**Strategy:** Feature flag with dual support (48h transition)

#### Hour 1: Deployment
- Old keys (SHA256) continue to work (unchanged in DB)
- New keys generated with HMAC-SHA256 only
- Verification checks both formats (soft migration)

#### Hour 24: Monitoring
- Monitor how many old vs new keys are used
- If all traffic is from new keys, can accelerate timeline
- If old keys still active, continue support

#### Hour 48: Cutover
- Mark old keys for deprecation
- Send notification: "Old API keys will be revoked in 7 days"
- Give users time to regenerate

#### Code to enable dual support:

```python
# In verify_api_key()
def verify_api_key(plain_key: str, db: Session) -> Optional[Tuple[str, str]]:
    # Try new format (HMAC-SHA256)
    import hmac
    import hashlib
    import os

    api_secret = os.getenv("API_KEY_SECRET").encode()
    new_hash = hmac.new(api_secret, plain_key.encode(), hashlib.sha256).hexdigest()

    api_key = db.query(ApiKey).filter(ApiKey.key_hash == new_hash).first()
    if api_key:
        return api_key.user_id, api_key.scopes

    # Fallback: try old format (SHA256) for backward compatibility
    import hashlib
    old_hash = hashlib.sha256(plain_key.encode()).hexdigest()
    api_key = db.query(ApiKey).filter(ApiKey.key_hash == old_hash).first()
    if api_key:
        # LOG: warn that old key format is being used
        logger.warning(f"Old API key format used: {api_key.id}")
        return api_key.user_id, api_key.scopes

    return None
```

---

## Post-Deployment Monitoring (4h)

### Minute 0-10: Critical Checks
- [ ] No error spikes (error rate = 0)
- [ ] No memory exhaustion alerts
- [ ] No auth failures (success rate = 100%)
- [ ] No SCAN timeouts

### Minute 10-60: Performance Validation
- [ ] P95 latency stable (< 500ms)
- [ ] Cache hit rate normal (> 80%)
- [ ] Memory usage steady (< 60MB)
- [ ] SCAN operations < 50ms (P95)

### Hour 1-4: Extended Monitoring
- [ ] Monitor all security alerts (should all be 0)
- [ ] Check for memory leaks (memory trend should be flat)
- [ ] Verify auth success rate consistency
- [ ] Review logs for any warnings

### Hour 4+: Team Standby → Normal
- [ ] If all looks good, declare deployment successful
- [ ] Team can return to normal rotation
- [ ] Continue monitoring for 24h before full "all clear"

---

## Rollback Criteria

**Automatic rollback if ANY of these occur:**

1. Error rate > 5% for > 5 minutes
2. Auth failure rate > 10% for > 2 minutes
3. Memory exhaustion (> 100MB)
4. P95 latency > 2000ms for > 10 minutes
5. SCAN operations timing out (> 5s)
6. Cache hit rate drops below 50%

**Manual rollback if:**
- Unknown errors appear in logs
- Alerts cascading/multiplying
- Uncertain whether issue is from this deployment

**DO NOT WAIT for multiple failures - rollback immediately if uncertain.**

---

## Rollback Procedure

If rollback needed:

```bash
# 1. Announce in #incidents
# "Initiating rollback due to [specific issue]"

# 2. Get previous image hash
git log --oneline | head -5
# Find the commit BEFORE security hardening

# 3. Rollback to previous version
kubectl set image deployment/lexikon-api \
  api=lexikon-api:stable-v0.9 \
  --record

# 4. Wait for rollout (2-3 minutes)
kubectl rollout status deployment/lexikon-api

# 5. Clear any corrupted caches
redis-cli FLUSHDB

# 6. Verify health
curl -X GET http://localhost:8000/api/health

# 7. Post-mortem
# Document what went wrong for review meeting
```

**Total rollback time: 5-10 minutes**

---

## Documentation Updates (Post-Deploy)

- [ ] Update SECURITY.md with new hash format
- [ ] Update API documentation with auth changes
- [ ] Update runbooks for ops team
- [ ] Add troubleshooting section to MONITORING_SETUP.md
- [ ] Update internal wiki with deployment notes

---

## Team Sign-Off

**Deployment Lead:** ______________________ Date: _______
**Incident Commander:** ___________________ Date: _______
**Monitoring Watcher:** ____________________ Date: _______
**Database Backup Verified:** ______________ Date: _______

---

## Success Criteria

Deployment is **SUCCESSFUL** when all of the following are true:

✅ No critical alerts firing
✅ Error rate = 0%
✅ Memory stable < 60MB
✅ Cache hit rate > 80%
✅ Auth success rate = 100%
✅ No performance regression
✅ All tests passing
✅ Team confidence high

**If all green, deployment is complete and successful!**

---

## Contact & Escalation

- **Deployment Lead**: Contact immediately if any issues
- **On-Call**: Escalate if deployment lead unavailable
- **Security Team**: Notify of any security-related issues
- **Ops Team**: Monitor infrastructure throughout deployment

**Post-deployment support:** Available 24h for rollback decision
