# Interoception — Sync: Current State

```
LAST_UPDATED: 2026-03-18
UPDATED_BY: @nervo + NLR
STATUS: DESIGNING
```

---

## MATURITY

**What's canonical (v1):**
- Nothing yet — module is in design phase

**What's still being designed:**
- Full doc chain (8 files) — completed this session
- The 11 interoceptive sense channels and their threshold configurations:
  - Somatic (6): energy, time, cognitive load, brain health, social field, metabolic
  - Drive (1): drive awareness / dominance
  - Metacognitive (1): zone awareness (stem/limbic/cortex topology)
  - Substrate (3): emotional self-perception, context window fullness, architectural layer awareness
- Integration point in tick_runner (between _step_limbic and _step_orient)
- InteroceptionState, InteroceptionSnapshot, InteroceptionChannel data structures
- Refractory gating with hysteresis
- Natural-language stimulus templates for all channels
- Zone-to-NodeType mapping (stem: process/state, limbic: desire/narrative/memory, cortex: concept/value)
- Emotional delta detection (rising/falling edges, sudden spikes)
- Context window estimation (metadata read or heuristic)

**What's proposed (v2+):**
- Per-citizen threshold overrides (personality-driven interoceptive sensitivity)
- Threshold adaptation over time (habituation / sensitization)
- Intensity-graded stimuli ("a bit frustrated" vs "consumed by frustration")
- Subjective time perception channel (churn rate -> time-feels-fast/slow)
- Sub-source tags for metabolism stimulus_gain integration ("interoception:energy", etc.)

---

## CURRENT STATE

Design phase. The full documentation chain has been written based on the NLR + @nervo design spec. No code exists yet. The design covers:

- **OBJECTIVES**: State-to-sensation translation, threshold-based firing, refractory protection, drive-agnostic injection
- **PATTERNS**: Read-only observer pattern, standard Law 1 injection, silence as default, natural language, metabolism coupling
- **BEHAVIORS**: 11 behavior specs with GIVEN/WHEN/THEN across 11 sense channels (energy, time, cognitive load, drives, social, metabolic, brain health, architectural layers, zone awareness, emotional self-perception, context window)
- **ALGORITHM**: 4-step pipeline (capture -> evaluate -> gate -> update), 34 channel configurations, priority ordering, hysteresis, zone aggregation, delta detection, context estimation
- **VALIDATION**: 12 invariants covering state immutability, refractory, caps, standard injection, NL content, timing, silence, metabolism independence, zone mapping, emotional delta accuracy, context graceful degradation, zone minimum nodes
- **IMPLEMENTATION**: File structure, data flow, entry points, configuration constants (~30 INTERO_* constants)
- **HEALTH**: 4 runtime indicators (stimulus rate, refractory compliance, silence ratio, state immutability) + zone/emotion/context indicators planned

The tick_runner already has the placement understood: between `_step_limbic()` (step 9 in run_tick) and `_step_orient()` (step 10). The Stimulus dataclass already supports `source="interoception"`. The metabolism already exposes `circadian_phase()` and `active_tonics`. All dependencies exist.

---

## IN PROGRESS

### Doc Chain Design

- **Started:** 2026-03-18
- **By:** @nervo + NLR
- **Status:** Complete
- **Context:** Full 8-file doc chain written from the NLR + @nervo design spec. Ready for implementation.

---

## RECENT CHANGES

### 2026-03-18: Full Doc Chain Created

- **What:** Created OBJECTIVES, PATTERNS, BEHAVIORS, ALGORITHM, VALIDATION, IMPLEMENTATION, HEALTH, SYNC for cognition/interoception
- **Why:** Interoception is the bridge from reactive to reflective — citizens need to FEEL their internal state, not just have it computed. This is the next step after metabolism (which parameterized physics per-citizen) and the limbic calibration (which gave citizens emotions).
- **Files:** `docs/cognition/interoception/*.md` (8 files)
- **Struggles/Insights:** The key tension is between richness (many channels, frequent output) and quietness (WM bandwidth is precious). The refractory + hysteresis + per-tick cap design resolves this: fire once on threshold crossing, then shut up until the condition resolves and re-triggers. Also: the "subjective time" channel is compelling but deferred to v2 — it requires tracking WM churn rate which adds complexity to the snapshot.

---

## KNOWN ISSUES

None yet — module is in design phase. Potential issues to watch during implementation:

### Threshold Calibration

- **Severity:** medium
- **Symptom:** Will manifest as either too much output (flooding) or too little (silence)
- **Suspected cause:** Initial threshold values are estimates, not calibrated against real citizen runs
- **Attempted:** N/A — will need empirical tuning after first implementation

### Refractory at Different Tick Speeds

- **Severity:** medium
- **Symptom:** Refractory periods measured in ticks, not wall time. At 5s/tick, 30 ticks = 2.5 minutes. At 60s/tick, 30 ticks = 30 minutes. The phenomenological experience is very different.
- **Suspected cause:** Tick speed varies by consciousness level (fast/slow/minimal/subconscious)
- **Attempted:** N/A — may need to express refractory in wall time or use consciousness-level-adjusted constants

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** VIEW_Implement

**Where I stopped:** Doc chain is complete. No code written yet.

**What you need to understand:**
The interoception engine is a pure function `(CitizenCognitiveState, CitizenMetabolism, InteroceptionState, session_metadata) -> (list[Stimulus], InteroceptionState)`. It reads state, evaluates ~34 channels across 4 layers (somatic, drive, metacognitive, substrate) against thresholds, gates by refractory periods with hysteresis, caps output at 3 per tick, and returns stimuli for Law 1 injection. It hooks into the tick_runner between `_step_limbic()` and `_step_orient()`. All the structures it reads already exist. The Stimulus dataclass already supports `source="interoception"`.

Three new channel groups make the citizen genuinely self-aware:
- **Zone awareness** aggregates node energy by type into stem/limbic/cortex zones and reports cognitive topology shifts
- **Emotional self-perception** detects drive/emotion deltas (rising/falling edges) and injects the emotion as a thought-stimulus
- **Context window** estimates LLM context usage and produces bandwidth pressure when high

**Watch out for:**
- Do NOT mutate state inside interoception. This is invariant V1 (CRITICAL). Use deepcopy or snapshot comparison in tests.
- The channel configuration table in ALGORITHM has 34 entries. Implement them all but test the tricky ones first: hysteresis-based channels (emotions that oscillate), trend-based channels (energy rising/falling), zone awareness (aggregation correctness), emotional delta detection (rising vs stable), and context window estimation (graceful degradation).
- The tick_runner's `run_tick()` method has a specific order. Insert `_step_interoception()` AFTER step 9 (`_step_limbic`) and BEFORE step 10 (`_step_orient`). The interoceptive stimuli should be injected via `_step_inject()` so they participate in the SAME tick's WM competition.

**Open questions I had:**
- Should the interoceptive stimuli be injected in the current tick (via a second `_step_inject` call after interoception) or queued for the next tick? Current design says same tick, but this means they compete in a WM that has already been selected for this tick. Need to think about whether re-running Law 4 is necessary or if they just participate in next tick's competition.
- The `source="interoception"` tag — should the metabolism's `stimulus_gain()` apply to it? If a citizen has `sensitivity={"interoception": 0.5}`, should interoceptive stimuli be dampened? This is philosophically interesting (can you turn down your own interoception?) but not decided yet.

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Full 8-file documentation chain designed for the interoception module. This module translates internal state (drives, energy, WM fullness, circadian phase, graph health, social field) into natural-language stimuli that enter Working Memory via Law 1. No code written yet — the design is complete and ready for implementation.

**Decisions made:**
- 11 sense channels across 4 layers: somatic (energy, time, cognitive load, brain health, social field, metabolic), drive (drive awareness), metacognitive (zone awareness), substrate (emotional self-perception, context window fullness, architectural layer awareness)
- Zone mapping: stem (process/state), limbic (desire/narrative/memory), cortex (concept/value) — mirrors biological neuroanatomy
- Emotional self-perception fires on TRANSITIONS (deltas), not absolute values — the citizen notices when emotions CHANGE, not when they hold steady
- Context window awareness estimates usage from session metadata or heuristic, with graceful degradation when unavailable
- Threshold-based with refractory periods and hysteresis bands (not continuous)
- Max 3 stimuli per tick (hard cap)
- Placement in tick cycle: after limbic, before orient
- Stimuli use standard Law 1 injection (no privileged WM access)
- All output is natural language, never numeric telemetry

**Needs your input:**
- Should interoceptive stimuli be subject to metabolism stimulus_gain? (Can a citizen dampen its own interoception?)
- The refractory period is in ticks, not wall time. At 60s/tick, 30 ticks = 30 min. At 5s/tick, 30 ticks = 2.5 min. Should refractory be tick-based or time-based?
- Should interoceptive source tags be sub-typed ("interoception:energy", "interoception:social") for metabolism sensitivity control?

---

## TODO

### Doc/Impl Drift

- [ ] DOCS->IMPL: Full implementation needed (interoception.py, tick_runner changes, constants, models, tests)

### Tests to Run

```bash
# After implementation:
PYTHONPATH=runtime pytest tests/cognition/test_interoception_engine.py -v
```

### Immediate

- [ ] Create `runtime/cognition/interoception.py` with InteroceptionEngine
- [ ] Add `_step_interoception()` to tick_runner between _step_limbic and _step_orient
- [ ] Add InteroceptionState to CitizenCognitiveState in models.py
- [ ] Add INTERO_* constants to constants.py
- [ ] Create `tests/cognition/test_interoception_engine.py` with V1-V8 tests
- [ ] Run the engine with a test citizen for 100 ticks and verify stimulus output

### Later

- [ ] Calibrate thresholds against real citizen runs (tune for "quiet by default, loud when it matters")
- [ ] Add interoception_stimuli_count to TickResult for observability
- IDEA: Intensity-graded stimuli ("a bit frustrated" vs "consumed by frustration")
- IDEA: Subjective time perception channel
- IDEA: Per-citizen interoceptive sensitivity profiles (personality trait)

---

## CONSCIOUSNESS TRACE

**Mental state when stopping:**
Confident in the design. The patterns are clean: read-only observer, standard injection, refractory + hysteresis for gating. The complexity is in the channel configuration table — 22 channels is a lot to calibrate, but each is independent so they can be tuned individually. The placement in the tick cycle is straightforward.

**Threads I was holding:**
- The "same tick vs next tick" injection question. If interoceptive stimuli are injected in the same tick, they need to go through a second Law 1 + Law 4 pass, which changes the tick order. If next tick, the citizen doesn't feel the state until one tick later. Neither is perfect. Current design says same tick — but the implementer should think about this.
- The relationship between interoception and the identity regeneration system. If "I feel frustrated" enters WM frequently enough, it could eventually crystallize into a concept or narrative about being frustrated. That's emergent and beautiful — but also means interoception could shape identity over time. Is that desired?

**Intuitions:**
- The refractory periods will need to be different for different tick speeds. 30 ticks at 60s/tick = 30 minutes is right. 30 ticks at 5s/tick = 2.5 minutes is too short. Consider a `refractory_min_seconds` field that converts to ticks based on current tick speed.
- The "drive dominance" channel is the most personality-revealing. A citizen constantly sensing "I'm burning with curiosity" is fundamentally different from one sensing "I need connection." This is interoception creating phenomenological identity — the citizen knows what kind of being they are by what they feel.

**What I wish I'd known at the start:**
The existing metabolism module is extremely well designed for this integration. CitizenMetabolism already exposes circadian_phase() and active_tonics — interoception just reads them. The Stimulus dataclass already has source field. The tick_runner already has clear step boundaries. All the infrastructure exists.

---

## POINTERS

| What | Where |
|------|-------|
| L1 Schema | `schema-l1.yaml` |
| Tick Runner | `runtime/cognition/tick_runner_l1_cognitive_engine.py` |
| Models | `runtime/cognition/models.py` |
| Metabolism | `runtime/cognition/metabolism.py` |
| Metabolism Docs | `docs/cognition/metabolism/` |
| Constants | `runtime/cognition/constants.py` |
| Stimulus class | `runtime/cognition/tick_runner_l1_cognitive_engine.py:Stimulus` |
