# Physics — Patterns: Attention Energy Split (Focus Redistribution as Physics)

```
STATUS: DRAFT
CREATED: 2025-12-20
VERIFIED: 2025-12-20 against local tree
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Attention_Energy_Split.md
THIS:            PATTERNS_Attention_Energy_Split.md (you are here)
BEHAVIORS:       ./BEHAVIORS_Attention_Split_And_Interrupts.md
ALGORITHM:       ./ALGORITHM_Attention_Energy_Split.md
VALIDATION:      ./VALIDATION_Attention_Split_And_Interrupts.md
HEALTH:          ./HEALTH_Attention_Energy_Split.md
SYNC:            ./SYNC_Attention_Energy_Split.md

IMPL:            runtime/physics/attention_split_sink_mass_distribution_mechanism.py
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read the linked IMPL source file

**After modifying this doc:**
1. Update the IMPL source file to match, OR
2. Add a TODO in SYNC_*.md: "Docs updated, implementation needs: attention split"
3. Run tests: `mind validate`

**After modifying the code:**
1. Update this doc chain to match, OR
2. Add a TODO in SYNC_*.md: "Implementation changed, docs need: attention split docs"
3. Run tests: `mind validate`

---

## THE PROBLEM

The engine needs a grounded way for new arrivals or newly linked narratives to
matter without relying on fiat interrupts, cooldown timers, or threat-only
heuristics. Interest must be causal and local to the player neighborhood while
staying mechanically honest.

Naive interrupt rules (any flip, any threat, type-only interrupts) cause
thrashing and make “urgency” meaningless. Cooldown timers and hidden scoring
systems undermine mechanical honesty and are difficult to debug. Attention and
interrupts belong to the same physical story: redistribution of energy is what
reconfigures focus, and focus reconfiguration is what fires interrupts.

---

## THE PATTERN

Model attention as a **conserved energy budget** distributed across
player-linked narratives and moments. When new sinks appear in the player
neighborhood, attention is redistributed via a dynamic split function. This
redistribution can demote previously dominant moments below threshold and
reconfigure focus without arbitrary rules.

Interruption is a consequence of focus reconfiguration, not a separate rule.

## INTERRUPT PATTERN

Define interruption as a **binary consequence** of focus reconfiguration in the
player neighborhood. An interrupt occurs only when the active focus state
changes, the previous active moment deactivates, a player-linked moment becomes
spoken, or a CONTRADICTS node surfaces. Interrupt is not a heuristic; it is a
direct outcome of attention physics.

---

## PRINCIPLES

### Energy Principles

### Principle 1: Conserved Attention Budget

Attention is a fixed budget per tick for the player neighborhood, redistributed
across eligible sinks.

Why this matters: makes focus shifts a physical consequence, not a heuristic.

### Principle 2: Structural Eligibility

Only nodes in the player neighborhood can receive attention.

Why this matters: preserves locality and prevents global mood leakage.

### Principle 3: Dynamic Split Function

Shares are computed by a function of focus, link weights, visibility, and
recency, never by hardcoded constants alone.

Why this matters: keeps the system tunable and avoids magic numbers.

### Interrupt Principles

### Principle 4: Focus Change Is the Interrupt

Interrupt fires only when the dominant active focus changes or deactivates.

Why this matters: keeps interrupts grounded in graph dynamics.

### Principle 5: Canonization Is Always Interrupting

If a player-linked moment becomes completed, interrupt is always yes.

Why this matters: canon changes are player-visible and must reset pacing.

### Principle 6: No Cooldowns as Primary Mechanism

Cooldown timers are never the main interrupt gate.

Why this matters: avoids hidden heuristics and preserves determinism.

---

## DATA

| Source | Type | Purpose / Description |
|--------|------|-----------------------|
| Player neighborhood | OTHER | Eligible attention sinks |
| Narrative focus | OTHER | Weighting factor for split function |
| Link weights | OTHER | Structural influence on shares |
| Visibility/recency | OTHER | Dynamic context for split_fn |
| Dominant active moment | OTHER | Identity for interrupt decisions |
| Activation threshold | OTHER | Defines when active focus loses activation |
| Canonization events | OTHER | Spoken/canon updates that force interrupts |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `runtime/physics/tick.py` | Applies energy propagation and decay |
| `docs/physics/PATTERNS_Physics.md` | Energy and determinism constraints |
| `docs/runtime/moments/PATTERNS_Moments.md` | Player-visible artifact rules |
| `docs/runtime/membrane/PATTERNS_Membrane_Scoping.md` | Dynamic parameter policy, scoping context |

---

## INSPIRATIONS

- Attention budgeting in cognitive architectures.
- Energy-conserving flow models in graph dynamics.

---

## SCOPE

### In Scope

- Redistribute attention energy across player-linked sinks each tick.
- Allow redistribution to change dominant moment and activation state.
- Keep all effects derived from structure and focus values.
- Evaluate interrupts as focus reconfiguration, completed moments, or visible
  contradictions inside the runner neighborhood.

### Out of Scope

- Query side-effects (reads that mutate energy).
- Type-only interrupts without physical coupling.
- Ad hoc energy injection for “interesting” events.
- Cheap cooldown or score systems that declare interrupts without a focus shift.

---

## MARKERS

<!-- @mind:todo Define the player_neighborhood() boundary (links + depth). -->
<!-- @mind:todo Specify split_fn inputs and bounds. -->
<!-- @mind:proposition Add debug-only observability for sink shares and dominant focus. -->
<!-- @mind:todo Define dominant active moment selection policy. -->
<!-- @mind:todo Define “player-linked” criteria for focus and interrupt evaluation. -->
*** End Patch"}}
