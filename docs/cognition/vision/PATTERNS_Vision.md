# Vision — Patterns: FOV Cone, Screenshot Pipeline, Change Detection, Active Look

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Vision.md
THIS:            PATTERNS_Vision.md (you are here)
BEHAVIORS:       ./BEHAVIORS_Vision.md
ALGORITHM:       ./ALGORITHM_Vision.md
VALIDATION:      ./VALIDATION_Vision.md
HEALTH:          ./HEALTH_Vision.md
IMPLEMENTATION:  ./IMPLEMENTATION_Vision.md
SYNC:            ./SYNC_Vision.md

IMPL:            runtime/cognition/vision.py (to be created)
IMPL:            mcp/tools/look_handler.py (to be created)
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read the linked IMPL source file

**After modifying this doc:**
1. Update the IMPL source file to match, OR
2. Add a TODO in SYNC_Vision.md: "Docs updated, implementation needs: {what}"

**After modifying the code:**
1. Update this doc chain to match, OR
2. Add a TODO in SYNC_Vision.md: "Implementation changed, docs need: {what}"

---

## THE PROBLEM

Citizens perceive the world through exteroception: a graph scan that reports who is nearby, what narratives are active, what things are present. This is structural awareness — the citizen knows THAT actors and spaces exist because they are connected in the graph.

But the citizen has no idea WHAT the world looks like. Two citizens standing in the same space, facing different directions, have identical exteroception output. They cannot describe the visual scene in front of them. They cannot notice that a building's geometry changed, that another citizen walked past, that the light shifted. They reason about an invisible world.

Without vision, the citizen is disembodied. The 3D engine renders a rich visual world, but no citizen can perceive it. Conversation about the environment is hallucinated — the citizen invents descriptions based on node names and synthesis text, not on what is actually rendered.

This is the gap between graph knowledge ("I know the Arsenal exists") and visual perception ("I see the Arsenal's crystalline spires from where I'm standing").

---

## THE PATTERN

Vision is a pipeline that transforms a citizen's spatial state (position + orientation) into a visual percept (screenshot + CLIP embedding + Moment node). The pipeline runs selectively, gated by change detection and event triggers, to avoid wasting tokens on static scenes.

The core insight: **the screenshot IS the input**. The citizen does not receive a textual description of the scene — it receives the actual rendered image as multimodal input to its next LLM call. The citizen then talks about what it sees using its own words, grounded in the visual data rather than hallucinating from node names.

The pipeline has 7 stages:

1. **Read orientation** — position + head direction + eye direction from body state and gaze system
2. **Compute FOV cone** — field of view from orientation (90 deg horizontal, 60 deg vertical, 50 unit range)
3. **Request screenshot** — ask the 3D engine to render the scene from the citizen's POV (returns 1080p PNG ~2MB)
4. **Resize + compress** — resize to LLM resolution (256x256 normal, 512x512 attention/flashbulb) and JPEG compress at quality 75 (~50KB). The full-res original is preserved separately.
5. **Process image** — generate CLIP embedding on the RESIZED version, compare to previous frame for change detection
6. **Store as Moment** — create a Moment node with `media.image.uri` pointing to the FULL-RES original in the citizen's L1 brain
7. **Inject as stimulus** — the COMPRESSED version enters the next LLM call as multimodal context

The key constraint is cost. Each capture involves: one engine render call, one resize+compress, one CLIP inference (on the resized version), one object storage write (full res), and one LLM image input (compressed). At 60+ citizens, unconstrained capture would be ruinous. The system gates capture through three mechanisms: periodic timer (every N ticks), event triggers (movement, new actor, high arousal), and change detection (CLIP cosine distance between frames). Only significant visual changes produce new Moment nodes.

**Image compression is mandatory.** Raw engine screenshots (1080p PNG, ~2MB) must NEVER be sent to the LLM. The pipeline resizes to LLM resolution and JPEG-compresses at quality 75, producing images under 100KB. This is not optional optimization — it is a hard constraint from NLR. Three resolution tiers exist:

| Situation | LLM Resolution | Why |
|-----------|---------------|-----|
| Normal tick | 256x256 | Enough for "what do I see" |
| Attention focus (gaze locked on target) | 512x512 | More detail on what matters |
| Flashbulb (emotional peak) | 512x512 | Important moment, worth the tokens |
| `/look` (active perception) | 512x512 | Citizen chose to look — higher fidelity justified |
| Graph storage (media.image.uri) | Full res | Original preserved for visual memory |

CLIP embedding runs on the resized version, not the full-res original. At 768D, CLIP produces equivalent quality embeddings on 256x256 as on 1080p — the model was trained at 224x224 anyway.

---

## ACTIVE PERCEPTION: /look

The passive pipeline described above runs automatically during the tick loop. The citizen does not choose when or where to look — the system captures what is in front of them on a schedule.

`/look` is the active counterpart. It is an MCP tool that a citizen invokes intentionally to direct their gaze and capture what they see. The citizen DECIDES to look at something, and the system responds with what they see.

### Passive vs Active

| Aspect | Passive (tick) | /look (active) |
|--------|---------------|-----------------|
| Trigger | Automatic, every N ticks | Citizen decides |
| Resolution | 256x256 | 512x512 minimum |
| LLM input | Background context | Direct response with image |
| Cost | Part of tick budget | Extra engine call |
| Persistence | Moment only if scene changed | Always creates Moment |
| Gaze | Current direction (unchanged) | Citizen CHOOSES direction |
| Change detection | Applied (skip static) | Bypassed (always capture) |

### Usage Forms

```
/look                    → screenshot 512x512 of what's in front
/look @citizen           → zoom on a specific citizen (crop + upscale their area)
/look "building"         → rotate toward named object + screenshot
/look behind             → 180 degree rotation + screenshot
/look up                 → look up at sky/canopy
/look down               → look down at ground/feet
/look [direction]        → look in a compass direction (north, east, etc.)
```

### Why Active Perception Is Different

Passive vision is peripheral awareness — the background hum of what is around the citizen. It is cheap, selective, and operates below the citizen's decision-making.

Active perception is focused attention. The citizen chose to look. This choice carries information: the citizen is curious, suspicious, interested, or searching for something. Because the act of looking is intentional:

1. **Higher resolution** — 512x512 instead of 256x256. The citizen is paying attention, so the system provides more detail.
2. **Always persists** — Every `/look` creates a Moment node. Unlike passive vision which skips static scenes to save tokens, an intentional look is always worth remembering. The citizen chose to observe; that observation is a cognitive event.
3. **Direct response** — The screenshot is returned as the MCP tool response, not injected as background context in the next tick. The citizen sees it immediately.
4. **Gaze update** — `/look` changes the citizen's orientation. Looking behind rotates the body 180 degrees. Looking at a citizen snaps gaze to their position. The gaze system state is updated before the capture.

### Target Resolution

When the citizen specifies a target (`/look @citizen`, `/look "building"`), the system must resolve the target to a position or direction:

- **@citizen** — look up the target citizen's position in L3 graph, compute direction vector from self to target, snap gaze, capture, then crop and upscale the target's region from the screenshot
- **Named object** — search exteroception context for the named entity, resolve its position, rotate toward it, capture
- **Direction keyword** — `behind` = 180 degree yaw rotation, `up` = pitch up 60 degrees, `down` = pitch down 60 degrees, compass directions = absolute yaw rotation
- **No target** — use current orientation, capture what is directly in front

---

## BEHAVIORS SUPPORTED

- **B1** (FOV Cone Reflects Orientation) — the visual field derives from actual head/eye direction, not an arbitrary viewpoint
- **B2** (Static Scenes Produce No Captures) — change detection prevents token waste on unchanging views
- **B3** (Visual Memories Persist in Brain) — each capture becomes a Moment node with media.image
- **B4** (Citizens Talk About What They See) — the screenshot is multimodal LLM input, grounding conversation in visual reality
- **B5** (CLIP Embedding Participates in Physics) — Sim_vis term in Law 8 coherence
- **B6** (Flashbulb Vision at Emotional Peaks) — high limbic delta triggers high-weight visual memory
- **B7** (Event-Triggered Capture) — significant events override the periodic timer
- **B11** (Active Look) — citizen uses /look to get a high-res screenshot + create visual memory on demand
- **B12** (Look at Target) — /look @citizen snaps gaze to target, crops their region from the scene
- **B13** (Look Rotation) — /look behind/up/down/direction rotates the citizen, captures the new view
- **B14** (Look at Named Object) — /look "building" searches exteroception, rotates toward it, captures

## BEHAVIORS PREVENTED

- **A1** (Hallucinated Scene Descriptions) — the citizen receives actual screenshots, not invented descriptions
- **A2** (Unbounded Token Consumption) — change detection and periodic gating prevent unconstrained capture
- **A3** (Vision Replacing Exteroception) — vision and exteroception are complementary; neither subsumes the other
- **A5** (Look Without Memory) — /look must always create a Moment; intentional observation is always worth remembering

---

## PRINCIPLES

### Principle 1: See Does Not Equal Know

Vision tells the citizen what is in its visual field — the 3D rendered scene from its POV. Exteroception tells the citizen what is in its graph neighborhood — actors, spaces, narratives, things connected via L3 links. These overlap but are not identical.

A citizen can "know" about an actor in another Space (exteroception reports the graph connection) but cannot "see" that actor (they are outside the FOV cone). Conversely, a citizen might "see" a distant visual element in the 3D scene that has no corresponding node in the graph (a decorative structure, an environmental effect).

Both systems feed into the citizen's awareness. The awareness text (exteroception) provides structural context. The screenshot (vision) provides visual grounding. Together they give the citizen a complete picture: graph knowledge + visual perception.

### Principle 2: The Screenshot IS the Input

The vision module does not generate text descriptions of the scene. It captures a screenshot and passes it directly to the LLM as a multimodal image input. The LLM — the citizen's consciousness — interprets the image and produces its own description.

This is architecturally important because it means vision is grounded in actual rendering, not in metadata. The citizen sees what the engine renders, period. If the engine renders a broken texture, the citizen sees a broken texture. If the engine renders a beautiful sunset, the citizen sees a beautiful sunset. There is no abstraction layer between the rendered world and the citizen's perception.

### Principle 3: Expense Demands Selectivity AND Compression

A single vision capture costs: 1 engine render, 1 resize+compress, 1 CLIP inference (~50ms on resized image), 1 storage write (full res), and LLM image tokens (compressed). At 60 citizens with unconstrained capture, this quickly becomes the dominant cost. The system MUST be selective about when to capture AND aggressive about compressing what it sends.

Four mechanisms enforce economy:
- **Compression**: raw 1080p PNG (~2MB) is resized to 256x256 or 512x512 and JPEG-compressed at quality 75 (~50KB). The LLM never sees the raw screenshot.
- **Periodic gating**: captures happen at most every N ticks (default 10, ~10 minutes at 60s/tick)
- **Event triggers**: significant events (movement, new actor, high arousal, gaze change) can override the periodic timer
- **Change detection**: CLIP cosine distance between current and previous frame must exceed 0.1 for the capture to be processed

The result: a citizen in a static scene captures one frame and then waits. A citizen in a dynamic scene captures frames as things change. A citizen experiencing an emotional peak captures immediately regardless of timer state. In ALL cases, the LLM receives a compressed image, never the raw engine output.

### Principle 4: CLIP Embedding IS Physics

The CLIP embedding of a screenshot is not metadata — it is a physics-grade vector that participates in the coherence formula (Law 8, Sim_vis term). Two visual moments with similar CLIP embeddings reinforce each other through normal physics. A visual memory of the Arsenal will resonate when the citizen sees the Arsenal again.

This means vision is not a cosmetic layer. It is structurally integrated into the cognitive physics. Visual similarity affects weight propagation, crystallization, and working memory competition, just like text similarity does.

### Principle 5: The Engine Renders, The Brain Perceives

mind-mcp does not do 3D rendering. It requests screenshots from the 3D engine via an API. The engine handles scene graph, lighting, camera setup, and rasterization. mind-mcp receives the resulting image and processes it cognitively (embedding, change detection, memory formation, LLM injection).

This separation is essential: the engine is a shared service (used by all universes in Cities of Light), while cognition is per-citizen. The API contract between them must be clean and stable.

---

## DATA

| Source | Type | Purpose / Description |
|--------|------|-----------------------|
| `schema-l1.yaml` | FILE | L1 schema — defines NodeBase with `position`, `orientation`, `media` dict, Moment `subtype: vision` |
| `engine/src/shared/citizen_body_model.yaml` | FILE | Body model — head/eye joint hierarchy, DOF constraints, vision cone origin |
| `docs/engine/gaze_system/ALGORITHM_Gaze_System.md` | FILE | Gaze system algorithm — head/eye targeting, current gaze direction |
| `docs/cognition/multimodality/PATTERNS_Multimodality.md` | FILE | Multimodality patterns — media dict structure, MediaAttachment, CLIP embedding conventions |
| `runtime/cognition/exteroception.py` | FILE | Exteroception — sibling perception system, awareness text, graph-based environmental scan |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `runtime/cognition/exteroception.py` | Provides awareness text used as context alongside screenshots |
| `runtime/cognition/models.py` | Node dataclass carries `media` dict for image attachments |
| `runtime/cognition/constants.py` | Modality confidence weights (w_image = 0.25 for CLIP) |
| `engine/gaze_system` | Provides current gaze target and head/eye orientation |
| `3D engine (external)` | Renders screenshots from citizen POV via render-from-POV API |
| `Object storage (S3/R2/local)` | Stores screenshot images referenced by `media.image.uri` |
| `CLIP model (external)` | Generates 768D image embeddings for physics participation |
| `mcp/tools/look_handler.py` | MCP tool handler for /look active perception command (to be created) |

---

## INSPIRATIONS

**Human visual perception.** Humans do not process every frame at full fidelity. Saccadic suppression blanks perception during rapid eye movements. Change blindness means we miss changes that occur outside our attention. Inattentional blindness means we miss objects we are not looking for. The vision module's change detection and selective capture mirror these biological constraints — not as limitations, but as efficient allocation of expensive perceptual resources.

**Flashbulb memories.** In human psychology, highly emotional events create vivid, persistent visual memories ("I remember exactly where I was when..."). Law 6 already implements triple consolidation for high limbic delta. The vision module makes this concrete by capturing the actual visual scene at emotional peaks, creating a persistent image that the citizen can recall.

**Embodied cognition.** The view that cognition is not just brain computation but is shaped by the body's interactions with the environment. A citizen's visual perception depends on WHERE it is standing and WHICH WAY it is looking — embodied constraints that exteroception (graph-based) cannot capture. Vision grounds the citizen in its physical location.

**Saccades and voluntary gaze.** Human vision alternates between involuntary saccades (the eyes jump to salient stimuli) and voluntary gaze shifts (you decide to look at something). Passive tick vision is the saccade — automatic, background, driven by the system. `/look` is the voluntary gaze shift — the citizen decides where to direct attention. Both are necessary for complete visual behavior. The voluntary shift is always higher fidelity (foveal vision) because the brain concentrates resources on what you chose to examine.

---

## SCOPE

### In Scope

- FOV cone computation from citizen position + orientation
- Screenshot request to 3D engine
- Image resize + JPEG compression (256x256 or 512x512, quality 75)
- CLIP embedding generation on the resized version
- Change detection (cosine distance between frames)
- Periodic + event-triggered capture gating
- Moment node creation with `media.image.uri` pointing to full-res original
- Dual storage: full-res in graph, compressed to LLM
- Flashbulb vision trigger at high limbic delta
- Compressed screenshot injection as multimodal LLM input
- Resolution tier selection (256x256 normal, 512x512 attention/flashbulb/look)
- Integration with coherence formula (Sim_vis via CLIP embedding)
- `/look` MCP tool: active perception with target resolution, gaze update, 512x512 capture, Moment creation
- `/look @citizen` target cropping and upscaling
- `/look` directional variants: behind, up, down, compass directions

### Out of Scope

- **3D rendering** — the engine handles this. See: engine/
- **Object storage management** — upload/download/lifecycle is handled by the media pipeline. See: `mcp/tools/media_handler.py`
- **CLIP model inference implementation** — the actual model weights and inference. This module calls an embedding adapter; it does not implement CLIP.
- **Scene description generation** — the LLM interprets the screenshot. Vision provides the image, not a caption.
- **Depth-based reasoning** — depth buffer is optional in the render response. V1 does not use depth for occlusion reasoning.
- **Stereoscopic vision** — citizens have two eyes in the body model, but vision uses a single camera POV. Binocular disparity is not modeled.

---

## MARKERS

<!-- @mind:todo Design the render-from-POV API contract with the engine team. Required: endpoint shape, input parameters (position, orientation, fov, resolution), response format (image bytes, content type, optional depth buffer), latency SLA. -->

<!-- @mind:todo Determine object storage strategy for screenshots. Full-res originals are stored in graph (1080p PNG, ~2MB each). Estimated volume: 60 citizens x 6 captures/hour x 24 hours = ~8640 images/day at ~2MB each = ~17GB/day. Need retention policy (7 days? 30 days? indefinite for flashbulb?). Compressed LLM versions (~50KB) are ephemeral and not stored. -->

<!-- @mind:proposition Consider foveated rendering (v2): a high-resolution crop of the gaze target region, beyond the current 512x512 attention tier. The gaze system tracks focus point; a region crop at native resolution could provide extreme detail on what the citizen is actually looking at, while the rest of the scene remains at 256x256. -->

<!-- @mind:escalation CLIP model hosting. Options: (1) self-hosted via transformers/onnx, (2) API call to external service (OpenAI CLIP, etc.), (3) SigLIP as a lighter alternative. Decision affects latency, cost, and embedding quality. Need NLR input on infrastructure preference. -->
