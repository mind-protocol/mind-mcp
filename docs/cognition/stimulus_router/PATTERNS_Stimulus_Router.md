# Stimulus Router — Patterns: Gateway Between World and Mind

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Stimulus_Router.md
THIS:            PATTERNS_Stimulus_Router.md (you are here)
BEHAVIORS:       ./BEHAVIORS_Stimulus_Router.md
ALGORITHM:       ./ALGORITHM_Stimulus_Router.md
VALIDATION:      ./VALIDATION_Stimulus_Router.md
HEALTH:          ./HEALTH_Stimulus_Router.md
IMPLEMENTATION:  ./IMPLEMENTATION_Stimulus_Router.md
SYNC:            ./SYNC_Stimulus_Router.md

IMPL:            runtime/cognition/stimulus_router.py
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read the linked IMPL source file

**After modifying this doc:**
1. Update the IMPL source file to match, OR
2. Add a TODO in SYNC_Stimulus_Router.md: "Docs updated, implementation needs: {what}"
3. Run tests: `python -m pytest runtime/cognition/tests/test_l1_wiring_integration.py`

**After modifying the code:**
1. Update this doc chain to match, OR
2. Add a TODO in SYNC_Stimulus_Router.md: "Implementation changed, docs need: {what}"
3. Run tests: `python -m pytest runtime/cognition/tests/test_l1_wiring_integration.py`

---

## THE PROBLEM

The L1 cognitive engine operates on `Stimulus` objects — structured carriers of energy, classification flags, and targeting information. But the outside world speaks in raw events: a Telegram message arrives as text with metadata, an MCP tool call returns structured output, the citizen's own LLM response needs to re-enter the graph as self-stimulus.

Without a router, every event source would need to understand the Stimulus dataclass, energy budgeting, anti-loop protection, and dedup semantics. Each bridge would implement its own incompatible version. The cognitive engine would receive malformed stimuli, duplicate injections, and feedback loops.

The stimulus router is the sensory cortex of the citizen. It sits between the raw event stream and the cognitive tick loop, translating the messy external world into clean energy injections that Law 1 can process.

---

## THE PATTERN

**One router per citizen, stateful, pipeline-based.**

Each citizen gets their own `StimulusRouter` instance that maintains per-citizen state: anti-loop tracking, dedup history, and (future) metabolism modulation parameters.

The routing pipeline is a linear filter chain:

```
IncomingEvent → anti-loop gate → dedup gate → classify → energy budget → build Stimulus
```

Each stage can reject the event (returning None) or pass it forward with modifications. The pipeline is synchronous and allocation-light — no LLM calls, no graph queries, no I/O. This ensures the router never becomes a bottleneck in the dispatch loop.

The key insight: **the router is a lossy filter, not a lossless pipe.** It deliberately discards events that would harm the cognitive engine (loops, duplicates, noise). The information loss is a feature, not a bug. A citizen that processes every event equally is a citizen with no attention.

---

## BEHAVIORS SUPPORTED

- **B1: External events produce stimuli** — The router converts any IncomingEvent with source != "self" into a Stimulus with full energy budget.
- **B2: Self-stimuli attenuate geometrically** — The anti-loop gate applies diminishing returns (0.5^(n/3) half-life) to prevent self-reinforcing loops.
- **B3: Duplicates are silently absorbed** — Content-hash dedup within a sliding window prevents double injection.
- **B4: Social sources get energy boost** — Telegram, Discord, WhatsApp events and events flagged is_social=True receive 1.2x base energy, ensuring social signals compete effectively for working memory.

## BEHAVIORS PREVENTED

- **A1: Feedback loops** — The three-layer anti-loop gate (refractory period, diminishing returns, novelty gate) prevents the citizen from entering an infinite self-stimulation cycle.
- **A2: Duplicate energy injection** — Hash-based dedup prevents the same content from injecting energy twice, even if it arrives through multiple bridges.

---

## PRINCIPLES

### Principle 1: Stateless Pipeline, Stateful Gate

The routing pipeline itself is stateless — given the same IncomingEvent and the same gate state, it produces the same Stimulus. All mutable state lives in the AntiLoopGate and the dedup history. This separation makes the pipeline testable and the state inspectable.

### Principle 2: Fail Closed

When in doubt, the router drops the event. A missed stimulus is recoverable (the sender resends, the event repeats, the system generates a new one). A bad stimulus that enters the graph corrupts attention and wastes compute. The router's default is "reject unless proven safe."

### Principle 3: Energy Is the Only Language

The router does not communicate classification to the tick loop through side channels. Everything is encoded in the Stimulus object: energy_budget for importance, is_social/is_failure/is_novelty/is_progress flags for limbic modulation, source string for provenance. Law 1 reads these fields and distributes energy accordingly.

---

## DATA

| Source | Type | Purpose / Description |
|--------|------|-----------------------|
| `runtime/cognition/stimulus_router.py` | FILE | Primary implementation — IncomingEvent, AntiLoopGate, StimulusRouter |
| `runtime/cognition/tick_runner_l1_cognitive_engine.py` | FILE | Defines the Stimulus dataclass consumed by the router's output |
| `runtime/cognition/feedback_injector.py` | FILE | Post-action feedback loop that creates IncomingEvents with source="self" |
| `runtime/orchestrator/dispatcher.py` | FILE | Creates per-citizen StimulusRouter instances and calls router.route() on incoming messages |
| `runtime/ingestion/l1_stimulus_injector_for_partner_data.py` | FILE | Partner data ingestion that produces PartnerStimulus objects (parallel interface) |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `cognition/tick_runner_l1_cognitive_engine` | Imports the `Stimulus` dataclass that the router produces |
| `cognition/constants` | (Indirect, via Law 1) Energy constants, thresholds, dedup parameters |

---

## INSPIRATIONS

The router draws from two sources:

**Sensory gating in neuroscience.** The thalamus filters sensory input before it reaches the cortex. Not everything gets through. Habituation (diminishing response to repeated stimuli) and refractory periods (neurons that just fired can't fire again immediately) are biological anti-loop mechanisms. The AntiLoopGate implements computational analogs of both.

**Event-driven architecture.** The IncomingEvent/Stimulus split mirrors the raw event / domain event pattern. Raw events are source-specific and potentially noisy. Domain events (Stimulus) are normalized, deduplicated, and enriched with classification. The router is the anti-corruption layer.

---

## SCOPE

### In Scope

- Converting IncomingEvent objects into Stimulus objects
- Anti-loop protection for self-generated stimuli
- Content-hash dedup within a sliding window
- Source-based classification (social detection, failure/progress flags)
- Energy budget assignment based on source and anti-loop state
- Concept extraction for node targeting (keyword-based, pre-embedding)

### Out of Scope

- **Embedding generation** — The router accepts an optional `embed_fn` but does not generate embeddings itself. Embedding is the caller's responsibility.
- **Node creation/mutation** — Law 1 creates nodes, merges with existing nodes, and distributes energy across the graph. The router only builds the Stimulus.
- **Bridge protocol handling** — Telegram, Discord, WhatsApp adapters parse protocol-specific formats into IncomingEvent objects before reaching the router.
- **LLM invocation decisions** — The dispatcher decides whether to invoke Claude based on tick results. The router only injects energy.
- **Partner data ingestion** — `l1_stimulus_injector_for_partner_data.py` has its own PartnerStimulus type that bypasses the StimulusRouter. Integration is handled at the dispatcher level.
