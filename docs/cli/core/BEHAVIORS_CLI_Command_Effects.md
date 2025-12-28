# mind Framework CLI — Behaviors: Command Effects and Observable Outcomes

```
STATUS: STABLE
CREATED: 2025-12-18
VERIFIED: 2025-12-18 against commit 6e0062c
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Why_CLI_Over_Copy.md
THIS:            BEHAVIORS_CLI_Command_Effects.md
ALGORITHM:       ./ALGORITHM_CLI_Command_Execution_Logic/ALGORITHM_Overview.md
VALIDATION:      ./VALIDATION_CLI_Instruction_Invariants.md
IMPLEMENTATION:  ./IMPLEMENTATION_CLI_Code_Architecture/overview/IMPLEMENTATION_Overview.md
HEALTH:          ./HEALTH_CLI_Command_Test_Coverage.md
SYNC:            ./SYNC_CLI_Development_State.md
```

---

## BEHAVIORS

### B1: Init Command

```
GIVEN:  A project directory without mind Framework
WHEN:   `mind init` is executed
THEN:   .mind-mcp/ directory is created with protocol files
AND:    .mind-mcp/CLAUDE.md is created or updated with protocol bootstrap
AND:    AGENTS.md is created or updated with the bootstrap plus Codex guidance
AND:    modules.yaml template is copied to project root
AND:    .mindignore is copied to project root if missing
AND:    skills are copied from .mind-mcp/skills into .claude/skills
AND:    skills are copied from .mind-mcp/skills into $CODEX_HOME/skills (default ~/.codex/skills)
AND:    Repository map is generated at map.md
```

### B2: Init with Force

```
GIVEN:  A project with existing .mind-mcp/
WHEN:   `mind init --force` is executed
THEN:   Existing .mind-mcp/ is removed
AND:    Fresh protocol files are copied
AND:    .mind-mcp/CLAUDE.md and AGENTS.md are updated (not duplicated)
AND:    If removal fails due to permissions, init falls back to a partial refresh with warnings
```

### B3: Validate Command

```
GIVEN:  A project with mind Framework installed
WHEN:   `mind validate` is executed
THEN:   8 validation checks are run
AND:    Results are printed with pass/fail for each check
AND:    Exit code is 0 if all pass, 1 if any fail
AND:    Fix guidance is printed for failures
```

### B4: Doctor Command

```
GIVEN:  A project with mind Framework installed
WHEN:   `mind doctor` is executed
THEN:   13 health checks are run
AND:    Issues are grouped by severity (critical, warning, info)
AND:    Health score (0-100) is calculated
AND:    Results saved to ...mind-mcp/state/SYNC_Project_Health.md
AND:    Exit code is 0 even when issues are found
AND:    GitHub issues are created only when `--github` is provided
```

### B5: Repair Command

```
GIVEN:  A project with health issues from doctor
WHEN:   `mind work` is executed
THEN:   Repair agents are spawned for each issue
AND:    `--model {claude,codex,gemini}` selects the agent model
AND:    Agents follow appropriate VIEW for each issue type
AND:    Progress is streamed to terminal
AND:    Report saved to ...mind-mcp/state/REPAIR_REPORT.md
```

### B6: Context Command

```
GIVEN:  A source file path
WHEN:   `mind context <file>` is executed
THEN:   Dependency map is printed
AND:    Linked documentation chain is found
AND:    Full doc content is printed
AND:    Access is logged to traces
```

### B7: Sync Command

```
GIVEN:  A project with SYNC files
WHEN:   `mind sync` is executed
THEN:   SYNC file status is displayed
AND:    Large files (>200 lines) are auto-archived
```

### B8: Prompt Command

```
GIVEN:  A project with mind Framework
WHEN:   `mind prompt` is executed
THEN:   Bootstrap prompt for LLM is printed to stdout
AND:    Contains PROJECT, SYNC, MODULES sections
```

### B9: Overview Command

```
GIVEN:  A project directory
WHEN:   `mind overview` is executed
THEN:   File tree is generated (respecting .gitignore/.mindignore)
AND:    Timestamp added (YYYY-MM-DD HH:MM format)
AND:    Character counts shown for files and directories
AND:    Bidirectional links extracted (code→docs via DOCS:, docs→code via refs)
AND:    Cross-folder doc refs extracted
AND:    Section headers extracted from markdown files
AND:    Function/class definitions extracted from code files
AND:    Local imports extracted (stdlib/npm filtered out)
AND:    Module dependencies from modules.yaml included
AND:    Main map is saved to map.{md|yaml|json} in project root
AND:    Copy of main map is saved to docs/map.{md|yaml|json} (if docs/ exists)
AND:    Specific maps (map_{folder}.md) are generated for core folders (src, app, backend, etc)
```

**Options:**
- `--dir, -d PATH` — Target directory (default: cwd)
- `--folder, -p NAME` — Subfolder to map only (relative to project root). If provided, only this map is generated in root.
- `--format, -f {md,yaml,json}` — Output format (default: md)

### B10: Solve Escalations Command

```
GIVEN:  A project with files containing `@mind&#58;escalation`, `@mind&#58;proposition`, or `@mind&#58;todo` markers
WHEN:   `mind solve-markers` is executed
THEN:   The CLI identifies all files containing these markers
AND:    The CLI prints a numbered list of these files in priority order
AND:    The CLI prompts the human to review and resolve them
```

### B11: Agents Command

```
GIVEN:  A project with mind Framework
WHEN:   `mind agents <agent_name>` is executed
THEN:   The specified agent is invoked with the given prompt and context
AND:    The agent's output is streamed to the terminal
```

**Agents:**
- `gemini`, `claude`, `codex` (provider options)

### B12: Refactor Command

```
GIVEN:  A resolved rename/move/promote/demote/batch plan (paths listed)
WHEN:   `mind refactor <action> ...` is executed
THEN:   The filesystem item moves or is rearranged as requested
AND:    Every docs/ string, DOCS: link, modules.yaml entry, and SYNC reference is rewritten
AND:    Generates the docs overview (`mind overview --folder docs`)
AND:    Runs `mind doctor` so health assertions update with the new layout
AND:    Optional module key renames in modules.yaml happen when `--module-old/--module-new` is supplied
AND:    `--overwrite` removes targets before moving (default), `--skip-existing` skips existing targets, and `--no-overwrite` disables the default behavior
```

---

## NOTES

Inputs/outputs, edge cases, and anti-behaviors are captured in `docs/cli/core/VALIDATION_CLI_Instruction_Invariants.md` and `docs/cli/core/ALGORITHM_CLI_Command_Execution_Logic/ALGORITHM_Overview.md` to avoid duplication.

---

## INPUTS / OUTPUTS

- **Inputs:** CLI args (`--dir`, `--model`, `--format`, etc.), environment variables (e.g., `MIND_AGENT_TIMEOUT`, `GEMINI_API_KEY`), and documentation templates stored under `.mind-mcp/`.
- **Outputs:** Printed summaries (doctor/report), generated files (`docs/*`, `map.md`, `.mind-mcp/*`), and health/repair reports saved under `...mind-mcp/state/`.

---

## EDGE CASES

- Running commands outside a project should print a helpful error referencing `.mind-mcp/`.
- If `.mind` is partially installed (`init` fails), commands should abort gracefully and instruct the human to rerun `mind init`.
- Repair agents with missing config values (agent credentials, docs path) should fail fast with clear messages.

---

## ANTI-BEHAVIORS

- Never mutate protocol files outside the CLI when a command fails.
- Never swallow doctor/repair errors; always log the issue for humans via `.mind-mcp/state` outputs.
- Never hardcode doc paths; resolve them via `modules.yaml` and doc chains.

---

## MARKERS

<!-- @mind:todo Should `mind` provide a `--dry-run` toggle that prints all DOCS/chain updates without modifying files? -->
<!-- @mind:proposition Capture which commands humans run most often and emit that telemetry into `docs/cli/core/HEALTH_CLI_Command_Test_Coverage.md`. -->
<!-- @mind:escalation Should VERSIONING be added to the CLI behavior doc chain so prompts mention the protocol version before running? -->
