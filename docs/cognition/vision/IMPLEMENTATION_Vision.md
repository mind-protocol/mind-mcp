# Vision — Implementation: Code Architecture and Structure

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Vision.md
BEHAVIORS:       ./BEHAVIORS_Vision.md
PATTERNS:        ./PATTERNS_Vision.md
ALGORITHM:       ./ALGORITHM_Vision.md
VALIDATION:      ./VALIDATION_Vision.md
THIS:            IMPLEMENTATION_Vision.md
HEALTH:          ./HEALTH_Vision.md
SYNC:            ./SYNC_Vision.md

IMPL:            runtime/cognition/vision.py (to be created)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

```
runtime/
├── cognition/
│   ├── vision.py                            # VisionEngine, VisionState, VisionConfig, vision_tick() — main module
│   ├── vision_fov_cone_and_quaternion_helpers.py  # FOV cone math, quaternion conversions, position delta
│   ├── vision_clip_embedding_adapter.py     # CLIP model adapter (encode_image, cosine similarity)
│   ├── vision_screenshot_storage_handler.py # Object storage upload/download for screenshots
│   ├── exteroception.py                     # Sibling: graph-based environmental awareness
│   ├── models.py                            # Node dataclass with media dict
│   └── constants.py                         # Modality weights, thresholds
├── checks/
│   └── vision_health.py                     # Health checkers (to be created)
```

### File Responsibilities

| File | Purpose | Key Functions/Classes | Lines | Status |
|------|---------|----------------------|-------|--------|
| `runtime/cognition/vision.py` | Main vision engine: state management, capture gating, pipeline orchestration | `VisionEngine`, `VisionState`, `VisionConfig`, `VisionOutput`, `vision_tick()` | ~300 (est.) | TO BE CREATED |
| `runtime/cognition/vision_fov_cone_and_quaternion_helpers.py` | Spatial math: FOV cone computation, quaternion to forward vector, head rotation application | `FOVCone`, `quaternion_to_forward()`, `apply_head_rotation()`, `position_delta()` | ~120 (est.) | TO BE CREATED |
| `runtime/cognition/vision_clip_embedding_adapter.py` | CLIP model interface: image encoding, cosine similarity, batched inference | `CLIPAdapter`, `encode_image()`, `cosine_similarity()`, `cosine_distance()` | ~100 (est.) | TO BE CREATED |
| `runtime/cognition/vision_screenshot_storage_handler.py` | Object storage: screenshot upload, URI generation, retention policy | `ScreenshotStorage`, `upload()`, `generate_uri()` | ~80 (est.) | TO BE CREATED |
| `runtime/checks/vision_health.py` | Health checkers for capture rate, embedding coverage, flashbulb fidelity, render reliability | `vision_capture_rate_checker()`, `vision_embedding_coverage_checker()`, `vision_flashbulb_fidelity_checker()` | ~150 (est.) | TO BE CREATED |

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Pipeline with Gate

**Why this pattern:** Vision is a sequential pipeline (orientation -> FOV -> render -> CLIP -> store -> inject) with a gate early in the pipeline that short-circuits most ticks. The gate pattern matches the design requirement of token efficiency — most ticks should cost O(1) to determine "nothing to do" and return immediately. When the gate opens, the full pipeline executes in sequence because each step depends on the previous step's output.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Adapter | `vision_clip_embedding_adapter.py:CLIPAdapter` | Isolate CLIP model dependency; swap implementations (local vs API) without changing vision logic |
| Adapter | `vision_screenshot_storage_handler.py:ScreenshotStorage` | Isolate storage dependency; swap S3/R2/local without changing vision logic |
| State Object | `vision.py:VisionState` | Persistent state across ticks; encapsulates capture timing, previous frame, statistics |
| Config Object | `vision.py:VisionConfig` | All tunable parameters in one place; no magic numbers in logic |
| Null Object | `VisionOutput(captured=False)` | Non-capture ticks return a meaningful output, not None |

### Anti-Patterns to Avoid

- **God Object**: Do not put CLIP inference, storage, and quaternion math into vision.py. These are separate responsibilities with separate dependencies. Keep them in dedicated files.
- **Silent Failure**: Do not swallow render or CLIP errors. Every failure must log and set `skipped_reason` in VisionOutput.
- **Premature Optimization**: Do not implement batched CLIP or foveated rendering until single-citizen vision is working and tested. Start simple, measure, then optimize.
- **Fallback Rendering**: Do not generate synthetic screenshots or placeholder images when the engine is unavailable. Fail loud. Fallback images would produce false visual memories.

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Vision pipeline | State, gating, pipeline orchestration | Engine rendering, CLIP inference, storage | `VisionEngine.vision_tick()` |
| CLIP adapter | Image encoding, similarity math | Model weights, GPU management | `CLIPAdapter.encode_image()` |
| Storage adapter | Upload, URI generation | S3 configuration, bucket management | `ScreenshotStorage.upload()` |
| FOV helpers | Quaternion math, FOV cone construction | Body model definition, engine coordinate system | `quaternion_to_forward()`, `FOVCone` |

---

## SCHEMA

### VisionState

```yaml
VisionState:
  required:
    - last_capture_tick: int              # tick of most recent capture attempt
    - capture_interval: int               # ticks between periodic captures
  optional:
    - prev_embedding: list[float]         # 768D CLIP embedding of last captured frame (null until first capture)
    - prev_position: list[float]          # [x,y,z] at last capture (null until first capture)
    - flashbulb_cooldown_ticks: int       # remaining cooldown after flashbulb
    - total_captures: int                 # lifetime capture count
    - total_skipped: int                  # lifetime skip count (change detection)
    - total_flashbulbs: int               # lifetime flashbulb count
  constraints:
    - "prev_embedding length must equal VisionConfig.clip_dimension (768)"
    - "capture_interval must be >= 1"
```

### VisionOutput

```yaml
VisionOutput:
  required:
    - captured: bool                      # whether a capture occurred
  optional:
    - screenshot_uri: str                 # object storage URI (null if not captured)
    - clip_embedding: list[float]         # 768D CLIP vector (null if not captured or CLIP failed)
    - moment_id: str                      # ID of created Moment node (null if not stored)
    - is_flashbulb: bool                  # whether this was a flashbulb capture
    - skipped_reason: str                 # why no capture: "timer", "change_detection", "no_spatial", "render_failed"
  constraints:
    - "If captured=True, screenshot_uri must be non-null"
    - "If captured=True and CLIP available, clip_embedding must be non-null"
    - "If captured=False, skipped_reason must be non-null"
```

### Moment Node (visual)

```yaml
VisualMoment:
  required:
    - node_type: "moment"
    - name: str                           # "vision_{tick}"
    - content: str                        # awareness context + "I see the world from where I stand"
    - synthesis: str                      # compact description for embedding
    - media.image.uri: str                # object storage URI
  optional:
    - media.image.embedding: list[float]  # 768D CLIP vector
    - media.image.meta.resolution: list[int]  # [width, height]
    - media.image.meta.format: str        # "png" or "jpeg"
    - media.image.meta.trigger: str       # "periodic", "event:movement", "flashbulb"
    - media.image.meta.is_flashbulb: bool
    - subtype: str                        # "vision" for flashbulb, "observation" for normal
    - weight: float                       # 3.0 for flashbulb, 1.0 for normal
  relationships:
    - link: Actor (citizen who captured this)
```

---

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| `VisionEngine.vision_tick()` | `runtime/cognition/vision.py` (to be created) | Tick runner calls once per tick |
| `VisionEngine.__init__()` | `runtime/cognition/vision.py` (to be created) | Citizen initialization at spawn |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

### Vision Capture Pipeline: Screenshot from POV to Moment Node

This flow covers the complete path from reading the citizen's body state to storing a visual memory in the brain graph. It is the vision module's primary flow and touches all external boundaries (engine, CLIP, storage, graph).

```yaml
flow:
  name: vision_capture_pipeline
  purpose: "Transform citizen spatial state into grounded visual memory"
  scope: "Inputs: body state, gaze, limbic delta. Outputs: Moment node with media.image, LLM visual context."
  steps:
    - id: read_orientation
      description: "Read position + orientation from citizen's NodeBase spatial fields"
      file: runtime/cognition/vision.py
      function: vision_tick()
      input: "citizen.position, citizen.orientation, gaze_output"
      output: "eye_origin, viewing_direction"
      trigger: "tick_runner calls vision_tick()"
      side_effects: "none"
    - id: capture_gate
      description: "Check periodic timer, event triggers, and flashbulb condition"
      file: runtime/cognition/vision.py
      function: vision_tick()
      input: "tick, limbic_delta, position_delta, exteroception_events"
      output: "should_capture (bool), is_flashbulb (bool), trigger_reason (str)"
      trigger: "sequential after read_orientation"
      side_effects: "none"
    - id: render_request
      description: "Send FOV parameters to 3D engine, receive screenshot bytes"
      file: runtime/cognition/vision.py
      function: vision_tick()
      input: "FOVCone parameters"
      output: "screenshot image bytes"
      trigger: "only if should_capture=True"
      side_effects: "engine API call (external)"
    - id: clip_embedding
      description: "Generate CLIP embedding from screenshot, compare to previous frame"
      file: runtime/cognition/vision_clip_embedding_adapter.py
      function: CLIPAdapter.encode_image()
      input: "screenshot image bytes"
      output: "768D CLIP embedding vector"
      trigger: "sequential after render_request"
      side_effects: "CLIP model inference (external)"
    - id: change_detection
      description: "Compare current CLIP embedding to previous via cosine distance"
      file: runtime/cognition/vision.py
      function: vision_tick()
      input: "current_embedding, state.prev_embedding"
      output: "change_detected (bool)"
      trigger: "sequential after clip_embedding"
      side_effects: "none"
    - id: store_moment
      description: "Upload screenshot to storage, create Moment node with media.image"
      file: runtime/cognition/vision.py
      function: vision_tick()
      input: "screenshot bytes, CLIP embedding, trigger metadata"
      output: "Moment node ID, screenshot URI"
      trigger: "only if change_detected=True or is_flashbulb=True"
      side_effects: "object storage write, graph write (Moment node)"
    - id: register_visual
      description: "Register screenshot for inclusion in next LLM multimodal context"
      file: runtime/cognition/vision.py
      function: vision_tick()
      input: "screenshot URI, image bytes, is_flashbulb"
      output: "registration confirmation"
      trigger: "sequential after store_moment"
      side_effects: "LLM context state update"
  docking_points:
    guidance:
      include_when: "Cross-boundary calls, state mutations, observable outputs"
      omit_when: "Internal variable assignments, pure math steps"
      selection_notes: "Focus on external API calls (engine, CLIP, storage, graph) and the final LLM registration"
    available:
      - id: dock_render_request
        type: api
        direction: output
        file: runtime/cognition/vision.py
        function: vision_tick()
        trigger: "should_capture=True"
        payload: "RenderRequest(camera_position, camera_direction, fov, resolution)"
        async_hook: optional
        needs: "add async hook for non-blocking render"
        notes: "External API call to 3D engine. Timeout-protected."
      - id: dock_render_response
        type: api
        direction: input
        file: runtime/cognition/vision.py
        function: vision_tick()
        trigger: "engine responds"
        payload: "screenshot image bytes (PNG/JPEG)"
        async_hook: optional
        needs: "none"
        notes: "Response from engine. May fail (timeout, error)."
      - id: dock_clip_inference
        type: api
        direction: output
        file: runtime/cognition/vision_clip_embedding_adapter.py
        function: CLIPAdapter.encode_image()
        trigger: "screenshot received"
        payload: "image bytes"
        async_hook: optional
        needs: "add async hook for batched inference"
        notes: "CLIP model inference. ~50ms per image."
      - id: dock_storage_write
        type: file
        direction: output
        file: runtime/cognition/vision_screenshot_storage_handler.py
        function: ScreenshotStorage.upload()
        trigger: "change detected or flashbulb"
        payload: "image bytes, path, content_type"
        async_hook: optional
        needs: "none"
        notes: "Object storage write (S3/R2/local)."
      - id: dock_moment_write
        type: graph_ops
        direction: output
        file: runtime/cognition/vision.py
        function: create_moment()
        trigger: "change detected or flashbulb"
        payload: "Moment node with media.image (uri + embedding + meta)"
        async_hook: not_applicable
        needs: "none"
        notes: "L1 brain graph write. Uses existing graph_write API."
      - id: dock_llm_registration
        type: event
        direction: output
        file: runtime/cognition/vision.py
        function: llm_context.register_visual()
        trigger: "after moment stored"
        payload: "citizen_id, image_uri, image_bytes, is_flashbulb"
        async_hook: not_applicable
        needs: "none"
        notes: "Registers screenshot for next LLM prompt. Consumed by prompt assembler."
    health_recommended:
      - dock_id: dock_render_response
        reason: "Engine reliability directly determines whether citizens can see"
      - dock_id: dock_clip_inference
        reason: "CLIP availability determines whether visual memories participate in physics"
      - dock_id: dock_moment_write
        reason: "Moment creation is the permanent record — if it fails, the visual memory is lost"
```

---

## LOGIC CHAINS

### LC1: Full Capture Pipeline

**Purpose:** Transform citizen body state into visual memory and LLM context.

```
body_state (position, orientation, gaze)
  -> VisionEngine.vision_tick()                 # gate check, orchestration
    -> vision_fov_cone_helpers.FOVCone()         # compute FOV from orientation
      -> engine.render_from_pov()                # external: get screenshot
        -> CLIPAdapter.encode_image()            # external: get embedding
          -> cosine_distance(prev, current)      # change detection
            -> ScreenshotStorage.upload()        # store image
              -> graph_write.create_moment()     # store Moment node
                -> llm_context.register_visual() # register for LLM
                  -> VisionOutput(captured=True)
```

**Data transformation:**
- Input: `position [x,y,z]` + `orientation [qx,qy,qz,qw]` + `head_pitch, head_yaw` -- spatial state
- After FOV: `FOVCone(origin, direction, angles, range)` -- geometric frustum
- After render: `bytes` -- raw screenshot image data
- After CLIP: `list[float]` 768D -- visual embedding vector
- After change detection: `bool` -- significant change flag
- After storage: `str` -- URI of stored screenshot
- After graph write: `str` -- Moment node ID
- Output: `VisionOutput` -- complete capture result

### LC2: Short-Circuit (No Capture)

**Purpose:** Most ticks produce no capture. The short-circuit path is the common case.

```
body_state
  -> VisionEngine.vision_tick()
    -> check: position is null? -> VisionOutput(skipped_reason="no_spatial")
    -> check: gate closed? -> VisionOutput(skipped_reason="timer")
    -> check: change_detection says static? -> VisionOutput(skipped_reason="change_detection")
```

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
runtime/cognition/vision.py
    └── imports -> runtime/cognition/vision_fov_cone_and_quaternion_helpers.py
    └── imports -> runtime/cognition/vision_clip_embedding_adapter.py
    └── imports -> runtime/cognition/vision_screenshot_storage_handler.py
    └── imports -> runtime/cognition/exteroception.py (for awareness text)
    └── imports -> runtime/cognition/models.py (for Node/Moment dataclass)
    └── imports -> runtime/cognition/constants.py (for modality weights)
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `numpy` | Cosine similarity, vector operations | `vision_clip_embedding_adapter.py` |
| `Pillow` (PIL) | Image bytes handling, format conversion | `vision.py`, `vision_clip_embedding_adapter.py` |
| `transformers` or `open_clip` | CLIP model inference (if self-hosted) | `vision_clip_embedding_adapter.py` |
| `boto3` or `httpx` | Object storage upload (S3/R2) or HTTP API | `vision_screenshot_storage_handler.py` |

---

## STATE MANAGEMENT

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| VisionState | `vision.py:VisionEngine._state` | Per-citizen instance | Created at citizen spawn, persists across ticks, not serialized (ephemeral) |
| VisionConfig | `vision.py:VisionEngine._config` | Per-citizen instance (but usually shared defaults) | Created at initialization, immutable during runtime |
| Previous CLIP embedding | `VisionState.prev_embedding` | Per-citizen | Updated on each successful capture, used for change detection |
| Capture statistics | `VisionState.total_*` | Per-citizen | Monotonically increasing counters, read by health checkers |

### State Transitions

```
NO_VISION (position=null) ──(position assigned)──> IDLE (gate closed, waiting)
IDLE ──(timer expires OR event triggers)──> CAPTURING (render + CLIP + store)
CAPTURING ──(change detected)──> STORED (Moment created, LLM registered)
CAPTURING ──(no change)──> IDLE (frame discarded, timer reset)
IDLE ──(limbic_delta > 0.7)──> FLASHBULB (always stores, triple weight)
FLASHBULB ──(stored)──> IDLE (cooldown active)
```

---

## RUNTIME BEHAVIOR

### Initialization

```
1. VisionEngine created with VisionConfig (default or citizen-specific)
2. VisionState initialized with last_capture_tick=-999 (forces first capture)
3. CLIPAdapter loaded (model initialization, may be shared across citizens)
4. ScreenshotStorage configured (connection to object storage)
5. Engine render API endpoint validated
```

### Main Loop (per tick)

```
1. Tick runner calls VisionEngine.vision_tick() with body state, gaze, limbic delta
2. Gate check: periodic timer, event triggers, flashbulb (O(1), fast)
3. If gate closed: return VisionOutput(captured=False) immediately
4. If gate open: FOV -> render -> CLIP -> change detection -> store -> register
5. Return VisionOutput with capture result
```

### Shutdown

```
1. Flush any pending storage uploads
2. Log final statistics (total_captures, total_skipped, total_flashbulbs)
```

---

## CONCURRENCY MODEL

| Component | Model | Notes |
|-----------|-------|-------|
| `vision_tick()` | Synchronous | Called sequentially by tick runner. No concurrent ticks for same citizen. |
| Engine render | Async-capable | render_from_pov could be async (non-blocking). V1 uses sync with timeout. |
| CLIP inference | Sync or batched | V1 uses sync per-image. V2 may batch across citizens for GPU efficiency. |
| Storage upload | Async-capable | Upload could be fire-and-forget. V1 uses sync to ensure URI is available. |

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `fov_horizontal_deg` | `VisionConfig` | `90.0` | Horizontal field of view in degrees |
| `fov_vertical_deg` | `VisionConfig` | `60.0` | Vertical field of view in degrees |
| `fov_range` | `VisionConfig` | `50.0` | Maximum visible distance in world units |
| `head_height_offset` | `VisionConfig` | `0.72` | Head height above root position |
| `capture_interval_ticks` | `VisionConfig` | `10` | Ticks between periodic captures |
| `change_threshold` | `VisionConfig` | `0.1` | CLIP cosine distance threshold for change detection |
| `movement_threshold` | `VisionConfig` | `5.0` | Position delta for event-triggered capture |
| `arousal_threshold` | `VisionConfig` | `0.5` | Stimulus energy threshold for event trigger |
| `flashbulb_threshold` | `VisionConfig` | `0.7` | Limbic delta threshold for flashbulb capture |
| `flashbulb_cooldown` | `VisionConfig` | `30` | Minimum ticks between flashbulb captures |
| `render_resolution` | `VisionConfig` | `(512, 512)` | Screenshot resolution |
| `render_format` | `VisionConfig` | `"png"` | Image format for storage |
| `render_timeout_ms` | `VisionConfig` | `2000` | Max wait for engine response |
| `clip_model` | `VisionConfig` | `"ViT-L/14"` | CLIP model variant |
| `clip_dimension` | `VisionConfig` | `768` | Embedding dimensionality |
| `clip_timeout_ms` | `VisionConfig` | `1000` | Max wait for CLIP inference |

---

## BIDIRECTIONAL LINKS

### Code -> Docs

Files that reference this documentation:

| File | Line | Reference |
|------|------|-----------|
| `runtime/cognition/vision.py` | (to be created) | `# DOCS: docs/cognition/vision/` |

### Docs -> Code

| Doc Section | Implemented In |
|-------------|----------------|
| ALGORITHM Step 1 (Read Orientation) | `vision.py:vision_tick()` (to be created) |
| ALGORITHM Step 2 (Capture Gate) | `vision.py:vision_tick()` (to be created) |
| ALGORITHM Step 3 (FOV + Render) | `vision.py:vision_tick()` + `vision_fov_cone_and_quaternion_helpers.py` (to be created) |
| ALGORITHM Step 4 (CLIP + Change Detection) | `vision_clip_embedding_adapter.py` + `vision.py` (to be created) |
| ALGORITHM Step 5 (Store Moment) | `vision.py:vision_tick()` + `vision_screenshot_storage_handler.py` (to be created) |
| ALGORITHM Step 6 (Register for LLM) | `vision.py:vision_tick()` (to be created) |
| BEHAVIOR B1 (FOV from orientation) | `vision_fov_cone_and_quaternion_helpers.py` (to be created) |
| BEHAVIOR B2 (Static scene suppression) | `vision.py:vision_tick()` change detection block (to be created) |
| VALIDATION V1 (FOV from body) | unit tests (to be created) |
| VALIDATION V2 (No token waste) | unit tests + `vision_health.py:vision_capture_rate_checker` (to be created) |

---

## EXTRACTION CANDIDATES

No extraction candidates yet (module not yet implemented). File size estimates are within OK range.

---

## MARKERS

<!-- @mind:todo Create runtime/cognition/vision.py with VisionEngine class, following the algorithm in ALGORITHM_Vision.md. Estimated ~300 lines. -->

<!-- @mind:todo Create runtime/cognition/vision_fov_cone_and_quaternion_helpers.py with FOVCone dataclass and quaternion math helpers. Estimated ~120 lines. -->

<!-- @mind:todo Create runtime/cognition/vision_clip_embedding_adapter.py with CLIPAdapter class. Start with a stub that returns random embeddings for testing; replace with real CLIP when infrastructure is ready. -->

<!-- @mind:todo Create runtime/cognition/vision_screenshot_storage_handler.py with ScreenshotStorage class. Start with local filesystem storage; add S3/R2 adapter later. -->

<!-- @mind:todo Create runtime/checks/vision_health.py implementing the 6 checkers defined in HEALTH_Vision.md. -->

<!-- @mind:todo Wire VisionEngine into the tick runner. The tick runner must call vision_tick() once per tick, after exteroception and interoception, providing body state, gaze output, and limbic delta. -->

<!-- @mind:escalation The LLM context assembly (Step 6) requires a registration mechanism that does not exist yet. The prompt assembler must know to include the latest screenshot as multimodal input. Need to design the interface between vision_tick() and the prompt assembly system. -->
