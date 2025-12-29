# Scene Memory System — Test: Moment Processing Coverage

```
STATUS: DRAFT
CREATED: 2025-12-19
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Scene_Memory.md
BEHAVIORS:       ./BEHAVIORS_Scene_Memory.md
ALGORITHM:       ./ALGORITHM_Scene_Memory.md
VALIDATION:      ./VALIDATION_Scene_Memory.md
IMPLEMENTATION:  ./IMPLEMENTATION_Scene_Memory.md
THIS:            TEST_Scene_Memory.md
SYNC:            ./SYNC_Scene_Memory.md

IMPL:            mind/tests/test_moment.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## TEST STRATEGY

- Unit-test moment model behavior and embedding gates.
- Validate moment processor outputs using mocked GraphOps and temporary transcript directories.
- Exercise moment graph behavior via integration-style tests around graph ops and lifecycle.

---

## UNIT TESTS

### Moment Processor and Model

| Test | Input | Expected | Status |
|------|-------|----------|--------|
| `TestMomentModel` | Moment construction | Pydantic fields and embedding flags | not run |
| `TestMomentProcessor.test_generate_id` | tick/place/name | Expanded ID includes day/time/place | not run |
| `TestMomentProcessor.test_tick_to_time_of_day` | tick values | Correct time-of-day bucket | not run |
| `TestMomentProcessor` transcript tests | mock ops + temp dir | transcript entries appended | not run |

---

## INTEGRATION TESTS

### Moment Graph Lifecycle

```
GIVEN:  moment graph ops and lifecycle helpers
WHEN:   moments are added/updated/queried
THEN:   status/weights and link transitions are consistent
STATUS: not run
```

Relevant files:
- `runtime/tests/test_moment_graph.py`
- `runtime/tests/test_moment_lifecycle.py`
- `runtime/tests/test_e2e_moment_graph.py`

---

## EDGE CASES

| Case | Test | Status |
|------|------|--------|
| Transcript missing on first run | `TestMomentProcessor` with empty dir | not run |
| Short text embedding skip | `TestMomentModel.test_should_embed_short_text` | not run |
| Day/time boundary ticks | `TestMomentProcessor.test_tick_to_time_of_day` | not run |

---

## TEST COVERAGE

| Component | Coverage | Notes |
|-----------|----------|-------|
| MomentProcessor | partial | Unit tests exist but not run in this repair |
| Transcript IO | partial | Covered via temp dir tests |
| GraphOps integration | partial | Separate graph tests exercise ops |
| Moments API | partial | `runtime/tests/test_moments_api.py` |

---

## HOW TO RUN

```bash
# Run MomentProcessor unit tests
pytest mind/tests/test_moment.py

# Run full moment-related suite
pytest mind/tests/test_moment.py mind/tests/test_moment_graph.py mind/tests/test_moment_lifecycle.py mind/tests/test_e2e_moment_graph.py mind/tests/test_moments_api.py
```

---

## KNOWN TEST GAPS

<!-- @mind:todo Transcript write failure paths (`_append_to_transcript` error logging). -->
<!-- @mind:todo End-to-end coverage for `link_moments` triggers with real click traversal. -->

---

## FLAKY TESTS

| Test | Flakiness | Root Cause | Mitigation |
|------|-----------|------------|------------|
| None noted | - | - | - |

---

## MARKERS

<!-- @mind:proposition Add a fixture for deterministic tick/time mapping across moment tests. -->
<!-- @mind:escalation Should we add a smoke test that verifies transcript entries align with graph line references? -->
