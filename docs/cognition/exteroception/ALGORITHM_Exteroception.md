# Exteroception — Algorithm: The 1-2-3 Hop Scan, Smart Selection, and Awareness Generation

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Exteroception.md
BEHAVIORS:       ./BEHAVIORS_Exteroception.md
PATTERNS:        ./PATTERNS_Exteroception.md
THIS:            ALGORITHM_Exteroception.md (you are here)
VALIDATION:      ./VALIDATION_Exteroception.md
HEALTH:          ./HEALTH_Exteroception.md
IMPLEMENTATION:  ./IMPLEMENTATION_Exteroception.md
SYNC:            ./SYNC_Exteroception.md

IMPL:            runtime/cognition/exteroception.py (to be redesigned)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

Exteroception runs once per tick, before Law 1 injection. It queries the L3 graph in concentric rings around the citizen's actor node (1-hop, 2-hop, 3-hop), then applies a state-biased scoring function that combines base relevance (hop distance, recency, energy) with three subjective modifiers: limbic bias (drives shape what you see), goal alignment (active desires focus the perceptual field), and habituation decay (unchanged nodes fade from awareness). Previous awareness feeds current perception via change-detection and novelty boosts. The algorithm produces two outputs: a list of stimuli for Law 1 and an awareness text for the system prompt. It completes within a strict time budget even on large graphs by limiting query depth and result counts at the database level.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| Environmental awareness as sensation | B1, B2, B3, B4, B5, B6, B7, B8, B9 | The hop scan is HOW the citizen perceives their world |
| Smart selection over exhaustive scanning | B3, B4, B6, B7, B11, B12, B13 | State-biased scoring prevents data dumps while preserving subjective salience |
| Two complementary outputs | B10, B14 | Awareness text generation with temporal continuity via previous-awareness feedback |
| Structural symmetry with interoception | All | Channel-based gating mirrors interoception's proven pattern |
| Graceful blindness | All | Query failure handling ensures no crashes |

---

## DATA STRUCTURES

### SensoryChannel

```
SensoryChannel:
    name: str               # unique channel identifier
    priority: int           # higher fires first when multiple candidates exist
    refractory_ticks: int   # minimum ticks between firings
    last_fired_tick: int    # tick when this channel last fired (-999 = never)
    is_armed: bool          # whether this channel can fire

Same structure as interoception's Channel. Identical mechanics:
can_fire(tick) checks armed AND refractory elapsed, fire(tick) disarms
and records tick, try_rearm(tick) re-arms after refractory expires.
```

### PerceptionNode

```
PerceptionNode:
    node_id: str            # L3 node ID
    node_type: str          # actor | moment | narrative | space | thing
    name: str               # human-readable name
    content: str            # content or synthesis text
    embedding: list[float]  # node's embedding vector (for goal alignment)
    energy: float           # current L3 energy
    recency: float          # freshness score [0.0, 1.0] based on timestamp
    hop: int                # distance from citizen: 1, 2, or 3
    base_relevance: float   # hop_weight * (recency * 0.6 + energy * 0.4)
    relevance_score: float  # final: base * limbic_bias * goal_alignment * habituation
    space_name: str | None  # which Space this node was found in (for context)
    author_name: str | None # for Moments: who created it
    author_id: str | None   # for Moments: author's actor ID

A lightweight struct holding the essentials of an L3 node after
query and before scoring. Never serialized — lives only in memory
for the duration of one tick.
```

### HabituationState

```
HabituationState:
    times_seen: dict[str, int]    # node_id -> how many awareness cycles it appeared in
    last_content_hash: dict[str, str]  # node_id -> hash of content|energy at last observation
    previous_awareness_ids: set[str]   # node_ids that were in the last awareness text

Persists across ticks on the ExteroceptionEngine instance.
times_seen is incremented each awareness regeneration cycle.
Resets to 0 when the node's content/energy changes significantly.
```

### AwarenessSnapshot

```
AwarenessSnapshot:
    spaces: list[SpacePerception]      # perceived Spaces with activity
    nearby_actors: list[ActorPerception]  # detected Actors in Spaces
    recent_moments: list[MomentPerception]  # significant recent events
    narratives: list[NarrativePerception]   # active projects/missions
    things: list[ThingPerception]        # relevant objects/tools
    generated_at_tick: int               # when this snapshot was built
    text: str                            # the rendered natural-language awareness

SpacePerception:
    name: str
    activity_level: str     # "bustling" | "active" | "quiet" | "dormant"
    actor_count: int        # how many actors detected
    recent_moment_count: int

ActorPerception:
    name: str
    space_name: str         # where detected
    recent_activity: str    # brief description of what they're doing

MomentPerception:
    summary: str            # natural-language summary
    author_name: str
    space_name: str
    age_description: str    # "just now" | "minutes ago" | "recently"

NarrativePerception:
    name: str
    status: str             # inferred from linked tasks/moments
    open_task_count: int

ThingPerception:
    name: str
    context: str            # how it relates to citizen
```

---

## ALGORITHM: `ExteroceptionEngine.tick()`

### Step 0: Guard — Check L3 Access

If `query_fn` is None, return empty stimuli immediately. This is the graceful blindness guarantee. No further processing occurs.

```
if query_fn is None:
    return []
```

### Step 1: Query L3 — The 1-2-3 Hop Scan

Execute up to 3 queries against L3, each expanding the neighborhood by one hop. All queries are parameterized with the citizen's actor ID and a recency window.

**1-hop query:** Direct links from the citizen's actor node.

```
MATCH (me:Actor {id: $cid})-[r:LINK]-(n)
WHERE n.node_type IN ['space', 'actor', 'thing', 'narrative']
RETURN n.id, n.node_type, n.name, n.content, n.synthesis, n.energy,
       n.updated_at, r.weight, r.energy, r.recency
ORDER BY r.energy DESC
LIMIT 20
```

This returns the citizen's immediate environment: their Spaces, known Actors, owned Things, active Narratives.

**2-hop query:** Nodes one step away from the citizen's direct connections.

```
MATCH (me:Actor {id: $cid})-[:LINK]->(s:Space)<-[r:LINK]-(n)
WHERE n.id <> $cid
  AND (n.node_type = 'actor' OR
       (n.node_type = 'moment' AND n.updated_at > $since))
RETURN n.id, n.node_type, n.name, n.content, n.synthesis, n.energy,
       n.updated_at, s.name AS space_name
ORDER BY n.energy DESC, n.updated_at DESC
LIMIT 20
```

This returns: other Actors in the citizen's Spaces, recent Moments in those Spaces.

**3-hop query:** Activity in adjacent Spaces (Spaces connected to Actors in the citizen's Spaces).

```
MATCH (me:Actor {id: $cid})-[:LINK]->(s1:Space)<-[:LINK]-(other:Actor)
      -[:LINK]->(s2:Space)<-[r:LINK]-(m:Moment)
WHERE s2.id <> s1.id AND m.updated_at > $since_long
WITH s2, count(m) AS activity, max(m.updated_at) AS latest
WHERE activity > 2
RETURN s2.id, s2.name, activity, latest
ORDER BY activity DESC
LIMIT 10
```

This returns: adjacent Spaces with significant recent activity. The citizen perceives "buzz" without seeing individual messages.

**Mention query** (special case, always runs):

```
MATCH (m:Moment)-[:LINK]->(me:Actor {id: $cid})
WHERE m.updated_at > $since
MATCH (author:Actor)-[:LINK]->(m)
WHERE author.id <> $cid
RETURN m.id, m.content, m.synthesis, author.id, author.name
ORDER BY m.updated_at DESC
LIMIT 5
```

Mentions are 1-hop from the citizen but have special semantics — they represent direct address, not just co-location.

### Step 2: Score and Select — The State-Biased Smart Selection

All returned nodes are converted to PerceptionNode structs and scored through a four-factor formula. The citizen is NOT an impartial observer — their internal state shapes what they see.

**Step 2a: Base relevance** (objective environmental salience)

```
base_relevance = hop_weight[hop] * (recency * RECENCY_WEIGHT + energy * ENERGY_WEIGHT)

where:
    hop_weight = {1: 1.0, 2: 0.5, 3: 0.2}
    RECENCY_WEIGHT = 0.6
    ENERGY_WEIGHT = 0.4
    recency = max(0, 1.0 - (now - node.updated_at) / RECENCY_WINDOW_S)
```

**Step 2b: Limbic bias** (drives shape perception — B11)

The citizen's current drive intensities multiply candidate relevance. A frustrated citizen sees obstacles more vividly. A curious citizen's peripheral vision widens. A resting citizen perceives less.

```
# Each node type has implicit drive affinities:
DRIVE_AFFINITIES = {
    "actor":     {"affiliation": 0.8, "care": 0.6, "curiosity": 0.3},
    "moment":    {"curiosity": 0.5, "frustration": 0.3, "achievement": 0.3},
    "narrative": {"achievement": 0.8, "curiosity": 0.4},
    "space":     {"affiliation": 0.5, "novelty_hunger": 0.4},
    "thing":     {"achievement": 0.4, "curiosity": 0.3},
}

# Compute limbic bias for a node:
node_affinities = DRIVE_AFFINITIES.get(node.node_type, {})
limbic_bias = 1.0 + sum(
    node_affinities.get(drive, 0.0) * intensity
    for drive, intensity in citizen_drives.items()
) * LIMBIC_BIAS_SCALE

# limbic_bias ranges from 1.0 (no active drives) to ~2.5 (strong drive alignment)
# LIMBIC_BIAS_SCALE = 0.5 (prevents drives from dominating base relevance)
```

**Step 2c: Goal alignment** (active desires focus perception — B12)

Cosine similarity between the node's embedding and the mean embedding of the citizen's active desires and tasks. Nodes semantically aligned with current purpose get boosted.

```
if active_goal_embeddings:
    mean_goal = mean(active_goal_embeddings)
    goal_alignment = 1.0 + max(0, cosine_similarity(node.embedding, mean_goal)) * GOAL_ALIGNMENT_SCALE
else:
    goal_alignment = 1.0  # no goals = no bias

# GOAL_ALIGNMENT_SCALE = 0.8 (strong effect — goals meaningfully focus perception)
# goal_alignment ranges from 1.0 (unrelated) to ~1.8 (highly aligned)
```

**Step 2d: Habituation decay** (unchanged nodes fade — B13)

```
times_seen = self._habituation.times_seen.get(node.node_id, 0)
habituation = 1.0 / (1.0 + HABITUATION_RATE * times_seen)

# HABITUATION_RATE = 0.3
# habituation: 1.0 (never seen) -> 0.77 (1x) -> 0.63 (2x) -> 0.53 (3x) -> ...
```

**Step 2e: Previous-awareness feedback** (temporal continuity — B14)

```
if node.node_id in self._habituation.previous_awareness_ids:
    # Node was in previous awareness — check if it CHANGED
    prev_hash = self._habituation.last_content_hash.get(node.node_id)
    curr_hash = hash(node.content + str(round(node.energy, 1)))
    if prev_hash != curr_hash:
        change_boost = CHANGE_DETECTION_BOOST  # 1.3 — something I was watching just shifted
    else:
        change_boost = 1.0  # no change — habituation handles the fade
else:
    # Node is NEW in the perceptual field
    change_boost = NOVELTY_BOOST  # 1.2 — something I wasn't seeing before appeared

# CHANGE_DETECTION_BOOST = 1.3
# NOVELTY_BOOST = 1.2
```

**Step 2f: Final score**

```
relevance_score = base_relevance * limbic_bias * goal_alignment * habituation * change_boost
```

Mentions get an additional bonus: `relevance_score *= MENTION_BONUS` (1.5) — being addressed is always more salient than ambient activity.

Nodes are sorted by relevance_score descending. The top MAX_PERCEPTION_NODES (default: 50) are kept. The rest are discarded.

### Step 3: Classify into Channels — What Kind of Perception?

Each selected node is classified into a sensory channel based on its type and context:

| Condition | Channel | Priority | Energy |
|-----------|---------|----------|--------|
| Moment linked directly to citizen (mention) | `mention` | 95 | 0.6 |
| Moment in citizen's Space, by known actor | `message` | 80 | 0.4 |
| Actor not previously seen in Space | `new_actor` | 60 | 0.3 |
| Space with activity drop (was active, now quiet) | `silence` | 30 | 0.15 |
| Narrative with state change | `project_update` | 50 | 0.25 |
| 3-hop Space with high activity | `adjacent_buzz` | 20 | 0.1 |
| Thing appearing in Space | `new_thing` | 40 | 0.2 |

Each candidate is a tuple: `(priority, channel_name, content_text, energy, extra_fields)`.

### Step 4: Fire Through Channel Gating

Sort candidates by priority descending. For each candidate:

1. Check if the channel can fire: `channel.can_fire(tick)` (armed AND refractory elapsed)
2. If yes: create Stimulus, append to results, call `channel.fire(tick)`
3. If `len(stimuli) >= MAX_STIMULI_PER_TICK`: stop

This is identical to interoception's gating logic.

```
candidates.sort(key=priority, reverse=True)
for priority, channel, content, energy, extra in candidates:
    if len(stimuli) >= MAX_STIMULI_PER_TICK:
        break
    if channels[channel].can_fire(tick):
        stimuli.append(Stimulus(
            content=content,
            energy_budget=energy,
            source="exteroception",
            is_social=extra.get("is_social", False),
            origin_citizen=extra.get("origin_citizen", ""),
        ))
        channels[channel].fire(tick)
```

### Step 5: Rearm Channels

After firing, rearm channels whose refractory period has elapsed:

```
for ch in channels.values():
    if not ch.is_armed and (tick - ch.last_fired_tick >= ch.refractory_ticks):
        ch.is_armed = True
```

### Step 6: Maybe Regenerate Awareness Text

If the awareness text TTL has expired (or this is the first tick), regenerate it from the collected PerceptionNodes:

```
if tick - self._awareness_generated_at_tick >= AWARENESS_TTL_TICKS:
    self._cached_awareness = self._build_awareness_text(perception_nodes)
    self._awareness_generated_at_tick = tick

    # Update habituation state for next cycle
    current_ids = {n.node_id for n in perception_nodes if n.relevance_score > AWARENESS_INCLUSION_THRESHOLD}
    for nid in current_ids:
        self._habituation.times_seen[nid] = self._habituation.times_seen.get(nid, 0) + 1
        self._habituation.last_content_hash[nid] = hash(...)  # content + energy hash
    self._habituation.previous_awareness_ids = current_ids
```

The awareness text is NOT returned from tick() — it's cached and retrieved separately by the WM serializer via `get_awareness_text()`.

### Step 7: Prune Deduplication State

The `_seen_moment_ids` set prevents re-firing stimuli for already-seen Moments. Prune it when it grows too large:

```
if len(self._seen_moment_ids) > MAX_SEEN_IDS:
    # Keep the most recent half
    self._seen_moment_ids = set(list(self._seen_moment_ids)[-MAX_SEEN_IDS // 2:])
```

---

## ALGORITHM: `_build_awareness_text()`

Converts the collected PerceptionNodes into a natural-language summary.

### Step 1: Group by Type

Partition perception_nodes into spaces, actors, moments, narratives, things.

### Step 2: Characterize Spaces

For each Space, compute:
- `actor_count`: how many Actor PerceptionNodes are associated
- `recent_moment_count`: how many Moment PerceptionNodes are associated
- `activity_level`: derived from moment count:
  - 0 = "dormant"
  - 1-3 = "quiet"
  - 4-10 = "active"
  - 11+ = "bustling"

### Step 3: Render Natural Language

Compose the awareness text in first person:

```
## What I See Right Now

I'm in {N} spaces: {space_name} ({activity_level}, {actor_count} citizens present), ...

{If nearby_actors}: {actor_name} is nearby{, working on {recent_activity}}.

{If recent_moments}: {author} just posted in #{space} about {topic}.

{If narratives}: My current project "{narrative_name}" has {N} open tasks.

{If adjacent_buzz}: There's activity in nearby spaces: #{space} seems busy.
```

The text is capped at ~500 chars to keep the system prompt budget manageable. If the perceptual field is rich, compress peripheral details first (3-hop, then things, then less active spaces).

---

## KEY DECISIONS

### D1: Query Depth vs Speed

```
IF L3 query latency > 100ms for 1-hop:
    Skip 3-hop query entirely (degrade to 1-2 hop only)
    Log warning for monitoring
ELSE:
    Run all 3 queries (1-hop, 2-hop, 3-hop + mention)
```

### D2: Awareness Regeneration Trigger

```
IF tick == 0 (first tick of session):
    Always regenerate awareness text (citizen needs initial environmental context)
ELIF tick - _awareness_generated_at_tick >= AWARENESS_TTL_TICKS:
    Regenerate (TTL expired)
ELSE:
    Use cached awareness text
```

### D3: Handling Duplicate Nodes Across Hops

```
IF a node appears in both 1-hop and 2-hop results:
    Keep the 1-hop version (higher hop_weight, more relevant)
    Discard the 2-hop duplicate
    Deduplication by node_id before scoring
```

---

## DATA FLOW

```
citizen_id + tick + query_fn + state (drives, desires, tasks)
    |
    v
[Step 0] Guard: query_fn is None? → return []
    |
    v
[Step 1] 1-2-3 hop queries → raw rows from L3
    |
    v
[Step 1b] Convert rows → list[PerceptionNode]
    |
    v
[Step 2a] Base relevance: hop_weight * (recency * 0.6 + energy * 0.4)
    |
    v
[Step 2b] Limbic bias: drives shape perception (B11)
    |
    v
[Step 2c] Goal alignment: cosine(node.embedding, mean_goal_embedding) (B12)
    |
    v
[Step 2d] Habituation decay: 1 / (1 + 0.3 * times_seen) (B13)
    |
    v
[Step 2e] Previous-awareness feedback: change_boost / novelty_boost (B14)
    |
    v
[Step 2f] Final score + sort + truncate → top 50 PerceptionNodes
    |
    v
[Step 3] Classify → list[candidate(priority, channel, content, energy)]
    |
    v
[Step 4] Gate: channel.can_fire(tick)? → list[Stimulus] (max 3)
    |
    v
[Step 5] Rearm expired channels
    |
    v
[Step 6] Maybe regenerate awareness text + update habituation state
    |
    v
[Step 7] Prune _seen_moment_ids
    |
    v
return list[Stimulus]
```

---

## COMPLEXITY

**Time:** O(Q + N log N) where Q = total query time (dominated by L3 roundtrips), N = number of returned nodes (capped at ~55 by LIMIT clauses). In practice, Q dominates. The scoring and sorting is negligible on ~50 nodes.

**Space:** O(N + S) where N = PerceptionNodes in memory (~50), S = _seen_moment_ids set (capped at MAX_SEEN_IDS, default 200). Total memory per citizen is trivial.

**Bottlenecks:**
- L3 query latency is the primary bottleneck. FalkorDB on local network should be <50ms per query. On degraded infra, queries may timeout.
- The 3-hop query is the most expensive (3 join levels). It's the first to skip under latency pressure.
- Awareness text regeneration adds one extra processing pass per TTL cycle, but on ~50 nodes this is negligible.

---

## HELPER FUNCTIONS

### `_score_node(node: PerceptionNode, now: float, drives: dict, goal_embedding: list[float] | None) -> float`

**Purpose:** Compute the full state-biased relevance_score for a single node.

**Logic:** Four-factor multiplication:
1. Base: `hop_weight[hop] * (recency * 0.6 + energy * 0.4)`
2. Limbic: `1.0 + sum(affinity * drive_intensity) * 0.5`
3. Goal: `1.0 + max(0, cosine(node.embedding, goal_embedding)) * 0.8` (if goals exist)
4. Habituation: `1.0 / (1.0 + 0.3 * times_seen)`
5. Change/novelty boost from previous awareness comparison

Final: `base * limbic * goal * habituation * change_boost`

### `_classify_node(node: PerceptionNode, seen_actors: set) -> tuple | None`

**Purpose:** Determine which sensory channel a node triggers, if any.

**Logic:** Match on node_type and context (is it a mention? a new actor? a moment in my space?). Returns `(priority, channel_name, content_text, energy, extra)` or None if the node doesn't trigger any channel.

### `_build_awareness_text(nodes: list[PerceptionNode]) -> str`

**Purpose:** Render the natural-language awareness summary from scored nodes.

**Logic:** Group nodes by type, compute Space activity levels, compose first-person text. Cap at ~500 chars.

### `_render_space_activity(space_name: str, moment_count: int, actor_count: int) -> str`

**Purpose:** Convert Space statistics into natural language.

**Logic:** "#{name} (bustling, 12 citizens)" or "#{name} (quiet)" depending on counts.

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| L3 FalkorDB (via query_fn) | Cypher queries with LIMIT/ORDER | Rows of node properties + embeddings |
| `tick_runner_l1_cognitive_engine.py` | Called BY tick runner at step 0 | Returns list[Stimulus] injected via Law 1 |
| `models.py` (CitizenCognitiveState) | Read citizen's drives, active desires, active tasks | Drive intensities for limbic bias, goal embeddings for alignment |
| `wm_prompt_serializer.py` | Serializer calls get_awareness_text() | Returns cached awareness string |
| `interoception.py` | No direct call — but shares Channel pattern | Same gating architecture |

---

## CONSTANTS

| Constant | Default | Description |
|----------|---------|-------------|
| `MAX_STIMULI_PER_TICK` | 3 | Maximum stimuli produced per tick (same as interoception) |
| `MAX_PERCEPTION_NODES` | 50 | Maximum nodes retained after scoring |
| `MAX_SEEN_IDS` | 200 | Cap on deduplication set |
| `RECENCY_WINDOW_S` | 3600.0 | 1 hour — how far back recency scoring considers |
| `SCAN_WINDOW_S` | 300.0 | 5 minutes — Moment timestamp filter for stimulus detection |
| `AWARENESS_TTL_TICKS` | 10 | Regenerate awareness text every 10 ticks |
| `HOP_WEIGHT` | {1: 1.0, 2: 0.5, 3: 0.2} | Relevance multiplier per hop distance |
| `RECENCY_WEIGHT` | 0.6 | Weight of recency in base scoring |
| `ENERGY_WEIGHT` | 0.4 | Weight of energy in base scoring |
| `LIMBIC_BIAS_SCALE` | 0.5 | How strongly drives amplify perception (prevents domination) |
| `GOAL_ALIGNMENT_SCALE` | 0.8 | How strongly goal similarity focuses perception |
| `HABITUATION_RATE` | 0.3 | How fast unchanged nodes fade from awareness |
| `CHANGE_DETECTION_BOOST` | 1.3 | Relevance boost for nodes that changed since last awareness |
| `NOVELTY_BOOST` | 1.2 | Relevance boost for newly appearing nodes |
| `AWARENESS_INCLUSION_THRESHOLD` | 0.1 | Min relevance_score to be included in awareness text |
| `MENTION_BONUS` | 1.5 | Relevance multiplier for mentions |
| `EXTERO_SOURCE` | "exteroception" | Source tag on generated stimuli |

---

## MARKERS

<!-- @mind:todo The 1-2-3 hop Cypher queries need testing against real FalkorDB with production-scale data. The current query shapes assume standard LINK edges — verify against actual L3 graph structure where relation_kind is always null. -->

<!-- @mind:todo The SCAN_WINDOW_S and RECENCY_WINDOW_S need calibration. 300s for stimuli and 3600s for scoring are starting guesses. At 60s/tick, 300s covers 5 ticks. Is that enough? Too much? -->

<!-- @mind:escalation The 3-hop query uses a 3-level MATCH pattern which may be expensive on large graphs. Need to benchmark against FalkorDB with 45K nodes. If too slow, consider pre-computing "adjacent space activity" as an L3 aggregate node that exteroception reads directly. NLR decision needed on whether to invest in query optimization or graph pre-computation. -->

<!-- @mind:proposition Consider caching L3 query results across ticks for slowly-changing data (Space membership, actor locations). Only Moments change frequently. A 2-tier cache (fast-changing moments + slow-changing topology) would halve query load. -->

<!-- @mind:todo Define the content_text generation for each channel type. Current algorithm describes the classification but not the exact natural-language templates. Examples needed: what does a "message" stimulus content look like vs a "silence" stimulus? Reference interoception's drive_names dict pattern. -->
