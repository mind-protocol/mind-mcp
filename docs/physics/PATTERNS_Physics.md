# Physics — Patterns: Why This Shape

```
STATUS: CANONICAL
UPDATED: 2025-12-26
VERSION: v1.6.1 (sibling awareness + continuous crystallization)
```

---

## CHAIN

```
THIS:           PATTERNS_Physics.md (you are here)
BEHAVIORS:      ./BEHAVIORS_Physics.md
ALGORITHMS:
  - ./ALGORITHM_Physics.md      (Consolidated: energy, tick, canon, handlers, input, actions, QA, speed)
SCHEMA:         ../schema/SCHEMA_Moments.md
API:            ./API_Physics.md
VALIDATION:     ./VALIDATION_Physics.md
IMPLEMENTATION: ./IMPLEMENTATION_Physics.md
HEALTH:         ./HEALTH_Physics.md
SYNC:           ./SYNC_Physics.md
```

---

## THE PROBLEM

We need a world simulation that produces believable drama without hand-coded
timelines or omniscient schedulers. The system must decide what happens next
from the living graph itself, keep state authoritative, and avoid separate,
contradictory sources of truth across subsystems.

---

## THE PATTERN

Treat physics as a graph-native scheduler: energy, weight, and link topology
drive what actualizes. Every subsystem reads from and writes to the same
graph, so causality and canon emerge from shared structure instead of
external orchestration rules.

---

## PRINCIPLES

### Principle 1: Single source of truth

Graph state is authoritative; handlers, tick loops, and canon logic are
purely readers and writers that do not maintain parallel state.

### Principle 2: Continuous propagation

Energy always flows and decays, so the system never waits for a "start" cue
and never suspends causality between ticks.

### Principle 3: Potential before canon

Potential moments compete by weight and energy until they actualize into
canon, keeping the system probabilistic without being arbitrary.

### Principle 4: Consequences emerge from links

Link topology determines transfer, proximity, and gating, so structure
drives behavior without ad hoc condition checks.

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `runtime/physics/graph/**` | Supplies graph reads/writes for energy flow and flip detection. |
| `docs/schema/SCHEMA_Moments.md` | Defines the moment and link fields that physics assumes. |
| `docs/infrastructure/api/` | Feeds player input and surfaces physics outputs to clients. |

---

## INSPIRATIONS

Systems-first narrative engines, emergent simulation design, and graph-based
knowledge models where structure, not scripts, produces behavior. The tone
leans toward "living world" sandboxes rather than deterministic story trees.

---

## SCOPE

### In Scope

- Energy propagation, decay, and flip detection in the living graph.
- Canon actualization of moments and sequencing through THEN links.
- Scheduler behavior derived from weights and proximity rules.

### Out of Scope

- LLM prompt design for narration or character voice (see narrator module).
- Visual presentation concerns (see frontend scene/map modules).
- World data ingestion or scraping pipelines (see world-scraping module).

---

## Core Principle

**The graph is the only truth.**

Everything else — handlers, ticks, canon — are processes that read from and write to the graph. No process owns state. No process is authoritative except through what it writes to the graph, so duplication is treated as a bug.

---

## P1: Potential vs Actual

Moments exist in two modes:

| Mode | Meaning | Graph State |
|------|---------|-------------|
| **Potential** | Could happen | Has weight, competes with other potentials |
| **Actual** | Did happen | Is canon, has THEN links to what came before |

No process decides what happens. Processes propose potentials. Physics determines what actualizes.

---

## P2: The Graph Is Alive

The graph is a mind. It doesn't stop thinking.

Energy always flows. Weights always decay. Propagation always happens. Player input is a perturbation, not an ignition.

**What we control:**
- Tick rate (speed setting)
- When we sample for display
- When we inject energy (input, world events, handler outputs)

**What we don't control:**
- "Starting" the cascade — it's always running
- "Stopping" the cascade — it doesn't stop

**Graph states:**

| State | Meaning |
|-------|---------|
| **Active** | High energy, many flips, drama unfolding |
| **Quiet** | Low energy, few flips, system settled |
| **Critical** | Energy building, thresholds approaching, tension rising |

But never **stopped**.

---

## P3: Everything Is Moments

There are no separate systems for dialogue, movement, actions, thoughts.

| What | How It's Represented |
|------|---------------------|
| Speech | Moment with type: dialogue |
| Thought | Moment with type: thought |
| Movement | Moment with type: action, action: travel |
| Combat | Moment with type: action, action: attack |
| Observation | Moment with type: narration |

The graph doesn't distinguish structurally — all are Moment nodes.
Physics doesn't distinguish — all propagate energy the same way.

**But:** Action Processing does distinguish. Moments with `action` field modify world state. Thoughts don't. The moment type determines *consequences*, not storage or propagation.

---

## P4: Moments Are Specific, Narratives Emerge

A moment: "That decision at the crossing cost us."
Another moment: "He's led us wrong before."
Another moment: "Someone else should lead."

These accumulate. Their links converge. A narrative emerges: "Leadership is contested."

**Moments are concrete.** They have text, speaker, time.
**Narratives are patterns.** They're recognized across moments, not authored directly.

---

## P5: Energy Must Land

When energy enters the system, it must go somewhere.

```
Player speaks
  → energy flows to all who heard
  → if no relevant moments exist → energy accumulates on characters
  → if no character flips → energy returns to player character
  → player character always has a handler → something always happens
```

There is no "nothing happens." There is "the silence stretches."

---

## P6: Sequential Actions, Parallel Potentials

**Parallel:** Many character handlers can generate potentials simultaneously.
**Sequential:** Actions that modify world state resolve one at a time.

Aldric and Mildred can both think at once.
Aldric and Mildred cannot both grab the sword at once.

---

## P7: The World Moves Without You

The system does not require player input to advance.

Player can press "Play" and observe.
Time passes. Pressure builds. Characters think. Events unfold.

The player is a participant, not a driver.

---

## P8: Time Is Elastic

The player controls the speed of time, not the content.

| Speed | Feel |
|-------|------|
| 1x | Every moment breathes |
| 2x | Time compresses but conversation persists |
| 3x | World rushes until drama demands attention |

The player is a viewer with a remote. Fast-forward through the boring parts. The system knows when to snap back.

**Speed changes rendering, not reality.** Canon is canon regardless of display speed.

---

## P9: Physics Is The Scheduler

No arbitrary triggers. No cooldowns. No caps.

Character important and close? More energy per tick → flips more often → handler runs more.
Character distant or minor? Less energy → flips rarely → handler runs rarely.

**Importance is derived, not assigned:**
```
importance = sum of weights of all moments ATTACHED_TO this character
```

Character with many high-weight potentials = important right now.
Character with few/low potentials = less important right now.

**Proximity is binary:**
```
proximity = 1.0 if character AT player_location else 0.0
```

Same location = full proximity. Different location = World Runner's domain.

---

## P10: Simultaneous Actions Are Drama

**Old thinking:** Aldric grabs sword + Mildred grabs sword = mutex = resolve conflict.

**New thinking:** Both actualize. Both canon.

```
"Aldric reaches for the sword."
"Mildred's hand closes on the hilt at the same moment."
```

That's not a problem. That's a scene. The consequences play out — struggle, tension, drama.

**Actual mutex (rare):** Same character, two incompatible actions, same tick.
- Aldric "walks east" AND Aldric "walks west"
- Resolution: Higher weight wins. Lower becomes potential for next tick.

Most "conflicts" are actually drama to embrace.

---

## P11: SubEntities Explore With Purpose (v1.8)

Queries are not passive lookups. They are explorations.

When an actor needs something — information, a narrative, a connection — they spawn a **SubEntity**: a temporary consciousness fragment that traverses the graph with query and intention.

**v1.8 Key Distinction: Query vs Intention**
- **Query**: WHAT we're searching for (semantic matching against graph content)
- **Intention**: WHY we're searching (colors traversal priority, stopping, filtering)
- **IntentionType**: HOW to traverse (SUMMARIZE, VERIFY, FIND_NEXT, EXPLORE, RETRIEVE)

Same query with different intentions yields different behavior:
- Query: "Events in Great Hall" + Intention: "summarize" → wide exploration, rich content
- Query: "Events in Great Hall" + Intention: "verify coherence" → look for contradictions
- Query: "Events in Great Hall" + Intention: "find next moment" → stop at first match

**SubEntities carry:**
- Query + query_embedding (what they're looking for)
- Intention + intention_embedding + intention_type (why they're looking)
- Criticality (how desperately they need it)
- Path (where they've been)
- Satisfaction (how much they've found)

**SubEntities evolve:**
| State | What Happens |
|-------|--------------|
| SEEKING | Follow aligned links toward query + intention |
| BRANCHING | Split at Moments (decision points) |
| RESONATING | Absorb aligned Narratives |
| REFLECTING | Backpropagate colors along path |
| CRYSTALLIZING | Create new Narrative if unsatisfied |
| MERGING | Return findings to parent/actor |

**SubEntities color the graph:**
- Forward: links absorb query+intention (less permanent = more colorable)
- Backward: permanence increases on aligned paths

**SubEntities create Narratives:**
When a SubEntity can't find what it's looking for, it crystallizes — generating a new Narrative from its accumulated exploration. This is how knowledge emerges.

**Key constraints:**
- Branching only on Moments (intentional decision points, not arbitrary)
- No arbitrary constants (rates derived from graph properties)
- SubEntities are temporary (exist only during exploration)

---

## P12: No Magic Numbers (v1.6)

All rates and thresholds derive from graph properties:

| Rate | Formula | Why |
|------|---------|-----|
| permanence_rate | `1 / (avg_degree + 1)` | Sparse graphs solidify faster |
| blend_weight | `flow / (flow + energy + 1)` | Hot links resist change |
| branch_threshold | 2:1 ratio | True decision points only |
| crystallization | 0.85 cosine | Novel patterns only |

The graph determines its own physics.

---

## P13: Siblings Diverge Naturally (v1.6.1)

When a SubEntity branches, its children are siblings. Siblings should explore *different* parts of the graph, not duplicate effort.

**The mechanism:**
- Each SubEntity computes `crystallization_embedding` at every step
- Siblings can see each other's embeddings
- Link scoring includes `sibling_divergence = 1 - max(cos(link, sibling.embedding))`
- Links similar to siblings' paths score lower → natural spread

**Why this matters:**
- Parallel exploration without coordination overhead
- Eventually consistent — siblings see "recent enough" state
- Tree structure maps directly to async task hierarchy

---

## P14: Crystallization Is Continuous (v1.8)

The `crystallization_embedding` isn't computed only at crystallization time. It's updated **every step**.

```
intent_weight = INTENTION_WEIGHTS[intention_type]  # 0.1-0.5

crystallization_embedding = weighted_sum([
    (0.4, query_embedding),
    (intent_weight, intention_embedding),
    (0.3, position),
    (0.2, found_narratives),
    (0.1, path)
])
```

**v1.8: Query dominates (0.4), intention adds flavor based on type.**

**Why continuous:**
- Enables sibling divergence (P13)
- Parent can see children's progress
- If SubEntity dies early, its embedding still represents what it found
- No special "crystallization moment" — just use current embedding

---

## P15: Found Narratives Have Alignment (v1.6.1)

When a SubEntity resonates with a Narrative, it stores the ID and max alignment:

```python
found_narratives: dict[str, float]  # {narrative_id: max_alignment}
```

**Why dict with max, not list of tuples:**
- Simple merge: on parent merge, take `max(alignment)` per narrative
- Weighted aggregation when computing crystallization_embedding
- Parent can prioritize high-alignment findings
- No duplicate entries to deduplicate

---

## P16: Sibling Init via Lazy Refs (v1.6.1)

SubEntities reference siblings by ID, not object. A shared `ExplorationContext` maintains the registry.

```python
sibling_ids: list[str]  # IDs, not objects

@property
def siblings(self) -> list[SubEntity]:
    return [context.get(sid) for sid in sibling_ids if context.exists(sid)]
```

**Why lazy refs:**
- No race at spawn — IDs added when branch happens
- Eventual consistency natural — missing sibling = not in list yet
- Serializable (just strings)
- Single source of truth in ExplorationContext

---

## P17: Branch on Count, Score Handles Selection (v1.6.1)

Branch threshold is simple count:

```python
should_branch = len(get_outgoing_links(moment)) >= 2
```

**Why simple:**
- Link scoring (semantic × polarity × permanence × novelty × divergence) handles path selection
- Branch threshold just needs "real choice exists"
- No complex ratio calculations

---

## P18: Link Embedding from Synthesis (v1.6.1)

Links get embedding from their synthesis text:

```python
link.embedding = embed(link.synthesis)  # at creation
link.embedding = blend(link.embedding, intention, 1 - permanence)  # on traverse
```

**Why synthesis:**
- Synthesis is human-readable summary of link meaning
- Embedding captures semantic content
- Less permanent links absorb more intention on traversal
- Graph learns from exploration

---

## What This Pattern Does NOT Solve

- Does not prevent bad drama (but makes state visible)
- Does not guarantee interesting content (handlers must produce it)
- Does not eliminate LLM latency (but pre-generation helps)
- Does not replace thinking (but structures it)

---

## The Philosophy

**Structure creates behavior.**

Moments don't have "speaker" because speakership is a relationship, not an attribute.
Conversations don't have "shape" because shape emerges from links.
Scenes don't exist because presence is computed, not declared.
Cascades don't have boundaries because the graph never stops.

**The graph is the single source of truth. No files. No trees. Just moments, links, and physics.**

---

*"The narrator weaves possibilities. Physics determines what actualizes. The graph remembers everything."*

---

## MARKERS

- How aggressively should energy decay when the world is in a "quiet" state?
- What is the right threshold for flipping from potential to canon in dense scenes?
- When do concurrent actions become mutually exclusive vs. staged drama?
