# Narrator — Behaviors: What the Narrator Produces

```
CREATED: 2024-12-16
UPDATED: 2025-12-19
STATUS: Canonical
```

---

## CHAIN

PATTERNS:        ./PATTERNS_Narrator.md  
ALGORITHM:       ./ALGORITHM_Scene_Generation.md  
VALIDATION:      ./VALIDATION_Narrator.md  
IMPLEMENTATION:  ./IMPLEMENTATION_Narrator.md  
TEST:            ./TEST_Narrator.md  
SYNC:            ./SYNC_Narrator.md  

---

## Two Response Modes

| Mode | Threshold | Output |
|------|-----------|--------|
| Conversational | <5 minutes | Dialogue chunks + mutations + `scene: {}` |
| Significant | >=5 minutes | Dialogue chunks + mutations + full SceneTree + time_elapsed |

---

## Dialogue Chunks

- Streamed in real-time as the narrator generates.
- Chunks with `speaker` are dialogue; chunks without `speaker` are narration.
- First chunk must arrive quickly (stream-first rule).

Schema: `TOOL_REFERENCE.md`.

---

## Graph Mutations

- Every invention must be persisted as a mutation.
- Mutations must link to existing graph nodes (or nodes in the same batch).
- Mutation schemas are defined in `runtime/models/` (see `TOOL_REFERENCE.md`).

---

## SceneTree (Significant Actions)

- Full scene tree is returned only for significant actions.
- Clickables must either include a pre-baked response or a waitingMessage.
- New clickables may appear in responses to extend the scene.

Schema: `TOOL_REFERENCE.md`.

---

## time_elapsed Rules

- Only include `time_elapsed` for significant actions.
- Conversational actions omit it entirely to keep the stream light and avoid implying every click should be tracked with a timestamp.

---

## BEHAVIORS

- Produces narrations and dialogue that stay anchored to current graph state and recent actions, with clear continuity and referential consistency.
- Emits a streaming response where the first chunk arrives fast and subsequent chunks preserve voice, pacing, and scene context.
- Returns a full SceneTree only for significant actions, while conversational actions return an empty scene structure.
- Persists inventions as graph mutations so new facts are canon and can be queried immediately in the next turn.

---

## OBJECTIVES SERVED

- Ensure the opening chunk lands within the 1-2 second window so streaming consumers can start rendering while the narrator continues composing the rest of the story without blocking.
- Keep every response traceable to the canonical graph state by persisting new inventions as mutations and referencing existing nodes, giving continuity tooling a single truthful timeline.
- Signal whether the action is conversational or significant so orchestrators know when to expect the lightweight placeholder scene versus a fully populated SceneTree with `time_elapsed`.
- Surface mutation metadata, pacing telemetry, and world-injection flags so health monitors and analytics can verify the narrator is honoring canon and avoiding runaway invention.

---

## INPUTS / OUTPUTS

Inputs include the player action payload, recent scene state, and any world injection breaks defined in `docs/agents/narrator/INPUT_REFERENCE.md`. Outputs are streamed narrator chunks plus mutations and either `scene: {}` or a full SceneTree as defined in `docs/agents/narrator/TOOL_REFERENCE.md`.

---

## EDGE CASES

- If graph context is sparse, the narrator should invent minimally, then persist it as mutations so the next step can reference it.
- If streaming stalls, the narrator must still honor the stream-first rule by sending an opening chunk before any long reasoning.
- If world injection conflicts with current narration, urgent interruptions override and the conflict is surfaced through character reactions.

---

## ANTI-BEHAVIORS

- Do not invent facts without recording mutations; unpersisted facts cause canon drift and break future continuity checks.
- Do not emit a full SceneTree for conversational actions; that breaks the lightweight response contract and slows the stream.
- Do not include `time_elapsed` for conversational actions; it must only appear on significant actions.

---

## MARKERS

Gaps: Recovery behavior for interrupted streams is documented elsewhere but not fully enumerated here.  
Ideas: Add explicit expectations for narrator fallback phrasing when click responses are missing.  
Questions: Should the narrator ever suppress mutations for clearly non-canonical chatter?

---

## World Injection Handling

When world injection is present (see `INPUT_REFERENCE.md`):
- `witnessed` breaks are woven directly into narration.
- `heard` breaks arrive as news from characters or messengers.
- `will_hear` breaks are noted but not surfaced yet.
- `interruption` with high urgency overrides the current flow.

---

## Quality Indicators

- Voice consistency: characters sound distinct and stable.
- Response time: first chunk within 1-2 seconds.
- Connection density: new content links to existing graph state.
- Setup/payoff: seeds are tracked and paid off later.

---

*"The narrator doesn't just produce text. It produces a world that grows through conversation."*
