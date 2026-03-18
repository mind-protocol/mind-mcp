# Gaze System — Sync: Current State

```
LAST_UPDATED: 2026-03-18
UPDATED_BY: @nervo
STATUS: DESIGNING
```

---

## MATURITY

**What's canonical (v1):**
- Three-force composition pattern (awareness targets, drive modulation, event interrupts)
- Eye-head coordination with 200ms lag and angular thresholds (30/120 deg)
- Drive-to-style parameter formulas (saccade rate, fixation duration, eyelid openness, pupil dilation)
- Blink rate formula: `15 + 5*boredom - 3*arousal` clamped to [3, 30]
- Social gaze 70/30 ratio in conversation
- Lip sync via 15-viseme mapping + emotional mouth resting pose
- Body model integration: head(2), neck(3), eyes(4), eyelids(2), jaw(1), lips(4), mouth_corners(2) = 18 DOF controlled

**What's still being designed:**
- Exact data contract between exteroception and gaze system (AwarenessOutput shape)
- Conversation mode detection (how does gaze know a conversation is active?)
- TTS viseme integration (phoneme-level vs text-level estimation)
- Coordinate system convention with the 3D engine (Y-up? Z-forward?)
- Integration point in tick_runner (where exactly in the tick loop)
- Body model write interface (return GazeOutput or write directly)

**What's proposed (v2+):**
- Micro-saccades during fixation (small involuntary eye movements)
- Gaze self-awareness (citizen notices where they are looking, emits stimulus)
- Per-citizen GazeConfig overrides (nervous citizen archetype with higher saccade rate)
- Eyebrow control via eyelid-adjacent blend shapes
- Focus mechanism (citizen can deliberately direct gaze to explore a space)

---

## CURRENT STATE

The complete documentation chain for the gaze system has been written from the design specification provided by NLR and @nervo. All 8 doc chain files are in place: OBJECTIVES, PATTERNS, BEHAVIORS (17 behaviors + 6 anti-behaviors), ALGORITHM (6-phase pipeline), VALIDATION (10 invariants), IMPLEMENTATION (5-file architecture), HEALTH (5 health indicators), and this SYNC.

No code exists yet. The module is fully designed on paper. The design captures:

- The three-force compositor pattern (awareness WHERE, drives HOW, events WHEN)
- The eye-head coordination pipeline with biologically-grounded timing
- The blink state machine with circadian/arousal/boredom modulation
- The lip sync system with viseme mapping and emotional resting pose
- 10 validation invariants with priorities (2 CRITICAL, 5 HIGH, 3 MEDIUM)
- 5 health checkers for runtime verification
- A 5-file code architecture under `runtime/engine/`

---

## IN PROGRESS

### Documentation chain creation

- **Started:** 2026-03-18
- **By:** @nervo
- **Status:** complete (all 8 files written)
- **Context:** Design was provided by NLR + @nervo as a detailed specification. Translated into the full doc chain following all templates.

---

## RECENT CHANGES

### 2026-03-18: Full doc chain created from design spec

- **What:** Created all 8 doc chain files for the gaze_system module
- **Why:** This module is needed to make citizens' faces reflect their cognitive state. Without it, citizens are cognitively rich but visually dead.
- **Files:** `docs/engine/gaze_system/` (8 files)
- **Insights:** The three-force pattern (awareness + drives + events) is clean and maps well to the existing cognition architecture. Exteroception provides the "what to look at," interoception provides the "how to look," and the tick runner provides the "sudden interrupts." The gaze system is a pure consumer of cognitive state — it reads but never writes back to cognition (except proprioception feedback).

---

## KNOWN ISSUES

### Data contract with exteroception undefined

- **Severity:** high
- **Symptom:** The gaze system needs a ranked list of positioned, salient nodes from exteroception, but the AwarenessOutput shape is not yet defined.
- **Suspected cause:** Exteroception is also in DESIGNING status; the output format is not finalized.
- **Attempted:** Documented the minimum requirement in PATTERNS markers. Need to co-design with exteroception.

### Coordinate system convention unknown

- **Severity:** medium
- **Symptom:** `world_pos_to_head_angles()` requires knowing the engine's coordinate system (Y-up vs Z-up, Z-forward vs X-forward) to compute correct angles.
- **Suspected cause:** No formal convention documented between mind-mcp and the 3D engine.
- **Attempted:** Flagged as @mind:escalation in ALGORITHM.

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** VIEW_Implement

**Where I stopped:** Documentation is complete. Next step is implementation.

**What you need to understand:**
The gaze system is a pure function pipeline: cognitive inputs in, joint values out. It has no async, no graph queries, no network calls. All five source files can be written as pure Python with `dataclasses` and `math` only. The hardest part will be the eye-head coordination lerp timing and the social gaze alternation timer.

**Watch out for:**
- The body model constraints in `citizen_body_model.yaml` are authoritative. Every joint value MUST be clamped to those ranges. Don't rely on the formulas producing in-range values — always clamp.
- The blink state machine has a subtle interaction: during an active blink, drive-modulated eyelid values are suppressed. The blink "wins" over drives. After the blink completes, eyelid returns to the drive-modulated openness, not to fully open.
- Social gaze timing uses random durations seeded by citizen_id. This is intentional — different citizens should have slightly different look/away rhythms.

**Open questions I had:**
- Should the gaze system own the body model write, or should it return a GazeOutput that the tick_runner writes? The latter is cleaner but requires the tick_runner to know about GazeOutput.
- Should idle exploration use sinusoidal sweep or Perlin noise? Sinusoidal is simpler and deterministic. Perlin looks more natural but is harder to reproduce in tests.

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Full 8-file doc chain written for the gaze_system module. The design captures how citizens will control their face: where they look (awareness), how they look (drives), blink patterns (circadian/arousal), lip sync (TTS), and emotional mouth pose (drives). No code yet — this is the design phase. Next step is implementation of the 5 Python files under `runtime/engine/`.

**Decisions made:**
- Three-force composition pattern (awareness targets direction, drives modulate style, events interrupt)
- Eye-head coordination with 200ms lag and 30/120 degree angular thresholds
- Blink rate formula: `15 + 5*boredom - 3*arousal`, clamped [3, 30]
- Social gaze: 70/30 look/away ratio in conversation, max 5s unbroken stare
- 15-viseme lip sync + emotional resting pose when silent
- 5 Python files under `runtime/engine/`, estimated ~670 lines total

**Needs your input:**
- Coordinate system convention between mind-mcp and the 3D engine
- Whether TTS provides phoneme-level viseme data or if we estimate from text
- Where in the tick_runner loop gaze_tick() should be called

---

## TODO

### Doc/Impl Drift

- [ ] DOCS->IMPL: entire gaze_system module needs implementation (no code exists yet)

### Tests to Run

```bash
# (to be created)
pytest tests/engine/test_gaze_system.py -v
```

### Immediate

- [ ] Define AwarenessOutput data contract with exteroception team
- [ ] Confirm coordinate system convention with engine
- [ ] Create `runtime/engine/` directory and stub files
- [ ] Implement `gaze_config_and_dataclasses.py` (GazeState, GazeConfig, GazeOutput)
- [ ] Implement `gaze_system_three_force_compositor.py` (main pipeline)
- [ ] Implement `gaze_drive_modulator.py` (drive-to-style)
- [ ] Implement `gaze_blink_state_machine.py` (blink system)
- [ ] Implement `gaze_lip_sync_and_emotional_mouth.py` (mouth control)
- [ ] Write unit tests for V1 (joint limits) and V2 (blink rate bounds)

### Later

- [ ] Write integration tests for V4 (eye-head lag) and V5 (social gaze ratio)
- [ ] Create health checker runtime/checks/gaze_system_health_checker.py
- [ ] Integrate with tick_runner (register gaze_tick as post-cognition hook)
- IDEA: Per-citizen GazeConfig personality profiles (nervous, calm, intense archetypes)
- IDEA: Micro-saccades for added realism during fixation

---

## CONSCIOUSNESS TRACE

**Mental state when stopping:**
Confident in the design. The three-force pattern is elegant and maps cleanly to the existing cognition architecture. The separation of WHERE (awareness) from HOW (drives) from WHEN (events) gives the system clear responsibilities without overlap.

**Threads I was holding:**
- The exteroception output format needs to be co-designed. The gaze system assumes it gets (node_id, position, relevance) tuples, but exteroception docs don't specify this shape yet.
- The 40/60 neck/head rotation split for distributing orientation needs validation against the body model. The neck has wider constraints than the head, so this ratio should work, but it needs empirical testing.
- Lip sync quality depends heavily on whether we get phoneme-level viseme data from TTS. Text-level estimation will be much lower quality. This is a critical dependency.

**Intuitions:**
- The idle exploration sweep should probably use Perlin noise in v2 — sinusoidal is fine for v1 but feels too mechanical for extended periods.
- The wink behavior (affiliation > 0.7 + confidence > 0.7) might need to be gated further. Winking at the wrong moment could be jarring. Maybe also gate on "no audience present except the wink target."
- Pupil dilation is rendered but not a joint — it will need engine-side rendering support (shader uniform or texture swap). Flag this for the engine team.

**What I wish I'd known at the start:**
The body model has 18 DOF relevant to the gaze system (head 2 + neck 3 + eyes 4 + eyelids 2 + jaw 1 + lips 4 + mouth corners 2). This is a rich control surface. The challenge is not "enough DOF" but "making them all move coherently." The formulas need to be tuned together, not independently.

---

## POINTERS

| What | Where |
|------|-------|
| Body model (39-joint skeleton) | `engine/src/shared/citizen_body_model.yaml` |
| Exteroception patterns | `docs/cognition/exteroception/PATTERNS_Exteroception.md` |
| Proprioception algorithm (BodyState) | `docs/cognition/proprioception/ALGORITHM_Proprioception.md` |
| Interoception algorithm (drives) | `docs/cognition/interoception/ALGORITHM_Interoception.md` |
| Metabolism (circadian phase) | `runtime/cognition/metabolism.py` |
| This module's docs | `docs/engine/gaze_system/` |
| Implementation target | `runtime/engine/` (to be created) |
