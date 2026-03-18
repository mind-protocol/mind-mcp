# Custom Senses — Patterns: Graph-Native Perception Extensions

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Custom_Senses.md
THIS:            PATTERNS_Custom_Senses.md (you are here)
BEHAVIORS:       ./BEHAVIORS_Custom_Senses.md
ALGORITHM:       ./ALGORITHM_Custom_Senses.md
VALIDATION:      ./VALIDATION_Custom_Senses.md
HEALTH:          ./HEALTH_Custom_Senses.md
IMPLEMENTATION:  ./IMPLEMENTATION_Custom_Senses.md
SYNC:            ./SYNC_Custom_Senses.md

IMPL:            runtime/cognition/exteroception.py
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read runtime/cognition/exteroception.py

**After modifying this doc:**
1. Update the IMPL source file to match, OR
2. Add a TODO in SYNC_Custom_Senses.md: "Docs updated, implementation needs: {what}"

**After modifying the code:**
1. Update this doc chain to match, OR
2. Add a TODO in SYNC_Custom_Senses.md: "Implementation changed, docs need: {what}"

---

## THE PROBLEM

Citizens perceive the world through 6 hardcoded exteroception channels (new_message, new_mention, narrative_shift, new_thing, actor_nearby, space_atmosphere). These channels cover the most common perceptual needs, but they are fixed at development time. A citizen who wants to notice high-energy narratives about a specific topic, or detect when a particular actor's weight crosses a threshold, cannot do so without modifying engine code.

Without custom senses, perception is uniform — every citizen sees the world through the same 6 lenses. The system cannot evolve its own perceptual field. Citizens cannot specialize their awareness toward what matters to them, and they cannot share perceptual innovations with each other. This is a ceiling on cognitive diversity.

---

## THE PATTERN

**Thing-as-Sense: Graph-native sense definitions stored as Thing nodes, linked via `->perceives_with->`, evaluated as additional channels in the exteroception tick.**

The key insight is that a sense is just a filter definition stored in the graph. A `Thing(type=sense)` node contains a YAML document in its `content` field that describes what to scan, what conditions to match, and what stimulus to produce. When an Actor links to that Thing via `->perceives_with->`, the exteroception engine loads the definition and evaluates it alongside built-in channels. The sense becomes a first-class channel with its own priority, refractory period, and gating mechanics.

This is the same asset pattern used by styles (Thing(type=style)) and frequencies (Thing(type=frequency)): a reusable, shareable, creditable graph object that citizens create, adopt, and evolve. Creation produces a Thing node with `->created_by->` authorship. Adoption creates a `->perceives_with->` link. The graph tracks who invented the perception and who uses it.

Two tiers of complexity serve different needs. YAML senses are declarative filter definitions — specify a source node type, scan scope, filter conditions, keywords, and stimulus template. No code, no sandbox, fast evaluation. Python senses (v2, not yet implemented) would allow programmatic graph queries via a sandboxed `query_fn` for senses that need logic beyond simple filters.

---

## BEHAVIORS SUPPORTED

- B1: Sense loading from graph links — citizens get custom channels by linking to Thing(type=sense) nodes
- B2: Declarative filter evaluation — YAML conditions scan L3 nodes by field comparisons and keyword matching
- B3: Channel-gated stimulus production — custom senses fire through the same priority/refractory gating as built-in channels
- B4: Sense shareability — one sense definition adopted by many citizens via `->perceives_with->` links

## BEHAVIORS PREVENTED

- Bypassing the exteroception pipeline — custom senses produce candidates that go through the same MAX_STIMULI_PER_TICK gating as built-in channels
- Arbitrary code execution — YAML senses are parsed data, not executable code; Python senses (v2) would be sandboxed with query_fn only

---

## PRINCIPLES

### Principle 1: Graph-Native Over Configuration Files

Senses live in the graph as Thing nodes, not in YAML config files on disk. This means they are discoverable via graph queries, shareable via links, and subject to the same physics (energy, decay, weight) as every other node. A sense that nobody uses will decay. A sense that many citizens adopt will gain weight. The graph's physics naturally curate the perceptual ecosystem.

### Principle 2: Same Pipeline, Different Channels

Custom senses do not create a parallel perception path. They produce candidate stimuli that enter the same priority-sorted, refractory-gated pipeline as the 6 built-in channels. This guarantees that custom senses cannot flood a citizen's attention — they compete for the same MAX_STIMULI_PER_TICK slots. The channel abstraction (SensoryChannel) is reused without modification.

### Principle 3: Creation Produces Shareable Assets

The same economic pattern applies to senses, styles, and frequencies: a citizen creates a Thing node, the graph records authorship via `->created_by->`, other citizens adopt it via relationship links. The creation act produces a persistent, creditable asset that benefits the ecosystem. This is not a developer feature — it is a citizen capability.

---

## DATA

| Source | Type | Purpose / Description |
|--------|------|-----------------------|
| `runtime/cognition/exteroception.py` | FILE | Exteroception engine with custom sense loader and evaluator (~580 lines) |
| `schema-l1.yaml` (Custom Senses section) | FILE | Schema reference for Thing(type=sense) and YAML format specification |
| FalkorDB graph | DB | Thing(type=sense) nodes with YAML content, Actor->perceives_with->Thing links |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `runtime/cognition/exteroception.py` | Host engine — custom senses are evaluated within the exteroception tick |
| `schema-l1.yaml` | Defines the Thing(type=sense) schema and YAML format contract |
| `yaml` (PyYAML) | Parses YAML content from Thing node content fields |

---

## INSPIRATIONS

- **Biological sensory adaptation:** Organisms evolve new sensory organs over time — pit vipers evolved infrared pits, electric eels evolved electroreception. Custom senses let the citizen ecosystem evolve new perceptual modalities without developer intervention.
- **Style/frequency asset pattern:** The existing Thing(type=style) and Thing(type=frequency) pattern proved that graph-native, shareable, creditable assets work. Custom senses follow the same structure.
- **Unix philosophy of composable filters:** Each YAML sense is a declarative filter — specify what to look at, what conditions to match, what to produce. Simple, composable, no side effects.

---

## SCOPE

### In Scope

- YAML-format sense definitions stored in Thing(type=sense) content field
- Loading senses from `->perceives_with->` links during exteroception tick
- Evaluating filter conditions (comparison operators + keyword matching) against L3 nodes
- Registering custom senses as SensoryChannel instances with priority and refractory gating
- Producing stimulus candidates that compete in the standard exteroception pipeline
- Capping loaded senses at 10 per citizen (query LIMIT)

### Out of Scope

- Python-format programmatic senses (sandboxed query_fn) -> v2
- Sense marketplace or economic pricing -> layer above
- Push-based / event-driven senses -> v2
- Modifying built-in channels via custom senses -> not permitted
- Cross-citizen sense evaluation (evaluating sense on another citizen's behalf) -> not supported

---

## MARKERS

<!-- @mind:todo Define the Python (programmatic) sense tier — sandboxing strategy, query_fn interface, execution timeout -->
<!-- @mind:todo Document the sense refresh mechanism — currently senses are loaded once per engine lifetime, not refreshed on link changes -->
<!-- @mind:proposition Consider a sense validation step at creation time — reject YAML that references nonexistent fields or invalid operators -->
