# OBJECTIVES — Spatial Geometry

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
THIS:            OBJECTIVES_Spatial_Geometry.md (you are here - START HERE)
PATTERNS:       ./PATTERNS_Spatial_Geometry.md
BEHAVIORS:      ./BEHAVIORS_Spatial_Geometry.md
ALGORITHM:      ./ALGORITHM_Spatial_Geometry.md
VALIDATION:     ./VALIDATION_Spatial_Geometry.md
IMPLEMENTATION: ./IMPLEMENTATION_Spatial_Geometry.md
HEALTH:         ./HEALTH_Spatial_Geometry.md
SYNC:           ./SYNC_Spatial_Geometry.md

IMPL:           runtime/infrastructure/spatial_geometry/ (to be created)
```

**Read this chain in order before making changes.** Each doc answers different questions. Skipping ahead means missing context.

---

## PRIMARY OBJECTIVES (ranked)

1. **Graph physics drive visual form** — Every Space node in the graph gets a 3D geometry that reflects its zone DNA, semantic content, and weight. The city is never hand-modeled; it is grown from data.

2. **Zone DNA inheritance** — Sub-spaces created by L10 macro-crystallization inherit their parent zone's visual attributes (primary_shape, material, light, particles, dynamics) so districts look coherent without manual art direction.

3. **Semantic variation within zones** — Two sub-spaces in the same zone look related but different. A library is more vertical and transparent than a forge in the same district. The Space's `synthesis` and `content` fields modulate the inherited zone attributes.

4. **Scalable rendering at 45K nodes** — Lumina Prime has ~45,000 nodes. The geometry pipeline must produce Level of Detail (LOD) variants so the Three.js client can render the full city without choking. LOD 0 (near) through LOD 3 (fog contribution only).

5. **GLTF as universal format** — All generated geometry ships as GLTF/GLB. Three.js, Blender, Unity, and any future renderer can consume it. The asset is stored via the multimodal media dict on the Space node: `media.geometry = {uri, embedding, meta}`.

## NON-OBJECTIVES

- **Manual 3D modeling workflow** — This module generates geometry procedurally. It does not provide a GUI editor or import pipeline for hand-made models.
- **Real-time mesh generation** — Geometry is pre-generated on crystallization events, not computed per frame. The renderer loads cached GLTF files.
- **Sound or particle runtime** — Zone YAMLs define sound and particle attributes, but this module only produces mesh geometry. Particle systems and audio are renderer-side concerns.
- **Non-Space node geometry** — Actors, moments, narratives, and things use the existing `physics_visual_mapping.py` for their visual representation (radius, glow, opacity). This module handles Space nodes only.

## TRADEOFFS (canonical decisions)

- When visual fidelity conflicts with render performance, choose **performance**. LOD exists to guarantee this.
- When zone coherence conflicts with sub-space uniqueness, choose **coherence**. A district must read as one visual identity; individual spaces vary within that frame, not outside it.
- When generation speed conflicts with mesh quality, choose **quality within a budget**. Generation happens offline (on crystallization events), so we can spend seconds, not milliseconds. But each GLTF must stay under 500KB at LOD 0.
- We accept that procedural geometry looks less polished than hand-crafted assets to preserve the principle that **the city grows from data**.

## SUCCESS SIGNALS (observable)

- Every Space node created by L10 macro-crystallization has a `media.geometry` entry within 30 seconds of creation.
- Sub-spaces within a zone are visually distinguishable but share their zone's primary shape language (crystal district has crystal sub-spaces, not organic blobs).
- The Three.js client renders 45K+ LOD representations at 30+ FPS on a mid-range GPU.
- A new zone YAML can be authored and immediately produces valid geometry for its sub-spaces without code changes.
- Generated GLTF files are valid (pass glTF-Validator) and loadable by Three.js, Blender, and Unity.

---

## MARKERS

<!-- @mind:todo Define the exact vertex budget per LOD level (LOD 0: target ~5000 verts, LOD 1: ~500 verts, LOD 2: ~50 verts or billboard, LOD 3: point sprite) -->
<!-- @mind:todo Determine whether generation runs in-process (Python) or as a sidecar service to avoid blocking the MCP server -->
<!-- @mind:proposition Consider generating zone-level aggregate geometry (the "district silhouette") as a separate LOD 3 asset, rather than compositing individual LOD 3 contributions -->
