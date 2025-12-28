# Tempo Controller — Algorithm: Tick Loop and Pacing

```
STATUS: DRAFT
CREATED: 2025-12-20
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Tempo.md
BEHAVIORS:       ./BEHAVIORS_Tempo.md
THIS:            ALGORITHM_Tempo_Controller.md (you are here)
VALIDATION:      ./VALIDATION_Tempo.md
HEALTH:          ./HEALTH_Tempo.md
SYNC:            ./SYNC_Tempo.md

IMPL:            mind/infrastructure/tempo/tempo_controller.py (planned)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

The Tempo Controller maintains the main loop cadence. It sleeps according to
speed mode, advances physics, and invokes canon surfacing. The loop does not
block on narrator output or external calls beyond physics and canon hooks.

---

## DATA STRUCTURES

### TempoState

```
TempoState:
  speed: enum
  running: bool
  tick_count: int
  last_tick_at: float
```

### TickResult (abstract)

```
TickResult:
  flips: list
  canon_count: int
  tick_at: float
```

---

## ALGORITHM: run

### Step 1: Resolve Speed Mode

Select the mode behavior based on `speed` (pause, 1x, 2x, 3x).
Modes define stop conditions, not just intervals.

### Step 2: Tick Loop

Iterate ticks according to mode rules:
- pause: run one tick, return no moment
- 1x: stop when a player-linked moment flips
- 2x: continue past player-linked flip, stop on interrupting flip
- 3x: run as fast as possible, stop on interrupting flip, then set speed to 1x

### Step 3: Physics Tick

Invoke physics to update energy, pressure, and detect flips.

### Step 4: Canon Scan

Invoke canon holder to surface a bounded set of moments.

### Step 5: Emit Tick Result

Return or log the tick result for monitoring.

---

## KEY DECISIONS

### D1: Pause Behavior

```
IF speed == pause:
    run exactly one tick
    return no player-visible moment
ELSE:
    continue tick cadence
```

### D2: Stop Conditions

```
IF speed == 1x AND player-linked moment flips:
    stop ticking
IF speed == 2x AND interrupting player-linked moment flips:
    stop ticking
IF speed == 3x AND interrupting player-linked moment flips:
    set speed = 1x and stop ticking
```

---

## DATA FLOW

```
TempoState + speed
    ↓
Mode rules
    ↓
Physics tick
    ↓
Canon surfacing
    ↓
TickResult
```

---

## COMPLEXITY

**Time:** O(1) per tick (excludes physics/canon internal cost)

**Space:** O(1)

**Bottlenecks:**
- Canon scan if it queries large possible-moment sets

---

## HELPER FUNCTIONS

### `_tick_interval(speed)`

**Purpose:** Map speed mode to a tick interval.

### `_should_backpressure(backlog)`

**Purpose:** Avoid overload by slowing the loop when output queues are saturated.

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| `mind/physics/tick.py` | `GraphTick.run()` | flips + energy stats |
| `mind/infrastructure/canon/` | `record_to_canon()` | surfaced moments |

---

## MARKERS

<!-- @mind:todo Define default interval values for each speed. -->
<!-- @mind:todo Decide pause behavior for pending canon outputs. -->
