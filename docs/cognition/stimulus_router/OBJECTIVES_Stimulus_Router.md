# OBJECTIVES — Stimulus Router

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
THIS:            OBJECTIVES_Stimulus_Router.md (you are here - START HERE)
PATTERNS:       ./PATTERNS_Stimulus_Router.md
BEHAVIORS:      ./BEHAVIORS_Stimulus_Router.md
ALGORITHM:      ./ALGORITHM_Stimulus_Router.md
VALIDATION:     ./VALIDATION_Stimulus_Router.md
IMPLEMENTATION: ./IMPLEMENTATION_Stimulus_Router.md
HEALTH:         ./HEALTH_Stimulus_Router.md
SYNC:           ./SYNC_Stimulus_Router.md

IMPL:           runtime/cognition/stimulus_router.py
```

**Read this chain in order before making changes.** Each doc answers different questions. Skipping ahead means missing context.

---

## PRIMARY OBJECTIVES (ranked)

1. **Faithful signal transduction** — Every meaningful external event (message, bridge signal, system event) must arrive at the L1 cognitive engine as a well-formed Stimulus with appropriate energy, classification, and targeting. If this fails, the citizen is deaf to the world.

2. **Anti-loop integrity** — Self-generated output fed back as stimulus must never produce runaway feedback loops. The router is the last line of defense before energy enters the graph. A loop means the citizen talks to itself forever, burning compute and producing nothing.

3. **Source-aware energy budgeting** — Different event sources carry different attentional weight. A Telegram message from a human partner is not the same as a system health check. The router must assign energy budgets that reflect the signal's importance so working memory prioritizes correctly.

4. **Deduplication fidelity** — Repeated or near-identical stimuli must be caught before injection. Without dedup, the same message arriving through multiple bridges (Telegram relay, MCP tool echo) would inject double energy and distort attention.

5. **Metabolism readiness** — The router's energy assignment pipeline must be extensible for per-citizen metabolism modulation. The upcoming metabolism feature will adjust stimulus sensitivity based on arousal, satiation, and circadian state. The router must not hardcode energy in ways that prevent this.

## NON-OBJECTIVES

- **Semantic understanding of content** — The router classifies events structurally (source, flags, hash-based novelty). Deep semantic analysis belongs to Law 1's embedding-based targeting and the threshold oracle.
- **Node creation or graph mutation** — The router produces Stimulus objects. Law 1 (`law_01_energy_injection.py`) handles node creation, deduplication against the graph, and energy distribution across nodes.
- **Conversation management** — The router does not decide whether to respond. It injects energy; the tick loop's orientation and action-emission pipeline decides if and how to act.
- **Bridge protocol handling** — Individual bridge adapters (Telegram, Discord, WhatsApp) handle protocol specifics. The router receives already-parsed `IncomingEvent` objects.

## TRADEOFFS (canonical decisions)

- When **dedup aggressiveness** conflicts with **signal preservation**, choose dedup. A missed duplicate wastes energy and distorts attention. A false positive (rejecting a genuinely new but similar message) is recoverable because the sender will rephrase or resend.
- When **anti-loop safety** conflicts with **self-reflection depth**, choose safety. The diminishing returns curve (0.5^n half-life) ensures self-stimuli still arrive but with geometrically decreasing energy.
- We accept **hash-based novelty detection** (which misses semantic similarity) to preserve **zero-latency routing**. No LLM calls in the routing path. When embeddings become available per-citizen, novelty detection will upgrade to cosine similarity.

## SUCCESS SIGNALS (observable)

- A citizen receiving 10 Telegram messages processes all 10 as distinct stimuli with social classification and 1.2x base energy
- A citizen's own output fed back as self-stimulus gets progressively attenuated: full energy at first, halved after 3 self-loops, quartered after 6
- Duplicate messages (same content hash) arriving within the dedup window (50 items) are silently dropped
- The feedback injector successfully routes post-action output back through the router with source="self" and appropriate is_failure/is_progress flags
- Under the upcoming metabolism feature, energy budgets scale with citizen arousal state without router code changes
