# Moment Graph — Patterns

```
STATUS: DESIGNING
CREATED: 2025-12-19
```

===============================================================================
## CHAIN
===============================================================================

```
OBJECTIVES:     ./OBJECTIVES_Moments.md
THIS:           PATTERNS_Moments.md (you are here)
BEHAVIORS:      ./BEHAVIORS_Moment_Lifecycle.md
ALGORITHM:      ./ALGORITHM_Moment_Graph_Operations.md
VALIDATION:     ./VALIDATION_Moment_Graph_Invariants.md
IMPLEMENTATION: ./IMPLEMENTATION_Moment_Graph_Stub.md
TEST:           ./TEST_Moment_Graph_Coverage.md
SYNC:           ./SYNC_Moments.md
SCHEMA:         ../../schema/SCHEMA_Moments.md
IMPL:           ../../../runtime/moments/__init__.py
```

===============================================================================
## THE PROBLEM
===============================================================================

The project needs a single, authoritative place to describe how moments are
modeled and why the moment graph exists. Without that anchor:

- Graph-facing code references a schema and invariants that are not centralized.
- Engine modules cannot agree on how moments should be queried or mutated.
- Future implementations risk diverging from the intended graph contract.

===============================================================================
## THE PATTERN
===============================================================================

**Define a moment-graph contract first, then implement graph-backed logic to
satisfy it.**

The moment graph is the canonical representation of narrative time:
- Moments are the atomic, player-visible units of story.
- Links capture ordering, visibility, and transitions.
- The schema (see SCHEMA) is the source of truth for node/link fields.

This module is currently a stub that preserves the shape of the API so other
systems can reference it while the graph-backed implementation is built.

===============================================================================
## PRINCIPLES
===============================================================================

### Principle 1: Schema-First Contract

Schema definitions drive implementation. Moment fields and links must match the
schema contract before new behavior is introduced.

### Principle 2: Graph Is Canon

If moment data exists anywhere else, it must reconcile with graph state. The
moment graph is the canonical source for what happened and what can happen.

### Principle 3: Single Module Owner

All moment-graph logic belongs in this module (runtime/moments) so callers have a
single place to integrate.

===============================================================================
## DEPENDENCIES
===============================================================================

| Module | Why We Depend On It |
|--------|----------------------|
| docs/schema/SCHEMA_Moments.md | Canonical schema definitions for moments |
| runtime/physics/graph | Graph operations that will back moment queries |

===============================================================================
## WHAT THIS DOES NOT SOLVE
===============================================================================

- It does not implement the graph-backed moment lifecycle yet.
- It does not define API endpoints (see API docs referenced elsewhere).
- It does not address rendering or UI concerns.

===============================================================================
## MARKERS
===============================================================================

<!-- @mind:todo Implement the graph-backed moment lifecycle and query helpers. -->
<!-- @mind:todo Author or relocate the API doc referenced by mind/app/tests. -->
