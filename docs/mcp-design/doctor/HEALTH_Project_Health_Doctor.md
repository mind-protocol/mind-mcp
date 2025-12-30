# Project Health Doctor — Health: Verification Mechanics and Coverage

```
STATUS: STABLE
CREATED: 2025-12-20
```

---

## PURPOSE OF THIS FILE

This file defines the health verification mechanics for the Project Health Doctor. It ensures that the doctor's diagnostic capabilities remain accurate, deterministic, and reliable across various project structures.

It safeguards:
- **Diagnostic Accuracy:** Ensuring that monoliths, undocumented code, and stale docs are correctly identified.
- **Scoring Integrity:** Ensuring the health score accurately reflects the project's adherence to the mind protocol.
- **Output Determinism:** Ensuring that the doctor produces consistent reports and JSON output for the same project state.

Boundaries:
- This file covers the doctor's internal checks and reporting logic.

---

## WHY THIS PATTERN

HEALTH is separate from tests because it verifies real system health without changing implementation files. For the Doctor, this allows verifying that the tool can correctly analyze projects in the real world, including its own repository (dogfooding).

- **Failure mode avoided:** The Doctor reporting a score of 100 on a project with major architectural issues due to a broken check function.
- **Docking-based checks:** Uses the `doctor_report.py` and `doctor_checks.py` as primary docking points.
- **Throttling:** Doctor is a heavy check by design; HEALTH verification should be throttled to avoid excessive CPU usage.

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Project_Health_Doctor.md
BEHAVIORS:       ./BEHAVIORS_Project_Health_Doctor.md
ALGORITHM:       ./ALGORITHM_Project_Health_Doctor.md
VALIDATION:      ./VALIDATION_Project_Health_Doctor.md
IMPLEMENTATION:  ./IMPLEMENTATION_Project_Health_Doctor.md
THIS:            HEALTH_Project_Health_Doctor.md
SYNC:            ./SYNC_Project_Health_Doctor.md

IMPL:            runtime/doctor.py
```

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: project_discovery
    purpose: Maps the filesystem to identify code and docs. Failure leads to missed issues.
    triggers:
      - type: event
        source: cli:mind doctor
    frequency:
      expected_rate: 1/hour
      peak_rate: 1/min
    risks:
      - V-DOC-DISCOVERY: Fails to find all source files or documentation.
    notes: Respects .gitignore and .mindignore.

  - flow_id: issue_check_loop
    purpose: Runs individual health checks. Failure leads to incorrect diagnostic signals.
    triggers:
      - type: event
        source: doctor.py:run_checks
    frequency:
      expected_rate: 1/hour
      peak_rate: 1/min
    risks:
      - V-DOC-CHECK: Bug in monolith detection or stale sync check.
    notes: Heavily dependent on correct threshold configuration.
```

---

## HEALTH INDICATORS SELECTED

```yaml
health_indicators:
  - name: check_determinism
    flow_id: issue_check_loop
    priority: med
    rationale: Inconsistent results erode user trust in the tool.
  - name: score_sanity
    flow_id: issue_check_loop
    priority: high
    rationale: A score of 100 must truly mean a healthy project.
```

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: ...mind/state/SYNC_Project_Health.md
  result:
    representation: tuple
    value: {OK, 1.0}
    updated_at: 2025-12-20T00:00:00Z
    source: issue_check_loop
```

---

## DOCK TYPES (COMPLETE LIST)

- `file` (filesystem discovery)
- `cli` (report generation)
- `metrics` (health score)

---

## CHECKER INDEX

```yaml
checkers:
  - name: self_health_check
    purpose: Running doctor on the mind project itself (dogfooding).
    status: active
    priority: high
  - name: fixture_validation_check
    purpose: Running checks against known broken fixtures (monolith, undocumented).
    status: active
    priority: high
```

---

## INDICATOR: Score Sanity

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: score_sanity
  client_value: Users can rely on the health score to prioritize refactoring and documentation work.
  validation:
    - validation_id: V-DOC-SCORE
      criteria: The score must decrease linearly with the number and severity of issues.
```

### HEALTH REPRESENTATION

```yaml
representation:
  allowed:
    - float_0_1
  selected:
    - float_0_1
  semantics:
    float_0_1: 1.0 if score calculation matches invariants, 0.0 otherwise.
```

---

## HOW TO RUN

```bash
# Run all doctor checks on the current project
mind doctor

# Run with JSON output for machine parsing
mind doctor --format json
```

---

## KNOWN GAPS

<!-- @mind:todo No automated check for "false positive rate". -->
<!-- @mind:todo No performance benchmarking for very large project trees. -->

---

## MARKERS

<!-- @mind:todo Add `mind doctor --benchmark` to measure check latency. -->
<!-- @mind:escalation
title: "Should we add a check for documentation quality (AI-assisted)?"
priority: 5
response:
  status: resolved
  choice: "No"
  behavior: "Doctor stays purely deterministic. No LLM calls. Fast, cheap, CI-friendly. Agents using CLI can assess quality themselves — they ARE AIs."
  notes: "2025-12-23: Decided by Nicolas."
-->
