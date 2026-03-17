# IMPLEMENTATION — L1 Individual Cognition

**Module:** L1 Cognitive Substrate
**Area:** cognition
**Status:** STABLE (v1.0)

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_L1_Cognition.md
PATTERNS:        ./PATTERNS_L1_Cognition.md
BEHAVIORS:       ./BEHAVIORS_L1_Cognition.md
ALGORITHM:       ./ALGORITHM_L1_Physics.md
VALIDATION:      ./VALIDATION_L1_Cognition.md
THIS:            IMPLEMENTATION_L1_Cognition.md (you are here)
HEALTH:          ./HEALTH_L1_Cognition.md
SYNC:            ./SYNC_L1_Cognition.md

IMPL:            runtime/cognition/
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

```
runtime/cognition/
├── __init__.py
├── models.py                                  # Node, Link, LimbicState, WorkingMemory, CitizenCognitiveState
├── constants.py                               # ~110 physics constants, env-overridable
├── tick_runner_l1_cognitive_engine.py          # Law 12 orchestrator — runs all laws per tick
├── citizen_brain_seeder.py                     # Profile → initial brain graph
├── wm_prompt_serializer.py                     # WM state → first-person natural language
├── stimulus_router.py                          # External events → Stimulus objects
├── feedback_injector.py                        # Satisfaction/frustration injection
├── orientation_taxonomy.py                     # Orientation labels and mappings
├── falkordb_checkpointer.py                    # Persist/restore state to FalkorDB
├── brain_health_score_periodic_calculator.py   # Graph density, WM stability scoring
├── visual_memory.py                            # Image URI + CLIP embedding handling
└── laws/
    ├── __init__.py                             # Re-exports: Stimulus, ImpulseResult, etc.
    ├── law_01_energy_injection.py              # Law 1: dual-channel injection, dedup, self-stimulus
    ├── law_02_propagation.py                   # Law 2: surplus spill-over through compatible links
    ├── law_03_energy_decay.py                  # Law 3: energy decay + state decay multiplier
    ├── law_04_attentional_competition.py       # Law 4: WM selection with arousal moat
    ├── law_05_coactivation_reinforcement.py    # Law 5: Hebbian co-activation link strengthening
    ├── law_06_consolidation.py                 # Law 6: utility-gated weight growth
    ├── law_07_forgetting.py                    # Law 7: weight decay, link dissolution
    ├── law_09_inhibition.py                    # Law 9: conflict suppression
    ├── law_13_to_18_limbic_engine.py           # Laws 13-18: limbic orchestrator (drives, emotions)
    ├── law_17_impulse.py                       # Law 17: desire activation + impulse accumulation
    └── law_18_relational_valence.py            # Law 18: trust, affinity, friction on links
```

### File Responsibilities

| File | Purpose | Key Types/Functions | Status |
|------|---------|---------------------|--------|
| `models.py` | Core dataclasses | `Node`, `Link`, `LimbicState`, `WorkingMemory`, `CitizenCognitiveState`, 7 `NodeType`, 14 `LinkType`, 8 `DriveName`, 6 `EmotionName` | STABLE |
| `constants.py` | Physics constants | ~110 constants, all `L1_` env-overridable | STABLE |
| `tick_runner_l1_cognitive_engine.py` | Law 12 orchestrator | `run_tick()`, `_compute_orientation()` | STABLE |
| `citizen_brain_seeder.py` | Brain initialization | `generate_citizen_brain()`, `load_brain_into_state()` | STABLE |
| `wm_prompt_serializer.py` | State → language | `serialize_wm_to_prompt()` | STABLE |
| `laws/law_01_energy_injection.py` | Energy injection | `inject_energy()`, `Stimulus` | STABLE |
| `laws/law_13_to_18_limbic_engine.py` | Limbic orchestrator | `update_limbic()`, Laws 13-16 + delegates 17-18 | STABLE |
| `laws/law_17_impulse.py` | Desire + impulse | `update_impulse()`, `goal_proximity()`, `narrative_legitimacy()` | STABLE |
| `laws/law_18_relational_valence.py` | Relational valence | `update_relational_valence()`, `update_link_valence()` | STABLE |

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Law-per-module with tick orchestrator.

Each law is a pure function: `(state, tick, ...) → result`. The tick runner (`tick_runner_l1_cognitive_engine.py`) calls each law in sequence per tick. Laws that grow complex enough get their own module (Law 17, Law 18); others stay inline in the limbic engine (Laws 13-16).

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Try-import degradation | tick_runner → all law modules | Engine runs even if a law module is missing |
| Delegate to standalone | law_13_to_18 → law_17, law_18 | Keep limbic engine manageable, full spec in dedicated modules |
| Env-overridable constants | constants.py | Tune physics without code changes |
| Dataclass state | models.py | Immutable-friendly, serializable cognitive state |

---

## ENTRY POINTS

| Entry Point | File | Triggered By |
|-------------|------|--------------|
| `run_tick()` | `tick_runner_l1_cognitive_engine.py` | Dispatcher per-citizen tick loop |
| `inject_energy()` | `laws/law_01_energy_injection.py` | External stimulus arrival |
| `update_limbic()` | `laws/law_13_to_18_limbic_engine.py` | Called by `run_tick()` |
| `update_impulse()` | `laws/law_17_impulse.py` | Called by limbic engine |
| `update_relational_valence()` | `laws/law_18_relational_valence.py` | Called by limbic engine |
| `serialize_wm_to_prompt()` | `wm_prompt_serializer.py` | Prompt assembly before LLM call |
| `generate_citizen_brain()` | `citizen_brain_seeder.py` | Citizen creation/spawn |

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
tick_runner_l1_cognitive_engine.py
    ├── models.py (CitizenCognitiveState, Node, Link, ...)
    ├── constants.py (all physics constants)
    └── laws/
        ├── law_01_energy_injection.py
        ├── law_02_propagation.py
        ├── law_03_energy_decay.py
        ├── law_04_attentional_competition.py
        ├── law_05_coactivation_reinforcement.py
        ├── law_06_consolidation.py
        ├── law_07_forgetting.py
        ├── law_09_inhibition.py
        └── law_13_to_18_limbic_engine.py
            ├── law_17_impulse.py
            └── law_18_relational_valence.py
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `numpy` | Vector math (cosine similarity, embeddings) | law_13_to_18, law_17, law_04 |
| `falkordb` | Graph persistence | falkordb_checkpointer |

---

## MISSING LAWS

Laws 8, 10, 11, 14b, 19, 20, 21 are specified in ALGORITHM but not yet implemented as standalone modules:

| Law | Name | Status |
|-----|------|--------|
| 8 | Emotional Contagion | Inline in tick_runner |
| 10 | Crystallization | Not implemented |
| 11 | Orientation | Inline in tick_runner (`_compute_orientation`) |
| 19 | Budget-Aware Tick | Handled by orchestrator, not cognition |
| 20 | Prospective Simulation | Not implemented |
| 21 | Vertical Membrane | Not implemented |
