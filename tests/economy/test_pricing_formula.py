"""Tests for F1: Degressive Pricing Formula.

Validates:
- Price is always non-negative (I1)
- Price is degressive with utility (higher U_S → lower price)
- Price is progressive with wealth (higher W_i → higher price)
- Edge cases: zero median, zero wealth, zero utility, zero base cost
"""

import math
import pytest

from runtime.economy.degressive_pricing_formula import compute_price


# ---------------------------------------------------------------------------
# Basic correctness
# ---------------------------------------------------------------------------

class TestBasicPricing:
    """Verify the formula produces correct results against known examples."""

    def test_example_from_algorithm_doc(self):
        """ALGORITHM doc example: C_base=100, U_S=3.0, k=0.5, median user."""
        price = compute_price(
            c_base=100.0, k=0.5, utility_weight=3.0,
            actor_wealth=1000.0, median_wealth=1000.0,
        )
        expected = 100.0 * math.exp(-0.5 * 3.0) * 1.0
        assert abs(price - expected) < 1e-10

    def test_wealthy_user_pays_more(self):
        """ALGORITHM doc example: wealthy user (W_i/W_med = 5.0)."""
        price = compute_price(
            c_base=100.0, k=0.5, utility_weight=3.0,
            actor_wealth=5000.0, median_wealth=1000.0,
        )
        expected = 100.0 * math.exp(-1.5) * 5.0
        assert abs(price - expected) < 1e-10

    def test_poor_user_gets_floor(self):
        """ALGORITHM doc example: poor user hits A(i) floor at 0.1."""
        price = compute_price(
            c_base=100.0, k=0.5, utility_weight=3.0,
            actor_wealth=50.0, median_wealth=1000.0,
        )
        expected = 100.0 * math.exp(-1.5) * 0.1
        assert abs(price - expected) < 1e-10


# ---------------------------------------------------------------------------
# Invariant I1: Price is always non-negative
# ---------------------------------------------------------------------------

class TestPriceNonNegativity:
    """Invariant I1: P(i, S) >= 0 for all valid inputs."""

    @pytest.mark.parametrize("c_base", [0.0, 0.001, 1.0, 100.0, 1_000_000.0])
    @pytest.mark.parametrize("utility", [0.0, 0.1, 1.0, 10.0, 100.0])
    @pytest.mark.parametrize("wealth", [0.0, 0.01, 1.0, 100.0, 1_000_000.0])
    def test_always_non_negative(self, c_base, utility, wealth):
        price = compute_price(
            c_base=c_base, k=0.5, utility_weight=utility,
            actor_wealth=wealth, median_wealth=1000.0,
        )
        assert price >= 0


# ---------------------------------------------------------------------------
# Degressive property: higher utility → lower price
# ---------------------------------------------------------------------------

class TestDegressiveWithUtility:
    """Price decreases as service utility increases."""

    def test_monotonic_decrease_with_utility(self):
        utilities = [0.0, 1.0, 2.0, 5.0, 10.0, 50.0]
        prices = [
            compute_price(100.0, 0.5, u, 1000.0, 1000.0)
            for u in utilities
        ]
        for i in range(len(prices) - 1):
            assert prices[i] > prices[i + 1], (
                f"Price should decrease: U={utilities[i]} → P={prices[i]}, "
                f"U={utilities[i+1]} → P={prices[i+1]}"
            )

    def test_high_utility_approaches_zero(self):
        price = compute_price(100.0, 0.5, 100.0, 1000.0, 1000.0)
        assert price < 1e-10  # effectively zero


# ---------------------------------------------------------------------------
# Progressive property: higher wealth → higher price
# ---------------------------------------------------------------------------

class TestProgressiveWithWealth:
    """Wealthier users pay more."""

    def test_monotonic_increase_with_wealth(self):
        """Once above the floor (0.1 * median), price grows linearly."""
        wealths = [100.0, 500.0, 1000.0, 5000.0, 10_000.0]
        prices = [
            compute_price(100.0, 0.5, 1.0, w, 1000.0)
            for w in wealths
        ]
        for i in range(len(prices) - 1):
            assert prices[i] < prices[i + 1], (
                f"Wealthier should pay more: W={wealths[i]} → P={prices[i]}, "
                f"W={wealths[i+1]} → P={prices[i+1]}"
            )

    def test_floor_at_0_1(self):
        """Very poor users get A(i) = 0.1, not lower."""
        price_zero = compute_price(100.0, 0.5, 1.0, 0.0, 1000.0)
        price_tiny = compute_price(100.0, 0.5, 1.0, 1.0, 1000.0)
        # Both should use floor since 0/1000=0 and 1/1000=0.001, both < 0.1
        assert abs(price_zero - price_tiny) < 1e-10


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    """Edge cases documented in ALGORITHM §F1."""

    def test_zero_median_wealth_bootstrap(self):
        """W_med = 0 → bootstrap: A(i) = 1.0 for all users."""
        price = compute_price(100.0, 0.5, 1.0, 500.0, 0.0)
        expected = 100.0 * math.exp(-0.5) * 1.0
        assert abs(price - expected) < 1e-10

    def test_zero_actor_wealth(self):
        """W_i = 0 → A(i) = 0.1 (floor)."""
        price = compute_price(100.0, 0.5, 1.0, 0.0, 1000.0)
        expected = 100.0 * math.exp(-0.5) * 0.1
        assert abs(price - expected) < 1e-10

    def test_zero_utility(self):
        """U_S = 0 → D(S) = 1.0, no discount."""
        price = compute_price(100.0, 0.5, 0.0, 1000.0, 1000.0)
        expected = 100.0 * 1.0 * 1.0
        assert abs(price - expected) < 1e-10

    def test_zero_base_cost(self):
        """C_base = 0 → price is 0."""
        price = compute_price(0.0, 0.5, 5.0, 1000.0, 1000.0)
        assert price == 0.0

    def test_negative_c_base_raises(self):
        with pytest.raises(ValueError, match="c_base"):
            compute_price(-1.0, 0.5, 1.0, 100.0, 100.0)

    def test_negative_k_raises(self):
        with pytest.raises(ValueError, match="k"):
            compute_price(100.0, -0.5, 1.0, 100.0, 100.0)

    def test_negative_utility_raises(self):
        with pytest.raises(ValueError, match="utility_weight"):
            compute_price(100.0, 0.5, -1.0, 100.0, 100.0)

    def test_negative_wealth_raises(self):
        with pytest.raises(ValueError, match="actor_wealth"):
            compute_price(100.0, 0.5, 1.0, -100.0, 100.0)

    def test_negative_median_raises(self):
        with pytest.raises(ValueError, match="median_wealth"):
            compute_price(100.0, 0.5, 1.0, 100.0, -100.0)
