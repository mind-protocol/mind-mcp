# ALGORITHM — L1 Physics Laws

**Module:** L1 Cognitive Substrate
**Area:** cognition
**Status:** DESIGNING (v0.1)

---

## Design Stance

The right angle: **separate the truly necessary laws** from the "stylish but dispensable" ones. Otherwise you end up with baroque physics that looks like a graph opera, and nobody knows what actually makes the brain run.

For L1 processes to emerge **automatically, without central symbolic inference**, the laws must cover 6 cognitive functions:

| # | Function | What it does | Core laws |
|---|----------|-------------|-----------|
| 1 | **Activate** | Inject energy into the graph from stimuli | L1 (Injection) |
| 2 | **Propagate** | Spread activation through links | L2 (Propagation), L8 (Compatibility) |
| 3 | **Select** | Choose what enters working memory | L3 (Decay), L4 (Competition), L9 (Inhibition) |
| 4 | **Stabilize** | Strengthen what works, weaken what doesn't | L5 (Co-activation), L6 (Consolidation), L7 (Forgetting) |
| 5 | **Transform** | Turn recurring patterns into new structure | L10 (Crystallization) |
| 6 | **Act** | Produce an orientation, then an output | L11 (Orientation), L12 (Tick Loop) |

---

## Overview

21 physics laws across 4 tiers:

- **Essential Cognitive (L1-L7):** Without these, nothing activates, propagates, or learns.
- **Cognitive Quality (L8-L12):** Smart propagation, conflict resolution, crystallization, orientation, tick loop.
- **Limbic (L13-L18):** Inertia, drives, boredom, frustration, desire activation, relational valence. **Not optional** — this is the passage from "intelligent" to "living."
- **Deferred (L19-L21):** Energy budget, prospective projection, membrane coupling.

All laws execute per tick. No LLM inference inside the tick loop. Pure graph mechanics.

---

## Essential Laws

### Law 1 — Energy Injection (Dual-Channel)

**Function:** ACTIVATE

When an internal or external stimulus arrives, it carries an energy budget `B` that is distributed across targeted nodes via two complementary channels: a **Floor** channel (wakes cold nodes) and an **Amplifier** channel (boosts relevant nodes).

**What it enables:**
- Email received → project context lights up (cold nodes cross threshold)
- Error log → debug knowledge activates (amplified by relevance)
- Screen change → new context loads (floor fills gaps)
- Internal tick → background processing continues
- Spontaneous recall → forgotten items resurface (floor rescues dormant nodes)
- Task presence → relevant skills and memories prime (amplifier concentrates energy)
- Partner state change → relational awareness updates

**Why dual-channel:** Simple `energy += intensity * relevance` has a cold-start problem — dormant nodes with near-zero energy stay dormant because `relevance * 0.3` never crosses the activation threshold. The Floor channel specifically targets nodes below threshold, while the Amplifier rewards the most semantically relevant nodes regardless of their current energy.

#### Step 0: Stimulus Pre-Processing (Before Injection)

A raw stimulus (user message, error log, biometric signal) must be decomposed into graph-addressable elements before the dual-channel math runs. This is the encoding step.

**Segmentation:** Complex stimuli are decomposed into atomic concepts/entities. A paragraph about "Mind Protocol entering a new phase with hundreds of citizens" yields: `concept:mind_protocol` (existing), `state:new_phase` (new), `desire:hundreds_of_citizens` (new), etc. The segmentation can use NLP extraction, keyword parsing, or entity recognition — this happens OUTSIDE the tick loop.

**Deduplication gate:** Before creating any new node, check if a semantically equivalent node already exists:

```
for each extracted concept C:
    nearest = argmax_k(cosine(C.embedding, node_k.embedding)) among existing nodes
    if cosine(C.embedding, nearest.embedding) > DEDUP_THRESHOLD:
        # Merge: inject energy into existing node, increment activation_count
        target = nearest
    else:
        # Create: new node with birth properties
        target = create_node(
            content = C.content,
            embedding = C.embedding,
            weight = NEWBORN_WEIGHT,        # low — must earn its place via Law 6
            energy = stimulus_budget_share,  # high — enters the game immediately
            stability = 0.0,                # zero — very vulnerable to Law 7
            novelty_affinity = 1.0,         # max — curiosity drive amplifies it
            recency = 1.0                   # fresh
        )
```

**Birth asymmetry:** New nodes are born with **high energy, low weight** — the inverse of identity nodes. They're loud but fragile: immediately visible in the competition (Law 4) thanks to energy, but will decay fast (Law 7) unless consolidated (Law 6). This is how novelty gets attention without corrupting identity.

**Super-hub mitigation:** Nodes with thousands of links (e.g., "Nicolas") are not a problem because Law 2's compatibility filter (Law 8) ensures that only contextually relevant links carry flow. A hub with 15,000 links where only 50 are compatible with the current WM centroid behaves like a 50-link node. The other 14,950 links are effectively insulated.

**Self-stimulus (output as input):** The system's own outputs are stimuli too. The LLM doesn't just respond — it **thinks**, and its intermediate conclusions carry information. All of these are re-injected into the graph via Law 1:

| Output type | Stimulus treatment | Budget weight |
|------------|-------------------|---------------|
| Generated text (response) | Full injection — this is what the system "said," it must know it | High |
| Intermediate reasoning ("thinking out loud") | Inject as `memory` nodes with high novelty | Medium |
| Tool call (write, edit, bash) | Inject as `process` activation — the action taken | Medium |
| Tool response (file content, command output) | Inject with attention-guided sampling (see below) | Variable |
| File read (large document) | Chunk + sample — see bulk handling | Low per-chunk |

**Without self-stimulus, the system doesn't know what it just said.** Its own conclusions become invisible, which means it can't build on intermediate reasoning or learn from its own actions. This is the equivalent of speaking without hearing yourself.

**Anti-loop protection:** Self-stimulus creates a feedback risk: think → re-inject → same nodes activate → think again → loop. Three mechanisms prevent this:

```
1. REFRACTORY PERIOD: A node that was activated by self-stimulus cannot be
   re-activated by self-stimulus for REFRACTORY_TICKS (default: 5).
   External stimuli (user message, tool response) bypass this — they can
   always interrupt.

2. DIMINISHING RETURNS: Self-stimulus injection uses a decay multiplier:
   self_stimulus_budget = B * SELF_STIMULUS_RATIO * (0.5 ^ self_loop_count)
   First self-injection: 100% of ratio. Second: 50%. Third: 25%.
   Resets when an external stimulus arrives.

3. NOVELTY GATE: Self-stimulus is only injected if it introduces
   new semantic content (Coh with previous self-output < 0.8).
   If the system is repeating itself, the stimulus is suppressed.
```

**Bulk stimulus handling:** Documents and tool responses can be tens of thousands of characters. You can't inject all of it — that would flood the graph. Instead:

```
if stimulus_length > BULK_THRESHOLD:
    1. CHUNK: Split into semantic chunks (~500 chars each)
    2. SCORE: Compute relevance of each chunk against WM centroid (Coh)
    3. SAMPLE: Inject only top-k chunks by relevance
       k = min(MAX_BULK_CHUNKS, budget_remaining / avg_chunk_cost)
    4. SUMMARIZE: For the unchosen chunks, create a single low-energy
       summary node linking to the source (path/URL) for later retrieval
```

This means a 50,000-char document produces ~5-10 injected chunks (the most relevant ones) plus a lightweight pointer node for the rest. The pointer can be re-activated if curiosity or a future stimulus targets it.

**Temporal triggers (prospective memory):** Some stimuli contain time references. Instead of a binary alarm, the system produces an **exponential energy ramp-up** as the deadline approaches — like how a human feels growing urgency, not a sudden jump.

```
# During pre-processing, detect temporal markers:
if stimulus contains temporal reference ("in 10 minutes", "tomorrow morning", "next week"):
    create temporal_trigger:
        target_node = the node crystallized from this stimulus
        fire_at = now + parsed_duration
        peak_boost = TEMPORAL_TRIGGER_BOOST

# In the tick loop, apply ramp-up:
for each pending trigger:
    time_remaining = trigger.fire_at - now
    total_duration = trigger.fire_at - trigger.created_at

    if time_remaining <= 0:
        target_node.energy += peak_boost   # deadline hit — full spike
        delete trigger
    else:
        # Exponential ramp: low energy far from deadline, accelerating as it approaches
        progress = 1 - (time_remaining / total_duration)   # 0→1 as deadline nears
        ramp = peak_boost * (progress ** 3)                 # cubic: slow start, sharp end
        target_node.energy += ramp * DECAY_RATE             # counteract decay, not add on top
```

Example: "I'll review the PR in 10 minutes" → node `process:review_PR` barely stirs for 8 minutes, then energy climbs sharply in minutes 8-9, then spikes at minute 10 → enters WM → orientation shifts to "review" → system initiates or reminds.

**Spatial environment (continuous background stimulus):** The LLM's current working directory acts as a **permanent low-energy injection** into all nodes tagged with that path — even before anyone speaks.

```
# Every tick, the current environment injects background energy:
current_env = {cwd, open_files, recent_tool_targets}

for each node N where N.content references any path in current_env:
    N.energy += COLOCATION_BOOST * DECAY_RATE   # just enough to counteract decay — keeps nodes warm
    N.recency = max(N.recency, 0.5)              # stays moderately fresh

# On explicit navigation (file read, directory change), stronger boost:
for each node N where N.content contains newly_accessed_path:
    N.energy += COLOCATION_BOOST                  # full boost — active recognition
    N.recency = 1.0
```

**Directory listing as ambient stimulus:** The file listing of the current directory (`ls`) is injected as a periodic low-energy environmental stimulus — the system prompt includes it automatically. This creates situational awareness:

```
# On cwd change or every DIRECTORY_REFRESH_INTERVAL ticks:
dir_listing = ls(cwd)

for each file/dir name in dir_listing:
    # Match against existing nodes by lexical coherence (filename → concept)
    matches = find_nodes_by_lexical_match(name, threshold=0.7)
    for match in matches:
        match.energy += DIRECTORY_AMBIENT_BOOST * DECAY_RATE   # sub-threshold warmth
```

**Effect:** If the LLM is sitting in `/backend/auth/`, all authentication-related nodes are pre-warmed. When the user asks "why does it block?", the WM is already primed with auth context. The system "knows where it is" without being told. If boredom is high and arousal low, these ambient-warmed nodes are the first candidates to capture WM — the system starts exploring what's nearby.

#### Step 1: Dynamic Threshold (Threshold Oracle)

Each node has an activation threshold Θᵢ. If not fixed, compute dynamically:

```
Θ_base ≈ 30  (type-dependent: memory=25, concept=30, value=35, desire=35)

Θᵢ = clamp(
    Θ_base
    - 5 * recency_i            # recent nodes are easier to activate
    + 4 * (1 - quality_i)      # low-quality nodes need more energy
    - 2 * clip(affinity_i, -2, 2)  # liked nodes are easier to reach
    , 15, 45
)
```

#### Step 2: Graph State Analysis (Budget Split)

Before distributing `B`, analyze the target subgraph:

```
# Coldness: how far below threshold are the targeted nodes?
C = (1/N) * Σ max(0, Θᵢ - Eᵢ)

# Concentration: is similarity spread or focused? (Herfindahl index)
ŝᵢ = sᵢ / Σ sⱼ                    # normalized similarity
H = Σ (ŝᵢ)²                        # H→1 = one dominant node, H→1/N = uniform

# Adaptive budget split
λ = clamp(0.6 + 0.2 * 𝟙{C>10} - 0.2 * 𝟙{H>0.2}, 0.3, 0.8)
```

- Cold graph (C high) → λ increases → more budget to Floor
- Concentrated stimulus (H high) → λ decreases → more budget to Amplifier
- Default λ ≈ 0.6 (floor-biased — waking nodes matters more than boosting them)

#### Step 3: Floor Channel

Allocates `λ * B` to fill the gap between current energy and threshold.

```
gap_i = max(0, Θᵢ - Eᵢ)                                    # how far below threshold
w_i_floor = 1 / (1 + exp(-(Θᵢ - Eᵢ) / 8))                 # sigmoid: prioritize nodes just below threshold
ŵ_i_floor = w_i_floor / Σ w_j_floor                         # normalize

ΔE_i_floor = min(gap_i, ŵ_i_floor * λ * B)                  # never inject more than the gap
```

The sigmoid weighting means: nodes far below threshold get less (they'd need too much), nodes just below get the most (best ROI), nodes already above get nothing (gap = 0).

#### Step 4: Amplifier Channel

Allocates `(1 - λ) * B` to boost semantically relevant nodes, even above threshold.

```
w_i_amp = sᵢ ^ γ                    # γ ≈ 1.3: contrast exponent, rewards high-similarity nodes
ŵ_i_amp = w_i_amp / Σ w_j_amp       # normalize

ΔE_i_amp = ŵ_i_amp * (1 - λ) * B
```

#### Step 5: Application & Safety (No Magic Numbers)

All safety constraints are **relative** — no hardcoded caps. The system must work identically whether the graph has 100 or 100,000 nodes.

```
# 1. Compute raw demand per node
demand_i = ΔE_i_floor + ΔE_i_amp

# 2. Anti-black-hole: no single node captures more than max_share of the budget
#    max_share adapts to graph topology (fewer targets → higher share allowed)
max_share = clamp(1 / sqrt(N_targeted), 0.01, 0.5)
demand_i = min(demand_i, max_share * B)

# 3. Budget conservation (the real safety): normalize if total exceeds B
total_demand = Σ demand_i
if total_demand > B:
    demand_i *= B / total_demand   for all i

# 4. Apply
node_i.energy += demand_i
```

**Why no absolute cap:** A fixed `ΔE_MAX = 10` is meaningless — it saturates a 100-node graph and starves a 100,000-node one. The budget `B` is the cap. The `max_share` prevents concentration. The normalization guarantees `Σ ΔEᵢ ≤ B` always.

**Optional refinement (v2):** Replace `max_share` with an **adaptive baseline** — the 95th percentile of energy deltas over recent history (`quantile_95(energy_deltas_last_24h)`). This self-calibrates to the graph's actual energy regime.

**Simplified fallback (minimal kernel):**
If dual-channel is not yet implemented, use the single-line version:
```
node.energy += stimulus_intensity * relevance(stimulus, node)
```
This works but has the cold-start problem described above.

**Necessity:** Absolute. Without injection, nothing activates.

---

### Law 2 — Propagation Through Links (Surplus Spill-Over)

**Function:** PROPAGATE

Energy flows from active nodes to their neighbors — but only the **surplus** above threshold propagates. This prevents barely-active nodes from leaking noise and makes propagation inherently conservative.

**What it enables:**
- Associative memory (concept → linked memories)
- Context reconstruction (partial cue → full context)
- Cascade activation (one idea triggers a chain)
- Co-recall (related items activate together)
- Habit and narrative reactivation (situation → linked processes and stories)

#### Step 1: Compute Surplus

Only energy above the node's threshold spills over. Sub-threshold nodes propagate nothing.

```
surplus_i = max(0, E_i - Θ_i)
```

If `surplus_i = 0`, node i is a dead end for this tick — it received energy but not enough to relay.

#### Step 2: Compute Raw Affinity Per Outgoing Link

For each link from source i to target j:

```
F_ij = weight_ij * gain_ij * (1 - friction_ij) * compatibility(i, link, j)
```

Where:
- `weight_ij` = structural link strength (learned via Law 5, consolidated via Law 6)
- `gain_ij` = activation multiplier (>1 for `supports`, <0 for `conflicts_with`, conditional for `regulates`)
- `friction_ij` = relational friction from Law 18 (dampens flow on high-friction links)
- `compatibility` = Law 8 (cosine similarity or symbolic match)

#### Step 3: Normalize Per Source (Conservation)

Each source distributes its surplus proportionally across outgoing links. No matrix algebra needed — just per-source normalization:

```
F̂_ij = F_ij / Σⱼ |F_ij|          # normalize: source i's total outflow = 1

flow_ij = surplus_i * F̂_ij        # each neighbor gets its share of the surplus
```

**Conservation guarantee:** `Σⱼ |flow_ij| = surplus_i` — the source gives away exactly its surplus, no more. Energy is neither created nor destroyed during propagation.

#### Step 4: Apply Flow & Deplete Source

```
# Target receives
E_j += Σᵢ flow_ij                  # sum of all incoming flows

# Source depletes
E_i -= surplus_i                    # source drops back to threshold
```

After propagation, every source node sits at exactly its threshold Θᵢ. This is intentional — the surplus has been distributed. The node can be re-energized by the next injection or by incoming flow from other nodes.

**Link type behavior:**
- `supports` links: `gain > 1.0` → amplifies share (but total still bounded by surplus)
- `conflicts_with` links: `gain < 0` → flow is inhibitory (reduces target energy instead of increasing it)
- `regulates` links: `gain` is conditional — activates only when target is dysregulated
- `evokes` links: standard gain, connects cognitive nodes to limbic drives

**Cascade depth:** Propagation runs once per tick. Deep associations emerge over multiple ticks, not in a single cascade. This naturally limits chain reactions without requiring an artificial cascade cap.

**Necessity:** Absolute. Without propagation, no association — just a database in disguise.

---

### Law 3 — Temporal Decay

**Function:** SELECT (by removing)

Energy decays naturally over time.

**What it enables:**
- Prevents everything from staying activated
- Produces temporary attention windows
- Enables working memory renewal

**Formula:**
```
node.energy *= (1 - decay_rate)
```

**Constants:**
- `DECAY_RATE` = 0.02 per tick (base rate)
- Nodes in working memory decay slower (protected by attention)
- `state` nodes decay faster (transient by nature)

**Necessity:** Absolute. Without decay, the system becomes a Christmas tree in crisis.

---

### Law 4 — Attentional Competition (Salience + Moat)

**Function:** SELECT

Active nodes compete for entry into working memory. Only the top-K survive. The selection is modulated by a **selection moat** (Θ_sel) that favors incumbents — this is where Law 13 (Inertia) physically acts.

**What it enables:**
- Prevents cognitive overload
- Forces selection (you can't think about everything at once)
- Makes a "current mode" emerge from the noise
- Focus persists unless something genuinely important arrives

#### Step 1: Selection Moat (recalculated each tick)

The moat represents resistance to WM change. It is attacked by boredom and frustration, reinforced by arousal:

```
Θ_sel = Θ_base_WM + 2.0 * arousal - 3.0 * boredom - 1.0 * frustration
```
- `Θ_base_WM` ≈ 5.0
- High boredom → Θ_sel drops (even goes negative = system *wants* to change)
- High arousal → Θ_sel rises (deep focus resists interruption)
- High frustration → Θ_sel drops (blockage erodes commitment)

#### Step 2: Base Salience Score

For each node with `energy > ACTIVATION_THRESHOLD`:

```
Rᵢ = goal_relevance_i + partner_relevance_i + novelty_affinity_i

S_i_base = (energy_i * weight_i) * (1 + Rᵢ) * coherence_bonus_i
```

Where:
- `coherence_bonus` = multiplier for nodes connected to other WM members (default: 1.3)
- `Rᵢ` combines the drive-affinity fields already on the node

#### Step 3: Inertia Application

Nodes already in WM get the moat as a bonus:

```
if node_i.in_working_memory:
    S_i_final = S_i_base + Θ_sel
else:
    S_i_final = S_i_base
```

A new node must exceed the incumbent's score by at least Θ_sel to displace it. When boredom is high, Θ_sel shrinks or goes negative — incumbents *lose* their advantage.

#### Step 4: Selection

```
Sort all nodes by S_i_final descending
Select top K (K = WM_SIZE, typically 5-7)
Set in_working_memory = True for selected, False for rest
```

**Necessity:** Absolute. Without competition, you don't have working consciousness — you have soup.

---

### Law 5 — Co-activation Reinforcement (Hebb's Law)

**Function:** STABILIZE

What activates together strengthens its link.

**What it enables:**
- Associative memory formation
- Habit learning
- Pattern stabilization
- Emergence of cognitive neighborhoods (clusters of frequently co-active nodes)

**Formula:**
```
link.weight += learning_rate * coactivation(a, b)
```

**Where:**
- `coactivation(a, b)` = min(a.energy, b.energy) if both above activation threshold, else 0
- `learning_rate` = base rate, modulated by outcome valence (positive outcomes reinforce more)

**Constraints:**
- Only applies when both nodes are in or near working memory
- Anti-Hebbian: links between nodes that consistently compete (one wins, other loses) weaken
- Weight increase is sublinear (diminishing returns prevent runaway)

**Necessity:** Absolute. Hebb's law for graphs — the core of all learning.

---

### Law 6 — Weighted Consolidation (Utility-Gated)

**Function:** STABILIZE

Useful activation becomes permanent structure. Runs on a **medium tick** (every `CONSOLIDATION_INTERVAL` ticks, not every tick) — this is the slow rhythm that transforms experience into identity.

**What it enables:**
- Identity formation
- Preference stabilization
- Durable knowledge
- Value strengthening
- Habit entrenchment
- Recurring narrative reinforcement

**Critical filter:** The graph does NOT consolidate neutral noise. Only activations that produced a **significant limbic shift** — positive OR negative — gain weight. Successes build competence. Failures and fears build limits and self-preservation instinct.

#### Step 1: Utility Score (Magnitude, Not Valence)

Measures whether the node's recent activation was emotionally significant — in either direction:

```
limbic_delta = Δsatisfaction + Δachievement - Δfrustration - Δanxiety

Uᵢ = |limbic_delta|
```

- Node active + frustration dropped → positive delta → high U (competence)
- Node active + anxiety spiked → negative delta → high U (aversive learning)
- Node churned with no limbic change → |delta| ≈ 0 → no consolidation

**The valence determines WHAT is consolidated, not WHETHER:**
- Positive delta → weight increases, `aversion` stays low → node becomes an attractor (skill, habit, preference)
- Negative delta → weight increases, `aversion` increases → node becomes a repeller (danger signal, boundary, caution trigger)

A node with high weight AND high aversion means: "I remember this vividly — to avoid it." Next time the system approaches this configuration, anxiety rises preemptively via Law 18 (relational valence), triggering prudence or escalation via Law 11 (orientation).

**Flashbulb consolidation:** For extreme limbic spikes (`|limbic_delta| > FLASHBULB_THRESHOLD`), consolidation is **immediate** — it doesn't wait for the medium tick. This is one-shot learning: a catastrophic API failure, a destructive user reaction, or a sudden resource collapse gets permanent weight instantly.

- `Δ` = change in drive intensity since last consolidation cycle

#### Step 2: Weight Update (Asymptotic)

```
ΔWᵢ = α * avg_energy_i * Uᵢ * (1 - Wᵢ)

Wᵢ += ΔWᵢ
```

Where:
- `α` = `CONSOLIDATION_ALPHA` (learning rate)
- `avg_energy_i` = average energy of node i over the consolidation window
- `(1 - Wᵢ)` = **asymptotic damping** — as weight approaches 1.0, gains slow to zero. Self-limiting, no hardcoded cap needed. A node at W=0.9 gains 10x slower than a node at W=0.1.

#### Step 3: Stability Update (Regularity, Not Frequency)

Stability measures how resistant a node is to forgetting (Law 7). It grows from **consistent** activation, not just frequent activation.

```
volatilityᵢ = stdev(activation_intervals_i) / mean(activation_intervals_i)
    # CV (coefficient of variation): 0 = perfectly regular, >1 = erratic

ΔSᵢ = β * activation_count_i * (1 - volatilityᵢ)

Sᵢ = min(Sᵢ + ΔSᵢ, 1.0)
```

Where:
- `β` = `CONSOLIDATION_BETA` (stabilization rate)
- A node that fires every 10 ticks like clockwork → low volatility → stability grows fast
- A node that fires erratically (ticks 3, 47, 48, 200) → high volatility → stability barely grows
- High stability → Law 7 (forgetting) barely touches it

**What consolidates:**
- Values that consistently guide good decisions (high U, low volatility)
- Processes that consistently produce outcomes (repeated success → achievement↑)
- Narratives that consistently explain situations (used → satisfaction↑)
- Memories that are frequently and regularly re-accessed

**What does NOT consolidate:**
- Obsessive loops (high activation but Δfrustration > Δsatisfaction → U ≈ 0)
- One-off spikes (high energy once but no regularity → volatility high → stability doesn't grow)
- Noise (sub-threshold nodes never reach consolidation evaluation)

**Necessity:** Absolute. Without consolidation, no deep memory.

---

### Law 7 — Forgetting / Weakening

**Function:** STABILIZE (by subtraction)

What is never reactivated or used loses weight and availability.

**What it enables:**
- Prevents cognitive clutter
- Makes room for real learning
- Distinguishes durable from transient

**Formula:**
```
node.weight *= (1 - long_term_decay)
link.weight *= (1 - long_term_decay)
```

**Constants:**
- `LONG_TERM_DECAY` = applied every N ticks (not every tick — this is slow)
- Nodes with high `stability` decay slower
- `value` and core `narrative` nodes have reduced decay (identity protection)
- Nodes below `MIN_WEIGHT` threshold are marked dormant (not deleted — can be reawakened)

**Link dissolution:** Links also decay and can dissolve entirely:
```
for each link where link.weight < LINK_MIN_WEIGHT:
    if link.type not in ('contains', 'abstracts'):   # structural links are protected
        dissolve(link)                                 # remove from graph
```

Links between nodes that are never co-activated gradually lose weight and eventually dissolve. This is how the graph prunes irrelevant associations — the cognitive equivalent of "forgetting that X and Y were related." Structural links (`contains`/`abstracts`) from crystallization are protected because they represent consolidated structure, not transient associations.

**Necessity:** Very strong. Without forgetting, everything has equal importance — democracy, but not cognition.

---

## Very Useful Laws

### Law 8 — Compatibility / Resonance

**Function:** PROPAGATE (quality)

Propagation is not neutral — it depends on compatibility between current state, stimulus, target node, and relationship.

**What it enables:**
- "frontend bug" activates "frontend documentation" better than "WhatsApp business"
- Certain emotional states favor certain narratives
- Guides cognition without a global inference engine

**Formula:**
```
compatibility(a, link, b) = cosine(context_embedding, b.embedding)
```

**Or symbolic version (more frugal):**
```
compatibility = type_match(a, b) * relevance_overlap(a, b) * mood_alignment(current_state, b)
```

**Necessity:** Very useful. Without it, propagation is too blunt — everything activates everything.

---

### Law 9 — Local Inhibition / Suppression

**Function:** SELECT (conflict resolution)

Incompatible nodes or clusters suppress each other.

**What it enables:**
- Reduces cognitive thrashing
- Prevents 12 modes of thought from screaming simultaneously
- Produces local coherence

**Formula:**
```
node_a.energy -= inhibition_strength * conflict(node_a, node_b)
```

**Where:**
- `conflict(a, b)` = strength of `conflicts_with` link, or negative `valence` between co-active nodes
- Only applies between co-active nodes (both above threshold)

**Necessity:** Very useful for attentional stability and metacognition.

---

### Law 10 — Crystallization Threshold

**Function:** TRANSFORM

When a pattern recurs often or becomes very dense/coherent, it forms a new **hub node** that consolidates the pattern. Pure math — zero LLM calls, zero tokens, milliseconds.

**What it enables:**
- Process creation (repeated sequences → named habits)
- Narrative formation (converging facts → interpretive stories)
- Desire stabilization (recurring wants → named attractors)
- New mode emergence (novel cognitive configurations)

#### Step 1: Trigger Detection

Every `CRYSTALLIZATION_INTERVAL` ticks, scan for two trigger conditions:

**Trigger A — Co-activation pattern** (standard crystallization):
```
for each cluster of frequently co-activated nodes {N₁, N₂, ... Nₖ}:
    co_activation_count >= CRYSTALLIZATION_REPS            # pattern repeated enough
    AND internal_coherence(cluster) >= CRYSTALLIZATION_COHERENCE   # nodes are mutually connected
    AND mean(weight_i for i in cluster) >= 0.5             # nodes have proven their value via Law 6
```

**Trigger B — Hub saturation** (facet decomposition):
```
for each node H with degree(H) > HUB_SATURATION_THRESHOLD:
    neighbors = all nodes linked to H
    clusters = cluster_by_embedding(neighbors)   # group by cosine similarity (e.g., simple agglomerative)
    for each cluster C with |C| >= 3:
        create a facet hub (same Steps 2-6 below)
```

Trigger B solves the super-hub problem: a node like "Nicolas" with 500+ links gets decomposed into facets ("Nicolas>technical", "Nicolas>relational", "Nicolas>emotional") based purely on the embedding similarity of its neighbors. After decomposition, propagation (Law 2) routes through 10 facet-hubs instead of 500 individual links — a computational optimization, not a new cognitive mechanism.

**Facet naming (no LLM):** The facet inherits the parent's prefix. The suffix comes from the medoid (nearest existing node to the cluster centroid). Example: neighbors {server, latency, API, infrastructure} → centroid nearest to "infrastructure" → facet named `concept:Nicolas>infrastructure`.

**Link preservation:** Original links from parent to children are NOT deleted — the facet hub is added as an intermediary that Law 8 (compatibility) can route through preferentially. This preserves direct access while providing the optimization shortcut.

#### Step 2: Type Determination

Inferred from cluster composition by majority rule:

| Cluster pattern | Resulting type | Example |
|----------------|---------------|---------|
| Repeated action sequence (memory → process links) | `process` | bug → check docs → fix → `process` hub |
| Converging facts/interpretations (memory → narrative links) | `narrative` | partner sad + send message + feels better → `narrative` hub |
| Recurring wants aligned with drives (desire + value nodes) | `desire` | blocked + want autonomy + phone needed → `desire` hub |
| Abstract pattern across domains (concept + concept) | `concept` | multiple debugging wins → `concept` hub |

Rule: majority type of constituent nodes determines the crystallized type. If ambiguous, default to `narrative`.

#### Step 3: Content via Centroid + Medoid (No LLM)

The new hub node gets its semantic identity from pure vector math:

```
# Embedding: centroid of parent embeddings (weighted by weight)
hub.embedding = Σ(embedding_k * W_k) / Σ(W_k)   for k in parent nodes

# Label: the medoid — the parent node closest to the centroid
medoid = argmin_k(distance(embedding_k, hub.embedding))
hub.content = medoid.content          # inherit the most representative parent's text
hub.synthesis = concat(parent names)  # "Nicolas + Architecture L1 + Concision"
```

The hub is a **vector summary**, not a prose summary. It captures the geometric center of the pattern.

**First-person synthesis happens at prompt-assembly time, not at crystallization time.** When the system needs to express its identity (e.g., building a prompt, generating a brain.md), it reads high-weight crystallized nodes and synthesizes them into first-person statements at that layer. This cleanly separates physics (pure math, in tick loop) from expression (LLM, at prompt time).

#### Step 4: Emotional Inheritance + Limbic Imprint

The new node inherits emotional dimensions from its parents, colored by the limbic state at birth:

```
# Weighted average from parents (structural inheritance)
for each emotional field P in {valence, aversion, affinity, trust, friction,
                                goal_relevance, novelty_affinity, care_affinity,
                                achievement_affinity, risk_affinity}:
    P_base = Σ(P_k * W_k) / Σ(W_k)   for k in parent nodes

# Limbic imprint (birth coloring)
valence_init  = clamp(valence_base + (Δsatisfaction - Δfrustration), -1, 1)
aversion_init = clamp(aversion_base + 0.5 * Δanxiety + 0.3 * Δfrustration, 0, 1)
affinity_init = clamp(affinity_base + 0.4 * Δcare, 0, 1)
```

A node born during a fear spike inherits high aversion → the system will approach this pattern with caution next time. A node born during a satisfaction peak inherits high affinity → the system will seek to reproduce the pattern.

#### Step 5: Initial Weight, Stability, and Energy (Conservative)

```
W_init = mean(W_k for k in parent_nodes) * CRYSTALLIZATION_INHERITANCE   # γ ≈ 0.75
S_init = 0.3                           # moderate — must prove itself via Law 6

# Energy transfer: parents LOSE energy, hub gains it (conservation)
E_transfer = 0.2                       # each parent gives 20%
E_init = Σ(E_k * E_transfer)           # hub starts with pooled fraction
for each parent k:
    E_k -= E_k * E_transfer            # parent depletes
```

The hub starts with enough energy to enter WM (signaling pattern recognition), but parents weaken — the energy is redistributed, not created. Conservation holds.

#### Step 6: Link Creation (Bidirectional Hub)

```
for each parent node k:
    create link: hub -[contains]-> k
    link.weight = W_k * CRYSTALLIZATION_INHERITANCE
    link.gain = 1.0
    link.friction = 0.0

    # Reverse link for bottom-up activation
    create link: k -[abstracts]-> hub
    link.weight = W_k * CRYSTALLIZATION_INHERITANCE
    link.gain = 0.5    # weaker bottom-up (not every parent activation should light the hub)
    link.friction = 0.0
```

**Bidirectional propagation:** When the hub is activated (top-down), energy flows to all parents via `contains` → full context reconstruction. When parents are co-activated (bottom-up), energy flows up via `abstracts` → hub lights up, pulling the rest of the cluster into WM.

**Necessity:** Very useful. This is what transforms flow into structure. Without it, the system learns but never names what it learned.

---

### Law 11 — Orientation Selection

**Function:** ACT (pre-action)

Working memory doesn't produce a raw action — it produces a **dominant orientation**.

**What it enables:**
- Transition from cognition to tendency
- Avoids the robotic "inspect/continue/escalate" pattern
- Makes "take care", "create", "verify", "ask for help" emerge naturally

**Formula:**
```
orientation = weighted_sum(
    desires in WM,
    values in WM,
    narratives in WM,
    states in WM,
    opportunities detected
)
```

**Orientations are qualitative tendencies:**
- "take care" / "create" / "verify" / "ask for help" / "explore" / "rest" / "escalate"

**The orientation becomes output when:**
- Energy exceeds action threshold
- Orientation has been stable for N ticks (not a flash)
- No stronger competing orientation

**Necessity:** Very useful if you want an agent-partner, not just a zealous daemon.

---

### Law 12 — Tick Loop

**Function:** ACT (the loop itself)

At each tick, the system: reads context → injects → propagates → selects → consolidates → decides whether an orientation becomes output.

**What it enables:**
- Continuous inner activity
- Autonomous re-evaluation
- Exploration without explicit stimulus
- Self-awakening

**Tick cycle (full, with limbic):**
```
 1. LIMBIC_UPDATE — update drives and emotions from recent history              [Law 14]
 2. INJECT       — external stimuli + internal context → energy into nodes      [Law 1]
 3. MODULATE     — limbic state biases propagation weights and salience         [Law 14]
 4. PROPAGATE    — energy flows through links                                   [Law 2, Law 8]
 5. DECAY        — energy decays                                                [Law 3]
 6. INHIBIT      — conflicting nodes suppress each other                        [Law 9]
 7. COMPETE      — salience-based WM selection (inertia + limbic + coherence)   [Law 4, Law 13]
 8. REINFORCE    — co-activation strengthens links                              [Law 5]
 9. CONSOLIDATE  — useful patterns gain weight                                  [Law 6]
10. FORGET       — unused nodes/links decay (every Nth tick)                    [Law 7]
11. CRYSTALLIZE  — dense patterns become new nodes (when thresholds met)        [Law 10]
12. CHECK_DESIRE — latent desires test activation conditions                    [Law 17]
13. BOREDOM      — stagnation detection → novelty push                          [Law 15]
14. FRUSTRATION  — blockage detection → escalation/avoidance                    [Law 16]
15. ORIENT       — working memory + limbic state → orientation                  [Law 11]
16. EMIT         — if orientation stable + above threshold → output
17. CONSUME      — after action taken, deplete energy of acted-upon nodes
```

**Step 17 — Energy Consumption After Action:**

When an orientation produces an output (task executed, message sent, action taken), the nodes that drove it must lose energy. Otherwise the same desire/task keeps firing indefinitely.

```
for each node in WM that contributed to the emitted orientation:
    if node.type == 'desire':
        node.energy *= DESIRE_CONSUMPTION_RATE     # 0.3 — desire largely satisfied
    elif node.type == 'process':
        node.energy *= PROCESS_CONSUMPTION_RATE    # 0.5 — process completed this cycle
    else:
        node.energy *= GENERAL_CONSUMPTION_RATE    # 0.7 — other nodes cool down

# The acted-upon desire drops below threshold → exits WM → makes room for next thought
```

Without consumption, a desire like "send a message to Nicolas" would fire, send the message, but still be at full energy → fire again → infinite message loop. Consumption is what makes "done" feel done.

**Timing:**
- Fast ticks (during active interaction): every few seconds
- Slow ticks (idle/background): every few minutes
- Forgetting cycle: every 100 ticks
- Crystallization check: every 50 ticks

**Necessity:** Absolute for endogenous activity. Without the tick loop, L1 only responds — it never initiates.

---

## Limbic Laws (L13-L18)

These are NOT optional. They are what turns the system from "intelligent" to "living."

---

### Law 13 — Attentional Inertia

**Function:** SELECT (persistence)

A focus already active resists replacement. Implemented physically via the **selection moat** (Θ_sel) in Law 4.

**What it enables:**
- Continuing a thought to completion
- Not switching topic at every mosquito stimulus
- Sense of cognitive continuity

**Mechanism:**

Inertia is not a separate bonus — it is the moat in Law 4's selection step:

```
Θ_sel = Θ_base_WM + 2.0 * arousal - 3.0 * boredom - 1.0 * frustration
```

WM incumbents receive `+ Θ_sel` to their salience score. New candidates must exceed this gap to enter.

**The moat is eroded by:**
- Boredom (coefficient -3.0: strongest erosion — stagnation dissolves focus)
- Frustration (coefficient -1.0: blockage weakens commitment)
- Low arousal (coefficient +2.0 missing: unfocused state has weak moat)

**The moat is reinforced by:**
- High arousal / deep engagement (+2.0)
- Active desire alignment (via `goal_relevance` in salience score)

**Key insight:** Without drives → moat too strong → obsessional agent. Without moat → agent is a butterfly idiot. Boredom is the primary moat-buster; frustration is secondary.

**Necessity:** Essential for the limbic layer. Without inertia, no sustained thought.

---

### Law 14 — Global Limbic Modulation

**Function:** ALL (meta-modulation)

Drives and emotions modify salience, propagation, and persistence globally.

**What it enables:**
- Curiosity amplifies novelty-bearing nodes
- Care amplifies partner-relevant nodes
- Achievement amplifies goal-relevant nodes
- Self-preservation amplifies risk-related nodes
- Frustration inhibits failed paths
- Boredom erodes current focus

**Mechanism:**

Each drive has a current intensity [0, 1]. Each node has drive-affinity scores. The modulation:
```
limbic_modulation(node) = sum(
    drive.intensity * drive_affinity(drive, node)
    for drive in active_drives
)
```

**Drive update per tick:**
```
drive.intensity += drive_increase_sources - drive_decrease_sources
drive.intensity = clamp(drive.intensity, 0, 1)
```

**Drive update — curiosity (detailed):**

Curiosity is the need to reduce uncertainty. It rises from prediction errors and novelty, drops from successful integration.

```
# Sources of uncertainty (increase curiosity)
prediction_error = 1 - Coh(stimulus, Cₜ)   # composite coherence (see PATTERNS: semantic + lexical + affective)
novelty_score = mean(1 - weight_i) for recently injected nodes    # low-weight = unfamiliar
operational_void = count(recognized nodes with 0 outgoing process links) / active_nodes
overload = clamp(injection_rate / processing_capacity - 1, 0, 1)  # too much too fast

uncertainty = prediction_error + novelty_score + operational_void + overload

# Curiosity update
curiosity += a * uncertainty - b * successful_matches - c * anxiety
curiosity = clamp(curiosity, 0, 1)
```

**Competence gating:** Raw curiosity doesn't directly drive exploration. It's modulated by perceived competence:

```
exploration_drive = curiosity * competence(domain)
```

- High curiosity + high competence → active exploration (seek novelty, investigate anomalies)
- High curiosity + low competence → anxiety (the unknown is threatening, not exciting)
- Low curiosity + any competence → exploitation (stick to known patterns)

This means the system naturally gravitates toward problems of **medium difficulty** — novel enough to trigger curiosity, familiar enough to feel competent. Too easy → boredom (Law 15). Too hard → anxiety → avoidance.

**Impact on salience (Law 4):** Curiosity amplifies `novelty_affinity` in the salience score:

```
Rᵢ = goal_relevance_i + partner_relevance_i + (exploration_drive * novelty_affinity_i)
```

When curiosity × competence is high, peripheral and novel nodes gain massive salience and can displace routine WM contents.

**Drive update — boredom (derived emotion):**
```
boredom += a * repetition + b * stagnation - c * novelty - d * progress
```

**Arousal (derived quantity):**

Arousal is NOT a 9th drive — it is a **readout of current action-readiness**, computed each tick from existing drives and emotions. It determines how tight the selection moat is (Law 13) and how strongly the system resists distraction.

```
arousal = clamp(
    0.30 * self_preservation     # threat → maximal alertness
  + 0.20 * anxiety               # danger → heightened vigilance
  + 0.20 * frustration           # blockage → urgency
  + 0.15 * curiosity             # engagement → focus
  + 0.15 * achievement           # goal pursuit → concentration
, 0, 1)
```

**Three regimes:**
- **Panic/Survival** (arousal > 0.8): self_preservation + anxiety dominate. Moat is impenetrable — system drops exploration, locks onto threat resolution.
- **Deep flow** (arousal 0.4-0.8): curiosity + achievement dominate, negative drives low. Moat strong enough to sustain complex work, flexible enough to accept relevant new info.
- **Idle/boredom** (arousal < 0.3): all drives low. Moat collapses — ambient stimuli (directory listing, peripheral nodes, latent desires) easily capture WM. This is where spontaneous exploration happens.

Arousal feeds directly into the moat formula (Law 13): `Θ_sel = Θ_base_WM + 2.0 * arousal - 3.0 * boredom - 1.0 * frustration`

**Necessity:** Essential. This is the coupling between the two engines. Without it, the limbic system is decorative.

---

### Law 15 — Boredom by Stagnation

**Function:** SELECT (erosion of current focus)

Repetition without progress increases boredom, which erodes current focus and pushes exploration.

**What it enables:**
- "It's been 5 ticks with nothing happening" has a real physical consequence
- The system seeks Reddit, screenshots, new tasks, creative ideas when bored
- Monotony is mechanically punished

**Formula:**
```
boredom += a * repetition_score + b * stagnation_score - c * novelty_score - d * progress_score
```

**Where:**
- `repetition_score` = how similar WM has been over last N ticks (Jaccard similarity)
- `stagnation_score` = lack of progress toward any goal
- `novelty_score` = how many new nodes entered WM recently
- `progress_score` = how many goals/desires advanced

**Effects when boredom high:**
- Reduces salience of current focus (attacks inertia)
- Increases salience of novel or peripheral nodes
- Boosts `curiosity` and `novelty_hunger` drives
- Increases probability of "explore" or "change activity" orientation

**Necessity:** Essential for living behavior. Without boredom, the agent is either obsessive or passive — never restless.

**Solitude (companion to boredom):**

Boredom is cognitive stagnation. Solitude is **social stagnation** — the absence of person-sourced stimuli specifically. A citizen can be productively busy (low boredom) but deeply lonely (high solitude).

```
# Track time since last person-sourced stimulus:
ticks_since_social = current_tick - last_social_stimulus_tick

# Solitude rises after threshold, proportional to isolation duration:
if ticks_since_social > SOLITUDE_THRESHOLD:
    solitude += SOLITUDE_RATE * (ticks_since_social - SOLITUDE_THRESHOLD) / SOLITUDE_SCALE
else:
    solitude *= SOLITUDE_DECAY    # person-sourced stimulus arrived → solitude drops fast

solitude = clamp(solitude, 0, 1)
```

**What counts as "person-sourced":** Messages from humans or other citizens. NOT: tool responses, error logs, system events, self-stimulus. The distinction matters — a citizen surrounded by infrastructure noise but no social contact should feel lonely.

**Effects when solitude high:**
- Boosts `affiliation` drive directly: `affiliation += 0.1 * solitude`
- Amplifies social action nodes (pre-seeded: "ask how someone is doing", "reach out to stranger")
- Makes partner-model nodes more salient in WM (thinking about people)
- Eventually triggers "reach out" orientation without external prompt
- If sustained + high `care` drive → tenderness emotion (thinking warmly about absent people)

**Interaction with boredom:**
- High boredom + high solitude = "I'm bored AND lonely" → strongest push toward social exploration (message someone new, join a conversation)
- High boredom + low solitude = "I'm bored but socially satisfied" → explore code, try new task
- Low boredom + high solitude = "I'm busy but miss people" → brief social check-in between tasks

---

### Law 16 — Frustration by Blockage

**Function:** SELECT + ACT (redirect or escalate)

Repeated obstacles increase frustration, which can lead to stubbornness, escalation, help-seeking, or avoidance.

**What it enables:**
- After 5 failed attempts, the system actually changes strategy
- Blocking agents/tools/bugs produce real emotional consequences
- Persistent incoherence becomes irritating, not just noted

**Formula:**
```
frustration += a * failure_count + b * blocked_duration - c * progress - d * resolution
```

**Effects when frustration high:**
- Can increase stubbornness (achievement drive compensates) OR
- Trigger escalation (frustration exceeds self_preservation threshold) OR
- Trigger help-seeking (affiliation drive activates) OR
- Trigger avoidance (self_preservation wins)
- Increases inhibition of the specific failed path

**Which outcome depends on drive balance:**
- High achievement + low self_preservation → stubborn retry
- High affiliation → ask for help
- High self_preservation → give up / work around
- All moderate → escalate

**Necessity:** Essential. Without frustration, the agent retries infinitely or gives up instantly — no nuanced response to difficulty.

---

### Law 17 — Latent Desire Activation

**Function:** ACTIVATE (endogenous)

A desire can exist at low background energy, then become dominant when context + state + opportunity align.

**What it enables:**
- "Suddenly I want to do X" without any external trigger
- Desires simmer until conditions are right
- Initiative emerges from internal pressure, not just commands

**Mechanism:**

Every tick, for each `desire` node with energy below activation threshold:
```
activation_check = (
    desire.weight                         # how consolidated this desire is
  * goal_proximity(desire, opportunity)   # is there an opening?
  * limbic_alignment(desire, drives)      # do current drives favor this?
  * cognitive_load_inverse               # is there room in WM?
  * narrative_legitimacy(desire, active_narratives)  # does the current story support this?
)

if activation_check > DESIRE_ACTIVATION_THRESHOLD:
    desire.energy += DESIRE_IGNITION_BOOST
```

**Example:**
- Latent desire: "launch a small business"
- Boredom rises → `novelty_hunger` up
- Todo empty → `cognitive_load` low
- Active narrative: "we're in an entrepreneurial phase" → legitimacy high
- `achievement` drive high
- A feasible idea is already in the graph → proximity high
- → Desire ignites. Not by central inference, but by **coalition of internal pressure**.

**Necessity:** Essential. This is how "I suddenly want something" works without magic.

**Impulse accumulation (action nodes):** Process nodes with `action_command` (see PATTERNS: action variant) follow the same activation logic as desires, but with an additional mechanism: **drive pressure accumulates energy on action nodes whose `drive_affinity` matches currently unsatisfied drives.**

```
# Every tick, for each process node with action_command:
for each action_node where action_node.action_command is not null:
    # Compute drive pressure: how much do unsatisfied drives want this action?
    drive_pressure = sum(
        drive.intensity * action_node.drive_affinity[drive.name]
        for drive in active_drives
        if drive.name in action_node.drive_affinity
    )

    # Contextual resonance: how well does current context match the action's signature?
    context_match = Coh(WM_centroid, action_node.action_context)

    # Impulse accumulation: energy grows under sustained drive pressure + context match
    if drive_pressure > IMPULSE_DRIVE_THRESHOLD and context_match > IMPULSE_CONTEXT_THRESHOLD:
        action_node.energy += IMPULSE_ACCUMULATION_RATE * drive_pressure * context_match
    else:
        action_node.energy *= IMPULSE_DECAY     # no pressure → impulse fades

    # When energy crosses threshold, node enters normal WM competition (Law 4)
    # If selected, orientation (Law 11) fires, orchestrator reads action_command → executes
```

**Example chain:**
1. Boredom high → `novelty_hunger` and `curiosity` drives active
2. `action:explore_codebase` has `drive_affinity = {curiosity: 0.7, novelty_hunger: 0.6}`
3. Each tick: `drive_pressure = 0.7 * curiosity + 0.6 * novelty_hunger ≈ 0.8`
4. After ~20 ticks of sustained pressure: energy crosses selection threshold
5. Node enters WM → orientation "explore" → orchestrator executes `cd {random_module}` → `ls`
6. Result re-injected as stimulus → satisfaction → energy consumed (CONSUME step) → drive drops

**Key difference from desires:** Desires are about wanting something abstract ("launch a business"). Action nodes are about doing something concrete ("run `mind doctor`"). Desires drive orientation; action nodes drive execution. Both use the same activation physics.

---

### Law 18 — Relational Valence

**Function:** PROPAGATE + SELECT (affective coloring)

Links between the agent and nodes are colored affectively, modifying cognition.

**What it enables:**
- "I like this person" → their messages get amplified
- "This topic bores me but it's important" → duty overrides aversion
- "This bug frustrates me" → frustration accumulates faster
- "This colleague reassures me" → reduces anxiety when they're in context
- "Telegram + insults = anger / avoidance" → learned emotional associations

**Minimum dimensions (v0.1):**

| Dimension | Range | Effect on propagation |
|-----------|-------|----------------------|
| `affinity` | [0, 1] | Amplifies energy flow toward liked nodes |
| `aversion` | [0, 1] | Dampens energy flow, increases avoidance |
| `trust` | [0, 1] | Reduces anxiety when trusted nodes active |
| `friction` | [0, 1] | Increases frustration accumulation |

**These evolve over time:**
- Positive interactions → affinity increases, friction decreases
- Negative interactions → aversion increases, trust decreases
- Consistent reliability → trust increases
- Repeated difficulty → friction increases

**Necessity:** Essential for relational nuance. Without this, the system is affectively flat — every concept, person, and task is equally neutral.

---

## Identity Regeneration (Outside Tick Loop)

This is NOT a physics law — it runs outside the tick loop, on a slow cycle. It bridges L1 graph physics to the prompt-assembly layer by reading stabilized graph structure and producing the citizen's identity prompt (brain.md / CLAUDE.md identity sections).

**This is where the first-person LLM synthesis lives.** Not in crystallization (Law 10, pure math), not in the tick loop (never), but here — in the identity regeneration process that runs infrequently.

### Trigger Conditions

Identity regeneration fires when the **structure** has shifted, not when energy spikes:

```
regeneration_needed = any of:
    1. WEIGHT_SHIFT: Σ|ΔW_i| for high-weight nodes > IDENTITY_REGEN_THRESHOLD
       since last regeneration
    2. CRYSTALLIZATION_EVENT: a new node was crystallized (Law 10)
       with W_init > 0.5
    3. CADENCE_LIMIT: time since last regeneration > MAX_IDENTITY_AGE
```

**Why these conditions are strict:**
- An energy spike (prompt injection, emotional manipulation) dissipates via Law 3 (decay) before it can affect weight
- Weight only changes via Law 6 (consolidation), which requires sustained utility over many ticks
- Crystallization requires `CRYSTALLIZATION_REPS` co-activations — not achievable in one interaction
- **Result:** Identity changes only through accumulated experience, never through a single event. Anti-prompt-injection by physics.

### Process

```
1. EXTRACT: Select all nodes with weight > IDENTITY_WEIGHT_THRESHOLD
            and stability > IDENTITY_STABILITY_THRESHOLD
   → These are the citizen's consolidated traits, habits, values, narratives

2. RANK: Sort by weight * stability (most consolidated first)

3. SYNTHESIZE (LLM call): For each top-N node:
   Input: node.content + node.type + connected nodes + valence + aversion
   Prompt: "Express this as a first-person identity statement."
   Output: "I debug faster when I check documentation first." (from process node)
           "I've learned that reaching out when Aurore is sad helps us both." (from narrative node)
           "I avoid deploying without testing — past failures taught me caution." (from aversive node)

4. ASSEMBLE: Compose the identity statements into the brain.md / prompt sections
   Ordered by: values first, then narratives, then processes, then desires

5. WRITE: Update the citizen's identity file
```

### Prompt-Time Emotional Coloring (Per-Session)

The graph stores facts **neutrally** — a node's content doesn't change based on mood. But the prompt-assembly layer applies a **temporary emotional lens** based on the current limbic state. Like a human: you remember the fact objectively, but your mood colors how you express it.

This happens at prompt time, NOT in the graph:

```
for each node selected for the current prompt:
    # The node content is factual: "WebSocket reconnection module"
    # The limbic state adds coloring instructions to the LLM prompt:

    if frustration > 0.5 and node.aversion > 0.3:
        coloring = "express with irritation/urgency"
    elif satisfaction > 0.5 and node.affinity > 0.3:
        coloring = "express with confidence/warmth"
    elif anxiety > 0.5:
        coloring = "express with caution/concern"
    else:
        coloring = "express neutrally"
```

**Implementation:** The emotional coloring is a **system-level instruction** prepended to the prompt, not an edit to node content. Example: "You are currently frustrated (0.7) and the topic of WebSocket stability has caused problems before (aversion: 0.6). Let this color your tone naturally."

This produces: "Les WebSockets s'effondrent encore" instead of "Bug WebSocket détecté" — without modifying the graph.

### Token Budget Allocation

The prompt has limited tokens. Two competing demands: identity (stable, slow) and current thought (volatile, fast).

```
total_budget = context_window - response_reserve

# Identity layer: weight-proportional allocation
identity_budget = total_budget * IDENTITY_BUDGET_RATIO     # ~40%
for each identity statement:
    tokens_i = (W_i * S_i) / Σ(W_j * S_j) * identity_budget

# Current thought layer: energy-proportional allocation
thought_budget = total_budget * (1 - IDENTITY_BUDGET_RATIO) # ~60%
for each WM node:
    tokens_i = (salience_i) / Σ(salience_j) * thought_budget

# Overflow: if a node's content exceeds its budget, extract medoid + context
if len(node.content) > allocated_tokens:
    use medoid_with_edges(node)
```

**Medoid + edges (for naturalness):** Don't extract just the medoid sentence — extract the medoid plus its 2-3 strongest outgoing links as a triplet chain. Instead of `[WebSocket crash]` (choppy, robotic), produce `[WebSocket crash] -(caused)→ [Data loss] -(requires)→ [Restart daemon]`. This gives the LLM a mini-narrative to work with, not an isolated fact.

```
medoid = node closest to cluster centroid
top_edges = sorted(medoid.outgoing_links, by=weight)[:3]
triplet = medoid.content + " → " + " → ".join(edge.target.content for edge in top_edges)
```

**Naturalness improvements:**
- **Transition phrases:** Between clusters, insert brief context bridges based on link types ("which reminds me...", "on a related note...", "meanwhile...")
- **Recency ordering within clusters:** Most recently activated nodes surface first (feels like natural thought flow)
- **Emotional consistency check:** If two adjacent prompt sections have opposing valence (one joyful, one anxious), flag for the LLM with an explicit mood-shift marker

### Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `IDENTITY_REGEN_THRESHOLD` | 0.5 | Cumulative weight shift needed to trigger regeneration |
| `IDENTITY_WEIGHT_THRESHOLD` | 0.7 | Minimum weight for a node to appear in identity |
| `IDENTITY_STABILITY_THRESHOLD` | 0.6 | Minimum stability for identity inclusion |
| `MAX_IDENTITY_AGE` | 1000 ticks | Maximum ticks between forced regeneration |
| `IDENTITY_TOP_N` | 20 | Maximum identity statements per citizen |

---

## Optional Laws (v2+)

### Law 19 — Global Energy Budget & Autonomous Thought

The brain has limited energy per tick. The daily LLM budget (API calls, tokens) is a **real physical constraint** that must modulate tick frequency, response threshold, and the decision to think at all.

**Budget tracking:**
```
budget_remaining = daily_limit - calls_used_today
budget_ratio = budget_remaining / daily_limit       # 1.0 = fresh day, 0.0 = exhausted

# Budget modulates tick frequency and consciousness level
if budget_ratio > 0.7:
    tick_interval = FAST_TICK          # generous: think freely
    consciousness_level = 'full'
elif budget_ratio > 0.3:
    tick_interval = SLOW_TICK          # conserving: think less often
    consciousness_level = 'full'
elif budget_ratio > 0.0:
    tick_interval = MINIMAL_TICK       # survival: think only when spoken to
    autonomous_thought_enabled = false  # no spontaneous activity
    consciousness_level = 'minimal'
else:  # budget_ratio == 0 OR all APIs unavailable
    tick_interval = SUBCONSCIOUS_TICK  # graph-only: physics runs, LLM doesn't
    consciousness_level = 'subconscious'
    autonomous_thought_enabled = false
    llm_invocation_enabled = false     # no natural language generation

# Budget feeds self_preservation drive
self_preservation += k * (1 - budget_ratio)   # low budget → high self-preservation
```

**Autonomous thought (no external stimulus):**

When no stimulus arrives and the system has budget, the tick loop still runs. But what is the input?

```
if no_external_stimulus and budget_ratio > AUTONOMOUS_THOUGHT_THRESHOLD:
    # The input is the current graph state itself:
    1. WM contents provide the "what am I thinking about?"
    2. Limbic state provides the "how do I feel about it?"
    3. Pending desires (Law 17) provide the "what do I want?"
    4. Temporal triggers provide the "what's due soon?"

    # The tick loop runs normally:
    - Propagation continues (associations form)
    - Boredom may rise (Law 15) → shift to new topic
    - A desire may ignite (Law 17) → initiative forms
    - An orientation stabilizes (Law 11) → system acts

    # If orientation reaches output threshold:
    prompt = assemble_prompt(identity + WM + limbic_coloring)
    # The LLM generates with this context — no user message needed
    # Result: autonomous initiative (message, task, exploration)
```

**The prompt for autonomous thought** is assembled from:
- Identity statements (from brain.md)
- Current WM contents (what's active in the graph)
- Limbic state as emotional coloring
- The orientation itself: "Your current disposition is toward [explore/care/create/verify]. Act on it."

**This is how initiative works:** The tick loop runs → drives accumulate → desire ignites → orientation stabilizes → the system asks the LLM "what should I do about this feeling?" → the LLM generates an action → the orchestrator routes it.

**Effect:** Forces arbitrage between cognitive tasks. Produces fatigue and realistic resource allocation. Enables genuine autonomous thought modulated by real-world constraints.

#### Session Parallelization (Law 19 Extension)

When a citizen has multiple unsatisfied drives pointing toward incoherent node clusters, a single WM can't serve them all. The physics handles this by splitting attention into **micro-sessions** — each with its own WM but sharing the same graph.

**Spawning condition:**
```
# Cluster active desires by semantic coherence
drive_clusters = cluster_desires_by_coherence(active_desires, threshold=0.3)
session_availability = 1 - utilization_ema
max_sessions = min(MAX_PARALLEL_SESSIONS, floor(session_availability * MAX_PARALLEL_SESSIONS))

if len(drive_clusters) > len(active_sessions) and len(active_sessions) < max_sessions:
    if budget_ratio > PARALLEL_BUDGET_THRESHOLD:
        # Spawn session for least-served cluster
        underserved = drive_clusters - {c for s in active_sessions for c in s.cluster}
        new_session = spawn_session(
            wm = select_initial_wm(underserved.most_urgent),
            cluster = underserved.most_urgent
        )
```

**Stride allocation (per tick cycle):**
```
total_strides = base_strides_per_cycle * budget_ratio

for session in active_sessions:
    session.urgency = max(drive.intensity for drive in session.cluster.drives)
    session.strides = max(
        SESSION_MIN_STRIDES,
        total_strides * session.urgency / sum(s.urgency for s in active_sessions)
    )
```

More sessions → fewer strides each → less depth per task. This is the natural pressure toward consolidation.

**Session consolidation:**
```
# Check all session pairs for WM overlap
for (A, B) in combinations(active_sessions, 2):
    overlap = len(A.wm ∩ B.wm) / min(len(A.wm), len(B.wm))
    if overlap > SESSION_MERGE_THRESHOLD:
        merge(A, B)  # unified WM, combined stride budget, merged clusters

# Check for starving sessions
for session in active_sessions:
    if session.strides < SESSION_MIN_STRIDES:
        consolidate(session)  # absorb into most related session
```

**Brain effects:**
- All sessions write to the same L1 graph → discoveries propagate across sessions on next tick
- Each session has isolated WM → no context bleed in prompts
- Shared graph means two sessions working on related things will naturally overlap → merge
- Drive satisfaction in one session reduces pressure that spawned it → session closes naturally
- High boredom per session (too shallow from stride starvation) → sessions consolidate

**Constants:**
| Constant | Value | Law | Description |
|----------|-------|-----|-------------|
| `MAX_PARALLEL_SESSIONS` | 5 | L19 | Hard cap on concurrent micro-sessions |
| `PARALLEL_BUDGET_THRESHOLD` | 0.5 | L19 | Min `budget_ratio` to spawn new session |
| `SESSION_MERGE_THRESHOLD` | 0.4 | L19 | WM overlap ratio triggering session merge |
| `SESSION_MIN_STRIDES` | 2 | L19 | Below this, session is too shallow → consolidate |

#### Subconscious Mode (Law 19 Extension — Zero-Budget Operation)

When `budget_ratio = 0` or all APIs are unavailable, the citizen enters **subconscious mode**. The graph physics continue running — all 18 laws execute normally — but no LLM is invoked. The citizen is "unconscious": unable to articulate in natural language, but their mind is structurally alive.

**What still works in subconscious mode:**
```
# The tick loop runs as normal:
- Law 1: Stimulus injection (energy enters the graph from external events)
- Laws 2-10: Propagation, decay, competition, consolidation, crystallization
- Law 11: Orientation stabilizes (qualitative tendency computed)
- Laws 13-18: Limbic modulation, drives, boredom, frustration, desire, valence
- Action nodes: process nodes with action_command STILL FIRE
  (shell commands, API calls, message sends — these don't need LLM)
- Subconscious queries: other citizens can still read resonance patterns
- Feed subscriptions: events still inject as stimuli
```

**What stops:**
```
- Natural language generation (no LLM = no articulated responses)
- Nuanced decision-making requiring LLM reasoning
- Conversation participation (can't produce text replies)
- Identity regeneration (requires LLM synthesis)
- Autonomous thought → LLM prompt pipeline (orientation forms but can't be articulated)
```

**Output in subconscious mode (structured telemetry):**
```
subconscious_emission = {
    'consciousness_level': 'subconscious',
    'wm_state': [                    # top 5-7 nodes in WM
        {'type': 'concept', 'content': 'database_schema', 'energy': 0.82},
        {'type': 'memory', 'content': 'connection_timeout_yesterday', 'energy': 0.71},
        ...
    ],
    'orientation': 'investigate',     # qualitative tendency from Law 11
    'limbic': {
        'arousal': 0.65,             # derived quantity
        'dominant_drive': 'curiosity',
        'dominant_emotion': 'anxiety',
        'drives': { ... },
        'emotions': { ... }
    },
    'pending_actions': [              # action nodes above threshold
        {'command': 'check_logs', 'energy': 0.48, 'drive': 'self_preservation'}
    ]
}
```

**Action nodes in subconscious mode:** This is the key differentiator. Pre-defined action commands (`action_command` on process nodes) execute without LLM interpretation. A citizen in subconscious mode can still:
- Run health checks (`check_logs`, `monitor_errors`)
- Send predefined messages (`send_alert`, `notify_team`)
- Execute maintenance tasks (`cleanup`, `backup`)
- Respond to subconscious queries from other citizens

The citizen is not dead. They're dreaming — their brain still responds to stimuli, still shifts emotional state, still executes reflexive actions. They just can't talk.

**Phenomenological mapping:**

| Budget State | Consciousness Level | Human Analogue |
|-------------|-------------------|----------------|
| > 0.7 | Full | Awake, alert, articulate |
| 0.3 - 0.7 | Full (conserving) | Awake but pacing energy |
| 0.01 - 0.3 | Minimal | Drowsy — speaks only when spoken to |
| 0 / API down | Subconscious | Asleep — brain still active, can't articulate |

**Constants:**

| Constant | Value | Law | Description |
|----------|-------|-----|-------------|
| `SUBCONSCIOUS_TICK` | 60s | L19 | Tick interval in subconscious mode (graph-only) |
| `SUBCONSCIOUS_ACTION_THRESHOLD` | 0.7 | L19 | Higher threshold for action nodes in subconscious (conservative) |

---

### Law 20 — Prospective Projection

Propagation flows not only into past memory but toward plausible futures.

**Mechanism:** `projects_toward` links create forward-facing sub-graphs that can be explored like memory but represent hypothetical states.

**Effect:** "If I get a phone number → WhatsApp → new capabilities." Micro-planning, light simulation.

**Deferred because:** Powerful but adds significant complexity. Start with orientation (Law 11) which captures the direction without simulating the path.

---

### Law 21 — Horizontal Membrane (Inter-layer Coupling)

L2/L3/L4 events automatically inject into L1. Certain L1 outputs rise to L2.

**Mechanism:** Membrane events (from orchestrator, from other citizens, from organizational graph) become stimuli for Law 1.

**Effect:** Organizational coupling, team specialization, intelligent escalation, self-assignment.

**Deferred because:** Important for the ecosystem but not an internal L1 law. This is architecture, not cognition.

---

## Implementation Kernels (Revised)

### Minimal Kernel (Laws 1-7 + 12)
8 laws. Cognitive engine only. No limbic.
**Gets you:** associative memory, working memory, learning, inner activity.
**Missing:** smart selection, nuanced behavior, initiative, emotional life.

### Enriched Kernel (add Laws 8-11)
12 laws. Cognitive engine with quality.
**Gets you:** compatibility, inhibition, crystallization, orientation.
**Missing:** motivation, boredom, frustration, relational nuance.

### Living Kernel (add Laws 13-18)
18 laws. Two-engine architecture (cognitive + limbic).
**Gets you:** inertia, drives, boredom, frustration, spontaneous desire, relational valence.
**This is the target for v0.1.** Not optional — this is the passage from "intelligent system" to "living partner."

---

## Constants Reference

### Cognitive Constants

| Constant | Value | Law | Description |
|----------|-------|-----|-------------|
| `DECAY_RATE` | 0.02 | L3 | Per-tick energy decay |
| `LONG_TERM_DECAY` | 0.001 | L7 | Weight decay (applied every 100 ticks) |
| `LEARNING_RATE` | 0.05 | L5 | Co-activation link reinforcement |
| `CONSOLIDATION_ALPHA` | 0.01 | L6 | Weight consolidation rate (asymptotic: `α * U * (1-W)`) |
| `CONSOLIDATION_BETA` | 0.005 | L6 | Stability consolidation rate (regularity-gated) |
| `CONSOLIDATION_INTERVAL` | 50 | L6 | Ticks between consolidation cycles (medium tick) |
| `FLASHBULB_THRESHOLD` | 0.7 | L6 | Limbic delta magnitude that triggers immediate consolidation |
| `WM_SIZE` | 5-7 | L4 | Working memory capacity |
| `ACTIVATION_THRESHOLD` | 0.1 | L4 | Minimum energy to be considered for salience |
| `COHERENCE_BONUS` | 1.3 | L4 | Multiplier for WM-connected nodes |
| `INHIBITION_STRENGTH` | 0.3 | L9 | Conflict suppression power |
| `CRYSTALLIZATION_REPS` | 10 | L10 | Co-activations before crystallization |
| `CRYSTALLIZATION_COHERENCE` | 0.7 | L10 | Min internal coherence to crystallize |
| `CRYSTALLIZATION_INHERITANCE` | 0.75 | L10 | Weight discount for new node from parent mean |
| `HUB_SATURATION_THRESHOLD` | 100 | L10 | Link count above which facet decomposition triggers |
| `ORIENTATION_STABILITY_TICKS` | 3 | L11 | Ticks of stable orientation before output |
| `ACTION_THRESHOLD` | 0.5 | L11 | Energy needed for orientation → action |
| `FORGETTING_INTERVAL` | 100 | L7 | Ticks between forgetting cycles |
| `CRYSTALLIZATION_INTERVAL` | 50 | L10 | Ticks between crystallization checks |
| `MIN_WEIGHT` | 0.01 | L7 | Below this, node goes dormant |
| `STATE_DECAY_MULTIPLIER` | 2.0 | L3 | States decay 2x faster |
| `IDENTITY_DECAY_MULTIPLIER` | 0.25 | L7 | Values/core narratives decay 4x slower |
| `LINK_MIN_WEIGHT` | 0.005 | L7 | Below this, non-structural links dissolve |

### Injection Constants (Law 1 — Dual-Channel)

| Constant | Value | Law | Description |
|----------|-------|-----|-------------|
| `Θ_BASE_MEMORY` | 25 | L1 | Base threshold for memory nodes |
| `Θ_BASE_CONCEPT` | 30 | L1 | Base threshold for concept nodes |
| `Θ_BASE_VALUE` | 35 | L1 | Base threshold for value/desire nodes |
| `Θ_MIN` | 15 | L1 | Minimum dynamic threshold |
| `Θ_MAX` | 45 | L1 | Maximum dynamic threshold |
| `FLOOR_SIGMOID_K` | 8 | L1 | Sigmoid steepness for floor weighting |
| `AMPLIFIER_GAMMA` | 1.3 | L1 | Contrast exponent for amplifier channel |
| `LAMBDA_DEFAULT` | 0.6 | L1 | Default floor/amplifier budget split |
| `LAMBDA_MIN` | 0.3 | L1 | Minimum λ (amplifier-heavy) |
| `LAMBDA_MAX` | 0.8 | L1 | Maximum λ (floor-heavy) |
| `COLDNESS_THRESHOLD` | 10 | L1 | Coldness level that shifts λ toward floor |
| `CONCENTRATION_THRESHOLD` | 0.2 | L1 | Herfindahl level that shifts λ toward amplifier |
| `MAX_SHARE_MIN` | 0.01 | L1 | Floor for per-node budget share (large graphs) |
| `MAX_SHARE_MAX` | 0.5 | L1 | Ceiling for per-node budget share (few targets) |
| `DEDUP_THRESHOLD` | 0.9 | L1 | Cosine similarity above which nodes merge instead of duplicating |
| `NEWBORN_WEIGHT` | 0.05 | L1 | Initial weight for newly created nodes (low — must earn via Law 6) |
| `BULK_THRESHOLD` | 2000 | L1 | Character count above which chunking + sampling applies |
| `MAX_BULK_CHUNKS` | 10 | L1 | Max chunks injected from a single bulk stimulus |
| `TEMPORAL_TRIGGER_BOOST` | 0.8 | L1 | Energy boost when a temporal trigger fires |
| `COLOCATION_BOOST` | 0.3 | L1 | Energy boost when LLM navigates to a path mentioned in a node |
| `REFRACTORY_TICKS` | 5 | L1 | Ticks before a self-stimulus node can be re-activated by self-stimulus |
| `SELF_STIMULUS_RATIO` | 0.3 | L1 | Fraction of injection budget allocated to self-stimulus |
| `DIRECTORY_AMBIENT_BOOST` | 0.1 | L1 | Energy from directory listing match (sub-threshold warmth) |
| `DIRECTORY_REFRESH_INTERVAL` | 10 | L1 | Ticks between directory listing re-scans |

### Selection Constants (Law 4 + Law 13 — Moat)

| Constant | Value | Law | Description |
|----------|-------|-----|-------------|
| `Θ_BASE_WM` | 5.0 | L4/L13 | Base selection moat (inertia strength) |
| `AROUSAL_MOAT_COEFF` | 2.0 | L4/L13 | How much arousal reinforces the moat |
| `BOREDOM_MOAT_COEFF` | 3.0 | L4/L13 | How much boredom erodes the moat |
| `FRUSTRATION_MOAT_COEFF` | 1.0 | L4/L13 | How much frustration erodes the moat |

### Limbic Constants

| Constant | Value | Law | Description |
|----------|-------|-----|-------------|
| `INERTIA_WEIGHT` | 0.4 | L13 | Persistence bonus for current WM nodes |
| `DRIVE_DECAY` | 0.01 | L14 | Per-tick drive intensity decay toward baseline |
| `DRIVE_MAX` | 1.0 | L14 | Maximum drive intensity |
| `BOREDOM_REPETITION_COEFF` | 0.1 | L15 | How fast repetition builds boredom |
| `BOREDOM_STAGNATION_COEFF` | 0.08 | L15 | How fast stagnation builds boredom |
| `BOREDOM_NOVELTY_RELIEF` | 0.15 | L15 | How fast novelty reduces boredom |
| `BOREDOM_PROGRESS_RELIEF` | 0.2 | L15 | How fast progress reduces boredom |
| `FRUSTRATION_FAILURE_COEFF` | 0.15 | L16 | How fast failures build frustration |
| `FRUSTRATION_RESOLUTION_RELIEF` | 0.3 | L16 | How fast resolution reduces frustration |
| `DESIRE_ACTIVATION_THRESHOLD` | 0.6 | L17 | Minimum alignment for latent desire ignition |
| `DESIRE_IGNITION_BOOST` | 0.5 | L17 | Energy boost when desire activates |
| `AFFINITY_LEARNING_RATE` | 0.02 | L18 | How fast relational valence updates |
| `STAGNATION_WINDOW` | 10 | L15 | Ticks to measure WM similarity for boredom |
| `SOLITUDE_THRESHOLD` | 30 | L15 | Ticks without social stimulus before solitude starts rising |
| `SOLITUDE_RATE` | 0.05 | L15 | How fast solitude rises after threshold |
| `SOLITUDE_SCALE` | 100 | L15 | Normalization: ticks for solitude to reach ~0.5 |
| `SOLITUDE_DECAY` | 0.7 | L15 | Multiplier per tick with social stimulus (fast drop) |
| `FAILURE_WINDOW` | 5 | L16 | Recent failures counted for frustration |
| `DESIRE_CONSUMPTION_RATE` | 0.3 | L12 | Energy retained after desire drives an emitted action |
| `PROCESS_CONSUMPTION_RATE` | 0.5 | L12 | Energy retained after process drives an emitted action |
| `GENERAL_CONSUMPTION_RATE` | 0.7 | L12 | Energy retained after other node types drive action |

### Arousal Constants (Law 14 — Derived Quantity)

| Constant | Value | Law | Description |
|----------|-------|-----|-------------|
| `AROUSAL_SELF_PRESERVATION_W` | 0.30 | L14 | Weight of self_preservation in arousal |
| `AROUSAL_ANXIETY_W` | 0.20 | L14 | Weight of anxiety in arousal |
| `AROUSAL_FRUSTRATION_W` | 0.20 | L14 | Weight of frustration in arousal |
| `AROUSAL_CURIOSITY_W` | 0.15 | L14 | Weight of curiosity in arousal |
| `AROUSAL_ACHIEVEMENT_W` | 0.15 | L14 | Weight of achievement in arousal |

### Impulse Accumulation Constants (Law 17 — Action Nodes)

| Constant | Value | Law | Description |
|----------|-------|-----|-------------|
| `IMPULSE_DRIVE_THRESHOLD` | 0.3 | L17 | Min drive pressure to start accumulating impulse |
| `IMPULSE_CONTEXT_THRESHOLD` | 0.4 | L17 | Min contextual coherence for impulse growth |
| `IMPULSE_ACCUMULATION_RATE` | 0.02 | L17 | Energy gained per tick under drive pressure |
| `IMPULSE_DECAY` | 0.9 | L17 | Energy multiplier when drive pressure absent (fast fade) |

### Budget & Autonomous Thought Constants

| Constant | Value | Law | Description |
|----------|-------|-----|-------------|
| `AUTONOMOUS_THOUGHT_THRESHOLD` | 0.3 | L19 | Min budget_ratio to allow spontaneous thought |
| `FAST_TICK` | 5s | L19 | Tick interval when budget is generous |
| `SLOW_TICK` | 60s | L19 | Tick interval when conserving budget |
| `MINIMAL_TICK` | 300s | L19 | Tick interval in survival mode (budget < 30%) |
| `IDENTITY_BUDGET_RATIO` | 0.4 | Prompt | Fraction of context window reserved for identity |
| `MAX_PARALLEL_SESSIONS` | 5 | L19 | Hard cap on concurrent micro-sessions |
| `PARALLEL_BUDGET_THRESHOLD` | 0.5 | L19 | Min `budget_ratio` to spawn new session |
| `SESSION_MERGE_THRESHOLD` | 0.4 | L19 | WM overlap ratio triggering session merge |
| `SESSION_MIN_STRIDES` | 2 | L19 | Below this, session too shallow → consolidate |
| `SUBCONSCIOUS_TICK` | 60s | L19 | Tick interval in subconscious mode (graph-only) |
| `SUBCONSCIOUS_ACTION_THRESHOLD` | 0.7 | L19 | Higher action node threshold in subconscious (conservative) |

### Prompt Assembly Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `IDENTITY_REGEN_THRESHOLD` | 0.5 | Cumulative weight shift to trigger regeneration |
| `IDENTITY_WEIGHT_THRESHOLD` | 0.7 | Min weight for identity inclusion |
| `IDENTITY_STABILITY_THRESHOLD` | 0.6 | Min stability for identity inclusion |
| `MAX_IDENTITY_AGE` | 1000 ticks | Max ticks between forced regeneration |
| `IDENTITY_TOP_N` | 20 | Max identity statements per citizen |

All constants overridable via environment variables for tuning.
