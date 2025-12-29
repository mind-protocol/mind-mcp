# CLI Prompt — Behaviors: What the bootstrap command surfaces to agents

@mind:id: CLI.PROMPT.BEHAVIORS

```
STATUS: DESIGNING
CREATED: 2025-12-21
VERIFIED: 2025-12-21 against HEAD
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Prompt_Command_Workflow_Design.md
THIS:            BEHAVIORS_Prompt_Command_Output_and_Flow.md
ALGORITHM:       ./ALGORITHM_Prompt_Bootstrap_Prompt_Construction.md
VALIDATION:      ./VALIDATION_Prompt_Bootstrap_Invariants.md
IMPLEMENTATION:  ./IMPLEMENTATION_Prompt_Code_Architecture.md
HEALTH:          ./HEALTH_Prompt_Runtime_Verification.md
SYNC:            ./SYNC_Prompt_Command_State.md

IMPL:            mind/prompt.py
```

> **Contract:** Read PATTERNS before touching this behavior; update implementation or note TODO in SYNC after changes.

---

## BEHAVIORS

### B1: Generate the canonical bootstrap prompt

```
GIVEN:  An agent is asked to run `mind prompt`
WHEN:   The CLI builds its bootstrap instructions
THEN:   The output lists PROTOCOL, PRINCIPLES, state, VIEW choices, and next steps in a structured prompt
AND:    It ends by asking the agent to state current project context before taking action
```

### B2: Guide VIEW selection

```
GIVEN:  The list of views defined in `.mind/views`
WHEN:   The prompt prints the VIEW table
THEN:   Agents can choose the exact VIEW that matches their task without guessing
```

---

## INPUTS / OUTPUTS

### Primary Function: `generate_bootstrap_prompt()`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `target_dir` | `Path` | Project root (used to resolve `.mind` paths) |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| `str` | Prompt | Multi-section bootstrap instructions for LLM agents |

**Side Effects:**

- None (pure string builder) unless the caller prints the prompt (handled by `print_bootstrap_prompt`).

---

## EDGE CASES

### E1: Missing `.mind` directory

```
GIVEN:  The command runs in a directory without `.mind`
THEN:   The printed prompt still references the expected `.mind` paths so the agent can report the missing install
```

### E2: Read-only scenario

```
GIVEN:  Files like `.mind/PROTOCOL.md` are locked
THEN:   The prompt includes the intended paths but does not fail the CLI (reading is not required at generation time)
```

---

## ANTI-BEHAVIORS

### A1: Prompt omission

```
GIVEN:  `mind prompt` runs
WHEN:   The CLI omits any of the required sections (docs, state, VIEW table)
MUST NOT: Leave the agent guessing about what to read next
INSTEAD:  Rebuild the missing sections before printing
```

### A2: Human defaults

```
GIVEN:  An agent wants to skip the VIEW table because "it looks verbose"
WHEN:   They look at the output
MUST NOT: Assume human conventions (e.g., single bullet list)
INSTEAD:  Trust the structured sections and follow the instructions verbatim
```

---

## MARKERS

<!-- @mind:todo @mind:TODO Capture actual view choice telemetry so health can report which VIEW is selected most often (`HEALTH_Prompt_Runtime_Verification.md` → `health_indicators`) -->
<!-- @mind:proposition Surface a short summary of `data/MIND Documentation Chain Pattern (Draft “Marco”).md` source sections (see `@mind:id: PROMPT.INGEST.MODULE_CHAIN.FEATURE_INTEGRATION — ## Recap — Action Items`) in the prompt output for transparency. -->
<!-- @mind:escalation Should the prompt warn if `SYNC_Project_State.md` appears to be template content or out-of-date per the health indicator `prompt_doc_reference_check`? -->
