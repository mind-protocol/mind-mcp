# PATTERNS: Core Utility Functions

```
STATUS: CANONICAL
CREATED: 2025-12-20
```

---

## CHAIN

```
THIS:            PATTERNS_Core_Utils_Functions.md
BEHAVIORS:       ./BEHAVIORS_Core_Utils_Helper_Effects.md
ALGORITHM:       ./ALGORITHM_Template_Path_Resolution_And_Doc_Discovery.md
VALIDATION:      ./VALIDATION_Core_Utils_Invariants.md
IMPLEMENTATION:  ./IMPLEMENTATION_Core_Utils_Code_Architecture.md
HEALTH:          ./HEALTH_Core_Utils_Verification.md
SYNC:            ./SYNC_Core_Utils_State.md
```

---

## WHY THIS SHAPE

This module exists to house common, reusable utility functions that are not specific to any particular domain or subsystem within the `mind` framework. The goal is to avoid duplication of basic functionalities across different modules.

---

## SCOPE

**In scope:**
- Generic helper functions (e.g., path manipulation, string processing).
- Constants used across multiple modules.

**Out of scope:**
- Domain-specific utilities (e.g., `doctor_files` for doctor-related file operations).
- Complex algorithms or business logic.

---

## PRINCIPLES

- **Reusability:** Functions should be generic enough to be used in various contexts.
- **Simplicity:** Functions should be small, focused, and easy to understand.
- **No external dependencies:** Core utilities should have minimal or no external library dependencies to keep the module lightweight.

---

## DATA

This module primarily operates on basic Python data types (strings, paths, lists) and does not manage complex data structures itself.

---

## DEPENDENCIES

This module has no internal `mind` dependencies, but may rely on standard Python library modules.

---

## INSPIRATIONS

Standard Python `os.path` and `shutil` modules.

---

## IMPLEMENTATION REFERENCES

| File | Role |
|------|------|
| `mind/core_utils.py` | Canonical location for utility helpers; used by CLI commands, health checks, and other modules for path resolution, doc discovery, and file operations. |

```
IMPL: mind/core_utils.py
```

---

## MARKERS

<!-- @mind:proposition Formalize a process for adding new utility functions to ensure they meet the reusability and simplicity criteria. -->
