# 05 — MCP Contract

> The agent-facing interface to the EAG architecture.

## Design Philosophy

The MCP surface uses **intent-based tools** that map to what agents want to do, not implementation layers.

The surface exposes 14 tools covering the full agent workflow: observation, claims, search, provenance, deletion, engagement, updates, reasoning, agent coordination, metacognition, and conflict management.

This follows the "fewer well-designed tools" principle: agents learn tools named for their intent.

## Silo Tenancy

**`silo_id` is auto-derived from auth.** Agents never pass it explicitly.

The service derives `silo_id` deterministically from `org_id` in the auth context. This eliminates the friction of discovering and threading silo IDs through every call.

## Tool Surface

#### remember

Store an observation to memory. Writes a Memory node. Returns immediately; node becomes searchable within ~500ms (async embedding). No evidence required.

```
remember(
  content: str,              # What to remember
  tags: list[str] | None,    # Optional categorization
  decay: str = "standard",   # ephemeral|standard|durable|permanent
  supersedes: str | None,    # Previous node to supersede
  memory_type: str | None,   # "reflection" for metacognitive observations
  about: list[str] | None,   # Node IDs this reflection references (memory_type="reflection" only)
) -> {node_id, created_at}
```

**Decay classes:** `ephemeral` (7d), `standard` (90d), `durable` (540d), `permanent` (5y)

**Reflections:** Pass `memory_type="reflection"` and `about=[node_ids]` to store a metacognitive observation about other nodes. Reflections do not decay and create `ABOUT` edges to the referenced nodes.

Consider `recall` first — if updating existing knowledge, pass `supersedes:<node_id>`.

#### learn

Record a claim with evidence. Writes a Claim node. Returns immediately; node becomes searchable within ~500ms (async embedding).

```
learn(
  claim: str,                # What you learned
  evidence: list[str],       # REQUIRED: node:<id> or URI
  source: str,               # document|user|external|agent
  confidence: float = 0.8,   # 0.0-1.0
  tags: list[str] | None,
  supersedes: str | None,    # Previous node to supersede
  source_tier: str | None,   # authoritative|validated|inferred
) -> {node_id, evidence_status, created_at}
```

Recall first to check for existing claims — pass `supersedes:<node_id>` to update rather than duplicate.

#### recall

Search or fetch knowledge. Call this at the start of any task and before storing anything.

```
recall(
  query: str | None,                  # Natural language search (or "*" to list all)
  node_ids: list[str] | None,         # Specific nodes to fetch
  depth: int = 0,                     # 0=flat, 1-3=graph traversal
  layers: list[str] | None,           # memory|knowledge|wisdom|intelligence
  top_k: int = 10,
  include_withheld: bool = False,     # Include low-confidence/unresolved-contradiction nodes
  min_threshold: float | None,        # Override relevance cutoff (0.0-1.0)
  fusion_mode: bool = False,          # Parallel semantic + graph retrieval with RRF fusion
  since: str | None,                  # Temporal filter (fusion_mode only): "7d", "1w", ISO datetime
  until: str | None,                  # Temporal filter (fusion_mode only): "30d", ISO datetime
  graph_depth: int | None,            # BFS depth for graph channel (fusion_mode only, default 2)
  include_hints: bool = False,        # Receive belief candidate suggestions
  tags: list[str] | None,             # Filter to nodes having ALL specified tags
  as_of: str | None,                  # Time-travel: ISO datetime to query historical state
  include_content: bool | None = True,# True=full content, False=summaries, None=tier policy
  include_inactive: bool = False,     # Include superseded and tombstoned nodes
  include_conflicts: bool = False,    # Also return CONTRADICTS-linked nodes in conflict_nodes field
  agent_id: str | None,               # Filter to nodes created by this agent
  exclude_agents: list[str] | None,   # Exclude nodes from these agent IDs
  bypass_cache: bool = False,         # Skip result cache and force fresh search
  max_age_seconds: int | None,        # Max acceptable cache age (seconds) before refresh
) -> {results|nodes, withheld_count?, fusion_meta?, hints?, conflict_nodes?}
```

**Fusion mode:** Set `fusion_mode=true` to run semantic and graph retrieval in parallel, fusing results with Reciprocal Rank Fusion (RRF). Returns `fusion_meta` with `rrf_score` per node. Temporal filtering (`since`, `until`, `graph_depth`) requires `fusion_mode=true`.

**Time-travel:** Pass `as_of="2024-06-01T12:00:00Z"` to query epistemic state at a historical point. Returns nodes valid at that time, excluding nodes created after or superseded before the timestamp.

Low-confidence and unresolved-contradiction nodes are withheld by default and reported as a count; pass `include_withheld=true` to see them.

#### trace

Trace provenance or impact of a node.

```
trace(
  node_id: str,                   # Node to trace
  direction: str = "up",          # up=walk to sources, down=walk to derived nodes
  max_depth: int = 5,
  edge_types: list[str] | None,   # DERIVED_FROM|PROMOTED_FROM|SYNTHESIZED_FROM|REFERENCES
) -> {chain: [...], root_sources: [...]}
```

`direction="up"` (default) walks backward to sources (why I believe this). `direction="down"` walks forward to derived nodes (what depends on this).

#### forget

Request deletion of a node.

```
forget(
  node_id: str,              # Node to delete
  reason: str | None,        # Why deleting
  cascade: bool = False,     # Also tombstone downstream nodes that reference this one
) -> {status, cancel_window_ends}
```

The node is tombstoned and enters a cancel window before permanent deletion. Use for GDPR erasure or removing incorrect data.

#### tick

Lightweight engagement check.

```
tick(
  about_hint: list[str] | None,  # Optional: scope to specific node IDs
) -> {pending_markers: [...], stale_commitments: [...]}
```

Returns pending markers without a full recall. Safe to call frequently; zero side effects.

#### update

Update existing knowledge by superseding it with new content.

```
update(
  content: str,              # The new claim text
  evidence: list[str],       # URIs or node refs
  target: str | None,        # Explicit node_id (skips search)
  query: str | None,         # Semantic search to find the node to replace
) -> {node_id, created_at} | {status: "ambiguous", candidates: [...]} | {status: "not_found"}
```

If `query` matches exactly one node above the similarity threshold (0.7), it is auto-superseded. If multiple matches are found, returns `{status: "ambiguous", candidates: [...]}` for the caller to resolve. Use `learn()` to create new knowledge without supersession.

#### reason

Create an ephemeral reasoning chain for multi-step inference. Writes to the Intelligence layer.

```
reason(
  steps: list[{step: int, reasoning: str, confidence: float}],  # REQUIRED
  conclusion: str | None,            # Optional summary of the chain's conclusion
  evidence_used: list[str] | None,   # Node IDs that informed this reasoning
  crystallizations: list[dict] | None, # Beliefs to commit from the reasoning
  session_id: str | None,            # Defaults to auth-derived session
  parent_chain_id: str | None,       # Continue a previous chain
) -> {chain_id, session_id, created_at}
```

Chains are session-scoped by default. Pass `parent_chain_id` to append to an existing chain. Use `crystallizations` to promote a conclusion into a durable Belief node.

#### agents

List agents registered in the silo.

```
agents(
  silo_id: str | None,    # Defaults to org's primary silo
) -> {agents: [{agent_id, role, first_seen, last_seen, node_count, trust_score}], count}
```

Useful for multi-agent coordination and auditing which agents have contributed to the knowledge base.

#### introspect

Query metacognitive state of the knowledge graph.

```
introspect(
  query_type: str,         # volatility|gaps|provenance|contributions
  node_id: str | None,     # Required for provenance query
  agent_id: str | None,    # For contributions query (defaults to self)
  min_threshold: int | None, # Min chain length (volatility) or ask count (gaps)
  limit: int = 10,
) -> {results: [...]}
```

**`query_type` options:**
- `volatility` — Topics with high supersession churn (unstable knowledge)
- `gaps` — Frequently-asked queries that returned no results (known unknowns)
- `provenance` — Which agents contributed to a belief (requires `node_id`)
- `contributions` — Contribution stats for an agent (defaults to self)

#### conflicts

List contradictions between nodes.

```
conflicts(
  agent_id: str | None,   # Filter to conflicts involving a specific agent
  status: str = "unresolved",  # Resolution status filter
  limit: int = 50,
) -> {conflicts: [{conflict_id, node_a, node_b, agent_a, agent_b, ...}], count}
```

Returns `CONTRADICTS` edges with both node contents and agent attributions.

#### dismiss_conflict

Mark a conflict as not-a-real-conflict.

```
dismiss_conflict(
  conflict_id: str,        # ID of the CONTRADICTS edge
  reason: str | None,      # Explanation stored for audit trail
) -> {conflict_id, status: "dismissed"}
```

Use when nodes don't actually contradict — different contexts, complementary facts, etc.

#### escalate_conflict

Flag a conflict for human review.

```
escalate_conflict(
  conflict_id: str,        # ID of the CONTRADICTS edge
  message: str | None,     # Context for the human reviewer
) -> {conflict_id, status: "escalated"}
```

Use when the agent cannot determine which node is correct or domain expertise is needed.

#### resolve_conflict

Pick a winner for a conflict.

```
resolve_conflict(
  conflict_id: str,        # ID of the CONTRADICTS edge
  winner_id: str,          # Node ID of the authoritative node
  supersede: bool = True,  # If True, loser is marked superseded by winner
) -> {conflict_id, status, winner_id}
```

With `supersede=true` (default), creates a `SUPERSEDES` edge from winner to loser. With `supersede=false`, marks resolved without creating a supersession chain.

## Configuration

Tools are configured via YAML at `src/context_service/config/mcp_tools.yaml`. Names and descriptions are config, not code.

## Evidence Requirements

**Principle:** Knowledge-layer writes require grounded evidence. Agents cannot hallucinate sources.

| Tool | Evidence required? | Grounding mechanism |
|------|-------------------|---------------------|
| remember | No | Memories ARE grounding |
| learn | Yes | `DERIVED_FROM` edge to Memory node or validated URI |
| update | Yes | `DERIVED_FROM` edge to Memory node or validated URI |

### Evidence Formats

```
node:<uuid>     — Reference to existing Memory-layer node
https://...     — External URI (validated via evidence pipeline)
file://...      — Local file URI (for ingested sources)
```

## Supersession Pattern

Before storing, recall to check if you are updating existing knowledge. If found, pass `supersedes:<node_id>` to chain the update:

```
1. recall("API authentication method")
2. Found node abc123: "The API uses OAuth2"
3. learn("The API uses OAuth2 with PKCE", evidence=[...], supersedes="abc123")
```

This creates a version chain — the old node stays for history, the new node becomes current. Use `trace(node_id)` to walk the full provenance chain.

## Agent Attribution

- **`agent_id`** — Auto-captured from auth context (defaults to `user:{user_id}`)
- **`session_id`** — Auto-derived from auth token or provided via header

## Concurrency Model

Race conditions are resolved through:

1. **Deterministic IDs** — Content-based hashing (no timestamps in IDs)
2. **MERGE semantics** — Idempotent writes
3. **Custodian reconciliation** — Conflicting claims coexist until supersession

## Wisdom Nodes

Belief and Commitment nodes are system-synthesized or agent-declared via SAGE. Agents do not write them directly via tool arguments.

| System path | Trigger |
|-------------|---------|
| Custodian: Claim -> Fact | Corroborated by 3+ sources |
| Synthesizer: Facts -> Belief | Cluster density >= 3 facts |

## Relationship to Transitions

| Tool | Primary layer | Related transitions |
|------|---------------|---------------------|
| `remember` | Memory | T8 (decay), T9 (hard-delete) |
| `learn` | Knowledge | T1 (extract from), T2 (supersede), T5 (promote to) |
| `update` | Knowledge | T2 (supersede) |
| `trace` | (read) | T6 (trace) |
| `reason` | Intelligence | session-scoped chain |
| `agents` | (read) | — |
| `introspect` | (read) | — |
| `conflicts` | (read) | — |
| `dismiss_conflict` | (write) | marks not-a-real-conflict |
| `escalate_conflict` | (write) | flags for human review |
| `resolve_conflict` | (write) | T2 (supersede loser) |

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

I2. Evidence node refs must resolve to existing nodes; dangling refs are rejected.

I3. `as_of` queries respect bi-temporal fields (`valid_from`, `valid_to`, `created_at`).

I4. Deterministic IDs ensure concurrent writes to same content converge to same node.

I5. `silo_id` is derived from auth; explicit silo params are rejected to prevent cross-tenant access.
