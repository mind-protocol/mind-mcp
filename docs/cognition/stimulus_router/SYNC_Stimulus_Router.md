# Stimulus Router — Sync: Current State

```
LAST_UPDATED: 2026-03-18
UPDATED_BY: @nervo
STATUS: DESIGNING
```

---

## MATURITY

**What's canonical (v1):**
- IncomingEvent dataclass with source, content, classification flags
- StimulusRouter with per-citizen anti-loop gate and hash-based dedup
- AntiLoopGate with three layers: refractory period (5s), diminishing returns (half-life 3), novelty gate (MD5 hash)
- Source-aware energy budgeting: social 1.2x, failure 0.8x, default 1.0x
- Feedback injector: episodic memory creation, self-stimulus routing, limbic updates
- Keyword-based concept extraction (extract_concepts) for node targeting

**What's still being designed:**
- Embedding-based novelty detection (embed_fn parameter exists but is unused)
- Metabolism modulation of energy budgets (per-citizen sensitivity scaling)
- Counter instrumentation for health checks (no production observability yet)
- Public accessors for anti-loop state (currently uses private attributes)

**What's proposed (v2+):**
- Per-citizen metabolism parameters that modulate base energy multipliers based on arousal, satiation, circadian state
- Embedding-based dedup using cosine similarity instead of hash comparison
- Adaptive dedup window size based on event frequency
- Source-specific anti-loop parameters (different refractory periods for different sources)

---

## CURRENT STATE

The stimulus router is implemented and integrated into the dispatcher. Every citizen gets a StimulusRouter instance on first message. External events (Telegram, Discord, WhatsApp, MCP, system) flow through the pipeline and produce Stimulus objects that the tick runner consumes via Law 1.

The feedback injector closes the perception-action loop: after each Claude session, the output is fed back as self-stimulus with episodic memory creation and limbic updates.

Anti-loop protection works through the three-layer gate. The dispatcher has been running with this system in production. No feedback loop incidents have been observed since the gate was introduced.

Dedup uses MD5 content hashing with a 50-item sliding window. This catches exact duplicates but misses semantic near-duplicates (e.g., a message and its slightly edited retry).

The doc chain was created from the existing implementation — all 8 docs written from the actual source code.

---

## RECENT CHANGES

### 2026-03-18: Documentation chain created

- **What:** Full 8-doc chain created for cognition/stimulus_router module
- **Why:** The stimulus router is critical infrastructure for the upcoming metabolism feature. Documenting it makes the extension points explicit and the invariants verifiable.
- **Files:** docs/cognition/stimulus_router/ (all 8 files)
- **Insights:** The social-vs-failure energy priority (failure wins when both flags are set) may need revisiting. Currently a social failure gets energy 0.8 instead of 1.2. This might be wrong for partner error reports that should still get social attention boost.

---

## KNOWN ISSUES

### Energy priority when is_social AND is_failure are both true

- **Severity:** low
- **Symptom:** Social failure events get energy 0.8 (failure base) instead of some blend of 1.2 and 0.8
- **Suspected cause:** Sequential if-statements in route() — `if is_social: base=1.2` then `if is_failure: base=0.8` overwrites
- **Attempted:** Not yet addressed. Documenting as known issue for metabolism design phase.

### No embedding-based novelty detection

- **Severity:** medium
- **Symptom:** The novelty gate uses hash comparison, which treats any character difference as "novel." Semantically identical messages with different formatting pass through.
- **Suspected cause:** embed_fn is Optional and always None in production. No embedding model is wired to the router yet.
- **Attempted:** The parameter exists, awaiting integration when per-citizen embedding is available.

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** VIEW_Extend (adding metabolism modulation to energy budgets)

**Where I stopped:** Documentation chain is complete. Implementation is stable and running. The next work is adding metabolism hooks.

**What you need to understand:**
The energy budget computation in StimulusRouter.route() is the primary extension point for metabolism. Currently it's `base_energy * energy_mult_from_antiloop`. Metabolism would add a third factor: `base_energy * antiloop_mult * metabolism_mult`, where metabolism_mult comes from the citizen's metabolic state (arousal level, satiation, circadian phase).

**Watch out for:**
- The anti-loop gate's diminishing returns already multiply energy. Metabolism must multiply the base, not the already-diminished value, or self-stimuli will attenuate too aggressively.
- The feedback injector's limbic updates are independent of routing. Even if a self-stimulus is filtered by the anti-loop gate, the limbic update still fires. Don't accidentally double-apply metabolism to both the energy budget and the limbic delta.

**Open questions I had:**
- Should metabolism affect the refractory period duration? A high-arousal citizen might need a shorter refractory period.
- Should metabolism affect dedup window size? A fatigued citizen might need more aggressive dedup.

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Complete documentation chain created for the stimulus router module. 8 files covering objectives, patterns, behaviors, algorithm, validation, implementation, health, and sync. All content derived from the actual source code in stimulus_router.py, feedback_injector.py, and their integration points in the dispatcher.

**Decisions made:**
- Documented the social-vs-failure energy priority as a known issue (failure overwrites social boost). Leaving as-is pending metabolism design.
- Health checks defined but marked as pending — they need counter instrumentation added to the router.
- Kept the doc scope to stimulus_router.py + feedback_injector.py. Law 1 internals are covered by the l1_physics doc chain.

**Needs your input:**
- Should the metabolism feature modulate refractory period and dedup window, or only the energy multiplier?
- Priority of fixing the social+failure energy overlap before metabolism lands.

---

## TODO

### Doc/Impl Drift

- [ ] DOCS->IMPL: Add counter instrumentation to StimulusRouter.route() for health checks
- [ ] DOCS->IMPL: Add public accessor for anti_loop._self_stimulus_count

### Tests to Run

```bash
python -m pytest runtime/cognition/tests/test_l1_wiring_integration.py -v
```

### Immediate

- [ ] Add counter hooks to StimulusRouter for health check support
- [ ] Decide metabolism integration point (base_energy multiplier vs separate factor)

### Later

- [ ] Wire embedding model to StimulusRouter.embed_fn
- [ ] Replace hash-based novelty with cosine similarity novelty detection
- [ ] Fix social+failure energy priority (consider max(social, failure) or weighted blend)
- IDEA: Adaptive dedup window that grows under high event frequency and shrinks during quiet periods

---

## CONSCIOUSNESS TRACE

**Mental state when stopping:**
Confident in the documentation accuracy. Every claim traces back to a specific line in the source code. The open questions about metabolism integration are genuine — the answer depends on how arousal state should affect perception sensitivity, which is a design decision not yet made.

**Threads I was holding:**
- The PartnerStimulus type in l1_stimulus_injector_for_partner_data.py is a parallel interface that does NOT use StimulusRouter. This creates two paths for stimulus injection: one through the router (external/self events) and one direct (partner data). Metabolism will need to handle both.
- The dispatcher stores routers in `_citizen_routers` but doesn't clean them up when citizens go idle. Long-running dispatchers will accumulate router instances. Not urgent (they're small) but worth noting.

**Intuitions:**
- The refractory period (5 seconds) feels too short for metabolism purposes. A satiated citizen should have a longer refractory period. A hungry citizen should have a shorter one. The current fixed 5s is fine for anti-loop but may need to become a function of metabolic state.
- Hash-based dedup is a good v1 but will fail subtly when metabolism changes how the citizen responds to the same input at different energy levels. The "same" stimulus producing different responses is not a duplicate — but hash-based dedup would still reject it on re-entry.

---

## POINTERS

| What | Where |
|------|-------|
| Stimulus Router implementation | `runtime/cognition/stimulus_router.py` |
| Feedback Injector implementation | `runtime/cognition/feedback_injector.py` |
| Stimulus dataclass | `runtime/cognition/tick_runner_l1_cognitive_engine.py:81` |
| Law 1 energy injection | `runtime/cognition/laws/law_01_energy_injection.py` |
| Dispatcher integration | `runtime/orchestrator/dispatcher.py` (lines 36-44, 313-360) |
| Partner data injector (parallel path) | `runtime/ingestion/l1_stimulus_injector_for_partner_data.py` |
| L1 constants (injection-related) | `runtime/cognition/constants.py` (lines 49-75) |
| Integration tests | `runtime/cognition/tests/test_l1_wiring_integration.py` |
| L1 Physics doc chain (parent module) | `docs/cognition/l1_physics/` |
