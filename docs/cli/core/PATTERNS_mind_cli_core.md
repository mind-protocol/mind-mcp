# mind_cli_core — PATTERNS: Design and Implementation Conventions

```
STATUS: CANONICAL
CREATED: 2023-11-20
UPDATED: 2025-12-29
```

---

## CHAIN

OBJECTIVES:      ./OBJECTIVES_mind_cli_core.md
BEHAVIORS:       ./BEHAVIORS_mind_cli_core.md
PATTERNS:        ./PATTERNS_mind_cli_core.md
ALGORITHM:       ./ALGORITHM_mind_cli_core.md
VALIDATION:      ./VALIDATION_mind_cli_core.md
IMPLEMENTATION:  ./IMPLEMENTATION_mind_cli_core.md
HEALTH:          ./HEALTH_mind_cli_core.md
SYNC:            ./SYNC_mind_cli_core.md
THIS:            PATTERNS_mind_cli_core.md

IMPL:            cli/__main__.py

---

## PATTERNS

This module adheres to the following design and implementation patterns:

### 1. Command-Line Interface (CLI) Structure

* **Argparse Framework:** All CLI commands are built using Python's standard `argparse` library for robust command definitions, argument parsing, and help generation.
* **Subcommand Pattern:** Each command is registered as a subparser (e.g., `mind init`, `mind status`) for clarity and modularity.
* **Explicit Dispatch:** The main entry point uses explicit if/elif dispatch to route commands to their handlers.

### 2. Directory Structure

```
cli/
├── __init__.py              # Package marker
├── __main__.py              # Main entry point (argparse setup, dispatch)
├── config.py                # Configuration constants
├── commands/
│   ├── __init__.py
│   ├── init.py              # mind init command
│   ├── status.py            # mind status command
│   ├── upgrade.py           # mind upgrade command
│   └── fix_embeddings.py    # mind fix-embeddings command
└── helpers/
    ├── __init__.py
    └── *.py                 # Reusable helper functions
```

### 3. Modular Command Design

* **One Command Per Module:** Each CLI command lives in its own module under `cli/commands/`.
* **Standard Interface:** Each command module exposes a `run(dir, **kwargs)` function that returns success status.
* **Helper Functions:** Common utilities are encapsulated in `cli/helpers/` with descriptive filenames following naming engineering principles.

### 4. Command Module Pattern

Each command module follows this pattern:

```python
# cli/commands/{command}.py

def run(directory: Path, **kwargs) -> bool:
    """
    Execute the command.

    Args:
        directory: Working directory
        **kwargs: Command-specific arguments

    Returns:
        True on success, False on failure
    """
    # Implementation
    return True
```

### 5. Helper Function Naming

Helper filenames are descriptive and action-oriented:
- `get_paths_for_templates_and_runtime.py`
- `check_mind_status_in_directory.py`
- `fix_embeddings_for_nodes_and_links.py`
- `validate_embedding_config_matches_stored.py`

This follows the naming engineering principle: 25-75 characters, explicit responsibility.

### 6. Exit Code Convention

* **0:** Success
* **1:** Failure (validation error, missing requirements, operation failed)
* All commands set exit codes explicitly via `sys.exit()` in `__main__.py`.

### 7. Doc-Code Alignment

* **`DOCS:` References:** Source files include `DOCS:` comments pointing to their primary documentation files.
* **`CHAIN` Sections:** Documentation files include `CHAIN` sections linking to related code and other documentation.

### 8. Error Handling

* **Graceful Degradation:** Commands aim to fail gracefully, providing informative error messages and suggestions for recovery.
* **Exit on Error:** Commands return False or raise exceptions that result in non-zero exit codes.
* **Verbose Output:** Commands print status messages to help users understand what is happening.

### 9. CLI vs MCP Separation

Features are grouped by use-case context, not technical category:

| Use Case | Interface | Rationale |
|----------|-----------|-----------|
| **CI enforcement** | CLI (`mind validate`) | Needs exit codes, fast, no interaction |
| **Developer quick check** | CLI (`mind status`) | Human-readable, terminal-friendly |
| **Agent work context** | MCP (`doctor_check`) | Graph mutations, structured data for agents |
| **Human decisions** | CLI (`mind human-review`) | Interactive, marker resolution |
| **State maintenance** | CLI (`mind sync-files`) | File operations, archiving |

**Principle:** CLI for humans and CI. MCP for agents. Graph mutations happen via MCP tools, not CLI.

### 10. Health Check Groupings

The 40+ health checks are grouped by what they validate:

| Category | Checks | Purpose |
|----------|--------|---------|
| **File Quality** | monolith, long_strings, magic_values, secrets | Code hygiene |
| **Doc Structure** | incomplete_chain, orphan_docs, no_docs_ref | Doc-code alignment |
| **Doc Content** | doc_duplication, template_drift, link_integrity | Doc quality |
| **Implementation** | stub_impl, stale_impl, broken_impl_links | Code state |
| **SYNC State** | stale_sync, conflicts, doc_gaps | State freshness |
| **Markers** | special_markers, legacy_markers | Human-AI handoff |
| **Prompt** | prompt_doc_reference, prompt_checklist | AI prompt quality |

All checks run via `mind validate`. MCP `doctor_check` also runs checks but focuses on issue/task creation for agents.

---

## ANTI-PATTERNS TO AVOID

* **Tight Coupling:** Avoid direct, rigid dependencies between unrelated modules; favor loose coupling through explicit dependency passing.
* **Magic Strings/Numbers:** Use constants or enums instead of hardcoded string or numeric literals for configuration and identifiers.
* **Excessive Global State:** Minimize reliance on global variables; prefer passing state explicitly.
* **Undocumented Features:** All public CLI commands and core functionalities must be documented.
* **Click Framework:** Do NOT use Click. The project uses argparse for consistency and stdlib dependency minimization.
* **Monolithic Commands:** Do NOT put all command logic in `__main__.py`. Each command should have its own module.
