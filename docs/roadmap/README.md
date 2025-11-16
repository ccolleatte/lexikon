# Lexikon Roadmap - Complete Planning

This directory contains detailed, actionable planning for Lexikon v0.1 → v1.0.

## Structure

### 🔴 TIER 1 - BLOCKER (Week 1)
**File**: [TIER-1-BLOCKER-week1.md](TIER-1-BLOCKER-week1.md)

5 critical tasks that **must** be done before any production release.

- ✅ JWT authentication integration
- ✅ CORS configuration for production
- ✅ Test coverage completion (80%+)
- ✅ Linting + automated formatting
- ✅ Security audit

**Effort**: 66-74 hours (1 week intensive)
**Status**: Not started
**Owner**: Lead Dev + QA Eng

**Deliverable**: v0.1.0 Release Candidate (can ship)

---

### 🟡 TIER 2 - IMPORTANT (Weeks 2-3)
**File**: [TIER-2-IMPORTANT-weeks2-3.md](TIER-2-IMPORTANT-weeks2-3.md)

6 features that transform MVP into viable product.

- ✅ Login/register backend (email + password)
- ✅ OAuth integration (GitHub, Google)
- ✅ PostgreSQL persistence (data doesn't disappear)
- ✅ Rate limiting (protect against abuse)
- ✅ Input validation improvements (international names)
- ✅ CI/CD pipeline automation

**Effort**: ~98 hours (2-3 weeks)
**Status**: Not started
**Owner**: Lead Dev, QA Eng

**Deliverable**: v0.1.1 - Feature-complete MVP

---

### 🟠 TIER 3 - POLISH (Weeks 4-6)
**File**: [TIER-3-POLISH-weeks4-6.md](TIER-3-POLISH-weeks4-6.md)

5 tasks that make product production-grade.

- ✅ Logging + error tracking (Sentry)
- ✅ Performance benchmarking
- ✅ Accessibility audit (WCAG AA)
- ✅ Documentation completion
- ✅ Security hardening

**Effort**: ~88 hours (3 weeks)
**Status**: Not started
**Owner**: Lead Dev, QA Eng, Tech Writer

**Deliverable**: v0.1 GA - Production ready

---

### 💚 TIER 4 - POST-LAUNCH
**File**: [TIER-4-POSTLAUNCH.md](TIER-4-POSTLAUNCH.md)

10 initiatives for v0.2+, prioritized based on user feedback.

- Neo4j vs PostgreSQL evaluation
- API key management
- Advanced monitoring (Prometheus, Grafana)
- Full-text search
- Caching layer (Redis)
- Batch import/export
- Collaborative features (teams, comments)
- LLM enhancements
- Monetization (freemium model)
- Mobile apps (iOS, Android)

**Effort**: 150-200 hours (varies by priority)
**Status**: Waiting for v0.1 user feedback
**Owner**: TBD post-launch

---

## Architecture Decision Records (ADRs)

Every significant architectural decision is documented in `docs/architecture/adr/`.

### Core ADRs

| ADR | Topic | Status | Review Date |
|-----|-------|--------|-------------|
| [ADR-0001](../architecture/ADR-0001-neo4j-decision.md) | Neo4j vs PostgreSQL | Accepted (provisional) | v0.2 (at 5k terms) |
| [ADR-0002](../architecture/ADR-0002-jwt-authentication.md) | JWT Authentication | Accepted | Week 1 (TIER-1) |
| ADR-0003 | SvelteKit Framework Choice | Accepted | - |
| ADR-0004 | FastAPI Backend | Accepted | - |
| ADR-0005 | PostgreSQL Primary DB | Accepted | - |

**New ADRs needed**:
- ADR-0006: Rate Limiting Strategy (TIER-2)
- ADR-0007: Caching Architecture (TIER-4)
- ADR-0008: Monitoring Strategy (TIER-3)

**Template**: See [ADR-TEMPLATE.md](../architecture/ADR-TEMPLATE.md)

---

## How to Use This Roadmap

### For PMs
1. Read [TIER-1-BLOCKER-week1.md](TIER-1-BLOCKER-week1.md) for release timeline
2. Understand critical path (JWT + CORS + Tests)
3. Plan sprint 1 around these constraints
4. Monitor TIER-2 for feature completeness messaging

### For Developers
1. Start with TIER-1 tasks in order
2. Use each task's "Success Criteria" to know when done
3. Update ADRs as you learn more
4. Reference TIER-2/3 for planning

### For QA/Testing
1. TIER-1: Focus on critical path (auth, security)
2. TIER-2: Build test infrastructure for new features
3. TIER-3: Run full audit (perf, a11y, security)
4. Document gaps in each tier

### For Stakeholders
1. **v0.1 (Week 1)**: TIER-1 = Launch candidate
2. **v0.1.1 (Week 3)**: TIER-2 = Feature complete
3. **v0.1 GA (Week 6)**: TIER-3 = Production ready
4. **v0.2+ (Post-launch)**: TIER-4 = Based on feedback

---

## Timeline Summary

```
Week 1  : TIER-1 BLOCKER (JWT, CORS, Tests, Linting, Security)
Weeks 2-3: TIER-2 IMPORTANT (Auth, OAuth, DB, Rate limiting, CI/CD)
Weeks 4-6: TIER-3 POLISH (Logging, Perf, A11y, Docs, Security hardening)
Week 7+  : TIER-4 POST-LAUNCH (Post-launch initiatives)
```

**Total Effort to Production**: 252-260 hours ≈ **6-7 weeks** (1 team of 2 devs @ 40h/week)

---

## Success Criteria by Tier

### TIER-1 ✅ (Done = Can Release)
- [ ] JWT tokens real (not fake)
- [ ] CORS configurable
- [ ] 80%+ test coverage
- [ ] Linting enforced
- [ ] Security audit passed

### TIER-2 ✅ (Done = Feature-complete MVP)
- [ ] Login/register working
- [ ] OAuth providers working
- [ ] Data persists in PostgreSQL
- [ ] Rate limiting enforced
- [ ] CI/CD pipeline running

### TIER-3 ✅ (Done = Production ready)
- [ ] Logs searchable
- [ ] Errors tracked to Sentry
- [ ] Performance meets targets
- [ ] WCAG AA compliant
- [ ] All docs complete

### TIER-4 ✅ (Done = v0.2+ planned)
- [ ] Neo4j decision made
- [ ] Post-launch roadmap prioritized
- [ ] Quarterly goals set

---

## Key Metrics

| Metric | v0.1 Target | v0.2 Target | v1.0 Target |
|--------|-------------|-------------|-------------|
| Test coverage | 80% | 85% | 90%+ |
| API uptime | 95% | 99% | 99.9% |
| P95 latency | 500ms | 200ms | 100ms |
| WCAG compliance | AA | AA | AAA (stretch) |
| Security vulns | 0 CRITICAL | 0 CRITICAL | 0 CRITICAL |
| Users | 0 (beta) | 50 | 1,000 |

---

## Dependencies Between Tiers

```
TIER-1 (Week 1) ← MUST COMPLETE
    ↓
TIER-2 (Weeks 2-3) ← BUILD ON TIER-1
    ↓
TIER-3 (Weeks 4-6) ← HARDEN TIER-2
    ↓
TIER-4 (v0.2+) ← PLAN BASED ON USER FEEDBACK
```

**Can't skip tiers**. TIER-1 is release-blocking.

---

## Communication

### Team Standup Template

```
Yesterday:
- Completed: [Task from current tier]
- Blockers: [Issues preventing progress]

Today:
- Working on: [Next task]
- Help needed: [Dependencies]

TIER-1 Progress: X/5 tasks done
```

### Release Readiness Checklist

```
TIER-1 Completion:
- [ ] JWT: All tests pass
- [ ] CORS: Env vars working
- [ ] Tests: 80%+ coverage
- [ ] Linting: 0 violations
- [ ] Security: All checks pass

Sign-off:
- [ ] PM: Feature complete for v0.1
- [ ] Dev: Code quality acceptable
- [ ] QA: Testing comprehensive
- [ ] Security: No blockers
```

---

## Questions?

See ADR documents for decision rationale.
See specific tier docs for detailed tasks.
Ask for clarification in #engineering Slack.

---

**Last Updated**: 2025-11-16
**Next Review**: Week 1 completion (2025-11-23)
