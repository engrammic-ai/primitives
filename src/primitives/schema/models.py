"""CITE v2 dataclass models for multi-agent coherence entities.

Provides Agent, BeliefEvent, and edge resolution fields for CONTRADICTS edges.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


def _now() -> datetime:
    return datetime.now(tz=UTC)


@dataclass
class Agent:
    """Registry entity representing an agent identity within a silo."""

    id: str
    silo_id: str
    role: str | None = None
    parent_agent_id: str | None = None
    trust_score: float = 0.5
    beliefs_validated: int = 0
    beliefs_contradicted: int = 0
    first_seen: datetime = field(default_factory=_now)
    last_seen: datetime = field(default_factory=_now)


@dataclass
class BeliefEvent:
    """Audit record for a single belief action by an agent.

    Records who did what to which node and when.
    """

    id: str
    silo_id: str
    agent_id: str
    action: str
    target_node_id: str
    created_at: datetime = field(default_factory=_now)


@dataclass
class ContradictionEdge:
    """Properties for a CONTRADICTS edge with resolution tracking.

    Extends the base edge with fields for tracking how a contradiction
    was detected and resolved.
    """

    source_id: str
    target_id: str
    resolution_status: str | None = None
    detected_by: str | None = None
    resolved_by: str | None = None
    resolved_at: datetime | None = None
