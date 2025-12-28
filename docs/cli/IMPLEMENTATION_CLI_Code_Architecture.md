# mind Framework CLI — Implementation: Code Architecture and Structure

```
STATUS: STABLE
CREATED: 2025-12-18
```

---

## CHAIN

```
PATTERNS:        ./core/PATTERNS_Why_CLI_Over_Copy.md
BEHAVIORS:       ./core/BEHAVIORS_CLI_Command_Effects.md
ALGORITHM:       ./ALGORITHM_CLI_Command_Execution_Logic.md
VALIDATION:      ./core/VALIDATION_CLI_Instruction_Invariants.md
THIS:            docs/cli/IMPLEMENTATION_CLI_Code_Architecture.md
HEALTH:          ./core/HEALTH_CLI_Command_Test_Coverage.md
SYNC:            ./core/SYNC_CLI_Development_State.md

IMPL:            mind/cli.py
IMPL:            mind/doctor.py
IMPL:            mind/repair.py
IMPL:            mind/prompt.py
```

> **Contract:** Read the chain before updating. Keep this overview aligned with the detailed subdocs in `docs/cli/core/IMPLEMENTATION_CLI_Code_Architecture/`.

---

## CODE STRUCTURE

```
mind/
├── mind/cli.py                      # single CLI entrypoint that routes into each command
├── init_cmd.py                 # protocol initialization helpers
├── validate.py                 # invariants enforcement command
├── doctor.py                   # health orchestration entrypoint
├── doctor_checks.py            # aggregated doctor checks
├── doctor_checks_core.py       # orchestrates check bundles
├── doctor_checks_metadata.py   # metadata-driven helpers
├── doctor_checks_reference.py  # reference-based helpers
├── doctor_checks_stub.py       # placeholder/stub checks
├── doctor_checks_prompt_integrity.py # prompt integrity helpers
├── doctor_report.py            # report generation
├── doctor_files.py             # doc discovery
├── repair.py                   # agent orchestration CLI interface
├── repair_core.py              # repair models and helpers
├── repair_instructions.py      # prompt generation
├── repair_instructions_docs.py # doc scaffolding for repairs
├── repair_escalation_interactive.py # interactive escalation helpers
├── repo_overview.py            # project-map generation
├── repo_overview_formatters.py # formatting helpers for overviews
├── solve_escalations.py        # marker scanner
├── core_utils.py               # shared utilities for doc discovery and JSON/YAML
├── mind/prompt.py                   # bootstrap prompt generation for agents
├── project_map.py              # repo overview command
└── project_map_html.py         # HTML export
```

This split is described in `docs/cli/core/IMPLEMENTATION_CLI_Code_Architecture/structure/IMPLEMENTATION_Code_Structure.md` along with file responsibilities and status indicators (OK/WATCH/SPLIT).

---

## DESIGN PATTERNS

- **Command pattern** for `mind/cli.py` routing and ensuring each subcommand implements a `run()` style function.
- **Monolith decomposition** documented in `doctor_checks` submodules to keep each health check self-contained (see ideas in the submodule GAPS).
- **Flow-based docking** described in the subdocs to ensure repair, doctor, and prompt flows expose explicit hooks for health observers.

Anti-pattern guardrails:
- **God objects** are avoided by splitting `doctor_checks` into `core`, `metadata`, and `reference` helpers as noted in the core doc chain.
- **Premature optimization**: new limits go into the config file (in `.mind-mcp/`) only when validated by DOC_TEMPLATE_DRIFT insights.

Boundaries:
| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Health checks | `mind/doctor.py` plus `mind/doctor_checks_*` modules | CLI routing logic | `run_doctor()` |
| Repair agents | `mind/repair.py` plus `mind/repair_core.py` and instruction modules | CLI routing logic | `run_repair()` |
| Prompt provisioning | `mind/prompt.py` | command parsing | `print_bootstrap_prompt()` |

---

## SCHEMA

```yaml
ValidationResult:
  required:
    - name: str           # refer to docs/cli/core/IMPLEMENTATION_CLI_Code_Architecture/schema/IMPLEMENTATION_Schema.md for fields
    - errors: list[str]
  optional:
    - severity: str
  constraints:
    - severity must be one of INFO|WARN|FAIL

DoctorIssue:
  required:
    - id: str
    - category: str
  optional:
    - doc: str
  relationships:
    - relates_to: RepairInstruction
```

---

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| `main()` | `mind/cli.py:42` | `mind` command |
| `init_protocol()` | `mind/init_cmd.py:10` | `mind init` |
| `validate_protocol()` | `mind/validate.py:667` | `mind validate` |
| `run_doctor()` | `mind/doctor.py:127` | `mind doctor` |
| `run_repair()` | `mind/repair.py:970` | `mind work` |
| `print_bootstrap_prompt()` | `mind/prompt.py:30` | `mind prompt` |
| `generate_repo_overview()` | `mind/repo_overview.py:12` | `mind repo-overview` |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

### Command Dispatch Flow: parse → route → execute

Purpose: translates CLI input into command executions, ensuring each flow routes through health hooks.

```yaml
flow:
  name: command_dispatch
  purpose: route argv into validated CLI commands
  scope: argv → command module → stdout/files
  steps:
    - id: parse_args
      description: argparse inspects sys.argv and applies subcommand definitions
      file: mind/cli.py
      function: main
      input: sys.argv
      output: command_name, parsed_args
      trigger: CLI invocation
      side_effects: may set logging config
    - id: select_module
      description: router resolves the command name to the implementer in doctor/repair/prompt
      file: mind/cli.py
      function: dispatch_command
      input: command_name, parsed_args
      output: selected module callable
      trigger: after parser completes
      side_effects: none
    - id: execute
      description: runs the selected command, which in turn may call doctor, repair, or prompt helpers
      file: {doctor.py | repair.py | mind/prompt.py}
      function: run_doctor/run_repair/print_bootstrap_prompt
      input: parsed_args
      output: exit code, artifacts
      trigger: dispatch_command
      side_effects: writes SYNC, state files, report artifacts
  docking_points:
    guidance:
      include_when: targeted health entry point or heavy flow
      omit_when: trivial helper command
    available:
      - id: doc_sync
        type: file
        direction: output
        file: ...mind-mcp/state/SYNC_Project_Health.md
        function: doctor_runner
        trigger: after doctor finishes
        payload: JSON
        async_hook: not_applicable
        needs: none
      - id: repair_report
        type: event
        direction: output
        file: mind/repair_report.py
        function: generate_final_report
        trigger: post repair agents
        payload: Markdown report
        async_hook: optional
        needs: journaling, timestamping
    health_recommended:
      - dock_id: doc_sync
        reason: captures health run results for monitoring

### Health Check Flow: doctor → checks → reports

Purpose: orchestrate the health analysis pipeline, ensuring each step updates `.mind-mcp/state` and surfaces doc-link integrity.

```yaml
flow:
  name: doctor_health
  purpose: run the doctor checks and surface reports for health tracking
  scope: docs → doctor modules → output artifacts
  steps:
    - id: load_context
      description: gather module mappings, sync files, and config to seed the checks
      file: mind/context.py
      function: get_module_context
      input: modules.yaml, docs/, ...mind-mcp/state/
      output: context bundle
      trigger: start of doctor run
      side_effects: none
    - id: run_checks
      description: execute each `doctor_check_*` function to collect issues
      file: mind/doctor_checks_core.py
      function: doctor_check_bundle
      input: context bundle
      output: list of DoctorIssue
      trigger: after context load
      side_effects: may log intermediate signals
    - id: render_report
      description: aggregate issues into markdown/JSON for CLI output and STATE files
      file: mind/doctor_report.py
      function: generate_health_markdown
      input: list of DoctorIssue
      output: Markdown + JSON + ...mind-mcp/state/SYNC_Project_Health.md
      trigger: after checks complete
      side_effects: writes health state
```

---

## LOGIC CHAINS

### LC1: Command-to-health handshake

**Purpose:** Guarantee that every CLI command touches health state in a predictable way.

```
sys.argv
  → mind/cli.py.dispatch_command()
    → {doctor.run_doctor() | repair.run_repair() | prompt.print_bootstrap_prompt()}
      → health artifacts (.mind-mcp/state, docs, reports)
```

**Data transformation:**
- Input: parsed CLI args → ensures command name and options.
- After dispatch: enriched context with module metadata.
- Output: `DoctorIssue` or `RepairResult` for downstream consumers.

### LC2: Health-report rendering

**Purpose:** Translate collected DoctorIssue objects into human-readable signals.

```
DoctorIssue list
  → mind/doctor_report.py.generate_health_markdown()
    → markdown + JSON + .mind-mcp/state reports
```

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
mind/cli.py
  └── imports → doctor.py, repair.py, mind/prompt.py, core_utils.py
doctor.py
  └── imports → doctor_checks_core.py, mind/doctor_checks_metadata.py, doctor_report.py
repair.py
  └── imports → repair_core.py, repair_instructions_docs.py, agent_cli.py
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `argparse` | CLI parsing | `mind/cli.py` |
| `json` | State/output serialization | `mind/core_utils.py` |
| `yaml` | Template loading/config | `mind/context.py`, `mind/init_cmd.py` |

Repair agent threading relies on a thread pool inside `mind/repair.py` so subprocess output is serialized while checks continue.

---

## STATE MANAGEMENT

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| Health report | `...mind-mcp/state/SYNC_Project_Health.md` | project | overwritten each `mind doctor` |
| Doc templates | `docs/` | project | updated when templates change |
| Module map | `modules.yaml` | project | edited when modules move |
| Repair results | `...mind-mcp/state/repair_results/` (future) | per run | appended per repair |

State transitions:

```
raw CLI args ──> dispatch context ──> command execution ──> issue artifacts ──> health report
```

---

## RUNTIME BEHAVIOR

### Initialization

```
1. Parse CLI args via argparse
2. Instantiate logging and config
3. Load module manifest
```

### Main Cycle

```
1. Dispatch command
2. Run doctor/repair/prompt
3. Print output and write SYNC/state files
4. Exit with result
```

### Shutdown

```
1. Flush logs/reports
2. Save final state (.mind-mcp/state)
3. Exit with code
```

---

## CONCURRENCY MODEL

| Component | Model | Notes |
|-----------|-------|-------|
| CLI commands | synchronous | Each command runs to completion before exit |
| Doctor checks | threaded | `doctor_checks_core` may parallelize per check bundle |
| Repair agents | `ThreadPoolExecutor` | Tracks agent subprocess output streams |

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `monolith_lines` | config file (in `.mind-mcp/`) | `500` | When to split files before checking |
| `stale_sync_days` | config file (in `.mind-mcp/`) | `14` | Stale SYNC threshold before warning |
| `disabled_checks` | config file (in `.mind-mcp/`) | `[]` | Doctor checks to skip |
| `svg_namespace` | config file (in `.mind-mcp/`) | `http://www.w3.org/2000/svg` | Namespace for project map exports |

---

## BIDIRECTIONAL LINKS

### Code → Docs

| File | Line | Reference |
|------|------|-----------|
| `mind/cli.py` | ~40 | `docs/cli/core/PATTERNS_Why_CLI_Over_Copy.md` |
| `mind/doctor.py` | ~120 | `docs/cli/core/IMPLEMENTATION_CLI_Code_Architecture/overview/IMPLEMENTATION_Overview.md` |

### Docs → Code

| Doc Section | Implemented In |
|-------------|----------------|
| Command dispatch flow | `mind/cli.py::dispatch_command` |
| Health runner | `mind/doctor.py::run_doctor` |

---

## MARKERS

### Extraction Candidates

| File | Current | Target | Extract To | Notes |
|------|---------|--------|------------|-------|
| `mind/doctor_checks_core.py` | ~800L | <400L | `mind/doctor_checks_metadata.py` | Completed split but watch for growth |
| `mind/repair.py` | ~1200L | <700L | `mind/repair_core.py` | Agent orchestration still heavy |

### Missing Implementation

<!-- @mind:todo Add DOCS pointers to `mind/prompt.py` and `mind/doctor_checks_*` in each submodule. -->
<!-- @mind:todo Ensure `mind/repair.py` writes to `...mind-mcp/state/repair_results/` (future work). -->

### Ideas

<!-- @mind:proposition Introduce a metadata-first doc when splitting new CLI modules. -->
<!-- @mind:proposition Surface prompt health data directly in `mind doctor` output for faster operator triage. -->

### Questions

<!-- @mind:escalation Should `mind/doctor_files.py` be split further or removed once new discovery helpers cover the same ground? -->
<!-- @mind:escalation How do we keep `modules.yaml` in sync when new CLI commands land? -->
