# mind_cli_core — OBJECTIVES: Core CLI Functionality and Design Goals

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
THIS:            OBJECTIVES_mind_cli_core.md

IMPL:            cli/__main__.py

---

## OBJECTIVE

The `mind_cli_core` module provides the command-line interface for the Mind Protocol. It enables project initialization, health monitoring, maintenance operations, and (in future) AI-assisted workflows.

---

## PRIMARY OBJECTIVES

### O1: Project Initialization and Setup
Enable seamless initialization of Mind Protocol in any project with database selection, graph sync, and configuration.
**Status:** CANONICAL (implemented via `mind init`)
**Features:** Database setup, file→node graph sync, embeddings, overview generation

### O2: Project Health Monitoring
Provide visibility into project state, including protocol version, database connectivity, and quick health summary.
**Status:** CANONICAL (implemented via `mind status`)
**Features:** Version info, database connectivity, SYNC file status

### O3: Protocol Maintenance
Support upgrade workflows and data integrity operations like embedding repair.
**Status:** CANONICAL (implemented via `mind upgrade`, `mind fix-embeddings`)

### O4: Protocol Enforcement (CI-focused)
Validate that projects adhere to Mind Protocol invariants, suitable for CI integration.
**Status:** PROPOSED (future `mind validate`)
**Features:** 40+ health checks, health score (0-100), exit codes, text/json output
**Use case:** CI/CD pipelines, pre-commit hooks, automated enforcement

### O5: AI-Assisted Workflows
Enable AI agents to work on code with graph-aware context.
**Status:** PROPOSED (future `mind work`, `mind context`, `mind talk`)
**Note:** Issue/Task creation handled by MCP `doctor_check` tool, not CLI

### O6: Human-AI Collaboration
Facilitate human review of AI-generated markers and decisions.
**Status:** PROPOSED (future `mind human-review`)
**Features:** Scan @mind:escalation, @mind:proposition, @mind:todo markers, interactive resolution

### O7: State Synchronization
Manage SYNC files programmatically for consistent state tracking.
**Status:** PROPOSED (future `mind sync-files`)
**Features:** Auto-archive large SYNCs (>200 lines), SYNC status display

### O8: External Integrations
Connect Mind Protocol state to external services.
**Status:** PROPOSED (future `mind github` or `--github` flag)
**Features:** Create GitHub issues from validation findings

---

## COMMAND INVENTORY

### Implemented Commands (CANONICAL)

| Command | Purpose | Status |
|---------|---------|--------|
| `mind init [--database falkordb\|neo4j]` | Initialize .mind/ directory | CANONICAL |
| `mind status` | Show mind protocol status | CANONICAL |
| `mind upgrade` | Check for protocol upgrades | CANONICAL |
| `mind fix-embeddings [--dry-run]` | Fix missing/mismatched embeddings | CANONICAL |

### Future Commands (PROPOSED)

| Command | Purpose | Status |
|---------|---------|--------|
| `mind validate` | Protocol enforcement, CI integration | PROPOSED |
| `mind work` | AI-assisted repair (needs redesign) | PROPOSED |
| `mind context [node_id] [--question "..."] [--intent "..."]` | Node context for actors, graph-aware | PROPOSED |
| `mind sync-files` | SYNC file management | PROPOSED |
| `mind human-review` | Marker resolution (@mind:escalation, @mind:proposition, @mind:todo) | PROPOSED |
| `mind talk` | Talk with an agent (agents can use too) | PROPOSED |

---

## CONSTRAINTS

* **Performance:** CLI commands should execute efficiently without undue latency.
* **Extensibility:** The core should be designed to easily integrate new commands via the `cli/commands/` module pattern.
* **Robustness:** Commands must handle unexpected inputs and system states gracefully, providing clear error messages.
* **Consistency:** Maintain a consistent user experience and internal API across all CLI commands.
* **Modularity:** Each command lives in its own module under `cli/commands/` with helper functions in `cli/helpers/`.

---

## MEASUREMENT

* **Test Coverage:** High unit and integration test coverage for core utilities and command logic.
* **Reliability:** Low incidence of CLI crashes or incorrect behavior reported during operation.
* **Usability:** Positive feedback from users regarding command clarity and effectiveness.
* **Command Success Rate:** All implemented commands exit with code 0 on success, non-zero on failure.
