"""CITE node labels organized by persistence layer.

Note: `PersistenceLayer` here extends the semantic 4-layer model (protocols.Layer)
with registry and audit layers for system nodes. Use protocols.Layer for scope
filtering in queries; use PersistenceLayer for storage-level classification.
"""

from __future__ import annotations

from enum import StrEnum


class PersistenceLayer(StrEnum):
    """The four EAG layers plus registry and audit."""

    MEMORY = "memory"
    KNOWLEDGE = "knowledge"
    WISDOM = "wisdom"
    INTELLIGENCE = "intelligence"
    REGISTRY = "registry"
    AUDIT = "audit"


class MemoryLabel(StrEnum):
    """Memory layer: raw ingested content."""

    DOCUMENT = "Document"
    PASSAGE = "Passage"
    UTTERANCE = "Utterance"
    EVENT = "Event"
    OBSERVATION = "Observation"


class KnowledgeLabel(StrEnum):
    """Knowledge layer: extracted and promoted facts."""

    FACT = "Fact"
    CLAIM = "Claim"
    COMMITMENT = "Commitment"  # Multi-label: Claim:Commitment


class WisdomLabel(StrEnum):
    """Wisdom layer: synthesized beliefs and patterns."""

    BELIEF = "Belief"
    PATTERN = "Pattern"
    PROPOSED_BELIEF = "ProposedBelief"


class IntelligenceLabel(StrEnum):
    """Intelligence layer: reasoning artifacts."""

    REASONING_CHAIN = "ReasoningChain"
    QUERY_CONTEXT = "QueryContext"
    WORKING_HYPOTHESIS = "WorkingHypothesis"


class RegistryLabel(StrEnum):
    """Registry: shared identity nodes."""

    ENTITY = "Entity"
    PREDICATE = "Predicate"
    AGENT = "Agent"


class AuditLabel(StrEnum):
    """Audit: system events and state snapshots."""

    ERASURE_EVENT = "ErasureEvent"
    CALIBRATION_EVENT = "CalibrationEvent"
    BOOTSTRAP_STATE = "BootstrapState"


class MetaMemoryLabel(StrEnum):
    """Meta-memory: agent observations about their own epistemic state."""

    META_OBSERVATION = "MetaObservation"


# Label sets by layer
MEMORY_LABELS: frozenset[str] = frozenset(lbl.value for lbl in MemoryLabel)
KNOWLEDGE_LABELS: frozenset[str] = frozenset(lbl.value for lbl in KnowledgeLabel)
WISDOM_LABELS: frozenset[str] = frozenset(lbl.value for lbl in WisdomLabel)
INTELLIGENCE_LABELS: frozenset[str] = frozenset(lbl.value for lbl in IntelligenceLabel)
REGISTRY_LABELS: frozenset[str] = frozenset(lbl.value for lbl in RegistryLabel)
AUDIT_LABELS: frozenset[str] = frozenset(lbl.value for lbl in AuditLabel)
META_LABELS: frozenset[str] = frozenset(lbl.value for lbl in MetaMemoryLabel)

ALL_CITE_LABELS: frozenset[str] = (
    MEMORY_LABELS
    | KNOWLEDGE_LABELS
    | WISDOM_LABELS
    | INTELLIGENCE_LABELS
    | REGISTRY_LABELS
    | AUDIT_LABELS
    | META_LABELS
)

# Content labels: nodes that carry retrievable content (excludes registry/audit)
CONTENT_LABELS: frozenset[str] = (
    MEMORY_LABELS | KNOWLEDGE_LABELS | WISDOM_LABELS | INTELLIGENCE_LABELS
)

# Label → layer mapping
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
for _mm in MetaMemoryLabel:
    _LABEL_TO_LAYER[_mm.value] = PersistenceLayer.AUDIT


def layer_for_label(label: str) -> PersistenceLayer | None:
    """Return the persistence layer for a given label, or None if unknown."""
    return _LABEL_TO_LAYER.get(label)
