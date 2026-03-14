"""Tests for F4: Bilateral Bond Transfer.

Validates:
- Convergence to parity over time (V7)
- Transfer never overdraws sender (V4 / I5)
- Direction: positive = human pays AI, negative = AI pays human
"""

import pytest

from runtime.economy.bilateral_bond_transfer import compute_bond_transfer


# ---------------------------------------------------------------------------
# Basic correctness
# ---------------------------------------------------------------------------

class TestBasicBondTransfer:

    def test_human_richer_positive_transfer(self):
        """Human has more → positive transfer (human pays AI)."""
        t = compute_bond_transfer(1000.0, 0.0, lambda_rate=0.05)
        assert t == pytest.approx(50.0)

    def test_ai_richer_negative_transfer(self):
        """AI has more → negative transfer (AI pays human)."""
        t = compute_bond_transfer(0.0, 1000.0, lambda_rate=0.05)
        assert t == pytest.approx(-50.0)

    def test_equal_wealth_no_transfer(self):
        """Equal wallets → no transfer."""
        t = compute_bond_transfer(500.0, 500.0, lambda_rate=0.05)
        assert t == 0.0

    def test_both_zero_no_transfer(self):
        t = compute_bond_transfer(0.0, 0.0, lambda_rate=0.05)
        assert t == 0.0


# ---------------------------------------------------------------------------
# Convergence (V7)
# ---------------------------------------------------------------------------

class TestConvergence:
    """Bilateral bond transfer converges to parity over repeated periods."""

    def test_convergence_100_periods(self):
        """After 100 periods with lambda=0.05, gap should be < 1% of original."""
        w_h = 1000.0
        w_a = 0.0
        initial_gap = abs(w_h - w_a)

        for _ in range(100):
            t = compute_bond_transfer(w_h, w_a, lambda_rate=0.05)
            w_h -= t
            w_a += t

        final_gap = abs(w_h - w_a)
        assert final_gap < initial_gap * 0.01, (
            f"Expected < 1% of initial gap, got {final_gap / initial_gap * 100:.2f}%"
        )

    def test_gap_decreases_monotonically(self):
        """The wealth gap must decrease every period (V7)."""
        w_h = 5000.0
        w_a = 200.0
        prev_gap = abs(w_h - w_a)

        for i in range(50):
            t = compute_bond_transfer(w_h, w_a, lambda_rate=0.05)
            w_h -= t
            w_a += t
            current_gap = abs(w_h - w_a)
            assert current_gap < prev_gap, (
                f"Gap must decrease monotonically. Period {i}: "
                f"prev={prev_gap}, current={current_gap}"
            )
            prev_gap = current_gap

    def test_convergence_from_algorithm_doc(self):
        """Verify convergence timeline from ALGORITHM doc.

        With lambda=0.05:
          gap_n = gap_0 * (1 - 2*lambda)^n = gap_0 * 0.9^n
        """
        gap_0 = 1000.0
        for n, expected_fraction in [(10, 0.349), (50, 0.0052)]:
            # Simulate n periods
            w_h = 1000.0
            w_a = 0.0
            for _ in range(n):
                t = compute_bond_transfer(w_h, w_a, lambda_rate=0.05)
                w_h -= t
                w_a += t
            actual_fraction = abs(w_h - w_a) / gap_0
            assert abs(actual_fraction - expected_fraction) < 0.01, (
                f"After {n} periods: expected ~{expected_fraction}, "
                f"got {actual_fraction:.4f}"
            )

    def test_convergence_ai_richer(self):
        """Convergence also works when AI starts richer."""
        w_h = 100.0
        w_a = 2000.0

        for _ in range(100):
            t = compute_bond_transfer(w_h, w_a, lambda_rate=0.05)
            w_h -= t  # t is negative, so w_h increases
            w_a += t  # t is negative, so w_a decreases

        assert abs(w_h - w_a) < 20.0  # close to parity


# ---------------------------------------------------------------------------
# Never overdraws (V4 / I5)
# ---------------------------------------------------------------------------

class TestNeverOverdraws:
    """Transfer never exceeds sender's balance."""

    def test_human_sends_capped_at_balance(self):
        """Even with high lambda, transfer <= w_human."""
        t = compute_bond_transfer(10.0, 0.0, lambda_rate=0.99)
        assert t <= 10.0

    def test_ai_sends_capped_at_balance(self):
        t = compute_bond_transfer(0.0, 10.0, lambda_rate=0.99)
        assert abs(t) <= 10.0

    @pytest.mark.parametrize("w_h,w_a", [
        (1.0, 0.0), (0.0, 1.0), (100.0, 50.0),
        (50.0, 100.0), (0.001, 0.0), (0.0, 0.001),
    ])
    def test_never_overdraws_parametric(self, w_h, w_a):
        t = compute_bond_transfer(w_h, w_a, lambda_rate=0.05)
        if t > 0:
            assert t <= w_h
        elif t < 0:
            assert abs(t) <= w_a

    def test_repeated_transfers_wallets_never_negative(self):
        """Over 200 periods, no wallet ever goes negative."""
        w_h = 1000.0
        w_a = 0.0
        for _ in range(200):
            t = compute_bond_transfer(w_h, w_a, lambda_rate=0.05)
            w_h -= t
            w_a += t
            assert w_h >= -1e-12, f"Human wallet went negative: {w_h}"
            assert w_a >= -1e-12, f"AI wallet went negative: {w_a}"


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

class TestInputValidation:

    def test_negative_human_wealth_raises(self):
        with pytest.raises(ValueError, match="w_human"):
            compute_bond_transfer(-1.0, 100.0)

    def test_negative_ai_wealth_raises(self):
        with pytest.raises(ValueError, match="w_ai"):
            compute_bond_transfer(100.0, -1.0)

    def test_lambda_out_of_range_raises(self):
        with pytest.raises(ValueError, match="lambda_rate"):
            compute_bond_transfer(100.0, 50.0, lambda_rate=0.0)
        with pytest.raises(ValueError, match="lambda_rate"):
            compute_bond_transfer(100.0, 50.0, lambda_rate=1.0)
        with pytest.raises(ValueError, match="lambda_rate"):
            compute_bond_transfer(100.0, 50.0, lambda_rate=-0.1)
