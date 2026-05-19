# 02 — The Four Layers (KMWI)

## Memory

**Semantics:** Gaussian decay. Experiences fade over time. Retrieval weight drops toward zero but content is preserved (until hard-deleted per the Cold Memory policy — see erasure rules).

**Node types:**
- `:Document` — an ingested source (file, page, transcript)
- `:Passage` — a chunk within a Document
- `:Utterance` — something an agent or human said in a conversation
- `:Event` — a system-observed occurrence (tool called, ingestion ran)

**Scoring:** `similarity × fresh(t) × heat × proximity(candidate, query_anchors)`
- `fresh(t)` is the Gaussian per-class decay (ephemeral 7d, standard 90d, durable 540d, permanent 5y)
- `heat` is ambient access-recency PPR (Heat-PPR)
- `proximity` is query-time ego-graph PPR (Anchor-PPR)

## Knowledge

**Semantics:** indefinite supersession. Facts persist until contradicted. No time decay.

**Node types:**
- `:Fact` — a validated proposition
- `:Claim` — an extracted proposition awaiting promotion (unpromoted Claim is persistent but scored lower)

**Structural rule:** every `:Fact` has at least one `DERIVED_FROM` edge to a Memory-layer source. No orphan Facts.

**Supersession:** when a new Fact contradicts an existing Fact, the Custodian writes `(:Fact_new)-[:SUPERSEDES]->(:Fact_old)` with `reason ∈ {'contradiction', 'evidence_shift', 'author_update', 'evidence_erased'}`. The old Fact remains queryable — audit and temporal queries (`as_of`) walk the SUPERSEDES chain.

**Scoring:** `similarity × confidence × corroboration × proximity × NOT_superseded`

## Wisdom

**Semantics:** evidence-gated revision. Beliefs update when the underlying fact distribution shifts past a threshold, not on a clock.

**Node types:**
- `:Belief` — a synthesised judgment over many Facts
- `:Pattern` — a recurring shape detected across Facts
- `:Commitment` — a declared stance (agent-authored)
- `:ProposedBelief` — a weak synthesis awaiting validation (status: pending/accepted/rejected)

**Transitions in:** Knowledge → Wisdom via synthesis (cluster density threshold). Knowledge → Wisdom via propose (weak confidence creates ProposedBelief). Wisdom → Wisdom via revision (distribution shift >= M%). ProposedBelief → Belief via accept. ProposedBelief → tombstone via reject.

Revision writes a new `:Belief` with a `SUPERSEDES` edge to the old Belief, `reason='evidence_shift'`. Old Beliefs remain queryable for audit and `as_of` temporal queries — Beliefs are never replaced in place.

> **Cross-layer exception:** `:Commitment` is structurally a Knowledge-layer Claim subtype (multi-labeled `:Claim:Commitment`, SPO-structured, predicate-registry-governed) but carries Wisdom-layer semantics (authored stance via `DECLARED_BY`, reconcilable by the `commitment_reconciler`, revisable on author update). This is the single cross-layer node type in CAG; every other node belongs to exactly one layer.

**Scoring:** `similarity × evidence_strength × underlying_fact_recency × proximity × wisdom_status_multiplier`
- `wisdom_status ∈ {'active', 'stale'}`; stale Beliefs score at 0.1x (defined by erasure cascade)

## Intelligence

**Semantics:** ephemeral inference. Session-scoped. Temporary computational state.

**Node types:**
- `:ReasoningChain` — a stored reasoning sequence with steps inlined as a `steps: list[ChainStep]` JSON property (not separate nodes)
- `:QueryContext` — the working set assembled for a specific query
- `:WorkingHypothesis` — an agent's in-progress hypothesis during reasoning (session-scoped, mutable)

**Promotion paths out:**
- `Intelligence → Knowledge` via consensus: >= K chains from effective_J >= threshold agents agree → promote to Fact
- `Intelligence → Memory` via trace: reasoning chain completes → compact trace stored as experience
- `Intelligence → Wisdom` via commit: agent declares a stance from session work → Commitment

**Scoring:** session-scoped only. Not retrieved cross-session (the session-end trace lives in Memory afterwards).

## Why these four (and not three or five)

- Three (conflating Knowledge and Wisdom) loses the authored-vs-synthesised distinction. A Commitment is not a Fact; a Belief about team patterns is not a Fact either. Both are Wisdom.
- Five (splitting Memory into raw-vs-compressed) is a storage tier, not a persistence-semantics distinction. Doesn't deserve top-level status.
- The four map cleanly onto distinct transition rules and distinct retrieval-scoring needs. That's the architectural test.

## Layer tagging

Every node carries a `PersistenceLayer` enum:

```python
class PersistenceLayer(str, Enum):
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
