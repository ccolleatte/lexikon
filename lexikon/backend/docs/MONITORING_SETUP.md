# Security Monitoring & Alerting Setup

**Version:** 1.0
**Last Updated:** 2025-11-21
**Status:** Configuration-Ready

## Overview

Monitoring configuration for security hardening features. Tracks all security-critical metrics and validates that fixes are working correctly in production.

---

## Critical Security Metrics

### 1. Cache Memory Protection

**Metric:** `cache.value.rejection.count`

```ini
[alert]
name = Cache Memory Limit Violations
condition = cache_rejection_count > 10 per 5 minutes
severity = HIGH
action = Notify ops-team
threshold = 10 rejections in 5 minutes
```

**What it measures:**
- Count of oversized values rejected (> 10MB limit)
- Indicates potential DoS attack or bad input

**Log line to grep:**
```
grep "Error setting cache key.*exceeds maximum" logs/application.log
```

**Dashboard visualization:**
```
[Chart] Rejected Cache Values
Y-axis: Count (per minute)
X-axis: Time
Alert: > 2 per minute
```

---

### 2. TTL Validation Violations

**Metric:** `cache.ttl.invalid.count`

```ini
[alert]
name = TTL Validation Failures
condition = ttl_error_count > 5 per 10 minutes
severity = MEDIUM
action = Notify dev-team
details = Include error message in alert
```

**What it measures:**
- Count of TTL values outside 1s - 24h range
- Indicates misconfiguration or code error

**Log line:**
```
grep "TTL must be at least\|TTL.*exceeds maximum" logs/application.log
```

**Expected behavior:**
- Normal: 0 errors (well-configured code)
- Warning: 1-5 per day (minor issues)
- Critical: > 5 in 10 minutes (systematic problem)

---

### 3. API Key HMAC Verification Failures

**Metric:** `auth.api_key.hmac.fail.count`

```ini
[alert]
name = API Key HMAC Verification Failures
condition = hmac_fail_count > 20 per hour
severity = HIGH
action = Notify security team
investigate = Check if API_KEY_SECRET changed
```

**What it measures:**
- Count of API keys that fail HMAC verification
- May indicate: wrong secret, compromised keys, or rollback issues

**Log line:**
```
grep "verify_api_key.*failed\|HMAC verification" logs/application.log
```

**Possible causes:**
- `API_KEY_SECRET` environment variable changed
- Rollback happened without updating keys
- API key database corrupted

**Recovery:**
```bash
# Verify API_KEY_SECRET is set correctly
echo $API_KEY_SECRET | wc -c  # Should be ~65 chars (64 hex + null)

# Check if keys are valid
redis-cli GET "api_key:*" | wc -l

# Reissue all API keys if needed
```

---

### 4. Redis SCAN Performance

**Metric:** `redis.scan.duration.ms`

```ini
[alert]
name = Slow SCAN Operations
condition = p95_scan_duration > 100ms
severity = MEDIUM
action = Notify ops-team
investigate = Check dataset size and Redis configuration
```

**What it measures:**
- P95, P99 latency of SCAN operations
- Indicates dataset size, network, or Redis performance issues

**How to measure:**
```bash
# Add to cache_redis_client.py logging
import time
start = time.time()
cursor, keys = self.client.scan(cursor, match=pattern, count=100)
duration_ms = (time.time() - start) * 1000
logger.debug(f"SCAN duration: {duration_ms}ms")
```

**Dashboard:**
```
[Chart] SCAN Operation Latency
Y-axis: Duration (ms)
X-axis: Time
Lines: P50, P95, P99
Alert: P95 > 100ms (indicates performance issue)
```

---

### 5. Memory Usage Monitoring

**Metric:** `redis.memory.mb` and `redis.memory.percent`

```ini
[alert]
name = Redis Memory Usage High
condition = memory_mb > 100 OR memory_percent > 80%
severity = HIGH
action = Notify ops-team, potentially trigger cache clear
```

**What it measures:**
- Current Redis memory consumption
- Triggers when approaching MAX_TOTAL_MEMORY_MB (100MB)

**Check command:**
```bash
redis-cli INFO memory | grep used_memory_mb
redis-cli CONFIG GET maxmemory
```

**Alert escalation:**
- Warning: > 80MB (85% of limit)
- Critical: > 95MB (95% of limit)
- Action: Evaluate cache TTL, invalidation strategy

---

## Security Event Logging

### Log Aggregation Setup

All security events should be tagged and searchable:

```python
# In application code
logger.warning(
    "Security event: TTL validation failure",
    extra={
        "security_event": True,
        "event_type": "ttl_validation",
        "severity": "medium",
        "key": cached_key,
        "ttl": ttl_value,
    }
)
```

### ELK Stack Configuration

```json
{
  "index_pattern": "lexikon-security-*",
  "mappings": {
    "properties": {
      "security_event": {"type": "boolean"},
      "event_type": {"type": "keyword"},
      "severity": {"type": "keyword"},
      "timestamp": {"type": "date"}
    }
  }
}
```

### Datadog Configuration

```yaml
# datadog.yaml
logs:
  - type: file
    path: "/var/log/lexikon/application.log"
    service: "lexikon-api"
    source: "python"
    tags:
      - env:production
    processors:
      - type: json-parser
      - type: message-remapper
        is_enabled: true
```

---

## Specific Alerts

### Alert 1: Cache Value Rejection (DoS Detection)

```yaml
name: High Cache Value Rejection Rate
query: |
  sum:rate(cache.value.rejection.count[5m]) > 2
duration: 5m
severity: HIGH
notification: |
  Cache values being rejected due to size limit.
  This may indicate:
  - Attacker trying to exhaust memory (DoS)
  - Legitimate large exports temporarily (expected)

  Check:
  - What values are being cached?
  - Are they legitimate?
  - Should we increase limits?

  Action:
  - Check logs for patterns
  - Identify source IP if applicable
  - Consider rate limiting if malicious
```

---

### Alert 2: Auth Failures Surge

```yaml
name: Authentication Failures Surge
query: |
  sum:rate(auth.api_key.hmac.fail.count[5m]) > 5
duration: 5m
severity: HIGH
notification: |
  Multiple API key authentication failures detected.

  Possible causes:
  1. API_KEY_SECRET changed or corrupted
  2. Database rollback without key migration
  3. Timing attack on login (if many failing)

  Steps:
  1. Verify API_KEY_SECRET matches production
  2. Check git log for recent changes
  3. If critical: initiate rollback plan
```

---

### Alert 3: Memory Exhaustion Risk

```yaml
name: Redis Memory Near Limit
query: |
  redis.memory.mb > 90 OR redis.memory.percent > 90%
duration: 10m
severity: CRITICAL
notification: |
  Redis memory approaching limit (MAX: 100MB)

  Actions (in order):
  1. Check what's consuming memory
  2. Increase MAX_TOTAL_MEMORY_MB if legitimate load
  3. Clear expired keys: redis-cli FLUSHALL
  4. Check for memory leaks in application
  5. Scale horizontally or increase Redis instance size
```

---

### Alert 4: SCAN Performance Degradation

```yaml
name: SCAN Operation Latency High
query: |
  p95:redis.scan.duration.ms > 100
duration: 15m
severity: MEDIUM
notification: |
  SCAN operations taking > 100ms (P95)

  This indicates:
  - Large Redis dataset (millions of keys)
  - High write load during SCAN
  - Network latency to Redis

  Check:
  1. Dataset size: redis-cli DBSIZE
  2. Network latency: redis-cli LATENCY DOCTOR
  3. Consider sharding or cluster mode
```

---

## Deployment Verification Checklist

**Before going live, verify these metrics:**

- [ ] No cache rejection errors in staging
- [ ] No TTL validation errors in logs
- [ ] SCAN operations < 50ms (P95) on typical dataset
- [ ] Memory usage stable around 30-50MB
- [ ] API key HMAC working (0 errors in test)
- [ ] Login timing consistent (no user enumeration possible)

---

## Monitoring Dashboards

### Dashboard 1: Security Overview

```
[Title] Security Status Dashboard

Row 1:
  - Cache Rejection Rate (gauge)
  - Auth Failure Rate (gauge)
  - Memory Usage (% of limit)
  - SCAN Performance (P95 ms)

Row 2:
  - Cache Hit Ratio (line chart, 24h)
  - Auth Success Rate (line chart, 24h)
  - Memory Trend (area chart, 7d)
  - SCAN Duration Trend (line chart, 24h)

Row 3:
  - TTL Errors (log table)
  - HMAC Failures (log table)
  - Memory Limit Violations (log table)
```

### Dashboard 2: Redis Health

```
[Title] Redis Cache Health

- Connected Clients
- Commands/sec
- Keyspace Info (by DB)
- Memory Breakdown
- Eviction Policy Status
- Key Expiration Rate
```

### Dashboard 3: Auth Security

```
[Title] Authentication Security

- Login Success/Failure Rate
- API Key Verification Rate
- Failed Attempts by IP (if tracked)
- Auth Latency (P50, P95, P99)
- Auth Error Types (pie chart)
```

---

## Monitoring as Code (Terraform Example)

```hcl
# monitoring/alerts.tf

resource "datadog_monitor" "cache_rejection_alert" {
  name            = "Cache Value Rejection Rate"
  type            = "metric alert"
  message         = <<-EOT
    Cache values being rejected due to size limit.
    {{#is_alert}} ALERT: {{threshold}} rejections per 5min {{/is_alert}}
  EOT

  query = "sum(rate(cache.value.rejection.count{env:production}[5m])) > 2"

  thresholds = {
    critical = 5
    warning  = 2
  }

  notify_audit = true

  tags = ["security", "cache", "critical"]
}

resource "datadog_monitor" "auth_failure_alert" {
  name    = "API Key HMAC Verification Failures"
  type    = "metric alert"
  message = <<-EOT
    {{#is_alert}} CRITICAL: {{value}} auth failures in 5min {{/is_alert}}
  EOT

  query = "sum(rate(auth.api_key.hmac.fail.count{env:production}[5m])) > 5"

  thresholds = {
    critical = 10
    warning  = 5
  }

  tags = ["security", "auth", "critical"]
}
```

---

## Log Patterns for Manual Investigation

### TTL Violations
```bash
grep -i "ttl" logs/application.log | grep -i error
```

### HMAC Failures
```bash
grep "verify_api_key" logs/application.log | grep -i fail
```

### Memory Limit Violations
```bash
grep "exceeds maximum" logs/application.log
```

### SCAN Latency (slow operations)
```bash
grep "SCAN duration:" logs/application.log | awk '{print $NF}'
```

### Login Timing (for timing attack analysis)
```bash
grep "login.*duration_ms" logs/application.log | awk '{print $(NF-1)}'
```

---

## Post-Deployment Validation (24-48 hours)

After deploying to production:

**Hour 1-4:**
- [ ] Check all alert channels are working
- [ ] Verify no false positives
- [ ] Monitor error rate (should be 0 for new features)

**Hour 4-24:**
- [ ] Review cache performance metrics
- [ ] Check auth success rate consistency
- [ ] Verify memory usage patterns
- [ ] Test SCAN with realistic dataset

**Day 2:**
- [ ] Generate security metrics report
- [ ] Review audit logs
- [ ] Confirm no regressions vs baseline
- [ ] Plan for ongoing monitoring

---

## Alert Tuning (First Week)

As production data comes in, adjust thresholds:

```
Current Alert:     2 rejections per 5min
Expected Baseline: 0 rejections per day (normal operation)
Adjust to:         > 5 rejections per hour (real alert)
```

---

## Contact & Escalation

- **Security Team Lead:** [@security-oncall]
- **Ops/Platform Team:** [@platform-team]
- **On-Call:** Check rotation schedule
- **Incident Channel:** #incidents (Slack)

---

**Next Review Date:** 2025-12-21
**Alert Update Frequency:** Weekly (first month), then monthly
