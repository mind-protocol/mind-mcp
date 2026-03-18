"""
Tick System Health — Sensory signals carried by specific citizens.

Spec: docs/orchestrator/tick_system/HEALTH_Tick_System.md

Each health signal is a state node injected into a carrier citizen's L1 brain.
The carrier FEELS the system health through their cognitive graph.
When something degrades, the state node's energy rises → enters WM → citizen becomes aware.

Health signals:
  H1: tick_loop_alive     → @nervo   (physics engine owner)
  H2: citizen_action_rate → @conductor (orchestration lead)
  H3: energy_conservation → @nervo   (decay law owner)
  H4: activation_pressure → @dev     (infra lead)
  H5: graph_latency       → @dev     (infra lead)
  H6: tick_duration       → @nervo   (physics must not stall)
  H7: serialization_speed → @nervo   (critical path owner)

Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger("orchestrator.tick_health")


# =========================================================================
# Health Signal Definitions
# =========================================================================

@dataclass
class HealthSignal:
    """A health signal carried by a specific citizen as a sense."""
    signal_id: str
    carrier: str          # citizen handle who FEELS this signal
    value: float = 1.0    # 0.0 = critical, 1.0 = healthy
    last_checked: float = 0.0
    alert_message: str = ""


# Carrier assignments (from HEALTH_Tick_System.md)
HEALTH_SIGNALS: dict[str, HealthSignal] = {
    "tick_loop_alive": HealthSignal(
        signal_id="state:tick_loop_alive",
        carrier="nervo",
    ),
    "citizen_action_rate": HealthSignal(
        signal_id="state:citizen_action_rate",
        carrier="conductor",
    ),
    "energy_conservation": HealthSignal(
        signal_id="state:energy_conservation",
        carrier="nervo",
    ),
    "activation_pressure": HealthSignal(
        signal_id="state:activation_pressure",
        carrier="dev",
    ),
    "graph_latency": HealthSignal(
        signal_id="state:graph_latency",
        carrier="dev",
    ),
    "tick_duration": HealthSignal(
        signal_id="state:tick_duration",
        carrier="nervo",
    ),
}


# =========================================================================
# Health Check State
# =========================================================================

@dataclass
class TickHealthState:
    """Running state for health checks."""
    last_tick_time: float = 0.0
    tick_count: int = 0
    action_count: int = 0
    total_energy_prev: float = 0.0
    action_history: list[float] = field(default_factory=list)  # timestamps


# Global health state
_state = TickHealthState()


# =========================================================================
# Health Check Functions
# =========================================================================

def record_tick_cycle(
    awareness_count: int,
    thought_count: int,
    action_count: int,
    duration_s: float,
    total_energy: float = 0.0,
    engine_count: int = 0,
):
    """Record a tick cycle for health analysis. Called from dispatcher._tick_all_citizens()."""
    now = time.time()
    _state.last_tick_time = now
    _state.tick_count += 1
    _state.action_count += action_count

    for _ in range(action_count):
        _state.action_history.append(now)

    # Trim action history to last 5 minutes
    cutoff = now - 300
    _state.action_history = [t for t in _state.action_history if t > cutoff]

    # Compute health signals
    signals = {}

    # H1: Tick loop alive (always healthy if we're here)
    signals["tick_loop_alive"] = 1.0

    # H2: Action rate (actions per citizen per 5 min)
    if engine_count > 0:
        actions_last_5min = len(_state.action_history)
        rate = actions_last_5min / engine_count  # actions per citizen per 5min
        # Healthy: 0.8-1.2 actions/citizen/5min (roughly 1 per 5 min)
        if 0.5 <= rate <= 2.0:
            signals["citizen_action_rate"] = 1.0
        elif rate < 0.05:
            signals["citizen_action_rate"] = 0.1  # critical: nobody acting
        else:
            signals["citizen_action_rate"] = max(0.3, 1.0 - abs(rate - 1.0))

    # H3: Energy conservation
    if _state.total_energy_prev > 0 and total_energy > 0:
        delta = abs(total_energy - _state.total_energy_prev) / _state.total_energy_prev
        signals["energy_conservation"] = max(0.0, 1.0 - delta * 5)  # 20% change → 0.0
    _state.total_energy_prev = total_energy

    # H6: Tick duration (< 1s = healthy)
    signals["tick_duration"] = max(0.0, 1.0 - duration_s)

    # Update signal objects
    for name, value in signals.items():
        sig = HEALTH_SIGNALS.get(name)
        if sig:
            sig.value = value
            sig.last_checked = now

    return signals


def inject_health_into_brains(citizen_states: dict):
    """Inject health state nodes into carrier citizens' L1 brains.

    This is the KEY function that makes health SENSORY.
    Called periodically by the dispatcher (e.g., every 60s).

    Args:
        citizen_states: dict[handle → CitizenCognitiveState] from dispatcher.
    """
    from runtime.cognition.models import Node, NodeType

    injected = 0
    now = time.time()

    for name, signal in HEALTH_SIGNALS.items():
        state = citizen_states.get(signal.carrier)
        if state is None:
            continue

        node_id = signal.signal_id
        existing = state.nodes.get(node_id)

        # Energy reflects health: unhealthy = HIGH energy (enters WM as alarm)
        # healthy = LOW energy (fades from WM, citizen not distracted)
        alarm_energy = max(0.0, 1.0 - signal.value)  # 0 health → 1.0 energy (ALARM)

        if existing:
            existing.energy = alarm_energy
            existing.content = signal.alert_message or f"{name}: {signal.value:.2f}"
        else:
            node = Node(
                id=node_id,
                node_type=NodeType.STATE,
                content=signal.alert_message or f"{name}: {signal.value:.2f}",
                weight=0.6,  # moderate weight — health is important
                energy=alarm_energy,
                stability=0.3,  # transient — updates every check
                created_at=now,
            )
            state.add_node(node)
            injected += 1

    if injected > 0:
        logger.info(f"Health signals injected into {injected} carrier brains")


def get_health_summary() -> dict:
    """Return current health state for API/monitoring."""
    return {
        name: {
            "value": sig.value,
            "carrier": sig.carrier,
            "last_checked": sig.last_checked,
            "status": "healthy" if sig.value > 0.7 else "warning" if sig.value > 0.3 else "critical",
        }
        for name, sig in HEALTH_SIGNALS.items()
    }
