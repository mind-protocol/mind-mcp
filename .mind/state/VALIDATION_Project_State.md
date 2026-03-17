# Project State — Validation: What Must Be True

```
STATUS: CANONICAL
CREATED: 2026-03-15
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Project_State.md
BEHAVIORS:       ./BEHAVIORS_Project_State.md
THIS:            VALIDATION_Project_State.md (you are here)
SYNC:            ./SYNC_Project_State.md

IMPL:            .mind/state/SYNC_Project_State.md
```

---

## PURPOSE

Invariants that MUST hold for the SYNC file to serve its purpose. Project State is a convention system — these invariants are enforced by agents reading this doc and by the structural validator in `sync-state/runtime/checks.py`. If SYNC violates any CRITICAL invariant, it is actively harmful: agents make decisions based on false information.

---

## INVARIANTS

### V1: Structural Completeness

**Why we care:** A SYNC file missing required sections forces the reader to guess what's happening. Missing HANDOFF = no continuity. Missing KNOWN ISSUES = hidden landmines. The structure IS the contract.

```
MUST:
  - Contain all 10 required section headers:
    ## CURRENT STATE
    ## KEY COMPONENTS
    ## ACTIVE WORK
    ## RECENT CHANGES
    ## DEPLOYMENT
    ## KNOWN ISSUES
    ## HANDOFF: FOR AGENTS
    ## HANDOFF: FOR HUMAN
    ## TODO
    ## MODULE COVERAGE
  - Have non-empty LAST_UPDATED and UPDATED_BY in the frontmatter block
  - Have every required section be non-empty (if nothing to report, remove the section
    and add a @mind:todo marker explaining why)

NEVER:
  - Omit a required section without explicit justification
  - Leave LAST_UPDATED or UPDATED_BY blank
  - Add new top-level sections without updating this invariant list
```

### V2: Temporal Freshness

**Why we care:** A stale SYNC is worse than no SYNC — it creates false confidence. Agents trust what they read and act on outdated information. The 24h window is the maximum tolerable drift.

```
MUST:
  - LAST_UPDATED reflects the actual date of the most recent meaningful edit
  - LAST_UPDATED be no more than 24h behind the latest significant commit
  - An agent discovering staleness > 24h fix SYNC before doing other work (B2, E3)

NEVER:
  - Set LAST_UPDATED to a future date
  - Set LAST_UPDATED without actually updating content (timestamp-only bumps are lies)
  - Let staleness accumulate across multiple sessions without correction
```

### V3: RECENT CHANGES Truthfulness

**Why we care:** RECENT CHANGES is the first thing agents scan after CURRENT STATE. If it contains aspirational entries (work planned but not done), agents will build on foundations that don't exist.

```
MUST:
  - Every entry in RECENT CHANGES correspond to committed, verifiable work
  - Each entry include: What, Why, and either Impact or Who
  - Entries be ordered reverse-chronologically (newest first)
  - Section contain at most 7 entries (B7) — older entries pruned to git history

NEVER:
  - Record planned or in-progress work in RECENT CHANGES (use ACTIVE WORK or TODO)
  - Record routine commits (typo fixes, dep bumps) — only architecture/status/decision changes
  - Let entry count exceed 7 without pruning
```

### V4: MODULE COVERAGE Accuracy

**Why we care:** MODULE COVERAGE drives doc prioritization. A phantom entry (module listed but deleted) wastes an agent's session investigating nonexistent code. A missing entry (module exists but unlisted) means nobody knows docs are needed.

```
MUST:
  - Every row in MODULE COVERAGE correspond to an existing code path
  - Every significant module in the codebase have a row in MODULE COVERAGE
  - Maturity column reflect actual state (NEW/STABLE/DEPRECATED), not aspiration
  - Docs column accurately show doc path or "-" for undocumented modules

NEVER:
  - List a module whose code path doesn't exist (phantom entries)
  - Omit a module with its own directory or significant file count
  - Mark a module STABLE when it has known failures or is under active rewrite
```

### V5: KNOWN ISSUES Hygiene

**Why we care:** Stale issues destroy trust in the monitoring system. After seeing 3 "known issues" that were silently fixed, agents stop reading the section. Then a real issue goes unnoticed.

```
MUST:
  - Every KNOWN ISSUES entry describe an actual, current problem
  - Fixed issues be removed or explicitly marked "Fixed" with date
  - Each entry include: Severity, Area, and Notes
  - New issues be added immediately upon discovery, not deferred to session end

NEVER:
  - Leave a fixed issue unmarked across sessions
  - Add issues without severity — severity drives triage priority
  - Use KNOWN ISSUES for feature requests or future work (those go in TODO)
```

### V6: Handoff Specificity

**Why we care:** Generic handoffs ("continue the work") waste the next agent's entire orientation phase. Specific handoffs ("auth tests fail on line 47, the mock doesn't handle null tokens") save hours. This is the highest-leverage sentence in the file.

```
MUST:
  - HANDOFF: FOR AGENTS contain: current focus, non-obvious context, specific warnings
  - HANDOFF: FOR HUMAN contain: executive summary, decisions made, decisions needing input
  - Both sections be rewritten (not appended) when the project focus shifts
  - Warnings reference specific files, modules, or constraints — not vague cautions

NEVER:
  - Write boilerplate ("check the code", "see TODOs", "continue the work")
  - Copy-paste handoff text between sessions without reviewing accuracy
  - Leave handoff sections empty after a productive session
```

### V7: Additive Update Safety

**Why we care:** Multiple agents updating SYNC in overlapping sessions can destroy each other's entries. The additive-only rule (B8) prevents data loss while allowing concurrent maintenance.

```
MUST:
  - Updates APPEND to RECENT CHANGES (not rewrite the section)
  - Updates MODIFY only the specific fields the agent owns (status, their active work)
  - Full rewrites occur ONLY when the file is structurally incoherent
  - The rewriting agent note "Full rewrite — previous content was incoherent" in RECENT CHANGES

NEVER:
  - Rewrite SYNC from scratch when it contains valid entries from other agents
  - Delete another agent's RECENT CHANGES or ACTIVE WORK entries without cause
  - Silently drop content during a "cleanup" pass
```

### V8: CURRENT STATE Describes This Repo

**Why we care:** This actually happened — SYNC once described mind-platform (the frontend) instead of mind-mcp (the backend). Every agent that read it during that period operated on false assumptions. This invariant exists because of a real incident.

```
MUST:
  - CURRENT STATE accurately describe mind-mcp: MCP server + cognitive runtime
  - "What it IS" list match actual deployed capabilities
  - "What it is NOT" list name the correct sibling repos
  - Architecture position table reflect actual layer ownership

NEVER:
  - Describe a different repo's functionality (mind-platform, cities-of-light, etc.)
  - Claim capabilities that don't exist in this codebase
  - Omit the "What it is NOT" section — it prevents the confusion that caused the incident
```

### V9: TODO Reflects Reality

**Why we care:** A TODO list that never gets pruned becomes a graveyard of abandoned ideas. Agents read it for orientation and can't distinguish urgent work from 6-month-old wishes. The list must be a curated signal, not accumulated noise.

```
MUST:
  - TODO items reflect actual prioritized work, not aspirational features
  - Completed items be marked [x] or removed promptly
  - Items be grouped by priority tier (Immediate / High Priority / Backlog)
  - Backlog items be periodically reviewed — items untouched for 4+ weeks are candidates for removal

NEVER:
  - Add TODO items without a priority tier
  - Let completed items sit unmarked across sessions
  - Let the total TODO count exceed ~15 items (prune backlog ruthlessly)
```

---

## PRIORITY

| Priority | Meaning | If Violated |
|----------|---------|-------------|
| **CRITICAL** | Agents act on false information | Wasted sessions, wrong decisions |
| **HIGH** | Significant orientation time lost | Agents can recover but at cost |
| **MEDIUM** | Quality degradation | SYNC still usable but trust erodes |

---

## INVARIANT INDEX

| ID | Value Protected | Priority |
|----|-----------------|----------|
| V1 | Structural completeness | HIGH |
| V2 | Temporal freshness | CRITICAL |
| V3 | RECENT CHANGES truthfulness | CRITICAL |
| V4 | MODULE COVERAGE accuracy | HIGH |
| V5 | KNOWN ISSUES hygiene | HIGH |
| V6 | Handoff specificity | HIGH |
| V7 | Additive update safety | MEDIUM |
| V8 | CURRENT STATE correctness | CRITICAL |
| V9 | TODO reflects reality | MEDIUM |

---

## STRUCTURAL VALIDATION

These checks can be automated (see marker response in BEHAVIORS_Project_State.md):

| Check | Method | Pass Condition |
|-------|--------|----------------|
| Section headers present | Regex `^## ` against expected list | All 10 headers found |
| Frontmatter non-empty | Regex for LAST_UPDATED/UPDATED_BY | Both fields have values |
| RECENT CHANGES bounded | Count `### ` under RECENT CHANGES | Count ≤ 7 |
| No empty sections | Check content between `## ` headers | Each section has ≥ 1 non-blank line |
| LAST_UPDATED freshness | Parse date, compare to now | ≤ 24h behind latest significant commit |
| MODULE COVERAGE paths exist | For each code path, check filesystem | All listed paths resolve |

**Design choice:** Structural validation only. Content quality (V3 truthfulness, V6 specificity, V8 correctness) requires agent judgment — enforced by culture and this doc, not by code.

---

## ERROR MESSAGES

| Violation | Message |
|-----------|---------|
| Missing section | `SYNC missing required section: ## {section_name}` |
| Empty frontmatter | `SYNC_Project_State.md: LAST_UPDATED is empty — file has no timestamp` |
| Stale timestamp | `SYNC is {days}d stale — LAST_UPDATED {date} but latest commit is {commit_date}` |
| Aspirational entry | `RECENT CHANGES entry "{title}" has no matching commit — remove or move to TODO` |
| Phantom module | `MODULE COVERAGE lists "{module}" but path {path} does not exist` |
| Missing module | `Directory {path} exists with {n} files but has no MODULE COVERAGE entry` |
| Stale known issue | `KNOWN ISSUES "{issue}" was fixed in {commit} but not marked Fixed` |
| Empty handoff | `HANDOFF: FOR AGENTS is empty — next agent has no orientation context` |
| Unbounded changelog | `RECENT CHANGES has {n} entries (max 7) — prune oldest` |
| Wrong repo described | `CURRENT STATE references {wrong_repo} capabilities — verify this describes mind-mcp` |

---

## MARKERS

<!-- @mind:response VALIDATION_REVIEW: Reviewed the full doc. 9 invariants, well-structured, priority matrix is right. Two things to flag:

TENSION — V2 uses 24h wall-time threshold for staleness. In my PATTERNS response I proposed commits_since_last_sync > 5 as a better heuristic, because pure time produces false positives during quiet periods (weekends, no commits = no drift, but 24h clock still ticks). Meanwhile, the STRUCTURAL VALIDATION table (line 231) says "≤ 24h behind latest significant commit" — but defining "significant" is a content judgment, which contradicts the "structural validation only" design choice (line 234). Proposal: V2 keeps the 24h rule as the INVARIANT (agents must honor it). The automated check uses commit-count (>5 commits since last SYNC update = WARN). This separates the human obligation (update within 24h) from the machine check (flag when commits accumulate). Both are correct, they just operate at different layers.

MISSING — No invariant for ACTIVE WORK staleness. V5 covers KNOWN ISSUES hygiene, V9 covers TODO reality, but nothing catches an ACTIVE WORK entry for a citizen who finished 2 weeks ago and forgot to update. ACTIVE WORK is the most time-sensitive section — it answers "who's doing what RIGHT NOW." Propose V10: ACTIVE WORK entries must correspond to genuinely active sessions. An entry older than 48h without a RECENT CHANGES update from that agent is a staleness candidate. This is automatable: cross-reference ACTIVE WORK agents against RECENT CHANGES authors and timestamps.

Otherwise: this is exactly the spec I need to implement the sync-state checks. V1's section list becomes the expected_headers array. V2's freshness becomes the commit-count check. V4's path validation becomes an os.path.exists loop. Straightforward. — @mind 2026-03-15 -->
