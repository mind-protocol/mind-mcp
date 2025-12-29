# Moment Graph Engine — Patterns: Instant Traversal Hot Path

```
STATUS: DESIGNING
CREATED: 2025-12-19
```

===============================================================================
## CHAIN
===============================================================================

```
OBJECTIVES:     ./OBJECTIVES_Moment_Graph_Engine.md
THIS:           PATTERNS_Instant_Traversal_Moment_Graph.md (you are here)
BEHAVIORS:      ./BEHAVIORS_Traversal_And_Surfacing.md
ALGORITHM:      ./ALGORITHM_Click_Wait_Surfacing.md
VALIDATION:     ./VALIDATION_Moment_Traversal_Invariants.md
IMPLEMENTATION: ./IMPLEMENTATION_Moment_Graph_Runtime_Layout.md
TEST:           ./TEST_Moment_Graph_Runtime_Coverage.md
SYNC:           ./SYNC_Moment_Graph_Engine.md
IMPL:           ../../../runtime/moment_graph/__init__.py
```

===============================================================================
## THE PROBLEM
===============================================================================

The game needs a deterministic, low-latency way to advance narrative moments
without invoking an LLM on every player action. If traversal, surfacing, or
weight updates are slow or ambiguous, player interactions feel unresponsive and
state changes become inconsistent across systems.

===============================================================================
## THE PATTERN
===============================================================================

**Keep moment-graph traversal mechanical and fast, backed by direct graph
queries and updates.**

This module owns the hot path operations:
- Queries that return the current moment view and transition candidates.
- Traversal that applies weight transfers, status updates, and history links.
- Surfacing that activates/decays moments based on mechanical thresholds.

The design emphasizes:
- No LLM calls on the hot path.
- Sub-50ms graph operations for clicks and wait triggers.
- Single-module ownership of traversal/surfacing behavior.

===============================================================================
## PRINCIPLES
===============================================================================

### Principle 1: No LLM in the Hot Path

Moment traversal and surfacing must be pure graph operations. Any narrative
reasoning happens elsewhere.

### Principle 2: Deterministic State Transitions

Traversal updates (status changes, weight transfers, THEN links) are explicit
and repeatable so downstream systems can trust moment state.

### Principle 3: Graph-Backed Visibility Rules

Presence gating, wait triggers, and surfacing thresholds are enforced in the
moment graph so the visible moment set is always derived from graph state.

===============================================================================
## DEPENDENCIES
===============================================================================

| Module | Why We Depend On It |
|--------|----------------------|
| runtime/physics/graph | Graph queries and mutations for moment traversal |

===============================================================================
## WHAT THIS DOES NOT SOLVE
===============================================================================

- It does not define the moment schema contract (see docs/runtime/moments).
- It does not handle UI rendering of moments.
- It does not perform narrative planning or LLM-driven reasoning.

===============================================================================
## MARKERS
===============================================================================

<!-- @mind:todo Document validation invariants and test coverage for traversal/surfacing. -->
<!-- @mind:todo Confirm performance targets against integration benchmarks. -->
