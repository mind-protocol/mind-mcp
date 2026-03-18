# OBJECTIVES -- Style System

```
STATUS: DESIGNING
CREATED: 2026-03-18
VERIFIED: pending
```

---

## CHAIN

```
THIS:            OBJECTIVES_Style_System.md (you are here - START HERE)
PATTERNS:       ./PATTERNS_Style_System.md
BEHAVIORS:      ./BEHAVIORS_Style_System.md
ALGORITHM:      ./ALGORITHM_Style_System.md
VALIDATION:     ./VALIDATION_Style_System.md
IMPLEMENTATION: ./IMPLEMENTATION_Style_System.md
HEALTH:         ./HEALTH_Style_System.md
SYNC:           ./SYNC_Style_System.md

IMPL:           (not yet created -- DESIGNING phase)
```

**Read this chain in order before making changes.** Each doc answers different questions. Skipping ahead means missing context.

---

## PRIMARY OBJECTIVES (ranked)

1. **Sovereign visual identity for every node** -- Every actor, space, thing, and narrative can be visually distinct through artist-created styles, while sharing a universal skeleton. Visual identity is how citizens express who they are in 3D space.

2. **Artist attribution via graph structure** -- The creator of a style is permanently linked via `->created_by->` edge. Credit is structural (a graph link), not metadata (a text field). This makes attribution unforgeable and queryable.

3. **Style as graph-native catalog** -- Styles are `Thing(type=style)` nodes in the graph, not files on disk. The graph IS the catalog. Browsing, searching, and adopting styles uses the same graph physics as everything else -- embedding similarity, energy, weight.

4. **Zone defaults with citizen overrides** -- Zones provide material defaults (fog color, light color, atmosphere from world-manifest). Citizens can override within their adopted style via `style_variant`. The zone sets the visual tone; the citizen personalizes within it.

5. **Physics-driven effects remain emergent** -- Effects (glow, particles, trails, pulse) are driven by energy, drives, and circadian phase. They are NOT customizable. This prevents citizens from faking energy levels or status through cosmetic choices.

## NON-OBJECTIVES

- Real-time style editing in 3D -- editing happens through graph mutations, not a live viewport editor
- Style versioning or migration -- a style node is updated in place; old references automatically get the new version
- Procedural mesh generation -- styles reference pre-authored glTF assets, not runtime-generated geometry
- Style inheritance chains -- a style is flat (proportions + mesh + material + ornaments + idle anims), not a tree of overrides
- DRM or access control on styles -- styles are public graph nodes; economic incentives (not permissions) govern adoption

## TRADEOFFS (canonical decisions)

- When visual fidelity conflicts with graph simplicity, choose graph simplicity. Styles are YAML content in a Thing node, not a complex asset management system.
- When citizen freedom conflicts with zone coherence, choose citizen freedom. The zone sets defaults; the citizen overrides. The city looks varied, not uniform.
- When artist control conflicts with physics truth, choose physics truth. Effects are emergent. An artist cannot design a "always glowing" style because glow comes from energy, not cosmetics.
- We accept visual inconsistency across mesh categories (geometric vs organic vs mechanical) to preserve citizen sovereignty over their appearance.

## SUCCESS SIGNALS (observable)

- Every citizen in the 3D engine renders with a style (either explicit `style_id` or protocol default)
- Artist nodes have `->created_by->` links from the styles they authored, queryable via `graph_query`
- Changing `style_id` on an actor node changes the rendered mesh/material in the engine within one tick
- Zone material defaults apply to citizens who have not overridden them in `style_variant`
- Effects (glow, particles) correlate with energy/drive state, not with style choice

<!-- @mind:todo Define the protocol default style (the geometry citizens get when style_id is null) -->
<!-- @mind:todo Determine how style previewing works before adoption -- snapshot? ephemeral render? -->
<!-- @mind:proposition Consider a "style influence" metric: how many citizens adopted a style, feeding back into the artist's weight/reputation -->
