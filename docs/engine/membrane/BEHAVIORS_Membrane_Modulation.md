# Engine — Behaviors: Membrane Modulation Effects

```
STATUS: DRAFT
CREATED: 2025-12-20
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Membrane_Modulation.md
PATTERNS:        ./PATTERNS_Membrane_Scoping.md
THIS:            BEHAVIORS_Membrane_Modulation.md (you are here)
ALGORITHM:       ./ALGORITHM_Membrane_Modulation.md
VALIDATION:      ./VALIDATION_Membrane_Modulation.md
HEALTH:          ./HEALTH_Membrane_Modulation.md
SYNC:            ./SYNC_Membrane_Modulation.md

IMPL:            runtime/physics/tick.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS

### B1: Modulation Computed Outside Hot Path

```
GIVEN:  a stable graph snapshot or aggregate metrics for a tick
WHEN:   the system prepares a view or schedules a tick
THEN:   a Modulation Frame is computed and cached
AND:    traversal/surfacing never perform membrane computation
```

### B2: Modulation Is Bounded And Idempotent

```
GIVEN:  identical aggregate inputs
WHEN:   modulation is computed multiple times
THEN:   the same frame is returned
AND:    all modifiers remain within bounded ranges
```

### B3: Modulation Never Writes Canon

```
GIVEN:  a Modulation Frame is present
WHEN:   traversal/surfacing/decay executes
THEN:   modifiers only affect local parameters
AND:    no nodes, links, or statuses are written by the membrane
```

### B4: Traversal Reweights Transfer Only

```
GIVEN:  a click or wait-trigger traversal resolves a transition
WHEN:   weight_transfer is computed
THEN:   the transfer uses membrane multipliers
AND:    THEN links and status updates remain mechanical
```

### B5: Surfacing Offsets Thresholds Only

```
GIVEN:  surfacing checks evaluate possible moments
WHEN:   check_for_flips runs
THEN:   activation thresholds apply membrane offsets
AND:    flips still depend on the mechanical condition
```

### B6: Decay Applies Scale Only

```
GIVEN:  decay runs for energy and moments
WHEN:   decay rates are applied
THEN:   rates are scaled by membrane modifiers
AND:    decayed threshold logic remains unchanged
```

### B7: Player View Remains Moment-Only

```
GIVEN:  a view request for player-visible state
WHEN:   get_current_view is called
THEN:   the payload contains Moments and transitions only
AND:    membrane metadata is never exposed
```

### B8: Dynamic Functions Replace Constants

```
GIVEN:  runtime parameters that affect surfacing/traversal
WHEN:   parameters are resolved
THEN:   values are computed via functions of context + frame
AND:    outputs are clamped to documented bounds
```

### B9: Momentum Biases Without Forcing

```
GIVEN:  a dominant pressure persists across ticks
WHEN:   membrane state updates
THEN:   modifiers may shift toward higher movement
AND:    no direct activation or canon writes occur
```

### B10: Membrane Is Scoped Per Place

```
GIVEN:  a scene is identified by place_id (or equivalent scope key)
WHEN:   membrane state is resolved
THEN:   modulation is read from the local place-scoped frame only
AND:    scene changes reset or recompute membrane state
```

---

## INPUTS / OUTPUTS

### Primary Function: `compute_modulation_frame()` (planned)

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| aggregates | dict | Counts/ratios for possible/active/spoken, pressure summary |
| tick | int | Current tick counter |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| frame | ModulationFrame | Bounded multipliers and offsets |

**Side Effects:**

- Writes the cached frame for hot-path read

---

## EDGE CASES

### E1: Frame Missing

```
GIVEN:  membrane errors or returns None
THEN:   runtime uses neutral modifiers (1.0 / 0.0)
```

### E2: Extreme Graph States

```
GIVEN:  sparse or saturated moment sets
THEN:   membrane may counter-bias within bounds
```

---

## ANTI-BEHAVIORS

### A1: Canon Mutation

```
GIVEN:   a modulation frame is applied
WHEN:    traversal or surfacing runs
MUST NOT: create links, create moments, or change statuses directly
INSTEAD:  only modify local parameters
```

### A2: Hot-Path Computation

```
GIVEN:   traversal/surfacing execution
WHEN:    membrane logic is invoked
MUST NOT: call LLMs or compute heavy aggregates
INSTEAD:  read cached modulation only
```

---

## MARKERS

<!-- @mind:todo Define bounded ranges for each modifier. -->
<!-- @mind:todo Decide whether modulation applies pre- or post-decay. -->
<!-- @mind:proposition Add debug sampling of applied frames. -->
