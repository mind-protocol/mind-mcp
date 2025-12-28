# Narrator — Algorithm: Scene Generation

```
CREATED: 2024-12-16
UPDATED: 2025-12-19
STATUS: Canonical (condensed)
DEPENDS_ON: graph.json, character backstories
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Narrator.md
BEHAVIORS:       ./BEHAVIORS_Narrator.md
THIS:            ALGORITHM_Scene_Generation.md (you are here)
VALIDATION:      ./VALIDATION_Narrator.md
IMPLEMENTATION:  ./IMPLEMENTATION_Narrator.md
TEST:            ./TEST_Narrator.md
SYNC:            ./SYNC_Narrator.md

IMPL:            agents/narrator/CLAUDE.md
```

---

## PURPOSE

Define the minimal, reliable generation flow that keeps narration responsive, graph-canonical, and ready to output the shaped payload that downstream tools expect. This write-up clarifies how the narrator classifies actions, streams dialogue, queries the graph for truth, invents when needed, and closes the loop with the schema-aligned response envelope.

By tracking world-injection urgency and thread health inside the same narrative frame, the algorithm prevents injected beats from derailing continuity while still surfacing the new facts the composer intended.

---

## OVERVIEW

This algorithm coordinates scene narration with graph-backed truth, balancing stream-first delivery with the need to record invented details. It keeps a persistent thread going so every chunk of dialogue inherits a shared memory while still deciding when to synthesize new facts and mutate the graph so the next round can consume them.

By explicitly tagging the action as either conversational or significant, the narrator avoids overloading lightweight exchanges with expensive SceneTree payloads and only builds the full tree when pacing demands it. Graph queries and invention steps happen in parallel with streaming so latency stays low while the structured output eventually arrives complete.

It also demystifies how world injection fragments (`heard`, `witnessed`, `will_hear`, `interruption`) flow through the decision layers, so downstream agents know that urgencies raise the significance threshold without breaking the rolling window.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| Stream-first narration | `BEH-STREAM-FIRST` | Guarantees the first dialogue chunk reaches the player before heavier graph work, keeping interactions snappy. |
| Canonical mutation persistence | `BEH-MUTATION-PERSISTENCE` | Ensures every invented detail is recorded so future queries and scenes stay consistent with the narrator’s claims. |
| Mode-aware payload gating | `BEH-SCENE-TREE` | Adds SceneTrees and `time_elapsed` only during significant actions, preventing unnecessary payload bloat during conversational turns. |

---

## DATA STRUCTURES

### NarratorOutput

```
Envelope for the narrator response.
Fields: dialogue_chunks (ordered list of streamed text), mutation_batch (facts to persist), scene (optional SceneTree or {}), metadata (mode tag, thread id, time_elapsed if significant).
```

### SceneTree

```
Structured snapshot of the current scene.
Fields: nodes (characters, locations), edges (relationships or actions), clickables (pre-filled responses), pacing_tags (significant vs conversational cues).
```

### ActionClassification

```
Derived label that picks conversational or significant mode.
Fields: estimated_duration (seconds), injective_flags (world injection urgency), graph_density (fact density score).
```

### MutationBatch

```
Collection of canonical facts created during narration.
Fields: mutations (list of nodes/edges/attributes), origin_thread (thread id), audit_tags (reason for invention, source action).
```

---

## ALGORITHM: generate_scene_output

### Step 1: Normalize and classify context

Gather the incoming action, relevant graph slice, thread metadata, and any world injection overrides, then normalize timestamps, resolve click contexts, and push everything through `classify_action`. The resulting `ActionClassification` determines thresholds, pacing tags, and whether the stream will be conversational or significant.

### Step 2: Stream while reconciling truth

Emit the first dialogue chunk immediately with `stream_dialogue_first` to honor the stream-first rule, then run `query_graph_if_needed` and `invent_missing_facts` concurrently. Graph queries are scoped to clickables and context nodes; invention only runs when the graph lacks explicit answers and attaches audit metadata for later inspection.

```
if action_classification.estimated_duration >= SIGNIFICANT_THRESHOLD:
    mode = "significant"
else:
    mode = "conversational"

stream_dialogue_first()
facts = query_graph_if_needed()
mutations = invent_missing_facts(facts)
persist_mutations(mutations)
```

### Step 3: Finalize response payload

If the mode is significant, run `build_scene_tree` to materialize the new SceneTree, add `time_elapsed`, and attach clickables for the next layer; otherwise, set `scene = {}` and leave `time_elapsed` empty. Return the assembled `NarratorOutput` containing the dialogue stream metadata, mutation batch, and the optional scene payload so downstream tools receive the expected schema.

---

## KEY DECISIONS

### D1: Significant payload vs conversational lean

```
IF action_classification.is_significant:
    scene = build_scene_tree()
    time_elapsed = action_classification.estimated_duration
ELSE:
    scene = {}
    time_elapsed = None
```

Keeping this branch ensures we only emit heavy SceneTrees when the action clearly crosses the significant threshold, preserving responsiveness for quick dialogue.

### D2: Invent only when graph truth is missing

```
IF facts.cover_click_targets():
    mutations = []
ELSE:
    mutations = invent_missing_facts()
```

Abstaining from invention when the graph already covers the clickables protects canon integrity and keeps mutation batches tightly scoped.

---

## DATA FLOW

```
Action + Thread Context + Graph Slice
    ↓
classify_action + prompt assembly
    ↓
stream_dialogue_first (immediate chunk) + query_graph_if_needed
    ↓
invent_missing_facts (if needed) → persist_mutations
    ↓
build_scene_tree (significant only) + attach time_elapsed
    ↓
NarratorOutput (dialogue chunks, mutations, optional scene, metadata)
```

---

## COMPLEXITY

**Time:** O(G + M) — where G is the number of graph facts fetched and M is the newly invented mutation count, because streaming and classification stay constant-time while queries and persistence scale with graph coverage.

**Space:** O(D + M) — dialogue metadata D and mutation batch size M dominate, especially when multiple invention branches open new clickables.

**Bottlenecks:**
- Graph queries for clickables: retrieving canonical facts for dozens of nodes can block the stream if the database is slow.
- Mutation persistence: writing invented facts before the final payload must finish before `NarratorOutput` is returned, so latency here directly delays the last chunk.

---

## HELPER FUNCTIONS

### `classify_action()`

**Purpose:** Map the incoming action to conversational or significant mode.

**Logic:** Normalize timestamps, check `time_elapsed`, evaluate world injection urgency, and return an `ActionClassification` that sets thresholds for streaming, mutation persistence, and SceneTree building.

### `stream_dialogue_first()`

**Purpose:** Deliver the first chunk of text before expensive graph work begins.

**Logic:** Emit the first narrator chunk using cached tone templates, mark it as pending, and signal the frontend stream consumer that the slot is occupied while the rest of the pipeline runs.

### `query_graph_if_needed()`

**Purpose:** Fetch canonical facts for clickables or context nodes referenced by the action.

**Logic:** Use the graph slice (from `graph.json` or FalkorDB) to return facts that cover click targets and check if any new nodes must be consulted.

### `invent_missing_facts()`

**Purpose:** Synthesize details when the graph lacks canonical answers.

**Logic:** Compare clickable requirements to fetched facts, run constrained generation to invent missing pieces, tag each invention with motivation metadata, and emit a `MutationBatch`.

### `persist_mutations()`

**Purpose:** Write invented facts back into canon storage before returning the final response.

**Logic:** Open a transaction, apply each mutation (nodes/edges attributes), record the origin thread, and add auditing metadata so downstream verification knows why the fact exists.

### `build_scene_tree()`

**Purpose:** Construct the `SceneTree` payload for significant actions.

**Logic:** Combine the normalized action, persisted mutations, and clickables into a structured tree with nodes, edges, pacing tags, and references to the latest world injection if present.

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| `agents/narrator/CLAUDE.md` | prompt orchestration | stream-started dialogue, thread state |
| Graph service (FalkorDB via `GraphReadOps`) | fact reads | canonical click facts and context |
| World tick pipeline | significant action trigger | time advancement + scheduled injections |
| Frontend stream consumer | open SSE/websocket slot | immediate player-visible chunks |

---

## MARKERS

<!-- @mind:todo Evaluate adaptive rolling-window depth when player latency grows above 3 seconds so narration stays ahead of clicks. -->
<!-- @mind:todo Capture richer metadata that distinguishes invented facts from retrieved facts for audit tooling and chaos testing. -->
<!-- @mind:proposition Replace the binary significant/conversational classification with a pacing score so short significant bursts still produce SceneTrees when needed. -->
<!-- @mind:escalation Should certain high-urgency world injections temporarily suppress SceneTree builds to avoid conflicting pacing signals? -->

---

## ROLLING WINDOW (SUMMARY)

The narrator pre-generates one layer of clickable responses and background-generates the next layer as the player clicks, keeping the perceived latency low. For the full architectural story, reference `HANDOFF_Rolling_Window_Architecture.md`.

---

## THREAD CONTINUITY (SUMMARY)

Use a single persistent thread per playthrough; `--continue` keeps the narrator tied to earlier output, and only summarize history when thread tokens approach the service limits so the narrative does not regress.

---

## QUALITY CHECKS (MINIMUM)

- Immediate first chunk (stream-first rule).
- Every invention is paired with a mutation.
- Clickables surface in the text before the click window closes.
- Mode classification matches the `time_elapsed` rules.

---

*"Talk first. Query as you speak. Invent when the graph is silent."*
