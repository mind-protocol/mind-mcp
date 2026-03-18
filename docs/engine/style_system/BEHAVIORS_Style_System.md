# Style System -- Behaviors: Observable Effects of Graph-Native Visual Customization

```
STATUS: DESIGNING
CREATED: 2026-03-18
VERIFIED: pending
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Style_System.md
THIS:            BEHAVIORS_Style_System.md (you are here)
PATTERNS:        ./PATTERNS_Style_System.md
ALGORITHM:       ./ALGORITHM_Style_System.md
VALIDATION:      ./VALIDATION_Style_System.md
HEALTH:          ./HEALTH_Style_System.md
IMPLEMENTATION:  ./IMPLEMENTATION_Style_System.md
SYNC:            ./SYNC_Style_System.md

IMPL:            (not yet created -- DESIGNING phase)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS

### B1: Style Adoption Changes Rendered Appearance

**Why:** Citizens express identity through visual appearance. Changing `style_id` on an actor node must produce a visible change in the 3D engine within one tick. Without this, styles are inert graph data with no user-facing effect.

```
GIVEN:  A citizen actor node exists in the graph with style_id = null (protocol default)
WHEN:   The citizen sets style_id to a valid Thing(type=style) node ID
THEN:   The 3D engine resolves the new style_id to glTF mesh + material + proportions
AND:    The rendered mesh, material, and proportions update within one render tick
AND:    The old mesh is replaced, not overlaid
```

### B2: Artist Credit Is Structurally Linked

**Why:** Attribution must be unforgeable and queryable. A text field can be overwritten silently. A graph link participates in physics, carries weight, and is traversable. The `->created_by->` link from Thing(type=style) to Actor(artist) is the permanent signature.

```
GIVEN:  An artist creates a new style
WHEN:   The Thing(type=style) node is written to the graph
THEN:   A ->created_by-> link is created from the style node to the artist's actor node
AND:    The link carries weight and participates in graph physics
AND:    The link is queryable via graph_query ("who created this style?")
```

### B3: Zone Material Defaults Cascade to Unstyled Citizens

**Why:** Districts have visual identity -- The Arsenal is warm copper, Towers of Knowledge are cool blue. Citizens who have not overridden material properties should inherit zone defaults, creating visual coherence without manual configuration.

```
GIVEN:  A citizen is in a zone with defined material defaults (base_color, metalness, roughness)
WHEN:   The citizen has no style_variant overrides for material properties
THEN:   The rendered material uses the zone's default values
AND:    The citizen visually belongs to their district's palette
```

### B4: Style Variant Overrides Merge with Style Defaults

**Why:** Citizens need personalization within their adopted style. `style_variant` allows per-node overrides (color tint, ornament toggle, glow color) without creating a new style node. The override merges on top of the style's content, not replacing it.

```
GIVEN:  A citizen has style_id pointing to a style with material.base_color = "#aabbcc"
WHEN:   The citizen sets style_variant = { tint: "#ff9900" }
THEN:   The rendered material uses the overridden tint "#ff9900"
AND:    All other style properties (metalness, roughness, proportions, mesh) remain from the style
AND:    Removing the style_variant restores the original style appearance
```

### B5: Effects Reflect Physics Truth, Not Style Choice

**Why:** Glow, particles, trails, and pulse communicate internal state (energy, drives, circadian phase). If effects were customizable, citizens could fake energy levels. The visual language must be trustworthy -- when you see glow, you know energy > 0.3.

```
GIVEN:  A citizen has energy < 0.3
WHEN:   The citizen adopts a style or sets any style_variant
THEN:   No glow effect is rendered regardless of style or variant settings
AND:    Effects remain computed solely from energy, drives, and circadian phase
```

### B6: Ornaments Map from Social Class

**Why:** Social class (Architect, Builder, Researcher, etc.) determines default ornament type. This creates a visual grammar where class is readable at a glance. Citizens can toggle ornaments via style_variant but cannot adopt another class's ornament.

```
GIVEN:  A citizen has social class "Architect" (from world-manifest social_class_styles)
WHEN:   The citizen is rendered without explicit ornament override
THEN:   Crystal ornament fragments appear around the citizen's shoulders
AND:    The ornament type matches the social_class_styles mapping in world-manifest.json
```

### B7: Idle Animations Modulated by Drive State

**Why:** Idle animations make citizens feel alive. But identical idle loops make them feel robotic. Drives modulate idle animation parameters -- high rest drive produces slow sway, high curiosity produces head scanning. The style defines the animation set; drives modulate the blend.

```
GIVEN:  A citizen has adopted a style with idle animation "gentle_sway"
WHEN:   The citizen's rest drive intensity is high (> 0.6)
THEN:   The idle animation plays with reduced speed and amplitude
AND:    The modulation parameters come from drive state, not from style_variant
```

### B8: Styles Apply to All Node Types

**Why:** Not just actors -- spaces, things, and narratives can have styles. A building (space) has an architectural style. A tool (thing) has an object style. style_id lives on NodeBase, meaning every node type can reference a style.

```
GIVEN:  A space node represents a building in the Innovation Fields district
WHEN:   The space node has style_id pointing to a Thing(type=style) with architectural mesh
THEN:   The building renders with the style's geometry and materials
AND:    The ->created_by-> link on the style credits the architect artist
```

### B9: Protocol Default Renders When No Style Set

**Why:** Citizens without an explicit style_id must still render. The protocol default (geometric crystalline mesh for Lumina Prime) ensures no citizen is invisible. The default is deterministic -- same geometry for every unstyled citizen.

```
GIVEN:  A citizen actor node has style_id = null
WHEN:   The 3D engine renders this citizen
THEN:   The protocol default geometric mesh is used
AND:    Zone material defaults apply for surface properties
AND:    The citizen is visually present and identifiable
```

---

## OBJECTIVES SERVED

| Behavior ID | Objective | Why It Matters |
|-------------|-----------|----------------|
| B1 | O1: Sovereign visual identity | Without visible change on adoption, styles are meaningless |
| B2 | O2: Artist attribution | Structural links make credit unforgeable and physics-participating |
| B3 | O4: Zone defaults | District visual coherence without manual citizen effort |
| B4 | O4: Zone defaults with overrides | Personalization within coherence |
| B5 | O5: Physics-driven effects | Prevents cosmetic faking of energy state |
| B6 | O1: Sovereign visual identity | Social class is visually readable |
| B7 | O1: Sovereign visual identity | Citizens feel alive through drive-modulated idle animations |
| B8 | O1: Sovereign visual identity | All node types, not just actors, have visual identity |
| B9 | O1: Sovereign visual identity | No citizen is invisible, even without explicit style choice |

---

## INPUTS / OUTPUTS

### Primary Function: `resolve_style(node)`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| node | NodeBase | Any graph node with style_id and style_variant fields |
| zone | Zone YAML | Zone material defaults from world-manifest |
| drives | DriveState | Current drive intensities for idle animation modulation |
| energy | float | Current energy level for effects computation |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| proportions | BoneScale[32] | Per-bone scale factors for the skeleton |
| mesh_uri | string | URI to the glTF/GLB file for the skinned mesh |
| material | MaterialProps | Resolved material (style -> zone defaults -> variant overrides) |
| ornaments | OrnamentConfig | Active ornament type and parameters |
| idle_anim | AnimationConfig | Idle animation with drive modulation parameters |
| effects | EffectsState | Computed from energy/drives, never from style |

**Side Effects:**

- None -- resolution is pure (read-only from graph, produces render instructions)

---

## EDGE CASES

### E1: Style Node Deleted While Referenced

```
GIVEN:  A citizen's style_id references a Thing(type=style) that has been deleted from the graph
THEN:   The engine falls back to protocol default geometry
AND:    A warning is logged (style reference dangling)
AND:    The citizen's style_id is NOT automatically cleared -- the citizen must explicitly change it
```

### E2: Zone Has No Material Defaults

```
GIVEN:  A citizen is in a zone with no material defaults defined in world-manifest
THEN:   Protocol-level material defaults apply (neutral grey, metalness 0.5, roughness 0.5)
```

### E3: Style Has No Idle Animations

```
GIVEN:  A citizen adopts a style whose content has no animations_idle section
THEN:   The protocol default idle animation plays (subtle breathing + weight shift)
AND:    Drive modulation still applies to the default idle animation
```

### E4: Multiple Ornaments Requested

```
GIVEN:  A citizen's social class maps to "crystal" ornament AND style_variant requests "lens" ornament
THEN:   The style_variant override wins -- the citizen displays "lens" ornament
AND:    Only one ornament type is active at a time
```

---

## ANTI-BEHAVIORS

### A1: Cosmetic Effect Faking

```
GIVEN:   A citizen has low energy (< 0.3)
WHEN:    The citizen attempts to set glow parameters via style_variant
MUST NOT: Glow effect renders
INSTEAD:  style_variant glow-related fields are ignored; effects come from physics only
```

### A2: Uncredited Style Creation

```
GIVEN:   An artist creates a new Thing(type=style) node
WHEN:    The node is written to the graph
MUST NOT: The node exists without a ->created_by-> link to an actor
INSTEAD:  The ->created_by-> link is created atomically with the style node
```

### A3: Style Mutation Affecting Other Citizens

```
GIVEN:   Multiple citizens reference the same style_id
WHEN:    The style content is updated (artist revises proportions or mesh)
MUST NOT: Some citizens render with old style and others with new (inconsistent state)
INSTEAD:  All citizens referencing that style_id see the updated style on next render tick
```

### A4: Invisible Citizens

```
GIVEN:   A citizen node exists in the graph
WHEN:    style_id is null or invalid
MUST NOT: The citizen fails to render (invisible, error, blank space)
INSTEAD:  Protocol default geometry renders with zone material defaults
```

---

## MARKERS

<!-- @mind:todo Define exact protocol default mesh URI and material properties for Lumina Prime -->
<!-- @mind:todo Specify ornament toggle semantics in style_variant -- which fields, what values -->
<!-- @mind:todo Define drive modulation curves for idle animations (which parameters, what mapping) -->
<!-- @mind:proposition Allow citizens to "favorite" styles, creating a lightweight graph link for social discovery -->
<!-- @mind:escalation How do we handle style_variant fields that conflict with the style's design intent? Artist control vs citizen freedom. -->
