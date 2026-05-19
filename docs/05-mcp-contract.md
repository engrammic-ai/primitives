# 05 — MCP Contract

> The agent-facing interface to the EAG architecture.

## Design Philosophy

The MCP surface uses **intent-based tools** that map to what agents want to do, not implementation layers. Two profiles serve different use cases:

| Profile | Tools | Use case |
|---------|-------|----------|
| **standard** | 7 | Most agents. Observe, claim, believe, search, trace, connect. |
| **reasoning** | 12 | Extended reasoning with tentative belief management. |

This follows the "fewer well-designed tools" principle: agents learn tools named for their intent, with profiles providing the right subset for the context.

## Silo Tenancy

**`silo_id` is auto-derived from auth.** Agents never pass it explicitly.

The service derives `silo_id` deterministically from `org_id` in the auth context. This eliminates the friction of discovering and threading silo IDs through every call.

## Tool Surface

### Standard Profile (7 tools)

#### remember

Store an observation to memory.

```
remember(
  content: str,              # What to remember
  tags: list[str] | None,    # Optional categorization
  decay: str = "standard",   # ephemeral|standard|durable|permanent
) -> {node_id, created_at}
```

**Decay classes:** `ephemeral` (7d), `standard` (90d), `durable` (540d), `permanent` (5y)

#### learn

Assert a claim with evidence.

```
learn(
  claim: str,                # What you learned
  evidence: list[str],       # REQUIRED: node:<id> or URI
  source: str,               # document|user|external|agent
  confidence: float = 0.8,   # 0.0-1.0
  tags: list[str] | None,
) -> {node_id, evidence_status, created_at}
```

#### believe

Declare a commitment.

```
believe(
  belief: str,               # What you believe
  about: list[str],          # REQUIRED: node IDs this concerns
  confidence: float = 0.8,
  reasoning: str | None,     # Why you believe this
) -> {node_id, created_at}
```

#### recall

Search or fetch knowledge.

```
recall(
  query: str | None,         # Natural language search
  node_ids: list[str] | None,# Specific nodes to fetch
  depth: int = 0,            # 0=flat, 1-3=graph traversal
  layers: list[str] | None,  # memory|knowledge|wisdom|intelligence
  top_k: int = 10,
  include_hypotheses: bool = False,  # Include tentative beliefs
) -> {results|nodes, hypotheses?, ...}
```

#### trace

Explain provenance of a belief.

```
trace(
  node_id: str,              # Node to trace
) -> {chain: [...], root_sources: [...]}
```

#### link

Create a typed relationship.

```
link(
  from_node: str,            # Source node
  to_node: str,              # Target node
  relationship: str,         # supports|contradicts|derives|references|causes|supersedes
  weight: float = 1.0,       # 0.0-10.0
  note: str | None,
) -> {edge_id, created_at}
```

#### patterns

Discover workflow templates.

```
patterns(
  action: str,               # list|get|search
  name: str | None,          # Pattern name (for get)
  query: str | None,         # Search query
  profile: str | None,       # Filter by profile
) -> {patterns: [...]}
```

### Reasoning Profile (adds 5 tools)

#### reason

Record a reasoning chain.

```
reason(
  steps: list[{step, reasoning, confidence?}],
  conclusion: str | None,
  evidence_used: list[str] | None,
) -> {chain_id, session_id, created_at}
```

#### reflect

Note a meta-observation.

```
reflect(
  observation: str,          # What you noticed
  type: str,                 # pattern|contradiction|uncertainty|drift
  about: list[str],          # REQUIRED: nodes this concerns
  confidence: float = 0.8,
) -> {node_id, created_at}
```

#### hypothesize

Form a tentative belief.

```
hypothesize(
  hypothesis: str,           # Tentative belief
  about: list[str],          # REQUIRED: nodes this concerns
  confidence: float = 0.8,
  session_id: str | None,    # Auto-derived from MCP connection
) -> {belief_id, session_id, potential_conflicts, created_at}
```

#### revise

Update a tentative belief.

```
revise(
  belief_id: str,            # Hypothesis to update
  confidence: float,         # New confidence
  content: str | None,       # New content (optional)
  reason: str,               # REQUIRED: why revising
) -> {updated_at}
```

#### commit

Crystallize to permanent commitment.

```
commit(
  belief_ids: list[str],     # Hypotheses to commit
  reason: str | None,
) -> {committed: [...], superseded: [...]}
```

## Internal Tools (Not Agent-Facing)

These are NOT exposed to agents. Used by SAGE and internal systems:

| Tool | Internal Use |
|------|--------------|
| `context_admin` | Silo management, session lifecycle |
| `context_accept_belief` | Custodian accepting ProposedBeliefs |
| `context_reject_belief` | Custodian rejecting ProposedBeliefs |
| `context_belief_state` | Internal session inspection |

## Configuration

Tools are configured via YAML at `src/context_service/config/mcp_tools.yaml`. Profile selection:

```python
# Priority: param > env > settings > default
profile = (
    param
    or os.environ.get("MCP_TOOL_PROFILE")
    or settings.mcp_tool_profile
    or "standard"
)
```

## Evidence Requirements

**Principle:** Knowledge-layer writes require grounded evidence. Agents cannot hallucinate sources.

| Tool | Evidence required? | Grounding mechanism |
|------|-------------------|---------------------|
| remember | No | Memories ARE grounding |
| learn | Yes | `DERIVED_FROM` edge to Memory node or validated URI |
| believe | No | Derives from Knowledge via synthesis |
| reason | No | Session-scoped, ephemeral |
| reflect | No | References existing nodes via `about` |

### Evidence Formats

```
node:<uuid>     — Reference to existing Memory-layer node
https://...     — External URI (validated via evidence pipeline)
file://...      — Local file URI (for ingested sources)
```

## Agent Attribution

- **`agent_id`** — Auto-captured from auth context (defaults to `user:{user_id}`)
- **`session_id`** — Auto-derived from auth token or provided via header
- **`DECLARED_BY`** — Commitments and reflections link to declaring agent

## Concurrency Model

Race conditions are resolved through:

1. **Deterministic IDs** — Content-based hashing (no timestamps in IDs)
2. **MERGE semantics** — Idempotent writes
3. **Agent-scoped nodes** — Commitments/reflections are per-agent, no conflict
4. **Custodian reconciliation** — Conflicting claims coexist until T2 supersession

## Relationship to Transitions

| Tool | Primary layer | Related transitions |
|------|---------------|---------------------|
| `remember` | Memory | T8 (decay), T9 (hard-delete) |
| `learn` | Knowledge | T1 (extract from), T2 (supersede), T5 (promote to) |
| `believe` | Wisdom | T7 (commit) |
| `reflect` | Meta | (none — meta-observations don't transition) |
| `reason` | Intelligence | T5 (consensus), T6 (trace) |
| `trace` | (read) | T6 (trace) |

The Custodian handles transitions; agents express intent through MCP tools.

## Evidence Pipeline (Service Layer)

The context-service implements evidence validation:

```
URI -> Cache -> Allowlist -> Reachability -> [Fetch] -> [Ingest] -> Result
```

Configurable per-silo via `EvidencePolicy`:
- `allowlist` — Trusted domains (skip fetch)
- `auto_ingest` — Create Memory nodes from fetched content
- `require_reachable` — Reject if HEAD fails
- `cache_ttl` — Validation cache duration

## Invariants

I1. Every `:Claim` in Knowledge has at least one `DERIVED_FROM` edge to Memory or validated URI.

I2. Every `:Commitment` has exactly one `DECLARED_BY` edge to the authoring agent.

I3. Evidence node refs must resolve to existing nodes; dangling refs are rejected.

I4. `as_of` queries respect bi-temporal fields (`valid_from`, `valid_to`, `created_at`).

I5. Deterministic IDs ensure concurrent writes to same content converge to same node.

I6. `silo_id` is derived from auth; explicit silo params are rejected to prevent cross-tenant access.
