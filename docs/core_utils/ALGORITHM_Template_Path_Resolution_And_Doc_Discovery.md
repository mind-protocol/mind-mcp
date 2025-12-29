# Core Utils — Algorithm: Template Path Resolution and Doc Discovery

```
STATUS: STABLE
CREATED: 2025-12-20
VERIFIED: 2025-12-20 against working tree
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Core_Utils_Functions.md
BEHAVIORS:       ./BEHAVIORS_Core_Utils_Helper_Effects.md
THIS:            ALGORITHM_Template_Path_Resolution_And_Doc_Discovery.md (you are here)
VALIDATION:      ./VALIDATION_Core_Utils_Invariants.md
HEALTH:          ./HEALTH_Core_Utils_Verification.md
SYNC:            ./SYNC_Core_Utils_State.md

IMPL:            mind/core_utils.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

This module provides two filesystem-oriented helpers: one locates the templates directory for installed or repo-based usage, and the other scans docs/ to discover module documentation folders. Both functions are simple linear scans designed to be predictable and dependency-light.

---

## DATA STRUCTURES

### `IGNORED_EXTENSIONS`

A module-level set of extensions that other modules may reference when filtering files. It is not mutated at runtime.

### `doc_prefixes`

```
['PATTERNS_', 'BEHAVIORS_', 'ALGORITHM_', 'VALIDATION_', 'TEST_', 'SYNC_']
```

Used to identify whether a directory contains module documentation files.

---

## ALGORITHM: `get_templates_path()`

### Step 1: Check package templates

- Build `package_templates = Path(__file__).parent / "templates"`.
- If it exists and contains `runtime/`, return it.

### Step 2: Check repo-root templates

- Compute `repo_root = Path(__file__).parent.parent`.
- Build `repo_templates = repo_root / "templates"`.
- If it exists and contains `runtime/`, return it.

### Step 3: Fail with context

- Raise `FileNotFoundError` listing both checked paths and hints.

---

## ALGORITHM: `find_module_directories(docs_dir)`

### Step 1: Iterate top-level docs entries

- Skip non-directories and the `concepts` directory.

### Step 2: Detect module directories

- If a directory has any markdown file whose name includes a doc prefix, treat it as a module directory.

### Step 3: Detect area/module directories

- If the top-level directory is not itself a module, iterate one level deeper.
- For each subdirectory, check for prefixed markdown files and add it if found.

### Step 4: Return collected list

- Return the list of module directories in discovery order.

---

## KEY DECISIONS

### D1: Prefer package templates over repo templates

```
IF package templates exist and include mind:
    return package templates
ELSE:
    check repo templates
```

Rationale: the installed package should be self-contained, with repo lookup only for development.

### D2: Identify modules by doc prefixes instead of fixed folder list

```
IF any filename contains a doc prefix:
    directory is treated as a module
ELSE:
    inspect one level deeper
```

Rationale: keeps discovery flexible and avoids hard-coding module names.

---

## DATA FLOW

```
filesystem
    ↓
path existence checks (templates)
    ↓
validated Path return or FileNotFoundError
```

```
docs_dir entries
    ↓
filter directories + doc prefixes
    ↓
list[Path] of module directories
```

---

## COMPLEXITY

**Time:** O(n + m) — n entries at docs root, m entries across one subdirectory level.

**Space:** O(k) — k module directories discovered.

**Bottlenecks:**
- Large docs trees increase filesystem traversal time.
- Using glob per directory scales linearly with file count.

---

## HELPER FUNCTIONS

None. Both functions implement their own logic directly.

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| pathlib.Path | `iterdir`, `glob`, `exists` | filesystem traversal and checks |

---

## MARKERS

<!-- @mind:todo Should discovery order be stable-sorted by name instead of filesystem order? -->
