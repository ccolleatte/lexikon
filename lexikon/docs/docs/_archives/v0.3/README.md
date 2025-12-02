# V0.3 Analysis Archive

This directory contains archived analysis documents from the v0.3 planning phase.

## Files

### `analyse-critique-complete-p1.md` (470 lines)
**Status**: Archived - Meta-analysis (historical context)

Original: `analyse-critique-opus-v03-p1.md`

Analysis of strengths/weaknesses of v0.3 approach. Now superseded by:
- [ADRs](../architecture/ADR-*.md) - Formal decision records
- [Roadmap Tiers](../roadmap/) - Structured execution plan

**Value**: Historical reference for trade-offs considered

---

### `analyse-critique-complete-p2.md` (1130 lines)
**Status**: Archived - Technical reference

Original: `analyse-critique-opus-v03-p2.md`

Detailed architecture (PostgreSQL, Neo4j, LLM). Content now referenced in:
- [technical-spec-v03.md](../architecture/technical-spec-v03.md) - Active reference
- [ADR-0001](../architecture/ADR-0001-neo4j-decision.md) - Neo4j decision
- [TIER-2-IMPORTANT](../roadmap/TIER-2-IMPORTANT-weeks2-3.md) - DB implementation

**Value**: Concrete SQL schemas and Cypher patterns

---

### `analyse-plan-travail-risks.md` (280 lines)
**Status**: Archived - Planning critique (now in ADRs)

Original: `analyse-plan-travail-v03.md`

Critique of planning approach. Insights now captured in:
- [Roadmap Tiers](../roadmap/) - Risk-aware planning
- [ADRs](../architecture/) - Decision documentation

**Value**: Planning methodology lessons learned

---

### `checklist-validation-v03.md` (293 lines)
**Status**: Archived - Superseded by consolidated model

Original: `checklist-validation-v03.md`

Validation criteria. Content merged into:
- [term-model.md](../specifications/term-model.md) - Active specification

**Value**: Historical validation framework (v0.3)

---

## Active Documents

The most valuable content has been consolidated into active docs:

| Active Doc | Source | Purpose |
|---|---|---|
| [PRD-ontologie-v03.md](../specifications/PRD-ontologie-v03.md) | Original | Product requirements |
| [term-model.md](../specifications/term-model.md) | fiche-terme-v03.md | Operational term model |
| [user-journeys-v03.md](../ux/user-journeys-v03.md) | analyse-ux-parcours | **Critical UX insights** |
| [technical-spec-v03.md](../architecture/technical-spec-v03.md) | analyse-critique-p2 | Architecture reference |

---

## When to Use

- **Never**: For planning (use Roadmap Tiers + ADRs instead)
- **Occasionally**: For architectural context (PostgreSQL schema, Neo4j patterns)
- **Reference**: For historical decision trade-offs
- **Learning**: For planning methodology critique

---

**Archived**: 2025-11-16
**Purpose**: Keep historical context while maintaining focused active documentation
