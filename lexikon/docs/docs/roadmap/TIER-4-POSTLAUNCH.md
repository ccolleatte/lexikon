# TIER 4 - POST-LAUNCH (v0.2+)

**Status**: Nice-to-have features, non-blocking for v0.1
**Prerequisites**: v0.1 successfully launched
**Timeline**: Post-MVP (v0.2 planning)

---

## Overview

Features that add significant value but are NOT required for MVP launch.

**Priority**: Depends on user feedback post-launch
**Team Size**: 1-2 developers
**Effort Estimate**: 50-80 hours

---

## Initiative 1: Neo4j Re-evaluation (1-2 weeks)

**Trigger**: When term count > 5,000 in production

### Benchmark Study

Compare Neo4j vs PostgreSQL for real-world queries:

```
Test Dataset:
- 5,000 terms
- 50,000 relations (10 per term average)
- Query depth: 1-5 hops

Scenarios:
1. Find all related terms (IS_A, PART_OF)
2. Find shortest path between terms
3. Detect cycles in IS_A hierarchy
4. Search by relation strength
```

### Metrics

| Metric | PostgreSQL CTE | Neo4j Cypher | Winner |
|--------|---|---|---|
| Query latency P95 | ? | ? | ? |
| Memory usage | ? | ? | ? |
| Index size | ? | ? | ? |
| Setup complexity | Easy | Medium | Easy |
| Operational cost | $$ | $$$ | $$ |

### Decision Gate

**If Neo4j < PostgreSQL latency × 0.5** → Keep Neo4j
**Else** → Migrate to PostgreSQL-only

### Effort
- Benchmark setup: 2-3 days
- Data generation: 1 day
- Query optimization: 2-3 days
- Report: 1 day
- **Total**: 1-2 weeks

---

## Initiative 2: API Key Management (5-7 days)

**Current State**: Skeleton exists (`backend/auth/api_keys.py`)
**Use Case**: Allow users to generate API keys for programmatic access

### Features

- [x] Generate API key (returns key once, never again)
- [x] List user's API keys
- [x] Revoke key
- [x] Set rate limits per key
- [x] Set scopes per key (read-only, write, admin)

### Implementation

```python
# POST /api/users/me/api-keys
async def create_api_key(current_user, scope: str):
    """
    Return: { key: "sk_live_xxxx", secret: "... (shown once)" }
    """

# GET /api/users/me/api-keys
async def list_api_keys(current_user):
    """List user's API keys (without secret)"""

# DELETE /api/users/me/api-keys/{key_id}
async def revoke_api_key(current_user, key_id: str):
    """Revoke a key immediately"""
```

### Testing

- [ ] Key generation unique
- [ ] Key validation works
- [ ] Revocation immediate
- [ ] Rate limiting per key
- [ ] Scopes enforced

### Effort
5-7 days

---

## Initiative 3: Advanced Monitoring & Observability (1-2 weeks)

**Current State**: Basic logging + error tracking (TIER-3)
**Goal**: Production observability + proactive alerting

### Components

#### 3.1 Metrics Collection
- [x] Prometheus scraping FastAPI + PostgreSQL
- [x] Custom metrics (terms created, API calls, errors)
- [x] Track SLA compliance (99.9% uptime)

#### 3.2 Visualization
- [x] Grafana dashboards
- [x] Real-time metrics
- [x] Historical trends

#### 3.3 Alerting
- [x] PagerDuty integration
- [x] Alert rules (error rate > 5%, latency > 1s, etc.)
- [x] Slack notifications

#### 3.4 Tracing
- [x] Distributed tracing (OpenTelemetry)
- [x] Jaeger backend
- [x] Request flow visualization

### Tools
```bash
pip install prometheus-client opentelemetry-api opentelemetry-sdk
pip install opentelemetry-exporter-jaeger
```

### Effort
1-2 weeks

---

## Initiative 4: Full-text Search (2-3 weeks)

**Current State**: Basic search in PostgreSQL
**Goal**: Fast, fuzzy search for terms

### Implementation

#### Option A: PostgreSQL Full-Text Search (5 days)
- Use `tsvector` for full-text
- Add GIN indexes
- Test with 10k+ terms

#### Option B: Elasticsearch (1-2 weeks)
- More powerful
- Fuzzy matching
- Synonyms support
- Heavier to operate

### Recommendation
Start with PostgreSQL, migrate to Elasticsearch if needed (> 100k terms)

---

## Initiative 5: Caching Layer (1 week)

**Current State**: No caching
**Goal**: Reduce database load, improve response time

### Implementation

#### 5.1 Redis Cache
```python
from redis import Redis

cache = Redis(host='localhost')

# Cache term lookups for 1 hour
cache.setex(f"term:{term_id}", 3600, term_json)
```

#### 5.2 Cache Invalidation
- TTL-based: 1h for read-only data
- Event-based: Clear on term update/delete

### Effort
1 week

---

## Initiative 6: Batch Import/Export (2 weeks)

**Current State**: Term CRUD one at a time
**Goal**: Bulk import (CSV/Excel) + export (JSON, RDF, SKOS)

### Formats
- CSV: Simple, universal
- Excel: User-friendly
- JSON-LD: Semantic web compatible
- RDF/SKOS: Linked data standard

### Implementation
- [ ] CSV importer (parse, validate, bulk insert)
- [ ] Excel importer (via `openpyxl`)
- [ ] JSON-LD exporter (for integration with other systems)
- [ ] SKOS exporter (standard ontology format)
- [ ] Progress tracking (for large imports)
- [ ] Error reporting

### Effort
2 weeks

---

## Initiative 7: Collaborative Features (3-4 weeks)

**Current State**: Single user per term
**Goal**: Multi-user editing, comments, version control

### Features
- [x] Projects (group terms)
- [x] Team members (invite, roles)
- [x] Comments on terms
- [x] Term versioning (history)
- [x] Merge conflicts (if editing simultaneously)

### Implementation
- [ ] Projects table + RBAC
- [ ] Comments system
- [ ] Audit trail (who changed what)
- [ ] Conflict resolution UI

### Effort
3-4 weeks

---

## Initiative 8: LLM Integration Enhancements (4-6 weeks)

**Current State**: LLM context injection ready (documented in ADR analysis)
**Goal**: Full-featured LLM assistance

### Features
- [ ] Term suggestion (given description, suggest term)
- [ ] Definition improvement (given raw definition, improve)
- [ ] Relation detection (given term pair, suggest relation)
- [ ] Synonym detection
- [ ] Multi-language translation
- [ ] Quality scoring

### Tools
- OpenAI GPT-4 (fallback)
- Claude 3 (Anthropic)
- Local LLM (Ollama) option

### Effort
4-6 weeks

---

## Initiative 9: User Tiers & Monetization (2-3 weeks)

**Current State**: No limits or billing
**Goal**: Freemium model (free = 100 terms, paid = unlimited)

### Features
- [ ] User tier system (free, pro, enterprise)
- [ ] API key quota per tier
- [ ] Stripe integration
- [ ] Usage tracking
- [ ] Billing history

### Effort
2-3 weeks

---

## Initiative 10: Mobile App (6-8 weeks)

**Current State**: Web-only
**Goal**: iOS + Android apps

### Options
- **React Native**: Cross-platform, shared logic
- **Flutter**: Fast, smooth
- **Native**: Best performance, more work

### Effort
6-8 weeks per team (1 iOS, 1 Android)

---

## Post-Launch Roadmap

### Phase 1: Stabilization (v0.2, 4-6 weeks)
1. Neo4j re-evaluation (if needed)
2. API key management
3. Batch import/export
4. Caching layer

### Phase 2: Scale (v0.3, 6-8 weeks)
1. Full-text search
2. Collaborative features
3. LLM enhancements
4. Monitoring/observability

### Phase 3: Monetization (v1.0, 4-6 weeks)
1. User tiers + billing
2. Usage tracking
3. API commercial offering

### Phase 4: Mobile (v1.1+, parallel)
1. iOS app
2. Android app

---

## Success Metrics (Post-Launch)

| Metric | v0.2 Target | v1.0 Target |
|--------|-------------|-------------|
| Monthly active users | 100 | 1,000 |
| Terms in system | 5,000 | 50,000 |
| API calls/day | 10k | 100k |
| Team collaboration % | 10% | 50% |
| LLM accuracy | - | > 85% |
| Monthly recurring revenue | $0 | $10k |

---

## How to Prioritize

**Ask users/customers**:
- What features would you pay for?
- What's blocking your adoption?
- What hurts most without it?

**Measure impact**:
- User feedback (qualitative)
- Usage metrics (quantitative)
- Revenue potential
- Effort required

**Example decision tree**:
```
If (user requests feature) AND (effort < 1 week) AND (high impact)
  → Prioritize immediately

If (user requests feature) AND (effort > 4 weeks)
  → Research alternative simpler solutions

If (feature enables monetization)
  → Prioritize over nice-to-haves
```

---

## Final Notes

- **Don't start v0.2 features until v0.1 is stable** (at least 2 weeks of production)
- **Get customer feedback first** (roadmap may change based on actual users)
- **Keep team small** (small, focused teams move faster)
- **Measure everything** (don't guess impact, measure it)

---

**Ready to launch v0.1?** → See [TIER-1-BLOCKER-week1.md](TIER-1-BLOCKER-week1.md)
