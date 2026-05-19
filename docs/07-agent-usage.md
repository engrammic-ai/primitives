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

Form a belief when:
1. You've seen the same pattern multiple times
2. You've reasoned from facts to a conclusion
3. You need to take a position

**The belief test:** "Based on [these facts], I believe [this conclusion]." If you can't fill in [these facts], you don't have a belief - you have a hunch. Store hunches to Memory.

### Commitment vs Belief

- **Belief:** "Based on benchmarks, X is faster" (grounded in facts)
- **Commitment:** "We will use X for all new work" (declared position)

Both live in Wisdom. Beliefs need evidence. Commitments need declaration.

---

## Layer Quick Reference

| Layer | Store when | Evidence? | Persists? |
|-------|-----------|-----------|-----------|
| Memory | Raw observation, context | No | Decays (7d-5y) |
| Knowledge | Verifiable claim | Required | Until superseded |
| Wisdom | Synthesized belief/pattern | Links to facts | Indefinite |
| Intelligence | Reasoning steps | No | Session only |
| Meta-Memory | Understanding changed | Links to nodes | Never decays |

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

## Belief Formation Flow

```
1. OBSERVE   → Store to Memory (decays)
2. CLAIM     → Store to Knowledge with evidence
3. VERIFY    → System promotes Claim → Fact when corroborated (3+ sources)
4. SYNTHESIZE → Form Belief linking multiple Facts
5. COMMIT    → Optionally declare Commitment
6. REVISE    → When new evidence, supersede (don't delete)
7. REFLECT   → Record changes to Meta-Memory
```

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

## Key Relationship Types

### Provenance
- `DERIVED_FROM` - this came from that source
- `EXTRACTED_FROM` - extracted from document
- `SUPERSEDES` - this replaces that (newer understanding)
- `PROMOTED_FROM` - claim promoted to fact

### Semantic
- `SUPPORTS` - evidence supports claim
- `CONTRADICTS` - conflicts with
- `CORROBORATES` - same claim from different source
- `CAUSES` / `PREVENTS` - causal relationships

---

## When to Reflect (Meta-Memory)

Record to Meta when:
- You update a belief based on new evidence
- You notice a contradiction
- You correct a mistake
- Your confidence shifts significantly

The history of belief is as valuable as current belief.

---

## Anti-patterns

1. **Storing to Knowledge without evidence** - always provide sources
2. **Storing to Wisdom without linking to facts** - always use `about` param
3. **Expecting Intelligence layer across sessions** - it's ephemeral
4. **Deleting instead of superseding** - old beliefs chain, not delete
5. **Not using Meta for belief changes** - lose audit trail

---

## Decision Tree

```
Is this worth storing?
├── No → Skip
└── Yes → What kind?
    ├── Raw observation/context → Memory (pick decay class)
    ├── Verifiable claim with source → Knowledge (include evidence)
    ├── Pattern/belief from multiple facts → Wisdom (link to facts)
    ├── Reasoning I'm doing now → Intelligence (session only)
    └── My understanding changed → Meta (audit trail)
```
