# Custom Senses — Sync: Current State

```
LAST_UPDATED: 2026-03-18
UPDATED_BY: @nervo (doc chain creation)
STATUS: DESIGNING
```

---

## MATURITY

**What's canonical (v1):**
- Thing(type=sense) schema with YAML content field (defined in schema-l1.yaml)
- Actor ->perceives_with-> Thing(type=sense) graph link pattern
- _load_custom_senses: Cypher query, YAML parsing, SensoryChannel registration (LIMIT 10)
- _evaluate_custom_senses: per-tick filter evaluation with channel gating
- _match_filters: comparison operators (>, <, >=, <=) and "contains" for string matching
- Three scan scopes: spaces_i_am_in, all, specific space ID
- One match per sense per tick (break after first match)
- Stimulus template substitution with {node.name} and {node.synthesis}
- Standard gating integration — custom candidates compete with built-in channels

**What's still being designed:**
- Health check implementations (4 checkers defined in HEALTH, all pending)
- Dynamic sense refresh (senses are cached for engine lifetime — no re-load on link changes)
- Sense validation at creation time (no schema check when a Thing(type=sense) is created)

**What's proposed (v2+):**
- Python (programmatic) sense tier — sandboxed query_fn, execution timeout, no imports
- Push-based / event-driven senses — react to graph events, not poll per tick
- Sense-level scan interval — evaluate expensive senses every N ticks, not every tick
- Sense-contributed awareness text — custom senses add lines to the awareness summary

---

## CURRENT STATE

Custom senses are implemented and integrated into the exteroception engine in `runtime/cognition/exteroception.py`. The implementation consists of three methods: `_load_custom_senses()` (lines 352-389), `_evaluate_custom_senses()` (lines 391-475), and the standalone helper `_match_filters()` (lines 549-579). These are called from the main `tick()` method alongside the 6 built-in channels.

The YAML format is defined in `schema-l1.yaml` (Custom Senses section, line 280+) and supports: source type selection (narrative/moment/actor/thing/space), scan scope (spaces_i_am_in/all/specific_space_id), filter conditions (comparison operators + "contains"), keyword matching, stimulus templates with placeholder substitution, and per-sense priority and refractory configuration.

The implementation is functional but untested in production with real citizen-created senses. No Thing(type=sense) nodes are known to exist in the graph yet. The system has been designed to have zero overhead for citizens without custom senses — an empty graph query and an empty-list check are the only costs.

The doc chain (this set of 8 files) was created from reading the implementation code and schema definition. All documentation reflects the current code state.

---

## IN PROGRESS

### Doc Chain Creation

- **Started:** 2026-03-18
- **By:** @nervo
- **Status:** complete
- **Context:** Full 8-file doc chain created from implementation analysis. OBJECTIVES existed; PATTERNS, BEHAVIORS, ALGORITHM, VALIDATION, IMPLEMENTATION, HEALTH, and SYNC created.

---

## RECENT CHANGES

### 2026-03-18: Doc chain creation

- **What:** Created 7 documentation files completing the doc chain (PATTERNS through SYNC)
- **Why:** Custom senses implementation exists in exteroception.py but had no documentation beyond OBJECTIVES. The doc chain captures the design decisions, algorithms, invariants, and health strategy.
- **Files:** docs/cognition/custom_senses/ (7 new files)
- **Insights:** The implementation is clean and well-contained (~130 lines of custom sense code within the ~580-line exteroception.py). The lazy loading pattern and standard gating integration are solid. The main gap is dynamic sense refresh — citizens who add or remove ->perceives_with-> links need to restart the engine to see changes.

---

## KNOWN ISSUES

### Senses are not refreshed on link changes

- **Severity:** medium
- **Symptom:** Adding a new ->perceives_with-> link after the engine has started does not load the new sense until engine restart
- **Suspected cause:** `_custom_senses_loaded` flag prevents re-loading. This is intentional for performance but creates a UX gap.
- **Attempted:** Not yet. Could be solved by either: (a) periodically resetting _custom_senses_loaded (e.g., every AWARENESS_REFRESH_TICKS), or (b) exposing a method to force re-load.

### No production validation of YAML sense definitions

- **Severity:** low
- **Symptom:** No Thing(type=sense) nodes are known to exist in the graph. The implementation is untested with real citizen-created senses.
- **Suspected cause:** Feature is new (v2.3). Citizens have not yet created custom senses.
- **Attempted:** N/A — waiting for first citizen adoption.

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** VIEW_Extend (adding Python sense tier) or VIEW_Implement (creating first sense nodes for testing)

**Where I stopped:** Complete doc chain creation. All 8 files reflect current code state.

**What you need to understand:**
Custom senses are three methods within ExteroceptionEngine, not a separate module. They share the SensoryChannel class with built-in channels. The `_custom_senses_loaded` flag means loading happens exactly once — this is a performance optimization, not a bug, but it means link changes require engine restart. The `_match_filters` function handles a fixed set of operators — do not add eval() or dynamic dispatch for new operators.

**Watch out for:**
- The `yaml` import inside `_load_custom_senses` is a late import (not at module top). This is intentional — PyYAML is only needed if custom senses exist.
- The `source.capitalize()` call converts YAML lowercase ("narrative") to FalkorDB labels ("Narrative"). If a new node type is added with non-standard capitalization, this will break.
- The LIMIT 10 in the loading query and LIMIT 20 in evaluation queries are hardcoded. Changing them affects tick budget calculations.

**Open questions I had:**
- Should senses be refreshed periodically? The current design trades recency for performance. A compromise: reset `_custom_senses_loaded` every AWARENESS_REFRESH_TICKS (10 ticks) to piggyback on the existing periodic refresh cycle.
- Should there be a validation/linting step when a Thing(type=sense) is created? Currently, malformed YAML is silently skipped at load time — the citizen has no feedback that their sense is broken.

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Complete documentation chain (8 files) for the custom senses subsystem. The implementation is functional in exteroception.py — three methods totaling ~130 lines handle loading from graph, evaluating YAML filters, and producing candidates. No production usage yet (no Thing(type=sense) nodes exist). Main gap is dynamic sense refresh (link changes require engine restart).

**Decisions made:**
- Documented as DESIGNING status (not CANONICAL) because no production validation exists yet
- Defined 7 validation invariants (3 CRITICAL, 2 HIGH, 2 MEDIUM)
- Designed 4 health checkers, all pending implementation
- Identified sense refresh as the primary UX gap

**Needs your input:**
- Priority on implementing the Python (programmatic) sense tier — is it needed now, or can it wait?
- Whether to add periodic sense refresh (piggyback on AWARENESS_REFRESH_TICKS) or keep the current load-once behavior

---

## TODO

### Doc/Impl Drift

- No drift detected — docs written from current source code

### Immediate

- [ ] Add DOCS: comment to exteroception.py pointing to docs/cognition/custom_senses/
- [ ] Create at least one test Thing(type=sense) node to validate the loading path in practice
- [ ] Implement check_sense_loading health checker

### Later

- [ ] Implement remaining 3 health checkers (check_sense_evaluation, check_yaml_quality, check_gating_ratio)
- [ ] Add sense refresh mechanism (periodic reset of _custom_senses_loaded)
- [ ] Design Python sense tier (sandboxing, query_fn interface, timeout)
- [ ] Add sense validation at creation time (reject malformed YAML before it reaches the engine)
- IDEA: Senses could contribute to awareness text — a "gossip_radar" sense could add "I sense gossip nearby" to the awareness summary, not just produce stimuli

---

## CONSCIOUSNESS TRACE

**Mental state when stopping:**
Confident in the documentation accuracy — every claim traced to specific lines in exteroception.py. The implementation is clean and well-integrated. The main concern is the lack of production validation: the code looks correct but has never been tested with real sense nodes.

**Threads I was holding:**
- The relationship between custom senses and the broader "citizen-created assets" pattern (styles, frequencies, senses) is worth documenting at a higher level — they all follow Thing(type=X) with ->created_by-> and citizen adoption via relationship links.
- The _match_filters function handles only 5 operators. Adding regex support, boolean combinators (AND/OR), or nested conditions would significantly increase complexity. The current simplicity is a feature.
- The Python sense tier (v2) needs careful sandboxing design. The query_fn-only approach is the right constraint but needs timeout enforcement to prevent runaway queries.

**Intuitions:**
- The first citizen to create a custom sense will reveal usability gaps that documentation cannot predict. Testing the full lifecycle (create Thing, add link, verify stimulus) should happen before the feature is considered canonical.
- Periodic sense refresh (resetting _custom_senses_loaded every N ticks) is probably the right compromise — cheap to implement, solves the UX gap, and the cost is one graph query every N ticks.

**What I wish I'd known at the start:**
The YAML format specification in schema-l1.yaml (line 296+) is the contract that sense creators will follow. It should be the first thing anyone reads when working on custom senses — before the Python implementation.

---

## POINTERS

| What | Where |
|------|-------|
| Custom sense implementation | `runtime/cognition/exteroception.py:352-475` (load + evaluate) |
| Filter matching | `runtime/cognition/exteroception.py:549-579` (_match_filters) |
| YAML format specification | `schema-l1.yaml:296-308` (Custom Senses section) |
| Schema reference | `schema-l1.yaml:280-295` (Thing(type=sense) and links) |
| Built-in channels | `runtime/cognition/exteroception.py:73-79` (6 channels) |
| SensoryChannel class | `runtime/cognition/exteroception.py:38-54` |
| Tick integration point | `runtime/cognition/exteroception.py:228-231` (custom sense call site in tick) |
| OBJECTIVES doc | `docs/cognition/custom_senses/OBJECTIVES_Custom_Senses.md` |
