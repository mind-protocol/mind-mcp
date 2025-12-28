# Energy Physics — Validation: Invariants and Criteria

```
@mind:id: VALIDATION.PHYSICS.ENERGY.V1.2
CREATED: 2024-12-23
STATUS: DESIGNING
```

---

## CHAIN

```
PATTERNS:       ./PATTERNS_Physics.md
BEHAVIORS:      ./BEHAVIORS_Physics.md
ALGORITHM:       ./ALGORITHM_Physics.md
IMPLEMENTATION:  ./IMPLEMENTATION_Physics.md
THIS:            VALIDATION_Energy_Physics.md
HEALTH:         ./HEALTH_Energy_Physics.md
SYNC:           ./SYNC_Physics.md
```

---

## PURPOSE

This document defines the invariants that MUST hold for the energy physics system.
Every invariant has a unique @mind:id anchor for traceability to IMPLEMENTATION and HEALTH.

---

## LINK TYPE REFERENCE

### Energy Flow Links

| Type | From → To | Energy Phase | Replaces |
|------|-----------|--------------|----------|
| `expresses` | Actor → Moment | Draw | CAN_SPEAK |
| `about` | Moment → Any | Flow | ATTACHED_TO |
| `relates` | Any → Any | Flow, Backflow | BELIEVES, ORIGINATED, ABOUT, SUPPORTS, CONTRADICTS, ELABORATES, SUBSUMES, SUPERSEDES |
| `attached_to` | Thing → Actor/Space | Flow | CARRIES (inverted) |

### Structural Links (No Energy)

| Type | From → To | Replaces |
|------|-----------|----------|
| `contains` | Space → Actor/Thing | AT (inverted) |
| `leads_to` | Space → Space | — |
| `sequence` | Moment → Moment | THEN |
| `primes` | Moment → Moment | CAN_LEAD_TO |
| `can_become` | Thing → Thing | — |

### Semantic Differentiation via Properties

Old type distinctions become link properties:

```yaml
# Role property replaces BELIEVES vs ORIGINATED vs witness
relates:
  role: originator | believer | witness | subject | creditor | debtor

# Emotions + direction replace SUPPORTS vs CONTRADICTS
relates:
  direction: support | oppose | elaborate | subsume | supersede
  emotions: [[alignment, 0.8]] or [[opposition, 0.9]]
```

---

## ENERGY CONSERVATION

### @mind:id: V-ENERGY-BOUNDED
**Total system energy stays within operational bounds**

```yaml
invariant: V-ENERGY-BOUNDED
priority: HIGH
criteria: |
  Total energy across all nodes and links stays within [MIN_SYSTEM_ENERGY, MAX_SYSTEM_ENERGY]
  where MIN = 0 and MAX = (actor_count × MAX_ACTOR_ENERGY) + (moment_count × MAX_MOMENT_ENERGY)
verified_by:
  health: mind/graph/health/check_health.py::energy_balance_checker
  confidence: needs-health
evidence:
  - energy_balance_checker compares tick snapshots
  - alert if ratio outside [0.8, 1.2]
failure_mode: |
  Unbounded growth: world becomes unstable
  Unbounded decay: world goes dead
```

### @mind:id: V-ENERGY-CONSERVED
**Energy change per tick matches expected flows**

```yaml
invariant: V-ENERGY-CONSERVED
priority: HIGH
criteria: |
  delta_energy = generation - strength_conversion
  Actual delta matches expected delta within 5% tolerance
verified_by:
  health: mind/graph/health/check_health.py::energy_conservation_checker
  confidence: needs-health
evidence:
  - Snapshot before/after tick
  - Calculate expected from generation and cooling formulas
failure_mode: |
  Leak: energy disappears (formula error in cooling)
  Accumulation: energy appears from nowhere (double-counting)
```

### @mind:physics:energy:invariant:V-ENERGY-NON-NEGATIVE
### @mind:physics:energy:test:test_energy_lifecycle
### @mind:physics:energy:health:no_negative_checker
**All energy values >= 0**

```yaml
invariant: V-ENERGY-NON-NEGATIVE
priority: HIGH
criteria: |
  For all nodes: node.energy >= 0
  For all links: link.energy >= 0
verified_by:
  test: mind/tests/test_energy_v1_2.py::TestNoDecay::test_energy_lifecycle
  confidence: partial
evidence:
  - Scan all energy values every tick
  - Immediate alert on first negative
failure_mode: |
  Negative energy breaks all formulas
  Indicates draw exceeded available (missing guard)
```

---

## LINK STATE INTEGRITY

### @mind:id: V-LINK-ALIVE
**At least 10% of links remain hot during active scene**

```yaml
invariant: V-LINK-ALIVE
priority: HIGH
criteria: |
  hot_ratio = count(links where energy × weight > COLD_THRESHOLD) / total_links
  hot_ratio >= 0.1 during any scene with active moments
verified_by:
  health: mind/graph/health/check_health.py::hot_ratio_checker
  confidence: needs-health
evidence:
  - Moving average over 10 ticks
  - Alert if ratio < 0.1
failure_mode: |
  All links cold = dead world
  Physics stops running, narrative freezes
```

### @mind:id: V-LINK-BOUNDED
**No more than 50% of links hot (memory bounded)**

```yaml
invariant: V-LINK-BOUNDED
priority: HIGH
criteria: |
  hot_ratio <= 0.5 under normal operation
  hot_ratio <= 0.8 under peak load
verified_by:
  health: mind/graph/health/check_health.py::hot_ratio_checker
  confidence: needs-health
evidence:
  - Moving average over 10 ticks
  - Warn if ratio > 0.5, alert if > 0.8
failure_mode: |
  Memory pressure from too many active links
  Physics tick time grows unbounded
```

### @mind:physics:energy:invariant:V-LINK-STRENGTH-GROWTH
### @mind:physics:energy:test:test_strength_growth_formula
### @mind:physics:energy:test:test_strength_diminishing_returns
**Link strength grows according to formula**

```yaml
invariant: V-LINK-STRENGTH-GROWTH
priority: MED
criteria: |
  growth = (amount × emotion_intensity × origin.weight) / ((1 + strength) × target.weight)
  Actual growth matches expected within 1% tolerance (float precision)
verified_by:
  test: mind/tests/test_energy_v1_2.py::TestLinkCooling::test_strength_growth_formula
  test: mind/tests/test_energy_v1_2.py::TestLinkCooling::test_strength_diminishing_returns
  confidence: high
evidence:
  - Sample 100 random traversals per tick
  - Compare expected vs actual growth
failure_mode: |
  Zero growth: no persistent memory forming
  Runaway growth: strength overflow or wrong formula
```

---

## TICK EXECUTION

### @mind:id: V-TICK-ORDER
**Phases execute in correct sequence**

```yaml
invariant: V-TICK-ORDER
priority: HIGH
criteria: |
  Phase execution order: Generate → Draw → Flow → Interaction → Backflow → Link Cooling
  Timestamps: phase_1_start < phase_2_start < ... < phase_6_end
verified_by:
  test: TODO::test_phases_execute_in_order
  confidence: untested
evidence:
  - Instrument phase start/end timestamps
  - Verify monotonically increasing
failure_mode: |
  Out-of-order: wrong physics (draw before generate = overdraw)
  Concurrency bug or code refactoring error
```

### @mind:id: V-TICK-COMPLETE
**Every tick completes all phases**

```yaml
invariant: V-TICK-COMPLETE
priority: HIGH
criteria: |
  If tick starts, all 6 phases execute
  No partial ticks (exception handling must complete or rollback)
verified_by:
  test: TODO::test_tick_completes_all_phases
  confidence: untested
evidence:
  - Phase completion flags
  - Tick end marker present
failure_mode: |
  Partial tick: graph in invalid state
  Subsequent ticks may crash or produce wrong results
```

---

## MOMENT LIFECYCLE

### @mind:physics:energy:invariant:V-MOMENT-TRANSITIONS
### @mind:physics:energy:test:test_support_threshold
### @mind:physics:energy:test:test_contradict_threshold
**Only allowed state transitions occur**

```yaml
invariant: V-MOMENT-TRANSITIONS
priority: HIGH
criteria: |
  Allowed transitions:
    possible → active
    possible → rejected
    active → completed
    active → interrupted
    active → overridden
  Terminal states: completed, rejected, interrupted, overridden
verified_by:
  test: mind/tests/test_energy_v1_2.py::TestMomentInteraction::test_support_threshold
  test: mind/tests/test_energy_v1_2.py::TestMomentInteraction::test_contradict_threshold
  confidence: partial
evidence:
  - Log all transitions
  - Reject any not in allowed set
failure_mode: |
  Invalid transition: narrative incoherence
  E.g., completed → possible would resurrect dead moments
```

### @mind:id: V-MOMENT-DRAW-BOUNDS
**Moment draw doesn't exceed available energy**

```yaml
invariant: V-MOMENT-DRAW-BOUNDS
priority: HIGH
criteria: |
  For each draw: draw_amount <= actor.energy
  After draw: actor.energy >= 0
verified_by:
  test: TODO::test_draw_clamps_to_available
  confidence: untested
evidence:
  - Guard check before each draw
  - Clamp if would exceed
failure_mode: |
  Overdraw: negative actor energy
  Breaks subsequent calculations
```

### @mind:physics:energy:invariant:V-MOMENT-DURATION-RATE
### @mind:physics:energy:test:test_radiation_rate_formula
**Radiation rate matches declared duration**

```yaml
invariant: V-MOMENT-DURATION-RATE
priority: MED
criteria: |
  radiation_rate = 1 / (duration_minutes × TICKS_PER_MINUTE)
  Actual flow per tick matches expected rate
verified_by:
  test: mind/tests/test_energy_v1_2.py::TestFlowFormulas::test_radiation_rate_formula
  confidence: high
evidence:
  - Sample moment flows
  - Compare to declared duration
failure_mode: |
  Wrong rate: moments complete too fast or linger forever
  Narrative pacing breaks
```

---

## GENERATION & PROXIMITY

### @mind:physics:energy:invariant:V-GEN-PROXIMITY-BOUNDS
### @mind:physics:energy:test:test_proximity_formula
**Proximity values in [0, 1]**

```yaml
invariant: V-GEN-PROXIMITY-BOUNDS
priority: MED
criteria: |
  proximity = 1 / (1 + path_resistance)
  For all actors: 0 <= proximity <= 1
  Player proximity = 1.0 (self)
verified_by:
  test: mind/tests/test_energy_v1_2.py::TestFlowFormulas::test_proximity_formula
  confidence: high
evidence:
  - Check proximity calculations
  - Alert if outside bounds
failure_mode: |
  Proximity > 1: over-generation
  Proximity < 0: mathematically impossible, indicates bug
```

### @mind:id: V-GEN-PROXIMITY-CORRELATION
**Proximity correlates with graph distance**

```yaml
invariant: V-GEN-PROXIMITY-CORRELATION
priority: MED
criteria: |
  Actors closer in graph (fewer hops, lower resistance) have higher proximity
  Pearson correlation between (1/hops) and proximity > 0.7
verified_by:
  health: mind/graph/health/check_health.py::proximity_correlation_checker
  confidence: needs-health
evidence:
  - Sample actor pairs
  - Compute correlation
failure_mode: |
  Low correlation: path resistance calculation wrong
  Distant actors generating as if close
```

---

## TOP-N FILTER

### @mind:id: V-TOPN-CRITICAL
**Critical links not excluded by filter**

```yaml
invariant: V-TOPN-CRITICAL
priority: MED
criteria: |
  Links with energy × weight in top 20 for a node are never excluded
  Player→moment links for active moments always included
verified_by:
  test: TODO::test_topn_includes_critical_links
  confidence: untested
evidence:
  - Check filter output includes expected high-priority links
  - Sample per tick
failure_mode: |
  Critical link excluded: narrative hole
  Important moment or actor ignored
```

### @mind:id: V-TOPN-DETERMINISTIC
**Filter produces same result for same input**

```yaml
invariant: V-TOPN-DETERMINISTIC
priority: LOW
criteria: |
  Given same link energies and weights, filter returns same set
  Tie-breaking is deterministic (by link ID)
verified_by:
  test: TODO::test_topn_deterministic
  confidence: untested
evidence:
  - Run filter twice on same input
  - Compare results
failure_mode: |
  Non-deterministic: unpredictable physics
  Hard to debug and reproduce issues
```

---

## BACKFLOW GATING

### @mind:id: V-BACKFLOW-GATED
**Backflow only to focused characters**

```yaml
invariant: V-BACKFLOW-GATED
priority: MED
criteria: |
  Backflow only occurs if link.energy > 0
  Characters with cold narrative links receive 0 backflow
verified_by:
  test: TODO::test_backflow_only_to_hot_links
  confidence: untested
evidence:
  - Check backflow recipients have hot links
  - Zero backflow to cold-linked actors
failure_mode: |
  Backflow to unfocused: narrative themes press on wrong characters
  Breaks character-centric attention model
```

---

## CRYSTALLIZATION

### @mind:id: V-CRYSTAL-ON-COMPLETE
**Actor↔actor links created on moment completion**

```yaml
invariant: V-CRYSTAL-ON-COMPLETE
priority: MED
criteria: |
  When moment completes:
    For each pair of actors sharing the moment:
      If no existing relates link → create one
      Link inherits moment emotions
verified_by:
  test: TODO::test_crystallize_creates_actor_links
  confidence: untested
evidence:
  - Check for new links after completion
  - Verify emotion inheritance
failure_mode: |
  No crystallization: shared experiences don't build relationships
  Missing link = broken path for future traversals
```

---

## EMOTION HANDLING

### @mind:physics:energy:invariant:V-EMOTION-BASELINE
### @mind:physics:energy:test:test_emotion_proximity_empty
### @mind:physics:energy:test:test_avg_emotion_intensity_empty
**Empty emotions use baseline proximity**

```yaml
invariant: V-EMOTION-BASELINE
priority: LOW
criteria: |
  If link.emotions is empty, emotion_proximity = 0.2 (baseline)
  Not 0 (would block all flow) or 1 (would over-amplify)
verified_by:
  test: mind/tests/test_energy_v1_2.py::TestEmotionFunctions::test_emotion_proximity_empty
  test: mind/tests/test_energy_v1_2.py::TestEmotionFunctions::test_avg_emotion_intensity_empty
  confidence: high
evidence:
  - Test with empty emotion links
  - Verify baseline applied
failure_mode: |
  Zero baseline: new links can't flow energy
  High baseline: over-amplification of uncolored links
```

### @mind:physics:energy:invariant:V-EMOTION-BLEND
### @mind:physics:energy:test:test_blend_emotions_same_emotion
### @mind:physics:energy:test:test_blend_emotions_new_emotion
### @mind:physics:energy:test:test_blend_emotions_max_cap
**Emotion blending preserves intensity sum**

```yaml
invariant: V-EMOTION-BLEND
priority: LOW
criteria: |
  After blending: sum(new_intensities) ≈ sum(old_intensities) (within 10%)
  No emotion intensity > 1.0
  No emotion intensity < 0.0
verified_by:
  test: mind/tests/test_energy_v1_2.py::TestEmotionFunctions::test_blend_emotions_same_emotion
  test: mind/tests/test_energy_v1_2.py::TestEmotionFunctions::test_blend_emotions_new_emotion
  test: mind/tests/test_energy_v1_2.py::TestEmotionFunctions::test_blend_emotions_max_cap
  confidence: high
evidence:
  - Sample blend operations
  - Check intensity bounds
failure_mode: |
  Intensity explosion: emotions grow unbounded
  Intensity collapse: all emotions fade to zero
```

---

## VALIDATION ID INDEX

| ID | Category | Priority |
|----|----------|----------|
| V-ENERGY-BOUNDED | Conservation | HIGH |
| V-ENERGY-CONSERVED | Conservation | HIGH |
| V-ENERGY-NON-NEGATIVE | Conservation | HIGH |
| V-LINK-ALIVE | Link State | HIGH |
| V-LINK-BOUNDED | Link State | HIGH |
| V-LINK-STRENGTH-GROWTH | Link State | MED |
| V-TICK-ORDER | Tick Execution | HIGH |
| V-TICK-COMPLETE | Tick Execution | HIGH |
| V-MOMENT-TRANSITIONS | Moment Lifecycle | HIGH |
| V-MOMENT-DRAW-BOUNDS | Moment Lifecycle | HIGH |
| V-MOMENT-DURATION-RATE | Moment Lifecycle | MED |
| V-GEN-PROXIMITY-BOUNDS | Generation | MED |
| V-GEN-PROXIMITY-CORRELATION | Generation | MED |
| V-TOPN-CRITICAL | Filter | MED |
| V-TOPN-DETERMINISTIC | Filter | LOW |
| V-BACKFLOW-GATED | Backflow | MED |
| V-CRYSTAL-ON-COMPLETE | Crystallization | MED |
| V-EMOTION-BASELINE | Emotions | LOW |
| V-EMOTION-BLEND | Emotions | LOW |

---

## MARKERS

<!-- @mind:todo Implement health checkers for all HIGH priority validations -->
<!-- @mind:todo Add integration tests for tick phase ordering -->
<!-- @mind:todo Define exact numeric thresholds through playtesting -->
<!-- @mind:todo Add validation for agent-physics boundary (agents don't manipulate energy) -->
