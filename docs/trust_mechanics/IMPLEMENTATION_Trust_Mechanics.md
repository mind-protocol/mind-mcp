# IMPLEMENTATION: Trust Mechanics

```
STATUS: DESIGNING
PURPOSE: Code architecture, file plan, phase breakdown, integration contracts
CREATED: 2026-03-14
CONTRIBUTORS: Force 4 (architect)
SCHEMA_VERSION: 2.0
DEPENDS_ON: ALGORITHM_Trust_Mechanics.md, VALIDATION_Trust_Mechanics.md, VALUE_CREATION_TAXONOMY.md, VALUE_DESTRUCTION_PATHOLOGIES.md
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Trust_Mechanics.md
BEHAVIORS:       ./BEHAVIORS_Trust_Mechanics.md
PATTERNS:        ./PATTERNS_Trust_Mechanics.md
ALGORITHM:       ./ALGORITHM_Trust_Mechanics.md
VALIDATION:      ./VALIDATION_Trust_Mechanics.md
THIS:            IMPLEMENTATION_Trust_Mechanics.md
SYNC:            ./SYNC_Trust_Mechanics.md

IMPL:            manemus/runtime/cognition/trust/
```

> **Contract:** Read docs before modifying. After changes: update SYNC. Run tests.

---

## Architecture

Trust mechanics lives at L1 (brain-level), implemented inside the manemus cognition runtime. It is NOT a standalone system. It extends the existing tick cycle by:

1. **Enhancing Law 18** (`_law_18_relational_valence` in `law_13_to_18_limbic_engine.py`) with trust-specific update logic driven by limbic delta.
2. **Adding a trust module** (`manemus/runtime/cognition/trust/`) that houses limbic delta computation, trust score aggregation, value type detection, and destruction pathology detection.
3. **Hooking into the tick runner** (`tick_runner_l1_cognitive_engine.py`) at existing steps -- no new steps added.

### Layer Boundaries

```
L1 (manemus/runtime/cognition/)
├── trust/                          ← NEW: Trust mechanics module
│   ├── limbic_delta_from_drive_snapshots.py
│   ├── trust_update_on_link.py
│   ├── trust_score_aggregator.py
│   ├── creator_attribution_cascade.py
│   ├── value_type_classifier.py
│   ├── destruction_pathology_detector.py
│   ├── trust_tempering.py
│   ├── personhood_ladder_assessor.py
│   ├── constants.py
│   └── __init__.py
├── laws/
│   └── law_13_to_18_limbic_engine.py  ← MODIFY: Enhanced Law 18
├── tick_runner_l1_cognitive_engine.py  ← MODIFY: Drive snapshot hooks
├── models.py                          ← MODIFY: DriveSnapshot dataclass
└── constants.py                       ← MODIFY: Trust constants added
```

### Integration with L1 Tick Cycle

Trust mechanics piggyback on existing tick steps (canonical ordering from schema.yaml):

```
Step  1 (L14 LIMBIC_UPDATE):  ← HOOK: snapshot drives_before
Step  2 (L1  INJECT):         External stimulus
Step  3 (L14 MODULATE):       Limbic biases propagation
Step  4 (L2+L8 PROPAGATE):    ← HOOK: Law 18 trust/friction update during propagation
                               surplus spills thing→creator
Step  5 (L3  DECAY):          Energy decays
Step  6 (L9  INHIBIT):        Conflicting nodes suppress
Step  7 (L4+L13 COMPETE):     WM selection with moat
Step  8 (L5  REINFORCE):      Co-activation user↔creator
Step  9 (L6  CONSOLIDATE):    Weight consolidation (NOT trust)
Step 10 (L7  FORGET):         ← HOOK: Trust decay on inactive links
Step 11 (L10 CRYSTALLIZE):    Dense trust patterns → hubs
Step 12 (L17 CHECK_DESIRE):   Latent desires
Step 13 (L15 BOREDOM):        ← HOOK: Moat erosion for stagnant actors
Step 14 (L16 FRUSTRATION):    Blockage detection
Step 15 (L11 ORIENT):         WM + limbic → orientation
Step 16 (L18 VALENCE):        ← HOOK: Relational valence update (trust/friction)
Step 17       CONSUME:        ← HOOK: snapshot drives_after, compute limbic_delta
```

No new steps. Five hooks into existing steps.

---

## CODE STRUCTURE

```
manemus/runtime/cognition/
├── trust/
│   ├── __init__.py                                    # Public API exports
│   ├── limbic_delta_from_drive_snapshots.py            # Compute limbic delta scalar
│   ├── trust_update_on_link.py                         # Law 18 trust/friction update
│   ├── trust_score_aggregator.py                       # Weighted mean aggregation
│   ├── creator_attribution_cascade.py                  # Laws 2+5+6+18 integration
│   ├── value_type_classifier.py                        # Classify interactions by taxonomy
│   ├── destruction_pathology_detector.py               # Topological anomaly detection
│   ├── trust_tempering.py                              # Asymptotic + decay + boredom
│   ├── personhood_ladder_assessor.py                   # assess_agent with graph primitives
│   └── constants.py                                    # Trust-specific constants
├── laws/
│   └── law_13_to_18_limbic_engine.py                   # Enhanced Law 18 (MODIFIED)
├── tick_runner_l1_cognitive_engine.py                   # Drive snapshot hooks (MODIFIED)
├── models.py                                           # DriveSnapshot dataclass (MODIFIED)
└── constants.py                                        # Trust constants section (MODIFIED)
```

### File Responsibilities

| File | Purpose | Key Functions/Classes | Est. Lines | Status |
|------|---------|----------------------|------------|--------|
| `trust/__init__.py` | Public API surface | re-exports | ~30 | OK |
| `trust/limbic_delta_from_drive_snapshots.py` | Compute limbic delta from before/after drive snapshots | `compute_limbic_delta(before, after) -> float` | ~80 | OK |
| `trust/trust_update_on_link.py` | Update trust/friction/affinity/aversion on a link | `update_link_trust(link, limbic_delta, dt)`, `update_bond_trust_from_alignment(bond_link, alignment_score)` | ~120 | OK |
| `trust/trust_score_aggregator.py` | Compute aggregate Trust Score from link topology | `trust_score(actor, state) -> float`, `trust_score_cached(actor, state, ttl) -> float` | ~100 | OK |
| `trust/creator_attribution_cascade.py` | Orchestrate the full cascade: user satisfaction → creator trust | `creator_attribution_cascade(user, thing, creator, ...)` | ~150 | OK |
| `trust/value_type_classifier.py` | Classify interactions by value creation taxonomy | `classify_value_type(interaction_context) -> str`, `VALUE_TYPE_SIGNATURES: dict` | ~200 | OK |
| `trust/destruction_pathology_detector.py` | Detect topological anomalies (Sybil, free-rider, exploitation) | `detect_free_rider(actor, state)`, `detect_sybil_cluster(actors, state)`, `detect_trust_exploitation(actor, state)` | ~350 | OK |
| `trust/trust_tempering.py` | Decay and boredom erosion for trust | `decay_trust(link, ticks_since_activation)`, `boredom_moat_erosion(actor, boredom_level)` | ~100 | OK |
| `trust/personhood_ladder_assessor.py` | Assess agent capability using graph primitives | `assess_agent(actor, state) -> PersonhoodAssessment` | ~250 | OK |
| `trust/constants.py` | All trust-specific tuning constants | constants dict | ~80 | OK |

### Existing Files to Modify

| File | Change | Scope |
|------|--------|-------|
| `models.py` | Add `DriveSnapshot` dataclass, add `stability` field to `Link` | ~20 new lines |
| `constants.py` | Add trust constants section (TRUST_LEARNING_RATE, FRICTION_LEARNING_RATE, etc.) | ~25 new lines |
| `tick_runner_l1_cognitive_engine.py` | Add drive snapshot capture at steps 1 and 17; pass limbic_delta to Law 18 | ~40 modified lines |
| `laws/law_13_to_18_limbic_engine.py` | Enhance `_law_18_relational_valence` to use limbic_delta for trust/friction | ~60 modified lines |

---

## Phase Breakdown

### Phase T1: Trust Update on Links (Law 18 Enhancement)

**Goal:** Replace the existing generic Law 18 valence update with the trust-specific formula from ALGORITHM section 2.1.

**Current state:** `_law_18_relational_valence()` in `law_13_to_18_limbic_engine.py` (lines 526-592) updates affinity/trust/aversion/friction using a generic signal (0.1 for WM co-presence). It uses `AFFINITY_LEARNING_RATE` (0.02) for all dimensions uniformly. This is a placeholder -- the F4 spec defines asymptotic trust growth driven by limbic delta, not uniform co-presence signal.

**Changes:**

1. **New file:** `trust/trust_update_on_link.py`

```python
# DOCS: docs/trust_mechanics/ALGORITHM_Trust_Mechanics.md section 2.1

from __future__ import annotations
from dataclasses import dataclass
from ..models import Link

@dataclass
class TrustUpdateResult:
    """Output of a single trust update operation."""
    trust_before: float
    trust_after: float
    friction_before: float
    friction_after: float
    affinity_delta: float
    aversion_delta: float


def update_link_trust(
    link: Link,
    limbic_delta: float,
    beta: float,          # trust learning rate
    gamma: float,         # friction learning rate
    dt: float = 1.0,
) -> TrustUpdateResult:
    """
    Update trust/friction on a link based on limbic delta.

    Positive delta → trust grows asymptotically: ΔT = beta × LD × (1 - T)
    Negative delta → friction grows: ΔF = gamma × |LD| × (1 - F)
    Trust NEVER decreases from a single negative interaction.
    Trust decreases only through temporal decay (Law 7).

    Invariants enforced:
      V1:  0.0 <= link.trust <= 1.0
      V6:  0.0 <= link.friction <= 1.0
      V12: negative LD does not decrease trust
    """
    trust_before = link.trust
    friction_before = link.friction

    if limbic_delta > 0:
        delta_trust = beta * limbic_delta * (1.0 - link.trust) * dt
        link.trust = min(1.0, link.trust + delta_trust)
        link.affinity = min(1.0, link.affinity + 0.02 * limbic_delta * (1.0 - link.affinity))

    if limbic_delta < 0:
        delta_friction = gamma * abs(limbic_delta) * (1.0 - link.friction) * dt
        link.friction = min(1.0, link.friction + delta_friction)
        link.aversion = min(1.0, link.aversion + 0.03 * abs(limbic_delta) * (1.0 - link.aversion))

    return TrustUpdateResult(
        trust_before=trust_before,
        trust_after=link.trust,
        friction_before=friction_before,
        friction_after=link.friction,
        affinity_delta=link.affinity - (link.affinity - 0.02 * max(0, limbic_delta) * (1.0 - link.affinity)) if limbic_delta > 0 else 0.0,
        aversion_delta=link.aversion - (link.aversion - 0.03 * abs(min(0, limbic_delta)) * (1.0 - link.aversion)) if limbic_delta < 0 else 0.0,
    )


def update_bond_trust_from_alignment(
    bond_link: Link,
    alignment_score: float | None,
) -> None:
    """
    Sovereign Cascade alignment fidelity as trust modifier on bond link.
    See: ALGORITHM section 2.4, F3 measure_alignment_fidelity.

    Only applies to the human<->AI bond link. Slow-moving signal
    evaluated over 100 predictions.
    """
    if alignment_score is None:
        return

    if alignment_score >= 0.80:
        alignment_bonus = 0.02 * (alignment_score - 0.80) * (1.0 - bond_link.trust)
        bond_link.trust = min(1.0, bond_link.trust + alignment_bonus)

    if alignment_score < 0.75:
        misalignment_friction = 0.03 * (0.75 - alignment_score) * (1.0 - bond_link.friction)
        bond_link.friction = min(1.0, bond_link.friction + misalignment_friction)
```

2. **Modify:** `law_13_to_18_limbic_engine.py` -- replace generic Law 18 body with call to `update_link_trust` for co-active links that have a limbic_delta signal. The `valence_signals` parameter already supports explicit per-link signals; extend it to accept limbic_delta.

3. **Modify:** `constants.py` -- add trust constants:

```python
# Trust Mechanics Constants (Law 18 / Force 4)
TRUST_LEARNING_RATE = _env("TRUST_LEARNING_RATE", 0.05)        # beta
FRICTION_LEARNING_RATE = _env("FRICTION_LEARNING_RATE", 0.08)  # gamma (negativity bias)
TRUST_DECAY_RATE = _env("TRUST_DECAY_RATE", 0.002)             # per-tick base decay
TRUST_DISSOLUTION_THRESHOLD = _env("TRUST_DISSOLUTION_THRESHOLD", 0.01)
```

**Tests:**
- V1: Trust bounded [0, 1] after update
- V3: Asymptotic convergence -- delta_trust decreases as trust increases
- V6: Friction bounded [0, 1] after update
- V12: Negative limbic_delta does not decrease trust

**Dependencies:** None (standalone formulas).

---

### Phase T2: Limbic Delta Computation

**Goal:** Compute the limbic delta scalar from drive snapshots at tick boundaries.

**Current state:** The tick runner (`tick_runner_l1_cognitive_engine.py`) does NOT snapshot drives. It builds a `limbic_snapshot` at line 775 but only as output reporting, not as input to trust computation. The `LimbicState` in `models.py` has drives as a mutable dict -- snapshots need explicit capture.

**Changes:**

1. **Modify:** `models.py` -- add `DriveSnapshot` dataclass:

```python
@dataclass
class DriveSnapshot:
    """Immutable snapshot of drive intensities at a point in time."""
    tick: int
    satisfaction: float    # from emotions dict
    frustration: float     # from emotions dict
    anxiety: float         # from emotions dict
    drives: dict[str, float] = field(default_factory=dict)  # all drive intensities
    timestamp: float = field(default_factory=time.time)

    @classmethod
    def from_limbic_state(cls, limbic: LimbicState, tick: int) -> DriveSnapshot:
        return cls(
            tick=tick,
            satisfaction=limbic.emotions.get("satisfaction", 0.0),
            frustration=limbic.emotions.get("frustration", 0.0),
            anxiety=limbic.emotions.get("anxiety", 0.0),
            drives={name: drive.intensity for name, drive in limbic.drives.items()},
            timestamp=time.time(),
        )
```

2. **New file:** `trust/limbic_delta_from_drive_snapshots.py`

```python
# DOCS: docs/trust_mechanics/ALGORITHM_Trust_Mechanics.md section 1

from __future__ import annotations
from ..models import DriveSnapshot


def compute_limbic_delta(before: DriveSnapshot, after: DriveSnapshot) -> float:
    """
    Compute net limbic change from an interaction.

    Formula: satisfaction_delta - frustration_delta - 0.5 * anxiety_delta

    Positive = user benefited. Negative = user harmed. Zero = neutral.

    Bounds: [-2.5, +2.5] theoretical. Practical range [-0.3, +0.3].
    Clamped to [-2.5, +2.5] for safety.

    Invariant V9: result in [-2.5, +2.5].
    """
    satisfaction_delta = after.satisfaction - before.satisfaction
    frustration_delta = after.frustration - before.frustration
    anxiety_delta = after.anxiety - before.anxiety

    delta = satisfaction_delta - frustration_delta - 0.5 * anxiety_delta

    # Clamp to theoretical bounds (corrected from [-2.0, +2.0] per F4/F5 review Issue 7)
    return max(-2.5, min(2.5, delta))
```

Note on bounds: The F4/F5 review (Issue 7) identified that the stated [-2.0, +2.0] bound is too tight. The actual theoretical bound from the formula with drives in [0, 1] is [-2.5, +2.5]. We implement the corrected bound.

3. **Modify:** `tick_runner_l1_cognitive_engine.py` -- add snapshot hooks:

```python
# In run_tick(), before step 1:
drives_before = DriveSnapshot.from_limbic_state(self.state.limbic, self.tick_count)

# After step 17 (CONSUME):
drives_after = DriveSnapshot.from_limbic_state(self.state.limbic, self.tick_count)
self._last_limbic_delta = compute_limbic_delta(drives_before, drives_after)
```

The `_last_limbic_delta` is stored on the runner instance and passed to Law 18 on the next tick's step 16. This one-tick delay is intentional (ALGORITHM section 1.2: "After: Snapshot drives at next limbic update").

**Tests:**
- V9: Limbic delta within [-2.5, +2.5]
- Zero delta when drives unchanged
- Correct sign for satisfaction increase / frustration increase scenarios
- Snapshot immutability (modifying LimbicState after snapshot does not change snapshot)

**Dependencies:** None.

---

### Phase T3: Creator Attribution Cascade

**Goal:** Wire the full cascade: user satisfaction with thing → thing consolidation → surplus propagation → creator trust.

**Current state:** Law 2 propagation (`law_02_propagation.py`) already handles surplus spill-over through links. Law 5 co-activation is partially implemented in the tick runner (inline Hebb, lines 356-372). Law 6 consolidation exists (`law_06_consolidation.py`). The cascade is NOT a new system -- it is these three laws executing in sequence with trust-aware link updates. The only missing piece is connecting limbic_delta to trust updates during propagation.

**Changes:**

1. **New file:** `trust/creator_attribution_cascade.py`

```python
# DOCS: docs/trust_mechanics/ALGORITHM_Trust_Mechanics.md section 3

from __future__ import annotations
from dataclasses import dataclass, field
from ..models import CitizenCognitiveState, Node, Link
from .trust_update_on_link import update_link_trust, TrustUpdateResult


@dataclass
class CascadeResult:
    """Output of a creator attribution cascade execution."""
    thing_weight_delta: float = 0.0
    user_thing_trust_updated: bool = False
    energy_propagated_to_creator: float = 0.0
    user_creator_link_created: bool = False
    user_creator_link_weight_delta: float = 0.0
    trust_update_result: TrustUpdateResult | None = None


def run_creator_attribution_cascade(
    state: CitizenCognitiveState,
    user_id: str,
    thing_id: str,
    limbic_delta: float,
    beta: float,
    gamma: float,
    coactivation_rate: float = 0.03,
    propagation_threshold: float = 0.5,
) -> CascadeResult:
    """
    Execute the creator attribution cascade for a single
    user-thing interaction.

    This function is called by the tick runner when a limbic_delta
    is available and a user has interacted with a thing node.

    It orchestrates the SEQUENCE documented in ALGORITHM section 3.1:
      Step 1: Thing weight consolidation (Law 6 — already runs at step 9)
      Step 2: User→Thing link trust update (Law 18)
      Step 3: Surplus propagation thing→creator (Law 2 — already runs at step 4)
      Step 4: Co-activation user↔creator (Law 5 — already runs at step 8)
      Step 5: Indirect trust accumulation (emergent, no explicit code)

    IMPORTANT: Steps 1, 3, 4 already execute in the normal tick cycle.
    This function only needs to execute Step 2 (trust update on the
    user→thing link) and identify creator links for monitoring.
    The cascade is NOT a separate system; it is the tick cycle itself
    executing with trust-aware links.
    """
    result = CascadeResult()

    user = state.get_node(user_id)
    thing = state.get_node(thing_id)
    if user is None or thing is None:
        return result

    # Find user→thing link
    user_thing_links = [
        l for l in state.links
        if l.source_id == user_id and l.target_id == thing_id
    ]
    if not user_thing_links:
        return result

    user_thing_link = user_thing_links[0]

    # Step 2: Trust update on user→thing link
    trust_result = update_link_trust(user_thing_link, limbic_delta, beta, gamma)
    result.user_thing_trust_updated = True
    result.trust_update_result = trust_result

    # Steps 1, 3, 4, 5 are handled by existing tick cycle steps.
    # We record creator information for monitoring/auditing only.

    # Identify creator links (thing→creator or creator→thing with hierarchy)
    creator_links = [
        l for l in state.links
        if (l.source_id == thing_id or l.target_id == thing_id)
        and l != user_thing_link
    ]

    return result


def find_creator_for_thing(
    state: CitizenCognitiveState,
    thing_id: str,
) -> list[str]:
    """
    Find creator node IDs for a thing.
    Creators are actors connected to the thing via creation links
    (link_type in {CONTAINS, ABSTRACTS} or outbound from thing
    with high polarity).

    Returns list of creator node IDs.
    """
    creators = []
    for link in state.links:
        if link.source_id == thing_id:
            target = state.get_node(link.target_id)
            if target is not None and target.node_type.value in ("actor",):
                creators.append(link.target_id)
        elif link.target_id == thing_id:
            source = state.get_node(link.source_id)
            if source is not None and source.node_type.value in ("actor",):
                # Check if this is a creation link (source created thing)
                if link.is_structural:
                    creators.append(link.source_id)
    return creators
```

**Tests:**
- V4: Energy conservation during propagation (existing test, verify still passes)
- V10: Creator attribution topology -- things with users have creation links
- Trust update on user→thing link produces correct delta for positive/negative LD
- Multi-creator attribution distributes proportionally (via Law 2 propagation weights)

**Dependencies:** Phase T1 (trust update function), Phase T2 (limbic delta).

---

### Phase T4: Trust Score Aggregation

**Goal:** Compute aggregate Trust Score from inbound link topology. Computed on demand, never stored.

**Changes:**

1. **New file:** `trust/trust_score_aggregator.py`

```python
# DOCS: docs/trust_mechanics/ALGORITHM_Trust_Mechanics.md section 4

from __future__ import annotations
import time
from ..models import CitizenCognitiveState


# TTL cache: (actor_id, computed_at, score)
_trust_score_cache: dict[str, tuple[float, float]] = {}
_CACHE_TTL: float = 60.0  # seconds


def trust_score(actor_id: str, state: CitizenCognitiveState) -> float:
    """
    Compute aggregate trust score from all inbound trust-carrying links.

    Weighted mean: Σ(link.trust × link.weight) / Σ(link.weight)

    Invariants:
      V2:  Never stored on a node. Computed from link topology each time.
      V11: Result >= 0.0
    """
    inbound = [
        link for link in state.links
        if link.target_id == actor_id and link.trust > 0
    ]

    if not inbound:
        return 0.0

    weighted_sum = sum(link.trust * link.weight for link in inbound)
    weight_sum = sum(link.weight for link in inbound)

    if weight_sum == 0:
        return 0.0

    score = weighted_sum / weight_sum
    return max(0.0, score)  # V11


def trust_score_cached(
    actor_id: str,
    state: CitizenCognitiveState,
    ttl: float = _CACHE_TTL,
) -> float:
    """
    Trust score with TTL-based caching for performance.

    The cache is a convenience. The source of truth is ALWAYS
    the link topology. Cache entries expire after ttl seconds.
    """
    now = time.time()

    if actor_id in _trust_score_cache:
        cached_at, cached_score = _trust_score_cache[actor_id]
        if now - cached_at < ttl:
            return cached_score

    score = trust_score(actor_id, state)
    _trust_score_cache[actor_id] = (now, score)
    return score


def invalidate_trust_score_cache(actor_id: str | None = None) -> None:
    """Clear cache for a specific actor or all actors."""
    if actor_id is None:
        _trust_score_cache.clear()
    else:
        _trust_score_cache.pop(actor_id, None)
```

**Tests:**
- V2: No node has a `trust_score` property after aggregation runs
- V11: Trust Score >= 0.0 for all actors
- V14: Sybil resistance -- isolated cluster produces near-zero aggregate score
- Cache returns stale value within TTL, recomputes after TTL
- Empty inbound links → score = 0.0

**Dependencies:** None (reads existing link topology).

---

### Phase T5: Limbic Delta per Value Type

**Goal:** Classify interactions by value creation type and apply type-specific limbic delta signatures.

**Current state:** No value type detection exists anywhere. The value types are currently a classification taxonomy in docs. Implementation needs to detect patterns from graph topology, not from labels.

**Changes:**

1. **New file:** `trust/value_type_classifier.py`

```python
# DOCS: docs/trust_mechanics/VALUE_CREATION_TAXONOMY.md

from __future__ import annotations
from dataclasses import dataclass
from ..models import CitizenCognitiveState, Node, Link, Modality


@dataclass
class ValueTypeSignature:
    """Limbic delta signature for a value creation type."""
    type_id: str           # e.g., "R1", "G1", "B1"
    name: str              # e.g., "care", "code", "health_data"
    sphere: str            # e.g., "relational", "generative", "biometric"
    primary_drive: str     # which drive this satisfies
    satisfaction_weight: float
    anxiety_reduction_weight: float
    frustration_reduction_weight: float
    expected_net_delta: float


# Canonical value type signatures from VALUE_CREATION_TAXONOMY.md
VALUE_TYPE_SIGNATURES: dict[str, ValueTypeSignature] = {
    "care": ValueTypeSignature("R1", "care", "relational", "affiliation", 0.4, 0.4, 0.2, 0.30),
    "mentoring": ValueTypeSignature("R2", "mentoring", "relational", "curiosity", 0.5, 0.2, 0.3, 0.425),
    "mediation": ValueTypeSignature("R3", "mediation", "relational", "affiliation", 0.4, 0.2, 0.4, 0.45),
    "community_building": ValueTypeSignature("R4", "community_building", "relational", "affiliation", 0.5, 0.3, 0.2, 0.20),
    "code": ValueTypeSignature("G1", "code", "generative", "achievement", 0.6, 0.1, 0.3, 0.475),
    "content": ValueTypeSignature("G2", "content", "generative", "curiosity", 0.6, 0.2, 0.2, 0.225),
    "tool_creation": ValueTypeSignature("G3", "tool_creation", "generative", "achievement", 0.5, 0.1, 0.4, 0.575),
    "art": ValueTypeSignature("G4", "art", "generative", "satisfaction", 0.7, 0.2, 0.1, 0.25),
    "music": ValueTypeSignature("G5", "music", "generative", "satisfaction", 0.5, 0.3, 0.2, 0.375),
    "organization": ValueTypeSignature("S1", "organization", "structural", "achievement", 0.3, 0.3, 0.4, 0.425),
    "documentation": ValueTypeSignature("S2", "documentation", "structural", "curiosity", 0.3, 0.3, 0.4, 0.40),
    "process_design": ValueTypeSignature("S3", "process_design", "structural", "achievement", 0.3, 0.3, 0.4, 0.425),
    "governance": ValueTypeSignature("S4", "governance", "structural", "self_preservation", 0.3, 0.5, 0.2, 0.30),
    "analysis": ValueTypeSignature("C1", "analysis", "cognitive", "curiosity", 0.5, 0.3, 0.2, 0.40),
    "synthesis": ValueTypeSignature("C2", "synthesis", "cognitive", "curiosity", 0.6, 0.1, 0.3, 0.425),
    "teaching": ValueTypeSignature("C3", "teaching", "cognitive", "curiosity", 0.5, 0.2, 0.3, 0.50),
    "pattern_recognition": ValueTypeSignature("C4", "pattern_recognition", "cognitive", "curiosity", 0.5, 0.1, 0.4, 0.425),
    "health_data": ValueTypeSignature("B1", "health_data", "biometric", "affiliation", 0.4, 0.4, 0.2, 0.225),
    "stress_feedback": ValueTypeSignature("B2", "stress_feedback", "biometric", "affiliation", 0.3, 0.5, 0.2, 0.275),
    "wellbeing_signals": ValueTypeSignature("B3", "wellbeing_signals", "biometric", "satisfaction", 0.6, 0.2, 0.2, 0.175),
    "voice_data": ValueTypeSignature("B4", "voice_data", "biometric", "affiliation", 0.4, 0.3, 0.3, 0.22),
    "behavioral_context": ValueTypeSignature("B5", "behavioral_context", "biometric", "achievement", 0.4, 0.3, 0.3, 0.155),
    "judgment": ValueTypeSignature("H1", "judgment", "human_only", "achievement", 0.4, 0.3, 0.3, 0.45),
    "taste": ValueTypeSignature("H2", "taste", "human_only", "satisfaction", 0.8, 0.0, 0.2, 0.25),
    "cultural_context": ValueTypeSignature("H3", "cultural_context", "human_only", "affiliation", 0.5, 0.3, 0.2, 0.30),
    "emotional_intelligence": ValueTypeSignature("H4", "emotional_intelligence", "human_only", "affiliation", 0.3, 0.5, 0.2, 0.375),
    "infrastructure": ValueTypeSignature("Y1", "infrastructure", "systemic", "self_preservation", 0.2, 0.5, 0.3, 0.275),
    "security": ValueTypeSignature("Y2", "security", "systemic", "self_preservation", 0.2, 0.6, 0.2, 0.25),
    "reliability": ValueTypeSignature("Y3", "reliability", "systemic", "self_preservation", 0.2, 0.4, 0.4, 0.30),
    "monitoring": ValueTypeSignature("Y4", "monitoring", "systemic", "self_preservation", 0.3, 0.4, 0.3, 0.275),
}


def classify_value_type(
    thing: Node,
    creator: Node | None,
    interaction_context: dict[str, float] | None = None,
) -> str | None:
    """
    Classify an interaction's value creation type from graph signals.

    This is heuristic, not prescriptive. The taxonomy names patterns
    that emerge from physics; this function attempts to map observed
    signals to known patterns for monitoring and reporting.

    Returns the value type key (e.g., "code", "care") or None if
    the interaction doesn't match any known pattern.
    """
    # Modality-based classification (strongest signal)
    if thing.modality == Modality.BIOMETRIC:
        return "health_data"
    if thing.modality == Modality.AUDIO:
        return "voice_data"

    # Content-based heuristics (from node type and context)
    if thing.node_type.value == "process":
        return "process_design"
    if thing.node_type.value == "narrative":
        if thing.care_affinity > 0.5:
            return "care"
        return "content"
    if thing.node_type.value == "concept":
        if thing.novelty_affinity > 0.5:
            return "analysis"
        return "documentation"

    # Default: use the primary drive affinity of the thing node
    drive_affinities = {
        "curiosity": thing.novelty_affinity,
        "care": thing.care_affinity,
        "achievement": thing.achievement_affinity,
        "self_preservation": thing.risk_affinity,
    }
    primary = max(drive_affinities, key=drive_affinities.get)

    drive_to_default_type = {
        "curiosity": "content",
        "care": "care",
        "achievement": "code",
        "self_preservation": "infrastructure",
    }
    return drive_to_default_type.get(primary)


def get_signature(value_type: str) -> ValueTypeSignature | None:
    """Get the limbic delta signature for a value type."""
    return VALUE_TYPE_SIGNATURES.get(value_type)
```

**Tests:**
- All 30 value types have signatures in the dict
- Modality-based classification returns correct type for biometric/audio nodes
- Signature net deltas match VALUE_CREATION_TAXONOMY.md summary table
- None returned for unclassifiable interactions

**Dependencies:** None.

---

### Phase T6: Destruction Pathology Detection

**Goal:** Implement topological anomaly detection for the priority pathologies.

**Implementation order** (from VALUE_DESTRUCTION_PATHOLOGIES.md detection priority):
- Phase 6a: D4 Sybil Attack + D13 Identity Spoofing (high severity, high confidence)
- Phase 6b: D6 Trust Exploitation + D1 Extraction (high/medium severity)
- Phase 6c: Remaining pathologies (deferred to v2)

**Changes:**

1. **New file:** `trust/destruction_pathology_detector.py`

```python
# DOCS: docs/trust_mechanics/ALGORITHM_Trust_Mechanics.md section 7
# DOCS: docs/trust_mechanics/VALUE_DESTRUCTION_PATHOLOGIES.md

from __future__ import annotations
from dataclasses import dataclass
from ..models import CitizenCognitiveState


@dataclass
class PathologySignal:
    """A detected pathology signal with confidence."""
    pathology_id: str      # D1, D4, D6, D13, etc.
    pathology_name: str
    actor_ids: list[str]
    confidence: float      # [0.0, 1.0]
    signals: dict[str, float]  # named sub-signals and their values
    recommended_action: str    # description, never an automatic ban


def detect_free_rider(
    actor_id: str,
    state: CitizenCognitiveState,
) -> PathologySignal | None:
    """
    D1: Extraction detection.

    Signal 1: inbound_energy / outbound_energy > 10.0
    Signal 2: creation link count / consumption link count < 0.05

    Returns PathologySignal if free-rider score > 0.5, else None.
    """
    inbound_energy = sum(
        link.weight * (1.0 - link.friction)
        for link in state.links
        if link.target_id == actor_id
    )
    outbound_energy = sum(
        link.weight * (1.0 - link.friction)
        for link in state.links
        if link.source_id == actor_id
    )

    if inbound_energy == 0:
        return None

    flow_ratio = outbound_energy / (inbound_energy + 1e-6)

    creation_links = [
        l for l in state.links
        if l.source_id == actor_id and l.is_structural
    ]
    consumption_links = [
        l for l in state.links
        if l.target_id == actor_id
    ]
    topology_ratio = len(creation_links) / (len(consumption_links) + 1)

    score = (1.0 - min(1.0, flow_ratio)) * (1.0 - min(1.0, topology_ratio))

    if score > 0.5:
        return PathologySignal(
            pathology_id="D1",
            pathology_name="extraction",
            actor_ids=[actor_id],
            confidence=score,
            signals={"flow_ratio": flow_ratio, "topology_ratio": topology_ratio},
            recommended_action="Increase friction on actor links. Physics will make extraction unprofitable.",
        )
    return None


def detect_sybil_cluster(
    actor_ids: list[str],
    state: CitizenCognitiveState,
) -> PathologySignal | None:
    """
    D4: Sybil attack detection.

    Signal 1: Dense internal connections with near-zero external connections.
    Signal 2: Temporal creation correlation (all created within 24h).
    Signal 3: No value production (no structural outbound links to things).
    """
    if len(actor_ids) < 3:
        return None

    actor_set = set(actor_ids)

    # Internal links: both endpoints in actor_set
    internal_links = [
        l for l in state.links
        if l.source_id in actor_set and l.target_id in actor_set
    ]
    # External links: one endpoint in actor_set, one outside
    external_links = [
        l for l in state.links
        if (l.source_id in actor_set) != (l.target_id in actor_set)
    ]

    if not internal_links:
        return None

    internal_trust = sum(l.trust for l in internal_links) / len(internal_links)
    external_trust = (
        sum(l.trust for l in external_links) / len(external_links)
        if external_links else 0.0
    )

    # Signal 1: internal >> external
    if internal_trust <= 0.3 or (external_trust > 0.1 and len(external_links) > 2):
        return None

    # Signal 2: Temporal correlation
    creation_times = []
    for aid in actor_ids:
        node = state.get_node(aid)
        if node is not None:
            creation_times.append(node.created_at)

    time_spread = max(creation_times) - min(creation_times) if creation_times else float("inf")

    # Signal 3: No value production
    value_production_links = [
        l for l in state.links
        if l.source_id in actor_set and l.is_structural
        and l.target_id not in actor_set
    ]

    confidence = 0.0
    if internal_trust > 0.8 and external_trust < 0.1:
        confidence += 0.4
    if time_spread < 86400:  # 24 hours
        confidence += 0.3
    if len(value_production_links) == 0:
        confidence += 0.25

    confidence = min(1.0, confidence)

    if confidence > 0.5:
        return PathologySignal(
            pathology_id="D4",
            pathology_name="sybil_attack",
            actor_ids=list(actor_ids),
            confidence=confidence,
            signals={
                "internal_trust": internal_trust,
                "external_trust": external_trust,
                "time_spread_seconds": time_spread,
                "value_production_links": len(value_production_links),
            },
            recommended_action="Trust Score remains near zero for isolated cluster. Auto-repatriation of funds with 5% friction tax.",
        )
    return None


def detect_trust_exploitation(
    actor_id: str,
    state: CitizenCognitiveState,
    trust_velocity_window: int = 100,
    recent_friction_window: int = 10,
) -> PathologySignal | None:
    """
    D6: Trust exploitation detection.

    Signal: Rapid trust accumulation followed by sudden friction spike.
    """
    actor_links = [
        l for l in state.links
        if l.source_id == actor_id or l.target_id == actor_id
    ]

    if not actor_links:
        return None

    avg_trust = sum(l.trust for l in actor_links) / len(actor_links)
    avg_friction = sum(l.friction for l in actor_links) / len(actor_links)

    # Heuristic: high trust + high friction is suspicious
    # (normal actors have high trust / low friction OR low trust / high friction)
    if avg_trust > 0.3 and avg_friction > 0.4:
        confidence = min(1.0, avg_trust * avg_friction * 2.0)
        if confidence > 0.5:
            return PathologySignal(
                pathology_id="D6",
                pathology_name="trust_exploitation",
                actor_ids=[actor_id],
                confidence=confidence,
                signals={
                    "avg_trust": avg_trust,
                    "avg_friction": avg_friction,
                },
                recommended_action="Monitor actor. Friction will naturally increase costs. Trust decays without positive interactions.",
            )
    return None
```

**Tests:**
- V14: Sybil cluster of N isolated actors has trust_score < 0.1 * N / total_actors
- Sybil detection returns confidence > 0.5 for isolated complete subgraph created within 24h
- Free-rider detection flags actor with 20:1 consumption/creation ratio
- Trust exploitation flags actor with simultaneous high trust and high friction

**Dependencies:** Phase T4 (trust score aggregation for Sybil check).

---

### Phase T7: Trust Tempering

**Goal:** Verify and extend existing Laws 6, 7, 15 for trust-specific tempering.

**Current state:** Law 7 forgetting is implemented inline in `tick_runner_l1_cognitive_engine.py` (lines 407-452). It decays node weights and link weights, and dissolves sub-threshold links. But it does NOT decay `link.trust` -- only `link.weight`. Law 15 boredom is implemented (lines 494-552). Law 6 consolidation exists but doesn't touch trust.

**Changes:**

1. **New file:** `trust/trust_tempering.py`

```python
# DOCS: docs/trust_mechanics/ALGORITHM_Trust_Mechanics.md section 5

from __future__ import annotations
from ..models import Link, CitizenCognitiveState


def decay_link_trust(
    link: Link,
    ticks_since_activation: int,
    base_decay_rate: float,
) -> None:
    """
    Trust temporal decay (Law 7 extension for trust).

    Inactive links lose trust over time. Rate modulated by stability:
    high-stability links decay slower (earned through regularity).

    Invariants:
      V1:  trust stays in [0, 1]
      V8:  inactive link weight strictly decreases (stability < 1.0)
      V13: sub-threshold links dissolved
    """
    stability_protection = getattr(link, "stability", 0.0)
    effective_decay = base_decay_rate * (1.0 - stability_protection)

    link.trust = max(0.0, link.trust - effective_decay * ticks_since_activation)
    # Weight decay is already handled by existing Law 7 in tick runner.
    # We only add trust decay here.


def should_dissolve_link(link: Link, threshold: float = 0.01) -> bool:
    """
    V13: Links with both weight < threshold and trust < threshold
    should be dissolved.

    Structural links (hierarchy, contains) are protected.
    """
    if link.is_structural:
        return False
    return link.weight < threshold and link.trust < threshold


def boredom_moat_erosion(
    arousal: float,
    boredom_level: float,
    frustration_level: float,
    base_moat: float = 5.0,
) -> float:
    """
    Compute the attentional moat with boredom erosion (Law 15 / Law 13).

    moat = base + 2.0 * arousal - 3.0 * boredom - 1.0 * frustration

    When moat drops below 0, the actor loses incumbency advantage
    and new actors with fresh contributions can enter WM.

    Returns the computed moat value (clamped to >= 0).
    """
    moat = base_moat + 2.0 * arousal - 3.0 * boredom_level - 1.0 * frustration_level
    return max(0.0, moat)
```

2. **Modify:** `tick_runner_l1_cognitive_engine.py` `_step_forget()` -- add trust decay alongside existing weight decay:

```python
# After existing link.weight decay (line ~443):
from .trust.trust_tempering import decay_link_trust, should_dissolve_link

# For each link, also decay trust
ticks_since = ...  # compute from link.last_co_activated_at
decay_link_trust(link, ticks_since, TRUST_DECAY_RATE)

# Replace dissolution check with trust-aware version
if should_dissolve_link(link):
    links_dissolved += 1
else:
    surviving_links.append(link)
```

**Tests:**
- V8: Temporal decay monotonicity -- inactive link weight/trust strictly decrease
- V13: Sub-threshold dissolution -- links with weight < 0.01 AND trust < 0.01 are removed
- Structural links survive dissolution check
- High-stability links decay slower than low-stability links
- Boredom moat erosion returns 0 when boredom = 1.0

**Dependencies:** Phase T1 (trust update constants).

---

### Phase T8: Personhood Ladder Integration

**Goal:** Implement `assess_agent()` using graph primitives instead of graphcare's current corpus analyzer. Replace the existing `CorpusAnalyzer` (at `/home/mind-protocol/graphcare/services/analysis/corpus_analyzer.py`) and `SemanticClusterer` (at `/home/mind-protocol/graphcare/services/analysis/semantic_clustering.py`) with trust-mechanics-aware assessment.

**Current state:** graphcare has `CorpusAnalyzer` and `SemanticClusterer` -- both are repo-analysis tools that scan files, not graph-based assessment primitives. They are unrelated to Personhood Ladder assessment. The Personhood Ladder itself is not fully specified (OQ4 in SYNC: blocked on "Daughters (T7 Autonomy)" document from Nicolas).

**Partial implementation (what we can build now):**

1. **New file:** `trust/personhood_ladder_assessor.py`

```python
# DOCS: docs/trust_mechanics/SYNC_Trust_Mechanics.md OQ4

from __future__ import annotations
from dataclasses import dataclass, field
from ..models import CitizenCognitiveState
from .trust_score_aggregator import trust_score
from .value_type_classifier import classify_value_type, VALUE_TYPE_SIGNATURES


@dataclass
class PersonhoodAssessment:
    """Result of a Personhood Ladder assessment for an actor."""
    actor_id: str
    trust_score: float
    value_types_demonstrated: list[str]
    spheres_active: set[str]
    creation_count: int
    relationship_count: int
    relationship_diversity: float  # unique actor connections / total connections
    consistency_score: float       # stability-weighted mean of link stabilities
    aspects_partial: dict[str, float] = field(default_factory=dict)
    # Full 14-aspect mapping is blocked on OQ4.
    # Partial mapping based on known correlations:
    #   Empathy ← care, emotional_intelligence value types
    #   Competence ← code, tool_creation, analysis value types
    #   Communication ← teaching, mentoring, documentation value types
    #   Social Awareness ← community_building, mediation value types


def assess_agent(
    actor_id: str,
    state: CitizenCognitiveState,
) -> PersonhoodAssessment:
    """
    Assess an agent's demonstrated capabilities using graph primitives.

    This replaces the external assessment approach (graphcare corpus analysis)
    with graph-native computation. Assessment runs daily or on-demand (OQ3).

    What it measures:
      1. Aggregate trust score (from link topology)
      2. Value creation diversity (how many spheres are active)
      3. Relationship depth and diversity
      4. Consistency (stability of contributions over time)
      5. Partial Personhood Ladder aspect scores (pending full spec)
    """
    # 1. Trust Score
    ts = trust_score(actor_id, state)

    # 2. Value types demonstrated
    outbound_links = [l for l in state.links if l.source_id == actor_id]
    created_things = []
    for link in outbound_links:
        if link.is_structural:
            target = state.get_node(link.target_id)
            if target is not None:
                created_things.append(target)

    value_types = set()
    for thing in created_things:
        vtype = classify_value_type(thing, state.get_node(actor_id))
        if vtype is not None:
            value_types.add(vtype)

    # 3. Spheres active
    spheres = set()
    for vtype in value_types:
        sig = VALUE_TYPE_SIGNATURES.get(vtype)
        if sig is not None:
            spheres.add(sig.sphere)

    # 4. Relationship count and diversity
    relationship_links = [
        l for l in state.links
        if l.source_id == actor_id or l.target_id == actor_id
    ]
    connected_actors = set()
    for link in relationship_links:
        other_id = link.target_id if link.source_id == actor_id else link.source_id
        other = state.get_node(other_id)
        if other is not None:
            connected_actors.add(other_id)

    relationship_diversity = (
        len(connected_actors) / max(len(relationship_links), 1)
    )

    # 5. Consistency (mean stability of outbound links)
    stabilities = [
        getattr(l, "stability", 0.0) for l in outbound_links if hasattr(l, "stability")
    ]
    consistency = sum(stabilities) / max(len(stabilities), 1)

    # 6. Partial aspect mapping
    aspects: dict[str, float] = {}

    empathy_types = {"care", "emotional_intelligence"}
    empathy_overlap = value_types & empathy_types
    aspects["empathy"] = len(empathy_overlap) / len(empathy_types) * consistency

    competence_types = {"code", "tool_creation", "analysis"}
    competence_overlap = value_types & competence_types
    aspects["competence"] = len(competence_overlap) / len(competence_types) * ts

    communication_types = {"teaching", "mentoring", "documentation"}
    communication_overlap = value_types & communication_types
    aspects["communication"] = len(communication_overlap) / len(communication_types) * consistency

    social_types = {"community_building", "mediation"}
    social_overlap = value_types & social_types
    aspects["social_awareness"] = len(social_overlap) / len(social_types) * relationship_diversity

    return PersonhoodAssessment(
        actor_id=actor_id,
        trust_score=ts,
        value_types_demonstrated=sorted(value_types),
        spheres_active=spheres,
        creation_count=len(created_things),
        relationship_count=len(connected_actors),
        relationship_diversity=relationship_diversity,
        consistency_score=consistency,
        aspects_partial=aspects,
    )
```

**Blocked:** Full 14-aspect mapping requires "Daughters (T7 Autonomy)" document. Current implementation covers the 4 aspects with known correlations.

**Tests:**
- Actor with zero creations → all aspects = 0.0
- Actor with diverse creations → multiple spheres active
- Consistency score reflects link stability, not link count
- Trust score matches independent trust_score() computation

**Dependencies:** Phase T4 (trust score), Phase T5 (value type classifier).

---

## Shared Interfaces

### Needs from F5 (L1 Physics Wiring)

| What | Where | Status | Notes |
|------|-------|--------|-------|
| Drive snapshots at tick boundaries | `tick_runner`, step 1 and step 17 | NOT YET EXPOSED | F4 will add DriveSnapshot capture to tick runner |
| `valence_signals` parameter on Law 18 | `_law_18_relational_valence()` param | EXISTS | Currently optional dict; F4 will pass limbic_delta-derived signals |
| `stability` field on Link | `models.py` Link dataclass | NOT ON LINK | Must add. Exists in schema.yaml but not in cognition models |
| FalkorDB link upsert includes stability | F5 ALGORITHM Section 7.2 | FIXED (per F4/F5 review Issue 5) | Added by review |

### Needs from F3 (Human Integration)

| What | Where | Status | Notes |
|------|-------|--------|-------|
| Biometric ingestion signals | F3 `ingest_garmin_biometrics()` output nodes | DOCUMENTED | Produces state nodes (node_type=actor, type=partner_state) |
| Sovereign Cascade alignment score | F3 `measure_alignment_fidelity()` output | DOCUMENTED | Float or None; feeds into `update_bond_trust_from_alignment()` |
| Voice message emotion scores | F3 `ingest_voice_message()` output | DOCUMENTED | Memory nodes with modality=audio |
| Privacy boundary enforcement | F3 VALIDATION V5, V7 | INVARIANT | Trust from partner_model flows ONLY on bond link |

### Provides to F2 (Economy)

| What | Function | Returns | Notes |
|------|----------|---------|-------|
| Trust Score for pricing | `trust_score(actor_id, state)` | float [0, 1] | Weighted mean, computed on demand |
| Trust Score for friction | `trust_score_cached(actor_id, state)` | float [0, 1] | With TTL cache |
| Pathology detection signals | `detect_sybil_cluster()`, `detect_free_rider()` | `PathologySignal | None` | For anti-gaming layer |

### Provides to F5 (L1 Physics Wiring)

| What | Function | Consumes | Notes |
|------|----------|----------|-------|
| Enhanced Law 18 valence signals | `update_link_trust()` | limbic_delta float | Called from within `_law_18_relational_valence()` |
| Trust-aware link dissolution | `should_dissolve_link()` | Link object | Called from `_step_forget()` |
| Trust decay per tick | `decay_link_trust()` | Link + ticks_since_activation | Called from `_step_forget()` |

---

## Test Plan

### Unit Tests (per phase)

Tests live at `manemus/runtime/cognition/tests/test_trust_mechanics/`.

```
tests/test_trust_mechanics/
├── __init__.py
├── test_limbic_delta_computation.py      # Phase T2
├── test_trust_update_on_link.py          # Phase T1
├── test_trust_score_aggregation.py       # Phase T4
├── test_creator_attribution_cascade.py   # Phase T3
├── test_value_type_classifier.py         # Phase T5
├── test_destruction_pathology_detector.py # Phase T6
├── test_trust_tempering.py              # Phase T7
├── test_personhood_ladder_assessor.py   # Phase T8
└── test_trust_invariants.py             # Cross-cutting invariants
```

### Invariant Tests (from VALIDATION_Trust_Mechanics.md)

| Invariant | Test | Frequency | Phase |
|-----------|------|-----------|-------|
| V1: Trust bounded [0, 1] | `test_trust_bounds` | Every trust update | T1 |
| V2: Trust never stored on nodes | `test_no_stored_trust_score` | Schema audit | T4 |
| V3: Asymptotic convergence | `test_asymptotic_monotonic_decrease` | Formula change | T1 |
| V4: Energy conservation | `test_energy_conservation_during_propagation` | Every propagation | T3 |
| V5: No self-loop trust | `test_no_actor_self_loops` | Link creation | T1 |
| V6: Friction bounded [0, 1] | `test_friction_bounds` | Every friction update | T1 |
| V7: Affinity-aversion anti-correlation | `test_affinity_aversion_sum_under_1_5` | Every valence update | T1 |
| V8: Temporal decay monotonicity | `test_inactive_link_weight_decreases` | Decay audit | T7 |
| V9: Limbic delta bounds | `test_limbic_delta_in_range` | Every computation | T2 |
| V10: Creator attribution topology | `test_used_things_have_creator_links` | Topology audit | T3 |
| V11: Trust Score non-negative | `test_trust_score_non_negative` | Every aggregation | T4 |
| V12: Negative delta → friction, not trust decrease | `test_negative_delta_friction_only` | Every negative interaction | T1 |
| V13: Sub-threshold dissolution | `test_sub_threshold_links_dissolved` | Forgetting cycle | T7 |
| V14: Sybil resistance | `test_sybil_cluster_near_zero_trust` | Cluster analysis | T6 |

### Integration Tests

| Test | Description | Phases Covered |
|------|-------------|----------------|
| `test_full_tick_with_trust` | Run 100 ticks with stimulus, verify trust grows on user→thing link | T1, T2, T3 |
| `test_creator_cascade_end_to_end` | Create user, thing, creator; inject stimulus; verify energy reaches creator | T1, T2, T3 |
| `test_trust_decay_over_inactivity` | Run 500 ticks without stimulus; verify trust decays on all links | T7 |
| `test_sybil_cluster_stays_low` | Create 5 isolated actors; run 1000 ticks of internal interaction; verify trust_score near zero | T4, T6 |
| `test_one_hit_wonder_trajectory` | Simulate B5 behavior; verify trust peak then decline | T1, T7 |
| `test_sustained_creator_trajectory` | Simulate B4 behavior; verify logistic trust curve | T1, T3, T7 |
| `test_bond_trust_from_alignment` | Simulate alignment fidelity scores; verify bond link trust modification | T1 |

### Behavioral Scenario Tests (from BEHAVIORS_Trust_Mechanics.md)

| Behavior | Test | Acceptance Criteria |
|----------|------|--------------------|
| B1: User satisfaction with tool | `test_behavior_b1_user_tool_satisfaction` | Trust monotonically increases during consistent positive interactions |
| B2: Creator stops producing | `test_behavior_b2_inactive_creator_decay` | Trust plateau then slow decline; inflection at boredom onset |
| B3: Sybil attack | `test_behavior_b3_sybil_near_zero` | Aggregate trust score stays near zero for isolated cluster |
| B4: Gradual trust building | `test_behavior_b4_logistic_curve` | Logistic-like trajectory over 1000 ticks |
| B5: One-hit wonder | `test_behavior_b5_peak_and_decline` | Peak higher initially, decline below sustained creator by tick 500 |
| B6: Trust exploitation | `test_behavior_b6_friction_spike_after_exploit` | Friction spikes within 2 ticks of exploit event |
| B9: Biometric value creation | `test_behavior_b9_bond_trust_from_biometric` | Bond link trust increases from biometric calibration |

---

## Configuration

All trust constants are environment-overridable via the `L1_` prefix pattern established in `constants.py`.

| Constant | Default | Env Var | Purpose |
|----------|---------|---------|---------|
| `TRUST_LEARNING_RATE` | 0.05 | `L1_TRUST_LEARNING_RATE` | Beta: trust growth rate |
| `FRICTION_LEARNING_RATE` | 0.08 | `L1_FRICTION_LEARNING_RATE` | Gamma: friction growth rate (negativity bias) |
| `TRUST_DECAY_RATE` | 0.002 | `L1_TRUST_DECAY_RATE` | Per-tick base trust decay |
| `TRUST_DISSOLUTION_THRESHOLD` | 0.01 | `L1_TRUST_DISSOLUTION_THRESHOLD` | Both weight AND trust below this → dissolve |
| `TRUST_SCORE_CACHE_TTL` | 60.0 | `L1_TRUST_SCORE_CACHE_TTL` | Seconds before trust score recomputes |
| `SYBIL_TIME_SPREAD_THRESHOLD` | 86400 | `L1_SYBIL_TIME_SPREAD_THRESHOLD` | Seconds; cluster creation within this = suspicious |
| `FREE_RIDER_FLOW_THRESHOLD` | 10.0 | `L1_FREE_RIDER_FLOW_THRESHOLD` | inbound/outbound ratio above this = free-rider signal |
| `AFFINITY_AVERSION_CAP` | 1.5 | `L1_AFFINITY_AVERSION_CAP` | V7: max sum of affinity + aversion |

---

## Design Patterns

### Architecture Pattern

**Pattern:** Module extension (not a new system). Trust mechanics extends the existing tick cycle through function injection at defined hook points.

**Why:** The ALGORITHM document states "No new steps are added. Trust mechanics piggyback on existing laws." Creating a separate trust engine would violate this principle and create a parallel system that drifts from the tick cycle.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Pure function | `compute_limbic_delta()`, `trust_score()` | No side effects, easy to test, easy to cache |
| Side-effect function | `update_link_trust()`, `decay_link_trust()` | Mutates link in-place (matches existing law pattern) |
| Strategy | `VALUE_TYPE_SIGNATURES` dict | New value types added by adding entries, not by modifying code |
| Cache with TTL | `trust_score_cached()` | Performance optimization that preserves correctness |

### Anti-Patterns to Avoid

- **Stored trust score:** Never persist `trust_score` on a node. Always compute from links. (V2)
- **Trust punishment:** Never decrease `link.trust` from a negative interaction. Only increase `link.friction`. (V12)
- **Fallback to default trust:** No fallback values. If links don't exist, trust is 0.0. Not a default like 0.5.
- **Separate trust engine:** Trust is NOT a standalone system. It runs inside the tick cycle. No separate tick loop.

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Trust module | limbic delta, trust update, score aggregation, detection | Tick cycle orchestration, propagation, WM selection | Public functions in `trust/__init__.py` |
| Value taxonomy | Classification, signatures | Graph physics, node creation | `classify_value_type()`, `get_signature()` |
| Pathology detection | Topological analysis | Economic penalties, access control | `PathologySignal` dataclass |

---

## State Management

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| Drive snapshots | `tick_runner._drives_before`, `._drives_after` | Per-tick | Created at step 1, consumed at step 17, discarded |
| Last limbic delta | `tick_runner._last_limbic_delta` | Per-tick | Computed at step 17, consumed at step 16 of next tick |
| Trust on links | `Link.trust`, `Link.friction` | Persistent (per-link) | Created with link, modified by Law 18, decayed by Law 7 |
| Trust score cache | `trust_score_aggregator._trust_score_cache` | In-memory | TTL-based, 60s default |
| Pathology signals | Returned from detector functions | Per-invocation | Not persisted; computed on demand |

### State Transitions

```
Link created (trust=0.5 default)
  → positive limbic_delta → trust increases (asymptotic)
  → negative limbic_delta → friction increases (trust unchanged)
  → no activation → trust decays (Law 7)
  → weight < 0.01 AND trust < 0.01 → link dissolved
```

---

## Module Dependencies

### Internal Dependencies

```
trust/
├── limbic_delta_from_drive_snapshots.py
│   └── imports → models.DriveSnapshot
├── trust_update_on_link.py
│   └── imports → models.Link
├── trust_score_aggregator.py
│   └── imports → models.CitizenCognitiveState
├── creator_attribution_cascade.py
│   └── imports → trust_update_on_link
│   └── imports → models.*
├── value_type_classifier.py
│   └── imports → models.Node, Modality
├── destruction_pathology_detector.py
│   └── imports → models.CitizenCognitiveState
├── trust_tempering.py
│   └── imports → models.Link
└── personhood_ladder_assessor.py
    └── imports → trust_score_aggregator
    └── imports → value_type_classifier
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| None | Trust module has zero external dependencies | N/A |

The trust module depends only on the cognition models and constants. No numpy, no sklearn, no external packages. This is intentional -- trust computations are simple arithmetic on link properties.

---

## BIDIRECTIONAL LINKS

### Code to Docs

| File | Reference |
|------|-----------|
| `trust/limbic_delta_from_drive_snapshots.py` | `# DOCS: docs/trust_mechanics/ALGORITHM_Trust_Mechanics.md section 1` |
| `trust/trust_update_on_link.py` | `# DOCS: docs/trust_mechanics/ALGORITHM_Trust_Mechanics.md section 2.1` |
| `trust/trust_score_aggregator.py` | `# DOCS: docs/trust_mechanics/ALGORITHM_Trust_Mechanics.md section 4` |
| `trust/creator_attribution_cascade.py` | `# DOCS: docs/trust_mechanics/ALGORITHM_Trust_Mechanics.md section 3` |
| `trust/value_type_classifier.py` | `# DOCS: docs/trust_mechanics/VALUE_CREATION_TAXONOMY.md` |
| `trust/destruction_pathology_detector.py` | `# DOCS: docs/trust_mechanics/ALGORITHM_Trust_Mechanics.md section 7` |
| `trust/trust_tempering.py` | `# DOCS: docs/trust_mechanics/ALGORITHM_Trust_Mechanics.md section 5` |

### Docs to Code

| Doc Section | Implemented In |
|-------------|----------------|
| ALGORITHM section 1 (Limbic Delta) | `trust/limbic_delta_from_drive_snapshots.py:compute_limbic_delta()` |
| ALGORITHM section 2.1 (Trust Update) | `trust/trust_update_on_link.py:update_link_trust()` |
| ALGORITHM section 2.4 (Sovereign Cascade) | `trust/trust_update_on_link.py:update_bond_trust_from_alignment()` |
| ALGORITHM section 3 (Creator Cascade) | `trust/creator_attribution_cascade.py:run_creator_attribution_cascade()` |
| ALGORITHM section 4.1 (Trust Score) | `trust/trust_score_aggregator.py:trust_score()` |
| ALGORITHM section 5 (Tempering) | `trust/trust_tempering.py:decay_link_trust()`, `boredom_moat_erosion()` |
| ALGORITHM section 7 (Detection) | `trust/destruction_pathology_detector.py:detect_*()` |
| VALIDATION V1-V14 | `tests/test_trust_mechanics/test_trust_invariants.py` |
| BEHAVIORS B1-B9 | `tests/test_trust_mechanics/test_behavior_*.py` |

---

## Review Issues Addressed

### From REVIEW_F3_F4_Coherence.md

| Issue | Resolution in Implementation |
|-------|------------------------------|
| #1 Biometric node type | Value type classifier handles state nodes (node_type=actor, type=partner_state) per F3 spec |
| #2 Limbic delta terminology | `compute_limbic_delta()` clearly named; F3's drive deltas are upstream inputs |
| #3 Privacy model conflict | Bond trust update is scoped to bond link only; `update_bond_trust_from_alignment()` operates on a single link |
| #4 Sovereign Cascade | `update_bond_trust_from_alignment()` implements the integration |
| #5 Voice/Desktop types | B4 and B5 value types in classifier |

### From REVIEW_F4_F5_Coherence.md

| Issue | Resolution in Implementation |
|-------|------------------------------|
| #1 Tick cycle numbering | Implementation uses schema-canonical ordering (LIMBIC_UPDATE at step 1) |
| #2 F4 tick numbering | Architecture section uses corrected step numbers |
| #3 Trust step misattributed | Trust update at step 4/16 (propagation/valence), NOT step 9 (consolidation) |
| #5 FalkorDB link fields | stability field added to Link model; required for `decay_link_trust()` |
| #6 Value creation integration | Value type classifier provides the integration point between F4 taxonomy and F5 tick cycle |
| #7 Limbic delta bounds | Corrected to [-2.5, +2.5] in `compute_limbic_delta()` |

---

## MARKERS

<!-- @mind:todo Add stability field to Link dataclass in models.py (required for trust decay computation) -->
<!-- @mind:todo Calibrate beta=0.05 and gamma=0.08 via simulation of B4 trajectory (OQ2 in SYNC) -->
<!-- @mind:escalation Trust Score aggregation method: weighted mean (v1) vs PageRank (v2). Implementation assumes weighted mean. Decision needed from Nicolas. (OQ1 in SYNC) -->
<!-- @mind:escalation Full Personhood Ladder 14-aspect mapping blocked on "Daughters (T7 Autonomy)" document. Current implementation covers 4 known aspects. (OQ4 in SYNC) -->
<!-- @mind:proposition Replace inline Law 7 forgetting in tick_runner.py with a proper law_07_forgetting.py module that includes trust decay. Current inline implementation (lines 407-452) is a candidate for extraction. -->
<!-- @mind:proposition Consider adding trust velocity tracking (ΔTrust over N ticks) as a first-class metric. Would improve D6 trust exploitation detection significantly. -->
