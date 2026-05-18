# Engrammic Primitives

EAG schema primitives for building epistemic context systems.

## Install

```bash
pip install engrammic-primitives
```

## Usage

```python
from primitives.schema import MemoryNode, KnowledgeNode, WisdomNode
from primitives.eag import CognitiveTier

# Create a memory node
node = MemoryNode(
    content="User prefers dark mode",
    importance=0.7,
)

# Check cognitive tier
tier = CognitiveTier.MEMORY
```

## When to Use

Building your own EAG-compatible system or extending Engrammic.

For using Engrammic directly, see:
- [engrammic-mcp](https://github.com/engrammic-ai/mcp) - hosted service
- [engrammic-engine](https://github.com/engrammic-ai/engine) - local engine

## Learn More

- [EAG Manifesto](docs/manifesto.md) - the paradigm explained

## Modules

| Module | Purpose |
|--------|---------|
| `primitives.schema` | Node and edge type definitions |
| `primitives.eag` | EAG-specific implementations |
| `primitives.protocols` | Storage and lifecycle interfaces |
| `primitives.scoring` | Decay and freshness formulas |

## License

Apache 2.0
