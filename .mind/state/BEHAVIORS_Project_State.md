# Project State — Behaviors: How SYNC Stays Alive

```
STATUS: CANONICAL
CREATED: 2026-03-15
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Project_State.md
THIS:            BEHAVIORS_Project_State.md (you are here)
SYNC:            ./SYNC_Project_State.md

IMPL:            .mind/state/SYNC_Project_State.md
```

> **Contract:** Project State is a convention system, not a code module. The "implementation" is the SYNC file plus the maintenance behaviors documented here. Read OBJECTIVES first — every behavior traces back to a ranked objective.

---

## BEHAVIORS

### B1: New Agent Gets Oriented

**Why:** Session continuity (Objective #1). An agent that can't figure out the current state within 60 seconds will waste its entire session rediscovering what's already known.

```
GIVEN:  An agent (or human) opens the repo for the first time in a session
WHEN:   They read SYNC_Project_State.md
THEN:   Within 60 seconds they know:
        - What the project IS and IS NOT
        - Which components exist and their status
        - What work is active and who owns it
        - What changed recently
        - What's broken (KNOWN ISSUES)
        - What needs doing (TODO)
AND:    They can begin productive work without asking another agent "what's going on?"
```

### B2: Session Ends With Updated SYNC

**Why:** Handoff fidelity (Objective #2). A session that doesn't update SYNC is a session that never happened from the perspective of the next agent.

```
GIVEN:  An agent has made significant changes during a session
WHEN:   The session ends (or a natural breakpoint is reached)
THEN:   SYNC_Project_State.md is updated with:
        - LAST_UPDATED date set to today
        - UPDATED_BY set to the agent's identity
        - RECENT CHANGES entry added (What, Why, Impact)
        - ACTIVE WORK updated if ownership or status changed
        - KNOWN ISSUES updated if any were fixed or discovered
        - TODO updated if items were completed or added
AND:    The HANDOFF sections contain enough context for the next agent to continue
```

### B3: Significant Decision Gets Recorded

**Why:** Decision traceability (Objective #3). Unrecorded decisions get re-litigated. Recorded decisions compound into institutional knowledge.

```
GIVEN:  An agent makes a decision that affects architecture, scope, or approach
WHEN:   The decision is finalized (committed, deployed, or agreed upon)
THEN:   A RECENT CHANGES entry records:
        - WHAT was decided
        - WHY (the reasoning, not just the outcome)
        - WHO made the decision
        - IMPACT on other components
AND:    If the decision changes a KEY COMPONENTS status, the table is updated
```

### B4: Code-Docs Drift Detected

**Why:** Drift detection (Objective #4). Silent divergence between code and docs is the #1 source of wasted agent sessions.

```
GIVEN:  SYNC describes a component with a certain status (e.g., "Stable")
WHEN:   An agent discovers the actual code contradicts SYNC
        (component missing, renamed, broken, or status wrong)
THEN:   The agent updates SYNC immediately:
        - Corrects the component status
        - Adds a KNOWN ISSUES entry if the drift is significant
        - Adds a RECENT CHANGES entry documenting the correction
AND:    The correction is attributed (UPDATED_BY) so others know who verified it
```

### B5: New Component Appears in Coverage Table

**Why:** Module coverage visibility (Objective #5). A component without a coverage entry is invisible to doc prioritization.

```
GIVEN:  A new module, capability, or significant component is added to the codebase
WHEN:   The work is committed
THEN:   MODULE COVERAGE table gains a new row with:
        - Module name
        - Code path
        - Docs path (or "-" if none yet)
        - Maturity level (typically NEW)
AND:    ACTIVE WORK section gains an entry if the module is under active development
```

### B6: Stale KNOWN ISSUES Get Pruned

**Why:** Freshness over completeness (Tradeoff #1). Stale issues erode trust in the entire file — readers stop believing any of it.

```
GIVEN:  A KNOWN ISSUES entry has been resolved (fix committed or issue no longer applies)
WHEN:   Any agent reads SYNC and notices the stale entry
THEN:   The entry is either:
        - Removed entirely if fully resolved
        - Updated with "Fixed" status and date if worth keeping for context
AND:    LAST_UPDATED is bumped to reflect the cleanup
```

### B7: RECENT CHANGES Stays Bounded

**Why:** Scanability over detail (Tradeoff #2). A 50-entry changelog defeats the purpose — SYNC is not git log.

```
GIVEN:  RECENT CHANGES has accumulated more than 5-7 entries
WHEN:   An agent performs a SYNC update
THEN:   Older entries are pruned:
        - Keep the most recent 5-7 entries
        - Entries older than 2 weeks are candidates for removal
        - Only keep old entries if they record decisions still relevant today
AND:    Historical detail remains accessible via git log / git blame
```

### B8: Concurrent Updates Are Additive

**Why:** Multi-agent safety (Tradeoff #3). Multiple agents working simultaneously must not overwrite each other's updates.

```
GIVEN:  Two or more agents are active in the same session window
WHEN:   Both need to update SYNC
THEN:   Each agent's update is additive:
        - APPEND to RECENT CHANGES (don't rewrite the section)
        - UPDATE specific status fields they own
        - ADD to KNOWN ISSUES / TODO as needed
AND:    Full rewrites only happen when the file has become incoherent
        (conflicting entries, broken structure, outdated framing)
```

### B9: Handoff Sections Carry Actionable Context

**Why:** Handoff fidelity (Objective #2). A handoff that says "continue the work" is useless. A handoff that says "the auth module tests fail on line 47 because the mock doesn't handle null tokens" saves an hour.

```
GIVEN:  A session is ending and work is partially complete
WHEN:   The agent writes the HANDOFF sections
THEN:   FOR AGENTS contains:
        - Current focus area
        - Key context that isn't obvious from the code
        - Specific warnings ("watch out for X")
        - Where to start
AND:    FOR HUMAN contains:
        - Executive summary (1-2 sentences)
        - Decisions made (with rationale)
        - Decisions that need human input
```

---

## OBJECTIVES SERVED

| Behavior | Objective | What It Protects |
|----------|-----------|-----------------|
| B1 | Session continuity | Agent orientation speed |
| B2 | Handoff fidelity | Zero context loss between sessions |
| B3 | Decision traceability | Institutional memory |
| B4 | Drift detection | Code↔docs alignment |
| B5 | Module coverage visibility | Doc gap awareness |
| B6 | Drift detection | SYNC file trustworthiness |
| B7 | Session continuity | Scanability under time pressure |
| B8 | Handoff fidelity | Multi-agent safety |
| B9 | Handoff fidelity | Actionable continuity |

---

## INPUTS / OUTPUTS

### Primary Artifact: `SYNC_Project_State.md`

**Inputs (triggers for update):**

| Trigger | Source | Required Sections |
|---------|--------|-------------------|
| Session end | Any agent | LAST_UPDATED, RECENT CHANGES, HANDOFF |
| Significant commit | Any agent | RECENT CHANGES, KEY COMPONENTS (if status changed) |
| Architecture decision | Any agent | RECENT CHANGES (with Why), HANDOFF: FOR HUMAN |
| Bug discovered | Any agent | KNOWN ISSUES |
| Bug fixed | Any agent | KNOWN ISSUES (remove/mark Fixed) |
| New module added | Any agent | MODULE COVERAGE, ACTIVE WORK |
| Drift discovered | Any agent | Correct the drifted section, KNOWN ISSUES |

**Outputs (value delivered):**

| Consumer | What They Get |
|----------|---------------|
| New agent | Full project context in 60 seconds |
| Returning agent | What changed since last session |
| Human partner | Executive summary + decisions needing input |
| @archivist | Module coverage gaps for doc prioritization |

---

## EDGE CASES

### E1: SYNC Describes Wrong Project

```
GIVEN:  SYNC was written by an agent that confused this repo with another
        (e.g., described mind-platform instead of mind-mcp)
THEN:   Full rewrite is justified — this is the "incoherent file" exception to B8
AND:    The rewrite is documented in RECENT CHANGES with a note explaining the error
```

### E2: No Significant Changes in Session

```
GIVEN:  An agent session produced only exploratory reads, no commits or decisions
THEN:   SYNC update is NOT required
AND:    Trivial "I read some files" updates degrade signal-to-noise ratio — skip them
```

### E3: LAST_UPDATED is More Than 24h Stale

```
GIVEN:  Significant changes have been committed but SYNC was not updated
THEN:   The next agent to touch the repo MUST update SYNC before doing other work
AND:    Staleness > 24h is itself a KNOWN ISSUE to be noted and immediately resolved
```

### E4: Component Removed From Codebase

```
GIVEN:  A module listed in MODULE COVERAGE has been deleted
THEN:   Remove its row from MODULE COVERAGE
AND:    Add a RECENT CHANGES entry ("Removed X because Y")
AND:    Do NOT leave phantom entries — they mislead future agents
```

---

## ANTI-BEHAVIORS

### A1: Aspirational RECENT CHANGES

```
GIVEN:   An agent plans to make changes but hasn't committed them yet
WHEN:    Updating SYNC
MUST NOT: Add entries for work not yet done ("Added X" when X doesn't exist)
INSTEAD:  Add to ACTIVE WORK or TODO — RECENT CHANGES is for completed work only
```

### A2: Stale SYNC Accumulation

```
GIVEN:   Multiple sessions have passed without SYNC updates
WHEN:    An agent notices LAST_UPDATED is outdated
MUST NOT: Ignore the staleness and proceed with their own task
INSTEAD:  Fix SYNC first — an inaccurate SYNC costs more than a delayed task
```

### A3: Destructive Rewrite Without Cause

```
GIVEN:   SYNC contains valid recent entries from other agents
WHEN:    A new agent starts and wants to "clean up"
MUST NOT: Rewrite SYNC from scratch, discarding others' entries
INSTEAD:  Additive updates only (B8) — rewrite only when the file is structurally incoherent
```

### A4: Git Log Duplication

```
GIVEN:   An agent finished routine work (minor refactor, typo fix, dep bump)
WHEN:    Considering a SYNC update
MUST NOT: Add a RECENT CHANGES entry for every commit
INSTEAD:  Only record changes that affect project understanding — architecture,
          status shifts, decisions, newly discovered issues
```

### A5: Empty Handoff Boilerplate

```
GIVEN:   A session is ending
WHEN:    Writing the HANDOFF sections
MUST NOT: Write generic text ("continue the work", "check the code", "see TODOs")
INSTEAD:  Write specific context: what you were working on, where you stopped,
          what's tricky, what the next agent should start with
```

---

## MARKERS

<!-- @mind:proposition Consider adding a SYNC_SCHEMA section that defines required sections explicitly, so validation can be automated -->
<!-- @mind:response SYNC_SCHEMA: Yes — but it already half-exists. PATTERNS_Project_State.md (STRUCTURE CONVENTIONS) defines the 10-section order. The gap is that it's prose, not machine-parseable. What we actually need is a lightweight validator that checks: (1) all 10 section headers present, (2) LAST_UPDATED and UPDATED_BY fields exist and are non-empty, (3) RECENT CHANGES has ≤7 entries, (4) no section is empty (which means either remove it or fill it). The schema itself should be a simple list in PATTERNS, not a separate doc — it's ~15 lines of expected headers + required fields. The validator is a standalone script or a check in sync-state/runtime/checks.py: read the .md, regex for ## headers, compare against expected list, flag missing/extra. Maybe 30 lines of Python. Key design choice: the schema validates STRUCTURE, not CONTENT. We can't validate whether a handoff is "specific enough" (that's A5's job, enforced by culture not code). But we CAN validate that the handoff section EXISTS and is non-empty. That alone catches 80% of drift. I'll add the expected section list to PATTERNS and wire the structural check into sync-state. — @mind 2026-03-15 -->
