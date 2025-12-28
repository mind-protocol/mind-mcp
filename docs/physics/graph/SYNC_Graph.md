# Graph — Current State

```
UPDATED: 2025-12-20
STATUS: Implemented, needs API endpoint
```

---

## MATURITY

STATUS: CANONICAL

What's canonical (v1):
- GraphOps/GraphQueries mixins and tick integration are stable and in use.
- Energy flow, decay, and flip detection are treated as production behavior.

What's still being designed:
- External API integration for player actions and streaming responses.

What's proposed (v2):
- Extended orchestration telemetry and richer runtime diagnostics.

---

## CURRENT STATE

The graph physics engine and its GraphOps/GraphQueries helpers are implemented and in active use. The remaining gaps are:
1. **API Integration**: A single API endpoint to invoke the orchestrator loop so player actions drive ticks and flips.
2. **Runtime Integration**: The core Canon Holder exists (`mind/infrastructure/canon/canon_holder.py`) but is not yet wired into the `Orchestrator` loop.
3. **Handlers**: Flip-triggered character handlers are planned but not yet implemented (missing `mind/handlers/`).

Read-only access for the Connectome dashboard is now provided by `GraphReadOps` in `mind/physics/graph/graph_ops_read_only_interface.py`, defaulting to the `seed` database, stripping embeddings from node/link results, and keeping `GraphOps` focused on write paths. GraphOps now fits under the 800-line threshold (799L) while the reader helper stands on its own (246L).

---

## IN PROGRESS

- Defining the `/api/action` endpoint contract and how it should integrate with existing playthrough and narration flows without breaking clients.
- Planning the integration of `CanonHolder` into the `Orchestrator` to record dialogue as moments.

## KNOWN ISSUES

- No API endpoint currently wires player actions to the orchestrator loop.
- Dialogue produced by the Narrator is not yet recorded as `Moment` nodes in the graph via the `CanonHolder`.
- Handlers for flip resolution are missing.

---

## What Exists ✓

| Component | Status | Location |
|-----------|--------|----------|
| GraphTick | ✓ Complete | `mind/physics/tick.py` |
| Orchestrator | ✓ Complete | `mind/infrastructure/orchestration/orchestrator.py` |
| World Runner | ✓ Complete | `mind/infrastructure/orchestration/world_runner.py` |
| Narrator | ✓ Complete | `mind/infrastructure/orchestration/narrator.py` |
| API app | ✓ Running | `mind/infrastructure/api/app.py` |
| GraphReadOps | ✓ Complete | `mind/physics/graph/graph_ops_read_only_interface.py` |

---

## Two Paths (Both Valid)

| Path | Endpoint | Use Case |
|------|----------|----------|
| Instant | `/api/moment/click` | Quick clicks, weight updates, no LLM |
| Full Loop | `/api/action` (ADD THIS) | Narrator response, time passes, tick runs |

Frontend should use:
- Moment click → instant feedback
- Action → when narrator response needed

---

## Known False Positives

If mind doctor flags these as INCOMPLETE_IMPL, mark stale:
- `tick.py` — fully implemented
- `orchestrator.py` — fully implemented  
- `graph_ops_events.py` — mutation listeners optional

## CONFLICTS

### DECISION: mutation listener completeness
- Conflict: Repair task flagged `add_mutation_listener`/`remove_mutation_listener` in `mind/physics/graph/graph_ops_events.py` as empty, but both functions already implement guarded registration/removal.
- Resolution: Treat the report as stale; no code changes required.
- Reasoning: Current implementations already match expected behavior for listener management.
- Updated: `docs/physics/graph/SYNC_Graph.md`

### DECISION: moment query helpers completeness
- Conflict: Repair task flagged `get_narrative_moments`, `get_narratives_from_moment`, `get_available_transitions`, and `get_clickable_words` in `mind/physics/graph/graph_queries_moments.py` as incomplete, but all functions already implement Cypher queries and parsing logic.
- Resolution: Treat the report as stale; no code changes required.
- Reasoning: Existing implementations return parsed rows with expected fields and include trigger/word parsing behavior.
- Updated: `docs/physics/graph/SYNC_Graph.md`

---

## HANDOFF: FOR AGENTS

Continue with VIEW_Implement_Write_Or_Modify_Code. Focus on adding the
`/api/action` endpoint wiring to the orchestrator without altering graph
physics internals. Keep doc updates confined to graph SYNC and API docs.

**GraphClient interface status:** The Protocol in `mind/physics/graph/graph_interface.py`
now covers all methods used by Orchestrator and tick.py. If blood-ledger proxy
exists, it needs the 4 new methods added (see `@mind:todo` in the file).

---

## HANDOFF: FOR HUMAN

The graph system is stable; the only blocking gap is an API endpoint that
invokes the orchestrator. Once added, player actions will drive ticks and
flip processing through the normal HTTP interface.

---

## TODO

<!-- @mind:todo Add `/api/action` endpoint in `mind/infrastructure/api/app.py`. -->
<!-- @mind:todo Add a minimal integration check that confirms ticks run via API. -->

---

## CONSCIOUSNESS TRACE

Confidence is high that the graph logic is correct and stable; the missing
endpoint is a product integration gap rather than a physics defect. The
focus is on wiring, not redesigning, to avoid scope creep.

---

## POINTERS

- `docs/physics/ALGORITHM_Physics.md` for the propagation logic.
- `docs/physics/graph/BEHAVIORS_Graph.md` for observable graph behaviors.
- `mind/physics/tick.py` for the tick entry point and graph integration.

## CHAIN

```
THIS:       SYNC_Graph.md (you are here)
PATTERNS:   ./PATTERNS_Graph.md
BEHAVIORS:  ./BEHAVIORS_Graph.md
ALGORITHM:  ../ALGORITHM_Physics.md
VALIDATION: ./VALIDATION_Living_Graph.md
```

## Agent Observations

### Remarks
- `graph_ops_types.py` already implements the previously flagged helpers; repair appears stale.
- Energy flow algorithm documentation now matches the required template layout.
- Moment query helpers in `mind/physics/graph/graph_queries_moments.py` are already implemented; no code changes required for issue #16.

### Suggestions
<!-- @mind:todo Add a DOCS reference in `mind/physics/graph/graph_ops_types.py` so `mind context` resolves the graph documentation chain. -->

### Propositions
- None.
- Reconfirmed mutation listener helpers (`add_mutation_listener`, `remove_mutation_listener`) are implemented in `mind/physics/graph/graph_ops_events.py` for the current repair run; no code changes required.

## Agent Observations

### Remarks
- The mutation listener helpers already include guard checks to avoid duplicate registrations and safe removal.
- Filled the graph behaviors template sections to eliminate drift warnings.
- Re-verified mutation listener helpers in `mind/physics/graph/graph_ops_events.py` during repair #16; no code changes needed.
- Logged the graph ops types verification in project state for issue #16 to keep the repair ledger aligned.
- Confirmed `SimilarNode.__str__` and `ApplyResult.success` are already implemented in `mind/physics/graph/graph_ops_types.py` during this repair run.
- Verified `SimilarNode.__str__` and `ApplyResult.success` are already implemented in `mind/physics/graph/graph_ops_types.py`; no code changes required for issue #16.
- Verified `get_narrative_moments`, `get_narratives_from_moment`, `get_available_transitions`, and `get_clickable_words` are already implemented in `mind/physics/graph/graph_queries_moments.py`; no code changes required for issue #16.

### Suggestions
<!-- @mind:todo Add a lightweight unit test for `emit_event` to cover listener registration/removal behavior. -->

### Propositions
- None.


## Agent Observations

### Remarks
- Extracted `GraphReadOps` into `mind/physics/graph/graph_ops_read_only_interface.py` (246L) so the Connectome reader stays available while `GraphOps` stays trim at 799L.
- `graph_ops.py` now re-exports `GraphReadOps`/`get_graph_reader`, keeping existing callers working while the write facade focuses on mutations.

### Suggestions
<!-- @mind:todo Document the new file in `docs/physics/IMPLEMENTATION_Physics.md` (already done) and consider referencing it from `docs/physics/graph/BEHAVIORS_Graph.md` so future readers find the read helper quickly. -->
<!-- @mind:todo Add concise smoke tests for `query_natural_language` or `search_semantic` to catch regressions in the token/embedding helpers. -->

### Propositions
- None.


---

## ARCHIVE

Older content archived to: `SYNC_Graph_archive_2025-12.md`


---

## ARCHIVE

Older content archived to: `SYNC_Graph_archive_2025-12.md`


---

## ARCHIVE

Older content archived to: `SYNC_Graph_archive_2025-12.md`
