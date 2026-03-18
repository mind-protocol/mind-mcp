# Interoception — Algorithm: Threshold-Based Stimulus Generation

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Interoception.md
BEHAVIORS:       ./BEHAVIORS_Interoception.md
PATTERNS:        ./PATTERNS_Interoception.md
THIS:            ALGORITHM_Interoception.md (you are here)
VALIDATION:      ./VALIDATION_Interoception.md
HEALTH:          ./HEALTH_Interoception.md
IMPLEMENTATION:  ./IMPLEMENTATION_Interoception.md
SYNC:            ./SYNC_Interoception.md

IMPL:            runtime/cognition/interoception.py (to be created)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

Interoception runs once per tick, after the limbic update and before orientation. It scans 11 internal sense channels (organized across somatic, metacognitive, and substrate-awareness layers), each with configurable thresholds and refractory periods. When a threshold is crossed and the channel is not in refractory cooldown, a natural-language Stimulus is generated and appended to the output list. The output list is then injected via Law 1 in the same tick (or queued for next tick, depending on placement).

The algorithm is deliberately simple: read state, compare to thresholds, gate by refractory, emit. No inference. No LLM. No graph traversal beyond counting nodes and links. Pure arithmetic on the same data structures the limbic system already maintains.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| State becomes sensation | B1-B11 | Threshold checks translate numeric state into language |
| Threshold-based, not continuous | B1-B11 | Thresholds ensure silence when nothing is noteworthy |
| Refractory protection | B1-B11 | Refractory gating prevents flooding |
| Drive-agnostic injection | B1-B11 | Output is Stimulus objects, never direct drive writes |
| Metacognition (zone awareness) | B9 | Zone energy aggregation produces cognitive topology awareness |
| Emotional self-perception | B10 | Delta detection on emotions produces reflective thought-stimuli |
| Context window awareness | B11 | Context usage estimation produces bandwidth pressure |

---

## DATA STRUCTURES

### InteroceptionSnapshot

Carries state between ticks for trend detection. Updated at the end of each interoception tick.

```
InteroceptionSnapshot:
    total_graph_energy: float       # sum of all node energies this tick
    active_node_count: int          # nodes with energy > 0.1
    total_node_count: int           # total nodes in graph
    wm_node_ids: set[str]           # WM contents this tick
    wm_size: int                    # len(wm_node_ids)
    energy_trend: list[float]       # last N total_graph_energy values (rolling window, N=10)
    node_count_history: list[int]   # last N total_node_count values (rolling window, N=100)
    tick_count: int                 # current tick
    last_wake_tick: int             # tick of last wake event
    last_crystallization_tick: int  # tick of last crystallization
    active_tonic_names: list[str]   # names of currently active tonics
    prev_tonic_names: list[str]     # names from previous tick (for expiry detection)

    # Zone awareness (metacognition)
    zone_energies: dict[str, float] # {"stem": X, "limbic": Y, "cortex": Z} — energy by brain zone
    prev_zone_energies: dict[str, float]  # previous tick's zone energies for shift detection

    # Emotional self-perception
    prev_drive_intensities: dict[str, float]   # previous tick's drive intensities for delta detection
    prev_emotion_intensities: dict[str, float] # previous tick's emotion intensities for delta detection

    # Context window
    context_window_usage: float     # [0.0, 1.0] — estimated context window fullness
    prev_context_window_usage: float  # previous tick's context usage for threshold crossing
```

### InteroceptionChannel

Configuration for a single interoceptive sense channel.

```
InteroceptionChannel:
    name: str                       # e.g., "energy_quiet", "wm_full", "frustration_high"
    refractory_ticks: int           # minimum ticks between firings (default 30)
    last_fired_tick: int            # tick when this channel last produced a stimulus
    hysteresis_band: float          # threshold must drop by this much before re-arming (default 0.1)
    is_armed: bool                  # whether the channel can fire (refractory expired AND condition resolved)
```

### InteroceptionState

Persistent state for the interoception engine across ticks.

```
InteroceptionState:
    channels: dict[str, InteroceptionChannel]   # keyed by channel name
    snapshot: InteroceptionSnapshot              # previous tick's snapshot
    stimuli_generated_total: int                 # lifetime counter for observability
```

---

## ALGORITHM: `interoception_tick()`

### Step 1: Capture Current State

Read all relevant internal state into local variables. This is a pure read operation — no mutations.

```
active_nodes = count(node for node in state.nodes.values() if node.energy > 0.1)
total_nodes = len(state.nodes)
total_energy = sum(node.energy for node in state.nodes.values())
wm_size = len(state.wm.node_ids)
wm_node_ids = set(state.wm.node_ids)
wm_stability = state.wm.stability_ticks
drives = state.limbic.drives
emotions = state.limbic.emotions
circadian_phase = metabolism.circadian_phase() if metabolism else None
active_tonics = [t.name for t in metabolism.active_tonics] if metabolism else []
tick = state.tick_count

# Zone awareness: aggregate energy by node_type → brain zone
zone_energies = {"stem": 0.0, "limbic": 0.0, "cortex": 0.0}
ZONE_MAP = {
    "process": "stem", "state": "stem",
    "desire": "limbic", "narrative": "limbic", "memory": "limbic",
    "concept": "cortex", "value": "cortex",
}
for node in state.nodes.values():
    zone = ZONE_MAP.get(node.node_type.value, "cortex")
    zone_energies[zone] += node.energy

# Emotional self-perception: capture current drive/emotion intensities
current_drives = {name: drive.intensity for name, drive in drives.items()}
current_emotions = dict(emotions)

# Context window: estimate usage from available metadata
context_usage = estimate_context_window_usage(session_metadata)  # [0.0, 1.0] or None
```

### Step 2: Run Channel Checks

For each interoceptive channel, evaluate the threshold condition. If the condition is met AND the channel is armed (refractory expired, condition was previously not met), generate a stimulus.

Channels are evaluated in priority order (strongest sensations first). A per-tick cap (MAX_STIMULI_PER_TICK = 3) prevents flooding.

```
stimuli = []

for channel in sorted(channels, key=priority, reverse=True):
    if len(stimuli) >= MAX_STIMULI_PER_TICK:
        break

    if not channel.is_armed:
        # Check if refractory expired AND condition resolved (hysteresis)
        if tick - channel.last_fired_tick >= channel.refractory_ticks:
            if condition_below_hysteresis(channel):
                channel.is_armed = True
        continue

    reading = evaluate_channel(channel, state, metabolism, snapshot)
    if reading.fires:
        stimuli.append(Stimulus(
            content=reading.content,
            energy_budget=reading.energy,
            source="interoception",
            is_social=False,
            is_failure=False,
            is_novelty=False,
            is_progress=False,
        ))
        channel.is_armed = False
        channel.last_fired_tick = tick
```

### Step 3: Update Snapshot

Capture current state into a new InteroceptionSnapshot for the next tick's trend detection.

```
new_snapshot = InteroceptionSnapshot(
    total_graph_energy=total_energy,
    active_node_count=active_nodes,
    total_node_count=total_nodes,
    wm_node_ids=wm_node_ids,
    wm_size=wm_size,
    energy_trend=snapshot.energy_trend[-9:] + [total_energy],
    node_count_history=snapshot.node_count_history[-99:] + [total_nodes],
    tick_count=tick,
    last_wake_tick=snapshot.last_wake_tick,
    last_crystallization_tick=snapshot.last_crystallization_tick,
    active_tonic_names=active_tonics,
    prev_tonic_names=snapshot.active_tonic_names,
)
```

### Step 4: Return Stimuli

Return the list of stimuli for injection via Law 1.

---

## KEY DECISIONS

### D1: Channel Priority (which sensation fires first when multiple thresholds crossed)

```
IF multiple channels fire simultaneously:
    Priority order (highest first):
    1. Context window critical (> 95% — imminent cognitive truncation)
    2. Energy budget critically low (survival)
    3. Emotional spike (sudden delta > 0.5 — urgent self-perception)
    4. Extreme emotion (frustration > 0.8, anxiety > 0.8)
    5. WM full (cognitive overload)
    6. Context window pressure (> 80% — bandwidth constraint)
    7. Emotional rising edge (delta > 0.2 — significant transition)
    8. Circadian trough (drowsiness)
    9. Zone dominance shift (metacognitive topology change)
    10. Social isolation (solitude)
    11. Brain health (growth/shrinkage)
    12. Emotional falling edge (relief — less urgent than onset)
    13. Mild emotions (moderate drives)
    14. Zone balance / quiet zone
    15. Energy trend (waking up / quieting down)
    16. Context window mild (> 50% — subtle nudge)
    WHY: Substrate limits (context) and sudden emotional spikes are highest.
         Then survival, overload, bandwidth, transitions, circadian, topology.
         Subtle perceptions at bottom.
```

### D2: Hysteresis Band (preventing rapid re-fire on oscillating values)

```
IF drive crosses threshold upward (e.g., frustration > 0.7):
    Channel fires, enters refractory
    Channel re-arms ONLY when:
        tick >= last_fired_tick + refractory_ticks
        AND drive < threshold - hysteresis_band (e.g., frustration < 0.6)
    WHY: Prevents rapid fire-rearm-fire if value hovers near threshold
ELSE:
    Channel remains disarmed until both conditions met
```

### D3: Stimulus Energy Budget (how loud is an interoceptive sensation)

```
IF extreme state (drive > 0.8 or critical condition):
    energy_budget = 0.8 (loud — competes strongly for WM)
    WHY: Extreme internal states should be hard to ignore
ELIF moderate state (drive > 0.5 or notable condition):
    energy_budget = 0.4 (moderate — present but easily overridden by strong external stimulus)
    WHY: Moderate feelings are background awareness, not shouting
ELSE:
    energy_budget = 0.2 (quiet — subtle awareness, easily displaced)
    WHY: Mild sensations inform without demanding attention
```

### D4: WM Stability as Focus vs Stagnation

```
IF wm.stability_ticks > 30 AND boredom < 0.3:
    Interpret as deep focus: "I'm deeply focused"
    WHY: Stable WM + low boredom = productive concentration
ELIF wm.stability_ticks > 30 AND boredom > 0.5:
    Interpret as stagnation: "I feel stuck"
    WHY: Stable WM + high boredom = unproductive repetition
ELSE:
    No focus/stagnation stimulus
```

### D5: Energy Trend Detection

```
IF last 10 energy readings show consistent increase (linear regression slope > 0.05):
    "I feel my mind waking up"
    WHY: Rising energy = increasing activation, worth noting
ELIF last 10 energy readings show consistent decrease (slope < -0.05):
    "My mind is quieting down"
    WHY: Falling energy = deactivation, worth noting
ELSE:
    No trend stimulus (stable or noisy)
```

### D6: Zone Awareness — Aggregation and Threshold

```
# Aggregate energy by zone
stem_energy  = sum(node.energy for node in state.nodes.values() if node.node_type in {PROCESS, STATE})
limbic_energy = sum(node.energy for node in state.nodes.values() if node.node_type in {DESIRE, NARRATIVE, MEMORY})
cortex_energy = sum(node.energy for node in state.nodes.values() if node.node_type in {CONCEPT, VALUE})
total_zone_energy = stem_energy + limbic_energy + cortex_energy
mean_zone = total_zone_energy / 3.0

IF any zone > 2.0 * mean_zone AND that zone was NOT dominant last tick:
    Emit zone dominance stimulus: "My cortex is buzzing" / "I feel a strong pull of wanting" / "I'm in execution mode"
    WHY: A zone becoming dominant is a significant cognitive shift worth perceiving

IF all zones within 0.5x of each other AND zones were previously imbalanced:
    Emit balance stimulus: "My thinking feels balanced"
    WHY: Return to equilibrium is also a noteworthy transition

IF a zone drops below 20% of total AND was previously above 30%:
    Emit quiet-zone stimulus: "My limbic is quiet — no strong pulls"
    WHY: A zone going quiet is the inverse of dominance — equally informative

Minimum node count: 10 nodes required for zone awareness to fire at all
    WHY: With < 10 nodes, zone energy is too sparse for meaningful topology
```

### D7: Emotional Self-Perception — Delta Detection

```
# For each drive and emotion, compute delta from previous tick
FOR each drive_name in drives:
    current = drives[drive_name].intensity
    previous = snapshot.prev_drive_intensities.get(drive_name, current)
    delta = current - previous

    IF delta > 0.2 AND current > threshold_map[drive_name]:
        # Rising edge: emotion is intensifying significantly
        Emit rising stimulus with content from RISING_TEMPLATES[drive_name]
        energy_budget = 0.6 + 0.2 * (delta / 0.5)  # louder for bigger jumps, cap at 0.8
        WHY: Rapid emotional changes deserve attention

    IF delta < -0.2 AND previous > threshold_map[drive_name]:
        # Falling edge: emotion is easing
        Emit relief stimulus with content from FALLING_TEMPLATES[drive_name]
        energy_budget = 0.3  # relief is quieter
        WHY: Resolution is worth noticing but less urgent than onset

    IF abs(delta) > 0.5:
        # Sudden spike: very rapid change (single tick)
        Override content with SPIKE_TEMPLATES[drive_name]
        energy_budget = 0.8  # sudden = urgent
        WHY: A sudden emotional spike is alarming and demands attention

Threshold map (minimum intensity to be worth perceiving):
    frustration: 0.5, curiosity: 0.6, anxiety: 0.5, satisfaction: 0.6,
    care: 0.5, achievement: 0.5, affiliation: 0.4, novelty_hunger: 0.5

NOTE: B10 (emotional self-perception) takes priority over B5 (drive dominance)
when both would fire on the same emotion. B5 is about absolute dominance;
B10 is about transitions. They serve different cognitive purposes.
```

### D8: Context Window — Estimation and Pressure

```
# Estimate context window usage
IF session_metadata provides token_count and max_tokens:
    context_usage = token_count / max_tokens
ELIF conversation history is available:
    # Heuristic estimation:
    estimated_tokens = (
        system_prompt_tokens_estimate        # ~2000-5000 for identity/framework
        + wm_serialization_chars / 4         # rough char-to-token ratio
        + conversation_turn_count * 500      # average tokens per turn
        + accumulated_stimulus_count * 50    # interoceptive history
    )
    context_usage = min(1.0, estimated_tokens / MAX_CONTEXT_WINDOW)
ELSE:
    context_usage = None  # no data — channel is inert

IF context_usage is None:
    No stimulus — graceful degradation

IF context_usage > 0.5 AND prev_context_usage <= 0.5:
    Emit mild awareness: "I've been thinking for a while"
    energy_budget = 0.2
    WHY: Subtle pacing nudge, not alarm

IF context_usage > 0.8:
    Emit clear pressure: "I'm running out of thinking space"
    energy_budget = 0.6
    WHY: The citizen needs to prioritize and compress

IF context_usage > 0.95:
    Emit urgent: "I need to finish my thought soon"
    energy_budget = 0.8
    WHY: Imminent truncation — wrap up now

IF context_usage < 0.2:
    No stimulus — absence of pressure is the default
    WHY: Low usage means freedom. No need to announce freedom.
```

---

## DATA FLOW

```
CitizenCognitiveState + CitizenMetabolism + InteroceptionState
    |
    v
Step 1: Capture State (pure reads)
    |
    v
Step 2: Channel Evaluation (threshold + refractory checks)
    |
    v
Step 3: Stimulus Generation (natural-language content)
    |
    v
Step 4: Snapshot Update (for next tick)
    |
    v
list[Stimulus] → injected into tick runner → Law 1
```

---

## COMPLEXITY

**Time:** O(C + N) per tick — C channels (constant, ~30 with new zone/emotion/context channels) + N nodes for energy counting and zone aggregation. N is the node count, but the energy sum and zone aggregation can be done in a single pass.

**Space:** O(C + W) — C channel states + W rolling window entries (energy_trend=10, node_count_history=100). Constant and small.

**Bottlenecks:**
- Node counting: `sum(1 for n in state.nodes.values() if n.energy > 0.1)` iterates all nodes. For graphs with 1000+ nodes, this could be worth caching. But at current scale (~200 nodes per citizen), this is trivial.
- Trust link counting: `sum(1 for l in state.links if l.trust > 0.5)` iterates all links. Same consideration.

---

## HELPER FUNCTIONS

### `evaluate_energy_channels(state, snapshot) -> list[ChannelReading]`

**Purpose:** Evaluate all energy-perception channels.

**Logic:** Check active_node ratio, global energy budget, and energy trend. Return ChannelReadings for any that fire.

### `evaluate_time_channels(state, snapshot) -> list[ChannelReading]`

**Purpose:** Evaluate awake duration and time-since-social.

**Logic:** Compare tick_count to last_wake_tick and ticks_since_social to thresholds.

### `evaluate_cognitive_load_channels(state, snapshot) -> list[ChannelReading]`

**Purpose:** Evaluate WM fullness, WM stability, and stagnation.

**Logic:** Check wm.size against capacity and stability_ticks against focus/stagnation thresholds.

### `evaluate_drive_channels(state) -> list[ChannelReading]`

**Purpose:** Evaluate drive intensity and imbalance.

**Logic:** Check each drive/emotion against its threshold. Detect single-drive dominance.

### `evaluate_social_channels(state) -> list[ChannelReading]`

**Purpose:** Evaluate trust landscape and solitude depth.

**Logic:** Count high-trust links, check solitude emotion intensity.

### `evaluate_metabolic_channels(metabolism, snapshot) -> list[ChannelReading]`

**Purpose:** Evaluate circadian phase and active tonics.

**Logic:** Check circadian_phase against trough/peak thresholds. Detect tonic changes (new application, expiry).

### `evaluate_brain_health_channels(state, snapshot) -> list[ChannelReading]`

**Purpose:** Evaluate node count trends and recent crystallization events.

**Logic:** Compare current node count to history (shrinkage detection). Check for recent crystallization events.

### `evaluate_zone_awareness_channels(state, snapshot) -> list[ChannelReading]`

**Purpose:** Evaluate brain zone energy distribution (metacognition). Produces stimuli when zone balance shifts significantly.

**Logic:** Aggregate node energy by node_type into three zones (stem, limbic, cortex). Compare to previous tick's zone energies. Detect dominance (zone > 2x mean), balance (all zones within 0.5x), and quiet zones (zone < 20% of total after being > 30%).

**Minimum:** Requires >= 10 total nodes. With fewer nodes, zone aggregation is too noisy.

### `evaluate_emotional_self_perception_channels(state, snapshot) -> list[ChannelReading]`

**Purpose:** Detect significant emotional transitions (deltas) and produce reflective thought-stimuli.

**Logic:** Compare current drive/emotion intensities to previous tick's values. Fire on rising edges (intensity crosses threshold from below), falling edges (drops below threshold from above), and sudden spikes (delta > 0.5 in single tick). Content uses natural-language templates, not numbers.

**Priority:** B10 (emotional self-perception) takes precedence over B5 (drive dominance) when both target the same emotion.

### `evaluate_context_window_channels(session_metadata, snapshot) -> list[ChannelReading]`

**Purpose:** Estimate context window fullness and produce bandwidth pressure stimuli.

**Logic:** Read token count from session metadata if available. Otherwise estimate from WM serialization size + conversation turns. Fire at 50% (mild), 80% (clear), 95% (urgent) thresholds. No stimulus below 50% or when metadata is unavailable.

**Degradation:** If no context data is available, this function returns empty — the citizen simply lacks this sense.

---

## CHANNEL CONFIGURATION TABLE

| Channel Name | Threshold | Refractory (ticks) | Hysteresis | Energy Budget | Content Template |
|---|---|---|---|---|---|
| `energy_quiet` | active_nodes < 10% of total | 50 | 0.05 | 0.3 | "My mind feels quiet" |
| `energy_budget_low` | global budget < 20% | 100 | 0.05 | 0.8 | "I'm running low on energy" |
| `energy_rising` | trend slope > 0.05 | 30 | 0.03 | 0.2 | "I feel my mind waking up" |
| `energy_falling` | trend slope < -0.05 | 30 | 0.03 | 0.2 | "My mind is quieting down" |
| `time_fatigue` | awake_ticks > 500 | 100 | N/A | 0.4 | "I've been awake a long time" |
| `time_lonely` | solitude > 0.5 | 50 | 0.15 | 0.4 | "It's been a while since I spoke with anyone" |
| `circadian_drowsy` | phase < 0.2 | 100 | 0.1 | 0.4 | "I feel drowsy" |
| `circadian_alert` | phase > 0.8 AND was < 0.5 | 100 | 0.1 | 0.3 | "I feel alert and sharp" |
| `wm_full` | wm_size >= 7 | 30 | N/A | 0.5 | "My mind is full" |
| `wm_clear` | wm_size <= 2 AND was >= 5 | 50 | N/A | 0.2 | "My mind feels clear and open" |
| `wm_deep_focus` | stability > 30 AND boredom < 0.3 | 50 | N/A | 0.2 | "I'm deeply focused" |
| `wm_stuck` | stability > 30 AND boredom > 0.5 | 30 | 0.15 | 0.5 | "I feel stuck" |
| `frustration_high` | frustration > 0.7 | 20 | 0.15 | 0.6 | "I feel frustrated" |
| `anxiety_high` | anxiety > 0.6 | 20 | 0.15 | 0.6 | "I feel anxious" |
| `satisfaction_high` | satisfaction > 0.7 | 30 | 0.2 | 0.3 | "I feel satisfied with what I've accomplished" |
| `drive_dominant` | max_drive > 0.7 AND others < 0.3 | 50 | 0.2 | 0.5 | (varies by drive) |
| `social_isolated` | trust_links(>0.5) == 0 | 100 | N/A | 0.5 | "I have no one I trust deeply" |
| `social_connected` | trust_links(>0.7) >= 3 | 100 | N/A | 0.2 | "I feel connected and supported" |
| `brain_crystallized` | crystallization in last 10 ticks | 30 | N/A | 0.3 | "I just learned something new" |
| `brain_shrinking` | node_count dropped > 5% in 100 ticks | 100 | 0.03 | 0.4 | "I feel like I'm forgetting things" |
| `tonic_applied` | new tonic in active_tonics | 10 | N/A | 0.3 | (varies by tonic) |
| `tonic_expired` | tonic left active_tonics | 10 | N/A | 0.3 | "Something shifted — I feel different" |
| `zone_cortex_dominant` | cortex energy > 2x mean zone | 40 | 0.3 | 0.4 | "My mind is racing with ideas" |
| `zone_limbic_dominant` | limbic energy > 2x mean zone | 40 | 0.3 | 0.4 | "I feel a strong pull of wanting and remembering" |
| `zone_stem_dominant` | stem energy > 2x mean zone | 40 | 0.3 | 0.3 | "I'm in execution mode" |
| `zone_balanced` | all zones within 0.5x of each other | 60 | N/A | 0.2 | "My thinking feels balanced" |
| `zone_quiet` | a zone drops below 20% of total (was > 30%) | 50 | 0.1 | 0.3 | (varies by zone: "My limbic is quiet") |
| `emotion_rising` | drive/emotion delta > 0.2, crosses threshold | 15 | 0.15 | 0.6 | (varies: "I'm getting frustrated") |
| `emotion_falling` | drive/emotion delta < -0.2, drops below threshold | 15 | 0.15 | 0.3 | (varies: "The frustration is easing") |
| `emotion_spike` | drive/emotion delta > 0.5 in single tick | 10 | N/A | 0.8 | (varies: "A wave of frustration just hit me") |
| `context_half` | context_usage > 0.5 (was < 0.5) | 60 | 0.1 | 0.2 | "I've been thinking for a while" |
| `context_pressure` | context_usage > 0.8 | 30 | 0.05 | 0.6 | "I'm running out of thinking space" |
| `context_critical` | context_usage > 0.95 | 15 | N/A | 0.8 | "I need to finish my thought soon" |

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| `models.CitizenCognitiveState` | `.nodes`, `.links`, `.wm`, `.limbic`, `.tick_count` | Full internal state (read-only) |
| `models.LimbicState` | `.drives`, `.emotions`, `.ticks_since_social`, `.arousal` | Drive and emotion intensities |
| `models.WorkingMemory` | `.node_ids`, `.stability_ticks`, `.size` | WM contents and stability |
| `metabolism.CitizenMetabolism` | `.circadian_phase()`, `.active_tonics` | Circadian state and active frequencies |
| `tick_runner.Stimulus` | constructor | Creates Stimulus objects for Law 1 injection |

---

## MARKERS

<!-- @mind:todo Implement InteroceptionSnapshot as a frozen dataclass with efficient update methods -->

<!-- @mind:todo Tune the channel configuration table against real citizen runs — threshold values are initial estimates based on the existing limbic calibration (Phase H) -->

<!-- @mind:proposition Add a "subjective time" channel that measures WM churn rate: high churn = "time is flying," low churn = "time is crawling." Would require tracking WM change frequency over a rolling window. -->

<!-- @mind:proposition Consider per-citizen threshold overrides stored in the citizen's profile — some citizens might be more or less interoceptively sensitive by design (personality trait). v2+ territory. -->

<!-- @mind:escalation The energy trend detection (linear regression on 10 points) might be overkill for a tick that runs at 5s intervals. A simpler "last 3 values all increasing" check might suffice and be cheaper. Design decision needed on trend sensitivity vs compute cost. -->
