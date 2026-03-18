# DECISION: Two-Tick Cognitive Architecture

DATE: 2026-03-18
DECIDED_BY: NLR
STATUS: CANONICAL
SUPERSEDES: L1 21-law single-rate tick, stimulus injection model

## Decision

Replace single-rate L1 tick with two variable-rate ticks. Eliminate stimuli entirely.

### Tick 1: Awareness Tick (slow, variable rate)

Scans external graph, imports new node clusters with energy = external_energy × novelty × valence × relevance. Rate scales with arousal. No duplicates — existing nodes get energy boost if external energy grew. The citizen perceives by scanning, not by receiving.

### Tick 2: Thought-Speed Tick (fast, variable rate)

Processes active subentities. Generates excess internal energy. Energy disperses bidirectionally through links. Crystallizes co-active pairs (Hebb). WM = top N active nodes (emergent). Subconscious behaviors fire automatically: consolidation, forgetting, pattern detection. One special behavior: "conscious action" — fires when WM intensity exceeds threshold, launches claude -p.

## Energy Flow

Internal energy production (continuous) → thought tick disperses → nodes accumulate → WM emerges → conscious action fires → claude -p → citizen acts on graph → internal energy transfers to external graph → propagates immediately → other citizens' awareness ticks pick it up.

No stimuli. No dispatch queue. No budget. Energy from within.

## Tick Rate Dynamics

awareness_interval = BASE_AWARENESS / arousal_level
thought_interval = BASE_THOUGHT / (active_nodes × load_factor)
