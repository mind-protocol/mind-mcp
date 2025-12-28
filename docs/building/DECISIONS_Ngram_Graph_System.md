# DECISIONS: Mind Graph System
@mind:id: DECISIONS.MIND.GRAPH.SYSTEM

```
LAST_UPDATED: 2025-12-24
UPDATED_BY: Claude (escalation resolution)
STATUS: PROPOSED
```

---

## Purpose

This document resolves escalation markers from the Mind Graph System doc chain.
Each decision includes context, options considered, and the chosen approach.

**Status legend:**
- DECIDED — Human approved, implement as written
- PROPOSED — Agent recommendation, awaiting human review
- DEFERRED — Postponed to v2

---

## Multi-Agent Coordination

### D-COORD-01: Multiple agents triggered by same Moment

**Question:** Who goes first? Energy split? Sequential? Race condition risk?

**Decision:** PROPOSED — Sequential by energy order

- Agents triggered in descending energy order (highest first)
- Each agent completes before next starts
- No energy split — each sees full Moment energy
- No race condition — single-threaded execution
- If agent creates Moments, those queue for next tick

**Rationale:** Simplicity over parallelism. Deterministic ordering enables reproducibility.

---

### D-COORD-02: Agent in multiple Spaces with hot Moments

**Question:** Which Space triggers first if agent is in multiple Spaces?

**Decision:** PROPOSED — Highest energy Space wins

- Compare `sum(hot_moment.energy)` per Space
- Agent triggers in Space with highest total hot energy
- Tie-breaker: alphabetical Space ID (deterministic)

**Rationale:** Energy already represents salience. No new concept needed.

---

## Agent Lifecycle

### D-AGENT-01: Agent failure handling

**Question:** What happens if LLM call fails (timeout, error, partial response)?

**Decision:** PROPOSED — Retry once, then reject

1. First failure: Retry with exponential backoff (2s, 4s)
2. Second failure: Mark moment as `failed`, return energy to source
3. Log failure reason for debugging
4. Do NOT mark as `completed` — that would lie about success

**Rationale:** Graceful degradation. Energy conservation. Clear failure signal.

---

### D-AGENT-02: Agent mid-call injection

**Question:** If agent is mid-LLM-call and new hot Moment arrives?

**Decision:** PROPOSED — Queue for next tick

- Current call completes uninterrupted
- New hot Moment queued for next tick processing
- Agent awareness via `pending_moments` in context (optional)

**Rationale:** Atomic operations. Avoid partial state corruption.

---

### D-AGENT-03: Agent count strategy

**Question:** Fixed 6 agents or dynamic spawn?

**Decision:** PROPOSED — Fixed pool, dynamic assignment

- Fixed agent pool defined at startup (e.g., 6 agents)
- Agents dynamically assigned to Spaces based on hot Narratives
- No runtime agent creation/destruction
- Configuration in `agents.yaml`

**Rationale:** Predictable resource usage. Simpler orchestration.

---

### D-AGENT-04: Agent Space assignment

**Question:** Initial assignment to which Space(s)?

**Decision:** PROPOSED — Start in all Spaces, narrow by activity

- Agents initially available to all Spaces
- First trigger narrows to triggering Space
- Can be reassigned if Space goes cold (no hot Narratives for N ticks)

**Rationale:** Lazy binding. Agents find work naturally.

---

## Bootstrap

### D-BOOT-01: Bootstrap sequence

**Question:** How does the world start? First Moment before agents exist?

**Decision:** PROPOSED — Human seeds, then agents wake

1. Human creates initial Moments (seed content)
2. Human sets one Moment to `active` with energy > 0
3. First tick: physics runs, finds hot Narrative
4. Agent triggers on hot Narrative, creates response Moments
5. Loop continues

**Rationale:** Human provides initial spark. Agents respond to energy.

---

## Query/Response Format

### D-QUERY-01: Agent query mechanism

**Question:** How do agents query context from graph?

**Decision:** PROPOSED — Structured context injection

- Engine provides `get_context(agent_id, space_id)` → structured dict
- Context includes: hot_narratives, recent_moments, active_goals, relevant_actors
- Agent receives context as system prompt section
- No direct graph queries from agent

**Rationale:** Engine controls what agents see. Prevents unbounded exploration.

---

### D-QUERY-02: Agent response format

**Question:** How to reliably extract Moments/Narratives from LLM response?

**Decision:** PROPOSED — Structured JSON output

- Agents output structured JSON (not freeform prose)
- Schema: `{moments: [...], narratives: [...], links: [...]}`
- Validation before graph mutation
- Parse failure → retry with schema reminder

**Rationale:** Reliable extraction. Schema enforcement. Machine-readable.

---

### D-QUERY-03: Opening message contents

**Question:** What goes in the opening message to agent?

**Decision:** PROPOSED — Minimal focused context

```
1. Agent identity (who you are)
2. Current Space (where you are)
3. Hot Narratives (what's happening)
4. Recent Moments (what just happened)
5. Active Goals (what to pursue)
6. Output schema (what to produce)
```

**Rationale:** Focus over exhaustiveness. Agents don't need everything.

---

### D-QUERY-04: Human query mechanism

**Question:** How does human query graph directly?

**Decision:** PROPOSED — Connectome UI + CLI

- Connectome UI for visual exploration
- `mind query` CLI for structured queries
- No direct Cypher access (too dangerous)
- Query language: find/links/related/contents (membrane spec)

**Rationale:** Controlled access. UI for exploration, CLI for automation.

---

## Space/Scope

### D-SPACE-01: Agent leaving a Space

**Question:** Explicit move action? Or just add to new Space? Can agent be in 0 Spaces?

**Decision:** PROPOSED — Implicit via activity

- Agent doesn't explicitly "leave"
- Activity in new Space → agent "present" there
- Agent can be in multiple Spaces simultaneously
- Presence = has created Moments in Space within last N ticks
- 0 Spaces = idle, available for any hot trigger

**Rationale:** Presence is emergent from activity. No explicit state management.

---

### D-SPACE-02: Narrative in multiple Spaces

**Question:** Does Narrative appear in both contexts? Energy split?

**Decision:** PROPOSED — Shared Narrative, no energy split

- Narrative can be `contains` linked to multiple Spaces
- Same Narrative instance (no duplication)
- Energy is property of Narrative, not per-Space
- Agents in either Space can see/respond to it

**Rationale:** Narratives are graph entities, not per-Space copies.

---

### D-SPACE-03: Module naming dispatcher

**Question:** How do we map file paths to module Spaces?

**Decision:** PROPOSED — `modules.yaml` mapping

- Use `modules.yaml` as authoritative mapping
- `code` pattern → `docs` path → Space ID
- Space ID = module name (e.g., `engine_physics`)
- Fallback: parent directory as Space

**Rationale:** Already have `modules.yaml`. Don't reinvent.

---

## Energy/Strength

### D-ENERGY-01: Strength unbounded accumulation

**Question:** Over years, doesn't everything max out?

**Decision:** PROPOSED — Soft cap with logarithmic growth

- No hard cap on strength
- Growth formula: `new_strength = strength + delta / (1 + strength)`
- At strength=10, delta=1 adds only 0.09
- Practical ceiling ~15-20 without hard limit

**Rationale:** Diminishing returns. Old things stabilize, new things can still grow.

---

### D-ENERGY-02: Stuck goals

**Question:** Goals that never complete because they keep getting referenced?

**Decision:** PROPOSED — Staleness detection

- Track `last_progress_tick` per goal
- Goal with no progress for N ticks → `stale` flag
- Stale goals eligible for agent review ("should this close?")
- Human can force-close via UI

**Rationale:** Detect stuckness. Don't auto-close (might be intentional).

---

## Ingest

### D-INGEST-01: Incremental ingest

**Question:** How to handle docs created/modified after bootstrap?

**Decision:** PROPOSED — File watcher + manual re-ingest

- File watcher detects changes (inotify/fswatch)
- Changed files queue for re-ingest
- `mind ingest --changed` processes queue
- Full re-ingest via `mind ingest --full`

**Rationale:** Incremental for speed. Full for recovery.

---

### D-INGEST-02: Type inference correction

**Question:** Type inference is heuristic. Should agents be able to correct/reclassify?

**Decision:** PROPOSED — Yes, via Narrative update

- Agents can create Narrative with corrected type
- Old Narrative gets `superseded_by` link to new
- Human can also reclassify via UI
- No automatic deletion (audit trail)

**Rationale:** Agents are smart. Let them fix mistakes.

---

## Deferred to v2

The following are explicitly deferred:

| ID | Question | Reason |
|----|----------|--------|
| D2 | Speed modes x1/x2/x3 in multiplayer | No multiplayer in v1 |
| - | Distributed graph support | Single-node in v1 |
| - | Real-time streaming | Batch tick in v1 |

---

## How to Use This Document

1. **Human review:** Accept/modify/reject each PROPOSED decision
2. **Mark DECIDED:** Change status when human approves
3. **Implement:** Reference decision ID in code comments
4. **Remove escalations:** Once DECIDED, remove corresponding `@mind:escalation` marker

---

## CHAIN

- **Related:** PATTERNS_Mind_Graph_System.md, ALGORITHM_Mind_Graph_System.md
- **Implements:** Escalation resolution per VALIDATION invariants
