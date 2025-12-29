# BEHAVIORS: Project Health Doctor

**Observable effects of the doctor command.**

---

## COMMAND INTERFACE

```bash
# Basic health check
mind doctor

# With specific directory
mind doctor --dir /path/to/project

# Output formats
mind doctor --format text     # Human readable (default)
mind doctor --format json     # Machine readable
mind doctor --format markdown # For reports

# Filter by severity
mind doctor --level critical  # Only critical issues
mind doctor --level warning   # Critical + warnings
mind doctor --level all       # Everything (default)

# Specific checks
mind doctor --check monolith
mind doctor --check stale
mind doctor --check undocumented
```

---

## HEALTH CHECKS

The doctor performs various checks across documentation, code, and project structure:

- **Naming Conventions** (NEW)
    - Flags directories and code files not using `snake_case`.
    - Flags code files containing `and` in their name (suggests multiple responsibilities).
    - Flags doc files not using `PREFIX_PascalCase_With_Underscores.md`.
    - Groups violations into tasks of 10 items for organized refactoring.

- **Monolith Files**
    - Flags files exceeding line count thresholds (default: 500 for code, 1000 for docs).

- **Documentation Health**
    - **Undocumented Code**: Modules without mappings in `modules.yaml`.
    - **Incomplete Chains**: Missing required doc types (PATTERNS, SYNC, etc.).
    - **Doc Template Drift**: Docs missing sections from templates or with very short content.
    - **Placeholder Docs**: Files containing template placeholders like `{TODO}`.
    - **Non-Standard Doc Type**: Doc files missing standard prefixes.

- **Code Health**
    - **No DOCS: Reference**: Code files missing headers pointing to their documentation.
    - **Broken Implementation Links**: Implementation docs referencing non-existent files.
    - **Stub/Incomplete Implementations**: Files with many TODOs or empty functions.

- **Sync and Workflow**
    - **Stale SYNC**: SYNC files not updated recently.
    - **Special Markers**: Detects `@mind&#58;escalation`, `@mind&#58;proposition`, and `@mind&#58;todo` markers in code and docs.
    - **Activity Gaps**: Long periods without any project activity.

---

## SPECIAL MARKERS

The doctor scans the entire project for special markers that require human attention:

- **@mind&#58;escalation**
    - **Type**: `ESCALATION`
    - **Severity**: `warning`
    - **Purpose**: Signals a blocker or conflict that requires a human decision.
    - **Action**: Use `mind solve-markers` to review and resolve.

- **@mind&#58;proposition**
    - **Type**: `PROPOSITION`
    - **Severity**: `info`
    - **Purpose**: Agent-suggested improvements, refactors, or new features.
    - **Action**: Use `mind solve-markers` to review suggested changes.

- **@mind&#58;todo**
    - **Type**: `TODO`
    - **Severity**: `info`
    - **Purpose**: Track tasks captured by agents or managers for later execution.
    - **Action**: Use `mind solve-markers` to triage and assign tasks.

Markers in `templates/` and `views/` directories are intentionally ignored to avoid false positives from framework documentation.

---

## OUTPUT BEHAVIOR

### Text Format (Default)

```
🏥 Project Health Report: my-project
=====================================

## Critical (2 issues)

  ✗ MONOLITH: src/game/combat.ts
    847 lines (threshold: 500)
    → Consider splitting into combat/attack.ts, combat/defense.ts, combat/damage.ts

  ✗ UNDOCUMENTED: src/api/
    No documentation exists for this code directory
    → Run: mind doctor --guide src/api/
    → See: VIEW_Document_Create_Module_Documentation.md

## Warnings (3 issues)

  ⚠ STALE_SYNC: docs/vision/SYNC_Vision_State.md
    Last updated 23 days ago, 47 commits since
    → Review and update SYNC with current state

  ⚠ NO_DOCS_REF: src/types/game.ts
    Code file has no DOCS: reference comment
    → Add: # DOCS: docs/types/PATTERNS_*.md

  ⚠ INCOMPLETE_CHAIN: docs/auth/
    Missing: HEALTH_*.md
    → Create TEST doc or mark as intentionally skipped

## Info (3 issues)

  ℹ ACTIVITY_GAP: .mind/
    No SYNC updates in 18 days
    → Review project state and update relevant SYNC files

  ℹ ABANDONED: docs/auth/
    Started 45 days ago, only has PATTERNS, SYNC
    → Either complete documentation or remove if no longer relevant

  ℹ VAGUE_NAME: src/utils.ts
    File named 'utils.ts' is non-descriptive
    → Consider naming by what it actually does (e.g., string_helpers, date_formatters)

─────────────────────────────────────
Health Score: 64/100
Critical: 2 | Warnings: 3 | Info: 3
─────────────────────────────────────

## Suggested Actions

1. [ ] Split src/game/combat.ts (Critical)
2. [ ] Document src/api/ (Critical)
3. [ ] Update docs/vision/SYNC_Vision_State.md (Warning)
4. [ ] Add DOCS: ref to src/types/game.ts (Warning)

Run `mind doctor --guide <path>` for detailed remediation.
```

### JSON Format

```json
{
  "project": "/path/to/project",
  "timestamp": "2025-12-16T10:30:00Z",
  "score": 67,
  "issues": {
    "critical": [
      {
        "type": "MONOLITH",
        "path": "src/game/combat.ts",
        "details": {
          "lines": 847,
          "threshold": 500
        },
        "suggestion": "Split into smaller modules"
      }
    ],
    "warning": [...],
    "info": [...]
  },
  "summary": {
    "critical": 2,
    "warning": 3,
    "info": 1
  }
}
```

---

## GUIDED REMEDIATION

```bash
mind doctor --guide src/api/
```

Outputs detailed steps for fixing a specific issue:

```
🔧 Remediation Guide: src/api/
==============================

Issue: UNDOCUMENTED
This code directory has no documentation.

## Current State
- 5 files in src/api/
- 423 total lines
- Main entry: index.ts

## Recommended Steps

1. Create documentation directory:
   mkdir -p docs/api/

2. Create minimum viable docs:
   - PATTERNS_Api_Design.md (why this API shape)
   - SYNC_Api_State.md (current status)

3. Add DOCS reference to main file:
   # DOCS: docs/api/PATTERNS_Api_Design.md

4. Update modules.yaml:
   api:
     code: "src/api/**"
     docs: "docs/api/"
     maturity: DESIGNING

5. Run validation:
   mind validate

## Template Commands

# Generate PATTERNS from template
mind doctor --scaffold PATTERNS docs/api/

## Reference
- VIEW: .mind/views/VIEW_Document_Create_Module_Documentation.md
```

---

## EXIT CODES

| Code | Meaning |
|------|---------|
| 0 | No critical issues |
| 1 | Critical issues found |
| 2 | Error running doctor |

Allows CI integration:
```bash
mind doctor --level critical || exit 1
```

---

## CONFIGURATION

`.mind/config.yaml`:

```yaml
doctor:
  # Thresholds
  monolith_lines: 500
  god_function_lines: 100
  stale_sync_days: 14
  designing_stuck_days: 21
  nesting_depth: 4

  # Ignore patterns
  ignore:
    - "src/generated/**"
    - "vendor/**"
    - "**/*.test.ts"

  # Disable specific checks
  disabled_checks:
    - circular_deps  # Too slow for large projects

  # Custom severity overrides
  severity_overrides:
    incomplete_chain: info  # Downgrade from warning
```

---

## FALSE POSITIVE SUPPRESSION

If a check is a false positive, the doctor ignores it when a linked doc declares it.

Add a line directly under the doc's `UPDATED: YYYY-MM-DD` metadata line:

`@mind:doctor:CHECK_TYPE_NAME:false_positive Explanation message`

The suppression applies when the issue's file references that doc via a `DOCS:` header, or when the issue targets that doc file directly.

---

## DOC TEMPLATE DRIFT DEFERMENTS

For the doc template drift check (`DOC_TEMPLATE_DRIFT`), you can defer or mark as non-required in the same metadata block:

`@mind:doctor:DOC_TEMPLATE_DRIFT:postponed YYYY-MM-DD Short explanation`
`@mind:doctor:DOC_TEMPLATE_DRIFT:non-required Short explanation`
`@mind:doctor:DOC_TEMPLATE_DRIFT:escalation Detailed choice/question/context for human`

If a postponed date is in the past, the issue is still reported.

---

## NON-STANDARD DOC TYPE DEFERMENTS

For the non-standard doc type check (`NON_STANDARD_DOC_TYPE`), you can defer or mark as exception:

`@mind:doctor:NON_STANDARD_DOC_TYPE:postponed YYYY-MM-DD Short explanation`
`@mind:doctor:NON_STANDARD_DOC_TYPE:exception Short explanation`

If a postponed date is in the past, the issue is still reported.

---

## RESOLVED ESCALATION MARKERS

Doctor flags any file containing `@mind:solved-escalations` (or `@mind:solved-escalation`) as `RESOLVE_ESCALATION` so resolved markers get applied and cleaned up.

---

## MARKER STANDARDIZATION

Metadata anchors themselves need a predictable format so the refactor tooling and doctor parser can treat every reference uniformly.

- `@mind:todo:postponed 2025-12-23 Establish `@mind:thing:docs/...` tagging and marker grammar before refactoring modules/areas.`

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Project_Health_Doctor.md
BEHAVIORS:       THIS
ALGORITHM:       ./ALGORITHM_Project_Health_Doctor.md
VALIDATION:      ./VALIDATION_Project_Health_Doctor.md
IMPLEMENTATION:  ./IMPLEMENTATION_Project_Health_Doctor.md
HEALTH:          ./HEALTH_Project_Health_Doctor.md
SYNC:            ./SYNC_Project_Health_Doctor.md
```
