"""Tests for F2: Progressive Demurrage Tax.

Validates:
- Tax is always non-negative (I2)
- Tax never exceeds balance (I3 / V2)
- Tax is progressive (higher wealth → higher effective rate)
- Edge cases: zero wealth, extreme wealth
"""

import math
import pytest

from runtime.economy.progressive_demurrage_tax import compute_daily_tax


# ---------------------------------------------------------------------------
# Basic correctness
# ---------------------------------------------------------------------------

class TestBasicTax:
    """Verify formula against known values from ALGORITHM doc."""

    def test_small_balance(self):
        """W=1, tau=0.001: T = 1 * 0.001 * log10(2) ≈ 0.000301."""
        tax = compute_daily_tax(1.0, tau_base=0.001)
        expected = 1.0 * 0.001 * math.log10(2.0)
        assert abs(tax - expected) < 1e-10

    def test_large_balance(self):
        """W=1,000,000: T ≈ 1,000,000 * 0.001 * 6.0 = 6,000."""
        tax = compute_daily_tax(1_000_000.0, tau_base=0.001)
        expected = 1_000_000.0 * 0.001 * math.log10(1_000_001.0)
        assert abs(tax - expected) < 1e-6


# ---------------------------------------------------------------------------
# Invariant I2: Tax is non-negative
# ---------------------------------------------------------------------------

class TestTaxNonNegativity:
    """Invariant I2: T_i >= 0."""

    @pytest.mark.parametrize("w", [0.0, 0.001, 1.0, 100.0, 1e6, 1e12])
    def test_always_non_negative(self, w):
        tax = compute_daily_tax(w, tau_base=0.001)
        assert tax >= 0


# ---------------------------------------------------------------------------
# Invariant I3 / V2: Tax never exceeds balance
# ---------------------------------------------------------------------------

class TestTaxNeverExceedsBalance:
    """Invariant I3: T_i <= W_total_i."""

    @pytest.mark.parametrize("w", [0.0, 0.001, 1.0, 100.0, 1e6, 1e12, 1e20])
    def test_bounded_by_balance(self, w):
        tax = compute_daily_tax(w, tau_base=0.001)
        assert tax <= w + 1e-12  # small tolerance for floating-point

    def test_extreme_tau_base_still_bounded(self):
        """Even with a ridiculously high tau_base, guard kicks in."""
        tax = compute_daily_tax(100.0, tau_base=0.9)
        assert tax <= 100.0


# ---------------------------------------------------------------------------
# Progressive property
# ---------------------------------------------------------------------------

class TestProgressiveTax:
    """Effective rate increases with wealth."""

    def test_effective_rate_increases(self):
        """Higher wealth → higher effective daily rate."""
        wealths = [10.0, 100.0, 1_000.0, 10_000.0, 100_000.0, 1_000_000.0]
        rates = []
        for w in wealths:
            tax = compute_daily_tax(w, tau_base=0.001)
            rates.append(tax / w)

        for i in range(len(rates) - 1):
            assert rates[i] < rates[i + 1], (
                f"Rate should increase: W={wealths[i]} → r={rates[i]:.6f}, "
                f"W={wealths[i+1]} → r={rates[i+1]:.6f}"
            )

    def test_effective_rate_matches_formula(self):
        """r_eff = tau_base * log10(1 + W)."""
        for w in [10.0, 100.0, 1000.0]:
            tax = compute_daily_tax(w, tau_base=0.001)
            expected_rate = 0.001 * math.log10(1 + w)
            actual_rate = tax / w
            assert abs(actual_rate - expected_rate) < 1e-10


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestTaxEdgeCases:

    def test_zero_wealth(self):
        """W=0 → T=0."""
        assert compute_daily_tax(0.0) == 0.0

    def test_negative_wealth_raises(self):
        with pytest.raises(ValueError, match="w_total"):
            compute_daily_tax(-1.0)

    def test_non_positive_tau_raises(self):
        with pytest.raises(ValueError, match="tau_base"):
            compute_daily_tax(100.0, tau_base=0.0)
        with pytest.raises(ValueError, match="tau_base"):
            compute_daily_tax(100.0, tau_base=-0.001)

    def test_default_tau_base(self):
        """Default tau_base is 0.001."""
        tax_explicit = compute_daily_tax(1000.0, tau_base=0.001)
        tax_default = compute_daily_tax(1000.0)
        assert tax_explicit == tax_default
