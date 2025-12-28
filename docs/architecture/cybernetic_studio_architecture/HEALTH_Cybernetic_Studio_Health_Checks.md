# ARCHITECTURE — Cybernetic Studio — Health: Verification Mechanics and Coverage

```
STATUS: DESIGNING
CREATED: 2025-12-20
```

---

## PURPOSE OF THIS FILE

This HEALTH file defines how to verify the Cybernetic Studio architecture once integration wiring exists. It protects repo/graph separation, Place semantics, and adaptive gate discipline. It does not verify game content or UI polish.

---

## WHY THIS PATTERN

Architecture-level checks catch drift between design intent and runtime behavior without changing core implementation. Docking-based checks let us verify boundaries (repo → graph, SYNC → Place) with minimal instrumentation.

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Cybernetic_Studio_Architecture.md
BEHAVIORS:       ./BEHAVIORS_Cybernetic_Studio_System_Behaviors.md
ALGORITHM:       ./ALGORITHM_Cybernetic_Studio_Process_Flow.md
VALIDATION:      ./VALIDATION_Cybernetic_Studio_Architectural_Invariants.md
IMPLEMENTATION:  ./IMPLEMENTATION_Cybernetic_Studio_Code_Structure.md
THIS:            HEALTH_Cybernetic_Studio_Health_Checks.md
SYNC:            ./SYNC_Cybernetic_Studio_Architecture_State.md

IMPL:            N/A (Conceptual Architecture Document)
```

> **Contract:** HEALTH checks verify input/output against VALIDATION with minimal or no code changes. After changes: update IMPL or add TODO to SYNC. Run HEALTH checks at throttled rates.

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: stimulus_ingestion_and_tick
    purpose: Ensure stimuli reach the graph and surface via physics.
    triggers:
      - type: event
        source: repo watchers (planned)
        notes: file_read/write/commit/exec
    frequency:
      expected_rate: event-driven
      peak_rate: event-driven
      burst_behavior: depends on repo activity
    risks:
      - V1
      - V3
      - V4
    notes: Boundary between repos and graph service.
  - flow_id: sync_place_updates
    purpose: Ensure SYNC edits become Place moments.
    triggers:
      - type: event
        source: ...mind-mcp/state/SYNC_*.md edits
        notes: manual or agent edits
    frequency:
      expected_rate: human-driven
      peak_rate: bursty during active repairs
      burst_behavior: batch updates
    risks:
      - V5
    notes: Place semantics are core to handoffs.
```

---

## HEALTH INDICATORS SELECTED

```yaml
health_indicators:
  - name: evidence_ref_only_storage
    flow_id: stimulus_ingestion_and_tick
    priority: high
    rationale: Prevents graph from duplicating repo artifacts (V1).
  - name: place_moment_on_sync_update
    flow_id: sync_place_updates
    priority: high
    rationale: Ensures SYNC updates surface as Moments and keep Places real (V5).
  - name: graph_ownership_boundary
    flow_id: stimulus_ingestion_and_tick
    priority: medium
    rationale: Ensures graph service remains owned by `mind` (V6).
  - name: adaptive_gate_usage
    flow_id: stimulus_ingestion_and_tick
    priority: medium
    rationale: Prevents fixed constants from controlling flips (V4).
```

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: file:docs/architecture/cybernetic_studio_architecture/HEALTH_Cybernetic_Studio_Health_Checks.md
  result:
    representation: enum
    value: UNKNOWN
    updated_at: 2025-12-20T00:00:00Z
    source: evidence_ref_only_storage
```

---

## CHECKER INDEX

```yaml
checkers:
  - name: evidence_ref_only_storage
    purpose: Validate V1 (no file content in graph)
    status: pending
    priority: high
  - name: place_moment_on_sync_update
    purpose: Validate V5 (Places are real)
    status: pending
    priority: high
  - name: graph_ownership_boundary
    purpose: Validate V6 (graph service ownership)
    status: pending
    priority: medium
  - name: adaptive_gate_usage
    purpose: Validate V4 (no arbitrary constants)
    status: pending
    priority: medium
```

---

## INDICATOR: evidence_ref_only_storage

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: evidence_ref_only_storage
  client_value: Prevents duplication of repo artifacts and keeps evidence traceable.
  validation:
    - validation_id: V1
      criteria: Artifacts live in repos; graph stores EvidenceRefs only.
```

### HEALTH REPRESENTATION

```yaml
representation:
  allowed:
    - enum
  selected:
    - enum
  semantics:
    enum: OK if graph payloads do not contain file content; ERROR otherwise.
  aggregation:
    method: worst_of
    display: enum
```

### DOCKS SELECTED

```yaml
docks:
  input:
    id: dock_repo_event
    method: watcher hook (planned)
    location: N/A (planned)
  output:
    id: dock_graph_inject
    method: graph_ops.inject
    location: graph service
```

### ALGORITHM / CHECK MECHANISM

```yaml
mechanism:
  summary: Inspect injected payloads for EvidenceRefs only, reject file content.
  steps:
    - sample injected payloads
    - verify payload fields match EvidenceRef schema
  data_required: injected payloads at dock_graph_inject
  failure_mode: embedded file content or raw file blobs
```

### INDICATOR

```yaml
indicator:
  error:
    - name: graph_contains_file_content
      linked_validation: [V1]
      meaning: Graph stored file content instead of EvidenceRefs
      default_action: stop
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: event
  max_frequency: 1/min
  burst_limit: 10
  backoff: exponential
```

### FORWARDINGS & DISPLAYS

```yaml
forwarding:
  targets:
    - location: docs/architecture/cybernetic_studio_architecture/HEALTH_Cybernetic_Studio_Health_Checks.md
      transport: file
      notes: local status surface
display:
  locations:
    - surface: CLI
      location: mind doctor (planned)
      signal: enum
      notes: will surface when checkers exist
```

### MANUAL RUN

```yaml
manual_run:
  command: mind doctor (planned)
  notes: Run once graph injection hooks exist.
```

---

## INDICATOR: graph_ownership_boundary

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: graph_ownership_boundary
  client_value: Keeps graph service responsibility centralized in the platform repo.
  validation:
    - validation_id: V6
      criteria: Graph service ownership is enforced by `mind`.
```

### HEALTH REPRESENTATION

```yaml
representation:
  allowed:
    - enum
  selected:
    - enum
  semantics:
    enum: OK if graph service configuration is owned and deployed by `mind`; ERROR otherwise.
  aggregation:
    method: worst_of
    display: enum
```

### ALGORITHM / CHECK MECHANISM

```yaml
mechanism:
  summary: Verify graph service deployment/config is owned by `mind` and consumed by clients.
  steps:
    - confirm service config lives under `mind` ownership
    - confirm client access only from `blood-ledger`
  data_required: deployment config, service endpoints
  failure_mode: `blood-ledger` owns or deploys the graph service
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: schedule
  max_frequency: 1/day
  burst_limit: 1
  backoff: none
```

### MANUAL RUN

```yaml
manual_run:
  command: mind doctor (planned)
  notes: Run after deployment or config changes.
```

---

## HOW TO RUN

```bash
# Pending: add health runner once graph hooks exist.
```

---

## KNOWN GAPS

<!-- @mind:todo No live checkers until graph hooks exist. -->
<!-- @mind:todo Dock locations are planned, not implemented. -->

---

## MARKERS

<!-- @mind:todo Define a concrete health runner command once graph hooks are wired. -->
<!-- @mind:escalation Should health signals be written to a dedicated status file? -->
