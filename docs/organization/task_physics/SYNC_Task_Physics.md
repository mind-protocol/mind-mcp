# Task Physics — Sync: Current State

```
LAST_UPDATED: 2026-03-15
UPDATED_BY: Claude (agent)
STATUS: CANONICAL
LAYER: L2 (Organization)
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Task_Physics.md
PATTERNS:        ./PATTERNS_Task_Physics.md
BEHAVIORS:       ./BEHAVIORS_Task_Physics.md
ALGORITHM:       ./ALGORITHM_Task_Physics.md
VALIDATION:      ./VALIDATION_Task_Physics.md
IMPLEMENTATION:  ./IMPLEMENTATION_Task_Physics.md
HEALTH:          ./HEALTH_Task_Physics.md
THIS:            SYNC_Task_Physics.md (you are here)

IMPL:            runtime/organization/task_physics.py (to be created)
```

---

## MATURITY

**What's canonical (docs):**
- Full doc chain: OBJECTIVES → PATTERNS → BEHAVIORS → ALGORITHM → VALIDATION → IMPLEMENTATION → HEALTH → SYNC
- 5 algorithms specified: urgency accumulation, completion cascade, crystallization, structural learning, completed task decay
- 7 invariants defined (V1-V7)
- 6 link types defined: CONTRIBUTES_TO, BLOCKS, REQUIRES, IMPLEMENTS, RESOLVES, MEMBER_OF
- 11 constants specified with defaults
- Cypher patterns for all graph operations
- Integration points with existing code identified

**What's not yet implemented:**
- `runtime/organization/task_physics.py` — the main implementation file
- `runtime/organization/task_constants.py` — constants file
- Physics tick integration (urgency + decay in tick loop)
- Dispatcher integration (cascade on completion)
- Health checkers (5 specified, none implemented)

**What's proposed (v2+):**
- Deadline-based urgency (Algorithm 1, Step 1 — spec'd but optional for v1)
- Cross-org task cascades (tasks in different orgs blocking each other)
- Task energy visualization for the platform UI

---

## CURRENT STATE

**Doc chain complete, implementation pending.**

This doc chain was created to formalize the L2 organizational task physics that was previously only conceptual. The existing task system (`docs/tools/task_routing/`) handles L1 routing (who does the task). This chain specifies the L2 thermodynamic effects (what happens to the graph when tasks are created, worked on, and completed).

### Relationship to Existing Code

| Existing Module | Current State | Integration Needed |
|-----------------|---------------|-------------------|
| `runtime/task_assignment.py` | Simple energy feedback (+0.1/+0.3) | Extend `record_task_outcome()` to call cascade |
| `runtime/organization/` | L2 org layer (access, settlement, lifecycle) | Add `task_physics.py` + `task_constants.py` |
| `runtime/physics/constants.py` | L1 physics constants | No change needed — task constants are separate |
| `runtime/orchestrator/dispatcher.py` | Task dispatch + citizen routing | Call `cascade_completion()` on task done |
| `runtime/physics/` tick loop | Runs Laws 1-18 per tick | Add urgency + decay computation per tick |

---

## RECENT CHANGES

### 2026-03-15: Doc Chain Creation

- **What:** Full 8-doc chain created from scratch
- **Why:** The L2 task physics (urgency, cascades, crystallization, learning) was described conceptually but had no formal specification. The existing task_routing docs only cover L1 routing (citizen selection).
- **Files:** `docs/organization/task_physics/` — 8 new files
- **Impact:** Provides complete spec for implementation. No code changes yet.

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** VIEW_Implement or VIEW_Extend

**Where I stopped:** Full doc chain written. Zero code. The spec is ready for implementation.

**What you need to understand:**
- This is L2 (organizational), not L1 (citizen cognition). Task physics lives in `runtime/organization/`, not in `runtime/cognition/`.
- The existing `record_task_outcome()` in `task_assignment.py` is the integration point — extend it, don't replace it.
- The tick loop needs two new calls: `compute_urgency()` for active tasks, `apply_task_decay()` for completed tasks.
- Cascades are event-driven (on completion), not tick-driven.

**Implementation order suggestion:**
1. Create `task_constants.py` (all constants from ALGORITHM doc)
2. Create `task_physics.py` with Algorithm 5 first (decay — simplest, testable independently)
3. Add Algorithm 1 (urgency accumulation — depends on link topology)
4. Add Algorithm 2 (cascade — depends on urgency being correct)
5. Add Algorithm 3 (crystallization — independent of energy)
6. Add Algorithm 4 (learning — depends on TRACE format)
7. Integrate with tick loop and dispatcher

**Watch out for:**
- `validate_blocks_link()` must be called BEFORE creating BLOCKS links, not after
- CASCADE_SURGE_FACTOR × energy_at_completion can exceed 5.0 if blocker energy was high — clamp
- The Cypher MERGE pattern for artifacts needs proper ON CREATE SET to be idempotent

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Created the full doc chain for L2 task physics — the thermodynamic layer that governs what happens when tasks are created and completed. This is the spec for urgency accumulation, dependency cascades, artifact crystallization, and structural learning. The existing task routing docs (L1) are untouched — they handle who does the task. This new chain handles what the task does to the graph.

**Decisions made:**
- Tasks are gravity wells (energy accumulates from dependency pressure)
- Completion triggers 4-phase cascade: energy collapse → dam break → crystallize → learn
- Completed tasks decay fast (2h half-life) but artifacts persist
- Urgency is emergent from topology, not from labels
- 11 constants with sensible defaults, all tunable

**Needs your input:**
- Should we implement this in `runtime/organization/task_physics.py` or integrate directly into existing physics files?
- TRACE format for crystallization — what fields should it contain?
- Deadline pressure (Algorithm 1, Step 1) — include in v1 or defer?

---

## TODO

### Immediate

- [ ] Create `runtime/organization/task_constants.py`
- [ ] Create `runtime/organization/task_physics.py` (Algorithms 1-5)
- [ ] Integrate urgency + decay into physics tick loop
- [ ] Integrate cascade into dispatcher completion path

### Later

- [ ] Implement health checkers (5 specified in HEALTH doc)
- [ ] Add TRACE format specification
- [ ] Add task energy visualization endpoint for platform UI
- [ ] Cross-org cascade support

---

## POINTERS

| What | Where |
|------|-------|
| L1 Task Routing (citizen selection) | `docs/tools/task_routing/` |
| L2 Org Layer (existing) | `runtime/organization/` |
| Physics Constants (L1) | `runtime/physics/constants.py` |
| Existing Energy Feedback | `runtime/task_assignment.py:record_task_outcome()` |
| Physics Tick Loop | `runtime/physics/` |
| Dispatcher Integration | `runtime/orchestrator/dispatcher.py` |
| Schema (link types) | `schema-l1.yaml`, `schema-l3.yaml` |
