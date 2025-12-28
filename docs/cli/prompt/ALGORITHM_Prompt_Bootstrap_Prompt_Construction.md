# CLI Prompt — Algorithm: Assemble the bootstrap prompt

@mind:id: CLI.PROMPT.ALGORITHM

```
STATUS: DESIGNING
CREATED: 2025-12-21
VERIFIED: 2025-12-21 against HEAD
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Prompt_Command_Workflow_Design.md
BEHAVIORS:       ./BEHAVIORS_Prompt_Command_Output_and_Flow.md
THIS:            ALGORITHM_Prompt_Bootstrap_Prompt_Construction.md
VALIDATION:      ./VALIDATION_Prompt_Bootstrap_Invariants.md
HEALTH:          ./HEALTH_Prompt_Runtime_Verification.md
SYNC:            ./SYNC_Prompt_Command_State.md

IMPL:            mind/prompt.py
generate_bootstrap_prompt()
```

> **Contract:** Read the full chain before changing algorithm; update SYNC or implementation afterward.

---

## OVERVIEW

The algorithm builds a multi-section prompt by interpolating the required doc paths, state location, and VIEW table into a string template. It follows the `@mind:id: PROMPT.INGEST.MODULE_CHAIN.FEATURE_INTEGRATION — ## Chain Hierarchy` directive by sequencing PATTERNS → BEHAVIORS → … → SYNC content and then handing the agent explicit next steps (SYNC updates, health reminder). It performs no IO except optional printing via `print_bootstrap_prompt()`.

---

## DATA STRUCTURES

### `prompt_template`

```
A literal string with placeholders for doc paths, instructions, and the VIEW lookup table.
```

### `view_rows`

```
A list of `(task, VIEW)` tuples used to render the VIEW table.
```

---

## ALGORITHM: `generate_bootstrap_prompt()`

### Step 1: Resolve canonical paths

Insert the absolute (or relative) `.mind` doc paths for `PROTOCOL.md`, `PRINCIPLES.md`, and `state/SYNC_Project_State.md`. This anchors the prompt to the correct project.

### Step 2: Define work-mode guidance

Describe autonomous vs collaborative modes, defaulting to collaborative when unspecified. This matches the PATTERNS intent to avoid human defaults.

### Step 3: Render the VIEW table

Loop over the predefined map of task descriptions to VIEW files and render the Markdown table used in the prompt. Keep the order stable so agents know which VIEW to load first.

### Step 4: Append execution checklist

Add steps reminding the agent to update SYNC, restate the project state, and re-run `mind prompt --dir {target_dir}` (the same directory you bootstrapped) whenever they lose the thread. Keep the quick “start now” question immediately before the checklist so the prompt still ends with actionable guidance.

---

## KEY DECISIONS

### D1: Relative vs absolute paths

```
IF project_dir is absolute:
    use absolute `.mind` paths
ELSE:
    use relative paths to keep the prompt portable
```

Decision rationale: absolute paths are easier to verify, but relative keeps prompts readable in shared logs.

### D2: Default work mode fallback

```
IF the human or previous agent specifies collaborative/autonomous:
    honor that
ELSE:
    default to collaborative mode
```

Rationale: collaborative mode keeps humans in the loop for complex choices.

---

## DATA FLOW

```
input: project_dir path (per `modules.yaml: prompt`) → render doc path strings (`PROTOCOL.md`, `PRINCIPLES.md`, `SYNC_Project_State.md`) → format work-mode guidance → build VIEW table (per `.mind-mcp/views/VIEW_Review_Evaluate_Changes.md`) → append SYNC/health checklist → output: prompt text
```

---

## COMPLEXITY

**Time:** O(n) where n = number of VIEW rows (constant ~10) — dominated by string formatting.

**Space:** O(1) additional memory beyond the returned string.

**Bottlenecks:** None; string operations are inexpensive.

---

## HELPER FUNCTIONS

### `print_bootstrap_prompt()`

**Purpose:** Print the generated prompt for easy copy/paste.

**Logic:** Calls `generate_bootstrap_prompt()` and writes to stdout.

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| `mind/cli.py` | `print_bootstrap_prompt()` | human-readable prompt text |
| `mind/prompt.py` | `generate_bootstrap_prompt()` | string used by CLI, docs, or tests |

---

## MARKERS

<!-- @mind:todo @mind:TODO Bake actual project metadata (e.g., `modules.yaml`) into the prompt in future iterations -->
<!-- @mind:proposition Parameterize the view table so custom tasks can be surfaced without editing the template string -->
<!-- @mind:escalation Should the prompt mention which health checks to verify before running work? -->
