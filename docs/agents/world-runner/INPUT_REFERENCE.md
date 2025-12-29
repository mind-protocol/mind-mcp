# World Runner Input Reference

What the World Runner receives from the Orchestrator.

---

## Script Location

```
runtime/infrastructure/orchestration/world_runner.py
mind/models/
```

---

## Prompt Structure

```
WORLD RUNNER INSTRUCTION
════════════════════════

You process flips detected by the graph tick.

{FLIP_CONTEXT}
{GRAPH_CONTEXT}
{PLAYER_CONTEXT}

Determine what happened. Output JSON matching WorldRunnerOutput schema.
```

---

## Flip Context

```typescript
interface FlipContext {
  time_span: string;
  flips: Flip[];
}

interface Flip {
  narrative_id: string;
  pressure: number;
  breaking_point: number;
  trigger_reason: string;
  narratives: string[];
  involved_characters: string[];
  location: string;
}
```

---

## Graph Context

```typescript
interface GraphContext {
  relevant_narratives: NarrativeDetail[];
  character_locations: Record<string, string>;
  character_beliefs: Record<string, Record<string, BeliefState>>;
}
```

---

## Player Context

```typescript
interface PlayerContext {
  location: string;
  engaged_with?: string;
  traveling_to?: string;
  recent_action?: string;
}
```

---

## Processing Guidance (Short)

- Focus on **why the flip happened** and **who it affects**.
- Scale outcomes to time span (minutes → small, days → cascade).
- If a flip destabilizes new pressure dynamics, report cascades.

---

## CHAIN

PATTERNS:        ./PATTERNS_World_Runner.md
BEHAVIORS:       ./BEHAVIORS_World_Runner.md
ALGORITHM:       ./ALGORITHM_World_Runner.md
VALIDATION:      ./VALIDATION_World_Runner_Invariants.md
IMPLEMENTATION:  ./IMPLEMENTATION_World_Runner_Service_Architecture.md
TEST:            ./TEST_World_Runner_Coverage.md
INPUTS:          ./INPUT_REFERENCE.md
TOOLS:           ./TOOL_REFERENCE.md
SYNC:            ./SYNC_World_Runner.md
