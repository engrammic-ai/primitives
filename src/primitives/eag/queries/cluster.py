"""Cluster Cypher query constants.

All queries use $param placeholders - no string concatenation with user input.
"""

# --- Cluster CRUD ---

CREATE_CLUSTER = """
CREATE (c:Cluster {
    id: $id,
    silo_id: $silo_id,
    level: $level,
    community_id: $community_id,
    summary: $summary,
    key_topics: $key_topics,
    node_count: $node_count,
    created_at: $created_at,
    updated_at: $updated_at
})
RETURN c
"""

GET_CLUSTER = """
MATCH (c:Cluster {id: $id, silo_id: $silo_id})
RETURN c
"""

LIST_CLUSTERS = """
MATCH (c:Cluster {silo_id: $silo_id})
WHERE ($level IS NULL OR c.level = $level)
RETURN c
ORDER BY c.node_count DESC
SKIP $offset
LIMIT $limit
"""

COUNT_CLUSTERS = """
MATCH (c:Cluster {silo_id: $silo_id})
WHERE ($level IS NULL OR c.level = $level)
RETURN count(c) as total
"""

DELETE_CLUSTERS = """
MATCH (c:Cluster {silo_id: $silo_id})
DETACH DELETE c
RETURN count(c) as deleted
"""

UPDATE_CLUSTER_SUMMARY = """
MATCH (c:Cluster {id: $id, silo_id: $silo_id})
SET c.summary = $summary, c.key_topics = $key_topics, c.updated_at = $updated_at
RETURN c
"""

# --- Cluster membership ---
#
# content_union_predicate("n") expands to (n:Document OR n:Passage OR n:Claim).

BATCH_CREATE_MEMBER_OF = """
MATCH (c:Cluster {id: $cluster_id, silo_id: $silo_id})
UNWIND $node_ids AS nid
MATCH (n {id: nid})
WHERE (n:Document OR n:Passage OR n:Claim) OR n:Entity
CREATE (n)-[:MEMBER_OF {weight: $weight, created_at: $created_at}]->(c)
RETURN count(*) as created
"""

CREATE_PART_OF = """
MATCH (child:Cluster {id: $child_id, silo_id: $silo_id})
MATCH (parent:Cluster {id: $parent_id, silo_id: $silo_id})
CREATE (child)-[r:PART_OF {created_at: $created_at}]->(parent)
RETURN r
"""

GET_CLUSTER_MEMBERS = """
MATCH (n)-[r:MEMBER_OF]->(c:Cluster {id: $cluster_id, silo_id: $silo_id})
RETURN n, labels(n) as node_labels, r.weight as weight
ORDER BY r.weight DESC
"""

GET_NODE_CLUSTERS = """
MATCH (n {id: $node_id})-[r:MEMBER_OF]->(c:Cluster {silo_id: $silo_id})
RETURN c, r.weight as weight
ORDER BY c.level ASC
"""

GET_CLUSTER_PARENT = """
MATCH (child:Cluster {id: $child_id, silo_id: $silo_id})-[:PART_OF]->(parent:Cluster)
RETURN parent.id AS parent_id
"""

# --- Community detection via Memgraph MAGE ---
#
# Uses igraphalg.community_leiden (igraph Leiden) instead of MAGE's native
# leiden_community_detection.get — native raises "No communities detected" on
# every resolution; igraph handles the same graph fine.
RUN_LEIDEN = """
CALL igraphalg.community_leiden("CPM", null, $gamma, 0.01, null, 2, null)
YIELD node, community_id
WITH node, community_id
WHERE node.silo_id = $silo_id
  AND ((node:Document OR node:Passage OR node:Claim) OR node:Entity)
RETURN node.id AS node_id, community_id
"""

# --- PageRank ---
#
# Runs on the whole graph; silo filter applied on results.
RUN_PAGERANK = """
CALL pagerank.get()
YIELD node, rank
WITH node, rank
WHERE ((node:Document OR node:Passage OR node:Claim) OR node:Entity)
  AND node.silo_id = $silo_id
RETURN node.id AS node_id, rank
"""

BATCH_UPDATE_NODE_IMPORTANCE = """
UNWIND $updates AS u
MATCH (n {id: u.node_id, silo_id: $silo_id})
WHERE (n:Document OR n:Passage OR n:Claim) OR n:Entity
SET n.importance = u.rank
RETURN count(n) as updated
"""
