# Primitives — Open Research Questions

## Axiom-to-primitive gaps (2026-06-25)

From axioms-of-humanness session. Two axioms lack clear primitive backing:

### Curiosity primitive
> "Understanding isn't a destination. It's a pull toward what you don't yet know."

Questions:
- What would a "what don't I know" query look like?
- Can the graph surface knowledge gaps (missing edges, low-confidence regions)?
- Should agents be able to declare "I need to know X" as a first-class node type?
- Relationship to SAGE synthesis — does synthesis reveal gaps?

### Context primitive
> "The same fact means different things in different moments. Truth without situation is abstraction."

Questions:
- Temporal reasoning beyond supersession chains — "what was true at T?"
- Situational scoping — fact valid in context A but not B?
- Action/effect modeling — "I did X, observed Y" (flagged in fundraise review as missing)
- Does this belong in primitives or in the service layer?

### Will primitive
> "Knowledge without agency is passive. Understanding is meant to be used."

Questions:
- Action/effect modeling — "I did X, observed Y" as first-class node type
- How do actions link to beliefs that informed them?
- Feedback loops: action outcome reinforces or refutes originating belief?
- Relationship to embodied AI / robotics wedge

### Meaning primitive
> "Knowledge without purpose is trivia. Humans know things *for* something."

Questions:
- Relevance scoring tied to purpose — how to represent "what is this for?"
- Dead-end beliefs decay faster — how to detect "serves nothing"?
- Goal/purpose nodes? Or implicit via usage patterns?
- Relationship to SAGE synthesis — does synthesis surface relevance?

### Intent-aware provenance (Transparency gap)
> Current supersession reasons are structural (contradiction, evidence_shift, etc). They say WHAT changed, not WHY the agent cared.

Gap identified: provenance shows mechanics, not motivation.

Questions:
- Goal linkage — supersession edges carry optional `goal_context`?
- Trigger capture — was update pulled (agent sought) or pushed (evidence arrived)?
- Decision context — what question was agent answering when it realized old belief was wrong?
- Impact annotation — "updating because X depends on this and X was failing"

Design options:
- Optional `intent` field on SUPERSEDES edges
- Separate MOTIVATED_BY edge type linking to goal/task nodes
- Capture at write time via `learn()`/`update()` with optional intent param

---

See also: `~/.claude-bits/engrammic/axioms-and-culture-2026-06-25.md`
