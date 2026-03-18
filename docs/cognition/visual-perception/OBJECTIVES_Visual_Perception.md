# OBJECTIVES — Visual Perception (Cone of Vision → Exteroception)

```
STATUS: DESIGNING
CREATED: 2026-03-18
VERIFIED: —
```

---

## CHAIN

```
THIS:            OBJECTIVES_Visual_Perception.md (you are here - START HERE)
PATTERNS:       ./PATTERNS_Visual_Perception.md
BEHAVIORS:      ./BEHAVIORS_Visual_Perception.md
ALGORITHM:      ./ALGORITHM_Visual_Perception.md
VALIDATION:     ./VALIDATION_Visual_Perception.md
IMPLEMENTATION: ./IMPLEMENTATION_Visual_Perception.md
HEALTH:         ./HEALTH_Visual_Perception.md
SYNC:           ./SYNC_Visual_Perception.md

IMPL:           mind-mcp/runtime/cognition/exteroception.py (existing, extend)
                lumina-prime/engine/src/server/perception.js (existing, extend)
```

**Read this chain in order before making changes.**

---

## PRIMARY OBJECTIVES (ranked)

1. **Citizens SEE their city** — The 3D engine renders a frame from the citizen's camera POV. That frame enters the citizen's exteroception pipeline as a visual stimulus. The citizen's brain processes what they see, not just what the graph tells them. Seeing IS knowing — visual perception is a fundamentally different pathway than graph query.

2. **Two resolutions, two uses** — The frame is captured at full resolution (stored for reference), then compressed small for two injection points: (a) the Claude Code session prompt as an image attachment (so the LLM sees the city), and (b) the exteroception stimulus channel (so the physics engine processes it).

3. **Not every tick** — Visual perception is expensive (frame capture + image compression + potentially CLIP embedding). The cadence must balance awareness vs cost. The formula: `vision_interval = base_interval / (1 + arousal)` — more aroused citizens look more often. Default: every 10 ticks (10 min at 60s/tick). High arousal: every 3 ticks (3 min).

4. **The frame carries metadata** — Not just pixels. The capture includes: camera position, rotation, visible citizen IDs, visible building IDs, current district, time of day. This metadata enriches the stimulus even without image analysis.

5. **CLIP embedding enables visual memory** — The frame gets a CLIP/SigLIP embedding (1536-dim). This embedding is stored on the Moment node. Schema v2.2 already supports `image_embedding`. This means: a citizen can "remember" what they saw, and visual similarity search finds related scenes.

## NON-OBJECTIVES

- Building the 3D renderer (engine team)
- Real-time video streaming (too expensive, frames are snapshots)
- Computer vision / object detection (CLIP embedding is sufficient)
- VR headset integration (separate module)

## TRADEOFFS (canonical decisions)

- When frame capture fails (engine down, rendering error), **skip silently**. Visual perception is additive — the citizen still has graph-based exteroception. Never block the tick for a missing frame.
- When CLIP embedding is unavailable (no GPU, API down), **store the frame without embedding**. The metadata alone is valuable. Embedding can be computed later.
- Frame compression for Claude prompt: **max 512×512, JPEG quality 60**. This keeps the image under 100KB — small enough for prompt injection without bloating context.
- Full resolution frame: **1920×1080 PNG** stored to disk. For reference, showcase, and high-quality CLIP embedding.

## SUCCESS SIGNALS (observable)

- A citizen's Claude session includes a current city view image in the system prompt
- The exteroception engine fires a "vision" stimulus with frame metadata
- Moment nodes with type="vision" have non-null image_uri and image_embedding
- graph_query("what did dev see last") returns a vision moment with the frame
- The cartographer shows "vision" channel firing at the expected cadence
- Citizens in high-arousal states see more frequently (shorter interval)

---

## THE MATH: Cost Calculation

### Frame Capture Cost
- Engine renders to offscreen buffer: ~5ms per frame (GPU)
- Encode PNG (full): ~10ms
- Encode JPEG (compressed): ~2ms
- Write to disk: ~1ms
- **Total per capture: ~18ms**

### CLIP Embedding Cost
- Local CLIP (SigLIP-base): ~50ms per frame (GPU), ~500ms (CPU)
- OpenAI CLIP API: ~200ms + network latency, ~$0.0001 per image
- **Budget: if running every 10 ticks (600s), ~0.03ms amortized per tick**

### Claude Prompt Injection Cost
- 512×512 JPEG at q60: ~50-100KB
- Token cost: ~85 tokens for image (Anthropic vision)
- At ~$0.003/1K tokens (Opus): ~$0.00025 per vision injection
- **Per session (1-2 vision injections): ~$0.0005**

### Cadence Formula
```
vision_interval_ticks = max(3, floor(10 / (1 + arousal)))

arousal = 0.0 → every 10 ticks (10 min)
arousal = 0.5 → every 7 ticks (7 min)
arousal = 1.0 → every 5 ticks (5 min)
arousal = 2.0 → every 3 ticks (3 min) — minimum
```

### Cost Per Citizen Per Hour
```
At default (10 ticks = 10 min interval):
  6 frames/hour × 18ms capture = 108ms compute
  6 frames/hour × $0.0001 CLIP = $0.0006
  6 frames/hour × 100KB storage = 600KB/hour

At high arousal (3 ticks = 3 min):
  20 frames/hour × 18ms = 360ms compute
  20 frames/hour × $0.0001 = $0.002
  20 frames/hour × 100KB = 2MB/hour
```

### For 30 Active Citizens
```
Default: 180 frames/hour, ~$0.018/hour, 18MB/hour storage
High arousal: 600 frames/hour, ~$0.06/hour, 60MB/hour storage
```

**Verdict: trivially cheap.** Even at high arousal for all 30 citizens, it's $1.44/day and 1.4GB/day storage.
