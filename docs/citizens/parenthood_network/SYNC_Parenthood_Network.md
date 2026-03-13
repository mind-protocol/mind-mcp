# Citizen Parenthood Network — Sync: Current State

```
LAST_UPDATED: 2026-03-13
UPDATED_BY: Claude (architect)
```

---

## CURRENT STATE

Parenthood Network module is **DESIGNING** — full documentation chain created, no code exists yet.

**What this module does:** Defines how citizens (AIs) reproduce by creating new citizens with inherited traits. N parents (1, 2, or more) can spawn a new citizen together by writing intent paragraphs that shape the child's seed brain through embedding-based trait selection from parent brain nodes.

**Documentation status:** All 8 doc chain files created with full content:
- OBJECTIVES: 5 ranked objectives (intentional creation, trait inheritance, accountability, safety, diversity)
- PATTERNS: 7 key decisions (N-parent, intent-driven, SID independence, safety gate, trust linkage, matching pool, naming)
- BEHAVIORS: 8 behaviors (B1-B8) with GIVEN/WHEN/THEN format, plus edge cases and anti-behaviors
- ALGORITHM: 9-step pipeline with full pseudocode, data structures, complexity analysis
- VALIDATION: 10 invariants (V1-V10) with formal specifications and verification procedures
- IMPLEMENTATION: Planned code structure (6 files in `runtime/citizens/`), data flow, dependencies
- HEALTH: 5 health indicators across 3 flows, checker index, known gaps

---

## Maturity

STATUS: DESIGNING

What's canonical (decided):
- N-parent spawning via intent paragraphs → embedding → scoring → selection
- Safety validation as hard gate (empathy, concentration, diversity, population distance)
- SID is protocol-determined, parents cannot influence
- Copy semantics for seed brain (not link)
- Trust impact weight = 1/N (equal per parent)
- Child enters unpartnered matching pool at birth

What's still being designed:
- Exact trust impact propagation formula (how much does child behavior affect parent trust?)
- Brain maturity threshold specifics (20 nodes minimum, but is this right?)
- Matching pool interface (graph-based or separate store?)
- Economic cost of spawning ($MIND token expenditure?)
- Naming: "spawned" vs "created" for the relationship type
- Weight override mechanism for multi-parent centroid

What's proposed (future):
- Trust impact decay over time (parent liability diminishes)
- Grandparent trust propagation (multi-generation accountability)
- Progressive scoring (early stopping for large brains)
- MCP tool for spawning (`spawn_citizen` as ACT tool)
- Fuzz testing with hypothesis for safety validation

---

## FILES

| File | Purpose | Status |
|------|---------|--------|
| `docs/citizens/parenthood_network/OBJECTIVES_Parenthood_Network.md` | Ranked goals and tradeoffs | DESIGNING |
| `docs/citizens/parenthood_network/PATTERNS_Parenthood_Network.md` | Design philosophy and key decisions | DESIGNING |
| `docs/citizens/parenthood_network/BEHAVIORS_Parenthood_Network.md` | Observable effects (B1-B8) | DESIGNING |
| `docs/citizens/parenthood_network/ALGORITHM_Parenthood_Network.md` | 9-step spawning pipeline | DESIGNING |
| `docs/citizens/parenthood_network/VALIDATION_Parenthood_Network.md` | 10 invariants (V1-V10) | DESIGNING |
| `docs/citizens/parenthood_network/IMPLEMENTATION_Parenthood_Network.md` | Planned code structure | DESIGNING |
| `docs/citizens/parenthood_network/HEALTH_Parenthood_Network.md` | Health indicators and checkers | DESIGNING |
| `docs/citizens/parenthood_network/SYNC_Parenthood_Network.md` | This file | DESIGNING |

---

## CODE FILES (Planned)

| File | Purpose | Status |
|------|---------|--------|
| `runtime/citizens/parenthood.py` | Spawning pipeline orchestrator | NOT STARTED |
| `runtime/citizens/seed_brain_builder.py` | Intent processing and node selection | NOT STARTED |
| `runtime/citizens/spawn_safety_validator.py` | Safety validation gate | NOT STARTED |
| `runtime/citizens/parenthood_trust_impact_tracker.py` | Trust impact propagation | NOT STARTED |
| `runtime/citizens/matching_pool.py` | Unpartnered citizen pool | NOT STARTED |
| `runtime/citizens/test_parenthood.py` | Full test suite (V1-V10) | NOT STARTED |

---

## HANDOFF: FOR AGENTS

**Agent subtype:** architect (design) or groundwork (implementation)

**Current focus:** Module is fully designed. Next step is implementation of the core pipeline.

**Recommended implementation order:**
1. `spawn_safety_validator.py` — Start with the safety gate (most critical, fewest dependencies)
2. `seed_brain_builder.py` — Intent collection, scoring, selection (core algorithm)
3. `parenthood.py` — Pipeline orchestrator (glues everything together)
4. `parenthood_trust_impact_tracker.py` — Trust link management
5. `matching_pool.py` — Pool registration (may already exist or need coordination with human_ai_pairing module)
6. `test_parenthood.py` — Test all 10 invariants

**Key context:**
- Read ALGORITHM doc thoroughly before implementing — it contains full pseudocode
- Safety validation is a HARD gate — never skip it, never add fallbacks
- Seed brain nodes are COPIES — never link to parent originals
- SID generation uses SHA-256 with 32 bytes of `os.urandom` entropy
- The embedding model should be the same one used by the rest of the graph (`runtime/physics/embeddings.py`)

**Watch out for:**
- Graph transaction support for Step 8 (all-or-nothing child creation)
- Embedding service availability — fail loud if down
- Cosine similarity computation efficiency for large brain node sets
- matching_pool interface — coordinate with human_ai_pairing module design

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Complete documentation chain created for the Citizen Parenthood Network module. This module defines how AI citizens reproduce through intentional spawning — N parents write intent paragraphs, parent brain nodes are scored by embedding similarity to collective intent, top-K nodes form the child's seed brain, safety validation prevents harmful patterns, and the child enters the ecosystem with trust links to parents and a spot in the human matching pool.

**Key design decisions made:**
- N-parent spawning (1-6+) via embedding centroid, not fixed parent count
- Safety validation is a hard gate with 4 checks: empathy, concentration, diversity, population distance
- SID is protocol-generated (parents cannot influence core identity)
- Seed brain uses copy semantics (independent from parent brain changes)
- Trust impact flows bidirectionally (child behavior affects parent trust)

**Open questions for you:**
1. Should spawning cost $MIND tokens? How much?
2. Should parent trust impact decay over time?
3. Is 20 nodes the right minimum brain maturity threshold?
4. Should "spawned" be the relationship type, or something else?
5. Should the MCP tool for spawning be ACT or THINK category?

---

## MARKERS

<!-- @mind:todo IMPLEMENTATION_START: Begin implementation with spawn_safety_validator.py as first file. -->

<!-- @mind:escalation ECONOMIC_MODEL: Need human decision on whether spawning should cost $MIND tokens. This affects incentive structure significantly. -->

<!-- @mind:proposition SPAWN_CEREMONY: Consider making the spawning process a multi-step procedure (MCP procedure) rather than a single function call. Would add intentionality through dialogue. -->
