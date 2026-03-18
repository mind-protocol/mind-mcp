"""
Tests for Phase U5: L3 Physics -- Energy, Consolidation, Macro-Crystallization

Covers:
- L3 energy injection split (60/30/10)
- L3 propagation (energy conservation, surplus distribution)
- L3 decay (rate correctness)
- L3 weight consolidation (structural utility, weight non-negative, bounded)
- L3 macro-crystallization (candidate detection, hub creation, weight preservation)

DOCS: docs/universe/IMPLEMENTATION_Universe_Graph.md (Phase U5)
"""

import math
import pytest

from runtime.physics.l3_energy_propagation_and_decay import (
    L3Node,
    L3Link,
    l3_inject_energy,
    l3_propagate,
    l3_decay,
    l3_decay_batch,
    EnergyInjectionResult,
)
from runtime.physics.l3_weight_consolidation import (
    L3ConsolidationLink,
    compute_structural_utility,
    l3_consolidate,
    l3_consolidate_batch,
)
from runtime.physics.l3_macro_crystallization import (
    ClusterNode,
    ClusterLink,
    CrystallizationCandidate,
    detect_crystallization_candidates,
    crystallize,
    validate_crystallization_preserves_weight,
)
from runtime.universe.constants import (
    L3_PROPAGATION_THRESHOLD,
    L3_DECAY_RATE,
    L3_RECENCY_DECAY,
    L3_ENERGY_SPLIT_SPACE,
    L3_ENERGY_SPLIT_ACTOR,
    L3_ENERGY_SPLIT_RELATED,
    L3_CONSOLIDATION_ALPHA,
    L3_CRYSTALLIZATION_MIN_SIZE,
    L3_CRYSTALLIZATION_DENSITY,
    L3_CRYSTALLIZATION_WEIGHT,
    L3_CRYSTALLIZATION_DAMPING_FACTOR,
)


# =============================================================================
# L3 Energy Injection
# =============================================================================

class TestL3EnergyInjection:
    """Tests for ALG-6 energy injection."""

    def test_energy_split_ratios(self):
        """Energy must split 60/30/10 between space/actor/context."""
        moment = L3Node(id="m1", energy=0.0)
        space_link = L3Link(node_a="m1", node_b="s1")
        actor_link = L3Link(node_a="m1", node_b="a1")
        related = [L3Link(node_a="m1", node_b="t1")]

        result = l3_inject_energy(moment, space_link, actor_link, related, 10.0)

        assert abs(result.space_energy_added - 6.0) < 1e-10
        assert abs(result.actor_energy_added - 3.0) < 1e-10
        assert abs(result.context_energy_added - 1.0) < 1e-10
        assert abs(result.total_injected - 10.0) < 1e-10

    def test_energy_split_multiple_related(self):
        """Context share divided equally among related links."""
        moment = L3Node(id="m1", energy=0.0)
        space_link = L3Link(node_a="m1", node_b="s1")
        actor_link = L3Link(node_a="m1", node_b="a1")
        related = [
            L3Link(node_a="m1", node_b="t1"),
            L3Link(node_a="m1", node_b="t2"),
        ]

        l3_inject_energy(moment, space_link, actor_link, related, 10.0)

        assert abs(related[0].energy - 0.5) < 1e-10  # 1.0 / 2
        assert abs(related[1].energy - 0.5) < 1e-10

    def test_energy_injection_no_related(self):
        """If no related links, context share is 0."""
        moment = L3Node(id="m1", energy=0.0)
        space_link = L3Link(node_a="m1", node_b="s1")
        actor_link = L3Link(node_a="m1", node_b="a1")

        result = l3_inject_energy(moment, space_link, actor_link, [], 10.0)

        assert abs(result.context_energy_added - 0.0) < 1e-10
        assert abs(moment.energy - 10.0) < 1e-10

    def test_energy_moment_accumulates(self):
        """Moment receives the full energy amount."""
        moment = L3Node(id="m1", energy=5.0)
        space_link = L3Link(node_a="m1", node_b="s1")
        actor_link = L3Link(node_a="m1", node_b="a1")

        l3_inject_energy(moment, space_link, actor_link, [], 10.0)

        assert abs(moment.energy - 15.0) < 1e-10

    def test_negative_energy_raises(self):
        """Negative energy injection must raise ValueError."""
        moment = L3Node(id="m1")
        space_link = L3Link(node_a="m1", node_b="s1")
        actor_link = L3Link(node_a="m1", node_b="a1")

        with pytest.raises(ValueError):
            l3_inject_energy(moment, space_link, actor_link, [], -1.0)

    def test_zero_energy_is_noop(self):
        """Zero energy injection should succeed without changing anything."""
        moment = L3Node(id="m1", energy=5.0)
        space_link = L3Link(node_a="m1", node_b="s1", energy=1.0)
        actor_link = L3Link(node_a="m1", node_b="a1", energy=2.0)

        result = l3_inject_energy(moment, space_link, actor_link, [], 0.0)

        assert abs(moment.energy - 5.0) < 1e-10
        assert abs(space_link.energy - 1.0) < 1e-10
        assert abs(actor_link.energy - 2.0) < 1e-10
        assert abs(result.total_injected - 0.0) < 1e-10


# =============================================================================
# L3 Propagation
# =============================================================================

class TestL3Propagation:
    """Tests for ALG-6 Law 2: surplus spill-over propagation."""

    def test_no_propagation_below_threshold(self):
        """Node energy at or below threshold should not propagate."""
        node = L3Node(id="n1", energy=L3_PROPAGATION_THRESHOLD)
        link = L3Link(node_a="n1", node_b="n2", weight=1.0)
        neighbor = L3Node(id="n2", energy=0.0)

        propagated = l3_propagate(node, [link], {"n2": neighbor})

        assert propagated == 0.0
        assert abs(node.energy - L3_PROPAGATION_THRESHOLD) < 1e-10
        assert abs(neighbor.energy - 0.0) < 1e-10

    def test_propagation_distributes_surplus(self):
        """Surplus above threshold is distributed proportional to weights."""
        node = L3Node(id="n1", energy=3.0)
        link1 = L3Link(node_a="n1", node_b="n2", weight=2.0)
        link2 = L3Link(node_a="n1", node_b="n3", weight=1.0)
        n2 = L3Node(id="n2", energy=0.0)
        n3 = L3Node(id="n3", energy=0.0)

        surplus = 3.0 - L3_PROPAGATION_THRESHOLD  # 2.0

        propagated = l3_propagate(node, [link1, link2], {"n2": n2, "n3": n3})

        # Weight ratio 2:1, so n2 gets 2/3 of surplus, n3 gets 1/3
        expected_n2 = surplus * (2.0 / 3.0) * 1.0  # polarity=1
        expected_n3 = surplus * (1.0 / 3.0) * 1.0
        assert abs(n2.energy - expected_n2) < 1e-10
        assert abs(n3.energy - expected_n3) < 1e-10

    def test_energy_conservation_during_propagation(self):
        """Total energy before == total energy after propagation."""
        node = L3Node(id="n1", energy=5.0)
        link1 = L3Link(node_a="n1", node_b="n2", weight=1.0)
        link2 = L3Link(node_a="n1", node_b="n3", weight=1.0)
        n2 = L3Node(id="n2", energy=1.0)
        n3 = L3Node(id="n3", energy=2.0)

        total_before = node.energy + n2.energy + n3.energy
        # Note: link energy is separate; we track it but don't include in node conservation
        l3_propagate(node, [link1, link2], {"n2": n2, "n3": n3})

        total_after = node.energy + n2.energy + n3.energy
        # Energy in links is 10% of each share -> total node energy decreases slightly
        # The 0.1 link storage means conservation is: node_total + link_total = constant
        # But for node-only: we need to account for the 10% going to links
        surplus = 5.0 - L3_PROPAGATION_THRESHOLD
        link_storage = surplus * 0.1  # Each share has 0.1 stored in link

        # Node energy is conserved (surplus moves to neighbors)
        assert abs(total_after - total_before) < 1e-10

    def test_propagation_depletes_to_threshold(self):
        """After propagation, source node energy equals threshold."""
        node = L3Node(id="n1", energy=10.0)
        link = L3Link(node_a="n1", node_b="n2", weight=1.0)
        n2 = L3Node(id="n2", energy=0.0)

        l3_propagate(node, [link], {"n2": n2})

        assert abs(node.energy - L3_PROPAGATION_THRESHOLD) < 1e-10

    def test_propagation_no_links(self):
        """Node with no outbound links should not propagate."""
        node = L3Node(id="n1", energy=10.0)
        propagated = l3_propagate(node, [], {})
        assert propagated == 0.0
        assert abs(node.energy - 10.0) < 1e-10

    def test_polarity_modulates_propagation(self):
        """Polarity affects share (negative polarity = negative energy flow)."""
        node = L3Node(id="n1", energy=3.0)
        link = L3Link(node_a="n1", node_b="n2", weight=1.0, polarity=0.5)
        n2 = L3Node(id="n2", energy=0.0)

        surplus = 3.0 - L3_PROPAGATION_THRESHOLD
        l3_propagate(node, [link], {"n2": n2})

        expected = surplus * 1.0 * 0.5  # weight_ratio=1 * polarity=0.5
        assert abs(n2.energy - expected) < 1e-10

    def test_link_remembers_flow(self):
        """Link energy increases by 10% of each share."""
        node = L3Node(id="n1", energy=3.0)
        link = L3Link(node_a="n1", node_b="n2", weight=1.0, energy=0.0)
        n2 = L3Node(id="n2", energy=0.0)

        surplus = 3.0 - L3_PROPAGATION_THRESHOLD
        l3_propagate(node, [link], {"n2": n2})

        expected_link_energy = surplus * 0.1
        assert abs(link.energy - expected_link_energy) < 1e-10


# =============================================================================
# L3 Decay
# =============================================================================

class TestL3Decay:
    """Tests for ALG-6 Law 3: energy and recency decay."""

    def test_energy_decay_rate(self):
        """Energy decays at L3_DECAY_RATE per tick."""
        node = L3Node(id="n1", energy=10.0, recency=1.0)
        l3_decay(node)
        expected = 10.0 * (1.0 - L3_DECAY_RATE)
        assert abs(node.energy - expected) < 1e-10

    def test_recency_decay_rate(self):
        """Recency decays at L3_RECENCY_DECAY per tick."""
        node = L3Node(id="n1", energy=1.0, recency=1.0)
        l3_decay(node)
        expected = 1.0 * (1.0 - L3_RECENCY_DECAY)
        assert abs(node.recency - expected) < 1e-10

    def test_decay_never_goes_negative(self):
        """Energy and recency clamp to 0."""
        node = L3Node(id="n1", energy=0.0, recency=0.0)
        l3_decay(node)
        assert node.energy >= 0.0
        assert node.recency >= 0.0

    def test_decay_multiple_ticks(self):
        """Multiple decay ticks compound."""
        node = L3Node(id="n1", energy=100.0, recency=1.0)
        for _ in range(100):
            l3_decay(node)
        expected_energy = 100.0 * ((1.0 - L3_DECAY_RATE) ** 100)
        expected_recency = 1.0 * ((1.0 - L3_RECENCY_DECAY) ** 100)
        assert abs(node.energy - expected_energy) < 1e-6
        assert abs(node.recency - expected_recency) < 1e-6

    def test_decay_slower_than_l1(self):
        """L3 decay rate must be slower than L1's 0.02."""
        assert L3_DECAY_RATE < 0.02  # L1 rate
        assert L3_RECENCY_DECAY < 0.02

    def test_decay_batch(self):
        """Batch decay returns total energy lost."""
        nodes = [
            L3Node(id=f"n{i}", energy=10.0, recency=1.0)
            for i in range(5)
        ]
        total_before = sum(n.energy for n in nodes)
        total_lost = l3_decay_batch(nodes)
        total_after = sum(n.energy for n in nodes)
        assert abs(total_lost - (total_before - total_after)) < 1e-10
        assert total_lost > 0


# =============================================================================
# L3 Weight Consolidation
# =============================================================================

class TestL3WeightConsolidation:
    """Tests for ALG-6 Law 6: weight consolidation."""

    def test_structural_utility_thing_link(self):
        """Thing/service link uses usage-based utility."""
        link = L3ConsolidationLink(
            node_a="a1", node_b="t1",
            node_a_type="actor", node_b_type="thing",
            usage_count=50,
        )
        u = compute_structural_utility(link)
        assert 0.0 < u <= 1.0

    def test_structural_utility_actor_actor(self):
        """Actor-actor link uses co-activation frequency."""
        link = L3ConsolidationLink(
            node_a="a1", node_b="a2",
            node_a_type="actor", node_b_type="actor",
            co_activation_count=25,
        )
        u = compute_structural_utility(link)
        assert 0.0 < u <= 1.0

    def test_structural_utility_space_link(self):
        """Space link uses presence intensity."""
        link = L3ConsolidationLink(
            node_a="a1", node_b="s1",
            node_a_type="actor", node_b_type="space",
            presence_hours=10.0,
        )
        u = compute_structural_utility(link)
        assert 0.0 < u <= 1.0

    def test_structural_utility_zero_usage(self):
        """Zero usage = zero utility."""
        link = L3ConsolidationLink(
            node_a="a1", node_b="t1",
            node_a_type="actor", node_b_type="thing",
            usage_count=0,
        )
        assert compute_structural_utility(link) == 0.0

    def test_structural_utility_bounded(self):
        """Utility is always in [0, 1]."""
        link = L3ConsolidationLink(
            node_a="a1", node_b="t1",
            node_a_type="actor", node_b_type="thing",
            usage_count=10000,
        )
        u = compute_structural_utility(link)
        assert 0.0 <= u <= 1.0

    def test_consolidation_weight_increases(self):
        """Consolidation increases weight when avg_energy and utility are positive."""
        link = L3ConsolidationLink(
            node_a="a1", node_b="t1",
            weight=0.3, avg_energy=2.0,
            node_a_type="actor", node_b_type="thing",
            usage_count=50,
        )
        result = l3_consolidate(link)
        assert result.delta_weight > 0
        assert link.weight > 0.3

    def test_consolidation_weight_non_negative(self):
        """Weight must never go below 0."""
        link = L3ConsolidationLink(
            node_a="a1", node_b="t1",
            weight=0.0, avg_energy=0.0,
            node_a_type="actor", node_b_type="thing",
            usage_count=0,
        )
        result = l3_consolidate(link)
        assert link.weight >= 0.0
        assert result.weight_after >= 0.0

    def test_consolidation_weight_bounded_at_one(self):
        """Weight must never exceed 1.0."""
        link = L3ConsolidationLink(
            node_a="a1", node_b="t1",
            weight=0.99, avg_energy=100.0,
            node_a_type="actor", node_b_type="thing",
            usage_count=100,
        )
        result = l3_consolidate(link)
        assert link.weight <= 1.0

    def test_consolidation_diminishing_returns(self):
        """dW decreases as weight approaches 1.0 (due to (1-weight) term)."""
        link_low = L3ConsolidationLink(
            node_a="a1", node_b="t1",
            weight=0.1, avg_energy=5.0,
            node_a_type="actor", node_b_type="thing",
            usage_count=50,
        )
        link_high = L3ConsolidationLink(
            node_a="a2", node_b="t2",
            weight=0.9, avg_energy=5.0,
            node_a_type="actor", node_b_type="thing",
            usage_count=50,
        )
        result_low = l3_consolidate(link_low)
        result_high = l3_consolidate(link_high)
        assert result_low.delta_weight > result_high.delta_weight

    def test_consolidation_batch(self):
        """Batch consolidation processes all links."""
        links = [
            L3ConsolidationLink(
                node_a=f"a{i}", node_b=f"t{i}",
                weight=0.1, avg_energy=3.0,
                node_a_type="actor", node_b_type="thing",
                usage_count=10 * (i + 1),
            )
            for i in range(5)
        ]
        results = l3_consolidate_batch(links)
        assert len(results) == 5
        for r in results:
            assert r.delta_weight >= 0

    def test_consolidation_formula_correctness(self):
        """Verify dW = ALPHA * avg_energy * U * (1 - weight) exactly."""
        link = L3ConsolidationLink(
            node_a="a1", node_b="t1",
            weight=0.5, avg_energy=4.0,
            node_a_type="actor", node_b_type="thing",
            usage_count=50,
        )
        U = compute_structural_utility(link)
        expected_dW = L3_CONSOLIDATION_ALPHA * 4.0 * U * (1.0 - 0.5)
        result = l3_consolidate(link)
        assert abs(result.delta_weight - expected_dW) < 1e-10


# =============================================================================
# L3 Macro-Crystallization
# =============================================================================

class TestL3MacroCrystallization:
    """Tests for ALG-3: macro-crystallization."""

    def _make_dense_cluster(self, n: int = 50, weight: float = 4.0):
        """Create a fully connected cluster of n nodes."""
        nodes = []
        links = []
        for i in range(n):
            nodes.append(ClusterNode(
                id=f"node_{i}",
                node_type="moment",
                name=f"Moment {i}",
                synthesis=f"Summary of moment {i}",
                embedding=[float(i % 10) / 10] * 8,
                weight=1.0,
                energy=0.5,
            ))

        # Fully connect
        for i in range(n):
            for j in range(i + 1, n):
                links.append(ClusterLink(
                    node_a=f"node_{i}",
                    node_b=f"node_{j}",
                    weight=weight,
                ))

        return nodes, links

    def test_detect_candidates_dense_cluster(self):
        """A fully connected cluster of 50+ nodes with high weight should be detected."""
        nodes, links = self._make_dense_cluster(50, 4.0)
        candidates = detect_crystallization_candidates(nodes, links)
        assert len(candidates) == 1
        assert len(candidates[0].node_ids) == 50
        assert candidates[0].density > L3_CRYSTALLIZATION_DENSITY
        assert candidates[0].avg_co_activation >= L3_CRYSTALLIZATION_WEIGHT

    def test_detect_no_candidates_small_cluster(self):
        """Cluster below min_size should not be detected."""
        nodes, links = self._make_dense_cluster(10, 4.0)
        candidates = detect_crystallization_candidates(nodes, links)
        assert len(candidates) == 0

    def test_detect_no_candidates_low_weight(self):
        """Cluster with low average weight should not be detected."""
        nodes, links = self._make_dense_cluster(50, 1.0)
        candidates = detect_crystallization_candidates(nodes, links)
        assert len(candidates) == 0

    def test_detect_no_candidates_sparse(self):
        """Sparse cluster (few links) should not be detected."""
        nodes = [
            ClusterNode(id=f"node_{i}", node_type="moment", embedding=[0.1] * 8)
            for i in range(50)
        ]
        # Only connect each node to its immediate neighbor (chain)
        links = [
            ClusterLink(node_a=f"node_{i}", node_b=f"node_{i+1}", weight=4.0)
            for i in range(49)
        ]
        candidates = detect_crystallization_candidates(nodes, links)
        assert len(candidates) == 0

    def test_crystallize_hub_type_moments_become_narrative(self):
        """Cluster of moments should produce a narrative hub."""
        nodes, links = self._make_dense_cluster(50, 4.0)
        candidate = detect_crystallization_candidates(nodes, links)[0]
        hub = crystallize(candidate, "hub_001")
        assert hub.hub_type == "narrative"

    def test_crystallize_hub_weight_damped(self):
        """Hub weight = sum(constituent weights) * damping_factor."""
        nodes, links = self._make_dense_cluster(50, 4.0)
        candidate = detect_crystallization_candidates(nodes, links)[0]
        hub = crystallize(candidate, "hub_002")

        expected_weight = sum(n.weight for n in nodes) * L3_CRYSTALLIZATION_DAMPING_FACTOR
        assert abs(hub.hub_weight - expected_weight) < 1e-10

    def test_crystallize_preserves_weight(self):
        """Validate weight preservation invariant."""
        nodes, links = self._make_dense_cluster(50, 4.0)
        candidate = detect_crystallization_candidates(nodes, links)[0]
        hub = crystallize(candidate, "hub_003")
        assert validate_crystallization_preserves_weight(hub)

    def test_crystallize_bidirectional_links(self):
        """Hub has contains + abstracts links for each constituent."""
        nodes, links = self._make_dense_cluster(50, 4.0)
        candidate = detect_crystallization_candidates(nodes, links)[0]
        hub = crystallize(candidate, "hub_004")
        assert len(hub.contains_links) == 50
        assert len(hub.abstracts_links) == 50

    def test_crystallize_contains_link_weight(self):
        """Contains links have weight = constituent.weight * 0.5."""
        nodes, links = self._make_dense_cluster(50, 4.0)
        candidate = detect_crystallization_candidates(nodes, links)[0]
        hub = crystallize(candidate, "hub_005")
        for hub_id, constituent_id, weight in hub.contains_links:
            assert hub_id == "hub_005"
            assert weight == 1.0 * 0.5  # All nodes have weight=1.0

    def test_crystallize_abstracts_link_weight(self):
        """Abstracts links have weight = constituent.weight * 0.3."""
        nodes, links = self._make_dense_cluster(50, 4.0)
        candidate = detect_crystallization_candidates(nodes, links)[0]
        hub = crystallize(candidate, "hub_006")
        for constituent_id, hub_id, weight in hub.abstracts_links:
            assert hub_id == "hub_006"
            assert weight == 1.0 * 0.3

    def test_crystallize_hub_embedding_is_centroid(self):
        """Hub embedding should be the mean of constituent embeddings."""
        nodes, links = self._make_dense_cluster(50, 4.0)
        candidate = detect_crystallization_candidates(nodes, links)[0]
        hub = crystallize(candidate, "hub_007")

        # Compute expected centroid
        embeddings = [n.embedding for n in nodes if n.embedding]
        dim = len(embeddings[0])
        expected = [sum(e[d] for e in embeddings) / len(embeddings) for d in range(dim)]

        assert hub.hub_embedding is not None
        for a, b in zip(hub.hub_embedding, expected):
            assert abs(a - b) < 1e-10

    def test_crystallize_hub_stability(self):
        """Hub starts with stability = 0.8."""
        nodes, links = self._make_dense_cluster(50, 4.0)
        candidate = detect_crystallization_candidates(nodes, links)[0]
        hub = crystallize(candidate, "hub_008")
        assert hub.hub_stability == 0.8

    def test_crystallize_empty_cluster_raises(self):
        """Crystallizing an empty cluster must raise ValueError."""
        candidate = CrystallizationCandidate(
            node_ids=[], density=0.5, avg_co_activation=4.0,
            internal_link_count=0, external_links=[], nodes=[], internal_links=[],
        )
        with pytest.raises(ValueError):
            crystallize(candidate, "hub_err")

    def test_crystallize_with_external_links(self):
        """External links should be inherited by the hub."""
        nodes, links = self._make_dense_cluster(50, 4.0)
        # Add an external node and link
        ext_node = ClusterNode(id="external_1", node_type="thing")
        ext_link = ClusterLink(
            node_a="node_0", node_b="external_1",
            weight=2.0, trust=0.5, affinity=0.3,
        )

        candidates = detect_crystallization_candidates(
            nodes + [ext_node], links + [ext_link]
        )
        assert len(candidates) == 1  # External node not in cluster

        hub = crystallize(candidates[0], "hub_ext")
        assert len(hub.external_links) >= 1
        ext_hub_link = hub.external_links[0]
        assert ext_hub_link[1] == "external_1"  # Connected to external
        assert abs(ext_hub_link[2] - 1.0) < 1e-10  # weight * 0.5
        assert abs(ext_hub_link[3] - 0.5) < 1e-10  # trust inherited
        assert abs(ext_hub_link[4] - 0.3) < 1e-10  # affinity inherited

    def test_two_separate_clusters(self):
        """Two disconnected dense clusters should produce two candidates."""
        n1, l1 = self._make_dense_cluster(50, 4.0)
        n2 = [
            ClusterNode(
                id=f"other_{i}", node_type="moment",
                embedding=[0.9] * 8, weight=1.0, energy=0.5,
            )
            for i in range(50)
        ]
        l2 = [
            ClusterLink(node_a=f"other_{i}", node_b=f"other_{j}", weight=4.0)
            for i in range(50) for j in range(i + 1, 50)
        ]

        candidates = detect_crystallization_candidates(n1 + n2, l1 + l2)
        assert len(candidates) == 2


# =============================================================================
# Integration: Energy + Consolidation + Crystallization
# =============================================================================

class TestL3PhysicsIntegration:
    """Integration tests for L3 physics pipeline."""

    def test_energy_inject_propagate_decay_cycle(self):
        """Full cycle: inject energy, propagate, decay -- energy decreases."""
        # Setup: moment linked to space and actor
        moment = L3Node(id="m1", energy=0.0)
        space = L3Node(id="s1", energy=0.0)
        actor = L3Node(id="a1", energy=0.0)
        space_link = L3Link(node_a="m1", node_b="s1", weight=1.0)
        actor_link = L3Link(node_a="m1", node_b="a1", weight=1.0)

        # Inject
        l3_inject_energy(moment, space_link, actor_link, [], 5.0)
        assert moment.energy == 5.0

        # Propagate
        outbound = [
            L3Link(node_a="m1", node_b="s1", weight=1.0),
            L3Link(node_a="m1", node_b="a1", weight=1.0),
        ]
        l3_propagate(moment, outbound, {"s1": space, "a1": actor})

        # Moment should be at threshold, neighbors got energy
        assert abs(moment.energy - L3_PROPAGATION_THRESHOLD) < 1e-10
        assert space.energy > 0
        assert actor.energy > 0

        # Decay all nodes
        total_before = moment.energy + space.energy + actor.energy
        for n in [moment, space, actor]:
            l3_decay(n)
        total_after = moment.energy + space.energy + actor.energy
        assert total_after < total_before

    def test_consolidation_after_activity(self):
        """Links with high energy usage should consolidate weight."""
        link = L3ConsolidationLink(
            node_a="a1", node_b="s1",
            weight=0.1, avg_energy=5.0,
            node_a_type="actor", node_b_type="space",
            presence_hours=20.0,
        )
        initial_weight = link.weight
        for _ in range(100):
            l3_consolidate(link)
        assert link.weight > initial_weight
        assert link.weight <= 1.0
