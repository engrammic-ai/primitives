# 03 — Transitions: the architecture lives here

The layers themselves are a taxonomy. The **transitions** between them define the system's behaviour.

## Transition diagram

```
    Memory --- extract ---> Knowledge --- synthesize ---> Wisdom
      |                       |                            |
      |                       v                            |
      |                   supersede                     revise
      |                (Claim->Claim,               (Belief->Belief
      |                 Fact->Fact)                  on evidence shift)
      v
    decay
   (retrieval
    weight -> 0)

    Agent --------- decide ------> Wisdom (Commitment, direct declaration)

    Any ----------- forget ------> tombstone (soft-delete, cancel window)
    tombstone ---- cancel_forget -> restored (within window only)
    tombstone ---- hard_delete --> gone (scheduled GC, no recovery)
```

## Transition catalogue

| # | Transition | Trigger predicate | Execution | Priority |
|---|---|---|---|---|
| T1 | **Memory -> Knowledge** (extract) | passage is hot OR source-changed OR cold-but-queried | batch (SAGE custodian) | `heat × (1 / last_extracted_at)` |
| T2 | **Knowledge -> Knowledge** (supersede) | new Fact's (s, p, o) conflicts with existing Fact | eager (synchronous in validator) | N/A |
| T3 | **Knowledge -> Wisdom** (synthesize) | cluster density >= 3 AND no current Belief covers it | batch (SAGE synthesizer) | `heat × cluster_density` |
| T4 | **Wisdom -> Wisdom** (revise) | distribution shift >= M% since last synthesis | batch (SAGE synthesizer) | `heat × shift_magnitude` |
| T7 | **Agent -> Wisdom** (decide) | agent declares a stance via `decide` tool | eager | N/A |
| T8 | **Memory -> decay** | time-based; retrieval weight -> 0 | batch (SAGE decayer) | N/A |
| T9 | **Memory -> gone** (hard-delete) | `age > 2 × class.σ` OR GDPR erasure | scheduled GC | `age` |
| T14 | **Any -> tombstone** (forget) | agent calls `forget` tool | eager | N/A |
| T15 | **tombstone -> restored** (cancel_forget) | agent calls `cancel_forget` within cancel window | eager | N/A |

## The execution rule

- **Eager** for correctness-critical transitions (T2 supersession, T7 decide, T14 forget, T15 cancel_forget)
- **Batch (SAGE pipeline)** for optimization transitions (T1 extract, T3 synthesize, T4 revise)
- **Scheduled GC** for housekeeping (T8 decay, T9 hard-delete)

## Why transitions, not layers, are the architecture

If you know the four layers but not the transitions, you can't build EAG. The layers tell you *what exists*; the transitions tell you *what moves*. An EAG implementation is largely the sum of its transition workers.

Consequence: the Custodian (service-layer proprietary) is internally structured as one worker per transition, plus a shared epistemology library. Transitions are first-class design objects.

The epistemology library in this package implements the deterministic decision functions that underlie T1, T2, T3, and T7. Scheduling and execution of the transitions themselves lives in the service layer.

## Provenance across transitions

Every transition that creates a node writes a provenance edge back to its source(s):

- T1 extract: `(:Claim)-[:DERIVED_FROM]->(:Memory)` (extraction provenance)
- T2 supersede: `(:Fact_new)-[:SUPERSEDES]->(:Fact_old)` with reason + timestamp
- T3 synthesize: `(:Belief)-[:SYNTHESIZED_FROM]->(:Fact)+` (>= 3 required)
- T7 decide: `(:Commitment)-[:ABOUT]->(:node)+`
- T14 forget: node gains `tombstoned_at` + `cancel_window_expires` timestamps
- T15 cancel_forget: `tombstoned_at` cleared (only if within cancel window)
