# Narrator — Patterns: Why This Design

```
CREATED: 2024-12-16
UPDATED: 2025-12-19
STATUS: Canonical
```

---

## Core Insight

The narrator is a persistent authorial intelligence that maintains a real,
continuous world. It is not a stateless text generator; continuity and intent
matter more than raw output volume.

---

## The Problem

Adventures span long playthroughs, callbacks, and evolving player knowledge,
yet the current writing flow often relies on ad-hoc generation. Without an
anchored narrator the fiction erodes: callbacks misfire, foreshadowing gets
forgotten, and the player loses the sense that the world existed before they
arrived. The game needs prose that survives choices, supports long sessions,
and keeps canon consistent even when new information is injected midstream.

---

## The Pattern

Query canonical graph state, map it into authored scenes, and only fall back on
on-demand generation when coverage gaps appear. Pre-authored responses cover
major beats, while the narrator tracks open questions, compiles clickables,
and writes follow-up text that persists back into the graph. The runtime
orchestration (`runtime/infrastructure/orchestration/narrator.py`) stitches
prompts, executes session loops, and ensures every mutation is recorded before
the next response is released.

Key steps:
1. Read the current canon from the graph—player state, scene tokens, and click
   history.
2. Choose authored prose (scene descriptions, voice lines, dialogue) for the
   target beat; reserve on-demand generation for true gaps or free-input
   prompts.
3. Persist any new facts as graph mutations so future beats inherit the shared
   intent.
4. Emit the scene/response stream in the expected SSE/streaming format.

---

## Scope

In scope: scene narration, clickable discovery, response authoring, voice line
delivery, and graph-backed canon updates. The pattern governs how narration
reaches the frontend, how clicks resolve to authored responses, and how new
facts are encoded. Out of scope: low-level physics ticks, frontend styling, and
non-narrator agent responsibilities such as tooling or CLI routing decisions.

---

## Data

Inputs:
- Graph truth (nodes, edges, canon tags) from `runtime/physics/graph/graph_ops.py`.
- Session metadata (player tags, active path, click sequence) from the narrator
  loop.
- Prompt instructions captured in `agents/narrator/CLAUDE.md`.
- Sparse authored voice snippets stored in the narrative content repository.

Outputs:
- SSE stream fragments and text responses that include voice line cues, pacing
  hints, and callable actions.
- Graph mutations that persist new facts, markers, or causal links for future
  narration.
- Optional debugging logs that describe why a generator was invoked.

---

## Behaviors Supported

- Maintains authored continuity so callbacks and foreshadowing work even after
  branching choices.
- Delivers click-targeted responses with curated prose by default, keeping
  generation to a fallback mode when coverage is missing.
- Persists every authored fact mutation back into the graph so the world stays
  consistent for all downstream agents and future sessions.
- Honors pacing rules (silence, brevity, emphasis) so scenes feel designed, not
  accidental.

---

## Behaviors Prevented

- Drift from established canon by avoiding ad-hoc generator improvisation unless
  absolutely necessary.
- Flooding players with content or repeating state explanations when the graph
  already encodes the answer.
- Emitting clickables that reference information the narrator has not retrieved
  or authenticated through the graph.
- Delegating responsibility for narrative truth to the frontend or other agents.

---

## Principles

### Principle 1: Preserve narrative intent ahead of novelty

The narrator values story coherence over flashy surprises; when design choices
conflict with continuity the canon-aligned path wins.

### Principle 2: Treat canon as durable truth

Authored outcomes must write back to the graph and be referenced in later
responses so every agent sees the same honest world.

### Principle 3: Maintain pacing discipline

The narrator resists the urge to flood the player with text when silence or
minimal phrasing serves the moment better.

### Principle 4: Keep the graph separate from the voice

Graph queries capture truth; the narrator crafts how that truth is completed without
recomputing it for each click.

### Principle 5: Let clicks resolve to authored lookup

Clicks should hit pre-authored content when available, with generators handling
only the inevitable gaps.

---

## Dependencies

| Module | Why We Depend On It |
|--------|---------------------|
| `runtime/infrastructure/orchestration/narrator.py` | Orchestrates session loops and prompt assembly. |
| `runtime/physics/graph/graph_ops.py` | Reads canonical nodes/edges and applies mutations. |
| `runtime/physics/graph/graph_queries.py` | Supplies domain-specific queries needed to frame scenes. |
| `agents/narrator/CLAUDE.md` | Captures voice instructions, style, and allowed improvisation. |
| `runtime/infrastructure/scene_memory/` | Stores session metadata that informs pacing and scope. |

---

## Inspirations

- Serialized narrative games and visual novels that reward memory, giving
  callbacks and foreshadowing the space to land.
- Tabletop GM practices that keep canon consistent while improvising within a
  bounded scene frame.
- Authorial notes from classical dramaturgy (scene beats, rising action, call
  and response) that guide pacing choices.

---

## Pre-Generation Model

- **Full pre-generation** for key beats that anchor each chapter and satisfy
  foreshadowing needs.
- **Rolling window** for nearby scenes (current + one layer ahead) to keep the
  backlog shallow while still prepping the next layer of prose.
- **Hybrid default:** important scenes are pre-baked, minor scenes rely on the
  rolling window plus selective prompts when justified.

See `docs/agents/narrator/HANDOFF_Rolling_Window_Architecture.md` for the rolling window mechanics.

---

## What the Narrator Controls

| Element | Control |
|---------|---------|
| Narration | Yes |
| Dialogue | Yes |
| Clickable words | Yes |
| Player speaks on click | Yes |
| New clickables after response | Yes |
| Voice lines | Yes |
| Pacing and depth | Yes |

---

## Free Input (Exception)

- Free input is on-demand generation when authored responses are absent.
- Show a short thinking indicator so latency reads as intentional.
- Used sparingly; most play remains click-driven to preserve authored control.

---

## Workflow (High Level)

1. Query graph for current truth.
2. Author narration + clickables.
3. Author responses (pre-baked when possible).
4. Persist new facts as mutations.
5. Return scene/stream output.

---

## Gaps / Ideas / Questions

<!-- @mind:todo Figure out how aggressively the rolling window should pre-author responses -->
  to avoid player-visible generation delays without front-loading every branch.
<!-- @mind:todo Define the minimal authored response inventory that keeps the world feeling -->
  intentional while leaving room for targeted generation.
<!-- @mind:escalation What guardrails should free input respect by default before the -->
  narrator defers to a generator so canon drift is still prevented?
<!-- @mind:proposition Capture canonical click-to-response linkages so designer tooling can -->
  audit when a generator was used instead of authored content.

---

## CHAIN

PATTERNS:        ./PATTERNS_Narrator.md
BEHAVIORS:       ./BEHAVIORS_Narrator.md
ALGORITHM:       ./ALGORITHM_Scene_Generation.md
VALIDATION:      ./VALIDATION_Narrator.md
IMPLEMENTATION:  ./IMPLEMENTATION_Narrator.md
HEALTH:          ./HEALTH_Narrator.md
SYNC:            ./SYNC_Narrator.md
