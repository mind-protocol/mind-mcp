# Metabolism — Implementation: Code Architecture and Structure

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Metabolism.md
BEHAVIORS:       ./BEHAVIORS_Metabolism.md
PATTERNS:        ./PATTERNS_Metabolism.md
ALGORITHM:       ./ALGORITHM_Metabolism.md
VALIDATION:      ./VALIDATION_Metabolism.md
THIS:            IMPLEMENTATION_Metabolism.md (you are here)
HEALTH:          ./HEALTH_Metabolism.md
SYNC:            ./SYNC_Metabolism.md

IMPL:            runtime/cognition/metabolism.py (to be created)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

```
runtime/cognition/
├── metabolism.py                              # Core: data structures, resolution, consumable management
├── metabolism_consumable_registry.py          # Consumable definitions (starter set + extensibility)
├── tick_runner_l1_cognitive_engine.py         # MODIFIED: accepts EffectiveConstants
├── constants.py                              # UNCHANGED: global defaults remain as-is
├── models.py                                 # MODIFIED: CitizenCognitiveState gains metabolism field
└── tests/
    └── test_metabolism.py                     # Unit tests for metabolism resolution and consumable logic
```

### File Responsibilities

| File | Purpose | Key Functions/Classes | Lines (est.) | Status |
|------|---------|----------------------|-------|--------|
| `metabolism.py` | Core metabolism logic: data structures, circadian computation, modifier processing, effective constant resolution, consumable application | `CitizenMetabolism`, `EffectiveConstants`, `Modifier`, `resolve_effective_constants()`, `apply_consumable()`, `apply_stimulus_sensitivity()` | ~300 | NEW |
| `metabolism_consumable_registry.py` | Consumable type definitions and registry | `ConsumableDefinition`, `CONSUMABLE_REGISTRY` | ~80 | NEW |
| `tick_runner_l1_cognitive_engine.py` | Tick orchestration — reads EffectiveConstants | `L1CognitiveTickRunner` | ~960 (current) | MODIFY |
| `constants.py` | Global default constants | (no changes) | ~238 (current) | UNCHANGED |
| `models.py` | Data models — adds metabolism field to CitizenCognitiveState | `CitizenCognitiveState` | ~400 (current) | MODIFY |

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Parameter Overlay

**Why this pattern:** The metabolism is a pure function: (CitizenMetabolism, time, tick) -> EffectiveConstants. No side effects beyond modifier tick-down and audit logging. This makes it testable, predictable, and isolated from the tick runner's complexity.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Null Object | `resolve_effective_constants(metabolism=None)` | Returns global defaults when no metabolism configured — backward compatibility |
| Registry | `CONSUMABLE_REGISTRY` | Consumable types are looked up by name from a central registry, not hardcoded in application logic |
| Append-Only Log | `ConsumableEvent` list on `CitizenMetabolism` | Audit trail that is never modified, only extended |

### Anti-Patterns to Avoid

- **Global state mutation**: Tempting to modify `constants.py` values at module load. Never do this — every citizen in the process shares those globals.
- **Lazy initialization of EffectiveConstants**: The constants must be fully resolved BEFORE the tick starts. Don't lazily compute them during Law 1 or Law 3 execution — that creates race conditions and makes debugging impossible.
- **Consumable logic in the tick runner**: The tick runner should not know about consumable names, cooldowns, or durations. It receives a flat EffectiveConstants struct. All consumable logic stays in metabolism.py.

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Metabolism resolution | Circadian math, modifier processing, clamping | Tick runner, law implementations | `EffectiveConstants` struct |
| Consumable management | Application, cooldown checking, audit logging | Tick runner, external MCP tools | `apply_consumable()` function |
| Stimulus sensitivity | Gain lookup, budget scaling | Law 1 injection logic | `apply_stimulus_sensitivity()` function |

---

## SCHEMA

### CitizenMetabolism (Persisted on Actor Node)

```yaml
CitizenMetabolism:
  required:
    - timezone_offset: float       # hours from UTC
  optional:
    - circadian_amplitude: float   # [0.0, 1.0], default 0.4
    - sensitivity: dict[str, float]  # per-stimulus-type gains
    - channel_gains: dict[str, float]  # per-MCP-tool gains
    - base_decay_rate: float       # citizen-specific decay override
    - base_moat: float             # citizen-specific moat override
    - base_consolidation_alpha: float  # citizen-specific consolidation override
    - base_arousal_baseline: float # citizen-specific arousal offset
    - active_modifiers: list[Modifier]  # currently active consumables
    - cooldowns: dict[str, int]    # consumable_type -> last_applied_tick
    - consumable_log: list[ConsumableEvent]  # audit trail
  constraints:
    - circadian_amplitude in [0.0, 1.0]
    - all sensitivity values in [0.0, 3.0]
    - all channel_gains values in [0.0, 3.0]
    - active_modifiers length <= 10 (sanity cap)
```

### EffectiveConstants (Transient, Per-Tick)

```yaml
EffectiveConstants:
  required:
    - decay_rate: float             # [0.001, 0.5]
    - long_term_decay: float        # [0.0001, 0.01]
    - consolidation_alpha: float    # [0.001, 0.1]
    - consolidation_beta: float     # [0.001, 0.05]
    - theta_base_wm: float         # [0.0, 20.0]
    - arousal_moat_coeff: float    # [0.0, 5.0]
    - boredom_moat_coeff: float    # [0.0, 10.0]
    - frustration_moat_coeff: float # [0.0, 5.0]
    - arousal_baseline_offset: float # [-0.3, 0.3]
    - arousal_dampening: float      # [0.3, 1.5]
  constraints:
    - All values within their documented ranges
    - All values are finite (no NaN, no inf)
```

---

## ENTRY POINTS

| Entry Point | File:Function | Triggered By |
|-------------|-----------|--------------|
| Constant resolution | `metabolism.py:resolve_effective_constants()` | Tick runner, at start of each tick |
| Stimulus scaling | `metabolism.py:apply_stimulus_sensitivity()` | Law 1 injection, when stimulus arrives |
| Consumable application | `metabolism.py:apply_consumable()` | MCP tool call or citizen self-administration |
| Consumable query | `metabolism.py:get_metabolic_summary()` | Prompt assembly, citizen introspection |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

### Flow 1: Per-Tick Constant Resolution

This flow runs once per tick before any law executes. It transforms the citizen's metabolic profile + current time into a flat constants struct.

```yaml
flow:
  name: constant_resolution
  purpose: Produce per-citizen effective constants for the tick runner
  scope: metabolism.py -> tick_runner
  steps:
    - id: step_1_circadian
      description: Compute circadian phase from UTC time + timezone
      file: runtime/cognition/metabolism.py
      function: compute_circadian_phase()
      input: timezone_offset (float), current_time_utc (float)
      output: phase (float, 0.0-1.0)
      trigger: tick start
      side_effects: updates metabolism.circadian_phase
    - id: step_2_modifiers
      description: Tick down active modifiers, expire finished ones
      file: runtime/cognition/metabolism.py
      function: process_modifiers()
      input: CitizenMetabolism.active_modifiers
      output: surviving modifiers, expiry events
      trigger: tick start
      side_effects: modifies active_modifiers list, appends to consumable_log
    - id: step_3_compose
      description: Compose all modifiers into EffectiveConstants
      file: runtime/cognition/metabolism.py
      function: resolve_effective_constants()
      input: base constants, circadian multipliers, consumable effects
      output: EffectiveConstants
      trigger: tick start
      side_effects: none (pure computation after modifier processing)
  docking_points:
    available:
      - id: dock_circadian_phase
        type: custom
        direction: output
        file: runtime/cognition/metabolism.py
        function: compute_circadian_phase()
        trigger: tick start
        payload: float (phase 0.0-1.0)
        async_hook: not_applicable
        needs: none
        notes: Observable for health checks — phase should follow a smooth sinusoid
      - id: dock_effective_constants
        type: custom
        direction: output
        file: runtime/cognition/metabolism.py
        function: resolve_effective_constants()
        trigger: tick start
        payload: EffectiveConstants dataclass
        async_hook: not_applicable
        needs: none
        notes: Primary output — all constants for this tick
      - id: dock_modifier_expiry
        type: event
        direction: output
        file: runtime/cognition/metabolism.py
        function: process_modifiers()
        trigger: modifier reaches ticks_remaining=0
        payload: ConsumableEvent
        async_hook: optional
        needs: none
        notes: Useful for tracking consumable lifecycle
    health_recommended:
      - dock_id: dock_effective_constants
        reason: All effective constants must be in valid ranges (V2)
      - dock_id: dock_circadian_phase
        reason: Phase must be continuous and in [0, 1] (V8)
```

### Flow 2: Consumable Application

Triggered by citizen action (via MCP tool or internal decision). Validates cooldown, creates modifier, logs event.

```yaml
flow:
  name: consumable_application
  purpose: Apply a temporary physics modifier to a citizen
  scope: external trigger -> metabolism.py
  steps:
    - id: step_1_validate
      description: Check cooldown and active modifier constraints
      file: runtime/cognition/metabolism.py
      function: apply_consumable()
      input: consumable_type (str), current_tick (int)
      output: (success: bool, reason: str)
      trigger: MCP tool call or citizen self-administration
      side_effects: none if rejected
    - id: step_2_apply
      description: Create Modifier and add to active_modifiers
      file: runtime/cognition/metabolism.py
      function: apply_consumable()
      input: ConsumableDefinition from registry
      output: Modifier added to active_modifiers
      trigger: validation success
      side_effects: modifies active_modifiers, cooldowns, consumable_log
  docking_points:
    available:
      - id: dock_consumable_result
        type: event
        direction: output
        file: runtime/cognition/metabolism.py
        function: apply_consumable()
        trigger: consumable application attempt
        payload: ConsumableEvent
        async_hook: optional
        needs: none
        notes: Every application attempt is logged (success or failure)
    health_recommended:
      - dock_id: dock_consumable_result
        reason: Audit trail completeness (V7), cooldown enforcement (V5)
```

---

## LOGIC CHAINS

### LC1: Tick-Start Metabolism Resolution

**Purpose:** Resolve effective constants before the tick runner executes any law.

```
tick_runner.run_tick()
  -> metabolism.resolve_effective_constants(state.metabolism, time.time(), state.tick_count)
    -> compute_circadian_phase(tz_offset, utc_time)
    -> circadian_multipliers(phase, amplitude)
    -> process_modifiers(metabolism, tick)
    -> compose + clamp
    -> EffectiveConstants
  -> tick_runner uses EffectiveConstants for all law executions
```

**Data transformation:**
- Input: `CitizenMetabolism` + `float (utc_time)` + `int (tick_count)` — raw metabolic profile
- After circadian: `dict` of multipliers — time-aware modifiers
- After modifiers: `dict` of cumulative effects — all modifiers composed
- Output: `EffectiveConstants` — flat, clamped, ready for tick runner

### LC2: Stimulus Sensitivity at Injection

**Purpose:** Scale stimulus energy before Law 1 processes it.

```
stimulus arrives
  -> metabolism.apply_stimulus_sensitivity(state.metabolism, stimulus.source, stimulus.tool, stimulus.budget)
    -> lookup gain in channel_gains or sensitivity
    -> scale budget
  -> law_01_energy_injection.inject_energy(state, modified_stimulus)
```

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
metabolism.py
    └── imports -> constants.py (global defaults for fallback)
    └── imports -> metabolism_consumable_registry.py (consumable definitions)

tick_runner_l1_cognitive_engine.py
    └── imports -> metabolism.py (resolve_effective_constants, apply_stimulus_sensitivity)
    └── imports -> constants.py (for any non-metabolized constants)

models.py
    └── imports -> metabolism.py (CitizenMetabolism type for state field)
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `math` (stdlib) | `cos()` for circadian curve | `metabolism.py` |
| `time` (stdlib) | UTC timestamp | `metabolism.py` |
| `dataclasses` (stdlib) | Data structure definitions | `metabolism.py` |

No external packages required. Pure Python stdlib.

---

## STATE MANAGEMENT

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| CitizenMetabolism | `CitizenCognitiveState.metabolism` | Per-citizen | Created on citizen birth or profile setup; persisted via FalkorDB checkpoint |
| EffectiveConstants | Local variable in `run_tick()` | Per-tick | Created at tick start, discarded at tick end |
| ConsumableEvent log | `CitizenMetabolism.consumable_log` | Per-citizen | Append-only, persisted with metabolism |

### State Transitions

```
No metabolism ──(citizen profile setup)──> CitizenMetabolism created
    |
    v
Each tick: resolve_effective_constants() produces transient EffectiveConstants
    |
    v
Consumable applied: Modifier added to active_modifiers, cooldown recorded
    |
    v
Each tick: active modifiers tick down, expired ones removed
```

---

## RUNTIME BEHAVIOR

### Initialization

```
1. Citizen loads from FalkorDB checkpoint
2. CitizenCognitiveState.metabolism is deserialized (or None for legacy citizens)
3. Tick runner initialized with state (which includes metabolism)
```

### Main Loop (Per-Tick Integration)

```
1. RESOLVE: effective = resolve_effective_constants(state.metabolism, utc_time, tick)
2. INJECT:  if stimulus, apply_stimulus_sensitivity() to scale budget, then Law 1
3. All other laws use effective.decay_rate, effective.theta_base_wm, etc.
4. (Laws that don't have metabolized constants use globals from constants.py as before)
```

### Shutdown

```
1. CitizenMetabolism (including active_modifiers and consumable_log) checkpointed to FalkorDB
2. No cleanup needed — all state is on CitizenCognitiveState
```

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `L1_METABOLISM_ENABLED` | env var | `true` | Master switch: if false, all citizens use global constants |
| Consumable definitions | `metabolism_consumable_registry.py` | See ALGORITHM doc | Which consumables exist and their parameters |
| Per-citizen metabolism | FalkorDB actor node properties | `None` | Each citizen's metabolic profile |

---

## BIDIRECTIONAL LINKS

### Code -> Docs

Files that should reference this documentation:

| File | Reference |
|------|-----------|
| `runtime/cognition/metabolism.py` | `# DOCS: docs/cognition/metabolism/` |
| `runtime/cognition/metabolism_consumable_registry.py` | `# DOCS: docs/cognition/metabolism/ALGORITHM_Metabolism.md` |
| `runtime/cognition/tick_runner_l1_cognitive_engine.py` | `# DOCS: docs/cognition/metabolism/ (metabolism integration)` |

### Docs -> Code

| Doc Section | Implemented In |
|-------------|----------------|
| ALGORITHM resolve_effective_constants | `metabolism.py:resolve_effective_constants()` |
| ALGORITHM apply_stimulus_sensitivity | `metabolism.py:apply_stimulus_sensitivity()` |
| ALGORITHM apply_consumable | `metabolism.py:apply_consumable()` |
| ALGORITHM compute_circadian_phase | `metabolism.py:compute_circadian_phase()` |
| BEHAVIOR B1 | `metabolism.py:circadian_multipliers()` |
| BEHAVIOR B3 | `metabolism.py:apply_consumable()` |
| VALIDATION V1 | `tests/test_metabolism.py:test_global_constants_immutable` |
| VALIDATION V2 | `tests/test_metabolism.py:test_effective_constants_ranges` |
| VALIDATION V3 | `tests/test_metabolism.py:test_none_metabolism_returns_defaults` |

---

## EXTRACTION CANDIDATES

No extraction needed — the module starts clean with two focused files. Monitor `metabolism.py` if it grows past 400 lines; likely extraction candidates would be circadian logic into its own file.

---

## MARKERS

<!-- @mind:todo The tick runner integration requires modifying L1CognitiveTickRunner to accept EffectiveConstants. This is the most delicate change — must preserve all existing behavior when metabolism is None. -->

<!-- @mind:todo FalkorDB serialization of CitizenMetabolism: need to define how active_modifiers and consumable_log are stored as node properties. Likely JSON-serialized strings. -->

<!-- @mind:proposition Consider making metabolism.py a standalone module (runtime/cognition/metabolism/) with __init__.py exporting the public API. This would be cleaner if the module grows. -->
