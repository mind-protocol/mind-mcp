# SYNC: Project Health Doctor

```
LAST_UPDATED: 2025-12-21
UPDATED_BY: codex (prompt health integration)
STATUS: CANONICAL
```

---

## CURRENT STATE

Doctor command implemented and working.

The command provides holistic project health analysis beyond pass/fail validation. Checks for:
- Monolith files (>500 lines by default)
- Undocumented code directories
- Stale SYNC files (>14 days by default)
- Placeholder docs (template markers)
- Missing DOCS: references (info only)
- Incomplete doc chains
- Doc template drift (missing or short sections vs templates)
- Non-standard doc type filenames
- Doc template drift supports escalation tags to capture human questions.
- Doctor now flags resolved escalation markers so they get applied and removed.
- Escaped marker references in BEHAVIORS to avoid triggering escalation scans.
- Special marker detection now includes `@mind&#58;todo` entries for task triage.
- Doc-link integrity and code-doc delta coupling checks now guard the prompt doc chain and flagged 27 doc-link + 3 code-doc delta warnings (see `...mind/state/SYNC_Project_Health.md`).
 - Implementation docs now explicitly list each doctor, repair, repo-overview, solve, and TUI code path mentioned by the latest doctor scan so the doc-link integrity check can anchor back to this module.
- Incomplete-implementation detection now treats stub-only bodies (pass/return None/NotImplemented) as incomplete while allowing concise return-based helpers.
- Stub-only detection now evaluates every function boundary (including end-of-file) to avoid false positives on short helpers.
- Large doc module threshold increased by 25% (62.5K chars) to reduce noisy warnings for moderately sized modules.

Features:
- Text and JSON output
- Severity filtering (--level)
- .gitignore pattern support
- Configurable thresholds via config.yaml
- Smart default ignores (node_modules, .next, etc.)
- False positive suppression from doc metadata via `@mind:doctor:CHECK_TYPE_NAME:false_positive` entries under `UPDATED:`.
- Legacy doctor-ignore entries migrated into doc metadata tags.
- Added doc template drift and non-standard doc type checks with deferred/exception tags in doc metadata.

The latest `mind doctor --format json` run (see `/tmp/doctor_final.json`) reports zero `DOC_LINK_INTEGRITY` and `CODE_DOC_DELTA_COUPLING` issues for the prompt doc chain while still surfacing the pre-existing warnings (monolith limits, undocumented directories, template drift). This verifies that the targeted refactor removed the 27 doc-link and 3 coupling warnings without masking other alerts.

---

## IMPLEMENTATION ORDER

Suggested order based on dependencies:

1. **Configuration loader** — Other checks need thresholds
2. **Project discovery** — Finds files to check
3. **Individual checks** — Start with monolith, undocumented
4. **Aggregation & scoring** — Combine results
5. **Output formatters** — Text first, then JSON
6. **CLI integration** — Wire into click
7. **Guided remediation** — `--guide` flag

---

## HANDOFF: FOR AGENTS

**Likely VIEW:** VIEW_Implement

**To implement:**
1. Read ALGORITHM doc for pseudocode
2. Add `doctor` command to cli.py
3. Create `doctor.py` module for checks
4. Follow existing CLI patterns (click decorators, Path handling)

**Key decisions already made:**
- Monolith threshold: 500 lines default
- Stale SYNC threshold: 14 days default
- Score deductions: critical=-10, warning=-3, info=-1

**Watch out for:**
- Don't count lines in binary files
- Handle permission errors gracefully
- Sort file traversal for determinism

---

## HANDOFF: FOR HUMAN

**Summary:** Doctor command fully designed. Docs specify checks, output format, configuration, and testing approach. Ready for implementation.

**Decisions to review:**
- Threshold defaults (500 lines, 14 days) — adjust?
- Severity assignments — anything miscategorized?
- Missing checks — anything else worth detecting?

---

## GAPS

- Completed: Reviewed `BEHAVIORS_Project_Health_Doctor.md` and module SYNC for escalation/conflict markers.
- Remaining: No conflicts or escalation markers found to resolve for this module.
- Blocker: Repair task references a decisionless escalation; needs confirmation of the intended conflict or missing marker.
- Observation: The latest `mind doctor` run reports zero doc-link integrity or code-doc delta coupling issues for the prompt/doc refactor; splitting `runtime/doctor_checks.py` into dedicated core/reference/stub/metadata/prompt-integrity modules also resolved the monolith warning while the remaining alerts now stem from template drift and metadata gaps.

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Project_Health_Doctor.md
BEHAVIORS:       ./BEHAVIORS_Project_Health_Doctor.md
ALGORITHM:       ./ALGORITHM_Project_Health_Doctor.md
VALIDATION:      ./VALIDATION_Project_Health_Doctor.md
IMPLEMENTATION:  ./IMPLEMENTATION_Project_Health_Doctor.md
HEALTH:          ./HEALTH_Project_Health_Doctor.md
THIS:            SYNC_Project_Health_Doctor.md
```


---

## ARCHIVE

Older content archived to: `SYNC_Project_Health_Doctor_archive_2025-12.md`
