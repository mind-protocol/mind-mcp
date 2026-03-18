# Spatial Presence — Implementation: Code Architecture and Structure

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Spatial_Presence.md
BEHAVIORS:       ./BEHAVIORS_Spatial_Presence.md
PATTERNS:        ./PATTERNS_Spatial_Presence.md
ALGORITHM:       ./ALGORITHM_Spatial_Presence.md
VALIDATION:      ./VALIDATION_Spatial_Presence.md
THIS:            IMPLEMENTATION_Spatial_Presence.md (you are here)
HEALTH:          ./HEALTH_Spatial_Presence.md
SYNC:            ./SYNC_Spatial_Presence.md

IMPL:           schema-l1.yaml (NodeBase fields)
                scripts/spatial_mapper.py
                runtime/cognition/physics_visual_mapping.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

```
mind-mcp/
├── schema-l1.yaml                          # NodeBase spatial field definitions
├── schema-l3.yaml                          # L3 spatial positioning context
├── scripts/
│   └── spatial_mapper.py                   # Mapper: computes position, zone_id, scale, mass
├── runtime/
│   └── cognition/
│       └── physics_visual_mapping.py       # Weight→radius, energy→glow (visual layer)
└── docs/
    └── schema/
        └── spatial_presence/               # This doc chain
```

### File Responsibilities

| File | Purpose | Key Functions/Classes | Lines | Status |
|------|---------|----------------------|-------|--------|
| `schema-l1.yaml` | Defines the 6 spatial fields on NodeBase | N/A (schema) | ~870 | OK |
| `scripts/spatial_mapper.py` | Computes position, zone_id from graph state | `compute_affinity()`, `compute_position()`, `map_graph()` | ~272 | OK |
| `runtime/cognition/physics_visual_mapping.py` | Physics→visual translation (related: node_radius from weight) | `node_radius()`, `NodeVisual.from_physics()` | ~296 | OK |

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Batch Computation Pipeline

**Why this pattern:** Spatial fields are not computed per-tick. The spatial mapper runs periodically, reads all nodes from the graph, computes positions, and writes them back in batch. This decouples spatial computation from the physics tick loop (which must complete in <1 second).

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Deterministic Hash | `spatial_mapper.py:compute_position()` | Stable dispersion within clusters — same node ID always produces same offset |
| Barycentrique Interpolation | `spatial_mapper.py:compute_position()` | Continuous position between zone attractors |
| Logarithmic Mapping | `physics_visual_mapping.py:node_radius()` | Weight→size with visual distinction across full range |

### Anti-Patterns to Avoid

- **Force-directed layout**: Tempting for organic clustering, but too chaotic. Fixed zone attractors with barycentrique interpolation provides stability.
- **Per-tick position recomputation**: Would stall the physics tick. Positions change slowly; periodic batch computation is sufficient.
- **Storing derived fields redundantly**: Scale and mass are derived from weight and link_count. They are written to the graph for renderer access but weight remains the source of truth.

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Spatial Mapper | Affinity computation, barycentrique, dispersion, zone assignment | 3D rendering, vision cone, proprioception | Writes position/zone_id/scale/mass to FalkorDB nodes |
| Schema Definition | Field types, constraints, defaults, descriptions | Computation logic | schema-l1.yaml NodeBase fields |
| Visual Mapping | Weight→radius, energy→glow, stability→opacity | Spatial position, zone assignment | `NodeVisual.from_physics()` |

---

## SCHEMA

### Spatial Fields on NodeBase

```yaml
NodeBase.spatial:
  required: false  # all spatial fields are nullable
  fields:
    - position: array[float, 3]         # [x, y, z] world cartesian
    - orientation: array[float, 4]      # [qx, qy, qz, qw] unit quaternion
    - scale: float                      # default 1.0, >= 1.0
    - velocity: array[float, 3]         # [vx, vy, vz] world units/tick
    - mass: float                       # default 1.0, >= 0.0
    - zone_id: string                   # one of 7 zone identifiers or null
  constraints:
    - position elements are finite floats (no NaN, no Infinity)
    - orientation magnitude within [0.999, 1.001]
    - scale >= 1.0
    - mass >= 0.0
    - zone_id in {radiant_core, innovation_fields, towers_of_knowledge,
      data_gardens, creative_nexus, arsenal, resonance_plaza} or null
    - if position is non-null then zone_id is non-null (V8)
    - if zone_id is non-null then position is non-null (V8)
```

### Zone Attractor Registry

```yaml
ZoneAttractor:
  required:
    - id: string               # zone identifier
    - position: array[float, 3] # fixed world coordinates
    - mass: float               # base gravitational mass
  instances: 7                  # fixed, not extensible without schema change
```

---

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| `map_graph()` | `scripts/spatial_mapper.py:182` | CLI invocation or periodic scheduler |
| `compute_position()` | `scripts/spatial_mapper.py:138` | Called by `map_graph()` for each node |
| `compute_affinity()` | `scripts/spatial_mapper.py:110` | Called by `compute_position()` for each zone |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

### Spatial Mapping Flow: Graph Nodes to 3D Positions

This flow covers the periodic batch computation that reads all L3 nodes, computes their spatial fields, and writes them back. It transforms abstract graph nodes into positioned 3D objects. This is the primary flow for 4 of the 6 spatial fields (position, scale, mass, zone_id).

```yaml
flow:
  name: spatial_mapping
  purpose: Transform cognitive graph state into 3D spatial coordinates
  scope:
    input: All L3 nodes in FalkorDB with cognitive fields
    output: position, scale, mass, zone_id written to each node
    boundary: FalkorDB graph (read + write)
  steps:
    - id: step_1_read_nodes
      description: Query all nodes from the L3 graph with cognitive fields
      file: scripts/spatial_mapper.py
      function: map_graph()
      input: graph_name (string)
      output: list of node dicts with id, node_type, type, weight, energy, etc.
      trigger: CLI invocation or scheduler
      side_effects: none (read only)

    - id: step_2_compute_affinities
      description: For each node, compute affinity score against all 7 zones
      file: scripts/spatial_mapper.py
      function: compute_affinity(node, zone_name)
      input: node dict, zone_name string
      output: float affinity score
      trigger: Called 7x per node by compute_position
      side_effects: none

    - id: step_3_compute_position
      description: Barycentrique + dispersion + y-offset = final [x, y, z] + zone_id
      file: scripts/spatial_mapper.py
      function: compute_position(node)
      input: node dict
      output: (x, y, z, zone_id) tuple
      trigger: Called per node by map_graph
      side_effects: none

    - id: step_4_write_graph
      description: Write position and zone_id to the node in FalkorDB
      file: scripts/spatial_mapper.py
      function: map_graph() (write loop)
      input: node id, position [x,y,z], zone_id
      output: FalkorDB node updated
      trigger: After compute_position
      side_effects: FalkorDB MATCH/SET query per node

  docking_points:
    guidance:
      include_when: Graph read/write boundaries, affinity computation output
      omit_when: Internal loop iteration
      selection_notes: Health should verify graph write success and position bounds
    available:
      - id: dock_graph_read
        type: db
        direction: input
        file: scripts/spatial_mapper.py
        function: map_graph()
        trigger: CLI or scheduler
        payload: list[node_dict]
        async_hook: not_applicable
        needs: none
        notes: Reads all nodes — performance sensitive at scale

      - id: dock_affinity_output
        type: custom
        direction: output
        file: scripts/spatial_mapper.py
        function: compute_affinity()
        trigger: Called per node per zone
        payload: float (affinity score)
        async_hook: not_applicable
        needs: none
        notes: 7 scores per node — sum must be > 0

      - id: dock_position_output
        type: custom
        direction: output
        file: scripts/spatial_mapper.py
        function: compute_position()
        trigger: Called per node
        payload: (x, y, z, zone_id)
        async_hook: not_applicable
        needs: none
        notes: Must satisfy V1 (bounds) and V5 (zone matches affinity)

      - id: dock_graph_write
        type: db
        direction: output
        file: scripts/spatial_mapper.py
        function: map_graph()
        trigger: After position computation
        payload: {id, position, zone_id}
        async_hook: not_applicable
        needs: none
        notes: One write query per node — batch optimization possible

    health_recommended:
      - dock_id: dock_position_output
        reason: Verify V1 (bounds), V5 (zone matches affinity), V8 (consistency)
      - dock_id: dock_graph_write
        reason: Verify writes succeed and graph reflects computed positions
```

### Engine Update Flow: Orientation and Velocity

This flow covers real-time updates from the 3D engine. When a citizen moves or rotates, the engine writes orientation and velocity to the graph. These are the 2 engine-computed spatial fields.

```yaml
flow:
  name: engine_spatial_update
  purpose: Update orientation and velocity from 3D engine movement
  scope:
    input: Movement/rotation events from Three.js engine
    output: orientation, velocity written to actor nodes in FalkorDB
    boundary: Engine → FalkorDB
  steps:
    - id: step_1_movement_event
      description: Engine detects actor movement or rotation
      file: engine/ (Three.js client)
      function: TBD
      input: user/AI movement input
      output: new position delta, new facing direction
      trigger: Per-frame engine loop
      side_effects: none

    - id: step_2_compute_velocity
      description: Velocity = position delta / frame delta time
      file: engine/ (Three.js client)
      function: TBD
      input: position(t), position(t-1), delta_t
      output: velocity [vx, vy, vz]
      trigger: Per-frame
      side_effects: none

    - id: step_3_write_orientation_velocity
      description: Write orientation quaternion and velocity to the actor node
      file: engine/ (Three.js client)
      function: TBD
      input: actor node id, orientation, velocity
      output: FalkorDB node updated
      trigger: On significant change (not every frame)
      side_effects: FalkorDB write

  docking_points:
    guidance:
      include_when: Graph writes of orientation and velocity
      omit_when: Per-frame interpolation internal to engine
      selection_notes: Health should verify quaternion normalization on write
    available:
      - id: dock_orientation_write
        type: db
        direction: output
        file: engine/ (TBD)
        function: TBD
        trigger: On rotation change
        payload: {actor_id, orientation [qx,qy,qz,qw]}
        async_hook: optional
        needs: add validation hook
        notes: Must satisfy V2 (normalized quaternion)

      - id: dock_velocity_write
        type: db
        direction: output
        file: engine/ (TBD)
        function: TBD
        trigger: On movement change
        payload: {actor_id, velocity [vx,vy,vz]}
        async_hook: optional
        needs: add validation hook
        notes: Must satisfy V7 (null when stationary)

    health_recommended:
      - dock_id: dock_orientation_write
        reason: Verify V2 (quaternion normalized) and V9 (default valid)
```

---

## LOGIC CHAINS

### LC1: Node to Position

**Purpose:** Full pipeline from graph node to 3D position.

```
FalkorDB node
  → spatial_mapper.compute_affinity(node, zone)   # 7x → affinity scores
    → spatial_mapper.compute_position(node)        # barycentrique + dispersion
      → [x, y, z], zone_id
        → FalkorDB SET n.position, n.zone_id
```

**Data transformation:**
- Input: `dict` — raw node with cognitive fields
- After affinity: `dict[str, float]` — 7 affinity scores
- After barycentrique: `(float, float, float)` — raw position
- After dispersion + y-offset: `(float, float, float, str)` — final position + zone_id

### LC2: Weight to Scale and Mass

**Purpose:** Derive visual and gravitational properties from cognitive weight.

```
node.weight, node.link_count
  → scale = 1.0 + log1p(weight)
  → mass = weight * (1 + 0.1 * link_count)
  → FalkorDB SET n.scale, n.mass
```

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
scripts/spatial_mapper.py
    └── imports → hashlib (stdlib, deterministic hashing)
    └── imports → math (stdlib, log1p)
    └── imports → falkordb (FalkorDB Python client)
    └── reads  → schema-l1.yaml (field definitions, conceptual dependency)
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `falkordb` | Graph database read/write | `scripts/spatial_mapper.py` |
| `hashlib` | Deterministic node dispersion | `scripts/spatial_mapper.py` |
| `math` | log1p for scale computation | `scripts/spatial_mapper.py`, `runtime/cognition/physics_visual_mapping.py` |

---

## STATE MANAGEMENT

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| Node position | FalkorDB `n.position` | Per-node | Written by mapper, persists until next mapper run |
| Node orientation | FalkorDB `n.orientation` | Per-node | Written by engine, persists until next movement |
| Node scale | FalkorDB `n.scale` | Per-node | Written by mapper, derived from weight |
| Node velocity | FalkorDB `n.velocity` | Per-node | Written by engine, null when stationary |
| Node mass | FalkorDB `n.mass` | Per-node | Written by mapper, derived from weight + links |
| Node zone_id | FalkorDB `n.zone_id` | Per-node | Written by mapper, highest affinity zone |
| Display position | Engine memory | Per-node, per-client | Damped interpolation, ephemeral |

### State Transitions

```
New node (no spatial fields) ──mapper run──> Positioned node (position, zone_id, scale, mass)
                                              ──engine movement──> Moving node (+orientation, +velocity)
                                              ──next mapper run──> Updated position (damped migration)
                                              ──actor stops──> Stationary node (velocity = null)
```

---

## RUNTIME BEHAVIOR

### Initialization

```
1. Schema defines spatial fields on NodeBase with nullable defaults
2. Spatial mapper first run: reads all nodes, computes positions, writes to graph
3. Engine reads positions for initial 3D placement
```

### Main Loop (Spatial Mapper — Periodic)

```
1. Read all nodes from FalkorDB with cognitive fields
2. For each node: compute affinities, barycentrique position, dispersion, scale, mass, zone_id
3. Write position, scale, mass, zone_id back to FalkorDB
4. Log zone distribution summary
```

### Main Loop (Engine — Per-Frame)

```
1. Read target positions from FalkorDB (or cached)
2. Apply damping: display_pos = lerp(display_pos, target_pos, 0.05)
3. On actor movement: compute velocity, update orientation
4. Write orientation + velocity to FalkorDB (throttled, not every frame)
```

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `DAMPING` | Renderer / engine | `0.95` | Position interpolation damping factor |
| `BASE_RADIUS` | `spatial_mapper.py` | `30.0` | Base cluster dispersion radius |
| `DISPERSION_FACTOR` | `spatial_mapper.py` | `0.7` | Dispersion multiplier within cluster |
| `KEYWORD_WEIGHT` | `spatial_mapper.py` | `0.2` | Weight of keyword matches in affinity |
| Zone attractors | `spatial_mapper.py:ZONE_ATTRACTORS` | See table | Fixed positions and masses of 7 zones |

---

## BIDIRECTIONAL LINKS

### Code to Docs

| File | Line | Reference |
|------|------|-----------|
| `scripts/spatial_mapper.py` | 4-5 | `# lumina-prime/docs/city-architecture/spatial-mapping/ALGORITHM_Spatial_Mapping.md` |

### Docs to Code

| Doc Section | Implemented In |
|-------------|----------------|
| ALGORITHM: Position (Steps 1-5) | `scripts/spatial_mapper.py:compute_position()` |
| ALGORITHM: Affinity | `scripts/spatial_mapper.py:compute_affinity()` |
| ALGORITHM: Scale | Not yet in mapper (formula defined but not written to graph) |
| ALGORITHM: Mass | Not yet in mapper (formula defined but not written to graph) |
| ALGORITHM: Orientation | Engine (TBD) |
| ALGORITHM: Velocity | Engine (TBD) |
| ALGORITHM: Damping | Engine (TBD) |

---

## EXTRACTION CANDIDATES

No files are at WATCH or SPLIT status. All files are under 300 lines.

---

## MARKERS

<!-- @mind:todo Add scale and mass computation to spatial_mapper.py (currently only computes position + zone_id) -->
<!-- @mind:todo Implement engine-side orientation and velocity writes to FalkorDB -->
<!-- @mind:todo Add DOCS: marker to spatial_mapper.py referencing this doc chain -->
<!-- @mind:todo Implement damping in the Three.js engine renderer -->
<!-- @mind:proposition Create a spatial_validator.py that checks V1-V9 invariants on the graph -->
