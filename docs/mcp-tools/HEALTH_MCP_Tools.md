# MCP Tools — Health: Verification Mechanics and Coverage

```
STATUS: DRAFT
CREATED: 2025-12-24
```

---

## WHEN TO USE HEALTH (NOT TESTS)

Health checks verify runtime behavior that tests cannot catch:

| Use Health For | Why |
|----------------|-----|
| Session state drift | Long-running dialogues accumulate state |
| Protocol execution ordering | Real multi-step flows, not fixtures |
| Call stack depth | Only visible in production recursion |
| Graph consistency | After real cluster creation |

**Tests gate completion. Health monitors runtime.**

Tests verify the membrane works. Health verifies it stays working during real usage.

---

## PURPOSE OF THIS FILE

This HEALTH file covers: Membrane system runtime verification (MCP server, runner, sessions, protocols).

Why it exists: Membrane orchestrates multi-step dialogues — state corruption or ordering bugs only surface during real protocol execution.

Boundaries: Does NOT verify protocol content quality (that's doctor's job). Verifies execution mechanics only.

---

## WHY THIS PATTERN

HEALTH is separate from tests because:
- Tests use mock protocols; health uses real protocols
- Tests verify single operations; health verifies stateful dialogues
- Tests run in CI; health runs during real usage

Docking-based checks are right here because membrane has clear input/output boundaries (MCP tools → graph operations).

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_MCP_Tools.md
PATTERNS:        ./PATTERNS_MCP_Tools.md
BEHAVIORS:       ./BEHAVIORS_MCP_Tools.md
ALGORITHM:       ./ALGORITHM_MCP_Tools.md
VALIDATION:      ./VALIDATION_MCP_Tools.md
IMPLEMENTATION:  ./IMPLEMENTATION_MCP_Tools.md
THIS:            HEALTH_MCP_Tools.md
SYNC:            ./SYNC_MCP_Tools.md

IMPL:            runtime/connectome/runner.py
                 mcp/server.py
```

---

## FLOWS ANALYSIS

```yaml
flows_analysis:
  - flow_id: protocol_execution
    purpose: "Execute protocol from start to complete"
    triggers:
      - type: event
        source: mcp/server.py:procedure_start
        notes: "Agent calls procedure_start with protocol name"
    frequency:
      expected_rate: 1-5/session
      peak_rate: 20/session
      burst_behavior: Sequential (one active session at a time)
    risks:
      - V-PROT-1: Steps execute out of order
      - V-MEM-4: Step transitions lead to invalid state
    notes: Most critical flow - if this fails, membrane is useless

  - flow_id: answer_validation
    purpose: "Validate agent answers before advancing"
    triggers:
      - type: event
        source: mcp/server.py:procedure_continue
        notes: "Agent provides answer to ask step"
    frequency:
      expected_rate: 3-10/protocol
      peak_rate: 50/protocol
      burst_behavior: Sequential per session
    risks:
      - V-MEM-1: Invalid answer proceeds
      - V-SESS-2: Answer not stored in history
    notes: Critical for data quality

  - flow_id: cluster_creation
    purpose: "Create nodes and links from protocol spec"
    triggers:
      - type: event
        source: runtime/connectome/steps.py:execute_create
        notes: "Protocol reaches create step"
    frequency:
      expected_rate: 1-3/protocol
      peak_rate: 10/protocol
      burst_behavior: Batch (multiple nodes/links per step)
    risks:
      - V-CLUST-1: Invalid node_type
      - V-CLUST-2: Dangling links
      - V-MEM-5: Empty output
    notes: Graph integrity depends on this
```

---

## HEALTH INDICATORS SELECTED

## OBJECTIVES COVERAGE

| Objective | Indicators | Why These Signals Matter |
|-----------|------------|--------------------------|
| Protocol execution correctness | h_session_valid, h_step_ordering | Corrupted sessions break dialogues |
| Cluster integrity | h_cluster_complete | Bad clusters break graph semantics |
| Answer validation | h_answer_validated | Invalid data pollutes graph |

```yaml
health_indicators:
  - name: h_session_valid
    flow_id: protocol_execution
    priority: high
    rationale: Session state corruption makes membrane unusable

  - name: h_step_ordering
    flow_id: protocol_execution
    priority: high
    rationale: Out-of-order steps produce wrong results

  - name: h_cluster_complete
    flow_id: cluster_creation
    priority: high
    rationale: Incomplete clusters violate graph invariants

  - name: h_answer_validated
    flow_id: answer_validation
    priority: med
    rationale: Invalid answers produce bad graph data
```

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: .mind/health/membrane_health.yaml
  result:
    representation: enum
    value: UNKNOWN
    updated_at: 2025-12-24T00:00:00Z
    source: h_session_valid
```

---

## CHECKER INDEX

```yaml
checkers:
  - name: session_state_checker
    purpose: Verify session maintains valid state through lifecycle
    status: pending
    priority: high

  - name: step_ordering_checker
    purpose: Verify steps execute in defined order
    status: pending
    priority: high

  - name: cluster_integrity_checker
    purpose: Verify created clusters have valid nodes and links
    status: pending
    priority: high

  - name: answer_validation_checker
    purpose: Verify invalid answers are rejected
    status: pending
    priority: med
```

---

## INDICATOR: h_session_valid

Verifies session state remains valid through protocol lifecycle.

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: h_session_valid
  client_value: "If sessions corrupt, dialogues fail mid-conversation"
  validation:
    - validation_id: V-SESS-1
      criteria: "Session ID is unique"
    - validation_id: V-SESS-2
      criteria: "Session maintains answer history"
    - validation_id: V-SESS-5
      criteria: "Session has single active step at any time"
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - enum
  semantics:
    enum: OK=valid session, WARN=stale session, ERROR=corrupted state
  aggregation:
    method: "worst-wins (ERROR > WARN > OK)"
    display: enum
```

### DOCKS SELECTED

```yaml
docks:
  input:
    id: session_start
    method: mind.connectome.runner.ConnectomeRunner.start
    location: runtime/connectome/runner.py
  output:
    id: session_complete
    method: mind.connectome.runner.ConnectomeRunner.continue_session
    location: runtime/connectome/runner.py
```

### ALGORITHM / CHECK MECHANISM

```yaml
mechanism:
  summary: "Compare session state before/after step execution"
  steps:
    - Capture session state at step start (session_id, current_step, answers count)
    - Execute step
    - Verify: session_id unchanged, current_step advanced, answers count incremented (if ask step)
    - Check: exactly one step marked active
  data_required: Session object fields
  failure_mode: "Session ID changed OR multiple active steps OR answer lost"
```

### INDICATOR

```yaml
indicator:
  error:
    - name: session_corrupted
      linked_validation: [V-SESS-1, V-SESS-5]
      meaning: "Session state invalid"
      default_action: abort
  warning:
    - name: session_stale
      linked_validation: [V-SESS-2]
      meaning: "Session older than timeout"
      default_action: warn
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: procedure_continue event
  max_frequency: 10/min
  burst_limit: 50/min
  backoff: exponential
```

### FORWARDINGS & DISPLAYS

```yaml
forwarding:
  targets:
    - location: .mind/health/membrane_health.yaml
      transport: file
      notes: Local health status file
display:
  locations:
    - surface: CLI
      location: mind doctor --stream
      signal: green/yellow/red
      notes: Color indicates health state
```

### MANUAL RUN

```yaml
manual_run:
  command: "pytest tests/connectome_v0/test_runner.py -v -k session"
  notes: "Run when session issues suspected"
```

---

## INDICATOR: h_step_ordering

Verifies protocol steps execute in defined order.

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: h_step_ordering
  client_value: "Out-of-order steps produce wrong dialogues and invalid data"
  validation:
    - validation_id: V-PROT-1
      criteria: "Protocol steps execute in defined order"
    - validation_id: V-MEM-4
      criteria: "All step transitions lead to valid next step or $complete"
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - binary
  semantics:
    binary: 1=correct ordering, 0=ordering violation
  aggregation:
    method: "AND (all must pass)"
    display: binary
```

### DOCKS SELECTED

```yaml
docks:
  input:
    id: step_dispatch
    method: mind.connectome.steps.execute_step
    location: runtime/connectome/steps.py
  output:
    id: step_complete
    method: mind.connectome.steps.execute_step
    location: runtime/connectome/steps.py
```

### ALGORITHM / CHECK MECHANISM

```yaml
mechanism:
  summary: "Track step execution order against protocol definition"
  steps:
    - Load protocol step order from YAML
    - Log each step execution with timestamp
    - Compare actual order to expected order
    - Flag any deviation
  data_required: Protocol YAML, step execution log
  failure_mode: "Step X executed before required predecessor"
```

---

## INDICATOR: h_cluster_complete

Verifies cluster creation produces valid nodes and links.

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: h_cluster_complete
  client_value: "Incomplete clusters break graph queries and semantics"
  validation:
    - validation_id: V-CLUST-1
      criteria: "All nodes in cluster have valid node_type"
    - validation_id: V-CLUST-2
      criteria: "All links reference existing nodes"
    - validation_id: V-MEM-5
      criteria: "Create step produces ≥1 node"
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - enum
  semantics:
    enum: OK=complete cluster, WARN=sparse links, ERROR=missing nodes or dangling links
  aggregation:
    method: "worst-wins"
    display: enum
```

### DOCKS SELECTED

```yaml
docks:
  input:
    id: create_step_start
    method: mind.connectome.steps.execute_create
    location: runtime/connectome/steps.py
  output:
    id: graph_commit
    method: mind.physics.graph.GraphOps.create_node
    location: runtime/physics/graph/
```

### ALGORITHM / CHECK MECHANISM

```yaml
mechanism:
  summary: "Verify cluster nodes exist and links resolve"
  steps:
    - Count nodes in create spec
    - After creation, query graph for each node ID
    - Verify all links have valid from/to references
    - Check: nodes_created >= 1, links/nodes >= 1
  data_required: Create step output, graph query results
  failure_mode: "Node not found OR link references missing node"
```

---

## HOW TO RUN

```bash
# Run all membrane health checks (when implemented)
mind doctor --stream --module membrane

# Run specific checker (via tests for now)
pytest tests/connectome_v0/ -v -k "session or cluster"
```

---

## KNOWN GAPS

<!-- @mind:todo V-MEM-3 (spawn depth) not yet covered - need call_protocol test -->
<!-- @mind:todo V-MOM-1 through V-MOM-4 (moment invariants) need checkers -->
<!-- @mind:todo V-QUERY-1 through V-QUERY-3 (query invariants) need checkers -->
<!-- @mind:todo V-DOC-1 through V-DOC-3 (doctor invariants) need doctor integration -->

---

## MARKERS

<!-- @mind:todo Implement session_state_checker -->
<!-- @mind:todo Implement cluster_integrity_checker -->
<!-- @mind:proposition Add health stream output to membrane_server.py -->
