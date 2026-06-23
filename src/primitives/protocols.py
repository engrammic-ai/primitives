"""Core protocols for hot-swappable knowledge primitives.

These protocols define the interface contract between the product layer
and the primitives library. Implementations can be swapped without
changing product code.

Usage:
    from primitives.protocols import KnowledgeStore, LifecycleManager

    def build_app(store: KnowledgeStore, lifecycle: LifecycleManager):
        # Product code uses protocols, not implementations
        ...
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any, Protocol, runtime_checkable

from primitives.schema.labels_v2 import NodeStatus

# ---------------------------------------------------------------------------
# Common types
# ---------------------------------------------------------------------------


class Layer(StrEnum):
    """Knowledge persistence layers."""

    MEMORY = "memory"  # Experiences that fade
    KNOWLEDGE = "knowledge"  # Facts that persist until contradicted
    WISDOM = "wisdom"  # Beliefs that revise on evidence shift
    INTELLIGENCE = "intelligence"  # Ephemeral reasoning


@dataclass(frozen=True)
class Scope:
    """Query/operation scope."""

    silo_id: str
    org_id: str | None = None
    agent_id: str | None = None
    layer: Layer | None = None


@dataclass
class KnowledgeNode:
    """Generic knowledge node returned by store operations."""

    id: str
    layer: Layer
    silo_id: str
    content: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    created_at: datetime | None = None
    updated_at: datetime | None = None
    status: NodeStatus = NodeStatus.ACTIVE
    # Identity fields for multi-agent coherence
    agent_id: str | None = None
    session_id: str | None = None
    owner_id: str | None = None
    model_id: str | None = None


@dataclass
class IngestResult:
    """Result of an ingest operation."""

    node_id: str
    layer: Layer
    extracted_claims: list[str] = field(default_factory=list)
    success: bool = True
    error: str | None = None


@dataclass
class PromoteResult:
    """Result of a promotion operation."""

    promoted: bool
    source_id: str
    target_id: str | None = None
    rule: str | None = None  # e.g., "R1", "R2"
    reason: str | None = None


@dataclass
class SupersedeResult:
    """Result of a supersession operation."""

    superseded: bool
    old_id: str
    new_id: str
    reason: str | None = None


@dataclass
class DecayResult:
    """Result of a decay operation."""

    decayed_count: int
    deleted_count: int
    scope: Scope


@dataclass
class DeleteResult:
    """Result of a delete operation."""

    deleted: bool
    node_id: str
    cascade_count: int = 0


@dataclass
class ProvenanceEdge:
    """Single edge in a provenance chain."""

    source_id: str
    target_id: str
    edge_type: str  # DERIVED_FROM, CITES, SUPERSEDES, etc.
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProvenanceChain:
    """Full provenance trace for a node."""

    root_id: str
    edges: list[ProvenanceEdge] = field(default_factory=list)
    depth: int = 0


# ---------------------------------------------------------------------------
# Core protocols
# ---------------------------------------------------------------------------


@runtime_checkable
class KnowledgeStore(Protocol):
    """Interface for storing and retrieving knowledge.

    Implementations handle the specifics of graph structure, vector indexing,
    and layer semantics. Product code interacts only through this interface.
    """

    async def ingest(
        self,
        content: str,
        metadata: dict[str, Any],
        scope: Scope,
    ) -> IngestResult:
        """Ingest content into the knowledge store.

        Implementations may extract claims, create passages, compute embeddings,
        etc. The specifics are paradigm-dependent.
        """
        ...

    async def query(
        self,
        q: str,
        scope: Scope,
        limit: int = 10,
    ) -> list[KnowledgeNode]:
        """Semantic query across knowledge.

        Implementations handle hybrid search, layer filtering, heat weighting, etc.
        """
        ...

    async def get(self, node_id: str, scope: Scope) -> KnowledgeNode | None:
        """Retrieve a specific node by ID."""
        ...

    async def get_batch(self, node_ids: list[str], scope: Scope) -> list[KnowledgeNode]:
        """Retrieve multiple nodes by ID."""
        ...

    async def delete(
        self,
        node_id: str,
        scope: Scope,
        cascade: bool = False,
    ) -> DeleteResult:
        """Delete a node, optionally cascading to derived nodes."""
        ...


@runtime_checkable
class LifecycleManager(Protocol):
    """Interface for knowledge lifecycle transitions.

    Handles promotion (Memory -> Knowledge -> Wisdom), supersession,
    and decay. The rules for when transitions fire are paradigm-specific.
    """

    async def promote(self, node_id: str, scope: Scope) -> PromoteResult:
        """Attempt to promote a node to the next layer.

        Returns whether promotion occurred and why/why not.
        """
        ...

    async def supersede(
        self,
        old_id: str,
        new_id: str,
        reason: str,
        scope: Scope,
    ) -> SupersedeResult:
        """Mark old_id as superseded by new_id."""
        ...

    async def decay(self, scope: Scope, threshold: float) -> DecayResult:
        """Apply decay to nodes below the threshold.

        May soft-delete (reduce retrieval weight) or hard-delete depending
        on implementation.
        """
        ...

    def should_promote(self, node: KnowledgeNode) -> tuple[bool, str]:
        """Pure predicate: should this node be promoted?

        Returns (should_promote, reason). Does not mutate.
        """
        ...

    def detect_contradiction(
        self, node_a: KnowledgeNode, node_b: KnowledgeNode
    ) -> tuple[bool, str | None]:
        """Detect if two nodes contradict each other.

        Returns (contradicts, explanation).
        """
        ...


@runtime_checkable
class SignalProvider(Protocol):
    """Interface for knowledge signals.

    Signals inform retrieval ranking, lifecycle transitions, and work
    prioritization. Implementations define the math.
    """

    def confidence(self, node: KnowledgeNode) -> float:
        """Compute confidence score for a node."""
        ...

    def heat(self, node: KnowledgeNode) -> float:
        """Compute heat (usage-based temperature) for a node."""
        ...

    def freshness(self, node: KnowledgeNode) -> float:
        """Compute freshness (time-based decay) for a node."""
        ...

    def priority(self, node: KnowledgeNode) -> float:
        """Compute composite priority for work ordering.

        Typically: heat * (1 - freshness) * (1 - confidence) * age_boost
        """
        ...


@runtime_checkable
class ProvenanceTracker(Protocol):
    """Interface for tracking derivation and citation chains.

    Every knowledge node should be traceable back to its sources.
    """

    async def derive(
        self,
        target_id: str,
        source_ids: list[str],
        scope: Scope,
    ) -> None:
        """Record that target was derived from sources.

        Creates DERIVED_FROM edges.
        """
        ...

    async def cite(
        self,
        target_id: str,
        source_ids: list[str],
        kind: str,
        scope: Scope,
    ) -> None:
        """Record that target cites sources.

        Creates CITES edges with kind (primary, supporting, etc.).
        """
        ...

    async def trace(
        self,
        node_id: str,
        depth: int,
        scope: Scope,
    ) -> ProvenanceChain:
        """Trace provenance chain back from a node."""
        ...


# ---------------------------------------------------------------------------
# Composite protocol for full implementation
# ---------------------------------------------------------------------------


@runtime_checkable
class KnowledgePrimitives(Protocol):
    """Full primitives implementation combining all protocols.

    Implementations provide all four capabilities as a coherent unit.
    """

    @property
    def store(self) -> KnowledgeStore: ...

    @property
    def lifecycle(self) -> LifecycleManager: ...

    @property
    def signals(self) -> SignalProvider: ...

    @property
    def provenance(self) -> ProvenanceTracker: ...
