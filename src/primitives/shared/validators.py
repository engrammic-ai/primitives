"""Validation primitives: citation checking, scope validation.

Reusable validators for ensuring data integrity across paradigms.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from primitives.protocols import Scope


@dataclass
class ValidationResult:
    """Result of a validation check."""

    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_citations(
    cited_ids: list[str],
    valid_ids: set[str],
    scope: Scope,
) -> ValidationResult:
    """Validate that all cited IDs exist and are in scope.

    Args:
        cited_ids: IDs being cited
        valid_ids: Set of valid IDs in the current scope
        scope: Current operation scope

    Returns:
        ValidationResult with any invalid citations as errors
    """
    errors = []
    for cid in cited_ids:
        if cid not in valid_ids:
            errors.append(f"Citation {cid} not found in scope {scope.silo_id}")

    return ValidationResult(valid=len(errors) == 0, errors=errors)


def validate_scope_access(
    requested_scope: Scope,
    allowed_scopes: list[Scope],
) -> ValidationResult:
    """Validate that requested scope is within allowed scopes.

    Args:
        requested_scope: The scope being requested
        allowed_scopes: List of scopes the caller has access to

    Returns:
        ValidationResult indicating access permission
    """
    for allowed in allowed_scopes:
        if allowed.org_id and requested_scope.org_id != allowed.org_id:
            continue
        if allowed.silo_id and requested_scope.silo_id != allowed.silo_id:
            continue
        # Match found
        return ValidationResult(valid=True)

    return ValidationResult(
        valid=False,
        errors=[f"Access denied to scope {requested_scope.silo_id}"],
    )


def validate_node_for_promotion(
    node_id: str,
    has_citations: bool,
    confidence: float,
    min_confidence: float = 0.0,
    derivation_edge_count: int | None = None,
    min_derivation_edges: int = 0,
) -> ValidationResult:
    """Validate that a node meets basic promotion requirements.

    Args:
        node_id: The node being validated
        has_citations: Whether node has at least one citation
        confidence: Node's confidence score
        min_confidence: Minimum confidence threshold
        derivation_edge_count: Number of SYNTHESIZED_FROM edges (for Beliefs)
        min_derivation_edges: Minimum required derivation edges (default 0)

    Returns:
        ValidationResult with any issues
    """
    errors = []
    warnings = []

    if not has_citations:
        errors.append(f"Node {node_id} has no citations (invariant I1)")

    if confidence < min_confidence:
        errors.append(
            f"Node {node_id} confidence {confidence:.2f} below threshold {min_confidence:.2f}"
        )

    if confidence < 0.5:
        warnings.append(f"Node {node_id} has low confidence {confidence:.2f}")

    if derivation_edge_count is not None and derivation_edge_count < min_derivation_edges:
        errors.append(
            f"Node {node_id} has {derivation_edge_count} derivation edges, "
            f"requires {min_derivation_edges} (EAG Table 2)"
        )

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )
