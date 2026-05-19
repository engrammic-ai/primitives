# Engrammic Primitives

EAG schema primitives for building epistemic context systems.

## Install

```bash
pip install engrammic-primitives
```

## Usage

```python
from primitives.schema import PersistenceLayer, MemoryLabel, KnowledgeLabel
from primitives.eag import combined_confidence, should_promote_r1

# Check persistence layer for a label
layer = PersistenceLayer.MEMORY
assert MemoryLabel.UTTERANCE.layer == layer

# Combine confidence scores
conf = combined_confidence(base=0.7, corroboration=0.85)

# Check if a claim should promote to Fact
decision = should_promote_r1(confidence=0.8, corroboration_count=3)
```

## When to Use

Building your own EAG-compatible system or extending Engrammic.

For using Engrammic directly, see:
- [engrammic-mcp](https://github.com/engrammic-ai/mcp) - hosted service
- [engrammic-engine](https://github.com/engrammic-ai/engine) - local engine

## Learn More

- [EAG Paradigm](docs/README.md) - the four-layer cognitive architecture

## Modules

| Module | Purpose |
|--------|---------|
| `primitives.schema` | Node and edge type definitions |
| `primitives.eag` | EAG-specific implementations |
| `primitives.protocols` | Storage and lifecycle interfaces |
| `primitives.scoring` | Decay and freshness formulas |

## License

Apache 2.0
