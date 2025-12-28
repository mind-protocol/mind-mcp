# mind Framework CLI — Algorithm: Command Execution Logic

```
STATUS: STABLE
CREATED: 2025-12-18
VERIFIED: 2025-12-18 against commit 6e0062c
```

---

## CHAIN

```
PATTERNS:        ./core/PATTERNS_Why_CLI_Over_Copy.md
BEHAVIORS:       ./core/BEHAVIORS_CLI_Command_Effects.md
THIS:            docs/cli/ALGORITHM_CLI_Command_Execution_Logic.md
VALIDATION:      ./core/VALIDATION_CLI_Instruction_Invariants.md
IMPLEMENTATION:  ./IMPLEMENTATION_CLI_Code_Architecture.md
HEALTH:          ./core/HEALTH_CLI_Command_Test_Coverage.md
SYNC:            ./core/SYNC_CLI_Development_State.md

IMPL:            mind/cli.py
IMPL:            mind/doctor.py
```

> **Contract:** Understand the chain and refer to the CLI core doc set before touching implementation.

---

## OVERVIEW

The CLI dispatches user inputs into commands, prioritizing health, repair, and prompt flows in separate modules. It parses arguments, routes to the appropriate module, and surfaces health data for downstream observers. Most complexity resides in ensuring heavy commands such as `doctor` and `repair` remain traceable via the doc chain while supporting prompt-generation entry points.

## DATA STRUCTURES

- `CommandDefinition`
  - `name: str`, `handler: Callable`, `requires_health: bool`
  - Stored in the dispatch table inside `cli.py`
  - Constraints: handler must accept `(args, context)`
- `DispatchContext`
  - `command_name: str`, `args: Namespace`, `metadata: dict`
  - Enriched with `modules.yaml` info and doc anchors before invoking modules
- `DoctorIssue`
  - Captured from doctor checks, includes `category`, `severity`, `loc`, `doc`

---

## ALGORITHM: `dispatch_command()`

### Step 1: Parse input

Argparse builds a `Namespace` for the provided subcommand and options, invoking the `parse_args()` call from `cli.py`.

### Step 2: Resolve handler

Dispatch looks up the subcommand in the registered command table (doctor, repair, validate, prompt, etc.), failing fast if unknown.

### Step 3: Execute command

The resolved handler runs with the parsed args; it returns exit codes, writes SYNC files, and emits DoctorIssue objects when health is involved.

### Step 4: Emit health signals

`doctor.py` and related modules translate issues into `...mind-mcp/state/SYNC_Project_Health.md` and supplemental Markdown reports.

---

## KEY DECISIONS

### D1: Should unknown commands fall back or fail?

```
IF parser.has_subcommand(cmd):
    proceed → handler(args)
ELSE:
    error message + return 1
```

Command discovery fails fast to avoid silent no-ops.

### D2: Health first or repair first?

```
IF command == doctor:
    run_doctor() → collect issues
ELSE IF command == repair:
    run_repair() → orchestrate agents
ELSE:
    run_lightweight_command()
```

Dedicated flows keep heavy operations isolated.

---

## DATA FLOW

```
user argv
  → argparse (mind/cli.py)
    → dispatch table
      → doctor.py / repair.py / prompt.py
        → doctor checks / repair agents / prompt generator
          → SYNC + README + terminal output
```

Docking points: `...mind-mcp/state/SYNC_Project_Health.md`, `...mind-mcp/state/SYNC_Project_Health_archive_*.md`, `.mind-mcp/traces/`.

---

## COMPLEXITY

**Time:** O(n) where `n` is the number of commands and checks invoked; `doctor` walks files but caches context.

**Space:** O(m) tracking DoctorIssue objects and command metadata until reporting completes.

**Bottlenecks:**
- `doctor` file discovery scanning `.gitignore` directories
- `repair` agent concurrency coordination

---

## HELPER FUNCTIONS

### `build_command_table()`

Purpose: exposes available commands and metadata for the dispatcher.

Logic: collects command definitions from the CLI registry, merges in module metadata, and links them to doc anchors.

### `run_command_with_health()`

Purpose: wraps heavy commands in health reporting to ensure SYNC updates happen.

Logic: executes the handler, collects DoctorIssue list, and calls `doctor_report.generate_health_markdown()`.

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| `mind/cli.py` | `dispatch_command()` | command exit code |
| `mind/doctor.py` | `run_doctor()` | health score + SYNC update |
| `mind/repair.py` | `run_repair()` | repair report + artifacts |

---

## MARKERS

<!-- @mind:todo Record per-command runtime metrics in `.mind-mcp/state` for future health graphs. -->
<!-- @mind:todo Surface doc integrity hooks as part of the doctor run output. -->
<!-- @mind:proposition Build a dedicated CLI diagnostics command to replay earlier doctor runs. -->
<!-- @mind:escalation Should command dispatch load modules lazily to reduce startup time? -->
