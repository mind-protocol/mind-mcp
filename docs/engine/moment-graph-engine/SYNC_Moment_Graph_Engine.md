# Moment Graph Engine — Sync: Current State

```
LAST_UPDATED: 2025-12-20
UPDATED_BY: codex
STATUS: DESIGNING
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Instant_Traversal_Moment_Graph.md
BEHAVIORS:       ./BEHAVIORS_Traversal_And_Surfacing.md
ALGORITHM:       ./ALGORITHM_Click_Wait_Surfacing.md
VALIDATION:      ./VALIDATION_Moment_Traversal_Invariants.md
IMPLEMENTATION:  ./IMPLEMENTATION_Moment_Graph_Runtime_Layout.md
TEST:            ./TEST_Moment_Graph_Runtime_Coverage.md
THIS:            SYNC_Moment_Graph_Engine.md (you are here)
IMPL:            mind/moment_graph/__init__.py
```

---

## MATURITY

**What's canonical (v1):**
- Traversal, query, and surfacing helpers implemented in `mind/moment_graph/`.
- Hot-path goal of sub-50ms graph operations with no LLM calls.

**What's still being designed:**
- Formal validation invariants for traversal/surfacing.
- Integration performance benchmarks and thresholds.

**What's proposed (v2+):**
- Expanded surface heuristics and richer transition strategies.

---

## CURRENT STATE

Moment graph traversal, query, and surfacing logic lives in `mind/moment_graph/`
with explicit click/wait transitions, weight updates, and surfacing thresholds.
The module relies on physics graph ops/queries and is treated as a hot path.

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** VIEW_Implement_Write_Or_Modify_Code

**Where I stopped:** Documentation only; no code changes beyond DOCS reference.

**What you need to understand:** This module is the runtime traversal/surfacing
engine; schema and contract docs live in `docs/mind/moments/`.

**Watch out for:** Performance expectations ("<50ms") in docstrings are
assumptions; validate against real graph benchmarks before tightening.

---

## TODO

### Doc/Impl Drift

<!-- @mind:todo Document additional invariants if traversal logic changes. -->

### Tests to Run

```bash
pytest mind/tests/test_moment_graph.py -v
pytest mind/tests/test_e2e_moment_graph.py -v -s
```

## CONFLICTS

### DECISION: moment graph module mapping drift
- Conflict: `docs/mind/moment-graph-mind/SYNC_Moment_Graph_Engine.md` claims
  the module is mapped in `modules.yaml`, but the manifest currently only lists
  `engine_models`.
- Resolution: Leave `modules.yaml` unchanged in this repair to keep scope on the
  traversal helper verification; record the drift for follow-up.
- Reasoning: The repair target is incomplete traversal helpers, and updating
  module mapping would be a separate maintenance change.
- Updated: `docs/mind/moment-graph-mind/SYNC_Moment_Graph_Engine.md`

## Agent Observations

### Remarks
- Repair task identified incomplete functions, but the current
  `mind/moment_graph/queries.py` implementations are already in place.

### Suggestions
- None.

### Propositions
- None.


---

## ARCHIVE

Older content archived to: `SYNC_Moment_Graph_Engine_archive_2025-12.md`
