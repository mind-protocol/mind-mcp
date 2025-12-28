# Graph — Algorithm: Energy Flow

```
CREATED: 2024-12-16
STATUS: Canonical
```

---

## OVERVIEW

This algorithm defines the per-tick energy flow, decay, and pressure update
cycle for the living graph. It specifies how character energy moves into
narratives, how narratives propagate through link types, and how flips are
detected after weight and pressure updates.

## DATA STRUCTURES

- Character: `energy`, `location`, and belief links to narratives.
- Narrative: `energy`, `weight`, `focus`, `last_active_tick`, and link edges.
- Link: `type`, `strength`, `source`, `target`, plus optional metadata.

Note: Tension/pressure is computed from narrative contradictions and energy concentration, not stored as separate entities.

## ALGORITHM: graph_tick

Primary entry point for the physics update loop. Runs a deterministic,
non-LLM tick that updates energy, weights, and pressures, then reports flips
to the orchestrator.

## Per-Tick Processing

Every tick (5 minutes game time), the graph engine runs this sequence:

```
1. Compute character energies
2. Flow energy from characters to narratives
3. Propagate energy between narratives
4. Decay energy
5. Recompute narrative weights
6. Detect energy threshold crossings
```

---

## KEY DECISIONS

- Energy is derived, not set: all updates flow through relationships and
  link structure to keep the story emergent and avoid direct overrides.
- Decay is the only dynamic knob: `decay_rate` is adjustable to maintain
  criticality while link factors and breaking points remain fixed.
- Transfers are collected before applying: this avoids order dependency in
  propagation and makes the tick deterministic for a given graph state.

## DATA FLOW

Character beliefs produce energy, which flows into narratives, propagates
across narrative links, decays, and then informs weight recalculation. The
updated weights drive tension pressure updates, which can trigger flips that
the orchestrator passes to the world runner.

## COMPLEXITY

Let `C` be characters, `N` narratives, `L` narrative links:
energy and weight steps are O(C + N + L), and threshold detection is O(N).
The full tick is linear in the graph size.

## HELPER FUNCTIONS

- `compute_character_energy` and `compute_proximity` for character energy.
- `flow_energy_from_characters` to inject energy into narratives.
- `propagate_energy`, `decay_with_exceptions`, `check_conservation`,
  `adjust_criticality` for flow and decay control.
- `recompute_weights`, `tick_pressures`, `detect_flips` for state updates.

## INTERACTIONS

The orchestrator calls `graph_tick` each time a player action advances time.
GraphOps provides the query/mutation surface for narrative, link, and pressure
data, while the world runner consumes flipped pressures to generate changes.

## MARKERS

- Confirm the exact source of `player` and `current_tick` in tick context.
- Validate propagation factors against current GraphOps link taxonomy.
- Decide whether to bound propagation by `MAX_HOPS` or rely on link sparsity.

## Step 1: Compute Character Energies

```python
def compute_character_energy(character, player):
    # Relationship intensity: how much player cares
    intensity = 0
    for narrative in graph.narratives_about(character):
        if player.believes(narrative):
            intensity += player.belief_strength(narrative)

    # Geographical proximity
    proximity = compute_proximity(character.location, player.location)

    return intensity * proximity

def compute_proximity(char_loc, player_loc):
    if char_loc == player_loc:
        return 1.0
    elif same_region(char_loc, player_loc):
        return 0.7
    elif adjacent_region(char_loc, player_loc):
        return 0.4
    else:
        days = travel_days(char_loc, player_loc)
        if days == 1: return 0.2
        elif days == 2: return 0.1
        else: return 0.05
```

---

## Step 2: Flow Energy Into Narratives

```python
BELIEF_FLOW_RATE = 0.1

def flow_energy_from_characters():
    for character in graph.characters:
        for narrative in character.believed_narratives():
            belief_strength = character.belief_strength(narrative)
            flow = character.energy * belief_strength * BELIEF_FLOW_RATE
            narrative.energy += flow
```

---

## Step 3: Propagate Between Narratives

Different link types flow differently. Contradictions heat both sides. Supersession drains the old.

```python
MAX_HOPS = 3

# Link type factors — each type has its own propagation strength
LINK_FACTORS = {
    'contradicts': 0.30,   # high — arguments need two hot takes
    'supports': 0.20,      # medium — allies rise together
    'elaborates': 0.15,    # lower — details inherit from parent
    'subsumes': 0.10,      # lowest — many specifics feed one general
    'supersedes': 0.25,    # draining — new gains, old loses
}

def propagate_energy():
    # Collect all transfers first (avoid order dependency)
    transfers = []
    drains = []  # for supersession

    for narrative in graph.narratives:
        for link in narrative.outgoing_links:
            target = link.target
            factor = LINK_FACTORS[link.type]
            transfer = narrative.energy * link.strength * factor

            if link.type == 'contradicts':
                # Bidirectional: contradiction heats both sides
                transfers.append((target, transfer))
                # Reverse direction handled when processing from target

            elif link.type == 'supports':
                # Bidirectional: allies rise together
                transfers.append((target, transfer))

            elif link.type == 'elaborates':
                # Unidirectional: general → specific
                transfers.append((target, transfer))

            elif link.type == 'subsumes':
                # Unidirectional: specific → general
                transfers.append((target, transfer))

            elif link.type == 'supersedes':
                # Draining: old loses, new gains
                transfers.append((target, transfer))
                drains.append((narrative, transfer * 0.5))

    # Apply transfers
    for target, amount in transfers:
        target.energy += amount

    # Apply drains (supersession)
    for source, drain in drains:
        source.energy -= drain
```

---

## Step 4: Decay Energy

```python
# Dynamic — adjusted by criticality feedback
decay_rate = 0.02
MIN_WEIGHT = 0.01

def decay_energy():
    for narrative in graph.narratives:
        # Apply decay
        narrative.energy *= (1 - decay_rate)

        # Floor at minimum
        if narrative.energy < MIN_WEIGHT:
            narrative.energy = MIN_WEIGHT

def decay_with_exceptions():
    """Version with exception handling"""
    global decay_rate

    for narrative in graph.narratives:
        # Skip recently active
        if narrative.last_active_tick >= current_tick - 10:
            continue

        # Core narratives decay slower
        rate = decay_rate
        if narrative.type in ['oath', 'blood', 'debt']:
            rate *= 0.25

        # Focused narratives decay slower
        if narrative.focus > 1.0:
            rate /= narrative.focus

        narrative.energy *= (1 - rate)
        narrative.energy = max(narrative.energy, MIN_WEIGHT)

def check_conservation():
    """
    Soft global constraint on total energy.
    Open system: not conservation, but prevents runaway.
    """
    global decay_rate

    TARGET_MIN_ENERGY = 10.0  # scale with graph size
    TARGET_MAX_ENERGY = 50.0  # scale with graph size

    total_energy = sum(n.energy for n in graph.narratives)

    if total_energy > TARGET_MAX_ENERGY:
        decay_rate *= 1.05  # cool down
    if total_energy < TARGET_MIN_ENERGY:
        decay_rate *= 0.95  # heat up

def adjust_criticality():
    """
    Maintain system near critical threshold.
    decay_rate is THE KNOB — safe to adjust.
    """
    global decay_rate

    avg_pressure = mean([p.level for p in graph.pressure_points])
    hot_count = sum(1 for p in graph.pressure_points if p.level > 0.7)
    recent_breaks = count_breaks_in_last_hour()

    # System too cold — let it heat
    if avg_pressure < 0.3 or hot_count == 0:
        decay_rate *= 0.9

    # System too hot — dampen
    if avg_pressure > 0.6 or recent_breaks > 3:
        decay_rate *= 1.1

    # Clamp to sane range
    decay_rate = max(0.005, min(decay_rate, 0.1))

# NEVER DYNAMICALLY ADJUST:
# - breaking_point (changes story meaning)
# - belief_flow_rate (changes character importance)
# - link propagation factors (changes story structure)
```

---

## Step 5: Recompute Weights

Weight is the computed importance of a narrative. It determines:
- What surfaces in the Narrator's context
- What the player hears as voices
- How fast related tensions build

**Weight is never set directly. It emerges from structure.**

### Weight Formula

```python
def compute_weight(narrative):
    raw_weight = (
        belief_intensity(narrative) *
        player_connection_factor(narrative) *
        (1 + contradiction_bonus(narrative)) *
        recency_factor(narrative)
    )

    # Clamp and apply focus evolution
    return clamp(raw_weight * focus_evolution(narrative), 0, 1)
```

### Component: Belief Intensity

```python
def belief_intensity(narrative):
    total = 0
    for believer in narrative.believers:
        importance = believer.connection_to_player
        belief_strength = believer.belief_strength(narrative)
        total += importance * belief_strength
    return total
```

Believer importance is computed from:
- Direct relationship with player
- Proximity (physical and graph distance)
- Recent interactions

### Component: Player Connection

```python
def player_connection_factor(narrative):
    # Direct: player believes it
    if player.believes(narrative):
        return 1.0

    # Indirect: about someone player knows
    for subject in narrative.about:
        if player.knows(subject):
            distance = graph_distance(player, subject)
            return 1.0 / (1 + distance)

    # Distant: no direct connection
    return 0.1
```

### Component: Contradiction Bonus

```python
def contradiction_bonus(narrative):
    bonus = 0
    for other in narrative.contradicts:
        if player.believes(other):
            # Bonus is limited by weaker of the two
            bonus += min(narrative.weight, other.weight) * 0.5
    return bonus
```

Contradictions create tension, and tension demands attention.

### Component: Recency Factor

```python
def recency_factor(narrative):
    ticks_since_active = current_tick - narrative.last_active_tick

    if ticks_since_active <= 10:
        return 1.0
    elif ticks_since_active <= 50:
        return 0.8
    elif ticks_since_active <= 100:
        return 0.5
    else:
        return 0.2
```

### Focus Evolution

```python
def focus_evolution(narrative):
    """
    focus > 1.0: weight rises faster, falls slower
    focus < 1.0: weight rises slower, falls faster
    focus = 1.0: normal evolution
    """
    if narrative.weight_increasing:
        return narrative.focus
    else:
        return 1.0 / narrative.focus
```

The Narrator sets focus. This is how authorial intent shapes the graph without overriding it.

### When Weight Is Recomputed

Weight is recomputed each tick after energy flow:

```python
def recompute_weights():
    for narrative in graph.narratives:
        old_weight = narrative.weight
        narrative.weight = compute_weight(narrative)
        narrative.weight_increasing = narrative.weight > old_weight
```

### Weight Thresholds

| Weight Range | Meaning |
|--------------|---------|
| 0.8 - 1.0 | Critical — always in context |
| 0.5 - 0.8 | Active — usually in context |
| 0.2 - 0.5 | Relevant — included if space |
| 0.01 - 0.2 | Dormant — rarely surfaces |

### Example Computation

**Narrative:** `narr_edmund_betrayal`

| Component | Value | Notes |
|-----------|-------|-------|
| Belief intensity | 1.8 | Player (1.0 × 1.0) + Aldric (0.8 × 1.0) |
| Player connection | 1.0 | Player believes it directly |
| Contradiction bonus | 0.3 | Contradicts "Edmund was forced" (0.6 weight) |
| Recency factor | 1.0 | Active 5 ticks ago |
| Focus | 1.2 | Narrator wants this prominent |

```
raw_weight = 1.8 × 1.0 × 1.3 × 1.0 = 2.34
clamped = clamp(2.34 × 1.0, 0, 1) = 1.0
```

This narrative is at maximum weight — always in context.

---

## Step 6: Tick Pressures

```python
BASE_RATE = 0.001  # per minute
DEFAULT_BREAKING_POINT = 0.9

def tick_pressures(time_elapsed_minutes):
    for pressure_point in graph.pressure_points:
        if pressure_point.pressure_type == 'gradual':
            tick_gradual(pressure_point, time_elapsed_minutes)
        elif pressure_point.pressure_type == 'scheduled':
            tick_scheduled(pressure_point)
        elif pressure_point.pressure_type == 'hybrid':
            tick_hybrid(pressure_point, time_elapsed_minutes)

        # Check for flip
        if pressure_point.level >= pressure_point.breaking_point:
            mark_for_flip(pressure_point)

def tick_gradual(pressure_point, time_elapsed):
    focus = average_focus(pressure_point.narratives)
    max_weight = max_narrative_weight(pressure_point.narratives)

    delta = time_elapsed * BASE_RATE * focus * max_weight
    pressure_point.level = min(pressure_point.level + delta, 1.0)

def tick_scheduled(pressure_point):
    for checkpoint in pressure_point.progression:
        if current_time >= checkpoint.at:
            pressure_point.level = max(pressure_point.level, checkpoint.pressure)

def tick_hybrid(pressure_point, time_elapsed):
    # Tick gradual component
    focus = average_focus(pressure_point.narratives)
    max_weight = max_narrative_weight(pressure_point.narratives)
    ticked = pressure_point.level + (time_elapsed * BASE_RATE * focus * max_weight)

    # Find scheduled floor
    floor = 0
    for checkpoint in pressure_point.progression:
        if current_time >= checkpoint.at:
            floor = max(floor, checkpoint.pressure_floor)

    # Use higher of ticked or floor
    pressure_point.level = min(max(ticked, floor), 1.0)
```

---

## Step 7: Detect Flips

```python
def detect_flips():
    flipped = []
    for pressure_point in graph.pressure_points:
        if pressure_point.level >= pressure_point.breaking_point:
            flipped.append(pressure_point)
    return flipped
```

When flips are detected, the orchestrator calls the World Runner.

---

## Full Tick

```python
def graph_tick(time_elapsed_minutes):
    """Complete tick cycle - no LLM, pure computation"""

    # 1. Character energies (relationship × proximity)
    for character in graph.characters:
        character.energy = compute_character_energy(character, player)

    # 2. Flow into narratives (characters pump)
    flow_energy_from_characters()

    # 3. Propagate between narratives (link-type dependent)
    propagate_energy()

    # 4. Decay
    decay_with_exceptions()

    # 5. Check conservation (soft global constraint)
    check_conservation()

    # 6. Adjust criticality (dynamic decay_rate)
    adjust_criticality()

    # 7. Weight recomputation
    recompute_weights()

    # 8. Pressure ticks
    tick_pressures(time_elapsed_minutes)

    # 9. Detect flips
    flipped = detect_flips()

    return flipped  # Orchestrator handles these
```

---

## Automatic Tension from Approach

When characters move, proximity changes. Energy follows automatically.

```python
# Edmund's energy as player approaches York
#
# Day 1 (one day travel):
#   Edmund: intensity=4.0, proximity=0.2 → energy=0.8
#
# Day 2 (same region):
#   Edmund: intensity=4.0, proximity=0.7 → energy=2.8
#
# No one decided this. Physics decided this.
# Confrontation pressure rises because Edmund's narratives heat up.
```

---

## Parameters Summary

| Parameter | Value | Notes |
|-----------|-------|-------|
| belief_flow_rate | 0.1 | Character → Narrative (FIXED) |
| max_propagation_hops | 3 | Prevents infinite chains |
| decay_rate | 0.02 (dynamic) | Adjusted by conservation + criticality |
| decay_rate_min | 0.005 | Floor for dynamic adjustment |
| decay_rate_max | 0.1 | Ceiling for dynamic adjustment |
| min_weight | 0.01 | Never fully zero |
| base_rate | 0.001 | Pressure per minute |
| default_breaking_point | 0.9 | When flips trigger (NEVER TOUCH) |
| tick_threshold | 5 min | Minimum time between ticks |

---

## Link Type Factors

| Link Type | Factor | Direction | Effect |
|-----------|--------|-----------|--------|
| **contradicts** | 0.30 | Bidirectional | Both sides heat — argument needs two takes |
| **supports** | 0.20 | Bidirectional | Allies rise together — doubt one, doubt all |
| **elaborates** | 0.15 | General → Specific | Details inherit from parent |
| **subsumes** | 0.10 | Specific → General | Many specifics feed bigger picture |
| **supersedes** | 0.25 | Draining | New gains, old loses 50% of transfer |

---

## Conservation Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| target_min_energy | 10.0 | Scale with graph size |
| target_max_energy | 50.0 | Scale with graph size |
| adjustment_factor | 0.05 | How fast decay adjusts (5% per check) |

---

## Never Adjust Dynamically

| Parameter | Why |
|-----------|-----|
| breaking_point | Changes story meaning |
| belief_flow_rate | Changes character importance |
| link propagation factors | Changes story structure |

Only `decay_rate` is safe to adjust — it's the temperature knob, not the story knob.

---

*"Pure physics. No authorial injection. The story emerges from the web."*

---

## CHAIN

PATTERNS: ../PATTERNS_Graph.md
BEHAVIORS: ../BEHAVIORS_Graph.md
ALGORITHM: ../../ALGORITHM_Physics.md
SYNC: ../SYNC_Graph.md
