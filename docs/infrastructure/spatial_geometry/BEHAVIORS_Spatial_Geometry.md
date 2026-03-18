# Spatial Geometry — Behaviors: Observable Effects of Zone-to-GLTF Generation

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Spatial_Geometry.md
THIS:            BEHAVIORS_Spatial_Geometry.md (you are here)
PATTERNS:        ./PATTERNS_Spatial_Geometry.md
ALGORITHM:       ./ALGORITHM_Spatial_Geometry.md
VALIDATION:      ./VALIDATION_Spatial_Geometry.md
HEALTH:          ./HEALTH_Spatial_Geometry.md
IMPLEMENTATION:  ./IMPLEMENTATION_Spatial_Geometry.md
SYNC:            ./SYNC_Spatial_Geometry.md

IMPL:            runtime/infrastructure/spatial_geometry/ (to be created)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS

### B1: Crystallization Creates Geometry

**Why:** When L10 macro-crystallization creates a new Space node in the L3 graph, the city must grow visually. Without this behavior, new spaces would be invisible — they would exist in the graph but have no 3D representation. The trigger is crystallization, not manual request.

```
GIVEN:  L10 macro-crystallization fires and creates a new Space node in the L3 graph
WHEN:   The spatial_geometry module receives the crystallization event
THEN:   A GLTF/GLB file is generated for the new Space, with LOD 0 through LOD 3 variants
AND:    The GLTF URI is stored on the Space node as media.geometry.uri
AND:    Metadata (vertex count, LOD levels, bounding box, parent zone) is stored in media.geometry.meta
```

### B2: Zone Coherence Maintained

**Why:** Lumina Prime has 7 visually distinct districts. A visitor should be able to look around and know which district they are in by the shapes, materials, and light. This means all sub-spaces within a zone must share the zone's visual DNA — they inherit the parent zone's attributes as their baseline.

```
GIVEN:  A new Space is created within a zone that has a YAML definition
WHEN:   The generator reads the parent zone's attributes
THEN:   The generated mesh uses the zone's primary_shape as its base geometry
AND:    The zone's material properties (transparency, reflectivity, roughness, warmth) are applied to the mesh material
AND:    The zone's light and particle attributes are recorded in the GLTF metadata
```

### B3: Semantic Variation Expressed

**Why:** If all sub-spaces in a zone looked identical, the city would be monotonous. A library should feel different from a forge, even within the same district. The Space's synthesis field carries semantic meaning that should modulate the visual output, producing variation within the zone's visual family.

```
GIVEN:  A Space node has a synthesis field describing its purpose (e.g., "research library for quantum physics")
WHEN:   The generator processes this Space
THEN:   The synthesis is analyzed for semantic dimensions (verticality hint, transparency hint, density hint)
AND:    Zone attributes are modulated by up to +/- 0.2 based on the semantic analysis
AND:    The resulting mesh is visually distinguishable from other sub-spaces in the same zone
```

### B4: LOD Variants Generated

**Why:** With 45K nodes, the renderer cannot display full geometry for every space simultaneously. LOD variants allow the renderer to select appropriate detail levels based on camera distance, maintaining frame rate while preserving the city's visual density at all scales.

```
GIVEN:  A GLTF is being generated for a Space node
WHEN:   The generation pipeline reaches the export stage
THEN:   Four LOD levels are produced:
        - LOD 0: Full mesh with PBR materials (< 5000 vertices)
        - LOD 1: Decimated mesh with flat color (< 500 vertices)
        - LOD 2: Billboard sprite or low-poly proxy (< 50 vertices)
        - LOD 3: Metadata only (color, glow, position for fog contribution)
AND:    All LOD levels are stored in the GLTF or as separate linked files
AND:    media.geometry.meta.lod_levels records the count and vertex budgets
```

### B5: Media Dict Integration

**Why:** The multimodal media dict pattern (see PATTERNS_Multimodality.md) is the canonical way to attach non-text media to nodes. Geometry follows the same pattern: URI + embedding + metadata. This means the physics engine, coherence computation, and traversal can all discover and reason about spatial geometry without special-casing.

```
GIVEN:  A GLTF has been generated and stored for a Space node
WHEN:   The media dict is updated on the node
THEN:   media.geometry contains:
        - uri: path to the GLTF/GLB file
        - embedding: vector representation of the geometry (if embedding model available)
        - meta: {vertices, lod_levels, bounding_box, parent_zone_id, generated_at}
AND:    The node is queryable via graph_query for geometry-bearing spaces
```

### B6: Weight Determines Scale

**Why:** A Space's weight in the L3 physics represents its consolidated importance — how much activity, how many connections, how long it has existed. This importance should be physically visible: important spaces are big, marginal spaces are small. This creates an intuitive, readable city where the significant landmarks stand out.

```
GIVEN:  A Space node has weight W from the L3 physics
WHEN:   The generator computes the mesh scale
THEN:   The mesh scale is proportional to log1p(W * scale_factor)
AND:    A minimum scale (base_scale) prevents zero-weight spaces from being invisible
AND:    A maximum scale (max_scale) prevents runaway growth
```

### B7: Barycentric Positioning Within Zone

**Why:** Sub-spaces need positions within their parent zone. Random placement would break spatial coherence — related spaces should cluster. Barycentric positioning uses semantic proximity: the closer a sub-space's embedding is to the zone center, the closer it is positioned to the zone's physical center.

```
GIVEN:  A new Space node has been created within a zone
WHEN:   The generator computes the space's position
THEN:   The position is determined by:
        - The zone's base position and radius (from the zone YAML)
        - The semantic distance between the space's embedding and the zone centroid
        - An angular offset based on the space's creation order (to avoid stacking)
AND:    The position is stored in media.geometry.meta.position
```

---

## OBJECTIVES SERVED

| Behavior ID | Objective | Why It Matters |
|-------------|-----------|----------------|
| B1 | O1: Graph physics drive visual form | Makes crystallization visually productive — the city grows from data |
| B2 | O2: Zone DNA inheritance | Ensures districts maintain visual identity |
| B3 | O3: Semantic variation within zones | Prevents monotony while preserving coherence |
| B4 | O4: Scalable rendering at 45K nodes | Makes large-scale rendering possible |
| B5 | O5: GLTF as universal format | Integrates with the multimodal system cleanly |
| B6 | O1: Graph physics drive visual form | Weight becomes visible — the physics ARE the visuals |
| B7 | O2: Zone DNA inheritance | Spatial layout reflects semantic structure |

---

## INPUTS / OUTPUTS

### Primary Function: `generate_space_geometry()`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| space_node | Node | The Space node from the L3 graph (with synthesis, content, weight, links) |
| zone_attributes | dict | Parent zone YAML parsed into a dictionary |
| zone_position | vec3 | The zone's center position in world space |
| zone_radius | float | The zone's base radius |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| gltf_path | str | Path/URI to the generated GLTF/GLB file |
| media_attachment | MediaAttachment | Complete attachment for media.geometry (uri, embedding, meta) |

**Side Effects:**

- GLTF/GLB file written to storage (filesystem or object store)
- Space node updated with media.geometry in the L3 graph

---

## EDGE CASES

### E1: Space Created in Unknown Zone

```
GIVEN:  A Space node is created but its parent zone has no YAML definition
THEN:   The generator uses a default zone profile (sphere, medium regularity, neutral material)
AND:    A warning is logged indicating the missing zone YAML
AND:    media.geometry.meta.fallback = true is set on the node
```

### E2: Space Has No Synthesis

```
GIVEN:  A Space node exists with an empty or null synthesis field
THEN:   No semantic modulation is applied — the space gets pure zone DNA geometry
AND:    The mesh is a "generic" instance of the zone family
```

### E3: Extremely High Weight Space

```
GIVEN:  A Space node has weight > 100 (extremely consolidated)
THEN:   The scale is capped at max_scale to prevent it from engulfing the zone
AND:    Visual importance is instead conveyed by glow intensity (from energy) and material emission
```

### E4: Zone Radius Exhausted

```
GIVEN:  A zone has more sub-spaces than can fit at minimum spacing within its radius
THEN:   The zone radius expands (growth_direction applies) rather than overlapping meshes
AND:    The expansion is recorded in the zone's spatial state
```

---

## ANTI-BEHAVIORS

What should NOT happen:

### A1: Manual Geometry Requirement

```
GIVEN:   L10 creates a new Space node
WHEN:    The crystallization event fires
MUST NOT: Require any human action to produce geometry
INSTEAD:  Geometry generation is fully automatic from the event trigger
```

### A2: Zone Visual Leakage

```
GIVEN:   A Space belongs to the "crystal" zone (The Radiant Core)
WHEN:    Its geometry is generated
MUST NOT: Produce organic, cloud-like, or toroidal shapes
INSTEAD:  Base geometry is always IcosahedronGeometry (crystal family), modulated within crystal parameter bounds
```

### A3: Raw Mesh Data in Graph

```
GIVEN:   A GLTF has been generated
WHEN:    The result is stored on the Space node
MUST NOT: Store vertex arrays, face indices, or binary mesh data in FalkorDB node properties
INSTEAD:  Store only the URI (string) pointing to external storage, plus lightweight metadata
```

### A4: Unbounded Generation Time

```
GIVEN:   A crystallization event creates a new Space
WHEN:    The geometry pipeline runs
MUST NOT: Take more than 30 seconds for a single space
INSTEAD:  Generation completes within a time budget; if mesh complexity exceeds budget, reduce fractal_depth
```

---

## MARKERS

<!-- @mind:todo Define the exact semantic-to-attribute modulation mapping. Which words in synthesis map to which attribute shifts? Consider using the node's embedding cosine similarity to semantic anchors (e.g., "library" anchor, "forge" anchor) rather than keyword matching. -->
<!-- @mind:todo Specify the default zone profile for E1 (unknown zone). Should it be a neutral sphere or should it inherit from the nearest known zone? -->
<!-- @mind:proposition Consider a B8: "Geometry Regeneration on Weight Change" — when a Space's weight changes significantly (e.g., doubles), its scale should update. This could be periodic rather than per-tick. v2+ territory. -->
