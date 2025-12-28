# Core Utils — Health: Verification Mechanics and Coverage

```
STATUS: STABLE
CREATED: 2025-12-20
```

---

## PURPOSE OF THIS FILE

This file defines how core_utils health is verified for template resolution and docs module discovery. It exists to reduce the risk of CLI/template failures and doc discovery regressions. It does not verify CLI command behavior, doc content correctness, or downstream module logic.

---

## WHY THIS PATTERN

HEALTH is separated so runtime checks can confirm that filesystem lookups return expected paths and module directories. This avoids the failure mode where tests pass but runtime paths are wrong due to environment differences.

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Core_Utils_Functions.md
BEHAVIORS:       ./BEHAVIORS_Core_Utils_Helper_Effects.md
ALGORITHM:       ./ALGORITHM_Template_Path_Resolution_And_Doc_Discovery.md
VALIDATION:      ./VALIDATION_Core_Utils_Invariants.md
IMPLEMENTATION:  ./IMPLEMENTATION_Core_Utils_Code_Architecture.md
THIS:            HEALTH_Core_Utils_Verification.md
SYNC:            ./SYNC_Core_Utils_State.md

IMPL:            n/a (manual checks only)
```

> **Contract:** HEALTH checks verify input/output against VALIDATION with minimal or no code changes. After changes: update IMPL or add TODO to SYNC. Run HEALTH checks at throttled rates.

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: templates_path_resolution
    purpose: ensure CLI templates are discoverable
    triggers:
      - type: manual
        source: n/a
        notes: run when changing templates or packaging
    frequency:
      expected_rate: on-demand
      peak_rate: on-demand
      burst_behavior: none (manual only)
    risks:
      - V1
    notes: filesystem-only
  - flow_id: docs_module_discovery
    purpose: ensure doc module discovery excludes concepts and only returns doc-prefix directories
    triggers:
      - type: manual
        source: n/a
        notes: run after docs structure changes
    frequency:
      expected_rate: on-demand
      peak_rate: on-demand
      burst_behavior: none (manual only)
    risks:
      - V2
      - V3
    notes: filesystem-only
```

---

## HEALTH INDICATORS SELECTED

```yaml
health_indicators:
  - name: templates_path_valid
    flow_id: templates_path_resolution
    priority: med
    rationale: wrong templates path breaks CLI template usage
  - name: docs_module_discovery_valid
    flow_id: docs_module_discovery
    priority: low
    rationale: incorrect discovery affects tooling and validation
```

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: manual
  result:
    representation: enum
    value: UNKNOWN
    updated_at: 2025-12-20T00:00:00Z
    source: manual_status
```

---

## CHECKER INDEX

```yaml
checkers:
  - name: templates_path_check
    purpose: verify V1 by calling get_templates_path()
    status: pending
    priority: med
  - name: docs_module_discovery_check
    purpose: verify V2/V3 by calling find_module_directories()
    status: pending
    priority: low
```

---

## INDICATOR: templates_path_valid

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: templates_path_valid
  client_value: ensures CLI template generation uses the correct directory
  validation:
    - validation_id: V1
      criteria: get_templates_path returns a templates directory that includes templates/mind
```

### HEALTH REPRESENTATION

```yaml
representation:
  allowed:
    - enum
  selected:
    - enum
  semantics:
    enum: OK/WARN/ERROR/UNKNOWN
  aggregation:
    method: n/a
    display: enum
```

### DOCKS SELECTED

```yaml
docks:
  output:
    id: dock_templates_path_return
    method: mind.core_utils.get_templates_path
    location: mind/core_utils.py:36
```

### ALGORITHM / CHECK MECHANISM

```yaml
mechanism:
  summary: call get_templates_path and confirm returned path includes templates/mind
  steps:
    - call get_templates_path()
    - verify returned path contains the mind subtree
  data_required: filesystem state
  failure_mode: FileNotFoundError or missing mind subtree
```

### INDICATOR

```yaml
indicator:
  error:
    - name: templates_path_missing
      linked_validation: [V1]
      meaning: templates path not found or invalid
      default_action: warn
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: manual
  max_frequency: on-demand
  burst_limit: 1
  backoff: n/a
```

### FORWARDINGS & DISPLAYS

```yaml
forwarding:
  targets:
    - location: manual logs
      transport: file
      notes: manual verification notes
```

```yaml
display:
  locations:
    - surface: CLI
      location: manual run output
      signal: ok/warn
      notes: printed Path or error message
```

### MANUAL RUN

```yaml
manual_run:
  command: python - <<'PY'
import mind.core_utils as cu
print(cu.get_templates_path())
PY
  notes: run after template path changes
```

---

## INDICATOR: docs_module_discovery_valid

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: docs_module_discovery_valid
  client_value: keeps documentation tooling aligned with actual module layout
  validation:
    - validation_id: V2
      criteria: docs/concepts is excluded from discovery
    - validation_id: V3
      criteria: only doc-prefix directories are returned
```

### HEALTH REPRESENTATION

```yaml
representation:
  allowed:
    - enum
  selected:
    - enum
  semantics:
    enum: OK/WARN/ERROR/UNKNOWN
  aggregation:
    method: n/a
    display: enum
```

### DOCKS SELECTED

```yaml
docks:
  output:
    id: dock_module_list_return
    method: mind.core_utils.find_module_directories
    location: mind/core_utils.py:67
```

### ALGORITHM / CHECK MECHANISM

```yaml
mechanism:
  summary: call find_module_directories on docs/ and ensure concepts is excluded
  steps:
    - call find_module_directories(Path('docs'))
    - ensure returned paths exclude docs/concepts
    - confirm each returned directory contains doc-prefix files
  data_required: filesystem state
  failure_mode: concepts included or non-doc directories returned
```

### INDICATOR

```yaml
indicator:
  warning:
    - name: discovery_includes_non_doc_dir
      linked_validation: [V2, V3]
      meaning: discovery list contains invalid directories
      default_action: warn
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: manual
  max_frequency: on-demand
  burst_limit: 1
  backoff: n/a
```

### FORWARDINGS & DISPLAYS

```yaml
forwarding:
  targets:
    - location: manual logs
      transport: file
      notes: manual verification notes
```

```yaml
display:
  locations:
    - surface: CLI
      location: manual run output
      signal: ok/warn
      notes: printed module list
```

### MANUAL RUN

```yaml
manual_run:
  command: python - <<'PY'
from pathlib import Path
import mind.core_utils as cu
print([p.as_posix() for p in cu.find_module_directories(Path('docs'))])
PY
  notes: run after docs structure changes
```

---

## HOW TO RUN

```bash
# Manual checks only
python - <<'PY'
import mind.core_utils as cu
from pathlib import Path
print(cu.get_templates_path())
print([p.as_posix() for p in cu.find_module_directories(Path('docs'))])
PY
```

---

## KNOWN GAPS

<!-- @mind:todo No automated health check runner for core_utils yet. -->

---

## MARKERS

<!-- @mind:todo Decide whether to add a small health check script under mind/health/. -->
