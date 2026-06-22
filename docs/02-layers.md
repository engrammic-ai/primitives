# 02 — The Four Layers (KMWI)

## Memory

**Semantics:** Gaussian decay. Experiences fade over time. Retrieval weight drops toward zero but content is preserved (until hard-deleted per the Cold Memory policy — see erasure rules).

**Node types:**
- `:Memory` — a raw observation from an agent (consolidates what were previously Document, Passage, Utterance, Event, and Observation). The `memory_type` property distinguishes subtypes at query time.

**Scoring:** `similarity × fresh(t) × heat × proximity(candidate, query_anchors)`
- `fresh(t)` is the Gaussian per-class decay (ephemeral 7d, standard 90d, durable 540d, permanent 5y)
- `heat` is ambient access-recency PPR (Heat-PPR)
- `proximity` is query-time ego-graph PPR (Anchor-PPR)

## Knowledge

**Semantics:** indefinite supersession. Facts persist until contradicted. No time decay.

**Node types:**
- `:Claim` — an agent assertion with evidence, awaiting promotion. Persistent but scored lower than Facts.
- `:Fact` — a SAGE-promoted proposition, corroborated by 3+ independent sources. Every Fact has at least one `DERIVED_FROM` edge to a Memory-layer source. No orphan Facts.

**Structural rule:** agents write Claims; the Custodian promotes to Fact. Agents never write Fact nodes directly.

**Supersession:** when a new Fact contradicts an existing Fact, the Custodian writes `(:Fact_new)-[:SUPERSEDES]->(:Fact_old)` with `reason ∈ {'contradiction', 'evidence_shift', 'author_update', 'evidence_erased'}`. The old Fact remains queryable — audit and temporal queries (`as_of`) walk the SUPERSEDES chain.

**Scoring:** `similarity × confidence × corroboration × proximity × NOT_superseded`

## Wisdom

**Semantics:** evidence-gated revision. Beliefs update when the underlying fact distribution shifts past a threshold, not on a clock.

**Node types:**
- `:Belief` — a SAGE-synthesized judgment over a cluster of Facts (cluster density >= 3). System-created only; agents do not write Beliefs directly.
- `:Commitment` — a declared stance authored by an agent via `decide()`. Agent-writable.

**Transitions in:** Knowledge -> Wisdom via synthesis (cluster density threshold triggers Synthesizer). Wisdom -> Wisdom via revision (distribution shift >= M% triggers a new Belief with a `SUPERSEDES` edge to the old one). Old Beliefs remain queryable for audit and `as_of` temporal queries — Beliefs are never replaced in place.

**Scoring:** `similarity × evidence_strength × underlying_fact_recency × proximity × wisdom_status_multiplier`
- `wisdom_status ∈ {'active', 'stale'}`; stale Beliefs score at 0.1x (defined by erasure cascade)

## Intelligence

**Semantics:** passive observation artifacts. System-created, not agent-written. Phase 2 feature — not yet active in production.

**Node types:**
- `:EpistemicState` — a confidence/confusion snapshot captured by the system
- `:Breakthrough` — records what resolved a stuck or contradictory epistemic state

**Agent paths to Wisdom (current behavior):**
- `decide` tool -> creates `:Commitment` directly (no Intelligence promotion path)
- Intelligence-layer nodes are not retrieved cross-session in Phase 1

**Scoring:** session-scoped only in Phase 1. Not retrieved cross-session.

## Why these four (and not three or five)

- Three (conflating Knowledge and Wisdom) loses the authored-vs-synthesised distinction. A Commitment is not a Fact; a Belief about team patterns is not a Fact either. Both are Wisdom.
- Five (splitting Memory into raw-vs-compressed) is a storage tier, not a persistence-semantics distinction. Doesn't deserve top-level status.
- The four map cleanly onto distinct transition rules and distinct retrieval-scoring needs. That's the architectural test.

## Layer tagging

Every node carries a `PersistenceLayer` enum:

```python
class PersistenceLayer(StrEnum):
    MEMORY = "memory"
    KNOWLEDGE = "knowledge"
    WISDOM = "wisdom"
    INTELLIGENCE = "intelligence"
```

Used for:
- Retrieval scoring dispatch
- Custodian worker routing
- Telemetry grouping
- Erasure cascade classification

## Agent-writable vs system-created

| Node | Writer |
|------|--------|
| `Memory` | Agent (`remember`) |
| `Claim` | Agent (`learn`) |
| `Commitment` | Agent (`decide`) |
| `Fact` | SAGE Custodian (promoted from Claim) |
| `Belief` | SAGE Synthesizer (promoted from Facts) |
| `EpistemicState` | System (Phase 2) |
| `Breakthrough` | System (Phase 2) |
