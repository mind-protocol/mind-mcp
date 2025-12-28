# Tools — Health: Verification

```
STATUS: DESIGNING
CREATED: 2025-12-20
UPDATED: 2025-12-21
```

---

## PURPOSE OF THIS FILE

This document names the health flows, indicators, and checkers that keep the Tools module reliable and docked to the protocol. It shows how the network of scripts, documentation, and fixtures is verified so DOC_TEMPLATE_DRIFT warnings know exactly which sections to inspect before any release.

By keeping the coverage narrative in one place, future agents do not need to reconstruct the health contract from `mind doctor` logs; they can follow this checklist to prove the module remains coherent and mapped.

---

## WHY THIS PATTERN

The pattern exists because utility scripts are inherently lightweight yet critical for system hygiene, so their health signal must live outside the code so no automation pipeline ever overlooks them. By explicitly listing flows, docks, and indicators the pattern prevents missing sections from causing rifts between the documentation and the `mind doctor` diagnostics.

This lens also forces us to refresh the tools doc chain immediately when new scripts or fixtures appear, keeping the module aligned with the one-solution-per-problem principle.

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Tools.md
BEHAVIORS:       ./BEHAVIORS_Tools.md
ALGORITHM:       ./ALGORITHM_Tools.md
VALIDATION:      ./VALIDATION_Tools.md
IMPLEMENTATION:  ./IMPLEMENTATION_Tools.md
THIS:            ./HEALTH_Tools.md
SYNC:            ./SYNC_Tools.md
```

> **Contract:** Health checks govern the tooling docs, fixture runners, and doctor alignment so that each utility remains documented and verified before another agent depends on it.

---

## HOW TO USE THIS TEMPLATE

- Start by reviewing the `FLOWS ANALYSIS` block to understand why each trigger exists and how frequently it should fire before you touch any doc or script.
- Refer to `HEALTH INDICATORS SELECTED` and follow the `CHECKER INDEX` to map your work to a measurable signal, then describe the dock types you touched.
- Update the `INDICATOR:` sections whenever you add a new health metric so operators always know the exact validations and representations behind the score.

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: tool_catalog_reconciliation
    purpose: Keep documentation, fixtures, and doctor coverage aligned whenever tools or supporting scripts change.
    triggers:
      - type: template_drift
        source: DOC_TEMPLATE_DRIFT warnings targeting docs/tools/HEALTH_Tools.md
        notes: Fires whenever mandatory headings are missing or under-length, so the template remains complete.
      - type: code_change
        source: tools/**
        notes: Fires when a script is added or altered, ensuring the documentation and fixtures catch up immediately.
    frequency:
      expected_rate: 2/month
      peak_rate: 1/week during repair sprints
      burst_behavior: Each flow run re-executes `mind doctor` plus fixture runners so the indicator table stays weighted by real checks.
    risks:
      - Forgetting to document a new script so the doctor still flags the module as incomplete.
      - Running `mind doctor` without the latest fixtures, causing false positives on doctored checks.
```

---

## HEALTH INDICATORS SELECTED

```yaml
health_indicators:
  - name: tool_doc_completeness
    flow_id: tool_catalog_reconciliation
    priority: high
    rationale: Ensures every mandatory section of this template exists and exceeds the 50-character guidance so the doctor stops warning about drift.
  - name: tool_execution_consistency
    flow_id: tool_catalog_reconciliation
    priority: medium
    rationale: Confirms the fixture-backed scripts still run without errors in the same environment that the doc references.
```

---

## OBJECTIVES COVERAGE

| Objective | Indicators | Why These Signals Matter |
|-----------|------------|---------------------------|
| Keep the Tools module officially mapped so new and existing utilities remain discoverable and documented. | tool_doc_completeness | Without this coverage, new scripts can slip through the protocol gaps and trigger DOC_TEMPLATE_DRIFT warnings for downstream agents. |
| Guarantee the documented scripts execute cleanly with their fixtures so references remain trustworthy. | tool_execution_consistency | Running the scripts after doc updates proves the module does more than just look correct on paper. |

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: doctor_logs
  result:
    representation: float_0_1
    value: 0.91
    updated_at: 2025-12-21T12:00:00Z
    source: tool_catalog_reconciliation_run
    notes: Aggregates the completeness of the health template and the success stories from fixture-backed executions.
```

---

## DOCK TYPES (COMPLETE LIST)

- `tools_manifest` (input) — Code and doc globs listed in `modules.yaml` that the doctor uses to validate coverage.
- `documentation_frames` (input/output) — The Markdown files inside `docs/tools/` that must present the template headings and tables.
- `execution_fixtures` (input) — Example inputs stored near each script that prove the script runs deterministically.
- `doctor_report` (output) — The `mind doctor` JSON payload that confirms or denies template drift for this module.
- `health_banner` (output) — The CLI/doctor banner that surfaces the 50+ character compliance state before the agent proceeds.

---

## CHECKER INDEX

```yaml
checkers:
  - name: doctor_alignment_checker
    purpose: Verifies `mind doctor` reports zero DOC_TEMPLATE_DRIFT warnings after the Tools health doc is updated.
    status: active
    priority: high
  - name: script_fixture_runner
    purpose: Executes each documented script with its fixture inputs to surface runtime failures that the docs are guarding against.
    status: active
    priority: medium
  - name: doc_link_checker
    purpose: Ensures every tool mentioned in the health doc appears in the module manifest or implementation tree so nothing is undocumented.
    status: pending
    priority: medium
```

---

## INDICATOR: tool_doc_completeness

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: tool_doc_completeness
  client_value: Flags the completion of every template section so downstream agents can trust the health narrative without rerunning the doc manually.
  validation:
    - validation_id: DOC_TEMPLATE_DRIFT-TOOLS
      criteria: `docs/tools/HEALTH_Tools.md` must include PURPOSE, WHY, FLOWS, INDICATORS, OBJECTIVES, STATUS, DOCKS, CHECKERS, INDICATOR narratives, HOW TO RUN, and GAP sections that each exceed 50 characters.
```

### DOCKS SELECTED

```yaml
docks:
  input:
    id: documentation_frames
    method: Markdown updates in docs/tools/
  output:
    id: doctor_report
    method: `mind doctor --format json` reporting template drift for this doc
```

### HEALTH REPRESENTATION

```yaml
representation:
  allowed:
    - float_0_1
  selected:
    - float_0_1
semantics:
  float_0_1: Ratio of fully populated template sections to the total number of mandatory sections plus indicator narratives.
  aggregation:
    method: Minimum of the completion ratios so a single missing section flags the health score.
    display: The clinic banner in doctor logs and the CLI health summary whenever the ratio drops below 0.75.
```

### ALGORITHM / CHECK MECHANISM

```yaml
mechanism:
  summary: After editing the docs, run `mind doctor --format json` and confirm `DOC_TEMPLATE_DRIFT` no longer references this file; failing sections are listed verbatim so the indicator drops below 1.0 if anything is missing.
```

---

## INDICATOR: tool_execution_consistency

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: tool_execution_consistency
  client_value: Builds confidence that the scripts stay runnable, so even tooling intended for ops remains safe to execute from the repository.
  validation:
    - validation_id: TOOL_FIXTURE_RUN
      criteria: Each script referenced in docs/tools/ runs against its fixture from the last commit without fatal errors.
```

### DOCKS SELECTED

```yaml
docks:
  input:
    id: modules_manifest
    method: modules.yaml mapped to tools/**
  output:
    id: execution_fixtures
    method: fixture execution traces stored in `.mind-mcp/logs/` or `logs/run_stack`
```

### HEALTH REPRESENTATION

```yaml
representation:
  allowed:
    - float_0_1
  selected:
    - float_0_1
semantics:
  float_0_1: Ratio of successful fixture runs versus total documented scripts, so flaky or missing fixtures drag the score.
  aggregation:
    method: Average across script families so a single script failure becomes visible in the indicator log.
    display: Doctor Banner and `logs/run_stack/health.log` entries.
```

### ALGORITHM / CHECK MECHANISM

```yaml
mechanism:
  summary: Automate running each fixture-backed script (or manual invocation for complex helpers), check the exit code, and capture stdout/stderr plus fixture expectations for future diffing.
```

---

## HEALTH CHECKS

- Run `mind doctor --scope tools --format json` to ensure template drift warnings are resolved and the indicator table stays above 0.8.
- Execute each fixture-backed script (for example, `tools/run_stack.sh --help` and any other scripts called out here) and capture logs under `.mind-mcp/logs/doctor`.
- Review the indicator sections before making further documentation changes so you can point at the exact validation ID that will update the health banner.

---

## HOW TO RUN

1. `cd /home/mind-protocol/mind`
2. `mind validate` (guarantees module mappings still pass after doc edits).
3. `mind doctor --scope tools --format json` to check for lingering template drift or missing CHAIN links.
4. Run each script referenced in `docs/tools/` with its fixture and direct output into `.mind-mcp/logs/doctor`.
5. Inspect `logs/run_stack` (if populated) to confirm helper scripts still start the expected services and report no errors.

---

## KNOWN GAPS

- No canonical fixtures exist for several helper scripts, so the execution indicator currently depends on manual verification notes.
- The `doc_link_checker` remains pending because it needs last-mile wiring to map doc references to actual script paths.

---

## MARKERS

<!-- @mind:todo Add per-script fixture directories and README excerpts so future runs can be automated rather than relying on manual runs described here. -->
<!-- @mind:todo Surface a canonical list of `tools/` scripts in `docs/tools/OBJECTIVES_Tools_Goals.md` so the health doc can cite it directly instead of repeating the names. -->
- What additional metrics should the doctor log to prove script execution consistency beyond exit codes?
