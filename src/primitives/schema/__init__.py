"""CITE schema definitions: node labels, edge types, layer taxonomy.

Single source of truth for graph structure. Import from here, not string literals.

Schema: 5 content nodes (Memory, Claim, Fact, Belief, Commitment), 6 edges.
Metacognition is not a layer - it's a capability via provenance edges and
Memory nodes with memory_type="reflection". See docs/04-metacognition.md.
"""

from primitives.schema.edges import (
    AGENT_CREATABLE_EDGES,
    ALL_CITE_EDGES,
    DEPRECATED_EDGES,
    EDGE_MIGRATION,
    EDGE_WEIGHTS,
    EPISTEMOLOGY_EDGES,
    META_EDGES,
    PROVENANCE_EDGES,
    SYSTEM_CREATED_EDGES,
    CITEEdgeType,
)
from primitives.schema.labels import (
    AGENT_WRITABLE_LABELS,
    ALL_CITE_LABELS,
    AUDIT_LABELS,
    CONTENT_LABELS,
    DEPRECATED_LABELS,
    INTELLIGENCE_LABELS,
    KNOWLEDGE_LABELS,
    LABEL_MIGRATION,
    MEMORY_LABELS,
    REGISTRY_LABELS,
    SYSTEM_CREATED_LABELS,
    WISDOM_LABELS,
    AuditLabel,
    IntelligenceLabel,
    KnowledgeLabel,
    MemoryLabel,
    NodeStatus,
    PersistenceLayer,
    RegistryLabel,
    WisdomLabel,
    layer_for_label,
)
from primitives.schema.models import (
    Agent,
    BeliefEvent,
    ContradictionEdge,
)

__all__ = [
    # Edges
    "CITEEdgeType",
    "PROVENANCE_EDGES",
    "EPISTEMOLOGY_EDGES",
    "META_EDGES",
    "ALL_CITE_EDGES",
    "EDGE_WEIGHTS",
    "AGENT_CREATABLE_EDGES",
    "SYSTEM_CREATED_EDGES",
    "DEPRECATED_EDGES",
    "EDGE_MIGRATION",
    # Layers
    "PersistenceLayer",
    # Node status
    "NodeStatus",
    # Labels by layer
    "MemoryLabel",
    "KnowledgeLabel",
    "WisdomLabel",
    "IntelligenceLabel",
    "RegistryLabel",
    "AuditLabel",
    # Label sets
    "MEMORY_LABELS",
    "KNOWLEDGE_LABELS",
    "WISDOM_LABELS",
    "INTELLIGENCE_LABELS",
    "REGISTRY_LABELS",
    "AUDIT_LABELS",
    "ALL_CITE_LABELS",
    "CONTENT_LABELS",
    "AGENT_WRITABLE_LABELS",
    "SYSTEM_CREATED_LABELS",
    "DEPRECATED_LABELS",
    "LABEL_MIGRATION",
    # Utilities
    "layer_for_label",
    # Multi-agent coherence models
    "Agent",
    "BeliefEvent",
    "ContradictionEdge",
]
