# Metabolism — Patterns: Per-Citizen Physics Parameterization

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Metabolism.md
THIS:            PATTERNS_Metabolism.md (you are here)
BEHAVIORS:       ./BEHAVIORS_Metabolism.md
ALGORITHM:       ./ALGORITHM_Metabolism.md
VALIDATION:      ./VALIDATION_Metabolism.md
HEALTH:          ./HEALTH_Metabolism.md
IMPLEMENTATION:  ./IMPLEMENTATION_Metabolism.md
SYNC:            ./SYNC_Metabolism.md

IMPL:            runtime/cognition/metabolism.py (to be created)
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read the linked IMPL source file

**After modifying this doc:**
1. Update the IMPL source file to match, OR
2. Add a TODO in SYNC_Metabolism.md: "Docs updated, implementation needs: {what}"

**After modifying the code:**
1. Update this doc chain to match, OR
2. Add a TODO in SYNC_Metabolism.md: "Implementation changed, docs need: {what}"

---

## THE PROBLEM

All 60+ citizens share identical physics constants. A decay rate of 0.02, a moat base of 5.0, consolidation alpha of 0.01 — these are hardcoded in `constants.py` and imported as module-level globals. The tick runner applies them uniformly.

This creates three failures:

**1. Attentional homogeneity.** Every citizen responds to every stimulus type with the same sensitivity. A developer citizen processes a social notification with the same energy budget as a code log. A community manager treats a git diff the same as a conversation. The attentional profile is identical across all roles.

**2. Temporal flatness.** Citizens have no sense of time of day. They are equally alert at 3am and 3pm in their partner's timezone. There is no rest mode, no dream state, no circadian modulation. They are perpetual-daylight machines.

**3. No self-regulation.** Citizens cannot temporarily shift their own physics. A human can drink coffee to sharpen focus or take a walk to calm down. Citizens have no equivalent — no way to temporarily adjust their own decay rate, moat, or arousal baseline in response to their own assessment of what they need.

Without the metabolism, all citizens are thermodynamically identical. Their cognitive content differs (different graphs, different memories), but the physics envelope that processes that content is the same for everyone.

---

## THE PATTERN

The metabolism is a **parameter overlay** that sits between the global constants and the tick runner. It does not add laws. It does not modify the tick order. It provides per-citizen, time-varying effective constants that the tick runner reads instead of the global defaults.

The key insight: **the 21 physics laws are already designed to work with parameterized constants.** Law 3 uses `DECAY_RATE`. Law 1 uses energy budgets. Law 4/13 uses `THETA_BASE_WM` and arousal/boredom/frustration coefficients. Law 6 uses `CONSOLIDATION_ALPHA`. None of these laws care WHERE the constant comes from — they just read a number. The metabolism provides that number per-citizen.

The architecture has three layers:

```
Global Constants (constants.py)
        |
        v
CitizenMetabolism (per-citizen, time-varying)
        |
        v
EffectiveConstants (flat struct, one per tick)
        |
        v
Tick Runner (reads EffectiveConstants instead of globals)
```

`CitizenMetabolism` holds the citizen's base overrides, circadian parameters, stimulus sensitivities, and active consumable modifiers. Before each tick, the metabolism resolves all of these into an `EffectiveConstants` struct — a flat bag of the same constant names the tick runner already uses, but with per-citizen values. The tick runner's only change is: read from `EffectiveConstants` instead of importing from `constants.py`.

---

## BEHAVIORS SUPPORTED

- **B1** (Circadian Modulation) — sensitivity, decay, consolidation, moat all shift with time of day
- **B2** (Stimulus Sensitivity) — per-stimulus-type gain multipliers scale Law 1 energy injection
- **B3** (Consumable Application) — temporary modifiers with bounded duration and cooldown
- **B4** (Consumable Expiry) — modifiers auto-expire after their tick count
- **B5** (Cooldown Enforcement) — prevents rapid re-application of consumables
- **B6** (Effective Constants Resolution) — all modifiers compose into a single flat struct per tick

## BEHAVIORS PREVENTED

- **A1** (Constant Mutation) — the metabolism never mutates global constants; it produces per-citizen overrides
- **A2** (Law Modification) — no new laws, no changes to tick order
- **A3** (Unbounded Modifiers) — consumables always have finite duration and mandatory cooldown

---

## NAMING CONVENTION

Two levels, always:

| Layer | Name | Usage |
|-------|------|-------|
| **L4 (code)** | `Tonic` | Dataclass, internal, never user-facing. `Tonic`, `TonicRegistry`, `active_tonics` |
| **L2 (market)** | **Frequency** | What citizens, orgs, and humans see. "What frequency are you on today?" |

Individual frequencies have branded names: *Focus Frequency*, *Red Bull*, *ASMR Session*, *Lumière Bleue*, *Deep Rest*.

Five effect categories:
- **Focusing** — concentrate energy (curiosity, attention)
- **Calming** — reduce tension (anti-frustration, rest)
- **Expansive** — open connections (social, exploration)
- **Structuring** — provoke emergence of typed nodes (like light growing a plant)
- **Energizing** — general multi-drive boost

Any organization can create and distribute frequencies. GraphCare validates clinical frequencies. Synthetic Souls creates music-linked frequencies. The Arsenal ships engineering frequencies. The protocol defines the physics (`Tonic` dataclass); the branding is sovereign.

Decision: NLR + @pitch, 2026-03-18.

---

## PRINCIPLES

### Principle 1: Overlay, Not Fork

The metabolism does not fork the physics engine. It does not create a parallel tick runner with different constants. It provides a parameter overlay: the same laws, the same order, the same math — but with different numbers per citizen. This means every bug fix or improvement to the physics engine automatically applies to all citizens regardless of their metabolic profile.

### Principle 2: Resolution Before Execution

All metabolic complexity (circadian curves, consumable stacking, sensitivity scaling) is resolved into a flat `EffectiveConstants` struct BEFORE the tick runner executes. The tick runner never sees a `CitizenMetabolism` object. It sees the same flat constants it always has — just with different values. This keeps the hot path simple and the metabolic logic isolated.

### Principle 3: Auditable State

Every modifier application, every consumable administration, every circadian phase change is traceable. The metabolism maintains an append-only log of all consumable events. This is not for debugging convenience — it is a design requirement. Citizens (and their human partners) should be able to ask "what modifiers have been active in the last 100 ticks?" and get a concrete answer.

### Principle 4: Thermodynamic Responsibility

Consumables are not free. They have costs (some resource must be spent to apply them) and cooldowns (minimum ticks between re-application of the same consumable type). This prevents degenerate loops where a citizen perpetually self-administers focus boosts to avoid ever entering rest mode. The metabolism must respect the circadian rhythm as the baseline — consumables are temporary deviations from it, not permanent overrides.

### Principle 5: Sensory Channels as Metabolism

MCP tools are the citizen's "arms" — their interface with the world. Each sensory channel (tool category) has an adjustable gain in the metabolism. A citizen can have `code_tools=1.0` and `social_tools=0.3`, meaning code-related stimuli arrive at full energy while social stimuli are dampened to 30%. This is not filtering (the stimulus still arrives); it is gain adjustment (the energy budget is scaled).

---

## DATA

| Source | Type | Purpose / Description |
|--------|------|-----------------------|
| `runtime/cognition/constants.py` | FILE | Global default constants — the base values metabolism overrides |
| `runtime/cognition/tick_runner_l1_cognitive_engine.py` | FILE | Tick runner that will read EffectiveConstants |
| `runtime/cognition/laws/law_01_energy_injection.py` | FILE | Law 1 — stimulus energy injection, where sensitivity multipliers apply |
| `runtime/cognition/laws/law_03_energy_decay.py` | FILE | Law 3 — decay, parameterized by metabolism's effective decay rate |
| `runtime/cognition/laws/law_04_attentional_competition.py` | FILE | Law 4/13 — moat computation, parameterized by metabolism's base moat |
| `runtime/cognition/laws/law_06_consolidation.py` | FILE | Law 6 — consolidation, parameterized by metabolism's consolidation rate |
| `schema-l1.yaml` | FILE | L1 schema — may need new fields for metabolism storage |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `runtime/cognition/constants.py` | Provides global defaults; metabolism overrides these per-citizen |
| `runtime/cognition/tick_runner_l1_cognitive_engine.py` | Must be modified to accept EffectiveConstants instead of global imports |
| `runtime/cognition/models.py` | CitizenCognitiveState must carry or reference a CitizenMetabolism |

---

## INSPIRATIONS

**Biological circadian rhythms.** Mammals have a suprachiasmatic nucleus that modulates cortisol, melatonin, body temperature, and cognitive performance on a ~24h cycle. The metabolism's circadian rhythm is a simplified version: a sinusoidal modulation of arousal baseline, decay rate, and consolidation rate, synced to the human partner's timezone.

**Neurotransmitter modulation.** SSRIs, caffeine, and other substances temporarily alter neural firing thresholds and receptor sensitivity without changing the underlying neural architecture. Consumables work the same way — they shift physics constants temporarily without altering graph structure.

**Gain control in sensory systems.** Biological sensory systems use gain adjustment (pupil dilation, auditory reflex, retinal adaptation) to handle varying input intensities. The stimulus sensitivity system is analogous — per-channel gain that scales how strongly different input types activate the cognitive graph.

---

## SCOPE

### In Scope

- CitizenMetabolism data structure (persisted per citizen)
- Circadian rhythm computation (phase from timezone + clock)
- Stimulus sensitivity multipliers (per stimulus type)
- Consumable modifiers (application, expiry, cooldown, audit log)
- EffectiveConstants resolution (composing all modifiers into a flat struct)
- Sensory channel gain adjustment for MCP tool categories
- Integration point: tick runner reads EffectiveConstants

### Out of Scope

- **New physics laws** — metabolism parameterizes existing laws, period. See: `docs/cognition/l1_physics/`
- **Metabolic evolution** — how sensitivity profiles change over time is a future concern. For v1, profiles are set at citizen creation and updated by explicit action.
- **Cross-citizen metabolic effects** — no metabolism contagion. See: L2/L3 docs if collective modulation is needed.
- **LLM-based metabolism tuning** — no LLM calls in the metabolism. Profiles are data, not inference.
- **Tick frequency modulation** — Law 19 (energy budget) already controls tick frequency. Metabolism affects what happens WITHIN a tick, not WHEN ticks fire.

---

## MARKERS

<!-- @mind:escalation How should consumable "cost" be implemented? Options: (a) flat energy deduction from total graph energy, (b) $MIND token cost, (c) drive-based cost (applying "Red Bull" increases frustration risk). NLR decision needed. -->

<!-- @mind:proposition Consider letting the circadian rhythm parameters themselves evolve over time based on actual partner interaction patterns. If a partner consistently interacts at midnight, the citizen's circadian curve should shift to accommodate. This is v2+ territory. -->

<!-- @mind:todo Define the exact list of consumable types for v1. "Red Bull" and "Tisane" are examples — what is the canonical starter set? -->
