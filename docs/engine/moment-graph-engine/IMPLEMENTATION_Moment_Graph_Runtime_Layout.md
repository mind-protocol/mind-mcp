# Moment Graph Engine — Implementation: Runtime Layout

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
VALIDATION:      ./VALIDATION_Moment_Traversal_Invariants.md
TEST:            ./TEST_Moment_Graph_Runtime_Coverage.md
SYNC:            ./SYNC_Moment_Graph_Engine.md
THIS:            IMPLEMENTATION_Moment_Graph_Runtime_Layout.md (you are here)
IMPL:            ../../../mind/moment_graph/__init__.py
```

===============================================================================
## FILES AND ROLES
===============================================================================

- `mind/moment_graph/__init__.py`
  Exposes MomentTraversal, MomentQueries, and MomentSurface as the public
  interface for the runtime module.

- `mind/moment_graph/queries.py`
  Read-only query helpers for current view, transitions, speaker resolution,
  dormant moments, wait triggers, and pressure-attached moments.

- `mind/moment_graph/traversal.py`
  Traversal and lifecycle mutations for click/wait triggers, status changes,
  weight updates, and history (THEN) links.

- `mind/moment_graph/surface.py`
  Surfacing logic for flips, decay, scene change handling, and dramatic boosts.

===============================================================================
## DATA FLOW
===============================================================================

1. Callers request a view via MomentQueries.get_current_view.
2. Player actions invoke MomentTraversal.handle_click or process_wait_triggers.
3. Per-tick systems call MomentSurface.check_for_flips and apply_decay.
4. Scene transitions call MomentSurface.handle_scene_change and
   MomentTraversal.reactivate_dormant.

===============================================================================
## DEPENDENCIES
===============================================================================

- `mind/physics/graph/graph_queries.py`
  Provides read access to the graph backend.
- `mind/physics/graph/graph_ops.py`
  Provides write access for mutations and link creation.
