# Core Utils — Behaviors: Template Path Resolution and Docs Discovery

```
STATUS: STABLE
CREATED: 2025-12-20
VERIFIED: 2025-12-20 against working tree
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Core_Utils_Functions.md
THIS:            BEHAVIORS_Core_Utils_Helper_Effects.md (you are here)
ALGORITHM:       ./ALGORITHM_Template_Path_Resolution_And_Doc_Discovery.md
VALIDATION:      ./VALIDATION_Core_Utils_Invariants.md
IMPLEMENTATION:  ./IMPLEMENTATION_Core_Utils_Code_Architecture.md
HEALTH:          ./HEALTH_Core_Utils_Verification.md
SYNC:            ./SYNC_Core_Utils_State.md

IMPL:            mind/core_utils.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS

### B1: Prefer package-local templates

```
GIVEN:  templates exist inside the installed package and include the mind subtree
WHEN:   get_templates_path() is called
THEN:   the package templates path is returned
```

### B2: Fall back to repo root templates

```
GIVEN:  package templates do not exist, but repo-root templates include the mind subtree
WHEN:   get_templates_path() is called
THEN:   the repo templates path is returned
```

### B3: Report missing templates clearly

```
GIVEN:  neither package nor repo templates exist
WHEN:   get_templates_path() is called
THEN:   FileNotFoundError is raised with both checked paths in the message
```

### B4: Identify documentation module directories

```
GIVEN:  a docs directory with module folders and/or area/module subfolders
WHEN:   find_module_directories(docs_dir) is called
THEN:   only directories containing doc-prefix markdown files are returned
AND:    the docs/concepts directory is ignored
```

---

## INPUTS / OUTPUTS

### Primary Function: `get_templates_path()`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| none | n/a | function reads the filesystem only |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| templates_path | Path | directory that contains templates/mind |

**Side Effects:**

- reads filesystem paths to check for existence

### Primary Function: `find_module_directories()`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| docs_dir | Path | root of docs tree to scan |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| modules | List[Path] | directories that contain doc-prefix markdown files |

**Side Effects:**

- iterates directories and glob-matches markdown files

---

## EDGE CASES

### E1: Invalid docs directory

```
GIVEN:  docs_dir is missing or not a directory
THEN:   the underlying Path.iterdir() error propagates
```

### E2: Empty directories

```
GIVEN:  a directory has no markdown files with doc prefixes
THEN:   it is not returned as a module directory
```

---

## ANTI-BEHAVIORS

What should NOT happen:

### A1: Treat non-doc directories as modules

```
GIVEN:   a directory with no PATTERNS/BEHAVIORS/ALGORITHM/VALIDATION/TEST/SYNC files
WHEN:    find_module_directories() scans the docs tree
MUST NOT: include that directory in results
INSTEAD:  ignore it and continue scanning
```

### A2: Return templates path that lacks the mind subtree

```
GIVEN:   a templates directory exists but is missing the mind subfolder
WHEN:    get_templates_path() is called
MUST NOT: return the incomplete templates path
INSTEAD:  check the next candidate or raise FileNotFoundError
```

---

## MARKERS

<!-- @mind:todo Should find_module_directories() return a stable sorted list to reduce diff noise? -->
