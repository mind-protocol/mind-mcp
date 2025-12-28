# Graph Management API

```
DOCS: mind/infrastructure/api/graphs.py
STATUS: IMPLEMENTED
UPDATED: 2025-12-22
```

---

## Purpose

Generic graph lifecycle endpoints for mind consumers. Games (like blood-ledger) call these to create isolated graph instances for their sessions.

**Ownership boundary:**
- mind owns: graph creation, cloning, deletion, generic queries
- Consumer owns: session concept (playthroughs), game logic, scenarios

---

## Endpoints

### POST /api/graph/create

Create a new named graph, optionally cloning from a template.

**Request:**
```json
{
    "name": "pt_abc123",
    "copy_from": "seed"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | yes | Unique graph name |
| `copy_from` | string | no | Source graph to clone (e.g., "seed") |

**Response (201):**
```json
{
    "name": "pt_abc123",
    "created_at": "2025-12-22T18:30:00Z",
    "copied_from": "seed",
    "node_count": 47,
    "edge_count": 123
}
```

**Errors:**
- `409 Conflict`: Graph already exists
- `404 Not Found`: `copy_from` graph doesn't exist

---

### DELETE /api/graph/{name}

Delete a graph and all its data.

**Response (200):**
```json
{
    "name": "pt_abc123",
    "deleted": true
}
```

**Errors:**
- `404 Not Found`: Graph doesn't exist

---

### GET /api/graph/{name}/info

Get graph metadata and statistics.

**Response (200):**
```json
{
    "name": "pt_abc123",
    "node_count": 52,
    "edge_count": 134,
    "node_types": ["Actor", "Space", "Thing", "Narrative", "Moment"],
    "edge_types": ["AT", "BELIEVES", "RELATES_TO", "FOLLOWS"]
}
```

---

### GET /api/graph/{name}/nodes

Query nodes with optional filters.

**Query params:**
- `label`: Filter by node label (e.g., "Character")
- `limit`: Max results (default 100)
- `offset`: Pagination offset

**Response (200):**
```json
{
    "nodes": [
        {"id": "char_aldric", "label": "Character", "name": "Aldric", ...}
    ],
    "total": 12,
    "limit": 100,
    "offset": 0
}
```

---

### POST /api/graph/{name}/query

Execute a Cypher query (read-only for safety).

**Request:**
```json
{
    "cypher": "MATCH (c:Character) WHERE c.type = $type RETURN c",
    "params": {"type": "companion"}
}
```

**Response (200):**
```json
{
    "results": [...],
    "count": 3
}
```

---

### POST /api/graph/{name}/mutate

Execute Cypher mutations (CREATE, MERGE, SET, DELETE).

**Request:**
```json
{
    "cypher": "CREATE (c:Character {id: $id, name: $name})",
    "params": {"id": "char_new", "name": "New Guy"}
}
```

**Response (200):**
```json
{
    "success": true,
    "stats": {
        "nodes_created": 1,
        "relationships_created": 0,
        "properties_set": 2
    },
    "result": []
}
```

**Notes:**
- Use individual parameters, not `$props` maps (FalkorDB limitation)
- For bulk mutations, call multiple times or use GraphOps.apply()

---

## Implementation Notes

### Graph Cloning

FalkorDB doesn't have native COPY. Clone via:
1. Query all nodes from source: `MATCH (n) RETURN n`
2. Query all edges from source: `MATCH ()-[r]->() RETURN r`
3. Create in target graph

### Graph Names

Convention for consumers:
- blood-ledger: `bl_{playthrough_id}` (e.g., `bl_pt_abc123`)
- Other games: `{game_prefix}_{session_id}`

Template graphs:
- `seed` — canonical starting state for blood-ledger

---

## Migration: What Moves to blood-ledger

| Current Location | New Location | Notes |
|------------------|--------------|-------|
| `mind/infrastructure/api/playthroughs.py` | blood-ledger | All playthrough logic |
| `get_playthrough_graph_name()` | blood-ledger | Naming is game-specific |
| Scenario loading in orchestrator | blood-ledger | Game content |
| `opening.json` templates | blood-ledger | Game content |

**mind keeps:**
- GraphOps / GraphQueries
- Physics engine (tick, energy, flips)
- Generic graph API (this spec)
- Moment operations (generic)

---

## Status

All endpoints implemented in `mind/infrastructure/api/graphs.py`:
- [x] `POST /api/graph/create` with clone support
- [x] `DELETE /api/graph/{name}`
- [x] `GET /api/graph/{name}` (info)
- [x] `GET /api/graph/{name}/nodes`
- [x] `POST /api/graph/{name}/query` (read-only)
- [x] `POST /api/graph/{name}/mutate` (writes)
- [x] blood-ledger integration tested
