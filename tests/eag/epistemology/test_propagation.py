"""Tests for propagation primitives."""

from primitives.eag.epistemology.propagation import (
    DEPENDENCY_EDGES,
    DependencyEdgeType,
    DependencySet,
    Edge,
    compute_deps,
    direct_dependents,
)


class TestDependencyEdges:
    """Tests for dependency edge type definitions."""

    def test_dependency_edges_contains_derived_from(self) -> None:
        assert "DERIVED_FROM" in DEPENDENCY_EDGES

    def test_dependency_edges_contains_supports(self) -> None:
        assert "SUPPORTS" in DEPENDENCY_EDGES

    def test_dependency_edges_contains_synthesized_from(self) -> None:
        assert "SYNTHESIZED_FROM" in DEPENDENCY_EDGES

    def test_enum_values_match_frozenset(self) -> None:
        for edge_type in DependencyEdgeType:
            assert edge_type.value in DEPENDENCY_EDGES


class TestDirectDependents:
    """Tests for direct_dependents function."""

    def test_finds_derived_from_dependents(self) -> None:
        edges = [
            Edge("belief-1", "fact-1", "DERIVED_FROM"),
            Edge("belief-2", "fact-1", "DERIVED_FROM"),
        ]
        deps = direct_dependents("fact-1", edges)
        assert deps == frozenset({"belief-1", "belief-2"})

    def test_finds_supports_dependents(self) -> None:
        edges = [
            Edge("claim-a", "memory-1", "SUPPORTS"),
        ]
        deps = direct_dependents("memory-1", edges)
        assert deps == frozenset({"claim-a"})

    def test_ignores_non_dependency_edges(self) -> None:
        edges = [
            Edge("belief-1", "fact-1", "DERIVED_FROM"),
            Edge("fact-1", "claim-1", "PROMOTED_FROM"),
        ]
        deps = direct_dependents("fact-1", edges)
        assert deps == frozenset({"belief-1"})
        assert "claim-1" not in deps

    def test_returns_empty_for_no_dependents(self) -> None:
        edges = [
            Edge("belief-1", "fact-1", "DERIVED_FROM"),
        ]
        deps = direct_dependents("fact-2", edges)
        assert deps == frozenset()

    def test_handles_empty_edges(self) -> None:
        deps = direct_dependents("node-1", [])
        assert deps == frozenset()


class TestComputeDeps:
    """Tests for compute_deps transitive closure."""

    def test_single_level_deps(self) -> None:
        edges = [
            Edge("belief-1", "fact-1", "DERIVED_FROM"),
            Edge("belief-2", "fact-1", "SYNTHESIZED_FROM"),
        ]
        result = compute_deps("fact-1", edges)
        assert result.root_id == "fact-1"
        assert result.dependents == frozenset({"belief-1", "belief-2"})

    def test_multi_level_deps(self) -> None:
        # fact-1 <- belief-1 <- commitment-1
        edges = [
            Edge("belief-1", "fact-1", "DERIVED_FROM"),
            Edge("commitment-1", "belief-1", "SUPPORTS"),
        ]
        result = compute_deps("fact-1", edges)
        assert "belief-1" in result.dependents
        assert "commitment-1" in result.dependents

    def test_respects_max_depth(self) -> None:
        # Create a long chain: node-0 <- node-1 <- node-2 <- ... <- node-5
        edges = [
            Edge(f"node-{i+1}", f"node-{i}", "DERIVED_FROM")
            for i in range(5)
        ]
        result = compute_deps("node-0", edges, max_depth=2)
        assert "node-1" in result.dependents
        assert "node-2" in result.dependents
        # node-3, node-4, node-5 should be cut off by max_depth
        assert result.depth <= 2

    def test_handles_cycles_gracefully(self) -> None:
        # Create a cycle: a <- b <- c <- a
        edges = [
            Edge("b", "a", "DERIVED_FROM"),
            Edge("c", "b", "DERIVED_FROM"),
            Edge("a", "c", "DERIVED_FROM"),
        ]
        result = compute_deps("a", edges)
        # Should not infinite loop, should find b and c
        assert "b" in result.dependents
        assert "c" in result.dependents

    def test_excludes_root_from_dependents(self) -> None:
        edges = [
            Edge("node-1", "root", "DERIVED_FROM"),
        ]
        result = compute_deps("root", edges)
        assert "root" not in result.dependents

    def test_returns_dependency_set_type(self) -> None:
        result = compute_deps("node-1", [])
        assert isinstance(result, DependencySet)
        assert result.root_id == "node-1"
        assert result.dependents == frozenset()
