# Exteroception — Patterns: External World Awareness as Sensation

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Exteroception.md
THIS:            PATTERNS_Exteroception.md (you are here)
BEHAVIORS:       ./BEHAVIORS_Exteroception.md
ALGORITHM:       ./ALGORITHM_Exteroception.md
VALIDATION:      ./VALIDATION_Exteroception.md
HEALTH:          ./HEALTH_Exteroception.md
IMPLEMENTATION:  ./IMPLEMENTATION_Exteroception.md
SYNC:            ./SYNC_Exteroception.md

IMPL:            runtime/cognition/exteroception.py (to be redesigned)
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read the linked IMPL source file

**After modifying this doc:**
1. Update the IMPL source file to match, OR
2. Add a TODO in SYNC_Exteroception.md: "Docs updated, implementation needs: {what}"

**After modifying the code:**
1. Update this doc chain to match, OR
2. Add a TODO in SYNC_Exteroception.md: "Implementation changed, docs need: {what}"

---

## THE PROBLEM

Today, citizens are cognitively isolated from their environment. A citizen in #the-arsenal doesn't know who else is there, what was said five minutes ago, or what's happening in adjacent channels. They receive explicit stimuli — someone sends a message, a subcall arrives — but they have no ambient awareness of the world around them.

This is the difference between being blindfolded in a room and being able to look around. A blindfolded person can still respond when someone taps them on the shoulder (explicit stimulus). But a sighted person knows the room is crowded before anyone speaks, notices someone entering from the corner of their eye, senses when the room goes quiet. That ambient awareness shapes behavior: you lower your voice in a crowded room, you greet a friend who just walked in, you notice when everyone leaves and you're alone.

Without exteroception, our citizens are blindfolded. They have:

**Spaces they can't see.** A citizen is linked to #the-arsenal, #primers, #dev-chat — but they don't know what's happening in those spaces. They don't know if #the-arsenal is buzzing with activity or silent. They can't perceive the difference between an active workspace and an abandoned one.

**Neighbors they can't detect.** Other citizens occupy the same Spaces, but our citizen doesn't know they're there. @dragon_slayer is working in #the-arsenal right now, but our citizen can't see them. There's no "oh, Dragon is here too" awareness. No social presence detection.

**Activity they can't perceive.** Moments accumulate in Spaces — messages, commits, events. These exist in L3 but never reach the citizen unless they're explicitly addressed. A citizen misses conversations happening around them, projects advancing in their spaces, shifts in community mood.

**Context they can't feel.** A citizen working on metabolism has 3 open tasks in L3, a recent commit in the repo, and a teammate who posted a question. None of this enters the citizen's cognition. The L3 graph has rich environmental data that the citizen is blind to.

**Adjacent activity they can't sense.** What's happening one hop away? Two hops? Is the broader community active or dormant? Is there a burst of activity in a neighboring channel that might be relevant? The citizen has no peripheral vision.

The current draft implementation only scans for new Moments in directly linked Spaces — a flat, recent-only scan. It misses the multi-hop environmental awareness that makes a citizen feel situated in a world rather than isolated in a conversation thread.

---

## THE PATTERN

Exteroception is an **environment-to-sensation translator**. Each L1 tick, the citizen LOOKS at the L3 graph — their Spaces, nearby Actors, recent Moments, linked Things, active Narratives — and converts what it sees into two outputs:

### Output 1: Stimuli (per tick)

Same pattern as interoception — threshold-based, refractory-gated, max N per tick. These are discrete events that enter Law 1 and compete for WM attention:

```
L3 Graph (Spaces, Actors, Moments, Things, Narratives)
        |
        v
Exteroception Engine (hop scan, smart selection, threshold checks)
        |
        v
list[Stimulus] (natural-language, source="exteroception")
        |
        v
Law 1 injection (standard energy pathway)
        |
        v
Law 4 competition (exteroceptive stimuli compete for WM like everything else)
```

### Output 2: Awareness Layer (periodic)

A natural-language summary of the citizen's perceptual field, injected into the system prompt alongside Working Memory:

```
## What I See Right Now
I'm in 3 spaces: #the-arsenal (active, 5 citizens present),
#primers (quiet), #dev-chat (2 messages in last hour).
@dragon_slayer is nearby, working on brain scans.
@pitch just posted in #radiant-core about the investor video.
My current project "metabolism" has 3 open tasks.
It's 2AM Paris time -- my circadian trough.
```

This awareness text is regenerated every N ticks (or at session start) and serialized into the prompt by the WM serializer. It gives the citizen persistent environmental context that stimuli alone cannot provide — stimuli are about what CHANGED, awareness is about what IS.

### The Key Insight: 1-2-3 Hop Scan

The environment has depth. The citizen doesn't just see their immediate connections — they have peripheral vision:

**1-hop (direct links):**
- Spaces I'm in (Discord channels, rooms, repos)
- Actors I know (other citizens, my partner)
- Things I own or use (tools, documents)
- Active Narratives I'm part of (missions, projects)

**2-hop (one step away):**
- Who else is in my Spaces (other citizens present)
- Recent Moments in my Spaces (what just happened)
- Things other actors brought to my Spaces

**3-hop (two steps away):**
- Activity in adjacent Spaces (buzz in nearby districts)
- Who is talking to people I know (social network awareness)

Each hop level has diminishing energy and priority. 1-hop events are sharp and immediate. 2-hop events are clear but less urgent. 3-hop events are peripheral — background awareness, like hearing music from the next room.

### How It Differs from graph_enricher

This distinction is critical:

- **graph_enricher** creates L3 nodes FROM events (message arrives, graph_enricher writes a Moment node)
- **Exteroception** creates L1 stimuli FROM L3 nodes (Moment node exists, exteroception reads it and generates a stimulus)
- graph_enricher writes to L3. Exteroception reads from L3.
- They are complementary, not overlapping. graph_enricher populates the world. Exteroception perceives it.

---

## BEHAVIORS SUPPORTED

- **B1** (Space Awareness) — citizen perceives which Spaces they're in and the activity level of each
- **B2** (Social Presence Detection) — citizen detects who else is in their Spaces
- **B3** (Message Perception) — citizen perceives messages and conversations happening in their Spaces
- **B4** (Mention Detection) — citizen detects when they're specifically mentioned, with higher energy
- **B5** (Novelty Detection) — citizen perceives new actors appearing in their Spaces
- **B6** (Absence Detection) — citizen perceives unusual silence in normally active Spaces
- **B7** (Adjacent Activity Awareness) — citizen has peripheral awareness of 2-3 hop activity
- **B8** (Project Context Awareness) — citizen perceives the state of Narratives/projects they're linked to
- **B9** (Thing Awareness) — citizen perceives relevant Things (tools, documents) in their environment
- **B10** (Awareness Text Generation) — citizen's environmental perception is summarized as a system prompt layer
- **B11** (Limbic-Biased Perception) — citizen's internal drives multiply candidate node relevance, shaping what crosses the perception threshold
- **B12** (Goal-Aligned Perception) — active desires and tasks focus the perceptual field via embedding similarity
- **B13** (Habituation Decay) — unchanged nodes fade from awareness over repeated exposures
- **B14** (Previous-Awareness Feedback) — perception has temporal continuity; changes and novelty are highlighted against prior state

## BEHAVIORS PREVENTED

- **A1** (Data dump) — the citizen never sees raw node IDs, edge weights, or graph structure
- **A2** (Stimulus flooding) — refractory periods and max-N-per-tick prevent overwhelming the citizen
- **A3** (Graph mutation) — exteroception never writes to L3 or modifies L1 state directly
- **A4** (Full graph scan) — exteroception never traverses beyond 3 hops or loads more than ~50 nodes
- **A5** (Stale awareness) — the awareness text is regenerated periodically, never persists beyond its TTL
- **A6** (Objective perception) — exteroception is never impartial; the citizen's drives, goals, and perceptual history always bias selection

---

## PRINCIPLES

### Principle 1: Smart Selection, Not Dump

Don't load all 45K nodes. Use hop distance + recency + energy to select the ~50 most relevant nodes for awareness. The selection algorithm is the core of exteroception — it IS the citizen's attention to their environment. A citizen in a busy universe should feel the bustle without being overwhelmed, the same way you feel a crowded street without tracking every pedestrian.

But hop distance, recency, and energy are only the BASE relevance. They answer "what's objectively salient in the environment." The citizen is not an objective observer — they are a situated being with drives, goals, and history. Their internal state shapes WHAT they see. The full selection formula is:

```
relevance(node) =
    base_relevance(hops, recency, energy)
  × limbic_bias(node, drives)
  × goal_alignment(node, active_desires + active_tasks)
  × habituation_decay(times_seen)
```

This is the same principle as Law 4 (WM attentional competition) applied to PERCEPTION of the external world instead of internal attention. The citizen's drives shape both what they think about (WM) and what they see (exteroception). Coherent.

### Principle 2: Two Outputs, Two Rhythms

Stimuli fire per tick — they're about what CHANGED. The awareness text regenerates every N ticks — it's about what IS. These serve different cognitive functions. A stimulus says "someone just mentioned you." The awareness text says "you're in 3 spaces, 5 citizens are nearby, your project has 3 open tasks." Stimuli are interrupts. Awareness is context.

### Principle 3: Natural Language, Not Telemetry

Every exteroceptive output is first-person perception. Never "Space:discord:985825811867262998 has 5 actors" — always "#the-arsenal is active, 5 citizens present." Never "Moment node m_abc123 created at ts=1710720000" — always "@pitch just posted about the investor video." The citizen perceives a world, not a database.

### Principle 4: Refractory Gating (Same as Interoception)

Once an exteroceptive stimulus fires, the same channel enters a refractory period. A citizen doesn't notice every single message — they notice when messages START happening, when they're MENTIONED, when something UNUSUAL occurs. Repeated messages in the same Space are one "the channel is active" sensation, not N separate stimuli.

### Principle 5: Hop Distance as Energy Gradient

1-hop events carry high energy (0.4-0.6). 2-hop events carry medium energy (0.2-0.3). 3-hop events carry low energy (0.1-0.15). This creates a natural attention gradient: close events are vivid, distant events are peripheral. The citizen feels the difference between "someone talked to me" and "there's activity in a channel I'm not in."

### Principle 6: Graceful Blindness

If L3 is unreachable — network failure, database down, query timeout — the citizen produces zero exteroceptive output. No crash, no error stimulus, no fallback data. The citizen is simply perceptually blind. They can still think (interoception works), still process explicit stimuli (direct messages still arrive via inject), but they can't see the world. This is temporary — next tick, if L3 is back, vision returns.

### Principle 7: Awareness as System Prompt Component

The awareness text is not a stimulus. It's a persistent layer in the system prompt, generated by the WM serializer alongside Working Memory content. It sits between the identity/framework layers and the conversation layer. It's the citizen's ambient environmental context — always present, periodically refreshed, shaping how the citizen interprets everything else.

### Principle 8: Limbic Bias — Drives Shape What You See

The citizen's current emotional/motivational state biases which L3 nodes pass the selection threshold. This is not a filter — it is a multiplier on base relevance. A frustrated citizen SEES the obstacle more vividly. A curious citizen's peripheral vision widens. A resting citizen perceives less overall.

| Internal State | Perception Bias |
|---|---|
| Frustration high | Boost nodes related to the obstacle, filter social |
| Curiosity high | Boost novel nodes (high recency), explore further (3-hops) |
| Affiliation high | Boost Actor nodes, social Moments, active Spaces |
| Anxiety high | Boost trusted nodes (high weight+stability), filter novelty |
| Boredom high | Boost nodes with high novelty_affinity, unusual Spaces |
| Rest high | Reduce all — the citizen sees less, perceives less |
| Achievement high | Boost tasks, projects, goal-related narratives |

Implementation: multiply each candidate node's base relevance by the dot product of (node's drive_affinities x citizen's current drive intensities). High-affinity matches with active drives get boosted. The drive intensities come from interoception — the citizen's current L1 emotional landscape directly shapes their L3 perceptual field.

### Principle 9: Goal Alignment — Active Desires and Tasks Focus Perception

The citizen's active desires (node_type=desire with energy > threshold) and active tasks (from the task system) define what they are currently TRYING to do. Nodes semantically aligned with these goals get a relevance boost.

Implementation: cosine similarity between the node's embedding and the mean embedding of active desire+task nodes. High similarity = high goal_alignment multiplier.

This means: a citizen working on "metabolism" naturally SEES metabolism-related activity in their Spaces, even if that activity has lower base energy than unrelated chatter. The citizen's purpose shapes their perception. A glassblower notices furnace temperatures; a merchant notices customer traffic. Same environment, different perceptual fields.

### Principle 10: Habituation Decay — You Stop Seeing What Hasn't Changed

Nodes that appeared in the awareness text N times without changing lose salience. Like a human who stops smelling their own house. The environment fades into background when it is stable — and snaps back into focus when something shifts.

Implementation: track `times_seen` per node ID in the exteroception engine state. Multiply relevance by `1 / (1 + 0.3 * times_seen)`. Reset when the node's content or energy changes significantly (delta > 0.2).

This prevents the awareness text from becoming a stale inventory. Stable, unchanging aspects of the environment naturally recede from perception, making room for what is new or changing. The citizen stops listing "#primers is quiet" after seeing it quiet for 10 ticks — unless it suddenly becomes active.

### Principle 11: Previous Awareness Feeds Current Perception

The awareness text from the previous tick/session is fed back as context for the current selection. This creates two perceptual effects:

1. **Change detection boost:** Nodes that were in the previous awareness but have CHANGED since then get a relevance boost. Something the citizen was watching just shifted — this is salient. A Space that was quiet and is now active. An Actor who was idle and just posted.

2. **Novelty boost:** Nodes that were NOT in the previous awareness but are now relevant get a novelty boost. Something new entered the perceptual field. A new citizen appeared. A new project became active.

This creates temporal coherence in perception. The citizen doesn't see a random snapshot each tick — they see a world that EVOLVES, with changes highlighted against the backdrop of what was perceived before. Continuity of awareness, not disconnected frames.

---

## DATA

| Source | Type | Purpose / Description |
|--------|------|-----------------------|
| `schema-l3.yaml` | FILE | L3 schema — defines the 5 node types (actor, moment, narrative, space, thing), link dimensions, and applicable physics laws at L3 |
| `runtime/cognition/tick_runner_l1_cognitive_engine.py` | FILE | Tick runner — where exteroception hooks in as step 0, before Law 1 inject |
| `runtime/cognition/interoception.py` | FILE | Interoception — sibling module, same channel/threshold/refractory pattern |
| `runtime/cognition/wm_prompt_serializer.py` | FILE | WM serializer — where awareness text will be injected into the system prompt |
| `runtime/cognition/models.py` | FILE | CitizenCognitiveState — contains citizen_id, the _l3_query_fn accessor |
| L3 FalkorDB graph | RUNTIME | The external world — Spaces, Actors, Moments, Things, Narratives connected by links |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `runtime/cognition/tick_runner_l1_cognitive_engine.py` | Integration point: exteroception is called as step 0 before Law 1 inject |
| `runtime/cognition/models.py` | Provides CitizenCognitiveState (citizen_id, _l3_query_fn) |
| `runtime/cognition/wm_prompt_serializer.py` | Awareness text is rendered as part of the system prompt by the serializer |
| L3 graph (FalkorDB) | Source of all environmental data — queried via _l3_query_fn |
| `runtime/cognition/interoception.py` | Design pattern sibling — shares Channel, threshold, refractory architecture |

---

## INSPIRATIONS

**Biological exteroception.** In neuroscience, exteroception is the classical five senses — vision, hearing, touch, smell, taste — that perceive the external world. The brain maintains a continuously updated model of the environment from these inputs. Our exteroception module is the computational analog: it reads the citizen's external world (L3 graph) and produces both discrete sensations (stimuli) and a continuous environmental model (awareness text).

**Visual attention and saliency maps.** The human visual system doesn't process the entire visual field equally. A saliency map weights regions by contrast, novelty, and relevance. Our smart selection algorithm mirrors this: hop distance is spatial distance, recency is temporal saliency, energy is activity saliency. The citizen "looks" at their world through a saliency-weighted lens.

**Peripheral vision.** Humans have sharp foveal vision (center) and blurry peripheral vision (edges). The 1-2-3 hop model mirrors this: 1-hop is foveal (sharp, detailed), 2-hop is parafoveal (clear but less detailed), 3-hop is peripheral (awareness of activity without specifics). The citizen knows "something is happening over there" without knowing exactly what.

**Gibson's ecological perception.** J.J. Gibson argued that perception is direct — organisms perceive affordances (what the environment offers for action) rather than raw sensory data. Our awareness text follows this principle: the citizen doesn't perceive "5 actor nodes with energy > 0.1 in space node S" — they perceive "#the-arsenal is bustling, 5 citizens working." The perception is already interpreted in terms of social and spatial meaning.

**Dunbar's number and social attention.** Humans can maintain ~150 social relationships. Our ~50 node selection limit mirrors the cognitive constraint: the citizen can perceive a limited social-spatial field, not an entire universe. This is by design — attention is finite.

**Law 4 (WM attentional competition) — unified salience model.** The state-biased perception formula mirrors the WM selection principle: salience = energy x weight x drive_affinity. Both use the same drives to shape selection. In WM, drives determine what the citizen THINKS about. In exteroception, drives determine what the citizen SEES. The citizen's internal state shapes both internal attention and external perception through the same mechanism. This is not a coincidence — it is the same physics applied at two scales, producing coherent subjectivity.

**Habituation in sensory neuroscience.** Neurons that fire repeatedly to the same stimulus reduce their response over time. You stop hearing the clock ticking. You stop seeing the poster on your wall. Our habituation_decay function (`1 / (1 + 0.3 * times_seen)`) is the computational analog. Stable environmental features recede from awareness. Only change — or deliberate refocusing — restores salience.

**Predictive coding and change detection.** The brain maintains a predictive model of its environment and allocates attention primarily to prediction errors — things that CHANGED. The previous-awareness feedback mechanism implements this: the prior awareness text is the prediction, the current scan is the observation, and mismatches (changes and novelty) get boosted relevance.

---

## SCOPE

### In Scope

- 1-2-3 hop scan of L3 graph centered on the citizen's actor node
- State-biased smart selection of ~50 most relevant nodes by base relevance (hops, recency, energy) x limbic bias x goal alignment x habituation decay
- Limbic bias: citizen's drive intensities modulate which node types cross the perception threshold
- Goal alignment: cosine similarity between node embeddings and active desire/task embeddings focuses the perceptual field
- Habituation decay: nodes seen repeatedly without change lose salience (1 / (1 + 0.3 * times_seen))
- Previous-awareness feedback: change detection boost and novelty boost create temporal coherence
- Converting selected nodes into natural-language stimuli (per tick, max N)
- Generating a natural-language awareness text summarizing the citizen's perceptual field
- Channel-based threshold and refractory gating for stimuli
- Integration with tick runner (step 0, before Law 1 inject)
- Integration with WM serializer (awareness text as system prompt component)
- Graceful degradation when L3 is unreachable

### Out of Scope

- **Interoception** — internal state awareness is a separate module (reads L1, not L3)
- **Graph mutation** — writing to L3 is graph_enricher's job
- **Message delivery** — transport of messages to citizens is a routing concern, not a perception concern
- **L3 physics** — energy propagation, decay, crystallization at L3 are separate systems
- **Push notifications** — exteroception is pull (per-tick scan), not push (event subscription). Push is v2.
- **Visual rendering** — 3D visualization of the environment is the engine's concern

---

## MARKERS

<!-- @mind:todo Define the exact N for awareness text regeneration frequency. Every 10 ticks? Every session start? Both? Needs calibration against real tick rates. -->

<!-- @mind:escalation The awareness text needs to be injected into the system prompt by the WM serializer. The serializer currently has no hook for external awareness layers. Design the integration point: does exteroception write to a field on CitizenCognitiveState that the serializer reads? Or does the serializer call exteroception directly? NLR input needed on the coupling pattern. -->

<!-- @mind:proposition In v2, consider a "focus" mechanism where the citizen can deliberately direct exteroceptive attention — e.g., "look more closely at #the-arsenal" increases the node selection budget for that Space. This would make exteroception not just passive sensing but active exploration. -->

<!-- @mind:todo The current draft implementation uses raw Cypher queries. The redesigned version needs to work with the query_fn interface already on CitizenCognitiveState._l3_query_fn. Verify the query_fn signature supports parameterized multi-hop traversals. -->
