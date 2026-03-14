"""Tests for all 9 invariants from VALIDATION_Metabolic_Economy.md.

V1: Price MUST be non-negative for all users and services.
V2: Daily tax MUST be non-negative and MUST NOT exceed total wallet balance.
V3: Anti-sybil repatriation MUST NOT reduce wealth by more than SYBIL_PENALTY
    fraction of the off-grid amount.
V4: Bilateral bond transfer MUST NOT overdraw the sending partner's wallet.
V5: Total $MIND entering UBC pool = total tax + penalties + unclaimed + dust
    (conservation of value).
V6: Every $MIND transfer to a non-L4 address MUST be attributed to exactly
    one entity.
V7: Bilateral bond transfer MUST converge (gap decreases monotonically).
V8: Each batch settlement MUST be atomic — all or nothing.
V9: No wallet balance MUST ever be negative.
"""

import math
import pytest

from runtime.economy.anti_sybil_repatriation import (
    compute_repatriation,
    detect_off_grid,
)
from runtime.economy.bilateral_bond_transfer import compute_bond_transfer
from runtime.economy.degressive_pricing_formula import compute_price
from runtime.economy.progressive_demurrage_tax import compute_daily_tax
from runtime.economy.settlement_engine import SettlementEngine
from runtime.economy.value_event_settlement import (
    aggregate_by_pair,
    filter_dust,
    net_positions,
    prepare_settlement_batch,
    record_energy_event,
    Event,
)


# ---------------------------------------------------------------------------
# V1: Price is non-negative
# ---------------------------------------------------------------------------

class TestV1PriceNonNegative:

    @pytest.mark.parametrize("c_base,k,u,w_actor,w_med", [
        (0.0, 0.5, 0.0, 0.0, 0.0),
        (100.0, 0.5, 0.0, 0.0, 1000.0),
        (100.0, 0.5, 100.0, 1e6, 1000.0),
        (1e6, 10.0, 50.0, 0.0, 0.0),
        (0.001, 0.001, 0.001, 0.001, 0.001),
    ])
    def test_price_non_negative(self, c_base, k, u, w_actor, w_med):
        price = compute_price(c_base, k, u, w_actor, w_med)
        assert price >= 0, f"V1 violated: price={price}"


# ---------------------------------------------------------------------------
# V2: Tax non-negative AND never exceeds balance
# ---------------------------------------------------------------------------

class TestV2TaxBounded:

    @pytest.mark.parametrize("w", [0.0, 0.001, 1.0, 100.0, 1e6, 1e12, 1e20])
    def test_tax_non_negative_and_bounded(self, w):
        tax = compute_daily_tax(w, tau_base=0.001)
        assert tax >= 0, f"V2 violated (non-negative): tax={tax}"
        assert tax <= w + 1e-12, f"V2 violated (bounded): tax={tax}, W={w}"


# ---------------------------------------------------------------------------
# V3: Anti-sybil penalty bound
# ---------------------------------------------------------------------------

class TestV3SybilPenaltyBound:

    @pytest.mark.parametrize("amount", [0.0, 1.0, 100.0, 1e6])
    def test_repatriation_penalty_bound(self, amount):
        """Entity loses exactly SYBIL_PENALTY fraction."""
        penalty_rate = 0.05
        repatriated, penalty = compute_repatriation(amount, penalty_rate)

        # Conservation: repatriated + penalty == amount
        assert abs((repatriated + penalty) - amount) < 1e-10, (
            f"V3 conservation: {repatriated} + {penalty} != {amount}"
        )

        # Penalty is exactly penalty_rate * amount
        assert abs(penalty - amount * penalty_rate) < 1e-10, (
            f"V3 penalty bound: penalty={penalty}, "
            f"expected={amount * penalty_rate}"
        )

        # Entity retains exactly (1 - penalty_rate) * amount
        assert abs(repatriated - amount * (1 - penalty_rate)) < 1e-10


# ---------------------------------------------------------------------------
# V4: Bilateral transfer never overdraws sender
# ---------------------------------------------------------------------------

class TestV4NeverOverdraws:

    @pytest.mark.parametrize("w_h,w_a,lam", [
        (1000.0, 0.0, 0.05),
        (0.0, 1000.0, 0.05),
        (100.0, 50.0, 0.99),
        (50.0, 100.0, 0.99),
        (0.001, 0.0, 0.5),
        (0.0, 0.001, 0.5),
    ])
    def test_transfer_within_sender_balance(self, w_h, w_a, lam):
        t = compute_bond_transfer(w_h, w_a, lam)
        if t > 0:
            assert t <= w_h + 1e-12, f"V4 violated: t={t} > w_h={w_h}"
        elif t < 0:
            assert abs(t) <= w_a + 1e-12, f"V4 violated: |t|={abs(t)} > w_a={w_a}"


# ---------------------------------------------------------------------------
# V5: Conservation of value (UBC pool inflow = tax + penalties)
# ---------------------------------------------------------------------------

class TestV5Conservation:

    def test_macro_settlement_conservation(self):
        """Tax + penalties collected must equal UBC pool inflow."""
        engine = SettlementEngine(
            dust_threshold=0.001,
            tau_base=0.001,
            sybil_penalty_rate=0.05,
        )

        wallets = {"alice": 10_000.0, "bob": 5_000.0, "carol": 1_000.0}

        # Add some off-grid transfers
        outbound = [("alice", "offgrid_wallet_1", 500.0)]
        registered = {"alice_wallet", "bob_wallet", "carol_wallet"}

        receipt = engine.run_macro_settlement(
            wallets=wallets,
            outbound_transfers=outbound,
            registered_wallets=registered,
            citizen_ids=[],  # no citizens → no UBC distribution
        )

        # V5: UBC pool should have received exactly tax + penalties
        assert engine.ubc_pool == pytest.approx(
            receipt.tax_collected + receipt.penalties_collected
        )

        # Verify tax is sum of individual taxes
        expected_tax = sum(compute_daily_tax(w, 0.001) for w in wallets.values())
        assert receipt.tax_collected == pytest.approx(expected_tax)

        # Verify penalty is 5% of off-grid amount
        expected_penalty = 500.0 * 0.05
        assert receipt.penalties_collected == pytest.approx(expected_penalty)


# ---------------------------------------------------------------------------
# V6: Off-grid attribution completeness
# ---------------------------------------------------------------------------

class TestV6OffGridAttribution:

    def test_every_off_grid_transfer_attributed(self):
        """Every detected off-grid transfer has exactly one sender."""
        transfers = [
            ("alice", "unknown_1", 100.0),
            ("bob", "unknown_2", 200.0),
            ("alice", "unknown_3", 50.0),
        ]
        registered = {"known_wallet_1", "known_wallet_2"}

        off_grid = detect_off_grid(transfers, registered)

        # All 3 are off-grid
        assert len(off_grid) == 3

        # Each has exactly one attributed sender
        for sender, dest, amount in off_grid:
            assert sender is not None
            assert len(sender) > 0
            assert amount > 0

    def test_registered_wallets_excluded(self):
        """Transfers to registered wallets are NOT off-grid."""
        transfers = [
            ("alice", "known_wallet", 100.0),
            ("bob", "unknown_wallet", 200.0),
        ]
        registered = {"known_wallet"}

        off_grid = detect_off_grid(transfers, registered)
        assert len(off_grid) == 1
        assert off_grid[0][0] == "bob"


# ---------------------------------------------------------------------------
# V7: Bilateral convergence
# ---------------------------------------------------------------------------

class TestV7Convergence:

    def test_gap_decreases_monotonically(self):
        """Absent external income, gap MUST decrease every period."""
        w_h = 10_000.0
        w_a = 100.0
        prev_gap = abs(w_h - w_a)

        for i in range(100):
            t = compute_bond_transfer(w_h, w_a, 0.05)
            w_h -= t
            w_a += t
            gap = abs(w_h - w_a)
            assert gap < prev_gap + 1e-12, (
                f"V7 violated at period {i}: gap={gap} >= prev={prev_gap}"
            )
            prev_gap = gap


# ---------------------------------------------------------------------------
# V8: Settlement atomicity
# ---------------------------------------------------------------------------

class TestV8Atomicity:

    def test_settlement_produces_complete_batch(self):
        """All transfers in a batch are present; no partial state."""
        engine = SettlementEngine(dust_threshold=0.001)

        # Ingest several events
        for i in range(10):
            engine.ingest_event(f"user_{i}", "service", 1.0, 10.0)

        receipt = engine.run_micro_settlement()

        # All events processed
        assert receipt.events_processed == 10

        # Pending events cleared (atomic: all processed or none)
        assert len(engine.pending_events) == 0

        # Receipt is recorded
        assert len(engine.receipts) == 1
        assert engine.receipts[0] is receipt

    def test_failed_ingestion_does_not_corrupt_state(self):
        """Events with non-positive delta don't enter pending list."""
        engine = SettlementEngine()
        engine.ingest_event("alice", "svc", 1.0, 10.0)   # valid
        engine.ingest_event("bob", "svc", -0.5, 10.0)    # invalid
        engine.ingest_event("carol", "svc", 0.0, 10.0)   # invalid

        assert len(engine.pending_events) == 1
        assert engine.pending_events[0].source == "alice"


# ---------------------------------------------------------------------------
# V9: Wallet balance never negative
# ---------------------------------------------------------------------------

class TestV9WalletNonNegative:

    def test_tax_never_makes_wallet_negative(self):
        """Tax is min(T, W), so wallet after tax >= 0."""
        for w in [0.001, 1.0, 100.0, 1e6]:
            tax = compute_daily_tax(w, tau_base=0.001)
            remaining = w - tax
            assert remaining >= -1e-12, (
                f"V9 violated: W={w}, tax={tax}, remaining={remaining}"
            )

    def test_bilateral_transfer_never_makes_wallet_negative(self):
        """Over many periods, both wallets stay >= 0."""
        w_h = 1000.0
        w_a = 0.0
        for _ in range(500):
            t = compute_bond_transfer(w_h, w_a, 0.05)
            w_h -= t
            w_a += t
            assert w_h >= -1e-12, f"V9: human wallet negative: {w_h}"
            assert w_a >= -1e-12, f"V9: AI wallet negative: {w_a}"

    def test_repatriation_never_creates_negative(self):
        """Repatriation: repatriated >= 0, penalty >= 0."""
        for amount in [0.0, 0.001, 1.0, 1e6]:
            repatriated, penalty = compute_repatriation(amount, 0.05)
            assert repatriated >= 0, f"V9: repatriated negative: {repatriated}"
            assert penalty >= 0, f"V9: penalty negative: {penalty}"

    def test_settlement_engine_ubc_pool_never_negative(self):
        """UBC pool stays >= 0 after distribution."""
        engine = SettlementEngine(dust_threshold=0.001, tau_base=0.001)

        wallets = {"alice": 1000.0, "bob": 500.0}
        citizen_ids = ["citizen_1", "citizen_2"]

        receipt = engine.run_macro_settlement(
            wallets=wallets,
            citizen_ids=citizen_ids,
        )

        assert engine.ubc_pool >= 0, (
            f"V9/I7: UBC pool negative: {engine.ubc_pool}"
        )
