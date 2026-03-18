# Spatial Geometry — Patterns: Zone DNA to GLTF via Procedural Generation

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Spatial_Geometry.md
THIS:            PATTERNS_Spatial_Geometry.md (you are here)
BEHAVIORS:       ./BEHAVIORS_Spatial_Geometry.md
ALGORITHM:       ./ALGORITHM_Spatial_Geometry.md
VALIDATION:      ./VALIDATION_Spatial_Geometry.md
HEALTH:          ./HEALTH_Spatial_Geometry.md
IMPLEMENTATION:  ./IMPLEMENTATION_Spatial_Geometry.md
SYNC:            ./SYNC_Spatial_Geometry.md

IMPL:            runtime/infrastructure/spatial_geometry/ (to be created)
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read the linked IMPL source file

**After modifying this doc:**
1. Update the IMPL source file to match, OR
2. Add a TODO in SYNC_Spatial_Geometry.md: "Docs updated, implementation needs: {what}"

**After modifying the code:**
1. Update this doc chain to match, OR
2. Add a TODO in SYNC_Spatial_Geometry.md: "Implementation changed, docs need: {what}"

---

## THE PROBLEM

Space nodes in the L3 graph are abstract containers. They have `synthesis`, `content`, `space_hint`, and link dimensions — but no visual form. When a visitor walks through Lumina Prime, what does a district look like? What does a building inside that district look like? Currently, nothing. The graph holds meaning but produces no geometry.

Lumina Prime has 7 districts, each with a zone YAML defining detailed visual attributes: `primary_shape`, `regularity`, `density`, `verticality`, `porosity`, `material`, `transparency`, `reflectivity`, and more. These attributes are a rich, curated visual DNA. But the DNA has no phenotype — nothing translates these numbers into actual 3D meshes.

When L10 macro-crystallization creates a new Space node (a new building, lab, or gathering hall within a district), that space should appear in the 3D world automatically — inheriting its district's visual language while expressing its own semantic identity. A library in the Towers of Knowledge should be tall, crystalline, transparent. A forge in The Arsenal should be dense, rough, dark metallic. Both should look like they belong to their district.

Without this module, the city would require hand-modeling every space, or it would be a featureless point cloud. Neither option scales to 45K nodes. Neither option allows the city to grow organically from graph physics.

---

## THE PATTERN

**Zone DNA inheritance with semantic modulation.**

Every zone (district) has a YAML file defining its visual attributes across 5 categories: geometry, surface, light, particles, and dynamics. These attributes are the zone's visual DNA — they define what "crystal district" or "organic garden" looks and feels like.

When a sub-space is created within a zone, the generation pipeline:

1. **Inherits** the parent zone's attributes as a starting point
2. **Modulates** those attributes based on the sub-space's semantic content (its `synthesis` field)
3. **Scales** the mesh based on the node's weight (heavier = physically larger)
4. **Positions** the mesh within the zone using barycentric placement (semantic proximity to zone center determines location)
5. **Exports** the result as a GLTF/GLB file with LOD variants
6. **Stores** the asset URI + embedding on the Space node via the media dict

The key insight: **the zone YAML is a parameter space, not a model**. It does not describe one fixed shape — it describes a family of shapes. Each sub-space is a specific instantiation within that family, varied by its semantic signature.

The second key insight: **the physics-to-visual mapping already exists** (see `runtime/cognition/physics_visual_mapping.py`). That module maps node physics (weight, energy, stability, recency) to visual properties (radius, glow, opacity, pulse). This module extends that paradigm to Space nodes specifically, using zone attributes as the additional parameter space that node physics alone cannot provide.

---

## BEHAVIORS SUPPORTED

- **B1** (Crystallization Creates Geometry) — when L10 creates a new Space, a GLTF is generated and stored automatically
- **B2** (Zone Coherence Maintained) — sub-spaces inherit parent zone visual DNA, maintaining district identity
- **B3** (Semantic Variation Expressed) — within a zone, sub-spaces differ based on their synthesis content
- **B4** (LOD Variants Generated) — each asset ships with 4 LOD levels for scalable rendering
- **B5** (Media Dict Integration) — geometry stored as `media.geometry` following the multimodal pattern
- **B6** (Weight Determines Scale) — heavier nodes produce physically larger meshes

## BEHAVIORS PREVENTED

- **A1** (Manual Geometry Required) — the pipeline is fully automatic; no human intervention needed for a space to appear
- **A2** (Zone Visual Leakage) — a crystal-district space cannot accidentally look organic; zone DNA constrains the output
- **A3** (Binary Blobs in Graph) — meshes stored as URI references only; raw vertex data never enters FalkorDB

---

## PRINCIPLES

### Principle 1: Zone DNA as Parameter Space

A zone YAML is not a description of one shape. It is a recipe for a family of shapes. `primary_shape: crystal` means "base geometry is an icosahedron with faceted normals." `regularity: 0.85` means "apply low-amplitude noise — mostly ordered." `density: 0.8` means "pack instances close together." The combination of all attributes defines the space of possible geometries. Each sub-space is a point in that space, selected by its semantic content.

This means adding a new zone is purely declarative — author a YAML, and the generator produces matching geometry. No new code paths, no custom shaders, no art asset pipeline.

### Principle 2: Semantic Modulation, Not Semantic Override

A sub-space's semantic content (from `synthesis`) modulates zone attributes — it does not replace them. If the zone says `primary_shape: crystal` and the sub-space is a library, the result is a crystal-shaped library (more vertical, more transparent), not a bookshelf. The zone DNA always dominates. Semantic content shifts parameters within bounds, typically +/- 0.2 from the zone baseline.

This preserves district coherence while allowing visual diversity. A visitor can always tell which district they are in by the shapes around them.

### Principle 3: GLTF Is the Universal Exchange

Every generated mesh is exported as GLTF/GLB. This is a deliberate choice:
- Three.js has first-class GLTF support (GLTFLoader)
- Blender imports GLTF natively (for manual touchup if ever needed)
- Unity, Godot, and other engines have GLTF importers
- The format supports PBR materials, vertex colors, and animations
- glTF-Validator provides automated validation

No custom binary format. No engine-specific serialization. GLTF is the interop layer between generation and rendering.

### Principle 4: Weight Is Size

A Space node's weight (from the L3 physics) determines its physical scale in the 3D world. This creates a direct, readable mapping: important spaces are big, marginal spaces are small. No separate "importance" annotation — the physics already computed it. The formula is logarithmic: `scale = base_scale * log1p(weight * scale_factor)`, matching the `node_radius()` pattern from `physics_visual_mapping.py`.

### Principle 5: LOD Is Not Optional

With 45K nodes, rendering full geometry for every space is impossible. LOD is a structural requirement, not an optimization:
- **LOD 0** (near, <50m): Full mesh with PBR materials, textures, particles
- **LOD 1** (medium, 50-200m): Simplified mesh (decimated), flat color material
- **LOD 2** (far, 200-1000m): Instanced billboard or point sprite
- **LOD 3** (very far, >1000m): Contribution to zone fog/glow accumulator only

Each LOD level is a separate entry in the GLTF file (or a separate file). The renderer selects the appropriate level based on camera distance. LOD 3 is special — it does not produce individual geometry but contributes color and density to a per-zone volumetric effect.

---

## DATA

| Source | Type | Purpose / Description |
|--------|------|-----------------------|
| `lumina-prime/docs/city-architecture/spatial-mapping/zones/*.yaml` | FILE | Zone attribute YAMLs — the visual DNA for each of the 7 districts |
| `lumina-prime/docs/city-architecture/spatial-mapping/zone_attributes_schema.yaml` | FILE | Schema defining all zone attributes (geometry, surface, light, particles, dynamics) |
| `schema-l3.yaml` | FILE | L3 schema — defines Space nodes, macro-crystallization trigger, media dict |
| `runtime/cognition/physics_visual_mapping.py` | FILE | Existing physics-to-visual mapping — pattern reference for weight-to-scale |
| `docs/cognition/multimodality/PATTERNS_Multimodality.md` | FILE | Media dict pattern — how `media.geometry` fits the multimodal system |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `runtime/cognition/multimodal.py` | MediaAttachment type for storing geometry URIs + embeddings in the media dict |
| `runtime/cognition/models.py` | Node/Space model — reading synthesis, content, weight, and media dict |
| `runtime/cognition/constants.py` | Modality confidence weight for geometry embeddings (w_geometry) |
| `mcp/tools/graph_write_handler.py` | Writing `media.geometry` back to Space nodes after generation |
| `runtime/physics/` | L10 macro-crystallization events — the trigger for geometry generation |
| `schema-l3.yaml` | Space node schema and L10 crystallization specification |

---

## INSPIRATIONS

**Wave Function Collapse (WFC).** Procedural generation technique where local constraints propagate to produce globally coherent output. Zone DNA acts similarly — it constrains the generative space so that all outputs within a zone are coherent without requiring global coordination.

**L-systems and fractal growth.** Lindenmayer systems generate complex organic shapes from simple recursive rules. The `fractal_depth` attribute in zone YAMLs controls recursive subdivision depth, echoing L-system iteration. Growth directions (upward, spiral_up, outward) mirror L-system tropisms.

**Three.js procedural geometry.** Three.js provides parametric geometry constructors (IcosahedronGeometry, BoxGeometry, SphereGeometry) that map directly to zone primary_shape values. The displacement, noise, and material pipeline follows established Three.js procedural generation patterns.

**Signed Distance Functions (SDF).** The porosity attribute (Boolean subtract operations for voids) is best implemented via SDF composition: `max(shape_sdf, -void_sdf)`. SDF-based generation also enables smooth blending between shapes when secondary_shape modulates primary_shape.

**physics_visual_mapping.py in mind-mcp.** The existing module maps node physics dimensions to visual properties using explicit, readable formulas (logarithmic for radius, sigmoid for glow, linear for opacity). Spatial geometry extends this approach: zone attributes are the "physics" and 3D mesh parameters are the "visual."

---

## SCOPE

### In Scope

- Procedural mesh generation from zone YAML attributes
- Semantic modulation of zone DNA based on Space node synthesis
- GLTF/GLB export with multiple LOD levels
- Weight-to-scale mapping for Space nodes
- Barycentric positioning within zones
- Media dict integration (`media.geometry = {uri, embedding, meta}`)
- Zone attribute-to-3D property mapping (shape, material, displacement, animation)
- Crystallization event listener (trigger for geometry generation)

### Out of Scope

- **Renderer / scene graph** — This module produces GLTF files. The Three.js client in `engine/` loads and renders them. Rendering logic is out of scope.
- **Zone YAML authoring** — Zone YAMLs are authored by worldbuilders in `lumina-prime/docs/city-architecture/`. This module reads them, does not write them.
- **Particle systems** — Zone YAMLs define particle attributes (type, density, behavior). These are runtime renderer effects, not mesh geometry.
- **Sound design** — Zone YAMLs define ambient_base and event_sound. Audio is a renderer concern.
- **Non-Space geometry** — Actor avatars, Thing icons, Moment markers use `physics_visual_mapping.py`. This module handles Space nodes only.
- **Texture painting** — PBR material properties come from zone attributes (transparency, reflectivity, roughness, warmth). No custom texture maps are generated.

---

## MARKERS

<!-- @mind:todo Evaluate trimesh (Python) vs Three.js (Node.js) for mesh generation. Python keeps the pipeline in the MCP runtime; Node.js would share code with the renderer. Decision needed before implementation. -->
<!-- @mind:todo Determine storage backend for GLTF files (local filesystem vs S3/R2). Must align with the media upload pipeline in mcp/tools/media_handler.py. -->
<!-- @mind:escalation Zone YAMLs currently live in lumina-prime, not mind-mcp. The spatial_geometry module in mind-mcp needs to read them. Either: (a) zones are copied to mind-mcp at deploy time, (b) the module reads from a configurable path, or (c) zone data is stored in the L3 graph as Space node properties. Decision needed. -->
<!-- @mind:proposition Consider a "geometry embedding" model (ULIP or similar) that embeds the generated GLTF into a vector, enabling visual similarity search across spaces. This would populate media.geometry.embedding and participate in multimodal coherence. -->
