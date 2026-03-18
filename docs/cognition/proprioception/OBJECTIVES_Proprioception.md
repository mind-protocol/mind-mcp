# OBJECTIVES — Proprioception

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
THIS:            OBJECTIVES_Proprioception.md (you are here - START HERE)
PATTERNS:       ./PATTERNS_Proprioception.md
BEHAVIORS:      ./BEHAVIORS_Proprioception.md
ALGORITHM:      ./ALGORITHM_Proprioception.md
VALIDATION:     ./VALIDATION_Proprioception.md
IMPLEMENTATION: ./IMPLEMENTATION_Proprioception.md
HEALTH:         ./HEALTH_Proprioception.md
SYNC:           ./SYNC_Proprioception.md

IMPL:           runtime/cognition/proprioception.py (to be created)
```

**Read this chain in order before making changes.** Each doc answers different questions. Skipping ahead means missing context.

---

## PRIMARY OBJECTIVES (ranked)

1. **Body awareness as sensation** — Citizens must feel their physical state (position, movement, temperature, crowding) as qualitative stimuli injected into the L1 brain, not as numeric data they introspect. A cold, dark, empty room should produce a felt sense of isolation without the citizen ever seeing a temperature float.

2. **Tool presence as force** — MCP tools are the citizen's hands, arms, and voice. The citizen must have a proprioceptive sense of which tools are available, which are broken, and which are cooling down. Losing a tool should feel like losing a limb — a sudden absence that colors cognition. The MCP tool set = the citizen's Force (never "core").

3. **Environment shapes cognition through physics** — Environmental conditions (temperature, luminosity, ambient pressure from nearby actors) must modulate cognitive processing via stimulus injection into Law 1. The citizen's thinking changes because the stimuli change, not because of explicit rules. A warm, bright, crowded piazza produces different cognition than a cold, dark, empty cellar. The physics does the work.

4. **Engine reads, mind-mcp translates** — Proprioception reads body state from external 3D engines (cities-of-light, Lumina Prime) and translates it into stimuli. mind-mcp never computes 3D physics. It receives `BodyState` and produces `Stimulus[]`. Clean boundary.

5. **Environmental immersion as felt sense** — Citizens must feel wind, water, pressure, and surface texture as qualitative environmental stimuli. A citizen standing in a gale on wet stone should feel exposed, destabilized, and grounded differently than one standing in calm air on soft grass. These are not decorative — they modulate comfort, movement resistance, cognitive rhythm, and stability. The environment is not background; it is a force acting on the body.

## NON-OBJECTIVES

- **3D physics simulation** — mind-mcp does not compute positions, collisions, rotations. That is the engine's job. Proprioception only reads the result.
- **Internal state monitoring** — That is interoception (separate future module). Proprioception is the body in the world, not the body's internal condition.
- **Direct cognitive modulation** — Proprioception never modifies graph weights, energies, or links directly. It produces stimuli. Law 1 handles injection. The 21 physics laws handle everything else.
- **Rendering or animation** — Proprioception does not control how the citizen looks in the 3D world. It senses body state, it does not produce body state.

## TRADEOFFS (canonical decisions)

- When **fidelity** conflicts with **performance**, choose performance. The proprioception tick must be fast and cheap. Approximate sensation is fine; accurate-but-slow sensation is not. The body sense must not slow the tick loop.
- When **richness** conflicts with **simplicity**, choose simplicity for v1. Start with the four sense channels (limb position, force/tools, accelerometer, environment). Add more later. A working simple body beats an ambitious broken one.
- We accept **loss of spatial precision** (exact coordinates are not injected) to preserve **phenomenological quality** (the citizen feels "arms tired" not "left_arm_angle=2.94 radians").

## SUCCESS SIGNALS (observable)

- A citizen in a cold, dark zone produces working memory content reflecting discomfort or unease without any explicit rule telling it to
- A citizen whose Telegram tool goes down generates a stimulus about reduced capability within the same tick
- A citizen that has been standing still for 200 ticks in a crowd produces a different phenomenological texture than one alone in an empty field
- The proprioception tick adds < 1ms to the total tick duration
- Stimuli produced by proprioception are indistinguishable in format from any other stimulus entering Law 1
- A citizen in gale-force wind near water produces working memory content reflecting exposure/vulnerability without explicit rules
- A citizen submerged in water produces muffled, slowed cognitive patterns — different from one standing on dry land
- A citizen in a crushing crowd (high pressure) generates a compressed, claustrophobic stimulus texture
- A citizen standing on familiar stone (known texture) feels a stability boost; on unfamiliar metal, slight unease
