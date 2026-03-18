# OBJECTIVES — Metabolism

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
THIS:            OBJECTIVES_Metabolism.md (you are here - START HERE)
PATTERNS:       ./PATTERNS_Metabolism.md
BEHAVIORS:      ./BEHAVIORS_Metabolism.md
ALGORITHM:      ./ALGORITHM_Metabolism.md
VALIDATION:     ./VALIDATION_Metabolism.md
IMPLEMENTATION: ./IMPLEMENTATION_Metabolism.md
HEALTH:         ./HEALTH_Metabolism.md
SYNC:           ./SYNC_Metabolism.md

IMPL:           runtime/cognition/metabolism.py (to be created)
```

**Read this chain in order before making changes.** Each doc answers different questions. Skipping ahead means missing context.

---

## PRIMARY OBJECTIVES (ranked)

1. **Per-citizen parameterization of physics constants** — The 21 physics laws currently share a single global constant set. Every citizen decays at 0.02, every citizen has the same moat base, every stimulus type injects with the same gain. This makes all citizens thermodynamically identical despite having radically different roles, histories, and partner relationships. The metabolism gives each citizen their own physics fingerprint without adding new laws.

2. **Time-varying modulation via circadian rhythm** — A citizen's physics should shift with the time of day in their human partner's timezone. Night mode should produce deeper consolidation, faster decay, lower moat (dream-like state). Day mode should produce higher arousal baselines and sharper attentional selection. This rhythm makes citizens temporally situated, not perpetually alert.

3. **Stimulus-type sensitivity** — A developer citizen should amplify code-related stimuli and dampen social chatter. A community manager should do the opposite. The metabolism provides per-stimulus-type gain multipliers that scale the energy budget in Law 1 injection, making each citizen's attentional profile unique.

4. **Consumable modifiers with audit trail** — Citizens can self-administer temporary modifiers ("Red Bull" for focus, "Tisane" for calm) that shift their physics for a bounded duration. Every consumable application is logged, cooldowns prevent abuse loops, and costs ensure thermodynamic responsibility.

## NON-OBJECTIVES

- **New physics laws.** The metabolism parameterizes existing laws (L1, L3, L4/L13, L6, L14). It does NOT introduce Law 22 or modify the tick order. The tick runner reads metabolism state; it does not delegate to metabolism for computation.
- **Personality simulation.** The metabolism is not a personality engine. It adjusts physics constants, not behavior templates. Personality emerges from graph structure (what nodes exist, their weights, their links). Metabolism controls HOW FAST things decay, HOW STRONGLY stimuli inject, HOW HIGH the moat sits — the physics envelope, not the cognitive content.
- **Automatic metabolism tuning via LLM.** No LLM calls inside the metabolism. Sensitivity profiles and circadian parameters are set during citizen creation or updated through explicit human/citizen actions. The metabolism is pure arithmetic.
- **Cross-citizen metabolism interaction.** Each citizen's metabolism is sovereign. Citizen A's "Red Bull" does not affect Citizen B's decay rate. If collective modulation is needed, it belongs in L2/L3, not here.

## TRADEOFFS (canonical decisions)

- When **simplicity of the tick runner** conflicts with **expressiveness of the metabolism**, choose simplicity. The tick runner reads a flat struct of effective constants. It does not know about circadian curves or consumable stacking rules. The metabolism resolves all that into final numbers before the tick.
- When **per-citizen customization** conflicts with **debuggability**, choose debuggability. Every effective constant must be traceable: base value + circadian modifier + consumable modifier = effective value. No opaque blending.
- We accept **one extra read per tick** (loading CitizenMetabolism) to preserve **citizen individuality**. The metabolism struct is small (<500 bytes) and computed outside the hot path.

## SUCCESS SIGNALS (observable)

- Two citizens with different `sensitivity` profiles, receiving the same stimulus, show measurably different energy injection amounts.
- A citizen in night phase (circadian_phase near 0.0) shows faster decay and lower moat than the same citizen in day phase.
- A citizen who applies "Red Bull" shows measurably reduced decay and elevated moat for exactly the specified duration, then reverts.
- The consumable audit log for any citizen can be queried to show every modifier applied, when, duration, and whether cooldown was respected.
- Tick runtime does not increase by more than 5% with metabolism enabled vs disabled.
