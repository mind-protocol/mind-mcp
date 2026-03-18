# Spatial Geometry — Implementation: Code Architecture and Structure

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Spatial_Geometry.md
BEHAVIORS:       ./BEHAVIORS_Spatial_Geometry.md
PATTERNS:        ./PATTERNS_Spatial_Geometry.md
ALGORITHM:       ./ALGORITHM_Spatial_Geometry.md
VALIDATION:      ./VALIDATION_Spatial_Geometry.md
THIS:            IMPLEMENTATION_Spatial_Geometry.md (you are here)
HEALTH:          ./HEALTH_Spatial_Geometry.md
SYNC:            ./SYNC_Spatial_Geometry.md

IMPL:            runtime/infrastructure/spatial_geometry/ (to be created)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

```
runtime/infrastructure/spatial_geometry/
├── __init__.py                                    # Public API: generate_space_geometry(), regenerate_zone()
├── zone_attribute_loader_and_resolver.py           # Load zone YAMLs, resolve parent zone, merge defaults
├── semantic_modulation_from_synthesis.py            # Analyze synthesis → SemanticModulation shifts
├── procedural_mesh_generator.py                     # Base mesh creation, noise, porosity, secondary shape
├── material_property_mapper.py                      # Zone surface/light attrs → PBR material parameters
├── scale_and_position_calculator.py                 # Weight→scale, barycentric positioning, golden angle
├── lod_variant_generator_and_decimator.py           # LOD 0→3 generation, mesh decimation, billboard creation
├── gltf_exporter_and_validator.py                   # GLTF/GLB export, glTF-Validator integration
├── media_dict_attachment_builder.py                 # Build MediaAttachment, write to graph via graph_write
├── crystallization_event_listener.py                # Subscribe to L10 events, dispatch generation pipeline
└── constants.py                                     # Shape map, anchor embeddings, scale factors, LOD budgets
```

### File Responsibilities

| File | Purpose | Key Functions/Classes | Est. Lines | Status |
|------|---------|----------------------|------------|--------|
| `__init__.py` | Public API surface | `generate_space_geometry()`, `regenerate_zone()` | ~50 | OK |
| `zone_attribute_loader_and_resolver.py` | Zone YAML I/O and parent resolution | `load_zone_yaml()`, `find_parent_zone()`, `DEFAULT_ZONE` | ~120 | OK |
| `semantic_modulation_from_synthesis.py` | Synthesis → modulation shifts | `compute_modulation()`, `SEMANTIC_ANCHORS` | ~100 | OK |
| `procedural_mesh_generator.py` | Core mesh generation | `generate_base_mesh()`, `apply_noise()`, `apply_porosity()` | ~300 | OK |
| `material_property_mapper.py` | Zone attrs → PBR material | `build_pbr_material()`, `warmth_to_color()` | ~80 | OK |
| `scale_and_position_calculator.py` | Weight/position math | `compute_scale()`, `compute_position()`, `GOLDEN_ANGLE` | ~100 | OK |
| `lod_variant_generator_and_decimator.py` | LOD pipeline | `generate_lod_variants()`, `decimate()`, `generate_billboard()` | ~200 | OK |
| `gltf_exporter_and_validator.py` | Export and validation | `export_glb()`, `validate_gltf()` | ~150 | OK |
| `media_dict_attachment_builder.py` | Media dict integration | `build_attachment()`, `store_on_node()` | ~80 | OK |
| `crystallization_event_listener.py` | Event subscription | `on_crystallization()`, `start_listener()` | ~100 | OK |
| `constants.py` | Configuration constants | Shape map, anchors, budgets | ~80 | OK |

**Size Thresholds:**
- **OK** (<400 lines): Healthy size, easy to understand
- **WATCH** (400-700 lines): Getting large, consider extraction opportunities
- **SPLIT** (>700 lines): Too large, must split before adding more code

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Pipeline (staged transformation)

**Why this pattern:** Geometry generation is a linear transformation: zone attributes in, GLTF file out. Each stage has clear inputs and outputs. Stages are independently testable. The pipeline can be extended (e.g., adding a texture generation stage) by inserting a new stage without modifying existing ones.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Pipeline | `generate_space_geometry()` in `__init__.py` | Orchestrates the 5-stage generation pipeline |
| Strategy | `SHAPE_MAP` in `constants.py` | Selects base geometry constructor by primary_shape string |
| Observer | `crystallization_event_listener.py` | Subscribes to L10 events without coupling to physics code |
| Builder | `media_dict_attachment_builder.py` | Assembles MediaAttachment from parts |
| Factory | `procedural_mesh_generator.py` | Creates mesh objects from zone attributes |

### Anti-Patterns to Avoid

- **God Object**: Do not let `procedural_mesh_generator.py` handle material, LOD, and export. Each concern has its own file.
- **Premature Abstraction**: Do not create a `MeshPlugin` interface until there are 3+ shape families with genuinely different code paths. The SHAPE_MAP dict is sufficient.
- **Fallback Geometry**: Do not silently substitute a default mesh when generation fails. Fail loud (V2 demands valid GLTF or error). Edge case E1 (unknown zone) is the only allowed fallback, and it is explicit.

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Generation pipeline | Mesh creation, LOD, export | Renderer, scene graph, camera | `generate_space_geometry()` returns MediaAttachment |
| Zone attribute space | YAML loading, defaults, validation | Zone YAML authoring | `load_zone_yaml(zone_id)` returns ZoneAttributes dict |
| Graph integration | Reading node data, writing media dict | Graph queries, traversal, physics | `graph_write()` via handler |

---

## SCHEMA

### ZoneAttributes (parsed from YAML)

```yaml
ZoneAttributes:
  required:
    - geometry.primary_shape: str     # from zone_attributes_schema.yaml enum
    - geometry.regularity: float      # [0, 1]
    - surface.material: str           # from schema enum
    - light.primary_color: hex        # e.g., "#e8e0ff"
  optional:
    - geometry.secondary_shape: str   # nullable
    - geometry.fractal_depth: int     # default 1
    - geometry.porosity: float        # default 0.0
    - surface.animation: str          # default "static"
    - dynamics.*: float               # all default to 0.5
  constraints:
    - All floats within their documented ranges
    - primary_shape must be one of the 11 enum values
    - fractal_depth must be int in [0, 5]
```

### MediaGeometryAttachment (stored on Space node)

```yaml
MediaGeometryAttachment:
  required:
    - uri: str                        # path to LOD 0 GLTF/GLB
    - meta.vertices_lod0: int         # vertex count at highest detail
    - meta.lod_levels: int            # always 4
    - meta.parent_zone_id: str        # which zone this belongs to
    - meta.position: list[float]      # [x, y, z] world position
    - meta.scale: float               # computed from weight
    - meta.generated_at: str          # ISO-8601
  optional:
    - embedding: list[float]          # geometry embedding vector (if model available)
    - meta.lod_uris: dict[int, str]   # paths to LOD 1, 2 files
    - meta.lod3_meta: dict            # color, emission, size for fog contribution
    - meta.bounding_box: dict         # {min: [x,y,z], max: [x,y,z]}
  relationships:
    - parent_zone: Space node (via containment link)
    - space_node: Space node this geometry belongs to
```

---

## ENTRY POINTS

| Entry Point | File | Triggered By |
|-------------|------|--------------|
| `generate_space_geometry()` | `__init__.py` | L10 crystallization event (via listener) |
| `regenerate_zone()` | `__init__.py` | Manual request to regenerate all spaces in a zone |
| `on_crystallization()` | `crystallization_event_listener.py` | L10 event subscription |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

### Flow 1: Crystallization-Triggered Geometry Generation

This is the primary flow. It transforms a new Space node and its parent zone attributes into a GLTF asset stored on the node. This flow matters because it is the only path to visual geometry — if it fails, spaces are invisible.

```yaml
flow:
  name: crystallization_geometry_generation
  purpose: Generate 3D geometry for a newly crystallized Space node
  scope: L10 event in → media.geometry on Space node out
  steps:
    - id: event_received
      description: L10 crystallization event arrives with new Space node ID
      file: runtime/infrastructure/spatial_geometry/crystallization_event_listener.py
      function: on_crystallization()
      input: crystallization_event {space_node_id, zone_id, timestamp}
      output: dispatches to generate_space_geometry()
      trigger: L10 macro-crystallization event
      side_effects: none

    - id: zone_resolution
      description: Load parent zone attributes from YAML
      file: runtime/infrastructure/spatial_geometry/zone_attribute_loader_and_resolver.py
      function: load_zone_yaml(), find_parent_zone()
      input: zone_id (str)
      output: ZoneAttributes dict
      trigger: called by generate_space_geometry()
      side_effects: filesystem read (zone YAML)

    - id: semantic_modulation
      description: Compute attribute shifts from Space synthesis
      file: runtime/infrastructure/spatial_geometry/semantic_modulation_from_synthesis.py
      function: compute_modulation()
      input: synthesis (str), embedding (list[float])
      output: SemanticModulation dataclass
      trigger: called by generate_space_geometry()
      side_effects: none (pure computation)

    - id: mesh_generation
      description: Generate base mesh from zone attrs + modulation
      file: runtime/infrastructure/spatial_geometry/procedural_mesh_generator.py
      function: generate_base_mesh()
      input: ZoneAttributes, SemanticModulation
      output: Mesh object (vertices, faces, normals)
      trigger: called by generate_space_geometry()
      side_effects: none (pure computation)

    - id: scale_position
      description: Compute scale from weight, position via barycentric formula
      file: runtime/infrastructure/spatial_geometry/scale_and_position_calculator.py
      function: compute_scale(), compute_position()
      input: weight (float), zone_position (vec3), zone_radius (float)
      output: scale (float), position (vec3)
      trigger: called by generate_space_geometry()
      side_effects: none

    - id: lod_generation
      description: Generate LOD 0-3 variants via decimation
      file: runtime/infrastructure/spatial_geometry/lod_variant_generator_and_decimator.py
      function: generate_lod_variants()
      input: Mesh (LOD 0), LOD budgets
      output: dict[int, Mesh|dict]
      trigger: called by generate_space_geometry()
      side_effects: none

    - id: gltf_export
      description: Export meshes as GLB files, validate
      file: runtime/infrastructure/spatial_geometry/gltf_exporter_and_validator.py
      function: export_glb(), validate_gltf()
      input: dict[int, Mesh], storage_path
      output: file paths (list[str])
      trigger: called by generate_space_geometry()
      side_effects: filesystem write (GLB files)

    - id: media_storage
      description: Build MediaAttachment and write to graph
      file: runtime/infrastructure/spatial_geometry/media_dict_attachment_builder.py
      function: build_attachment(), store_on_node()
      input: file paths, metadata, space_node_id
      output: MediaAttachment
      trigger: called by generate_space_geometry()
      side_effects: graph write (media.geometry on Space node)

  docking_points:
    guidance:
      include_when: transformative step, risk of data loss, cross-boundary I/O
      omit_when: pure in-memory computation with no side effects
      selection_notes: Focus on I/O boundaries (event input, file write, graph write) and the mesh generation output (core value)
    available:
      - id: dock_event_input
        type: event
        direction: input
        file: runtime/infrastructure/spatial_geometry/crystallization_event_listener.py
        function: on_crystallization()
        trigger: L10 crystallization event
        payload: {space_node_id, zone_id, timestamp}
        async_hook: required
        needs: add event subscription
        notes: Entry point — if this fails, no geometry is generated

      - id: dock_mesh_output
        type: custom
        direction: output
        file: runtime/infrastructure/spatial_geometry/procedural_mesh_generator.py
        function: generate_base_mesh()
        trigger: internal pipeline step
        payload: Mesh {vertices, faces, normals, material}
        async_hook: not_applicable
        needs: none
        notes: Core generation output — vertex count and shape correctness are critical

      - id: dock_gltf_write
        type: file
        direction: output
        file: runtime/infrastructure/spatial_geometry/gltf_exporter_and_validator.py
        function: export_glb()
        trigger: internal pipeline step
        payload: GLB binary file
        async_hook: optional
        needs: none
        notes: Filesystem write — validation must pass before write completes

      - id: dock_graph_write
        type: graph_ops
        direction: output
        file: runtime/infrastructure/spatial_geometry/media_dict_attachment_builder.py
        function: store_on_node()
        trigger: internal pipeline step
        payload: {media.geometry: MediaAttachment}
        async_hook: required
        needs: add async hook for graph_write completion
        notes: Final step — if this fails, geometry exists on disk but is not linked to the node

    health_recommended:
      - dock_id: dock_event_input
        reason: Entry point — missed events mean invisible spaces (V1)
      - dock_id: dock_mesh_output
        reason: Core output — vertex budget (V4) and shape correctness (V3) must hold
      - dock_id: dock_gltf_write
        reason: GLTF validity (V2) verified at this point
      - dock_id: dock_graph_write
        reason: Final storage — confirms media dict is populated (V1, V5)
```

---

## LOGIC CHAINS

### LC1: Crystallization → Geometry → Storage

**Purpose:** Complete path from a crystallization event to a visible space in the 3D world.

```
L10 crystallization event
  → crystallization_event_listener.on_crystallization()     # receive event
    → zone_attribute_loader_and_resolver.load_zone_yaml()   # load zone DNA
    → semantic_modulation_from_synthesis.compute_modulation() # analyze semantics
      → procedural_mesh_generator.generate_base_mesh()      # create geometry
        → scale_and_position_calculator.compute_scale()     # weight → size
        → scale_and_position_calculator.compute_position()  # barycentric placement
          → lod_variant_generator_and_decimator.generate_lod_variants() # LOD 0-3
            → gltf_exporter_and_validator.export_glb()      # write files
            → gltf_exporter_and_validator.validate_gltf()   # verify validity
              → media_dict_attachment_builder.store_on_node() # write to graph
                → Space node now has media.geometry
```

**Data transformation:**
- Input: `crystallization_event` — {space_node_id, zone_id}
- After zone resolution: `ZoneAttributes` — full parameter space
- After modulation: `ZoneAttributes + SemanticModulation` — personalized parameters
- After mesh gen: `Mesh` — vertices, faces, normals, material
- After scale/position: `Mesh` — scaled and positioned
- After LOD: `dict[int, Mesh]` — 4 detail levels
- After export: `list[str]` — file paths on disk
- Output: `MediaAttachment` — stored on graph node

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
__init__.py
    └── imports → crystallization_event_listener.py
    └── imports → zone_attribute_loader_and_resolver.py
    └── imports → semantic_modulation_from_synthesis.py
    └── imports → procedural_mesh_generator.py
    └── imports → material_property_mapper.py
    └── imports → scale_and_position_calculator.py
    └── imports → lod_variant_generator_and_decimator.py
    └── imports → gltf_exporter_and_validator.py
    └── imports → media_dict_attachment_builder.py
    └── imports → constants.py
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `trimesh` | Mesh creation, Boolean ops, decimation, GLB export | `procedural_mesh_generator.py`, `lod_variant_generator_and_decimator.py`, `gltf_exporter_and_validator.py` |
| `numpy` | Vertex math, noise computation, vector operations | `procedural_mesh_generator.py`, `scale_and_position_calculator.py` |
| `noise` (pnoise3) | Perlin noise for displacement | `procedural_mesh_generator.py` |
| `pyyaml` | Zone YAML loading | `zone_attribute_loader_and_resolver.py` |
| `pygltflib` or `trimesh.exchange.gltf` | GLTF/GLB export | `gltf_exporter_and_validator.py` |

---

## STATE MANAGEMENT

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| Zone YAML cache | `zone_attribute_loader_and_resolver.py:_zone_cache` | module-level dict | Created on first load, invalidated on file change |
| Semantic anchor embeddings | `constants.py:SEMANTIC_ANCHORS` | module-level dict | Computed once at import, immutable |
| Generation queue | `crystallization_event_listener.py:_queue` | module-level asyncio.Queue | Created at listener start, drained continuously |

### State Transitions

```
L10 event arrives ──enqueue──▶ generation_pending ──dequeue──▶ generating ──export──▶ stored_on_node
```

---

## RUNTIME BEHAVIOR

### Initialization

```
1. Load and cache zone YAMLs from configured path
2. Pre-compute semantic anchor embeddings (6 anchors)
3. Start crystallization event listener (subscribes to L10 events)
4. System ready — awaiting crystallization events
```

### Main Loop / Request Cycle

```
1. L10 crystallization event received → enqueue space_node_id
2. Worker dequeues → calls generate_space_geometry()
3. Pipeline runs 5 stages → produces GLTF + MediaAttachment
4. MediaAttachment written to graph → space is now visible
5. Log generation time and vertex counts
```

### Shutdown

```
1. Stop accepting new events
2. Drain remaining queue items (finish pending generations)
3. Close zone YAML file handles
```

---

## CONCURRENCY MODEL

| Component | Model | Notes |
|-----------|-------|-------|
| Event listener | async (asyncio) | Non-blocking event subscription |
| Generation pipeline | sync within async worker | Mesh generation is CPU-bound, runs in thread pool executor |
| GLTF export | sync (file I/O) | Writes to local filesystem or object store |
| Graph write | async | graph_write_handler is async |

The generation pipeline itself is synchronous (CPU-bound mesh math). It runs inside an `asyncio.to_thread()` call to avoid blocking the MCP server event loop. A bounded semaphore limits concurrent generations to prevent CPU exhaustion (default: 2 concurrent).

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `ZONE_YAML_ROOT` | `constants.py` | `"zones/"` | Path to zone YAML directory |
| `GEOMETRY_STORAGE_ROOT` | `constants.py` | `"assets/spaces/"` | Where GLTF files are written |
| `GEOMETRY_STORAGE_URI` | `constants.py` | `"file://assets/spaces/"` | URI prefix for media.geometry.uri |
| `BASE_SCALE` | `constants.py` | `1.0` | Minimum mesh scale |
| `SCALE_FACTOR` | `constants.py` | `5.0` | Weight-to-scale multiplier |
| `MAX_SCALE` | `constants.py` | `20.0` | Maximum mesh scale |
| `LOD0_VERTEX_BUDGET` | `constants.py` | `5000` | Max vertices for LOD 0 |
| `LOD1_VERTEX_BUDGET` | `constants.py` | `500` | Max vertices for LOD 1 |
| `MAX_CONCURRENT_GENERATIONS` | `constants.py` | `2` | Semaphore limit for concurrent gen |
| `GENERATION_TIMEOUT_S` | `constants.py` | `30` | Max seconds per generation |
| `MODULATION_BOUND` | `constants.py` | `0.2` | Max attribute shift from semantic modulation |

---

## BIDIRECTIONAL LINKS

### Code → Docs

Files that reference this documentation:

| File | Line | Reference |
|------|------|-----------|
| `runtime/infrastructure/spatial_geometry/__init__.py` | TBD | `# DOCS: docs/infrastructure/spatial_geometry/IMPLEMENTATION_Spatial_Geometry.md` |
| `runtime/infrastructure/spatial_geometry/constants.py` | TBD | `# DOCS: docs/infrastructure/spatial_geometry/ALGORITHM_Spatial_Geometry.md` |

### Docs → Code

| Doc Section | Implemented In |
|-------------|----------------|
| ALGORITHM step 1 (zone resolution) | `zone_attribute_loader_and_resolver.py:load_zone_yaml()` |
| ALGORITHM step 2 (semantic modulation) | `semantic_modulation_from_synthesis.py:compute_modulation()` |
| ALGORITHM step 3 (mesh generation) | `procedural_mesh_generator.py:generate_base_mesh()` |
| ALGORITHM step 4 (scale and position) | `scale_and_position_calculator.py:compute_scale(), compute_position()` |
| ALGORITHM step 5 (LOD and export) | `lod_variant_generator_and_decimator.py`, `gltf_exporter_and_validator.py` |
| BEHAVIOR B1 | `crystallization_event_listener.py:on_crystallization()` |
| BEHAVIOR B5 | `media_dict_attachment_builder.py:build_attachment()` |
| VALIDATION V2 | `gltf_exporter_and_validator.py:validate_gltf()` |

---

## EXTRACTION CANDIDATES

No files approaching WATCH/SPLIT status — all estimated under 300 lines. If `procedural_mesh_generator.py` grows beyond 400 lines, extract noise functions and Boolean operations into separate modules.

---

## MARKERS

<!-- @mind:todo Create the runtime/infrastructure/spatial_geometry/ directory and stub files once implementation begins -->
<!-- @mind:todo Evaluate trimesh vs open3d vs custom mesh generation. trimesh is the leading candidate (MIT license, GLB export, Boolean ops, decimation). Profile Boolean subtract performance for porosity. -->
<!-- @mind:todo Set up the crystallization event subscription mechanism. Currently L10 crystallization is defined in schema-l3.yaml but no event bus exists. Need to coordinate with physics module on event delivery. -->
<!-- @mind:escalation The ZONE_YAML_ROOT path crosses repository boundaries (zone YAMLs are in lumina-prime, this code is in mind-mcp). Either: (1) configure at deploy time via env var, (2) copy zones at build time, or (3) store zone data in the graph itself. Architecture decision needed. -->
<!-- @mind:proposition Consider a CLI command `mind generate-geometry [space_id|zone_id]` for manual (re)generation, useful during development and debugging. -->
