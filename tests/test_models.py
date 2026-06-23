"""Tests for multi-agent coherence schema models."""

from datetime import UTC, datetime

from primitives.protocols import KnowledgeNode, Layer
from primitives.schema.models import Agent, BeliefEvent, ContradictionEdge


class TestKnowledgeNodeIdentityFields:
    def test_identity_fields_default_none(self):
        node = KnowledgeNode(id="n1", layer=Layer.MEMORY, silo_id="s1")
        assert node.agent_id is None
        assert node.session_id is None
        assert node.owner_id is None
        assert node.model_id is None

    def test_identity_fields_set(self):
        node = KnowledgeNode(
            id="n1",
            layer=Layer.KNOWLEDGE,
            silo_id="s1",
            agent_id="agent-abc",
            session_id="sess-xyz",
            owner_id="agent-abc",
            model_id="claude-sonnet-4-6",
        )
        assert node.agent_id == "agent-abc"
        assert node.session_id == "sess-xyz"
        assert node.owner_id == "agent-abc"
        assert node.model_id == "claude-sonnet-4-6"


class TestAgent:
    def test_required_fields(self):
        now = datetime.now(tz=UTC)
        agent = Agent(id="agent-1", silo_id="silo-1", first_seen=now, last_seen=now)
        assert agent.id == "agent-1"
        assert agent.silo_id == "silo-1"
        assert agent.role is None
        assert agent.parent_agent_id is None

    def test_defaults(self):
        now = datetime.now(tz=UTC)
        agent = Agent(id="agent-1", silo_id="silo-1", first_seen=now, last_seen=now)
        assert agent.trust_score == 0.5
        assert agent.beliefs_validated == 0
        assert agent.beliefs_contradicted == 0

    def test_role_and_hierarchy(self):
        now = datetime.now(tz=UTC)
        agent = Agent(
            id="agent-child",
            silo_id="silo-1",
            role="reviewer",
            parent_agent_id="agent-parent",
            first_seen=now,
            last_seen=now,
        )
        assert agent.role == "reviewer"
        assert agent.parent_agent_id == "agent-parent"

    def test_trust_and_stats(self):
        now = datetime.now(tz=UTC)
        agent = Agent(
            id="agent-1",
            silo_id="silo-1",
            trust_score=0.8,
            beliefs_validated=10,
            beliefs_contradicted=2,
            first_seen=now,
            last_seen=now,
        )
        assert agent.trust_score == 0.8
        assert agent.beliefs_validated == 10
        assert agent.beliefs_contradicted == 2


class TestBeliefEvent:
    def test_required_fields(self):
        now = datetime.now(tz=UTC)
        event = BeliefEvent(
            id="01JABCDEF",
            silo_id="silo-1",
            agent_id="agent-abc",
            action="asserted",
            target_node_id="node-xyz",
            created_at=now,
        )
        assert event.id == "01JABCDEF"
        assert event.silo_id == "silo-1"
        assert event.agent_id == "agent-abc"
        assert event.action == "asserted"
        assert event.target_node_id == "node-xyz"

    def test_valid_actions(self):
        now = datetime.now(tz=UTC)
        for action in ("asserted", "retracted", "challenged", "superseded"):
            event = BeliefEvent(
                id="01JABCDEF",
                silo_id="silo-1",
                agent_id="agent-abc",
                action=action,
                target_node_id="node-xyz",
                created_at=now,
            )
            assert event.action == action

    def test_default_created_at(self):
        event = BeliefEvent(
            id="01JABCDEF",
            silo_id="silo-1",
            agent_id="agent-abc",
            action="asserted",
            target_node_id="node-xyz",
        )
        assert isinstance(event.created_at, datetime)


class TestContradictionEdge:
    def test_required_fields(self):
        edge = ContradictionEdge(source_id="node-a", target_id="node-b")
        assert edge.source_id == "node-a"
        assert edge.target_id == "node-b"

    def test_resolution_fields_default_none(self):
        edge = ContradictionEdge(source_id="node-a", target_id="node-b")
        assert edge.resolution_status is None
        assert edge.detected_by is None
        assert edge.resolved_by is None
        assert edge.resolved_at is None

    def test_resolution_fields_set(self):
        now = datetime.now(tz=UTC)
        edge = ContradictionEdge(
            source_id="node-a",
            target_id="node-b",
            resolution_status="superseded",
            detected_by="system",
            resolved_by="agent-abc",
            resolved_at=now,
        )
        assert edge.resolution_status == "superseded"
        assert edge.detected_by == "system"
        assert edge.resolved_by == "agent-abc"
        assert edge.resolved_at == now

    def test_valid_resolution_statuses(self):
        for status in ("unresolved", "superseded", "dismissed", "escalated"):
            edge = ContradictionEdge(
                source_id="node-a",
                target_id="node-b",
                resolution_status=status,
            )
            assert edge.resolution_status == status
