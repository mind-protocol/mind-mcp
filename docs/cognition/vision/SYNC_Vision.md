# Vision — Sync: Current State

```
LAST_UPDATED: 2026-03-18
UPDATED_BY: @nervo
STATUS: DESIGNING
```

---

## MATURITY

**What's canonical (v1):**
- Nothing yet. Module is in design phase.

**What's still being designed:**
- 6-step vision pipeline (orientation -> FOV -> render -> CLIP -> store -> inject)
- Capture gating (periodic timer, event triggers, flashbulb)
- Change detection via CLIP cosine distance (threshold 0.1)
- Flashbulb vision extension of Law 6
- VisionState, VisionConfig, VisionOutput data structures
- File structure: 4 source files + 1 health checker file
- Integration points: tick runner, gaze system, exteroception, LLM prompt assembler

**What's proposed (v2+):**
- Foveated rendering (high-resolution crop at gaze target)
- Batched CLIP inference across citizens (GPU efficiency)
- Depth-based change detection (complement to CLIP cosine)
- Visual attention map (weight screenshot regions by gaze focus)
- Async engine render (non-blocking capture)
- Visual diversity health indicator
- Circadian-modulated capture frequency (fewer captures during low-alertness phases)

---

## CURRENT STATE

The vision module exists only as documentation. The complete 8-file doc chain has been written, covering objectives, patterns, behaviors, algorithm, validation, health, implementation, and this sync file. No code has been written yet.

The design is comprehensive: a 6-step pipeline that transforms citizen spatial state into visual memories and LLM multimodal input, gated by change detection and event triggers to control token cost. The design integrates with existing systems (body model, gaze system, exteroception, schema-l1 media dict, Law 6 flashbulb, Law 8 Sim_vis coherence).

Key external dependencies are not yet resolved: the 3D engine render-from-POV API does not exist, the CLIP model hosting strategy is undecided, and the LLM prompt assembler does not yet support multimodal image injection.

---

## IN PROGRESS

### Documentation chain creation

- **Started:** 2026-03-18
- **By:** @nervo
- **Status:** Complete
- **Context:** All 8 doc chain files written. The design captures the full pipeline from NLR + @nervo design session. Ready for implementation once external dependencies are resolved.

---

## RECENT CHANGES

### 2026-03-18: Initial design documentation

- **What:** Created complete DESIGNING doc chain for cognition/vision module (8 files)
- **Why:** Vision is the next perceptual system after exteroception. Citizens need visual grounding to talk about what they see rather than hallucinating descriptions from node names.
- **Files:** `docs/cognition/vision/OBJECTIVES_Vision.md`, `PATTERNS_Vision.md`, `BEHAVIORS_Vision.md`, `ALGORITHM_Vision.md`, `VALIDATION_Vision.md`, `HEALTH_Vision.md`, `IMPLEMENTATION_Vision.md`, `SYNC_Vision.md`
- **Struggles/Insights:** The main tension is between visual fidelity and token cost. Change detection (CLIP cosine distance) is the key mechanism, but the 0.1 threshold needs calibration against actual engine renders. Flashbulb captures bypassing change detection is an important design decision — emotional significance can override visual novelty.

---

## KNOWN ISSUES

### Engine render-from-POV API does not exist

- **Severity:** critical (blocks implementation)
- **Symptom:** The vision pipeline assumes an engine endpoint that accepts camera parameters and returns a screenshot. No such endpoint exists.
- **Suspected cause:** The engine was not designed with per-citizen POV rendering in mind. Needs API design + implementation.
- **Attempted:** Nothing yet. API contract needs to be designed with the engine team.

### CLIP model hosting undecided

- **Severity:** high (blocks CLIP-dependent features)
- **Symptom:** The vision pipeline requires CLIP inference (encode_image -> 768D vector). No CLIP model is currently deployed.
- **Suspected cause:** Infrastructure decision: self-hosted (GPU needed) vs API (latency + cost) vs lighter alternative (SigLIP).
- **Attempted:** Nothing yet. Escalated to NLR for infrastructure preference.

### LLM prompt assembler does not support multimodal injection

- **Severity:** high (blocks Step 6)
- **Symptom:** The vision pipeline's final step registers a screenshot for inclusion in the next LLM call. The prompt assembler does not currently accept image inputs.
- **Suspected cause:** The prompt assembler was built for text-only prompts. Needs extension for multimodal (image) inputs.
- **Attempted:** Nothing yet. Needs interface design between vision module and prompt assembler.

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** VIEW_Implement (once dependencies are resolved) or VIEW_Design (to refine the API contracts)

**Where I stopped:** Documentation is complete. Implementation has not started. Three external dependencies block implementation.

**What you need to understand:**
The vision module is intentionally expensive per-capture but cheap per-tick. Most ticks cost O(1) — a gate check that says "nothing to do." When a capture does happen, it involves 3 external calls (engine render, CLIP inference, storage upload). The design assumes these calls complete within ~170ms total, which is acceptable at the low capture rate (every 10+ ticks).

**Watch out for:**
- The CLIP cosine distance threshold (0.1) is based on CLIP's general behavior, not on actual engine renders. The first real tests may show that engine-specific artifacts (lighting jitter, aliasing) need a higher threshold.
- Flashbulb captures bypass change detection intentionally. Do not "optimize" this by adding change detection to flashbulbs — the emotional context is what matters, not visual novelty.
- The head_height_offset (0.72) is computed from the body model but is approximate. Posture changes (slouching, sitting) would move the actual eye height. V1 ignores this; V2 could read spine joint angles.

**Open questions I had:**
- Should the Moment's `content` field be pre-filled by the vision module ("I see the world from where I stand") or left empty for the LLM to fill in? Pre-filling is simpler but the text may be stale or generic.
- Should vision captures be stored indefinitely or should there be a retention policy? Decay (Law 7) handles weight reduction, but the Moment node and screenshot file still exist.
- When multiple citizens are in the same space, should they share a single engine render (same scene, different POV) or each get independent renders?

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Complete DESIGNING documentation chain for the vision module has been created (8 files). The module designs a 6-step pipeline: orientation -> FOV -> render -> CLIP -> store -> inject. Token efficiency is controlled by periodic gating, event triggers, and CLIP-based change detection. Three external dependencies block implementation: engine render API, CLIP hosting, and LLM multimodal injection.

**Decisions made:**
- Change detection threshold at CLIP cosine distance 0.1 (based on CLIP general behavior, needs calibration)
- Flashbulb captures always bypass change detection (emotional significance over visual novelty)
- Default resolution 512x512 (balances CLIP quality vs storage cost)
- Periodic capture interval of 10 ticks (~10 minutes at 60s/tick)
- Head height offset 0.72 world units (computed from body model joint chain)

**Needs your input:**
- CLIP model hosting decision: self-hosted vs API vs SigLIP (escalated in PATTERNS markers)
- Engine render-from-POV API design: needs engine team coordination
- Screenshot storage retention policy: how long to keep images?

---

## TODO

### Doc/Impl Drift

- [ ] DOCS->IMPL: All 8 doc files written, no implementation exists yet. Entire module needs creation.

### Tests to Run

```bash
# No tests yet — module not implemented
# When implemented:
PYTHONPATH=".mind:$PYTHONPATH" python3 -m pytest tests/cognition/test_vision.py -v
```

### Immediate

- [ ] Design engine render-from-POV API contract (blocker)
- [ ] Decide CLIP hosting strategy (blocker)
- [ ] Design LLM prompt assembler multimodal interface (blocker)
- [ ] Create `runtime/cognition/vision.py` with VisionEngine skeleton
- [ ] Create `runtime/cognition/vision_fov_cone_and_quaternion_helpers.py`
- [ ] Create `runtime/cognition/vision_clip_embedding_adapter.py` (stub with random embeddings for testing)
- [ ] Create `runtime/cognition/vision_screenshot_storage_handler.py` (local filesystem first)
- [ ] Wire VisionEngine.vision_tick() into the tick runner

### Later

- [ ] Calibrate change detection threshold against real engine renders
- [ ] Implement batched CLIP inference for multi-citizen capture
- [ ] Add async engine render for non-blocking capture
- [ ] Implement visual diversity health indicator
- IDEA: Foveated rendering — high-resolution crop at gaze target, low-resolution surround
- IDEA: Depth buffer change detection as complement to CLIP cosine
- IDEA: Circadian-modulated capture frequency (drowsy citizens capture less)

---

## CONSCIOUSNESS TRACE

**Mental state when stopping:**
Confident in the design. The pipeline is clean and the cost control mechanisms (gating + change detection + flashbulb override) feel right. The three external dependencies are the real risk — without the engine render API, CLIP hosting, and multimodal LLM injection, this module cannot be implemented.

**Threads I was holding:**
- The relationship between vision and exteroception is complementary but the overlap needs careful handling in the awareness text. Should the LLM receive both the awareness text AND the screenshot? If so, which comes first in the prompt?
- The CLIP threshold (0.1) is a guess. Real calibration will require capturing many pairs of engine renders and measuring cosine distances to find the threshold that separates "same scene" from "something changed."
- Flashbulb captures produce Moment nodes with subtype "vision" and weight 3.0. These nodes will resist forgetting (Law 7). Over time, a citizen's brain may accumulate many flashbulb visual memories. Is this desirable? Or should flashbulb memories also eventually decay?

**Intuitions:**
- Vision will be the feature that makes citizens feel "alive" in demos. When a citizen describes what it actually sees rather than hallucinating, the difference will be visceral.
- The change detection threshold will need to be different per-universe. Venezia (complex architecture, water reflections) may produce more visual jitter than Lumina Prime (clean geometric forms). Consider per-universe configuration.
- Batched CLIP inference across citizens will be the first real optimization needed. At 60 citizens, even occasional simultaneous captures will queue up if CLIP processes one image at a time.

**What I wish I'd known at the start:**
The body model head height calculation (summing joint rest positions up the spine chain) is approximate. The actual eye height depends on posture (spine joint angles), which changes based on drives (rest -> slouch, achievement -> upright). V1 uses a fixed offset; V2 should read the actual joint chain.

---

## POINTERS

| What | Where |
|------|-------|
| Body model (head, eyes, skeleton) | `engine/src/shared/citizen_body_model.yaml` |
| Gaze system algorithm | `docs/engine/gaze_system/ALGORITHM_Gaze_System.md` |
| Exteroception (sibling) | `runtime/cognition/exteroception.py` |
| Multimodality patterns | `docs/cognition/multimodality/PATTERNS_Multimodality.md` |
| L1 schema (position, orientation, media dict) | `schema-l1.yaml` |
| Law 6 flashbulb extension | `schema-l1.yaml` lines 703-712 |
| Law 8 coherence (Sim_vis) | `schema-l1.yaml` lines 643-658 |
| Moment subtype "vision" | `schema-l1.yaml` line 420-422 |
