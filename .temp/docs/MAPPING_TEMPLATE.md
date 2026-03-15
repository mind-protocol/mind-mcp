# MAPPING: {Project_Name}

<!-- STATUS: DRAFT | REVIEW | STABLE -->
<!-- CREATED: YYYY-MM-DD -->
<!-- UPDATED: YYYY-MM-DD -->

## PURPOSE

Translates TAXONOMY terms to the mind universal schema (schema.yaml v2.2).
Referenced by all modules that create or query graph nodes and links.

---

## MIND UNIVERSAL SCHEMA

**Fixed. Non-negotiable. Modules map to this — they don't extend it.**

### Node types (enum — 5 values)

| Type | Role | Behavior |
|------|------|----------|
| actor | Pump | Injects energy via moments. Citizens, humans, services. |
| moment | Router + Branch Point | Events, interactions, episodes. Receives energy, triggers cascades. |
| narrative | Attractor | Stories, values, processes, desires. Created by crystallization or seeded. |
| space | Context container | Bidirectional flow with contents. Channels, worlds, rooms. |
| thing | Fast passthrough | Entities, tools, abstractions. Receives briefly, tends toward 0. |

### Cognitive types (L1 only — 7 values mapping to 5 universal)

| Cognitive type | Universal type | type field | Description |
|----------------|---------------|------------|-------------|
| memory | moment | null | Remembered content tied to experience |
| concept | thing | null | Notion, entity, person, tool, abstraction |
| narrative | narrative | null | Interpretive story about world or self |
| value | narrative | "value" | Deep preference, principle, style |
| process | narrative | "process" | Routine, habit, procedure |
| desire | narrative | "desire" | Internal attractor, want, tension |
| state | actor | null | Current affective/cognitive/functional state |

### Link type: one — `link`

All semantics in properties. Never stored as verbs — computed from dimensions.

### Backend notes

- **FalkorDB:** `node_type` is a field on each node
- **Neo4j:** `node_type` is a label (e.g., `:Actor`, `:Moment`)

### Why no custom fields

- Mind never does Cypher queries for content — all retrieval is embedding-based
- Everything searchable goes in `synthesis` (embedded summary)
- Everything detailed goes in `content` (full prose)
- The schema is the physics substrate — changing it changes the laws

---

## NODE MAPPINGS

| Domain term | Maps to | Synthesis template | Content includes | Example |
|-------------|---------|-------------------|------------------|---------|
| {domain_term} | node_type: {type}, cognitive_type: {type or N/A}, type: "{field value or null}" | "{synthesis pattern}" | {what goes in content} | {concrete example} |

## LINK MAPPINGS

| Domain relationship | Key dimensions | Synthesis template |
|--------------------|----------------|-------------------|
| {relationship} | polarity: [{a→b}, {b→a}], hierarchy: {val}, permanence: {val}, trust: {val}, friction: {val}, affinity: {val}, aversion: {val} | "{synthesis pattern}" |

### L1 relation_kind mapping

| Domain relationship | relation_kind | Activation gain | Typical dimensions |
|--------------------|---------------|-----------------|-------------------|
| {relationship} | {one of 14 kinds or null} | {>1 for supports, <0 for conflicts_with, etc.} | {primary dimensions} |

## L3 RULES (NON-NEGOTIABLE)

These are hard constraints from schema.yaml. Violating them breaks the system.

1. **No custom node types** — 5 types only. Map everything to actor/moment/narrative/space/thing.
2. **relation_kind is ALWAYS null at L3** — link semantics emerge from math, not from labels.
3. **space_type is free text, optional, NEVER filtered** — no taxonomy, no algorithmic branching.
4. **No emotions at L3** — Plutchik axes always 0.0 at universe level. Limbic is L1 only.
5. **Trust on links only, NEVER on nodes** — reputation is computed, never stored.
6. **Link semantics are computed from dimensions** — verbs are never stored.

## COMMON PATTERNS

| Pattern | Node type | Typical synthesis | Typical links |
|---------|-----------|------------------|---------------|
| Documentation → | narrative | "{doc type}: {title}" | contains (hierarchy: -0.7) |
| Code directory → | space | "{AREA/MODULE}: {name}" | contains (hierarchy: -0.7) |
| Source file → | thing | "{first docstring or heading}" | imports (hierarchy: 0.3) |
| Citizen → | actor | "{role}: {name}" | creates, collaborates |
| Event → | moment | "{event description}" | triggers, follows |

<!-- @mind:TODO — -->
<!-- @mind:proposition — -->
<!-- @mind:escalation — -->
