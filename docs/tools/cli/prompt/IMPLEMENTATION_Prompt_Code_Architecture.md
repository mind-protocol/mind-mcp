# CLI Prompt — Implementation: Code architecture and docking

@mind:id: CLI.PROMPT.IMPLEMENTATION

```
STATUS: DESIGNING
CREATED: 2025-12-21
```

---

## CHAIN

```
PATTERNS:       ./PATTERNS_Prompt_Command_Workflow_Design.md
BEHAVIORS:      ./BEHAVIORS_Prompt_Command_Output_and_Flow.md
ALGORITHM:      ./ALGORITHM_Prompt_Bootstrap_Prompt_Construction.md
VALIDATION:     ./VALIDATION_Prompt_Bootstrap_Invariants.md
THIS:           IMPLEMENTATION_Prompt_Code_Architecture.md
HEALTH:         ./HEALTH_Prompt_Runtime_Verification.md
SYNC:           ./prompt command sync (in ...mind/state/)

IMPL:           mind/prompt.py
                mind/cli.py
```

> **Contract:** Read the doc chain before modifying code. If implementation changes, update SYNC with what docs need adjustments.

---

## CODE STRUCTURE

```
mind/
├── prompt.py               # Builds and prints the bootstrap prompt
├── cli.py                  # Parses commands and routes `mind prompt`
``` 

### File Responsibilities

| File | Purpose | Key Functions/Classes | Lines | Status |
|------|---------|----------------------|-------|--------|
| `runtime/prompt.py` | Prompt generation helper | `generate_bootstrap_prompt`, `print_bootstrap_prompt` | ~90 | OK |
| `runtime/cli.py` | CLI routing for prompt command | `main()`, `print_bootstrap_prompt` invocation | ~400 | OK |

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Conventions-first orchestration

**Why:** The CLI provides a single command that composes doc references and prints them without altering state.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Template | `runtime/prompt.py` | Reuses a static string template with placeholders for docs and views |
| Router | `runtime/cli.py` | Maps CLI subcommands to implementation helpers |

### Anti-Patterns to Avoid

- **Heuristic prompts**: Do not hardcode agent assumptions; keep doc references canonical.
- **Prompt drift**: Keep `mind prompt` tied to PATTERNS/BEHAVIORS docs to avoid ad hoc instructions.

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Prompt generation | Composing doc path table and instructions | Executing repairs or reading state | `generate_bootstrap_prompt()` |

---

## SCHEMA

### PromptPayload

```yaml
prompt:
  required:
    - docs_section: string    # e.g., PROTOCOL/PRINCIPLES pointers
    - view_table: list        # table rows for VIEW selections
  optional:
    - checklist
  constraints:
    - Must mention SYNC updates
```

---

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| `print_bootstrap_prompt()` | `runtime/cli.py:364` | `mind prompt` subcommand |
| `generate_bootstrap_prompt()` | `runtime/prompt.py:17` | `print_bootstrap_prompt()` |

---

## DATA FLOW AND DOCKING

### Flow: Prompt Construction

```yaml
flow:
  name: prompt_construction
  purpose: Provide a guaranteed plan for agents to process the protocol
  scope: `runtime/prompt.py` string assembly -> CLI output
  steps:
    - id: resolve_docs
      description: Render `.mind` doc paths
      file: mind/prompt.py
      function: generate_bootstrap_prompt
      input: project_dir
      output: doc path strings
      trigger: CLI `prompt` command
      side_effects: none
    - id: build_view_table
      description: Assemble Markdown table of VIEWs
      file: mind/prompt.py
      function: generate_bootstrap_prompt
      input: view mapping
      output: string table
      trigger: same
    - id: append_checklist
      description: Add SYNC reminder and next steps
      file: mind/prompt.py
      function: generate_bootstrap_prompt
      input: const checklist
      output: final prompt text
      trigger: same
  docking_points:
    guidance:
      include_when: output is agent-facing and needs verification
      omit_when: generating logs without prompts
      selection_notes: focus on doc references and view table
    available:
      - id: dock_docs
        type: file
        direction: output
        file: mind/prompt.py
        function: generate_bootstrap_prompt
        trigger: mind prompt CLI
        payload: doc path references
        async_hook: not_applicable
        needs: none
        notes: verifies doc references remain canonical
      - id: dock_view_table
        type: file
        direction: output
        file: mind/prompt.py
        function: generate_bootstrap_prompt
        trigger: mind prompt CLI
        payload: view table strings
        async_hook: not_applicable
        needs: none
        notes: ensures VIEW map is accurate
      - id: dock_checklist
        type: file
        direction: output
        file: mind/prompt.py
        function: generate_bootstrap_prompt
        trigger: mind prompt CLI
        payload: checklist strings
        async_hook: not_applicable
        needs: none
        notes: reminds agents to update SYNC and rerun prompt checks
    health_recommended:
      - dock_id: dock_docs
        reason: Critical for doc traversal
      - dock_id: dock_view_table
        reason: Ensures VIEW selection guidance remains correct
      - dock_id: dock_checklist
        reason: Guards the SYNC checklist invariant
```

---

## LOGIC CHAINS

### LC1: Prompt Construction Chain

**Purpose:** Ensure prompt generation remains canonical, referencing docs and next steps.

1. PATTERNS defines required sections (docs, VIEW table, checklist).
2. ALGORITHM describes string assembly steps.
3. IMPLEMENTATION keeps the helper function aligned to the template.
4. HEALTH ensures runtime checks keep these invariants.

---

## MODULE DEPENDENCIES

- CLI prompt uses `runtime/cli.py` for the command entrypoint and relies on the doc chain (PATTERNS, BEHAVIORS, ALGORITHM, etc.) living under `docs/cli/prompt`. It also references the protocol docs to build the view table.

## STATE MANAGEMENT

- State artifacts include `...mind/state/SYNC_Project_Health.md` (health runtime can detect prompt drift) and `...mind/state/SYNC_Prompt_Command_State.md` (prompt-specific health snapshots). Prompt generation itself is stateless but pushes reminders into SYNC for agent follow-ups.
- Equivalent monitoring hooks may reference the same paths without the dot prefix.

## RUNTIME BEHAVIOR

1. CLI routes `mind prompt` to `print_bootstrap_prompt()`.
2. `generate_bootstrap_prompt()` reads the doc chain and assembles doc links + VIEW options.
3. Output is streamed to stdout; health checks expect the `PROMPT` command to produce these sections without mutation.

## CONCURRENCY MODEL

- The prompt command runs synchronously on a single thread and does not spawn subprocesses; it reads offline docs and writes to stdout.

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `prompt_docs` | config file (in `.mind/`) | `[]` | Additional docs to include in the prompt |
| `prompt_views` | config file (in `.mind/`) | standard VIEW table | Custom VIEW options for agents |

## BIDIRECTIONAL LINKS

- Code → Docs: `runtime/prompt.py` includes `DOCS:` references to this file and to the PATTERNS/ALGORITHM chain.
- Docs → Code: `docs/cli/prompt/ALGORITHM_Prompt_Bootstrap_Prompt_Construction.md` links back to `generate_bootstrap_prompt()` and mentions `print_bootstrap_prompt()` to keep the chain tidy.

## MARKERS

<!-- @mind:todo @mind:TODO Link this doc to `docs/cli/PATTERNS...` and confirm watchers know to update the template when impression shifts -->
<!-- @mind:proposition Emit telemetry when CLI prompt is generated to track compliance -->
<!-- @mind:escalation Should the CLI ever insert module-specific guidance (e.g., `modules.yaml` summary)? -->
