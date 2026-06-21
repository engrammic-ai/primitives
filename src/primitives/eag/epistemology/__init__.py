"""Epistemology primitives: confidence, promotion, supersession, propagation.

All functions here are pure and deterministic. No LLM calls happen
at adjudication time.
"""

from primitives.eag.epistemology.confidence import (
    SourceTier,
    combined_confidence,
    incremental_noisy_or,
    noisy_or_aggregate,
    partial_confidence,
    warrant,
)
from primitives.eag.epistemology.promotion import (
    ClaimForPromotion,
    PromotionDecision,
    PromotionRule,
    should_promote_r1,
    should_promote_r2,
)
from primitives.eag.epistemology.propagation import (
    DEPENDENCY_EDGES,
    DependencyEdgeType,
    DependencySet,
    Edge,
    compute_deps,
    direct_dependents,
)
from primitives.eag.epistemology.supersession import (
    ContradictionResult,
    FactForSupersession,
    SupersessionDecision,
    detect_contradiction,
    should_supersede,
)

__all__ = [
    "SourceTier",
    "combined_confidence",
    "warrant",
    "noisy_or_aggregate",
    "incremental_noisy_or",
    "partial_confidence",
    "PromotionRule",
    "ClaimForPromotion",
    "PromotionDecision",
    "should_promote_r1",
    "should_promote_r2",
    "DependencyEdgeType",
    "DEPENDENCY_EDGES",
    "Edge",
    "DependencySet",
    "direct_dependents",
    "compute_deps",
    "ContradictionResult",
    "FactForSupersession",
    "SupersessionDecision",
    "detect_contradiction",
    "should_supersede",
]
