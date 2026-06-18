"""CITE v2 node labels - simplified schema.

Coherence Layer v2: 5 content nodes, 6 edges.
See context/specs/2026-06-18-coherence-layer-v2.md for rationale.
"""

from __future__ import annotations

from enum import StrEnum


class PersistenceLayer(StrEnum):
    """The four EAG layers plus registry and audit."""

    MEMORY = "memory"
    KNOWLEDGE = "knowledge"
    WISDOM = "wisdom"
    INTELLIGENCE = "intelligence"  # Phase 2: passive observation
    REGISTRY = "registry"
    AUDIT = "audit"


class MemoryLabel(StrEnum):
    """Memory layer: raw observations from agents.

    Consolidates: Document, Passage, Utterance, Event, Observation.
    Use memory_type property to distinguish subtypes.
    """

    MEMORY = "Memory"


class KnowledgeLabel(StrEnum):
    """Knowledge layer: claims and verified facts."""

    CLAIM = "Claim"  # Agent assertion with evidence
    FACT = "Fact"  # SAGE-promoted from corroborated Claims


class WisdomLabel(StrEnum):
    """Wisdom layer: synthesized beliefs and agent decisions."""

    BELIEF = "Belief"  # SAGE-synthesized from Facts
    COMMITMENT = "Commitment"  # Agent decisions via decide()


class IntelligenceLabel(StrEnum):
    """Intelligence layer: passive observation artifacts (Phase 2).

    These are system-created, not agent-written.
    """

    EPISTEMIC_STATE = "EpistemicState"  # Confidence/confusion snapshot
    BREAKTHROUGH = "Breakthrough"  # What resolved a stuck state
    # Backwards compat (v1): remove after hypothesize/commit migration
    REASONING_CHAIN = "ReasoningChain"
    WORKING_HYPOTHESIS = "WorkingHypothesis"
    REASONING_SESSION = "ReasoningSession"


class RegistryLabel(StrEnum):
    """Registry: shared identity nodes."""

    AGENT = "Agent"  # Keep for multi-agent silos


class AuditLabel(StrEnum):
    """Audit: system events and state snapshots."""

    ERASURE_EVENT = "ErasureEvent"
    CALIBRATION_EVENT = "CalibrationEvent"


# Label sets by layer
MEMORY_LABELS: frozenset[str] = frozenset(lbl.value for lbl in MemoryLabel)
KNOWLEDGE_LABELS: frozenset[str] = frozenset(lbl.value for lbl in KnowledgeLabel)
WISDOM_LABELS: frozenset[str] = frozenset(lbl.value for lbl in WisdomLabel)
INTELLIGENCE_LABELS: frozenset[str] = frozenset(lbl.value for lbl in IntelligenceLabel)
REGISTRY_LABELS: frozenset[str] = frozenset(lbl.value for lbl in RegistryLabel)
AUDIT_LABELS: frozenset[str] = frozenset(lbl.value for lbl in AuditLabel)

ALL_CITE_LABELS: frozenset[str] = (
    MEMORY_LABELS
    | KNOWLEDGE_LABELS
    | WISDOM_LABELS
    | INTELLIGENCE_LABELS
    | REGISTRY_LABELS
    | AUDIT_LABELS
)

# Content labels: nodes that carry retrievable content
CONTENT_LABELS: frozenset[str] = (
    MEMORY_LABELS | KNOWLEDGE_LABELS | WISDOM_LABELS | INTELLIGENCE_LABELS
)

# Agent-writable labels (via MCP tools)
AGENT_WRITABLE_LABELS: frozenset[str] = frozenset({
    MemoryLabel.MEMORY.value,
    KnowledgeLabel.CLAIM.value,
    WisdomLabel.COMMITMENT.value,
})

# System-created labels (SAGE dreaming)
SYSTEM_CREATED_LABELS: frozenset[str] = frozenset({
    KnowledgeLabel.FACT.value,
    WisdomLabel.BELIEF.value,
    IntelligenceLabel.EPISTEMIC_STATE.value,
    IntelligenceLabel.BREAKTHROUGH.value,
})

# Label -> layer mapping
_LABEL_TO_LAYER: dict[str, PersistenceLayer] = {}
for _m in MemoryLabel:
    _LABEL_TO_LAYER[_m.value] = PersistenceLayer.MEMORY
for _k in KnowledgeLabel:
    _LABEL_TO_LAYER[_k.value] = PersistenceLayer.KNOWLEDGE
for _w in WisdomLabel:
    _LABEL_TO_LAYER[_w.value] = PersistenceLayer.WISDOM
for _i in IntelligenceLabel:
    _LABEL_TO_LAYER[_i.value] = PersistenceLayer.INTELLIGENCE
for _r in RegistryLabel:
    _LABEL_TO_LAYER[_r.value] = PersistenceLayer.REGISTRY
for _a in AuditLabel:
    _LABEL_TO_LAYER[_a.value] = PersistenceLayer.AUDIT


def layer_for_label(label: str) -> PersistenceLayer | None:
    """Return the persistence layer for a given label, or None if unknown."""
    return _LABEL_TO_LAYER.get(label)


# Deprecated labels - for migration tooling
DEPRECATED_LABELS: frozenset[str] = frozenset({
    # Memory layer consolidation
    "Document",  # -> Memory
    "Passage",  # -> Memory
    "Utterance",  # -> Memory
    "Event",  # -> Memory
    "Observation",  # -> Memory
    # Knowledge layer
    # (Claim and Fact kept)
    # Wisdom layer
    "Pattern",  # killed
    "ProposedBelief",  # -> Belief with status property
    # Intelligence layer (agent-facing tools killed)
    "ReasoningChain",  # killed
    "QueryContext",  # killed
    "WorkingHypothesis",  # killed
    # Registry
    "Entity",  # killed (RAG scaffolding)
    "Predicate",  # killed (RAG scaffolding)
    # Meta
    "MetaObservation",  # -> Memory
    # Audit
    "BootstrapState",  # killed
})

LABEL_MIGRATION: dict[str, str] = {
    "Document": "Memory",
    "Passage": "Memory",
    "Utterance": "Memory",
    "Event": "Memory",
    "Observation": "Memory",
    "MetaObservation": "Memory",
    "ProposedBelief": "Belief",
}
