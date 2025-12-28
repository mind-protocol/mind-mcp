# Schema — Health: Verification Mechanics and Coverage

```
STATUS: STABLE (v1.3), DESIGNING (v1.6.1)
CREATED: 2025-12-23
UPDATED: 2025-12-26
```

---

## PURPOSE OF THIS FILE

This HEALTH file covers schema validation mechanics — how we verify that graphs comply with schema constraints at runtime.

**Why it exists:** Schema drift happens. Nodes get created with missing fields, invalid enums, orphan links. Without health checks, these issues accumulate silently until something breaks. Health checks catch violations early.

**Boundaries:**
- DOES verify: Schema compliance (required fields, enum values, link structure)
- DOES NOT verify: Business logic, game rules, narrative consistency
- DOES NOT verify: Pydantic model alignment (that's a separate concern)

---

## WHY THIS PATTERN

HEALTH is separate from tests because:
- Tests run in CI, health checks run against live graphs
- Tests use fixtures, health checks use real data
- Tests are pass/fail, health reports have severity levels

Docking-based checks are the right tradeoff because:
- We read from graph without modifying
- We can run at any time without side effects
- We generate actionable reports

Throttling protects performance:
- Large graphs can have thousands of nodes
- Query batching prevents timeout
- Report truncation prevents output explosion

---

## HOW TO USE THIS TEMPLATE

1. Read VALIDATION_Schema.md for invariants we're checking
2. Read IMPLEMENTATION_Schema.md for code locations
3. Each indicator below maps to one or more VALIDATION criteria
4. Run manually or via mind doctor

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Schema.md
PATTERNS:       ./PATTERNS_Schema.md
BEHAVIORS:      ./BEHAVIORS_Schema.md
ALGORITHM:      ./ALGORITHM_Schema.md
VALIDATION:     ./VALIDATION_Schema.md
IMPLEMENTATION: ./IMPLEMENTATION_Schema.md
THIS:           HEALTH_Schema.md (you are here)
SYNC:           ./SYNC_Schema.md

IMPL:           mind/graph/health/check_health.py
                mind/graph/health/test_schema.py
```

> **Contract:** HEALTH checks verify input/output against VALIDATION with minimal or no code changes. After changes: update IMPL or add TODO to SYNC.

---

## FLOWS ANALYSIS

```yaml
flows_analysis:
  - flow_id: graph_validation
    purpose: Catch schema violations before they cause runtime errors
    triggers:
      - type: manual
        source: python check_health.py
        notes: Developer runs when debugging
      - type: schedule
        source: mind doctor
        notes: Part of overall health check
    frequency:
      expected_rate: 1/day
      peak_rate: 10/day during active development
      burst_behavior: Each run independent, no queuing
    risks:
      - V6 violation: Missing required fields
      - V2 violation: Out-of-range physics values
    notes: Connects to FalkorDB, requires running instance

  # v1.6.1 SubEntity Validation Flow
  - flow_id: subentity_validation
    purpose: Validate SubEntity structure during exploration
    triggers:
      - type: runtime
        source: SubEntity state transitions
        notes: Checked at each step
      - type: schedule
        source: mind doctor
        notes: Validates any persisted SubEntity state
    frequency:
      expected_rate: per-exploration
      peak_rate: 100/min during active exploration
      burst_behavior: Validated inline with traversal
    risks:
      - V15 violation: Broken tree structure
      - V16 violation: Malformed found_narratives
      - V17 violation: Null crystallization embedding
      - V18 violation: Missing sibling embeddings
      - V19 violation: Crystallized field inconsistency
    notes: SubEntities are ephemeral but must be valid during lifetime
```

---

## HEALTH INDICATORS SELECTED

```yaml
health_indicators:
  - name: schema_compliance
    flow_id: graph_validation
    priority: high
    rationale: Schema violations cause runtime errors in physics/narrator

  - name: required_fields_present
    flow_id: graph_validation
    priority: high
    rationale: Missing id/name breaks lookups and display

  - name: enum_values_valid
    flow_id: graph_validation
    priority: med
    rationale: Invalid enums may cause display issues but often recoverable

  - name: link_structure_valid
    flow_id: graph_validation
    priority: high
    rationale: Invalid link endpoints break traversal

  # v1.6.1 SubEntity Health Indicators
  - name: subentity_tree_integrity
    flow_id: subentity_validation
    priority: high
    rationale: Tree structure must be consistent for sibling divergence

  - name: found_narratives_tuples
    flow_id: subentity_validation
    priority: high
    rationale: Alignment scores needed for weighted aggregation

  - name: crystallization_embedding_continuous
    flow_id: subentity_validation
    priority: high
    rationale: Sibling divergence requires up-to-date embeddings

  - name: crystallized_field_consistency
    flow_id: subentity_validation
    priority: med
    rationale: Crystallized narratives must exist and be in found_narratives
```

## OBJECTIVES COVERAGE

| Objective | Indicators | Why These Signals Matter |
|-----------|------------|--------------------------|
| Physics-ready structure | schema_compliance, required_fields_present | Physics needs valid weight/energy values |
| Project-agnostic foundation | link_structure_valid | Link constraints are universal |
| Minimal surface area | required_fields_present | Only essential fields checked |

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: stdout (CLI output)
  result:
    representation: enum
    value: HEALTHY | UNHEALTHY
    updated_at: per-run
    source: check_health.py HealthReport.is_healthy
```

---

## CHECKER INDEX

```yaml
checkers:
  - name: check_health_cli
    purpose: Full graph schema validation via CLI
    status: active
    priority: high

  - name: test_schema_pytest
    purpose: Schema validation test suite
    status: active
    priority: high

  - name: mind_doctor_integration
    purpose: Schema check as part of mind doctor
    status: pending
    priority: med

  # v1.6.1 SubEntity Checkers
  - name: subentity_tree_checker
    purpose: Validate parent/sibling/children consistency (V15)
    status: pending
    priority: high

  - name: found_narratives_checker
    purpose: Validate (id, alignment) tuple format (V16)
    status: pending
    priority: high

  - name: crystallization_embedding_checker
    purpose: Verify non-null embeddings of correct dimension (V17, V18)
    status: pending
    priority: high

  - name: crystallized_consistency_checker
    purpose: Verify crystallized field matches found_narratives (V19)
    status: pending
    priority: med
```

---

## INDICATOR: Schema Compliance

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: schema_compliance
  client_value: Prevents runtime errors from malformed graph data
  validation:
    - validation_id: V1
      criteria: All link endpoints must exist
    - validation_id: V6
      criteria: Required fields (id, name, node_type, type) present
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - enum
    - float_0_1
  semantics:
    enum: HEALTHY (0 errors), UNHEALTHY (1+ errors)
    float_0_1: (total_nodes - error_nodes) / total_nodes
  aggregation:
    method: Any error → UNHEALTHY
    display: enum for CLI, float for dashboards
```

### DOCKS SELECTED

```yaml
docks:
  input:
    id: dock_graph_connection
    method: db.graph_ops.GraphOps._query
    location: mind/graph/health/check_health.py:272
  output:
    id: dock_validation_result
    method: HealthReport.to_dict
    location: mind/graph/health/check_health.py:79
```

### ALGORITHM / CHECK MECHANISM

```yaml
mechanism:
  summary: Query all nodes by type, check each against schema, accumulate issues
  steps:
    - Load merged schema (base + project)
    - For each node type, query all nodes
    - For each node, check required fields
    - For each node, check enum values
    - Generate HealthReport with all issues
  data_required: Graph connection, schema files
  failure_mode: Non-empty issues list with severity=error
```

### INDICATOR

```yaml
indicator:
  error:
    - name: missing_required_field
      linked_validation: [V6]
      meaning: Node lacks id, name, or type
      default_action: alert
    - name: orphan_link
      linked_validation: [V1]
      meaning: Link references non-existent node
      default_action: alert
  warning:
    - name: invalid_enum_value
      linked_validation: [V6]
      meaning: Enum field has unexpected value
      default_action: log
  info:
    - name: missing_optional_field
      linked_validation: []
      meaning: Optional field not set
      default_action: ignore
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: manual or mind doctor
  max_frequency: 10/hour
  burst_limit: none (stateless)
  backoff: not applicable
```

### FORWARDINGS & DISPLAYS

```yaml
forwarding:
  targets:
    - location: stdout
      transport: CLI output
      notes: Primary interface for developers
    - location: JSON file (optional --json flag)
      transport: file
      notes: Machine-readable for automation
display:
  locations:
    - surface: CLI
      location: check_health.py print_summary()
      signal: HEALTHY/UNHEALTHY with issue counts
      notes: Color-coded, grouped by category
```

### MANUAL RUN

```yaml
manual_run:
  command: python mind/graph/health/check_health.py --graph seed --verbose
  notes: Run when debugging graph issues or after bulk imports
```

---

## HOW TO RUN

```bash
# Run CLI health check
python mind/graph/health/check_health.py --graph seed --verbose

# Run with JSON output
python mind/graph/health/check_health.py --graph seed --json

# Run pytest suite
pytest mind/graph/health/test_schema.py -v

# Run specific test
pytest mind/graph/health/test_schema.py::test_character_required_fields -v
```

---

## INDICATOR: SubEntity Integrity (v1.6.1)

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: subentity_integrity
  client_value: Ensures SubEntity exploration produces valid results
  validation:
    - validation_id: V15
      criteria: Tree structure consistent (siblings share parent, children point to parent)
    - validation_id: V16
      criteria: found_narratives are (id, alignment) tuples
    - validation_id: V17
      criteria: crystallization_embedding is non-null and correct dimension
    - validation_id: V18
      criteria: All siblings have crystallization_embedding for divergence
    - validation_id: V19
      criteria: crystallized field exists in found_narratives with alignment 1.0
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - enum
    - float_0_1
  semantics:
    enum: HEALTHY (0 tree errors), UNHEALTHY (1+ errors)
    float_0_1: (total_subentities - error_subentities) / total_subentities
  aggregation:
    method: Any tree error → UNHEALTHY
    display: enum for CLI, float for dashboards
```

### ALGORITHM / CHECK MECHANISM

```yaml
mechanism:
  summary: Validate SubEntity tree structure and field consistency at each state transition
  steps:
    - For each SubEntity, verify parent/sibling/children consistency
    - Check found_narratives format (list of 2-tuples)
    - Verify crystallization_embedding is non-null
    - If crystallized is set, verify it exists in found_narratives
    - Check sibling embeddings are available for divergence computation
  data_required: SubEntity instance during exploration
  failure_mode: Validation error blocks state transition
```

### INDICATOR

```yaml
indicator:
  error:
    - name: tree_inconsistency
      linked_validation: [V15]
      meaning: Sibling doesn't share parent or child doesn't point to parent
      default_action: block_transition
    - name: malformed_found_narratives
      linked_validation: [V16]
      meaning: Item in found_narratives is not (id, alignment) tuple
      default_action: block_transition
    - name: null_crystallization_embedding
      linked_validation: [V17]
      meaning: crystallization_embedding is null or wrong dimension
      default_action: block_transition
  warning:
    - name: missing_sibling_embedding
      linked_validation: [V18]
      meaning: Sibling lacks crystallization_embedding
      default_action: log
    - name: crystallized_not_in_found
      linked_validation: [V19]
      meaning: crystallized field not in found_narratives
      default_action: alert
```

---

## KNOWN GAPS

| VALIDATION Criterion | Checker Status | Notes |
|----------------------|----------------|-------|
| V1 Link endpoints | Partial | Structure checked, not all link types |
| V2 Physics ranges | Partial | Defined in schema, not explicitly checked |
| V3 Polarity range | Partial | Only BELIEVES links checked |
| V4 No mutation | By design | Read-only queries |
| V5 No LLM | By design | No LLM imports |
| V6 Required fields | Covered | All node types checked |
| V15 SubEntity tree | Pending | v1.6.1 - not yet implemented |
| V16 Found narratives | Pending | v1.6.1 - not yet implemented |
| V17 Crystallization embedding | Pending | v1.6.1 - not yet implemented |
| V18 Sibling embeddings | Pending | v1.6.1 - not yet implemented |
| V19 Crystallized consistency | Pending | v1.6.1 - not yet implemented |

<!-- @mind:todo Add explicit physics range checks (V2) for weight/energy/strength on all nodes/links -->
<!-- @mind:todo Extend polarity check (V3) to all link types that have polarity field -->
<!-- @mind:todo Add link type endpoint validation (valid_from/valid_to from schema) -->

---

## MARKERS

<!-- @mind:todo MIND_DOCTOR_INTEGRATION: Integrate check_health.py into mind doctor command. Currently runs separately. -->

<!-- @mind:proposition DASHBOARD_INTEGRATION: Expose HealthReport as JSON endpoint for monitoring dashboards. Would enable continuous schema health monitoring. -->

<!-- @mind:escalation PARTIAL_COVERAGE: V2 and V3 are only partially checked. Should we add explicit checks, or is schema-defined ranges sufficient? Current state works but may miss violations. -->
