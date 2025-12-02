# TIER 3 - POLISH (Semaines 4-6)

**Status**: Production-hardened
**Effort**: ~60 hours
**Prerequisites**: TIER-1 + TIER-2 completed
**Timeline**: 3 weeks (Weeks 4-6)

---

## Overview

Finitions, observabilité, défense contre bugs.

**Without TIER-3**: MVP works but fragile (hard to debug, support issues hard to resolve)
**With TIER-3**: Production-ready, supportable, defensible

---

## Task 1: Instrumentation (Logging + Error Tracking) (2-3 days, 16h)

**Priority**: 🟠 POLISH
**Owner**: Lead Dev + DevOps
**Driver**: Support customer issues, debug production problems

### Backend Logging

**Tool**: `structlog` (structured logging)

```bash
pip install structlog python-json-logger
```

**Configuration**:
```python
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

log = structlog.get_logger()
```

**Usage**:
```python
# Instead of print or print(f"...")
log.info("user_login", email=user.email, ip=request.client.host)
log.error("term_creation_failed", error=str(e), user_id=user_id)
```

**Tasks**:
- [ ] Configure structlog
- [ ] Replace all print() statements
- [ ] Add logging to critical paths (auth, term CRUD, API calls)
- [ ] Setup log aggregation (CloudWatch, Datadog, or local file)
- [ ] Add request/response logging middleware
- **Time**: 1-2 days

### Frontend Error Tracking

**Tool**: `Sentry` (error tracking + session replay)

```bash
npm install @sentry/svelte
```

**Setup**:
```typescript
import * as Sentry from "@sentry/svelte";

Sentry.init({
  dsn: "https://examplePublicKey@o0.ingest.sentry.io/0",
  environment: import.meta.env.MODE,
  tracesSampleRate: 1.0,
});
```

**Tasks**:
- [ ] Setup Sentry project
- [ ] Add to frontend
- [ ] Verify errors captured
- [ ] Setup Slack alerts for critical errors
- **Time**: 4-6 hours

### Backend Error Tracking

**Tool**: `Sentry` (same as frontend)

```bash
pip install sentry-sdk
```

**Tasks**:
- [ ] Setup Sentry integration
- [ ] Configure sample rate
- [ ] Setup alerts
- **Time**: 2-3 hours

### Success Criteria
- ✅ All auth flows logged
- ✅ All errors captured to Sentry
- ✅ Logs searchable (structured format)
- ✅ Team alerted on critical errors
- ✅ Session replay possible (frontend)

---

## Task 2: Performance Benchmarking (3-4 days, 24h)

**Priority**: 🟠 POLISH
**Owner**: QA Eng + Lead Dev
**Driver**: Meet SLA guarantees

### Baseline Targets

| Operation | Target P95 | Acceptable | Critical |
|-----------|-----------|-----------|----------|
| Profile form submit | <500ms | <1s | >2s |
| Term listing (1000 items) | <2s | <3s | >5s |
| Full onboarding flow | <10s | <15s | >30s |
| API response (single term) | <100ms | <200ms | >500ms |
| Memory (no leaks) | Stable | <5% growth/hour | >10% growth/hour |

### Benchmark Setup

**Tools**:
- `Lighthouse` (frontend performance)
- `k6` (load testing)
- `pytest-benchmark` (backend)

#### 2.1 Frontend Performance (1 day)

```bash
npm install --save-dev lighthouse
```

**Metrics**:
- First Contentful Paint (FCP)
- Largest Contentful Paint (LCP)
- Cumulative Layout Shift (CLS)
- Time to Interactive (TTI)

**Lighthouse audit**:
```bash
# Run on each page
npm run build
npx lighthouse http://localhost:5173 --view
```

**Tasks**:
- [ ] Baseline Lighthouse scores for each page
- [ ] Profile with Chrome DevTools
- [ ] Identify bottlenecks
- [ ] Document findings in `docs/PERFORMANCE.md`

#### 2.2 Backend Performance (1 day)

**pytest-benchmark**:
```python
def test_get_terms_benchmark(benchmark):
    result = benchmark(get_terms, user_id="123")
    assert len(result) > 0
```

**Load test with k6**:
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  vus: 100,        // 100 virtual users
  duration: '30s', // 30 seconds
};

export default function () {
  let res = http.get('http://localhost:8000/api/terms');
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}
```

**Tasks**:
- [ ] Setup pytest-benchmark
- [ ] Benchmark critical endpoints
- [ ] Load test with k6
- [ ] Document baseline

#### 2.3 Memory Leak Testing (1-2 days)

**Frontend**:
- [ ] Chrome DevTools heap snapshots
- [ ] Track memory over time
- [ ] Verify no growth during component unmount

**Backend**:
- [ ] `tracemalloc` for Python
- [ ] Monitor memory during load test
- [ ] Verify cleanup on request end

### Success Criteria
- ✅ All operations meet target P95
- ✅ No memory leaks detected
- ✅ Lighthouse score > 80
- ✅ Load test passes (100 concurrent users)
- ✅ Performance documented

---

## Task 3: Accessibility Audit (2-3 days, 16h)

**Priority**: 🟠 POLISH
**Owner**: QA Eng
**Driver**: Legal compliance + inclusive design

### WCAG AA Checklist

#### 3.1 Keyboard Navigation (4h)

- [ ] All interactive elements reachable via Tab
- [ ] Focus order logical
- [ ] Focus visible (outline present)
- [ ] No keyboard traps

**Test**: Navigate entire app with keyboard only (no mouse)

#### 3.2 Screen Reader (4h)

- [ ] All inputs have labels
- [ ] Form errors announced
- [ ] Buttons have accessible names
- [ ] Images have alt text
- [ ] Headings properly nested

**Test**: Use NVDA (Windows) or VoiceOver (Mac)

#### 3.3 Color Contrast (2h)

- [ ] Text contrast ≥ 4.5:1 (AA standard)
- [ ] Focus indicators visible
- [ ] No color-only signals

**Tools**: WebAIM Color Contrast Checker

#### 3.4 Semantic HTML (3h)

- [ ] Use proper headings (h1, h2, etc.)
- [ ] Lists marked up correctly
- [ ] Form controls properly associated
- [ ] ARIA roles where needed

#### 3.5 Motion & Animations (2h)

- [ ] Respect `prefers-reduced-motion`
- [ ] No auto-playing animations
- [ ] Flashing content rare (< 3 per second)

### Success Criteria
- ✅ WCAG AA compliant
- ✅ Keyboard fully navigable
- ✅ Screen reader compatible
- ✅ No color-only signals
- ✅ Documentation: `docs/ACCESSIBILITY.md`

---

## Task 4: Documentation Completion (2-3 days, 16h)

**Priority**: 🟠 POLISH
**Owner**: Tech Writer + PM
**Driver**: User onboarding, team knowledge

### Documents to Complete

#### 4.1 API Documentation
- [ ] OpenAPI spec auto-generated
- [ ] Example requests/responses
- [ ] Authentication flows documented
- [ ] Rate limit policies documented
- [ ] Error codes documented

#### 4.2 Deployment Guide
- [ ] Environment variables listed
- [ ] Database setup instructions
- [ ] Secrets management
- [ ] Monitoring setup
- [ ] Rollback procedures

#### 4.3 Architecture Documentation
- [ ] System diagram
- [ ] Data flow
- [ ] Component interactions
- [ ] Security model
- [ ] Scalability considerations

#### 4.4 User Guide
- [ ] Getting started (signup, login)
- [ ] Creating terms
- [ ] Managing projects
- [ ] Best practices
- [ ] FAQ

### Success Criteria
- ✅ Every API endpoint documented
- ✅ Deployment runbook exists
- ✅ Architecture clear to new dev
- ✅ User guide complete
- ✅ No orphaned features

---

## Task 5: Security Hardening (2-3 days, 16h)

**Priority**: 🟠 POLISH
**Owner**: Security Lead + Lead Dev

### Checklist

- [ ] HTTPS enforced in production
- [ ] CORS strictly configured
- [ ] CSRF protection added (if needed)
- [ ] SQL injection impossible (ORM handles)
- [ ] XSS impossible (framework escapes)
- [ ] Sensitive data not logged
- [ ] Dependencies scanned (no known vulnerabilities)
- [ ] Secrets rotated (if in code accidentally)
- [ ] Rate limiting verified
- [ ] Auth token validation complete

**Tools**:
```bash
npm audit            # Frontend vulnerabilities
pip-audit           # Backend vulnerabilities
gitleaks detect     # Secret detection
snyk test           # Comprehensive scan
```

### Success Criteria
- ✅ 0 CRITICAL vulnerabilities
- ✅ 0 HIGH vulnerabilities (or mitigated)
- ✅ No secrets in code
- ✅ All dependencies scanned
- ✅ Security report filed: `SECURITY-REPORT-v0.1.md`

---

## Summary

| Task | Hours | Owner |
|------|-------|-------|
| 1. Logging + Error Tracking | 16 | Lead Dev |
| 2. Performance Benchmarking | 24 | QA + Dev |
| 3. Accessibility Audit | 16 | QA |
| 4. Documentation | 16 | Tech Writer |
| 5. Security Hardening | 16 | Sec Lead |
| **TOTAL** | **88** | - |

### Timeline
- Week 4: Tasks 1 + 2 (logging + performance)
- Week 5: Tasks 3 + 4 (accessibility + docs)
- Week 6: Task 5 + final polish (security)

### Definition of Done (v0.1 release)

✅ TIER-1 BLOCKER complete
✅ TIER-2 IMPORTANT complete
✅ TIER-3 POLISH complete
✅ All ADRs documented
✅ Security audit passed
✅ Performance meets targets
✅ Accessibility WCAG AA
✅ Documentation complete
✅ Ready for production

---

**Next Steps**

→ v0.1 Launch

Or continue with [TIER-4-POSTLAUNCH.md](TIER-4-POSTLAUNCH.md) (optional, post-MVP)
