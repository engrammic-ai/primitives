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
    ← referenced from Memory "security-policy.md excerpt"
      ← ingested from source "internal wiki"
```

Implementation: Nodes are connected via edges (REFERENCES, DERIVED_FROM, etc.) that trace the evidence chain. The `trace()` tool walks these edges backward to the source.

### 2. Time-Travel

Query the epistemic state at any point in time.

```
as_of("2026-04-01"): "OAuth tokens expire in 7 days"
as_of("2026-04-20"): "OAuth tokens expire in 30 days"
```

Implementation: Bi-temporal fields (`valid_from`, `valid_to`) on all content nodes. Queries can filter by valid time to reconstruct historical knowledge state.

### 3. Belief History

Track how understanding of a subject evolved.

```
Subject: "OAuth token expiry"
Timeline:
  2026-03-01: Claim "7 days" (confidence 0.85) [ACTIVE]
  2026-04-15: Claim "30 days" (confidence 0.92) [ACTIVE, SUPERSEDES previous]
```

Implementation: `SUPERSEDES` edges form chains. Each new Claim or Fact can reference the node it replaces. Traversing these chains shows the evolution of understanding.

### 4. Self-Reflection

Agent stores observations about its own cognition as Memory nodes.

```
Memory:
  memory_type: "reflection"
  content: "I noticed my belief about token expiry changed significantly
            after reading the new security policy. The previous document
            may have been outdated."
  ABOUT: [fact-old, fact-new, doc-policy]
```

Implementation: Memory nodes with `memory_type="reflection"` encode agent self-observations. ABOUT edges link to the entities the agent is reflecting on.

## Relationship to EAG Layers

Meta-Memory is orthogonal to the four cognitive layers:

```
┌─────────────────────────────────────────────────────────┐
│                     Meta-Memory                        │
│  provenance · time-travel · belief-history · reflection │
│ ┌─────────────────────────────────────────────────────┐ │
│ │                  Intelligence                       │ │
│ │      epistemic state, breakthroughs (Phase 2)       │ │
│ ├─────────────────────────────────────────────────────┤ │
│ │                    Wisdom                           │ │
│ │         beliefs, commitments (synthesized)          │ │
│ ├─────────────────────────────────────────────────────┤ │
│ │                   Knowledge                         │ │
│ │              claims, facts (verified)               │ │
│ ├─────────────────────────────────────────────────────┤ │
│ │                    Memory                           │ │
│ │       observations, reflections, documents          │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

Each content node across all layers has:
- Bi-temporal fields (valid_from, valid_to, created_at, updated_at) for time-travel
- Edge connections (REFERENCES, DERIVED_FROM) for provenance
- SUPERSEDES edges for belief history

Meta-Memory queries span all layers using these shared structures.

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

## Reflection Memory Nodes

Memory nodes with `memory_type="reflection"` encode metacognitive observations:

Schema:
```
(:Memory {
  id: string,
  content: string,              // the observation itself
  memory_type: "reflection",    // indicates this is a self-observation
  confidence: float,            // agent's confidence in this observation
  created_at: datetime,
  agent_id: string,
  silo_id: string
})-[:ABOUT]->(:Memory|:Claim|:Fact|:Belief|:*)
```

Common reflection types encoded in content:
- `belief_change` — agent noticed a belief was superseded
- `confidence_shift` — agent noticed confidence changed
- `contradiction` — agent noticed conflicting information
- `uncertainty` — agent noticed high uncertainty about something
- `correction` — agent acknowledges a previous error
- `insight` — agent formed a new understanding
- `pattern` — agent identified a recurring theme or connection

ABOUT edges link to the specific entities being reflected upon, enabling queries like "what has this agent reflected on?" or "find reflections connected to this Fact."

## Interface (MCP Tools)

| Tool | Purpose |
|------|---------|
| `remember(observation)` | Store reflection as Memory node (memory_type="reflection") |
| `recall(query)` | Search knowledge across all layers |
| `trace(node_id)` | Walk provenance chain (edges backward to source) |
| `learn(claim, evidence)` | Record verified claim to Knowledge layer |
| `update(node_id, claim, evidence)` | Supersede existing Knowledge node |

Note: There is no `reflect()` tool. Self-reflection is accomplished via `remember()` with appropriate content marking it as metacognitive observation.

## Design Principles

### 1. Non-invasive

Meta-Memory doesn't change how the four layers work. It adds observability without modifying core semantics. Reflection is just another Memory node type.

### 2. Explicit over implicit

Agents explicitly call `remember()` to store reflections. The system doesn't auto-generate reflections (though it could in the future via SAGE components).

### 3. Silo-scoped

All nodes, including reflections, respect silo boundaries. An agent's reflections in silo A are not visible in silo B.

### 4. No decay

Unlike transient Memory content, reflection nodes provide permanent audit trails and are valuable for understanding agent behavior over time.

## Example: Belief Supersession with Reflection

A complete scenario showing metacognition in action:

1. Agent learns initial claim:
   ```
   learn("OAuth tokens expire in 7 days", evidence="old_policy.md")
   → Creates Claim node C1 with confidence 0.85
   ```

2. Later, agent learns new information:
   ```
   learn("OAuth tokens expire in 30 days", evidence="new_policy.md", supersedes="C1")
   → Creates Claim node C2 with confidence 0.92
   → C2 has SUPERSEDES edge to C1
   ```

3. SAGE promotes both to Facts after corroboration, C2 becomes the active Fact F2

4. Agent reflects on this change:
   ```
   remember("I initially believed tokens expired in 7 days after reading the old policy.
            Today I learned the expiry changed to 30 days when the security policy was updated.
            This is a significant security implication.")
   → Creates Memory node M with memory_type="reflection"
   → M has ABOUT edges to [C1, C2, F2, policy-doc-nodes]
   ```

5. Later, trace the evolution:
   ```
   trace(F2) → walks DERIVED_FROM → C2 → SUPERSEDES → C1 → REFERENCES → old_policy.md
   recall("token expiry") → includes M as contextual reflection on the belief
   ```

This enables complete auditability: not just what the agent believes now, but why it changed, when it changed, and the agent's own reasoning about the change.

