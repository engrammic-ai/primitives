# 01 — Paradigm: LeAP (Layered Epistemic Agent Protocol)

## The category error in RAG

Plain RAG retrieves documents and appends them to a prompt. Systems built on top tend to apply **one persistence model** (usually some form of decay) uniformly to all information they store. This conflates:

- A raw observation from yesterday ("I'm thinking we should use Dagster")
- A validated fact ("OAuth refresh tokens expire in 30 days")
- A belief synthesised from dozens of observations ("this team ships on Fridays")
- A reasoning chain generated for the current query

These have *different persistence semantics*. A decaying observation is correct; a decaying validated fact is a bug. The paper (arxiv:2604.11364v1) calls this a category error.

## The LeAP move

Split persistence into four layers, each with its own semantics:

| Layer | Semantics | Example |
|---|---|---|
| **Memory** | Gaussian decay — observations fade | "User asked about auth on 2026-04-21 14:32" |
| **Knowledge** | Indefinite supersession — facts until contradicted | "OAuth refresh tokens expire in 30 days" |
| **Wisdom** | Evidence-gated revision — beliefs update on shift | "This team ships on Fridays" |
| **Intelligence** | Ephemeral — temporary inference | "For this query, I considered facts A, B, C" |

The Memory layer consolidates what were previously separate node types (Document, Passage, Utterance, Event, Observation) into a single `Memory` node. The `memory_type` property distinguishes subtypes. Agents write to Memory and Knowledge; SAGE promotes to Wisdom.

## Four distinctions from RAG

LeAP is not RAG-with-extras. It differs structurally:

1. **Multi-layered persistence** — no single decay model; each layer has its own rules
2. **Active adjudication** — the Custodian promotes, supersedes, validates. Retrieval is one verb among many
3. **Usage-shaped** — attention (heat) drives priority for maintenance transitions, not just retrieval
4. **Graph-structured claim-level extraction** — claims (structured triples), not chunks, are the unit of knowledge

## What LeAP is *not*

- Not a replacement for plain RAG in all contexts — when you just want cheap retrieval-augmented prompting, RAG is fine
- Not about bigger embeddings or better retrieval tricks; the architecture is the thesis
- Not AGI-adjacent; it's bookkeeping for agent-authored information, not cognition itself

## When LeAP pays off

LeAP's overhead (Custodian, provenance, multi-layer scoring) is justified when:
- Agents operate over long horizons where facts change
- Multiple agents share a knowledge substrate and disagree
- Audit / compliance / temporal queries matter ("what did we believe on 2026-03-01?")
- Information has authorship that needs tracking (who said what, when)

It's overkill for: chat-with-your-PDF, single-agent short-horizon tasks, purely factual FAQ retrieval.
