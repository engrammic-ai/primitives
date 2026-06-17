# 05 — MCP Contract

> The agent-facing interface to the EAG architecture.

## Design Philosophy

The MCP surface uses **intent-based tools** that map to what agents want to do, not implementation layers. Two profiles serve different use cases:

The surface exposes 17 tools covering the full cognitive stack: observation, claims, decisions, search, provenance, and reasoning.

This follows the "fewer well-designed tools" principle: agents learn tools named for their intent.

## Silo Tenancy

**`silo_id` is auto-derived from auth.** Agents never pass it explicitly.

The service derives `silo_id` deterministically from `org_id` in the auth context. This eliminates the friction of discovering and threading silo IDs through every call.

## Tool Surface

### Core Tools

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

#### decide

Declare a commitment or decision.

```
decide(
  conclusion: str,           # What you decided
  about: list[str],          # REQUIRED: node IDs this concerns
  confidence: float = 0.8,
  supersedes: str | None,    # Previous node to supersede
) -> {node_id, created_at}
```

#### accept

Accept a ProposedBelief from SAGE synthesis. The system synthesizes beliefs from corroborated facts; agents must explicitly accept or dismiss them.

```
accept(
  node_id: str,              # ProposedBelief to accept
) -> {node_id, status: "accepted"}
```

#### dismiss

Dismiss an engagement marker or reject a ProposedBelief.

```
dismiss(
  node_id: str,              # Marker or ProposedBelief to dismiss
  reason: str | None,        # Why dismissing
) -> {status: "dismissed"}
```

#### history

View how a node evolved over time via supersession chain.

```
history(
  node_id: str,              # Node to get history for
) -> {chain: [{node_id, content, created_at, superseded_by}, ...]}
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

Form a tentative belief. **Session-scoped:** hypotheses only exist within the MCP session that created them. Must call `commit` within the same session to persist as permanent wisdom. For cross-session conclusions, use `decide` directly.

```
hypothesize(
  hypothesis: str,           # Tentative belief
  about: list[str],          # REQUIRED: nodes this concerns
  confidence: float = 0.8,
  session_id: str | None,    # Auto-derived from MCP connection
) -> {belief_id, session_id, potential_conflicts, created_at}
```

#### revise

Update a tentative belief. Only works within the session that created the hypothesis.

```
revise(
  belief_id: str,            # Hypothesis to update
  confidence: float,         # New confidence
  content: str | None,       # New content (optional)
  reason: str,               # REQUIRED: why revising
) -> {updated_at}
```

#### commit

Crystallize hypotheses to permanent commitments. **Must be called in the same session as `hypothesize`.** Hypotheses that are not committed before the session ends are garbage collected.

```
commit(
  belief_ids: list[str],     # Hypotheses to commit
  reason: str | None,
) -> {committed: [...], superseded: [...]}
```

### Utility Tools (both profiles)

#### forget

Request deletion of a node.

```
forget(
  node_id: str,              # Node to delete
  reason: str | None,        # Why deleting
) -> {status, cancel_window_ends}
```

The node enters a cancel window before permanent deletion.

#### dismiss

Dismiss a contradiction or stale-commitment marker.

```
dismiss(
  marker_id: str,            # Marker to dismiss
  reason: str | None,        # Why dismissing (false positive, acknowledged, etc.)
) -> {dismissed_at}
```

Use for false positives or acknowledged issues that don't require resolution.

#### tick

Lightweight engagement check.

```
tick(
  about_hint: list[str] | None,  # Optional: scope to specific nodes
) -> {pending_markers: [...], stale_commitments: [...]}
```

Returns pending markers without a full recall. Safe to call frequently; zero side effects.

## Configuration

Tools are configured via YAML at `src/context_service/config/mcp_tools.yaml`.

## Evidence Requirements

**Principle:** Knowledge-layer writes require grounded evidence. Agents cannot hallucinate sources.

| Tool | Evidence required? | Grounding mechanism |
|------|-------------------|---------------------|
| remember | No | Memories ARE grounding |
| learn | Yes | `DERIVED_FROM` edge to Memory node or validated URI |
| decide | No | Derives from Knowledge via synthesis |
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
| `decide` | Wisdom | T7 (commit) |
| `reflect` | Meta | (none — meta-observations don't transition) |
| `reason` | Intelligence | T5 (consensus), T6 (trace) |
| `trace` | (read) | T6 (trace) |

The Custodian handles transitions; agents express intent through MCP tools.

## Evidence Pipeline (Service Layer)

The service layer implements evidence validation:

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
