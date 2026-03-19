"""Silence Sentinel — Output-rate monitoring for silent failure detection.

Tracks the ratio of substantive outputs to attempted calls per flow.
When a flow's output drops below its self-calibrating baseline,
a stimulus is routed to the best available infra actor.

Docs: docs/orchestrator/silence_sentinel/

Usage (instrumentation — 1 line per call site):
    from runtime.orchestrator.silence_counter import record_attempt, record_success
    record_attempt("invoke_claude")
    ...
    if is_substantive(response):
        record_success("invoke_claude")

Usage (evaluation — called by dispatcher every tick):
    from runtime.orchestrator.silence_counter import evaluate_all
    results = evaluate_all(pressure, circadian_factor, inject_fn)
"""

import logging
import os
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Callable, Optional

logger = logging.getLogger("orchestrator.silence_sentinel")

# ── Configuration ─────────────────────────────────────────────────────────

WINDOW_SECONDS = int(os.environ.get("SILENCE_WINDOW_SECONDS", "300"))
CALIBRATION_MIN = int(os.environ.get("SILENCE_CALIBRATION_MIN", "5"))
BASELINE_MINUTES = int(os.environ.get("SILENCE_BASELINE_MINUTES", "60"))
RED_THRESHOLD = float(os.environ.get("SILENCE_RED_THRESHOLD", "0.5"))
YELLOW_THRESHOLD = float(os.environ.get("SILENCE_YELLOW_THRESHOLD", "0.8"))

# Suppress patterns — responses containing these are NOT substantive
SUPPRESS_PATTERNS = [
    "rate limit", "429", "quota", "credit balance", "out of",
    "overloaded", "capacity",
]


# ── Data Structures ───────────────────────────────────────────────────────

@dataclass
class Bucket:
    timestamp: int  # minute-aligned epoch
    attempted: int = 0
    substantive: int = 0


@dataclass
class FlowCounter:
    flow_name: str
    buckets: deque = field(default_factory=lambda: deque(maxlen=60))


@dataclass
class SentinelState:
    flow_name: str
    observations: int = 0
    rolling_baseline: float = 0.0
    last_ratio: Optional[float] = None
    last_status: str = "CALIBRATING"
    last_evaluated: float = 0.0
    last_stimulus_ts: float = 0.0  # debounce: don't spam stimuli


# ── Module State ──────────────────────────────────────────────────────────

_counters: dict[str, FlowCounter] = {}
_states: dict[str, SentinelState] = {}
_last_evaluate_ts: float = 0.0


# ── Counter API (fire-and-forget — MUST NOT raise) ────────────────────────

def record_attempt(flow_name: str) -> None:
    """Record that a flow attempted a call. Fire-and-forget."""
    try:
        bucket = _get_or_create_bucket(flow_name)
        bucket.attempted += 1
    except Exception:
        pass  # V2: counter calls NEVER propagate exceptions


def record_success(flow_name: str) -> None:
    """Record that a flow produced a substantive result. Fire-and-forget."""
    try:
        bucket = _get_or_create_bucket(flow_name)
        bucket.substantive += 1
    except Exception:
        pass  # V2: counter calls NEVER propagate exceptions


def _get_or_create_bucket(flow_name: str) -> Bucket:
    """Get or create the current minute's bucket for a flow."""
    if flow_name not in _counters:
        _counters[flow_name] = FlowCounter(flow_name=flow_name)
    counter = _counters[flow_name]
    now_minute = int(time.time()) // 60 * 60
    if not counter.buckets or counter.buckets[-1].timestamp != now_minute:
        counter.buckets.append(Bucket(timestamp=now_minute))
    return counter.buckets[-1]


# ── Substantive Classification ────────────────────────────────────────────

def is_invoke_substantive(response: str) -> bool:
    """Classify whether an invoke_claude response is substantive output.

    Rejects: empty, short, subconscious placeholders, rate limit errors.
    """
    if not response or len(response) < 100:
        return False
    if response.startswith("*[Subconscious response"):
        return False
    response_lower = response.lower()
    if any(p in response_lower for p in SUPPRESS_PATTERNS):
        return False
    return True


# ── Evaluation (called every tick by dispatcher) ──────────────────────────

def evaluate_all(
    pressure: float = 0.0,
    circadian_factor: float = 1.0,
    inject_fn: Optional[Callable] = None,
) -> dict[str, dict]:
    """Evaluate all tracked flows. Returns {flow_name: {status, ratio, baseline, sample}}.

    Args:
        pressure: current activation_pressure value
        circadian_factor: 1.0 = peak, 0.5 = trough
        inject_fn: callable(target, content, source, energy, is_failure) for stimulus routing
    """
    global _last_evaluate_ts
    _last_evaluate_ts = time.time()

    results = {}
    for flow_name in list(_counters.keys()):
        result = _evaluate_flow(flow_name, pressure, circadian_factor)
        results[flow_name] = result

        # Route stimulus if degraded
        if result["status"] in ("RED", "YELLOW") and inject_fn:
            _route_stimulus(flow_name, result, inject_fn)

    return results


def _evaluate_flow(
    flow_name: str, pressure: float, circadian_factor: float,
) -> dict:
    """Evaluate a single flow's output ratio against its baseline."""
    if flow_name not in _states:
        _states[flow_name] = SentinelState(flow_name=flow_name)
    state = _states[flow_name]
    state.observations += 1
    state.last_evaluated = time.time()

    ratio, sample = _compute_ratio(flow_name)

    # Calibration gate
    if state.observations <= CALIBRATION_MIN:
        if ratio is not None and ratio == 0.0 and sample >= 10:
            state.last_status = "RED"
            state.last_ratio = 0.0
            logger.warning(
                f"[sentinel] {flow_name}: RED during calibration "
                f"(ratio=0.0, sample={sample}) — complete silence"
            )
            return {"status": "RED", "ratio": 0.0, "baseline": None, "sample": sample}
        state.last_status = "CALIBRATING"
        return {"status": "CALIBRATING", "ratio": ratio, "baseline": None, "sample": sample}

    # No attempts
    if ratio is None:
        return {"status": state.last_status, "ratio": None, "baseline": state.rolling_baseline, "sample": 0}

    baseline = _compute_baseline(flow_name, pressure, circadian_factor)
    if baseline is None:
        state.last_status = "CALIBRATING"
        return {"status": "CALIBRATING", "ratio": ratio, "baseline": None, "sample": sample}

    state.rolling_baseline = baseline
    state.last_ratio = ratio

    # Evaluate against baseline
    if ratio >= baseline * YELLOW_THRESHOLD:
        status = "GREEN"
    elif ratio >= baseline * RED_THRESHOLD:
        status = "YELLOW"
    else:
        status = "RED"

    if status != state.last_status:
        logger.info(
            f"[sentinel] {flow_name}: {state.last_status} → {status} "
            f"(ratio={ratio:.2f}, baseline={baseline:.2f}, sample={sample})"
        )
    state.last_status = status

    return {"status": status, "ratio": round(ratio, 3), "baseline": round(baseline, 3), "sample": sample}


def _compute_ratio(flow_name: str, window_seconds: int = WINDOW_SECONDS) -> tuple[Optional[float], int]:
    """Compute the output ratio for a flow over the recent window."""
    counter = _counters.get(flow_name)
    if not counter or not counter.buckets:
        return None, 0

    cutoff = time.time() - window_seconds
    attempted = 0
    substantive = 0
    for bucket in counter.buckets:
        if bucket.timestamp >= cutoff:
            attempted += bucket.attempted
            substantive += bucket.substantive

    if attempted == 0:
        return None, 0
    return substantive / attempted, attempted


def _compute_baseline(
    flow_name: str, pressure: float, circadian_factor: float,
) -> Optional[float]:
    """Compute the self-calibrating rolling baseline for a flow."""
    counter = _counters.get(flow_name)
    if not counter or not counter.buckets:
        return None

    total_attempted = sum(b.attempted for b in counter.buckets)
    total_substantive = sum(b.substantive for b in counter.buckets)

    if total_attempted < 10:
        return None  # not enough data

    raw_baseline = total_substantive / total_attempted

    # Adjust for system context
    pressure_factor = 1.0 if pressure < 5.0 else 0.5 if pressure < 15.0 else 0.2
    adjusted = raw_baseline * pressure_factor * max(circadian_factor, 0.3)
    return max(adjusted, 0.1)  # floor: never expect 0 output


# ── Stimulus Routing ──────────────────────────────────────────────────────

_STIMULUS_DEBOUNCE = 60  # seconds between stimuli for the same flow


def _route_stimulus(
    flow_name: str, result: dict, inject_fn: Callable,
) -> None:
    """Route a silence stimulus to the best available infra actor."""
    state = _states.get(flow_name)
    if not state:
        return

    # Debounce: don't spam
    now = time.time()
    if now - state.last_stimulus_ts < _STIMULUS_DEBOUNCE:
        return
    state.last_stimulus_ts = now

    status = result["status"]
    ratio = result.get("ratio", "?")
    baseline = result.get("baseline", "?")
    sample = result.get("sample", 0)

    content = (
        f"[SILENCE DETECTED] {flow_name}: ratio={ratio} "
        f"(expected={baseline}, sample={sample}). Status: {status}."
    )
    energy = 0.8 if status == "RED" else 0.5

    try:
        inject_fn(
            target="infra",
            content=content,
            source="silence_sentinel",
            energy=energy,
            is_failure=(status == "RED"),
        )
        logger.warning(f"[sentinel] Stimulus routed for {flow_name}: {status}")
    except Exception as e:
        logger.error(f"[sentinel] Failed to route stimulus for {flow_name}: {e}")


# ── Health Status ─────────────────────────────────────────────────────────

def get_health_status() -> dict:
    """Return health status for H1/H2/H3 checkers."""
    now = time.time()

    # H1: Is the sentinel alive?
    h1_alive = (now - _last_evaluate_ts) < 60 if _last_evaluate_ts > 0 else False

    # H2: Are per-flow counters active?
    active_flows = sum(
        1 for c in _counters.values()
        if c.buckets and c.buckets[-1].timestamp > (int(now) // 60 * 60 - 600)
    )
    h2_active = active_flows >= 1

    # H3: Any false positives? (simplified — tracks RED firings during high pressure)
    # Full implementation would track historical false positives over 24h
    h3_ok = True  # placeholder until historical tracking is added

    return {
        "h1_alive": h1_alive,
        "h1_last_evaluate": _last_evaluate_ts,
        "h2_active_flows": active_flows,
        "h2_total_flows": len(_counters),
        "h3_calibration_ok": h3_ok,
        "flows": {
            name: {
                "status": _states[name].last_status if name in _states else "UNKNOWN",
                "ratio": _states[name].last_ratio if name in _states else None,
                "baseline": _states[name].rolling_baseline if name in _states else None,
                "observations": _states[name].observations if name in _states else 0,
            }
            for name in _counters
        },
    }


# ── CLI ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Silence Sentinel")
    parser.add_argument("--status", action="store_true", help="Show current counter status")
    parser.add_argument("--health", action="store_true", help="Run health checks")
    args = parser.parse_args()

    if args.status or args.health:
        status = get_health_status()
        print(json.dumps(status, indent=2, default=str))
    else:
        parser.print_help()
