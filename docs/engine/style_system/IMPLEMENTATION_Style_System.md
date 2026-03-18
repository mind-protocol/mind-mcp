# Style System -- Implementation: Code Architecture and Structure

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Style_System.md
BEHAVIORS:       ./BEHAVIORS_Style_System.md
PATTERNS:        ./PATTERNS_Style_System.md
ALGORITHM:       ./ALGORITHM_Style_System.md
VALIDATION:      ./VALIDATION_Style_System.md
THIS:            IMPLEMENTATION_Style_System.md (you are here)
HEALTH:          ./HEALTH_Style_System.md
SYNC:            ./SYNC_Style_System.md

IMPL:            (not yet created -- DESIGNING phase)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

Code does not exist yet. This section defines the planned architecture.

```
engine/src/
├── shared/
│   ├── citizen_body_model.yaml            # Skeleton definition (exists)
│   └── style_system/                      # (to be created)
│       ├── style_resolver.js              # Core resolution algorithm (Steps 1-7)
│       ├── style_cache.js                 # Resolved style caching by (style_id, zone_id, variant_hash)
│       └── style_constants.js             # Protocol defaults, material defaults
├── server/
│   └── style_graph_operations.js          # Graph read/write for style nodes (to be created)
└── client/
    └── style_renderer_bridge.js           # Connects resolved styles to Three.js (to be created)
```

### File Responsibilities

| File | Purpose | Key Functions/Classes | Lines | Status |
|------|---------|----------------------|-------|--------|
| `style_resolver.js` | Resolution algorithm: node -> renderable assets | `resolveStyle()`, `applyZoneDefaults()`, `applyVariantOverrides()` | ~250 est. | PLANNED |
| `style_cache.js` | Cache resolved styles, invalidate on change | `StyleCache`, `getCachedStyle()`, `invalidate()` | ~120 est. | PLANNED |
| `style_constants.js` | Protocol default mesh, material, animations | `PROTOCOL_DEFAULT`, `DEFAULT_MATERIAL` | ~80 est. | PLANNED |
| `style_graph_operations.js` | Create/read/update style Thing nodes with ->created_by-> | `createStyle()`, `adoptStyle()`, `fetchStyleNode()` | ~200 est. | PLANNED |
| `style_renderer_bridge.js` | Map ResolvedStyle to Three.js SkinnedMesh + Material | `applyResolvedStyle()`, `loadGLTF()` | ~180 est. | PLANNED |

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Pipeline (resolution cascade) + Cache-Aside (resolved style cache)

**Why this pattern:** Style resolution is a deterministic pipeline: given the same inputs (style_id, zone_id, style_variant, drive state), it always produces the same output. This makes it ideal for caching. The cache-aside pattern means the renderer checks cache first, only running the pipeline on cache miss.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Pipeline | `style_resolver.js` | 7-step sequential resolution cascade |
| Cache-Aside | `style_cache.js` | Avoid re-resolving unchanged styles |
| Constants Object | `style_constants.js` | Single source for protocol defaults |
| Atomic Write | `style_graph_operations.js:createStyle()` | Style node + ->created_by-> link created together |

### Anti-Patterns to Avoid

- **Separate asset database**: Styles live in the graph, not in a parallel system. Do not create a "style store" alongside FalkorDB.
- **Deep inheritance**: Styles are flat. Do not add parent-style or style-extends-style relationships. If a new style is desired, create a new Thing node.
- **Effect customization leakage**: Never add effect-related fields to style content or style_variant processing. Effects are physics-only.

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Style Resolution | Cascade logic, caching, defaults | Three.js rendering, graph mutations | `resolveStyle(node, zone, drives, energy) -> ResolvedStyle` |
| Graph Operations | Style CRUD, ->created_by-> links | Resolution logic, rendering | `createStyle(content, media, artist_id) -> style_id` |
| Renderer Bridge | Three.js mesh/material application | Resolution logic, graph | `applyResolvedStyle(threeObject, resolvedStyle)` |

---

## SCHEMA

### Thing(type=style) Node

```yaml
ThingStyleNode:
  required:
    - id: string              # Unique node ID (e.g., "style:geometric_crystal")
    - name: string             # Human-readable style name
    - node_type: "thing"       # Always "thing"
    - subtype: "style"         # Always "style"
    - synthesis: string        # Embeddable description for graph_query discovery
    - content: string          # YAML string with proportions, material, ornaments, animations_idle
  optional:
    - media.geometry.uri: string   # glTF/GLB mesh file URI
    - media.geometry.meta: dict    # format, vertex_count, lod_levels
    - media.image.uri: string      # Preview thumbnail URI
  relationships:
    - ->created_by->: Actor    # Artist attribution (REQUIRED -- see V2)
  constraints:
    - content must be valid YAML
    - content.proportions.bone_scales values must be positive floats
    - content.material values must be in valid ranges (metalness [0,1], roughness [0,1], etc.)
```

### style_variant Dict (on NodeBase)

```yaml
StyleVariant:
  optional:
    - tint: string             # Hex color override for base_color
    - ornament: string         # Ornament type override (from social_class_styles vocabulary)
    - metalness: float         # Material override [0, 1]
    - roughness: float         # Material override [0, 1]
  constraints:
    - Effect-related keys (glow, particles, trail, pulse) are silently ignored
    - Values must be in valid ranges
```

---

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| `resolveStyle()` | `style_resolver.js` (planned) | Render tick per visible node |
| `createStyle()` | `style_graph_operations.js` (planned) | Artist publishes new style via MCP |
| `adoptStyle()` | `style_graph_operations.js` (planned) | Citizen changes style_id via MCP |
| `applyResolvedStyle()` | `style_renderer_bridge.js` (planned) | After resolution, applies to Three.js object |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

### Flow 1: Style Resolution (render tick)

This flow runs per visible node per render tick. It transforms graph state into Three.js render instructions. It is the highest-frequency flow and must be fast (< 1ms per node with caching).

```yaml
flow:
  name: style_resolution
  purpose: "Transform node graph state into renderable visual output"
  scope: "Input: NodeBase fields + graph. Output: ResolvedStyle for renderer."
  steps:
    - id: fetch_style
      description: "Read Thing(type=style) node from graph by style_id"
      file: style_resolver.js (planned)
      function: resolveStyle
      input: node.style_id (string)
      output: Thing node or null
      trigger: render tick
      side_effects: none
    - id: parse_content
      description: "Parse YAML content into structured style data"
      file: style_resolver.js (planned)
      function: resolveStyle
      input: Thing.content (YAML string)
      output: { proportions, material, ornaments, animations_idle }
      trigger: cache miss
      side_effects: none
    - id: cascade_material
      description: "Merge style material with zone defaults and variant overrides"
      file: style_resolver.js (planned)
      function: applyZoneDefaults + applyVariantOverrides
      input: style material + zone defaults + style_variant
      output: fully resolved material properties
      trigger: after parse
      side_effects: none
    - id: compute_effects
      description: "Compute effects from physics state (independent of style)"
      file: style_resolver.js (planned)
      function: computeEffects
      input: node.energy, node.drives, node.circadian_phase
      output: effects config
      trigger: after material cascade
      side_effects: none
  docking_points:
    guidance:
      include_when: "Data crosses graph->renderer boundary, or physics->visual boundary"
      omit_when: "Internal cache operations"
    available:
      - id: dock_style_fetch
        type: graph_ops
        direction: input
        file: style_resolver.js (planned)
        function: resolveStyle
        trigger: render tick with cache miss
        payload: "{ style_id: string } -> Thing node"
        async_hook: not_applicable
        needs: none
        notes: "Performance-critical -- must be fast or cached"
      - id: dock_resolved_output
        type: event
        direction: output
        file: style_resolver.js (planned)
        function: resolveStyle
        trigger: after full resolution
        payload: "ResolvedStyle object"
        async_hook: optional
        needs: none
        notes: "The complete render instruction set for one node"
    health_recommended:
      - dock_id: dock_style_fetch
        reason: "Dangling style_id references detected here (V5)"
      - dock_id: dock_resolved_output
        reason: "Material completeness verified here (V4)"
```

### Flow 2: Style Creation (artist publishes)

This flow runs infrequently when an artist creates a new style. It writes a Thing(type=style) node and atomically creates the ->created_by-> link. Data integrity is more important than speed.

```yaml
flow:
  name: style_creation
  purpose: "Artist publishes a new style to the graph catalog"
  scope: "Input: style definition + artist ID. Output: new Thing node + link."
  steps:
    - id: validate_content
      description: "Validate style content YAML schema"
      file: style_graph_operations.js (planned)
      function: createStyle
      input: "{ content: YAML, media: dict, artist_id: string }"
      output: validated content or error
      trigger: MCP call
      side_effects: none
    - id: write_style_node
      description: "Create Thing(type=style) node in graph"
      file: style_graph_operations.js (planned)
      function: createStyle
      input: validated content + media
      output: style node ID
      trigger: after validation
      side_effects: "New node in FalkorDB"
    - id: create_attribution_link
      description: "Create ->created_by-> link from style to artist"
      file: style_graph_operations.js (planned)
      function: createStyle
      input: style node ID + artist actor ID
      output: link ID
      trigger: atomic with node creation
      side_effects: "New link in FalkorDB"
  docking_points:
    available:
      - id: dock_style_created
        type: graph_ops
        direction: output
        file: style_graph_operations.js (planned)
        function: createStyle
        trigger: after atomic write
        payload: "{ style_id: string, artist_id: string }"
        async_hook: optional
        needs: none
        notes: "Must verify ->created_by-> link exists (V2)"
    health_recommended:
      - dock_id: dock_style_created
        reason: "Artist attribution integrity (V2)"
```

---

## LOGIC CHAINS

### LC1: Resolution Cascade

**Purpose:** Transform graph style data into renderer instructions

```
node.style_id
  -> graph.get(style_id)                # Fetch Thing(type=style) node
    -> parseYAML(node.content)          # Extract style layers
      -> mergeWith(zoneDefaults)        # Fill gaps with zone palette
        -> overrideWith(style_variant)  # Apply citizen customizations
          -> modulateWith(drives)       # Drive state alters idle animations
            -> ResolvedStyle            # Complete render instructions
```

**Data transformation:**
- Input: `string (style_id)` -- a graph node reference
- After step 1: `Thing node` -- raw graph data
- After step 2: `{ proportions, material, ornaments, animations }` -- structured layers
- After step 3: `material fully populated` -- no null properties
- After step 4: `citizen overrides applied` -- personalized
- Output: `ResolvedStyle` -- everything the renderer needs

### LC2: Style Adoption

**Purpose:** Citizen changes visual identity

```
citizen chooses style_id
  -> graph_write(actor.style_id = new_style_id)  # Update NodeBase field
    -> cache.invalidate(actor.id)                 # Bust resolved style cache
      -> next render tick resolves new style       # LC1 runs with new style_id
```

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
style_resolver.js
    └── imports -> style_cache.js
    └── imports -> style_constants.js
style_graph_operations.js
    └── imports -> graph adapter (FalkorDB)
style_renderer_bridge.js
    └── imports -> style_resolver.js
    └── imports -> Three.js (GLTFLoader, SkinnedMesh, MeshStandardMaterial)
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `three` | SkinnedMesh, MeshStandardMaterial, GLTFLoader | `style_renderer_bridge.js` |
| `js-yaml` | Parse YAML style content | `style_resolver.js` |
| FalkorDB client | Graph read/write | `style_graph_operations.js` |

---

## STATE MANAGEMENT

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| Style definitions | FalkorDB graph (Thing nodes) | Global | Persistent until deleted |
| Style references | NodeBase.style_id field | Per-node | Persistent, mutable |
| Resolved style cache | `StyleCache` in memory | Per engine instance | Invalidated on change, cleared on restart |
| Protocol defaults | `style_constants.js` | Global constant | Immutable |

### State Transitions

```
style_id = null ──(adopt)──> style_id = "style:xyz" ──(change)──> style_id = "style:abc" ──(clear)──> style_id = null
```

---

## RUNTIME BEHAVIOR

### Initialization

```
1. Load protocol defaults from style_constants.js
2. Initialize empty StyleCache
3. Pre-load zone material defaults from world-manifest.json
4. Style resolution is ready (lazy -- nodes resolved on first render)
```

### Main Loop (per render tick per visible node)

```
1. Check StyleCache for (node.id, node.style_id, node.zone_id, hash(node.style_variant))
2. If cache hit: return cached ResolvedStyle
3. If cache miss: run 7-step resolution pipeline (ALGORITHM Steps 1-7)
4. Store in StyleCache
5. Pass ResolvedStyle to style_renderer_bridge for Three.js application
```

### On Style Change (adoption or variant update)

```
1. graph_write updates node.style_id or node.style_variant
2. StyleCache.invalidate(node.id) removes cached entry
3. Next render tick triggers cache miss -> full resolution
```

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `PROTOCOL_DEFAULT.mesh_uri` | `style_constants.js` | TBD | URI to default geometric crystal mesh |
| `PROTOCOL_DEFAULT.material` | `style_constants.js` | `{ base_color: "#a0a8b8", metalness: 0.5, roughness: 0.5, transmission: 0.0, emissive: "#000000" }` | Fallback material when no style or zone set |
| `STYLE_CACHE_TTL_MS` | `style_cache.js` | 60000 (1 min) | Time before cache entries expire even without invalidation |
| `GLOW_ENERGY_THRESHOLD` | `style_constants.js` | 0.3 | Minimum energy for glow effect |
| `PARTICLE_DRIVE_THRESHOLD` | `style_constants.js` | 0.6 | Minimum curiosity drive for sparkle particles |

---

## BIDIRECTIONAL LINKS

### Code -> Docs

No code exists yet. When created, files should reference:

| File | Line | Reference |
|------|------|-----------|
| `style_resolver.js` | (planned) | `# DOCS: docs/engine/style_system/ALGORITHM_Style_System.md` |
| `style_graph_operations.js` | (planned) | `# DOCS: docs/engine/style_system/IMPLEMENTATION_Style_System.md` |
| `style_renderer_bridge.js` | (planned) | `# DOCS: docs/engine/style_system/IMPLEMENTATION_Style_System.md` |

### Docs -> Code

| Doc Section | Implemented In |
|-------------|----------------|
| ALGORITHM Steps 1-7 | `style_resolver.js:resolveStyle()` (planned) |
| BEHAVIOR B2 (artist credit) | `style_graph_operations.js:createStyle()` (planned) |
| BEHAVIOR B1 (adoption) | `style_graph_operations.js:adoptStyle()` (planned) |
| BEHAVIOR B3 (zone cascade) | `style_resolver.js:applyZoneDefaults()` (planned) |

---

## MARKERS

<!-- @mind:todo Create style_resolver.js implementing the 7-step resolution algorithm -->
<!-- @mind:todo Create style_cache.js with cache-aside pattern and invalidation -->
<!-- @mind:todo Create style_constants.js with protocol default mesh URI (needs asset creation first) -->
<!-- @mind:todo Create style_graph_operations.js with atomic style+link creation -->
<!-- @mind:todo Create style_renderer_bridge.js connecting to Three.js GLTFLoader -->
<!-- @mind:proposition Consider using a Web Worker for YAML parsing to avoid blocking render thread -->
<!-- @mind:escalation Protocol default mesh asset does not exist yet -- needs artist or procedural generation decision -->
