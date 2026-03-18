# Style System -- Validation: What Must Be True

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Style_System.md
PATTERNS:        ./PATTERNS_Style_System.md
BEHAVIORS:       ./BEHAVIORS_Style_System.md
ALGORITHM:       ./ALGORITHM_Style_System.md
THIS:            VALIDATION_Style_System.md (you are here)
IMPLEMENTATION:  ./IMPLEMENTATION_Style_System.md
HEALTH:          ./HEALTH_Style_System.md
SYNC:            ./SYNC_Style_System.md
```

---

## PURPOSE

**Validation = what we care about being true.**

These invariants protect the style system's core value: that every node is visually rendered, that artists are credited, that effects communicate physics truth, and that the graph is the single source of truth for visual identity.

---

## INVARIANTS

### V1: Every Node Renders

**Why we care:** An invisible citizen is a broken citizen. If style resolution fails for any reason -- dangling reference, missing node, malformed content -- the system must fall back to protocol default geometry. No citizen, space, or thing may be invisible.

```
MUST:   Every node with a position in 3D space renders with a visible mesh and material
NEVER:  A node fails to render due to style_id resolution failure, missing style node, or malformed style content
```

### V2: Artist Attribution Is Structural

**Why we care:** If a style exists without a `->created_by->` link, the artist has no structural credit. The link is what makes attribution unforgeable, queryable, and physics-participating. A style without this link is an orphan that cannot feed reputation or future $MIND flow to its creator.

```
MUST:   Every Thing(type=style) node has exactly one ->created_by-> link to an Actor node
NEVER:  A Thing(type=style) node exists in the graph without a ->created_by-> link
```

### V3: Effects Are Physics-Only

**Why we care:** If effects (glow, particles, trails, pulse) can be influenced by style or style_variant, citizens can cosmetically fake energy state. The visual language of the city becomes meaningless -- glow no longer means "high energy," it means "the citizen chose to glow." Trust in the visual language collapses.

```
MUST:   Effects are computed exclusively from energy, drives, and circadian phase
NEVER:  style_variant or style content influences glow intensity, particle emission, trail color, or pulse rate
```

### V4: Style Resolution Is Complete

**Why we care:** Every material property must have a resolved value at render time. Null or undefined material properties cause rendering artifacts (black faces, transparent patches, missing textures). The cascade (style -> zone -> protocol default) guarantees completeness.

```
MUST:   After resolution, every material property (base_color, metalness, roughness, transmission, emissive) has a non-null value
NEVER:  A resolved style reaches the renderer with undefined material properties
```

### V5: Style ID References Valid Nodes

**Why we care:** A style_id that points to a non-existent node or a node that is not Thing(type=style) is a data integrity failure. While the system gracefully degrades to protocol default (V1), dangling references should be detectable and trackable.

```
MUST:   When style_id is non-null, it references an existing Thing node with subtype "style"
NEVER:  style_id references a node of wrong type (actor, space, moment, narrative) or a deleted node without generating a warning
```

### V6: Skeleton Universality

**Why we care:** If styles modify the skeleton (joint count, joint hierarchy, DOF constraints), then animations break, IK breaks, and the physics bridge needs per-style logic. The skeleton is the universal contract that makes all styles interchangeable.

```
MUST:   Style resolution never modifies skeleton joints, hierarchy, or DOF constraints
NEVER:  A style adds, removes, or reorders joints in the 32-joint skeleton
```

### V7: Single Ornament Active

**Why we care:** Multiple simultaneous ornaments create visual noise and ambiguity. The ornament system maps social class to a single visual accent. Stacking ornaments would break the readability of the class grammar.

```
MUST:   Exactly zero or one ornament type is active on a node at any time
NEVER:  Multiple ornament types render simultaneously on the same node
```

### V8: Style Adoption Is Reversible

**Why we care:** If changing style_id is irreversible, citizens are locked into choices. The system must support free experimentation -- adopting a new style simply overwrites the previous style_id, and the old style remains available as a graph node for re-adoption.

```
MUST:   Changing style_id from one valid value to another (or to null) succeeds without side effects
NEVER:  Adopting a style permanently modifies the citizen's node beyond the style_id and style_variant fields
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
| V1 | No citizen is invisible | CRITICAL |
| V2 | Artists are credited | CRITICAL |
| V3 | Effects communicate physics truth | CRITICAL |
| V4 | Complete material resolution | HIGH |
| V5 | Style references are valid | HIGH |
| V6 | Skeleton universality | CRITICAL |
| V7 | Ornament readability | MEDIUM |
| V8 | Style adoption freedom | HIGH |

---

## MARKERS

<!-- @mind:todo Define test for V1: create a node with dangling style_id, verify protocol default renders -->
<!-- @mind:todo Define test for V2: attempt to create Thing(type=style) without ->created_by->, verify rejection -->
<!-- @mind:todo Define test for V3: set style_variant with glow fields, verify effects unchanged -->
<!-- @mind:todo Define test for V4: create style with partial material, verify zone defaults fill gaps -->
<!-- @mind:proposition Add V9 for style content schema validation -- malformed YAML should be detected early, not at render time -->
<!-- @mind:escalation Should V2 be enforced at graph_write time (reject the mutation) or detected after the fact (health check)? Enforcement is stronger but requires graph_write middleware. -->
