"""Predicates for validating layer transitions."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class MissingEvidenceError(Exception):
    """Raised when Knowledge layer write lacks required evidence."""

    message: str = "Knowledge layer requires evidence. Use 'remember' for observations without evidence."

    def __str__(self) -> str:
        return self.message


def validate_evidence_non_empty(evidence: Sequence[str] | None) -> bool:
    """Check that evidence list is non-empty.

    Args:
        evidence: List of evidence URIs/references.

    Returns:
        True if evidence is non-empty, False otherwise.
    """
    if evidence is None:
        return False
    return len(evidence) > 0
