# ADR Template - Architecture Decision Records

Use this template for every significant architecture decision.

```markdown
# ADR-NNNN: Brief Descriptive Title

**Date**: YYYY-MM-DD
**Status**: Proposed | Accepted | Deprecated | Superseded by ADR-XXXX
**Deciders**: [PM name], [Lead Dev name], [Architect]
**Consulted**: [CTO, stakeholders]
**Informed**: [Team members]

## Context
What is the issue that we're addressing?
What constraints or prerequisites exist?

## Decision
What is our decision?
Why are we making this decision?

## Rationale
Detailed justification.
Why this is the best approach given the context.

## Consequences

### Positives
- Benefit 1
- Benefit 2

### Negatives
- Tradeoff 1
- Tradeoff 2
- Mitigation strategy for each

## Alternatives Considered

### Alternative A: [Name]
- Pros: ...
- Cons: ...
- Rejection reason: ...

### Alternative B: [Name]
- Pros: ...
- Cons: ...
- Rejection reason: ...

## Activation Criteria
When should this decision be revisited or changed?
What metrics/conditions trigger re-evaluation?

Example:
- If term count > 10k and Neo4j latency < 50% PostgreSQL, keep Neo4j
- If term count < 1k, consider PostgreSQL-only simplification

## Rollback Plan
How can we revert this decision if needed?
Time estimate + effort?

Example:
- Neo4j → PostgreSQL: Export graph as JSON, import to JSONB column (< 1h)
- SvelteKit → Other framework: Build layer already exists (~2 weeks)

## Related Decisions
- ADR-XXXX: [Related decision]
- ADR-YYYY: [Dependent decision]

## Implementation Checklist
- [ ] Component/feature implemented
- [ ] Tests written
- [ ] Documentation updated
- [ ] Deployed to staging
- [ ] Monitoring configured

## Review & Approval
- [ ] Technical review: _____ (date)
- [ ] PM sign-off: _____ (date)
- [ ] Team informed: _____ (date)
```

---

## ADR Guidelines

### When to write an ADR
- Major tech choice (framework, DB, architecture pattern)
- Significant refactoring that affects multiple systems
- Trade-offs between alternatives
- Decisions that are hard to reverse

### When NOT to write an ADR
- Bug fixes
- Small features
- Implementation details that don't affect architecture
- Temporary hacks (these should trigger an issue instead!)

### Naming Convention
- `ADR-0001-neo4j-decision.md` (0-padded number)
- Filename matches title
- Lowercase, kebab-case

### Status Lifecycle
1. **Proposed** - Initial draft, under discussion
2. **Accepted** - Decided and approved
3. **Deprecated** - No longer applicable
4. **Superseded by ADR-XXXX** - Replaced by newer decision

### Review Process
1. Author writes ADR and posts to team Slack/Discord
2. Team reviews & comments (48h window)
3. Deciders approve
4. Commit to `docs/architecture/adr/`
5. Link from README + relevant project docs
