# World Runner — Patterns: Why This Shape

```
CREATED: 2024-12-16
UPDATED: 2025-12-19
STATUS: Canonical
```

---

## The Core Insight

**The Runner owns time. The Narrator owns story.**

When the player takes a time-consuming action, the Narrator hands control to the Runner to advance the world. The Runner simulates time and detects player-affecting flips, then returns an Injection for the Narrator to write the moment or the summary.

---

## THE PROBLEM

Long actions need consistent world evolution so the narrator does not have to
simulate physics, travel passages, or pressure decay while also keeping the graph
canon intact. When the narrator owns both time and storytelling the result is
either a stall on simulation detail or a drift into conflicting reality that
breaks continuity for the player.

---

## THE PATTERN

Delegate time advancement to a stateless runner that reads the canonical graph,
ticks pressure until a player-facing flip or completion occurs, and emits a
structured Injection describing the flips, mutations, and remaining duration for
the narrator to render. This keeps the runner deterministic while the narrator
stays expressive.

---

## BEHAVIORS SUPPORTED

- Runs deterministic tick loops until the requested duration ends or a human-affecting flip forces an interrupt, making long actions predictable.
- Applies pressure decay and graph mutations before returning so each call leaves the graph ready for resumed runs or narrator reactions.
- Emits structured Injection payloads with flip metadata, completion flags, and remaining durations so the narrator can resume without recomputing scheduling.

---

## BEHAVIORS PREVENTED

- Prevents the narrator from inventing hidden time leaps or ad-hoc pressure rewrites by centralizing all world evolution inside the runner tick loop.
- Blocks random, story-irrelevant events from sneaking into the next moment by only emitting flips that arise from declared pressure points and player context.

---

## PRINCIPLES

- Treat time advancement as a strict control-flow boundary so the runner owns elapsed time and cadence while the narrator only reacts to legible outputs.
- Always read from the canonical graph state so the runner never invents new state beyond validated mutations and continuity remains intact.
- Translate every player-facing flip into an explicit Injection payload rather than performing silent mutations that the narrator needs to guess.
- Keep each run stateless and composable so retries, resumptions, and parallel reads resolve deterministically from the graph.
- Structure runner output to be inspectable, minimal, and descriptive so the narrator understands exactly what changed and why.

---

## Interrupt/Resume Pattern

```
NARRATOR                              RUNNER
   │                                     │
   │ long action                           │
   │─────────────────────────────────────► │
   │                                     │ runs tick loop
   │                                     │ flip affects player
   │         Injection (interrupted)     │
   │ ◄────────────────────────────────────
   │ writes scene + resolves             │
   │                                     │
   │ resume with remaining time          │
   │─────────────────────────────────────►│
   │                                     │ runs to completion
   │         Injection (completed)       │
   │ ◄────────────────────────────────────
```

**Key rule:** Runner runs until interrupted OR completed. Narrator handles the interrupt, then resumes.

---

## Stateless Runner

The Runner does not keep memory between calls. The graph is the memory.

- Inputs: action, duration, player context, graph context
- Output: Injection + graph mutations already applied
- Next call reads updated graph and continues

---

## What the Runner Is Not

- **Not a full simulation:** It ticks only what matters for narratives under pressure.
- **Not random events:** Events come from narrative pressure, not dice rolls.
- **Not a time system:** Time is a trigger, not a physics engine.
- **Not the Narrator's boss:** Injection is information, not instruction.

---

## Player Impact Threshold

**Only flips that affect the player interrupt.** Everything else becomes world changes or news.

See `docs/agents/world-runner/ALGORITHM_World_Runner.md` for the `affects_player()` logic.

---

## Why Separation Matters

- **Focus:** Narrator writes scenes; Runner handles world evolution.
- **Continuity:** Offscreen changes happen consistently.
- **Clean interrupts:** Player-facing events become explicit moments.

---

## DATA

Reads the canonical graph state (nodes, edges, pressure values, and node
attributes), the current action metadata (player context, goals, and remaining
duration), and outputs Injection payloads that bundle flips, completion status,
remaining time, and mutation logs so downstream agents can audit every world
transition.

---

## DEPENDENCIES

- `mind/infrastructure/orchestration/world_runner.py` for the outer orchestration loop, injection assembly, and aligning the runner lifecycle with the engine service contract.
- `mind/physics/graph/graph_ops.py` and `mind/physics/graph/graph_queries.py` for safely reading pressure, applying mutations, and keeping read-models isolated.
- `agents/world_runner/CLAUDE.md` for the runner instructions, output schema, and the format the narrator expects so the narrated Injection is interpreted without drift.

---

## INSPIRATIONS

- Inspired by narrative simulation systems that split world ticks from authored prose so chronology stays stable while narration can layer meaning on top.
- Draws from GM-style adjudication loops where time advances offscreen until a decisive trigger demands a player-facing interruption, simplifying what the narrator must manage.

---

## SCOPE

In scope: tick orchestration, flip detection, mutation emission, structured Injection output, trace logging, and deterministic resumption semantics for long actions.
Out of scope: narrator prose, frontend rendering, and non-pressure systems such as combat physics or economic simulation unless those systems surface legitimately through documented pressure flips.

---

## MARKERS

- Should the runner expose a trace summary for debugging long actions so we can step through partial ticks when telemetry shows drift?
- How should partial ticks be represented when resuming mid-action to ensure narrators see consistent remaining durations and graph context?
- What is the minimum Injection payload that still feels narratively grounded, and can we compress it further without losing the clarity narrators need?

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
