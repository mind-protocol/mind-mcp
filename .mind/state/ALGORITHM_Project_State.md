# Project State — Algorithm: Procedures for Reading, Updating, and Maintaining SYNC

```
STATUS: CANONICAL
CREATED: 2026-03-15
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Project_State.md
PATTERNS:        ./PATTERNS_Project_State.md
THIS:            ALGORITHM_Project_State.md (you are here)
SYNC:            ./SYNC_Project_State.md

IMPL:            .mind/state/SYNC_Project_State.md (the SYNC file IS the implementation)
```

> **Contract:** Read OBJECTIVES and PATTERNS before modifying. The SYNC file is maintained by these procedures, not by code.

---

## OVERVIEW

Project State has no runtime code. The "algorithm" is the set of procedures that agents and humans follow to keep SYNC accurate. There are four core procedures:

1. **Session Start** — read SYNC, orient, begin work
2. **Session End** — update SYNC with what changed
3. **Staleness Audit** — detect and prune outdated entries
4. **Full Rewrite** — rebuild SYNC from scratch when it's drifted too far

Each procedure is deterministic enough to follow mechanically, but requires judgment about what matters.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | What This Algorithm Guarantees |
|-----------|---------------------|-------------------------------|
| Session continuity | B1: 60-second orientation | Agent reads fixed-order sections, gets full context |
| Handoff fidelity | B2: Zero-loss handoff | Session-end procedure captures departing context |
| Decision traceability | B3: Decision persistence | RECENT CHANGES records who/when/why |
| Drift detection | B4: Drift detection | MODULE COVERAGE audit catches code/doc mismatches |
| Freshness | B5: Stale pruning | Staleness audit removes dead entries |

---

## DATA STRUCTURES

### SYNC File Sections (fixed order)

```
Section              | Purpose                          | Update Frequency
---------------------|----------------------------------|------------------
CURRENT STATE        | What the project IS              | Rarely (arch changes only)
KEY COMPONENTS       | Module table with paths/status   | On module add/remove/status change
ACTIVE WORK          | In-progress initiatives          | On start/complete of major work
RECENT CHANGES       | Last ~5 significant events       | Every session that produces changes
DEPLOYMENT           | Infra summary                    | On deploy config change
KNOWN ISSUES         | Active problems                  | On discover/resolve
HANDOFF: FOR AGENTS  | Technical gotchas                | When new gotchas discovered
HANDOFF: FOR HUMAN   | Executive summary + open Qs      | When decisions needed
TODO                 | Prioritized list (3 tiers)       | On complete/add/reprioritize
MODULE COVERAGE      | Code vs docs completeness        | On doc chain changes
```

### RECENT CHANGES Entry

```
### {DATE}: {Title}

- **What:** {1-2 sentences — what was done}
- **Why:** {1 sentence — motivation}
- **Impact:** {1 sentence — what it affects}
```

### KNOWN ISSUES Entry

```
| {description} | {severity: Low/Medium/High/Critical} | {area} | {notes} |
```

---

## ALGORITHM: SESSION START (Read Procedure)

### Step 1: Read SYNC Header

Read `LAST_UPDATED` and `UPDATED_BY`. If LAST_UPDATED is more than 48h old and commits exist since then, the file may be stale — proceed with caution.

```
read SYNC_Project_State.md
check LAST_UPDATED timestamp
if (now - LAST_UPDATED > 48h) AND (commits since LAST_UPDATED > 0):
    flag: "SYNC may be stale — verify entries against code"
```

### Step 2: Scan CURRENT STATE and KEY COMPONENTS

Understand what the project is and what modules exist. This is stable context — it rarely changes.

### Step 3: Read ACTIVE WORK and RECENT CHANGES

Understand what's happening NOW. This is the highest-value section for orientation.

```
for each entry in RECENT CHANGES:
    note: what changed, why, impact
    if entry references files you'll touch:
        read those files before starting work
```

### Step 4: Check KNOWN ISSUES

Avoid stepping on known landmines.

### Step 5: Read your audience's HANDOFF section

- If you're an agent: read HANDOFF: FOR AGENTS
- If you're a human: read HANDOFF: FOR HUMAN

### Step 6: Check TODO for task selection

If you don't have a specific task, pick from TODO based on tier (Immediate > High Priority > Backlog).

**Total time target: 60 seconds.** If it takes longer, the SYNC file needs trimming.

---

## ALGORITHM: SESSION END (Update Procedure)

### Step 1: Determine if changes warrant a SYNC update

```
if session produced:
    - code changes (committed or staged)
    - resolved a KNOWN ISSUE
    - discovered a new issue
    - made an architectural decision
    - changed deployment config
    - completed a TODO item
then:
    update SYNC
else:
    skip (no-op sessions don't need SYNC updates)
```

### Step 2: Update RECENT CHANGES (prepend)

Add new entry at the top of RECENT CHANGES. Use the standard format. If RECENT CHANGES has more than 5 entries, remove the oldest.

```
prepend to RECENT CHANGES:
    ### {today's date}: {Title}
    - What: {description}
    - Why: {motivation}
    - Impact: {what it affects}

if len(RECENT CHANGES entries) > 5:
    remove oldest entry
```

### Step 3: Update affected sections

```
if module added/removed/status changed:
    update KEY COMPONENTS table

if new issue discovered:
    append to KNOWN ISSUES

if issue resolved:
    remove from KNOWN ISSUES (or mark "Fixed")

if TODO item completed:
    mark [x] or remove

if deployment changed:
    update DEPLOYMENT section

if doc chain changed:
    update MODULE COVERAGE table

if new gotcha discovered:
    add to HANDOFF: FOR AGENTS

if decision needs human input:
    add to HANDOFF: FOR HUMAN
```

### Step 4: Update header

```
set LAST_UPDATED to today's date
set UPDATED_BY to your identity (agent name or "human")
```

### Step 5: Verify scanability

Re-read the file. If any section is hard to scan in 10 seconds, tighten it. Tables over prose. Status markers over paragraphs.

---

## ALGORITHM: STALENESS AUDIT

Run when LAST_UPDATED is old, or periodically (weekly recommended).

### Step 1: Check RECENT CHANGES against git

```
for each entry in RECENT CHANGES:
    if entry.date > 30 days ago:
        remove (too old — git has the history)
    if entry references work that has been superseded:
        remove or update
```

### Step 2: Check KNOWN ISSUES against code

```
for each issue in KNOWN ISSUES:
    if issue has been fixed (check code/git):
        remove from table
    if issue severity changed:
        update severity
    if issue has been open > 30 days with no activity:
        flag for review (still relevant?)
```

### Step 3: Check TODO against reality

```
for each TODO item:
    if completed (check code/git):
        mark [x] or remove
    if no longer relevant:
        remove
    if blocked:
        add note explaining blocker
```

### Step 4: Check MODULE COVERAGE against filesystem

```
for each module in KEY COMPONENTS:
    verify path still exists
    verify status is accurate
    check if docs exist in doc chain

for each entry in MODULE COVERAGE:
    verify code path exists
    verify doc paths exist
    update maturity (NEW → STABLE → etc.)

if module exists in code but not in tables:
    add to KEY COMPONENTS and MODULE COVERAGE

if module exists in tables but not in code:
    remove from both tables
```

### Step 5: Check ACTIVE WORK

```
for each item in ACTIVE WORK:
    if completed:
        move to RECENT CHANGES, remove from ACTIVE WORK
    if abandoned:
        remove, note in RECENT CHANGES
    if stale (no progress in > 7 days):
        flag for review
```

---

## ALGORITHM: FULL REWRITE

Triggered when incremental updates have left the SYNC file incoherent — sections contradict each other, entries reference things that don't exist, or structure has drifted from the standard.

### Step 1: Gather ground truth

```
sources = {
    "components": list_directories(["mcp/", "runtime/", "cli/"]),
    "recent_commits": git_log(last=20),
    "deployment": read("home_server.py", "render.yaml"),
    "docs": glob(".mind/**/*.md", "docs/**/*.md"),
    "issues": grep("TODO|FIXME|HACK", "**/*.py"),
}
```

### Step 2: Rebuild each section from ground truth

Follow the fixed section order from DATA STRUCTURES above. Write each section fresh, using current filesystem/git state, not the old SYNC content.

### Step 3: Preserve useful context from old SYNC

```
old_sync = read current SYNC

for each section in old_sync:
    if section contains context NOT derivable from code/git:
        (decisions, rationale, gotchas, human questions)
        merge into new SYNC
```

### Step 4: Validate

```
for each module in KEY COMPONENTS:
    assert path exists on disk
for each issue in KNOWN ISSUES:
    assert issue is still open
for each TODO:
    assert not already done
assert len(RECENT CHANGES) <= 5
assert LAST_UPDATED == today
```

---

## KEY DECISIONS

### D1: When to update vs. skip

```
IF session produced observable changes (commits, issues, decisions):
    update SYNC
ELSE:
    skip — no-op sessions don't pollute the file
```

### D2: When to prune vs. keep old entries

```
IF entry is > 30 days old:
    prune (git has the history)
ELIF entry references superseded work:
    prune or update
ELSE:
    keep
```

### D3: When to rewrite vs. incrementally fix

```
IF > 3 sections have stale/contradictory content:
    full rewrite (incremental fixes won't restore coherence)
ELIF 1-2 sections need updates:
    incremental update
```

### D4: When to add to ACTIVE WORK vs. TODO

```
IF work is currently in progress (someone is actively doing it):
    ACTIVE WORK
ELIF work needs to be done but nobody is on it:
    TODO (appropriate tier)
```

---

## DATA FLOW

```
Session Start:
    SYNC file → agent reads → mental model → productive work begins

Session End:
    Work results → agent judgment → SYNC update → file written

Staleness Audit:
    SYNC file + git log + filesystem → comparison → pruned SYNC

Full Rewrite:
    filesystem + git + old SYNC context → fresh SYNC
```

---

## COMPLEXITY

**Time:** O(1) per session — reading/updating is constant work regardless of project size.

**Space:** O(1) — the SYNC file is bounded by convention (~200 lines max, enforced by pruning).

**Bottlenecks:**
- Staleness audit requires checking git history and filesystem — can be slow on large repos
- Full rewrite requires reading multiple source directories — most expensive operation
- Human judgment is the true bottleneck — knowing what matters can't be automated

---

## INTERACTIONS

| Module | What We Read/Write | What We Get |
|--------|-------------------|-------------|
| `git log` | Recent commit history | Ground truth for RECENT CHANGES |
| `filesystem` | Directory listings, file existence | Ground truth for KEY COMPONENTS, MODULE COVERAGE |
| `.mind/capabilities/sync-state/` | Health checks for SYNC staleness | Automated staleness detection triggers |
| Doc chain files | OBJECTIVES, PATTERNS, IMPLEMENTATION, etc. | MODULE COVERAGE accuracy |
