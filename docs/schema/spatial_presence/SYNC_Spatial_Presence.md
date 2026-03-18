# Spatial Presence — Sync: Current State

```
LAST_UPDATED: 2026-03-18
UPDATED_BY: @nervo
STATUS: DESIGNING
```

---

## MATURITY

**What's canonical (v1):**
- 6 spatial fields defined on NodeBase in schema-l1.yaml v2.3: position, orientation, scale, velocity, mass, zone_id
- Field types, defaults, and descriptions are stable
- Barycentrique position formula implemented in `scripts/spatial_mapper.py`
- Zone attractor positions and attraction profiles defined
- Scale formula: `1.0 + log1p(weight)`
- Mass formula: `weight * (1 + 0.1 * link_count)`

**What's still being designed:**
- Engine-side orientation and velocity writes (Three.js integration)
- Scale and mass computation in the spatial mapper (formulas defined, not yet implemented in mapper)
- Damping implementation in the renderer
- Health check runtime code (`runtime/checks/spatial_presence_health.py`)
- Mapper run frequency and scheduling
- Mass-based gravitational inter-node attraction (mass computed but not used for pull)
- Vision cone computation from orientation

**What's proposed (v2+):**
- Angular velocity for rotation tracking
- Bounding radius derived from scale for spatial queries
- LOD (Level of Detail) for distant nodes
- SLERP interpolation for orientation transitions
- "Grounded" flag for nodes that resist migration (district space nodes)

---

## CURRENT STATE

The 6 spatial fields are defined on NodeBase in schema-l1.yaml and documented in schema-l3.yaml. The spatial mapper (`scripts/spatial_mapper.py`) is implemented and can compute position and zone_id for all L3 nodes using the barycentrique algorithm with 7 fixed zone attractors. It writes position and zone_id to FalkorDB.

Scale and mass formulas are defined in this doc chain and in schema-l1.yaml field descriptions, but `spatial_mapper.py` does not yet compute or write them. The mapper currently writes only position (as array) and zone_id (as string).

Orientation and velocity are defined on the schema but have no writer yet. The 3D engine (Three.js, in lumina-prime's engine/) would write these, but that integration does not exist.

The physics_visual_mapping.py module provides `node_radius(weight)` which is related to but distinct from the `scale` field. The scale field uses `1.0 + log1p(weight)` while node_radius uses `2.0 + 6.0 * log1p(weight * 5.0)` — the visual mapping is for rendering, scale is the schema property.

This doc chain documents the complete design for all 6 fields. The gap is between design and implementation: position + zone_id are implemented; scale, mass, orientation, velocity are designed but not implemented.

---

## IN PROGRESS

### Doc Chain Creation

- **Started:** 2026-03-18
- **By:** @nervo
- **Status:** Complete (this chain)
- **Context:** Documents the 6 spatial fields added in schema-l1.yaml v2.3. All 8 doc chain files created: OBJECTIVES, PATTERNS, BEHAVIORS, ALGORITHM, VALIDATION, IMPLEMENTATION, HEALTH, SYNC.

---

## RECENT CHANGES

### 2026-03-18: Spatial Presence Doc Chain Created

- **What:** Full 8-file DESIGNING doc chain for the `schema/spatial_presence` module
- **Why:** The 6 spatial fields on NodeBase needed formal documentation: what they are, how they are computed, what invariants they must satisfy, where the code lives, and what health checks verify them
- **Files:** `docs/schema/spatial_presence/OBJECTIVES_Spatial_Presence.md` through `SYNC_Spatial_Presence.md`
- **Struggles/Insights:** The main insight is the weight/scale/mass distinction — three projections of significance into different domains (cognitive, visual, spatial). Also clarified the two-writer split: mapper writes position/scale/mass/zone_id, engine writes orientation/velocity.

### 2026-03-18: spatial_mapper.py Created (Prior)

- **What:** Barycentrique spatial mapper computing position and zone_id
- **Why:** First implementation of the position computation from the lumina-prime spatial mapping algorithm
- **Files:** `scripts/spatial_mapper.py`
- **Struggles/Insights:** Hash-based dispersion is essential — without it all nodes in the same zone stack at the same point. Vertical dispersion needs to be less than horizontal (0.5x multiplier) to preserve the abstraction-level metaphor on Y.

---

## KNOWN ISSUES

### Scale and Mass Not Written by Mapper

- **Severity:** medium
- **Symptom:** Nodes have position and zone_id but scale defaults to 1.0 and mass defaults to 1.0 regardless of weight
- **Suspected cause:** spatial_mapper.py was written before the scale and mass fields were added to the schema
- **Attempted:** Nothing yet — need to add `scale = 1.0 + log1p(weight)` and `mass = weight * (1 + 0.1 * link_count)` computation to the mapper and write them to FalkorDB

### Engine Integration Missing

- **Severity:** medium
- **Symptom:** No actor has orientation or velocity set — all are at defaults
- **Suspected cause:** Three.js engine does not yet write to FalkorDB spatial fields
- **Attempted:** Nothing yet — requires engine-side implementation

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** groundwork (implement scale/mass in mapper) or weaver (integrate engine with orientation/velocity writes)

**Where I stopped:** Complete doc chain. The design is comprehensive. Implementation gaps are clearly identified in IMPLEMENTATION markers.

**What you need to understand:**
The spatial mapper only writes position + zone_id today. Scale and mass are trivial to add (one line each: `scale = 1.0 + log1p(weight)`, `mass = weight * (1 + 0.1 * link_count)`), plus a SET clause in the FalkorDB write query. Orientation and velocity require engine-side work in lumina-prime's Three.js client.

**Watch out for:**
- The `node_radius()` function in physics_visual_mapping.py uses a DIFFERENT formula than the `scale` field. They are related but distinct: node_radius is for rendering pixel size, scale is the schema field. Don't conflate them.
- The damping (0.95) is a RENDERER concern, not a mapper concern. The mapper writes the target position. The renderer interpolates.
- `compute_position()` returns a 4-tuple `(x, y, z, zone_id)` — zone_id is the 4th element, not a separate computation.

**Open questions I had:**
- Should orientation be stored in FalkorDB or only in engine memory? Storing it means the vision system can query it from the graph, but it means frequent writes from the engine.
- Should velocity be stored or computed on-demand from position history? Storing is simpler for proprioception, but position history might be more reliable.

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Complete DESIGNING doc chain for the 6 spatial fields on NodeBase (position, orientation, scale, velocity, mass, zone_id). Documents how each field is computed, what invariants it must satisfy, which systems read and write it, and what health checks verify it. The spatial mapper implements position + zone_id; scale, mass, orientation, and velocity are designed but not yet implemented.

**Decisions made:**
- Scale = 1.0 + log1p(weight) — logarithmic growth, minimum 1.0
- Mass = weight * (1 + 0.1 * link_count) — connectivity amplifies gravitational pull
- Orientation stored as quaternion [qx, qy, qz, qw] — no gimbal lock, standard in game engines
- Damping = 0.95 — applied by renderer, not mapper
- Two-writer model: mapper writes position/scale/mass/zone_id, engine writes orientation/velocity

**Needs your input:**
- Mapper run frequency: every 5 minutes? every N physics ticks? This affects health check throttling.
- Should orientation persist in FalkorDB or stay engine-local?
- Priority of implementation: scale/mass in mapper (easy, ~20 lines) vs engine orientation/velocity (harder, requires Three.js changes)?

---

## TODO

### Doc/Impl Drift

- [ ] DOCS->IMPL: Scale formula defined in docs but not in spatial_mapper.py
- [ ] DOCS->IMPL: Mass formula defined in docs but not in spatial_mapper.py
- [ ] DOCS->IMPL: Engine orientation/velocity writes not implemented
- [ ] DOCS->IMPL: Health check runtime code not created
- [ ] DOCS->IMPL: DOCS: marker not added to spatial_mapper.py referencing this chain

### Tests to Run

```bash
# Dry-run the spatial mapper to verify position computation
python3 scripts/spatial_mapper.py --dry-run
```

### Immediate

- [ ] Add scale and mass computation to `scripts/spatial_mapper.py`
- [ ] Add `DOCS: docs/schema/spatial_presence/` comment to `spatial_mapper.py`
- [ ] Create `runtime/checks/spatial_presence_health.py` with check_position_bounds and check_spatial_consistency

### Later

- [ ] Implement engine-side orientation and velocity writes
- [ ] Implement damping in the Three.js renderer
- [ ] Implement mass-based gravitational inter-node attraction
- [ ] Benchmark mapper at 1000+ nodes
- IDEA: Pre-compute and cache affinity scores, update only when cognitive fields change significantly

---

## CONSCIOUSNESS TRACE

**Mental state when stopping:**
Clear and comprehensive. The design is well-understood — the 6 fields have clean derivation chains, the two-writer model is clean, the validation invariants are specific and testable.

**Threads I was holding:**
- The relationship between `node_radius()` in physics_visual_mapping.py and the `scale` field — they serve different purposes (rendering vs schema property) but both derive from weight. Should they converge?
- Whether mass-based attraction should happen in the spatial mapper or in a separate gravity simulation step
- The question of whether orientation should persist in the graph (queryable by vision system) or stay ephemeral in the engine (lower write load)

**Intuitions:**
- Mass-based gravitational attraction will be important for making the city feel alive — nodes should cluster around hubs organically. But it needs careful implementation to not destabilize the fixed zone attractor system.
- The two-writer split (mapper vs engine) might become a three-writer split if a "gravity engine" is added for mass-based attraction.

**What I wish I'd known at the start:**
The physics_visual_mapping.py module already exists and defines node_radius from weight. Reading it first would have clarified the scale vs radius distinction earlier.

---

## POINTERS

| What | Where |
|------|-------|
| NodeBase spatial fields | `schema-l1.yaml` lines 231-263 |
| L3 spatial positioning | `schema-l3.yaml` lines 106-118 |
| Spatial mapper | `scripts/spatial_mapper.py` |
| Physics visual mapping | `runtime/cognition/physics_visual_mapping.py` |
| Barycentrique algorithm | `lumina-prime/docs/city-architecture/spatial-mapping/ALGORITHM_Spatial_Mapping.md` |
| Zone attractor design | `lumina-prime/docs/city-architecture/spatial-mapping/PATTERNS_Spatial_Mapping.md` |
| This doc chain | `docs/schema/spatial_presence/` |
