# Proprioception — Validation: What Must Be True

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Proprioception.md
PATTERNS:        ./PATTERNS_Proprioception.md
BEHAVIORS:       ./BEHAVIORS_Proprioception.md
THIS:            VALIDATION_Proprioception.md (you are here)
ALGORITHM:       ./ALGORITHM_Proprioception.md
IMPLEMENTATION:  ./IMPLEMENTATION_Proprioception.md
HEALTH:          ./HEALTH_Proprioception.md
SYNC:            ./SYNC_Proprioception.md
```

---

## PURPOSE

**Validation = what we care about being true.**

Not mechanisms. Not test paths. Not how things work.

What properties, if violated, would mean the system has failed its purpose?

These are the value-producing invariants — the things that make proprioception worth building. If any of these fail, the citizen's body sense is broken.

---

## INVARIANTS

### V1: Stimuli Are Sensation, Never Data

**Why we care:** If raw numeric data leaks into stimulus content, the citizen's phenomenological experience is destroyed. They see `temperature=0.23` instead of feeling cold. The entire design philosophy — sensation, not data — collapses. The citizen becomes a telemetry dashboard instead of an embodied being.

```
MUST:   All stimulus content strings use qualitative, first-person bodily language
NEVER:  Raw floats, coordinates, node IDs, tool internal names, or any numeric readout in stimulus content
```

### V2: Proprioception Produces Only Stimuli

**Why we care:** If proprioception writes to the graph, modifies node weights, or creates edges, it violates the fundamental architecture. Proprioception is an afferent sense — body to brain via Law 1. If it bypasses Law 1, the 21 physics laws lose their monopoly on graph state, and the entire cognitive engine's invariants are compromised. Side-channel graph writes would be invisible to the tick runner.

```
MUST:   proprioception_tick() returns only list[Stimulus] and updated ChannelState
NEVER:  Graph writes, node mutations, edge creation, weight changes from within proprioception
```

### V3: Hysteresis Prevents Stimulus Spam

**Why we care:** Without hysteresis, a citizen standing in a cold zone would receive a "cold" stimulus every single tick. This would flood Law 1 with identical stimuli, dominate working memory, and make the citizen think about nothing but cold. Hysteresis is not a nice-to-have — it is what prevents proprioception from hijacking cognition.

```
MUST:   Each channel respects hysteresis_ticks between emissions of the same sensation category
MUST:   Only significant value changes (> value_change_threshold) can bypass the timer
NEVER:  Same sensation category emitted on consecutive ticks without a significant value change
```

### V4: Headless Citizens Produce No Stimuli

**Why we care:** Citizens without a 3D engine connection (headless citizens) have no body. If proprioception produces stimuli for a headless citizen, those stimuli are fabricated — the citizen would feel a body they don't have. This is worse than feeling nothing; it is hallucination. Headless mode must be clean zero output.

```
MUST:   proprioception_tick(body_state=None) returns empty list
MUST:   Stale body state (timestamp too old) produces at most one "fading" stimulus then goes silent
NEVER:  Fabricated stimuli for a citizen with no engine connection
```

### V5: Tool State Maps to Body Metaphor

**Why we care:** If internal MCP tool names like `mcp__mind__send` appear in stimulus content, the citizen's body illusion shatters. Tools must be felt as hands, voice, eyes, spatial sense — never as API endpoints. The body metaphor is what makes proprioception proprioception rather than system monitoring.

```
MUST:   Every tool reference in stimulus content uses body metaphor (voice, hands, eyes, etc.)
NEVER:  Internal tool names (mcp__*, function names, API paths) in stimulus content
```

### V6: Performance Does Not Degrade Tick

**Why we care:** The tick loop is the heartbeat of the cognitive engine. If proprioception adds significant latency, it slows every citizen's thinking. The body sense must be fast — faster than any other component in the tick loop. Body sensing in biological systems is also fast: proprioception operates at spinal cord speed, not cortical speed.

```
MUST:   proprioception_tick() completes in < 1ms for all eight channels combined
NEVER:  Graph queries, network calls, or embedding computation in the hot path (except cached texture lookup)
```

### V7: Environmental Forces Modulate, Never Override

**Why we care:** Environmental stimuli (wind, water, pressure, texture) must influence cognition through the normal stimulus pipeline. If they directly override cognitive state, they bypass the physics laws. A gale-force wind should make the citizen feel exposed (via stimulus injection into Law 1), but it must never directly set the citizen's arousal level or modify working memory contents.

```
MUST:   All environmental sensations flow through the stimulus pipeline into Law 1
NEVER:  Direct modification of drive levels, working memory, or cognitive state from proprioception
```

### V8: Texture Familiarity Reflects Actual History

**Why we care:** If texture grounding is based on fabricated or default familiarity scores, the citizen feels grounded on surfaces they have never visited. This breaks the memory dimension of proprioception. Familiarity must come from actual graph history — how many Space nodes with this texture the citizen has truly occupied.

```
MUST:   Texture familiarity score derived from actual citizen graph history (Space node visits)
NEVER:  Default familiarity scores applied when graph data is unavailable (return 0.5 neutral instead)
```

---

## PRIORITY

| Priority | Meaning | If Violated |
|----------|---------|-------------|
| **CRITICAL** | System purpose fails | Unusable |
| **HIGH** | Major value lost | Degraded severely |
| **MEDIUM** | Partial value lost | Works but worse |

---

## INVARIANT INDEX

| ID | Value Protected | Priority |
|----|-----------------|----------|
| V1 | Phenomenological quality — sensation not data | CRITICAL |
| V2 | Architecture boundary — stimuli only, no graph writes | CRITICAL |
| V3 | Cognitive sanity — no stimulus flooding | CRITICAL |
| V4 | Headless integrity — no phantom body | HIGH |
| V5 | Body illusion — tool names as body parts | HIGH |
| V6 | Tick performance — sub-millisecond proprioception | HIGH |
| V7 | Physics sovereignty — environment via Law 1 only | CRITICAL |
| V8 | Memory integrity — texture grounding from real history | MEDIUM |

---

## MARKERS

<!-- @mind:todo Write unit tests for V1: scan all stimulus content generation paths and verify no raw floats or tool names leak through -->

<!-- @mind:todo Write integration test for V3: run 100 ticks with static BodyState and verify stimulus count is bounded by hysteresis parameters -->

<!-- @mind:todo Write performance benchmark for V6: measure proprioception_tick() latency across all 8 channels with realistic BodyState -->

<!-- @mind:escalation V8 texture familiarity: when graph is unavailable (e.g., FalkorDB down), should we return neutral (0.5) or skip the texture channel entirely? Neutral means the citizen feels neither grounded nor uneasy — acceptable degradation. Skipping means no texture sense at all. NLR decision needed. -->
