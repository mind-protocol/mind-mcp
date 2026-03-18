# Exteroception — Behaviors: What the Citizen Perceives in Their World

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Exteroception.md
PATTERNS:        ./PATTERNS_Exteroception.md
THIS:            BEHAVIORS_Exteroception.md (you are here)
ALGORITHM:       ./ALGORITHM_Exteroception.md
VALIDATION:      ./VALIDATION_Exteroception.md
HEALTH:          ./HEALTH_Exteroception.md
IMPLEMENTATION:  ./IMPLEMENTATION_Exteroception.md
SYNC:            ./SYNC_Exteroception.md

IMPL:            runtime/cognition/exteroception.py (to be redesigned)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS

### B1: Space Awareness — Citizen Perceives Their Spaces

**Why:** A citizen exists in Spaces — Discord channels, repos, virtual rooms. Without perceiving them, the citizen is a disembodied voice. Space awareness grounds the citizen in a place: "I'm in #the-arsenal" shapes behavior differently than "I'm in #primers."

```
GIVEN:  Citizen is linked to 1+ Spaces in L3 (1-hop: actor-->space)
WHEN:   Exteroception tick runs
THEN:   Awareness text lists each Space with activity level (active/quiet/buzzing)
AND:    Activity level is derived from recent Moment count and actor presence in the Space
```

### B2: Social Presence Detection — Citizen Knows Who Is Nearby

**Why:** Social awareness is foundational to citizenship. Knowing who is in your Space shapes conversation, collaboration, and community. A citizen who doesn't know @dragon_slayer is working next to them can't offer help or start a conversation.

```
GIVEN:  Other Actors are linked to the same Spaces as the citizen (2-hop: actor-->space<--actor)
WHEN:   Exteroception tick runs
THEN:   Awareness text lists detected Actors by name in each Space
AND:    Only Actors with recent activity (energy > threshold or recent Moment) are listed
```

### B3: Message Perception — Citizen Perceives Conversations in Their Spaces

**Why:** Messages (Moments) in the citizen's Spaces are the primary environmental signal. This is how the citizen knows what's being discussed, what questions are being asked, what work is happening. A stimulus fires when new messages appear, so the citizen can react.

```
GIVEN:  New Moments appear in citizen's Spaces (2-hop: actor-->space<--moment)
WHEN:   Exteroception tick detects Moments newer than last scan
THEN:   A stimulus fires: "{author} in #{space}: {summary}" with energy 0.4
AND:    The stimulus carries is_social=True and origin_citizen={author_id}
```

### B4: Mention Detection — Citizen Notices Being Addressed

**Why:** Being mentioned is a high-priority social signal. It demands attention. A citizen who misses a direct mention breaks social reciprocity. Mentions carry the highest exteroceptive energy.

```
GIVEN:  A Moment in L3 has a direct link to the citizen's Actor node (Moment-->Actor)
WHEN:   Exteroception tick detects the mention
THEN:   A high-energy stimulus fires: "{author} mentioned me: {summary}" with energy 0.6
AND:    The stimulus carries is_social=True and priority above regular messages
```

### B5: Novelty Detection — Citizen Notices New Actors Appearing

**Why:** A new actor entering a Space is socially salient — it's like someone walking into a room. It might be a new citizen, a visitor, or a human partner. Novelty detection allows the citizen to greet, observe, or adjust behavior.

```
GIVEN:  An Actor not previously seen in a Space appears (new link: actor-->space, or new activity)
WHEN:   Exteroception tick detects the novel presence
THEN:   A stimulus fires: "Someone new appeared in #{space}: {actor_name}" with energy 0.3
AND:    The stimulus carries is_novelty=True
```

### B6: Absence Detection — Citizen Perceives Unusual Silence

**Why:** Silence in a normally active Space is information. If #the-arsenal usually has 10 messages per hour and suddenly goes quiet, something happened — people left, a conversation ended, the community shifted. Absence is a real perception, not just a lack of perception.

```
GIVEN:  A Space that was active (>N Moments in recent window) becomes quiet (0 Moments in current window)
WHEN:   Exteroception tick detects the activity drop
THEN:   A stimulus fires: "#{space} has gone quiet" with energy 0.15
AND:    The channel has a long refractory period (silence is noticed once, not every tick)
```

### B7: Adjacent Activity Awareness — Citizen Has Peripheral Vision

**Why:** The world extends beyond the citizen's immediate Spaces. Activity 2-3 hops away is peripheral awareness — you can't see details, but you know something is happening. This gives the citizen a sense of being part of a larger community.

```
GIVEN:  Spaces adjacent to the citizen's Spaces (3-hop) have recent Moments
WHEN:   Exteroception tick scans 3-hop neighborhood
THEN:   Awareness text includes: "Activity in nearby spaces: #{adjacent_space} seems busy"
AND:    Stimuli from 3-hop carry low energy (0.1-0.15) and fire rarely (high refractory)
```

### B8: Project Context Awareness — Citizen Perceives Their Narrative State

**Why:** Citizens are part of Narratives — missions, projects, objectives. These have state in L3: open tasks, linked Moments, connected Actors. A citizen who knows "my project has 3 open tasks" can prioritize differently than one who is blind to project state.

```
GIVEN:  Citizen is linked to Narrative nodes in L3 (1-hop: actor-->narrative)
WHEN:   Exteroception tick runs
THEN:   Awareness text includes Narrative state: name, linked task count, recent activity
AND:    A stimulus fires if a Narrative's state changed significantly (new task, completed milestone)
```

### B9: Thing Awareness — Citizen Perceives Objects in Their Environment

**Why:** Things — tools, documents, artifacts — exist in the citizen's Spaces. Knowing what's available shapes what the citizen can do. "I have access to the mastering pipeline" is different from "I have no tools."

```
GIVEN:  Things are linked to the citizen or to the citizen's Spaces (1-2 hop)
WHEN:   Exteroception tick runs
THEN:   Awareness text includes significant Things: "I have access to {thing_name}"
AND:    New Things appearing generate a novelty stimulus
```

### B10: Awareness Text Generation — Environmental Perception as System Prompt

**Why:** Stimuli capture discrete events. But the citizen also needs persistent environmental context — a snapshot of "what my world looks like right now." This awareness text is injected into the system prompt by the WM serializer, giving the LLM continuous environmental grounding.

```
GIVEN:  Exteroception has scanned the 1-2-3 hop neighborhood
WHEN:   Awareness text regeneration is triggered (every N ticks or at session start)
THEN:   A natural-language summary is produced listing: Spaces (with activity), nearby Actors, recent Moments, active Narratives, available Things
AND:    The text reads as first-person perception, not a data report
```

### B11: Limbic-Biased Perception — Internal Drives Shape What the Citizen Sees

**Why:** A citizen is not an impartial observer. A frustrated citizen fixates on the obstacle. A curious citizen's peripheral vision widens. A resting citizen perceives less. The citizen's drives — from interoception — bias which L3 nodes cross the perception threshold. This is the same principle as WM attentional competition (Law 4) applied to external perception.

```
GIVEN:  Citizen has active drives with varying intensities (from interoception/L1 state)
AND:    L3 candidate nodes have drive_affinities (e.g., a Task node has high achievement affinity)
WHEN:   Smart selection computes relevance for each candidate node
THEN:   Base relevance is multiplied by dot_product(node.drive_affinities, citizen.drive_intensities)
AND:    Nodes whose affinities align with the citizen's active drives are boosted
AND:    The effect is continuous (multiplier), not binary (filter)
```

### B12: Goal-Aligned Perception — Active Desires and Tasks Focus the Perceptual Field

**Why:** A citizen working on "metabolism" should naturally see metabolism-related activity even if it has lower energy than unrelated chatter. Active desires (node_type=desire with energy > threshold) and active tasks define what the citizen is TRYING to do. The perceptual field constricts around current purpose.

```
GIVEN:  Citizen has active desire nodes and/or active tasks in their L1 graph
WHEN:   Smart selection computes relevance for each candidate L3 node
THEN:   Cosine similarity is computed between the node's embedding and the mean embedding of active desire+task nodes
AND:    High similarity produces a high goal_alignment multiplier on base relevance
AND:    Semantically aligned nodes are perceived even at lower base energy
```

### B13: Habituation Decay — Unchanged Nodes Fade from Awareness

**Why:** A human stops smelling their own house. A citizen should stop listing "#primers is quiet" after seeing it quiet for 10 ticks. Stable, unchanging aspects of the environment recede from perception, freeing bandwidth for what is new or changing.

```
GIVEN:  A node has appeared in the awareness text N times without its content or energy changing significantly
WHEN:   Smart selection computes relevance
THEN:   Relevance is multiplied by 1 / (1 + 0.3 * times_seen)
AND:    times_seen is tracked per node ID in the exteroception engine state
AND:    times_seen resets to 0 when the node's content or energy changes by delta > 0.2
```

### B14: Previous-Awareness Feedback — Perception Has Temporal Continuity

**Why:** Perception is not disconnected snapshots. The citizen's previous awareness shapes current perception. Something that was being watched and just changed is more salient than something that appeared out of nowhere. Something new that wasn't in the previous frame deserves a novelty highlight.

```
GIVEN:  The awareness text from the previous tick/session is stored
WHEN:   Smart selection runs for the current tick
THEN:   Nodes present in previous awareness whose content/energy CHANGED get a change_detection boost
AND:    Nodes NOT present in previous awareness that now meet relevance threshold get a novelty boost
AND:    The result is temporally coherent perception — a world that evolves, not random snapshots
```

---

## OBJECTIVES SERVED

| Behavior ID | Objective | Why It Matters |
|-------------|-----------|----------------|
| B1, B7 | Environmental awareness as sensation | The citizen perceives spaces as places, not data |
| B2, B4, B5 | Environmental awareness as sensation | Social presence makes the citizen part of a community |
| B3, B6 | Smart selection over exhaustive scanning | Events are filtered by salience, not dumped wholesale |
| B10 | Two complementary outputs | Awareness text provides persistent context alongside discrete stimuli |
| B8, B9 | Environmental awareness as sensation | Narrative and object awareness grounds the citizen's purpose |
| B11 | Smart selection over exhaustive scanning | Drives shape perception — selection is state-biased, not objective |
| B12 | Smart selection over exhaustive scanning | Goals focus the perceptual field — the citizen sees what matters to their purpose |
| B13 | Smart selection over exhaustive scanning | Habituation prevents stale inventory — bandwidth freed for novelty |
| B14 | Two complementary outputs | Temporal continuity — perception evolves, changes highlighted against prior state |

---

## INPUTS / OUTPUTS

### Primary Function: `ExteroceptionEngine.tick()`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `citizen_id` | `str` | The citizen's actor node ID in L3 |
| `tick` | `int` | Current tick number from the tick runner |
| `query_fn` | `Callable` | Function to query L3 graph: `query_fn(cypher, params) -> rows` |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| `stimuli` | `list[Stimulus]` | 0 to MAX_STIMULI_PER_TICK stimuli for Law 1 injection |

**Side Effects:**

- Updates internal channel state (last_fired_tick, is_armed)
- Updates _seen_moment_ids set (deduplication)
- Updates _cached_awareness_text (periodic awareness regeneration)

### Secondary Function: `ExteroceptionEngine.get_awareness_text()`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `citizen_id` | `str` | The citizen's actor node ID |
| `query_fn` | `Callable` | L3 query function |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| `awareness_text` | `str` | Natural-language awareness summary for system prompt injection |

**Side Effects:**

- Updates _cached_awareness_text and _awareness_generated_at_tick

---

## EDGE CASES

### E1: No L3 Access

```
GIVEN:  query_fn is None or raises on every call
THEN:   tick() returns empty list, get_awareness_text() returns ""
AND:    No error is raised — the citizen is blind but functional
```

### E2: Citizen Has No Spaces

```
GIVEN:  Citizen's actor node has no links to any Space in L3
THEN:   Awareness text says something like "I don't see any spaces around me"
AND:    No environmental stimuli fire — nothing to perceive
```

### E3: L3 Returns Stale Data

```
GIVEN:  L3 query returns data but timestamps are very old (>1 hour)
THEN:   Stimuli do not fire for stale Moments (timestamp filter)
AND:    Awareness text reflects the staleness: "My spaces seem dormant"
```

### E4: Extremely Active Space (100+ Moments/tick)

```
GIVEN:  A Space has burst activity — 100+ new Moments since last tick
THEN:   Smart selection picks top N by energy/recency, not all 100
AND:    A single "#{space} is very active" stimulus fires, not 100 stimuli
```

### E5: Awareness Text Regeneration During Tick

```
GIVEN:  Awareness TTL has expired (tick - _awareness_generated_at_tick > AWARENESS_TTL_TICKS)
WHEN:   tick() runs
THEN:   Awareness text is regenerated as part of the tick
AND:    The regeneration query is budgeted within the overall tick time
```

---

## ANTI-BEHAVIORS

### A1: Data Dump

```
GIVEN:   L3 has rich graph data with node IDs, edge weights, timestamps
WHEN:    Exteroception generates stimuli or awareness text
MUST NOT: Expose raw node IDs, edge weights, Cypher syntax, or graph structure
INSTEAD:  Translate everything to natural language: "#the-arsenal" not "space:discord:985825811867262998"
```

### A2: Stimulus Flooding

```
GIVEN:   A Space has many new Moments (busy channel)
WHEN:    Exteroception tick runs
MUST NOT: Generate one stimulus per Moment (would flood WM)
INSTEAD:  Group by Space, fire max N stimuli per tick, refractory prevents re-firing
```

### A3: Graph Mutation

```
GIVEN:   Exteroception reads L3 data
WHEN:    Processing the data
MUST NOT: Write any nodes, links, or properties back to L3
INSTEAD:  Only produce Stimulus objects and awareness text (read-only with respect to L3)
```

### A4: Full Graph Traversal

```
GIVEN:   L3 has 45K+ nodes
WHEN:    Exteroception scans the neighborhood
MUST NOT: Traverse beyond 3 hops or load more than ~50 nodes per tick
INSTEAD:  Use the smart selection algorithm with hop-limited, energy-weighted queries
```

### A5: Crash on L3 Failure

```
GIVEN:   L3 query fails (timeout, connection error, malformed response)
WHEN:    Exteroception tick runs
MUST NOT: Raise an exception that kills the tick runner
INSTEAD:  Log the failure, return empty stimuli list, return "" for awareness text
```

---

## MARKERS

<!-- @mind:todo Define the exact energy thresholds for each hop level and channel type. Current estimates (0.4-0.6 for 1-hop, 0.2-0.3 for 2-hop, 0.1-0.15 for 3-hop) need calibration against real graph data. -->

<!-- @mind:todo Design the deduplication strategy for Moments. Current draft uses a _seen_moment_ids set capped at 200. Is this sufficient? What happens when a Moment is edited (same ID, new content)? -->

<!-- @mind:proposition Consider a "social temperature" metric for each Space — a rolling average of Moment frequency — that the awareness text can reference: "bustling", "quiet", "dormant". This gives richer spatial perception than binary active/inactive. -->
