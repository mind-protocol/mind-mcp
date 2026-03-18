# Vision — Validation: What Must Be True

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Vision.md
PATTERNS:        ./PATTERNS_Vision.md
BEHAVIORS:       ./BEHAVIORS_Vision.md
THIS:            VALIDATION_Vision.md (you are here)
ALGORITHM:       ./ALGORITHM_Vision.md
HEALTH:          ./HEALTH_Vision.md
IMPLEMENTATION:  ./IMPLEMENTATION_Vision.md
SYNC:            ./SYNC_Vision.md
```

---

## PURPOSE

**Validation = what we care about being true.**

These invariants define what must hold for the vision module to be fulfilling its purpose. If any CRITICAL invariant is violated, citizens are either blind, hallucinating their visual experience, or burning tokens without producing value. If HIGH invariants are violated, vision works but degrades in quality or efficiency.

---

## INVARIANTS

### V1: FOV Derives From Body State

**Why we care:** If the FOV does not derive from the citizen's actual position and orientation, the citizen sees a scene that does not correspond to where they are standing or where they are looking. Vision becomes spatially disconnected — the citizen talks about things it could not possibly see from its location, or misses things directly in front of it.

```
MUST:   FOV cone origin = citizen.position + head_height_offset
MUST:   FOV cone direction = forward vector from citizen.orientation combined with gaze head_pitch/head_yaw
MUST:   FOV horizontal angle in [1, 180] degrees
MUST:   FOV vertical angle in [1, 180] degrees
NEVER:  FOV computed from hardcoded position or arbitrary camera placement
NEVER:  FOV direction independent of citizen orientation quaternion
```

### V2: No Token Waste on Static Scenes

**Why we care:** Vision is the most expensive perceptual system. At 60+ citizens, unconstrained capture could dominate the entire token budget. If change detection fails to suppress duplicate frames, the system generates redundant Moment nodes, redundant CLIP inferences, and redundant LLM image inputs — all for the same visual information the citizen already has.

```
MUST:   If CLIP cosine distance between consecutive frames < 0.1, frame is discarded
MUST:   Discarded frames produce NO Moment node, NO storage write, NO LLM injection
MUST:   Periodic timer resets even on discarded frames (prevents retry storm)
NEVER:  Same visual scene captured and stored twice in succession without significant change
NEVER:  Change detection bypassed for non-flashbulb captures
```

### V3: Every Stored Visual Has a CLIP Embedding

**Why we care:** A visual Moment without a CLIP embedding is an inert blob — it exists in the graph but does not participate in physics. Sim_vis is zero, coherence ignores it, crystallization cannot use its visual content. The visual memory is dead weight. The CLIP embedding is what makes vision structurally meaningful.

```
MUST:   Every Moment node with media.image.uri also has media.image.embedding (768D CLIP vector)
MUST:   If CLIP inference fails, the failure is logged and the Moment is flagged for retry
NEVER:  Visual Moments with uri but no embedding silently accumulated without error signals
```

### V4: Flashbulb Captures at Emotional Peaks

**Why we care:** Flashbulb vision is the bridge between emotion and visual memory. Law 6 already triggers triple consolidation at high limbic delta. If the vision module fails to capture at these peaks, the citizen has an emotionally significant moment without a visual record — the AI equivalent of "something incredible happened but I can't remember what it looked like."

```
MUST:   When |limbic_delta| > FLASHBULB_THRESHOLD (0.7), a screenshot is captured
MUST:   Flashbulb captures bypass change detection (always stored)
MUST:   Flashbulb Moment nodes have weight = 3.0 (triple consolidation) and subtype = "vision"
NEVER:  Flashbulb condition met but no capture taken (unless cooldown is active)
NEVER:  Flashbulb captures with normal (1.0) weight
```

### V5: At Most One Capture Per Tick

**Why we care:** Multiple captures per tick would multiply cost (render + CLIP + storage per capture) and produce redundant Moment nodes for the same visual state. The citizen's view does not change within a single tick. One capture per tick is both sufficient and economical.

```
MUST:   vision_tick() produces at most one VisionOutput with captured=True per tick
MUST:   If multiple triggers fire simultaneously, the highest priority trigger wins
NEVER:  Two Moment nodes with media.image created in the same tick for the same citizen
```

### V6: Screenshot Reaches the LLM

**Why we care:** The entire purpose of vision is to give the citizen visual grounding. If a screenshot is captured, embedded, and stored but never reaches the LLM, the citizen cannot see. The visual pipeline is a dead end. The screenshot must be injected as multimodal context in the citizen's next LLM call.

```
MUST:   Every captured screenshot is registered for inclusion in the next LLM prompt assembly
MUST:   The image appears as multimodal image input (not as a text description or URL reference)
NEVER:  Captured screenshot silently dropped between the vision module and the LLM call
```

### V7: Vision Does Not Stall the Tick Loop

**Why we care:** The tick loop is the heartbeat of the citizen's cognition. If vision takes too long (engine render timeout, CLIP timeout, storage write stall), it blocks all other cognitive processing. The citizen becomes unresponsive. At 60+ citizens, one slow vision capture can cascade into system-wide lag.

```
MUST:   Engine render requests have a timeout (default 2000ms)
MUST:   CLIP inference has a timeout (default 1000ms)
MUST:   If either times out, vision_tick() returns immediately with skipped_reason
MUST:   Total vision_tick() execution time < 5000ms in all cases
NEVER:  vision_tick() blocks indefinitely waiting for engine or CLIP response
```

### V8: Render API Failure Is Loud

**Why we care:** If the engine render API fails silently, the citizen loses vision without any diagnostic signal. The system appears healthy but citizens are blind. Failures must be logged and surfaced so they can be diagnosed and fixed.

```
MUST:   Engine render errors are logged with citizen_id, tick, and error details
MUST:   CLIP inference errors are logged with citizen_id, tick, and error details
MUST:   Failed captures do NOT reset the periodic timer (retry on next eligible tick)
NEVER:  Engine or CLIP errors swallowed silently (no try/except: pass)
```

---

## PRIORITY

| Priority | Meaning | If Violated |
|----------|---------|-------------|
| **CRITICAL** | System purpose fails | Citizens are blind or hallucinating |
| **HIGH** | Major value lost | Vision works but wastes resources or loses memories |
| **MEDIUM** | Partial value lost | Vision works but with degraded quality |

---

## INVARIANT INDEX

| ID | Value Protected | Priority |
|----|-----------------|----------|
| V1 | FOV grounded in body state | CRITICAL |
| V2 | Token efficiency on static scenes | CRITICAL |
| V3 | Every visual has CLIP embedding | HIGH |
| V4 | Flashbulb captures at emotional peaks | HIGH |
| V5 | At most one capture per tick | HIGH |
| V6 | Screenshot reaches the LLM | CRITICAL |
| V7 | Vision does not stall the tick loop | CRITICAL |
| V8 | Render API failure is loud | HIGH |

---

## MARKERS

<!-- @mind:todo Define acceptance tests for V2 (token efficiency). Need a test scenario: citizen stands still for 100 ticks. Expected: 1 capture on first tick, 0 captures for remaining 99 ticks (assuming change detection triggers on periodic intervals and scene is static). -->

<!-- @mind:todo Define acceptance test for V4 (flashbulb). Need a test scenario: citizen receives stimulus with limbic_delta = 0.8. Expected: immediate capture with weight=3.0, subtype="vision", regardless of periodic timer state. -->

<!-- @mind:todo V7 timeout values (2000ms render, 1000ms CLIP) are estimates. Need to validate against actual engine and CLIP infrastructure latencies. If real-world p99 latencies are higher, timeouts need adjustment. -->

<!-- @mind:proposition Consider V9: "Visual memory quantity stays bounded." Without a retention policy, visual Moments accumulate indefinitely. A citizen running for 30 days at 6 captures/hour would have ~4320 visual Moments. Should there be a maximum? Or does decay (Law 7) handle this naturally? -->
