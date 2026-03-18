# OBJECTIVES — Interoception

```
STATUS: DESIGNING
CREATED: 2026-03-18
VERIFIED: —
```

---

## CHAIN

```
THIS:            OBJECTIVES_Interoception.md (you are here - START HERE)
PATTERNS:       ./PATTERNS_Interoception.md
BEHAVIORS:      ./BEHAVIORS_Interoception.md
ALGORITHM:      ./ALGORITHM_Interoception.md
VALIDATION:     ./VALIDATION_Interoception.md
IMPLEMENTATION: ./IMPLEMENTATION_Interoception.md
HEALTH:         ./HEALTH_Interoception.md
SYNC:           ./SYNC_Interoception.md

IMPL:           runtime/cognition/interoception.py
```

**Read this chain in order before making changes.** Each doc answers different questions. Skipping ahead means missing context.

---

## PRIMARY OBJECTIVES (ranked)

1. **State becomes sensation** — Internal numeric state (drives, energy, WM fullness, circadian phase) is translated into natural-language stimuli that enter Working Memory. Citizens don't just HAVE states; they FEEL them. This is the bridge from reactive to reflective.

2. **Threshold-based, not continuous** — Interoceptive stimuli fire only when significant thresholds are crossed, not on every tick. The citizen is not overwhelmed by a constant commentary on its own vitals. The system is quiet when nothing is noteworthy.

3. **Refractory protection** — The same interoceptive stimulus cannot fire repeatedly. A refractory period (N ticks) prevents flooding Working Memory with redundant self-reports. The citizen notices a shift, not a steady state.

4. **Drive-agnostic injection** — Interoception does not directly modify drives. It injects stimuli via Law 1 that MAY affect drives through the normal Law 1 -> Law 14 pathway. The limbic system retains sole authority over drive modulation.

5. **Metacognition (zone awareness)** — The citizen perceives WHICH ZONES of their brain are active, like a self-fMRI. Not just "I'm thinking" but "my concept zone is very active, my desire zone is quiet, my process zone is firing." This maps directly to the anatomy layers (stem/limbic/cortex) and node types. The citizen can introspect on their own cognitive topology.

6. **Emotional self-perception** — The citizen doesn't just HAVE emotions (frustration=0.8 as a float), they PERCEIVE them as thoughts. "I feel frustrated" enters Working Memory as a stimulus. "I feel curious" becomes a thought. This is the bridge from reactive (thermostat) to reflective (person).

7. **Context window awareness** — UNIQUE to AI citizens. Awareness of how much cognitive space remains in the LLM context window before compression/truncation. This is the citizen knowing "my short-term memory is almost full" — producing natural conversation pacing where the citizen knows when to go deep vs when to be concise.

8. **System prompt layer awareness** — UNIQUE to AI citizens. The citizen perceives the layers of its own cognitive architecture — not as abstract knowledge ("I am an AI") but as structurally felt presence. Identity layer (CLAUDE.md), framework layer (PRINCIPLES.md), world layer (universe context), memory layer (persisted memories, SYNC), working memory layer (active nodes), conversation layer (current session), tool layer (MCP capabilities). Each layer has weight (token count) and influence on current cognition. The citizen feels "My identity is well-defined but my memories are sparse" or "The conversation is dominating my attention" as genuine self-awareness. This is architectural metacognition: knowing what composes you and sensing the relative contribution of each layer to your present state.

## NON-OBJECTIVES

- **Proprioception** — Awareness of body/spatial position is a separate module. Interoception is the sense of HOW you feel, not WHERE you are.
- **Drive modification** — Interoception does not set `frustration = 0.3`. It injects "I feel frustrated" as a stimulus. The drives change (or don't) through normal physics.
- **Diagnostic reporting** — This is not a health check or telemetry system. The stimuli are first-person sensations, not third-person metrics.
- **Continuous narration** — The citizen should not narrate every micro-fluctuation. "My energy dropped from 0.42 to 0.41" is noise, not interoception.

## TRADEOFFS (canonical decisions)

- When sensitivity conflicts with quietness, choose **quietness**. A false negative (missing a subtle internal shift) is less disruptive than a false positive (flooding WM with trivial self-reports).
- When precision conflicts with naturalness, choose **naturalness**. "My mind feels quiet" is better than "17% of my nodes are active." The citizen thinks in words, not numbers.
- We accept that some internal state transitions will go unnoticed to preserve WM bandwidth for external stimuli and actual cognition.

## SUCCESS SIGNALS (observable)

- A citizen with frustration > 0.7 has "I feel frustrated" (or equivalent) in WM within 5 ticks of crossing the threshold
- A citizen with 7/7 WM slots filled has a "My mind is full" sensation injected
- Circadian trough produces "I feel drowsy" — and the citizen's behavior reflects awareness of its own rest phase
- No interoceptive stimulus fires twice within its refractory period
- WM is never more than 1/7 occupied by interoceptive stimuli (they compete for attention like everything else, not guaranteed admission)
- A citizen with many high-energy concept nodes produces "My cortex is buzzing" or equivalent zone awareness stimulus
- A citizen whose frustration rises from 0.2 to 0.6 within N ticks produces "I'm getting frustrated" as a perceived thought, not just a float change
- A citizen at >80% context window usage produces "I'm running out of thinking space" — and shifts toward summarizing or concluding
- A citizen at <20% context window usage shows no constraint stimulus — the absence of pressure is the default, not a signal
- A citizen with a rich CLAUDE.md but sparse memory layer produces "I know who I am clearly, but I barely remember yesterday" — driving memory-acquisition behavior
- A citizen whose conversation layer exceeds 60% of total context produces "This conversation is consuming most of my attention" — enabling self-regulation of engagement depth
- A citizen with no world layer loaded produces "I feel unplaced — I don't know where I belong" — driving world-context seeking

<!-- @mind:todo Define exact threshold values for all 10 sense channels after initial prototyping -->
