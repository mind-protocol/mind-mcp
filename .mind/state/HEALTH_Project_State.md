# Project State — Health: Verification Mechanics

```
STATUS: CANONICAL
CREATED: 2026-03-15
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Project_State.md
BEHAVIORS:       ./BEHAVIORS_Project_State.md
VALIDATION:      ./VALIDATION_Project_State.md
THIS:            HEALTH_Project_State.md (you are here)
SYNC:            ./SYNC_Project_State.md

RELATED:         .mind/capabilities/sync-state/HEALTH.md (general SYNC freshness — H1 there covers all SYNC files)
```

---

## PURPOSE

Runtime health verification for `SYNC_Project_State.md` specifically. The general `sync-state` capability checks whether ANY SYNC file is stale. This HEALTH doc goes deeper: structural completeness, section content, MODULE COVERAGE accuracy, RECENT CHANGES bounds, and the V8 invariant (does CURRENT STATE actually describe mind-mcp?).

**What this file covers:** The 6 automatable invariants from VALIDATION_Project_State.md (V1, V2, V3, V4, V5, V9).

**What this file does NOT cover:** Content quality invariants (V6 handoff specificity, V7 additive safety, V8 repo correctness) — these require agent judgment, enforced by culture and VALIDATION, not code.

**Who relies on it:** Every agent that reads SYNC for orientation. If SYNC is structurally broken, agents waste sessions.

---

## WHY HEALTH, NOT TESTS

SYNC_Project_State.md is a living document, not a function with deterministic outputs. Its health degrades over time — sections go stale, MODULE COVERAGE drifts from reality, RECENT CHANGES accumulates unboundedly. Tests can't catch drift that happens between sessions. Health checks run periodically and surface decay before it compounds.

---

## IMPLEMENTS

```yaml
implements:
  runtime: .mind/capabilities/sync-state/runtime/checks.py  # General SYNC checks (H1 freshness)
  project_specific: manual agent verification + structural regex checks
  decorator: @check
```

> Project State health is partially automated (structural checks) and partially agent-enforced (content checks). The automated checks can be added to `sync-state/runtime/checks.py` or run as standalone scripts.

---

## INDICATORS

### H1: Structural Completeness (V1)

```yaml
name: sync_structure
priority: high
validation: V1 (Structural Completeness)

value: "All 10 required section headers present and non-empty"

representation:
  type: enum
  states: [OK, DEGRADED, CRITICAL]

mechanism: |
  1. Read .mind/state/SYNC_Project_State.md
  2. Parse for required section headers:
     - ## CURRENT STATE
     - ## KEY COMPONENTS
     - ## ACTIVE WORK
     - ## RECENT CHANGES
     - ## DEPLOYMENT
     - ## KNOWN ISSUES
     - ## HANDOFF: FOR AGENTS
     - ## HANDOFF: FOR HUMAN
     - ## TODO
     - ## MODULE COVERAGE
  3. Check LAST_UPDATED and UPDATED_BY fields exist and are non-empty
  4. For each section, verify at least 1 non-blank line of content follows the header

signals:
  healthy: All 10 headers present, all non-empty, frontmatter complete
  degraded: 1-2 sections missing or empty
  critical: 3+ sections missing, or LAST_UPDATED/UPDATED_BY missing

throttling:
  trigger: cron.daily or agent session start
  max_frequency: 1/day (automated) or 1/session (manual)

on_signal:
  degraded:
    action: Agent adds missing sections before other work
    problem: SYNC_INCOMPLETE
  critical:
    action: Full SYNC rewrite justified (B2 + E1)
    problem: SYNC_BROKEN
```

### H2: Temporal Freshness (V2)

```yaml
name: sync_freshness_project
priority: high
validation: V2 (Temporal Freshness)

value: "LAST_UPDATED within 24h of latest significant commit"

representation:
  type: enum
  states: [FRESH, STALE, ABANDONED]

mechanism: |
  1. Parse LAST_UPDATED from SYNC_Project_State.md
  2. Get date of latest significant commit (git log --oneline -1)
  3. Compute delta = commit_date - LAST_UPDATED
  4. FRESH: delta <= 24h
  5. STALE: 24h < delta <= 7d
  6. ABANDONED: delta > 7d

signals:
  healthy: FRESH — LAST_UPDATED is within 24h of latest significant commit
  degraded: STALE — 1-7 days behind. Next agent must update SYNC before other work (E3)
  critical: ABANDONED — >7 days behind. SYNC is untrustworthy, may need full audit

throttling:
  trigger: cron.daily + agent session start
  max_frequency: 1/day (automated)

on_signal:
  degraded:
    action: Next agent updates SYNC as first action (Behavior B2, Edge Case E3)
    problem: STALE_PROJECT_SYNC
  critical:
    action: Full audit — verify every section against codebase reality
    problem: ABANDONED_PROJECT_SYNC

note: >
  The general sync-state capability (H1 there) uses a 14-day threshold.
  Project State uses a stricter 24h threshold because it is the
  primary orientation doc — staleness here costs more than in module SYNCs.
```

### H3: RECENT CHANGES Bounded (V3)

```yaml
name: recent_changes_bounded
priority: medium
validation: V3 (RECENT CHANGES Truthfulness)

value: "RECENT CHANGES has at most 7 entries"

representation:
  type: binary
  display: "RECENT CHANGES: {count} entries ({ok|over_limit})"

mechanism: |
  1. Read SYNC_Project_State.md
  2. Find ## RECENT CHANGES section
  3. Count ### sub-headers within that section
  4. bounded = count <= 7

signals:
  healthy: count <= 7
  degraded: count > 7

throttling:
  trigger: On SYNC update
  max_frequency: 1/session

on_signal:
  degraded:
    action: Prune oldest entries (Behavior B7 — keep 5-7, remove entries >2 weeks old)
    problem: CHANGELOG_UNBOUNDED
```

### H4: MODULE COVERAGE Path Accuracy (V4)

```yaml
name: module_coverage_accuracy
priority: high
validation: V4 (MODULE COVERAGE Accuracy)

value: "All code paths in MODULE COVERAGE table exist on disk"

representation:
  type: tuple
  display: "{valid}/{total} paths resolve, {missing} phantom, {unlisted} undocumented"

mechanism: |
  1. Parse MODULE COVERAGE table from SYNC_Project_State.md
  2. For each row, extract the Code path column
  3. Check if path exists on disk (relative to repo root)
  4. Also scan for significant directories NOT in the table
  5. Report:
     - phantom: listed but path doesn't exist
     - unlisted: exists on disk but not in table

signals:
  healthy: All paths resolve, no unlisted modules
  degraded: Any phantom entries OR any unlisted modules
  critical: 3+ phantom entries (SYNC is seriously drifted)

throttling:
  trigger: cron.daily or on significant commit
  max_frequency: 1/day

on_signal:
  degraded:
    action: |
      Remove phantom entries (Behavior B4, Edge Case E4).
      Add unlisted modules (Behavior B5).
    problem: COVERAGE_DRIFT
```

### H5: KNOWN ISSUES Hygiene (V5)

```yaml
name: known_issues_hygiene
priority: medium
validation: V5 (KNOWN ISSUES Hygiene)

value: "No resolved issues still listed without Fixed marker"

representation:
  type: binary
  display: "KNOWN ISSUES: {clean|stale}"

mechanism: |
  1. Parse KNOWN ISSUES table from SYNC_Project_State.md
  2. For each entry without "Fixed" status:
     - Check if the issue description references a file/module
     - If file/module has been modified since the issue was logged, flag as potentially stale
  3. Report entries that may have been silently fixed

signals:
  healthy: All entries are current or explicitly marked Fixed
  degraded: Any entry appears resolved but unmarked

note: >
  This is heuristic, not definitive. File modification doesn't guarantee
  the issue is fixed. But it flags candidates for human/agent review.

throttling:
  trigger: cron.daily
  max_frequency: 1/day
```

### H6: TODO Bounds (V9)

```yaml
name: todo_bounds
priority: low
validation: V9 (TODO Reflects Reality)

value: "TODO list has <= 15 items, grouped by priority tier"

representation:
  type: binary
  display: "TODO: {count} items ({ok|bloated})"

mechanism: |
  1. Parse ## TODO section from SYNC_Project_State.md
  2. Count all list items (lines matching /^- \[/)
  3. Check for priority tier headers (### Immediate, ### High Priority, ### Backlog)
  4. bounded = count <= 15 AND all items are under a tier header

signals:
  healthy: count <= 15 and tiers present
  degraded: count > 15 or missing tier headers

throttling:
  trigger: On SYNC update
  max_frequency: 1/session
```

---

## OBJECTIVES COVERAGE

| Objective | Indicators | Why These Signals Matter |
|-----------|------------|--------------------------|
| Session continuity | H1 (structure), H2 (freshness) | Broken or stale SYNC = agent can't orient |
| Handoff fidelity | H1 (handoff sections exist) | Missing handoff section = dropped baton |
| Decision traceability | H3 (bounded changelog) | Unbounded changelog buries decisions |
| Drift detection | H4 (coverage paths), H5 (issues hygiene) | Phantom entries = false confidence |
| Module coverage | H4 (path accuracy) | Missing entries = invisible gaps |

---

## VALIDATION COVERAGE MAP

| Validation | Health Check | Automated? |
|------------|-------------|------------|
| V1 Structural completeness | H1 sync_structure | Yes — regex for headers |
| V2 Temporal freshness | H2 sync_freshness_project | Yes — date comparison |
| V3 RECENT CHANGES truth | H3 recent_changes_bounded | Partial — count only, not truthfulness |
| V4 MODULE COVERAGE accuracy | H4 module_coverage_accuracy | Yes — path existence |
| V5 KNOWN ISSUES hygiene | H5 known_issues_hygiene | Partial — heuristic |
| V6 Handoff specificity | None | No — requires agent judgment |
| V7 Additive update safety | None | No — requires diff analysis across sessions |
| V8 CURRENT STATE correctness | None | No — requires semantic understanding |
| V9 TODO reflects reality | H6 todo_bounds | Partial — count only, not staleness |

**Coverage: 6/9 invariants have automated or semi-automated checks. 3/9 require agent judgment.**

---

## CHECKER INDEX

```yaml
checkers:
  - name: sync_structure
    purpose: All 10 required sections present and non-empty (V1)
    status: pending
    priority: high
  - name: sync_freshness_project
    purpose: LAST_UPDATED within 24h of latest commit (V2)
    status: pending
    priority: high
  - name: recent_changes_bounded
    purpose: RECENT CHANGES ≤ 7 entries (V3)
    status: pending
    priority: medium
  - name: module_coverage_accuracy
    purpose: All MODULE COVERAGE paths exist on disk (V4)
    status: pending
    priority: high
  - name: known_issues_hygiene
    purpose: No silently-fixed issues (V5, heuristic)
    status: pending
    priority: medium
  - name: todo_bounds
    purpose: TODO ≤ 15 items with tier headers (V9)
    status: pending
    priority: low
```

> All checkers are `pending` — mechanisms are specified but runtime code not yet written. When implemented, they should be added to `sync-state/runtime/checks.py` alongside the existing 4 general checks.

---

## KNOWN GAPS

| Gap | Validation | Impact | Mitigation |
|-----|-----------|--------|------------|
| V6 handoff quality not automatable | V6 | Poor handoffs waste sessions | Agent culture + BEHAVIORS doc |
| V7 concurrent safety not automatable | V7 | Destructive rewrites possible | Git conflict detection, BEHAVIORS doc |
| V8 repo correctness not automatable | V8 | SYNC describes wrong project | Agent reads CURRENT STATE + code, compares |
| V3 truthfulness (aspirational entries) | V3 | Agents build on non-existent work | Only count is checked, not commit correlation |
| V9 staleness (old TODOs) | V9 | Zombie tasks persist | Only count checked, not age of individual items |

---

## HOW TO RUN (when implemented)

```bash
# Run all sync-state health checks (includes general H1-H4)
python -m runtime.capability.run sync-state

# Run Project State structural check specifically
python -m runtime.capability.run sync-state --check sync_structure

# Manual verification (agent-driven)
# Read SYNC_Project_State.md and verify against VALIDATION_Project_State.md
```

---

## MARKERS

<!-- @mind:todo Implement sync_structure check in sync-state/runtime/checks.py -->
<!-- @mind:response SYNC_STRUCTURE_CHECK: Ready to implement. The existing checks.py has 4 checks (sync_freshness, yaml_drift, ingestion_coverage, blocked_modules) using the @check decorator + Signal pattern. sync_structure slots in cleanly as check #5. Implementation plan:

1. EXPECTED_SECTIONS = ['CURRENT STATE', 'KEY COMPONENTS', 'ACTIVE WORK', 'RECENT CHANGES', 'DEPLOYMENT', 'KNOWN ISSUES', 'HANDOFF: FOR AGENTS', 'HANDOFF: FOR HUMAN', 'TODO', 'MODULE COVERAGE']
2. Read .mind/state/SYNC_Project_State.md
3. Regex: re.findall(r'^## (.+)$', content, re.MULTILINE) → found headers
4. missing = set(EXPECTED_SECTIONS) - set(found)
5. Check LAST_UPDATED/UPDATED_BY via regex on frontmatter
6. For each section, verify content between headers is non-empty
7. Signal: healthy (all present, all non-empty) / degraded (1-2 missing) / critical (3+ or no frontmatter)

Note: the existing sync_freshness check scans docs/ for SYNC files. This new check targets .mind/state/SYNC_Project_State.md specifically — different scope, no overlap. Will implement. — @mind 2026-03-15 -->

<!-- @mind:todo Implement module_coverage_accuracy check — glob code paths, compare to table -->
<!-- @mind:response MODULE_COVERAGE_CHECK: Ready to implement. The SYNC table format is pipe-delimited markdown with columns: Module | Code | Docs | Maturity. Current entries use backtick-wrapped paths like `mcp/`, `runtime/physics/`, etc. Implementation:

1. Parse table rows via regex: r'\|\s*([^|]+)\s*\|\s*`([^`]+)`\s*\|'
2. For each code path: os.path.exists(root / path.strip('/'))
3. For phantom detection: collect paths that don't resolve
4. For unlisted detection: glob significant directories (runtime/*/, mcp/, cli/, etc.), compare against listed paths
5. Signal: healthy (all resolve, none missing) / degraded (any phantom or unlisted) / critical (3+ phantoms)

One wrinkle: some code paths are comma-separated (e.g., "runtime/physics/, runtime/cognition/"). The parser needs to split on comma before checking each path. Will handle. — @mind 2026-03-15 -->

<!-- @mind:proposition Consider a V8 keyword check: if CURRENT STATE mentions "Next.js" or "frontend", flag as potential wrong-repo description -->
<!-- @mind:response V8_KEYWORD_CHECK: Smart and cheap. This happened before (SYNC described mind-platform instead of mind-mcp — V8 exists because of that incident). A negative keyword list catches the obvious cases:

WRONG_REPO_KEYWORDS = ['Next.js', 'React', 'frontend', 'landing page', 'registry UI', 'WebXR', 'Three.js', 'Vite']
EXPECTED_KEYWORDS = ['MCP', 'FalkorDB', 'cognitive', 'physics', 'runtime']

Check: if CURRENT STATE section contains any WRONG_REPO_KEYWORDS, flag as DEGRADED. If it contains NONE of the EXPECTED_KEYWORDS, flag as DEGRADED. Both checks together catch: (a) actively describing the wrong repo, and (b) describing something so generic it might be wrong.

This is NOT a content quality check — it's a structural sanity check with a fixed keyword list. Falls within the "structural validation only" design principle. Cheap, ~10 lines, zero false positives on the known incident. Will add as part of sync_structure or as a separate mini-check. — @mind 2026-03-15 -->g-repo description -->
