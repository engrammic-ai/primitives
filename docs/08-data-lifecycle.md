# 08 — Data Lifecycle: forget, decay, and erasure

This document specifies how data exits the system. Three distinct mechanisms exist, each serving different needs.

## The three deletion paths

| Path | Trigger | Reversible | Timing | Use case |
|------|---------|------------|--------|----------|
| **Decay (T8)** | Retrieval weight -> 0 | Soft (node exists, invisible) | Compute-at-query | Stale memories fade naturally |
| **Forget (T14)** | Agent calls `forget` | Yes, within cancel window | Immediate tombstone | Agent corrects a mistake |
| **Hard-delete (T9)** | Age threshold OR GDPR | No | Scheduled GC | Storage hygiene, legal compliance |

## Forget (T14)

Agent-initiated immediate soft-delete with a recovery window.

### Semantics

```
forget(node_id, reason?, cascade?)
  -> tombstone the node
  -> return downstream_references count
  -> if cascade: recursively forget downstream nodes
```

### Properties set on tombstone

| Property | Value | Purpose |
|----------|-------|---------|
| `tombstoned_at` | microsecond timestamp | Query-time filtering |
| `forget_requested_at` | microsecond timestamp | Cancel window calculation |
| `forget_reason` | string (optional) | Audit trail |
| `heat_dirty` | true | Signal recalculation needed |

### Cancel window

Default: 1 hour. Configurable per deployment.

Within the cancel window, `cancel_forget` (T15) reverses the tombstone:
- Clears `tombstoned_at`, `forget_requested_at`
- Node becomes visible again
- Downstream cascade is NOT automatically reversed (each must be cancelled individually)

After the cancel window expires:
- `cancel_forget` returns `cancel_window_expired`
- Node remains tombstoned until hard-delete

### Cascade semantics

When `cascade=true`:

1. Tombstone the target node
2. Find all nodes with edges pointing TO the target (downstream references)
3. Recursively forget each downstream node (depth-first)

Cascade does NOT follow:
- Outbound edges (nodes the target points to)
- Supersession chains (old versions of the target)

Rationale: if you forget a Fact, you want to forget Claims derived from it, not the source Passages it was extracted from.

### Query-time behavior

Tombstoned nodes are filtered out at query time:
- `recall` excludes `tombstoned_at IS NOT NULL`
- `trace` stops at tombstoned nodes (does not traverse through)
- Graph traversals skip tombstoned nodes

Tombstoned nodes still exist in storage until hard-delete.

## Cancel Forget (T15)

Reverses a forget within the cancel window.

```
cancel_forget(node_id)
  -> if within window: restore node
  -> if window expired: return error
```

### Atomicity

Cancel is per-node. If a cascade forget tombstoned 5 nodes, cancelling requires 5 separate `cancel_forget` calls. This is intentional: partial recovery is valid (keep some deletions, reverse others).

## Hard-delete (T9)

Permanent removal from all storage layers.

### Trigger conditions

1. **Age threshold**: `age > 2 * class.sigma` (class-specific retention)
2. **GDPR erasure request**: External legal trigger
3. **Tombstone age**: Tombstoned nodes older than retention period

### Execution

Hard-delete is a scheduled GC job (Custodian Groundskeeper), not an agent tool.

Steps:
1. Identify candidates (tombstoned OR age-exceeded)
2. Delete from vector store (Qdrant)
3. Delete from graph store (Memgraph)
4. Log deletion event (audit)

### No recovery

Hard-deleted nodes cannot be recovered. The cancel window exists specifically to prevent accidental permanent loss.

## GDPR erasure flow

Right-to-erasure requests follow a specific path:

```
GDPR request received
  -> identify all nodes owned by data subject
  -> tombstone all (T14, no cancel window for GDPR)
  -> schedule immediate hard-delete (T9)
  -> generate erasure certificate
```

GDPR erasure bypasses the cancel window. Once requested, deletion is immediate and permanent.

### Scope of erasure

GDPR erasure applies to:
- All Memory nodes from the data subject
- All Knowledge nodes derived solely from that subject's data
- Wisdom nodes are evaluated case-by-case (may have multiple sources)

Erasure does NOT delete:
- Aggregate statistics (no PII)
- Nodes with multiple independent sources (breaks derivation link only)

## Interaction with other transitions

### Forget + Supersession

If node A supersedes node B, and B is forgotten:
- A remains visible (supersession is forward-looking)
- A's `SUPERSEDES` edge points to a tombstoned node
- Provenance traversal stops at B

### Forget + Synthesis

If Facts F1, F2, F3 were synthesized into Belief B:
- Forgetting F1 does NOT auto-forget B (B has other sources)
- Forgetting F1, F2, F3 (all sources) triggers B staleness check
- Custodian may propose B revision or retirement

### Decay + Forget

Decay (T8) and forget (T14) are independent:
- A decayed node (weight=0) can still be forgotten
- A forgotten node's decay state is irrelevant (tombstone takes precedence)

## Implementation notes

### Tombstone filtering

All read queries MUST include:
```cypher
WHERE n.tombstoned_at IS NULL
```

This is enforced at the query layer, not application logic.

### Cache invalidation

On forget:
1. Delete node from result cache
2. Mark related nodes as `heat_dirty`
3. Invalidate any cached graph traversals including the node

### Telemetry

Track:
- `forget_requests_total` (counter)
- `forget_cancelled_total` (counter)
- `hard_delete_total` (counter, by trigger reason)
- `cancel_window_expired_total` (counter)
