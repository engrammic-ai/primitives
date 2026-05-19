# 03 — Transitions: the architecture lives here

The layers themselves are a taxonomy. The **transitions** between them define the system's behaviour.

## Transition diagram

```
    Memory --- extract ---> Knowledge --- synthesize ---> Wisdom
      |                       |              |              |
      |                       v              v              |
      |                   supersede      propose         revise
      |                (Knowledge->     (creates       (Wisdom->Wisdom
      |                 Knowledge)    ProposedBelief)  on evidence shift)
      v                                    |
    decay                            accept/reject
   (retrieval                     (ProposedBelief ->
    weight -> 0)                   Belief or tombstone)

    Intelligence -- consensus ---> Knowledge
    Intelligence -- trace -------> Memory
    Intelligence -- commit ------> Wisdom (Commitment)
    Intelligence -- crystallize -> Wisdom (from WorkingHypothesis)
```

## Transition catalogue

| # | Transition | Trigger predicate | Execution | Priority |
|---|---|---|---|---|
| T1 | **Memory -> Knowledge** (extract) | passage is hot OR source-changed OR cold-but-queried | signal-driven | `heat × (1 / last_extracted_at)` |
| T2 | **Knowledge -> Knowledge** (supersede) | new Fact's (s, p, o) conflicts with existing Fact | eager (synchronous in validator) | N/A |
| T3 | **Knowledge -> Wisdom** (synthesize) | cluster density >= N AND no current Belief covers it | signal-driven | `heat × cluster_density` |
| T4 | **Wisdom -> Wisdom** (revise) | distribution shift >= M% since last synthesis | signal-driven — Revision = supersede-with-new-Belief, not in-place edit. Preserves audit chain. | `heat × shift_magnitude` |
| T5 | **Intelligence -> Knowledge** (consensus) | >= K reasoning chains from effective_J >= J agents agree | lazy | consensus timestamp |
| T6 | **Intelligence -> Memory** (trace) | reasoning chain completes | batched post-session | session end time |
| T7 | **Intelligence -> Wisdom** (commit) — writes `:Claim:Commitment` (Knowledge-structure, Wisdom-semantics) | agent declares a stance | eager | N/A |
| T8 | **Memory -> ⊥** (decay) | time-based; retrieval weight -> 0 | compute-at-query | N/A |
| T9 | **Memory -> ⊥** (hard-delete) | `age > 2 × class.σ` OR GDPR | scheduled GC (hard-delete default) | `age` |
| T10 | **Knowledge -> Wisdom** (propose) | synthesis confidence in weak range (above min, below auto-promote) | signal-driven | `heat × confidence` |
| T11 | **Wisdom -> Wisdom** (accept) | validator accepts ProposedBelief | eager | N/A |
| T12 | **Wisdom -> ⊥** (reject) | validator rejects ProposedBelief | eager | N/A |
| T13 | **Intelligence -> Wisdom** (crystallize) | agent crystallizes WorkingHypothesis | eager | N/A |

## The execution rule

- **Eager** for correctness-critical transitions (T2 supersession, T7 commit)
- **Signal-driven + heat-ranked** for optimisation transitions (T1 extract, T3 synthesize, T4 revise)
- **Batched / lazy / scheduled** for housekeeping (T5 consensus, T6 trace, T8/T9 decay)

## Why transitions, not layers, are the architecture

If you know the four layers but not the transitions, you can't build CAG. The layers tell you *what exists*; the transitions tell you *what moves*. A CAG implementation is largely the sum of its transition workers.

Consequence: the Custodian (service-layer proprietary) is internally structured as one worker per transition, plus a shared epistemology library. Transitions are first-class design objects.

The epistemology library in this package implements the deterministic decision functions that underlie T1, T2, T3, T5, and T7. Scheduling and execution of the transitions themselves lives in the service layer.

## Provenance across transitions

Every transition that creates a node writes a provenance edge back to its source(s):

- T1 extract: `(:Claim)-[:DERIVED_FROM]->(:Passage)` (Extraction owns)
- T2 supersede: `(:Fact_new)-[:SUPERSEDES]->(:Fact_old)` with reason + timestamp
- T3 synthesize: `(:Belief)-[:SYNTHESIZED_FROM]->(:Fact)+` (>= N required)
- T5 consensus: `(:Fact)-[:PROMOTED_FROM]->(:ReasoningChain)+`
- T6 trace: `(:ReasoningChain)-[:DERIVED_FROM_EVIDENCE]->(:Document|:Passage|:Claim)+`; optionally `(:ReasoningChain)-[:CRYSTALLIZED_INTO]->(:Claim)` for crystallizations
- T7 commit: `(:Claim:Commitment)-[:DECLARED_BY]->(:Agent)` (per D1); `CRYSTALLIZED_INTO` used for Intelligence->Knowledge linkage
- T10 propose: `(:ProposedBelief)-[:SYNTHESIZED_FROM]->(:Fact)+` (same as T3, but creates proposal)
- T11 accept: `(:Belief)-[:PROMOTED_FROM]->(:ProposedBelief)` with `accepted_at` timestamp
- T12 reject: `(:ProposedBelief)` marked `status='rejected'` with `reason` and `rejected_at`
- T13 crystallize: `(:Commitment)-[:CRYSTALLIZED_FROM]->(:WorkingHypothesis)`
