"""CITE edge types organized by function."""

from __future__ import annotations

from enum import StrEnum


class CITEEdgeType(StrEnum):
    """All CITE schema edge types."""

    # Provenance edges (transition outputs)
    DERIVED_FROM = "DERIVED_FROM"
    EXTRACTED_FROM = "EXTRACTED_FROM"
    SUPERSEDES = "SUPERSEDES"
    SYNTHESIZED_FROM = "SYNTHESIZED_FROM"
    PROMOTED_FROM = "PROMOTED_FROM"
    CRYSTALLIZED_INTO = "CRYSTALLIZED_INTO"
    DECLARED_BY = "DECLARED_BY"

    # Semantic structure edges
    MENTIONS = "MENTIONS"
    USES_PREDICATE = "USES_PREDICATE"
    CAUSES = "CAUSES"
    CORROBORATES = "CORROBORATES"
    PREVENTS = "PREVENTS"
    REFERENCES = "REFERENCES"

    # Clustering edges
    MEMBER_OF = "MEMBER_OF"
    COVERS = "COVERS"

    # Pattern edges
    OBSERVED_IN = "OBSERVED_IN"

    # Meta-memory edges
    ABOUT = "ABOUT"


# Edge sets by function
PROVENANCE_EDGES: frozenset[str] = frozenset(
    {
        CITEEdgeType.DERIVED_FROM,
        CITEEdgeType.EXTRACTED_FROM,
        CITEEdgeType.SUPERSEDES,
        CITEEdgeType.SYNTHESIZED_FROM,
        CITEEdgeType.PROMOTED_FROM,
        CITEEdgeType.CRYSTALLIZED_INTO,
        CITEEdgeType.DECLARED_BY,
    }
)

SEMANTIC_EDGES: frozenset[str] = frozenset(
    {
        CITEEdgeType.MENTIONS,
        CITEEdgeType.USES_PREDICATE,
        CITEEdgeType.CAUSES,
        CITEEdgeType.CORROBORATES,
        CITEEdgeType.PREVENTS,
        CITEEdgeType.REFERENCES,
    }
)

CLUSTERING_EDGES: frozenset[str] = frozenset(
    {
        CITEEdgeType.MEMBER_OF,
        CITEEdgeType.COVERS,
    }
)

PATTERN_EDGES: frozenset[str] = frozenset(
    {
        CITEEdgeType.OBSERVED_IN,
    }
)

META_MEMORY_EDGES: frozenset[str] = frozenset(
    {
        CITEEdgeType.ABOUT,
    }
)

ALL_CITE_EDGES: frozenset[str] = (
    PROVENANCE_EDGES | SEMANTIC_EDGES | CLUSTERING_EDGES | PATTERN_EDGES | META_MEMORY_EDGES
)
