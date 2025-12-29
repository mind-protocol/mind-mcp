# Moment Graph Engine — Behaviors: Traversal And Surfacing

```
STATUS: DESIGNING
CREATED: 2025-12-19
```

===============================================================================
## CHAIN
===============================================================================

```
PATTERNS:        ./PATTERNS_Instant_Traversal_Moment_Graph.md
ALGORITHM:       ./ALGORITHM_Click_Wait_Surfacing.md
VALIDATION:      ./VALIDATION_Moment_Traversal_Invariants.md
IMPLEMENTATION:  ./IMPLEMENTATION_Moment_Graph_Runtime_Layout.md
TEST:            ./TEST_Moment_Graph_Runtime_Coverage.md
SYNC:            ./SYNC_Moment_Graph_Engine.md
THIS:            BEHAVIORS_Traversal_And_Surfacing.md (you are here)
IMPL:            ../../../runtime/moment_graph/__init__.py
```

===============================================================================
## OBSERVABLE BEHAVIORS
===============================================================================

- `get_current_view` returns visible moments and transitions filtered by
  presence rules, sorted by weight, and scoped to active/possible moments.
- `handle_click` resolves a clicked word to a transition, boosts target weight,
  updates statuses, and records a THEN link.
- `process_wait_triggers` auto-fires transitions after wait thresholds and
  applies the same weight/status/THEN updates as clicks.
- `check_for_flips` activates moments when weights cross the activation
  threshold.
- `apply_decay` decays weights each tick and marks moments as decayed below the
  decay threshold.
- `handle_scene_change` moves moments to dormant/decayed states and reactivates
  dormant moments at the new location.

===============================================================================
## INPUTS AND OUTPUTS
===============================================================================

Inputs:
- Player/moment identifiers, click words, and tick counters.
- Presence context (location, characters, things).
- Energy pressure values.

Outputs:
- Moment/transition payloads for rendering.
- Updated graph state for statuses, weights, and history links.

===============================================================================
## SIDE EFFECTS
===============================================================================

- Writes to the graph: status fields, weight adjustments, THEN/SAID links.
- Updates tick metadata on spoken/decayed moments.
