# mind Framework CLI — Health: Verification Mechanics and Coverage

```
STATUS: STABLE
CREATED: 2025-12-20
```

---

## PURPOSE OF THIS FILE

This file defines the health verification mechanics for the mind CLI. It protects the core user-facing entry points of the framework, ensuring that commands like `init`, `validate`, `doctor`, and `repair` function correctly across different project environments.

It safeguards:
- **Project Integrity:** Ensuring protocol files are correctly installed and maintained.
- **Verification Reliability:** Ensuring `validate` and `doctor` provide accurate health signals.
- **Agent Effectiveness:** Ensuring `repair` and `context` provide the right data for AI agents to work.

Boundaries:
- This file covers CLI command execution and output correctness.
- It does not verify the deep internal logic of the LLM agents (covered in `docs/llm_agents/HEALTH_LLM_Agent_Coverage.md`).
- It does not verify TUI visual components (covered in `docs/tui/HEALTH_TUI_Coverage.md`).

---

## WHY THIS PATTERN

HEALTH is separate from tests because it verifies real system health without changing implementation files. For the CLI, this is critical because behavior can depend on the environment (working directory, existence of `.git`, filesystem permissions).

- **Failure mode avoided:** Commands returning success exit codes but producing corrupted or incomplete protocol files.
- **Docking-based checks:** Uses the filesystem and stdout as the primary docking points to verify that commands had the intended effect.
- **Throttling:** Protects performance by ensuring heavy checks like `doctor` or `repair --dry-run` are run at appropriate cadences.

---

## HOW TO USE THIS TEMPLATE

1. Read the full doc chain (PATTERNS → BEHAVIORS → ALGORITHM → VALIDATION → IMPLEMENTATION → SYNC).
2. Identify critical CLI flows that must never fail (init, validate, doctor).
3. Select docks (filesystem, stdout/stderr, exit codes).
4. Verify command outputs against VALIDATION criteria.

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Why_CLI_Over_Copy.md
BEHAVIORS:       ./BEHAVIORS_CLI_Command_Effects.md
ALGORITHM:       ./ALGORITHM_CLI_Command_Execution_Logic/ALGORITHM_Overview.md
VALIDATION:      ./VALIDATION_CLI_Instruction_Invariants.md
IMPLEMENTATION:  ./IMPLEMENTATION_CLI_Code_Architecture/overview/IMPLEMENTATION_Overview.md
THIS:            HEALTH_CLI_Command_Test_Coverage.md
SYNC:            ./SYNC_CLI_Development_State.md
```

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: init_command
    purpose: Installs the protocol in a new project. Failure leads to broken agent workflows.
    triggers:
      - type: manual
        source: cli:mind init
    frequency:
      expected_rate: 1/project
      peak_rate: 10/min (during mass onboarding)
      burst_behavior: stable
    risks:
      - V-CLI-INIT: Protocol files missing or corrupted
    notes: Critical for first-time user experience.

  - flow_id: validate_command
    purpose: Verifies protocol health. Failure leads to silent drift and agent confusion.
    triggers:
      - type: event
        source: pre-commit hook or agent start
    frequency:
      expected_rate: 10/day
      peak_rate: 100/min (CI runs)
      burst_behavior: spikes during PR reviews
    risks:
      - V-CLI-VALIDATE: False negatives on broken chains
    notes: Foundational for all other health checks.

  - flow_id: doctor_command
    purpose: Deep project analysis. Failure leads to unaddressed monoliths or stale docs.
    triggers:
      - type: schedule
        source: daily cron or TUI refresh
    frequency:
      expected_rate: 1/hour
      peak_rate: 5/min
      burst_behavior: stable
    risks:
      - V-CLI-DOCTOR: Incorrect health score or missed issues
    notes: Heavy check, must be throttled.
```

---

## HEALTH INDICATORS SELECTED

```yaml
health_indicators:
  - name: init_success
    flow_id: init_command
    priority: high
    rationale: If init fails, the user cannot use mind.
  - name: validation_accuracy
    flow_id: validate_command
    priority: high
    rationale: Protocol integrity depends on accurate validation.
  - name: doctor_reliability
    flow_id: doctor_command
    priority: med
    rationale: Surfaces project-level quality issues.
```

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: ...mind-mcp/state/SYNC_Project_Health.md
  result:
    representation: float_0_1
    value: 0.85
    updated_at: 2025-12-20T00:00:00Z
    source: doctor_command
```

---

## DOCK TYPES (COMPLETE LIST)

- `file` (protocol files in .mind-mcp/)
- `cli` (stdout/stderr and exit codes)
- `process` (agent subprocesses for repair)

---

## INDICATOR: CLI Command Health

- **Purpose:** Tracks whether the core CLI commands (`init`, `validate`, `doctor`, `repair`) complete without corruption or missing artifacts.
- **Dock:** stdout/stderr + `...mind-mcp/state/SYNC_Project_Health.md`.
- **Validation:** Cross-check `DoctorIssue` outputs against the `doctor` command to ensure no dramatic regression in docs or templates.

---

## CHECKER INDEX

```yaml
checkers:
  - name: file_integrity_check
    purpose: Verifies .mind-mcp/ files exist and match templates
    status: active
    priority: high
  - name: command_exit_check
    purpose: Verifies CLI commands return 0 on success
    status: active
    priority: high
  - name: doctor_issue_count
    purpose: Monitors critical issues found by doctor
    status: active
    priority: med
```

---

## INDICATOR: Init Integrity

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: init_integrity
  client_value: Users can successfully bootstrap mind in their projects.
  validation:
    - validation_id: V-CLI-INIT
      criteria: All required protocol files are present and uncorrupted.
```

### HEALTH REPRESENTATION

```yaml
representation:
  allowed:
    - binary
  selected:
    - binary
  semantics:
    binary: 1 if all files present, 0 if any missing.
  aggregation:
    method: all-or-nothing
    display: binary
```

### DOCKS SELECTED

```yaml
docks:
  output:
    id: protocol_files
    method: init_protocol
    location: mind/init_cmd.py:10
```

---

## HOW TO RUN

```bash
# Run all health checks via validate
mind validate

# Run project health via doctor
mind doctor
```

---

## KNOWN GAPS

<!-- @mind:todo No automated unit tests for CLI argument parsing. -->
<!-- @mind:todo No integration tests for parallel repair agents. -->
<!-- @mind:todo No automated check for template version drift after upgrade. -->

---

## MARKERS

<!-- @mind:todo Add `mind doctor --check-only` for fast CI checks. -->
<!-- @mind:escalation Should `validate` automatically fix simple file missing issues? -->
