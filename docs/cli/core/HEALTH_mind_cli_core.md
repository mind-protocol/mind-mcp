# mind_cli_core — Health: Verification Mechanics and Coverage

```
STATUS: CANONICAL
CREATED: 2025-12-24
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
THIS:            HEALTH_mind_cli_core.md
SYNC:            ./SYNC_mind_cli_core.md

---

## HEALTH INDICATORS SELECTED

| Objective | Indicators | Why These Signals Matter |
|-----------|------------|--------------------------|
| O1: Initialization | h_cli_init_success | Ensures new projects can be initialized |
| O2: Health Monitoring | h_cli_status_accuracy | Verifies status correctly reports state |
| O3: Maintenance | h_cli_embedding_fix | Confirms embedding repair works |
| All | h_cli_command_success | General command execution health |

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  result:
    representation: enum
    value: OK
    updated_at: 2025-12-29T00:00:00Z
    source: manual_verification
```

---

## CHECKER INDEX

```yaml
checkers:
  - name: cli_smoke_test
    purpose: Verifies that 'mind --help' and all commands execute without crash
    status: active
    priority: high
    commands:
      - mind --help
      - mind init --help
      - mind status --help
      - mind upgrade --help
      - mind fix-embeddings --help

  - name: cli_init_test
    purpose: Verifies init creates correct directory structure
    status: active
    priority: high

  - name: cli_status_test
    purpose: Verifies status reports correct project state
    status: active
    priority: high

  - name: cli_embedding_test
    purpose: Verifies fix-embeddings detects and repairs issues
    status: active
    priority: medium
```

---

## INDICATOR: h_cli_command_success

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: h_cli_command_success
  client_value: Users can rely on the CLI to perform requested actions reliably.
  validation:
    - validation_id: V-CLI-VALID-COMMANDS
      criteria: All commands and subcommands map to existing handler modules.
    - validation_id: V-CLI-EXIT-CODES
      criteria: Commands return appropriate exit codes.
```

### HEALTH REPRESENTATION

```yaml
representation:
  allowed: [enum, float_0_1]
  selected: [enum]
  semantics:
    enum:
      OK: All implemented commands execute successfully.
      WARN: Some commands have issues but core functionality works.
      ERROR: Critical commands (init, status) failing.
  aggregation:
    method: minimum_score
    display: enum
```

### ALGORITHM / CHECK MECHANISM

```yaml
mechanism:
  summary: Execute basic CLI commands and verify exit codes and output.
  steps:
    - Run 'mind --help'
    - Run 'mind init --help'
    - Run 'mind status --help'
    - Verify exit_code == 0 for all
  data_required: CLI execution environment
  failure_mode: Commands crash or return non-zero exit codes for basic requests.
```

---

## INDICATOR: h_cli_init_success

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: h_cli_init_success
  client_value: New projects can be initialized with Mind Protocol.
  validation:
    - validation_id: V-CLI-DATABASE-SELECTION
      criteria: Database backend selection works correctly.
    - validation_id: V-CLI-INIT-IDEMPOTENCE
      criteria: Reinitializing doesn't corrupt state.
```

### ALGORITHM / CHECK MECHANISM

```yaml
mechanism:
  summary: Initialize a test project and verify .mind/ structure.
  steps:
    - Create temp directory
    - Run 'mind init --database falkordb'
    - Verify .mind/ exists
    - Verify database.yaml contains 'backend: falkordb'
    - Verify mcp-config.json exists
    - Clean up temp directory
  data_required: Writable temp directory, network access for database
  failure_mode: Init fails to create required files or crashes.
```

---

## INDICATOR: h_cli_status_accuracy

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: h_cli_status_accuracy
  client_value: Status command correctly reflects project health.
  validation:
    - validation_id: V-CLI-DIR-RESOLUTION
      criteria: Working directory is resolved correctly.
```

### ALGORITHM / CHECK MECHANISM

```yaml
mechanism:
  summary: Run status on initialized and uninitialized directories.
  steps:
    - Run 'mind status' on initialized project
    - Verify output shows version, database, health metrics
    - Verify exit code is 0
    - Run 'mind status' on empty directory
    - Verify output indicates 'Not a mind project'
    - Verify exit code is non-zero
  data_required: Initialized mind project, empty test directory
  failure_mode: Status reports incorrect state or wrong exit code.
```

---

## INDICATOR: h_cli_embedding_fix

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: h_cli_embedding_fix
  client_value: Embedding issues can be detected and repaired.
  validation:
    - validation_id: V-CLI-EMBEDDING-VALIDATION
      criteria: Embedding config validation detects mismatches.
```

### ALGORITHM / CHECK MECHANISM

```yaml
mechanism:
  summary: Verify fix-embeddings detects and repairs embedding issues.
  steps:
    - Run 'mind fix-embeddings --dry-run' on healthy project
    - Verify no fixes needed
    - Introduce embedding mismatch (if testable)
    - Run 'mind fix-embeddings --dry-run'
    - Verify issues detected
    - Run 'mind fix-embeddings'
    - Verify issues resolved
  data_required: Initialized project with graph data
  failure_mode: Embedding issues not detected or not repaired.
```

---

## HOW TO RUN

```bash
# Smoke test - verify help works
mind --help
mind init --help
mind status --help
mind upgrade --help
mind fix-embeddings --help

# Manual integration test
mkdir /tmp/test-mind
cd /tmp/test-mind
mind init --database falkordb
mind status
mind fix-embeddings --dry-run
cd -
rm -rf /tmp/test-mind

# Run any pytest tests if available
pytest tests/cli/ -v
```

---

## FUTURE HEALTH CHECKS (PROPOSED)

When future commands are implemented, add these checks:

```yaml
future_checkers:
  - name: cli_validate_test
    purpose: Verifies validate command checks all invariants
    status: proposed

  - name: cli_context_test
    purpose: Verifies context command returns relevant graph data
    status: proposed

  - name: cli_human_review_test
    purpose: Verifies human-review finds and presents markers
    status: proposed
```
