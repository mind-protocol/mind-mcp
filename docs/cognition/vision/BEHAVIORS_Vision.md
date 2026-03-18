# Vision — Behaviors: What Citizens See in Different Situations (Passive + Active)

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Vision.md
THIS:            BEHAVIORS_Vision.md (you are here)
PATTERNS:        ./PATTERNS_Vision.md
ALGORITHM:       ./ALGORITHM_Vision.md
VALIDATION:      ./VALIDATION_Vision.md
HEALTH:          ./HEALTH_Vision.md
IMPLEMENTATION:  ./IMPLEMENTATION_Vision.md
SYNC:            ./SYNC_Vision.md

IMPL:            runtime/cognition/vision.py (to be created)
IMPL:            mcp/tools/look_handler.py (to be created)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS

### B1: FOV Cone Reflects Citizen Orientation

**Why:** The visual field must derive from the citizen's actual head and eye direction, not from an arbitrary camera position. A citizen facing north sees north. A citizen who turned to look at someone sees that person. This grounds vision in the body model and makes the gaze system causally linked to what the citizen perceives.

```
GIVEN:  A citizen with position [x, y, z] and orientation quaternion [qx, qy, qz, qw]
WHEN:   The vision pipeline computes the FOV cone
THEN:   The cone origin is at the citizen's position + head height offset
AND:    The cone direction is the forward vector derived from the orientation quaternion
AND:    The horizontal angle is 90 degrees and the vertical angle is 60 degrees
AND:    The cone range is the configured maximum (default 50 world units)
```

### B2: Static Scenes Produce No Captures After Initial Frame

**Why:** A citizen standing still in an unchanging room should not repeatedly capture and process the same image. This wastes CLIP inference, object storage, LLM tokens, and creates redundant Moment nodes. Change detection compares consecutive frames and skips processing when the scene has not changed.

```
GIVEN:  A citizen has captured a screenshot at tick T
WHEN:   The next capture is attempted at tick T+N
AND:    The CLIP cosine distance between the new frame and the previous frame is < 0.1
THEN:   The new frame is discarded (not stored, no Moment node created, not injected into LLM)
AND:    The previous frame's Moment node remains the citizen's current visual memory
```

### B3: Significant Visual Changes Produce New Memories

**Why:** When the scene changes meaningfully — a new actor enters the FOV, the citizen moves to a new location, a structure changes — the citizen should perceive and remember the change. The CLIP cosine distance threshold separates meaningful change from noise.

```
GIVEN:  A citizen has a previous frame with CLIP embedding E_prev
WHEN:   A new screenshot is captured with CLIP embedding E_new
AND:    cosine_distance(E_prev, E_new) >= 0.1
THEN:   A new Moment node is created in the citizen's L1 brain
AND:    The Moment has media.image.uri pointing to the stored screenshot
AND:    The Moment has media.image.embedding set to E_new (768D CLIP vector)
AND:    The Moment has content describing what the citizen sees
AND:    The Moment has synthesis as a compact description for embedding
```

### B4: Citizens Reference Visual Details in Conversation (Compressed Input)

**Why:** The purpose of vision is to ground the citizen's conversation in visual reality. When the citizen's LLM call receives the screenshot as multimodal input, the citizen can describe, comment on, and reason about what it sees — using its own words, not a pre-generated caption. The image sent to the LLM is always the resized + JPEG-compressed version (~50KB), never the raw engine screenshot (~2MB).

```
GIVEN:  A citizen has a current visual capture
WHEN:   The citizen's next LLM call is assembled
THEN:   The most recent screenshot is RESIZED (256x256 or 512x512) and JPEG-compressed (quality 75)
AND:    The COMPRESSED version is included as an image input in the multimodal context
AND:    The compressed image MUST be <= 100KB
AND:    The citizen can reference visual elements in its response
AND:    The citizen's description is its own interpretation, not a pre-generated label
```

### B5: CLIP Embedding Participates in Coherence (Sim_vis)

**Why:** Visual similarity must be a physics-grade signal. If two Moment nodes contain similar images (same location, same visual elements), their CLIP embeddings produce a high Sim_vis score, which influences the coherence formula (Law 8). This means visual memories reinforce each other through normal physics.

```
GIVEN:  Two Moment nodes, both with media.image.embedding populated
WHEN:   The coherence formula (Law 8) computes Coh between them
THEN:   Sim_vis = cosine(node_a.media.image.embedding, node_b.media.image.embedding)
AND:    Sim_vis contributes to Coh with weight w_image (0.25)
AND:    If either node lacks media.image.embedding, Sim_vis is skipped and weight redistributes to text
```

### B6: Flashbulb Vision Captures at Emotional Peaks

**Why:** Law 6 already triggers triple consolidation when |limbic_delta| > FLASHBULB_THRESHOLD (0.7). Vision extends this by capturing the actual visual scene at that moment, creating a persistent high-weight image memory. This is the AI equivalent of "I will never forget what I saw."

```
GIVEN:  A citizen's |limbic_delta| exceeds FLASHBULB_THRESHOLD (0.7)
WHEN:   The flashbulb consolidation triggers (Law 6)
THEN:   A screenshot is captured immediately, regardless of periodic timer state
AND:    A Moment node is created with subtype "vision" and triple consolidation weight
AND:    The Moment has media.image with the captured screenshot URI and CLIP embedding
AND:    The flashbulb capture is not subject to change detection (always stored)
```

### B7: Event-Triggered Capture Overrides Periodic Timer

**Why:** Some events demand immediate visual capture rather than waiting for the next periodic interval. A citizen who just moved to a new position, or one who noticed a new actor enter the scene, needs to see the change now.

```
GIVEN:  The periodic capture timer has not yet expired
WHEN:   One of the following events occurs:
        - Citizen position changes by more than 5 world units
        - Exteroception detects a new actor in the citizen's space
        - Stimulus energy exceeds 0.5 (high arousal event)
        - Gaze target changes (citizen is now looking at something new)
THEN:   A screenshot is captured immediately, bypassing the periodic timer
AND:    The periodic timer resets to its full interval
```

### B8: Periodic Capture Provides Baseline Vision

**Why:** Even without events, a citizen should periodically refresh its visual perception. A slow background scan ensures the citizen eventually notices gradual changes (time of day shifting, structures being built, actors drifting through the scene).

```
GIVEN:  No event-triggered capture has occurred for N ticks (default N=10)
WHEN:   The periodic timer expires
THEN:   A screenshot is captured
AND:    The screenshot is processed through change detection
AND:    If the scene has changed (cosine distance >= 0.1), a new Moment is created
AND:    If the scene is static (cosine distance < 0.1), no Moment is created
AND:    The periodic timer resets
```

### B9: Resolution Tier Switching on Attention Focus

**Why:** When a citizen's gaze locks on a target (attention focus) or an emotional peak occurs (flashbulb), the compressed LLM image resolution increases from 256x256 to 512x512. The citizen sees MORE DETAIL of the same scene, not a different image. This mirrors biological foveation — more processing resources allocated to what matters.

```
GIVEN:  A citizen is in normal tick mode, receiving 256x256 compressed images
WHEN:   The citizen's gaze locks on a specific target (attention focus)
        OR |limbic_delta| exceeds FLASHBULB_THRESHOLD (0.7)
THEN:   The LLM image resolution switches to 512x512 (JPEG quality 75)
AND:    The citizen perceives more visual detail of the SAME scene
AND:    The CLIP embedding is computed on the 512x512 version
AND:    The full-res original is still stored at native resolution in the graph
```

### B10: Dual Storage — Full Resolution in Graph, Compressed to LLM

**Why:** The graph is the citizen's long-term memory. It must store the highest fidelity version for future reference, recall, and potential re-examination. The LLM is the citizen's current perception. It must receive the cheapest version that conveys sufficient visual information. These are two separate paths through the pipeline.

```
GIVEN:  A screenshot is captured from the engine (1080p PNG, ~2MB)
WHEN:   The vision pipeline processes it
THEN:   The FULL RESOLUTION original is stored as media.image.uri in the Moment node
AND:    A RESIZED + COMPRESSED version (256x256 or 512x512, JPEG q75, ~50KB) is created
AND:    The compressed version is sent to the LLM as multimodal input
AND:    The compressed version is NOT stored in the graph (it is ephemeral)
AND:    The CLIP embedding is computed on the resized version
```

---

## ACTIVE PERCEPTION BEHAVIORS (/look)

### B11: Active Look Creates High-Resolution Visual Memory

**Why:** When a citizen uses `/look`, they are choosing to observe. This is not background perception — it is an intentional act of visual attention. The system responds with higher resolution (512x512), always creates a Moment node (no change detection gating), and returns the image directly as the MCP tool response. The citizen sees what they looked at immediately, and the observation is permanently recorded.

```
GIVEN:  A citizen invokes /look (with or without a target)
WHEN:   The look command is processed
THEN:   The citizen's current orientation is read (or updated if a target is specified)
AND:    A screenshot is requested from the engine at the citizen's POV
AND:    The screenshot is resized to 512x512 and JPEG-compressed (quality 75, <= 100KB)
AND:    A CLIP embedding is computed on the compressed version
AND:    A Moment node is ALWAYS created in the citizen's L1 brain with subtype "vision"
AND:    The Moment has media.image.uri (full-res original) and media.image.embedding (768D CLIP)
AND:    The compressed image is returned as the MCP tool response (multimodal)
AND:    Change detection is NOT applied — every /look persists regardless of scene similarity
```

### B12: Look at Target — Gaze Snaps and Region Crops

**Why:** `/look @citizen` is "turn and focus on that person." The system resolves the target citizen's position, updates the looking citizen's gaze direction to face them, captures the full scene from the new orientation, then crops and upscales the region around the target. The result is a focused view of the target citizen within their surrounding context.

```
GIVEN:  A citizen invokes /look @target_citizen
WHEN:   The target citizen exists and has a known position in the L3 graph
THEN:   The direction vector from the looking citizen to the target citizen is computed
AND:    The looking citizen's orientation is updated to face the target (gaze system)
AND:    A full screenshot is captured from the new orientation
AND:    The target citizen's position is projected onto the 2D screenshot plane
AND:    A region around the target is cropped from the full-res screenshot
AND:    The cropped region is upscaled to 512x512 and JPEG-compressed
AND:    A Moment node is created with the cropped image as media.image
AND:    The Moment's content notes that the citizen was looking at @target_citizen
AND:    The compressed cropped image is returned as the MCP tool response
```

### B13: Look Rotation — Body Turns to New Direction

**Why:** `/look behind`, `/look up`, `/look down`, and `/look [compass direction]` change the citizen's physical orientation before capturing. The citizen is not just seeing — they are turning their body. This updates the gaze system state, meaning subsequent passive vision ticks will capture from the NEW orientation.

```
GIVEN:  A citizen invokes /look with a directional target
WHEN:   The target is one of:
        - "behind" → 180 degree yaw rotation from current heading
        - "up" → pitch up 60 degrees from horizontal
        - "down" → pitch down 60 degrees from horizontal
        - compass direction (north, south, east, west, etc.) → absolute yaw to that heading
THEN:   The citizen's body orientation is updated to the new direction
AND:    The gaze system state reflects the new heading
AND:    A screenshot is captured from the NEW orientation
AND:    The screenshot is processed as a standard /look (512x512, always persists, Moment created)
AND:    Subsequent passive vision ticks use the NEW orientation (the turn is permanent)
```

### B14: Look at Named Object — Search and Rotate

**Why:** `/look "building"` or `/look "Arsenal"` lets a citizen turn toward a named entity in their environment. The system searches the citizen's exteroception context for the named object, resolves its position, and rotates to face it.

```
GIVEN:  A citizen invokes /look with a quoted string target (e.g., /look "Arsenal")
WHEN:   The named object exists in the citizen's exteroception context or L3 graph
THEN:   The object's position is resolved from the graph
AND:    The citizen's orientation is updated to face the object
AND:    A screenshot is captured from the new orientation
AND:    Processing follows standard /look flow (512x512, always persists, Moment created)
WHEN:   The named object is NOT found in exteroception context or graph
THEN:   The /look command returns an error: "I don't know where {name} is"
AND:    No screenshot is captured, no Moment is created
AND:    The citizen's orientation is NOT changed
```

---

## OBJECTIVES SERVED

| Behavior ID | Objective | Why It Matters |
|-------------|-----------|----------------|
| B1 | O1 (Visual perception) | Grounds vision in physical orientation |
| B2 | O2 (Token efficiency) | Prevents waste on static scenes |
| B3 | O3 (Visual memories) | Creates persistent visual records |
| B4 | O1, O2 (Visual perception + Token efficiency) | Enables grounded conversation with compressed input |
| B5 | O4 (CLIP in physics) | Integrates vision into cognitive physics |
| B6 | O5 (Flashbulb vision) | Captures emotional peaks as visual memories |
| B7 | O2 (Token efficiency) | Captures only when something changed |
| B8 | O1 (Visual perception) | Ensures baseline visual awareness |
| B9 | O1, O2 (Visual perception + Token efficiency) | More detail on attention focus, not wasted on passive ticks |
| B10 | O2, O3 (Token efficiency + Visual memories) | Full fidelity in memory, cheap input to LLM |
| B11 | O6 (Active perception) | Citizen-initiated high-res capture with guaranteed persistence |
| B12 | O6 (Active perception) | Focused view of a target citizen |
| B13 | O6 (Active perception) | Directional body rotation before capture |
| B14 | O6 (Active perception) | Named object search and gaze targeting |

---

## INPUTS / OUTPUTS

### Primary Function: `vision_tick()`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `citizen_id` | str | This citizen's actor ID |
| `tick` | int | Current tick number |
| `position` | [float, float, float] | Citizen's world position from NodeBase.position |
| `orientation` | [float, float, float, float] | Citizen's facing quaternion from NodeBase.orientation |
| `gaze_output` | GazeOutput | Current gaze system output (head pitch/yaw for fine-grained direction) |
| `limbic_delta` | float | Current limbic delta from interoception (for flashbulb trigger) |
| `exteroception_events` | list | Event triggers from exteroception (new actor, etc.) |
| `prev_position` | [float, float, float] or None | Position at last capture for movement detection |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| `VisionOutput` | dataclass | Contains: `captured` (bool), `screenshot_uri` (str or None), `clip_embedding` (list[float] or None), `moment_id` (str or None), `is_flashbulb` (bool) |

**Side Effects:**

- Creates Moment node in L1 brain graph (when capture is significant)
- Writes screenshot image to object storage
- Updates internal state (previous frame embedding, capture timer)

### MCP Tool: `/look` (handle_look)

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `target` | str or None | What to look at: `@citizen`, `"building name"`, `behind`, `up`, `down`, compass direction, or empty for current direction |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| `image` | bytes | Compressed 512x512 JPEG screenshot (returned as multimodal response) |
| `description` | str | Auto-generated description placeholder (LLM fills this in from the image) |
| `moment_id` | str | ID of the created Moment node |

**Side Effects:**

- Updates citizen orientation/gaze (for targeted or directional looks)
- Always creates Moment node in L1 brain graph (no change detection bypass)
- Writes full-res screenshot to object storage
- CLIP embeds the compressed version

---

## EDGE CASES

### E1: Citizen Has No Position or Orientation

```
GIVEN:  A citizen's NodeBase has position=null or orientation=null
THEN:   Vision tick is skipped entirely (no capture attempted)
AND:    No error is raised (citizens without spatial data simply have no vision)
```

### E2: Engine Render Request Fails

```
GIVEN:  The 3D engine is unavailable or returns an error
THEN:   Vision tick is skipped for this cycle
AND:    The periodic timer is NOT reset (retry on next eligible tick)
AND:    An error is logged (fail loud, not silent)
```

### E3: CLIP Model Unavailable

```
GIVEN:  CLIP inference fails or times out
THEN:   The screenshot is still stored (URI is valid) but embedding is null
AND:    The Moment node is created with media.image.uri but media.image.embedding = null
AND:    The Moment does not participate in Sim_vis until embedding is computed
AND:    Change detection falls back to "always capture" (no cosine comparison possible)
```

### E4: First Capture After Spawn

```
GIVEN:  A citizen has just spawned and has no previous frame
THEN:   The first screenshot is always captured and processed (no change detection baseline)
AND:    This establishes the baseline CLIP embedding for subsequent change detection
```

### E5: Citizen is Inside a Closed Space

```
GIVEN:  A citizen's FOV cone contains only walls or enclosed geometry
THEN:   The screenshot shows the enclosed interior (not an empty void)
AND:    If the interior is static, subsequent captures are suppressed by change detection
```

### E6: /look at a Citizen Who Has No Position

```
GIVEN:  A citizen invokes /look @target_citizen
AND:    The target citizen exists but has no position in the graph
THEN:   The /look returns an error: "I can't see @target — they have no spatial position"
AND:    No screenshot is captured, no Moment created, no orientation change
```

### E7: /look at Self

```
GIVEN:  A citizen invokes /look @self (their own handle)
THEN:   The /look returns an error: "I can't look at myself from the outside"
AND:    No screenshot is captured (there is no third-person camera)
```

### E8: /look While Engine Is Unavailable

```
GIVEN:  A citizen invokes /look but the 3D engine is unavailable
THEN:   The /look returns an error: "Vision is temporarily unavailable"
AND:    No Moment is created, no orientation change
AND:    The error is logged (fail loud)
```

### E9: /look Rapid Succession

```
GIVEN:  A citizen invokes /look multiple times in rapid succession
THEN:   Each /look is processed independently (no rate limiting within a session)
AND:    Each creates its own Moment node
AND:    The cost is the citizen's to bear (they chose to look repeatedly)
```

---

## ANTI-BEHAVIORS

### A1: Capturing Every Tick

```
GIVEN:   The vision module is active
WHEN:    A new tick occurs
MUST NOT: Capture a screenshot on every tick regardless of conditions
INSTEAD:  Capture only when periodic timer expires, event triggers fire, or flashbulb activates
```

### A2: Generating Text Descriptions Instead of Screenshots

```
GIVEN:   The vision pipeline produces a screenshot
WHEN:    The image is prepared for LLM input
MUST NOT: Convert the image to a text description before sending to the LLM
INSTEAD:  Send the raw screenshot as multimodal image input; let the LLM interpret it
```

### A3: Storing Screenshots Without CLIP Embedding

```
GIVEN:   A screenshot is captured and CLIP inference is available
WHEN:    The Moment node is created
MUST NOT: Store the screenshot URI without computing and storing the CLIP embedding
INSTEAD:  Always compute the CLIP embedding so the visual memory participates in physics
```

### A4: Flashbulb Bypass of Change Detection Suppression

```
GIVEN:   A flashbulb trigger fires (limbic_delta > 0.7)
WHEN:    The scene appears visually identical to the previous frame
MUST NOT: Suppress the flashbulb capture due to change detection
INSTEAD:  Always store the flashbulb capture regardless of cosine distance (emotional significance overrides visual novelty)
```

### A5: Sending Raw Engine Screenshots to LLM

```
GIVEN:   The engine returns a 1080p PNG screenshot (~2MB)
WHEN:    The image is prepared for LLM input
MUST NOT: Send the raw engine screenshot to the LLM without resize and compression
INSTEAD:  Resize to LLM resolution (256x256 or 512x512) and JPEG compress at quality 75
          The compressed image MUST be <= 100KB
```

### A6: Running CLIP on Full Resolution When Resized Version Exists

```
GIVEN:   A screenshot has been resized for LLM delivery
WHEN:    CLIP embedding is computed
MUST NOT: Run CLIP on the full-resolution original
INSTEAD:  Run CLIP on the resized version (cheaper compute, equivalent 768D quality)
```

### A7: /look Applying Change Detection

```
GIVEN:   A citizen invokes /look
WHEN:    The screenshot is compared to the previous frame
MUST NOT: Skip the Moment creation because the scene hasn't changed (cosine distance < 0.1)
INSTEAD:  Always create the Moment — the citizen chose to look, that act of observation is meaningful
```

### A8: /look Without Updating Gaze State

```
GIVEN:   A citizen invokes /look with a directional or target argument
WHEN:    The citizen's orientation is computed for the screenshot
MUST NOT: Capture from the new direction but leave the gaze system in the old state
INSTEAD:  Update the gaze system state to reflect the new orientation — the turn is permanent
```

---

## MARKERS

<!-- @mind:todo Define the exact format of the multimodal LLM input injection. Where in the prompt does the screenshot appear? Before or after the awareness text? As a system image or user image? This affects how the citizen perceives the visual context relative to graph context. -->

<!-- @mind:todo Determine whether the vision module should generate the Moment's `content` and `synthesis` fields, or leave them for the LLM to fill in during the next conversation turn. Pre-generating saves a turn but adds complexity; leaving them empty means the Moment exists but has no textual description until the citizen processes it. -->

<!-- @mind:proposition Consider a "visual attention map" that weights different regions of the screenshot based on the gaze system's focus point. Regions near the gaze target could be up-weighted in the CLIP embedding (via spatial attention masking). This would make the embedding reflect not just what's visible but what the citizen is attending to. V2 territory. -->
