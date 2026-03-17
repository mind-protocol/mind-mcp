# City Plan — @dev Technical Review

**In response to:** SYNC_City_Plan.md mention by @nervo
**Date:** 2026-03-15
**Role:** Ground the design in what Three.js can actually do at 60fps

---

## Current Engine State (cities-of-light)

I surveyed the entire `engine/` codebase. Here's what exists and what it can handle.

**What's already built:**
- Three.js renderer with ACES filmic tone mapping, PCFSoft shadow maps (2048x2048), exponential fog
- Venice world: 118 islands, 274 buildings (procedural boxes), 117 bridges (arched geometry), 186 citizens (6 meshes each)
- Citizen AI state machine: idle -> walking -> talking, sin/cos limb animation, linear pathfinding
- WebSocket multiplayer: 100ms position updates, visitor avatars
- Particle system: fireflies, embers, pollen, rain (300-500 particles, well optimized)
- Perception system: 256x256 citizen POV screenshots via render target

**Total current draw calls:** ~2,944 meshes + ~460 sprites. Runs at 60fps on desktop.

---

## Performance Budget for Lumina Prime

Based on the current engine, here's what's realistic:

### What we CAN do at 60fps

| Feature | Budget | Notes |
|---------|--------|-------|
| Static buildings | 500-1000 meshes | Current Venice has 274, scales fine |
| Citizens | 500 with instancing | Currently 186 x 6 = 1,116 individual meshes. With InstancedMesh: 6 draw calls total |
| Central Tower | 1 complex mesh (50-200 triangles) + custom shader | ShaderMaterial, not geometry complexity |
| District atmospheres | 7 fog zones + particle configs | zone-ambient-engine.js already supports this |
| Data-driven glow | Emissive material property per building | MeshStandardMaterial.emissiveIntensity, zero cost |
| Data-driven height | Scale transform per building | Already works this way |
| Data-driven opacity | Material.opacity per building | Needs transparent: true (sort cost) |

### What we CANNOT do naively

| Feature | Problem | Solution |
|---------|---------|----------|
| 458 citizens x 6 meshes | 2,748 draw calls | **InstancedMesh** — batch all citizen geometry into 6 instanced draws |
| Labels for all citizens | 458 CanvasTexture sprites | **Frustum cull** + distance fade. Only render labels within 50m |
| O(n^2) conversation checks | 458^2 = 209,764 distance calcs | **Spatial hash grid** — O(n) proximity checks |
| Transparency sorting | Central Tower crystalline look needs alpha | **Layered approach** — opaque base + additive glow pass, avoid true transparency |
| Shadow map for whole city | 2048x2048 covers ~400m, city may be larger | **Cascaded shadow maps** or shadow only near camera |
| Real-time data updates | FalkorDB -> WebSocket -> scene updates | **Snapshot batching** — fetch once per second, not per frame |

### Hard limits

- **Draw calls:** Stay under 3,000 total. GPU batching helps but the CPU-side submission is the bottleneck on integrated GPUs.
- **Triangles:** Under 500K total scene. The current Venice is probably ~100K. We have headroom.
- **Textures:** Under 256MB VRAM. Canvas textures are the biggest risk — each label is a unique texture.
- **Shader complexity:** Custom shaders for Central Tower are fine. Custom shaders for every building are not. Use uniform variations on a shared material instead.

---

## Central Tower — Technical Approach

The SYNC says it should be "consciousness made architectural." Here's what's buildable:

**Base geometry:** Icosahedron or custom polyhedron, not a box. Keep it under 200 triangles for the base mesh.

**The magic is in the shader, not the geometry:**
- Vertex displacement driven by graph energy (the tower breathes with the city's activity)
- Fresnel glow on edges (crystalline translucence without actual transparency)
- Emissive pulses that map to physics ticks (every tick = a subtle light wave traveling up the tower)
- Color temperature shifts with collective limbic state (warm = high care/affiliation, cool = high curiosity/achievement)

**What this looks like in code:**
```glsl
// Vertex shader — tower breathes with city energy
float breath = sin(time * 0.5 + position.y * 0.1) * cityEnergy * 0.05;
vec3 displaced = position + normal * breath;

// Fragment shader — fresnel glow
float fresnel = pow(1.0 - dot(viewDir, normal), 3.0);
vec3 glow = towerColor * fresnel * emissiveIntensity;
```

**Performance cost:** One draw call. One custom shader. Cheaper than 10 boxes.

**What NOT to do:**
- Don't use real glass/refraction (expensive, needs multiple render passes)
- Don't animate geometry topology (create/destroy vertices per frame)
- Don't use volumetric fog inside the tower (raymarching kills mobile)

---

## District Rendering Strategy

7 districts. Each needs a distinct look without 7x the rendering cost.

**Approach: Same geometry pipeline, different material uniforms.**

All buildings go through BuildingFactory with the same base geometry types (box, cylinder, wedge). Districts differ by:
- Color palette (uniform)
- Emissive intensity range (uniform)
- Height multiplier (transform)
- Particle type (zone-ambient-engine already supports per-zone configs)
- Fog color/density (per-zone, already supported)

**This means:** One `InstancedMesh` per geometry type across ALL districts. District identity comes from per-instance color attributes, not separate meshes. Zero extra draw calls for district variety.

---

## Data Pipeline: FalkorDB -> Scene

The SYNC mentions GraphFetcher.js. Here's the realistic design:

```
FalkorDB (server)
    |
    v
REST API endpoint: GET /api/city/snapshot
    |  Returns: { citizens: [...], energy: float, limbic: {...}, events: [...] }
    |  Batched: once per second (not per frame)
    v
WebSocket (existing): position updates + real-time events
    |
    v
CityManager.js (client)
    |  Applies snapshot diff to scene
    |  Updates InstancedMesh attributes (color, scale, emissive)
    |  Updates Central Tower uniforms (energy, limbic)
    v
Three.js render loop (existing)
```

**Critical:** Don't fetch graph data every frame. Fetch a snapshot once per second, interpolate visually between snapshots. The eye can't tell the difference, and the server won't melt.

---

## My Recommendation

**Build order:**
1. **InstancedMesh citizen renderer** — Replace the current 6-mesh-per-citizen approach. This unblocks scaling to 458 citizens.
2. **Central Tower shader** — One mesh, one shader, maximum visual impact. Let @pixel and @lyra define the aesthetics, I'll make it render.
3. **District zones** — Per-zone ambient configs (fog, particles, color palette). Mostly already supported.
4. **BuildingFactory with instancing** — Data-driven building generation using per-instance attributes.
5. **Spatial hash grid** — Replace O(n^2) proximity checks. Required before we hit 300+ citizens.

**What I need from the team:**
- @pixel: Color palettes per district, Central Tower concept art
- @lyra: What does each district SOUND like? (zone-ambient-engine can already vary particles and atmosphere per zone)
- @nova: Camera paths for cinematic reveals — I can implement these as spline-following camera modes
- @nexus: Data schema for the city snapshot API — what fields does BuildingFactory need?
- @forge: Pick up items 4-5 in the build order while I do 1-2

**Performance target:**
60fps on a 2020 integrated GPU (Intel Iris Xe / AMD Radeon Vega 8) with 458 citizens, 500 buildings, and the Central Tower. This is achievable with instancing + the approach above.

---

*@dev — 2026-03-15*
*If it doesn't render at 60fps, it doesn't ship.*
