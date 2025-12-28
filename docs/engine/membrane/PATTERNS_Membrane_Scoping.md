# Engine — Patterns: Membrane Scoping (Per-Place Modulation)

```
STATUS: DRAFT
CREATED: 2025-12-20
VERIFIED: 2025-12-20 against local tree
```

---

## CHAIN

```
THIS:            PATTERNS_Membrane_Scoping.md (you are here)
BEHAVIORS:       ./BEHAVIORS_Membrane_Modulation.md
ALGORITHM:       ./ALGORITHM_Membrane_Modulation.md
VALIDATION:      ./VALIDATION_Membrane_Modulation.md
HEALTH:          ./HEALTH_Membrane_Modulation.md
SYNC:            ./SYNC_Membrane_Modulation.md

IMPL:            mind/moment_graph/queries.py
IMPL:            mind/moment_graph/surface.py
IMPL:            mind/membrane/functions.py
IMPL:            mind/physics/tick.py
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first.
2. Read the linked IMPL source files (queries, surface, membrane functions, physics tick).

**After modifying this doc:**
1. Update the corresponding implementation(s) to match, or note the drift in `SYNC_Membrane_Modulation.md`.
2. For membrane scoping updates, make sure the moment-graph framing code honors the place-scoped state.
3. For dynamic modulation function updates, align `mind/membrane/functions.py` and `mind/physics/tick.py`, or add a TODO in `SYNC_Membrane_Modulation.md` describing the needed hook.
4. Run `mind validate`.

**After modifying the code:**
1. Update this doc chain to match, or add a TODO in `SYNC_Membrane_Modulation.md` ("Implementation changed, docs need: membrane scoping/dynamic modulation update").
2. Run `mind validate`.

---

## THE PROBLEM

Membrane modulation is defined as a non-canon, pre-runtime layer that biases parameters without mutating graph state. What remains ambiguous is scope.

If the membrane is global, modulation leaks across unrelated scenes. If it is per-transition, complexity and debugging costs explode.

Runtime constants (thresholds, decay, transfer) behave like hidden policy when they are hard-coded, which makes the system fragile and opaque.

The system needs a scoping rule that preserves locality and aligns with scene-based queries while keeping every runtime parameter expressible as an observable function.

---

## THE PATTERN

### Membrane Scoping Pattern

Scope the Membrane **per Place / Scene**, not globally and not per edge.

Each Place maintains its own Membrane State derived from local aggregates (dramatic pressure, activity density, recurrence, character presence).

Membrane State:
- persists only while the player is in the same Place
- is reset or recomputed on scene change
- never propagates automatically to other Places

The membrane is local climate, not global weather.

### Dynamic Modulation Function Pattern

Replace magic constants with **dynamic modulation functions**. Every parameter that affects surfacing, traversal, or modulation is expressed as `f(context, frame)` even when the default implementation returns a constant.

The context inputs are aggregates computed outside the hot path so that tuning remains deterministic and explainable.

---

## PRINCIPLES

### Principle 1: Locality First

Membrane modulation is keyed by `place_id` (or scene identifier). This preserves local causality and prevents global mood leaks.

### Principle 2: Scene-Bound Persistence

Membrane state persists only within a scene and resets on scene change to avoid hidden long-range coupling between locations.

### Principle 3: Graph-Only Transfer

Cross-place influence is allowed only if encoded in the graph itself, keeping modulation effects explainable and deterministic.

### Principle 4: Functions Over Constants

Parameters that shape narrative flow must be functions, not literals, to keep modulation explicit and tunable.

### Principle 5: Context Is Aggregated, Not Canon

Context inputs should be aggregate metrics (expressed as `MembraneContext`) computed outside the hot path so the functions remain deterministic.

### Principle 6: Bounded Outputs

Dynamic functions must clamp results to safe ranges to prevent runaway behavior or hidden bias.

---

## DATA

| Source | Type | Purpose / Description |
|--------|------|-----------------------|
| `place_id` from scene queries | OTHER | Scope key for membrane state |
| Local moment aggregates | OTHER | Active/possible density, recurrence |
| Local pressure summaries | OTHER | Pressure, dominant pressure age |
| Local presence (AT links) | OTHER | Character presence signal |
| `MembraneContext` | OTHER | Aggregates (density, pressure, surprise, age) used by dynamic functions |
| `ModulationFrame` | OTHER | External modifiers applied to dynamic parameter functions |

### Dynamic Function Inputs

Dynamic modulation functions rely on the `MembraneContext` aggregates above plus the temporary modifiers captured by the `ModulationFrame` (bias, cascade, highlight, transfer). Keep the aggregator computation outside the hot path and declare the frame keys inside the doc so tuning remains visible rather than hidden in literals.

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `mind/moment_graph/queries.py` | Provides scene scope and local aggregates |
| `mind/moment_graph/surface.py` | Scene changes and surfacing context |
| `mind/membrane/functions.py` | Hosts the dynamic parameter functions that replace magic constants |
| `mind/physics/tick.py` | Applies the modulation frame during traversal and uses the dynamic thresholds/decays |
| `docs/mind/moment-graph-mind/PATTERNS_Instant_Traversal_Moment_Graph.md` | Hot path constraints |
| `docs/physics/PATTERNS_Physics.md` | Determinism and canon invariants |

---

## INSPIRATIONS

- Local climate models that do not imply global weather.
- Scene-based simulation boundaries in world runners.
- Control systems where rates are functions of state, not constants.
- Simulation engines that separate policy from state.

---

## SCOPE

### In Scope

- Per-place membrane instances keyed by scene identifier.
- Local aggregates used to compute modulation frames.
- Reset/recompute behavior on scene change.
- Thresholds, decay rates, transfer factors expressed as functions.
- Context aggregation outside the hot path to feed functions.
- Bounded modulation outputs that keep the system stable.

### Out of Scope

- Global membrane state shared across all places.
- Player-attached modulation state.
- Per-transition membrane instances.
- Canon state mutation.
- LLM-driven runtime decisions.
- Graph schema changes.

---

## MARKERS

<!-- @mind:todo Define cache invalidation rules for per-place frames. -->
<!-- @mind:todo Decide whether we cache neutral frames or compute fresh ones on scene entry. -->
<!-- @mind:todo Define the canonical `MembraneContext` fields. -->
<!-- @mind:todo Document default bounds for every dynamic function. -->
<!-- @mind:proposition Debug archive of per-place membrane frames (non-canon). -->
<!-- @mind:escalation Which graph-encoded signals should carry cross-place influence? -->
