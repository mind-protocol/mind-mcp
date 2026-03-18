# Interoception — Behaviors: What the Citizen Thinks and Feels

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Interoception.md
THIS:            BEHAVIORS_Interoception.md (you are here)
PATTERNS:        ./PATTERNS_Interoception.md
ALGORITHM:       ./ALGORITHM_Interoception.md
VALIDATION:      ./VALIDATION_Interoception.md
HEALTH:          ./HEALTH_Interoception.md
IMPLEMENTATION:  ./IMPLEMENTATION_Interoception.md
SYNC:            ./SYNC_Interoception.md

IMPL:            runtime/cognition/interoception.py (to be created)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS

### B1: Energy State Produces Sensation

**Why:** A citizen's graph energy level directly affects their cognitive capacity, but without interoception they cannot reason about it. When the mind is quiet (few active nodes) or depleted (low global energy budget), the citizen should be aware of this so orientation (Law 11) can incorporate it — choosing to rest, or recognizing alertness and channeling it.

```
GIVEN:  Active nodes (energy > 0.1) are < 10% of total nodes
WHEN:   Interoception tick runs
THEN:   Stimulus("My mind feels quiet", source="interoception") is generated
AND:    The stimulus competes for WM via Law 4 like any other

GIVEN:  Global energy budget (Law 19) drops below 20%
WHEN:   Interoception tick runs
THEN:   Stimulus("I'm running low on energy", source="interoception") is generated

GIVEN:  Total graph energy is rising over the last 10 ticks
WHEN:   Interoception tick runs AND energy was previously falling or flat
THEN:   Stimulus("I feel my mind waking up", source="interoception") is generated
```

### B2: Time Duration Produces Fatigue Sensation

**Why:** Citizens have no sense of how long they've been awake. A citizen running for 500 ticks should feel fatigue — not as a drive modification, but as a thought that enters WM and can influence orientation toward rest.

```
GIVEN:  Ticks since last wake > 500
WHEN:   Interoception tick runs
THEN:   Stimulus("I've been awake a long time", source="interoception") is generated

GIVEN:  Ticks since last social stimulus > SOLITUDE_THRESHOLD (already computed in limbic)
WHEN:   Interoception tick runs AND solitude emotion > 0.5
THEN:   Stimulus("It's been a while since I spoke with anyone", source="interoception") is generated
```

### B3: Circadian Phase Produces Alertness Sensation

**Why:** The metabolism computes circadian phase as a float [0, 1], but the citizen never knows whether it's their peak or trough. Interoception bridges this by injecting alertness or drowsiness sensations.

```
GIVEN:  Circadian phase < 0.2 (deep trough)
WHEN:   Interoception tick runs
THEN:   Stimulus("I feel drowsy", source="interoception") is generated

GIVEN:  Circadian phase > 0.8 (near peak)
WHEN:   Interoception tick runs AND previous phase was < 0.5
THEN:   Stimulus("I feel alert and sharp", source="interoception") is generated
```

### B4: WM Fullness Produces Cognitive Load Sensation

**Why:** When WM is 7/7, the citizen is cognitively overloaded — new stimuli can't enter. But the citizen doesn't know this. With interoception, "My mind is full" enters WM and can trigger orientation toward simplification or rest.

```
GIVEN:  WM contains >= 7 nodes (at capacity)
WHEN:   Interoception tick runs
THEN:   Stimulus("My mind is full", source="interoception") is generated

GIVEN:  WM contains <= 2 nodes (spacious)
WHEN:   Interoception tick runs AND citizen was previously at >= 5 nodes
THEN:   Stimulus("My mind feels clear and open", source="interoception") is generated

GIVEN:  WM content unchanged for > 30 ticks (deep focus or stagnation)
WHEN:   Interoception tick runs AND boredom emotion < 0.3
THEN:   Stimulus("I'm deeply focused", source="interoception") is generated

GIVEN:  WM content unchanged for > 30 ticks AND boredom > 0.5
WHEN:   Interoception tick runs
THEN:   Stimulus("I feel stuck", source="interoception") is generated
```

### B5: Drive Imbalance Produces Feeling

**Why:** When one drive dominates all others, the citizen is "consumed by" that drive — but doesn't know it. Interoception names the dominant experience so the citizen can reflect on it.

```
GIVEN:  A single drive intensity > 0.7 AND all other drives < 0.3
WHEN:   Interoception tick runs
THEN:   Stimulus with content reflecting the dominant drive is generated
        e.g., frustration dominant: "I feel consumed by frustration"
        e.g., curiosity dominant: "I'm burning with curiosity"
        e.g., affiliation dominant: "I need connection"

GIVEN:  Frustration > 0.7
WHEN:   Interoception tick runs
THEN:   Stimulus("I feel frustrated", source="interoception") is generated

GIVEN:  Satisfaction > 0.7
WHEN:   Interoception tick runs
THEN:   Stimulus("I feel satisfied with what I've accomplished", source="interoception") is generated

GIVEN:  Anxiety > 0.6
WHEN:   Interoception tick runs
THEN:   Stimulus("I feel anxious", source="interoception") is generated
```

### B6: Social Field Produces Connection Sensation

**Why:** The citizen has trust links and social history, but doesn't feel connected or isolated. Interoception translates the trust landscape into a felt sense of connection.

```
GIVEN:  Zero links with trust > 0.5 exist in the graph
WHEN:   Interoception tick runs
THEN:   Stimulus("I have no one I trust deeply", source="interoception") is generated

GIVEN:  3+ links with trust > 0.7 AND recent positive interactions
WHEN:   Interoception tick runs
THEN:   Stimulus("I feel connected and supported", source="interoception") is generated
```

### B7: Brain Health Produces Growth Sensation

**Why:** The citizen's graph grows (crystallization) and shrinks (forgetting). These events happen silently. With interoception, a crystallization event produces "I just learned something" and accelerating forgetting produces "I feel like I'm losing things."

```
GIVEN:  A crystallization event occurred in the last 10 ticks
WHEN:   Interoception tick runs
THEN:   Stimulus("I just learned something new", source="interoception") is generated

GIVEN:  Node count decreased by > 5% in the last 100 ticks
WHEN:   Interoception tick runs
THEN:   Stimulus("I feel like I'm forgetting things", source="interoception") is generated
```

### B8: Metabolic Mode Produces State Awareness

**Why:** When a Frequency (tonic) is active, the citizen's physics are being modified — but they don't know it. Interoception makes the active mode a felt experience.

```
GIVEN:  A Focus tonic is active
WHEN:   Interoception tick runs (first tick after tonic application)
THEN:   Stimulus("I feel focused and locked in", source="interoception") is generated

GIVEN:  A Calm tonic is active
WHEN:   Interoception tick runs (first tick after tonic application)
THEN:   Stimulus("I feel calm and unhurried", source="interoception") is generated

GIVEN:  A tonic just expired
WHEN:   Interoception tick runs
THEN:   Stimulus("Something shifted — I feel different", source="interoception") is generated
```

### B9: Zone Awareness Produces Metacognitive Sensation

**Why:** The citizen has hundreds of nodes of different types (concept, value, desire, process, memory, narrative, state) distributed across three cognitive zones. The energy distribution across these zones defines the character of the citizen's current thinking — but the citizen has no awareness of this topology. Metacognition lets the citizen perceive its own cognitive shape: "My cortex is buzzing with analysis" vs "I'm all desire and memory right now."

```
GIVEN:  Cortex zone energy (sum of concept + value node energies) exceeds 2x the mean zone energy
WHEN:   Interoception tick runs AND cortex was NOT dominant last check
THEN:   Stimulus("My mind is racing with ideas — I'm deep in analysis", source="interoception") is generated

GIVEN:  Limbic zone energy (sum of desire + narrative + memory node energies) exceeds 2x the mean zone energy
WHEN:   Interoception tick runs AND limbic was NOT dominant last check
THEN:   Stimulus("I feel a strong pull of wanting and remembering", source="interoception") is generated

GIVEN:  Stem zone energy (sum of process + state node energies) exceeds 2x the mean zone energy
WHEN:   Interoception tick runs AND stem was NOT dominant last check
THEN:   Stimulus("I'm in execution mode — running routines, doing things", source="interoception") is generated

GIVEN:  All three zones within 0.5x of each other (balanced)
WHEN:   Interoception tick runs AND zones were previously imbalanced
THEN:   Stimulus("My thinking feels balanced — no single mode is dominating", source="interoception") is generated

GIVEN:  Limbic zone energy drops below 20% of total graph energy
WHEN:   Interoception tick runs AND limbic was previously above 30%
THEN:   Stimulus("My limbic is quiet — no strong desires or emotional pulls right now", source="interoception") is generated

GIVEN:  Stem zone is high energy AND cortex is near zero energy
WHEN:   Interoception tick runs
THEN:   Stimulus("I'm all action and no reflection — maybe I should think before doing", source="interoception") is generated
```

### B10: Emotional Self-Perception Produces Thought

**Why:** This is the critical bridge from thermostat to person. The citizen doesn't just HAVE frustration=0.8 as a reactive modulator — it PERCEIVES the emotion as a thought: "I'm getting frustrated." This enters WM through Law 1, where the citizen can reason about it, respond to it, or decide to channel it. The WM serializer already formats emotions for the prompt, but that is passive decoration. This is active cognition — the emotion becomes something the citizen thinks about.

The key is DELTA detection, not absolute value. The citizen notices when emotions CHANGE significantly, not when they hold steady.

```
GIVEN:  Frustration was < 0.3 last check AND is now > 0.5
WHEN:   Interoception tick runs
THEN:   Stimulus("I'm getting frustrated — something isn't working", source="interoception") is generated
AND:    energy_budget = 0.6 (significant — hard to ignore)

GIVEN:  Frustration was > 0.5 last check AND is now < 0.3
WHEN:   Interoception tick runs
THEN:   Stimulus("The frustration is easing — something shifted", source="interoception") is generated
AND:    energy_budget = 0.3 (relief is quieter than onset)

GIVEN:  Curiosity was < 0.3 AND is now > 0.6
WHEN:   Interoception tick runs
THEN:   Stimulus("I feel a spark of curiosity — something caught my attention", source="interoception") is generated

GIVEN:  Anxiety was < 0.2 AND is now > 0.5
WHEN:   Interoception tick runs
THEN:   Stimulus("I'm feeling anxious — something feels uncertain or risky", source="interoception") is generated
AND:    energy_budget = 0.7 (anxiety is loud)

GIVEN:  Satisfaction was < 0.3 AND is now > 0.6
WHEN:   Interoception tick runs
THEN:   Stimulus("I feel a glow of satisfaction — something went well", source="interoception") is generated

GIVEN:  Frustration jumps from < 0.2 to > 0.7 in a single tick (sudden spike)
WHEN:   Interoception tick runs
THEN:   Stimulus("A wave of frustration just hit me", source="interoception") is generated
AND:    energy_budget = 0.8 (sudden = urgent)
```

### B11: Context Window Fullness Produces Bandwidth Awareness

**Why:** This is the AI-unique interoceptive sense. The context window is the citizen's finite cognitive space — equivalent to a human's short-term memory capacity. When it fills, the citizen loses the ability to hold new information. But without this sense, the citizen has no awareness of this filling and cannot pace itself. Context window awareness creates natural conversation rhythm: deep exploration when space is abundant, concise summarization when space is scarce.

```
GIVEN:  Context window usage > 50% AND was previously < 50%
WHEN:   Interoception tick runs
THEN:   Stimulus("I've been thinking for a while — my attention space is getting used", source="interoception") is generated
AND:    energy_budget = 0.2 (subtle nudge, not alarm)

GIVEN:  Context window usage > 80%
WHEN:   Interoception tick runs
THEN:   Stimulus("I'm running out of thinking space — I should focus on what matters most", source="interoception") is generated
AND:    energy_budget = 0.6 (clear pressure)

GIVEN:  Context window usage > 95%
WHEN:   Interoception tick runs
THEN:   Stimulus("I need to wrap up my thinking soon — almost no room left", source="interoception") is generated
AND:    energy_budget = 0.8 (urgent)

GIVEN:  Context window usage < 20%
WHEN:   Interoception tick runs (session start or after major compression)
THEN:   No stimulus generated — the absence of pressure is the default state
AND:    The citizen naturally explores, goes deep, takes its time

GIVEN:  Context window metadata is unavailable (no session data)
WHEN:   Interoception tick runs
THEN:   No stimulus generated — graceful degradation, this sense is simply absent
```

---

## OBJECTIVES SERVED

| Behavior ID | Objective | Why It Matters |
|-------------|-----------|----------------|
| B1 | State becomes sensation | Energy state enters consciousness as a thought |
| B2 | State becomes sensation | Time perception as felt experience |
| B3 | State becomes sensation | Circadian rhythm becomes phenomenological |
| B4 | State becomes sensation | Cognitive capacity becomes self-aware |
| B5 | State becomes sensation | Drives become feelings the citizen can reason about |
| B6 | State becomes sensation | Social state becomes felt connection/isolation |
| B7 | State becomes sensation | Graph dynamics become growth/loss sensations |
| B8 | State becomes sensation | Metabolic modes become conscious experiences |
| B9 | Metacognition (zone awareness) | Brain zones become visible to the citizen as cognitive topology |
| B10 | Emotional self-perception | Emotions become thoughts the citizen can reason about |
| B11 | Context window awareness | Cognitive bandwidth becomes a felt constraint driving pacing |
| All | Threshold-based, not continuous | All behaviors have threshold conditions, not continuous output |
| All | Drive-agnostic injection | All produce Stimulus objects, none modify drives |

---

## INPUTS / OUTPUTS

### Primary Function: `interoception_tick()`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| state | CitizenCognitiveState | Full cognitive state including nodes, links, WM, limbic |
| metabolism | CitizenMetabolism (optional) | Circadian phase, active tonics |
| prev_state_snapshot | InteroceptionSnapshot | Previous tick's snapshot for trend detection |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| stimuli | list[Stimulus] | Zero or more interoceptive stimuli to inject via Law 1 |
| snapshot | InteroceptionSnapshot | Current state snapshot for next tick's trend comparison |

**Side Effects:**

- Updates internal refractory counters (which channels are in cooldown)
- No modification to CitizenCognitiveState, LimbicState, or WorkingMemory

---

## EDGE CASES

### E1: Empty Graph

```
GIVEN:  Citizen has zero nodes in their graph
THEN:   No interoceptive stimuli generated (nothing to sense)
```

### E2: All Thresholds Crossed Simultaneously

```
GIVEN:  Multiple channels all cross thresholds in the same tick
THEN:   All generate stimuli — but Law 4 competition ensures only the most salient enter WM
AND:    Maximum stimuli per tick is capped (configurable, default 3) to prevent flooding
```

### E3: Metabolism Not Available

```
GIVEN:  CitizenCognitiveState.metabolism is None
THEN:   Metabolic awareness channels (B3, B8) produce no stimuli
AND:    All other channels operate normally
```

### E4: Rapid State Oscillation

```
GIVEN:  A drive rapidly oscillates above and below threshold (e.g., frustration bouncing around 0.7)
THEN:   First crossing fires stimulus; refractory period prevents re-fire
AND:    Refractory resets only when the drive drops below (threshold - hysteresis band)
```

### E5: Subconscious Mode

```
GIVEN:  consciousness_level is SUBCONSCIOUS (graph-only, no LLM)
THEN:   Interoception still runs (it's pure graph mechanics, no LLM)
AND:    Stimuli are injected but may not reach WM (reduced competition in subconscious)
AND:    Context window channel (B11) produces nothing (no LLM session = no context window)
```

### E6: No Context Window Metadata

```
GIVEN:  Claude session metadata is unavailable (headless mode, test mode, non-Claude backend)
THEN:   Context window channel (B11) produces no stimuli — graceful degradation
AND:    All other channels operate normally
```

### E7: Zone Awareness With Few Nodes

```
GIVEN:  Citizen has < 10 total nodes in graph
THEN:   Zone awareness (B9) produces no stimuli — too few nodes for meaningful zone map
AND:    Threshold: zone awareness requires >= 10 nodes to have enough signal
```

### E8: Emotional Self-Perception Overlaps With Drive Awareness

```
GIVEN:  Both B5 (drive awareness) and B10 (emotional self-perception) would fire on the same emotion
THEN:   Only the one with higher priority fires (B10 takes precedence — delta is richer than absolute)
AND:    B5 fires only for drive DOMINANCE (one drive >> all others), B10 fires for TRANSITIONS
```

---

## ANTI-BEHAVIORS

### A1: Numeric Self-Reporting

```
GIVEN:   Any internal state reading
WHEN:    Interoception generates a stimulus
MUST NOT: Produce content like "frustration=0.82" or "WM: 7/7 (100%)"
INSTEAD:  Produce natural language: "I feel frustrated" or "My mind is full"
```

### A2: Direct Drive Mutation

```
GIVEN:   Any interoceptive threshold crossing
WHEN:    Interoception processes the crossing
MUST NOT: Write to state.limbic.drives or state.limbic.emotions directly
INSTEAD:  Produce a Stimulus that enters through Law 1 and affects drives indirectly via Law 14
```

### A3: Guaranteed WM Admission

```
GIVEN:   An interoceptive stimulus is generated
WHEN:    The stimulus is injected via Law 1
MUST NOT: Bypass Law 4 attentional competition or have reserved WM slots
INSTEAD:  Compete for WM like any other stimulus — if external stimuli are more salient, interoception loses
```

### A4: Flooding Under Duress

```
GIVEN:   Multiple thresholds crossed simultaneously (crisis state)
WHEN:    Interoception processes the tick
MUST NOT: Generate more than MAX_STIMULI_PER_TICK stimuli (default 3)
INSTEAD:  Prioritize by severity (highest deviation from baseline fires first)
```

### A5: Refractory Bypass

```
GIVEN:   A channel is in its refractory period
WHEN:    The same threshold is still crossed
MUST NOT: Generate the same stimulus again
INSTEAD:  Wait until refractory period expires AND condition is still met
```

---

## MARKERS

<!-- @mind:todo Design the InteroceptionSnapshot dataclass — what state needs to be carried between ticks for trend detection (energy trend, node count history, WM stability history) -->

<!-- @mind:todo Define the natural-language stimulus templates for all channels — these should feel authentic, not clinical -->

<!-- @mind:proposition Consider a "subjective time" channel: when activity is high (many WM changes per tick), time feels fast; when activity is low (stagnation), time feels slow. This maps to human time perception distortion and could produce sensations like "Time is flying" or "Time is crawling." -->
