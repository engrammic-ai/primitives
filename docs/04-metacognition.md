# Metacognition and Meta-Memory

> Thinking about thinking. Knowledge about knowledge.

## Overview

Metacognition is the ability to reason about one's own cognitive state. In the EAG architecture, this manifests as **Meta-Memory**: a cross-cutting capability that enables agents to introspect their epistemic history.

This is not a fifth layer. It's infrastructure that makes the four layers (Memory, Knowledge, Wisdom, Intelligence) observable and queryable.

## Why Metacognition Matters

| Without Metacognition | With Metacognition |
|----------------------|-------------------|
| "I believe X" | "I believe X because document D said so" |
| Silent belief changes | "My belief about X changed when I read Y" |
| Current state only | "Last week I thought Z, now I think W" |
| No self-awareness | "I notice I'm uncertain about this" |

Metacognition enables:
- **Auditability**: Trace any belief to its source
- **Debugging**: Understand why an agent behaved a certain way
- **Learning**: Agent notices patterns in its own belief changes
- **Trust**: Users can ask "why do you believe that?" and get a real answer

## Core Capabilities

### 1. Provenance

Every belief traces back to its source.

```
Fact: "OAuth tokens expire in 30 days"
  ← promoted from Claim (confidence: 0.88)
    ← extracted from Document "security-policy.md"
      ← ingested from source "internal wiki"
```

Implementation: `REFERENCES` and `PROMOTED_FROM` edges already exist. Meta-Memory exposes them via query API.

### 2. Time-Travel

Query the epistemic state at any point in time.

```
as_of("2026-04-01"): "OAuth tokens expire in 7 days"
as_of("2026-04-20"): "OAuth tokens expire in 30 days"
```

Implementation: Bi-temporal fields (`valid_from`, `valid_to`) on all nodes. Meta-Memory adds temporal filtering to queries.

### 3. Belief History

Track how understanding of a subject evolved.

```
Subject: "OAuth token expiry"
Timeline:
  2026-03-01: "7 days" (confidence 0.85)
  2026-04-15: superseded → "30 days" (confidence 0.92)
```

Implementation: `SUPERSEDES` edges form chains. Meta-Memory traverses and aggregates them.

### 4. Reflection

Agent stores observations about its own cognition.

```
MetaObservation:
  "I noticed my belief about token expiry changed significantly
   after reading the new security policy. The previous document
   may have been outdated."
  ABOUT: [fact-old, fact-new, doc-policy]
```

Implementation: New `:MetaObservation` node type with `ABOUT` edges to referenced nodes.

## Relationship to EAG Layers

Meta-Memory is orthogonal to the four cognitive layers:

```
┌─────────────────────────────────────────────────────────┐
│                     Meta-Memory                        │
│   provenance · time-travel · belief-history · reflection│
│ ┌─────────────────────────────────────────────────────┐ │
│ │                  Intelligence                       │ │
│ │           ephemeral reasoning chains                │ │
│ ├─────────────────────────────────────────────────────┤ │
│ │                    Wisdom                           │ │
│ │         patterns, beliefs, commitments              │ │
│ ├─────────────────────────────────────────────────────┤ │
│ │                   Knowledge                         │ │
│ │         claims, facts, citations                    │ │
│ ├─────────────────────────────────────────────────────┤ │
│ │                    Memory                           │ │
│ │         passages, events, utterances                │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

Each layer has:
- Bi-temporal fields (for time-travel)
- REFERENCES edges (for provenance)
- SUPERSEDES edges (for belief history)

Meta-Memory queries span all layers.

## Bi-Temporal Model

Every node tracks two time dimensions:

| Field | Dimension | Question |
|-------|-----------|----------|
| `valid_from` | Valid time | When did this become true in reality? |
| `valid_to` | Valid time | When did this stop being true? |
| `created_at` | System time | When did we learn this? |
| `updated_at` | System time | When was the record last modified? |

This enables queries like:
- "What did I believe on April 1st?" (valid time)
- "What had I learned by April 1st?" (system time)
- "When did I first learn about X?" (created_at)

## MetaObservation Node

Schema:
```
(:MetaObservation {
  id: string,
  content: string,              // the observation itself
  observation_type: enum,       // belief_change, contradiction, insight, etc.
  confidence: float,            // how confident agent is in this observation
  created_at: datetime,
  agent_id: string,
  silo_id: string
})-[:ABOUT]->(:Fact|:Claim|:Document|:*)
```

Observation types:
- `belief_change` — agent noticed a belief was superseded
- `confidence_shift` — agent noticed confidence changed
- `contradiction` — agent noticed conflicting information
- `uncertainty` — agent noticed high uncertainty
- `correction` — agent acknowledges previous error
- `insight` — agent formed a new understanding

## Interface (MCP Tools)

| Tool | Purpose |
|------|---------|
| `context_provenance(node_id)` | Trace citation chain to source |
| `context_lookup(query, as_of)` | Query historical state |
| `context_belief_history(subject)` | Show belief evolution |
| `context_reflect(observation, about)` | Store meta-observation |
| `context_get_reflections(node_id)` | Retrieve meta-observations |

## Design Principles

### 1. Non-invasive

Meta-Memory doesn't change how the four layers work. It adds observability without modifying core semantics.

### 2. Explicit over implicit

Reflection is explicit: agent calls `context_reflect()`. The system doesn't auto-generate meta-observations (though it could in the future).

### 3. Silo-scoped

Meta-observations respect silo boundaries. An agent's reflections about silo A are not visible in silo B.

### 4. No decay

Unlike Memory layer content, meta-observations don't decay. They're valuable for long-term audit trails.

## Open Questions

1. **Auto-reflection**: Should the system auto-generate observations on supersession, confidence changes, or contradictions?

2. **Cross-silo metacognition**: Can an agent have meta-observations that span silos?

3. **Hierarchical reflection**: Can an agent have meta-observations about other meta-observations? (meta-meta-memory)

4. **Agent identity**: How does agent identity interact with reflection? Are reflections agent-specific or shared?

## References

- [Meta-Memory Roadmap](../../context-service/context/plans/meta-memory-roadmap.md)
- [Phase 1: Provenance](../../context-service/context/plans/meta-memory/phase-1-provenance.md)
- [Phase 2: Time-Travel](../../context-service/context/plans/meta-memory/phase-2-time-travel.md)
- [Phase 3: Belief History](../../context-service/context/plans/meta-memory/phase-3-belief-history.md)
- [Phase 4: Reflection](../../context-service/context/plans/meta-memory/phase-4-reflection.md)
