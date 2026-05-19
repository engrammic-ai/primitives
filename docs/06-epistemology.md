# 06 — Epistemology: deterministic primitives

## Architectural commitment

Extraction produces **structured claims** in the form `(subject, predicate, object) + rationale`. The epistemology library operates on structured claims and is a pure function. LLM calls happen at extraction time, never at adjudication.

**Consequence:** promotion, supersession, and synthesis decisions are replayable, auditable, fast, cheap.

This is the core of what `primitives` exposes: all four primitives below are implemented as pure functions in `primitives.epistemology`.

## The four primitives

| Primitive | Deterministic? | Implementation |
|---|---|---|
| Contradiction detection | Mostly (hybrid) | Structural first; LLM only for semantic edge cases |
| Confidence | Fully | Multiplicative formula over four factors |
| Corroboration | Fully | `count(distinct sources of (s, p, o))` |
| Provenance | Fully | Transaction invariant (DERIVED_FROM exists at commit) |

## Contradiction detection

**Structural:** same subject, same predicate, different object → contradiction. Requires entity resolution + predicate registry.

```
(:Fact {s: 'tokens', p: 'expires_in', o: '30d'})
(:Fact {s: 'tokens', p: 'expires_in', o: '90d'})  # contradiction
```

**LLM fallback:** only for semantic cases where structural check misses — "never" vs "rarely", hedged assertions, temporal scope mismatch. Should be rare if predicate registry is well-designed. Fallback calls are logged and cached.

## Confidence math

```
combined_confidence = source_tier × corroboration_factor × method_weight × raw_confidence
```

| Factor | Values |
|---|---|
| `source_tier` (by agent.trust_tier and document type) | 1.0 authoritative / 0.85 validated / 0.6 community / 0.4 unknown |
| `corroboration_factor` | `1 - exp(-0.5 × n)` where n = distinct corroborating sources. Caps at 1.0. |
| `method_weight` | 0.85 validated extractor / 0.75 standard / 0.6 experimental |
| `raw_confidence` | LLM's self-reported score for this extraction (0..1) |

**Known structural ceiling:** community-tier-only corroboration maxes at 0.383 (`0.6 × 1.0 × 0.75 × 0.85`). Therefore R2 community-tier promotion requires **>=1 authoritative source** in the corroboration set. See service-layer threshold configuration.

## Corroboration math

```
corroboration_count(claim) = |distinct(source_node_id for claim_with_same_spo)|
```

Weighted variant (future):

```
weighted_corroboration = sum(1 × agent.trust_tier / 10 for each distinct source)
```

Used in promotion rules and supersession priority.

## Provenance invariants

Enforced at commit time by the Custodian (service layer) — not at read time. The epistemology library exposes these as validation functions.

- **I1:** every `:Fact` has >= 1 `DERIVED_FROM` to a Memory-layer source
- **I2:** every `:Belief` has >= N `SYNTHESIZED_FROM` to `:Fact` (N is the synthesis threshold)
- **I3:** every `:Fact` with `PROMOTED_FROM` has >= K incoming edges from distinct agents (consensus rule)
- **I4:** no cycles in provenance edges — layer ordering enforces it (edges always point backwards in layer order: Knowledge -> Memory; Wisdom -> Knowledge; never forwards)
- **I5:** `SUPERSEDES` edges require non-null `reason ∈ {'contradiction', 'evidence_shift', 'author_update', 'evidence_erased'}`
- **I6:** every `:ReasoningChain` has >= 1 `DERIVED_FROM_EVIDENCE` edge when `source='session_trace_inferred'` or >= 1 `CRYSTALLIZED_INTO` edge when `source='agent_explicit'`

Violations are rejected at write time, not ignored.

## Clean seam: extraction vs Custodian

What lives in extraction (not Custodian):
- LLM calls to turn text into structured claims
- Entity resolution (surface form -> canonical entity)
- Coref and NER (optional preprocessing)
- Open-vocabulary rejection (claims with unregistered predicates go to admin queue)

What lives in Custodian (not extraction):
- Contradiction detection against existing Facts
- Promotion decision (apply R1/R2/R3 rules)
- Synthesis triggers
- Revision decisions
- Consensus detection

The `primitives.epistemology` functions are the shared math that both sides can call. Extraction calls `combined_confidence` and `detect_contradiction` (structural only). The Custodian calls promotion rules + full contradiction detection.
