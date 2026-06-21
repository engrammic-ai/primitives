"""Tests for promotion rule primitives."""

from primitives.eag.epistemology.confidence import SourceTier
from primitives.eag.epistemology.promotion import (
    ClaimForPromotion,
    PromotionRule,
    should_promote_r1,
    should_promote_r2,
)


def make_claim(
    fingerprint: str = "abc123",
    combined_confidence: float = 0.85,
    source_tier: SourceTier = SourceTier.AUTHORITATIVE,
    raw_confidence: float = 0.8,
) -> ClaimForPromotion:
    return ClaimForPromotion(
        fingerprint=fingerprint,
        combined_confidence=combined_confidence,
        source_tier=source_tier,
        raw_confidence=raw_confidence,
    )


class TestShouldPromoteR1:
    def test_authoritative_high_confidence_promotes(self):
        claim = make_claim(raw_confidence=0.8, source_tier=SourceTier.AUTHORITATIVE)
        decision = should_promote_r1(claim)

        assert decision.should_promote is True
        assert decision.rule == PromotionRule.R1
        assert "authoritative" in decision.reason.lower()

    def test_authoritative_low_confidence_rejected(self):
        claim = make_claim(raw_confidence=0.5, source_tier=SourceTier.AUTHORITATIVE)
        decision = should_promote_r1(claim)

        assert decision.should_promote is False
        assert decision.rule is None
        assert "0.7" in decision.reason

    def test_non_authoritative_rejected(self):
        claim = make_claim(raw_confidence=0.9, source_tier=SourceTier.VALIDATED)
        decision = should_promote_r1(claim)

        assert decision.should_promote is False
        assert "authoritative" in decision.reason.lower()

    def test_boundary_confidence_0_7_promotes(self):
        claim = make_claim(raw_confidence=0.7, source_tier=SourceTier.AUTHORITATIVE)
        decision = should_promote_r1(claim)

        assert decision.should_promote is True

    def test_boundary_confidence_below_0_7_rejected(self):
        claim = make_claim(raw_confidence=0.69, source_tier=SourceTier.AUTHORITATIVE)
        decision = should_promote_r1(claim)

        assert decision.should_promote is False

    def test_aggregate_confidence_in_result(self):
        claim = make_claim(
            raw_confidence=0.8,
            combined_confidence=0.9,
            source_tier=SourceTier.AUTHORITATIVE,
        )
        decision = should_promote_r1(claim)

        assert decision.aggregate_confidence == 0.9


class TestShouldPromoteR2:
    def test_single_claim_rejected(self):
        claims = [make_claim()]
        decision = should_promote_r2(claims)

        assert decision.should_promote is False
        assert ">= 3" in decision.reason

    def test_empty_list_rejected(self):
        decision = should_promote_r2([])
        assert decision.should_promote is False

    def test_two_claims_rejected(self):
        claims = [
            make_claim(combined_confidence=0.7, source_tier=SourceTier.AUTHORITATIVE),
            make_claim(combined_confidence=0.6, source_tier=SourceTier.VALIDATED),
        ]
        decision = should_promote_r2(claims)

        assert decision.should_promote is False
        assert ">= 3" in decision.reason

    def test_three_claims_with_authoritative_promotes(self):
        claims = [
            make_claim(combined_confidence=0.7, source_tier=SourceTier.AUTHORITATIVE),
            make_claim(combined_confidence=0.6, source_tier=SourceTier.VALIDATED),
            make_claim(combined_confidence=0.6, source_tier=SourceTier.COMMUNITY),
        ]
        decision = should_promote_r2(claims)

        assert decision.should_promote is True
        assert decision.rule == PromotionRule.R2

    def test_no_authoritative_source_rejected(self):
        claims = [
            make_claim(combined_confidence=0.9, source_tier=SourceTier.VALIDATED),
            make_claim(combined_confidence=0.9, source_tier=SourceTier.COMMUNITY),
            make_claim(combined_confidence=0.9, source_tier=SourceTier.COMMUNITY),
        ]
        decision = should_promote_r2(claims)

        assert decision.should_promote is False
        assert "authoritative" in decision.reason.lower()

    def test_low_aggregate_confidence_rejected(self):
        claims = [
            make_claim(combined_confidence=0.3, source_tier=SourceTier.AUTHORITATIVE),
            make_claim(combined_confidence=0.3, source_tier=SourceTier.VALIDATED),
            make_claim(combined_confidence=0.3, source_tier=SourceTier.COMMUNITY),
        ]
        decision = should_promote_r2(claims)

        assert decision.should_promote is False
        assert "0.8" in decision.reason

    def test_aggregate_uses_noisy_or(self):
        claims = [
            make_claim(combined_confidence=0.7, source_tier=SourceTier.AUTHORITATIVE),
            make_claim(combined_confidence=0.7, source_tier=SourceTier.VALIDATED),
            make_claim(combined_confidence=0.7, source_tier=SourceTier.COMMUNITY),
        ]
        decision = should_promote_r2(claims)

        expected_aggregate = 1 - (0.3 * 0.3 * 0.3)
        assert abs(decision.aggregate_confidence - expected_aggregate) < 0.01

    def test_many_weak_sources_can_promote(self):
        claims = [
            make_claim(combined_confidence=0.5, source_tier=SourceTier.AUTHORITATIVE),
            make_claim(combined_confidence=0.5, source_tier=SourceTier.VALIDATED),
            make_claim(combined_confidence=0.5, source_tier=SourceTier.COMMUNITY),
        ]
        decision = should_promote_r2(claims)

        assert decision.should_promote is True
