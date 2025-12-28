# Moment Graph Engine — Tests: Runtime Coverage

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
IMPLEMENTATION:  ./IMPLEMENTATION_Moment_Graph_Runtime_Layout.md
SYNC:            ./SYNC_Moment_Graph_Engine.md
THIS:            TEST_Moment_Graph_Runtime_Coverage.md (you are here)
IMPL:            ../../../mind/moment_graph/traversal.py
```

===============================================================================
## EXISTING TESTS
===============================================================================

| Area | Coverage | Location |
|------|----------|----------|
| Graph ops + moment queries | partial | `mind/tests/test_moment_graph.py` |
| End-to-end traversal | integration | `mind/tests/test_e2e_moment_graph.py` |

===============================================================================
## HOW TO RUN
===============================================================================

```bash
pytest mind/tests/test_moment_graph.py -v
```

```bash
# Requires FalkorDB running on localhost:6379
pytest mind/tests/test_e2e_moment_graph.py -v -s
```

===============================================================================
## GAPS
===============================================================================

- No isolated unit tests for `MomentSurface` decay/flip logic.
- No performance regression checks for the <50ms hot path target.
