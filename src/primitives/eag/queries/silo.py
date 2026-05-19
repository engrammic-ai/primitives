"""Silo Cypher query constants.

All queries use $param placeholders - no string concatenation with user input.
"""

CREATE_SILO = """
CREATE (s:Silo {
    id: $id,
    name: $name,
    description: $description,
    org_id: $org_id,
    dissolvability: $dissolvability,
    metadata: $metadata,
    created_at: timestamp(),
    updated_at: timestamp()
})
RETURN s
"""

GET_SILO = """
MATCH (s:Silo {id: $id, org_id: $org_id})
RETURN s
"""

LIST_SILOS = """
MATCH (s:Silo {org_id: $org_id})
RETURN s
ORDER BY s.name
"""

UPDATE_SILO = """
MATCH (s:Silo {id: $id, org_id: $org_id})
SET s.name = $name,
    s.description = $description,
    s.dissolvability = $dissolvability,
    s.metadata = $metadata,
    s.updated_at = timestamp()
RETURN s
"""

DELETE_SILO = """
MATCH (s:Silo {id: $id, org_id: $org_id})
DELETE s
RETURN count(s) AS deleted
"""

RESET_SILO = """
MATCH (n)
WHERE (n:Document OR n:Passage OR n:Claim OR n:Entity OR n:HyperEdge)
  AND n.silo_id = $silo_id
DETACH DELETE n
RETURN count(n) AS deleted_nodes
"""
