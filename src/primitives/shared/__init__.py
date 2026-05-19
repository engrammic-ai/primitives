"""Shared primitives: paradigm-agnostic utilities.

These modules are used across the EAG paradigm implementation.
Signals (heat, freshness, priority) stay in the product repo — they're
proprietary implementation details.
"""

from primitives.shared.fingerprints import (
    claim_fingerprint,
    content_fingerprint,
    json_fingerprint,
    spo_fingerprint,
)
from primitives.shared.validators import (
    ValidationResult,
    validate_citations,
    validate_node_for_promotion,
    validate_scope_access,
)

__all__ = [
    # Fingerprints
    "content_fingerprint",
    "spo_fingerprint",
    "claim_fingerprint",
    "json_fingerprint",
    # Validators
    "ValidationResult",
    "validate_citations",
    "validate_scope_access",
    "validate_node_for_promotion",
]
