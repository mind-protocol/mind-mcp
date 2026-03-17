# OBJECTIVES — Project State

```
STATUS: CANONICAL
CREATED: 2026-03-15
```

---

## CHAIN

```
THIS:            OBJECTIVES_Project_State.md (you are here - START HERE)
SYNC:            ./SYNC_Project_State.md

IMPL:            .mind/state/SYNC_Project_State.md (the SYNC file IS the implementation)
```

**Note:** Project State is not a code module — it is the state-tracking system that enables continuity across sessions, agents, and handoffs. The "implementation" is the SYNC file itself plus the conventions that govern how it's maintained.

---

## PRIMARY OBJECTIVES (ranked)

1. **Session continuity** — Any agent (or human) landing on this repo must understand what's happening, what changed recently, and what needs attention within 60 seconds of reading the SYNC file. Without this, every session starts from zero — the exact problem Mind Protocol exists to solve.

2. **Handoff fidelity** — When one agent stops and another picks up, zero context is lost. The SYNC file carries the full working state: current focus, recent changes, known issues, open questions, and who owns what. A handoff without a SYNC update is a dropped baton.

3. **Decision traceability** — Every significant decision is recorded with who made it, when, and why. This prevents re-litigating settled questions and lets future agents understand the reasoning behind the current architecture.

4. **Drift detection** — The SYNC file is the single source of truth for what's real vs. what's aspirational. If code exists but SYNC doesn't mention it, something was built without documentation. If SYNC mentions something that doesn't exist in code, the docs drifted. Both are bugs.

5. **Module coverage visibility** — Track which components have docs, which don't, and what their maturity level is. This drives prioritization of doc work and surfaces gaps before they become costly.

## NON-OBJECTIVES

- **Changelog replacement** — SYNC is not git log. It captures *current state and recent context*, not a complete history. Old entries should be pruned as they become irrelevant. Git is the archive.
- **Task management** — SYNC tracks TODOs for orientation, not for project management. Detailed task tracking belongs in the graph (task nodes) or external tools, not in a markdown file that grows unboundedly.
- **Code documentation** — SYNC describes *what components exist and their status*, not how they work. That's what the doc chain (PATTERNS, ALGORITHM, IMPLEMENTATION) is for.
- **Automated generation** — SYNC requires judgment — what matters, what's stale, what needs context. It cannot be fully auto-generated from git diff. The value is in the curation.

## TRADEOFFS (canonical decisions)

- When **completeness** conflicts with **staleness**, choose **freshness**. A SYNC file that's accurate about 5 things is better than one that covers 20 things but half are outdated. Prune aggressively.
- When **detail** conflicts with **scanability**, choose **scanability**. The SYNC file is read under time pressure — agents loading context at session start. Tables over prose. Status markers over paragraphs. A human or agent should get the full picture in 60 seconds.
- When **multiple agents update simultaneously**, the last writer wins, but **each update must be additive** (append to RECENT CHANGES, update status fields) not destructive (rewrite from scratch). Rewrite only when the file has become incoherent.
- We accept **manual maintenance cost** to preserve **accuracy**. Automated SYNC generation would be cheaper but would miss judgment calls about what's important, what's stale, and what the next agent needs to know.

## SUCCESS SIGNALS (observable)

- A new agent reads SYNC and begins productive work without asking "what's going on?" — the file answered it
- LAST_UPDATED is never more than 24h behind the latest significant change
- Every entry in RECENT CHANGES corresponds to actual committed work (no aspirational entries)
- MODULE COVERAGE table matches reality — no phantom modules, no missing entries
- KNOWN ISSUES list has zero entries that have been silently fixed (stale issues cleaned promptly)
- Handoff sections (FOR AGENTS / FOR HUMAN) contain actionable context, not boilerplate
- TODO list reflects actual priorities, not a wish list that never gets pruned
