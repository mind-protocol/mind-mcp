# Spatial Geometry — Algorithm: Zone-to-GLTF Generation Pipeline

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
THIS:            ALGORITHM_Spatial_Geometry.md (you are here)
VALIDATION:      ./VALIDATION_Spatial_Geometry.md
HEALTH:          ./HEALTH_Spatial_Geometry.md
IMPLEMENTATION:  ./IMPLEMENTATION_Spatial_Geometry.md
SYNC:            ./SYNC_Spatial_Geometry.md

IMPL:            runtime/infrastructure/spatial_geometry/ (to be created)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

The spatial geometry algorithm translates zone YAML attributes and Space node semantics into 3D mesh geometry exported as GLTF/GLB. It is a pipeline with five stages: zone attribute loading, semantic modulation, mesh generation, LOD decimation, and GLTF export with media dict storage. The pipeline runs once per Space creation event (triggered by L10 macro-crystallization), producing a static asset that the renderer loads on demand.

The core computational challenge is converting a high-dimensional parameter space (30+ zone attributes across geometry, surface, light, particles, dynamics) into a coherent 3D mesh. The algorithm addresses this by decomposing the problem: shape first (primary_shape selects base geometry), then displacement (regularity controls noise), then material (surface attributes map to PBR), then scale (weight), then position (barycentric).

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| O1: Graph physics drive form | B1, B6 | The algorithm IS the bridge between physics and visuals |
| O2: Zone DNA inheritance | B2, B7 | Zone attributes are the algorithm's primary input |
| O3: Semantic variation | B3 | Semantic modulation stage produces within-zone diversity |
| O4: Scalable rendering | B4 | LOD decimation stage guarantees render-time performance |
| O5: GLTF universal format | B5 | Export stage produces standards-compliant assets |

---

## DATA STRUCTURES

### ZoneAttributes

```
ZoneAttributes:
  geometry:
    primary_shape: str          # crystal|organic|angular|sphere|torus|cube|pyramid|...
    secondary_shape: str|null   # optional modifier shape
    symmetry: str               # radial|bilateral|none|fractal_self_similar
    regularity: float [0,1]     # noise amplitude control
    density: float [0,1]        # instance packing
    verticality: float [-1,1]   # Y-scale bias
    porosity: float [0,1]       # void fraction
    fractal_depth: int [0,5]    # recursive subdivision levels
    edge_sharpness: float [0,1] # boundary crispness
    growth_direction: str       # outward|inward|upward|downward|omni|spiral_up|spiral_down
  surface:
    material: str               # crystal_clear|metallic|organic|liquid|...
    transparency: float [0,1]
    reflectivity: float [0,1]
    roughness: float [0,1]
    warmth: float [0,1]
    age_patina: float [0,1]
    animation: str              # static|pulse|wave|shimmer|rotate|breathe|...
    animation_speed: float [0,2]
  light:
    primary_color: hex
    secondary_color: hex
    emission: float [0,2]
    color_variance: float [0,1]
    light_source: str
    shadow_depth: float [0,1]
  particles:
    type: str
    density: float [0,1]
    behavior: str
    reactivity: float [0,1]
    fog_density: float [0,1]
  dynamics:
    breathing: float [0,1]
    stability: float [0,1]
    gravity: float [0,2]
    entropy: float [0,1]
    responsiveness: float [0,1]
```

### SemanticModulation

```
SemanticModulation:
  verticality_shift: float [-0.2, +0.2]    # from synthesis analysis
  transparency_shift: float [-0.2, +0.2]
  density_shift: float [-0.2, +0.2]
  roughness_shift: float [-0.2, +0.2]
  warmth_shift: float [-0.2, +0.2]
  emission_shift: float [-0.3, +0.3]
```

### GeneratedAsset

```
GeneratedAsset:
  gltf_path: str                    # URI to GLTF/GLB file
  lod_paths: dict[int, str]         # {0: "lod0.glb", 1: "lod1.glb", ...}
  media_attachment:
    uri: str
    embedding: list[float]|null     # geometry embedding if model available
    meta:
      vertices_lod0: int
      lod_levels: int
      bounding_box: {min: vec3, max: vec3}
      parent_zone_id: str
      position: vec3
      scale: float
      generated_at: str             # ISO-8601
```

---

## ALGORITHM: generate_space_geometry()

### Step 1: Zone Attribute Resolution

Load the parent zone's YAML attributes. The parent zone is determined by the Space's link structure — follow the containment link (hierarchy=-1) upward to find the zone Space node, then look up its YAML by zone ID.

```
zone_id = find_parent_zone(space_node)
zone_attrs = load_zone_yaml(zone_id)

IF zone_attrs is None:
    zone_attrs = DEFAULT_ZONE_PROFILE   # neutral sphere, mid-range attributes
    log_warning(f"No zone YAML for {zone_id}, using default")
```

The zone YAML path is configurable: `{zone_yaml_root}/{zone_id}.yaml`. Default root is `lumina-prime/docs/city-architecture/spatial-mapping/zones/`.

### Step 2: Semantic Modulation

Analyze the Space node's `synthesis` field to compute attribute modulation values. The modulation shifts zone attributes within bounded ranges to express the space's semantic identity.

```
synthesis = space_node.synthesis

IF synthesis is empty:
    modulation = SemanticModulation(all zeros)  # no shift, pure zone DNA
ELSE:
    # Compute semantic dimensions via embedding similarity to reference anchors
    embedding = space_node.embedding

    # Reference anchors are pre-computed embeddings for semantic concepts:
    ANCHORS = {
        "knowledge": embed("library, research, contemplation, study, archives"),
        "creation":  embed("workshop, forge, laboratory, production, making"),
        "gathering": embed("plaza, forum, hall, meeting, social, celebration"),
        "nature":    embed("garden, growth, organic, ecosystem, living"),
        "power":     embed("tower, government, authority, decision, command"),
        "commerce":  embed("market, exchange, trade, transaction, economy"),
    }

    # Cosine similarity to each anchor gives a 6D semantic signature
    signature = {k: cosine_sim(embedding, v) for k, v in ANCHORS.items()}

    # Map semantic signature to attribute shifts
    modulation = SemanticModulation(
        verticality_shift  = 0.2 * (signature["power"] - signature["nature"]),
        transparency_shift = 0.2 * (signature["knowledge"] - signature["creation"]),
        density_shift      = 0.2 * (signature["commerce"] - signature["gathering"]),
        roughness_shift    = 0.2 * (signature["creation"] - signature["knowledge"]),
        warmth_shift       = 0.2 * (signature["gathering"] - signature["power"]),
        emission_shift     = 0.3 * (signature["power"] + signature["knowledge"]) / 2,
    )
```

### Step 3: Mesh Generation

Generate the base mesh from zone attributes + semantic modulation.

**3a. Select base geometry from primary_shape:**

```
SHAPE_MAP = {
    "crystal":  IcosahedronGeometry(radius=1, detail=fractal_depth),
    "sphere":   SphereGeometry(radius=1, widthSegments=32, heightSegments=32),
    "cube":     BoxGeometry(width=1, height=1, depth=1),
    "pyramid":  ConeGeometry(radius=1, height=1.5, radialSegments=4),
    "torus":    TorusGeometry(radius=1, tube=0.3, radialSegments=16),
    "cylinder": CylinderGeometry(radius=1, height=1.5),
    "cone":     ConeGeometry(radius=1, height=1.5, radialSegments=32),
    "spiral":   generate_spiral_geometry(turns=3, radius=1),
    "ring":     TorusGeometry(radius=1, tube=0.1, radialSegments=32),
    "cloud":    SphereGeometry + heavy Perlin noise,
    "fractal":  recursive_subdivision(depth=fractal_depth),
}

base_mesh = SHAPE_MAP[zone_attrs.geometry.primary_shape]
```

**3b. Apply noise displacement (regularity controls amplitude):**

```
noise_amplitude = (1.0 - effective_regularity) * 0.3   # 0 regularity = 0.3 max displacement
effective_regularity = clamp(zone_attrs.geometry.regularity + modulation.density_shift, 0, 1)

FOR each vertex in base_mesh.vertices:
    noise = perlin_3d(vertex.x * 2, vertex.y * 2, vertex.z * 2)
    vertex.position += vertex.normal * noise * noise_amplitude
```

**3c. Apply verticality (Y-scale bias):**

```
effective_verticality = clamp(zone_attrs.geometry.verticality + modulation.verticality_shift, -1, 1)
y_scale = 1.0 + effective_verticality * 0.5    # range [0.5, 1.5]
scale_mesh(base_mesh, x=1.0, y=y_scale, z=1.0)
```

**3d. Apply porosity (Boolean subtract voids):**

```
effective_porosity = zone_attrs.geometry.porosity

IF effective_porosity > 0.1:
    num_voids = int(effective_porosity * 10)     # 0-10 voids
    FOR i in range(num_voids):
        void_position = random_interior_point(base_mesh)
        void_radius = 0.05 + effective_porosity * 0.15
        base_mesh = boolean_subtract(base_mesh, sphere(void_position, void_radius))
```

**3e. Apply secondary_shape modulation:**

```
IF zone_attrs.geometry.secondary_shape is not None:
    secondary_mesh = SHAPE_MAP[zone_attrs.geometry.secondary_shape]
    scale_mesh(secondary_mesh, 0.3)  # secondary is smaller
    base_mesh = boolean_intersect_blend(base_mesh, secondary_mesh, blend=0.5)
```

**3f. Apply material properties:**

```
effective_transparency = clamp(zone_attrs.surface.transparency + modulation.transparency_shift, 0, 1)
effective_roughness = clamp(zone_attrs.surface.roughness + modulation.roughness_shift, 0, 1)
effective_warmth = clamp(zone_attrs.surface.warmth + modulation.warmth_shift, 0, 1)

material = PBRMaterial(
    baseColor       = warmth_to_color(effective_warmth, zone_attrs.light.primary_color),
    metalness       = zone_attrs.surface.reflectivity,
    roughness       = effective_roughness,
    transmission    = effective_transparency,
    emissiveFactor  = clamp(zone_attrs.light.emission + modulation.emission_shift, 0, 2) / 2.0,
    emissiveColor   = zone_attrs.light.primary_color,
)
```

### Step 4: Scale and Position

**4a. Weight-to-scale mapping:**

```
weight = space_node.weight or 0.1  # minimum weight to avoid zero-size

BASE_SCALE = 1.0
SCALE_FACTOR = 5.0
MAX_SCALE = 20.0

scale = min(MAX_SCALE, BASE_SCALE + 6.0 * log1p(weight * SCALE_FACTOR))
# Mirrors node_radius() from physics_visual_mapping.py

scale_mesh(base_mesh, scale, scale, scale)
```

**4b. Barycentric position within zone:**

```
zone_center = zone_position     # from zone YAML
zone_radius = zone_base_radius  # from zone YAML

# Semantic distance: how far from zone centroid embedding
IF space_node.embedding and zone_centroid_embedding:
    semantic_distance = 1.0 - cosine_sim(space_node.embedding, zone_centroid_embedding)
ELSE:
    semantic_distance = 0.5  # default: mid-distance

# Radial distance: semantic distance maps to physical distance from center
radial_distance = semantic_distance * zone_radius * 0.8  # leave 20% border

# Angular offset: creation-order-based to prevent stacking
angle = (creation_index * GOLDEN_ANGLE_RAD) % (2 * PI)
# Golden angle (137.508 degrees) ensures even angular distribution

position = vec3(
    zone_center.x + radial_distance * cos(angle),
    zone_center.y,  # Y determined by growth_direction
    zone_center.z + radial_distance * sin(angle),
)

# Growth direction modulates Y
IF zone_attrs.geometry.growth_direction == "upward":
    position.y += creation_index * 2.0 * scale  # stack upward
ELIF zone_attrs.geometry.growth_direction == "spiral_up":
    position.y += creation_index * 1.0 * scale
    angle += creation_index * 0.3   # spiral
```

### Step 5: LOD Generation and GLTF Export

**5a. Generate LOD levels:**

```
lod_meshes = {}

# LOD 0: Full mesh (already generated)
lod_meshes[0] = base_mesh   # target: < 5000 vertices

# LOD 1: Decimated mesh
lod_meshes[1] = decimate(base_mesh, target_ratio=0.1)   # ~500 vertices
lod_meshes[1].material = FlatColorMaterial(zone_attrs.light.primary_color)

# LOD 2: Billboard proxy
lod_meshes[2] = generate_billboard(
    width=bounding_box.width,
    height=bounding_box.height,
    color=zone_attrs.light.primary_color,
    alpha=0.8
)   # 4 vertices (quad)

# LOD 3: Point sprite metadata (no mesh — data only)
lod_3_meta = {
    "color": zone_attrs.light.primary_color,
    "emission": zone_attrs.light.emission,
    "size": scale,
    "position": position,
}
```

**5b. Export GLTF/GLB:**

```
FOR lod_level, mesh in lod_meshes.items():
    path = f"{storage_root}/spaces/{zone_id}/{space_node.id}_lod{lod_level}.glb"
    export_glb(mesh, path)

# Validate GLTF
validate_gltf(f"{storage_root}/spaces/{zone_id}/{space_node.id}_lod0.glb")
```

**5c. Build media attachment and store on node:**

```
media_attachment = MediaAttachment(
    uri = f"{storage_uri}/spaces/{zone_id}/{space_node.id}_lod0.glb",
    embedding = compute_geometry_embedding(base_mesh) if embedding_model else None,
    meta = {
        "vertices_lod0": count_vertices(lod_meshes[0]),
        "lod_levels": 4,
        "lod_uris": {
            0: f"{storage_uri}/spaces/{zone_id}/{space_node.id}_lod0.glb",
            1: f"{storage_uri}/spaces/{zone_id}/{space_node.id}_lod1.glb",
            2: f"{storage_uri}/spaces/{zone_id}/{space_node.id}_lod2.glb",
        },
        "lod3_meta": lod_3_meta,
        "bounding_box": compute_bounding_box(base_mesh),
        "parent_zone_id": zone_id,
        "position": [position.x, position.y, position.z],
        "scale": scale,
        "generated_at": now_iso8601(),
    }
)

# Write to graph
graph_write(space_node.id, {"media.geometry": media_attachment.to_dict()})
```

---

## KEY DECISIONS

### D1: Semantic Modulation via Embedding Anchors (not keywords)

```
IF using keyword matching on synthesis:
    Fragile — misses synonyms, requires keyword lists, breaks on novel descriptions.
    Rejected.
ELSE (using embedding cosine similarity to semantic anchors):
    Robust — captures semantic meaning regardless of wording.
    A synthesis like "space for quiet study and contemplation" matches "knowledge" anchor
    without needing to enumerate every possible phrasing.
    Chosen.
```

### D2: LOD 3 as Metadata, Not Geometry

```
IF generating a mesh for LOD 3:
    45K point sprites × individual meshes = 45K draw calls. Too many.
    Rejected.
ELSE (LOD 3 as metadata contributing to per-zone volumetric fog):
    The renderer aggregates LOD 3 data per zone into a single volumetric effect.
    One draw call per zone (7 total), not per space.
    Chosen.
```

### D3: Golden Angle for Angular Distribution

```
IF using uniform angular spacing (360° / n):
    Spaces clump when n changes. Existing spaces would need repositioning.
    Rejected.
ELSE (using golden angle, 137.508° increment per space):
    Maximally uniform distribution at any n. Adding a space never disturbs existing positions.
    Same technique used in phyllotaxis (sunflower seed patterns).
    Chosen.
```

### D4: Scale Formula Mirrors physics_visual_mapping.py

```
IF using a linear scale formula:
    High-weight nodes would be absurdly large. Weight ranges span orders of magnitude.
    Rejected.
ELSE (using logarithmic scale: base + factor * log1p(weight * multiplier)):
    Same formula as node_radius() in physics_visual_mapping.py.
    Consistent visual language: weight maps to size the same way everywhere.
    Chosen.
```

---

## DATA FLOW

```
L10 crystallization event (new Space node created)
    |
    v
find_parent_zone(space_node) -> zone_id
    |
    v
load_zone_yaml(zone_id) -> ZoneAttributes
    |
    v
compute_semantic_modulation(space_node.synthesis, space_node.embedding) -> SemanticModulation
    |
    v
generate_base_mesh(zone_attrs, modulation) -> Mesh
    |   - select shape from primary_shape
    |   - apply noise (regularity)
    |   - apply verticality
    |   - apply porosity
    |   - apply secondary_shape
    |   - apply material (surface + light attrs)
    |
    v
compute_scale_and_position(space_node.weight, zone_position, zone_radius) -> (scale, position)
    |
    v
generate_lod_variants(base_mesh) -> {0: Mesh, 1: Mesh, 2: Billboard, 3: MetaOnly}
    |
    v
export_gltf(lod_meshes, storage_path) -> file paths
    |
    v
build_media_attachment(paths, meta) -> MediaAttachment
    |
    v
graph_write(space_node.id, media.geometry = attachment) -> done
```

---

## COMPLEXITY

**Time:** O(V * log V) per space — V = vertex count of LOD 0 mesh. Noise displacement is O(V). Mesh decimation for LOD 1 is O(V log V) using quadric error metrics. Boolean subtraction (porosity) is O(V log V) per void.

**Space:** O(V) — vertex and face data for the mesh. Peak is LOD 0 mesh (~5000 vertices) + LOD 1 (~500) + billboard (4). Approximately 100KB in memory.

**Bottlenecks:**
- Boolean subtraction for porosity is the most expensive step. Each void requires a CSG operation. Mitigation: cap at 10 voids, use simple sphere voids.
- GLTF export I/O — writing 4 files per space. Mitigation: batch writes, use GLB (binary, single file).
- Embedding computation for geometry (if ULIP or similar model is available) could be slow. Mitigation: make embedding optional; generate it asynchronously.

---

## HELPER FUNCTIONS

### `find_parent_zone(space_node)`

**Purpose:** Walk the graph upward via containment links (hierarchy < 0) to find the nearest zone-level Space ancestor.

**Logic:** Query graph for outgoing links from space_node where hierarchy > 0.5 (abstracts/extends links point upward). Follow until a Space with a matching zone YAML is found. Return zone_id.

### `warmth_to_color(warmth, base_color)`

**Purpose:** Shift a base color toward warm (amber/gold) or cool (blue/white) based on warmth value.

**Logic:** Interpolate between cool white (#e0e8ff) and warm gold (#ffd699) by warmth factor, then blend with base_color at 50%.

### `decimate(mesh, target_ratio)`

**Purpose:** Reduce mesh vertex count while preserving shape. Used for LOD 1 generation.

**Logic:** Quadric error metric decimation (Garland & Heckbert). Iteratively collapse the edge with lowest error until target vertex count reached.

### `generate_billboard(width, height, color, alpha)`

**Purpose:** Create a camera-facing quad for LOD 2.

**Logic:** Two triangles forming a rectangle, with the zone's primary color as flat texture. The renderer orients this toward the camera each frame.

### `compute_geometry_embedding(mesh)`

**Purpose:** Generate a vector embedding of the 3D geometry for multimodal coherence.

**Logic:** If a geometry embedding model (ULIP) is available, render the mesh from 12 canonical viewpoints, pass through the model, average the view embeddings. If no model is available, return None — the geometry still works, it just does not participate in coherence search.

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| `runtime/cognition/models.py` | `Node.from_graph(id)` | Space node with synthesis, embedding, weight |
| `runtime/cognition/multimodal.py` | `MediaAttachment(uri, embedding, meta)` | Typed attachment for media dict |
| `mcp/tools/graph_write_handler.py` | `graph_write(node_id, properties)` | Updates Space node with media.geometry |
| `runtime/physics/` | L10 crystallization event subscription | Trigger for generation |
| Zone YAML files | `yaml.safe_load(file)` | ZoneAttributes dict |

---

## MARKERS

<!-- @mind:todo Implement the semantic anchor embeddings. These need to be pre-computed once and cached. Decide whether anchors are stored in constants.py or in a separate config file. -->
<!-- @mind:todo Validate the modulation bounds (+/- 0.2). Run visual tests with extreme synthesis values to confirm the variation is noticeable but does not break zone coherence. -->
<!-- @mind:todo Profile the Boolean subtraction (porosity) step. If CSG is too slow in Python, consider pre-computing void patterns per zone and reusing them. -->
<!-- @mind:escalation The golden angle positioning assumes a flat (XZ-plane) layout within each zone. For zones with growth_direction=upward or spiral_up, the 3D positioning formula needs more thought — pure golden angle only distributes on a disc. Consider a Fibonacci sphere for 3D distribution. -->
<!-- @mind:proposition Consider a two-pass generation: pass 1 generates all spaces in a zone in batch (allows inter-space awareness for collision avoidance), pass 2 exports GLTFs individually. This would improve spatial coherence at the cost of complexity. -->
