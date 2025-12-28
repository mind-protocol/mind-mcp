# IMPLEMENTATION: Coverage Validation System
@mind:id: IMPLEMENTATION.COVERAGE.VALIDATION.SYSTEM

```
STATUS: DESIGNING
PURPOSE: Code structure and file locations for coverage validation
```

---

## Directory Structure

```
specs/
├── coverage.yaml              # Single source of truth
└── README.md                  # How to update coverage spec

tools/
└── coverage/
    ├── __init__.py
    ├── validate.py            # Main validator script
    ├── models.py              # Data classes (Gap, CoverageResult, etc.)
    ├── loaders.py             # YAML loading utilities
    ├── checks/
    │   ├── __init__.py
    │   ├── detection_check.py # V-COV-001, V-COV-011
    │   ├── skill_check.py     # V-COV-002, V-COV-003, V-COV-004, V-COV-012
    │   ├── protocol_check.py  # V-COV-005, V-COV-006, V-COV-007, V-COV-008
    │   └── call_graph_check.py # V-COV-009, V-COV-010
    └── report.py              # Markdown report generator

docs/concepts/coverage/
├── OBJECTIVES_Coverage_Validation.md
├── PATTERNS_Coverage_Validation.md
├── BEHAVIORS_Coverage_Validation.md
├── ALGORITHM_Coverage_Validation.md
├── VALIDATION_Coverage_Validation.md
├── IMPLEMENTATION_Coverage_Validation.md  # This file
└── SYNC_Coverage_Validation.md

# Generated
COVERAGE_REPORT.md             # Output from validator
```

---

## Coverage Spec Format

```yaml
# specs/coverage.yaml

version: "1.0"

doctor_workflow:
  detections:
    # Documentation health
    - id: "D-UNDOC-CODE"
      trigger: "Undocumented code directory"
      category: doc_health
      skill: "mind.create_module_docs"

    - id: "D-PLACEHOLDER-DOCS"
      trigger: "Placeholder docs ({template})"
      category: doc_health
      skill: "mind.create_module_docs"

    - id: "D-ORPHAN-DOCS"
      trigger: "Orphaned docs (point to deleted code)"
      category: doc_health
      skill: "mind.create_module_docs"

    - id: "D-STALE-SYNC"
      trigger: "Stale SYNC (not updated recently)"
      category: doc_health
      skill: "mind.update_sync"

    - id: "D-INCOMPLETE-CHAIN"
      trigger: "Incomplete doc chain"
      category: doc_health
      skill: "mind.create_module_docs"

    # Module definition
    - id: "D-NO-MAPPING"
      trigger: "Missing modules.yaml entry"
      category: module_def
      skill: "mind.module_define_boundaries"

    - id: "D-NO-OBJECTIVES"
      trigger: "Missing OBJECTIVES"
      category: module_def
      skill: "mind.module_define_boundaries"

    - id: "D-NO-PATTERNS"
      trigger: "Missing PATTERNS"
      category: module_def
      skill: "mind.module_define_boundaries"

    # Code structure
    - id: "D-MONOLITH"
      trigger: "Monolith file (>500 lines)"
      category: code_struct
      skill: "mind.implement_with_docs"

    - id: "D-NO-IMPL-DOC"
      trigger: "No IMPLEMENTATION doc"
      category: code_struct
      skill: "mind.implement_with_docs"

    # Health verification
    - id: "D-NO-HEALTH"
      trigger: "No health indicators for module"
      category: health_ver
      skill: "mind.health_define_and_verify"

    - id: "D-VALIDATION-NO-HEALTH"
      trigger: "Validation without health check"
      category: health_ver
      skill: "mind.health_define_and_verify"

    # Escalation management
    - id: "D-STUCK-MODULE"
      trigger: "Stuck module (DESIGNING with no activity)"
      category: escalation
      skill: "mind.debug_investigate"

    - id: "D-UNRESOLVED-ESC"
      trigger: "Unresolved escalation"
      category: escalation
      skill: "mind.debug_investigate"

    - id: "D-TODO-ROT"
      trigger: "TODO rot (aging backlog)"
      category: escalation
      skill: "mind.debug_investigate"

skills:
  mind.create_module_docs:
    file: "templates/mind/skills/SKILL_Create_Module_Documentation_Chain_From_Templates_And_Seed_Todos.md"
    protocols:
      - explore_space
      - create_doc_chain

  mind.module_define_boundaries:
    file: "templates/mind/skills/SKILL_Define_Module_Boundaries_Objectives_And_Scope.md"
    protocols:
      - explore_space
      - define_space
      - add_objectives
      - add_patterns

  mind.implement_with_docs:
    file: "templates/mind/skills/SKILL_Implement_Write_Or_Modify_Code_With_Doc_Chain_Coupling.md"
    protocols:
      - explore_space
      - add_implementation
      - record_work

  mind.health_define_and_verify:
    file: "templates/mind/skills/SKILL_Define_And_Verify_Health_Signals_Mapped_To_Validation_Invariants.md"
    protocols:
      - explore_space
      - add_invariant
      - add_health_coverage

  mind.debug_investigate:
    file: "templates/mind/skills/SKILL_Debug_Investigate_And_Fix_Issues_With_Evidence_First.md"
    protocols:
      - investigate
      - raise_escalation
      - resolve_blocker
      - capture_decision

  mind.update_sync:
    file: "templates/mind/skills/SKILL_Update_Module_Sync_State_And_Record_Markers.md"
    protocols:
      - record_work
      - update_sync

protocols:
  # Phase 1: Core
  explore_space:
    file: "protocols/explore_space.yaml"
    phase: 1
    output_nodes: [moment]
    output_links: [about, expresses]

  record_work:
    file: "protocols/record_work.yaml"
    phase: 1
    output_nodes: [moment]
    output_links: [about, expresses, references]

  investigate:
    file: "protocols/investigate.yaml"
    phase: 1
    output_nodes: [moment, escalation, decision]
    output_links: [about, expresses, triggers, proposes]

  # Phase 2: Doc chain
  add_objectives:
    file: "protocols/add_objectives.yaml"
    phase: 2
    output_nodes: [narrative_objective, moment]
    output_links: [contains, supports, bounds]

  add_patterns:
    file: "protocols/add_patterns.yaml"
    phase: 2
    output_nodes: [narrative_pattern, moment]
    output_links: [contains, expresses]

  update_sync:
    file: "protocols/update_sync.yaml"
    phase: 2
    output_nodes: [narrative_sync, moment]
    output_links: [contains, expresses]

  # Phase 3: Verification
  add_invariant:
    file: "protocols/add_invariant.yaml"
    phase: 3
    output_nodes: [narrative_validation, moment]
    output_links: [contains, ensures]

  add_health_coverage:
    file: "protocols/add_health_coverage.yaml"
    phase: 3
    output_nodes: [narrative_health, thing_dock, moment]
    output_links: [contains, verifies, attached_to]

  add_implementation:
    file: "protocols/add_implementation.yaml"
    phase: 3
    output_nodes: [narrative_implementation, thing_dock, moment]
    output_links: [contains, expresses]

  # Phase 4: Issue handling
  raise_escalation:
    file: "protocols/raise_escalation.yaml"
    phase: 4
    output_nodes: [escalation, moment]
    output_links: [about, expresses]

  resolve_blocker:
    file: "protocols/resolve_blocker.yaml"
    phase: 4
    output_nodes: [moment]
    output_links: [resolves, expresses]

  capture_decision:
    file: "protocols/capture_decision.yaml"
    phase: 4
    output_nodes: [narrative_decision, moment]
    output_links: [contains, affects, expresses]

  # Phase 5: Full coverage
  define_space:
    file: "protocols/define_space.yaml"
    phase: 5
    output_nodes: [space, moment]
    output_links: [expresses]

  create_doc_chain:
    file: "protocols/create_doc_chain.yaml"
    phase: 5
    output_nodes: [narrative_objectives, narrative_patterns, narrative_sync, moment]
    output_links: [contains, expresses]

  add_goals:
    file: "protocols/add_goals.yaml"
    phase: 5
    output_nodes: [narrative_goal, moment]
    output_links: [contains, expresses]

  add_todo:
    file: "protocols/add_todo.yaml"
    phase: 5
    output_nodes: [todo, moment]
    output_links: [about, expresses]
```

---

## Docking Points

### Input Dock: specs/coverage.yaml

All coverage data flows from this file. Validator reads it.

### Output Dock: COVERAGE_REPORT.md

Generated report with current coverage state.

### Check Dock: tools/coverage/validate.py

Entry point for validation. Called by CI.

---

## CLI Interface

```bash
# Run validation
python -m tools.coverage.validate

# Run with verbose output
python -m tools.coverage.validate --verbose

# Generate report only (no exit code)
python -m tools.coverage.validate --report-only

# Check specific phase
python -m tools.coverage.validate --phase 1
```

---

## CI Integration

```yaml
# .github/workflows/coverage.yaml
name: Coverage Validation

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install pyyaml
      - run: python -m tools.coverage.validate
      - uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: COVERAGE_REPORT.md
```

---

## Dependencies

```
pyyaml >= 6.0    # YAML parsing
```

No other dependencies. Keeps validator lightweight.

---

## CHAIN

- **Prev:** VALIDATION_Coverage_Validation.md
- **Next:** SYNC_Coverage_Validation.md
