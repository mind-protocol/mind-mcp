# Data Models — Health: Pydantic Schema Integrity

```
STATUS: DRAFT
CREATED: 2025-12-20
UPDATED: 2025-12-20
```

---

## PURPOSE OF THIS FILE

This file defines the health checks and verification mechanics for the `runtime/models/` module. It ensures the integrity and consistency of the game's data schema, protecting against type mismatches, missing required fields, and incorrect value ranges.

What it protects:
- **Type Safety**: Ensuring all data adheres to Python type hints and Pydantic field definitions.
- **Schema Consistency**: Guaranteeing that models reflect the intended data structure across the application.
- **Data Integrity**: Preventing invalid data from entering the system by enforcing constraints.

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Models.md
BEHAVIORS:       ./BEHAVIORS_Models.md
ALGORITHM:       ./ALGORITHM_Models.md
VALIDATION:      ./VALIDATION_Models.md
IMPLEMENTATION:  ./IMPLEMENTATION_Models.md
THIS:            HEALTH_Models.md
SYNC:            ./SYNC_Models.md

IMPL:            mind/models/
```

> **Contract:** HEALTH checks verify data model compliance and prevent schema drift.

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: model_ingestion
    purpose: Convert raw input into validated Pydantic models.
    triggers:
      - type: api_call
        source: API endpoints (e.g., /api/playthrough)
      - type: file_load
        source: World Scraper (YAML injection)
    frequency:
      expected_rate: high (multiple times per game tick or API request)
      peak_rate: very_high (during bulk data loads)
      burst_behavior: Synchronous, validation can introduce latency.
    risks:
      - `ValidationError` on malformed input breaking downstream logic.
      - Performance impact from complex validation on hot paths.
```

---

## HEALTH INDICATORS SELECTED

```yaml
health_indicators:
  - name: model_validation_success
    flow_id: model_ingestion
    priority: critical
    rationale: Core data integrity relies on models successfully validating.
  - name: enum_consistency
    flow_id: model_ingestion
    priority: high
    rationale: Invalid enum values lead to runtime errors and corrupted data.
```

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: logs
  result:
    representation: enum
    value: OK
    updated_at: 2025-12-20T10:45:00Z
    source: automated_tests
```

---

## CHECKER INDEX

```yaml
checkers:
  - name: pydantic_validation_checker
    purpose: Assert that models raise `ValidationError` for invalid inputs (E1, E2).
    status: active
    priority: critical
  - name: mutable_default_checker
    purpose: Identify and flag mutable default fields not using `default_factory` (V4).
    status: active
    priority: high
```

---

## INDICATOR: model_validation_success

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: model_validation_success
  client_value: Ensures game data is reliable, preventing crashes and unexpected behavior.
  validation:
    - validation_id: V1 (Models)
      criteria: All required fields are present and valid.
    - validation_id: V2 (Models)
      criteria: Enum fields use valid members.
```

### DOCKS SELECTED

```yaml
docks:
  input:
    id: raw_data_input
    method: engine.models.nodes.Character.__init__
    location: mind/models/nodes.py:53
  output:
    id: validated_model_output
    method: engine.models.nodes.Character.__init__
    location: mind/models/nodes.py:53
```

---

## HOW TO RUN

```bash
# Execute all tests for the data models module
pytest tests/mind/models/ -v

# Run Pydantic schema consistency checks
python scripts/verify_schema_consistency.py
```

---

## MARKERS

### Missing Health Check Implementation

<!-- @mind:todo Implement a checker for mutable default fields not using `default_factory` (V4). -->
<!-- @mind:todo Develop property-based tests for model serialization roundtrip (P1) and derived properties (P2). -->

### Ideas for Improvement

<!-- @mind:proposition Integrate Pydantic's `Config.extra = 'forbid'` into health checks to detect unexpected fields in incoming data. -->
<!-- @mind:proposition Monitor `ValidationError` rates in production logs as a real-time health indicator for data quality. -->

### Open Questions

<!-- @mind:escalation What is the acceptable latency for model instantiation during high-frequency data ingestion? -->