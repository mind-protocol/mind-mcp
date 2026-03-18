# Style System -- Algorithm: Style Resolution, Adoption, and Creation Pipelines

```
STATUS: DESIGNING
CREATED: 2026-03-18
VERIFIED: pending
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Style_System.md
BEHAVIORS:       ./BEHAVIORS_Style_System.md
PATTERNS:        ./PATTERNS_Style_System.md
THIS:            ALGORITHM_Style_System.md (you are here)
VALIDATION:      ./VALIDATION_Style_System.md
HEALTH:          ./HEALTH_Style_System.md
IMPLEMENTATION:  ./IMPLEMENTATION_Style_System.md
SYNC:            ./SYNC_Style_System.md

IMPL:            (not yet created -- DESIGNING phase)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

The style system has three primary algorithms: **style resolution** (graph data to renderable assets), **style adoption** (citizen chooses a style), and **style creation** (artist publishes a new style). Resolution runs every render tick per visible node. Adoption and creation are infrequent graph mutations.

The core insight is that all three algorithms operate on the graph -- there is no separate asset database. Resolution reads a Thing node. Adoption updates a field on NodeBase. Creation writes a Thing node with a link. The graph is the single source of truth.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| O1: Sovereign visual identity | B1, B6, B7, B8, B9 | Resolution transforms graph state into renderable output |
| O2: Artist attribution | B2 | Creation ensures ->created_by-> link exists atomically |
| O3: Style as graph catalog | B1, B8 | Adoption uses graph_write, not file operations |
| O4: Zone defaults with overrides | B3, B4 | Resolution cascade merges zone, style, and variant |
| O5: Physics-driven effects | B5 | Resolution separates effects (physics) from style (choice) |

---

## DATA STRUCTURES

### Thing(type=style) Node Content

```yaml
# Stored in Thing.content as YAML string
proportions:
  bone_scales:                       # Per-bone or per-group scale factors
    spine: [1.0, 1.2, 1.0]          # [x, y, z] -- tall slender example
    limbs: [0.9, 1.1, 0.9]
    head: [1.0, 1.0, 1.0]
  height_class: "tall"               # Metadata for search/filtering

material:
  base_color: "#c0c8d4"             # Hex color
  metalness: 0.7                     # 0.0 - 1.0
  roughness: 0.3                     # 0.0 - 1.0
  transmission: 0.0                  # 0.0 - 1.0 (glass-like transparency)
  emissive: "#000000"                # Self-illumination color

ornaments:
  default_type: "crystal"           # From social_class_styles vocabulary
  attachment_points: ["left_shoulder", "right_shoulder"]
  scale: 0.8

animations_idle:
  clips:
    - name: "gentle_sway"
      uri: "s3://assets/anims/gentle_sway.glb"
      loop: true
      base_speed: 1.0
    - name: "weight_shift"
      uri: "s3://assets/anims/weight_shift.glb"
      loop: true
      base_speed: 0.8
  drive_modulation:
    rest: { speed_mult: 0.6, amplitude_mult: 0.7 }
    curiosity: { speed_mult: 1.3, amplitude_mult: 1.0, blend_to: "head_scan" }
    achievement: { speed_mult: 1.1, amplitude_mult: 0.9 }
```

### Thing(type=style) Media

```yaml
media:
  geometry:
    uri: "s3://assets/meshes/geometric_crystal_v1.glb"   # glTF/GLB file
    meta:
      format: "glb"
      vertex_count: 12400
      lod_levels: 3
  image:
    uri: "s3://assets/previews/geometric_crystal_preview.png"  # Preview thumbnail
```

### Resolved Style Output

```yaml
# The output of resolve_style() -- everything the renderer needs
resolved:
  mesh_uri: string          # Final glTF URI
  proportions: BoneScale[]  # Per-bone scale array (32 entries)
  material:                 # Fully resolved material properties
    base_color: string
    metalness: float
    roughness: float
    transmission: float
    emissive: string
  ornament:                 # Active ornament config
    type: string
    attachment_points: string[]
    scale: float
  idle_animation:           # Animation with drive modulation applied
    clip_uri: string
    speed: float
    amplitude: float
  effects:                  # Computed from physics, NOT from style
    glow: { active: bool, intensity: float, color: string }
    particles: { active: bool, type: string, rate: float }
    trail: { active: bool, color: string }
    pulse: { active: bool, rate_bpm: float }
```

---

## ALGORITHM: Style Resolution

The resolution algorithm runs per visible node per render tick. It transforms graph state into renderable output by cascading through four sources: style content, zone defaults, style_variant overrides, and physics state.

### Step 1: Fetch Style Node

Read the node's `style_id` field. If non-null, query the graph for the referenced Thing(type=style) node. If the node does not exist (dangling reference), fall through to protocol default.

```
style_node = null
IF node.style_id IS NOT null:
    style_node = graph.get(node.style_id)
    IF style_node IS null OR style_node.node_type != "thing" OR style_node.subtype != "style":
        LOG_WARNING("dangling style_id", node.id, node.style_id)
        style_node = null
```

### Step 2: Parse Style Content

If a valid style node was found, parse its `content` field as YAML. Extract proportions, material, ornaments, and animations_idle sections. If content is malformed, fall through to protocol default for that section.

```
style_content = PARSE_YAML(style_node.content) IF style_node ELSE {}
proportions = style_content.proportions OR PROTOCOL_DEFAULT.proportions
material = style_content.material OR {}
ornaments = style_content.ornaments OR {}
animations_idle = style_content.animations_idle OR PROTOCOL_DEFAULT.animations_idle
mesh_uri = style_node.media.geometry.uri IF style_node ELSE PROTOCOL_DEFAULT.mesh_uri
```

### Step 3: Apply Zone Material Defaults

Fetch the node's zone material defaults from world-manifest. For each material property not defined in the style, use the zone default. The cascade order is: style content > zone default > protocol default.

```
zone = get_zone_defaults(node.zone_id)
FOR EACH property IN [base_color, metalness, roughness, transmission, emissive]:
    IF material[property] IS NOT defined:
        material[property] = zone[property] OR PROTOCOL_DEFAULT.material[property]
```

### Step 4: Apply Style Variant Overrides

Read the node's `style_variant` dict. For each key in style_variant, override the corresponding resolved property. style_variant can override: tint (maps to base_color), ornament (maps to ornament type), glow_color (ignored -- effects are physics).

```
variant = node.style_variant OR {}
IF variant.tint:
    material.base_color = variant.tint
IF variant.ornament:
    ornaments.default_type = variant.ornament
IF variant.metalness IS NOT null:
    material.metalness = variant.metalness
IF variant.roughness IS NOT null:
    material.roughness = variant.roughness
# NOTE: variant.glow, variant.particles, variant.effects -- all IGNORED (physics-owned)
```

### Step 5: Resolve Ornaments from Social Class

If ornaments.default_type was not overridden by style_variant, look up the node's social class from world-manifest.json `avatar.social_class_styles` and use the mapped ornament type.

```
IF ornaments.default_type IS NOT set:
    social_class = get_social_class(node)
    ornaments.default_type = SOCIAL_CLASS_STYLES[social_class].ornament
```

### Step 6: Modulate Idle Animations by Drives

Apply drive state to idle animation parameters. Each drive has modulation multipliers defined in the style content. The dominant drive (highest intensity) determines the primary modulation.

```
dominant_drive = MAX_BY(drives, intensity)
modulation = animations_idle.drive_modulation[dominant_drive.name] OR { speed_mult: 1.0, amplitude_mult: 1.0 }
resolved_idle = {
    clip_uri: animations_idle.clips[0].uri,
    speed: animations_idle.clips[0].base_speed * modulation.speed_mult,
    amplitude: 1.0 * modulation.amplitude_mult
}
```

### Step 7: Compute Effects from Physics (Not Style)

Effects are entirely physics-derived. They do not read style content or style_variant. This step is included in the resolution algorithm for completeness but is logically separate -- it reads energy, drives, and circadian phase.

```
effects = {
    glow: { active: node.energy > 0.3, intensity: clamp(node.energy - 0.3, 0, 1), color: material.emissive },
    particles: { active: drives.curiosity > 0.6, type: "sparkle", rate: drives.curiosity * 10 },
    trail: { active: node.velocity IS NOT null AND magnitude(node.velocity) > 0.1, color: material.base_color },
    pulse: { active: true, rate_bpm: circadian_to_bpm(node.circadian_phase) }
}
```

---

## KEY DECISIONS

### D1: Cascade Order for Material Resolution

```
IF style content defines a material property:
    USE style value
    WHY: artist intent takes precedence over zone defaults
ELSE IF zone defaults define the property:
    USE zone value
    WHY: district coherence is the fallback for unstylized properties
ELSE:
    USE protocol default
    WHY: every property must have a value; no null materials at render time
```

### D2: Style Variant Override Scope

```
IF style_variant contains effect-related keys (glow, particles, trail, pulse):
    IGNORE those keys
    WHY: effects are physics-owned; allowing overrides would let citizens fake energy state
ELSE:
    APPLY the override to the corresponding resolved property
    WHY: citizen sovereignty over appearance within the non-effects layers
```

### D3: Single Ornament Constraint

```
IF both social class and style_variant specify ornament type:
    USE style_variant ornament
    WHY: explicit citizen choice overrides default class mapping
    NOTE: only one ornament renders at a time to prevent visual noise
```

---

## DATA FLOW

```
node (NodeBase with style_id, style_variant, zone_id)
    |
    v
[Step 1] Fetch Thing(type=style) from graph
    |
    v
[Step 2] Parse YAML content -> proportions, material, ornaments, animations
    |
    v
[Step 3] Zone material defaults fill gaps
    |
    v
[Step 4] style_variant overrides apply on top
    |
    v
[Step 5] Social class ornament fallback
    |
    v
[Step 6] Drive modulation on idle animations
    |
    v
[Step 7] Physics effects (independent of style)
    |
    v
ResolvedStyle (mesh_uri, proportions, material, ornament, idle_animation, effects)
    |
    v
Three.js renderer
```

---

## COMPLEXITY

**Time:** O(1) per node per tick -- graph lookup is by ID (hash map), YAML parse is cached after first resolution, drive modulation is arithmetic.

**Space:** O(N) where N = number of visible nodes -- each node's resolved style is cached until style_id, style_variant, zone, or physics state changes.

**Bottlenecks:**
- Graph lookup for style node (mitigated by caching resolved styles per style_id)
- YAML parsing of style content (mitigated by parsing once and caching)
- At 464 citizens, worst case is 464 resolutions per tick -- well within budget if cached

---

## HELPER FUNCTIONS

### `get_zone_defaults(zone_id)`

**Purpose:** Retrieve material defaults for a zone from world-manifest.json.

**Logic:** Lookup zone_id in world-manifest zones array. Return the zone's atmosphere/material section. Return empty dict if zone_id is null or zone not found.

### `get_social_class(node)`

**Purpose:** Determine a node's social class for ornament mapping.

**Logic:** Read the node's social class from its graph properties or from the citizen data. Return "Citizen" as default if not set.

### `circadian_to_bpm(phase)`

**Purpose:** Convert circadian phase (0.0 - 1.0) to heartbeat-like pulse rate in BPM.

**Logic:** Map phase to BPM range: rest phase (0.0-0.3) -> 40-50 BPM, active phase (0.3-0.7) -> 60-80 BPM, high phase (0.7-1.0) -> 80-100 BPM. Smooth interpolation.

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| Graph (FalkorDB) | `graph.get(style_id)` | Thing(type=style) node with content + media |
| World Manifest | `get_zone_defaults(zone_id)` | Zone material default properties |
| Physics Tick | (reads) `node.energy`, `node.drives`, `node.circadian_phase` | Effects computation inputs |
| Skeleton (citizen_body_model) | (reads) bone definitions | 32 bones for proportions mapping |
| Three.js Renderer | (produces) ResolvedStyle | Render instructions consumed downstream |

---

## MARKERS

<!-- @mind:todo Define PROTOCOL_DEFAULT constant: mesh_uri, proportions, material, idle animations -->
<!-- @mind:todo Implement style content caching strategy (invalidate on style node update) -->
<!-- @mind:todo Define YAML schema validation for Thing(type=style).content -- what fields are required vs optional -->
<!-- @mind:proposition Cache resolved styles per (style_id, zone_id, variant_hash) tuple for O(1) repeat lookups -->
<!-- @mind:proposition Pre-compute drive modulation lookup table for common drive combinations -->
<!-- @mind:escalation Should proportions be per-bone (32 entries) or per-group (spine, limbs, head)? Per-bone is more flexible but more data. -->
