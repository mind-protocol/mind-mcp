# Spatial Presence — Algorithm: How Each Spatial Field Is Computed

```
STATUS: DESIGNING
CREATED: 2026-03-18
VERIFIED: —
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Spatial_Presence.md
BEHAVIORS:       ./BEHAVIORS_Spatial_Presence.md
PATTERNS:        ./PATTERNS_Spatial_Presence.md
THIS:            ALGORITHM_Spatial_Presence.md (you are here)
VALIDATION:      ./VALIDATION_Spatial_Presence.md
IMPLEMENTATION:  ./IMPLEMENTATION_Spatial_Presence.md
HEALTH:          ./HEALTH_Spatial_Presence.md
SYNC:            ./SYNC_Spatial_Presence.md

IMPL:           schema-l1.yaml (NodeBase spatial fields, lines 231-263)
                scripts/spatial_mapper.py
                runtime/cognition/physics_visual_mapping.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

Six spatial fields on NodeBase give every node a complete physical presence in 3D space. This document specifies exactly how each field is computed: what inputs it reads, what formula it applies, and what system writes it. The fields divide into two groups: **mapper-computed** (position, scale, mass, zone_id — written by the spatial mapper on periodic runs) and **engine-computed** (orientation, velocity — written by the 3D engine in real time).

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| O1: Physical presence | B1, B7 | Defines how position and zone_id are produced |
| O2: Derived, not assigned | B1, B2, B5 | All formulas derive spatial from cognitive fields |
| O3: Visual stability | B6 | Damping formula prevents position jumps |
| O4: Vision + proprioception | B3, B4 | Orientation and velocity computation |
| O5: Gravitational clustering | B5 | Mass formula and gravitational pull |

---

## DATA STRUCTURES

### Spatial State Vector (per node)

```
spatial_state = {
    position:    [x, y, z]           # float[3], nullable
    orientation: [qx, qy, qz, qw]   # float[4], nullable, unit quaternion
    scale:       float               # >= 1.0, default 1.0
    velocity:    [vx, vy, vz]        # float[3], nullable
    mass:        float               # >= 0.0, default 1.0
    zone_id:     string              # nullable
}
```

### Zone Attractor (7 fixed points)

```
zone_attractor = {
    id:       string                 # e.g. "radiant_core"
    position: [x, y, z]             # fixed world coordinates
    mass:     float                  # base gravitational mass of the zone
}
```

7 zone attractors from PATTERNS_Spatial_Mapping.md:

| Zone | Position (x, y, z) | Base Mass |
|------|-------------------|-----------|
| radiant_core | (0, 0, 0) | 10 |
| innovation_fields | (90, -10, 30) | 6 |
| towers_of_knowledge | (-60, 40, 60) | 6 |
| data_gardens | (0, -20, -90) | 5 |
| creative_nexus | (70, 80, -50) | 7 |
| arsenal | (100, -30, 60) | 6 |
| resonance_plaza | (-70, -10, -50) | 7 |

---

## ALGORITHM: Position Computation

### Step 1: Compute Zone Affinities

For each node `n` and each of the 7 zones `d`, compute `affinity(n, d)`:

```
affinity(n, d) =
    type_score(n.node_type, d.attracts.node_type)
  + subtype_score(n.subtype, d.attracts.subtype)
  + sum(d.attracts.dimensions[dim] * n[dim] for dim in d.dimensions)
  + keyword_match(n.synthesis, d.keywords) * keyword_weight
  + special_bonuses(n, d)
```

Where:
- `type_score` returns the attraction weight for the node's type (e.g., actor=0.4 for radiant_core)
- `subtype_score` returns the attraction weight for the node's subtype (e.g., vision=0.9 for radiant_core)
- Dimensional scores multiply the node's dimension value by the zone's attraction coefficient
- `keyword_match` counts keyword hits in the node's synthesis, normalized by total keywords
- `special_bonuses` include multi_author, platform_source, age_bias, status

Result is clamped to min 0.001 to avoid division by zero.

**Full attraction profiles are defined in:** `lumina-prime/docs/city-architecture/spatial-mapping/ALGORITHM_Spatial_Mapping.md`

### Step 2: Barycentrique Position

The node's position is the weighted average of all 7 zone attractor positions:

```
total_aff = sum(affinity(n, d) for d in zones)

x = sum(affinity(n, d) * zone_pos(d).x for d in zones) / total_aff
y = sum(affinity(n, d) * zone_pos(d).y for d in zones) / total_aff
z = sum(affinity(n, d) * zone_pos(d).z for d in zones) / total_aff
```

This places the node between zones in proportion to its affinities. A node with 80% Arsenal affinity and 20% Innovation Fields affinity sits 80% of the way toward the Arsenal.

### Step 3: Hash-Based Dispersion

Nodes in the same cluster must not stack at the same point. A deterministic hash provides stable dispersion:

```
h_x = int(md5(node.id)[:8], 16) / 0xFFFFFFFF           # [0, 1]
h_y = int(md5(node.id + "_y")[:8], 16) / 0xFFFFFFFF
h_z = int(md5(node.id + "_z")[:8], 16) / 0xFFFFFFFF

radius = base_radius * dispersion_factor    # 30.0 * 0.7 = 21.0
x += (h_x - 0.5) * radius * 2
y += (h_y - 0.5) * radius * 0.5            # less vertical dispersion
z += (h_z - 0.5) * radius * 2
```

The hash is deterministic: same node ID always produces the same offset. No random jitter between runs.

### Step 4: Type-Based Y Offset

Within a cluster, node type adds a vertical offset to encode the type hierarchy:

```
y_offset = {
    actor:     +10    # Citizens above (visible, prominent)
    narrative:  +5    # Stories slightly elevated
    moment:      0    # Events at cluster center
    space:      -3    # Spaces slightly below (foundation)
    thing:      -5    # Things below (support layer)
}

y += y_offset[n.node_type]
```

### Step 5: Zone Assignment

The node's zone_id is the zone with the highest affinity:

```
zone_id = argmax(affinity(n, d) for d in zones)
```

Tiebreaker: Radiant Core wins ties (closest to center).

---

## ALGORITHM: Scale Computation

```
scale = 1.0 + log1p(weight)
```

Where `log1p(x) = ln(1 + x)`, the natural logarithm of (1 + weight).

| Weight | Scale | Meaning |
|--------|-------|---------|
| 0.0 | 1.0 | Minimum visible |
| 1.0 | 1.69 | Normal node |
| 5.0 | 2.79 | Important node |
| 10.0 | 3.40 | Very important |
| 100.0 | 5.62 | Dominant node |

Logarithmic growth ensures visual distinguishability across the full weight range without any node dominating the viewport.

---

## ALGORITHM: Mass Computation

```
mass = weight * (1 + 0.1 * link_count)
```

| Weight | Links | Mass | Meaning |
|--------|-------|------|---------|
| 1.0 | 0 | 1.0 | Isolated, no pull |
| 1.0 | 10 | 2.0 | Well-connected, moderate pull |
| 5.0 | 20 | 15.0 | Important hub, strong pull |
| 10.0 | 50 | 60.0 | Major attractor |
| 20.0 | 100 | 220.0 | Gravitational center |

Mass determines how strongly this node attracts neighbors in subsequent mapper runs. High-mass nodes create spatial neighborhoods — nearby low-mass nodes drift toward them.

---

## ALGORITHM: Orientation

Orientation is a unit quaternion [qx, qy, qz, qw]:

- **Default:** [0, 0, 0, 1] = facing +Z axis
- **Updated by:** 3D engine when the actor moves or rotates
- **Written to graph:** by the engine, not the spatial mapper

### Quaternion Convention

```
q = [qx, qy, qz, qw]    # Hamilton convention
facing = rotate([0, 0, 1], q)    # Forward vector
up     = rotate([0, 1, 0], q)    # Up vector
right  = rotate([1, 0, 0], q)    # Right vector
```

### Vision Cone Computation

```
facing = forward_vector(orientation)
fov_half_angle = 60 degrees    # configurable
for each nearby_node:
    direction = normalize(nearby_node.position - actor.position)
    angle = acos(dot(facing, direction))
    if angle < fov_half_angle:
        node is visible in FOV
```

### Normalization

Floating point drift can denormalize quaternions. After any update:

```
magnitude = sqrt(qx^2 + qy^2 + qz^2 + qw^2)
if abs(magnitude - 1.0) > 0.001:
    q = q / magnitude    # renormalize
```

---

## ALGORITHM: Velocity

Velocity is the movement vector in world units per tick:

```
velocity = (position(t) - position(t-1)) / delta_t
```

- **Updated by:** 3D engine from frame-to-frame position delta
- **Null when:** actor is stationary (no movement between frames)
- **Used by:** proprioception accelerometer sense, renderer motion trails

### Acceleration (derived, not stored)

```
acceleration = (velocity(t) - velocity(t-1)) / delta_t
```

Acceleration is computed on-demand by the proprioception system, not stored on the node.

---

## ALGORITHM: Damping (Display Interpolation)

Damping prevents visual jumps when target position changes:

```
position_display(t) = position_display(t-1) * damping + position_target * (1 - damping)
damping = 0.95
```

At 30fps: 5% closer per frame. Full migration in ~60 frames = ~2 seconds.

Damping is applied by the **renderer**, not by the spatial mapper. The mapper writes the target position; the renderer interpolates toward it.

---

## KEY DECISIONS

### D1: Barycentrique vs Hard Zone Assignment

```
CHOSEN: Barycentrique (weighted average of ALL zone positions)
REASON: A node "between" two zones is visually between them.
        Creates natural transition zones instead of hard borders.
REJECTED: Hard assignment (node belongs to exactly one zone)
        Too rigid. Interesting nodes are often multi-zonal.
```

### D2: Logarithmic Scale vs Linear Scale

```
CHOSEN: scale = 1.0 + log1p(weight) — logarithmic
REASON: Equal visual distinction across weight ranges.
        Weight 1→10 is as visually distinct as 10→100.
REJECTED: scale = 1.0 + 0.1 * weight — linear
        High-weight nodes would dominate viewport.
        Low-weight nodes would be invisible.
```

### D3: Mass Includes Link Count

```
CHOSEN: mass = weight * (1 + 0.1 * link_count)
REASON: A hub (many links) should attract neighbors more than an
        isolated heavy node. Connectivity amplifies gravitational
        influence. This creates organic clustering.
REJECTED: mass = weight (pure weight)
        Ignores topology. Two nodes with equal weight but
        different connectivity would have equal pull.
```

### D4: Quaternion vs Euler Angles

```
CHOSEN: Quaternion [qx, qy, qz, qw]
REASON: No gimbal lock. Smooth SLERP interpolation.
        Standard in game engines and 3D frameworks.
REJECTED: Euler angles [pitch, yaw, roll]
        Gimbal lock at 90 degree pitch. Interpolation artifacts.
```

---

## DATA FLOW

```
Graph (FalkorDB)
    ↓ read node_type, subtype, weight, energy, stability, recency,
    ↓ drive affinities, synthesis, link_count
    ↓
Affinity Computation (per node × 7 zones)
    ↓ affinity scores
    ↓
Barycentrique Position
    ↓ [x, y, z] raw
    ↓
Hash Dispersion + Type Y Offset
    ↓ [x, y, z] final target
    ↓
Scale + Mass Computation
    ↓ scale, mass
    ↓
Zone Assignment
    ↓ zone_id
    ↓
Write to Graph: position, scale, mass, zone_id
    ↓
Renderer reads position, applies damping (0.95)
    ↓
Display position (interpolated)

Engine Movement/Rotation
    ↓
Write to Graph: orientation, velocity
    ↓
Vision System reads orientation → FOV cone
Proprioception reads velocity → accelerometer sense
```

---

## COMPLEXITY

**Time:** O(N * Z) per mapper run — N nodes, Z = 7 zones. For each node, compute 7 affinity scores plus barycentrique. With N = 1000 and Z = 7, this is 7000 affinity computations.

**Space:** O(N) — one spatial state vector per node.

**Bottlenecks:**
- Keyword matching in affinity computation (substring search in synthesis). Can be optimized with pre-computed keyword sets.
- Graph read/write for all nodes. Batch queries help.
- Hash computation (MD5 per node per axis). Cheap individually but scales linearly.

---

## HELPER FUNCTIONS

### `compute_affinity(node, zone_name) -> float`

**Purpose:** Compute how strongly a zone attracts a given node.

**Logic:** Sum of type_score + subtype_score + dimensional_scores + keyword_matches + special_bonuses. Clamped to min 0.001.

### `compute_position(node) -> (x, y, z, zone_id)`

**Purpose:** Full position pipeline: affinities, barycentrique, dispersion, y-offset, zone assignment.

**Logic:** Calls compute_affinity for all 7 zones, then weighted average, then hash dispersion, then type offset.

### `node_radius(weight) -> float`

**Purpose:** Map weight to visual radius (related to but distinct from scale).

**Logic:** `2.0 + 6.0 * log1p(weight * 5.0)` — defined in physics_visual_mapping.py.

---

## INTERACTIONS

| Module | What We Read | What We Produce |
|--------|--------------|-----------------|
| FalkorDB (graph) | All node fields (cognitive + structural) | position, scale, mass, zone_id per node |
| 3D Engine (Three.js) | — | Reads position, orientation, velocity, scale for rendering |
| Vision System | orientation | FOV cone, visible nodes list |
| Proprioception | velocity | Movement speed, direction, acceleration |
| physics_visual_mapping.py | weight | Visual radius (related to scale) |
| ALGORITHM_Spatial_Mapping.md (lumina-prime) | Zone attractor profiles | Used by affinity computation |

---

## MARKERS

<!-- @mind:todo Implement mass-based gravitational attraction in the spatial mapper (currently mass is computed but not used for inter-node pull) -->
<!-- @mind:todo Benchmark affinity computation for 1000+ nodes — is keyword matching the bottleneck? -->
<!-- @mind:todo Define cluster_radius dynamic scaling: radius = base_radius * (1 + 0.1 * log(node_count_in_zone)) -->
<!-- @mind:proposition Pre-compute affinity scores on graph tick (60s), decouple from render frame rate -->
<!-- @mind:proposition Add LOD (Level of Detail): distant nodes use simplified spatial state -->
