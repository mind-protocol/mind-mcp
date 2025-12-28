# mind Framework CLI — Implementation: Runtime and Dependencies

```
STATUS: STABLE
CREATED: 2025-12-18
```

---

## CHAIN

```
PATTERNS:        ../../PATTERNS_Why_CLI_Over_Copy.md
BEHAVIORS:       ../../BEHAVIORS_CLI_Command_Effects.md
ALGORITHM:       ../../ALGORITHM_CLI_Command_Execution_Logic/ALGORITHM_Overview.md
VALIDATION:      ../../VALIDATION_CLI_Instruction_Invariants.md
IMPLEMENTATION:  ../overview/IMPLEMENTATION_Overview.md
HEALTH:          ../../HEALTH_CLI_Command_Test_Coverage.md
SYNC:            ../../SYNC_CLI_Development_State.md
```

---

## CONTEXT

Entry point: `../overview/IMPLEMENTATION_Overview.md`.

---

## CODE STRUCTURE

See `../structure/IMPLEMENTATION_Code_Structure.md` for the physical file layout, responsibilities, and split guidance. Runtime insights assume that structure stays roughly the same while doctor/repair modules evolve.

## DESIGN PATTERNS

- **Flow-based docking**: runtime flows focus on command dispatch plus health reporting to keep instrumentation visible.
- **Agent orchestration**: `mind/repair.py` and `mind/agent_cli.py` treat each agent invocation as an isolated subprocess with deterministic inputs/outputs.
- **Command dispatcher**: `mind/cli.py` resolves subcommands by mapping names to handler modules, avoiding hardwired switches.

## SCHEMA

Schema definitions live in `../schema/IMPLEMENTATION_Schema.md`. Runtime flows rely on `ValidationResult`, `DoctorIssue`, and `RepairResult` to carry status through the flows described below.

---

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| main | mind/cli.py:43 | `mind` command |
| init_protocol | mind/init_cmd.py:15 | `mind init` |
| validate_protocol | mind/validate.py:667 | `mind validate` |
| doctor_command | mind/doctor.py:127 | `mind doctor` |
| repair_command | mind/repair.py:970 | `mind work` |
| sync_command | mind/sync.py | `mind sync` |
| print_module_context | mind/context.py:442 | `mind context` |
| print_bootstrap_prompt | mind/prompt.py | `mind prompt` |
| print_project_map | mind/project_map.py | `mind overview` |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

- **Command dispatch flow:** `mind/cli.py` parses args → selects handler → writes outputs to stdout/files → writes SYNC/state artifacts.
- **Health flow:** `mind/doctor.py` collects issues → `mind/doctor_report.py` renders Markdown + JSON → writes `...mind-mcp/state/SYNC_Project_Health.md` and archives.
- **Repair flow:** `mind/repair.py` builds prompts → `mind/agent_cli.py` runs subprocesses → `mind/repair_report.py` emits artifacts plus the repair report (in `...mind-mcp/state/`).
- **Init flow:** `mind/init_cmd.py` copies protocol assets → writes AGENTS/CLAUDE → copies `.mind-mcp/skills` into `.claude/skills` and `$CODEX_HOME/skills`.

Docking points include `...mind-mcp/state/`, `.mind-mcp/traces/`, `docs/`, and `...mind-mcp/state/SYNC_Project_Health.md`.

## LOGIC CHAINS

1. CLI dispatch → module handler → `DoctorIssue`/`RepairResult` → final report.
2. Health runner → `mind/doctor_report.py` → `...mind-mcp/state/SYNC_Project_Health.md` + Markdown + JSON outputs.

---

## MODULE DEPENDENCIES

Internal: CLI → doctor, repair, prompt, repo_overview, core_utils. Doctor → `doctor_checks_*`, `doctor_report`, `doctor_files`. Repair → `mind/repair_core`, `mind/repair_instructions`, `mind/agent_cli`. External: `argparse`, `pathlib`, `subprocess`, `yaml`, `json`.

## STATE MANAGEMENT

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| Doctor config | `DoctorConfig` | per-command | in-memory |
| Validation results | `List[ValidationResult]` | per-command | in-memory |
| Repair results | `List[RepairResult]` | per-command | in-memory |
| Trace logs | `.mind-mcp/traces/` | persistent | rotates daily |
| Health report | `...mind-mcp/state/SYNC_Project_Health.md` | persistent | overwritten each run |

## RUNTIME BEHAVIOR

```
1. argparse parses sys.argv
2. Router dispatches to command function
3. Command loads config if needed
4. Command executes
5. Results printed/saved
6. sys.exit(code)
```

### Agent Execution (repair)

```
1. Build prompt from issue + instructions
2. Spawn agent subprocess via `mind/agent_cli.py` wrapper
3. Stream JSON (Claude) or text (Codex/Gemini)
4. Wait for completion or timeout
5. Return RepairResult
```

## CONCURRENCY MODEL

| Component | Model | Notes |
|-----------|-------|-------|
| CLI commands | synchronous | run sequentially |
| Doctor checks | threaded | `doctor_checks_core` runs bundles in parallel |
| Repair agents | ThreadPoolExecutor | guard output with print_lock |

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `monolith_lines` | config file (in `.mind-mcp/`) | 500 | Monolith threshold |
| `stale_sync_days` | config file (in `.mind-mcp/`) | 14 | SYNC staleness |
| `ignore` | config file (in `.mind-mcp/`) + `.gitignore` | common | Ignore patterns |
| `disabled_checks` | config file (in `.mind-mcp/`) | [] | Checks to skip |
| `svg_namespace` | config file (in `.mind-mcp/`) or `MIND_SVG_NAMESPACE` | http://www.w3.org/2000/svg | Project map SVG namespace |

## BIDIRECTIONAL LINKS

`mind/cli.py` and command modules contain `DOCS:` pointers to this file; the file also links back to `../overview/IMPLEMENTATION_Overview.md` and the entry point files listed above to keep doc-code coherence.

## MARKERS

<!-- @mind:todo Capture runtime telemetry (command durations, doctor coverage) in `.mind-mcp/state`. -->
<!-- @mind:proposition Add CLI telemetry for frequent commands to feed into future architecture docs. -->
