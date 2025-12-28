# mind Framework CLI — Implementation: Code Architecture and Structure (Overview)

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
THIS:            ./IMPLEMENTATION_Overview.md
HEALTH:          ../../HEALTH_CLI_Command_Test_Coverage.md
SYNC:            ../../SYNC_CLI_Development_State.md
```

---

## OVERVIEW

The CLI is a modular command suite. Each subcommand lives in its own module and is dispatched by `mind/cli.py`. The two largest subsystems are Doctor (health checks) and Repair (agent orchestration).

**Implementation sections:**
- `../structure/IMPLEMENTATION_Code_Structure.md`
- `../runtime/IMPLEMENTATION_Runtime_And_Dependencies.md`
- `../schema/IMPLEMENTATION_Schema.md`

---

## DESIGN PATTERNS

- **Command pattern** for argparse routing (`*_command()` functions).
- **Composition** for doctor checks (`doctor_check_*`).
- **Factory-style dispatch** for repair instruction generation.
- **Subprocess isolation** for agent execution.

**Boundaries:**
- Doctor subsystem: `mind/doctor.py`, `mind/doctor_checks_*` modules.
- Repair subsystem: `mind/repair.py`, `mind/repair_core.py` modules.
- File discovery: `mind/doctor_files.py`, `mind/core_utils.py`.

## SUBSYSTEM IMPLEMENTATIONS

| Subsystem | Files | Description |
|-----------|-------|-------------|
| Doctor core | `mind/doctor.py`, `mind/doctor_checks.py`, `mind/doctor_checks_*`, `mind/doctor_files.py` | CLI entry (`DoctorRunner`), check catalog, and discovery helpers powering `mind doctor`. |
| Repair pipeline | `mind/repair_core.py`, `mind/repair_escalation_interactive.py`, `mind/repair_instructions.py`, `mind/repair_instructions_docs.py`, `mind/repair_report.py` | Orchestrates agent repair flows, escalation UI, and remediation doc generation. |
| Repository overview | `mind/repo_overview.py`, `mind/repo_overview_formatters.py` | Generates project maps and README summaries referenced by doc navigation health indicators. |
| Escalation solver | `mind/solve_escalations.py` | Prior stores escalate markers and surfaces proposals for humans/agents. |
| Core utilities | `mind/core_utils.py` | Shared helpers for path resolution, doc discovery, JSON/YAML handling, and canonical file operations. |
| Refactor pipeline | `mind/refactor.py` | Automates renaming/moving doc modules and regenerates overview/doctor outputs to keep the documentation graph consistent. |

```
IMPL: mind/doctor.py
IMPL: mind/doctor_checks.py
IMPL: mind/doctor_checks_content.py
IMPL: mind/doctor_checks_docs.py
IMPL: mind/doctor_checks_quality.py
IMPL: mind/doctor_checks_naming.py
IMPL: mind/doctor_checks_sync.py
IMPL: mind/doctor_files.py
IMPL: mind/repair_core.py
IMPL: mind/repair_escalation_interactive.py
IMPL: mind/repair_instructions.py
IMPL: mind/repair_instructions_docs.py
IMPL: mind/repair_report.py
IMPL: mind/repo_overview.py
IMPL: mind/repo_overview_formatters.py
IMPL: mind/solve_escalations.py
IMPL: mind/core_utils.py
```

---

## BIDIRECTIONAL LINKS (ENTRY)

- `mind/cli.py` includes a `DOCS:` pointer to `docs/cli/core/PATTERNS_Why_CLI_Over_Copy.md`.

---

## CODE STRUCTURE

The detailed file layout is captured in `../structure/IMPLEMENTATION_Code_Structure.md`; refer there for line counts and split candidates.

## SCHEMA

See `../schema/IMPLEMENTATION_Schema.md` for rich schema definitions (ValidationResult, DoctorIssue, RepairResult) used across CLI flows.

## ENTRY POINTS

Core entrypoints include `mind/cli.py::main`, `mind/doctor.py::run_doctor`, and `mind/repair.py::run_repair`; nested commands read from `modules.yaml` to check doc ownership before executing.

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

Flows are described in `../runtime/IMPLEMENTATION_Runtime_And_Dependencies.md`; the biggest ones are command dispatch and health reporting. Each flow lists docking points for `.mind-mcp/state` and `doc` artifacts.

## LOGIC CHAINS

Logic chains such as CLI dispatch → doctor runner → SYNC update are summarized in `../structure/IMPLEMENTATION_Code_Structure.md`, linking each step to doc anchors for traceability.

## MODULE DEPENDENCIES

Internal dependencies (CLI → doctor → repair, etc.) are captured in the runtime doc, while `modules.yaml` records how the CLI core relies on prompt + repo_overview modules.

## STATE MANAGEMENT

State layers include `...mind-mcp/state/` (health reports), `.mind-mcp/traces/`, and `modules.yaml`; the CLI writes them after each run to advertise progress to the doctor.

## RUNTIME BEHAVIOR

Runtime behavior splits across `mind/cli.py` (parsing/dispatch) and each command module (doctor, repair, prompt); the runtime doc describes their initialization and exit flows.

## CONCURRENCY MODEL

The CLI itself is synchronous, but `repair` uses a `ThreadPoolExecutor` to manage agent subprocesses and `doctor_checks` parallelizes independent checks.

## CONFIGURATION

Key switches (monolith thresholds, disabled checks, agent timeouts) live in the config file (in `.mind-mcp/`); the runtime doc references them with default values.

## BIDIRECTIONAL LINKS

Code references this overview via `DOCS:` markers inside `mind/cli.py`, and the overview links back to key files listed above to ensure traceability.

## MARKERS

<!-- @mind:todo Add DOCS: pointers from newly split doctor checks to this overview so each check is represented. -->
<!-- @mind:proposition Provide a CLI command to regenerate this overview automatically after code moves. -->
## GAPS (ACTIVE)

### Extraction Candidates

- `mind/doctor_checks.py` (~1364L) still needs further splitting.
- `mind/validate.py` (~712L) needs check extraction.

### Missing Implementation

<!-- @mind:todo Add type hints across the CLI codebase. -->
<!-- @mind:todo Add DOCS: references to all source files. -->

---

## ARCHIVE POINTER

Older extraction history moved to `docs/cli/archive/SYNC_archive_2024-12.md` to keep this overview current.
