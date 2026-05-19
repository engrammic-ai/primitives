"""EAG abstract knowledge store base class."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any

from primitives.protocols import (
    DeleteResult,
    IngestResult,
    KnowledgeNode,
    Scope,
)


class EAGKnowledgeStore:
    """Abstract base for EAG-backed storage implementations.

    Subclasses wire in the actual graph/vector backends (Memgraph, Qdrant, etc.)
    while product code interacts only through the KnowledgeStore protocol shape.
    All methods are abstract — no default behavior is assumed because storage
    semantics are entirely backend-dependent.
    """

    @abstractmethod
    async def ingest(
        self,
        content: str,
        metadata: dict[str, Any],
        scope: Scope,
    ) -> IngestResult:
        """Ingest content into the knowledge store.

        Implementations are responsible for claim extraction, embedding
        computation, graph node creation, and layer assignment based on scope.
        """
        ...

    @abstractmethod
    async def query(
        self,
        q: str,
        scope: Scope,
        limit: int = 10,
    ) -> list[KnowledgeNode]:
        """Semantic query across the knowledge store.

        Implementations handle hybrid search (dense + sparse), heat weighting,
        layer filtering, and RRF fusion. Results are ordered by relevance.
        """
        ...

    @abstractmethod
    async def get(self, node_id: str, scope: Scope) -> KnowledgeNode | None:
        """Retrieve a specific node by ID.

        Returns None when the node does not exist or is not accessible within
        the given scope.
        """
        ...

    @abstractmethod
    async def get_batch(self, node_ids: list[str], scope: Scope) -> list[KnowledgeNode]:
        """Retrieve multiple nodes by ID in a single round-trip.

        Absent node IDs are silently omitted from the result list rather than
        raising errors, so callers must reconcile the returned list against
        node_ids if presence checks matter.
        """
        ...

    @abstractmethod
    async def delete(
        self,
        node_id: str,
        scope: Scope,
        cascade: bool = False,
    ) -> DeleteResult:
        """Delete a node, optionally cascading to derived nodes.

        When cascade=True implementations must walk DERIVED_FROM and CITES edges
        and apply the right-to-erasure DAG walk before removing from both graph
        and vector stores.
        """
        ...
