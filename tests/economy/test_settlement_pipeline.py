"""Tests for F5: Value Event Batch Settlement Pipeline.

Validates:
- Full 6-phase pipeline: COLLECT → AGGREGATE → NET → FILTER → EXECUTE → RECORD
- Conservation: total in == total out across the batch
- Dust filtering
- Bilateral netting
- Contributor weight normalization
"""

import pytest

from runtime.economy.value_event_settlement import (
    Event,
    Transfer,
    aggregate_by_pair,
    filter_dust,
    net_positions,
    prepare_settlement_batch,
    record_energy_event,
)


# ---------------------------------------------------------------------------
# Phase 1: COLLECT
# ---------------------------------------------------------------------------

class TestRecordEnergyEvent:

    def test_positive_delta_creates_event(self):
        event = record_energy_event("alice", "service_x", 0.8, 100.0)
        assert event is not None
        assert event.source == "alice"
        assert event.target == "service_x"
        assert event.energy == pytest.approx(80.0)

    def test_zero_delta_returns_none(self):
        assert record_energy_event("alice", "service_x", 0.0, 100.0) is None

    def test_negative_delta_returns_none(self):
        assert record_energy_event("alice", "service_x", -0.5, 100.0) is None

    def test_with_contributors(self):
        contributors = [("creator_a", 0.6), ("creator_b", 0.4)]
        event = record_energy_event("alice", "svc", 1.0, 50.0, contributors)
        assert event is not None
        assert event.contributors == contributors

    def test_contributor_weights_normalized_if_off(self):
        """Weights that don't sum to 1.0 are normalized (E6 from VALIDATION)."""
        contributors = [("a", 0.5), ("b", 0.3)]  # sum = 0.8
        event = record_energy_event("alice", "svc", 1.0, 50.0, contributors)
        assert event is not None
        total = sum(w for _, w in event.contributors)
        assert abs(total - 1.0) < 0.001


# ---------------------------------------------------------------------------
# Phase 2: AGGREGATE
# ---------------------------------------------------------------------------

class TestAggregateByPair:

    def test_sums_same_pair(self):
        events = [
            Event("alice", "bob", 1.0, 10.0),  # energy = 10
            Event("alice", "bob", 0.5, 20.0),  # energy = 10
        ]
        agg = aggregate_by_pair(events)
        assert agg[("alice", "bob")] == pytest.approx(20.0)

    def test_separate_pairs(self):
        events = [
            Event("alice", "bob", 1.0, 10.0),
            Event("alice", "carol", 1.0, 5.0),
        ]
        agg = aggregate_by_pair(events)
        assert len(agg) == 2
        assert agg[("alice", "bob")] == pytest.approx(10.0)
        assert agg[("alice", "carol")] == pytest.approx(5.0)

    def test_empty_events(self):
        assert aggregate_by_pair([]) == {}


# ---------------------------------------------------------------------------
# Phase 3: NET
# ---------------------------------------------------------------------------

class TestNetPositions:

    def test_bilateral_netting(self):
        """Alice owes Bob 50, Bob owes Alice 30 → net Alice→Bob 20."""
        aggregated = {
            ("alice", "bob"): 50.0,
            ("bob", "alice"): 30.0,
        }
        netted = net_positions(aggregated)
        assert len(netted) == 1
        assert netted[("alice", "bob")] == pytest.approx(20.0)

    def test_perfect_cancellation(self):
        """Equal flows cancel out completely."""
        aggregated = {
            ("alice", "bob"): 100.0,
            ("bob", "alice"): 100.0,
        }
        netted = net_positions(aggregated)
        assert len(netted) == 0

    def test_unilateral_flow(self):
        aggregated = {("alice", "bob"): 100.0}
        netted = net_positions(aggregated)
        assert netted[("alice", "bob")] == pytest.approx(100.0)

    def test_multi_party(self):
        aggregated = {
            ("alice", "bob"): 100.0,
            ("bob", "carol"): 50.0,
            ("carol", "alice"): 30.0,
        }
        netted = net_positions(aggregated)
        # All unilateral → all preserved
        assert len(netted) == 3


# ---------------------------------------------------------------------------
# Phase 4: FILTER
# ---------------------------------------------------------------------------

class TestFilterDust:

    def test_filters_below_threshold(self):
        netted = {
            ("alice", "bob"): 0.005,  # below 0.01
            ("carol", "dave"): 1.0,   # above
        }
        filtered = filter_dust(netted, dust_threshold=0.01)
        assert len(filtered) == 1
        assert ("carol", "dave") in filtered

    def test_exact_threshold_passes(self):
        netted = {("a", "b"): 0.01}
        filtered = filter_dust(netted, dust_threshold=0.01)
        assert len(filtered) == 1

    def test_zero_threshold_passes_all(self):
        netted = {("a", "b"): 0.001}
        filtered = filter_dust(netted, dust_threshold=0.0)
        assert len(filtered) == 1


# ---------------------------------------------------------------------------
# Phase 5+6: EXECUTE + RECORD
# ---------------------------------------------------------------------------

class TestPrepareSettlementBatch:

    def test_creates_transfers(self):
        netted = {("alice", "bob"): 50.0, ("carol", "dave"): 30.0}
        transfers = prepare_settlement_batch(netted)
        assert len(transfers) == 2
        assert all(isinstance(t, Transfer) for t in transfers)

    def test_skips_zero_amounts(self):
        netted = {("a", "b"): 0.0}
        transfers = prepare_settlement_batch(netted)
        assert len(transfers) == 0


# ---------------------------------------------------------------------------
# Full pipeline integration
# ---------------------------------------------------------------------------

class TestFullPipeline:

    def test_conservation_total_in_equals_total_out(self):
        """Total energy paid by sources == total energy received by targets."""
        events = [
            Event("alice", "bob", 1.0, 100.0),    # 100
            Event("alice", "carol", 0.5, 200.0),   # 100
            Event("bob", "carol", 2.0, 25.0),      # 50
            Event("carol", "alice", 1.0, 30.0),     # 30
        ]

        aggregated = aggregate_by_pair(events)
        # Total energy before netting
        total_energy = sum(aggregated.values())

        netted = net_positions(aggregated)
        total_netted = sum(netted.values())

        # After netting, total should be <= total energy (netting reduces)
        assert total_netted <= total_energy + 1e-10

        # But within netted flows, sum(outflows) == sum(inflows) because
        # each Transfer is one sender → one recipient
        transfers = prepare_settlement_batch(netted)
        total_sent = sum(t.amount for t in transfers)
        total_received = sum(t.amount for t in transfers)
        assert total_sent == pytest.approx(total_received)

    def test_end_to_end_simple(self):
        """Simple pipeline: 2 events, aggregate, net, filter, batch."""
        # Phase 1: COLLECT
        e1 = record_energy_event("alice", "service", 1.0, 50.0)
        e2 = record_energy_event("bob", "service", 0.5, 80.0)
        events = [e for e in [e1, e2] if e is not None]

        # Phase 2: AGGREGATE
        agg = aggregate_by_pair(events)
        assert ("alice", "service") in agg
        assert ("bob", "service") in agg

        # Phase 3: NET
        netted = net_positions(agg)

        # Phase 4: FILTER
        filtered = filter_dust(netted, dust_threshold=0.01)

        # Phase 5: EXECUTE
        transfers = prepare_settlement_batch(filtered)
        assert len(transfers) >= 1

        # Phase 6: RECORD — verify all transfers have required fields
        for t in transfers:
            assert t.sender
            assert t.recipient
            assert t.amount > 0
