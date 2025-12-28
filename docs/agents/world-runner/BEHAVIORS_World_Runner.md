# World Runner — Behaviors: What It Produces

```
CREATED: 2024-12-16
UPDATED: 2025-12-19
STATUS: Canonical
```

---

## Injection Interface

The Runner returns a structured **Injection** for the Narrator.
This interface is the only observable contract the Narrator consumes after a long action, so every call must describe what mutated, why time stopped, and how much duration remains before the next scene.

## BEHAVIORS

- Reads graph state, advances time, and emits a structured Injection that
  mirrors actual graph mutations and detected flips.
- Interrupts immediately when a player-affecting flip occurs, returning the
  event payload and remaining minutes for a resume call.
- Completes cleanly when time elapses without player-facing flips, returning
  world changes and news for narration context.
- Emits low-urgency beats to the injection queue without interrupting the
  current scene, keeping narration flow smooth.

## OBJECTIVES SERVED

| Behavior ID | Objective | Why It Matters |
|-------------|-----------|----------------|
| B1 | Keep injection payloads grounded in deterministic evaluation of the canonical graph and pressure flips so narrators see the same reality every run. | Ensures follow-up narration can rely on consistent world state instead of guessing what the runner did during the tick loop. |
| B2 | Interrupt immediately when a player-facing flip occurs and surface the triggering payload along with the remaining duration for resumption. | Lets the narrator split long actions cleanly so players always react to interrupts with faithful context about why time stopped. |
| B3 | Complete the requested duration when no player-facing flips arise, summarizing background changes and elapsed minutes for scene continuity. | Supplies narrators with the quiet aftermath data they need to keep world news and pressure updates in sync without rerunning the simulation. |
| B4 | Append low-urgency beats to the injection queue without interrupting the current scene, documenting supplemental reactions for optional narration. | Gives narrators optional hooks for flavor beats while preserving the smooth pacing of the ongoing scene and the deterministic interrupt contract. |

The table above spells out how each observable behavior ties back to the runner contract so the narrator can audit interrupts, completions, and queued beats against explicit objectives before weaving the Injection into prose, and now the objective rows explicitly reference the output channels (`world_changes`, `news_available`, `remaining`, and `interrupted`) each behavior drives so narrators know which payload fields to trust.

## INPUTS / OUTPUTS

Inputs come from the orchestrator (action context, elapsed minutes, player
context, and graph state); see `docs/agents/world-runner/INPUT_REFERENCE.md`
for the full contract. Outputs are the Injection payload (plus queued
injections when appropriate) documented in `docs/agents/world-runner/TOOL_REFERENCE.md`.

## OUTPUTS

```typescript
interface Injection {
  interrupted: boolean;
  at_minute?: number;
  remaining?: number;
  event?: Event;

  completed?: boolean;
  time_elapsed?: number;

  world_changes: WorldChange[];
  news_available: News[];
}
```

See `docs/agents/world-runner/TOOL_REFERENCE.md` for canonical schemas.

---

## BEHAVIORS

- Emits an Injection for every run, marking `interrupted` or `completed`
  explicitly so the Narrator can branch the response.
- Stops on player-affecting flips and returns the triggering `event` payload.
- Applies graph mutations during the run and summarizes them in `world_changes`.
- Packages low-urgency beats as `news_available` for optional narration.

---

## INPUTS / OUTPUTS

**Inputs:**
- Long action intent + expected duration from the Narrator.
- Playthrough context (id, player identity, location, current scene).
- Graph state and pressure records queried at tick time.

**Outputs:**
- Injection payload describing interrupt/completion and elapsed time.
- Graph mutations already applied in the engine store.
- Optional queued injections for in-scene beats or reactions.

---

## Interrupted Injection

- Trigger: a flip affects the player.
- Behavior: stop immediately, return `interrupted: true` and `event`.
- Narrator writes the scene, resolves it, then resumes with `remaining` minutes.

---

## Completed Injection

- Trigger: time span ends without a player-facing flip.
- Behavior: return `completed: true`, `time_elapsed`, and any background world changes/news.

---

## Injection Queue (In-Scene Events)

The Runner can append low-urgency events to `playthroughs/{id}/injection_queue.json` for the Narrator to weave into the current scene. These do **not** interrupt. Typical uses: companion actions, reactions, minor scene beats.

---

## Event / WorldChange / News

```typescript
interface Event {
  type: EventType;
  location: string;
  description: string;
  characters: string[];
  narrator_notes?: string;
}

type EventType = 'ambush' | 'encounter' | 'discovery' | 'arrival' | 'message' | 'event';
```

```typescript
interface WorldChange {
  type: WorldChangeType;
  id: string;
  summary?: string;
  pressure?: number;
}

type WorldChangeType =
  | 'narrative_created'
  | 'narrative_updated'
  | 'pressure_created'
  | 'pressure_resolved'
  | 'pressure_changed'
  | 'character_moved'
  | 'belief_changed';
```

```typescript
interface News {
  summary: string;
  narrative_id?: string;
  source: string;
  reliability: number;
  location_heard?: string;
}
```

## EDGE CASES

- No flips occur during the full duration: returns `completed` with
  `time_elapsed` and empty `world_changes`/`news_available` arrays as needed.
- Multiple flips in a single tick: only the first player-affecting flip
  interrupts; remaining flips become background changes or news.
- Optional fields stay absent rather than populated with placeholders when
  there is no interrupt or completion payload to provide.

## ANTI-BEHAVIORS

- Must not invent events or world changes that are not anchored in graph
  mutations produced by the tick loop.
- Must not interrupt for non-player-facing flips; those remain background
  updates or queued injections.
- Must not author narrative prose or override the Narrator’s scene writing.

## MARKERS

- Should the Injection include a compact trace summary for debugging long
  actions without rehydrating full tick logs?
- Is there a single canonical schema artifact we can link to, rather than
  repeating partial examples across docs?

--- 

## Resume Pattern (Narrator)

```
1. Narrator writes interrupt scene
2. Player responds and resolves
3. Narrator calls Runner with remaining time
4. Runner continues until next interrupt or completion
```

---

## EDGE CASES

- No flips occur: Runner still returns `completed: true` with `time_elapsed`.
- Multiple flips: first player-affecting flip interrupts; later ones wait.
- Empty `world_changes`: Injection still returns structural fields for caller.
- Zero or near-zero duration: may immediately complete with no mutations.

---

## ANTI-BEHAVIORS

- Does not author prose or resolve player choices; Narrator owns narration.
- Does not invent non-graph facts; reads and writes through graph APIs only.
- Does not interrupt on non-player-facing flips; those become background news.

---

## MARKERS

- Should the Runner attach a concise tick trace for debugging interruptions?
- Is there a canonical JSON schema artifact we can link instead of duplicates?
- How should partial tick progress be represented when resuming mid-action?

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
