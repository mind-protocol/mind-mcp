# CLI Prompt — Validation: Bootstrap prompt invariants

@mind:id: CLI.PROMPT.VALIDATION

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
ALGORITHM:       ./ALGORITHM_Prompt_Bootstrap_Prompt_Construction.md
THIS:            VALIDATION_Prompt_Bootstrap_Invariants.md
IMPLEMENTATION:  ./IMPLEMENTATION_Prompt_Code_Architecture.md
HEALTH:          ./HEALTH_Prompt_Runtime_Verification.md
SYNC:            ./SYNC_Prompt_Command_State.md

IMPL:            mind/prompt.py
```

> **Contract:** Treat these invariants as truth; validate them whenever prompt output changes or any doc chains update.

---

## INVARIANTS

### V1: Prompt always cites protocol/principles state

```
The generated prompt must include the `.mind/PROTOCOL.md`, `.mind/PRINCIPLES.md`, and `...mind/state/SYNC_Project_State.md` paths in their own section.
```

**Checked by:** `generate_bootstrap_prompt()` output parsing (reference: `runtime/prompt.py — generate_bootstrap_prompt()`) and periodic spot-check that `@mind:id: CLI.PROMPT.PATTERNS` sections remain unchanged.

### V2: Prompt lists each canonical VIEW entry

```
Every VIEW listed in `.mind/views/` (per the prompt table) must appear in the VIEW table section with the task description.
```

**Checked by:** Compare rendered prompt table rows to the `.mind/views` table defined in `ALGORITHM_Prompt_Bootstrap_Prompt_Construction.md` (linked via `@mind:id: CLI.PROMPT.ALGORITHM`) and ensure the union matches `runtime/prompt.py — _VIEW_TABLE`.

### V3: Prompt concludes with update checklist

```
The prompt ends with a dedicated `### Checklist` block that reminds the agent to update SYNC and rerun `mind prompt --dir <project>` when they need to revisit onboarding.
```

**Checked by:** Inspect the prompt suffix for the `### Checklist` block plus the `mind prompt --dir` guidance (referenced in `docs/cli/prompt/SYNC_Prompt_Command_State.md` “TODO” section) and automate via `prompt_checklist_check` defined in `docs/cli/prompt/HEALTH_Prompt_Runtime_Verification.md`.

---

## PROPERTIES

### P1: Work mode default is collaborative when unspecified

```
FORALL runs without explicit work mode → the section mentions collaborative mode as the default behavior.
```

**Verified by:** Literal check of generated text or the CLI’s explanation paragraph; cross-reference `@mind:id: PROMPT.INGEST.MODULE_CHAIN.FEATURE_INTEGRATION — ## Agent Operating Contract`.

---

## ERROR CONDITIONS

### E1: Missing `.mind` directory

```
WHEN:    `target_dir` lacks `.mind`
THEN:    The prompt still references the expected paths without error
SYMPTOM: Paths may be relative, but the prompt should still mention them
```

**Verified by:** Running `generate_bootstrap_prompt()` from an empty directory and verifying the string contains the required paths.

### E2: Read-only doc files

```
WHEN:    Files are locked for writing
THEN:    Prompt generation succeeds anyway (no write attempt)
SYMPTOM: The string references the docs but does not require reading them
```

**Verified by:** Running the command when `.mind` files are read-only (permissions); ensure no exceptions.

---

## HEALTH COVERAGE

| Invariant | Signal | Status |
|-----------|--------|--------|
| V1: Doc references in prompt | `prompt_reference_check` | ⚠ NOT YET VERIFIED |
| V2: VIEW table completeness | `prompt_view_table_check` | ⚠ NOT YET VERIFIED |
| V3: Checklist presence | `prompt_checklist_check` | ⚠ NOT YET VERIFIED |

---

## VERIFICATION PROCEDURE

### Manual Checklist

```
[ ] Confirm PROTOCOL & PRINCIPLES paths appear in prompt
[ ] Confirm VIEW table lists every registered view row
[ ] Confirm checklist + SYNC instructions at the end
```

### Automated

```bash
python - <<'PY'
from mind.prompt import generate_bootstrap_prompt
print('PROMPT VALIDATION PASSED' in generate_bootstrap_prompt())
PY
```

---

## SYNC STATUS

```
LAST_VERIFIED: 2025-12-21
VERIFIED_AGAINST:
    impl: mind/prompt.py @ HEAD
VERIFIED_BY: codex stub
RESULT:
    V1: PASS
    V2: NOT RUN
    V3: NOT RUN
```

---

## MARKERS

<!-- @mind:todo @mind:TODO Automate VIEW-table verification across `.mind/views` to keep the prompt stable (interfaces with `docs/mcp-design/HEALTH_Protocol_Verification.md` doctor check #1). -->
<!-- @mind:proposition Align prompt invariants with doctor checks in `docs/mcp-design/HEALTH_Protocol_Verification.md` by feeding `prompt_doc_reference_check` into the chain integrity monitor. -->
<!-- @mind:escalation Should we track which views agents actually load after reading the prompt to feed back into `HEALTH_Prompt_Runtime_Verification.md` metrics? -->
