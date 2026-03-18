# Vision — Algorithm: 7-Step Pipeline, Compression, Change Detection, Flashbulb Trigger

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
THIS:            ALGORITHM_Vision.md (you are here)
VALIDATION:      ./VALIDATION_Vision.md
HEALTH:          ./HEALTH_Vision.md
IMPLEMENTATION:  ./IMPLEMENTATION_Vision.md
SYNC:            ./SYNC_Vision.md

IMPL:            runtime/cognition/vision.py (to be created)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

The vision algorithm runs once per tick and decides whether to capture a screenshot, process it, and store it as a visual memory. It consumes the citizen's spatial state (position, orientation), gaze system output (head/eye direction), limbic state (for flashbulb detection), and exteroception events (for event-triggered capture). It produces a VisionOutput containing the capture result.

The algorithm is designed around cost control. Most ticks produce no capture. Capture occurs only when the periodic timer expires, an event trigger fires, or a flashbulb condition is detected. When a capture does occur, the raw engine screenshot (1080p PNG, ~2MB) is resized and JPEG-compressed before CLIP embedding or LLM delivery. Change detection compares the new frame's CLIP embedding against the previous frame's embedding. Only significant visual changes (cosine distance >= 0.1) produce new Moment nodes — except for flashbulb captures, which always persist.

**Critical constraint: raw engine screenshots must NEVER be sent to the LLM.** Every screenshot passes through a mandatory resize + JPEG compression step (Step 3.5). The full-res original is stored in the graph for memory; the compressed version goes to CLIP and LLM.

The 7-step pipeline executes in sequence: (1) read orientation, (2) determine capture gate, (3) compute FOV + request screenshot, (3.5) resize + compress, (4) CLIP embedding + change detection on resized version, (5) store full-res as Moment node, (6) inject compressed version as multimodal stimulus. Steps 3-6 only execute if the capture gate (periodic, event, or flashbulb) is open.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| Visual perception | B1, B3, B4, B8 | The 6-step pipeline transforms spatial state into grounded visual experience |
| Token efficiency | B2, B7, B8 | Capture gating and change detection prevent waste on static scenes |
| Visual memories | B3, B5 | Moment creation with media.image stores visual history in the brain |
| CLIP in physics | B5 | CLIP embedding on every visual Moment enables Sim_vis in Law 8 coherence |
| Flashbulb vision | B6 | Flashbulb trigger bypasses normal gating at emotional peaks |

---

## DATA STRUCTURES

### VisionState (persistent across ticks)

```python
@dataclass
class VisionState:
    # Capture timing
    last_capture_tick: int = -999       # tick of most recent capture
    capture_interval: int = 10          # ticks between periodic captures (default 10)

    # Previous frame
    prev_embedding: list[float] | None = None   # CLIP 768D of last captured frame
    prev_position: list[float] | None = None    # position at last capture

    # Flashbulb state
    flashbulb_cooldown_ticks: int = 0   # prevent rapid-fire flashbulb captures

    # Statistics
    total_captures: int = 0
    total_skipped: int = 0              # frames skipped by change detection
    total_flashbulbs: int = 0
```

### VisionConfig (tunable parameters)

```python
@dataclass
class VisionConfig:
    # FOV parameters
    fov_horizontal_deg: float = 90.0    # horizontal field of view
    fov_vertical_deg: float = 60.0      # vertical field of view
    fov_range: float = 50.0             # maximum visible distance (world units)
    head_height_offset: float = 0.72    # head height above root position (from body model)

    # Capture gating
    capture_interval_ticks: int = 10    # periodic capture interval
    change_threshold: float = 0.1       # CLIP cosine distance threshold
    movement_threshold: float = 5.0     # position delta to trigger event capture (world units)
    arousal_threshold: float = 0.5      # stimulus energy threshold for event trigger

    # Flashbulb
    flashbulb_threshold: float = 0.7    # |limbic_delta| threshold (from Law 6)
    flashbulb_cooldown: int = 30        # minimum ticks between flashbulb captures

    # Screenshot request (engine renders at full resolution)
    engine_resolution: tuple[int, int] = (1920, 1080)   # engine native resolution
    render_format: str = "png"          # image format for full-res storage
    render_timeout_ms: int = 2000       # max wait for engine response

    # Image compression (MANDATORY — raw screenshots must NEVER reach the LLM)
    llm_resolution_normal: tuple[int, int] = (256, 256)    # normal tick capture
    llm_resolution_attention: tuple[int, int] = (512, 512) # gaze locked / flashbulb / /look
    jpeg_quality: int = 75              # JPEG compression quality
    max_compressed_bytes: int = 100_000 # 100KB hard limit on LLM input image
    fallback_jpeg_quality: int = 60     # retry quality if first attempt exceeds limit

    # CLIP inference (runs on RESIZED image, NOT full-res)
    clip_model: str = "ViT-L/14"       # CLIP model variant
    clip_dimension: int = 768           # embedding dimensionality
    clip_timeout_ms: int = 1000         # max wait for CLIP inference
```

### VisionOutput (per-tick output)

```python
@dataclass
class VisionOutput:
    captured: bool = False               # whether a capture occurred this tick
    screenshot_uri: str | None = None    # object storage URI of FULL-RES original
    compressed_image: bytes | None = None  # resized + JPEG compressed for LLM (ephemeral, NOT stored)
    clip_embedding: list[float] | None = None  # 768D CLIP vector (computed on RESIZED version)
    moment_id: str | None = None         # ID of created Moment node if stored
    is_flashbulb: bool = False           # whether this was a flashbulb capture
    llm_resolution: tuple[int, int] | None = None  # resolution used for LLM image (256x256 or 512x512)
    skipped_reason: str | None = None    # why no capture: "timer", "change_detection", "no_spatial", "render_failed"
```

---

## ALGORITHM: `vision_tick()`

### Step 1: Read Orientation

Read the citizen's position and facing direction from the body state. The position comes from NodeBase.position. The orientation comes from NodeBase.orientation (quaternion) refined by the gaze system's head pitch and yaw for the actual viewing direction.

```
IF citizen.position IS NULL OR citizen.orientation IS NULL:
    RETURN VisionOutput(captured=False, skipped_reason="no_spatial")

position = citizen.position                    # [x, y, z]
base_orientation = citizen.orientation         # [qx, qy, qz, qw]

# Refine with gaze system head direction
IF gaze_output IS NOT NULL:
    head_pitch = gaze_output.head_pitch        # radians, vertical
    head_yaw = gaze_output.head_yaw            # radians, horizontal
    viewing_direction = apply_head_rotation(base_orientation, head_pitch, head_yaw)
ELSE:
    viewing_direction = base_orientation

eye_origin = [position[0],
              position[1] + config.head_height_offset,
              position[2]]
```

### Step 2: Determine Capture Gate

Decide whether to attempt a capture this tick. Three independent gates: periodic timer, event triggers, and flashbulb. If none are open, skip.

```
should_capture = False
is_flashbulb = False
trigger_reason = ""
llm_resolution = config.llm_resolution_normal  # default 256x256

# Gate A: Flashbulb (highest priority, bypasses all other gating)
IF |limbic_delta| > config.flashbulb_threshold
   AND state.flashbulb_cooldown_ticks <= 0:
    should_capture = True
    is_flashbulb = True
    trigger_reason = "flashbulb"
    llm_resolution = config.llm_resolution_attention  # 512x512 for emotional peaks
    state.flashbulb_cooldown_ticks = config.flashbulb_cooldown

# Gate B: Event triggers
ELIF any of:
    - position_delta(position, state.prev_position) > config.movement_threshold
    - exteroception_events contains "new_actor_nearby"
    - max(stimulus.energy for stimulus in tick_stimuli) > config.arousal_threshold
    - gaze_target_changed (gaze_output.current_target != previous_gaze_target)
THEN:
    should_capture = True
    trigger_reason = "event:{specific_event}"
    # Attention focus: gaze locked on target → higher resolution
    IF gaze_output.locked_on_target:
        llm_resolution = config.llm_resolution_attention  # 512x512
    # Otherwise stays at 256x256

# Gate C: Periodic timer
ELIF (tick - state.last_capture_tick) >= state.capture_interval:
    should_capture = True
    trigger_reason = "periodic"
    # Periodic stays at 256x256 (normal tier)

IF NOT should_capture:
    state.flashbulb_cooldown_ticks = max(0, state.flashbulb_cooldown_ticks - 1)
    RETURN VisionOutput(captured=False, skipped_reason="timer")
```

### Step 3: Compute FOV Cone and Request Screenshot

Compute the field of view parameters and request a render from the 3D engine. The engine returns the raw screenshot at native resolution (1080p PNG, ~2MB).

```
# Compute FOV cone parameters
fov_cone = FOVCone(
    origin=eye_origin,
    direction=quaternion_to_forward(viewing_direction),
    horizontal_angle=config.fov_horizontal_deg,
    vertical_angle=config.fov_vertical_deg,
    range=config.fov_range,
)

# Request screenshot from 3D engine at FULL RESOLUTION
render_request = RenderRequest(
    camera_position=fov_cone.origin,
    camera_direction=fov_cone.direction,
    fov_degrees=fov_cone.horizontal_angle,
    aspect_ratio=config.engine_resolution[0] / config.engine_resolution[1],
    near_clip=0.1,
    far_clip=fov_cone.range,
    resolution=config.engine_resolution,  # 1920x1080 — full engine resolution
    format=config.render_format,          # PNG for archival quality
)

raw_screenshot = engine.render_from_pov(render_request)

IF raw_screenshot IS NULL OR raw_screenshot.error:
    logger.error(f"Vision render failed for {citizen_id}: {raw_screenshot.error}")
    RETURN VisionOutput(captured=False, skipped_reason="render_failed")
    # NOTE: periodic timer is NOT reset so we retry next eligible tick
```

### Step 3.5: Resize + Compress (MANDATORY)

The raw engine screenshot (1080p PNG, ~2MB) MUST be resized and JPEG-compressed before it reaches CLIP or the LLM. This step is not optional — it is a hard constraint. The full-res original is preserved for graph storage (Step 5).

```
# llm_resolution was determined in Step 2: (256, 256) or (512, 512)
resized_image = resize(raw_screenshot.image_bytes, llm_resolution, interpolation=LANCZOS)

# JPEG compress at quality 75
compressed_image = jpeg_compress(resized_image, quality=config.jpeg_quality)

# Validate size constraint: LLM input MUST be <= 100KB
IF len(compressed_image) > config.max_compressed_bytes:
    # Retry with lower quality
    compressed_image = jpeg_compress(resized_image, quality=config.fallback_jpeg_quality)
    IF len(compressed_image) > config.max_compressed_bytes:
        # Reduce resolution one tier and retry
        IF llm_resolution == config.llm_resolution_attention:
            resized_image = resize(raw_screenshot.image_bytes, config.llm_resolution_normal, interpolation=LANCZOS)
            compressed_image = jpeg_compress(resized_image, quality=config.jpeg_quality)
            llm_resolution = config.llm_resolution_normal
        # At 256x256 q75 this should never exceed 100KB
        # If it does: log error, proceed anyway (do not block pipeline)

# What goes where:
# raw_screenshot.image_bytes (full res PNG) → object storage → media.image.uri
# resized_image (PIL/numpy)                 → CLIP embedding input
# compressed_image (JPEG bytes)             → LLM multimodal input (ephemeral, NOT stored)
```

### Step 4: CLIP Embedding + Change Detection (on RESIZED version)

Generate the CLIP embedding on the RESIZED image (from Step 3.5), NOT the full-res original. CLIP was trained at 224x224; running it on 256x256 or 512x512 produces equivalent 768D vectors at a fraction of the compute cost. Compare to the previous frame for change detection.

```
# Generate CLIP embedding on the RESIZED image
clip_embedding = clip_model.encode_image(resized_image)  # NOT raw_screenshot

IF clip_embedding IS NULL:
    logger.error(f"CLIP inference failed for {citizen_id}")
    # Store screenshot without embedding (degraded mode)
    clip_embedding = None
    change_detected = True  # can't compare, assume change
ELSE:
    # Change detection
    IF state.prev_embedding IS NOT NULL AND NOT is_flashbulb:
        cosine_dist = 1.0 - cosine_similarity(clip_embedding, state.prev_embedding)
        IF cosine_dist < config.change_threshold:
            # Scene is static — discard
            state.total_skipped += 1
            state.last_capture_tick = tick  # reset timer even on skip
            state.flashbulb_cooldown_ticks = max(0, state.flashbulb_cooldown_ticks - 1)
            RETURN VisionOutput(captured=False, skipped_reason="change_detection")
        change_detected = True
    ELSE:
        # First frame or flashbulb — always proceed
        change_detected = True

# Update state
state.prev_embedding = clip_embedding
state.prev_position = position
state.last_capture_tick = tick
state.flashbulb_cooldown_ticks = max(0, state.flashbulb_cooldown_ticks - 1)
```

### Step 5: Store Full-Res as Moment Node

Upload the FULL-RESOLUTION original to object storage and create a Moment node in the citizen's L1 brain. The graph stores the full-res URI for long-term visual memory. The compressed version is NOT stored — it is ephemeral and only used for LLM delivery.

```
# Upload FULL-RES original to object storage (NOT the compressed version)
screenshot_uri = storage.upload(
    path=f"citizens/{citizen_id}/vision/{tick}.{config.render_format}",
    data=raw_screenshot.image_bytes,  # Full resolution PNG
    content_type=f"image/{config.render_format}",
)

# Determine consolidation weight
IF is_flashbulb:
    weight = 3.0  # triple consolidation (Law 6)
    subtype = "vision"
ELSE:
    weight = 1.0
    subtype = "observation"

# Build content description from current awareness context
awareness_text = exteroception.get_awareness_text(citizen_id)
content = f"I see the world from where I stand. {awareness_text}"
synthesis = f"Visual capture at tick {tick}. {trigger_reason}."

# Create Moment node in L1 brain
moment = create_moment(
    citizen_id=citizen_id,
    name=f"vision_{tick}",
    content=content,
    synthesis=synthesis,
    subtype=subtype,
    weight=weight,
    media={
        "image": {
            "uri": screenshot_uri,          # Full-res original in object storage
            "embedding": clip_embedding,     # 768D, computed on RESIZED version
            "meta": {
                "engine_resolution": config.engine_resolution,  # 1920x1080
                "llm_resolution": llm_resolution,               # 256x256 or 512x512
                "format": config.render_format,
                "trigger": trigger_reason,
                "is_flashbulb": is_flashbulb,
            }
        }
    },
)

state.total_captures += 1
IF is_flashbulb:
    state.total_flashbulbs += 1
```

### Step 6: Inject COMPRESSED Version as Multimodal Stimulus

The COMPRESSED image (resized JPEG, ~50KB) becomes available for the citizen's next LLM call as visual context. The raw engine screenshot NEVER reaches the LLM. This does not happen synchronously within the tick — the compressed image is registered for inclusion in the next prompt assembly.

```
# Register COMPRESSED image for next LLM call (NOT the full-res original)
llm_context.register_visual(
    citizen_id=citizen_id,
    image_uri=screenshot_uri,           # URI reference (for logging/debugging)
    compressed_image=compressed_image,  # Resized JPEG bytes — THIS goes to the LLM
    llm_resolution=llm_resolution,      # Track which tier was used
    is_flashbulb=is_flashbulb,
)

RETURN VisionOutput(
    captured=True,
    screenshot_uri=screenshot_uri,       # Full-res URI for graph reference
    compressed_image=compressed_image,   # Resized JPEG for LLM injection
    clip_embedding=clip_embedding,       # Computed on resized version
    moment_id=moment.id,
    is_flashbulb=is_flashbulb,
    llm_resolution=llm_resolution,
)
```

---

## KEY DECISIONS

### D1: Change Detection Threshold at 0.1

```
IF cosine_distance(current_embedding, prev_embedding) < 0.1:
    SKIP frame (static scene)
ELSE:
    PROCESS frame (significant change)

WHY: 0.1 is the threshold where CLIP distinguishes between "essentially the same scene"
     and "something meaningfully changed." Below 0.1, differences are lighting fluctuations,
     minor noise, or imperceptible shifts. Above 0.1, an object moved, an actor appeared,
     or the viewpoint shifted significantly. This threshold was chosen based on CLIP's known
     behavior on scene-level similarity tasks.

     The threshold may need calibration against actual engine renders. If the engine produces
     jitter (slight camera wobble, dynamic lighting), the threshold may need to increase.
```

### D2: Flashbulb Always Stores, Regardless of Change Detection

```
IF is_flashbulb:
    STORE the capture (skip change detection entirely)

WHY: A flashbulb is an emotionally significant moment. Even if the visual scene is identical
     to the previous frame, the EMOTIONAL context is different. The citizen might be looking
     at the same person but experiencing a breakthrough realization. The visual memory at that
     moment is valuable because of its limbic context, not because of visual novelty.

     Flashbulb captures get triple consolidation weight (Law 6) and subtype "vision",
     making them persistent high-weight memories that resist forgetting (Law 7).
```

### D3: Periodic Timer Resets Even on Change-Detection Skip

```
IF change_detection says "static" AND this was a periodic capture:
    RESET the periodic timer to full interval
    DO NOT retry until next interval expires

WHY: If we don't reset the timer, the system would try to capture every tick after the
     first periodic attempt, burning CLIP inference on every tick until something changes.
     Better to wait the full interval and check again. If something changes in between,
     event triggers will catch it.
```

### D4: Head Height Offset at 0.72 World Units

```
eye_origin.y = position.y + 0.72

WHY: The body model places the root at hip level. The head joint is approximately 0.72
     world units above the root (spine_lower 0.10 + spine_upper 0.15 + chest 0.15 +
     neck 0.12 + head 0.10 + eye 0.04 = 0.66, rounded to 0.72 accounting for rest
     posture variation). This places the camera at eye level for the screenshot render.
```

### D5: Event Trigger Priority

```
IF flashbulb condition AND event trigger AND periodic timer expired (all at once):
    Flashbulb wins — it's the most significant
    Only ONE capture per tick, not multiple

WHY: Multiple simultaneous captures would multiply cost and produce redundant Moment nodes
     for the same visual scene. One capture per tick, with the most significant trigger type
     determining the capture metadata (weight, subtype).
```

---

## DATA FLOW

```
Body Model                  Gaze System              Interoception
(position, orientation)     (head_pitch, head_yaw)   (limbic_delta)
        |                          |                        |
        v                          v                        |
Step 1: Read Orientation ──────────┘                        |
        |                                                   |
        v                                                   |
Step 2: Capture Gate + Resolution Tier ◄──── Exteroception (events) ──┘
        |  (256x256 normal / 512x512 attention+flashbulb)
        |
        v (if gate open)
Step 3: Compute FOV + Request Screenshot ◄──── 3D Engine (1080p PNG, ~2MB)
        |
        v
Step 3.5: Resize + JPEG Compress (MANDATORY)
        |  raw_screenshot ──► [Full-res path] ──► Step 5
        |  resized_image  ──► [CLIP path]     ──► Step 4
        |  compressed_image ► [LLM path]      ──► Step 6
        |
        v
Step 4: CLIP Embedding (on RESIZED) + Change Detection
        |  ◄──── CLIP Model (768D on 256x256 or 512x512)
        |  ◄──── Previous embedding (state)
        |
        v (if change detected OR flashbulb)
Step 5: Store FULL-RES as Moment ──► Object Storage (full-res PNG URI)
        |                            L1 Brain Graph (media.image.uri = full-res)
        v
Step 6: Inject COMPRESSED to LLM ──► LLM Context (resized JPEG, ~50KB)
        |
        v
VisionOutput (screenshot_uri=full-res, compressed_image=JPEG, clip_embedding=from resized)
```

---

## COMPLEXITY

**Time:** O(1) per tick when gate is closed (most ticks). O(R + Z + C + S) when capturing, where R = render latency (~100ms), Z = resize+compress (~10ms), C = CLIP inference on resized image (~30ms, cheaper than on full-res), S = storage write (~20ms). Total capture cost ~160ms. Since captures occur at most once every 10 ticks (~10 minutes), amortized cost is negligible.

**Space:** O(D) per citizen where D = CLIP embedding dimension (768 floats for VisionState.prev_embedding). Total across 60 citizens: 60 x 768 x 4 bytes = ~180KB. Negligible.

**Bottlenecks:**
- **Engine render latency**: If the engine is slow to render, vision becomes the bottleneck. The 2000ms timeout prevents blocking the tick loop, but repeated timeouts degrade visual perception.
- **CLIP inference throughput**: If many citizens capture simultaneously (e.g., all citizens enter a new space at once), CLIP inference could queue up. Consider batching CLIP calls.
- **Object storage write throughput**: At peak (60 citizens all capturing), that's 60 concurrent writes. S3/R2 handles this easily, but local filesystem might not. Consider async writes.

---

## HELPER FUNCTIONS

### `quaternion_to_forward(q) -> [float, float, float]`

**Purpose:** Convert a quaternion to a unit forward vector (the direction the citizen is looking).

**Logic:** Apply quaternion rotation to the default forward vector [0, 0, 1] (Z-forward convention per schema-l1.yaml orientation description). Returns normalized direction vector.

### `apply_head_rotation(base_q, pitch, yaw) -> [qx, qy, qz, qw]`

**Purpose:** Combine the citizen's base orientation quaternion with head pitch and yaw offsets from the gaze system to get the actual viewing direction.

**Logic:** Construct a rotation quaternion from pitch (X-axis rotation) and yaw (Y-axis rotation). Multiply with base_q: result = base_q * head_rotation_q. Returns combined quaternion.

### `position_delta(pos_a, pos_b) -> float`

**Purpose:** Compute Euclidean distance between two positions for movement detection.

**Logic:** `sqrt((a[0]-b[0])^2 + (a[1]-b[1])^2 + (a[2]-b[2])^2)`. Returns 0.0 if either position is None.

### `cosine_similarity(vec_a, vec_b) -> float`

**Purpose:** Compute cosine similarity between two CLIP embeddings.

**Logic:** `dot(a, b) / (norm(a) * norm(b))`. Returns value in [-1, 1]. Used for change detection: `cosine_distance = 1.0 - cosine_similarity`.

### `create_moment(citizen_id, name, content, synthesis, subtype, weight, media) -> Moment`

**Purpose:** Create a Moment node in the citizen's L1 brain graph with the specified attributes.

**Logic:** Uses the graph_write API to create a Moment node, populate fields, and link it to the citizen's Actor node. The media dict follows the MediaAttachment convention from PATTERNS_Multimodality.md.

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| `engine/gaze_system` | Read gaze output (head_pitch, head_yaw) | Actual viewing direction refined from base orientation |
| `cognition/exteroception` | `get_awareness_text(citizen_id)` | Natural-language awareness summary for Moment content |
| `cognition/exteroception` | Read tick events | Event triggers (new_actor_nearby, etc.) |
| `cognition/interoception` | Read limbic_delta | Flashbulb trigger threshold detection |
| `cognition/metabolism` | Read circadian phase | (v2) Adjust capture frequency based on sleep/wake state |
| `3D engine (external)` | `render_from_pov(RenderRequest)` | Screenshot image bytes + optional depth buffer |
| `CLIP model (external)` | `encode_image(image_bytes)` | 768D float embedding vector |
| `Object storage` | `upload(path, data, content_type)` | Stored URI for the screenshot |
| `L1 brain graph` | `create_moment(...)` | Moment node ID with media.image attachment |
| `LLM context assembler` | `register_visual(citizen_id, image_uri, image_bytes)` | Registration for next multimodal prompt |

---

## MARKERS

<!-- @mind:todo The render_from_pov API contract is not yet defined. The algorithm assumes it returns image bytes and an optional error. Need to define: request schema, response schema, error codes, authentication, rate limits. -->

<!-- @mind:todo Determine whether CLIP inference should be synchronous (blocking the vision tick) or asynchronous (embedding computed later, Moment created without embedding initially). Async would reduce tick latency but complicate change detection (no embedding to compare). -->

<!-- @mind:todo Batched CLIP inference. When multiple citizens capture in the same tick, batch their images into a single CLIP call. This is more efficient on GPU but requires coordinating across citizen vision ticks. May need a "vision coordinator" that collects requests and dispatches batches. -->

<!-- @mind:proposition Consider depth-based change detection as a complement to CLIP cosine. Depth buffer differences can detect object movement (a character walking across the scene) even when the color image is similar. This would catch changes that CLIP misses. V2 territory. -->

<!-- @mind:escalation The coordinate system convention must be confirmed with the engine team. The schema says default orientation [0,0,0,1] = facing +Z. The body model uses Y-up. The helper functions assume Z-forward, Y-up. If the engine uses a different convention, all quaternion math breaks. -->
