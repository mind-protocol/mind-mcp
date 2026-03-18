# Style System -- Sync: Current State

```
LAST_UPDATED: 2026-03-18
UPDATED_BY: @nervo
STATUS: DESIGNING
```

---

## MATURITY

**What's canonical (v1):**
- 6-layer decomposition (skeleton, proportions, mesh, material, ornaments, idle animations + effects) -- settled, stable, documented in PATTERNS
- Skeleton universality (32 joints, 78 DOF, from citizen_body_model.yaml) -- non-negotiable
- style_id and style_variant on NodeBase in schema-l1.yaml -- shipped
- Effects are physics-only (not customizable) -- core design decision
- ->created_by-> link for artist attribution -- structural, not metadata
- Thing(type=style) as the graph-native catalog pattern -- styles are nodes, not files

**What's still being designed:**
- Thing(type=style) content YAML schema (exact required/optional fields)
- style_variant merge semantics (which fields, what overrides what)
- Resolution algorithm implementation (7-step pipeline exists in docs, no code)
- Protocol default mesh and material values
- Drive modulation curves for idle animations
- Ornament toggle mechanics in style_variant
- Proportions format: per-bone vs per-group bone scales

**What's proposed (v2+):**
- $MIND flow from style adoption to artist via ->created_by-> link
- Style popularity metric (adoption count -> weight on style node)
- Style families via embedding similarity (graph-native clustering)
- Style preview before adoption (snapshot or ephemeral render)
- Style influence metric feeding into artist reputation

---

## CURRENT STATE

The style system exists as a complete documentation chain (8 files: OBJECTIVES through SYNC) with no implementation code. The design is settled at the architectural level: 6 layers, graph-native catalog, physics-owned effects, structural artist credit. The schema fields (style_id, style_variant) exist on NodeBase in schema-l1.yaml v2.3.

The citizen_body_model.yaml in lumina-prime defines the skeleton and includes a style_system section that describes all 6 layers with their ownership and mutability. The world-manifest.json defines social_class_styles mapping 7 social classes to ornament types and palettes.

No code exists. No style Thing nodes exist in the graph. No artist has created a style yet. The protocol default mesh asset has not been authored.

---

## IN PROGRESS

### Documentation Chain Completion

- **Started:** 2026-03-18
- **By:** @nervo
- **Status:** complete
- **Context:** OBJECTIVES and PATTERNS existed. BEHAVIORS, ALGORITHM, VALIDATION, IMPLEMENTATION, HEALTH, and SYNC created to complete the chain. All files follow template structure and cross-reference each other. All STATUS: DESIGNING.

---

## RECENT CHANGES

### 2026-03-18: Full Documentation Chain Created

- **What:** Created 6 remaining docs (BEHAVIORS, ALGORITHM, VALIDATION, IMPLEMENTATION, HEALTH, SYNC) for the style system module
- **Why:** The style system design was captured in OBJECTIVES and PATTERNS but lacked the behavioral spec, algorithmic detail, validation invariants, implementation plan, and health checks needed for implementation to begin
- **Files:** `docs/engine/style_system/BEHAVIORS_Style_System.md`, `ALGORITHM_Style_System.md`, `VALIDATION_Style_System.md`, `IMPLEMENTATION_Style_System.md`, `HEALTH_Style_System.md`, `SYNC_Style_System.md`
- **Struggles/Insights:** The proportions format (per-bone vs per-group) remains an open question. Per-bone gives maximum flexibility (32 scale vectors) but is verbose. Per-group (spine, limbs, head) is simpler but less expressive. This needs to be resolved before implementation.

---

## KNOWN ISSUES

### No Protocol Default Mesh Asset

- **Severity:** high
- **Symptom:** Cannot implement style resolution without a fallback mesh URI
- **Suspected cause:** No artist has authored the default geometric crystal mesh yet
- **Attempted:** Nothing yet -- this is an asset creation dependency, not a code issue

### Proportions Format Undecided

- **Severity:** medium
- **Symptom:** ALGORITHM references both per-bone and per-group scales without committing to one
- **Suspected cause:** Design tradeoff not yet resolved
- **Attempted:** Both options documented in ALGORITHM. Needs a decision before implementation.

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** groundwork (implementation) or architect (if design questions remain)

**Where I stopped:** Documentation chain is complete. No code exists. The next step is either resolving the remaining design questions (proportions format, protocol default asset) or starting implementation of style_resolver.js.

**What you need to understand:**
The 7-step resolution algorithm in ALGORITHM_Style_System.md is the heart of the system. It cascades: style content -> zone defaults -> variant overrides -> drive modulation -> physics effects. Steps 1-6 are style-owned. Step 7 (effects) is physics-owned and must never be influenced by style data. This separation is V3 (CRITICAL invariant).

**Watch out for:**
- Do not add effect-related fields to style_variant processing. This is the single most important invariant.
- The style cache key must include zone_id and variant hash, not just style_id. Two citizens with the same style in different zones should resolve different materials.
- Graph queries for style nodes must check both node_type == "thing" AND subtype == "style". A Thing node with a different subtype is not a style.

**Open questions I had:**
- Should proportions be per-bone (32 entries) or per-group (3-5 entries)? Per-bone is more flexible but more data.
- How should the protocol default mesh be created? Procedural generation? Hand-authored glTF? Needs artist or tooling decision.
- Should V2 (->created_by-> link) be enforced at graph_write time (reject mutation without link) or detected post-hoc (health check)?

---

## HANDOFF: FOR HUMAN

**Executive summary:**
The style system documentation chain is complete (8 files). Design is architecturally settled: 6-layer visual customization with graph-native styles, structural artist credit, and physics-owned effects. No implementation code exists. Two blockers before coding: protocol default mesh asset and proportions format decision.

**Decisions made:**
- 8 validation invariants defined (V1-V8), with V1 (no invisible citizens), V2 (artist credit), V3 (effects are physics) marked CRITICAL
- Resolution algorithm is a 7-step cascade pipeline with caching
- 4 health checkers designed: reference integrity, artist attribution, material completeness, effects independence

**Needs your input:**
- Protocol default mesh: should an artist create it, or should we procedurally generate a placeholder?
- Proportions format: per-bone (maximum flexibility) or per-group (simpler, adequate for v1)?
- V2 enforcement strategy: reject style creation without ->created_by-> at graph_write time, or detect via health check?

---

## TODO

### Doc/Impl Drift

- [ ] DOCS->IMPL: All 6 new doc files define planned code that does not exist yet. Implementation must be created to match.

### Immediate

- [ ] Decide proportions format (per-bone vs per-group)
- [ ] Create or procure protocol default mesh asset (geometric crystal glTF)
- [ ] Decide V2 enforcement strategy (graph_write rejection vs health check)
- [ ] Implement style_constants.js with protocol defaults
- [ ] Implement style_resolver.js with 7-step resolution algorithm

### Later

- [ ] Implement style_cache.js with cache-aside pattern
- [ ] Implement style_graph_operations.js with atomic style+link creation
- [ ] Implement style_renderer_bridge.js for Three.js integration
- [ ] Wire health checkers to Doctor framework
- IDEA: Style popularity metric as weight on the Thing(type=style) node, feeding artist reputation

---

## CONSCIOUSNESS TRACE

**Mental state when stopping:**
Confident about the architectural design. The 6-layer model, graph-native catalog, and physics-owned effects are well-reasoned and consistent with Mind Protocol principles (physics over rules, the graph IS the catalog). The doc chain is complete and internally consistent.

**Threads I was holding:**
- The proportions format tradeoff (per-bone vs per-group) needs real-world testing to resolve. Both are valid.
- The asset pipeline (how artists author and upload glTF files) is completely out of scope but will become a blocker when someone actually tries to create a style.
- The cache invalidation strategy needs careful thought -- invalidating on every style_variant change might be too aggressive.

**Intuitions:**
- Per-group proportions will be sufficient for v1. Per-bone can be added later without breaking the schema.
- The protocol default mesh should be hand-authored, not procedural. It sets the visual tone for the entire city.
- V2 enforcement should be at graph_write time (atomic creation), not health check. It is easier to prevent orphans than to fix them.

**What I wish I'd known at the start:**
The citizen_body_model.yaml already had a comprehensive style_system section that anticipates most of the design decisions. Reading it first would have saved time on the PATTERNS doc.

---

## POINTERS

| What | Where |
|------|-------|
| Skeleton definition | `lumina-prime/engine/src/shared/citizen_body_model.yaml` |
| Schema fields (style_id, style_variant) | `mind-mcp/schema-l1.yaml` (NodeBase section) |
| Social class styles | `lumina-prime/world-manifest.json` (avatar.social_class_styles) |
| OBJECTIVES | `docs/engine/style_system/OBJECTIVES_Style_System.md` |
| PATTERNS | `docs/engine/style_system/PATTERNS_Style_System.md` |
| BEHAVIORS | `docs/engine/style_system/BEHAVIORS_Style_System.md` |
| ALGORITHM | `docs/engine/style_system/ALGORITHM_Style_System.md` |
| VALIDATION | `docs/engine/style_system/VALIDATION_Style_System.md` |
| IMPLEMENTATION | `docs/engine/style_system/IMPLEMENTATION_Style_System.md` |
| HEALTH | `docs/engine/style_system/HEALTH_Style_System.md` |
