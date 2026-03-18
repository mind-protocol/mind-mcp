# Interoception — Validation: What Must Be True

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Interoception.md
PATTERNS:        ./PATTERNS_Interoception.md
BEHAVIORS:       ./BEHAVIORS_Interoception.md
THIS:            VALIDATION_Interoception.md (you are here)
ALGORITHM:       ./ALGORITHM_Interoception.md
IMPLEMENTATION:  ./IMPLEMENTATION_Interoception.md
HEALTH:          ./HEALTH_Interoception.md
SYNC:            ./SYNC_Interoception.md
```

---

## PURPOSE

**Validation = what we care about being true.**

These are the properties that, if violated, would mean interoception has failed its purpose: transforming internal state into felt sensation without disrupting the existing physics.

---

## INVARIANTS

### V1: State Is Never Mutated

**Why we care:** Interoception is a READ-ONLY observer of internal state. If it writes to drives, emotions, or WM, it creates uncontrolled feedback loops and violates the limbic system's sole authority over drive dynamics. The entire architecture depends on interoception being a pure function from state to stimuli.

```
MUST:   interoception_tick() never modifies CitizenCognitiveState, LimbicState, WorkingMemory, or CitizenMetabolism
NEVER:  Any write to state.limbic.drives[*].intensity, state.limbic.emotions[*], state.wm.node_ids, or any node.energy/weight from within interoception code
```

### V2: Refractory Period Is Respected

**Why we care:** Without refractory gating, interoception floods WM with the same sensation every tick. "I feel frustrated" every 5 seconds is not interoception — it's spam. Refractory periods model biological adaptation and keep WM bandwidth available for actual cognition.

```
MUST:   A channel that fires at tick T cannot fire again before tick T + refractory_ticks
MUST:   Re-arming requires both refractory expiry AND hysteresis condition (value dropped below threshold - hysteresis_band)
NEVER:  Two stimuli from the same channel within the refractory window
```

### V3: Stimuli Per Tick Are Bounded

**Why we care:** Even with refractory gating, a crisis state (everything going wrong at once) could produce many stimuli in one tick. This would overwhelm Law 1 injection and distort WM competition. A hard cap ensures interoception remains a whisper, not a shout.

```
MUST:   At most MAX_STIMULI_PER_TICK (default 3) stimuli generated per tick
NEVER:  More than MAX_STIMULI_PER_TICK stimuli returned by interoception_tick()
```

### V4: Stimuli Use Standard Injection Pathway

**Why we care:** Interoceptive stimuli must enter the citizen's cognition the same way external stimuli do — via Law 1 energy injection and Law 4 competition. If interoception bypasses these laws, it breaks the fundamental physics: something can enter WM without competing for attention, which is a privilege no information source should have.

```
MUST:   All interoceptive stimuli are Stimulus objects with source="interoception"
MUST:   All stimuli are injected via the same Law 1 pathway as external stimuli
NEVER:  Direct insertion into state.wm.node_ids from interoception code
NEVER:  Stimulus objects with reserved WM slots or bypassed competition
```

### V5: Content Is Natural Language

**Why we care:** The citizen thinks in words. Numeric telemetry ("frustration=0.82") breaks immersion and produces meaningless content in LLM prompts. Natural language ensures interoceptive content is semantically useful when it enters WM and influences the citizen's reasoning.

```
MUST:   All stimulus.content is a natural-language first-person sentence
NEVER:  Raw numeric values, variable names, or technical identifiers in stimulus.content
```

### V6: Tick Execution Time Is Bounded

**Why we care:** Interoception runs inside the tick loop. If it takes too long, it violates the invariant that the tick completes in under 1 second. The channel checks are simple arithmetic — there is no reason for interoception to be a bottleneck.

```
MUST:   interoception_tick() completes in under 1ms for graphs up to 1000 nodes
NEVER:  Graph traversal, embedding computation, or LLM calls inside interoception
```

### V7: Silence Is Default

**Why we care:** A citizen at steady state (moderate drives, stable WM, normal energy) should produce zero interoceptive stimuli. If interoception generates output on every tick, it wastes WM bandwidth and makes the citizen perpetually self-absorbed. The absence of interoceptive output IS information: everything is nominal.

```
MUST:   A citizen with all drives < 0.5, WM size 3-5, stable energy produces zero stimuli
NEVER:  Interoceptive stimuli on a tick where no threshold is crossed
```

### V8: No Metabolism Dependency for Core Operation

**Why we care:** Not all citizens have a metabolism configured. Interoception must work without it — the metabolic awareness channels simply don't fire, while all other channels (energy, cognitive load, drives, social) operate normally.

```
MUST:   interoception_tick() runs without error when metabolism is None
MUST:   Energy, time, cognitive load, drive, social, and brain health channels work without metabolism
NEVER:  Crash, exception, or degraded core operation when CitizenMetabolism is absent
```

### V9: Zone Mapping Completeness

**Why we care:** The zone map must cover ALL 7 NodeType values and assign each to exactly one zone (stem, limbic, cortex). An unmapped node_type means zone energy aggregation is wrong, producing inaccurate metacognitive stimuli.

```
MUST:   ZONE_MAP covers all 7 NodeType enum values: memory, concept, narrative, value, process, desire, state
MUST:   Each NodeType maps to exactly one zone from {"stem", "limbic", "cortex"}
NEVER:  A NodeType missing from ZONE_MAP (would silently drop energy from zone calculation)
```

### V10: Emotional Delta Accuracy

**Why we care:** Emotional self-perception fires on TRANSITIONS (deltas between ticks), not absolute values. If the system fires on stable high values instead of crossings, the citizen gets repetitive "I feel frustrated" stimuli identical to the refractory-violation failure mode. The delta detection must distinguish onset (low->high) from persistence (high->high).

```
MUST:   Emotional self-perception fires at most once per threshold crossing event
MUST:   Stable emotion at 0.7 for 50 ticks produces exactly 1 emotional self-perception stimulus (at the crossing tick)
NEVER:  Multiple emotional self-perception stimuli for the same emotion crossing the same threshold in the same direction
```

### V11: Context Window Graceful Degradation

**Why we care:** Context window metadata is not always available (headless mode, non-Claude backends, test environments). The context window channel must produce nothing when data is unavailable — never crash, never hallucinate a usage value, never produce a stimulus based on no data.

```
MUST:   context_usage is None when session metadata is unavailable
MUST:   Zero stimuli from context window channel when context_usage is None
NEVER:  Exception, crash, or fallback stimulus when context data is missing
```

### V12: Zone Minimum Node Count

**Why we care:** With fewer than 10 nodes, zone energy aggregation is meaningless — a single high-energy concept node would make "cortex dominant" even though the citizen barely has a brain. Zone awareness must stay silent until there are enough nodes for meaningful topology.

```
MUST:   Zone awareness channels produce no stimuli when total_node_count < 10
NEVER:  Zone awareness stimulus with < 10 nodes in graph
```

---

## PRIORITY

| Priority | Meaning | If Violated |
|----------|---------|-------------|
| **CRITICAL** | System purpose fails | Unusable |
| **HIGH** | Major value lost | Degraded severely |
| **MEDIUM** | Partial value lost | Works but worse |

---

## INVARIANT INDEX

| ID | Value Protected | Priority |
|----|-----------------|----------|
| V1 | State read-only integrity | CRITICAL |
| V2 | Refractory prevents flooding | CRITICAL |
| V3 | Bounded stimuli per tick | HIGH |
| V4 | Standard injection pathway | CRITICAL |
| V5 | Natural language content | HIGH |
| V6 | Tick execution time | HIGH |
| V7 | Silence at steady state | MEDIUM |
| V8 | Core works without metabolism | HIGH |
| V9 | Zone mapping covers all NodeTypes | HIGH |
| V10 | Emotional delta fires on transitions only | CRITICAL |
| V11 | Context window graceful degradation | HIGH |
| V12 | Zone minimum node count enforced | MEDIUM |

---

## MARKERS

<!-- @mind:todo Write unit tests for V1 (state mutation detection) — mock state, run interoception, assert state unchanged -->
<!-- @mind:todo Write unit tests for V2 (refractory gating) — fire a channel, advance ticks, verify no re-fire within window -->
<!-- @mind:todo Write unit tests for V3 (bounded output) — create crisis state with all thresholds crossed, verify cap -->
<!-- @mind:todo Write unit tests for V7 (silence at steady state) — create nominal state, verify empty output -->
<!-- @mind:todo Write unit tests for V8 (metabolism=None) — verify no crash, verify metabolic channels silenced -->
