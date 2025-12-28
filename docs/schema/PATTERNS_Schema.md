# Schema Design Patterns

```
STATUS: CANONICAL
UPDATED: 2025-12-26
VERSION: v1.6.1 (sibling awareness + continuous crystallization)
```

## Core Philosophy

**Minimal, extensible, project-agnostic.**

The schema defines the graph structure that all mind projects share. It is NOT a game schema or a dev-tool schema — it's the foundation both inherit from.

## Key Decisions

### 1. Five Node Types (Constrained)

```
node_type: actor | space | thing | narrative | moment
```

These five categories cover all graph entities:
- **actor** — anything that can act (human, agent, NPC, system)
- **space** — containers and locations (folder, module, city, room)
- **thing** — objects that can be referenced/possessed (file, weapon, document)
- **narrative** — stories and knowledge about nodes (pattern, memory, oath)
- **moment** — temporal events (task, input, thought, tick)

### 2. Subtype is Free String

```yaml
type: string  # project-specific, not constrained
```

Each project defines its own subtypes:
- mind (dev): `agent`, `module`, `file`, `pattern`, `task`
- blood-ledger (game): `companion`, `monastery`, `weapon`, `oath`, `thought`

This keeps the schema lean while allowing project-specific vocabulary.

### 3. ID Convention (for auto-generation)

All node and link IDs follow a consistent pattern for agent scanning:

```
{node-type}_{SUBTYPE}_{instance-context}_{disambiguator}
```

| Component | Case | Purpose |
|-----------|------|---------|
| `node-type` | lowercase | Schema type (`narrative`, `space`, `thing`, `actor`, `moment`) |
| `SUBTYPE` | ALLCAPS | High-info scan target (`ISSUE`, `TASK`, `OBJECTIVE`, `MODULE`, `FILE`) |
| `instance-context` | lowercase, `-` between words | Descriptive path (`engine-physics-graph-ops`) |
| `disambiguator` | lowercase | 2-char hash or index (`a7`, `01`) |

**Examples:**
```yaml
# Nodes
narrative_ISSUE_monolith-engine-physics-graph-ops_a7
narrative_OBJECTIVE_engine-physics-documented
narrative_TASK_serve-engine-physics-documented_01
space_MODULE_engine-physics
thing_FILE_engine-physics-graph-ops_a7
moment_TICK_1000_a7

# Links
relates_BLOCKS_narrative-issue-a7_TO_narrative-objective-b3
contains_space-module-engine_TO_narrative-issue-a7
```

**Rationale:**
- SUBTYPE in ALLCAPS: When scanning a list of IDs, the subtype differentiates entries — ALLCAPS makes it jump out
- Lowercase node-type: Already known context, low information value
- Dashes within sections, underscores between: Clear visual separation
- Short hash: 2 chars = 256 buckets, sufficient collision safety

**Auto-generation:** Systems creating nodes MUST use this convention. See `mind/doctor_graph.py` for `generate_*_id()` functions.

### 4. Two Physics Fields

```yaml
weight: float [0,1]  # persistent importance
energy: float [0,1]  # instantaneous/computed
```

- **weight** is authored/stored — "how important is this node?"
- **energy** is computed at runtime — "how activated is this node right now?"

All physics mechanisms operate on these two fields.

### 5. Links Have Polarity

```yaml
polarity: float [-1, +1]  # negative = contradict, positive = support
```

This enables the contradiction pressure mechanism — when two narratives contradict, their polarity creates tension that must be resolved.

### 6. Minimal Type-Specific Fields

Most nodes only have base fields. Type-specific additions are rare:
- `thing.uri` — optional locator
- `narrative.content` — the story text
- `moment.content`, `moment.status`, `moment.tick_*` — temporal state

### 7. Single Link Type (v1.4.1+)

```yaml
type: linked  # universal link type
```

All relationships use `linked`. Semantics come from properties:
- `polarity [a→b, b→a]` — bidirectional flow strength
- `hierarchy` — containment vs elaboration
- `permanence` — speculative to definitive
- `emotions` — Plutchik 4 bipolar axes

### 8. Links Have Embeddings (v1.5+)

```yaml
embedding: vector    # source of truth
synthesis: string    # regenerated on drift
```

Links accumulate intentions from traversals. When embedding drifts from synthesis, synthesis regenerates.

### 9. SubEntities Explore (v1.6)

SubEntities are temporary consciousness fragments that traverse the graph:

| State | Purpose |
|-------|---------|
| SEEKING | Follow aligned links |
| BRANCHING | Split at Moments (only) |
| RESONATING | Absorb Narratives |
| REFLECTING | Backprop colors |
| CRYSTALLIZING | Create new Narratives |
| MERGING | Return findings |

Key constraints:
- SubEntities are NOT persistent (exist only during exploration)
- Branching only on Moments (intentional decision points)
- Narratives created by crystallization, not declared directly

### 10. No Arbitrary Constants (v1.6)

All rates derive from graph properties:

| Rate | Formula |
|------|---------|
| permanence_rate | `1 / (avg_degree + 1)` |
| blend_weight | `flow / (flow + energy + 1)` |
| branch_threshold | 2:1 outgoing/incoming |
| crystallization | 0.85 cosine similarity |

### 11. SubEntity Tree Structure (v1.6.1)

SubEntities form a tree during exploration:

```yaml
SubEntity:
  origin_moment: string     # What triggered this exploration
  parent: SubEntity | null  # null for root
  siblings: [SubEntity]     # Other children of same parent
  children: [SubEntity]     # Spawned from branching
  crystallized: string | null  # Narrative ID if created one
```

Tree structure enables:
- Sibling awareness for divergence
- Parent aggregation of child findings
- Async execution mapped to coroutine hierarchy

### 12. Link Score Formula (v1.6.1)

Link selection is not just alignment — it includes novelty and divergence:

```python
link_score = semantic × polarity[direction] × (1 - permanence) × self_novelty × sibling_divergence
```

| Factor | Formula | Purpose |
|--------|---------|---------|
| self_novelty | `1 - max(cos(link, path))` | Avoid backtracking |
| sibling_divergence | `1 - max(cos(link, sibling.embedding))` | Spread exploration |

### 13. Continuous Crystallization Embedding (v1.6.1)

`crystallization_embedding` updated at EVERY step, not just at crystallization:

```python
crystallization_embedding = weighted_sum([
    (0.4, intention_embedding),
    (0.3, position.embedding),
    (0.2, mean(found_narratives.embeddings)),
    (0.1, mean(path.embeddings))
])
```

This enables sibling divergence — siblings compare embeddings to spread out.

### 14. Found Narratives With Alignment (v1.6.1)

```python
found_narratives: dict[str, float]  # {narrative_id: max_alignment}
```

Dict with max alignment per narrative (not list of tuples). Enables:
- Weighted crystallization embedding
- Simple merge on parent (take max)
- Satisfaction computation

On merge from children, parent takes `max(alignment)` per narrative_id.

## What's NOT in the Schema

- **Game-specific attributes** (skills, face, voice, atmosphere) — belong in project data
- **Computed fields** (trust, relationship strength) — derived from graph queries
- **UI/rendering hints** — belong in view layer
- **Historical fields** (provenance, version) — use links or separate tracking

## Invariants

See `schema.yaml` invariants section:
- All link endpoints must exist
- weight, energy, strength in [0,1]
- polarity in [-1, +1]
- Queries cannot mutate graph
- Hot path cannot invoke LLM
