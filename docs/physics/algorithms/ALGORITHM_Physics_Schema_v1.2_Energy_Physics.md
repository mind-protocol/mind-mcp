# Physics — Algorithm: Schema v1.2 Energy Physics

```
CREATED: 2025-12-23
UPDATED: 2025-12-25
STATUS: CANONICAL (v1.2 — no conductivity, weight controls flow)
```

---

## CHAIN

```
PATTERNS:       ../PATTERNS_Physics.md
BEHAVIORS:      ../BEHAVIORS_Physics.md
THIS:           ALGORITHM_Physics_Schema_v1.2_Energy_Physics.md
VALIDATION:     ../VALIDATION_Physics.md
IMPLEMENTATION: ../IMPLEMENTATION_Physics.md
HEALTH:         ../HEALTH_Physics.md
SYNC:           ../SYNC_Physics.md
```

---

## CORE MODEL

### Characters Generate, Moments Consume

```
Characters GENERATE energy (source — alive, thinking)
    ↓
Moments DRAW from connected characters (drain)
    ↓
Moments FLOW to all connected nodes (narratives, actors, spaces)
    ↓ via weight × emotion_proximity
Completion: LIQUIDATE to connected nodes, become inert bridge
```

### The Unified Formula

**All energy flow uses one formula (v1.2: no conductivity):**

```
flow = source.energy × base_rate × link.weight × emotion_factor
```

No special cases for speaker/witness/subject. Link properties determine everything.

---

## MOMENT LIFECYCLE

```
POSSIBLE ──→ ACTIVE ──→ COMPLETED
    │           │
    │           ├──→ INTERRUPTED (something else happens)
    │           │
    │           └──→ OVERRIDDEN (contradicted by new moment)
    │
    └──→ REJECTED (canon holder refuses)
```

### State Behaviors

| State | Energy Behavior | Graph Role |
|-------|-----------------|------------|
| POSSIBLE | None — exists but not considered | Potential |
| ACTIVE | Draws from actors, flows to nodes | Consuming attention |
| COMPLETED | Liquidates immediately to connected nodes | Becomes inert bridge |
| REJECTED | Energy returns to player | Discarded |
| INTERRUPTED | Liquidates to connected nodes | Cancelled |
| OVERRIDDEN | Redirects through player to new narrative | Contradicted |

### Transitions

**possible → active**
- Trigger: Canon holder validates
- Checks: Coherent with existing canon, no contradictions
- Effect: Starts drawing/flowing

**active → completed**
- Trigger: Canon holder approves for narration
- Checks: Energy > threshold, duration > minimum, valid
- Effect: Immediate liquidation, becomes bridge

**active → interrupted**
- Trigger: Another event supersedes
- Effect: Liquidate to connected nodes

**active → overridden**
- Trigger: New moment contradicts this one
- Effect: Redirect energy through player → new narrative's targets
- Remainder "haunts" original narrative

**possible → rejected**
- Trigger: Canon holder refuses
- Checks: Incoherent, contradicts canon, impossible
- Effect: Energy returns to player (consideration cost returned)

---

## ENERGY PHASES (Per Tick)

### Phase 1: Generation

```python
for actor in actors:
    actor.energy += actor.weight × generation_rate
    # No cap — decay handles runaway energy naturally
```

High-weight characters generate more.

---

### Phase 2: Moment Draw

Active moments draw from connected actors.

```python
for moment in active_moments:
    weighted_emotions = get_weighted_average_emotions(moment)

    for link in actor_links_to_moment:
        actor = link.source

        # Unified formula (v1.2: no conductivity)
        emotion_factor = emotion_proximity(link.emotions, weighted_emotions)
        flow_rate = link.weight × emotion_factor
        draw = actor.energy × base_rate × flow_rate

        # Transfer
        actor.energy -= draw
        moment.energy += draw

        # Link receives injection (tracks attention)
        link.energy += draw
        link.weight += draw × 0.1  # accumulated depth

        # Hebbian: color link with moment's emotions
        link.emotions = blend(link.emotions, weighted_emotions, draw/(draw+1))
```

**Why speaker draws more:** Their link has high weight (1.0), matching emotions. No special case needed.

**Why witness draws less:** Lower weight, partial emotion match.

---

### Phase 3: Moment Flow

Active moments flow to all connected nodes.

```python
for moment in active_moments:
    weighted_emotions = get_weighted_average_emotions(moment)
    speaker = get_speaker(moment)  # highest weight expresses link

    for link in outgoing_links:
        target = link.target

        # Base flow (v1.2: no conductivity)
        emotion_factor = emotion_proximity(link.emotions, weighted_emotions)
        base_flow = moment.energy × flow_rate × link.weight × emotion_factor

        if target.type == "actor" and speaker:
            # Apply path resistance from speaker
            resistance = path_resistance(speaker, target)
            flow = base_flow × (1 / (1 + resistance))
        else:
            flow = base_flow

        target.energy += flow

        # Hebbian coloring
        link.emotions = blend(link.emotions, weighted_emotions, flow/(flow+1))
```

---

### Phase 4: Narrative Backflow

Narratives with energy radiate to connected actors.

```python
for narrative in narratives:
    if narrative.energy < backflow_threshold:
        continue

    for link in narrative.actor_links:
        actor = link.target

        flow = narrative.energy × backflow_rate × link.weight × emotion_factor
        actor.energy += flow
```

**Why:** Themes "press" on characters. Violence narrative active → characters feel the tension.

---

### Phase 5: Decay

```python
# Link energy decays fast (attention fades)
for link in links:
    link.energy *= (1 - 0.4)  # 40% per tick

# Node energy decays based on weight
for node in nodes:
    decay_rate = 1 / (1 + node.weight)
    node.energy *= (1 - decay_rate × base_decay)
```

---

### Phase 6: Completion Processing

```python
for moment in moments_to_complete:
    # Liquidate to all connected nodes
    total_weight = sum(link.weight for link in moment.links)

    for link in moment.links:
        share = link.weight / total_weight
        target = link.target
        target.energy += moment.energy × share × liquidation_efficiency

    moment.energy = 0
    moment.status = COMPLETED
    # Moment remains as graph bridge
```

---

## PATH RESISTANCE

### Computed, Not Hops

Path resistance uses link properties, not hop count.

```python
def path_resistance(from_id, to_id):
    """Dijkstra with resistance = 1/(weight × emotion_factor)"""

    # Each edge: low weight = high resistance
    edge_resistance = 1 / (link.weight × emotion_factor)

    # Total = sum of edge resistances on shortest path
    return dijkstra_min_path(from_id, to_id, edge_resistance)

def flow_factor(from_id, to_id):
    resistance = path_resistance(from_id, to_id)
    return 1 / (1 + resistance)
```

**High weight path:** resistance low → flow factor high → energy flows easily

**Low weight path:** resistance high → flow factor low → energy blocked

---

### Moments as Bridges

Completed moments become permanent graph bridges.

```
Before m_encounter:
    aldric ──── bjorn (existing relationship)
    stranger (isolated)

After m_encounter COMPLETED:
    aldric ──── bjorn
       │          │
       └── m_encounter ──┘
              │
           stranger

Path aldric→stranger now exists:
    aldric → m_encounter → stranger
    resistance = link_resistance(aldric→m_encounter) + link_resistance(m_encounter→stranger)
```

**Implication:** Shared history creates closeness. More shared moments = lower resistance = easier energy flow.

---

## EMOTION MECHANICS

### Never Empty

Emotions are always computed, never absent.

```python
def get_link_emotions(link, source_node):
    if link.emotions:
        return link.emotions

    # Inherit from source's current focused state
    focused_links = [l for l in source_node.links if l.energy > threshold]
    return weighted_average_emotions(focused_links)
```

**Implication:** Stranger meeting aldric while terrified → new link immediately colored by fear.

---

### Weighted Average

```python
def weighted_average_emotions(emotion_lists):
    totals = {}
    for emotions in emotion_lists:
        for [name, intensity] in emotions:
            if name in totals:
                totals[name] = (totals[name] + intensity) / 2
            else:
                totals[name] = intensity
    return [[k, v] for k, v in totals.items()]
```

---

### Emotion Proximity

```python
def emotion_proximity(emotions_a, emotions_b):
    """0-1 similarity score"""
    if not emotions_a or not emotions_b:
        return 0.2  # minimal baseline, mostly blocked

    dict_a = {e[0]: e[1] for e in emotions_a}
    dict_b = {e[0]: e[1] for e in emotions_b}

    all_keys = set(dict_a.keys()) | set(dict_b.keys())
    overlap = sum(min(dict_a.get(k, 0), dict_b.get(k, 0)) for k in all_keys)
    total = sum(max(dict_a.get(k, 0), dict_b.get(k, 0)) for k in all_keys)

    return overlap / total if total > 0 else 0.2
```

---

### Hebbian Coloring

```python
def blend_emotions(link_emotions, incoming_emotions, blend_rate):
    """Energy flow colors the link"""
    result = {e[0]: e[1] for e in link_emotions}

    for [name, intensity] in incoming_emotions:
        if name in result:
            result[name] = min(1.0, result[name] + intensity × blend_rate)
        else:
            result[name] = intensity × blend_rate

    return [[k, v] for k, v in result.items()]
```

---

## LINK CRYSTALLIZATION

### Shared Moments Create Relationships

When two actors share a moment, physics creates `relates` link if none exists.

```python
def crystallize_links(completed_moment):
    actors = [link.target for link in moment.links if target.type == "actor"]

    for a, b in combinations(actors, 2):
        if not link_exists(a, b):
            # Create with inherited emotions
            create_link(
                a, b,
                type="relates",
                weight=0.2,  # weak initial
                emotions=weighted_average(a.focused_emotions, moment.emotions)
            )
```

---

## REDIRECT MECHANICS (Override)

When moment is overridden, energy redirects through player to new targets.

```python
def redirect_energy(old_moment, new_moment):
    speaker = get_speaker(old_moment)
    energy = old_moment.energy

    # Find new targets
    new_targets = new_moment.narrative_links

    for link in new_targets:
        target = link.target

        # Emotion proximity determines transfer rate
        proximity = emotion_proximity(old_moment.emotions, link.emotions)
        transfer_rate = 0.3 + 0.7 × proximity  # 30% minimum

        transfer = energy × share × transfer_rate
        target.energy += transfer

    # Remainder "haunts" original narrative
    remainder = energy - total_transferred
    for target in old_moment.narrative_targets:
        target.energy += remainder / len(targets)
```

**Narrative meaning:** Can't switch focus without residue. The intensity invested in one thing partially transfers, partially lingers.

---

## AGENT RESPONSIBILITIES

### World Runner

| Creates | Why |
|---------|-----|
| Possible moments | Procedural generation from graph state |
| New actors | Strangers, enemies emerge from narrative |
| Moment → actor links | Who's involved (speaker, witnesses, subjects) |

### Canon Holder

| Does | Why |
|------|-----|
| Validates possible → active | Prevents contradictions |
| Approves active → completed | Decides what becomes canon |
| Triggers interrupt/override | Handles conflicts |
| Rejects incoherent moments | Maintains consistency |

### Narrator

| Does | Why |
|------|-----|
| Creates moment → narrative links | Semantic understanding of what moment is "about" |
| Speaks completed moments | Generates prose from moment data |
| Uses emotions for tone | Fear → "gasps," "trembling" |

### Physics (Automatic)

| Does | Why |
|------|-----|
| Energy generation | Characters are alive |
| Draw/flow | Attention is finite |
| Decay | Things fade without reinforcement |
| Hebbian coloring | Relationships learn from experience |
| Link crystallization | Shared history creates bonds |
| Liquidation | Completion transfers charge |

---

## EXAMPLE: Full Scene Trace

### Setup

```
Nodes:
  aldric (actor, w=5, e=8)
  bjorn (actor, w=3, e=5)
  journey (narrative, w=2, e=3)

Links:
  aldric ↔ bjorn (relates, cond=0.8, emotions=[trust,0.7])
  aldric → journey (relates, cond=0.9)
  bjorn → journey (relates, cond=0.6)
```

### Tick 0: Encounter

**Runner creates:**
```
stranger (actor, w=1, e=2)
m_encounter (moment, POSSIBLE)
  - aldric → m_encounter (expresses, cond=1.0, w=1.0)
  - bjorn → m_encounter (expresses, cond=0.8, w=0.6)
  - m_encounter → stranger (about, cond=1.0)
  - m_encounter → journey (relates, cond=0.7)
```

**Canon holder:** Validates → ACTIVE

**Physics:**
```
Generate: aldric +2.5→10.5, bjorn +1.5→6.5, stranger +0.5→2.5

Draw (unified formula):
  aldric: 10.5 × 0.3 × 1.0 × 1.0 × 0.5 = 1.58
  bjorn: 6.5 × 0.3 × 0.8 × 0.6 × 0.5 = 0.47
  m_encounter.energy = 2.05

Flow:
  → stranger: 0.21 (× path factor)
  → journey: 0.07

Decay: all nodes
```

### Tick 1: "Please don't kill me"

**Runner creates:**
```
m_plea (moment, POSSIBLE)
  - stranger → m_plea (expresses, cond=1.0, w=1.0, emotions=[fear,0.9])
  - aldric → m_plea (expresses, cond=0.3, w=0.2)
  - bjorn → m_plea (expresses, cond=0.2, w=0.1)
  - m_plea → stranger (about, emotions=[vulnerability,0.8])
  - m_plea → aldric (about, emotions=[power,0.6])
  - m_plea → violence (relates, cond=0.9, emotions=[fear,0.9])
```

**Canon holder:** Validates → ACTIVE

**Physics:**
```
Draw (unified):
  stranger: 2.97 × 0.3 × 1.0 × 1.0 × 0.9 = 0.80  ← speaker draws most
  aldric: 11.27 × 0.3 × 0.3 × 0.2 × 0.5 = 0.10
  bjorn: 7.38 × 0.3 × 0.2 × 0.1 × 0.5 = 0.02
  m_plea.energy = 0.92

Flow:
  → violence: 0.15 ← narrative awakens
  → stranger: 0.15
  → aldric: 0.04
```

### Tick 2: Completion

**Canon holder:** m_plea energy sufficient → COMPLETED

**Liquidation:**
```
m_plea.energy (0.92) distributed:
  → stranger: 0.28
  → aldric: 0.23
  → bjorn: 0.09
  → violence: 0.32
m_plea.energy = 0
```

**Link crystallization:**
```
stranger ↔ aldric (NEW, emotions=[fear,0.7])
stranger ↔ bjorn (NEW, emotions=[fear,0.5])
```

**m_plea becomes bridge:**
```
Path stranger→aldric now: stranger→m_plea→aldric
```

**Narrator speaks:**
> "Please," he gasps, voice cracking. "Please don't kill me."

---

## SCHEMA CHANGES (v1.1)

### LinkBase

```yaml
LinkBase:
  fields:
    id: string, required
    node_a: string, required
    node_b: string, required
    type: enum [contains, leads_to, expresses, sequence, primes, can_become, relates]
    weight: float [0,∞], default 1.0  # importance + accumulated depth (grows with traversal)
    energy: float [0,∞], default 0  # current attention
    emotions: List[[string, float]], default []
    created_at_s: int, required
    # Note: conductivity removed in v1.2 — weight controls flow rate
    # Note: strength merged into weight in v1.2 — weight now dual-purpose
```

### Moment

```yaml
Moment:
  fields:
    id: string, required
    text: string, default ""
    status: enum [possible, active, completed, rejected, interrupted, overridden]
    energy: float [0,∞], default 0
    tick_created: int, required
    tick_activated: int, optional
    tick_resolved: int, optional
```

### Actor

```yaml
Actor:
  extends: NodeBase
  fields:
    # No energy_capacity — decay handles runaway energy naturally
```

---

## CONSTANTS

```python
GENERATION_RATE = 0.5          # energy per tick per unit weight
MOMENT_DRAW_RATE = 0.3         # base draw rate
MOMENT_FLOW_RATE = 0.2         # base flow rate
NARRATIVE_BACKFLOW_RATE = 0.1  # slower than moment flow
BACKFLOW_THRESHOLD = 0.5       # min narrative energy to radiate

LINK_ENERGY_DECAY = 0.4        # 40% per tick (attention fades fast)
BASE_NODE_DECAY = 0.1          # multiplied by 1/(1+weight)

LIQUIDATION_EFFICIENCY = 0.9   # 90% of energy transfers
REJECTION_RETURN_RATE = 0.8    # 80% returns to player

EMOTION_EMPTY_BASELINE = 0.2   # flow factor when no emotions
```

---

## VALIDATION

Simulation (`diffusion_sim_v2.py`) confirms:

| Behavior | Validated |
|----------|-----------|
| Characters generate energy | ✓ |
| Unified draw formula (no speaker/witness special case) | ✓ |
| Path resistance (not hops) | ✓ |
| Emotion proximity gates flow | ✓ |
| Hebbian link coloring | ✓ |
| Override redirects with haunting | ✓ |
| Liquidation on completion | ✓ |
| Narrative backflow | ✓ |

---

## MARKERS

### Todos

<!-- @mind:todo Implement all 6 tick phases in runtime/physics/tick.py -->
<!-- @mind:todo Add path resistance Dijkstra to graph_ops -->
<!-- @mind:todo Implement link crystallization on moment completion -->
<!-- @mind:todo Add moment state machine (possible→active→completed) to canon_holder -->
<!-- @mind:todo Implement narrative backflow in physics tick -->

### Escalations

<!-- @mind:escalation
title: "COMPLETION_THRESHOLD: What energy level triggers active→completed?"
priority: 4
context: "Canon holder approves active→completed when energy > threshold. What's the threshold?"
options:
  - "A: Fixed threshold (e.g., 1.0 energy)"
  - "B: Relative to speaker weight (e.g., 0.2 × speaker.weight)"
  - "C: Duration-based (e.g., 3 ticks active minimum)"
recommendation: "B — ties completion to character importance"
-->

<!-- @mind:escalation
title: "CRYSTALLIZATION_STRENGTH: How strong are auto-created relates links?"
priority: 4
context: "When actors share a moment, crystallization creates relates link. Current spec: weight=0.2"
options:
  - "A: Fixed weak (0.2, 0.2) — requires repeated interaction to strengthen"
  - "B: Proportional to moment energy — intense moments create stronger bonds"
  - "C: Inherit from speaker's existing link strengths"
recommendation: "B — moment intensity should matter"
-->

### Propositions

<!-- @mind:proposition
title: "Batch processing for large graphs"
description: "Phase 2-3 (moment draw/flow) could bottleneck on large graphs. Consider batching moments by locality or energy level."
priority: 3
-->

<!-- @mind:proposition
title: "Energy conservation validation"
description: "Add health check that verifies total energy (generated - decayed - liquidated) balances each tick. Detects leaks."
priority: 4
-->

<!-- @mind:proposition
title: "Emotion vocabulary for common feelings"
description: "Optional vocabulary of common emotions with pre-computed embeddings for faster proximity calculation."
priority: 2
-->
