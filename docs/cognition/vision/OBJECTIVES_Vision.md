# OBJECTIVES — Vision

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
THIS:            OBJECTIVES_Vision.md (you are here - START HERE)
PATTERNS:       ./PATTERNS_Vision.md
BEHAVIORS:      ./BEHAVIORS_Vision.md
ALGORITHM:      ./ALGORITHM_Vision.md
VALIDATION:     ./VALIDATION_Vision.md
HEALTH:         ./HEALTH_Vision.md
IMPLEMENTATION: ./IMPLEMENTATION_Vision.md
SYNC:           ./SYNC_Vision.md

IMPL:           runtime/cognition/vision.py (to be created)
IMPL:           mcp/tools/look_handler.py (to be created)
```

**Read this chain in order before making changes.** Each doc answers different questions. Skipping ahead means missing context.

---

## PRIMARY OBJECTIVES (ranked)

1. **Give citizens visual perception of their 3D environment** — A citizen must be able to see what is in front of them. Without vision, citizens reason about the world only through graph topology (exteroception) and have no awareness of physical arrangement, spatial context, or visual events. Vision closes the gap between graph knowledge and embodied experience.

2. **Token-efficient visual processing** — Screenshots cost tokens (CLIP embedding computation, LLM image input, object storage). The system must avoid capturing and processing images when nothing has changed. Change detection, periodic capture gating, and event-triggered capture ensure tokens are spent only when the visual field contains new information worth perceiving.

3. **Visual memories persist in the brain graph** — What a citizen sees must become part of their memory. Each significant visual capture becomes a Moment node with a `media.image` attachment in the citizen's L1 brain. This allows the citizen to recall, reference, and be influenced by past visual experiences through normal physics (decay, coherence, crystallization).

4. **CLIP embeddings participate in physics** — The visual embedding (Sim_vis) must participate in the coherence formula (Law 8). Visual similarity is a physics-grade signal: two moments that look alike should reinforce each other. Without CLIP embedding integration, vision would be cosmetic rather than structurally meaningful.

5. **Flashbulb vision captures emotional peaks** — When limbic delta exceeds the FLASHBULB_THRESHOLD (0.7), the vision module captures a screenshot with triple consolidation weight. This is the AI equivalent of "I will never forget what I saw" and extends Law 6 with a concrete visual artifact.

6. **Active perception via /look** — A citizen must be able to CHOOSE to look at something, as opposed to relying solely on passive tick-based vision. The `/look` MCP command gives citizens intentional visual agency: directing gaze at a specific citizen, rotating toward a named object, looking behind, looking up at the sky, or looking down at their feet. Active perception is higher resolution (512x512 minimum vs 256x256 passive), always creates a Moment node (unlike passive which skips static scenes), and returns the image directly as a multimodal response. This is the difference between peripheral awareness and focused attention.

## NON-OBJECTIVES

- **3D rendering** — The vision module does NOT render the scene. It requests a screenshot from the 3D engine and processes the result. mind-mcp has no 3D renderer.
- **Object recognition or scene labeling** — Vision does not label objects in the image ("chair", "table"). The LLM does that when it receives the screenshot as multimodal input. Vision produces the image and embedding; understanding is the LLM's job.
- **Real-time video streaming** — Vision captures discrete screenshots at controlled intervals, not continuous video feeds.
- **Replacing exteroception** — Vision complements exteroception, it does not replace it. A citizen can "know" about an actor 3 hops away in the graph (exteroception) but cannot "see" them if they are outside the visual field. Both systems are needed for complete awareness.

## TRADEOFFS (canonical decisions)

- When **token cost** conflicts with **visual fidelity**, choose token efficiency. A missed frame is recoverable; wasted tokens across 60+ citizens are not.
- When **capture frequency** conflicts with **responsiveness to change**, choose event-triggered capture over periodic capture. Capturing every N ticks is the baseline; events (movement, new actor, high arousal) override the timer.
- We accept **latency in visual perception** (up to 10 ticks between captures) to preserve **system throughput**. Citizens do not need frame-by-frame vision; they need meaningful visual snapshots.
- When **CLIP embedding quality** conflicts with **embedding compute cost**, choose lower resolution and accept the quality tradeoff. CLIP on 256x256 JPEG produces equivalent 768D embeddings to full-res at a fraction of the compute cost.
- **Full resolution is preserved, compressed is sent.** The engine screenshot (1080p PNG ~2MB) is always saved at full resolution in the graph as `media.image.uri` for visual memory. A separate resized + JPEG-compressed version (256x256 or 512x512, quality 75, ~50KB) is sent to the LLM. These are two distinct paths: archival fidelity vs. token economy. Never send raw engine output to the LLM.
- When **passive vision cost** conflicts with **active perception quality**, active perception (`/look`) spends more. `/look` is citizen-initiated and explicitly budgeted as an extra engine call outside the tick budget. Higher resolution (512x512), always persists, always returns to the citizen. The citizen chose to look — the cost is justified.

## SUCCESS SIGNALS (observable)

- Citizens reference visual details in conversation ("I can see the Arsenal from here", "there is a new structure in the Data Gardens")
- Static scenes produce zero screenshot captures after the initial frame (change detection prevents waste)
- Flashbulb captures occur at emotional peaks and produce high-weight Moment nodes with `subtype: vision`
- CLIP embeddings on visual Moment nodes participate in coherence calculations (Sim_vis term is non-zero)
- System sustains 60+ citizens with vision enabled without exceeding token budget or stalling the tick loop
- `/look` returns a 512x512 screenshot and multimodal description within a single MCP tool response
- `/look @citizen` crops and upscales the target citizen's region from the scene
- `/look behind` rotates the citizen 180 degrees and captures the new view
- Every `/look` invocation creates a Moment node, regardless of scene change

---

## MARKERS

<!-- @mind:todo Define the exact token budget per citizen per tick cycle for vision captures. At 256x256 JPEG quality 75 (~50KB), token cost per image is significantly reduced vs raw 1080p PNG. At 60 citizens x 6 captures/hour, validate compressed image token cost against actual Claude billing. -->

<!-- @mind:escalation The 3D engine must expose a render-from-POV API. This does not exist yet. Vision design depends on this API contract being defined. Need engine team confirmation on: endpoint shape, response format (PNG vs JPEG), depth buffer availability, latency expectations. -->
