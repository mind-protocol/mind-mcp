# Moment Graph Engine — Validation: Traversal Invariants

```
STATUS: DESIGNING
CREATED: 2025-12-19
```

===============================================================================
## CHAIN
===============================================================================

```
PATTERNS:        ./PATTERNS_Instant_Traversal_Moment_Graph.md
BEHAVIORS:       ./BEHAVIORS_Traversal_And_Surfacing.md
ALGORITHM:       ./ALGORITHM_Click_Wait_Surfacing.md
IMPLEMENTATION:  ./IMPLEMENTATION_Moment_Graph_Runtime_Layout.md
TEST:            ./TEST_Moment_Graph_Runtime_Coverage.md
SYNC:            ./SYNC_Moment_Graph_Engine.md
THIS:            VALIDATION_Moment_Traversal_Invariants.md (you are here)
IMPL:            ../../../mind/moment_graph/traversal.py
```

===============================================================================
## INVARIANTS
===============================================================================

- Status values remain within the expected lifecycle set:
  `possible`, `active`, `completed`, `possible`, `decayed`.
- Weight updates are clamped to [0, 1].
- Traversal updates always write a `THEN` link between origin and target.
- `tick_resolved` is set when a moment becomes `completed`.
- `tick_resolved` is set when a moment becomes `decayed`.
- Surfacing only activates moments from `possible` status.
- Presence-gated visibility requires all `presence_required` attachments to be
  present in the view context.

===============================================================================
## PERFORMANCE EXPECTATIONS
===============================================================================

- Query and traversal helpers are expected to run in <50ms under normal load.
- No LLM calls are permitted in this module.

===============================================================================
## FAILURE MODES TO WATCH
===============================================================================

- Click traversal returns no match even when a transition exists (word matching
  mismatch).
- Weight transfer writes NaN or values outside [0, 1].
- Wait triggers fire without `tick_resolved` or with incorrect tick math.
- Scene change leaves moments in `active` state for old locations.
