"""CITE schema definitions: node labels, edge types, layer taxonomy.

Single source of truth for graph structure. Import from here, not string literals.

Schema versions:
- v1 (legacy): Full schema with 15+ nodes, 23 edges. Import from .labels, .edges
- v2 (current): Simplified 5 nodes, 6 edges. Import from .labels_v2, .edges_v2

Default exports are v2. For v1 compatibility, import explicitly:
    from primitives.schema.labels import MemoryLabel as MemoryLabelV1
"""

# v2 schema (current default)
# v1 schema (legacy, for migration)
from primitives.schema import edges as edges_v1
from primitives.schema import labels as labels_v1
from primitives.schema.edges_v2 import (
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
from primitives.schema.labels_v2 import (
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
    PersistenceLayer,
    RegistryLabel,
    WisdomLabel,
    layer_for_label,
)

__all__ = [
    # Edges (v2)
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
    # Labels by layer (v2)
    "MemoryLabel",
    "KnowledgeLabel",
    "WisdomLabel",
    "IntelligenceLabel",
    "RegistryLabel",
    "AuditLabel",
    # Label sets (v2)
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
    # Legacy modules (for explicit v1 imports)
    "edges_v1",
    "labels_v1",
]
