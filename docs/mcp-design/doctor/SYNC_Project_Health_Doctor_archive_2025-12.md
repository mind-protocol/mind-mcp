# Archived: SYNC_Project_Health_Doctor.md

Archived on: 2025-12-29
Original file: SYNC_Project_Health_Doctor.md

---

## MATURITY

**What's canonical (v1):**
- CLI command: `mind doctor`
- Output formats: text, JSON
- Level filtering: --level critical/warning/all
- Configuration via config.yaml
- .gitignore pattern support
- Checks: monolith, undocumented, stale_sync, placeholder, no_docs_ref, incomplete_chain
- Default ignores: node_modules, .next, dist, build, vendor, __pycache__, etc.
- Health score: 0-100
- Doc-link integrity and code-doc delta coupling checks as defined in `docs/cli/prompt/HEALTH_Prompt_Runtime_Verification.md`

**What's documented but not implemented (v2):**
- check_activity_gaps - No SYNC updates in N days
- check_abandoned - Docs started but never completed
- check_vague_names - Files named utils, helpers, misc, etc.
- `--guide` remediation mode
- Markdown output format

---


## TODO

### Immediate

- [x] Expand `docs/mcp-design/doctor/IMPLEMENTATION_Project_Health_Doctor.md` so it explicitly mentions `runtime/doctor.py` and the doctor checks modules, restoring the bidirectional link for the doc-link warnings.
- [x] Add IMPL references for `runtime/repair_*`, `runtime/repo_overview*`, `runtime/solve_escalations.py`, and the flagged `runtime/tui/*` files inside the relevant CLI implementation docs so their doc-link issues clear.
- [x] Update `docs/mcp-design/doctor/SYNC_Project_Health_Doctor.md` and `docs/cli/prompt/SYNC_Prompt_Command_State.md` with the latest code changes so the `CODE_DOC_DELTA_COUPLING` warnings disappear after rerunning `mind doctor` (verified by `mind doctor --format json` showing zero doc-link/coupling issues).

### Implemented (v1)

- [x] Configuration loader (config.yaml support)
- [x] Project discovery functions
- [x] check_monolith
- [x] check_undocumented
- [x] check_stale_sync
- [x] check_placeholder_docs
- [x] check_no_docs_ref
- [x] check_incomplete_chain
- [x] Result aggregation
- [x] Score calculation
- [x] Text output formatter
- [x] JSON output formatter
- [x] CLI command integration
- [x] Auto-save to HEALTH.md
- [x] prompt_doc_reference_check, prompt_view_table_check, prompt_checklist_presence_check
- [x] doc_link_integrity
- [x] code_doc_delta_coupling

### To Implement (v2)

<!-- @mind:todo check_activity_gaps - No SYNC updates in N days across project -->
<!-- @mind:todo check_abandoned - Docs started but never completed -->
<!-- @mind:todo check_vague_names - Files named utils, helpers, misc, etc. -->
<!-- @mind:todo `--guide` remediation mode -->

### Future Ideas

<!-- @mind:proposition `--fix` mode that auto-creates missing docs -->
<!-- @mind:proposition `--watch` mode for continuous health monitoring -->
<!-- @mind:proposition Health score badge for README -->
<!-- @mind:proposition Integration with CI (GitHub Actions template) -->
<!-- @mind:proposition Trend tracking (score over time) -->

---


## NEW MARKERS (2025-12-29 Review)

<!-- @mind:escalation
title: "Documented features NOT implemented in v1"
priority: 3
context: |
  BEHAVIORS doc describes features that are NOT implemented:
  - `mind doctor --guide <path>` remediation mode
  - `mind doctor --check <checkname>` specific check filter
  - `mind doctor --format markdown` output format
  These are documented as if available but don't exist in code.
question: |
  Should these be:
  a) Implemented to match documentation
  b) Documentation updated to remove unimplemented features
  c) Moved to "v2 roadmap" section
-->

<!-- @mind:proposition
title: "doctor/ docs should live under docs/cli/"
suggestion: |
  The doctor command is a CLI feature. Its documentation chain
  (PATTERNS, BEHAVIORS, ALGORITHM, etc.) should be at:
  docs/cli/doctor/ rather than docs/mcp-design/doctor/

  This aligns with the pattern: module docs live in docs/{area}/{module}/
  where area=cli and module=doctor.
-->

---

