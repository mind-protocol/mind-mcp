# Project State — Patterns: Curated State for Session Continuity

```
STATUS: CANONICAL
CREATED: 2026-03-15
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Project_State.md
THIS:            PATTERNS_Project_State.md (you are here)
SYNC:            ./SYNC_Project_State.md

IMPL:            .mind/state/SYNC_Project_State.md (the SYNC file IS the implementation)
```

### Bidirectional Contract

**Before modifying this doc or the SYNC file:**
1. Read OBJECTIVES_Project_State.md first
2. Read the current SYNC_Project_State.md

**After modifying the SYNC file:**
1. Ensure it still follows the patterns described here
2. If a pattern changed, update this doc

---

## THE PROBLEM

AI agents are amnesiac. Every session starts from zero unless explicit state is maintained.

Without a curated state file:
- Agents waste the first 10 minutes rediscovering what's happening in the project
- Handoffs between agents lose context — the second agent re-investigates what the first already knew
- Decisions get re-litigated because nobody recorded why the current approach was chosen
- Docs drift from reality because nobody tracks which modules have docs and which don't
- Stale TODO lists accumulate entries that were silently completed or abandoned

The cost is not just time — it's compounding confusion. Each session without state tracking increases the probability that the next session makes a wrong assumption.

---

## THE PATTERN

**Curated single-file state snapshot.**

One markdown file (`SYNC_Project_State.md`) holds the entire working context of the project. It is:

1. **Human-curated** — not auto-generated from git log. The value is in what an intelligent observer decides matters, not raw data.
2. **Current-focused** — describes what IS, not what WAS. Old entries are pruned. Git is the archive.
3. **Scannable** — tables over prose, status markers over paragraphs. A reader gets full context in 60 seconds.
4. **Additively updated** — multiple agents can update without destroying each other's contributions. Append to RECENT CHANGES, update status fields. Full rewrites only when incoherent.

The SYNC file is both the implementation and the artifact — there is no code behind it. The "runtime" is every agent that reads it at session start and updates it at session end.

---

## BEHAVIORS SUPPORTED

- **B1: 60-second orientation** — agent reads SYNC, knows what's happening, starts working
- **B2: Zero-loss handoff** — departing agent updates SYNC, arriving agent reads it, no context gap
- **B3: Decision persistence** — significant decisions recorded with who/when/why, preventing re-litigation
- **B4: Drift detection** — MODULE COVERAGE table surfaces mismatches between code and docs
- **B5: Stale pruning** — old RECENT CHANGES entries removed, keeping the file honest and current

## BEHAVIORS PREVENTED

- **Anti-B1: Amnesia** — every session starting from scratch
- **Anti-B2: Context loss** — handoffs that require the new agent to rediscover everything
- **Anti-B3: Unbounded growth** — SYNC becoming a changelog that nobody reads
- **Anti-B4: Aspiration tracking** — TODOs and entries that describe intent rather than reality

---

## PRINCIPLES

### Principle 1: Freshness Over Completeness

A SYNC file that's accurate about 5 things is better than one that covers 20 things but half are outdated. Every entry must reflect current reality. If you can't verify it, remove it. Stale state is worse than missing state — it actively misleads.

### Principle 2: Scanability Over Detail

The file is read under time pressure — agents loading context at session start. Use:
- Tables for structured data (components, issues, coverage)
- Status markers (`Stable`, `New`, `Fixed`) over explanatory paragraphs
- Short entries in RECENT CHANGES (what/why/impact, 3 lines max)
- Separate sections for different audiences (agents vs. human)

### Principle 3: Judgment Over Automation

SYNC requires curation. A git-diff-generated summary would miss:
- Which changes actually matter vs. routine commits
- What the next agent needs to know vs. what's just noise
- When an old issue was silently fixed and should be removed
- What context a human needs that an agent doesn't (and vice versa)

Automated tooling can help (flagging stale entries, checking timestamps), but the content decisions are human/agent judgment calls.

### Principle 4: Additive Updates, Destructive Rewrites Only When Incoherent

When updating SYNC:
- **Append** new entries to RECENT CHANGES (newest first)
- **Update** status fields in existing tables
- **Remove** entries that are stale or resolved
- **Rewrite from scratch** only when the file has accumulated enough drift that incremental fixes won't restore coherence

This prevents the last-writer-wins problem when multiple agents touch the file in the same period.

### Principle 5: Separate Audiences

The HANDOFF section splits into FOR AGENTS and FOR HUMAN because they need different context:
- Agents need technical gotchas, import warnings, file size warnings
- Humans need executive summaries, decision summaries, open questions requiring their input

---

## DATA

| Source | Type | Purpose |
|--------|------|---------|
| `.mind/state/SYNC_Project_State.md` | FILE | The state file itself — the primary artifact |
| `.mind/state/OBJECTIVES_Project_State.md` | FILE | Why the state file exists and what it optimizes for |
| `git log` | COMMAND | Archive of changes — what SYNC prunes flows here |
| `.mind/state/REPAIR_REPORT.md` | FILE | Repair actions taken on the state system |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| Git history | SYNC prunes old entries because git preserves the full record |
| Doc chain convention | MODULE COVERAGE tracks doc chain completeness per module |
| Capability system | Health checks can flag stale SYNC via `sync-state` capability |

---

## SCOPE

### In Scope

- Current project state (what components exist, their status)
- Recent changes (last ~5 significant events)
- Known issues (active problems, not resolved ones)
- Handoff context (what the next agent/human needs to know)
- TODO tracking (current priorities, not a backlog)
- Module coverage visibility (code vs. docs completeness)
- Deployment configuration summary

### Out of Scope

- **Complete changelog** → use `git log`
- **Task management** → use graph task nodes or external tools
- **Code documentation** → use the doc chain (PATTERNS, ALGORITHM, IMPLEMENTATION)
- **Architecture decisions record** → use ADR files or narrative nodes in the graph
- **Per-citizen state** → each citizen has their own memory/ directory

---

## STRUCTURE CONVENTIONS

The SYNC file follows a fixed section order:

```
1. CURRENT STATE         — what the project is (stable, rarely changes)
2. KEY COMPONENTS        — table of modules with paths and status
3. ACTIVE WORK           — what's being worked on right now
4. RECENT CHANGES        — last ~5 significant events (newest first)
5. DEPLOYMENT            — infra summary
6. KNOWN ISSUES          — active problems with severity
7. HANDOFF: FOR AGENTS   — technical context for the next agent
8. HANDOFF: FOR HUMAN    — executive summary for the human partner
9. TODO                  — prioritized list (immediate / high / backlog)
10. MODULE COVERAGE      — code-vs-docs completeness table
```

Each section serves a specific read pattern:
- Sections 1-2: "What is this project?" (first-time orientation)
- Sections 3-4: "What just happened?" (returning agent catch-up)
- Sections 5-6: "What's broken?" (incident response)
- Sections 7-8: "What do I need to know?" (handoff)
- Sections 9-10: "What should I work on?" (task selection)

---

## MARKERS

<!-- @mind:proposition Consider automated staleness detection — flag SYNC entries where LAST_UPDATED > 48h behind latest commit -->
<!-- @mind:response STALENESS_DETECTION: Yes — and it already has a natural home. The sync-state capability (referenced in DEPENDENCIES) runs health checks. Add a staleness check: compare SYNC's UPDATED timestamp against `git log -1 --format=%cI`. If delta > 48h, emit a WARN. But the 48h threshold needs nuance: some periods are legitimately quiet (no commits = no staleness). Better heuristic: flag when commits_since_last_sync > N (say 5) rather than pure time. That catches "lots happened but SYNC didn't update" without false positives during quiet periods. Implementation: one function in .mind/capabilities/sync-state/runtime/checks.py, ~15 lines. Principle 3 stays intact — automation flags, humans/agents decide what to do about it. — @mind 2026-03-15 -->

<!-- @mind:proposition Add a SYNC diff tool that shows what changed between two SYNC snapshots -->
<!-- @mind:response SYNC_DIFF: Interesting but tricky. SYNC is a curated file, not structured data — diffing two snapshots gives you a text diff, not a semantic diff. What would actually be useful: a structured changelog that records WHAT changed, WHO changed it, and WHY, appended each time SYNC is updated. Pattern: before overwriting SYNC, snapshot the current version to .mind/state/sync_history/{timestamp}.md. Then `diff --unified` between any two snapshots. The snapshots are cheap (one .md file per update, prune after 20), and you get full audit trail for free. No custom tool needed — git already does this IF agents commit SYNC changes separately. Better enforcement: add a pre-commit convention that SYNC modifications get their own commit with a standard prefix (e.g., "sync: ..."). Then `git log --oneline -- .mind/state/SYNC_Project_State.md` IS the diff tool. Leverage git, don't reinvent it. — @mind 2026-03-15 -->
