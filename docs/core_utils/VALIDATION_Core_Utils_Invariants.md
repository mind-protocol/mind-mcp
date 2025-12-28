# Core Utils — Validation: Core Utility Invariants

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
ALGORITHM:       ./ALGORITHM_Template_Path_Resolution_And_Doc_Discovery.md
THIS:            VALIDATION_Core_Utils_Invariants.md (you are here)
IMPLEMENTATION:  ./IMPLEMENTATION_Core_Utils_Code_Architecture.md
HEALTH:          ./HEALTH_Core_Utils_Verification.md
SYNC:            ./SYNC_Core_Utils_State.md

IMPL:            mind/core_utils.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## INVARIANTS

These must ALWAYS be true:

### V1: Template path includes the mind subtree

```
get_templates_path() must only return a templates directory that contains templates/mind.
```

**Checked by:** manual verification of `get_templates_path` in `mind/core_utils.py`

### V2: docs/concepts is excluded from module discovery

```
find_module_directories() must never return the docs/concepts directory.
```

**Checked by:** manual review of `find_module_directories` filtering logic

### V3: Only directories with doc-prefix markdown files are returned

```
find_module_directories() must only return directories that contain at least one doc-prefix markdown file.
```

**Checked by:** manual review of doc-prefix detection logic

---

## PROPERTIES

For property-based testing:

### P1: Template resolution is deterministic

```
FORALL filesystem states:
    get_templates_path() returns the first valid candidate in the defined priority order.
```

**Verified by:** NOT YET VERIFIED — no property tests exist

---

## ERROR CONDITIONS

### E1: Templates not found

```
WHEN:    neither package nor repo templates exist
THEN:    FileNotFoundError is raised and includes both checked paths
SYMPTOM: CLI actions that depend on templates fail early with a clear message
```

**Verified by:** NOT YET VERIFIED — no automated check

### E2: docs_dir is invalid

```
WHEN:    docs_dir does not exist or is not a directory
THEN:    Path.iterdir raises an exception
SYMPTOM: caller receives an exception when scanning docs
```

**Verified by:** NOT YET VERIFIED — no automated check

---

## HEALTH COVERAGE

| Invariant | Signal | Status |
|-----------|--------|--------|
| V1: Template path includes mind | Manual call to get_templates_path | ⚠ NOT YET VERIFIED |
| V2: concepts excluded | Manual review of directory filter | ⚠ NOT YET VERIFIED |
| V3: doc-prefix-only modules | Manual review of doc-prefix filter | ⚠ NOT YET VERIFIED |

---

## VERIFICATION PROCEDURE

### Manual Checklist

```
[ ] V1 holds — call get_templates_path() in a repo checkout
[ ] V2 holds — ensure docs/concepts is explicitly skipped
[ ] V3 holds — verify doc-prefix matching in find_module_directories()
[ ] All behaviors from BEHAVIORS_*.md work
[ ] All edge cases handled
[ ] All anti-behaviors prevented
```

### Automated

```bash
# No tests currently exist for core_utils.
# Add tests under tests/core_utils/ if behaviors become critical.
```

---

## SYNC STATUS

```
LAST_VERIFIED: 2025-12-20
VERIFIED_AGAINST:
    impl: mind/core_utils.py @ working tree
    test: n/a
VERIFIED_BY: manual review
RESULT:
    V1: NOT RUN
    V2: NOT RUN
    V3: NOT RUN
```

---

## MARKERS

<!-- @mind:todo Add tests for template resolution priority and failure message content. -->
<!-- @mind:todo Add tests for module directory discovery (including docs/concepts exclusion). -->
