# CLI Prompt — Health: Runtime verification of bootstrap guidance

@mind:id: CLI.PROMPT.HEALTH

```
STATUS: DESIGNING
CREATED: 2025-12-21
```

---

## PURPOSE OF THIS FILE

This HEALTH doc verifies that `mind prompt` remains a reliable launchpad for agents. It guards correctness (all sections present), traceability (doc paths match canonical files), and handoffs (the checklist forces agents to update SYNC).

---

## WHY THIS PATTERN

Prompts can drift even when the CLI doesn't change; sections may be removed, doc paths updated, or VIEW tables misaligned. The health check monitors the runtime prompt output without touching implementation code.

---

## HOW TO USE THIS TEMPLATE

1. Read PATTERNS → BEHAVIORS → ALGORITHM to understand what the prompt must include.
2. Identify the flows that `mind prompt` exercises and select dock points (stdout, docs, SYNC).
3. Map those flows to validation invariants and desired indicators.
4. Run `mind doctor` or the manual scripts below before certifying a health update.

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Prompt_Command_Workflow_Design.md
BEHAVIORS:       ./BEHAVIORS_Prompt_Command_Output_and_Flow.md
ALGORITHM:       ./ALGORITHM_Prompt_Bootstrap_Prompt_Construction.md
VALIDATION:      ./VALIDATION_Prompt_Bootstrap_Invariants.md
IMPLEMENTATION:  ./IMPLEMENTATION_Prompt_Code_Architecture.md
THIS:            HEALTH_Prompt_Runtime_Verification.md
SYNC:            ./SYNC_Prompt_Command_State.md

IMPL:            mind/prompt.py ➜ generate_bootstrap_prompt()
```

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: prompt_construction
    purpose: Ensure bootstrap prompt outputs canonical doc pointers and instructions
    triggers:
      - type: cli
        source: mind.cli:print_bootstrap_prompt
        notes: Triggered when humans invoke `mind prompt`
    frequency:
      expected_rate: 1/day
      peak_rate: 5/min
      burst_behavior: Human-invoked
    risks:
      - V1: Missing doc references → agent direction fails
      - V2: VIEW table stale → wrong VIEW chosen
    notes: Validate per release or after CLI doc updates and log manual reviews in SYNC.
```

---

## HEALTH INDICATORS SELECTED

```yaml
health_indicators:
  - name: prompt_doc_reference_check
    flow_id: prompt_construction
    priority: high
    rationale: Agents rely on canonical doc pointers before touching files.
  - name: prompt_view_table_check
    flow_id: prompt_construction
    priority: med
    rationale: VIEW misalignment sends agents to incorrect instructions.
  - name: prompt_checklist_presence_check
    flow_id: prompt_construction
    priority: med
    rationale: Checklist reminds agents to update SYNC; missing it invites regressions.
```

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: ...mind-mcp/state/SYNC_Prompt_Command_State.md
  result:
    representation: binary
    value: 1
    updated_at: 2025-12-21T00:00:00Z
    source: mind doctor (prompt health instrumentation)
```

---

## DOCK TYPES (COMPLETE LIST)

- `cli` — `mind prompt` stdout includes doc sections, VIEW table, and checklist.
- `file` — Canonical docs referenced (e.g., `.mind-mcp/PROTOCOL.md`, `.mind-mcp/views/*.md`).
- `state` — `...mind-mcp/state/SYNC_Prompt_Command_State.md` records health verification outcomes.

---

## CHECKER INDEX

```yaml
checkers:
  - name: prompt_doc_reference_check
    purpose: Confirm required doc paths appear in the prompt output
    status: active
    priority: high
  - name: prompt_view_table_check
    purpose: Confirm the VIEW table renders each entry defined by the algorithm doc
    status: active
    priority: med
  - name: prompt_checklist_presence_check
    purpose: Ensure the final checklist block exists referencing SYNC reminders
    status: active
    priority: med
```

---

## HEALTH SIGNAL MAPPING

| Signal | Maps to invariant | Docking point | Description |
|--------|------------------|---------------|-------------|
| `prompt_doc_reference_check` | V1: canonical docs appear (`VALIDATION_Prompt_Bootstrap_Invariants.md`) | `dock_docs` | Ensures `generate_bootstrap_prompt()` still emits the canonical protocol and state references. |
| `prompt_view_table_check` | V2: Every `.mind-mcp/views/` entry appears | `dock_view_table` | Confirms the VIEW table still renders the authoritative rows defined by the ALGORITHM doc. |
| `prompt_checklist_presence_check` | V3: prompt ends with `### Checklist` and SYNC reminder | `dock_checklist` | Validates the final checklist block that asks agents to update SYNC remains. |

---

## VERIFICATION RESULTS

- `prompt_doc_reference_check`: PASS — `python3 - <<'PY'` confirmed `generate_bootstrap_prompt(Path('.'))` still emits `.mind-mcp/PROTOCOL.md`, `.mind-mcp/PRINCIPLES.md`, and `...mind-mcp/state/SYNC_Project_State.md`, and `mind doctor --format json` reported zero `DOC_LINK_INTEGRITY` issues for the prompt doc chain (`doc_link count 0`).
- `prompt_view_table_check`: PASS — the same script verified the prompt still renders the canonical `| Task | VIEW |` table described in the algorithm doc, so each view entry remains visible to agents.
- `prompt_checklist_presence_check`: PASS — `### Checklist` is still present in prompt output, and `mind doctor --format json` did not raise any checklist-related warnings.

---

## INDICATOR: Prompt Doc Reference Health

- **Purpose:** Track that canonical protocol docs are present in the prompt output.
- **Dock:** `dock_docs` (stdout string) and `...mind-mcp/state/SYNC_Project_State.md`.
- **Validation:** `VALIDATION_Prompt_Bootstrap_Invariants.md` V1-V2.

## INDICATOR: Prompt Checklist Presence

- **Purpose:** Ensure checklist reminder stays so agents update SYNC before proceeding.
- **Dock:** `dock_checklist`.
- **Validation:** `VALIDATION_Prompt_Bootstrap_Invariants.md` V3.

---

## HOW TO RUN

```bash
mind prompt > /tmp/prompt_output.txt
python3 - <<'PY'
from mind.prompt import generate_bootstrap_prompt
print(generate_bootstrap_prompt())
PY
mind doctor --format json > /tmp/doctor_prompt.json
```

## KNOWN GAPS

<!-- @mind:todo No automated parser currently compares `mind prompt` output to the canonical doc list defined in the PATTERNS doc. -->
<!-- @mind:todo VIEW table detection still relies on string matching; future work should parse rows to ensure new VIEW entries aren't missed. -->

---

## MARKERS

<!-- @mind:todo Triaged the doc-link integrity and code-doc delta warnings emitted by `mind doctor` and promoted the highest-priority follow-ups to `...mind-mcp/state/SYNC_Project_Health.md`. -->
<!-- @mind:proposition Save the last prompt output snapshot under `.mind-mcp/traces/` for audit and doc-link validation. -->
<!-- @mind:escalation Should prompt health metrics feed into the CLI health dashboard or the doc-link metrics aggregated by doctor? -->
