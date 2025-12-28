# mind Framework CLI — Algorithm: Command Processing Logic (Overview)

```
STATUS: STABLE
CREATED: 2025-12-18
VERIFIED: 2025-12-18 against commit 6e0062c
```

---

## CHAIN

```
PATTERNS:        ../PATTERNS_Why_CLI_Over_Copy.md
BEHAVIORS:       ../BEHAVIORS_CLI_Command_Effects.md
THIS:            ALGORITHM_Overview.md
VALIDATION:      ../VALIDATION_CLI_Instruction_Invariants.md
IMPLEMENTATION:  ../IMPLEMENTATION_CLI_Code_Architecture/overview/IMPLEMENTATION_Overview.md
HEALTH:          ../HEALTH_CLI_Command_Test_Coverage.md
SYNC:            ../SYNC_CLI_Development_State.md
```

---

## OVERVIEW

The CLI follows a simple dispatch pattern: parse arguments, route to a command module, execute, and return an exit code. The heaviest flows are `doctor` (health analysis) and `repair` (agent orchestration); `refactor` keeps documentation paths and `modules.yaml` entries coherent when files move, and `docs-fix` repairs stray chains without manual editing. This document is the single canonical source for every CLI command algorithm so readers can follow the narrative end to end.

---

## COMMAND ALGORITHMS

Each heading below keeps the previous command-specific details while leaving only one ALGORITHM doc in this folder.

### Init & Validate

#### Init command
- **Step 1: Preserve learnings.** If any `.mind-mcp/views/*_LEARNINGS.md` files exist, copy their non-empty sections into the refreshed protocol before deleting them.
- **Step 2: Copy protocol files.** When `--force` is provided, try to remove `.mind-mcp/` and warn if permissions prevent it; otherwise clone `templates/mind` into `.mind-mcp/` via `copytree`.
- **Step 3: Bootstrap supporting files.** Write `.mind-mcp/CLAUDE.md` and `AGENTS.md`, combining the command-specific prompts with `CODEX_SYSTEM_PROMPT_ADDITION.md` so agents receive the latest instructions.

#### Validate command
- **Step 1: Run every check.** Iterate through the validation suite (`check_protocol_installed`, `check_views_exist`, `check_project_sync_exists`, `check_module_docs_minimum`, `check_full_chain`, `check_naming_conventions`, `check_chain_links`, `check_module_manifest`) and aggregate the results.
- **Step 2: Print verdicts.** Display a green check for passing checks and list failures with their details when a result fails.
- **Step 3: Offer fix guidance.** For each failing check, print tailored remediation steps, link the appropriate VIEW, and show the templates that will help.

---

### Doctor & Repair

#### Doctor command
1. Load configuration from `target_dir`, merging `.gitignore` patterns, optional `config.yaml` settings, and thresholds (`monolith_lines`, `stale_sync_days`).
2. Run the doctor checks in priority order (`doctor_check_monolith`, `doctor_check_undocumented`, `doctor_check_stale_sync`, `doctor_check_placeholder`, `doctor_check_no_docs_ref`, `doctor_check_incomplete_chain`, `doctor_check_broken_impl_links`, `doctor_check_stub_impl`, `doctor_check_incomplete_impl`, `doctor_check_undoc_impl`, `doctor_check_large_doc_module`, `doctor_check_yaml_drift`, `doctor_check_recent_log_errors`).
3. Calculate a health score starting at 100, subtracting penalties per issue bucket (10 per critical, 3 per warning, 1 per info) and clamping at 0.
4. Shuffle issues within each severity bucket before publishing so agents do not repeatedly focus on the same items.
5. Serialize the markdown report to `...mind-mcp/state/SYNC_Project_Health.md` so downstream commands have the latest snapshot.

#### Repair command
1. Use `run_doctor()` to gather critical and warning issues, filtering by the requested depth (`links`, `docs`, or `full`) and any explicit issue-type filters; higher-priority issues (e.g., `YAML_DRIFT`) surface first.
2. For every remaining issue, build a repair prompt: fetch the issue instructions, split docs into existing vs missing, and call `build_agent_prompt` with the issue, the associated VIEW, the docs list, and the written task description.
3. Spawn repair agents in parallel (`ThreadPoolExecutor`) so each issue is handled concurrently, streaming progress via Claude/Gemini subprocesses and waiting for `REPAIR COMPLETE` or `REPAIR FAILED` signals from each session.
4. For each issue, run the assembled command, capture JSON/text output, and add the result to the aggregated list.
5. After agents finish, rerun `doctor` to compare before/after health scores and write a summary to `...mind-mcp/state/REPAIR_REPORT.md`.

##### Key decisions
- **D1: Depth filtering.** `links` restricts fixes to references (`NO_DOCS_REF`, `BROKEN_IMPL_LINK`, `YAML_DRIFT`, `UNDOC_IMPL`), `docs` adds document content fixes (`INCOMPLETE_CHAIN`, `PLACEHOLDER`, `LARGE_DOC_MODULE`), and `full` enables code changes including `MONOLITH`, `STUB_IMPL`, and `INCOMPLETE_IMPL`.
- **D2: Issue priority.** `YAML_DRIFT` issues are handled first, followed by `BROKEN_IMPL_LINK`, `UNDOCUMENTED`, and so on down to `NO_DOCS_REF` so the repair workflow targets the riskiest drifts before polishing references.

---

### Marker Scans & Support

#### Solve markers command
1. Load the doctor configuration as a baseline and aggregate ignore patterns plus log-file globs.
2. Scan every repository file (skipping ignored/binary blobs) for escalation (`@mind:escalation`, `@mind:doctor:escalation`), proposition (`@mind:proposition`, `@mind:doctor:proposition`), and todo tags; collect file paths and priorities.
3. Sort matches by severity (doctor markers first) and occurrence count, then print a numbered list so a human can resolve escalations or review propositions.

Helper utilities mentioned in this flow: `find_module_directories()`, `should_ignore_path()`, and `get_issue_instructions()` (which returns the VIEW, supporting docs, and a prompt template per issue type).

---

### Refactor command

#### Purpose
`mind refactor` keeps the documentation graph and `modules.yaml` in sync after renames/moves so the system maintains one authoritative layout.

#### Steps
1. Parse `mind refactor <action>` arguments, resolve every path relative to the repo root, and support `docs/…` values alongside module directories.
2. Move files/directories to their destination, creating parents as needed.
3. Compute canonical replacements (`old_rel` → `new_rel`), including directory-slash variants.
4. Scan text files (`.md`, `.py`, `.yaml`, `.json`, etc.) to replace every matching doc path.
5. Update `modules.yaml` entries, optionally renaming module keys to match the new layout.
6. Run `mind overview --folder docs` and `mind doctor` so the overview map and health checks reflect the refactor.

Optional flags (`--overwrite` default, `--skip-existing`, `--no-overwrite`) let callers control how collisions are handled. Actions extend past `rename`: `move` mirrors rename, `promote` raises a module into an area, `demote` places a module under an area, and `batch` applies multiple instructions in one run.

`DOCS: mind/refactor.py`

---

### Docs Fix command

#### Purpose
`mind docs-fix` repairs documentation chains and inserts minimal missing docs so protocol checks succeed without humans editing every file by hand.

#### Steps
1. Create any missing minimum docs for the CLI and schema modules.
2. Ensure the world-runner health documentation exists.
3. Rewrite broken CHAIN links so they point to the correct targets.
4. Print a summary of the fixes performed to stdout.

`DOCS: mind/docs_fix.py`

---

## DATA STRUCTURES

See `../IMPLEMENTATION_CLI_Code_Architecture/IMPLEMENTATION_Schema.md` for the canonical type definitions (e.g., `ValidationResult`, `DoctorIssue`, `RepairResult`).

---

## DATA FLOW (SUMMARY)

```
User Command
    ↓
argparse (cli.py)
    ↓
Command Router (cli.py:main)
    ↓
Command Module (e.g., doctor.py)
    ↓
Health/Validation/Repair Logic
    ↓
Output (stdout + files)
```

---

## PERFORMANCE NOTES

- `doctor` and `repair` are the heaviest commands because they scan repos and orchestrate agents.
- Parallel `repair` output is serialized via a print lock so messages from multiple agents do not interleave.
