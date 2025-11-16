# ADR-0001: Neo4j vs PostgreSQL-only for Ontological Relations

**Date**: 2025-11-16
**Status**: Accepted (with reservation)
**Deciders**: [PM], [Lead Dev], [Architect]
**Consulted**: Database specialist, LLM integration lead
**Informed**: Full dev team

## Context

Lexikon v0.1-v0.2 requires storing ontological relations between terms:
- IS_A (inheritance)
- PART_OF (composition)
- RELATED_TO (semantic similarity)
- Custom domain-specific relations

**Current implementation**: Both PostgreSQL (relational) and Neo4j (graph) added in Sprint 2
**Problem**:
- Neo4j adds operational complexity (2 DBs instead of 1)
- Requires coordination between PostgreSQL and Neo4j
- v0.1 MVP has 0 terms in production
- GraphQL/Cypher queries may be premature optimization

**Questions to resolve**:
1. Do we actually need graph database for MVP?
2. What's the minimum viable option?
3. When should we pay the migration cost to Neo4j?

## Decision

**Accept Neo4j implementation, BUT with explicit re-evaluation gate.**

We keep both PostgreSQL + Neo4j in Sprint 2, but:
1. Primary data source remains PostgreSQL (source of truth)
2. Neo4j becomes optional/secondary (can be disabled)
3. **Before v0.2 release**: Benchmark real usage patterns
4. **Activation criterion**: Re-evaluate when term count > 5,000

### Rationale

**Why Neo4j now (provisional)**:
- Ontological queries naturally benefit from graph models
- Team already familiar with Neo4j from analysis phase
- Eventual product needs sophisticated relation queries
- Infrastructure already built (docker-compose, init scripts)
- No extra cost to keep both (only dev time)

**Why provisional**:
- Complexity cost is real (2 DBs, sync logic, dual migrations)
- PostgreSQL's JSONB + recursive CTEs handle most cases
- At small scale (< 5k terms), performance difference negligible
- Neo4j commercial support may become necessary later

## Consequences

### Positives
✅ Sophisticated graph queries possible (shortest path, relation inference)
✅ Foundation for future AI relation extraction
✅ Can prove value before full migration
✅ Demonstrates sophistication to investors

### Negatives
❌ Operational complexity: Maintain 2 DBs
❌ Data consistency: PostgreSQL ↔ Neo4j sync required
❌ Migrations: Schema changes affect both systems
❌ Debugging: Graph issues harder to diagnose
❌ Cost: Neo4j license (Aura managed) if scaling
❌ Developer cognitive load: Learn Cypher + SQL

### Mitigations
- PostgreSQL as primary, Neo4j as secondary (read-only initially)
- Simple sync: batch export from PostgreSQL → Neo4j nightly
- Version both databases in migrations
- Document Cypher patterns in code

## Alternatives Considered

### Alternative A: PostgreSQL-only (JSONB relations)
**Pros**:
- Single database (simpler ops)
- Easier migrations
- JSONB can store arbitrary relation structures
- Native PostgreSQL recursion (CTEs, window functions)

**Cons**:
- Complex queries become very long CTEs
- No native graph algorithms (shortest path, etc.)
- Harder to visualize relations
- May need Elasticsearch for complex search

**Rejection**: Viable for MVP, but limits future product vision. PostgreSQL recursion becomes bottleneck at 10k+ terms.

### Alternative B: Neo4j-only (drop PostgreSQL)
**Pros**:
- True graph database semantics
- Best performance for relation queries
- Cleaner schema

**Cons**:
- Lose ACID guarantees for critical data (users, terms)
- Neo4j transactions weaker than PostgreSQL
- Need separate storage for user auth, settings
- Operational burden higher than combo approach

**Rejection**: Too risky for production MVP. Need relational DB for user/session data.

## Activation Criteria

### Condition 1: Scale Evaluation (v0.2 milestone)
**Trigger**: When term count reaches 5,000 in production
**Decision**:
- Benchmark Neo4j vs PostgreSQL recursive queries
- Measure latency for common patterns (find related terms, depth=3)
- If Neo4j < PostgreSQL latency × 0.5 → Keep Neo4j
- Else → Migrate to PostgreSQL-only

**Acceptance criteria**:
```
SELECT
  CASE
    WHEN neo4j_p95_latency < postgres_recursive_cte_p95 * 0.5 THEN 'KEEP_NEO4J'
    ELSE 'MIGRATE_TO_PG_ONLY'
  END as decision
FROM benchmark_results
WHERE term_count = 5000;
```

### Condition 2: Complexity Threshold (Operational)
**Trigger**: If Neo4j sync fails > 2% of the time OR causes production incident
**Decision**: Disable Neo4j, migrate to PostgreSQL-only immediately

### Condition 3: Cost Analysis (v1.0)
**Trigger**: Before production scaling decision
**Review**:
- PostgreSQL (RDS): ~$50/month base
- Neo4j (Aura): ~$150/month minimum + scaling costs
- Dev time maintaining dual schema: 10-20% overhead
- If ROI of graph features < cost → Consolidate to PostgreSQL

## Rollback Plan

### PostgreSQL ← Neo4j Export (if needed)
**Scenario**: Decide to drop Neo4j after v0.2
**Steps**:
1. Export Neo4j term relationships as JSON
   ```cypher
   MATCH (source:Term)-[r]-(target:Term)
   RETURN source.id, r.type, target.id, r.strength, r.confidence
   ```
2. Transform JSON → PostgreSQL JSONB format
3. Import into `ontological_relations` table
4. Verify data integrity (count relations, sample validation)
5. Deprecate Neo4j service
6. **Time estimate**: 2-4 hours total

### PostgreSQL → Neo4j Migration (full adoption)
**Scenario**: Decide to make Neo4j primary after v0.2
**Steps**:
1. Implement bidirectional sync service (Kafka/Temporal job)
2. Export all PostgreSQL terms → Neo4j
3. Implement read-through caching
4. Gradually shift queries to Neo4j
5. Monitor performance
6. **Time estimate**: 2-3 weeks

## Related Decisions
- ADR-0005-postgres-primary: PostgreSQL as source of truth
- ADR-0002-authentication: Auth data stays in PostgreSQL only

## Implementation Status (Sprint 2)

- [x] Neo4j docker-compose service
- [x] Schema + constraints + indexes
- [x] Python client wrapper (neo4j.py)
- [x] Cypher initialization scripts
- [x] Basic CRUD operations
- [ ] Data sync logic (PostgreSQL → Neo4j)
- [ ] Integration tests for both DBs
- [ ] Documentation of dual-DB patterns

## Monitoring Checklist

Before shipping v0.1:
- [ ] Neo4j container starts/stops cleanly
- [ ] Cypher queries execute without errors
- [ ] Python driver handles connection failures
- [ ] Documented how to drop Neo4j if needed

Before scaling to production:
- [ ] Benchmark at 1k, 5k, 10k terms
- [ ] Monitor Neo4j disk usage
- [ ] Verify sync reliability (if implemented)
- [ ] Cost analysis vs PostgreSQL-only

## Approval

- Technical Review: ______ (date)
- PM Sign-off: ______ (date)
- Architecture Review: ______ (date)

---

**Next Review Date**: v0.2 release (when term count > 1,000)
**Last Updated**: 2025-11-16
