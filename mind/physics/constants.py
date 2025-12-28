"""
Physics Constants

All constants for the graph physics engine.
Based on Schema v1.2 Energy Physics.

v1.2 CHANGES:
    - NO DECAY — energy flows through links, cooling handles lifecycle
    - Added COLD_THRESHOLD, TOP_N_LINKS for hot/cold filtering
    - Added LINK_DRAIN_RATE, LINK_TO_STRENGTH_RATE for link cooling
    - Added SUPPORT_THRESHOLD, CONTRADICT_THRESHOLD for moment interaction
    - Added REJECTION_RETURN_RATE

v1.1 CHANGES:
    - Added GENERATION_RATE, MOMENT_DRAW_RATE, FLOW_RATE
    - Added emotion proximity and Hebbian coloring constants
    - Added moment completion thresholds

TESTS:
    engine/tests/test_behaviors.py::TestEnergyFlow
    engine/tests/test_behaviors.py::TestWeightComputation
    engine/tests/test_behaviors.py::TestDecaySystem
    engine/tests/test_behaviors.py::TestCriticality
    engine/tests/test_behaviors.py::TestProximity
    engine/tests/test_spec_consistency.py::TestConstantsConsistency

VALIDATES:
    V4.2: Energy flow (BELIEF_FLOW_RATE, MAX_PROPAGATION_HOPS, LINK_FACTORS)
    V4.3: Weight computation (MIN_WEIGHT)
    V4.4: Decay system (DECAY_RATE, CORE_TYPES, CORE_DECAY_MULTIPLIER)
    V4.6: Criticality (CRITICALITY_TARGET_*, distance_to_proximity)

SEE ALSO:
    docs/physics/algorithms/ALGORITHM_Physics_Schema_v1.1_Energy_Physics.md
    docs/engine/VALIDATION_Complete_Spec.md
"""

# =============================================================================
# ENERGY FLOW
# =============================================================================

# Rate at which characters pump energy into narratives they believe
BELIEF_FLOW_RATE = 0.1

# Maximum hops for energy propagation between narratives
MAX_PROPAGATION_HOPS = 3

# Link-type propagation factors (how energy flows between narratives)
LINK_FACTORS = {
    'contradicts': 0.30,  # Both heat up
    'supports': 0.20,     # Flows one way
    'elaborates': 0.15,   # Detail flows to general
    'subsumes': 0.10,     # Specific to general
    'supersedes': 0.25,   # Drains source by 50% of transfer
}

# =============================================================================
# DECAY
# =============================================================================

# Base decay rate per tick (dynamic, adjusted for criticality)
DECAY_RATE = 0.02

# Decay rate bounds
DECAY_RATE_MIN = 0.005
DECAY_RATE_MAX = 0.1

# Minimum weight (narratives never decay to zero)
MIN_WEIGHT = 0.01

# Core narrative types that decay slower (0.25x rate)
CORE_TYPES = ['oath', 'blood', 'debt']
CORE_DECAY_MULTIPLIER = 0.25

# =============================================================================
# PRESSURE
# =============================================================================

# Base pressure accumulation rate (per minute)
BASE_PRESSURE_RATE = 0.001

# Default breaking point
DEFAULT_BREAKING_POINT = 0.9

# Maximum cascade depth (prevent infinite loops)
MAX_CASCADE_DEPTH = 5

# =============================================================================
# CRITICALITY
# =============================================================================

# Target average pressure range
CRITICALITY_TARGET_MIN = 0.4
CRITICALITY_TARGET_MAX = 0.6

# At least one narrative should be "hot"
CRITICALITY_HOT_THRESHOLD = 0.7

# =============================================================================
# PROXIMITY
# =============================================================================

# Distance-to-proximity conversion
# Same location = 1.0, 1 day = 0.5, 2 days = 0.25, 3+ days = 0.05
def distance_to_proximity(days: float) -> float:
    """Convert travel days to proximity factor."""
    if days <= 0:
        return 1.0
    elif days <= 1:
        return 0.5
    elif days <= 2:
        return 0.25
    else:
        return 0.05

# =============================================================================
# TICK
# =============================================================================

# Minimum time elapsed to trigger a tick
MIN_TICK_MINUTES = 5

# Tick interval in minutes (for scheduled pressure)
TICK_INTERVAL_MINUTES = 5

# =============================================================================
# SCHEMA v1.2 — ENERGY PHYSICS (NO DECAY)
# =============================================================================

# --- Generation Phase ---
# Rate at which actors generate energy per tick (proximity-gated)
GENERATION_RATE = 0.5

# --- Moment Draw Phase ---
# Rate at which moments draw energy from connected actors
# Both POSSIBLE and ACTIVE draw (POSSIBLE at reduced effective rate via formula)
DRAW_RATE = 0.3

# --- Backflow Phase ---
# Rate at which narratives backflow to connected actors
BACKFLOW_RATE = 0.1

# Unified flow formula: flow = source.energy × rate × weight × emotion_factor
# received = flow × sqrt(target.weight)

# --- Hot/Cold Link Filter (v1.2) ---
# Links below this threshold are "cold" and excluded from physics
COLD_THRESHOLD = 0.01

# Maximum links to process per node (top-N by energy × weight)
TOP_N_LINKS = 20

# --- Link Cooling (v1.2, replaces decay) ---
# Percentage of link energy that drains to connected nodes per tick
LINK_DRAIN_RATE = 0.3

# Percentage of link energy that converts to permanent weight per tick
LINK_TO_WEIGHT_RATE = 0.1

# --- Moment Interaction (v1.2) ---
# Emotion proximity threshold for support (>0.7 = support)
SUPPORT_THRESHOLD = 0.7

# Emotion proximity threshold for contradict (<0.3 = contradict)
CONTRADICT_THRESHOLD = 0.3

# Rate of support/contradict energy transfer
INTERACTION_RATE = 0.05

# --- Rejection ---
# Percentage of moment energy returned to player on rejection
REJECTION_RETURN_RATE = 0.8

# --- Tick Timing ---
# Tick duration in seconds
TICK_DURATION_SECONDS = 5

# Ticks per minute (for radiation rate calculation)
TICKS_PER_MINUTE = 12

# --- Emotion Mechanics ---
# Maximum emotions per link
MAX_EMOTIONS_PER_LINK = 7

# Minimum emotion intensity to keep (below this, emotion is pruned)
MIN_EMOTION_INTENSITY = 0.01

# Baseline emotion intensity when list is empty
EMOTION_BASELINE_INTENSITY = 0.5

# Baseline emotion proximity when lists are empty
EMOTION_BASELINE_PROXIMITY = 0.2

# --- Link Crystallization ---
# Initial weight for crystallized links (controls flow rate)
CRYSTALLIZATION_WEIGHT = 0.2

# --- Path Resistance ---
# Maximum hops for path finding (Dijkstra)
MAX_PATH_HOPS = 5

# Default resistance for blocked paths
BLOCKED_PATH_RESISTANCE = 100.0

# Resistance formula: resistance = 1 / (weight × emotion_factor)
# If any factor is 0, resistance is BLOCKED_PATH_RESISTANCE


# =============================================================================
# PLUTCHIK AXES (v1.9)
# =============================================================================
# 4 bipolar emotion axes, each in [-1, +1]:
#   joy_sadness:          -1 = sadness, +1 = joy
#   trust_disgust:        -1 = disgust, +1 = trust
#   fear_anger:           -1 = fear, +1 = anger
#   surprise_anticipation: -1 = surprise, +1 = anticipation

PLUTCHIK_AXES = ['joy_sadness', 'trust_disgust', 'fear_anger', 'surprise_anticipation']


def plutchik_proximity(axes_a: dict, axes_b: dict) -> float:
    """
    Calculate emotion similarity between two Plutchik axis dicts.

    v1.9: Returns value in [0, 1]:
        1.0 = identical axes
        0.0 = maximally different (all axes opposite)

    Uses normalized Euclidean distance.

    Args:
        axes_a: {joy_sadness: float, trust_disgust: float, ...}
        axes_b: {joy_sadness: float, trust_disgust: float, ...}

    Returns:
        Proximity in [0.0, 1.0] range
    """
    if not axes_a and not axes_b:
        return EMOTION_BASELINE_PROXIMITY

    # Calculate squared differences
    total_sq_diff = 0.0
    for axis in PLUTCHIK_AXES:
        val_a = axes_a.get(axis, 0.0)
        val_b = axes_b.get(axis, 0.0)
        diff = val_a - val_b
        total_sq_diff += diff * diff

    # Max possible distance: 4 axes × (2.0)^2 = 16
    # Normalized distance: sqrt(total) / sqrt(16) = sqrt(total) / 4
    # Proximity = 1 - normalized_distance
    import math
    normalized_dist = math.sqrt(total_sq_diff) / 4.0
    return max(0.0, 1.0 - normalized_dist)


def plutchik_intensity(axes: dict) -> float:
    """
    Calculate overall intensity from Plutchik axes.

    v1.9: Returns average absolute value of axes.
    0.0 = neutral on all axes
    1.0 = maximum intensity on all axes

    Args:
        axes: {joy_sadness: float, trust_disgust: float, ...}

    Returns:
        Intensity in [0.0, 1.0] range
    """
    if not axes:
        return EMOTION_BASELINE_INTENSITY

    total = 0.0
    count = 0
    for axis in PLUTCHIK_AXES:
        if axis in axes:
            total += abs(axes[axis])
            count += 1

    if count == 0:
        return EMOTION_BASELINE_INTENSITY

    return total / count


