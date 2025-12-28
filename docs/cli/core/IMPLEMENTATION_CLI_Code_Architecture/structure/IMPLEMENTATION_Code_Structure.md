# mind Framework CLI — Implementation: Code Structure

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

````
mind/
├── `mind/cli.py`
├── `mind/init_cmd.py`
├── `mind/validate.py`
├── `mind/doctor.py`
├── `mind/doctor_checks.py`
├── `mind/doctor_checks_core.py`
├── `mind/doctor_checks_metadata.py`
├── `mind/doctor_checks_reference.py`
├── `mind/doctor_checks_stub.py`
├── `mind/doctor_checks_prompt_integrity.py`
├── `mind/doctor_types.py`
├── `mind/doctor_report.py`
├── `mind/doctor_files.py`
├── `mind/agent_cli.py`
├── `mind/repair.py`
├── `mind/repair_core.py`
├── `mind/repair_report.py`
├── `mind/repair_instructions.py`
├── `mind/repair_instructions_docs.py`
├── `mind/repair_escalation_interactive.py`
├── `mind/solve_escalations.py`
├── `mind/sync.py`
├── `mind/context.py`
├── `mind/prompt.py`
├── `mind/project_map.py`
├── `mind/project_map_html.py`
├── `mind/repo_overview.py`
├── `mind/repo_overview_formatters.py`
├── `mind/github.py`
└── `mind/core_utils.py`
```

## DESIGN PATTERNS

- **Command dispatcher** — separates parsing (`mind/cli.py`) from execution (commands).
- **Check catalog** — each `doctor_checks_*` module owns a `doctor_check_*` function to keep the scope manageable.
- **Agent orchestration** — `mind/repair.py` calls `mind/agent_cli.py` to spawn and monitor repair agents consistently.

## SCHEMA

Key data structures such as `ValidationResult`, `DoctorIssue`, `RepairResult`, and `RepairInstruction` are defined in `../schema/IMPLEMENTATION_Schema.md`.

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| `main()` | `mind/cli.py:42` | `mind` CLI |
| `run_doctor()` | `mind/doctor.py:127` | `mind doctor` |
| `run_repair()` | `mind/repair.py:970` | `mind work` |
| `print_bootstrap_prompt()` | `mind/prompt.py:30` | `mind prompt` |
| `generate_repo_overview()` | `mind/repo_overview.py:12` | `mind overview` |

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

Flow descriptions mirror `../runtime/IMPLEMENTATION_Runtime_And_Dependencies.md`; the primary flows are macros for command dispatch and health reporting, docking to `...mind-mcp/state/SYNC_Project_Health.md` and `docs/`.

## LOGIC CHAINS

1. CLI dispatch → module handler → health/repair outcomes.
2. Doctor checks → `...mind-mcp/state/SYNC_Project_Health.md` → `mind/doctor_report.py`.

## MODULE DEPENDENCIES

CLI (`mind/cli.py`) → `mind/doctor.py`, `mind/repair.py`, `mind/prompt.py`, `mind/repo_overview.py`, `mind/core_utils.py`. Doctor → `mind/doctor_checks_*`, `mind/doctor_report.py`. Repair → `mind/repair_core.py`, `mind/repair_instructions*`, `mind/agent_cli.py`.

## STATE MANAGEMENT

State lives in `...mind-mcp/state/` (health, archives), `.mind-mcp/traces/`, and `modules.yaml`; commands write snapshots after every run for observability.

## RUNTIME BEHAVIOR

Initialization: parse args, load modules metadata.
Main loop: dispatch → run command → collect DoctorIssue/RepairResult → persist state.
Shutdown: flush logs, exit cleanly.

## CONCURRENCY MODEL

| Component | Model | Notes |
|-----------|-------|-------|
| CLI commands | synchronous | run sequentially |
| Doctor checks | threaded per bundle | may parallelize independent checks |
| Repair agents | ThreadPoolExecutor | agent subprocesses run concurrently with output serialized |

## CONFIGURATION

| Config | File | Description |
|--------|------|-------------|
| `monolith_lines` | config file (in `.mind-mcp/`) | threshold for splitting monolith files |
| `stale_sync_days` | config file (in `.mind-mcp/`) | staleness threshold for SYNC files |
| `disabled_checks` | config file (in `.mind-mcp/`) | list of doctor checks to skip |

## BIDIRECTIONAL LINKS

`mind/cli.py` contains `DOCS:` references back to this doc, and this doc links forward to `../overview/IMPLEMENTATION_Overview.md` and the referred code in the responsibilities table to keep doc-code coupling clear.

## FILE RESPONSIBILITIES

| File | Purpose | Key Functions/Classes | Lines | Status |
|------|---------|----------------------|-------|--------|
| `mind/cli.py` | Entry point, argument parsing | `main()` | ~290 | OK |
| `mind/init_cmd.py` | Protocol initialization | `init_protocol()` | ~168 | OK |
| `mind/validate.py` | Protocol invariant checking | `validate_protocol()` | ~712 | SPLIT |
| `mind/doctor.py` | Health check orchestration | `run_doctor()` | ~211 | OK |
| `mind/doctor_checks.py` | Core health checks | `doctor_check_*()` | ~1364 | SPLIT |
| `mind/doctor_checks_content.py` | Content analysis checks | `doctor_check_doc_duplication()` | ~410 | OK |
| `mind/doctor_checks_docs.py` | Documentation checks | `doctor_check_incomplete_chain()` | ~316 | OK |
| `mind/doctor_checks_quality.py` | Code quality checks | `doctor_check_hardcoded_secrets()` | ~172 | OK |
| `mind/doctor_checks_sync.py` | SYNC checks | `doctor_check_stale_sync()` | ~228 | OK |
| `mind/doctor_types.py` | Type definitions | `DoctorIssue`, `DoctorConfig` | ~41 | OK |
| `mind/doctor_report.py` | Report generation | `generate_health_markdown()` | ~465 | WATCH |
| `mind/doctor_files.py` | File discovery | `find_source_files()` | ~321 | OK |
| `mind/agent_cli.py` | Agent CLI wrapper | `build_agent_command()` | ~60 | OK |
| `mind/repair.py` | Repair orchestration | `repair_command()` | ~1013 | SPLIT |
| `mind/repair_core.py` | Repair models + helpers | `RepairResult` | ~693 | WATCH |
| `mind/repair_report.py` | Repair report generation | `generate_final_report()` | ~305 | OK |
| `mind/repair_instructions.py` | Code/test/config repair prompts | `get_issue_instructions()` | ~765 | WATCH |
| `mind/repair_instructions_docs.py` | Doc-related repair prompts | `get_doc_instructions()` | ~492 | WATCH |
| `mind/repair_escalation_interactive.py` | Interactive repair helpers | `resolve_escalation_interactive()` | ~372 | OK |
| `mind/solve_escalations.py` | Marker scanner | `find_escalation_markers()` | ~70 | OK |
| `mind/sync.py` | SYNC file management | `sync_command()` | ~346 | OK |
| `mind/context.py` | Documentation discovery | `get_module_context()` | ~553 | WATCH |
| `mind/prompt.py` | LLM prompt generation | `print_bootstrap_prompt()` | ~89 | OK |
| `mind/project_map.py` | Terminal dependency map | `print_project_map()` | ~359 | OK |
| `mind/project_map_html.py` | HTML export | `generate_html_map()` | ~315 | OK |
| `mind/repo_overview.py` | Repo overview | `generate_repo_overview()` | ~754 | SPLIT |
| `mind/repo_overview_formatters.py` | Overview formatting | `format_text_overview()` | ~264 | OK |
| `mind/github.py` | GitHub API integration | `create_issues_for_findings()` | ~288 | OK |
| `mind/core_utils.py` | Shared helpers | `get_templates_path()` | ~103 | OK |

**Size Thresholds:**
- **OK** (<400 lines)
- **WATCH** (400-700 lines)
- **SPLIT** (>700 lines)

**GAPS**
- `mind/doctor_checks.py` (~1364L) still needs further splitting.
- `mind/validate.py` (~712L) needs check extraction.

**GAPS / IDEAS / QUESTIONS**
<!-- @mind:todo Monitor `mind/repair.py` for growth above 700 lines and extract new helpers if needed. -->
<!-- @mind:proposition Provide an auto-generated summary of file statuses for doctors to reference. -->
