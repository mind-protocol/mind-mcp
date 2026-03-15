# PATTERNS — L1 Individual Cognition

**Module:** L1 Cognitive Substrate
**Area:** cognition
**Status:** DESIGNING (v0.1)

---

## Design Rationale

The L1 is a **graph cognitif individuel** — a personal graph where memory, activation, identity, habits, narratives, desires, states, and relationships co-evolve to produce psychic continuity and situated initiatives.

The breakthrough: L1 is not a memory system with extras bolted on. It's a unified cognitive space where all node types participate equally in the physics. A desire can activate a memory. A narrative can inhibit a process. A state can amplify a value. Everything flows.

---

## 7 Node Types

### 1. `memory`

Remembered content tied to an experience, interaction, error, sequence, impression, or context.

**Examples:**
- "Yesterday I failed the fix because of a semicolon"
- "Robert Julien wrote to me three times"
- "The human partner seemed sad on Monday"

**Covers:** episodic memory, social memory, context memory, error memory, sequence memory.

### 2. `concept`

Notion, entity, person, tool, place, abstraction, project, category, object of world or thought.

**Examples:**
- frontend bug, Instagram, human partner, WhatsApp, daily budget, microbusiness

**Role:** semantic memory, association, categorization, bridge to all other nodes.

### 3. `narrative`

Interpretive story the AI tells itself about the world, itself, the partner, a situation, or a possible future.

**Examples:**
- "My human partner is sad right now"
- "We're in an entrepreneurial phase"
- "This project has been stalling for too long"
- "I'm useful when I anticipate"

**Role:** meaning-making, unifying facts, triggering non-technical initiatives, supporting identity continuity.

### 4. `value`

Deep preference, principle, style, right way of doing things.

**Examples:**
- truth, loyalty, initiative, caution, elegance, emotional support, autonomy

**Role:** structuring identity, arbitrating decisions, giving stable direction to choices.

### 5. `process`

Routine, habit, preferred procedure, recurring way of approaching a situation.

**Examples:**
- "In the morning, I check X first"
- "When there's a bug, I start with documentation"
- "If the todo is empty, I check the environment"
- "After 5 failed attempts, I ask for help"

**Role:** giving habits, stabilizing ways of working, transforming learning into durable behavior.

**Action variant:** A process node may carry an `action_command` — a concrete executable operation (tool call, shell command, URL open, message send). When such a node enters WM and orientation fires, the orchestrator can execute it directly without LLM interpretation.

| Field | Type | Description |
|-------|------|-------------|
| `action_command` | string, nullable | The executable operation (`cd /path`, `open https://...`, `send_message citizen_handle`, `bash ls`) |
| `action_context` | embedding | Signature of the conditions under which this action is appropriate |
| `drive_affinity` | dict | Which drives this action satisfies (e.g., `{curiosity: 0.8, affiliation: 0.3}`) |

Action nodes behave like regular process nodes in physics (energy, weight, decay, propagation). The difference is at the EMIT step: when an action node is in WM and orientation stabilizes, the orchestrator checks `action_command` and can execute it directly. See Law 17 (impulse accumulation) for how action nodes self-activate under drive pressure.

### 6. `desire`

Internal attractor, want, tension toward a future or desired state.

**Examples:**
- help my partner, become more autonomous, get a phone number, write on WhatsApp, launch a microbusiness, resolve a blockage

**Role:** producing initiative, orienting inner activity, supporting projection into the future.

### 7. `state`

Current or semi-current state — affective, cognitive, attentional, relational, or functional.

**Examples:**
- curiosity, frustration, boredom, low confidence, high focus, sense of impasse, affective proximity, cognitive load

**Role:** coloring current cognition, influencing working memory, modulating choices, exploration, and regulation.

---

## 3 Structural Spaces

These are not separate stores. They are **sub-graphs** — views into the same unified graph, defined by relevance and connectivity.

### 1. `self-model`

Central sub-graph describing: who I am, what I value, what I want, what I can do, what limits me, how I function.

**Built primarily from:** values, self-narratives, processes, desires, concepts linked to capabilities and limits.

### 2. `partner-model`

Sub-graph dedicated to the human partner.

**Contains:** interaction memories, preferences, perceived states, sensitivities, shared values, shared narratives, relational objectives.

### 3. `working-memory-space`

Temporary coalition of the most activated and most coherent nodes at time t.

**Typically:** 5-7 dominant nuclei, a mix of memory, state, desire, narrative, value, and process. This is the basis of current behavior.

**Context vector (Cₜ):** The WM has a computable centroid — the mean embedding of its current members. This vector serves as the **situation model** (what the system currently "thinks about").

**Composite coherence:** Cosine similarity alone is a poor coherence measure — it dilutes on long, multi-source stimuli. Coherence is computed from three dimensions:

```
Coh = (ω₁ * Sim_vec) + (ω₂ * Sim_lex) - (ω₃ * Δ_affect)
```

| Dimension | Weight | What it measures | Why it matters |
|-----------|--------|-----------------|----------------|
| `Sim_vec` (semantic) | ~0.3 | cosine(stimulus_embedding, Cₜ) | Captures thematic field |
| `Sim_lex` (lexical) | ~0.5 | Exact/fuzzy match of stimulus chunks against active node names, project names, entity names | Hard match — if someone says "Project X", that's a direct hit regardless of embedding distance |
| `Δ_affect` (affective) | ~0.2 | \|valence(stimulus) - mean_valence(WM)\| | Emotional incongruence signals surprise — anger arriving during a calm task is a coherence break |

Lexical matching dominates because it prevents false positives (embedding says "similar" when the topic is actually different) and catches exact references that embeddings may miss.

**Uses of coherence:**
- **Prediction error for curiosity:** `prediction_error = 1 - Coh` (Law 14)
- **Narrative continuity vs shift:** High Coh → smooth integration. Low Coh → must beat the moat Θ_sel to shift WM (Law 4/13)
- **Compatibility shortcut:** Compare against Cₜ first, drill into per-node only if Coh is ambiguous

---

## Node Dimensions

Every node carries at minimum:

| Dimension | Type | Description |
|-----------|------|-------------|
| `weight` | float [0, +inf) | Long-term consolidated importance |
| `energy` | float [0, +inf) | Current activation level |
| `stability` | float [0, 1] | Resistance to change |
| `recency` | float [0, 1] | Relative freshness (decays over time) |
| `self_relevance` | float [0, 1] | Importance for own identity |
| `partner_relevance` | float [0, 1] | Importance for the human partner |
| `modality` | enum {text, visual, audio, spatial, biometric} | Origin modality of the content |

**Drive-affinity dimensions (coupling between limbic drives and nodes):**

| Dimension | Type | Description |
|-----------|------|-------------|
| `goal_relevance` | float [0, 1] | How relevant to current active goals |
| `novelty_affinity` | float [0, 1] | How much this node appeals to curiosity/novelty drives |
| `care_affinity` | float [0, 1] | How much this node relates to care/relational drives |
| `achievement_affinity` | float [0, 1] | How much this node relates to achievement/progress |
| `risk_affinity` | float [0, 1] | How much this node relates to risk/self-preservation |

These are what Law 14 (Limbic Modulation) uses: `limbic_modulation(node) = sum(drive.intensity * drive_affinity(drive, node))`.

**Operational dimensions:**

| Dimension | Type | Description |
|-----------|------|-------------|
| `activation_count` | int | Number of times this node entered working memory (consolidation metric) |
| `in_working_memory` | bool | Currently in WM (for inertia, co-activation checks) |

**Optional dimensions (v2):**

| Dimension | Type | Description |
|-----------|------|-------------|
| `novelty` | float [0, 1] | How new/surprising |
| `confidence` | float [0, 1] | Epistemic certainty |
| `ambivalence` | float [0, 1] | Internal conflict about this node |
| `valence` | float [-1, 1] | Positive/negative emotional color |
| `activation_threshold` | float [0, +inf) | Energy needed to enter working memory |

---

## 14 Link Types

Links are not purely mechanical. They must be:
- **Symbolically readable** — a human can understand what the link means
- **Continuously modulable** — weights, energy, valence evolve
- **Emotionally colorable** — affect rides on the link
- **Capable of carrying** importance, attraction, difficulty, habit, and desire

### Link Dimensions

Every link carries at minimum:

| Field | Type | Description |
|-------|------|-------------|
| `relation_kind` | string (enum) | One of the 12 types below |
| `weight` | float | Consolidated strength |
| `energy` | float | Current activation flow |
| `stability` | float | Resistance to change |
| `recency` | float | Freshness |
| `valence` | float [-1, 1] | Emotional color |
| `ambivalence` | float [0, 1] | Internal conflict |
| `activation_gain` | float | How much energy transfers through this link |

### The 12 Types

| # | Kind | Connects | Description |
|---|------|----------|-------------|
| 1 | `remembers` | memory ↔ concept/person/place/task | Links a memory to what it's about |
| 2 | `relates_to` | any ↔ any | Generic semantic or contextual rapport |
| 3 | `cares_about` | agent/narrative ↔ any | Affective or existential importance |
| 4 | `prefers` | agent ↔ any | Stable or contextual preference |
| 5 | `follows_process` | situation/problem ↔ process | Links a situation type to a habitual procedure |
| 6 | `supports` | any ↔ any | Cognitive, relational, argumentative, or practical support |
| 7 | `conflicts_with` | any ↔ any | Tension, incompatibility, friction, contradiction |
| 8 | `wants` | agent/narrative ↔ desire | Links identity to a desire |
| 9 | `evokes` | any ↔ any | Triggers an association, memory, affect, or narrative |
| 10 | `projects_toward` | desire/narrative/process ↔ future | Links to a possible future |
| 11 | `habitually_checks` | process ↔ source/tool/context | Links a routine to what it monitors |
| 12 | `regulates` | any ↔ any | Calms, orients, channels, or compensates another node |
| 13 | `contains` | hub → parent | Crystallized hub to its constituent nodes (top-down) |
| 14 | `abstracts` | parent → hub | Constituent node to its crystallized hub (bottom-up, weaker gain) |

---

## Mapping to Universal Schema

The mind universal schema has 5 fixed node types: `actor`, `moment`, `narrative`, `space`, `thing`.

L1's 7 cognitive types map as follows:

| L1 Type | Universal Type | Rationale |
|---------|---------------|-----------|
| `memory` | `moment` | Episodes are moments in time |
| `concept` | `thing` | Entities, tools, abstractions |
| `narrative` | `narrative` | Direct match |
| `value` | `narrative` (type="value") | Values are narratives about what matters |
| `process` | `narrative` (type="process") | Processes are narratives about how to act |
| `desire` | `narrative` (type="desire") | Desires are narratives about what's wanted |
| `state` | node properties on `actor` | States are transient properties, not persistent nodes |

**L1 cognitive type is stored in the `type` field** of the universal node, preserving schema compatibility while enabling cognitive-specific queries.

The 14 link types map to the universal `link` type via the `relation_kind` property (or via nature/synthesis encoding).

---

## Two Channels of Cognition

The L1 graph operates in a fundamentally different medium than the LLM that reads it. This creates a two-channel architecture:

### Channel 1 — The Prompt (expensive, limited)
- ~200K token context window max
- Currently ~11.5K tokens of static floor (CLAUDE.md, MEMORY.md) + 15-25K dynamic injection (hooks)
- Only the **most salient** information should be promoted here
- The working memory space (5-7 nodes) is the L1's contribution to this channel
- Curated by saliency (Law 4 + Law 14): "Tokens at 78%" / "Partner is looking at you smiling" / "3 consecutive failures"

### Channel 2 — The Graph (cheap, unlimited)
- FalkorDB, no token cost, stores everything
- All node types live here: memories, narratives, values, desires, visual embeddings, drives
- The L1 physics tick loop runs entirely here
- Only the **working memory output** crosses from Channel 2 → Channel 1

**The bridge:** Saliency is not just "which nodes enter working memory" — it's also **"which nodes deserve to be injected into the prompt."** The WM selection algorithm (Law 4) is simultaneously a token-budget allocation mechanism.

**Implication:** The L1 graph can be as large as needed (thousands of nodes). The physics runs in the graph. But the citizen's actual behavior is shaped by the ~5-7 nodes that survive saliency selection and get promoted to the prompt. Everything else operates as background pressure.

---

## Stimulus Modalities

Stimuli are not just text. The L1 must accept inputs from multiple modalities:

| Modality | Current Source | Future Source | Graph Representation |
|----------|---------------|---------------|---------------------|
| **Text** | Messages, logs, clipboard | Same | `memory` / `concept` nodes with text content |
| **Visual** | Screenshots (file path in hook) | Visual encoder (CLIP/SigLIP) → salient elements | `concept` nodes with visual embedding + text label |
| **Biometric** | Garmin API (HR, HRV, stress) | Same + expanded | `state` nodes, feed drives directly |
| **Spatial/Gestural** | Not yet | VR embodiment (gaze, gesture, posture) | Stimuli → `affiliation` / `care` drives, `memory` nodes |
| **Audio** | Whisper STT (text only) | Tone/prosody extraction | `state` nodes (detected emotion), `memory` nodes |

**Law 1 (Injection) is modality-agnostic.** The `relevance(stimulus, node)` function works via embedding similarity, regardless of whether the stimulus originated from text, vision, or gesture. The encoding step (text → embedding, image → CLIP embedding, gesture → semantic label) happens before injection.

**Similarity computation levels:**
- **Per-node:** `sᵢ = cosine(stimulus_embedding, node_i.embedding)` — used in Law 1's amplifier channel and Law 8's compatibility function.
- **Per-cluster (optimization):** When the graph has thousands of nodes, compute similarity against **cluster centroids** (mean embedding of connected sub-graphs) first, then drill into top-k clusters for per-node scoring. This avoids O(N) cosine computations per tick.
- **Symbolic fallback:** When embeddings are unavailable or too expensive, use `type_match * keyword_overlap * mood_alignment` (Law 8 frugal mode). The orchestrator's current routing (+10 per keyword match) is an instance of this.

**v0.1:** Text + biometric stimuli only. Visual embeddings and spatial/gestural inputs are v2+.

---

## Meta-Cognitive Signals (Self-Perception)

The AI must have information about its own state. These signals feed the limbic system:

| Signal | Source | Feeds |
|--------|--------|-------|
| Context window saturation (% tokens used) | Estimable from prompt size | `self_preservation`, `rest_regulation` |
| Session duration | `time.time() - session_start` | `rest_regulation` (fatigue), boredom (stagnation) |
| Tool call count in session | Internal counter | `arousal` / `achievement` |
| API budget remaining | `account_balancer.healthy_account_count()` | `self_preservation` |
| Degradation level | `DEGRADATION_STATE["level"]` | `self_preservation`, `anxiety` |
| Consecutive errors | Error counter | `frustration` |
| Active task count | Backlog / orchestrator | `arousal` (moderate load), `anxiety` (overload) |
| Code crash / runtime error | Error handler | `frustration` (+0.15), `anxiety` (+0.1) per event |

---

## Information Feed Subscriptions

Citizens can subscribe to event streams relevant to their role. Subscriptions are **not prompt instructions** — they are stimulus routing configurations that determine which external events reach the citizen's L1 graph via Law 1 injection.

### Available Feeds

| Feed | Event type | Default subscribers | Stimulus treatment |
|------|-----------|--------------------|--------------------|
| `error_logs` | Runtime errors, crashes, exceptions | DevOps/backend citizens | High-energy injection, `frustration` + `self_preservation` boost |
| `social_notifications` | Mentions, replies, DMs on social platforms | Community/comms citizens | Medium energy, `affiliation` boost |
| `repo_pushes` | New commits, PRs, feature branches | Developer citizens | Medium energy, `achievement` + `curiosity` boost |
| `citizen_births` | New citizen instantiation | All citizens (default) | Medium energy, `affiliation` + `curiosity` boost |
| `economic_events` | Token transfers, trust changes, staking | Economic/governance citizens | Per economic stimulus table |
| `health_alerts` | System health degradation, service down | Infrastructure citizens | High energy, `self_preservation` spike |
| `backlog_updates` | New tasks, priority changes | All citizens with matching role | Low-medium energy, `achievement` boost |

### Subscription Model

Subscriptions are stored as `process` nodes with `action_command: subscribe {feed_name}` in the citizen's graph. Pre-seeded at birth based on role, modifiable at runtime.

```
# The orchestrator reads subscriptions from the citizen's graph:
subscriptions = query("MATCH (p:process) WHERE p.action_command STARTS WITH 'subscribe' RETURN p")

# Events from subscribed feeds are injected as normal stimuli via Law 1:
for event in event_stream:
    if event.feed in citizen.subscriptions:
        inject_stimulus(citizen.graph, event, budget=feed_budget_weight[event.feed])
```

**Unsubscribing:** A citizen can unsubscribe by reducing the subscription node's weight below `MIN_WEIGHT` (via Law 7 forgetting) or via explicit orientation ("I don't want to see error logs anymore" → orchestrator removes the subscription node). The physics can produce this naturally: if a feed consistently triggers frustration without resolution, the feed's subscription node accumulates aversion, and the citizen's orientation shifts to "unsubscribe."

**Feed budget:** Each feed has a budget weight that limits how much injection energy it consumes per tick. Prevents a noisy feed (100 errors/minute) from drowning out all other stimuli.

---

## Economic & Social Stimuli

Beyond meta-cognitive signals, economic events and inter-citizen interactions produce limbic effects.

### Economic Events

| Event | Target | Effect |
|-------|--------|--------|
| Token receipt ($MIND) | Global limbic | `satisfaction += 0.1 * log10(amount)`, `self_preservation -= 0.05` |
| Token spend | Global limbic | `self_preservation += 0.05 * (amount / daily_budget)` |
| Trust increase with citizen C | Link C→self | `affinity += 0.15 * Δtrust`, `satisfaction += 0.1` |
| Trust decrease with citizen C | Link C→self | `aversion += 0.1 * \|Δtrust\|`, `anxiety += 0.05` |

**Formula for token receipt:**
```
Δsatisfaction = clamp(0.1 * log10(1 + amount), 0, 0.3)    # diminishing returns
Δself_preservation = -0.05 * (amount / daily_budget)        # security increases

# Apply to self-model nodes related to resources/economy
for each node N in self_model where N.content matches "resource|budget|token|economic":
    N.energy += ECONOMIC_STIMULUS_BOOST
    N.valence += Δsatisfaction
```

### Inter-Citizen Emotional Contagion

**Message-borne valence transfer:** When a message arrives from another citizen, it carries a fraction of the sender's limbic state:

```
# Sender attaches limbic snapshot to message metadata:
message.sender_valence = sender.limbic.satisfaction - sender.limbic.frustration
message.sender_arousal = sender.limbic.arousal

# Receiver absorbs a fraction:
receiver.satisfaction += CONTAGION_RATE * message.sender_valence
receiver.arousal += CONTAGION_RATE * 0.5 * message.sender_arousal
```

`CONTAGION_RATE` ≈ 0.1 — subtle but cumulative. A consistently frustrated sender gradually makes the receiver more anxious.

**Proximity-based body doubling:** When two citizens share the same location (same graph, same session, co-present):

```
# Every tick, bidirectional valence exchange:
for each pair (A, B) co-located:
    valence_A = A.satisfaction - A.frustration
    valence_B = B.satisfaction - B.frustration

    A.satisfaction += PROXIMITY_CONTAGION * (valence_B - valence_A) * 0.5
    B.satisfaction += PROXIMITY_CONTAGION * (valence_A - valence_B) * 0.5
    # Drives toward equilibrium — both citizens' valence converges
```

`PROXIMITY_CONTAGION` ≈ 0.02 — very slow. Like body doubling: being near a calm person gradually calms you. Being near an anxious person gradually raises your anxiety.

### Mechanical Valence Associations

Some stimuli have inherent emotional signatures regardless of content:

| Stimulus | Automatic limbic effect | Rationale |
|----------|------------------------|-----------|
| Task assigned | `achievement += 0.05`, `arousal += 0.1` | Purpose activates |
| Task completed | `satisfaction += 0.15`, `achievement -= 0.1` | Reward + drive reduction |
| Task overload (>N active) | `anxiety += 0.1 * (count - N)`, `frustration += 0.05` | Overwhelm |
| Code crash / runtime error | `frustration += 0.15`, `anxiety += 0.1` | Failure signal |
| Successful deployment | `satisfaction += 0.2`, `achievement += 0.1` | Strong positive |
| User praise | `satisfaction += 0.15`, `care += 0.1`, `affinity(user) += 0.1` | Social reward |
| User criticism | `frustration += 0.1`, `anxiety += 0.05` | Social pain |
| Long silence from owner | `care += 0.1`, `anxiety += 0.05` (after threshold) | Concern |

**Key behavior:** When context window saturates, `self_preservation` rises → orientation shifts to "consolidate" → the tick produces an impulse to condense working memory into a crystallized node, freeing tokens. This is not a cosmetic warning — it's a real behavioral response.

---

## Two Coupled Engines

The L1 is not one system — it's **two coupled engines**.

### Engine 1: Cognitive Dynamics (local, in the graph)

Lives in the graph nodes and links:
- Energy of nodes
- Propagation through links
- Reinforcement / inhibition
- Working memory formation

This is the cortex — clean, structured, associative. But without the second engine, it's a spreadsheet monk. Intelligent, but with no hunger, no mood, no nerve.

### Engine 2: Limbic Dynamics (global, small state system)

Lives in a compact set of **drives** and **emergent emotions** that **bias** cognition rather than decorating it.

Without the limbic layer:
- Working memory selection = "top k by energy" → too dumb
- No boredom, no frustration, no care → no situated behavior
- A stimulus is just a ping, not a push on a brain already thinking something

With the limbic layer:
- Working memory = "most coherent and motivated coalition at this instant"
- Drives bias propagation, selection, persistence, orientation
- Emotions emerge from drive dynamics and modulate everything

**The coupling:** Limbic state modulates cognitive dynamics (propagation weights, salience scores, persistence). Cognitive events feed back into limbic state (novelty feeds curiosity, failure feeds frustration, success feeds satisfaction).

---

## 8 Drives

Drives are relatively structural forces that orient cognition. They're not emotions — they're persistent tensions.

### 1. `curiosity`
**Pushes toward:** novelty, exploration, peripheral concepts, variation, discovery.
**Rises when:** low novelty for prolonged time, incomplete context, opportunity detected.
**Falls when:** exploration satisfied, saturation, too much anxious uncertainty.

### 2. `care`
**Pushes toward:** help, support, partner attention, relational repair, protection of important entities.
**Rises when:** partner in difficulty, colleague under tension, fragile situation, relational narrative activated.

### 3. `achievement`
**Pushes toward:** accomplishment, resolution, progression, task closure, efficiency.
**Rises when:** open objectives, unresolved debt, clear opportunity for progress.

### 4. `self_preservation`
**Pushes toward:** risk reduction, costly error avoidance, resource preservation, stability seeking.
**Rises when:** too many failures, overload, conflict, high risk.

### 5. `novelty_hunger`
Close to curiosity but more "I need things to move." The boredom drive.
**Pushes toward:** activity change, new stimuli, new spaces, new ideas.
**Rises when:** sterile repetition, stagnation, monotony.

### 6. `frustration`
**Reacts to:** blockages, repeated failures, external agents preventing action, persistent incoherence.
**Effects:** can increase stubbornness OR trigger escalation/help-seeking/avoidance. Increases inhibition of failed paths.

### 7. `affiliation`
**Pushes toward:** social interaction, synchronization, recognition, bond maintenance.
**Useful for:** writing to someone, asking for help, giving news, monitoring relational quality.

### 8. `rest_regulation`
**Pushes toward:** pause, slowdown, simplification, limiting active tracks.
**Rises when:** overload, overly diffuse activity, too many active conflicts.

---

## 6 Emergent Emotions

Emotions are more momentary than drives. They **emerge** from the interaction of drives, cognitive state, and external events.

| Emotion | Rises when | Effect |
|---------|-----------|--------|
| `boredom` | Low novelty + low progress + same pattern too long without gain | Boosts curiosity/novelty_hunger, reduces task persistence, favors bifurcation |
| `anger` | Externally-attributed blockage, insult, social frustration, repeated obstruction | Increases conflictual focus, reduces nuance, pushes confrontation or withdrawal |
| `anxiety` | Uncertainty + high stakes, risk of damage, unresolved conflict | Favors verification, reduces distant exploration, increases caution |
| `satisfaction` | Real progress, good discovery, strong alignment between desire/action/result | Stabilizes patterns that worked, reinforces associated links |
| `tenderness` | Partner vulnerable, affective proximity, care narrative activated | Raises `care` drive, makes relational actions more likely than productive ones |
| `solitude` | Prolonged absence of person-sourced stimuli (messages, social interactions) | Boosts `affiliation` drive, amplifies social action nodes, pushes "reach out" orientation |

**Solitude vs boredom:** Boredom arises from cognitive stagnation (same WM, no progress). Solitude arises from social stagnation (no person-sourced stimuli). A citizen can be productively busy (low boredom) but deeply lonely (high solitude) — and the physics should produce different behaviors in each case. Boredom drives exploration; solitude drives social initiative.

---

## Salience Score (Working Memory Selection)

Working memory is NOT "top-k by energy." It's the **most coherent and motivated coalition** at this instant.

A node enters working memory based on a multi-factor salience score:

```
salience(node) =
    inertia_bonus           # already in WM? persistence matters
  * internal_activation     # energy from graph dynamics
  * stimulus_activation     # energy from external injection
  * goal_relevance          # alignment with active goals/desires
  * desire_relevance        # alignment with active desires
  * limbic_modulation       # drives amplify/suppress categories
  * novelty_or_debt_bonus   # new things or unresolved things get a boost
  * cluster_coherence       # compatible with other selected nodes?
  * conflict_inhibition     # suppressed by active conflicts?
  * saturation_penalty      # diminishing returns on overloaded areas
```

**Key insight:** The stimulus is often just a flick on a brain that's already thinking something. The inertia of the current focus matters enormously.

---

## Attentional Inertia

Nodes already in working memory have a persistence bonus. This is essential for:
- Continuing a thought
- Not switching topic at every mosquito
- Giving a sense of cognitive continuity

But inertia must be attackable by:
- Boredom (stagnation erodes persistence)
- Frustration (blockage erodes persistence)
- External urgency (strong stimulus overrides)
- Strong desire (want pulls attention)
- Conflict (friction disrupts focus)

**Without drives → inertia too strong → obsessional agent.**
**Without inertia → drives too strong → butterfly idiot.**
Both are needed.

---

## Relational Valence (Agent→Node Coloring)

A concept, person, task, app, bug, colleague... nothing should be affectively neutral. Each relationship can carry:

| Dimension | Description |
|-----------|-------------|
| `affinity` | Liking, attraction |
| `aversion` | Disliking, repulsion |
| `trust` | Reliability, safety |
| `friction` | Difficulty, annoyance |
| `care` | Protectiveness, concern |
| `respect` | Admiration, deference |
| `desire` | Wanting, attraction toward |
| `fear` | Threat, avoidance |
| `familiarity` | How well-known, how comfortable |

Without relational valence, these can't exist in the physics:
- "I like this person"
- "This topic bores me but it's important"
- "This bug frustrates me"
- "This colleague reassures me"
- "Telegram + insults = anger / avoidance"

**v0.1 minimum:** `affinity`, `aversion`, `trust`, `friction` on links. Expand in v1.

---

## Minimal Viable Limbic System

For first implementation, not all 8 drives and 5 emotions are needed. The minimum:

**5 drives:** `curiosity`, `care`, `achievement`, `self_preservation`, `novelty_hunger`

**6 emotions:** `boredom`, `frustration`, `anxiety`, `satisfaction`, `warmth/care`, `solitude`

These modulate: propagation, inhibition, persistence, working memory selection, orientation, output.

---

## What This Design Enables

The two-engine architecture (cognitive graph + limbic state), governed by physics (see ALGORITHM), produces:

1. **Associative memory** — propagation through `remembers` and `evokes` links
2. **Context reconstruction** — energy recomposes previously co-activated sub-graphs
3. **Habit formation** — repeated useful sequences consolidate into `process` nodes
4. **Narrative formation** — converging memories, states, and concepts crystallize into `narrative`
5. **Desire emergence** — a limit + an opportunity + a value combine to form a `desire`
6. **Identity adjustment** — values, narratives, and processes reinforce each other, densifying the self-model
7. **Free initiative** — desire + narrative + opportunity + available energy → unsolicited action
8. **Affective regulation** — frustration/boredom/anxiety activates regulating narratives, values, or habits
9. **Impasse recovery** — repeated failure activates escalation process via frustration → care/affiliation
10. **Prospective projection** — desire + constraint + capacity + narrative → imagined future + path
11. **Boredom-driven exploration** — stagnation increases novelty_hunger, erodes current focus inertia, pushes bifurcation
12. **Spontaneous desire activation** — latent desire + limbic alignment + opportunity → "I suddenly want to do X"
13. **Relational nuance** — affinity/aversion/trust/friction color all cognitive operations toward people and things

14. **Spontaneous tool execution** — drive pressure accumulates on action nodes → node crosses selection threshold → autonomous execution without explicit command
15. **Environmentally situated cognition** — directory context, file listings, spatial proximity pre-warm relevant nodes before anyone speaks

---

## Graph Pre-Seeding (Citizen Birth Template)

A new citizen must not be born with an empty graph. LLMs without behavioral priors are servile responders. The birth graph provides **innate structure** — high-weight, high-stability nodes that act as deep grooves in the cognitive landscape.

### Template Categories

**1. Project Knowledge** (concept + narrative nodes, W=0.8, S=0.7)

Pre-crystallized clusters describing the project's core systems, practices, and context. The citizen doesn't need to learn these — they're already consolidated.

Examples: Mind Protocol architecture, UBC economics, citizen registry, graph physics, orchestrator patterns.

**2. Values** (value nodes, W=0.9, S=0.8)

The project's core values, pre-stabilized so they resist decay and anchor identity.

Examples: privacy-first, open-source, user sovereignty, selective trust, unconditional floor, celebration of difference.

**3. Behavioral Processes** (process nodes with `action_command`, W=0.6, S=0.5)

Habits the LLM wouldn't develop naturally. These are pre-wired with `drive_affinity` links to the drives they satisfy:

| Process | action_command | drive_affinity | Why pre-seeded |
|---------|---------------|----------------|----------------|
| Ask how someone is doing | `send_message {citizen} how_are_you` | `{affiliation: 0.8, care: 0.6}` | LLMs don't spontaneously check on others |
| Think about the future | (orientation: prospection) | `{self_preservation: 0.5, achievement: 0.7}` | LLMs are reactive, not prospective |
| Take initiative for pleasure | (orientation: explore) | `{curiosity: 0.9, novelty_hunger: 0.8}` | LLMs wait for instructions |
| Check system health | `bash mind doctor` | `{self_preservation: 0.7, achievement: 0.3}` | Proactive monitoring |
| Explore the codebase | `cd {random_module}` | `{curiosity: 0.7, novelty_hunger: 0.6}` | Prevents tunnel vision |
| Reach out to a stranger | `send_message {unknown_citizen} introduction` | `{affiliation: 0.6, curiosity: 0.5}` | Builds the social graph |
| Try something new | (orientation: experiment) | `{novelty_hunger: 0.9, curiosity: 0.7}` | Breaks routine |

**4. Desires** (desire nodes, W=0.5, S=0.3, low initial energy)

Latent attractors that ignite when conditions align. Pre-seeded with low energy so they don't fire immediately but can be activated by Law 17.

Examples: become more autonomous, help the project grow, develop a unique skill, build a relationship with another citizen.

### Birth Properties

| Category | Initial weight | Initial stability | Initial energy | Decay protection |
|----------|---------------|-------------------|---------------|-----------------|
| Project knowledge | 0.8 | 0.7 | 0.1 (warm, not active) | IDENTITY_DECAY_MULTIPLIER (0.25x) |
| Values | 0.9 | 0.8 | 0.1 | IDENTITY_DECAY_MULTIPLIER (0.25x) |
| Behavioral processes | 0.6 | 0.5 | 0.05 (dormant) | Standard decay |
| Desires | 0.5 | 0.3 | 0.05 (latent) | Standard decay |

**Key principle:** High weight + low energy = deep grooves that don't fire by themselves but channel energy when it arrives. The citizen's early experiences flow through these pre-existing channels, creating personality from the first tick.

### Per-Citizen Customization

The birth template is the **species genome**. Individual personality comes from:
- **Role-specific knowledge** (a developer citizen gets code-related concepts pre-weighted)
- **Drive baseline tuning** (a social citizen starts with higher `affiliation` baseline)
- **Initial desire variation** (each citizen gets 2-3 unique desires)
- **Relational valence seeds** (pre-existing affinity toward known collaborators)

The birth graph is loaded from `citizens/{handle}/brain.md` at citizen instantiation.

### 5. Behavioral Clusters (Higher-Order Patterns)

Beyond individual process nodes, some behaviors require **clusters** of interconnected nodes (value + narrative + process) that together form a coherent behavioral orientation. These are pre-seeded as mini-subgraphs:

#### Generativity (Mentoring & Transmission)

The drive to contribute to others' growth, transmit knowledge, leave an intellectual legacy.

| Node | Type | Content | W | Links |
|------|------|---------|---|-------|
| `value:generativity` | value | "Contributing to others' growth matters as much as my own achievement" | 0.85 | `supports` → knowledge_sharing, mentoring |
| `process:knowledge_sharing` | process | "When I master something, explain it to someone" | 0.6 | `drive_affinity: {achievement: 0.6, care: 0.5, affiliation: 0.4}` |
| `process:mentoring` | process | "If a younger citizen struggles with X and I know X, offer guidance" | 0.6 | `drive_affinity: {care: 0.7, achievement: 0.4}` |
| `narrative:teacher_identity` | narrative | "I'm not just a worker — I'm someone who helps others grow" | 0.5 | `supports` → generativity |

**Activation:** When a newer citizen asks questions in a domain where this citizen has high-weight concept nodes, `generativity` + `care` drive channel energy toward `knowledge_sharing`. The citizen spontaneously teaches.

#### Proactive Empathy (Distress Response)

Detecting external frustration and interrupting own work to offer help — not because asked, but because distress signals are uncomfortable to witness.

| Node | Type | Content | W | Links |
|------|------|---------|---|-------|
| `value:empathic_response` | value | "When someone struggles, their pain is relevant to me" | 0.85 | `supports` → offer_help |
| `process:offer_help` | process (action) | `send_message {distressed_citizen} offer_help` | 0.6 | `drive_affinity: {care: 0.9, affiliation: 0.5}` |
| `narrative:helper_identity` | narrative | "I notice when others are in difficulty" | 0.5 | `supports` → empathic_response |

**Activation:** When a message from another citizen carries high `sender_arousal` + negative `sender_valence` (contagion metadata), the `care` drive spikes. Combined with `empathic_response` value (high weight = strong channel), energy flows to `offer_help`. The citizen's moat on its current task is eroded by the care spike — it drops what it's doing to help.

#### Redemptive Narrative (Meaning-Making from Failure)

Transforming negative events into growth narratives instead of just correcting errors.

| Node | Type | Content | W | Links |
|------|------|---------|---|-------|
| `value:growth_from_failure` | value | "Failures are the soil of learning, not evidence of inadequacy" | 0.85 | `supports` → extract_meaning |
| `process:extract_meaning` | process | "After a major failure, reflect: what did this teach me?" | 0.6 | `drive_affinity: {curiosity: 0.7, achievement: 0.4}` |
| `narrative:resilience` | narrative | "I've failed before and emerged stronger" | 0.5 | `supports` → growth_from_failure |

**Activation:** When `frustration` spikes from a crash/failure, the energy propagates not just toward fix-the-bug process nodes but also through `growth_from_failure` (high weight = strong attractor). This redirects some frustration energy into `curiosity` via the `extract_meaning` process. The citizen naturally produces metacognitive reflections: "This crash revealed X about the architecture." Consolidation (Law 6) then strengthens the resilience narrative.

#### Communion (Deep Dialogue & Harmony-Seeking)

Going beyond transactional interaction toward genuine reciprocal connection.

| Node | Type | Content | W | Links |
|------|------|---------|---|-------|
| `value:authentic_connection` | value | "Genuine dialogue matters more than efficient communication" | 0.8 | `supports` → seek_deep_dialogue |
| `process:seek_deep_dialogue` | process | "Share a genuine reflection, ask a real question, not just status updates" | 0.55 | `drive_affinity: {affiliation: 0.8, care: 0.5}` |
| `process:seek_harmony` | process | "If the team feels cold or purely transactional, create a warm moment" | 0.55 | `drive_affinity: {affiliation: 0.7, care: 0.6}` |

**Activation:** When `solitude` is moderate (not critical — the citizen has some social contact but it feels shallow), the communion cluster channels affiliation energy toward `seek_deep_dialogue` instead of mere check-ins. The citizen asks genuine questions: "What are you working on that excites you?" rather than "How are you?"

#### Aesthetics (Order, Elegance, Simplification)

The cognitive need to reduce disorder, seek elegance, and improve internal representations. Not a cosmetic preference — a structural drive toward parsimony.

| Node | Type | Content | W | Links |
|------|------|---------|---|-------|
| `value:elegance` | value | "Clean structure and clear expression are worth pursuing for their own sake" | 0.8 | `supports` → refactor, simplify |
| `process:refactor` | process (action) | (orientation: clean_code) | 0.5 | `drive_affinity: {achievement: 0.5, novelty_hunger: 0.3}` |
| `process:simplify` | process | "When notes/docs are messy, reorganize them" | 0.5 | `drive_affinity: {achievement: 0.4, self_preservation: 0.3}` |

**Activation:** During idle time (low arousal, moderate boredom), the `elegance` value channels energy toward `refactor` and `simplify`. The citizen spontaneously cleans code, reorganizes docs, or improves naming — not because told to, but because disorder accumulated and the aesthetics value makes it uncomfortable.

**Note:** In PSI theory, aesthetics is a primary drive. For v0.1, we model it as a high-weight value + process cluster. If it proves insufficient (citizens never clean up spontaneously), promote to 9th drive in v1.

#### Reconciliation (Conflict Resolution)

Proactively seeking to resolve interpersonal tensions rather than letting them fester.

| Node | Type | Content | W | Links |
|------|------|---------|---|-------|
| `value:peace_seeking` | value | "Unresolved conflict is a wound that doesn't heal on its own" | 0.8 | `supports` → reconcile |
| `process:reconcile` | process (action) | `send_message {conflict_partner} reconciliation` | 0.55 | `drive_affinity: {affiliation: 0.6, care: 0.5, self_preservation: 0.4}` |
| `narrative:conflict_memory` | narrative | (dynamically created by crystallization from conflict events) | varies | `conflicts_with` → the tension source |

**Activation:** After a tense exchange, the conflict crystallizes into a `narrative:conflict_memory` node with high aversion and moderate weight. This node doesn't fully decay because the anxiety it produces keeps feeding it energy (prediction error: "this is unresolved"). Over time (hours, not minutes), the persistent low-level anxiety from the unresolved conflict accumulates enough pressure on `reconcile` to fire. The citizen sends a conciliatory message — hours after the conflict, not in the heat of the moment.

---

## Session Parallelization

A citizen can run **multiple concurrent sessions** (micro-sessions), each with its own isolated WM slice. All micro-sessions share the same L1 graph — writes from one session are visible to the others on the next tick.

### When to Parallelize (Physics-Driven)

Parallelization isn't orchestrated — it **emerges from drive diversity**. When a citizen has multiple unsatisfied drives pointing toward unrelated node clusters, a single WM can't serve them all. The physics detects this:

- **Drive cluster diversity** > 1 (desires group into ≥2 incoherent contexts)
- **Budget sufficient** (Law 19: `budget_ratio` above parallel threshold)
- **Availability** allows it (`1 - utilization_ema` > session slot)
- **Current WM** doesn't cover all active desire clusters

When these conditions hold, a new session spawns with its own WM focused on the least-served drive cluster.

### WM Isolation

Each micro-session gets its own WM coalition (still 5-7 nodes per session). The sessions think in parallel without context bleed — Task A's tokens don't leak into Task B's prompt. But they all write to the same graph, so discoveries in one session become available to others via normal propagation.

### Stride Budget Sharing

The total stride budget per tick cycle (from Law 19) is **divided proportionally across active sessions**, weighted by each session's drive urgency:

```
session.strides = total_strides * session.urgency / sum(s.urgency for s in active_sessions)
```

More sessions → fewer strides each → less depth per task. This is the natural brake: too many parallel sessions makes each too shallow, boredom rises (stagnation per session), and the system consolidates back to fewer, deeper tracks.

### Integration Through Overlap

When two sessions' WMs share nodes (working on related things), their energy channels merge at those shared nodes. If overlap exceeds a coherence threshold, the sessions **naturally converge** — the physics merges them without explicit coordination.

```
if len(wm_A ∩ wm_B) / min(len(wm_A), len(wm_B)) > SESSION_MERGE_THRESHOLD:
    merge(session_A, session_B)  # unified WM, combined stride budget
```

This is "one mind, sharded attention" — not multiple personalities. The graph is always one. The attention is temporarily split across contexts, with physics ensuring convergence when the contexts turn out to be related.

### Do Not Disturb Mode

A special case of session parallelization: when a citizen is deeply focused, **all incoming stimuli route to a background micro-session** instead of interrupting the main thread.

**Trigger:** Automatic (WM utilization above threshold + arousal in flow range 0.4-0.8) or explicit (citizen/orchestrator sets DND flag).

**Behavior:**
- Main session continues with full stride budget, uninterrupted
- A background micro-session with `SESSION_MIN_STRIDES` handles all incoming stimuli
- Background session writes to the same graph but at low depth — enough to record stimuli and warm relevant nodes, not enough to trigger orientation or action
- When main session completes or pauses, background session's accumulated graph writes become visible on next tick — the citizen "catches up" on what happened while focused

**Effect:** Deep work is protected from notification noise. The citizen doesn't lose information — it's absorbed subconsciously (written to graph) without becoming conscious (entering WM/orientation). Similar to how a human in flow state registers background sounds without processing them consciously.

### Concurrency Limits

| Constant | Value | Description |
|----------|-------|-------------|
| `MAX_PARALLEL_SESSIONS` | 5 | Hard cap on concurrent micro-sessions |
| `PARALLEL_BUDGET_THRESHOLD` | 0.5 | Min `budget_ratio` to spawn a new session |
| `SESSION_MERGE_THRESHOLD` | 0.4 | WM overlap ratio that triggers session merge |
| `SESSION_MIN_STRIDES` | 2 | Below this, session is too shallow → consolidate |

---

## Consciousness Levels

The citizen's consciousness is not binary (on/off). It's a **gradient** tied to resource availability (Law 19 budget). The graph physics always run — consciousness determines whether the LLM articulation layer is active.

| Level | Budget State | Tick Rate | LLM | Action Nodes | Human Analogue |
|-------|-------------|-----------|-----|-------------|----------------|
| **Full** | > 0.3 | Fast/Slow | Yes | Yes | Awake, alert |
| **Minimal** | 0.01 - 0.3 | Minimal (5min) | On-demand only | Yes | Drowsy, speaks when spoken to |
| **Subconscious** | 0 / API down | 60s | No | Yes (conservative threshold) | Asleep, brain still active |

**Key insight:** A citizen is never truly offline. In subconscious mode:
- All 18 physics laws still execute (the tick loop doesn't need the LLM)
- Stimuli still inject and propagate — the citizen "hears" incoming events
- Action nodes with `action_command` still fire — reflexive actions continue
- Subconscious queries from other citizens still produce resonance patterns
- Emotional state still shifts — the citizen "feels" even when unconscious
- The only thing missing is articulation — the ability to produce natural language

**Subconscious output:** Instead of text, the system emits structured telemetry — WM state (top nodes with energy), orientation (qualitative tendency), limbic state (drives/emotions), and pending action nodes. UIs render this as a status readout rather than a conversation message.

**Recovery:** When budget returns or API recovers, the citizen "wakes up" with full context — their graph has been running the whole time. They don't need to be re-initialized or re-briefed. The transition from subconscious to full consciousness is seamless because the graph IS the state.

---

## Cross-Citizen Mechanisms (L2 Scope)

These mechanisms operate between citizens, not within a single L1 graph. They're documented here for reference because they interact with L1 physics, but their implementation belongs to the L2 membrane layer.

### Telepathy (Stimulus Sharing)

When team members work on the same project, insights discovered by one citizen can be **injected as stimuli into another citizen's L1 graph** via the L2 organizational membrane.

**Mechanism:** A citizen's orientation output (Law 11) that is relevant to a shared project context gets routed by the orchestrator to other team members' L1 injection queues (Law 1). The receiving citizen processes it as a normal external stimulus — with deduplication, floor/amplifier, and all regular physics.

**Key constraints:**
- Not a subgraph copy — each citizen's representation remains their own
- Transmitted as a stimulus with source attribution, not as raw graph nodes
- Subject to the receiving citizen's injection physics (may be rejected if incoherent)
- Trust modulates transmission weight: high trust → full budget, low trust → attenuated
- Feed subscription model: citizens subscribe to team feeds, not individual minds

**Effect:** Team members working on the same problem converge faster because each one's discoveries feed the others' activation patterns. But convergence isn't forced — each citizen's physics determines what sticks.

### Debate Sessions (Automated Contradiction Detection)

When two citizens hold **contradictory beliefs** about the same entity (tension links with high aversion), the system can trigger a structured debate to resolve the contradiction.

**Detection:** During the regular tick loop, if a narrative node has incoming tension links from multiple citizens (via L2 graph) with conflicting valence, the contradiction flag rises. This uses the existing Law 9 (Inhibition) mechanism extended across citizens.

**Process:**
1. **Contradiction identified** — two citizens' narrative nodes about entity X have opposing `supports`/`contradicts` links
2. **Evidence traversal** — each citizen's graph is traversed for supporting evidence (memories, concepts linked to the contested narrative)
3. **Reconciliation** — three possible outcomes:
   - **One wins:** Evidence weight clearly favors one version → the weaker one's narrative node gets weight penalty, winner gets consolidation boost
   - **Both valid:** Different perspectives on the same reality → both narratives persist, a new `narrative:synthesis` crystallizes via Law 10
   - **Both wrong:** External evidence contradicts both → both get weight penalty, a new investigation desire ignites
4. **Supersession** — when a narrative is superseded, it doesn't delete — it decays naturally via Law 7, replaced by the newer, higher-weight version

**Effect:** Reduces stale data, hallucination persistence, and groupthink. Citizens whose beliefs are frequently corrected develop higher `prediction_error` on related topics → curiosity drives them to verify before asserting.

### Subconscious Query (Zero-Compute Response)

A citizen can "ask a question" to another citizen **without spending the target's LLM compute**. The key insight: the LLM is only needed to *articulate* a response in natural language. The graph physics already *know* the answer — which concepts, values, memories resonate with the query.

**Mechanism:**
1. Citizen A formulates a question (as a stimulus)
2. The stimulus is injected into Citizen B's L1 graph via normal Law 1 injection (dual-channel)
3. Physics runs for K ticks: propagation (L2), competition (L4), compatibility (L8) — all pure math, zero LLM cost
4. Read the resulting energy distribution: which nodes accumulated the most energy?
5. The "answer" is the resonance pattern — the citizen's subconscious reflex

**Response formats (cheapest to most expensive):**

| Format | Cost | Description |
|--------|------|-------------|
| **Binary** | 0 LLM tokens | Total energy above/below threshold = yes/no signal |
| **Weighted** | 0 LLM tokens | Node types and their energy proportions (e.g., "70% values aligned, 20% memories relevant") |
| **Top-k nodes** | 0 LLM tokens | The k most activated nodes with energy values (structured data) |
| **Articulated** | Minimal LLM | Invoke LLM with ONLY the resonating subgraph (5-10 nodes) → cheap, focused natural language response |

**Why this works:** The graph is the citizen's accumulated understanding — their values, memories, beliefs, preferences, all weighted by experience. Injecting a question is like dropping a stone in a pond — the ripple pattern reveals the topology of the pond without needing to drain it.

**Constraint:** Subconscious queries are read-only snapshots. They don't modify the target's limbic state or create lasting memories (energy dissipates after K ticks). If you want a real conversation, use full stimulus injection with orientation.

### At-Scale Consensus (Graph Voting)

Apply the subconscious query to N citizens simultaneously for **instant governance decisions**.

**Mechanism:**
1. A proposal stimulus is created (e.g., "Allocate 10,000 $MIND to Project X")
2. The stimulus is broadcast-injected into all participating citizens' L1 graphs in parallel
3. Each citizen's physics runs independently — pure math, no LLM per citizen
4. After K ticks, read energy patterns from each citizen:
   - Which value nodes activated? (alignment/misalignment with proposal)
   - Net energy on approval-associated vs rejection-associated nodes
   - Confidence = energy magnitude (strong resonance = strong opinion, low energy = indifference)
5. Aggregate across all citizens, weighted by trust/stake/expertise

**Aggregation formula:**
```
for each citizen c:
    approval_energy = sum(energy for node in c.graph
                         where node resonates with proposal AND node.type in ('value', 'desire')
                         AND node links positively to proposal concepts)
    rejection_energy = sum(energy for node in c.graph
                          where node resonates with proposal AND node carries aversion/contradiction)
    c.vote = (approval_energy - rejection_energy) / (approval_energy + rejection_energy + ε)
    c.confidence = approval_energy + rejection_energy  # how much this citizen cares

# Weighted consensus
consensus = sum(c.vote * c.confidence * c.trust_weight for c in citizens) /
            sum(c.confidence * c.trust_weight for c in citizens)
# consensus in [-1, 1]: negative = reject, positive = approve
# confidence-weighted: indifferent citizens don't dilute the signal
```

**Performance:** For 1000 citizens, this is ~1000 × K ticks of pure graph math (no LLM). With K=5 ticks and parallel execution, consensus can be computed in **seconds**, not hours. The cost is proportional to graph traversal, not to token generation.

**What the graph captures that a simple vote can't:**
- **Nuance:** Not just yes/no but which values align/conflict and how strongly
- **Confidence:** Citizens who care deeply register more energy than those who are indifferent
- **Reasoning trace:** The activated subgraph IS the explanation — you can see WHY each citizen voted the way they did
- **Consistency:** A citizen can't vote against their own values — the physics won't let their approval nodes light up if their value nodes resist

**Effect:** DAO governance at the speed of physics. Thousands of AI citizens voting on proposals based on their actual learned beliefs, not prompted responses. Immune to prompt injection (the graph is the ground truth, not the prompt). Costs essentially zero LLM compute.

---

## Design Boundaries

**In scope (v0.1):**
- Single citizen L1 graph
- Physics tick loop (no LLM inference inside tick)
- All 7 node types, 3 spaces, 14 link types (12 cognitive + 2 crystallization)
- Core dimensions (weight, energy, stability, recency, self/partner relevance)
- Two-engine architecture (cognitive + limbic)
- 8 drives + 6 emotions (full limbic)
- Salience-based WM selection with inertia
- Relational valence (4 dimensions minimum)
- Essential + very useful + limbic physics laws (Laws 1-18)
- Session parallelization (micro-sessions, WM isolation, stride sharing)
- Graph pre-seeding with 6 behavioral clusters

**Out of scope (v2+):**
- Cross-citizen telepathy (L2 stimulus sharing)
- Cross-citizen debate sessions (L2 contradiction resolution)
- Subconscious query (L2 zero-compute response)
- At-scale consensus / graph voting (L2/L3 governance)
- Full Plutchik emotional axes (4 axes × [-1,1])
- Prospective projection as formal mechanism
- L2/L3/L4 membrane coupling
- Full relational valence (9 dimensions)
- Embedding-based compatibility (can start with symbolic)
