# mind Framework — Algorithm: Overview

```
STATUS: STABLE
CREATED: 2024-12-15
```

---

## CHAIN

```
PATTERNS:        ../PATTERNS_Bidirectional_Documentation_Chain_For_AI_Agents.md
BEHAVIORS:       ../BEHAVIORS_Observable_Protocol_Effects.md
THIS:            ./ALGORITHM_Protocol_Process_Flow.md
VALIDATION:      ../VALIDATION_Protocol_Invariants.md
HEALTH:          ../HEALTH_Protocol_Verification.md
SYNC:            ../SYNC_Protocol_Current_State.md
```

---

## OVERVIEW

This module describes the procedures agents follow to install the protocol and execute work.
Detailed workflows are consolidated here for easier navigation.

---

## CONTENTS

- Install and bootstrap
- Module workflows

---

## ALGORITHM: Install Protocol in Project

1. Copy templates into `.mind/`.
   - Source: `templates/mind/`
   - Target: `{project}/.mind/`
2. Update bootstrap files.
   - Append `templates/CLAUDE_ADDITION.md` to `.mind/CLAUDE.md` (create if missing).
   - Mirror the same content to root `AGENTS.md` and append `templates/CODEX_SYSTEM_PROMPT_ADDITION.md`.
   - For manager role, write `.mind/actors/ACTOR_Manager.md` using actor template.
3. Initialize `...mind/state/SYNC_Project_State.md` with current state.
4. (Optional) Create `docs/` and add module docs as needed.

---

## ALGORITHM: Agent Starts Task

1. Read bootstrap: `.mind/CLAUDE.md` (or root `AGENTS.md`), then `.mind/PROTOCOL.md`.
2. Identify task type and select the matching VIEW.
3. Read the VIEW and load required context (SYNC, module docs).
4. Execute work.
5. Update SYNC files and any affected docs.

---

## ALGORITHM: Create New Module

1. Create `docs/{area}/{module}/`.
2. Write PATTERNS first (copy from template).
3. Write SYNC (copy from template).
4. Implement code and add DOCS reference to the header.
5. Add BEHAVIORS/ALGORITHM/VALIDATION/TEST as needed.
6. Update project SYNC.

---

## ALGORITHM: Modify Existing Module

1. Read PATTERNS and SYNC for the module.
2. Verify change fits the design (or update PATTERNS with justification).
3. Implement the change.
4. Update BEHAVIORS/ALGORITHM/VALIDATION if applicable.
5. Always update module SYNC and project SYNC.

---

## ALGORITHM: Document Cross-Cutting Concept

1. Create `docs/concepts/{concept}/`.
2. Write CONCEPT and TOUCHES using templates.
3. Reference the concept in each module that uses it.

---

## NOTES

Data flow and structure diagrams live in the IMPLEMENTATION docs.
