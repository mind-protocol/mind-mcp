# Core Utils — Implementation: Code Architecture and Structure

```
STATUS: STABLE
CREATED: 2025-12-20
```

---

## CHAIN

```
PATTERNS:       ./PATTERNS_Core_Utils_Functions.md
BEHAVIORS:      ./BEHAVIORS_Core_Utils_Helper_Effects.md
ALGORITHM:      ./ALGORITHM_Template_Path_Resolution_And_Doc_Discovery.md
VALIDATION:     ./VALIDATION_Core_Utils_Invariants.md
THIS:           IMPLEMENTATION_Core_Utils_Code_Architecture.md
HEALTH:         ./HEALTH_Core_Utils_Verification.md
SYNC:           ./SYNC_Core_Utils_State.md

IMPL:           mind/core_utils.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

```
mind/
├── core_utils.py          # shared filesystem and docs utilities
```

### File Responsibilities

| File | Purpose | Key Functions/Classes | Lines | Status |
|------|---------|----------------------|-------|--------|
| `runtime/core_utils.py` | core helper functions and constants | `get_templates_path`, `find_module_directories` | ~106 | OK |

**Size Thresholds:**
- **OK** (<400 lines): Healthy size, easy to understand
- **WATCH** (400-700 lines): Getting large, consider extraction opportunities
- **SPLIT** (>700 lines): Too large, must split before adding more code

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Layered utility module

**Why this pattern:** The helpers provide low-level, dependency-light functionality that other modules can import without circular dependencies.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Guarded fallback | `runtime/core_utils.py:get_templates_path` | Select the first valid templates location with a clear fallback order |
| Prefix-based discovery | `runtime/core_utils.py:find_module_directories` | Identify module docs without hard-coding names |

### Anti-Patterns to Avoid

- **Domain-specific helpers**: Keep logic generic; move domain-specific utilities into their own modules.
- **Hidden global state**: Avoid mutable globals that alter behavior across imports.
- **Premature abstraction**: Do not introduce new helpers until there are 3+ clear call sites.

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Core utilities | filesystem helpers, constants | CLI command logic, doc rendering, CLI | `get_templates_path`, `find_module_directories` |

---

## SCHEMA

No custom schemas. Uses `Path` from the standard library.

---

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| `get_templates_path` | `runtime/core_utils.py:36` | CLI or templates lookup calls |
| `find_module_directories` | `runtime/core_utils.py:67` | docs scanning utilities |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

### Templates Resolution: Choose the first valid templates path

This flow determines where templates are loaded from. It is low-risk but impacts CLI actions that rely on templates.

```yaml
flow:
  name: templates_path_resolution
  purpose: locate templates/mind for installed or repo use
  scope: filesystem reads only
  steps:
    - id: check_package_templates
      description: test package-local templates path
      file: mind/core_utils.py
      function: get_templates_path
      input: Path(__file__).parent
      output: Path or continue
      trigger: CLI action requiring templates
      side_effects: filesystem exists checks
    - id: check_repo_templates
      description: test repo-root templates path
      file: mind/core_utils.py
      function: get_templates_path
      input: repo_root
      output: Path or error
      trigger: fallback after package check
      side_effects: filesystem exists checks
  docking_points:
    guidance:
      include_when: input/output changes the chosen templates path
      omit_when: trivial exists checks
      selection_notes: choose the return decision point for health
    available:
      - id: dock_templates_path_return
        type: file
        direction: output
        file: mind/core_utils.py
        function: get_templates_path
        trigger: return path or raise
        payload: Path or error
        async_hook: not_applicable
        needs: none
        notes: decision point for templates source
    health_recommended:
      - dock_id: dock_templates_path_return
        reason: incorrect path breaks template-based commands

### Docs Module Discovery: Identify doc modules under docs/

This flow discovers documentation modules for validation and tooling.

```yaml
flow:
  name: docs_module_discovery
  purpose: return module doc directories based on doc prefix files
  scope: filesystem reads only
  steps:
    - id: scan_docs_root
      description: iterate top-level docs entries and filter
      file: mind/core_utils.py
      function: find_module_directories
      input: docs_dir
      output: candidate directories
      trigger: docs scanning command
      side_effects: filesystem iteration
    - id: scan_area_subdirs
      description: check one level deeper for area/module layout
      file: mind/core_utils.py
      function: find_module_directories
      input: subdirectories
      output: module directories
      trigger: when top-level is not a module
      side_effects: filesystem iteration
  docking_points:
    guidance:
      include_when: output list changes or concepts directory is incorrectly included
      omit_when: single directory iteration
      selection_notes: focus on final module list output
    available:
      - id: dock_module_list_return
        type: file
        direction: output
        file: mind/core_utils.py
        function: find_module_directories
        trigger: return list
        payload: List[Path]
        async_hook: not_applicable
        needs: none
        notes: ensures doc prefix filtering is correct
    health_recommended:
      - dock_id: dock_module_list_return
        reason: incorrect discovery impacts validation and tooling
```

---

## MODULE DEPENDENCIES

### Internal Dependencies

None. This module is intended to be dependency-light.

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `pathlib` | filesystem paths and checks | `runtime/core_utils.py` |
| `typing` | type hints | `runtime/core_utils.py` |
| `yaml` (optional) | YAML detection via import | `runtime/core_utils.py` |

---

## STATE MANAGEMENT

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| `HAS_YAML` | `runtime/core_utils.py:10` | module | set at import time |
| `IGNORED_EXTENSIONS` | `runtime/core_utils.py:17` | module | constant at import time |

---

## RUNTIME BEHAVIOR

### Initialization

```
1. Import standard library modules.
2. Attempt to import yaml and set HAS_YAML.
3. Define constants and functions.
```

### Main Loop / Request Cycle

```
1. Call utility function from caller.
2. Perform filesystem checks.
3. Return path or list.
```

### Shutdown

```
No shutdown behavior; stateless helpers only.
```

---

## CONCURRENCY MODEL

Synchronous, single-threaded filesystem access.

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| templates directory | filesystem | n/a | discovered via get_templates_path |

---

## BIDIRECTIONAL LINKS

### Code → Docs

Files that reference this documentation:

| File | Line | Reference |
|------|------|-----------|
| `runtime/core_utils.py` | 4 | `docs/core_utils/PATTERNS_Core_Utils_Functions.md` |

### Docs → Code

| Doc Section | Implemented In |
|-------------|----------------|
| ALGORITHM get_templates_path | `runtime/core_utils.py:get_templates_path` |
| ALGORITHM find_module_directories | `runtime/core_utils.py:find_module_directories` |
| BEHAVIOR B1 | `runtime/core_utils.py:get_templates_path` |
| BEHAVIOR B3 | `runtime/core_utils.py:find_module_directories` |

---

## MARKERS

### Extraction Candidates

None. File size is well under WATCH threshold.

### Missing Implementation

<!-- @mind:todo None noted. -->

### Ideas

<!-- @mind:proposition Add optional sorting flag for deterministic module discovery ordering. -->

### Questions

<!-- @mind:escalation Should module discovery include HEALTH docs in the prefix list? -->
