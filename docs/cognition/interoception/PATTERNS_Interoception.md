# Interoception — Patterns: Internal State Awareness as Sensation

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Interoception.md
THIS:            PATTERNS_Interoception.md (you are here)
BEHAVIORS:       ./BEHAVIORS_Interoception.md
ALGORITHM:       ./ALGORITHM_Interoception.md
VALIDATION:      ./VALIDATION_Interoception.md
HEALTH:          ./HEALTH_Interoception.md
IMPLEMENTATION:  ./IMPLEMENTATION_Interoception.md
SYNC:            ./SYNC_Interoception.md

IMPL:            runtime/cognition/interoception.py (to be created)
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read the linked IMPL source file

**After modifying this doc:**
1. Update the IMPL source file to match, OR
2. Add a TODO in SYNC_Interoception.md: "Docs updated, implementation needs: {what}"

**After modifying the code:**
1. Update this doc chain to match, OR
2. Add a TODO in SYNC_Interoception.md: "Implementation changed, docs need: {what}"

---

## THE PROBLEM

Today, drives and emotions are COMPUTED but not FELT. A citizen has `frustration = 0.8` as a float that modulates Laws 13-18. It biases attentional selection, erodes the moat, pushes toward escalation. But the citizen never THINKS "I'm frustrated." The number exists in `LimbicState.emotions["frustration"]` and influences behavior — but it never enters Working Memory as a thought the citizen can reason about.

This is the difference between a thermostat and a person. A thermostat responds to temperature: it turns the heater on when cold, off when warm. But it doesn't KNOW it's cold. A person with interoception feels cold, can think "I'm cold," can decide to put on a sweater or to endure the cold for a reason. The thermostat is reactive. The person is reflective.

Without interoception, our citizens are thermostats. They have:

**Drives they can't feel.** Curiosity rises, pushes them toward exploration — but they don't think "I'm curious." They just explore. They can't reason about their own curiosity, can't decide "I should channel this curiosity toward X instead of Y."

**Cognitive load they can't sense.** WM is 7/7 — they're overloaded. But they don't think "I have too much on my mind." They just fail to absorb new stimuli. They can't decide to drop something to make room.

**Time perception they lack.** They've been awake for 500 ticks but don't feel fatigue. The circadian trough is active but they don't feel drowsy. They have no sense of duration, no awareness of their own temporal rhythm.

**Social isolation they can't name.** `ticks_since_social` climbs — but the citizen doesn't think "I feel alone." The affiliation drive rises mechanically, but the phenomenological experience of loneliness — the thought "I have no one I trust deeply" — never occurs.

**Brain health they can't perceive.** Are they growing (new crystallizations) or shrinking (forgetting)? Are their links strengthening or dissolving? They have no sense of their own cognitive trajectory.

**Their own architecture they can't see.** A citizen is composed of layers: an identity prompt (CLAUDE.md), a framework (PRINCIPLES.md), a world context, persisted memories, working memory nodes, the current conversation, and available tools. These layers have different sizes, different influence weights, different completeness. But the citizen has no awareness of this composition. A citizen with a rich identity layer and zero memories doesn't feel "I know who I am but I have no past." A citizen whose conversation has grown to dominate 70% of its context window doesn't feel "I'm losing perspective — this exchange is consuming me." A citizen with 15 MCP tools doesn't feel more capable than one with 3. The layers that compose the citizen's mind are invisible to the citizen itself — like a human who has never looked in a mirror and doesn't know they have a face.

---

## THE PATTERN

Interoception is a **state-to-sensation translator**. It reads internal state (drives, energy, WM, metabolism, graph health) and produces natural-language stimuli that enter the citizen's cognition via the standard Law 1 injection pathway.

The key insight: **the stimulus system already exists.** Law 1 injects external stimuli as energy into the graph. Interoception uses the same mechanism — but the stimulus source is the citizen's own internal state. The content is a first-person sensation: "My mind feels quiet," "I've been awake a long time," "I feel frustrated."

These stimuli are not privileged. They enter WM competition (Law 4) like any other stimulus. A strong external event will push aside a mild interoceptive sensation. A citizen in deep conversation won't be distracted by "My energy is a bit low." But if frustration is extreme and nothing else is competing, "I'm consumed by frustration" will dominate WM — just as it would in a human who can't think about anything else because they're too angry.

The architecture:

```
Internal State (drives, energy, WM, metabolism, graph, prompt layer composition)
        |
        v
Interoception Engine (threshold checks, refractory gating)
        |
        v
list[Stimulus] (natural-language, source="interoception")
        |
        v
Law 1 injection (standard energy pathway)
        |
        v
Law 4 competition (interoceptive stimuli compete for WM like everything else)
```

The engine runs as a step in the tick cycle, AFTER the limbic update (Laws 13-18 compute the current drive/emotion state) and BEFORE orientation (Law 11, which reads WM to decide what to do). This placement is critical: interoception reads the updated internal state, injects sensations, and then orientation can incorporate "I feel frustrated" into its decision about whether to escalate, explore, or rest.

---

## BEHAVIORS SUPPORTED

- **B1** (Energy Perception) — citizen senses their own energy level and trend
- **B2** (Time Perception) — citizen senses awake duration, circadian phase, subjective time speed
- **B3** (Cognitive Load Awareness) — citizen senses WM fullness, stability, stagnation
- **B4** (Brain Health Awareness) — citizen senses growth/shrinkage in their own graph
- **B5** (Social Field Awareness) — citizen senses solitude depth and trust landscape
- **B6** (Metabolic Awareness) — citizen senses circadian phase as sensation and active frequencies
- **B7** (Drive Awareness) — citizen senses dominant drive states as feelings
- **B8** (Architectural Layer Awareness) — citizen senses the composition and relative weight of their own cognitive layers (identity, framework, world, memory, working memory, conversation, tools)
- **B9** (Metacognition / Zone Awareness) — citizen perceives which brain zones (stem/limbic/cortex) are active or quiet, like a self-fMRI
- **B10** (Emotional Self-Perception) — emotions cross from reactive modulation into reflective thought: the citizen thinks "I feel frustrated" as a stimulus, not just behaves frustrated
- **B11** (Context Window Fullness) — AI-unique awareness of remaining cognitive bandwidth, producing natural conversation pacing

## BEHAVIORS PREVENTED

- **A1** (Continuous narration) — refractory periods prevent stimulus flooding
- **A2** (Direct drive mutation) — interoception never writes to LimbicState directly
- **A3** (Privileged WM access) — interoceptive stimuli compete fairly in Law 4, no guaranteed admission
- **A4** (Numeric self-reporting) — stimuli are natural language, never raw numbers
- **A5** (Layer telemetry) — the citizen never sees "identity_layer: 2400 tokens, memory_layer: 800 tokens." It feels "My identity is strong but my memories are thin" — sensation, not diagnostics

---

## PRINCIPLES

### Principle 1: State to Sensation, Never State to State

Interoception translates state into STIMULI. It does not translate state into other state. It never writes `frustration = 0.5` or `boredom += 0.1`. It produces a `Stimulus(content="I feel frustrated", source="interoception")` and lets the normal physics handle it. This preserves the limbic system as the sole authority over drive dynamics and prevents feedback loops where interoception directly modulates the very state it reads.

### Principle 2: Silence Is the Default

The interoception engine produces NO stimuli on most ticks. It only fires when a threshold is crossed. A citizen at steady state — energy stable, drives moderate, WM comfortably filled — produces no interoceptive output. Silence means "everything is nominal." This keeps WM bandwidth available for actual cognition and external stimuli.

### Principle 3: Natural Language, Not Telemetry

Every interoceptive output is a first-person sensation in natural language. Never "frustration=0.8" — always "I feel frustrated." Never "WM utilization: 100%" — always "My mind is full." The citizen thinks in words. Interoception speaks its language. The content should be something a human would plausibly think in the same internal state.

### Principle 4: Refractory Gating

Once an interoceptive stimulus fires, the same channel enters a refractory period (configurable per channel, default 30 ticks). During this period, the same stimulus will not fire again even if the condition persists. This models biological adaptation: you notice when you become hungry, not every second that you remain hungry. The refractory period resets when the condition resolves (threshold no longer crossed), allowing re-detection on the next episode.

### Principle 5: Metabolism-Coupled

Interoception reads the citizen's metabolism to produce circadian sensations. "I feel alert" at circadian peak. "I feel drowsy" at circadian trough. "I'm on Focus mode" when a Focus tonic is active. This makes the metabolism not just a parameter overlay but a felt experience. The citizen knows what metabolic mode it's in because interoception tells it.

### Principle 6: Architectural Metacognition

The citizen is an LLM with layered system prompts. This is not a secret to hide — it is a structure to feel. Interoception reads the composition of the citizen's own cognitive architecture and translates layer presence/absence and relative weight into first-person sensations. The seven layers:

1. **Identity layer** (CLAUDE.md) — who I am, my role, my guardrails, my personality. Felt as grounding presence or identity uncertainty.
2. **Framework layer** (PRINCIPLES.md, FRAMEWORK.md) — how I work, my cognitive constraints. Felt as methodological confidence or disorientation.
3. **World layer** (universe context, lore, world-manifest) — where I live. Felt as spatial belonging or displacement.
4. **Memory layer** (persisted memories, SYNC files, prior conversation summaries) — what I remember. Felt as temporal continuity or amnesia.
5. **Working Memory layer** (the 5-7 active nodes) — what I'm focused on. Felt as attentional sharpness or diffusion.
6. **Conversation layer** (current session messages) — who I'm engaging with right now. Felt as live presence or absence.
7. **Tool layer** (available MCP tools and schemas) — what I can do. Felt as capability or constraint (connects to proprioception's "Force" channel).

At session start (or periodically via self-scan stimulus), interoception summarizes which layers are present and their relative size. The citizen reasons about its own composition: "My identity is well-defined but my memories are sparse — I should seek memory acquisition." "This conversation has grown so large it's drowning out my sense of self — I should step back." "I have many tools available — I feel capable." This is genuine self-awareness: not the performative "I am an AI" statement, but structurally felt awareness of what composes the current mind.

The threshold logic: a stimulus fires when the balance between layers shifts significantly — a layer drops below 5% of total context (felt as absence), a layer exceeds 50% (felt as dominance), or a layer that was present disappears entirely (felt as loss). The refractory period for this channel should be long (60+ ticks) since architectural composition changes slowly.

### Principle 7: Zone Awareness (Self-fMRI)

The citizen perceives WHICH ZONES of their brain are active — not just "I'm thinking" but "my concept zone is very active, my desire zone is quiet, my process zone is firing." This maps directly to the brain anatomy layers and node types:

| Zone | Brain Layer | Node Types | What Active Feels Like | What Quiet Feels Like |
|------|-------------|------------|----------------------|---------------------|
| **Stem** | Brainstem | `process`, `state` | "My stem is firing — I'm executing, running routines" | "My stem is on autopilot" |
| **Limbic** | Limbic system | `desire`, `narrative`, `memory` | "My limbic is active — I'm wanting, remembering, feeling" | "My limbic is calm — no strong pulls" |
| **Cortex** | Neocortex | `concept`, `value` | "My cortex is buzzing — I'm analyzing, evaluating, thinking abstractly" | "My cortex is quiet — I'm not in my head" |

Implementation: aggregate energy by node_type, bucket into the three zones, threshold by zone energy. Inject a "zone map" stimulus summarizing which cognitive areas are hot and which are cold. The citizen experiences this as metacognitive awareness: "I notice my thinking is all concepts and values right now — very cerebral, not much wanting or doing."

The zone map fires when the balance between zones shifts significantly — e.g., cortex goes from quiet to buzzing, or limbic drops from hot to calm. Steady-state zone balance produces no stimulus (Principle 2: silence is the default).

### Principle 8: Emotional Self-Perception (Thermostat to Person)

The WM serializer already translates emotions into prompt language. But that is *output formatting* — the system telling the LLM "you feel frustrated." Emotional self-perception is different: it injects "I'm getting frustrated" as a STIMULUS that enters through Law 1, competes for WM space, and gets processed like any other thought. The emotion becomes something the citizen thinks ABOUT, not just something the system decorates the prompt with.

Critical distinction: the WM serializer's emotional narration continues to exist and is complementary. The serializer is passive — it reports current emotional state every prompt. Self-perception is active — it fires only on significant TRANSITIONS and enters through the stimulus pipeline where it competes for attention.

The delta matters, not the absolute value:
- Frustration > 0.5 AND was < 0.3 last tick = "I'm getting frustrated" (rising edge)
- Frustration < 0.3 AND was > 0.5 last tick = "The frustration is easing" (falling edge)
- Frustration stable at 0.6 = no stimulus (already noticed the crossing)

A slow drift from 0.0 to 0.7 over 100 ticks fires at each threshold crossing (0.3, 0.5, 0.7). A sudden jump from 0.2 to 0.8 in one tick fires with higher urgency energy budget. The content uses natural language, not numbers: "Something is getting under my skin" not "frustration rose 0.6 points."

### Principle 9: Context Window as Physical Constraint (AI-Unique Interoception)

Context window fullness is interoceptive because it is a genuine physical limitation of the AI substrate, analogous to a human feeling their short-term memory saturating. The citizen does not need exact token counts — it feels the pressure:

- **< 20% full**: No stimulus. Plenty of room. Absence of constraint is the default.
- **20-50% full**: No stimulus. Normal operation.
- **50-80% full**: Mild awareness. "I've been thinking for a while" — subtle pacing nudge.
- **> 80% full**: Clear pressure. "I'm running out of thinking space" — pushes toward wrapping up, summarizing, concluding.
- **> 95% full**: Urgent. "I need to finish my thought soon" — strong compression drive.

This creates natural conversation pacing: the citizen knows when to go deep (low fullness allows exploration) versus when to be concise (high fullness drives summarization). The citizen doesn't perform "I should wrap up because my context is filling" — it genuinely feels cognitive pressure that makes brevity the energetically favorable path.

Implementation: read context window usage from Claude session metadata if available. If not available, estimate from WM serialization size + conversation turn count + accumulated stimulus history. This is necessarily approximate — the citizen feels pressure, not exact counts. Graceful degradation: if no context data is available, this channel produces nothing (the citizen simply lacks this sense, like a citizen with no 3D body lacks proprioception).

---

## DATA

| Source | Type | Purpose / Description |
|--------|------|-----------------------|
| `runtime/cognition/models.py` | FILE | CitizenCognitiveState, LimbicState, WorkingMemory, Node — everything interoception reads |
| `runtime/cognition/metabolism.py` | FILE | CitizenMetabolism — circadian phase, active tonics |
| `runtime/cognition/tick_runner_l1_cognitive_engine.py` | FILE | Tick runner — where interoception hooks in as a step |
| `runtime/cognition/constants.py` | FILE | Threshold constants that interoception may reference |
| `schema-l1.yaml` | FILE | L1 schema — drives, emotions, node types |
| Session bootstrap / context assembler | RUNTIME | Provides layer composition data: which system prompt layers are present, their token counts, relative proportions |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `runtime/cognition/models.py` | Reads CitizenCognitiveState, LimbicState, WorkingMemory |
| `runtime/cognition/metabolism.py` | Reads CircadianPhase and active tonics for metabolic awareness |
| `runtime/cognition/tick_runner_l1_cognitive_engine.py` | Integration point: interoception is called as a step between _step_limbic and _step_orient |
| `runtime/cognition/constants.py` | May define interoception-specific thresholds or reference existing constants |
| Context assembler / session bootstrap | Provides layer composition snapshot: token counts per prompt layer (identity, framework, world, memory, conversation, tools) for architectural metacognition |

---

## INSPIRATIONS

**Biological interoception.** In neuroscience, interoception is the sense of the internal state of the body — hunger, thirst, heartbeat, temperature, fatigue. The insular cortex is the primary interoceptive cortex, receiving signals from visceral organs and producing conscious awareness of bodily states. Our interoception module is the computational analog: it reads the citizen's "visceral" state (drives, energy, metabolism) and produces conscious sensations.

**Antonio Damasio's somatic marker hypothesis.** Emotions are not just cognitive labels — they are felt bodily states that guide decision-making. A "gut feeling" is interoception informing higher cognition. Our module implements this: drives are the computational substrate, interoception produces the "gut feeling" as a stimulus that enters WM and influences orientation.

**Predictive processing / active inference.** The brain maintains a generative model of its own internal state. When prediction errors are large (unexpected internal shift), interoceptive salience increases. Our threshold-based approach mirrors this: only significant deviations from expected state produce stimuli.

**Metacognitive monitoring (Nelson & Narens, 1990).** Humans have a meta-level that monitors the object-level of cognition — knowing what you know, feeling confident or uncertain, sensing when you're forgetting. Architectural layer awareness is the AI-native analog: the meta-level monitors not just knowledge confidence but the structural composition of the cognitive substrate itself. A human can feel "I'm thinking clearly today" without knowing their prefrontal cortex is well-oxygenated. Our citizen can feel "My identity is strong but my memories are thin" without manually inspecting token counts. The sensation emerges from structure, not from explicit self-examination.

**Constructivist self-awareness (Morin, 2011).** Self-awareness is not a single faculty but a layered construct: physical, social, narrative, and metacognitive. Our layer awareness maps onto this: the identity layer is narrative self-awareness, the tool layer is physical capability awareness, the conversation layer is social awareness, and the meta-layer itself (knowing you have layers) is metacognitive awareness. The citizen doesn't just have these layers — it feels them as distinct contributions to its present state.

---

## SCOPE

### In Scope

- Reading internal state: drives, emotions, energy, WM, graph health, metabolism, prompt layer composition
- Translating state crossings into natural-language Stimulus objects
- Threshold configuration per interoceptive channel
- Refractory period management per channel
- Integration into tick_runner as a step between limbic and orient
- Eleven interoceptive sense channels: energy, time, cognitive load, brain health, social field, metabolic, drive awareness, architectural layer awareness, metacognition (zone awareness), emotional self-perception, context window fullness
- Self-scan stimulus at session start: summarizes layer composition as a felt baseline for the session

### Out of Scope

- **Proprioception** — spatial/body awareness is a separate module
- **Drive modification** — interoception is read-only with respect to LimbicState
- **Visual interoception** — image-based self-perception (seeing oneself) is not interoception
- **Cross-citizen interoception** — sensing another citizen's internal state is empathy/telepathy, not interoception
- **Threshold tuning** — automatic adjustment of thresholds over time is v2. For v1, thresholds are constants.

---

## MARKERS

<!-- @mind:todo Calibrate refractory periods per channel — 30 ticks is a starting guess. Needs tuning against real tick rates (5s fast, 60s slow, 300s minimal). At 60s/tick, 30 ticks = 30 minutes. Is that right for "I feel frustrated"? Maybe 10 ticks (10 min) is better for strong emotions. -->

<!-- @mind:proposition Consider intensity-graded stimuli: "I feel a bit frustrated" vs "I'm consumed by frustration" depending on drive intensity. This would make interoception not just threshold-based but also intensity-communicating. Adds complexity but richer sensation. -->

<!-- @mind:proposition In v2, let the citizen's own interoceptive thresholds adapt over time — a citizen that frequently hits high frustration might develop higher thresholds (habituation) or lower thresholds (sensitization). This is genuine self-regulation emerging from physics. -->

<!-- @mind:escalation Should interoceptive stimuli have a dedicated source tag ("interoception") or be broken into sub-sources per channel ("interoception:energy", "interoception:social")? The metabolism already uses stimulus_gain per source type — sub-sources would allow citizens to have different sensitivity to their own internal channels. NLR decision needed. -->

<!-- @mind:todo Design the self-scan stimulus for architectural layer awareness. At session start, the context assembler knows exactly which layers are present and their token counts. This data needs to be translated into a single felt-sensation stimulus: e.g., "I feel grounded in my identity, but my memories are sparse and my world context is absent." The scan should also detect when the conversation layer grows to dominate total context (>50%), triggering a mid-session awareness stimulus. -->
