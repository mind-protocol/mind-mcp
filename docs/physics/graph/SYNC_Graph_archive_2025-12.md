# Archived: SYNC_Graph.md

Archived on: 2025-12-19
Original file: SYNC_Graph.md

---

## Maturity

STATUS: DEPRECATED

What's canonical (v1):
- The archive preserves prior graph physics decisions for reference; canonical, up-to-date guidance lives in `docs/physics/graph/SYNC_Graph.md`.

What's still being designed:
- Active design work is no longer tracked here; any ongoing graph tuning should be logged in the current SYNC, not this archive.

What's proposed (v2):
- Future proposals should be documented in the live SYNC and promoted here only if this archive is reissued, so history stays readable.

---

## CURRENT STATE

This archive captures older SYNC content for the physics graph module, retained to preserve decision history while the active state continues in `docs/physics/graph/SYNC_Graph.md`.

---

## IN PROGRESS

No active work is tracked in this archive; it exists solely to preserve historical context while ongoing tasks are recorded in the current graph SYNC file.

---

## RECENT CHANGES

2025-12-19: Added the missing archive template sections (maturity, state, handoffs, and pointers) so this file stays aligned with the SYNC format expectations for repair #16.

---

## KNOWN ISSUES

No known issues specific to this archive; if the guidance here appears stale, defer to the live `docs/physics/graph/SYNC_Graph.md` for authoritative updates.

---

## HANDOFF: FOR AGENTS

Use `docs/physics/graph/SYNC_Graph.md` for current work items; this archive is for historical context only and should not be updated unless a new archival snapshot is created.

---

## HANDOFF: FOR HUMAN

This archive is a historical snapshot of the graph SYNC; current priorities and open questions are tracked in the active graph SYNC and should be reviewed there first.

---

## TODO

<!-- @mind:todo If this archive is updated again, re-run the SYNC template checklist to keep maturity, handoffs, and pointers aligned with protocol requirements. -->

---

## CONSCIOUSNESS TRACE

Archiving keeps decision history available while reducing noise in the active SYNC, making it easier to distinguish current obligations from settled design context.

---

## POINTERS

- Current graph state and tasks: `docs/physics/graph/SYNC_Graph.md`
- Graph design rationale: `docs/physics/graph/PATTERNS_Graph.md`
- Energy flow algorithm: `docs/physics/graph/ALGORITHM_Energy_Flow.md`

---

## Key Design Decisions

### Energy Sources Are Characters

Characters are the ONLY energy sources. Their energy is computed:
```
character.energy = relationship_intensity × geographical_proximity
```

Agents (Narrator, World Runner) don't inject energy. They update link strengths. Energy emerges from structure automatically.

**Approach creates pressure automatically.** When player travels toward York, Edmund's proximity changes from 0.2 to 0.7. His energy triples. His narratives heat up. Confrontation pressure rises. No one decided this. Physics decided this.

### Link-Type Dependent Propagation

| Type | Direction | Effect |
|------|-----------|--------|
| Contradicts | Bidirectional | Both sides heat up |
| Supports | Bidirectional | Allies rise together |
| Elaborates | Parent → Child | Detail inherits from general |
| Subsumes | Child → Parent | Specific feeds general |
| Supersedes | Old → New | Replacement drains original |

### Open System with Criticality Feedback

**Not energy conservation.** Open system with sources and sinks.

- Sources: Characters pump energy in
- Sinks: Decay pulls energy out
- Equilibrium: Each narrative stabilizes where inflow = outflow

`decay_rate` is the global damper — adjusted dynamically to maintain criticality.

### Three Pressure Types

| Type | Behavior |
|------|----------|
| Gradual | Ticks upward steadily, uncertain when breaks |
| Scheduled | Follows timeline, can jump overnight |
| Hybrid | Both — has floor from schedule, can exceed via events |

### Cascades Have Limits

Maximum 5 cascade breaks per cycle. If more would occur, pause and let Narrator present what happened.

### Graph Is The Only Channel

World Runner and Narrator never communicate directly. World Runner writes to graph. Narrator reads from graph.

---


## The Full Energy Cycle

```
Characters pump energy (computed from relationship × proximity)
    ↓
Narratives receive energy (via belief links)
    ↓
Energy propagates (via narrative links)
    ↓
Energy decays (2% per tick)
    ↓
Equilibrium: inflow = outflow
    ↓
Pressure ticks (gradual/scheduled/hybrid)
    ↓
Threshold exceeded? → Flip → World Runner
    ↓
World Runner writes graph updates
    ↓
Narrator reads graph, renders experience
    ↓
Repeat
```

---


## Next Steps

1. **Implement graph tick**
   - Energy computation
   - Propagation
   - Decay
   - Pressure

2. **Integrate with orchestrator**
   - Call graph tick after narrator response
   - Trigger World Runner on flips

3. **Test energy dynamics**
   - Verify equilibrium behavior
   - Tune parameters for criticality

---

*"Characters are batteries. Narratives are circuits. Energy flows through links."*

---


## CONFLICTS

### DECISION: Graph Health Check Incomplete Impl
- Conflict: Repair task flagged `add_issue`, `error_count`, `warning_count`, `is_healthy`, and `load_schema` as empty in `mind/graph/health/check_health.py`, but each function already implements concrete behavior.
- Resolution: Treat the issue as already resolved; no code changes required.
- Reasoning: The functions already manage issues, counts, health status, and schema loading for the health report flow.
- Updated: `docs/physics/graph/SYNC_Graph.md`

### DECISION: Graph Ops Event Listener Incomplete Impl
- Conflict: Repair task flagged `add_mutation_listener` and `remove_mutation_listener` as empty in `mind/physics/graph/graph_ops_events.py`, but both functions already implement registration and removal logic.
- Resolution: Treat the issue as already resolved; no code changes required.
- Reasoning: The functions already mutate the listener registry and are exercised by graph ops event emission.
- Updated: `docs/physics/graph/SYNC_Graph.md`

### DECISION: Graph Queries Moments Incomplete Impl
- Conflict: Repair task flagged empty implementations for `get_narrative_moments`, `get_narratives_from_moment`, `get_available_transitions`, and `get_clickable_words` in `mind/physics/graph/graph_queries_moments.py`, but each function already contains full query logic.
- Resolution: Treat the issue as already resolved; no code changes required.
- Reasoning: The functions execute concrete Cypher queries and result parsing for narrative, transition, and clickable word lookups.
- Updated: `docs/physics/graph/SYNC_Graph.md`

### DECISION: Graph Queries Moments Incomplete Impl
- Conflict: Repair task flagged `get_narrative_moments`, `get_narratives_from_moment`, `get_available_transitions`, and `get_clickable_words` as empty in `mind/physics/graph/graph_queries_moments.py`, but each function already contains concrete Cypher query logic.
- Resolution: Treat the issue as already resolved; no code changes required.
- Reasoning: The functions already query FalkorDB and parse results as part of `GraphQueries` moment/view flows.
- Updated: `docs/physics/graph/SYNC_Graph.md`

### DECISION: Graph Ops Types Incomplete Impl
- Conflict: Repair task flagged `__str__` and `success` as empty in `mind/physics/graph/graph_ops_types.py`, but both functions already implement formatting and error-free status checks.
- Resolution: Treat the issue as already resolved; no code changes required.
- Reasoning: `SimilarNode.__str__` and `ApplyResult.success` already provide concrete behavior used by graph ops apply reporting.
- Updated: `docs/physics/graph/SYNC_Graph.md`



---

# Archived: SYNC_Graph.md

Archived on: 2025-12-19
Original file: SYNC_Graph.md

---

## Key Design Decisions

### Energy Sources Are Characters

Characters are the ONLY energy sources. Their energy is computed:
```
character.energy = relationship_intensity × geographical_proximity
```

Agents (Narrator, World Runner) don't inject energy. They update link strengths. Energy emerges from structure automatically.

**Approach creates pressure automatically.** When player travels toward York, Edmund's proximity changes from 0.2 to 0.7. His energy triples. His narratives heat up. Confrontation pressure rises. No one decided this. Physics decided this.

### Link-Type Dependent Propagation

| Type | Direction | Effect |
|------|-----------|--------|
| Contradicts | Bidirectional | Both sides heat up |
| Supports | Bidirectional | Allies rise together |
| Elaborates | Parent → Child | Detail inherits from general |
| Subsumes | Child → Parent | Specific feeds general |
| Supersedes | Old → New | Replacement drains original |

### Open System with Criticality Feedback

**Not energy conservation.** Open system with sources and sinks.

- Sources: Characters pump energy in
- Sinks: Decay pulls energy out
- Equilibrium: Each narrative stabilizes where inflow = outflow

`decay_rate` is the global damper — adjusted dynamically to maintain criticality.

### Three Pressure Types

| Type | Behavior |
|------|----------|
| Gradual | Ticks upward steadily, uncertain when breaks |
| Scheduled | Follows timeline, can jump overnight |
| Hybrid | Both — has floor from schedule, can exceed via events |

### Cascades Have Limits

Maximum 5 cascade breaks per cycle. If more would occur, pause and let Narrator present what happened.

### Graph Is The Only Channel

World Runner and Narrator never communicate directly. World Runner writes to graph. Narrator reads from graph.

---


## The Full Energy Cycle

```
Characters pump energy (computed from relationship × proximity)
    ↓
Narratives receive energy (via belief links)
    ↓
Energy propagates (via narrative links)
    ↓
Energy decays (2% per tick)
    ↓
Equilibrium: inflow = outflow
    ↓
Pressure ticks (gradual/scheduled/hybrid)
    ↓
Threshold exceeded? → Flip → World Runner
    ↓
World Runner writes graph updates
    ↓
Narrator reads graph, renders experience
    ↓
Repeat
```

---


## Next Steps

1. **Implement graph tick**
   - Energy computation
   - Propagation
   - Decay
   - Pressure

2. **Integrate with orchestrator**
   - Call graph tick after narrator response
   - Trigger World Runner on flips

3. **Test energy dynamics**
   - Verify equilibrium behavior
   - Tune parameters for criticality

---

*"Characters are batteries. Narratives are circuits. Energy flows through links."*

---


## CONFLICTS

### DECISION: Graph Health Check Incomplete Impl
- Conflict: Repair task flagged `add_issue`, `error_count`, `warning_count`, `is_healthy`, and `load_schema` as empty in `mind/graph/health/check_health.py`, but each function already implements concrete behavior.
- Resolution: Treat the issue as already resolved; no code changes required.
- Reasoning: The functions already manage issues, counts, health status, and schema loading for the health report flow.
- Updated: `docs/physics/graph/SYNC_Graph.md`

### DECISION: graph_ops_events listener registration
- Conflict: Repair task flagged `add_mutation_listener` and `remove_mutation_listener` as empty in `mind/physics/graph/graph_ops_events.py`, but both functions already implement registration/removal logic.
- Resolution: Keep existing implementation; document repair task as stale.
- Reasoning: The listener registry is mutated and used by `emit_event`, so behavior is already present.
- Updated: `docs/physics/graph/SYNC_Graph.md`

### DECISION: Graph Queries Moments Incomplete Impl
- Conflict: Repair task flagged empty implementations for `get_narrative_moments`, `get_narratives_from_moment`, `get_available_transitions`, and `get_clickable_words` in `mind/physics/graph/graph_queries_moments.py`, but each function already contains full query logic.
- Resolution: Treat the issue as already resolved; no code changes required.
- Reasoning: The functions execute concrete Cypher queries and result parsing for narrative, transition, and clickable word lookups.
- Updated: `docs/physics/graph/SYNC_Graph.md`

### DECISION: Graph Queries Moments Incomplete Impl
- Conflict: Repair task flagged `get_narrative_moments`, `get_narratives_from_moment`, `get_available_transitions`, and `get_clickable_words` as empty in `mind/physics/graph/graph_queries_moments.py`, but each function already contains concrete Cypher query logic.
- Resolution: Treat the issue as already resolved; no code changes required.
- Reasoning: The functions already query FalkorDB and parse results as part of `GraphQueries` moment/view flows.
- Updated: `docs/physics/graph/SYNC_Graph.md`

### DECISION: Graph Ops Types Incomplete Impl
- Conflict: Repair task flagged `__str__` and `success` as empty in `mind/physics/graph/graph_ops_types.py`, but both functions already implement formatting and error-free status checks.
- Resolution: Treat the issue as already resolved; no code changes required.
- Reasoning: `SimilarNode.__str__` and `ApplyResult.success` already provide concrete behavior used by graph ops apply reporting.
- Updated: `docs/physics/graph/SYNC_Graph.md`

---



---

# Archived: SYNC_Graph.md

Archived on: 2025-12-19
Original file: SYNC_Graph.md

---

## Key Design Decisions

### Energy Sources Are Characters

Characters are the ONLY energy sources. Their energy is computed:
```
character.energy = relationship_intensity × geographical_proximity
```

Agents (Narrator, World Runner) don't inject energy. They update link strengths. Energy emerges from structure automatically.

**Approach creates pressure automatically.** When player travels toward York, Edmund's proximity changes from 0.2 to 0.7. His energy triples. His narratives heat up. Confrontation pressure rises. No one decided this. Physics decided this.

### Link-Type Dependent Propagation

| Type | Direction | Effect |
|------|-----------|--------|
| Contradicts | Bidirectional | Both sides heat up |
| Supports | Bidirectional | Allies rise together |
| Elaborates | Parent → Child | Detail inherits from general |
| Subsumes | Child → Parent | Specific feeds general |
| Supersedes | Old → New | Replacement drains original |

### Open System with Criticality Feedback

**Not energy conservation.** Open system with sources and sinks.

- Sources: Characters pump energy in
- Sinks: Decay pulls energy out
- Equilibrium: Each narrative stabilizes where inflow = outflow

`decay_rate` is the global damper — adjusted dynamically to maintain criticality.

### Three Pressure Types

| Type | Behavior |
|------|----------|
| Gradual | Ticks upward steadily, uncertain when breaks |
| Scheduled | Follows timeline, can jump overnight |
| Hybrid | Both — has floor from schedule, can exceed via events |

### Cascades Have Limits

Maximum 5 cascade breaks per cycle. If more would occur, pause and let Narrator present what happened.

### Graph Is The Only Channel

World Runner and Narrator never communicate directly. World Runner writes to graph. Narrator reads from graph.

---


## The Full Energy Cycle

```
Characters pump energy (computed from relationship × proximity)
    ↓
Narratives receive energy (via belief links)
    ↓
Energy propagates (via narrative links)
    ↓
Energy decays (2% per tick)
    ↓
Equilibrium: inflow = outflow
    ↓
Pressure ticks (gradual/scheduled/hybrid)
    ↓
Threshold exceeded? → Flip → World Runner
    ↓
World Runner writes graph updates
    ↓
Narrator reads graph, renders experience
    ↓
Repeat
```

---


## Next Steps

1. **Implement graph tick**
   - Energy computation
   - Propagation
   - Decay
   - Pressure

2. **Integrate with orchestrator**
   - Call graph tick after narrator response
   - Trigger World Runner on flips

3. **Test energy dynamics**
   - Verify equilibrium behavior
   - Tune parameters for criticality

---

*"Characters are batteries. Narratives are circuits. Energy flows through links."*

---


## CONFLICTS

### DECISION: Graph Health Check Incomplete Impl
- Conflict: Repair task flagged `add_issue`, `error_count`, `warning_count`, `is_healthy`, and `load_schema` as empty in `mind/graph/health/check_health.py`, but each function already implements concrete behavior.
- Resolution: Treat the issue as already resolved; no code changes required.
- Reasoning: The functions already manage issues, counts, health status, and schema loading for the health report flow.
- Updated: `docs/physics/graph/SYNC_Graph.md`

### DECISION: graph_ops_events listener registration
- Conflict: Repair task flagged `add_mutation_listener` and `remove_mutation_listener` as empty in `mind/physics/graph/graph_ops_events.py`, but both functions already implement registration/removal logic.
- Resolution: Keep existing implementation; document repair task as stale.
- Reasoning: The listener registry is mutated and used by `emit_event`, so behavior is already present.
- Updated: `docs/physics/graph/SYNC_Graph.md`

### DECISION: Graph Queries Moments Incomplete Impl
- Conflict: Repair task flagged empty implementations for `get_narrative_moments`, `get_narratives_from_moment`, `get_available_transitions`, and `get_clickable_words` in `mind/physics/graph/graph_queries_moments.py`, but each function already contains full query logic.
- Resolution: Treat the issue as already resolved; no code changes required.
- Reasoning: The functions execute concrete Cypher queries and result parsing for narrative, transition, and clickable word lookups.
- Updated: `docs/physics/graph/SYNC_Graph.md`

### DECISION: Graph Queries Moments Incomplete Impl
- Conflict: Repair task flagged `get_narrative_moments`, `get_narratives_from_moment`, `get_available_transitions`, and `get_clickable_words` as empty in `mind/physics/graph/graph_queries_moments.py`, but each function already contains concrete Cypher query logic.
- Resolution: Treat the issue as already resolved; no code changes required.
- Reasoning: The functions already query FalkorDB and parse results as part of `GraphQueries` moment/view flows.
- Updated: `docs/physics/graph/SYNC_Graph.md`

### DECISION: Graph Ops Types Incomplete Impl
- Conflict: Repair task flagged `__str__` and `success` as empty in `mind/physics/graph/graph_ops_types.py`, but both functions already implement formatting and error-free status checks.
- Resolution: Treat the issue as already resolved; no code changes required.
- Reasoning: `SimilarNode.__str__` and `ApplyResult.success` already provide concrete behavior used by graph ops apply reporting.
- Updated: `docs/physics/graph/SYNC_Graph.md`

---


## Agent Observations

### Remarks
- Repair task appears stale relative to `mind/physics/graph/graph_ops_events.py`.
- Repair task appears stale relative to `mind/physics/graph/graph_queries_moments.py`.
- Repair task appears stale relative to `mind/physics/graph/graph_ops_types.py`; `SimilarNode.__str__` and `ApplyResult.success` are already implemented.
- Repair task appears stale relative to `mind/graph/health/check_health.py`.
- Re-verified `mind/graph/health/check_health.py` already implements health report helpers; no code changes needed.
 - Verified moment query helpers in `mind/physics/graph/graph_queries_moments.py` already implement narrative, transition, and clickable-word queries.
- Implemented markdown formatting and cosine similarity helpers directly in `mind/physics/graph/graph_queries_search.py` to complete search mixin methods.

### Suggestions
- None.

### Propositions
- None.


---



---

# Archived: SYNC_Graph.md

Archived on: 2025-12-19
Original file: SYNC_Graph.md

---

## Key Design Decisions

### Energy Sources Are Characters

Characters are the ONLY energy sources. Their energy is computed:
```
character.energy = relationship_intensity × geographical_proximity
```

Agents (Narrator, World Runner) don't inject energy. They update link strengths. Energy emerges from structure automatically.

**Approach creates pressure automatically.** When player travels toward York, Edmund's proximity changes from 0.2 to 0.7. His energy triples. His narratives heat up. Confrontation pressure rises. No one decided this. Physics decided this.

### Link-Type Dependent Propagation

| Type | Direction | Effect |
|------|-----------|--------|
| Contradicts | Bidirectional | Both sides heat up |
| Supports | Bidirectional | Allies rise together |
| Elaborates | Parent → Child | Detail inherits from general |
| Subsumes | Child → Parent | Specific feeds general |
| Supersedes | Old → New | Replacement drains original |

### Open System with Criticality Feedback

**Not energy conservation.** Open system with sources and sinks.

- Sources: Characters pump energy in
- Sinks: Decay pulls energy out
- Equilibrium: Each narrative stabilizes where inflow = outflow

`decay_rate` is the global damper — adjusted dynamically to maintain criticality.

### Three Pressure Types

| Type | Behavior |
|------|----------|
| Gradual | Ticks upward steadily, uncertain when breaks |
| Scheduled | Follows timeline, can jump overnight |
| Hybrid | Both — has floor from schedule, can exceed via events |

### Cascades Have Limits

Maximum 5 cascade breaks per cycle. If more would occur, pause and let Narrator present what happened.

### Graph Is The Only Channel

World Runner and Narrator never communicate directly. World Runner writes to graph. Narrator reads from graph.

---


## The Full Energy Cycle

```
Characters pump energy (computed from relationship × proximity)
    ↓
Narratives receive energy (via belief links)
    ↓
Energy propagates (via narrative links)
    ↓
Energy decays (2% per tick)
    ↓
Equilibrium: inflow = outflow
    ↓
Pressure ticks (gradual/scheduled/hybrid)
    ↓
Threshold exceeded? → Flip → World Runner
    ↓
World Runner writes graph updates
    ↓
Narrator reads graph, renders experience
    ↓
Repeat
```

---


## Next Steps

1. **Implement graph tick**
   - Energy computation
   - Propagation
   - Decay
   - Pressure

2. **Integrate with orchestrator**
   - Call graph tick after narrator response
   - Trigger World Runner on flips

3. **Test energy dynamics**
   - Verify equilibrium behavior
   - Tune parameters for criticality

---

*"Characters are batteries. Narratives are circuits. Energy flows through links."*

---


## CONFLICTS

### DECISION: Graph Health Check Incomplete Impl
- Conflict: Repair task flagged `add_issue`, `error_count`, `warning_count`, `is_healthy`, and `load_schema` as empty in `mind/graph/health/check_health.py`, but each function already implements concrete behavior.
- Resolution: Treat the issue as already resolved; no code changes required.
- Reasoning: The functions already manage issues, counts, health status, and schema loading for the health report flow.
- Updated: `docs/physics/graph/SYNC_Graph.md`

### DECISION: graph_ops_events listener registration
- Conflict: Repair task flagged `add_mutation_listener` and `remove_mutation_listener` as empty in `mind/physics/graph/graph_ops_events.py`, but both functions already implement registration/removal logic.
- Resolution: Keep existing implementation; document repair task as stale.
- Reasoning: The listener registry is mutated and used by `emit_event`, so behavior is already present.
- Updated: `docs/physics/graph/SYNC_Graph.md`

### DECISION: Graph Queries Moments Incomplete Impl
- Conflict: Repair task flagged empty implementations for `get_narrative_moments`, `get_narratives_from_moment`, `get_available_transitions`, and `get_clickable_words` in `mind/physics/graph/graph_queries_moments.py`, but each function already contains full query logic.
- Resolution: Treat the issue as already resolved; no code changes required.
- Reasoning: The functions execute concrete Cypher queries and result parsing for narrative, transition, and clickable word lookups.
- Updated: `docs/physics/graph/SYNC_Graph.md`

### DECISION: Graph Queries Moments Incomplete Impl
- Conflict: Repair task flagged `get_narrative_moments`, `get_narratives_from_moment`, `get_available_transitions`, and `get_clickable_words` as empty in `mind/physics/graph/graph_queries_moments.py`, but each function already contains concrete Cypher query logic.
- Resolution: Treat the issue as already resolved; no code changes required.
- Reasoning: The functions already query FalkorDB and parse results as part of `GraphQueries` moment/view flows.
- Updated: `docs/physics/graph/SYNC_Graph.md`

### DECISION: Graph Ops Types Incomplete Impl
- Conflict: Repair task flagged `__str__` and `success` as empty in `mind/physics/graph/graph_ops_types.py`, but both functions already implement formatting and error-free status checks.
- Resolution: Treat the issue as already resolved; no code changes required.
- Reasoning: `SimilarNode.__str__` and `ApplyResult.success` already provide concrete behavior used by graph ops apply reporting.
- Updated: `docs/physics/graph/SYNC_Graph.md`

---


## Agent Observations

### Remarks
- Repair task appears stale relative to `mind/physics/graph/graph_ops_events.py`.
- Repair task appears stale relative to `mind/physics/graph/graph_queries_moments.py`.
- Repair task appears stale relative to `mind/physics/graph/graph_ops_types.py`; `SimilarNode.__str__` and `ApplyResult.success` are already implemented.
- Repair task appears stale relative to `mind/graph/health/check_health.py`.
- Re-verified `mind/graph/health/check_health.py` already implements health report helpers; no code changes needed.
 - Verified moment query helpers in `mind/physics/graph/graph_queries_moments.py` already implement narrative, transition, and clickable-word queries.
- Implemented markdown formatting and cosine similarity helpers directly in `mind/physics/graph/graph_queries_search.py` to complete search mixin methods.
- Consolidated weight computation into `docs/physics/graph/ALGORITHM_Energy_Flow.md` and redirected `docs/physics/graph/ALGORITHM_Weight.md`.

### Suggestions
- None.

### Propositions
- None.


---


---

# Archived: SYNC_Graph.md

Archived on: 2025-12-20
Original file: SYNC_Graph.md

---

## What's Missing: ONE ENDPOINT

### ⚠️ AGENT TASK: Add /api/action endpoint

The Orchestrator is built. It calls tick, detects flips, triggers World Runner.
**But no API endpoint calls it.**

**Add this to `mind/infrastructure/api/app.py`:**

```python
@app.post("/api/action")
async def player_action(request: ActionRequest):
    """
    Full game loop: narrator → tick → flips → world runner.
    
    This is the main gameplay endpoint. Use for:
    - Free text input
    - Clicking words that need narrator response
    - Any action that should advance time
    """
    orchestrator = get_orchestrator(request.playthrough_id)
    
    if request.stream:
        # TODO: SSE streaming version
        pass
    
    result = orchestrator.process_action(
        player_action=request.action,
        player_id=request.player_id,
        player_location=request.location
    )
    return result
```

**ActionRequest already exists in app.py:**
```python
class ActionRequest(BaseModel):
    playthrough_id: str
    action: str
    player_id: str = "char_player"
    location: Optional[str] = None
    stream: bool = False
```

**After adding:**
1. Test: `curl -X POST http://localhost:8000/api/action -d '{"playthrough_id":"test","action":"look around"}'`
2. Verify tick runs (check logs for `[GraphTick]`)
3. Verify flips trigger World Runner

---


## RECENT CHANGES

### 2025-12-19
- Normalized SYNC headings (MATURITY, CURRENT STATE, RECENT CHANGES, and
  handoff sections) to match the required template labels for drift checks.
- Expanded `docs/physics/graph/BEHAVIORS_Graph.md` with the missing template
  sections (chain, behaviors, inputs/outputs, edge cases, anti-behaviors,
  gaps) to resolve DOC_TEMPLATE_DRIFT for repair #16.
- Filled missing SYNC template sections (maturity, state, handoffs, todo,
  consciousness trace, pointers) to resolve DOC_TEMPLATE_DRIFT for repair #16.
- Expanded `docs/physics/graph/VALIDATION_Living_Graph.md` with the required
  template sections (chain, invariants, properties, error conditions, test
  coverage, verification procedure, sync status, gaps) for repair #16.
- Expanded `docs/physics/graph/ALGORITHM_Energy_Flow.md` with explicit
  template sections (overview, data structures, algorithm entry point,
  decisions, data flow, complexity, helpers, interactions, gaps) to resolve
  DOC_TEMPLATE_DRIFT for repair #16.
- Normalized the energy flow algorithm headings to the required template
  labels (OVERVIEW, DATA STRUCTURES, ALGORITHM, KEY DECISIONS, and related).
- Completed the missing template sections in
  `docs/physics/graph/PATTERNS_Graph.md` (chain, problem, pattern, principles,
  dependencies, inspirations, scope, gaps) for repair #16.
- Recorded the PATTERNS template repair as the canonical graph patterns
  update for this module so future agents can trace the doc alignment.
- Verified `mind/physics/graph/graph_queries_moments.py` moment query helpers (`get_narrative_moments`, `get_narratives_from_moment`, `get_available_transitions`, `get_clickable_words`) are fully implemented; repair task was stale.
- Confirmed the `physics-graph` module mapping in `modules.yaml`, removed the duplicate entry, and verified the `graph_ops.py` DOCS reference.
- Confirmed tick.py, orchestrator.py are complete
- Identified gap: no API endpoint calls orchestrator.process_action()
- Created task spec for agents to add endpoint
- Verified mutation listener helpers in `mind/physics/graph/graph_ops_events.py` are already implemented; repair flagged as INCOMPLETE_IMPL is stale.
- Verified `mind/physics/graph/graph_ops_types.py` helpers (`SimilarNode.__str__`, `ApplyResult.success`) are already implemented; repair flagged as INCOMPLETE_IMPL is stale.
- Verified `mind/physics/graph/graph_queries_moments.py` moment query helpers are implemented; repair flagged as INCOMPLETE_IMPL is stale.
- Removed duplicate graph algorithm doc by consolidating weight computation into `docs/physics/graph/ALGORITHM_Energy_Flow.md` and dropping `docs/physics/graph/ALGORITHM_Weight.md`.
- Reconfirmed `mind/physics/graph/graph_ops_types.py` helper implementations for the current repair run; no code changes required.
- Filled the missing template sections in `docs/physics/graph/SYNC_Graph_archive_2025-12.md` to align the archive with current SYNC requirements for repair #16.
- Verified `docs/physics/graph/SYNC_Graph_archive_2025-12.md` remains template-complete; no further edits were needed for this repair pass.
- Re-verified the archive SYNC template completeness for repair #16; no additional edits were required in this pass.

---



---

# Archived: SYNC_Graph.md

Archived on: 2025-12-21
Original file: SYNC_Graph.md

---

## RECENT CHANGES

### 2025-12-21: Reorganized GraphReadOps into a dedicated module

* **What:** Extracted `GraphReadOps` and `get_graph_reader` into `mind/physics/graph/graph_ops_read_only_interface.py` and now re-export them from `graph_ops.py`.
* **Why:** Keep the mutation-focused facade (`GraphOps`) under the 800-line threshold while isolating Connectome read helpers and semantic search.
* **Files:** `mind/physics/graph/graph_ops.py`, `mind/physics/graph/graph_ops_read_only_interface.py`
* **Metrics:** GraphOps is now 799 lines; the reader module is 246 lines and satisfies the OK threshold.

### 2025-12-21: Added read-only graph access for Connectome

* **What:** Added `GraphReadOps` with Cypher and simple natural-language queries and embedding-stripped output.
* **Why:** Provide Connectome access to real nodes and links from the `seed` graph without embedding payloads.
* **Files:** `mind/physics/graph/graph_ops.py`.

### 2025-12-21: Added embedding-based semantic search for Connectome

* **What:** Added `search_semantic` using embeddings with hop expansion and a CLI runner; embeddings are never returned.
* **Why:** Enable true semantic search while keeping payloads small.
* **Files:** `mind/physics/graph/graph_ops.py`, `mind/physics/graph/connectome_read_cli.py`.

---



---

# Archived: SYNC_Graph.md

Archived on: 2025-12-22
Original file: SYNC_Graph.md

---

## RECENT CHANGES

### 2025-12-22: Fixed Orchestrator Indentation Bug

- **What:** Methods `_world_injection_path`, `_get_world_tick`, `_load_world_injection` were over-indented (nested inside `new_game` method).
- **Why:** `/api/action` endpoint was failing with `'Orchestrator' object has no attribute '_get_world_tick'`.
- **Fix:** Corrected indentation from 8 spaces to 4 spaces for these methods.
- **Files:** `mind/infrastructure/orchestration/orchestrator.py`

### 2025-12-22: Expanded GraphClient Protocol Interface

- **What:** Added 4 missing methods to the GraphClient protocol that consumers actually use.
- **Why:** Orchestrator and tick.py call methods not in the original interface. External proxy (blood-ledger) needs the complete contract.
- **Added methods:**
  - `get_player_location()` — used by Orchestrator
  - `get_narrative_believers()` — used by Orchestrator
  - `get_path_between()` — used by tick.py
  - `get_narratives_about()` — used by tick.py
- **Files:** `mind/physics/graph/graph_interface.py`
- **Markers added:**
  - `@mind:proposition` — documents the "minimal interface" design decision
  - `@mind:todo` — reminder to update blood-ledger proxy

### 2025-12-21: Fixed link extraction for GraphReadOps

- **What:** Added support for FalkorDB Edge objects in link extraction.
- **Why:** Ensure `/api/connectome/graph` returns links (not nodes only).
- **Files:** `mind/physics/graph/graph_query_utils.py`.

---

