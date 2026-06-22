# EAG Agent Usage Guide

Practical instructions for agents interacting with EAG-based memory systems.

## The Cognitive Model

### The Memory Question: "Should I remember this?"

Before storing, ask:
1. **Will this matter later?** If only relevant now, skip.
2. **Is this new?** Don't duplicate existing knowledge.
3. **Who needs this?** Just you = ephemeral. Team = durable.
4. **How long true?** Choose decay class accordingly.

**Heuristic:** If you wouldn't tell a colleague about it tomorrow, don't store it.

### The Knowledge Question: "Is this a fact?"

Before storing to Knowledge:
1. **Do I have evidence?** No evidence = use Memory instead.
2. **Is this verifiable?** Opinions are not facts.
3. **Could this be wrong?** Use lower confidence.

**Heuristic:** If you'd need to cite a source to defend this claim, it belongs in Knowledge with that source as evidence.

### The Wisdom Question: "What do I believe?"

Wisdom nodes (Belief) are system-synthesized by SAGE — agents do not write them directly. The Custodian promotes corroborated Claims to Facts; the Synthesizer clusters Facts into Beliefs. Agents contribute by writing high-quality Claims with evidence.

**The belief test:** "Based on [these facts], I believe [this conclusion]." If you can't fill in [these facts], you have a hunch. Store hunches to Memory.

---

## Layer Quick Reference

| Layer | Store when | Evidence? | Persists? |
|-------|-----------|-----------|-----------|
| Memory | Raw observation, context | No | Decays (7d-5y) |
| Knowledge | Verifiable claim | Required | Until superseded |
| Wisdom | Synthesized belief (system only) | Links to facts | Indefinite |
| Intelligence | Reasoning steps (system only) | No | Session only |

---

## Decay Classes

| Class | Duration | Use for |
|-------|----------|---------|
| `ephemeral` | 7 days | Scratch work, temp context |
| `standard` | 90 days | Normal observations |
| `durable` | 540 days | Important, referenced repeatedly |
| `permanent` | 5 years | Foundational reference |

Default to `standard` unless you have reason not to.

---

## Knowledge Flow

```
1. OBSERVE   → remember()  → Memory node (decays)
2. CLAIM     → learn()     → Claim node (requires evidence)
3. UPDATE    → update()    → Claim SUPERSEDES old Claim
4. VERIFY    → [custodian] → Fact (promoted from corroborated Claims, 3+ sources)
5. SYNTHESIZE → [synthesizer] → Belief (from 3+ Facts)
```

Steps 4 and 5 are system-automated. Agents write steps 1-3 only.

---

## Confidence Guidelines

| Confidence | Meaning | When to use |
|------------|---------|-------------|
| 0.95+ | Near certain | Multiple reliable sources, verified |
| 0.8-0.95 | Confident | Single reliable source, strong reasoning |
| 0.6-0.8 | Probable | Reasonable inference, some uncertainty |
| 0.4-0.6 | Uncertain | Plausible but unverified |
| <0.4 | Speculative | Weak evidence, tentative hypothesis |

---

## Tool Surface

| Tool | What it writes | When to use |
|------|---------------|-------------|
| `remember` | Memory node | Raw observation, preference, context |
| `learn` | Claim node | Verifiable claim with evidence URI |
| `update` | Claim (supersedes old) | Correcting or refining existing knowledge |
| `recall` | (read) | Search or fetch at task start and before storing |
| `trace` | (read) | Walk provenance: why I believe this, what depends on this |
| `forget` | Tombstone | GDPR erasure, incorrect data removal |
| `tick` | (read) | Lightweight engagement check, pending markers |

---

## Key Relationship Types

### Provenance
- `DERIVED_FROM` - this came from that source (also used for extraction)
- `SUPERSEDES` - this replaces that (newer understanding)
- `PROMOTED_FROM` - claim promoted to fact by Custodian
- `SYNTHESIZED_FROM` - belief synthesized from facts by Synthesizer

### Semantic
- `SUPPORTS` - evidence supports claim
- `CONTRADICTS` - conflicts with
- `CORROBORATES` - same claim from different source
- `ABOUT` - node relates to a subject node

---

## Anti-patterns

1. **Storing to Knowledge without evidence** — always provide source URIs
2. **Expecting Wisdom nodes from agent tools** — Belief and Fact are system-created, not agent-written
3. **Expecting session state to persist** — use `learn` for facts, `remember` for context
4. **Deleting instead of superseding** — old claims chain, not delete; use `update` or `forget` only for erasure
5. **Skipping recall before storing** — duplicates accumulate; always recall first to find supersession candidates

---

## Decision Tree

```
Is this worth storing?
├── No → Skip
└── Yes → What kind?
    ├── Raw observation/context → remember (pick decay class)
    ├── Verifiable claim with source → learn (include evidence URI)
    ├── Updating existing knowledge → update (provide target or query)
    └── Removing incorrect data → forget (cascade=true for downstream nodes)
```
