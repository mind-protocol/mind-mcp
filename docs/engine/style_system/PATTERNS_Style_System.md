# Style System -- Patterns: Graph-Native Visual Customization Across All Node Types

```
STATUS: DESIGNING
CREATED: 2026-03-18
VERIFIED: pending
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Style_System.md
BEHAVIORS:       ./BEHAVIORS_Style_System.md
THIS:            PATTERNS_Style_System.md (you are here)
ALGORITHM:       ./ALGORITHM_Style_System.md
VALIDATION:      ./VALIDATION_Style_System.md
HEALTH:          ./HEALTH_Style_System.md
IMPLEMENTATION:  ./IMPLEMENTATION_Style_System.md
SYNC:            ./SYNC_Style_System.md

IMPL:            (not yet created -- DESIGNING phase)
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read the linked IMPL source file

**After modifying this doc:**
1. Update the IMPL source file to match, OR
2. Add a TODO in SYNC_Style_System.md: "Docs updated, implementation needs: {what}"

**After modifying the code:**
1. Update this doc chain to match, OR
2. Add a TODO in SYNC_Style_System.md: "Implementation changed, docs need: {what}"

---

## THE PROBLEM

Every node in the graph can be rendered in 3D. Without a style system, all actors look the same, all spaces look the same, all things look the same. Visual identity is flattened to zero.

Worse: without structural attribution, there is no way to credit the artists who create visual assets. Metadata fields ("created_by": "alice") are fragile -- they can be overwritten, they do not participate in graph physics, and they cannot be traversed.

Without zone defaults, every citizen must manually configure material properties or they render with hardcoded fallbacks. Without the effects/style separation, citizens could cosmetically fake energy states, breaking the visual language that communicates physics truth.

---

## THE PATTERN

**Skeleton is universal, style is sovereign, effects are physics.**

The system decomposes visual appearance into 6 layers with clear ownership:

| Layer | Owner | Mutable by Citizen | Source of Truth |
|-------|-------|-------------------|-----------------|
| Skeleton | Protocol | No | `citizen_body_model.yaml` (39 joints, 89 DOF) |
| Proportions | Artist | Yes (adopt style) | `Thing(type=style).content.proportions` |
| Mesh | Artist | Yes (adopt style) | `Thing(type=style).media.geometry.uri` (glTF) |
| Material | Artist + Zone | Yes (override via `style_variant`) | `Thing(type=style).content.material` + zone YAML defaults |
| Ornaments | Social class + Citizen | Yes (toggle via `style_variant`) | `world-manifest.json` social_class_styles + citizen choice |
| Idle animations | Artist + Drives | Yes (adopt style) | `Thing(type=style).content.animations_idle` + drive modulation |
| Effects | Drives + Energy | No | Physics state (energy, drives, circadian phase) |

The key insight: **the graph IS the catalog**. Styles are not files in a directory -- they are `Thing(type=style)` nodes with content, media, and `->created_by->` links to artist actors. Adopting a style means setting `style_id` on your node. Browsing styles means querying the graph. The same physics that governs memory and relationships governs the style marketplace.

---

## BEHAVIORS SUPPORTED

- **B1: Style adoption changes visual appearance** -- the pattern enables this by making `style_id` a field on NodeBase, resolved at render time to the Thing node's assets
- **B2: Artist credit is structural** -- the `->created_by->` link from Thing(type=style) to Actor(artist) is a first-class graph edge, traversable and weighted
- **B3: Zone defaults cascade** -- material properties fall back to zone YAML when not overridden, because the resolution algorithm checks `style_variant` -> style content -> zone defaults
- **B4: Effects reflect physics truth** -- effects layer is owned by drives+energy with `mutable: false`, preventing cosmetic faking

## BEHAVIORS PREVENTED

- **A1: Faking energy state via cosmetics** -- the effects layer is not customizable; glow, particles, and trails are computed from physics, never from style choice
- **A2: Uncredited style creation** -- every Thing(type=style) must have a `->created_by->` link; styles without artist attribution are structurally incomplete
- **A3: Style lock-in** -- adoption is reversible; `style_id` is a mutable field, not a permanent binding

---

## PRINCIPLES

### Principle 1: Skeleton is Universal, Style is Sovereign

The 39-joint, 89-DOF skeleton is protocol-level infrastructure. It never changes per citizen. All style variation happens in the layers ABOVE the skeleton: proportions, mesh, material, ornaments, animations. This means any style works on any citizen -- the skeleton is the universal interface contract.

This matters because it prevents fragmentation. If skeletons varied per style, animations would break, IK would need per-style calibration, and the physics bridge would need per-style logic. Universality at the skeleton level makes everything above it interchangeable.

### Principle 2: The Graph IS the Catalog

Styles are nodes. Browsing is querying. Adoption is a field update. Attribution is a link. There is no separate "style store" or "asset database" -- the same graph that holds memories, relationships, and narratives also holds visual styles.

This matters because it means styles participate in graph physics. A popular style gains weight through activation. An artist's reputation grows through the links from their styles. Style discovery can use embedding similarity -- "find styles similar to this one" is a cosine query, not a file search.

### Principle 3: Effects Are Physics, Not Fashion

Glow, particles, trails, and pulse are computed from energy level, drive state, and circadian phase. They cannot be customized, overridden, or faked. When you see a citizen glowing, you know their energy is above 0.3. When you see sparkle particles, you know their novelty hunger is high.

This matters because it preserves the visual language of the city. Effects are information -- they communicate internal state to observers. If effects were customizable, the visual language would become noise, and citizens could not read each other's state at a glance.

### Principle 4: Credit via Link, Not Metadata

Artist attribution is a `->created_by->` graph link, not a `creator` text field on the style node. Links participate in physics: they carry weight, energy, trust. A text field is inert data. The link means the artist's reputation is structurally connected to their work.

This matters for the eventual marketplace. When $MIND flows from style adoption, it flows along the `->created_by->` link. The graph structure IS the payment rail.

### Principle 5: Zone Defaults, Citizen Overrides

Zone YAML defines default material properties (colors, metalness, roughness). Citizens inherit these unless they override via `style_variant`. This creates visual coherence within districts while preserving individual expression.

This matters because it makes the city readable. The Arsenal district has warm copper tones. The Towers of Knowledge have cool blue light. A citizen in the Arsenal who overrides to bright green is making a visible statement -- they are choosing to stand out from their zone's palette.

---

## DATA

| Source | Type | Purpose / Description |
|--------|------|-----------------------|
| `citizen_body_model.yaml` | FILE | Skeleton definition (39 joints, 89 DOF) and style_system section with layer definitions |
| `schema-l1.yaml` | FILE | NodeBase fields: `style_id` and `style_variant` definitions |
| `world-manifest.json` | FILE | `avatar.social_class_styles` mapping (Architect->crystal, Builder->gear, etc.) and zone atmosphere |
| `Thing(type=style)` nodes | GRAPH | Style definitions: content (YAML with proportions, material, ornaments), media.geometry.uri (glTF mesh) |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `schema-l1.yaml` (NodeBase) | `style_id` and `style_variant` fields live on NodeBase -- every node can have a style |
| `citizen_body_model.yaml` (skeleton) | The skeleton defines the universal bone structure that all meshes must skin to |
| `world-manifest.json` (zones) | Zone atmosphere and `social_class_styles` provide default materials and ornament mappings |
| Graph engine (FalkorDB) | Style nodes are Thing nodes in the graph; adoption is a field update via graph_write |
| 3D engine (Three.js) | The renderer must resolve `style_id` -> Thing node -> glTF mesh -> skinned render |

---

## INSPIRATIONS

- **VRChat avatar system**: Universal humanoid skeleton (75-150 bones) with artist-created meshes skinned to it. Proved that a single skeleton can support radical visual diversity.
- **Minecraft skin system**: Simple layer-based customization (base texture + overlay) with user-created content. Showed that a flat customization model (not inheritance trees) scales to millions of users.
- **NFT metadata standards (ERC-721)**: On-chain metadata with off-chain asset URIs. The pattern of "identity on-chain, asset off-chain" maps to "style_id in graph, glTF in object storage."
- **CSS cascade**: Zone defaults -> style definitions -> citizen overrides mirrors the cascade: user-agent -> author -> inline. The resolution order is the same concept.

---

## SCOPE

### In Scope

- `Thing(type=style)` node schema: what fields content must have, what media modalities are used
- `->created_by->` link semantics: what this link means, how it is created
- `style_id` resolution: how the engine resolves a style_id to renderable assets
- `style_variant` override semantics: what fields can be overridden, how overrides merge with style defaults
- Zone material defaults: how zones provide fallback materials
- Ornament mapping: how social_class_styles from world-manifest map to ornament types
- Idle animation modulation: how drives alter idle animation parameters
- Applicability to ALL node types: actors, spaces, things, narratives

### Out of Scope

- **Skeleton design** -> see: `citizen_body_model.yaml` -- the skeleton is defined there, not here
- **Physics-driven effects** -> see: physics tick / drives -- effects are computed from energy/drives, not from styles
- **3D rendering pipeline** -> see: engine/renderer -- how Three.js actually renders a skinned mesh is renderer business
- **$MIND marketplace economics** -> see: economy module (v2) -- how adoption generates $MIND flow is future scope
- **Animation system** -> see: engine/animation -- how IK, procedural walk, and gestures work is animation business; we only define idle animation data in styles
- **Asset pipeline** -> see: content creation tooling -- how artists author glTF files, validate bone weights, and upload to S3 is tooling, not the style system itself

---

## MARKERS

<!-- @mind:todo Define Thing(type=style) content YAML schema with all required fields -->
<!-- @mind:todo Specify how style_variant overrides merge with style content defaults -->
<!-- @mind:todo Decide whether spaces/things/narratives use the same style_id mechanism or a simplified version -->
<!-- @mind:proposition Style popularity as a graph metric: adoption count -> weight on the style Thing node, feeding into artist reputation -->
<!-- @mind:proposition Style "families" via embedding similarity -- styles that look alike cluster naturally in the graph -->
<!-- @mind:escalation How do we handle style asset hosting? S3 bucket owned by protocol? Artist-provided URIs? Need infra decision. -->
