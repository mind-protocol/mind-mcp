# Spatial Presence — Validation: What Must Be True

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Spatial_Presence.md
PATTERNS:        ./PATTERNS_Spatial_Presence.md
BEHAVIORS:       ./BEHAVIORS_Spatial_Presence.md
ALGORITHM:       ./ALGORITHM_Spatial_Presence.md
THIS:            VALIDATION_Spatial_Presence.md (you are here)
IMPLEMENTATION:  ./IMPLEMENTATION_Spatial_Presence.md
HEALTH:          ./HEALTH_Spatial_Presence.md
SYNC:            ./SYNC_Spatial_Presence.md
```

---

## PURPOSE

**Validation = what we care about being true.**

If any of these invariants fail, the spatial presence system is broken — nodes have invalid positions, the 3D world is physically impossible, or derived fields diverge from their sources. These are the properties that make the difference between a navigable city and a jumble of misplaced dots.

---

## INVARIANTS

### V1: Position Bounded Within World

**Why we care:** An unbounded position means a node flies off to infinity. The renderer cannot display it. Spatial queries fail because the node is outside all search volumes. The city loses a citizen.

```
MUST:   For every node with non-null position:
          |x| <= 500, |y| <= 300, |z| <= 500
        (bounds derived from the outermost zone attractor positions
         plus maximum dispersion radius)
NEVER:  position contains NaN or Infinity
NEVER:  position has fewer or more than 3 elements
```

### V2: Quaternion Normalized

**Why we care:** A denormalized quaternion produces incorrect facing direction. The vision cone points in the wrong direction. The citizen sees nodes it should not see, and misses nodes it should. Visual perception is corrupted.

```
MUST:   For every node with non-null orientation:
          magnitude([qx, qy, qz, qw]) within [0.999, 1.001]
NEVER:  orientation contains NaN
NEVER:  orientation has fewer or more than 4 elements
NEVER:  orientation = [0, 0, 0, 0] (zero quaternion — no valid rotation)
```

### V3: Scale Positive and Derived From Weight

**Why we care:** A node with scale <= 0 is invisible or inverted. A scale that does not match weight means the visual representation lies about the node's importance.

```
MUST:   scale >= 1.0 for every node
MUST:   scale = 1.0 + log1p(weight) within floating point tolerance (epsilon = 0.01)
NEVER:  scale = 0 or negative
NEVER:  scale > 10.0 (sanity bound: log1p(8102) ~ 9.0, more than sufficient)
```

### V4: Mass Non-Negative and Derived From Weight + Links

**Why we care:** Negative mass would create repulsion instead of attraction — a node pushes neighbors away, fragmenting the cluster. Mass divorced from weight+links means gravitational pull does not reflect the node's actual significance.

```
MUST:   mass >= 0.0 for every node
MUST:   mass = weight * (1 + 0.1 * link_count) within floating point tolerance
NEVER:  mass < 0
NEVER:  mass = NaN
```

### V5: Zone ID Matches Highest Affinity

**Why we care:** If zone_id does not match the zone with the highest affinity score, the node's district label is wrong. Systems that filter by zone_id (e.g., "show me all Arsenal nodes") return incorrect results. The city directory lies.

```
MUST:   zone_id = argmax(affinity(node, zone) for zone in all_zones)
MUST:   zone_id is one of the 7 valid zone identifiers
NEVER:  zone_id is a string not in the zone registry
NEVER:  zone_id is non-null while position is null (spatial inconsistency)
```

### V6: No Position Teleportation

**Why we care:** If a node jumps more than damping allows between consecutive display frames, the city stutters. Citizens lose spatial orientation. The visual experience breaks trust.

```
MUST:   |position_display(t) - position_display(t-1)| <=
        |position_target - position_display(t-1)| * (1 - damping)
        where damping = 0.95
MUST:   Maximum single-frame displacement < 5% of world radius per frame
NEVER:  A node appears at its target position in fewer than 20 frames
        (unless it was just created)
```

### V7: Velocity Null When Stationary

**Why we care:** A stationary node with a non-zero velocity vector produces false proprioception signals. The citizen thinks it is moving when it is still. The accelerometer sense hallucinates.

```
MUST:   If position has not changed between frames, velocity = null or [0, 0, 0]
MUST:   velocity components are finite (no NaN, no Infinity)
NEVER:  velocity has fewer or more than 3 elements
```

### V8: Spatial Consistency — All Or None

**Why we care:** A node with position but no zone_id, or mass but no position, is in an inconsistent spatial state. Systems reading spatial fields cannot trust partial data.

```
MUST:   If position is non-null, then zone_id is non-null
MUST:   If zone_id is non-null, then position is non-null
MUST:   Scale has a valid value (default 1.0) whether or not position is set
MUST:   Mass has a valid value (default 1.0) whether or not position is set
NEVER:  zone_id is set while position is null
```

### V9: Default Orientation Is Valid

**Why we care:** A node created without explicit orientation must have a valid default so the vision system does not crash. The default [0, 0, 0, 1] means "facing +Z" — a neutral, predictable direction.

```
MUST:   Default orientation = [0, 0, 0, 1]
MUST:   [0, 0, 0, 1] is a unit quaternion (magnitude = 1.0)
NEVER:  Default orientation = null for actor nodes that participate in vision
```

---

## PRIORITY

| Priority | Meaning | If Violated |
|----------|---------|-------------|
| **CRITICAL** | System purpose fails | Unusable |
| **HIGH** | Major value lost | Degraded severely |
| **MEDIUM** | Partial value lost | Works but worse |

---

## INVARIANT INDEX

| ID | Value Protected | Priority |
|----|-----------------|----------|
| V1 | Position stays within renderable world bounds | CRITICAL |
| V2 | Orientation produces correct facing direction | CRITICAL |
| V3 | Scale reflects cognitive importance | HIGH |
| V4 | Mass reflects gravitational significance | HIGH |
| V5 | Zone assignment matches actual affinities | HIGH |
| V6 | Visual stability — no teleportation | CRITICAL |
| V7 | Proprioception accuracy — no phantom movement | MEDIUM |
| V8 | Spatial fields are internally consistent | HIGH |
| V9 | Default orientation is valid and predictable | MEDIUM |

---

## MARKERS

<!-- @mind:todo Define exact world bounds (V1) — derive from max attractor position + max dispersion -->
<!-- @mind:todo Write unit tests for V3 (scale formula) and V4 (mass formula) -->
<!-- @mind:todo Implement V6 verification in the renderer — log warnings when damping is violated -->
<!-- @mind:proposition Consider V10: orientation SLERP interpolation invariant — rotation transitions must be smooth -->
<!-- @mind:escalation V5 tiebreaker (Radiant Core wins ties) — is this the right default? Should it be "nearest zone" instead? -->
