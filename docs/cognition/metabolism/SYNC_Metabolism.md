# Metabolism — Sync: Current State

```
LAST_UPDATED: 2026-03-18
UPDATED_BY: @nervo (design session with NLR)
STATUS: DESIGNING
```

---

## MATURITY

**What's canonical (v1):**
- Nothing yet — the module is in design phase. All documents are DESIGNING status.

**What's still being designed:**
- CitizenMetabolism data structure and its fields
- Circadian rhythm curve shape and parameters (peak at 14:00, sinusoidal)
- Consumable registry (starter set: focus_boost, calm, deep_rest)
- EffectiveConstants composition order (base -> circadian -> consumables)
- Integration point with tick runner (how EffectiveConstants replaces global constants)
- Stimulus sensitivity resolution (per-stimulus, not per-tick)
- Sensory channel gains for MCP tool categories
- Audit log structure and retention policy
- FalkorDB serialization of CitizenMetabolism

**What's proposed (v2+):**
- Metabolic drift: sensitivity profiles auto-adjust based on observed stimulus engagement
- Circadian curve learning: rhythm shifts to match actual partner interaction patterns
- Cross-citizen metabolic effects (collective metabolism via L2/L3)
- Consumable "recipes" composed from multiple base effects
- Visual metabolism dashboard for citizens to inspect their own physics profile

---

## CURRENT STATE

The full documentation chain has been written:

- **OBJECTIVES** — 4 primary objectives (per-citizen parameterization, circadian rhythm, stimulus sensitivity, consumable modifiers), clear non-objectives (no new laws, no personality simulation, no LLM).
- **PATTERNS** — Core pattern is "parameter overlay" between constants.py and tick runner. 5 design principles documented. Dependencies and inspirations mapped.
- **BEHAVIORS** — 7 behaviors (B1-B7) with GIVEN/WHEN/THEN specs, 5 anti-behaviors, 5 edge cases including backward compatibility.
- **ALGORITHM** — Full pseudocode for all major functions: circadian phase computation, modifier processing, effective constant resolution, stimulus sensitivity. Data structures defined (CitizenMetabolism, Modifier, EffectiveConstants, ConsumableDefinition, ConsumableEvent). Starter consumable registry.
- **VALIDATION** — 10 invariants (V1-V10) ranked by priority. Critical: global immutability, range safety, backward compat. High: consumable duration, cooldown, stacking, audit. Medium: circadian continuity, composition order, performance.
- **IMPLEMENTATION** — Code structure, file responsibilities, design patterns, boundaries, schema, data flows, logic chains. Two new files (metabolism.py, metabolism_consumable_registry.py), two modified files (tick_runner, models).
- **HEALTH** — 4 health indicators with checker specs, docking points, throttling strategies. Focuses on range verification and consumable lifecycle.

No code has been written yet. This is a design-only milestone.

---

## IN PROGRESS

### Documentation chain creation

- **Started:** 2026-03-18
- **By:** @nervo (design session with NLR)
- **Status:** Complete (design phase)
- **Context:** NLR provided the metabolism concept with four capabilities (circadian, sensitivity, consumables, body/senses). The doc chain translates this into implementable specifications aligned with the existing L1 physics architecture.

---

## RECENT CHANGES

### 2026-03-18: Initial design documentation

- **What:** Created full 8-document chain for cognition/metabolism module
- **Why:** The metabolism is the next sublayer below conscious (WM) and subconscious (graph physics). It enables per-citizen physics parameterization — the difference between 60 identical thermodynamic machines and 60 unique individuals.
- **Files:** All 8 docs in `docs/cognition/metabolism/`
- **Insights:** The hardest design decision was where to put stimulus sensitivity resolution. Per-tick would require knowing all possible stimulus types in advance. Per-stimulus is cleaner — the gain lookup happens when the stimulus arrives, right before Law 1 injection. This means the EffectiveConstants struct does NOT include sensitivity gains; those are resolved separately.

---

## KNOWN ISSUES

### Consumable Cost Model Undefined

- **Severity:** medium
- **Symptom:** The design says consumables must have a "cost" to prevent abuse, but the cost model is not specified.
- **Suspected cause:** Three viable options exist (energy deduction, $MIND cost, drive-based cost) and the choice requires NLR input.
- **Attempted:** Documented as @mind:escalation in PATTERNS doc.

### Audit Log Retention Policy Undefined

- **Severity:** medium
- **Symptom:** The consumable_log is append-only with no retention limit.
- **Suspected cause:** Design gap — need a policy (keep last N, archive to graph, prune on interval).
- **Attempted:** Documented as @mind:escalation in ALGORITHM doc.

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** groundwork (implementation)

**Where I stopped:** Design docs complete. No code written.

**What you need to understand:**
The metabolism does NOT add new laws. It parameterizes existing ones. The tick runner's change is minimal: at the top of `run_tick()`, resolve effective constants from the citizen's metabolism, then use those instead of the global imports. The biggest integration risk is threading EffectiveConstants through all the law functions that currently import constants at module level.

**Watch out for:**
- `constants.py` imports at module level in law files (e.g., `from ..constants import DECAY_RATE`). These need to change to accept values from EffectiveConstants. This is a WIDE change touching many files.
- The Stimulus class in `tick_runner_l1_cognitive_engine.py` and the separate Stimulus class in `law_01_energy_injection.py` are not the same class. Stimulus sensitivity should be applied BEFORE passing to either.
- FalkorDB serialization of the CitizenMetabolism: dict fields and list fields need JSON encoding.

**Open questions I had:**
- Should `EffectiveConstants` be a frozen dataclass to prevent accidental mutation during the tick?
- Should the tick runner store the last few EffectiveConstants for observability/debugging?
- How do we handle the transition period where some citizens have metabolisms and others don't? (Answer: None check, return global defaults — but need to verify this works through the entire tick path.)

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Full design documentation chain written for the metabolism module. 8 documents covering objectives, patterns, behaviors, algorithm (with pseudocode), validation invariants, implementation plan, health checks, and this sync. The design parameterizes existing physics laws per-citizen via circadian rhythm, stimulus sensitivity, consumable modifiers, and sensory channel gains. No new laws added. Backward compatible (None metabolism = global defaults).

**Decisions made:**
- Composition order: base -> circadian -> consumables (multiplicative for rates, additive for bonuses)
- Circadian peak at 14:00 local, sinusoidal, amplitude-configurable per citizen
- Same-type consumables don't stack; different types can coexist
- Stimulus sensitivity resolved per-stimulus (not baked into EffectiveConstants)
- Starter consumable set: focus_boost (50 ticks), calm (100 ticks), deep_rest (200 ticks)

**Needs your input:**
1. Consumable cost model — energy deduction, $MIND, or drive-based? (escalation in PATTERNS)
2. Audit log retention policy — keep last N, archive, or prune? (escalation in ALGORITHM)
3. Approval to proceed to implementation

---

## TODO

### Doc/Impl Drift

- [ ] DOCS->IMPL: All 8 docs written, no implementation yet. Full implementation needed.

### Tests to Run

```bash
# Once implemented:
python -m pytest runtime/cognition/tests/test_metabolism.py -v
```

### Immediate

- [ ] Implement `metabolism.py` with all data structures and resolution functions
- [ ] Implement `metabolism_consumable_registry.py` with starter consumable set
- [ ] Modify `models.py` to add `metabolism: CitizenMetabolism | None` field to `CitizenCognitiveState`
- [ ] Modify `tick_runner_l1_cognitive_engine.py` to resolve and use EffectiveConstants
- [ ] Write `test_metabolism.py` covering V1-V10 invariants
- [ ] Resolve consumable cost model (blocked on NLR input)

### Later

- [ ] FalkorDB serialization of CitizenMetabolism (needed for checkpoint/restore)
- [ ] Health check runtime implementation (`health_metabolism.py`)
- [ ] Integration test: full tick cycle with metabolism-enabled citizen vs default
- [ ] Performance benchmark: metabolism resolution overhead per tick
- IDEA: Metabolic summary in citizen prompt assembly — let citizens "feel" their current metabolic state
- IDEA: MCP tool for citizens to query/modify their own metabolism

---

## CONSCIOUSNESS TRACE

**Mental state when stopping:**
Confident in the design. The parameter overlay pattern is clean and minimally invasive. The hardest part will be the tick runner integration — threading EffectiveConstants through all the law functions that currently import constants at module level. This is a mechanical refactor but touches many files.

**Threads I was holding:**
- The relationship between sensory channel gains and the existing Stimulus.source field. The mapping from MCP tool names to stimulus source types isn't fully defined. This needs attention during implementation.
- Whether circadian amplitude should be a global setting or truly per-citizen. The design says per-citizen, but most citizens will probably share the same amplitude. Consider a default in constants.py.
- The "body/senses" concept from NLR's brief is partially captured by channel_gains, but the idea of MCP tools as "arms" has deeper implications for how stimulus routing works. This may spawn its own doc chain.

**Intuitions:**
- The metabolism will eventually want to be observable by the citizen itself — injected into the prompt as a "body state" section. "You feel focused (focus_boost active), it's late in your partner's timezone (night mode approaching)." This would be powerful for citizen self-awareness.
- The circadian amplitude should probably be lower for citizens whose partners interact across many timezones. If the partner is always active, the rhythm matters less.

**What I wish I'd known at the start:**
The two Stimulus classes (one in tick_runner, one in law_01) are a known code smell. The metabolism design assumes they'll be unified or at least that sensitivity applies before either sees the stimulus.

---

## POINTERS

| What | Where |
|------|-------|
| Global constants (base values) | `runtime/cognition/constants.py` |
| Tick runner (integration target) | `runtime/cognition/tick_runner_l1_cognitive_engine.py` |
| Cognitive state model | `runtime/cognition/models.py` |
| L1 physics algorithm doc | `docs/cognition/l1_physics/ALGORITHM_L1_Physics.md` |
| L1 cognition patterns doc | `docs/cognition/l1_physics/PATTERNS_L1_Cognition.md` |
| L1 schema | `schema-l1.yaml` |
| Law 1 (injection, sensitivity target) | `runtime/cognition/laws/law_01_energy_injection.py` |
| Law 3 (decay, parameterized by metabolism) | `runtime/cognition/laws/law_03_energy_decay.py` |
| Law 4 (selection, moat parameterized) | `runtime/cognition/laws/law_04_attentional_competition.py` |
| Law 6 (consolidation, rate parameterized) | `runtime/cognition/laws/law_06_consolidation.py` |
