# API — Algorithm

## OVERVIEW

This algorithm doc describes how the API module wires the FastAPI app, handles
core runtime helpers (graph access, health checks, SSE debug streaming), and
executes the playthrough-creation flow that seeds the game graph and scene
payloads for the frontend.

## DATA STRUCTURES

- Playthrough folder layout: per-player directory containing queues, scene
  snapshots, and metadata files for API and agent coordination.
- Scenario YAML payloads: structured nodes, links, and opening narration blocks
  injected into the per-playthrough graph.
- Moment records: narration lines stored as moment nodes with status/weight,
  linked to locations for initial scene rendering.
- Debug SSE queues: per-client in-memory queues carrying event payloads.

## ALGORITHM: create_scenario_playthrough

The primary flow accepts a scenario request, generates a unique playthrough id,
creates the on-disk playthrough structure, initializes the FalkorDB graph,
injects scenario nodes/links, seeds opening narration moments, and returns the
scene payload plus identifiers required for the frontend to continue.

## KEY DECISIONS

- Use a single app factory to centralize shared resources, keeping endpoints
  thin and delegating heavy logic to orchestration and graph layers.
- Isolate debug SSE streams from gameplay SSE to avoid cross-talk and stalled
  consumers.
- Keep playthrough graphs isolated per player by using a unique graph name.

## DATA FLOW

Client requests enter FastAPI routes, the API loads scenario data from disk,
executes graph mutations through GraphOps, writes playthrough artifacts to
disk, and returns a scene payload that the frontend rehydrates into the game
view while SSE streams deliver ongoing updates.

## COMPLEXITY

Runtime cost is dominated by I/O and graph writes; scenario injection scales
roughly with the number of nodes/links in the scenario, while playthrough
folder creation and scene serialization are linear in payload size.

## HELPER FUNCTIONS

Graph helpers cache GraphQueries/GraphOps instances per request context, health
checks validate read/write access with lightweight queries, and debug SSE
streams maintain per-client queues that emit events or keepalive pings.
Discussion tree helpers count remaining leaf branches to determine when the
background generator should refresh a companion's topics.

## INTERACTIONS

This module coordinates with graph physics for mutations, with orchestration
services for playthrough actions, with scenario files for seed content, and
with frontend hooks that call playthrough and view endpoints.

## MARKERS

<!-- @mind:todo Document API versioning once public clients exist and endpoints stabilize. -->
<!-- @mind:todo Clarify how auth and rate limiting should be layered (API vs gateway). -->
<!-- @mind:escalation Should health checks validate scenario assets on disk? -->

## Graph Helpers

1. On first access, construct `GraphQueries` or `GraphOps` with `graph_name`, `host`, and `port`.
2. Cache the instance for reuse in subsequent requests.

## Health Check

1. Capture the current UTC timestamp.
2. Run `RETURN 1 AS ok` through `GraphQueries` to validate read access.
3. Instantiate `GraphOps` to validate write access.
4. If any step fails, return `503` with a `degraded` status and error details.
5. If all steps succeed, return `status=ok` with connection details.

## Debug Mutation Stream

1. Create an `asyncio.Queue` per connected client.
2. Register the queue in `_debug_sse_clients`.
3. Yield a `connected` event, then enter a loop:
   - Wait up to 30 seconds for queued events.
   - If an event arrives, emit it as an SSE event with a JSON payload.
   - If idle, emit a `ping` keepalive event.
4. On disconnect or cancellation, remove the queue from `_debug_sse_clients`.

---

## Playthrough Creation

### Overview

End-to-end flow when a player creates a new playthrough, from frontend form submission through graph initialization to first scene render.
This section supersedes the deprecated `ALGORITHM_Playthrough_Creation.md` alias.

### Data Structures

- `PlaythroughCreateRequest` carries `scenario_id`, `player_name`, and `player_gender` for creating a new run with consistent inputs.
- `player.yaml`, `scene.json`, and the queue files (`message_queue.json`, `injection_queue.json`, `stream.jsonl`) persist state on disk for later endpoints.
- Scenario YAML provides `nodes`, `links`, and `opening` blocks that seed the graph and opening scene.

### Algorithm: create_playthrough

1. Slugify the player name and pick a unique playthrough ID by checking the playthroughs directory.
2. Create the playthrough directory structure and write `player.yaml` with scenario metadata.
3. Load the scenario YAML and initialize a dedicated graph using `load_initial_state()`.
4. Apply scenario nodes/links with `GraphOps.apply`, updating the player node name/gender.
5. Create opening moments from `opening.narration` and attach them to the opening place.
6. Build `scene.json` from the opening template (fallback to a minimal scene if absent).
7. Return the playthrough ID, scenario ID, and scene payload for the frontend to render.

### Key Decisions

- Use the playthrough ID as the graph name to isolate player sessions without cross-talk.
- Continue after seed-data or scenario injection failures so the frontend can still render a starter scene.
- Store queues and transcripts on disk so async systems can resume from simple file state.

### Data Flow

Request data flows from the frontend form into `create_playthrough`, then into disk state (`player.yaml`, queues) and graph mutations (seed + scenario), culminating in `scene.json` plus a response payload.

### Complexity

Time scales linearly with the number of scenario nodes, links, and opening lines; disk I/O and graph calls dominate runtime for larger scenarios.

### Helper Functions

- `_opening_to_scene_tree` transforms the opening template into the `scene.json` structure.
- `load_initial_state` seeds the base world graph before scenario injection.
- `GraphOps.apply` and `GraphOps.add_moment` write scenario content and opening moments.

### Interactions

Creates playthrough artifacts consumed by `GET /api/view/{playthrough_id}`, relies on `mind/physics/graph` for mutations, and loads scenario assets from `scenarios/*.yaml`.

### Gaps / Ideas / Questions

<!-- @mind:todo Should scenario YAML be schema-validated before graph injection to surface errors earlier? -->
<!-- @mind:todo Should playthrough creation fail hard if seed data fails, or continue as it does now? -->

### Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND FLOW                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. /start                    2. /scenarios                              │
│  ┌──────────────────┐        ┌──────────────────┐                       │
│  │ Enter name       │───────▶│ Select scenario  │                       │
│  │ Select gender    │        │ (5 options)      │                       │
│  │                  │        │                  │                       │
│  │ sessionStorage:  │        │ Click "Begin"    │                       │
│  │  playerName      │        │        │         │                       │
│  │  playerGender    │        └────────┼─────────┘                       │
│  └──────────────────┘                 │                                 │
│                                       ▼                                 │
│                      POST /api/playthrough/create                       │
│                      {scenario_id, player_name, player_gender}          │
│                                       │                                 │
└───────────────────────────────────────┼─────────────────────────────────┘
                                        │
┌───────────────────────────────────────┼─────────────────────────────────┐
│                           BACKEND FLOW                                   │
│                                       ▼                                 │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 1. GENERATE PLAYTHROUGH ID                                       │   │
│  │    - Slugify player name: "Edmund" → "edmund"                    │   │
│  │    - Add suffix if exists: "edmund_2", "edmund_3"...             │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                       │                                 │
│                                       ▼                                 │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 2. CREATE FOLDER STRUCTURE                                       │   │
│  │    playthroughs/{playthrough_id}/                                │   │
│  │    ├── mutations/                                                │   │
│  │    ├── conversations/                                            │   │
│  │    ├── player.yaml          # name, gender, scenario, graph_name │   │
│  │    ├── scene.json           # opening scene for frontend         │   │
│  │    ├── message_queue.json   # player inputs queue                │   │
│  │    ├── injection_queue.json # world events queue                 │   │
│  │    ├── stream.jsonl         # narrator output stream             │   │
│  │    └── PROFILE_NOTES.md     # narrator's player observations     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                       │                                 │
│                                       ▼                                 │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 3. INITIALIZE GRAPH (FalkorDB)                                   │   │
│  │    - Graph name = playthrough_id (isolated per player)           │   │
│  │    - load_initial_state() loads seed data:                       │   │
│  │      • Base world nodes (places, characters)                     │   │
│  │      • Core narratives and pressures                             │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                       │                                 │
│                                       ▼                                 │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 4. LOAD SCENARIO YAML                                            │   │
│  │    scenarios/{scenario_id}.yaml                                  │   │
│  │    Contains:                                                     │   │
│  │      • nodes: characters, places, things specific to scenario    │   │
│  │      • links: relationships, AT positions, BELIEVES edges        │   │
│  │      • opening: {narration, location, characters_present}        │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                       │                                 │
│                                       ▼                                 │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 5. INJECT SCENARIO INTO GRAPH                                    │   │
│  │    - Update char_player with player_name, player_gender          │   │
│  │    - graph.apply(nodes, links) merges into FalkorDB              │   │
│  │    - Creates/updates nodes and relationships                     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                       │                                 │
│                                       ▼                                 │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 6. CREATE OPENING MOMENTS                                        │   │
│  │    - Parse opening.narration from scenario                       │   │
│  │    - Split into lines, create Moment nodes:                      │   │
│  │      {id, text, type:"narration", status:"active", weight:1.0}   │   │
│  │    - Attach to opening location via AT_PLACE edge                │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                       │                                 │
│                                       ▼                                 │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 7. GENERATE scene.json                                           │   │
│  │    - Load opening.json template (discussion tree structure)      │   │
│  │    - Convert to SceneTree format for frontend                    │   │
│  │    - Save to playthrough folder                                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                       │                                 │
│                                       ▼                                 │
│                      RETURN {playthrough_id, scenario, scene}           │
│                                                                          │
└───────────────────────────────────────┬─────────────────────────────────┘
                                        │
┌───────────────────────────────────────┼─────────────────────────────────┐
│                           FRONTEND CONTINUES                             │
│                                       ▼                                 │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 8. REDIRECT TO GAME                                              │   │
│  │    - Store playthrough_id in sessionStorage                      │   │
│  │    - Navigate to /playthroughs/{playthrough_id}                  │   │
│  │    - useGameState() fetches /api/view/{playthrough_id}           │   │
│  │    - Renders moments from active_moments                         │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### Key Files

| Step | File | Purpose |
|------|------|---------|
| 1-2 | `frontend/app/start/page.tsx` | Name/gender input |
| 2 | `frontend/app/scenarios/page.tsx` | Scenario selection |
| 3-7 | `mind/infrastructure/api/playthroughs.py` | POST /playthrough/create |
| 3 | `mind/init_db.py` | load_initial_state() |
| 4 | `scenarios/*.yaml` | Scenario definitions |
| 5 | `mind/physics/graph/graph_ops.py` | apply() for graph injection |
| 6 | `mind/physics/graph/graph_ops.py` | add_moment() |
| 8 | `frontend/hooks/useGameState.ts` | Fetches view, renders scene |

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/playthrough/create` | POST | Create new playthrough from scenario |
| `/api/playthrough/scenario` | POST | Alternative endpoint (same function) |
| `/api/view/{playthrough_id}` | GET | Get current view for rendering |

### Error States

| Error | Cause | Fix |
|-------|-------|-----|
| 404 on /scenario | Wrong endpoint path | Use `/api/playthrough/scenario` |
| "No moments found, needs opening" | Opening moments not created | Check step 6, verify graph has Moments |
| Empty view | Player not AT any location | Check scenario has player AT link |

---

## CHAIN

PATTERNS: ./PATTERNS_Api.md
BEHAVIORS: ./BEHAVIORS_Api.md
ALGORITHM: ./ALGORITHM_Api.md
VALIDATION: ./VALIDATION_Api.md
IMPLEMENTATION: ./IMPLEMENTATION_Api.md
TEST: ./TEST_Api.md
SYNC: ./SYNC_Api.md
