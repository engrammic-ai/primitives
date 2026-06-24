"""CITE edge types organized by function.

Coherence Layer schema: 6 core edges.
See primitives/docs/04-metacognition.md for how ABOUT edges enable metacognition.
"""

from __future__ import annotations

from enum import StrEnum


class CITEEdgeType(StrEnum):
    """Core CITE schema edge types."""

    # Provenance edges
    DERIVED_FROM = "DERIVED_FROM"  # Claim -> Memory, Fact -> Claim
    SYNTHESIZED_FROM = "SYNTHESIZED_FROM"  # Belief -> Fact
    SUPERSEDES = "SUPERSEDES"  # Any -> Any (version chain)

    # Epistemology edges (confidence propagation)
    SUPPORTS = "SUPPORTS"  # Positive evidence
    CONTRADICTS = "CONTRADICTS"  # Negative evidence / conflict

    # Meta-structure
    ABOUT = "ABOUT"  # Commitment -> target nodes, reflection -> target nodes


# Edge sets by function
PROVENANCE_EDGES: frozenset[str] = frozenset({
    CITEEdgeType.DERIVED_FROM,
    CITEEdgeType.SYNTHESIZED_FROM,
    CITEEdgeType.SUPERSEDES,
})

EPISTEMOLOGY_EDGES: frozenset[str] = frozenset({
    CITEEdgeType.SUPPORTS,
    CITEEdgeType.CONTRADICTS,
})

META_EDGES: frozenset[str] = frozenset({
    CITEEdgeType.ABOUT,
})

ALL_CITE_EDGES: frozenset[str] = (
    PROVENANCE_EDGES
    | EPISTEMOLOGY_EDGES
    | META_EDGES
)

# Confidence propagation weights
EDGE_WEIGHTS: dict[str, float] = {
    CITEEdgeType.SUPPORTS: 0.90,
    CITEEdgeType.CONTRADICTS: -0.95,
    CITEEdgeType.DERIVED_FROM: 0.85,
    CITEEdgeType.SYNTHESIZED_FROM: 0.80,
    CITEEdgeType.SUPERSEDES: 0.0,  # Replaces, doesn't propagate
    CITEEdgeType.ABOUT: 0.0,  # Structural, not epistemic
}

# Agent-creatable edges (via MCP tools)
AGENT_CREATABLE_EDGES: frozenset[str] = frozenset({
    CITEEdgeType.DERIVED_FROM,  # via learn() references
    CITEEdgeType.SUPERSEDES,  # via remember()/learn() supersedes param
    CITEEdgeType.ABOUT,  # via decide() about param
})

# System-created edges (SAGE)
SYSTEM_CREATED_EDGES: frozenset[str] = frozenset({
    CITEEdgeType.SYNTHESIZED_FROM,
    CITEEdgeType.SUPPORTS,
    CITEEdgeType.CONTRADICTS,
})


# Deprecated edges - for migration tooling
DEPRECATED_EDGES: frozenset[str] = frozenset({
    # Provenance (consolidated)
    "EXTRACTED_FROM",  # -> DERIVED_FROM
    "PROMOTED_FROM",  # -> DERIVED_FROM
    "CRYSTALLIZED_INTO",  # killed (no hypothesize flow)
    "DECLARED_BY",  # killed (no agent wisdom writes)
    # Semantic (killed)
    "MENTIONS",  # killed (NER extraction)
    "USES_PREDICATE",  # killed (NER extraction)
    "CAUSES",  # killed (causal reasoning premature)
    "CORROBORATES",  # -> SUPPORTS
    "PREVENTS",  # killed (causal reasoning premature)
    "REFERENCES",  # -> DERIVED_FROM
    # Clustering (killed)
    "MEMBER_OF",  # killed (batch clustering)
    "COVERS",  # killed (batch clustering)
    # Pattern (killed)
    "OBSERVED_IN",  # killed (pattern detection)
    # Reasoning chain (killed)
    "TRACED_FROM",  # killed (reasoning chains)
    "CONSENSUS_FROM",  # killed (reasoning chains)
})

EDGE_MIGRATION: dict[str, str | None] = {
    "EXTRACTED_FROM": "DERIVED_FROM",
    "PROMOTED_FROM": "DERIVED_FROM",
    "REFERENCES": "DERIVED_FROM",
    "CORROBORATES": "SUPPORTS",
    # These are killed, no migration target
    "CRYSTALLIZED_INTO": None,
    "DECLARED_BY": None,
    "MENTIONS": None,
    "USES_PREDICATE": None,
    "CAUSES": None,
    "PREVENTS": None,
    "MEMBER_OF": None,
    "COVERS": None,
    "OBSERVED_IN": None,
    "TRACED_FROM": None,
    "CONSENSUS_FROM": None,
}
