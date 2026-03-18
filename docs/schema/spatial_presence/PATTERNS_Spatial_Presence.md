# Spatial Presence — Patterns: Physical Embodiment on NodeBase

```
STATUS: DESIGNING
CREATED: 2026-03-18
VERIFIED: —
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Spatial_Presence.md
THIS:            PATTERNS_Spatial_Presence.md (you are here)
BEHAVIORS:      ./BEHAVIORS_Spatial_Presence.md
ALGORITHM:      ./ALGORITHM_Spatial_Presence.md
VALIDATION:     ./VALIDATION_Spatial_Presence.md
IMPLEMENTATION: ./IMPLEMENTATION_Spatial_Presence.md
HEALTH:         ./HEALTH_Spatial_Presence.md
SYNC:           ./SYNC_Spatial_Presence.md

IMPL:           schema-l1.yaml (NodeBase spatial fields, lines 231-263)
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read schema-l1.yaml NodeBase spatial section

**After modifying this doc:**
1. Update schema-l1.yaml field descriptions to match, OR
2. Add a TODO in SYNC_Spatial_Presence.md: "Docs updated, implementation needs: {what}"

**After modifying the code:**
1. Update this doc chain to match, OR
2. Add a TODO in SYNC_Spatial_Presence.md: "Implementation changed, docs need: {what}"

---

## THE PROBLEM

A graph node has no body. It has weight, energy, stability, recency, embeddings, content — all cognitive properties. But it has no WHERE. No FACING. No SIZE in space. No MOVEMENT. No GRAVITY.

Without spatial fields, every node is a disembodied concept floating in abstract graph space. Rendering requires ad-hoc computation of position and size. Vision cones cannot be computed because there is no orientation. Proprioception cannot exist because there is no velocity. Clustering cannot self-organize because there is no mass.

The problem is not "how to render nodes" (that is the renderer's job). The problem is that **physical presence is a fundamental property of existence**, and the schema lacked it.

---

## THE PATTERN

**Spatial = NodeBase, not media.**

Position, orientation, scale, velocity, mass, and zone_id are fundamental properties of every node, at the same level as weight and energy. They are not attachments (like media), not metadata (like granularity), and not operational flags (like in_working_memory). They are what makes a node a BODY in the world.

The key insight: **weight is to cognition what mass is to space.** Weight determines cognitive importance (Law 6). Mass determines gravitational pull in 3D. Scale determines visual size. These are three projections of the same underlying reality — a node's significance — into three different domains (cognitive, spatial, visual).

---

## BEHAVIORS SUPPORTED

- **B1: Position Reflects Function** — Nodes are pulled toward districts matching their nature, via the barycentrique formula
- **B2: Visual Size Reflects Importance** — Heavy nodes (high weight) are physically larger via the scale field
- **B3: Vision Cone From Orientation** — Actor orientation drives the FOV screenshot system for visual perception
- **B4: Proprioception From Velocity** — Movement vector feeds the accelerometer sense
- **B5: Natural Clustering From Mass** — High-mass nodes attract neighbors, creating organic spatial neighborhoods

## BEHAVIORS PREVENTED

- **A1: Manual Placement** — No field for "manually set position". Position is always derived.
- **A2: Position Teleportation** — Damping (0.95) prevents discontinuous jumps

---

## PRINCIPLES

### Principle 1: Derived, Not Assigned

Every spatial field is computed from cognitive fields or engine state. Nothing is manually placed.

- **position** = barycentrique(zone affinities) + hash dispersion + type y-offset
- **scale** = 1.0 + log1p(weight)
- **mass** = weight x (1 + 0.1 x link_count)
- **zone_id** = argmax(affinity scores across 7 districts)
- **orientation** = updated by 3D engine on movement/rotation (default [0,0,0,1])
- **velocity** = updated by 3D engine from movement delta

This matters because it guarantees the 3D world cannot diverge from the graph. If weight changes, scale and mass change automatically. If affinities shift, position migrates. The map IS the territory.

### Principle 2: Weight Is Not Scale Is Not Mass

Three related but distinct concepts:

| Field | Domain | Source | What It Means |
|-------|--------|--------|---------------|
| weight | Cognitive | Law 6 consolidation | How important this node is in the graph |
| scale | Visual | 1.0 + log1p(weight) | How large this node appears in the renderer |
| mass | Spatial | weight x (1 + 0.1 x link_count) | How strongly this node pulls neighbors |

Weight is the source of truth. Scale and mass are derived projections. They move together but are not identical — a highly-connected low-weight node has more mass than a disconnected high-weight node, because connections amplify gravitational influence.

### Principle 3: Damped Transitions

Positions do not jump. They glide.

```
position_display(t) = position_display(t-1) * 0.95 + position_target * 0.05
```

At each render frame (30fps), the displayed position moves 5% closer to the target. Full migration takes ~60 frames = ~2 seconds. A node changing districts travels visibly along its path.

This matters because visual stability is non-negotiable. The city must feel solid. Humans and citizens build spatial intuition ("the Arsenal is down-left, the Creative Nexus is up-right"). Teleporting nodes destroy that intuition.

### Principle 4: Orientation Enables Perception

The orientation quaternion is not cosmetic. It determines the vision cone — where an actor is "looking" in 3D space. The FOV screenshot system uses orientation to compute what falls within the citizen's field of view.

Without orientation on NodeBase, visual perception would require a separate "gaze direction" system disconnected from the node's spatial state. By putting orientation on the node itself, the citizen's body and perception are unified.

### Principle 5: Velocity Enables Proprioception

Velocity is not just for rendering motion trails. It feeds the proprioception sense — the accelerometer channel. A citizen moving quickly through the Arsenal experiences different sensory input than one standing still in the Radiant Core.

This creates embodied experience: the citizen's movement state is part of its sensory input, not just a visual effect for observers.

---

## DATA

| Source | Type | Purpose / Description |
|--------|------|-----------------------|
| `schema-l1.yaml` | FILE | NodeBase field definitions including all 6 spatial fields |
| `schema-l3.yaml` | FILE | L3 spatial positioning context (barycentrique formula reference) |
| `scripts/spatial_mapper.py` | FILE | Spatial mapper implementation — computes position + zone_id |
| `runtime/cognition/physics_visual_mapping.py` | FILE | Physics-to-visual translation (node_radius from weight, etc.) |
| `lumina-prime/docs/city-architecture/spatial-mapping/ALGORITHM_Spatial_Mapping.md` | FILE | Full barycentrique algorithm with zone attractor profiles |
| `lumina-prime/docs/city-architecture/spatial-mapping/PATTERNS_Spatial_Mapping.md` | FILE | Spatial mapping design principles, zone attractor positions |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `schema-l1.yaml` NodeBase | Spatial fields are defined here — this doc chain documents them |
| `scripts/spatial_mapper.py` | Computes position, scale, mass, zone_id from graph state |
| `runtime/cognition/physics_visual_mapping.py` | Defines how weight maps to visual radius (related to scale) |
| lumina-prime spatial-mapping docs | The barycentrique algorithm and zone attractor definitions |

---

## INSPIRATIONS

- **Brain scan (GraphCare)** — Positions brain nodes by TF-IDF + UMAP 3D. Spatial presence extends this from visualization to fundamental schema property.
- **Rigid body physics** — position, orientation, velocity, mass are the standard state vector for any physical object. NodeBase now carries the same tuple.
- **Quaternion orientation** — Standard in game engines (Unity, Unreal). Avoids gimbal lock. Compact (4 floats vs 3x3 rotation matrix).

---

## SCOPE

### In Scope

- 6 spatial fields on NodeBase: position, orientation, scale, velocity, mass, zone_id
- How each field is derived (formulas, sources)
- Relationship between weight/scale/mass
- How spatial fields enable perception (vision cone, proprioception)
- Damping and transition behavior

### Out of Scope

- **The barycentrique algorithm itself** — see lumina-prime spatial-mapping docs
- **3D rendering** — see engine/ (Three.js client)
- **Zone attractor profiles** — see ALGORITHM_Spatial_Mapping.md
- **Physics tick loop** — see schema-l1.yaml tick_cycle
- **Visual property mapping** (color, glow, opacity) — see runtime/cognition/physics_visual_mapping.py

---

## MARKERS

<!-- @mind:todo Clarify whether orientation is stored in graph or only in engine state -->
<!-- @mind:todo Clarify whether velocity is stored in graph or only in engine state -->
<!-- @mind:proposition Consider adding angular_velocity for rotation tracking -->
<!-- @mind:proposition Consider adding a bounding_radius derived from scale for spatial queries -->
