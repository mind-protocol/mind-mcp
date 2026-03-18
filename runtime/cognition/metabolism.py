"""
Metabolism — Per-Citizen Physics Parameterization

The sublayer below conscious (WM) and subconscious (graph physics).
Makes physics constants per-citizen, time-varying, and self-adjustable.

Three built-in properties:
  - Circadian rhythm: sinusoidal curve, default Paris time (UTC+1)
  - Circadian adaptation: peak_hour drifts toward actual activity center
  - Stimulus sensitivity: per-type gain multipliers (v0.2, stubbed)

Frequencies (Tonic at L4) are external modifiers applied on top.
First frequency: Circadian Shift (temporary timezone override).

Spec: docs/cognition/metabolism/ALGORITHM_Metabolism.md
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Optional


# =========================================================================
# Tonic — L4 dataclass for Frequencies (L2 market name)
# =========================================================================

@dataclass
class Tonic:
    """A frequency modifier applied to a citizen's metabolism.

    L2 name: Frequency. Each tonic has a branded name and modifies
    specific physics constants for a bounded duration.
    """
    name: str                               # branded name: "Circadian Shift LA"
    category: str                           # focusing | calming | expansive | structuring | energizing
    constant_overrides: dict[str, float]    # e.g. {"timezone_offset": -8.0}
    drive_profile: dict[str, float] = field(default_factory=dict)  # drive energy injection
    duration_ticks: int = 0                 # 0 = permanent until removed
    cooldown_ticks: int = 0                 # min ticks before reapplication
    applied_at_tick: int = 0                # tick when applied
    ticks_elapsed: int = 0                  # ticks since application


@dataclass
class TonicEvent:
    """Audit log entry for tonic application/expiry."""
    tonic_name: str
    action: str          # "applied" | "expired" | "removed"
    tick: int
    timestamp: float
    details: dict = field(default_factory=dict)


# =========================================================================
# Activity Record — for circadian adaptation
# =========================================================================

@dataclass
class ActivityRecord:
    """A single activity observation for circadian adaptation."""
    hour_of_day: float   # 0.0 - 23.99 in citizen's local time
    energy: float        # how much energy was in this activity
    timestamp: float     # epoch seconds


# =========================================================================
# CitizenMetabolism — the per-citizen parameter overlay
# =========================================================================

# Paris timezone offset (CET = UTC+1, CEST = UTC+2)
DEFAULT_TIMEZONE_OFFSET = 1.0
DEFAULT_PEAK_HOUR = 14.0        # 2PM local time
ADAPTATION_RATE = 0.1           # hours of drift per day (slow, like jet lag)
ACTIVITY_WINDOW_DAYS = 7        # days of activity to consider for adaptation
MIN_ACTIVITY_RECORDS = 10       # minimum records before adaptation kicks in


@dataclass
class CitizenMetabolism:
    """Per-citizen physics parameterization.

    The metabolism sits between global constants and the tick runner.
    It resolves to effective constants per tick based on:
    - Circadian rhythm (time of day in citizen's timezone)
    - Active tonics (temporary modifiers)
    - Stimulus sensitivity (per-type gain, v0.2)
    """

    # ── Circadian properties (always active) ──
    timezone_offset: float = DEFAULT_TIMEZONE_OFFSET    # hours from UTC (Paris default)
    peak_hour: float = DEFAULT_PEAK_HOUR                # hour of peak activity (adapts)

    # ── Circadian adaptation ──
    activity_log: list[ActivityRecord] = field(default_factory=list)
    last_adaptation_tick: int = 0

    # ── Active tonics (frequencies) ──
    active_tonics: list[Tonic] = field(default_factory=list)

    # ── Stimulus sensitivity (v0.2 stub) ──
    sensitivity: dict[str, float] = field(default_factory=dict)

    # ── Audit log ──
    tonic_log: list[TonicEvent] = field(default_factory=list)

    # ── Computed (cached per tick) ──
    _cached_phase: float = 0.5
    _cached_tick: int = -1

    # ------------------------------------------------------------------
    # Circadian rhythm
    # ------------------------------------------------------------------

    def circadian_phase(self, now: Optional[float] = None) -> float:
        """Compute circadian phase [0, 1] where 1 = peak, 0 = trough.

        Sinusoidal curve with peak at self.peak_hour and trough 12h later.
        Uses the citizen's timezone_offset (or tonic override if active).

        Returns a value between 0.0 (deepest rest) and 1.0 (peak alertness).
        """
        if now is None:
            now = time.time()

        # Effective timezone (may be shifted by a tonic)
        tz = self._effective_timezone()

        # Local hour as float (0.0 - 23.99)
        utc_hour = (now % 86400) / 3600.0
        local_hour = (utc_hour + tz) % 24.0

        # Sinusoidal: peak at peak_hour, trough at peak_hour + 12
        # phase = 0.5 + 0.5 * cos(2pi * (local_hour - peak_hour) / 24)
        angle = 2.0 * math.pi * (local_hour - self.peak_hour) / 24.0
        phase = 0.5 + 0.5 * math.cos(angle)

        return phase

    def circadian_multipliers(self, now: Optional[float] = None) -> dict[str, float]:
        """Compute per-constant multipliers from the circadian phase.

        At peak (phase=1.0): normal operation (multiplier=1.0)
        At trough (phase=0.0): rest mode

        Returns dict of {constant_name: multiplier}.
        """
        phase = self.circadian_phase(now)

        # Decay: faster at night (2x at trough, 1x at peak)
        decay_mult = 2.0 - phase          # 1.0 at peak, 2.0 at trough

        # Consolidation: deeper at night (3x at trough, 1x at peak)
        consol_mult = 3.0 - 2.0 * phase   # 1.0 at peak, 3.0 at trough

        # Activation threshold: higher at night (harder to wake)
        activation_mult = 1.5 - 0.5 * phase  # 1.0 at peak, 1.5 at trough

        # Energy injection: reduced at night
        injection_mult = 0.5 + 0.5 * phase    # 0.5 at trough, 1.0 at peak

        return {
            "DECAY_RATE": decay_mult,
            "LONG_TERM_DECAY": decay_mult,
            "CONSOLIDATION_ALPHA": consol_mult,
            "ACTIVATION_THRESHOLD": activation_mult,
            "energy_injection_scale": injection_mult,
        }

    # ------------------------------------------------------------------
    # Circadian adaptation
    # ------------------------------------------------------------------

    def record_activity(self, energy: float, now: Optional[float] = None) -> None:
        """Record a stimulus/activity for circadian adaptation.

        Called by the tick runner when a stimulus arrives.
        """
        if now is None:
            now = time.time()

        tz = self._effective_timezone()
        utc_hour = (now % 86400) / 3600.0
        local_hour = (utc_hour + tz) % 24.0

        self.activity_log.append(ActivityRecord(
            hour_of_day=local_hour,
            energy=energy,
            timestamp=now,
        ))

        # Prune old records (keep last ACTIVITY_WINDOW_DAYS)
        cutoff = now - (ACTIVITY_WINDOW_DAYS * 86400)
        self.activity_log = [r for r in self.activity_log if r.timestamp > cutoff]

    def adapt_circadian(self, current_tick: int) -> None:
        """Drift peak_hour toward the energy-weighted center of activity.

        Called periodically (every ~100 ticks). The peak drifts slowly
        toward where the citizen is actually most active — like natural
        jet lag recovery.
        """
        if len(self.activity_log) < MIN_ACTIVITY_RECORDS:
            return

        # Energy-weighted circular mean of activity hours
        # (circular because 23:00 and 01:00 are close)
        sin_sum = 0.0
        cos_sum = 0.0
        weight_sum = 0.0

        for record in self.activity_log:
            angle = 2.0 * math.pi * record.hour_of_day / 24.0
            w = record.energy
            sin_sum += w * math.sin(angle)
            cos_sum += w * math.cos(angle)
            weight_sum += w

        if weight_sum < 0.001:
            return

        mean_angle = math.atan2(sin_sum / weight_sum, cos_sum / weight_sum)
        activity_center = (mean_angle * 24.0 / (2.0 * math.pi)) % 24.0

        # The peak should be at the activity center
        # Drift slowly toward it
        diff = activity_center - self.peak_hour
        # Handle circular wrapping
        if diff > 12.0:
            diff -= 24.0
        elif diff < -12.0:
            diff += 24.0

        # Drift rate: ADAPTATION_RATE hours per adaptation call
        # (called every ~100 ticks at 60s/tick = ~100 min)
        drift = max(-ADAPTATION_RATE, min(ADAPTATION_RATE, diff))
        self.peak_hour = (self.peak_hour + drift) % 24.0
        self.last_adaptation_tick = current_tick

    # ------------------------------------------------------------------
    # Tonic management
    # ------------------------------------------------------------------

    def apply_tonic(self, tonic: Tonic, current_tick: int) -> bool:
        """Apply a frequency (tonic) to this metabolism.

        Returns True if applied, False if on cooldown.
        """
        # Check cooldown
        for event in reversed(self.tonic_log):
            if event.tonic_name == tonic.name and event.action == "expired":
                ticks_since = current_tick - event.tick
                if ticks_since < tonic.cooldown_ticks:
                    return False

        tonic.applied_at_tick = current_tick
        tonic.ticks_elapsed = 0
        self.active_tonics.append(tonic)

        self.tonic_log.append(TonicEvent(
            tonic_name=tonic.name,
            action="applied",
            tick=current_tick,
            timestamp=time.time(),
            details={"overrides": tonic.constant_overrides},
        ))
        return True

    def tick_tonics(self, current_tick: int) -> list[str]:
        """Advance all active tonics by one tick. Remove expired ones.

        Returns list of expired tonic names.
        """
        expired = []
        surviving = []

        for tonic in self.active_tonics:
            tonic.ticks_elapsed += 1
            if tonic.duration_ticks > 0 and tonic.ticks_elapsed >= tonic.duration_ticks:
                expired.append(tonic.name)
                self.tonic_log.append(TonicEvent(
                    tonic_name=tonic.name,
                    action="expired",
                    tick=current_tick,
                    timestamp=time.time(),
                ))
            else:
                surviving.append(tonic)

        self.active_tonics = surviving
        return expired

    # ------------------------------------------------------------------
    # Effective constants resolution
    # ------------------------------------------------------------------

    def resolve_effective_constants(self, now: Optional[float] = None) -> dict[str, float]:
        """Resolve all metabolic modifiers into a flat dict of constant multipliers.

        Composition order:
        1. Circadian multipliers (base modulation)
        2. Tonic overrides (multiplicative on top)
        3. Clamp to safe ranges

        Returns {constant_name: multiplier} — the tick runner multiplies
        the global constant by this value.
        """
        # 1. Circadian base
        effective = self.circadian_multipliers(now)

        # 2. Tonic overrides (multiplicative)
        for tonic in self.active_tonics:
            for key, value in tonic.constant_overrides.items():
                if key in effective:
                    effective[key] *= value
                else:
                    effective[key] = value

        # 3. Clamp to safe ranges
        _CLAMP = {
            "DECAY_RATE": (0.5, 4.0),
            "LONG_TERM_DECAY": (0.5, 4.0),
            "CONSOLIDATION_ALPHA": (0.5, 5.0),
            "ACTIVATION_THRESHOLD": (0.5, 3.0),
            "energy_injection_scale": (0.1, 2.0),
        }
        for key, (lo, hi) in _CLAMP.items():
            if key in effective:
                effective[key] = max(lo, min(hi, effective[key]))

        return effective

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _effective_timezone(self) -> float:
        """Get effective timezone, considering active Circadian Shift tonics."""
        tz = self.timezone_offset
        for tonic in self.active_tonics:
            if "timezone_offset" in tonic.constant_overrides:
                tz = tonic.constant_overrides["timezone_offset"]
        return tz


# =========================================================================
# Circadian Shift — the first Frequency
# =========================================================================

def create_circadian_shift(target_timezone: float, duration_ticks: int = 500) -> Tonic:
    """Create a Circadian Shift frequency.

    Temporarily shifts the citizen's circadian rhythm to a different timezone.
    Example: create_circadian_shift(-8.0) → shift to LA time (PST).

    Args:
        target_timezone: UTC offset in hours (e.g., -8 for LA, 9 for Tokyo)
        duration_ticks: how long the shift lasts (default 500 ticks ~= 8h at 60s/tick)
    """
    return Tonic(
        name=f"Circadian Shift UTC{target_timezone:+.0f}",
        category="calming",
        constant_overrides={"timezone_offset": target_timezone},
        duration_ticks=duration_ticks,
        cooldown_ticks=100,  # ~100 min cooldown between shifts
    )
