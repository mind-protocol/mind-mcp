# Physics — Validation: Attention Split + Interrupt Invariants

```
STATUS: DRAFT
CREATED: 2025-12-20
VERIFIED: 2025-12-20 against local tree
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Attention_Energy_Split.md
                 ../../mind/moment-graph-mind/PATTERNS_Instant_Traversal_Moment_Graph.md
BEHAVIORS:       ./BEHAVIORS_Attention_Split_And_Interrupts.md
                 ../../mind/membrane/BEHAVIORS_Membrane_Modulation.md
THIS:            VALIDATION_Attention_Split_And_Interrupts.md
IMPL:            ../../../mind/physics/attention_split_sink_mass_distribution_mechanism.py
                 ../../../mind/physics/tick.py
                 ../../../mind/moment_graph/surface.py
                 ../../../mind/moment_graph/traversal.py
                 ../../../mind/moment_graph/queries.py
                 ../../../mind/infrastructure/canon/canon_holder.py
                 ../../../mind/world_builder/*
```

---

## BEHAVIORS GUARANTEED

| Behavior ID | Behavior | Why This Validation Matters |
|-------------|----------|-----------------------------|
| B1 | Attention redistribution each tick | Ensures split_fn is deterministic and sink set is correct |
| B2 | Arrival/witness creates new sink | Prevents missing causal attention shifts |
| B3 | Interrupt on focus reconfiguration | Locks binary interrupt rule |
| B4 | Non-interrupt flips keep acceleration | Prevents cooldown heuristics |
| B5 | CONTRADICTS visibility interrupts | Guarantees contradiction awareness |
| B6 | Void pressure can create a sink | Ensures void remains local and player-linked |

## INVARIANTS (MUST ALWAYS HOLD)

### V1: Queries Are Read-Only

```
FORALL graph_queries.* calls:
  MUST NOT mutate canonical graph state:
    - moment.energy, moment.weight, moment.status
    - creation/deletion of nodes/links
    - writing THEN / CONTRADICTS / PRESENT / BELIEF
```

**Checked by:** static import or runtime guard (GraphOps writes forbidden from query modules)

### V2: Canon Single-Writer

```
ONLY CanonHolder may:
  - transition moment.status -> completed
  - write THEN links
  - emit moment_completed SSE
```

**Checked by:** code ownership guard + integration test "spoke path"

### V3: Energy Is Computed (No Arbitrary Injection)

```
All changes to energy/weight must be produced by:
  - physics tick rules (propagate/decay/split)
  - explicit events written to graph (player action, narrator possibility, witnessed narrative)
NOT by:
  - queries
  - UI refresh
  - health checks
```

**Checked by:** restricted write API paths or write provenance tagging

### V4: Attention Split Is Deterministic

```
Given same (graph snapshot + tick + neighborhood definition):
  split_fn produces identical shares
  energies after tick are identical
```

**Checked by:** replay test with fixed snapshot

### V5: Interrupt Is Binary and Physics-Derived

```
Interrupt = YES iff one of:
  (a) primary active moment in player neighborhood changes
  (b) current primary active deactivates (falls below threshold)
  (c) a moment becomes completed in player neighborhood
  (d) CONTRADICTS becomes visible in player neighborhood
No other rule may trigger interrupts.
```

**Checked by:** runner simulation tests

### V6: Runner Streams Only Local Neighborhood Flips

```
Runner(position P) may only stream flips where:
  node ∈ player_neighborhood(P)
No far-away flips are streamed by this runner.
```

**Checked by:** stream filter unit test

### V7: WorldBuilder DMZ Safety

```
WorldBuilder MUST NOT mutate within DMZ neighborhood of the player view.
DMZ = N_k(current_view(player)) with whitelisted link types.
```

**Checked by:** write interceptor that rejects DMZ writes

### V8: Void Pressure Visibility Rule

```
A narrative_void moment MUST NOT surface unless it is linked into player neighborhood.
If not linked, it can exist but never becomes completed for the player stream.
```

**Checked by:** surfacing constraint test

### V9: Void Cooldown / Non-Spam

```
Within a cooldown window W:
  at most one narrative_void node is created per player neighborhood
Repeated player inputs within Δt are coalesced or appended.
```

**Checked by:** input burst tests

### V10: Simultaneity Selection Keeps One Spoken

```
Within a beat window:
  at most one candidate is completed
All alternatives persist and are linked via CONTRADICTS (or equivalent).
```

**Checked by:** canonization test "one spoken per window + contradicts links exist"

### V11: Hot Path Performance

```
Traversal / Surfacing / Tick operations:
  MUST be mechanical and complete under target budget (<50ms/op)
No LLM calls in hot path.
```

**Checked by:** benchmark test + call graph assertions

---

## PROPERTIES (PROPERTY-BASED TESTS)

### P1: Conservation / Boundedness

```
FORALL ticks:
  0.0 <= energy(node) <= 1.0
  0.0 <= weight(moment) <= 1.0
  split shares sum to expected budget constraints
```

**Verified by:** fuzzed tick runner

### P2: Replayability

```
FORALL identical inputs (snapshot + event list):
  resulting spoken sequence and THEN chain are identical
```

**Verified by:** replay test harness

### P3: Locality

```
FORALL runner positions:
  streamed events depend only on neighborhood(P) and canon transitions,
  not on unrelated graph regions
```

**Verified by:** locality tests with far-away changes

---

## ERROR CONDITIONS

### E1: Query Mutation Detected

```
WHEN: graph_queries tries to write
THEN: throw or abort in dev, log and block in prod
SYMPTOM: non-replayable behavior, observer changes world
```

**Verified by:** write-guard test

### E2: Multiple Spoken Writers

```
WHEN: any module other than CanonHolder emits spoken or THEN
THEN: error
SYMPTOM: forked canon or duplicated SSE
```

### E3: DMZ Violation

```
WHEN: WorldBuilder writes inside DMZ
THEN: reject mutation or quarantine
SYMPTOM: scene contradictions, world changes under player
```

### E4: Interrupt Thrash

```
WHEN: interrupts fire repeatedly without focus reconfiguration or spoken
THEN: failure (violates V5)
SYMPTOM: jitter pacing, unusable acceleration modes
```

---

## HEALTH COVERAGE

| Invariant | Signal | Status |
|-----------|--------|--------|
| V1: Read-only queries | query_write_guard | ⚠ NOT YET VERIFIED |
| V2: Canon single-writer | canon_single_writer | ⚠ NOT YET VERIFIED |
| V5: Interrupt rule | interrupt_reconfig_only | ⚠ NOT YET VERIFIED |
| V6: Locality | runner_locality | ⚠ NOT YET VERIFIED |
| V11: Hot path perf | hot_path_budget | ⚠ NOT YET VERIFIED |

---

## VERIFICATION PROCEDURE

### Manual Checklist

```
[ ] V1 Queries are read-only (no GraphOps writes)
[ ] V2 CanonHolder is sole spoken writer
[ ] V3 Energy changes only from physics + explicit events
[ ] V4 Deterministic split on replay
[ ] V5 Interrupt only on focus reconfig / spoken / contradicts-visible
[ ] V6 Runner streams only local neighborhood
[ ] V7 WorldBuilder respects DMZ
[ ] V8 Void requires player link to surface
[ ] V9 Void cooldown + input coalescing
[ ] V10 One spoken per beat window + CONTRADICTS persists
[ ] V11 <50ms hot path + no LLM in hot path
```

### Automated

```bash
pytest tests/moment_graph/test_queries_readonly.py
pytest tests/moment_graph/test_canon_single_writer.py
pytest tests/physics/test_attention_split_determinism.py
pytest mind/tests/test_physics_mechanisms.py -k attention
pytest tests/runtime/test_interrupt_invariants.py
pytest tests/runtime/test_dmz_worldbuilder.py
pytest tests/runtime/test_void_pressure.py
pytest tests/runtime/test_simultaneity_contradicts.py
pytest tests/perf/test_hot_path_budget.py
```

---

## SYNC STATUS

```yaml
LAST_VERIFIED: 2025-12-20
VERIFIED_AGAINST:
  impl: local tree
VERIFIED_BY: manual review (doc-only)
RESULT:
  V1: NOT RUN
  V2: NOT RUN
  V3: NOT RUN
  V4: NOT RUN
  V5: NOT RUN
  V6: NOT RUN
  V7: NOT RUN
  V8: NOT RUN
  V9: NOT RUN
  V10: NOT RUN
  V11: NOT RUN
```

---

## GAPS / QUESTIONS

<!-- @mind:todo Define exact player_neighborhood() whitelist + hop depth k -->
<!-- @mind:todo Define CONTRADICTS visibility rule in surfacing policy -->
<!-- @mind:todo Define beat window boundaries (epoch_id vs tick window) -->
<!-- @mind:todo Define split budget constraint (strict conservation vs bounded clamp) -->
