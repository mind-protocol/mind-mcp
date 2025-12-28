# mind Framework CLI — Patterns: Why CLI Over Copy

```
STATUS: STABLE
CREATED: 2025-12-18
VERIFIED: 2025-12-18 against commit 1440b4c
```

---

## CHAIN

```
THIS:            docs/cli/core/PATTERNS_Why_CLI_Over_Copy.md
BEHAVIORS:       ./BEHAVIORS_CLI_Command_Effects.md
ALGORITHM:       ../ALGORITHM_CLI_Command_Execution_Logic.md
VALIDATION:      ./VALIDATION_CLI_Instruction_Invariants.md
IMPLEMENTATION:  ./IMPLEMENTATION_CLI_Code_Architecture/overview/IMPLEMENTATION_Overview.md
HEALTH:          ./HEALTH_CLI_Command_Test_Coverage.md
SYNC:            ./SYNC_CLI_Development_State.md
```

---

## THE PROBLEM

Everything the protocol documents already live as markdown files. An agent could copy/paste them, but without tooling there is no easy way to discover, validate, or repair them. Manual updates require re-copying directories, manual health triage, and no shared instrumentation, so the protocol becomes brittle as soon as the doc surface grows.

## THE PATTERN

Wrap those files with a CLI that orchestrates: installation, validation, health, automated repair, and navigation helpers. The CLI minimizes logic to metadata routing while the heavy lifting stays in the markdown docs; it is orchestration, not a new specification.

## PRINCIPLES

### Principle 1: Files First, CLI Second

The CLI is a convenience layer. Every command is a thin wrapper around file manipulations, health signals, or agent prompts that could be reproduced manually. If the CLI becomes unavailable, the protocol still works because the files remain authoritative.

### Principle 2: Modular Subcommands

Each CLi command lives in its own partner module (init/verify/doctor/repair/sync/prompt). Modules register their entrypoints and doc references so new subcommands can be added without touching the existing ones.

### Principle 3: Agent-Driven Commands

Repair and agent-facing commands build structured prompts, spawn subprocesses via `agent_cli.py`, stream output, and capture results. Every prompt provides VIEW guidance, reference docs, and verification cues so progress stays traceable.

### Principle 4: Health Instruments Always Run

`mind doctor` is the gating flow. Every command either directly runs the doctor checks or integrates with its outputs to keep DOC_TEMPLATE_DRIFT, DOC_LINK_INTEGRITY, and CODE_DOC_DELTA couplings alive.

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `argparse` | CLI argument parsing |
| `pathlib` | Deterministic path manipulation |
| `subprocess` | Agent orchestration through `agent_cli.py` |
| `yaml` (optional) | Modules manifest (`modules.yaml`) and config ingestion |

---

## INSPIRATIONS

- **Git** — Subcommand pattern keeps behavior consistent (`git init`, `git status`).
- **Terraform** — `init`/`validate`/`plan`/`apply` workflow mirrors CLI structure.
- **Claude Code** — Agent-as-subprocess pattern informs repair/prompt orchestration.
- **Unix toolchain** — Compose small utilities (doctor, repair, sync) with clear doc boundaries.

---

## DATA

- Documentation chains, module manifests, SYNC files, and REPORT outputs are the primary data the CLI manipulates. Each CLI command shapes these artifacts without rewriting the protocol itself.
- Health reports, repair results, and module metadata flow through this layer so `mind doctor` can keep doc/code coupling honest and surface drift before it spreads.

## SCOPE

- **In scope:** CLI commands that install the protocol, validate invariants, surface health, spawn agents, or generate navigation context within a project.
- **Out of scope:** IDE/editor plugins, multi-repo orchestration, and any automation that bypasses the markdown-first workflow.

---

## WHAT THIS DOES NOT SOLVE

- The CLI does not define the protocol — the docs are canonical.
- It does not guarantee project-specific customization beyond `.mind-mcp/config.yaml`.
- There is no editor integration — it stays in the terminal.
- Multi-project orchestrations are outside its remit; the CLI works per repository.

---

## CLI SUBSYSTEM REFERENCES

| File | Subsystem | Role |
|------|-----------|------|
| `mind/doctor_files.py` | Health discovery | Enumerates doc roots, false positives, and ignores for `mind doctor`. |
| `mind/repair_core.py` | Repair orchestration | Builds repair tasks, runs agents, and tracks results. |
| `mind/repair_escalation_interactive.py` | Escalation handling | Provides interactive helper steps for repair flows. |
| `mind/repair_instructions.py` | Prompt builder | Serializes repair instructions for downstream agents. |
| `mind/repair_instructions_docs.py` | Doc scaffolding | Emits repair docs derived from `templates/` for agent output. |
| `mind/repair_report.py` | Reporting | Saves the final repair summary with success/failure states. |
| `mind/repo_overview.py` | Repository mapping | Generates project maps used by doc-link integrity signals. |
| `mind/solve_escalations.py` | Marker resolution | Surfaces proposals detected by `doctor` and `solve-markers`. |
| `mind/core_utils.py` | Utils | Path resolution, doc discovery, and canonical file helpers reused across CLI checks. |
| `mind/github.py` | GitHub integration | Creates issues from doctor results and tracks issue state. |

```
IMPL: mind/doctor_files.py
IMPL: mind/repair_core.py
IMPL: mind/repair_escalation_interactive.py
IMPL: mind/repair_instructions.py
IMPL: mind/repair_instructions_docs.py
IMPL: mind/repair_report.py
IMPL: mind/repo_overview.py
IMPL: mind/solve_escalations.py
IMPL: mind/core_utils.py
IMPL: mind/github.py
```

---

## MARKERS

<!-- @mind:todo Add `mind watch` for continuous health monitoring. -->
<!-- @mind:todo
title: "Replace repair with work command"
priority: high
status: resolved
decision: "2025-12-23: `mind repair` removed. Replaced by `mind work <path> [objective]`. Doctor auto-runs before work. Migration script to update all references. Clean switch, no deprecation."
completed: |
  1. Created work.py with new signature: work(path, objective=None)
  2. Added 'work' subparser to cli.py with positional path argument
  3. Doctor auto-runs (inherited from repair implementation)
  4. Migration script updated 12 doc files
  5. repair command kept as legacy alias
-->
<!-- @mind:proposition Integrate MCP server hints for richer tool access while work runs. -->
