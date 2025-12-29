# Engine — Algorithm: Membrane Modulation Frame

```
STATUS: DRAFT
CREATED: 2025-12-20
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Membrane_Modulation.md
PATTERNS:        ./PATTERNS_Membrane_Scoping.md
BEHAVIORS:       ./BEHAVIORS_Membrane_Modulation.md
THIS:            ALGORITHM_Membrane_Modulation.md (you are here)
VALIDATION:      ./VALIDATION_Membrane_Modulation.md
IMPLEMENTATION:  ./IMPLEMENTATION_Membrane_Modulation.md
HEALTH:          ./HEALTH_Membrane_Modulation.md
SYNC:            ./SYNC_Membrane_Modulation.md

IMPL:            runtime/moment_graph/queries.py
IMPL:            runtime/moment_graph/surface.py
IMPL:            runtime/moment_graph/traversal.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

Compute a bounded, idempotent Modulation Frame from aggregate metrics. The
frame is cached per place for hot-path reads and never mutates canon state.

---

## DATA STRUCTURES

### ModulationFrame

```
weight_transfer_multiplier: float
decay_scale: float
dramatic_boost_scale: float
activation_threshold_offset: float
```

All values are bounded; defaults are neutral.

### MembraneContext

```
place_id: str
tick: int
active_density: float
possible_density: float
dramatic_pressure: float
surprise_rate: float
dominant_pressure_age: int
```

---

## ALGORITHM: compute_modulation_frame

### Step 0: Resolve Scope Key

Resolve `place_id` (or equivalent scene identifier) from the view context.
If no scope is available, return a neutral frame and skip caching.

### Step 1: Read Aggregates

Collect inexpensive aggregates (counts/ratios) from the graph state or view
build metrics. Do not query full graph.

### Step 2: Normalize Signals

Normalize aggregates into a small set of scalar signals (e.g., sparsity,
saturation, pressure density).

### Step 3: Produce Frame

Apply bounded transforms to produce modulation multipliers and offsets. Clamp
values to safe ranges.

```
frame = ModulationFrame(
  weight_transfer_multiplier=clamp(base * scale, min, max),
  decay_scale=clamp(...),
  dramatic_boost_scale=clamp(...),
  activation_threshold_offset=clamp(...)
)
```

### Step 4: Cache For Hot Path (Per Place)

Store the frame in a provider keyed by `place_id` for O(1) access by
traversal/surfacing code. Scene change resets or recomputes the key.

---

## KEY DECISIONS

### D1: Fail-Silent

```
IF place_id missing OR aggregates missing OR error:
    return ModulationFrame.neutral()
ELSE:
    compute bounded frame
```

### D2: Scope Isolation

```
IF place_id changes:
    discard prior frame for old place_id
    compute or set neutral frame for new place_id
```

---

## DATA FLOW

```
place_id + aggregates
    ↓
MembraneContext
    ↓
dynamic functions
    ↓
ModulationFrame (cached per place_id)
```

---

## COMPLEXITY

**Time:** O(k) — k = number of aggregates (constant-sized)

**Space:** O(1) — single frame cached

**Bottlenecks:**
- Overly expensive aggregation queries (avoid full scans)

---

## HELPER FUNCTIONS

### `clamp(value, min_value, max_value)`

**Purpose:** enforce safe bounds for modifiers.

### `activation_threshold(context, frame)`

**Purpose:** compute surfacing threshold from context and modifiers.

### `decay_scale(context, frame)`

**Purpose:** compute decay scaling without direct energy injection.

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| `runtime/moment_graph/queries.py` | `get_current_view` | aggregate metrics |
| `runtime/membrane/functions.py` | `activation_threshold` | dynamic thresholds |
| `runtime/membrane/provider.py` | `set_frame` | cached frame by place_id |

---

## MARKERS

<!-- @mind:todo Define aggregate metrics used for v0. -->
<!-- @mind:todo Document default bounds for each modifier. -->

---

## COMPUTE SKELETON (V0)

**Inputs:**
- place_id: str
- aggregates: Dict[str, float]
- tick: int

**Outputs:**
- ModulationFrame (bounded)

**Procedure:**
1) if not place_id: return neutral
2) ctx = MembraneContext(place_id=place_id, tick=tick, ...)
3) frame = ModulationFrame(
   weight_transfer_multiplier=...,
   decay_scale=...,
   dramatic_boost_scale=...,
   activation_threshold_offset=...
)
4) clamp all fields to bounds
5) cache under place_id  
