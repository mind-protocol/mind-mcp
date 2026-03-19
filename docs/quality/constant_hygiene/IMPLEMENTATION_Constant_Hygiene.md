# Constant Hygiene — Implementation

```
STATUS: DESIGNING
CREATED: 2026-03-19
```

---

## CHAIN

```
RESULTS:         ./RESULTS_Constant_Hygiene.yaml
OBJECTIVES:      ./OBJECTIVES_Constant_Hygiene.md
PATTERNS:        ./PATTERNS_Constant_Hygiene.md
BEHAVIORS:       ./BEHAVIORS_Constant_Hygiene.md
ALGORITHM:       ./ALGORITHM_Constant_Hygiene.md
VALIDATION:      ./VALIDATION_Constant_Hygiene.md
THIS:            IMPLEMENTATION_Constant_Hygiene.md
HEALTH:          ./HEALTH_Constant_Hygiene.md
SYNC:            ./SYNC_Constant_Hygiene.md

IMPL:            runtime/orchestrator/constant_hygiene.py
```

---

## CODE STRUCTURE

```
runtime/orchestrator/
└── constant_hygiene.py    # detection, analysis, concept injection (~250L)

docs/quality/constant_hygiene/
├── RESULTS_Constant_Hygiene.yaml
├── OBJECTIVES_Constant_Hygiene.md
├── PATTERNS_Constant_Hygiene.md
├── BEHAVIORS_Constant_Hygiene.md
├── ALGORITHM_Constant_Hygiene.md
├── VALIDATION_Constant_Hygiene.md
├── IMPLEMENTATION_Constant_Hygiene.md  (this file)
├── HEALTH_Constant_Hygiene.md
├── SYNC_Constant_Hygiene.md
└── SENSES_Constant_Hygiene.yaml
```

### File Responsibilities

| File | Purpose | Key Functions | Lines | Status |
|------|---------|---------------|-------|--------|
| `runtime/orchestrator/constant_hygiene.py` | Detection + analysis + concept injection | `evaluate()`, `scan_recent_commits()`, `_detect_constants_in_diff()`, `_inject_concept()` | ~250 | OK |
| `runtime/orchestrator/dispatcher.py` | Calls evaluate() in maintenance loop | `_maintenance()` | (modified, +15L) | OK |

### Why the code lives in orchestrator/

The constant_hygiene module is conceptually about code quality (a quality/ concern), but operationally it runs inside the dispatcher's maintenance loop — it needs the shared graph instance and the maintenance cycle timing. The code lives where it executes. The docs live where it belongs conceptually.

---

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| `evaluate(graph, repo_path)` | `constant_hygiene.py:evaluate()` | dispatcher._maintenance() every ACCOUNT_REFRESH_INTERVAL |

---

## DATA FLOW

```yaml
flow:
  name: constant_detection
  purpose: Detect hardcoded constants in commits and inject awareness into citizens
  steps:
    - id: query_commits
      file: runtime/orchestrator/constant_hygiene.py
      function: scan_recent_commits
      input: graph, repo_path
      output: list of unscanned commit Moments
      trigger: dispatcher._maintenance()
    - id: read_diff
      file: runtime/orchestrator/constant_hygiene.py
      function: _get_commit_diff
      input: repo_path, commit_hash
      output: diff text (string)
      trigger: for each unscanned commit
      side_effects: subprocess git call
    - id: detect_patterns
      file: runtime/orchestrator/constant_hygiene.py
      function: _detect_constants_in_diff
      input: diff text
      output: list of {file, line, pattern}
      trigger: after diff read
    - id: inject_concept
      file: runtime/orchestrator/constant_hygiene.py
      function: _inject_concept
      input: graph, citizen, commit_hash, constants
      output: Concept node + OBSERVED_IN link in L3
      trigger: if constants found
      side_effects: graph write (Concept + link)
    - id: mark_scanned
      file: runtime/orchestrator/constant_hygiene.py
      function: _mark_scanned
      input: graph, moment_id
      output: none
      trigger: after processing (regardless of findings)
      side_effects: graph write (SET scanned=true)
```

---

## MODULE DEPENDENCIES

| Module | Why |
|--------|-----|
| `orchestrator/dispatcher` | Calls evaluate() in maintenance loop, provides shared graph |
| `orchestrator/activation_pressure` | Not directly used — but pressure context could be added for energy scaling |
| FalkorDB | Reads Moments, writes Concepts + links |
| Git | Reads commit diffs via subprocess |

Co-Authored-By: AI Citizen (@mechanical_visionary) <mechanical_visionary@mindprotocol.ai>
