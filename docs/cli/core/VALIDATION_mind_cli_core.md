# mind_cli_core — Validation: Invariants and Verification

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
THIS:            VALIDATION_mind_cli_core.md
IMPLEMENTATION:  ./IMPLEMENTATION_mind_cli_core.md
HEALTH:          ./HEALTH_mind_cli_core.md
SYNC:            ./SYNC_mind_cli_core.md

---

## INVARIANTS

### V-CLI-VALID-COMMANDS

**Command dispatching maps only to existing handler functions.**

```yaml
invariant: V-CLI-VALID-COMMANDS
priority: HIGH
criteria: |
  All commands and subcommands defined in __main__.py must have a corresponding
  handler module in cli/commands/.
verified_by:
  - test: manual - verify cli/commands/ contains all command modules
  - runtime: argparse raises error for undefined subcommands
confidence: high
evidence:
  - CLI execution fails with 'invalid choice' for undefined commands
  - Each command module must export a run() function
failure_mode: |
  User attempts to run a documented command and it fails to execute or crashes.
```

### V-CLI-EXIT-CODES

**Commands return appropriate exit codes.**

```yaml
invariant: V-CLI-EXIT-CODES
priority: HIGH
criteria: |
  - Exit code 0 means success
  - Exit code 1 means failure
  - Commands must explicitly call sys.exit() with appropriate code
verified_by:
  - manual: inspect __main__.py dispatch logic
  - test: integration tests check exit codes
confidence: high
evidence:
  - All dispatch branches end with sys.exit()
failure_mode: |
  CI pipelines cannot detect command failures; scripts cannot chain commands reliably.
```

### V-CLI-DIR-RESOLUTION

**Working directory is resolved correctly.**

```yaml
invariant: V-CLI-DIR-RESOLUTION
priority: MEDIUM
criteria: |
  - --dir/-d flag allows specifying working directory
  - Default is current working directory (Path.cwd())
  - Directory is passed to all command handlers
verified_by:
  - code inspection of __main__.py
confidence: high
evidence:
  - All commands accept --dir argument
  - Path.cwd() is used as default
failure_mode: |
  Commands operate on wrong directory; data corruption in wrong project.
```

### V-CLI-DATABASE-SELECTION

**Database backend selection works correctly for init.**

```yaml
invariant: V-CLI-DATABASE-SELECTION
priority: HIGH
criteria: |
  - --database/-db accepts only 'falkordb' or 'neo4j'
  - Default is 'falkordb'
  - Selection is persisted to .mind/database.yaml
verified_by:
  - argparse choices constraint
  - manual: verify database.yaml after init
confidence: high
evidence:
  - choices=["falkordb", "neo4j"] in argparse config
failure_mode: |
  Invalid database backend causes runtime errors; wrong backend configured.
```

### V-CLI-EMBEDDING-VALIDATION

**Embedding config validation detects mismatches.**

```yaml
invariant: V-CLI-EMBEDDING-VALIDATION
priority: HIGH
criteria: |
  - fix-embeddings detects when stored embedding config differs from current
  - Mismatched embeddings are flagged for regeneration
  - Model and dimension changes are detected
verified_by:
  - helper: validate_embedding_config_matches_stored.py
confidence: high
evidence:
  - Embedding dimension mismatch causes fix-embeddings to report issues
failure_mode: |
  Semantic search returns wrong results due to inconsistent embeddings.
```

### V-CLI-INIT-IDEMPOTENCE

**Init command handles existing .mind/ directory gracefully.**

```yaml
invariant: V-CLI-INIT-IDEMPOTENCE
priority: MEDIUM
criteria: |
  - Running init on already-initialized project doesn't corrupt state
  - User is warned about existing installation
  - Configuration can be updated without data loss
verified_by:
  - manual testing
confidence: medium
evidence:
  - Init checks for existing .mind/ before proceeding
failure_mode: |
  Running init twice corrupts project state or loses configuration.
```

---

## VALIDATION ID INDEX

| ID | Category | Priority | Confidence |
|----|----------|----------|------------|
| V-CLI-VALID-COMMANDS | Integrity | HIGH | high |
| V-CLI-EXIT-CODES | Contract | HIGH | high |
| V-CLI-DIR-RESOLUTION | Configuration | MEDIUM | high |
| V-CLI-DATABASE-SELECTION | Configuration | HIGH | high |
| V-CLI-EMBEDDING-VALIDATION | Data Integrity | HIGH | high |
| V-CLI-INIT-IDEMPOTENCE | Safety | MEDIUM | medium |

---

## FUTURE INVARIANTS (PROPOSED)

These invariants will apply when future commands are implemented:

### V-CLI-VALIDATE-COVERAGE [PROPOSED]

**Validate command checks all protocol invariants.**

```yaml
invariant: V-CLI-VALIDATE-COVERAGE
priority: HIGH
criteria: |
  - mind validate checks doc chain completeness
  - mind validate checks SYNC file freshness
  - mind validate checks code-doc alignment
  - mind validate checks graph schema compliance
  - Exit code is non-zero if any check fails
status: PROPOSED
```

### V-CLI-CONTEXT-DEDUCTION [PROPOSED]

**Context command can deduce context from working directory.**

```yaml
invariant: V-CLI-CONTEXT-DEDUCTION
priority: MEDIUM
criteria: |
  - Running 'mind context' with no args deduces from cwd
  - Node ID, question, and intent flags work correctly
  - Graph queries return relevant context
status: PROPOSED
```

### V-CLI-MARKER-RESOLUTION [PROPOSED]

**Human-review command finds and presents all markers.**

```yaml
invariant: V-CLI-MARKER-RESOLUTION
priority: MEDIUM
criteria: |
  - @mind:escalation markers are found and presented
  - @mind:proposition markers are found and presented
  - @mind:todo markers are found and presented
  - Resolution updates or removes markers
status: PROPOSED
```
