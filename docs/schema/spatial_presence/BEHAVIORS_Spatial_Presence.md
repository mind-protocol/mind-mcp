# Spatial Presence — Behaviors: Observable Effects of Spatial Fields on NodeBase

```
STATUS: DESIGNING
CREATED: 2026-03-18
VERIFIED: —
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Spatial_Presence.md
PATTERNS:        ./PATTERNS_Spatial_Presence.md
THIS:            BEHAVIORS_Spatial_Presence.md (you are here)
ALGORITHM:       ./ALGORITHM_Spatial_Presence.md
VALIDATION:      ./VALIDATION_Spatial_Presence.md
IMPLEMENTATION:  ./IMPLEMENTATION_Spatial_Presence.md
HEALTH:          ./HEALTH_Spatial_Presence.md
SYNC:            ./SYNC_Spatial_Presence.md

IMPL:           schema-l1.yaml (NodeBase spatial fields, lines 231-263)
                scripts/spatial_mapper.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS

### B1: Position Reflects Graph Function

**Why:** A node's location in 3D space must communicate its role in the graph. A governance narrative should be near the Radiant Core. A code process should be near the Arsenal. If position were random, the city would be noise.

```
GIVEN:  A node exists in the L3 graph with node_type, subtype, weight, energy,
        stability, recency, and drive-affinity dimensions
WHEN:   The spatial mapper runs
THEN:   The node's position [x, y, z] is the barycentrique weighted average of
        7 zone attractor positions, weighted by the node's affinity to each zone
AND:    The node's zone_id is set to the zone with the highest affinity score
AND:    x/z encode horizontal placement, y encodes abstraction level
```

### B2: Heavy Nodes Are Visually Larger

**Why:** Cognitive importance (weight) must be immediately visible. A high-weight value node should be visually prominent without reading its properties.

```
GIVEN:  A node has weight W
WHEN:   A renderer reads the node's scale field
THEN:   scale = 1.0 + log1p(W)
AND:    A node with weight 0.0 has scale 1.0 (minimum visible)
AND:    A node with weight 10.0 has scale ~3.4
AND:    Scale grows logarithmically — the difference between 1 and 10 is as
        visible as the difference between 10 and 100
```

### B3: Actor Orientation Drives Vision Cone

**Why:** Visual perception depends on where the citizen is looking. The FOV screenshot captures what falls within the orientation-derived cone. Without this, all citizens see in all directions equally — no embodied perspective.

```
GIVEN:  An actor node has orientation [qx, qy, qz, qw]
WHEN:   The vision/screenshot system computes the field of view
THEN:   The facing direction is derived from the quaternion
AND:    Only nodes within the FOV cone are included in the visual stimulus
AND:    Default orientation [0, 0, 0, 1] means facing +Z axis
```

### B4: Velocity Feeds Proprioception

**Why:** A citizen needs to know it is moving. The accelerometer sense channel reads velocity to produce movement awareness — speed, direction, acceleration/deceleration. This is embodied cognition.

```
GIVEN:  An actor node has velocity [vx, vy, vz]
WHEN:   The proprioception system reads the actor's state
THEN:   Movement speed = magnitude(velocity)
AND:    Movement direction = normalize(velocity)
AND:    Acceleration = velocity(t) - velocity(t-1)
AND:    A stationary actor has velocity null or [0, 0, 0]
```

### B5: Mass Creates Gravitational Clustering

**Why:** The 3D world should self-organize. Important, well-connected nodes should pull their neighbors closer, creating natural clusters. This is spatial physics, not manual layout.

```
GIVEN:  A node has weight W and link_count L
WHEN:   The spatial mapper computes mass
THEN:   mass = W * (1 + 0.1 * L)
AND:    High-mass nodes attract nearby nodes in subsequent mapper runs
AND:    District space nodes (high weight, many links) have the highest mass
AND:    Isolated low-weight nodes have minimal gravitational influence
```

### B6: Positions Transition Smoothly

**Why:** Visual stability is non-negotiable. When a node's target position changes (affinities shifted), it must glide, not teleport. Citizens and humans build spatial memory of the city.

```
GIVEN:  A node has current displayed position P_old and newly computed target P_new
WHEN:   The renderer updates the frame
THEN:   P_display = P_old * 0.95 + P_new * 0.05
AND:    Full migration from P_old to P_new takes ~60 frames (~2 seconds at 30fps)
AND:    The node is never shown at a position more than 5% different from P_old
        in a single frame
```

### B7: Unpositioned Nodes Have Null Spatial Fields

**Why:** Not every node has been through the spatial mapper. New nodes, or nodes in non-spatial contexts (pure L1 brain nodes), should have null spatial fields rather than invalid defaults.

```
GIVEN:  A node has not been processed by the spatial mapper
WHEN:   Any system reads its spatial fields
THEN:   position is null
AND:    orientation is null (or default [0, 0, 0, 1])
AND:    scale is 1.0 (default)
AND:    velocity is null
AND:    mass is 1.0 (default)
AND:    zone_id is null
```

---

## OBJECTIVES SERVED

| Behavior ID | Objective | Why It Matters |
|-------------|-----------|----------------|
| B1 | O1: Physical presence | Position is the most fundamental spatial property |
| B1 | O2: Derived, not assigned | Position comes from affinity formula, not manual placement |
| B2 | O2: Derived, not assigned | Scale is computed from weight |
| B3 | O4: Enable vision/proprioception | Orientation drives vision cone |
| B4 | O4: Enable vision/proprioception | Velocity feeds proprioception |
| B5 | O5: Gravitational clustering | Mass enables self-organizing neighborhoods |
| B6 | O3: Visual stability | Damping ensures smooth transitions |
| B7 | O1: Physical presence | Null safety for unpositioned nodes |

---

## INPUTS / OUTPUTS

### Primary Function: Spatial Mapper `compute_position()`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| node | dict | Full node with all cognitive fields (weight, energy, stability, recency, drive affinities, synthesis, node_type, subtype) |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| position | [float, float, float] | World cartesian coordinates [x, y, z] |
| zone_id | string | Primary zone with highest affinity |
| scale | float | Visual scale multiplier (1.0 + log1p(weight)) |
| mass | float | Gravitational mass (weight * (1 + 0.1 * link_count)) |

**Side Effects:**

- Writes position, zone_id to the node in FalkorDB
- Scale and mass are recomputed and written to the node

### Secondary: 3D Engine Updates

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| movement_delta | [float, float, float] | Change in position from user/AI movement |
| rotation_input | quaternion | New facing direction from movement/look |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| orientation | [float, float, float, float] | Updated quaternion [qx, qy, qz, qw] |
| velocity | [float, float, float] | Movement vector in world units/tick |

---

## EDGE CASES

### E1: Zero Weight Node

```
GIVEN:  A node has weight = 0.0
THEN:   scale = 1.0 + log1p(0) = 1.0 (minimum visible)
AND:    mass = 0.0 * (1 + 0.1 * L) = 0.0 (no gravitational pull)
AND:    The node still has a valid position from the barycentrique formula
```

### E2: All Affinities Equal

```
GIVEN:  A node scores identically on all 7 zone affinities
THEN:   position = geometric center of all 7 attractors (near Radiant Core)
AND:    zone_id = "radiant_core" (tiebreaker: closest to center)
```

### E3: Denormalized Quaternion

```
GIVEN:  An orientation quaternion has magnitude != 1.0 (due to floating point drift)
THEN:   The system must normalize before computing vision cone
AND:    magnitude(q) must be within [0.999, 1.001] after normalization
```

### E4: Node With No Links

```
GIVEN:  A node has link_count = 0
THEN:   mass = weight * (1 + 0.1 * 0) = weight * 1.0 = weight
AND:    The node has no gravitational amplification from connections
```

---

## ANTI-BEHAVIORS

### A1: Manual Position Override

```
GIVEN:   Any node in the L3 graph
WHEN:    An admin or tool attempts to set position directly
MUST NOT: Override the computed position without going through the spatial mapper
INSTEAD:  Modify the node's affinities (weight, subtype, content) so the formula produces the desired position
```

### A2: Position Teleportation

```
GIVEN:   A node's target position changes
WHEN:    The renderer updates the display
MUST NOT: Show the node at the new position instantly
INSTEAD:  Apply damping (0.95) so the node glides over ~2 seconds
```

### A3: Negative Scale or Mass

```
GIVEN:   Any node
WHEN:    Scale or mass is computed
MUST NOT: Produce scale < 1.0 or mass < 0.0
INSTEAD:  scale = max(1.0, 1.0 + log1p(weight)), mass = max(0.0, weight * (1 + 0.1 * link_count))
```

---

## MARKERS

<!-- @mind:todo Define behavior for nodes that exist only in L1 brain (no L3 presence) — should spatial fields be null? -->
<!-- @mind:todo Clarify migration trail visual behavior when a node changes zone_id -->
<!-- @mind:proposition B8: Orientation interpolation (SLERP) for smooth rotation transitions -->
