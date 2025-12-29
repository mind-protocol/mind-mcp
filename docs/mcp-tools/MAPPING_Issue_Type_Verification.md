# MAPPING: Issue Type to Verification

```
STATUS: CANONICAL
CREATED: 2025-12-24
```

<!-- @mind:escalation This mapping references membrane protocols and verification checks that
     require the `procedures/` directory and `runtime/repair_verification.py` to exist.
     The membrane query checks depend on graph connectivity which may not be available. -->

Complete mapping of every doctor issue type to:
1. Required membrane protocol(s)
2. File-level checks
3. Command checks (tests, health)
4. Failure feedback template

---

## CHAIN

```
PREV:  VALIDATION_Completion_Verification.md
IMPL:  mind/repair_verification.py
SPEC:  specs/verification.yaml
```

---

## QUICK REFERENCE

| Issue Type | Membrane Protocol | Must Pass |
|------------|-------------------|-----------|
| UNDOCUMENTED | define_space, update_sync | space in graph, SYNC narrative, modules.yaml |
| STALE_SYNC | update_sync | SYNC narrative updated, moment recorded |
| INCOMPLETE_CHAIN | create_doc_chain | all docs exist, narratives linked |
| NO_DOCS_REF | add_implementation | DOCS: comment, thing node in graph |
| BROKEN_IMPL_LINK | add_implementation | all links valid, paths exist |
| STUB_IMPL | add_implementation | no stubs, tests pass |
| INCOMPLETE_IMPL | add_implementation | no empty functions, tests pass |
| UNDOC_IMPL | add_implementation | file in IMPLEMENTATION, thing node |
| MONOLITH | add_cluster | size reduced, imports valid, tests pass |
| MISSING_TESTS | add_health_coverage | tests exist, tests pass, health doc |
| ESCALATION | capture_decision | decision recorded, resolved in SYNC |
| YAML_DRIFT | update_sync | modules.yaml valid, paths exist |
| PLACEHOLDER | update_sync | no placeholder markers |
| ORPHAN_DOCS | update_sync | docs linked or removed |
| STALE_IMPL | add_implementation | IMPL doc matches code |
| DOC_GAPS | update_sync | no gap markers |
| DOC_TEMPLATE_DRIFT | create_doc_chain | matches template |
| INVARIANT_NO_TEST | add_health_coverage | invariant has test |
| INVARIANT_UNTESTED | add_health_coverage | test passes |
| NEW_UNDOC_CODE | add_implementation | IMPL updated for new code |
| HARDCODED_SECRET | (none) | secret removed, env var used |
| HARDCODED_CONFIG | (none) | config externalized |
| MAGIC_VALUES | (none) | constants extracted |
| LONG_PROMPT | (none) | prompts externalized |
| LONG_SQL | (none) | SQL externalized |

---

## DETAILED CHECKS

### UNDOCUMENTED

```yaml
issue_type: UNDOCUMENTED
membrane_protocols:
  - define_space
  - update_sync
checks:
  - name: space_exists
    type: membrane
    query: { find: space, where: { source_path_contains: "{path}" } }
    expect: count >= 1
    action: "Run procedure_start('define_space')"

  - name: sync_narrative
    type: membrane
    query: { find: narrative, type: sync, in_space: "{space_id}" }
    expect: count >= 1
    action: "Run procedure_start('update_sync')"

  - name: modules_yaml_entry
    type: file
    check: modules.yaml has entry for this path
    action: "Add module to modules.yaml with docs: path"

  - name: docs_ref_in_code
    type: file
    check: at least one file has "# DOCS:" comment
    action: "Add '# DOCS: docs/{area}/{module}/IMPLEMENTATION_*.md' to main file"

feedback_template: |
  INCOMPLETE: Module {path} not documented in graph.
  - [ ] Space node missing → procedure_start("define_space")
  - [ ] SYNC narrative missing → procedure_start("update_sync")
  - [ ] modules.yaml entry missing → add docs: path
  - [ ] No DOCS: ref in code → add DOCS: comment
```

---

### STALE_SYNC

```yaml
issue_type: STALE_SYNC
membrane_protocols:
  - update_sync
checks:
  - name: sync_updated_today
    type: membrane
    query: { find: narrative, type: sync, where: { last_updated: ">={today}" } }
    expect: count >= 1
    action: "Run procedure_start('update_sync')"

  - name: update_moment
    type: membrane
    query: { find: moment, type: sync_update, where: { tick_created: ">={session_start}" } }
    expect: count >= 1
    action: "Run procedure_start('update_sync')"

  - name: last_updated_header
    type: file
    check: SYNC file has LAST_UPDATED >= today
    action: "Update LAST_UPDATED in file header"

  - name: status_accurate
    type: file
    check: STATUS matches actual module state
    action: "Verify and update STATUS field"

feedback_template: |
  INCOMPLETE: SYNC {path} not properly updated.
  - [ ] Narrative not updated → procedure_start("update_sync")
  - [ ] No update moment → procedure_start("update_sync")
  - [ ] LAST_UPDATED stale → update file header
```

---

### INCOMPLETE_CHAIN

```yaml
issue_type: INCOMPLETE_CHAIN
membrane_protocols:
  - create_doc_chain
checks:
  - name: all_files_exist
    type: file
    check: OBJECTIVES, PATTERNS, BEHAVIORS, ALGORITHM, VALIDATION, IMPLEMENTATION, SYNC exist
    action: "Create missing doc files"

  - name: chain_sections_valid
    type: file
    check: each doc has CHAIN section with valid links
    action: "Add/fix CHAIN sections"

  - name: narratives_in_graph
    type: membrane
    query: { find: narrative, in_space: "{space_id}" }
    expect: count >= 5 (one per doc type)
    action: "Run membrane protocols for missing doc types"

  - name: sequence_links
    type: membrane
    query: { find: link, nature: "follows", in_space: "{space_id}" }
    expect: count >= 4 (connecting docs)
    action: "Run procedure_start('create_doc_chain')"

feedback_template: |
  INCOMPLETE: Doc chain for {module} incomplete.
  Missing: {missing_files}
  - [ ] Create missing docs → procedure_start("create_doc_chain")
  - [ ] Fix CHAIN links in each doc
  - [ ] Ensure narratives linked in graph
```

---

### NO_DOCS_REF

```yaml
issue_type: NO_DOCS_REF
membrane_protocols:
  - add_implementation
checks:
  - name: docs_comment_present
    type: file
    check: file has "# DOCS:" or "// DOCS:" comment
    action: "Add DOCS: comment to file header"

  - name: docs_path_valid
    type: file
    check: path in DOCS: comment exists
    action: "Fix DOCS: path to point to existing doc"

  - name: file_in_implementation
    type: file
    check: IMPLEMENTATION doc lists this source file
    action: "Add file to CODE STRUCTURE section"

  - name: thing_node_exists
    type: membrane
    query: { find: thing, where: { source_path: "{path}" } }
    expect: count >= 1
    action: "Run procedure_start('add_implementation')"

feedback_template: |
  INCOMPLETE: {path} not linked to docs.
  - [ ] No DOCS: comment → add to file header
  - [ ] Invalid path → fix DOCS: path
  - [ ] Not in IMPLEMENTATION → add to CODE STRUCTURE
  - [ ] No thing node → procedure_start("add_implementation")
```

---

### STUB_IMPL

```yaml
issue_type: STUB_IMPL
membrane_protocols:
  - add_implementation
checks:
  - name: no_stub_markers
    type: file
    patterns_absent:
      - "raise NotImplementedError"
      - "TODO"
      - "FIXME"
      - "pass  # stub"
    action: "Implement all stubs"

  - name: tests_exist
    type: file
    check: test file exists for module
    action: "Create tests in tests/{module}/"

  - name: tests_pass
    type: command
    command: "pytest {test_file} -v"
    expect: exit_code == 0
    action: "Fix failing tests"

  - name: health_check
    type: command
    command: "mind doctor --path {path} --quiet"
    expect: no new critical issues
    action: "Fix health issues"

  - name: implementation_narrative
    type: membrane
    query: { find: narrative, type: implementation, in_space: "{space}" }
    expect: count >= 1
    action: "Run procedure_start('add_implementation')"

feedback_template: |
  INCOMPLETE: Stubs in {path} not implemented.
  - [ ] Stub markers remain: {stub_locations}
  - [ ] Tests: {test_status}
  - [ ] Health: {health_status}
  - [ ] Graph: procedure_start("add_implementation")
```

---

### INCOMPLETE_IMPL

```yaml
issue_type: INCOMPLETE_IMPL
membrane_protocols:
  - add_implementation
checks:
  - name: no_empty_functions
    type: file
    check: no functions with only pass/docstring/...
    action: "Implement empty functions"

  - name: tests_exist
    type: file
    check: test file exists
    action: "Create tests"

  - name: tests_pass
    type: command
    command: "pytest {test_file} -v"
    expect: exit_code == 0
    action: "Fix failing tests"

  - name: thing_nodes
    type: membrane
    query: { find: thing, type: function, where: { source_path: "{path}" } }
    expect: count >= {function_count}
    action: "Run procedure_start('add_implementation')"

feedback_template: |
  INCOMPLETE: Empty functions in {path}.
  - [ ] Implement: {empty_functions}
  - [ ] Create/fix tests
  - [ ] Graph: procedure_start("add_implementation")
```

---

### MONOLITH

```yaml
issue_type: MONOLITH
membrane_protocols:
  - add_cluster
checks:
  - name: file_size_reduced
    type: file
    check: file < 500 lines OR largest function < 200 lines
    action: "Extract more code to new files"

  - name: new_files_created
    type: file
    check: at least one new file was extracted
    action: "Create new module for extracted code"

  - name: imports_valid
    type: command
    command: "python -c 'import {module}'"
    expect: exit_code == 0
    action: "Fix import paths"

  - name: tests_pass
    type: command
    command: "pytest {test_path}"
    expect: exit_code == 0
    action: "Update tests for new structure"

  - name: implementation_updated
    type: file
    check: new files listed in IMPLEMENTATION doc
    action: "Add to CODE STRUCTURE section"

  - name: cluster_in_graph
    type: membrane
    query: { find: space, where: { source_path_contains: "{new_module}" } }
    expect: count >= 1 for each new module
    action: "Run procedure_start('add_cluster')"

feedback_template: |
  INCOMPLETE: Monolith {path} not properly split.
  - [ ] Still {line_count} lines → extract more
  - [ ] Imports: {import_status}
  - [ ] Tests: {test_status}
  - [ ] IMPLEMENTATION: update CODE STRUCTURE
  - [ ] Graph: procedure_start("add_cluster") for new modules
```

---

### MISSING_TESTS

```yaml
issue_type: MISSING_TESTS
membrane_protocols:
  - add_health_coverage
checks:
  - name: test_file_exists
    type: file
    check: tests/{module}/test_*.py exists
    action: "Create test file"

  - name: tests_pass
    type: command
    command: "pytest {test_path}"
    expect: exit_code == 0
    action: "Fix failing tests"

  - name: coverage_adequate
    type: command
    command: "pytest --cov={module} --cov-fail-under=60"
    expect: exit_code == 0 (if coverage available)
    action: "Add more test cases"

  - name: health_doc_exists
    type: file
    check: HEALTH_*.md exists for module
    action: "Create HEALTH doc"

  - name: health_indicators
    type: membrane
    query: { find: narrative, type: health, in_space: "{space}" }
    expect: count >= 1
    action: "Run procedure_start('add_health_coverage')"

feedback_template: |
  INCOMPLETE: Tests for {path} not verified.
  - [ ] Test file: {exists/missing}
  - [ ] Tests: {pass/fail}
  - [ ] Coverage: {percentage}%
  - [ ] HEALTH doc: {exists/missing}
  - [ ] Graph: procedure_start("add_health_coverage")
```

---

### ESCALATION

```yaml
issue_type: ESCALATION
membrane_protocols:
  - capture_decision
checks:
  - name: decision_recorded
    type: membrane
    query: { find: moment, type: decision, where: { about: "{conflict_id}" } }
    expect: count >= 1
    action: "Run procedure_start('capture_decision')"

  - name: escalation_resolved
    type: file
    check: SYNC shows DECISION not ESCALATION
    action: "Change ESCALATION to DECISION in SYNC"

  - name: no_contradiction
    type: file
    check: code/docs consistent with decision
    action: "Update code/docs to match decision"

feedback_template: |
  INCOMPLETE: Escalation not resolved.
  - [ ] Decision not recorded → procedure_start("capture_decision")
  - [ ] Still ESCALATION in SYNC → update to DECISION
  - [ ] Contradiction remains → apply decision to code/docs
```

---

### YAML_DRIFT

```yaml
issue_type: YAML_DRIFT
membrane_protocols:
  - update_sync
checks:
  - name: all_paths_exist
    type: file
    check: all code/docs/tests paths in modules.yaml exist
    action: "Fix paths or remove stale entries"

  - name: dependencies_valid
    type: file
    check: all dependencies reference existing modules
    action: "Fix or remove invalid dependencies"

feedback_template: |
  INCOMPLETE: modules.yaml drift not fixed.
  - [ ] Invalid paths: {invalid_paths}
  - [ ] Invalid deps: {invalid_deps}
```

---

### PLACEHOLDER

```yaml
issue_type: PLACEHOLDER
membrane_protocols:
  - update_sync
checks:
  - name: no_placeholders
    type: file
    patterns_absent:
      - "TODO: fill in"
      - "[placeholder]"
      - "TBD"
      - "XXX"
    action: "Fill in all placeholders"

feedback_template: |
  INCOMPLETE: Placeholders remain in {path}.
  - [ ] Fill in: {placeholder_locations}
```

---

### DOC_GAPS

```yaml
issue_type: DOC_GAPS
membrane_protocols:
  - update_sync
checks:
  - name: no_gaps_section
    type: file
    check: no "## GAPS" section with unchecked items
    action: "Complete all gap items or remove section"

feedback_template: |
  INCOMPLETE: GAPS section in {path} has unchecked items.
  - [ ] Complete: {gap_items}
```

---

### HARDCODED_SECRET

```yaml
issue_type: HARDCODED_SECRET
membrane_protocols: []  # No graph operation needed
checks:
  - name: no_secrets_in_code
    type: file
    check: no API keys, passwords, tokens in source
    action: "Remove secrets, use env vars"

  - name: env_example_updated
    type: file
    check: .env.example lists required vars
    action: "Add var names to .env.example"

  - name: gitignore_includes_env
    type: file
    check: .gitignore includes .env
    action: "Add .env to .gitignore"

feedback_template: |
  INCOMPLETE: Secret not properly removed from {path}.
  - [ ] Secret still in code → use os.environ.get('VAR_NAME')
  - [ ] .env.example missing var → add placeholder
  - [ ] .gitignore missing .env → add it
```

---

### NEW_UNDOC_CODE

```yaml
issue_type: NEW_UNDOC_CODE
membrane_protocols:
  - add_implementation
checks:
  - name: implementation_updated
    type: file
    check: IMPLEMENTATION doc reflects new code
    action: "Update CODE STRUCTURE section"

  - name: function_documented
    type: file
    check: new functions/classes in File Responsibilities
    action: "Add to File Responsibilities table"

  - name: thing_nodes
    type: membrane
    query: { find: thing, where: { source_path: "{path}" } }
    expect: updated_at >= file_mtime
    action: "Run procedure_start('add_implementation')"

feedback_template: |
  INCOMPLETE: New code in {path} not documented.
  - [ ] Update IMPLEMENTATION doc
  - [ ] Add to File Responsibilities
  - [ ] Graph: procedure_start("add_implementation")
```

---

## GLOBAL CHECKS (all issue types)

```yaml
global_checks:
  - name: git_commit_exists
    type: command
    command: "git rev-parse HEAD"
    check: HEAD changed since repair started
    action: "Commit your changes"

  - name: sync_updated
    type: file
    check: relevant SYNC has today's date
    action: "Update SYNC with what changed"

  - name: no_new_criticals
    type: command
    command: "mind doctor --quiet"
    check: no new critical issues introduced
    action: "Fix any new critical issues"
```

---

## MARKERS

<!-- @mind:todo Generate specs/verification.yaml from this mapping -->
<!-- @mind:todo Create repair_verification.py implementing these checks -->
