# Stimulus Router — Validation: What Must Be True

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Stimulus_Router.md
PATTERNS:        ./PATTERNS_Stimulus_Router.md
BEHAVIORS:       ./BEHAVIORS_Stimulus_Router.md
THIS:            VALIDATION_Stimulus_Router.md (you are here)
ALGORITHM:       ./ALGORITHM_Stimulus_Router.md
IMPLEMENTATION:  ./IMPLEMENTATION_Stimulus_Router.md
HEALTH:          ./HEALTH_Stimulus_Router.md
SYNC:            ./SYNC_Stimulus_Router.md
```

---

## PURPOSE

**Validation = what we care about being true.**

These are the properties that, if violated, mean the stimulus router has failed its purpose. The router is the sensory gateway to the cognitive engine. If it breaks, the citizen either goes deaf (missing events), goes into seizure (feedback loops), or develops hallucinations (duplicate/phantom energy injections).

---

## INVARIANTS

### V1: External Events Always Produce Stimuli

**Why we care:** If an external event (message, bridge signal, system event) fails to produce a Stimulus, the citizen cannot perceive or respond to the outside world. This is the most critical failure mode — a deaf citizen.

```
MUST:   Every IncomingEvent with source != "self" that has non-duplicate content
        produces a non-None Stimulus with energy_budget > 0.
NEVER:  An external event with unique content is silently dropped by the anti-loop gate.
```

### V2: Self-Stimulus Energy Is Bounded and Decreasing

**Why we care:** Unbounded self-stimulus creates runaway feedback loops. The citizen enters an infinite cycle of producing output, perceiving it, and producing more output. This burns compute, produces incoherent behavior, and prevents the citizen from attending to external events.

```
MUST:   For consecutive self-stimuli (no intervening external events), the energy multiplier
        is strictly decreasing: energy_n+1 < energy_n.
NEVER:  A self-stimulus receives energy_budget >= the previous self-stimulus in the same
        chain (unless an external event intervened to reset the counter).
```

### V3: Feedback Loops Terminate

**Why we care:** The combination of refractory period + diminishing returns + novelty gate must guarantee that any self-stimulus chain eventually terminates (energy approaches zero or content is rejected as duplicate).

```
MUST:   After K consecutive self-stimuli with no external events (K <= 20 in practice),
        the energy multiplier is below 0.01 (effectively zero) OR the novelty gate
        rejects the content as a duplicate hash.
NEVER:  An unbounded sequence of self-stimuli passes through the router with non-trivial energy.
```

### V4: Duplicate Content Does Not Inject Twice

**Why we care:** Duplicate energy injection distorts working memory competition. A message that arrives through two bridges gets twice the attention it deserves, potentially displacing more important signals.

```
MUST:   Two IncomingEvents with identical content within the dedup window (50 events)
        produce at most one Stimulus.
NEVER:  The same content hash appears twice in the dedup history without the first
        being evicted by window overflow.
```

### V5: Social Classification Is Consistent

**Why we care:** Social stimuli get 1.2x energy and reset the solitude counter. Inconsistent classification means the citizen might ignore a partner's message (classified as non-social) or treat a system event as social (resetting solitude incorrectly).

```
MUST:   Every event from source in ("telegram", "whatsapp", "discord") is classified
        as social, regardless of the is_social flag on the IncomingEvent.
MUST:   Events with is_social=True from any source are classified as social.
NEVER:  A Telegram/WhatsApp/Discord message produces a Stimulus with is_social=False.
```

### V6: Router State Is Per-Citizen

**Why we care:** Each citizen has independent anti-loop and dedup state. If state leaks between citizens, one citizen's self-stimulus chain could affect another citizen's event processing. The dispatcher creates one StimulusRouter per citizen_handle, and their states must never interact.

```
MUST:   Each StimulusRouter instance maintains independent anti-loop gate state
        and independent dedup history.
NEVER:  An event processed by citizen A's router affects the anti-loop or dedup
        state of citizen B's router.
```

### V7: Feedback Injector Preserves the Perception-Action Loop

**Why we care:** The feedback injector must correctly close the loop: action output -> self-stimulus -> cognitive engine. If the injector fails to call record_action(), the refractory period doesn't activate. If it fails to create episodic memories, the citizen has no autobiographical trace. If it fails to update limbic state, success/failure signals are lost.

```
MUST:   inject_post_action_feedback() calls router.record_action() before routing.
MUST:   Episodic memories are created for outputs >= 30 chars with significance-weighted
        weight (0.35 * significance) and linked to WM nodes.
MUST:   Limbic state updates fire for both success and failure outcomes.
NEVER:  A feedback injection skips record_action() (this would disable the refractory period).
```

---

## PRIORITY

| Priority | Meaning | If Violated |
|----------|---------|-------------|
| **CRITICAL** | System purpose fails | Citizen is deaf or in seizure |
| **HIGH** | Major value lost | Attention distorted or state leaked |
| **MEDIUM** | Partial value lost | Classification wrong or memories missed |

---

## INVARIANT INDEX

| ID | Value Protected | Priority |
|----|-----------------|----------|
| V1 | External events always produce stimuli | CRITICAL |
| V2 | Self-stimulus energy is bounded and decreasing | CRITICAL |
| V3 | Feedback loops terminate | CRITICAL |
| V4 | Duplicate content does not inject twice | HIGH |
| V5 | Social classification is consistent | HIGH |
| V6 | Router state is per-citizen | HIGH |
| V7 | Feedback injector preserves perception-action loop | MEDIUM |
