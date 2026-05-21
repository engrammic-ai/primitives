# EAG - Epistemic Augmented Generation

Reference documentation for the EAG paradigm implemented in this library.

## What is EAG

EAG (Epistemic Augmented Generation) is a four-layer cognitive architecture for AI agents. Information flows through distinct persistence regimes:

- **Memory** - experiences that fade (Gaussian decay)
- **Knowledge** - facts that persist until contradicted (indefinite supersession)
- **Wisdom** - beliefs that revise on evidence shift (evidence-gated revision)
- **Intelligence** - ephemeral reasoning (session-scoped)

Unlike RAG, EAG adjudicates (via a Custodian), tracks provenance, supports supersession, and shapes itself around usage (heat). Extraction produces structured claims; the epistemology library is deterministic.

## What this library provides

`primitives` implements the open, deterministic parts of EAG:

- **Epistemology** - confidence math, contradiction detection, promotion rules (R1/R2), corroboration. Pure functions, no LLM at decision time.
- **Signals** - heat, freshness, priority scoring formulas.
- **Schema** - node type definitions, `PersistenceLayer` enum, edge catalogue.
- **Protocols** - `KnowledgeStore`, `LifecycleManager`, `SignalProvider`, `ProvenanceTracker`.
- **Shared utilities** - used across modules.

What is NOT in this library (proprietary to the service layer):

- Custodian workers (promotion, synthesis, revision scheduling)
- Extraction prompts and LLM orchestration
- Graph + vector write paths
- Storage backends (Memgraph, Qdrant, Redis, Postgres)
- API and MCP interface

## Specs index

| Doc | Contents |
|-----|----------|
| [01-paradigm.md](01-paradigm.md) | Why EAG, the category error in RAG, when EAG pays off |
| [02-layers.md](02-layers.md) | KMWI layer semantics, node types, scoring formulas |
| [03-transitions.md](03-transitions.md) | Transition catalogue (T1-T15), execution rules, provenance |
| [04-metacognition.md](04-metacognition.md) | Meta-memory, provenance, time-travel, reflection |
| [05-mcp-contract.md](05-mcp-contract.md) | MCP tool contract and invariants |
| [06-epistemology.md](06-epistemology.md) | Deterministic primitives: confidence, contradiction, corroboration |
| [07-agent-usage.md](07-agent-usage.md) | Agent cognitive guide for EAG usage |
| [08-data-lifecycle.md](08-data-lifecycle.md) | Forget, decay, hard-delete, GDPR erasure |

## Reading order

1. [01-paradigm.md](01-paradigm.md) - what and why
2. [02-layers.md](02-layers.md) - KMWI taxonomy
3. [03-transitions.md](03-transitions.md) - architecture lives here
4. [06-epistemology.md](06-epistemology.md) - deterministic primitives (maps directly to this library's API)
