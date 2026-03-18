# Spatial Geometry — Validation: What Must Be True

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Spatial_Geometry.md
PATTERNS:        ./PATTERNS_Spatial_Geometry.md
BEHAVIORS:       ./BEHAVIORS_Spatial_Geometry.md
THIS:            VALIDATION_Spatial_Geometry.md (you are here)
ALGORITHM:       ./ALGORITHM_Spatial_Geometry.md
IMPLEMENTATION:  ./IMPLEMENTATION_Spatial_Geometry.md
HEALTH:          ./HEALTH_Spatial_Geometry.md
SYNC:            ./SYNC_Spatial_Geometry.md
```

---

## PURPOSE

**Validation = what we care about being true.**

Not mechanisms. Not test paths. Not how things work.

What properties, if violated, would mean the spatial geometry system has failed its purpose? These invariants protect the core promise: that graph physics produce coherent, performant, standards-compliant 3D geometry.

---

## INVARIANTS

### V1: Every Crystallized Space Gets Geometry

**Why we care:** If a Space node exists in the L3 graph (created by L10) but has no `media.geometry`, that space is invisible in the 3D world. The city has a hole. Visitors walk through a void. The promise that "the city grows from data" is broken.

```
MUST:   Every Space node created by L10 macro-crystallization has a non-null media.geometry entry
        within 30 seconds of creation
NEVER:  A Space node created by crystallization remains without geometry indefinitely
```

### V2: GLTF Structural Validity

**Why we care:** An invalid GLTF crashes the renderer, shows as a missing object, or produces visual artifacts. The Three.js GLTFLoader silently fails on malformed files. If generated assets are structurally invalid, the city is unreliable.

```
MUST:   Every generated GLTF/GLB file passes glTF-Validator with zero errors
MUST:   Every GLTF has at least one mesh, one material, and valid accessor/buffer references
NEVER:  A generated GLTF contains NaN vertex positions, degenerate triangles, or orphaned accessors
```

### V3: Zone Coherence Preserved

**Why we care:** Districts must be visually distinct. If a crystal district contains organic blobs or an angular district contains smooth spheres, the spatial language of the city is broken. Visitors cannot orient themselves by district identity.

```
MUST:   The primary_shape of every sub-space mesh matches the parent zone's primary_shape family
MUST:   Material properties (metalness, roughness, color temperature) of sub-spaces fall within
        +/- 0.2 of the parent zone's surface attributes
NEVER:  A sub-space uses a primary_shape from a different zone family
```

### V4: LOD Budget Respected

**Why we care:** If LOD 0 meshes exceed the vertex budget, the renderer chokes when the camera approaches dense areas. If LOD 1/2 are missing, the renderer has no fallback at medium/far distances. Both cases cause frame drops below 30 FPS, breaking the interactive experience.

```
MUST:   LOD 0 meshes have fewer than 5000 vertices
MUST:   LOD 1 meshes have fewer than 500 vertices
MUST:   LOD 2 is a billboard (4 vertices) or low-poly proxy (< 50 vertices)
MUST:   All LOD levels exist for every generated space
NEVER:  A generated mesh exceeds its LOD vertex budget
```

### V5: No Binary Data in Graph

**Why we care:** FalkorDB stores node properties as Redis-compatible types. Vertex arrays and buffer data would bloat the graph, degrade query performance, and risk serialization failures. The graph must remain lean — geometry lives in external storage, referenced by URI.

```
MUST:   media.geometry.uri is a string (file path or object store URI)
MUST:   media.geometry.meta contains only JSON-serializable primitives (strings, numbers, lists, dicts)
NEVER:  Vertex positions, face indices, texture data, or base64-encoded binary appears in node properties
```

### V6: Generation Time Bounded

**Why we care:** Geometry generation runs when L10 crystallization fires. If generation takes minutes, it blocks the crystallization pipeline and delays the graph's self-management. The system becomes sluggish. The 30-second window (V1) requires generation to complete within that budget.

```
MUST:   Single-space geometry generation completes in under 30 seconds
MUST:   Generation time is logged and measurable
NEVER:  Generation blocks the main MCP server event loop (must run async or in a worker)
```

### V7: Weight-to-Scale Monotonicity

**Why we care:** If a heavier space is smaller than a lighter one, the visual language is broken. Weight is supposed to mean importance. Size is supposed to reflect weight. The relationship must be strictly monotonic.

```
MUST:   For spaces within the same zone: if weight_A > weight_B, then scale_A >= scale_B
MUST:   scale >= BASE_SCALE for all spaces (no invisible/zero-size spaces)
NEVER:  A space's scale decreases when its weight increases
```

### V8: Positioning Within Zone Bounds

**Why we care:** If sub-spaces are placed outside their parent zone's radius, the district boundaries dissolve. Spaces from one district visually overlap into another. The city's spatial organization breaks down.

```
MUST:   Every sub-space's position falls within 1.2x the parent zone's base_radius from zone center
        (20% overshoot allowed for growth)
MUST:   No two sub-spaces within the same zone occupy the same position (minimum spacing enforced)
NEVER:  A sub-space is placed at the exact center of another zone
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
| V1 | Every space is visible | CRITICAL |
| V2 | Assets are structurally valid | CRITICAL |
| V3 | Districts are visually distinct | HIGH |
| V4 | Renderer stays performant | HIGH |
| V5 | Graph stays lean | HIGH |
| V6 | Generation does not block the system | HIGH |
| V7 | Weight means size (visual honesty) | MEDIUM |
| V8 | Spatial layout is coherent | MEDIUM |

---

## MARKERS

<!-- @mind:todo V2 needs an automated validation step in the pipeline — run glTF-Validator as part of export. Define what happens on validation failure (retry with simpler mesh? log and skip?). -->
<!-- @mind:todo V4 vertex budgets are provisional. Profile actual rendering performance on target hardware to confirm 5000/500/50 thresholds are appropriate. -->
<!-- @mind:proposition Consider V9: "Semantic Modulation Perceptibility" — the visual difference between two semantically different spaces in the same zone should be measurable (e.g., perceptual color difference deltaE > 5, or mesh Hausdorff distance > threshold). This would ensure B3 is not just technically correct but actually visible. -->
<!-- @mind:escalation V3's +/- 0.2 modulation bound is a design decision. Too tight (0.1) makes all sub-spaces look identical. Too wide (0.4) breaks zone coherence. Need visual testing to validate 0.2 as the right number. -->
