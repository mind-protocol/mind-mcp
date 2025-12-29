# CLI Prompt — Patterns: Workflow that surfacing protocol context

@mind:id: CLI.PROMPT.PATTERNS

```
STATUS: DESIGNING
CREATED: 2025-12-21
VERIFIED: 2025-12-21 against HEAD
```

---

## CHAIN

```
THIS:            PATTERNS_Prompt_Command_Workflow_Design.md
BEHAVIORS:       ./BEHAVIORS_Prompt_Command_Output_and_Flow.md
ALGORITHM:       ./ALGORITHM_Prompt_Bootstrap_Prompt_Construction.md
VALIDATION:      ./VALIDATION_Prompt_Bootstrap_Invariants.md
IMPLEMENTATION:  ./IMPLEMENTATION_Prompt_Code_Architecture.md
HEALTH:          ./HEALTH_Prompt_Runtime_Verification.md
SYNC:            ./SYNC_Prompt_Command_State.md

IMPL:            mind/prompt.py
```

### Bidirectional Contract

**Before modifying:** Read every doc in this chain and `runtime/prompt.py`.
**After modifying:** Align implementation, or log a TODO in `SYNC_Prompt_Command_State.md` if implementation must wait.

---

## THE PROBLEM

Agents entering a project lack a structured entry point that enforces the protocol: they drift, re-read the wrong docs, or jump into code with missing state. Without a canonical bootstrap prompt, each repair agent experiments with ad hoc instructions and loses productivity.

---

## THE PATTERN

Create a single CLI action (`mind prompt`) that reads the `@mind:id: PROMPT.INGEST.MODULE_CHAIN.FEATURE_INTEGRATION — data/MIND Documentation Chain Pattern (Draft “Marco”).md — ## The Documentation Chain › ## Chain Hierarchy` guidance, enumerates the required doc chain, and hands the agent an explicit plan. The prompt also articulates work mode, VIEW selection, and verification steps so the agent follows the mind method instead of default repo instincts.

---

## PRINCIPLES

### Principle 1: Protocol First

Every bootstrap prompt must surface `PROTOCOL.md`, `PRINCIPLES.md`, and the current `SYNC_Project_State.md` before anything else. Without that ordering, agents rebuild a nav tree from scratch each time.

### Principle 2: Visible Decisions

The prompt lists VIEW names, required verification steps, and when to update SYNC. Agents can choose confidently because responsibility boundaries are explicit.

### Principle 3: Evidence Over Assumptions

The prompt includes references to doc paths and states what counts as verified. Agents never guess what has been read or which SYNC sections they must update.

---

## DATA

| Source | Type | Description |
|--------|------|-------------|
| `@mind:id: PROMPT.INGEST.MODULE_CHAIN.FEATURE_INTEGRATION — data/MIND Documentation Chain Pattern (Draft “Marco”).md — ## The Documentation Chain` | SPEC | Canonical policy describing chain order, linking rules, doctor responsibilities, health wiring, and minimal chain manifest requirements. |
| `@mind:id: CLI.PROMPT.PATTERNS` | DOC | This module’s pattern doc (this file) outlines the prompt workflow. |
| `@mind:id: CLI.DOC_CHAIN.RULES` (pending) | DOC | TBD cross-cutting reference for link integrity (see `MIND Documentation Chain Pattern` “Doctor Responsibilities”). |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| docs/cli/core/PATTERNS_Why_CLI_Over_Copy.md | Defines why the CLI anchors the prompt command to doc navigation |
| docs/cli/core/ALGORITHM_CLI_Command_Execution_Logic/ALGORITHM_Overview.md | Describes how CLI commands are orchestrated and where `prompt` fits |

---

## INSPIRATIONS

- Claude Code’s agent bootstrap prompt that enumerates rules and references
- Git’s `help` output that lists subcommands + usage before doing anything
- The mind method that documents context, plan, and handoffs atomically

---

## SCOPE

### In Scope

- Leading LLM agents through the required VIEW loading sequence
- Encoding canonical doc references and state tokens in the prompt text
- Including immediate next steps (sync updates, health checks) so agents are auditable

### Out of Scope

- Implementing new agent features beyond bootstrap guidance (see `agent_cli.py` for that)
- Running the prompt command inside CI without an agent in control

---

## MARKERS

<!-- @mind:todo @mind:TODO Flesh out the preceding VIEW descriptions with LOC-aligned guidance from `.mind/views` and cite them here plus cross-cutting `@mind:id: PROMPT.INGEST.MODULE_CHAIN.FEATURE_INTEGRATION — ## Canon Linking Rules`. -->
<!-- @mind:proposition Capture usage metrics (which VIEW is chosen most) via future health indicator described in `docs/cli/prompt/HEALTH_Prompt_Runtime_Verification.md` (see `health_indicators` section). -->
<!-- @mind:escalation Should the prompt ever auto-switch agents to autonomous mode when `SYNC_Project_State.md` is empty or flagged “DESIGNING”? If so, what doc + health signal anchors that decision? Document answer here. -->
