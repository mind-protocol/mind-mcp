# DECISION: One Physics Engine — L1 Only

DATE: 2026-03-18
DECIDED_BY: NLR
STATUS: CANONICAL
SUPERSEDES: L3 8-phase tick (GraphTickV1_2)

## Decision

L1 cognitive tick is the ONLY physics engine. The old L3 universe tick (GraphTickV1_2, 8-phase energy physics) is deprecated. Same physics was running at two scales — redundant.

## Rationale

The 8 L3 phases map 1:1 to existing L1 laws:

| L3 Phase | L1 Equivalent |
|----------|---------------|
| Generation | Internal energy production |
| Moment Draw/Flow | Energy dispersion through links |
| Moment Interaction | Co-activation / inhibition |
| Narrative Backflow | Bidirectional energy flow |
| Link Cooling | Energy decay |
| Completion | Conscious action fires |
| Rejection | Forgetting dissolves weak nodes |
| Crystallization | Hebb's law strengthens co-active links |

No synchronization needed between citizens. Citizens learn about world events through their awareness tick scanning the shared graph — exactly like reality. You don't know what your neighbor did unless you look.

## What Changes

- L3 tick code (tick_v1_2.py, phases/) is deprecated
- World events become nodes in citizen brains, processed by L1 physics
- Cross-citizen effects flow through graph writes, not state sync
- FalkorDB = shared memory, not physics engine

The citizen is not a reactor. The citizen is a generator.
