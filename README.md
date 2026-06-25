# Engrammic Primitives

The schema library for Engrammic, a structured memory system for AI agents.

Most AI agents treat context like a scratchpad. Engrammic treats it like cognition: observations become claims, claims become facts, facts become beliefs. This library defines the types and rules that make that work.

> **Library for integrators.** If you just want to use Engrammic memory in your agent, see [engrammic-mcp](https://github.com/engrammic-ai/mcp) for the hosted service or [engrammic](https://github.com/engrammic-ai/engrammic) to self-host.

## Install

```bash
pip install engrammic-primitives
```

## What's Inside

**Schema types** for four cognitive layers:

| Layer | What it holds | Example |
|-------|---------------|---------|
| Memory | Raw observations | "User mentioned they prefer dark mode" |
| Knowledge | Claims with evidence | "User prefers dark mode" (based on 3 mentions) |
| Wisdom | Synthesized beliefs | "Optimize for low-light viewing in this user's sessions" |
| Intelligence | Reasoning chains | Step-by-step derivation of a conclusion |

**Scoring functions** for promotion decisions:

```python
from primitives.eag import combined_confidence, should_promote_r1

# When should a claim become a fact?
decision = should_promote_r1(confidence=0.8, corroboration_count=3)
```

**Transition predicates** for enforcing layer rules (e.g., Knowledge requires evidence).

**Protocols** for storage backends (implement these to build your own store).

## When to Use This

You're building something that stores and retrieves structured agent context, and you want compatibility with the Engrammic ecosystem.

If you just want to use Engrammic:
- [engrammic-mcp](https://github.com/engrammic-ai/mcp) for the hosted service
- [engrammic](https://github.com/engrammic-ai/engrammic) to self-host

## Modules

| Module | Purpose |
|--------|---------|
| `primitives.schema` | Node and edge type definitions |
| `primitives.eag` | Confidence, promotion, decay logic |
| `primitives.eag.transitions` | Layer transition predicates and constraints |
| `primitives.protocols` | Storage and lifecycle interfaces |
| `primitives.scoring` | Freshness and relevance formulas |

## Learn More

- [LeAP Paradigm](docs/README.md) for the full cognitive architecture spec

## License

Apache 2.0
