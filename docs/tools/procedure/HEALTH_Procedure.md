# Procedure — Health: Verification Mechanics and Coverage

```
STATUS: DRAFT v2.0
CREATED: 2025-12-29
UPDATED: 2025-12-29
```

---

## WHEN TO USE HEALTH (NOT TESTS)

Health checks verify runtime behavior that tests cannot catch:

| Use Health For | Why |
|----------------|-----|
| Zombie runs | Runs stuck active for 24h+ need real time, not fixtures |
| Invariant drift | Single-active-step can drift with concurrent operations |
| Guide completeness | Steps missing What/Why/How sections are unusable |
| Template mutation attempts | Runtime monitoring, not unit testing |

**Tests gate completion. Health monitors runtime.**

---

## PURPOSE OF THIS FILE

This HEALTH file monitors the Procedure execution system's runtime invariants.

**What it covers:** Run Space lifecycle, step transition integrity, guide availability (What/Why/How sections), template protection.

**Why it exists:** Procedures are long-running (minutes to hours). Tests verify logic; health verifies the system doesn't drift into invalid states during real operation.

**Boundaries:** This file does NOT verify graph infrastructure (that's graph health) or physics calculations (that's physics health). Only procedure-specific state.

---

## WHY THIS PATTERN

HEALTH is separate from tests because procedure invariants can drift during real execution — concurrent runs, crashed agents, partial transitions. Tests pass; runtime fails.

Docking-based checks are right because we can verify state at transition points without modifying the core procedure_runner logic. Throttling protects against alert storms during high-procedure-volume periods.

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Procedure.md
PATTERNS:        ./PATTERNS_Procedure.md
BEHAVIORS:       ./BEHAVIORS_Procedure.md
VOCABULARY:      ./VOCABULARY_Procedure.md
ALGORITHM:       ./ALGORITHM_Procedure.md
VALIDATION:      ./VALIDATION_Procedure.md
IMPLEMENTATION:  ./IMPLEMENTATION_Procedure.md
THIS:            HEALTH_Procedure.md (you are here)
SYNC:            ./SYNC_Procedure.md

IMPL:            runtime/health/procedure_health.py (planned)
```

> **Contract:** HEALTH checks verify input/output against VALIDATION with minimal or no code changes. After changes: update IMPL or add TODO to SYNC. Run HEALTH checks at throttled rates.

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: start_procedure
    purpose: Creates Run Space and activates first step
    triggers:
      - type: event
        source: mcp/server.py:procedure_start
        notes: MCP tool call from agent
    frequency:
      expected_rate: 10/hour
      peak_rate: 100/hour
      burst_behavior: Queue if DB under load, no retry
    risks:
      - Orphan Run Space if crash before step link (V3)
      - Missing doc chain if IMPLEMENTED_IN links broken (V4)
    notes: First step activation is critical for invariant V3

  - flow_id: continue_procedure
    purpose: Validates and advances to next step
    triggers:
      - type: event
        source: mcp/server.py:procedure_continue
        notes: MCP tool call from agent
    frequency:
      expected_rate: 50/hour
      peak_rate: 500/hour
      burst_behavior: Sequential per run, parallel across runs
    risks:
      - Multiple active steps if transition non-atomic (V3)
      - Validation bypass if spec malformed (V6)
    notes: Most frequent operation, highest risk for V3 drift

  - flow_id: end_procedure
    purpose: Marks run complete, flips actor link
    triggers:
      - type: event
        source: mcp/server.py:procedure_end or continue_procedure (last step)
        notes: Explicit end or automatic on last continue
    frequency:
      expected_rate: 10/hour
      peak_rate: 100/hour
      burst_behavior: None, terminal operation
    risks:
      - Zombie run if end never called (V7)
      - Actor link not flipped (V7)
    notes: Less frequent but important for cleanup
```

---

## HEALTH INDICATORS SELECTED

```yaml
health_indicators:
  - name: single_active_step
    flow_id: continue_procedure
    priority: high
    rationale: V3 is CRITICAL — ambiguous state breaks crash recovery

  - name: guide_completeness
    flow_id: start_procedure
    priority: high
    rationale: V4 — steps without guide content (What/Why/How) defeat the purpose

  - name: zombie_runs
    flow_id: end_procedure
    priority: med
    rationale: V7 — runs active >24h indicate crashed agents

  - name: template_mutation_attempts
    flow_id: continue_procedure
    priority: high
    rationale: V2 — any attempt is a severe bug
```

## OBJECTIVES COVERAGE

| Objective | Indicators | Why These Signals Matter |
|-----------|------------|--------------------------|
| O1 (Steps Self-Contained) | guide_completeness | Detects steps without What/Why/How sections |
| O2 (Template Immutability) | template_mutation_attempts | Zero tolerance for template writes |
| O4 (Deterministic Flow) | single_active_step | Proves state machine integrity |

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: .mind/state/health/procedure.yaml
  result:
    representation: enum
    value: UNKNOWN
    updated_at: pending
    source: procedure_health_checker
```

---

## CHECKER INDEX

```yaml
checkers:
  - name: single_active_step_checker
    purpose: Verify each active Run Space has exactly 1 high-energy step link
    status: pending
    priority: high

  - name: guide_completeness_checker
    purpose: Verify all Steps have guide content (What/Why/How sections)
    status: pending
    priority: high

  - name: zombie_run_checker
    purpose: Find Run Spaces with status=active and started_at > 24h ago
    status: pending
    priority: med

  - name: template_mutation_checker
    purpose: Detect any write operations targeting Procedure template nodes
    status: pending
    priority: high
```

---

## INDICATOR: Single Active Step

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: single_active_step
  client_value: Agents can always determine current step; crash recovery works
  validation:
    - validation_id: V3
      criteria: Exactly one high-energy (e > 5) step link per active Run Space
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - enum
  semantics:
    enum:
      OK: All active Run Spaces have exactly 1 high-energy step link
      WARN: Not applicable (this is binary)
      ERROR: At least 1 Run Space has 0 or 2+ high-energy step links
  aggregation:
    method: any_error_fails
    display: enum
```

### DOCKS SELECTED

```yaml
docks:
  input:
    id: dock_transition_complete
    method: engine.execution.procedure_runner.continue_procedure
    location: engine/execution/procedure_runner.py:TBD
  output:
    id: dock_step_state
    method: health query
    location: engine/health/procedure_health.py:TBD
```

### ALGORITHM / CHECK MECHANISM

```yaml
mechanism:
  summary: Query all Run Spaces with status=active, count high-energy step links per run
  steps:
    - Query nodes where type=space AND subtype=run AND content.status=active
    - For each run, query outgoing links where energy > 5 AND verb=acts_on
    - If count != 1, flag ERROR with run_id
  data_required: Run Space nodes, step links
  failure_mode: Returns list of violating run_ids
```

### INDICATOR

```yaml
indicator:
  error:
    - name: multiple_active_steps
      linked_validation: [V3]
      meaning: Run Space has ambiguous state, agent cannot determine current step
      default_action: alert
    - name: zero_active_steps
      linked_validation: [V3]
      meaning: Run Space is stuck, no step to execute
      default_action: alert
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: schedule
  max_frequency: 1/5min
  burst_limit: 1
  backoff: none (scheduled only)
```

### FORWARDINGS & DISPLAYS

```yaml
forwarding:
  targets:
    - location: .mind/state/health/procedure.yaml
      transport: file
      notes: Doctor reads from here
display:
  locations:
    - surface: CLI
      location: mind doctor output
      signal: OK/ERROR
      notes: Part of mind doctor procedure checks
```

### MANUAL RUN

```yaml
manual_run:
  command: python -m engine.health.procedure_health --check single_active_step
  notes: Run after suspected transition failures
```

---

## INDICATOR: Guide Completeness

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: guide_completeness
  client_value: Every step has self-contained guide; O1 objective met
  validation:
    - validation_id: V4
      criteria: Every Step has guide content (What/Why/How sections)
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - float_0_1
  semantics:
    float_0_1: Percentage of steps with complete guide content (1.0 = all, 0.8 = 80%)
  aggregation:
    method: percentage
    display: float_0_1
```

### ALGORITHM / CHECK MECHANISM

```yaml
mechanism:
  summary: Query all Step nodes, check each has guide content (What/Why/How)
  steps:
    - Query nodes where type=narrative AND subtype=step
    - For each step, parse content for required sections
    - Check for "## What" or "What you're doing" section
    - Check for "## Why" section
    - Check for "## How" section
    - Calculate percentage with all required sections present
  data_required: Step nodes with content field
  failure_mode: Returns list of incomplete step_ids and percentage
```

### INDICATOR

```yaml
indicator:
  error:
    - name: incomplete_guide
      linked_validation: [V4]
      meaning: Step missing What/Why/How sections, agent lacks context
      default_action: warn
  warning:
    - name: low_coverage
      linked_validation: [V4]
      meaning: Less than 100% of steps have complete guides
      default_action: log
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: schedule
  max_frequency: 1/hour
  burst_limit: 1
  backoff: none
```

---

## INDICATOR: Zombie Runs

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: zombie_runs
  client_value: Runs don't accumulate indefinitely; resources freed
  validation:
    - validation_id: V7
      criteria: Active runs should complete or fail within reasonable time
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - enum
  semantics:
    enum:
      OK: Zero runs active > 24h
      WARN: 1-5 runs active > 24h
      ERROR: > 5 runs active > 24h
```

### ALGORITHM / CHECK MECHANISM

```yaml
mechanism:
  summary: Find Run Spaces with status=active and started_at older than 24h
  steps:
    - Query nodes where type=space AND subtype=run AND content.status=active
    - Filter where content.started_at < (now - 24h)
    - Count results
  data_required: Run Space nodes with timestamps
  failure_mode: Returns count and list of zombie run_ids
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: schedule
  max_frequency: 1/hour
  burst_limit: 1
  backoff: none
```

---

## HOW TO RUN

```bash
# Run all health checks for this module
python -m runtime.health.procedure_health --all

# Run a specific checker
python -m runtime.health.procedure_health --check single_active_step
python -m runtime.health.procedure_health --check guide_completeness
python -m runtime.health.procedure_health --check zombie_runs
```

---

## KNOWN GAPS

- V2 (Template Mutation): No checker implemented yet. Requires write-path interception.
- V5 (API Contract): No checker for return structure validation. Should be unit tests.
- V6 (Validation Spec): No checker for malformed specs. Should be unit tests.

<!-- @mind:todo Implement template_mutation_checker — requires write-path hook -->
<!-- @mind:todo Add threshold config for zombie run hours (currently hardcoded 24h) -->
<!-- @mind:todo Implement guide_completeness_checker — parse step content for What/Why/How -->

---

## RESOLVED DECISIONS

### RD1: Mutation Detection

**Decision:** Periodic audit (not interception).

Health checker queries for links FROM procedure nodes WHERE created_at > last_check. Runs every 5 minutes. Low overhead, catches violations eventually.

**Why not interception:** Wrapping persistence layer is invasive and adds latency to every write. Periodic audit is sufficient for V1.

### RD2: Timestamp Format

**Decision:** ISO-8601 string.

```python
from datetime import datetime
started_at = datetime.utcnow().isoformat() + "Z"
# Example: "2025-12-29T10:30:00.000000Z"
```

**Rationale:**
- Human readable in graph queries
- Python's `datetime.isoformat()` is native
- FalkorDB can compare strings chronologically

---

## MARKERS

<!-- @mind:proposition Add self-healing for zombie runs: auto-fail after 48h with status="timeout" -->
