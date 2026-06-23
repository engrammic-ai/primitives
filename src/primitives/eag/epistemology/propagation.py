"""Propagation primitives.

Pure functions for computing dependency sets per EAG Definition A.8:
deps(n) = {m | DERIVED_FROM(m,n) OR SUPPORTS(m,n)}

The transitive closure requires graph traversal in the service layer.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum


class DependencyEdgeType(StrEnum):
    """Edge types that constitute dependencies for propagation."""

    DERIVED_FROM = "DERIVED_FROM"
    SUPPORTS = "SUPPORTS"
    SYNTHESIZED_FROM = "SYNTHESIZED_FROM"


DEPENDENCY_EDGES: frozenset[str] = frozenset(e.value for e in DependencyEdgeType)


@dataclass(frozen=True)
class Edge:
    """Minimal edge representation for dependency computation."""

    source_id: str
    target_id: str
    edge_type: str


@dataclass
class DependencySet:
    """Result of deps(n) computation."""

    root_id: str
    dependents: frozenset[str]
    depth: int


def direct_dependents(node_id: str, edges: Iterable[Edge]) -> frozenset[str]:
    """Compute direct dependents of a node (depth 1).

    A node m is a direct dependent of n if:
    - There exists edge (m)-[DERIVED_FROM|SUPPORTS|SYNTHESIZED_FROM]->(n)

    Args:
        node_id: The node to find dependents for
        edges: All edges in the subgraph

    Returns:
        Set of node IDs that directly depend on node_id
    """
    dependents: set[str] = set()
    for edge in edges:
        if edge.target_id == node_id and edge.edge_type in DEPENDENCY_EDGES:
            dependents.add(edge.source_id)
    return frozenset(dependents)


def compute_deps(
    node_id: str,
    edges: Iterable[Edge],
    max_depth: int = 10,
) -> DependencySet:
    """Compute transitive closure of deps(n).

    Performs BFS to find all nodes that transitively depend on node_id.

    Args:
        node_id: The root node
        edges: All edges in the subgraph (caller fetches from graph DB)
        max_depth: Maximum traversal depth

    Returns:
        DependencySet with all transitive dependents
    """
    edge_list = list(edges)
    all_dependents: set[str] = set()
    frontier: set[str] = {node_id}
    depth = 0

    while frontier and depth < max_depth:
        next_frontier: set[str] = set()
        for current in frontier:
            deps = direct_dependents(current, edge_list)
            new_deps = deps - all_dependents - {node_id}
            all_dependents.update(new_deps)
            next_frontier.update(new_deps)
        frontier = next_frontier
        depth += 1

    return DependencySet(
        root_id=node_id,
        dependents=frozenset(all_dependents),
        depth=depth,
    )
