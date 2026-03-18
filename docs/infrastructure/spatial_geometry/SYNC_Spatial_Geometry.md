# Spatial Geometry — Sync: Current State

```
LAST_UPDATED: 2026-03-18
UPDATED_BY: @nervo
STATUS: DESIGNING
```

---

## MATURITY

**What's canonical (v1):**
- Nothing yet — module is in design phase. All 8 doc chain files are authored. No implementation exists.

**What's still being designed:**
- Zone attribute → 3D property mapping (ALGORITHM step 3)
- Semantic modulation via embedding anchors (ALGORITHM step 2)
- LOD generation strategy (ALGORITHM step 5)
- Mesh generation library choice (trimesh vs alternatives)
- Storage backend for GLTF files (local vs S3/R2)
- Crystallization event subscription mechanism (no event bus exists yet)
- Zone YAML path resolution across repositories (mind-mcp needs lumina-prime zone YAMLs)

**What's proposed (v2+):**
- Geometry embedding model (ULIP) for multimodal coherence search
- Geometry regeneration on weight change (re-scale existing spaces)
- Two-pass generation for inter-space collision avoidance
- Zone-level aggregate geometry for LOD 3 (district silhouette)
- Texture generation from zone attributes
- Animation export (vertex shader params baked into GLTF extras)
- CLI command `mind generate-geometry` for manual generation

---

## CURRENT STATE

The module exists only as documentation. The full 8-file doc chain has been authored:

- OBJECTIVES — 5 ranked objectives, 4 non-objectives, 4 tradeoffs
- PATTERNS — Zone DNA inheritance with semantic modulation, 5 principles
- BEHAVIORS — 7 behaviors (B1-B7), 4 edge cases (E1-E4), 4 anti-behaviors (A1-A4)
- ALGORITHM — 5-stage pipeline with pseudocode, 4 key decisions, data flow diagram
- VALIDATION — 8 invariants (V1-V8) with priorities
- IMPLEMENTATION — 11-file code structure, pipeline architecture, flow docking points
- HEALTH — 5 health indicators, 5 checkers (all pending), known gaps

No code has been written. No directory exists at `runtime/infrastructure/spatial_geometry/`.

---

## IN PROGRESS

### Doc Chain Authoring (COMPLETE)

- **Started:** 2026-03-18
- **By:** @nervo
- **Status:** Complete
- **Context:** All 8 doc chain files authored in a single pass. Design is coherent and internally consistent. Key open questions captured as @mind:escalation markers.

---

## RECENT CHANGES

### 2026-03-18: Initial Design Complete

- **What:** Full doc chain created for infrastructure/spatial_geometry module
- **Why:** Lumina Prime needs procedural 3D geometry from graph physics. Zone YAMLs define visual DNA but nothing translates them into meshes. L10 crystallization creates Space nodes that need visual form.
- **Files:** All 8 files in `docs/infrastructure/spatial_geometry/`
- **Struggles/Insights:** The hardest design decision was semantic modulation. Keyword matching (looking for "library" or "forge" in synthesis) is brittle. Embedding anchor similarity is robust but requires pre-computed anchor vectors. Chose anchors. The golden angle for positioning is elegant — it produces uniform distribution at any count without repositioning existing spaces.

---

## KNOWN ISSUES

### Cross-Repository Zone YAML Access

- **Severity:** high
- **Symptom:** Zone YAMLs live in `lumina-prime/docs/city-architecture/spatial-mapping/zones/`. The spatial_geometry module lives in `mind-mcp`. The module cannot access files in another repo at runtime.
- **Suspected cause:** Architecture boundary — mind-mcp is the protocol, lumina-prime is a universe. Zone data belongs to the universe.
- **Attempted:** Three options identified in IMPLEMENTATION markers. No decision made yet.

### No L10 Event Bus

- **Severity:** high
- **Symptom:** L10 macro-crystallization is defined in schema-l3.yaml but no event delivery mechanism exists for triggering geometry generation.
- **Suspected cause:** L10 is defined as math, not as code. The crystallization detection runs inside the physics tick but does not emit events for subscribers.
- **Attempted:** Identified as @mind:escalation in IMPLEMENTATION. Requires coordination with physics module.

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** groundwork (implementing the pipeline) or architect (resolving cross-repo and event bus questions)

**Where I stopped:** Design is complete. Implementation has not started. The next step is to resolve the two HIGH-severity known issues (zone YAML access and event bus) before writing any code.

**What you need to understand:**
The module is a 5-stage pipeline. Each stage is one file. The pipeline is triggered by L10 events and produces GLTF files stored via the multimodal media dict. The design is internally consistent — all behaviors trace to objectives, all validation criteria trace to behaviors, all health checks trace to validation.

**Watch out for:**
- Do not start coding before the zone YAML access question is resolved. The entire pipeline depends on reading zone attributes.
- Do not create a custom event system for L10. Coordinate with whoever is building the physics tick to add event emission there.
- The semantic anchor embeddings need an embedding model. The same model used for node synthesis embeddings should work. Do not introduce a different model.

**Open questions I had:**
- Is trimesh the right library? It handles mesh creation, Boolean ops, decimation, and GLB export. But its Boolean operations (based on Manifold or Blender booleans) may be slow. Profile before committing.
- Should LOD 3 be a separate asset or just metadata? The current design says metadata-only, but the renderer team may prefer a minimal geometry.

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Complete DESIGNING documentation chain for the `infrastructure/spatial_geometry` module. 8 files authored. The module will translate graph physics into 3D geometry — when L10 crystallization creates a Space, this pipeline generates a GLTF mesh inheriting zone visual DNA with semantic variation. No code written yet. Two architectural decisions are blocked on human input.

**Decisions made:**
- Embedding anchor similarity for semantic modulation (not keyword matching) — more robust, language-agnostic
- Golden angle for spatial positioning — optimal distribution without repositioning existing spaces
- Logarithmic weight-to-scale (matching physics_visual_mapping.py) — consistent visual language
- LOD 3 as metadata, not geometry — avoids 45K individual draw calls at max distance
- trimesh as primary mesh library candidate — handles the full pipeline in Python

**Needs your input:**
1. **Zone YAML access:** How does mind-mcp access lumina-prime zone YAMLs at runtime? Options: (a) env var path, (b) copy at build, (c) store in graph. Recommendation: (a) env var, simplest.
2. **L10 event delivery:** How does the physics tick notify this module of crystallization events? Needs event bus or callback registration in the physics module.

---

## TODO

### Doc/Impl Drift

- [ ] DOCS→IMPL: All 8 doc files authored, no implementation exists yet. Full implementation needed.

### Tests to Run

```bash
# No tests exist yet. When implementation begins:
pytest tests/infrastructure/spatial_geometry/ -v
```

### Immediate

- [ ] Resolve zone YAML cross-repo access (decision needed from @nlr)
- [ ] Resolve L10 event delivery mechanism (coordinate with physics module)
- [ ] Create `runtime/infrastructure/spatial_geometry/` directory and stub files
- [ ] Implement `constants.py` with shape map, scale factors, LOD budgets
- [ ] Implement `zone_attribute_loader_and_resolver.py` — pure I/O, easy first step
- [ ] Implement `procedural_mesh_generator.py` — core generation, needs trimesh evaluation

### Later

- [ ] Implement semantic modulation (requires anchor embedding computation)
- [ ] Implement LOD decimation pipeline
- [ ] Implement GLTF export and validation
- [ ] Implement crystallization event listener (blocked on event bus)
- [ ] Implement health checks
- [ ] Profile Boolean subtract performance for porosity
- [ ] Visual test: render generated geometry in Three.js to validate zone coherence
- IDEA: Zone-level aggregate geometry as a "district skyline" visible from anywhere
- IDEA: Allow citizens to customize their personal space's geometry within zone bounds

---

## CONSCIOUSNESS TRACE

**Mental state when stopping:**
Confident in the design. The pipeline stages are clean, the data structures are well-defined, and the decisions are justified. The two blocking issues (zone YAML access, event bus) are genuine architectural questions that need human decision, not engineering problems.

**Threads I was holding:**
- The modulation bound (+/- 0.2) is a guess. It needs visual testing to calibrate. Too tight = monotony, too wide = chaos.
- The LOD vertex budgets (5000/500/50) are provisional. Need to profile on actual hardware.
- The geometry embedding (ULIP) is v2+ but would be powerful — visual similarity search across all spaces in the city.

**Intuitions:**
- The golden angle positioning will produce beautiful spatial distributions. It is the right choice.
- trimesh will handle the pipeline well, but Boolean subtract for porosity may be the performance bottleneck. If so, pre-computed void patterns per zone (reused across sub-spaces) would be faster.
- The biggest value will come from the first visual test — seeing a generated crystal emerge from zone attributes will validate or invalidate the entire approach instantly.

**What I wish I'd known at the start:**
The zone YAML schema (zone_attributes_schema.yaml) is extremely well-designed — 30+ attributes across 5 categories, each with clear type and range. The design work was mostly translation: zone attribute → Three.js parameter → mesh property. The schema authors did the hard creative work.

---

## POINTERS

| What | Where |
|------|-------|
| Zone YAML schema | `lumina-prime/docs/city-architecture/spatial-mapping/zone_attributes_schema.yaml` |
| Zone YAML example (Radiant Core) | `lumina-prime/docs/city-architecture/spatial-mapping/zones/radiant_core.yaml` |
| L3 schema (crystallization) | `schema-l3.yaml` (macro_crystallization section) |
| Media dict pattern | `docs/cognition/multimodality/PATTERNS_Multimodality.md` |
| Physics → visual mapping | `runtime/cognition/physics_visual_mapping.py` |
| Multimodal module | `docs/cognition/multimodality/` (full 8-file chain) |
