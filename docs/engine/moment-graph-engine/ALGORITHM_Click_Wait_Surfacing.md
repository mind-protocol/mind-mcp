# Moment Graph Engine — Algorithm: Click, Wait, Surfacing

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
VALIDATION:      ./VALIDATION_Moment_Traversal_Invariants.md
IMPLEMENTATION:  ./IMPLEMENTATION_Moment_Graph_Runtime_Layout.md
TEST:            ./TEST_Moment_Graph_Runtime_Coverage.md
SYNC:            ./SYNC_Moment_Graph_Engine.md
THIS:            ALGORITHM_Click_Wait_Surfacing.md (you are here)
IMPL:            ../../../mind/moment_graph/traversal.py
```

===============================================================================
## CLICK TRAVERSAL
===============================================================================

1. Query candidate transitions for the current moment.
2. Filter candidates by the clicked word (substring match against
   `require_words`).
3. Pick the first matching target.
4. Boost target weight by `weight_transfer` (default 0.3), clamped to [0, 1].
5. If the transition consumes origin, mark origin as `completed` and stamp tick.
6. Mark target as `active` and stamp tick if applicable.
7. Create a `THEN` link from origin to target with tick and causation flag.

===============================================================================
## WAIT TRIGGER TRAVERSAL
===============================================================================

1. Query active moments with `CAN_LEAD_TO` links triggered by `wait`.
2. Filter to links whose wait threshold has elapsed since `tick_resolved`.
3. For each trigger, apply the same weight transfer and status updates as
   click traversal.
4. Create `THEN` links with `player_caused = false`.

===============================================================================
## SURFACING AND DECAY
===============================================================================

1. `check_for_flips` activates any `possible` moment with weight >= threshold.
2. `apply_decay` multiplies weights by `DECAY_RATE` for active/possible moments.
3. Moments with weight below the decay threshold are marked `decayed` with a
   `tick_resolved` stamp.

===============================================================================
## SCENE CHANGE
===============================================================================

1. For the old location, set persistent attached moments to `possible`.
2. For the old location, set non-persistent attached moments to `decayed`.
3. For the new location, set dormant moments to `possible` and restore minimum
   weight to 0.3.

===============================================================================
## DRAMATIC BOOST
===============================================================================

1. Multiply dramatic pressure by `DRAMATIC_ENERGY_FACTOR`.
2. Add that boost to weights of attached moments, clamped to 1.0.
