"""Promotion rule primitives.

Pure predicates for determining when claims should promote to facts.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from primitives.eag.epistemology.confidence import SourceTier, noisy_or_aggregate


class PromotionRule(StrEnum):
    """Promotion rule identifiers."""

    R1 = "R1"  # Single authoritative source
    R2 = "R2"  # Multi-source corroboration


@dataclass
class ClaimForPromotion:
    """Minimal claim data needed for promotion decision."""

    fingerprint: str  # sha256(subject|predicate|object)
    combined_confidence: float
    source_tier: SourceTier
    raw_confidence: float


@dataclass
class PromotionDecision:
    """Result of a promotion check."""

    should_promote: bool
    rule: PromotionRule | None
    reason: str
    aggregate_confidence: float = 0.0


def should_promote_r1(claim: ClaimForPromotion) -> PromotionDecision:
    """Check if a single claim qualifies for R1 promotion.

    R1: Single claim with raw_confidence >= 0.7 and authoritative source tier.

    Args:
        claim: The claim to evaluate

    Returns:
        PromotionDecision with result and reasoning
    """
    if claim.source_tier != SourceTier.AUTHORITATIVE:
        return PromotionDecision(
            should_promote=False,
            rule=None,
            reason=f"R1 requires authoritative source, got {claim.source_tier.value}",
        )

    if claim.raw_confidence < 0.7:
        return PromotionDecision(
            should_promote=False,
            rule=None,
            reason=f"R1 requires raw_confidence >= 0.7, got {claim.raw_confidence:.2f}",
        )

    return PromotionDecision(
        should_promote=True,
        rule=PromotionRule.R1,
        reason="Single authoritative source with high confidence",
        aggregate_confidence=claim.combined_confidence,
    )


def should_promote_r2(claims: list[ClaimForPromotion]) -> PromotionDecision:
    """Check if a group of claims qualifies for R2 promotion.

    R2: >= 3 claims with same fingerprint, combined confidence >= 0.8,
    at least one authoritative source.

    Args:
        claims: Claims sharing the same (s,p,o) fingerprint

    Returns:
        PromotionDecision with result and reasoning
    """
    if len(claims) < 3:
        return PromotionDecision(
            should_promote=False,
            rule=None,
            reason=f"R2 requires >= 3 sources, got {len(claims)}",
        )

    has_authoritative = any(c.source_tier == SourceTier.AUTHORITATIVE for c in claims)
    if not has_authoritative:
        return PromotionDecision(
            should_promote=False,
            rule=None,
            reason="R2 requires at least one authoritative source",
        )

    confidences = [c.combined_confidence for c in claims]
    aggregate = noisy_or_aggregate(confidences)

    if aggregate < 0.8:
        return PromotionDecision(
            should_promote=False,
            rule=None,
            reason=f"R2 requires aggregate confidence >= 0.8, got {aggregate:.2f}",
            aggregate_confidence=aggregate,
        )

    return PromotionDecision(
        should_promote=True,
        rule=PromotionRule.R2,
        reason=f"Multi-source corroboration: {len(claims)} sources, aggregate {aggregate:.2f}",
        aggregate_confidence=aggregate,
    )
