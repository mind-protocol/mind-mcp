# OBJECTIVES — Spatial Presence

```
STATUS: DESIGNING
CREATED: 2026-03-18
VERIFIED: —
```

---

## CHAIN

```
THIS:            OBJECTIVES_Spatial_Presence.md (you are here - START HERE)
PATTERNS:       ./PATTERNS_Spatial_Presence.md
BEHAVIORS:      ./BEHAVIORS_Spatial_Presence.md
ALGORITHM:      ./ALGORITHM_Spatial_Presence.md
VALIDATION:     ./VALIDATION_Spatial_Presence.md
IMPLEMENTATION: ./IMPLEMENTATION_Spatial_Presence.md
HEALTH:         ./HEALTH_Spatial_Presence.md
SYNC:           ./SYNC_Spatial_Presence.md

IMPL:           schema-l1.yaml (NodeBase, lines 231-263)
```

**Read this chain in order before making changes.** Each doc answers different questions. Skipping ahead means missing context.

---

## PRIMARY OBJECTIVES (ranked)

1. **Every node has a complete physical presence in 3D space** — Without position, orientation, scale, velocity, mass, and zone_id on NodeBase, nodes are abstract graph entries with no body. Spatial presence makes them inhabitants of a world, not rows in a database.

2. **Spatial fields are derived from cognitive fields, not manually assigned** — Position comes from the barycentrique affinity formula. Scale comes from weight. Mass comes from weight and link_count. This ensures the 3D world reflects the graph's actual structure rather than arbitrary placement.

3. **Visual stability through damped transitions** — Positions must never jump. A damping factor of 0.95 guarantees smooth migration over ~2 seconds (60 frames). The city must feel solid even as the graph evolves underneath.

4. **Enable vision and proprioception as first-class senses** — Orientation drives the FOV cone for screenshot-based visual perception. Velocity feeds the accelerometer sense for proprioception. Without these fields on the node, embodied perception is impossible.

5. **Gravitational clustering through mass** — High-mass nodes pull neighbors, creating natural spatial neighborhoods. This makes the 3D world self-organizing rather than needing explicit layout rules.

## NON-OBJECTIVES

- **Per-tick position recomputation** — Positions change slowly. The spatial mapper runs periodically, not every physics tick. Real-time physics simulation of node movement is not the goal.
- **Manual node placement** — No admin tool for dragging nodes around. Position is always computed. If you want a node somewhere, change its affinities.
- **Collision detection** — Nodes can overlap. There is no physics engine preventing intersection. Dispersion within clusters provides visual separation, not physical exclusion.
- **Client-side physics simulation** — The 3D engine (Three.js) reads positions and interpolates. It does not run its own force-directed layout.

## TRADEOFFS (canonical decisions)

- When **visual stability** conflicts with **accuracy**, choose visual stability. A node showing 2-second-old position is better than a node that teleports.
- When **derivation** conflicts with **performance**, choose derivation. We accept recomputation cost to preserve the principle that no spatial field is manually set.
- We accept **coarser Y resolution** (type-based offset within clusters) to preserve the **abstraction-level metaphor** on the vertical axis.

## SUCCESS SIGNALS (observable)

- Every node in the L3 graph has non-null position and zone_id after the spatial mapper runs
- Orientation quaternions are normalized (magnitude within [0.999, 1.001])
- Scale values are positive and grow logarithmically with weight
- Mass values are positive and correlate with weight x link_count
- No node position jumps more than 5% of world radius between consecutive mapper runs (damping working)
- Vision cone computation succeeds for every actor node with non-null orientation

---

## MARKERS

<!-- @mind:todo Define world radius bounds for position validation -->
<!-- @mind:todo Determine mapper run frequency (every N ticks? every M seconds?) -->
<!-- @mind:proposition Consider adding a "grounded" boolean for nodes that should resist migration (e.g., district space nodes) -->
