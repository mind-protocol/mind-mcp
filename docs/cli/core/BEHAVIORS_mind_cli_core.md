# Mind CLI Core — Behaviors: Observable Effects of CLI Commands

```
STATUS: CANONICAL
CREATED: 2023-12-19
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
THIS:            BEHAVIORS_mind_cli_core.md

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS — IMPLEMENTED COMMANDS (CANONICAL)

### B1: mind init

```
GIVEN:  User runs 'mind init' in a directory without .mind/
WHEN:   The command executes successfully
THEN:   A .mind/ directory is created with 13 steps:
        1. Ecosystem templates copied
        2. Runtime package copied
        3. AI config files created (CLAUDE.md, GEMINI.md, AGENTS.md)
        4. Skills synced to AI tool directories
        5. Database config created (falkordb or neo4j)
        6. Database schema applied
        7. Repository files ingested (Spaces and Things created)
        8. Seed data injected (Actors linked to Spaces)
        9. .env.example created
        10. MCP config created
        11. .gitignore updated
        12. Overview generated (map.md files)
        13. Embeddings generated (with progress bar)
AND:    Human actor created from git config (user.name, user.email) if .git exists
AND:    Repo Thing created from git remote with GitHub API metadata if public
AND:    All nodes with synthesis get embeddings
AND:    Exit code is 0
```

```
GIVEN:  User runs 'mind init --database neo4j'
WHEN:   The command executes
THEN:   database.yaml contains 'backend: neo4j'
```

```
GIVEN:  User runs 'mind init' in a directory with existing .mind/
WHEN:   The command executes
THEN:   Existing configuration is preserved or updated
AND:    User is warned about existing installation
```

### B2: mind status

```
GIVEN:  User runs 'mind status' in an initialized project
WHEN:   The command executes
THEN:   Output displays:
        - Mind Protocol version
        - Database backend and connection status
        - Graph health metrics (node/link counts)
        - Embedding configuration status
AND:    Exit code reflects health (0 = healthy, non-zero = issues)
```

```
GIVEN:  User runs 'mind status' in an uninitialized project
WHEN:   The command executes
THEN:   Output indicates 'Not a mind project'
AND:    Exit code is non-zero
```

### B3: mind upgrade

```
GIVEN:  User runs 'mind upgrade'
WHEN:   A newer version of mind-mcp is available
THEN:   Output displays:
        - Current version
        - Available version
        - Upgrade instructions
AND:    Exit code is 0
```

```
GIVEN:  User runs 'mind upgrade'
WHEN:   Already on the latest version
THEN:   Output indicates 'Already up to date'
AND:    Exit code is 0
```

### B4: mind fix-embeddings

```
GIVEN:  User runs 'mind fix-embeddings'
WHEN:   There are nodes/links with missing or mismatched embeddings
THEN:   Embeddings are regenerated for affected entities
AND:    Output shows number of fixed entities
AND:    Exit code is 0
```

```
GIVEN:  User runs 'mind fix-embeddings --dry-run'
WHEN:   There are nodes/links with missing or mismatched embeddings
THEN:   Output shows what WOULD be fixed
AND:    No actual changes are made
AND:    Exit code is 0
```

```
GIVEN:  User runs 'mind fix-embeddings'
WHEN:   All embeddings are valid
THEN:   Output indicates 'No fixes needed'
AND:    Exit code is 0
```

---

## BEHAVIORS — FUTURE COMMANDS (PROPOSED)

### B5: mind validate [PROPOSED]

```
GIVEN:  User runs 'mind validate'
WHEN:   The command executes
THEN:   Protocol invariants are checked:
        - Doc chain completeness
        - SYNC file freshness
        - Code-doc alignment
        - Graph schema compliance
AND:    Exit code is 0 if all pass, non-zero if any fail
AND:    Output is CI-friendly (parseable, clear pass/fail)
```

### B6: mind work [PROPOSED]

```
GIVEN:  User runs 'mind work [path] [objective]'
WHEN:   The command executes
THEN:   AI-assisted repair workflow is initiated
AND:    Agent works on the specified path with graph context
AND:    Changes are tracked in SYNC
```

Note: This command needs redesign. Current implementation scope is TBD.

### B7: mind context [PROPOSED]

```
GIVEN:  User runs 'mind context node_id'
WHEN:   The node exists in the graph
THEN:   Output displays:
        - Node content and metadata
        - Connected nodes (by relationship type)
        - Relevant code references
        - Related documentation
```

```
GIVEN:  User runs 'mind context --question "How does X work?"'
WHEN:   The command executes
THEN:   Graph is queried semantically
AND:    Relevant nodes are returned with context
```

```
GIVEN:  User runs 'mind context --intent "fix bug in Y"'
WHEN:   The command executes
THEN:   Context relevant to the intent is assembled
AND:    Related issues, code, and docs are surfaced
```

```
GIVEN:  User runs 'mind context' with no arguments
WHEN:   The command executes
THEN:   Context is deduced from current working directory/file
AND:    Relevant graph context is displayed
```

### B8: mind sync-files [PROPOSED]

```
GIVEN:  User runs 'mind sync-files'
WHEN:   The command executes
THEN:   SYNC files are scanned and updated:
        - Stale entries are archived
        - Current state is validated
        - Handoffs are surfaced
```

### B9: mind human-review [PROPOSED]

```
GIVEN:  User runs 'mind human-review'
WHEN:   There are unresolved @mind: markers
THEN:   Markers are presented for review:
        - @mind:escalation - decisions needed
        - @mind:proposition - ideas to accept/reject
        - @mind:todo - tasks to assign/complete
AND:    User can interactively resolve each marker
```

### B10: mind talk [PROPOSED]

```
GIVEN:  User runs 'mind talk'
WHEN:   The command executes
THEN:   An interactive session with an agent is started
AND:    Agent has full graph context
AND:    Conversation is recorded in the graph
```

```
GIVEN:  Agent runs 'mind talk' from another agent context
WHEN:   The command executes
THEN:   Agent-to-agent communication is facilitated
AND:    Conversation is recorded in the graph
```

---

## GENERIC BEHAVIORS

### B11: Display Help Information

```
GIVEN:  User runs 'mind --help' or 'mind <command> --help'
WHEN:   The help command is executed
THEN:   Usage instructions and available commands/arguments are displayed
AND:    Exit code is 0
```

### B12: Handle Invalid Command

```
GIVEN:  User runs 'mind invalid-command'
WHEN:   The command is not recognized
THEN:   Error message is displayed
AND:    Help is shown
AND:    Exit code is 1
```

---

## OBJECTIVES SERVED

| Behavior ID | Objective | Why It Matters |
|-------------|-----------|----------------|
| B1 | O1: Project Initialization | Enables new projects to use Mind Protocol |
| B2 | O2: Health Monitoring | Gives visibility into project state |
| B3, B4 | O3: Protocol Maintenance | Keeps projects up-to-date and healthy |
| B5 | O4: Protocol Enforcement | Enables CI integration |
| B6, B7, B10 | O5: AI-Assisted Workflows | Powers AI agent capabilities |
| B9 | O6: Human-AI Collaboration | Bridges human and AI decision-making |
| B8 | O7: State Synchronization | Maintains consistent state tracking |

---

## INPUTS / OUTPUTS

### Primary Function: `mind` CLI

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `command` | `str` | The subcommand to execute (init, status, upgrade, fix-embeddings) |
| `--dir` | `Path` | Working directory (default: cwd) |
| `--database` | `str` | Database backend for init (falkordb or neo4j) |
| `--dry-run` | `bool` | Preview mode for fix-embeddings |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| `stdout` | `str` | Textual output from command execution |
| `stderr` | `str` | Error messages or warnings |
| `exit_code` | `int` | 0 for success, non-zero for failure |

**Side Effects:**

- Creation/modification of .mind/ directory and contents
- Database schema changes and data mutations
- Graph node/link creation and updates
- Embedding generation and storage

---

## EDGE CASES

### E1: Invalid Command

```
GIVEN:  A non-existent CLI command is provided
THEN:   An error message is displayed with help text
AND:    Exit code is 1
```

### E2: Database Connection Failure

```
GIVEN:  Database is not reachable during init or status
THEN:   Error message indicates connection issue
AND:    Suggestions for resolution are provided
AND:    Exit code is non-zero
```

### E3: Embedding Model Mismatch

```
GIVEN:  Stored embeddings were created with different model/dimensions
WHEN:   fix-embeddings is run
THEN:   Mismatched embeddings are detected and flagged for regeneration
```

---

## ANTI-BEHAVIORS

What should NOT happen:

### A1: Silent Failure

```
GIVEN:  A critical operation fails (e.g., database write error)
WHEN:   The command is executed
MUST NOT: The program exits silently or indicates success
INSTEAD:  An informative error message is displayed, and exit code is non-zero
```

### A2: Partial State Changes

```
GIVEN:  A multi-step operation fails partway through
WHEN:   The command is executed
MUST NOT: Leave the system in an inconsistent state
INSTEAD:  Either complete fully or roll back changes
```

### A3: Swallowed Exceptions

```
GIVEN:  An unexpected exception occurs
WHEN:   The command is executed
MUST NOT: Catch and ignore the exception
INSTEAD:  Log the error, provide context, and exit with non-zero code
```
