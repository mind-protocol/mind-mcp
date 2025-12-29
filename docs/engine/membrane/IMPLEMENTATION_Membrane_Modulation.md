# Engine — Implementation: Membrane Modulation (Scoping + Hooks)

```
STATUS: DRAFT
CREATED: 2025-12-20
VERIFIED: 2025-12-20 against local tree
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Membrane_Modulation.md
PATTERNS:        ./PATTERNS_Membrane_Scoping.md
BEHAVIORS:       ./BEHAVIORS_Membrane_Modulation.md
ALGORITHM:       ./ALGORITHM_Membrane_Modulation.md
VALIDATION:      ./VALIDATION_Membrane_Modulation.md
THIS:            IMPLEMENTATION_Membrane_Modulation.md (you are here)
HEALTH:          ./HEALTH_Membrane_Modulation.md
SYNC:            ./SYNC_Membrane_Modulation.md

IMPL (planned):  runtime/membrane/*
IMPL (planned):  runtime/moment_graph/queries.py
IMPL (planned):  runtime/moment_graph/traversal.py
IMPL (planned):  runtime/moment_graph/surface.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

Membrane modulation is not implemented yet. This document reserves the
implementation hooks and scope ownership to prevent drift while code is built.

Core idea: compute per-place modulation frames outside hot paths and read them
inside traversal/surfacing without canon writes.

---

## CODE STRUCTURE (PLANNED)

```
runtime/membrane/frame.py      # ModulationFrame dataclass
runtime/membrane/provider.py   # Place-scoped cache + retrieval
runtime/membrane/functions.py  # Dynamic modulation functions (O(1))
runtime/membrane/compute.py    # Aggregate-to-frame computation (no hot path)
```

---

## ENTRY POINTS (PLANNED)

| Entry Point | File | Triggered By |
|-------------|------|--------------|
| Compute frame | `runtime/moment_graph/queries.py` | view build / scene query |
| Read frame | `runtime/moment_graph/traversal.py` | click/wait traversal |
| Read frame | `runtime/moment_graph/surface.py` | surfacing + decay |
| Reset scope | `runtime/moment_graph/surface.py` | scene change |

---

## RESPONSIBILITIES

- Membrane compute runs outside hot paths.
- Modulation frames are keyed by `place_id`.
- Hot path reads are O(1) and fail-silent to neutral frame.

---

## DATA FLOW (PLANNED)

```
Place-scoped aggregates
    ↓
compute_modulation_frame(place_id, aggregates)
    ↓
MembraneProvider.set_frame(place_id, frame)
    ↓
Traversal/Surfacing reads frame(place_id) only
```

---

## MARKERS

<!-- @mind:todo Decide exact aggregate fields for compute step. -->
<!-- @mind:todo Define bounds for each modifier. -->
<!-- @mind:todo Add tests for scope isolation and idempotency. -->
