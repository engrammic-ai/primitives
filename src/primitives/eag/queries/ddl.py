"""DDL (index + constraint) Cypher statements for the EAG graph schema.

Applied at startup; idempotent in Memgraph.
"""

# --- HyperEdge / Silo / EDGE indexes (engine layer) ---

HYPEREDGE_ID_INDEX = "CREATE INDEX ON :HyperEdge(id);"
HYPEREDGE_SILO_INDEX = "CREATE INDEX ON :HyperEdge(silo_id);"
HYPEREDGE_TYPE_INDEX = "CREATE INDEX ON :HyperEdge(type);"
SILO_ID_INDEX = "CREATE INDEX ON :Silo(id);"
SILO_ORG_INDEX = "CREATE INDEX ON :Silo(org_id);"
EDGE_TYPE_INDEX = "CREATE INDEX ON :EDGE(type);"
EDGE_SILO_INDEX = "CREATE INDEX ON :EDGE(silo_id);"

ENGINE_INDEX_QUERIES: tuple[str, ...] = (
    HYPEREDGE_ID_INDEX,
    HYPEREDGE_SILO_INDEX,
    HYPEREDGE_TYPE_INDEX,
    SILO_ID_INDEX,
    SILO_ORG_INDEX,
    EDGE_TYPE_INDEX,
    EDGE_SILO_INDEX,
)

# --- Cluster indexes (clustering layer) ---

CLUSTER_ID_INDEX = "CREATE INDEX ON :Cluster(id);"
CLUSTER_LEVEL_INDEX = "CREATE INDEX ON :Cluster(level);"
CLUSTER_SILO_INDEX = "CREATE INDEX ON :Cluster(silo_id);"

CLUSTER_INDEX_QUERIES: tuple[str, ...] = (
    CLUSTER_ID_INDEX,
    CLUSTER_LEVEL_INDEX,
    CLUSTER_SILO_INDEX,
)

# --- Entity index (db layer) ---

ENTITY_SILO_INDEX = "CREATE INDEX ON :Entity(silo_id);"

ENTITY_INDEX_QUERIES: tuple[str, ...] = (ENTITY_SILO_INDEX,)

# --- Custodian schema: constraints + indexes ---

# Cluster-scope uniqueness constraint on :Finding.
FINDING_CLUSTER_SCOPE_UNIQUE = (
    "CREATE CONSTRAINT ON (f:Finding) ASSERT f.scope, f.cluster_id, f.silo_id IS UNIQUE;"
)

FINDING_ORG_SCOPE_INDEX = "CREATE INDEX ON :Finding(org_id);"
FINDING_SILO_INDEX = "CREATE INDEX ON :Finding(silo_id);"
FINDING_CLUSTER_INDEX = "CREATE INDEX ON :Finding(cluster_id);"
PASS_ID_INDEX = "CREATE INDEX ON :Pass(id);"
PASS_SILO_INDEX = "CREATE INDEX ON :Pass(silo_id);"
REFERENCE_ORG_INDEX = "CREATE INDEX ON :Reference(org_id);"
REFERENCE_URL_INDEX = "CREATE INDEX ON :Reference(url);"
FINDING_HISTORY_PASS_INDEX = "CREATE INDEX ON :FindingHistory(pass_id);"

CUSTODIAN_DDL_STATEMENTS: tuple[str, ...] = (
    FINDING_CLUSTER_SCOPE_UNIQUE,
    FINDING_ORG_SCOPE_INDEX,
    FINDING_SILO_INDEX,
    FINDING_CLUSTER_INDEX,
    PASS_ID_INDEX,
    PASS_SILO_INDEX,
    REFERENCE_ORG_INDEX,
    REFERENCE_URL_INDEX,
    FINDING_HISTORY_PASS_INDEX,
)

# --- Aggregate ---

ALL_CONTEXT_SERVICE_DDL: tuple[str, ...] = (
    *ENGINE_INDEX_QUERIES,
    *CLUSTER_INDEX_QUERIES,
    *ENTITY_INDEX_QUERIES,
    *CUSTODIAN_DDL_STATEMENTS,
)
