# Engine — Patterns: Membrane Modulation (Pre-Runtime Field Shaping)

```
STATUS: DRAFT
CREATED: 2025-12-20
```

---

## CHAIN

```
THIS:            PATTERNS_Membrane_Modulation.md (you are here)
BEHAVIORS:       ./BEHAVIORS_Membrane_Modulation.md
ALGORITHM:       ./ALGORITHM_Membrane_Modulation.md
VALIDATION:      ./VALIDATION_Membrane_Modulation.md
HEALTH:          ./HEALTH_Membrane_Modulation.md
SYNC:            ./SYNC_Membrane_Modulation.md

IMPL:            mind/physics/tick.py
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read the linked IMPL source file

**After modifying this doc:**
1. Update the IMPL source file to match, OR
2. Add a TODO in SYNC_*.md: "Docs updated, implementation needs: membrane modulation hook"
3. Run tests: `mind validate`

**After modifying the code:**
1. Update this doc chain to match, OR
2. Add a TODO in SYNC_*.md: "Implementation changed, docs need: membrane modulation updates"
3. Run tests: `mind validate`

---

## THE PROBLEM

The moment engine must remain:
- Instant (<50ms hot path, no LLM)
- Locally deterministic (graph-backed state transitions)
- Player-legible (Moments are the only visible narrative artifact)

At the same time, long-form play needs tension shaping, delayed interpretation,
and avoidance of premature closure. Direct orchestration or late-stage agent
reasoning would violate core runtime patterns.

---

## THE PATTERN

Introduce a **Membrane**: a pre-runtime modulation layer that adjusts existing
mechanical parameters without altering graph topology or canon state.

The Membrane:
- Does not create nodes, links, or moments
- Does not change moment status directly
- Does not generate player-facing text
- Does not inject energy

It only re-weights how existing forces interact (thresholds, transfer factors,
decay, pressure scaling) so deterministic mechanics operate in a biased field.

**Position in the system:**

```
[ Graph State ]
      ↓
[ Aggregation / Diagnostics ]
      ↓
[ Membrane Modulation ]
      ↓
[ Physics / Traversal / Surfacing ]
      ↓
[ Moments (player-visible) ]
```

---

## PRINCIPLES

### Principle 1: No Runtime Coupling

The Membrane must run outside traversal/surfacing. Hot-path code only consumes
numeric modifiers already computed.

Why this matters: preserves instant traversal guarantees.

### Principle 2: No Canon Mutation

The Membrane never mutates graph structure or moment status. It only modulates
existing numeric parameters.

Why this matters: preserves replayable, graph-backed determinism.

### Principle 3: Player-Invisible Effects

Membrane outputs are not player-visible. The player only sees Moments that
emerge from standard runtime logic.

Why this matters: preserves narrative legibility and avoids meta-signal leaks.

### Principle 4: No Magic Constants

Any runtime parameter that affects surfacing or traversal must be expressed as
a function of membrane context, even if the default function returns a constant.

Why this matters: enables safe modulation, observability, and future tuning
without breaking determinism.

### Principle 5: Bounded Momentum

The membrane may keep a small non-canon state (e.g., dominant pressure age) to
avoid under-modulation plateaus, but outputs remain bounded and indirect.

Why this matters: prevents stagnation without introducing fiat outcomes.

---

## DATA

| Source | Type | Purpose / Description |
|--------|------|-----------------------|
| Aggregated moment stats | OTHER | Possible/active ratios, density, surprise proxies |
| Pressure summaries | OTHER | Dominant pressure id, value, age |
| Membrane state | OTHER | Bounded, non-canon momentum counters |
| Runtime parameters | OTHER | Current surface/decay/transfer defaults |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `mind/physics/tick.py` | Applies per-tick thresholds and decay rates |
| `mind/moment_graph/*` | Consumes transfer coefficients and traversal thresholds |
| `docs/mind/moment-graph-mind/PATTERNS_Instant_Traversal_Moment_Graph.md` | Hot path constraints |
| `docs/physics/PATTERNS_Physics.md` | Energy and canon constraints |
| `docs/mind/moments/PATTERNS_Moments.md` | Player-visible artifact constraints |

---

## INSPIRATIONS

- Graph-native schedulers where structure drives outcomes.
- Control systems that bias rates instead of altering state.

---

## SCOPE

### In Scope

- Modulating weights, thresholds, decay, and pressure scaling.
- Producing idempotent numeric frames that can be cached or dropped.
- Operating strictly outside traversal/surfacing hot paths.

### Out of Scope

- Creating or deleting graph entities.
- Directly setting energy, status, or canon history.
- Narrative generation or player-facing text.

---

## MARKERS

<!-- @mind:todo Define the Modulation Frame schema and bounds. -->
<!-- @mind:todo Decide where modulation is applied in tick order (pre- or post-decay). -->
<!-- @mind:todo Add a health check for over/under-modulation. -->
<!-- @mind:todo Document membrane momentum state and decay rules. -->
