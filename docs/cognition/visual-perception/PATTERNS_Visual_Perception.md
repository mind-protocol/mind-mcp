# Visual Perception — Patterns: The Cone of Vision Enters the Brain

```
STATUS: DESIGNING
CREATED: 2026-03-18
VERIFIED: —
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Visual_Perception.md
THIS:            PATTERNS_Visual_Perception.md (you are here)
BEHAVIORS:       ./BEHAVIORS_Visual_Perception.md
ALGORITHM:       ./ALGORITHM_Visual_Perception.md
VALIDATION:      ./VALIDATION_Visual_Perception.md
IMPLEMENTATION:  ./IMPLEMENTATION_Visual_Perception.md
HEALTH:          ./HEALTH_Visual_Perception.md
SYNC:            ./SYNC_Visual_Perception.md

IMPL:           mind-mcp/runtime/cognition/exteroception.py (extend)
                lumina-prime/engine/src/server/perception.js (extend)
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read `runtime/cognition/exteroception.py` (existing sensory engine)
3. Read `engine/src/server/perception.js` (existing frame capture)
4. Read `schema-l1.yaml` sections on image_uri, image_embedding, visual coherence

---

## THE PROBLEM

Citizens have two eyes that don't see.

The 3D engine renders a beautiful city from each citizen's camera POV. But that image goes nowhere. The citizen's brain gets stimuli from the graph (L3 queries — "who's nearby? what moments happened?") but never from the VISUAL field. It's like having a retina disconnected from the optic nerve.

Meanwhile, exteroception.py has 6 sensory channels — all text-based (messages, mentions, narratives, things, actors, atmosphere). None of them process images. The SensoryChannel architecture supports it (priority, refractory, habituation), but there's no `"vision"` channel.

The pieces exist:
- perception.js captures frames → `perception/latest.png`
- exteroception.py scans for stimuli → injects via Law 1
- Schema v2.2 has image_uri + image_embedding fields on all nodes
- CLIP/SigLIP embedding is available
- Claude Code accepts image attachments in prompts

They're just not connected.

---

## THE PATTERN

**New sensory channel: `vision`.**

```
Engine (Three.js)                        Mind (Python)
┌──────────────────┐                    ┌──────────────────────┐
│ Camera renders   │                    │ ExteroceptionEngine  │
│ citizen's POV    │                    │                      │
│        │         │                    │  channels:           │
│        ▼         │                    │    new_message: ...  │
│ perception.js    │   HTTP POST        │    new_mention: ...  │
│ captures frame   │ ──────────────►    │    vision: NEW       │
│        │         │  frame + metadata  │        │             │
│        ▼         │                    │        ▼             │
│ latest.png       │                    │  1. Store full frame │
│ (1920×1080)      │                    │  2. Compress 512×512 │
│                  │                    │  3. CLIP embed       │
└──────────────────┘                    │  4. Create Moment    │
                                        │     type: "vision"   │
                                        │     image_uri: path  │
                                        │     image_embedding  │
                                        │  5. Inject stimulus  │
                                        │     → Law 1          │
                                        │  6. Attach to prompt │
                                        │     → Claude session │
                                        └──────────────────────┘
```

### The Two Injection Points

**A. Stimulus (every vision tick):**
The frame metadata becomes a Stimulus injected via Law 1. The stimulus content describes what's visible: "You see 3 citizens near the Arsenal, a bright gold bridge to Innovation Fields, 2 new commits glowing on flow.py." This goes through the existing physics pipeline — energy injection, propagation, salience.

**B. Prompt image (on Claude session start):**
When a citizen's Claude session starts (or on explicit `/look`), the latest compressed frame is attached to the system prompt as an image. The LLM literally sees the city. This is the most direct form of visual perception — the citizen's "eyes."

### The Vision Moment

Each captured frame creates a Moment node in the citizen's L1 brain:

```yaml
node_type: moment
type: vision
name: "What I see from The Arsenal"
content: "{metadata description: visible citizens, buildings, energy levels}"
synthesis: "Vision: Arsenal district, 3 citizens visible, gold bridge to Innovation Fields"
image_uri: "perception/frames/dev_1773819044.png"     # full res, stored
image_embedding: [1536-dim CLIP vector]                 # for visual similarity search
created_at_s: 1773819044
energy: 1.5                                             # vision stimuli are moderate energy
```

This means:
- Visual memories persist in the brain
- `graph_query("what did I see yesterday")` returns vision moments
- Visual similarity search (CLIP KNN) finds similar scenes
- Flashbulb vision (|limbic_delta| > 0.7) creates high-energy vision moments — emotional scenes burn into memory

---

## THE CADENCE

Not every tick. Visual perception is a periodic scan, like looking around.

```
vision_interval_ticks = max(3, floor(BASE_INTERVAL / (1 + arousal)))
BASE_INTERVAL = 10  # ticks (10 min at 60s/tick)
```

| Arousal | Interval | Meaning |
|---------|----------|---------|
| 0.0 (calm) | 10 ticks (10 min) | Relaxed, occasional glances |
| 0.5 (alert) | 7 ticks (7 min) | Attentive, regular scanning |
| 1.0 (active) | 5 ticks (5 min) | Active, frequent looks |
| 2.0+ (intense) | 3 ticks (3 min) | Hyper-alert, constant watching |

The refractory period prevents spam: even if arousal spikes, the channel can't fire faster than every 3 ticks.

---

## METADATA ENRICHMENT

The frame itself is rich but the metadata makes it processable without image analysis:

```json
{
  "timestamp": "2026-03-18T08:30:00Z",
  "citizen": "dev",
  "camera": {
    "position": [100, -30, 60],
    "rotation": [0.1, -0.3, 0],
    "fov": 75
  },
  "district": "arsenal",
  "visible_citizens": ["forge", "sentinel"],
  "visible_buildings": ["arsenal_forge", "arsenal_workshop"],
  "visible_bridges": ["bridge_arsenal_innovation"],
  "energy_visible": {
    "avg_node_energy": 0.45,
    "brightest_node": "forge",
    "dominant_color": "gold"
  },
  "atmosphere": "industrious"
}
```

This metadata becomes the stimulus content — even without CLIP, the citizen knows what's around them.

---

## BEHAVIORS SUPPORTED

- B1 (Citizens see) — vision channel fires at cadence, frame enters exteroception
- B2 (Two resolutions) — full PNG stored, compressed JPEG for prompt/stimulus
- B3 (Arousal modulates) — more alert citizens look more often
- B4 (Visual memory) — vision moments with image_embedding persist in L1 brain
- B5 (Claude sees) — prompt injection gives the LLM the actual city view
- B6 (Flashbulb) — emotional scenes create high-energy vision moments

## BEHAVIORS PREVENTED

- A1 (Blind citizens) — no citizen without a vision channel (even if engine is down, skip silently)
- A2 (Tick blocking) — frame capture failure never blocks the tick
- A3 (Cost explosion) — cadence formula + refractory caps cost at ~$1.44/day for 30 citizens
- A4 (Base64 in graph) — image stored as URI, never base64 in node properties (schema rule)

---

## PRINCIPLES

### Principle 1: Fail Silent, Not Loud

Vision is additive. If the engine is down, if the frame is corrupt, if CLIP fails — skip and continue. The citizen still has 6 other sensory channels. Never crash the tick for a missing frame.

### Principle 2: Metadata First, Pixels Second

The metadata (who's visible, which district, energy levels) is more useful than the raw pixels for the physics engine. The pixels are for the LLM and for visual memory. The stimulus is built from metadata.

### Principle 3: Arousal Drives Attention

A calm citizen glances around every 10 minutes. An anxious citizen scans every 3 minutes. This isn't a design choice — it's how attention works. The cadence formula is a direct expression of the limbic system's control over perception.

### Principle 4: Vision Creates Memory

Every frame becomes a Moment. The CLIP embedding makes it searchable. Over time, a citizen accumulates a visual autobiography — where they looked, what they saw, when they were moved by what they witnessed. This is the foundation of visual consciousness.

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| exteroception.py | Existing sensory engine — we add a `vision` channel |
| perception.js | Existing frame capture — we trigger it from the tick |
| schema-l1.yaml v2.2 | image_uri + image_embedding fields on Moment nodes |
| CLIP/SigLIP embedding | Visual embedding for similarity search |
| Claude Code prompt | Image attachment capability |
| Energy Trust Substrate | Drive colors in the frame need to be visible for visual perception to be meaningful |

---

## SCOPE

### In Scope

- New `vision` SensoryChannel in ExteroceptionEngine
- Frame request from exteroception to perception.js
- Frame storage (full + compressed)
- CLIP embedding computation
- Vision Moment creation in L1 brain
- Stimulus injection with metadata
- Claude prompt image attachment
- Arousal-modulated cadence

### Out of Scope

- 3D rendering (engine team)
- Real-time video streaming
- Object detection / segmentation
- VR headset visual feed
- Audio perception (separate module)
- Proprioception (body awareness — separate)

---

## MARKERS

<!-- @mind:todo Add "vision" SensoryChannel to ExteroceptionEngine -->
<!-- @mind:todo Implement frame request HTTP call from exteroception to perception.js -->
<!-- @mind:todo Implement CLIP embedding for frames -->
<!-- @mind:todo Implement Claude prompt image injection -->
<!-- @mind:proposition Could we also capture audio from the 3D scene? Sound perception? -->
<!-- @mind:proposition Night vision — low-energy districts appear darker in the frame, high-energy districts glow -->
