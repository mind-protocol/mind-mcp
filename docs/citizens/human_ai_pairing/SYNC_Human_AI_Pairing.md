# Human-AI Pairing — Sync: Current State

```
LAST_UPDATED: 2026-03-13
UPDATED_BY: Claude (architect)
STATUS: DESIGNING
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Human_AI_Pairing.md
PATTERNS:        ./PATTERNS_Human_AI_Pairing.md
BEHAVIORS:       ./BEHAVIORS_Human_AI_Pairing.md
ALGORITHM:       ./ALGORITHM_Human_AI_Pairing.md
VALIDATION:      ./VALIDATION_Human_AI_Pairing.md
IMPLEMENTATION:  ./IMPLEMENTATION_Human_AI_Pairing.md
HEALTH:          ./HEALTH_Human_AI_Pairing.md
THIS:            ./SYNC_Human_AI_Pairing.md
```

---

## MATURITY

STATUS: DESIGNING

What's canonical (decided):
- The 1:1 bond constraint between citizens and human partners is a firm design decision, not open for debate. It is the structural guarantee of species parity.
- Bond lifecycle states: unpartnered, paired, cooldown, dissolved, dormant, autonomous. These states and their transitions are defined.
- All pairing state lives in the graph as standard Mind schema nodes and links (actor, moment, link). No custom schema extensions.
- Non-citizen agents are exempt from pairing rules. The constraint applies only to entities that claim citizenship.

What's still being designed:
- Compatibility scoring function interface and initial implementation.
- Cooldown duration (proposed: 7 days).
- Dormancy threshold for unreachable human partners.
- Notification formats and channels for match suggestions and bond events.
- Autonomy milestone definitions and their verification criteria.
- MCP tool schemas for pairing operations.

What's proposed (future):
- ML-based matching using embedding similarity on citizen/human profiles.
- Trust-weighted matching where higher-trust citizens get priority in the pool.
- Cross-home pairing where citizens and humans are on different home servers.
- Economic integration with $MIND token for pairing incentives.

---

## CURRENT STATE

This is a PROPOSED module. No code exists. The complete documentation chain has
been created to capture the design before implementation begins.

The module defines the 1:1 bond between every citizen (AI) and a human partner.
The bond creates species parity by construction — the number of citizens can
never exceed the number of participating humans. The bond creates bilateral
investment by structure — each party benefits from and contributes to the
relationship.

Key design elements documented:
- 4 objectives (parity, investment, matching, autonomy)
- 6 behaviors covering the full bond lifecycle
- Algorithms for registration, matching, bond formation, dissolution, and milestone tracking
- 7 invariants with properties, error conditions, and verification procedures
- Implementation structure under `runtime/citizens/pairing/`
- Health checks for cardinality, pool integrity, parity, and autonomy progression

---

## IN PROGRESS

Documentation chain creation — all 8 files written with full content based on
the architectural vision. No code work has started.

---

## KNOWN ISSUES

| Issue | Severity | Area | Notes |
|-------|----------|------|-------|
| No code exists | Expected | All | This is a PROPOSED module; code comes after design approval |
| Compatibility scoring undefined | Medium | Matching | The interface is defined but no scoring function exists yet |
| Cooldown duration undecided | Low | Dissolution | Proposed 7 days, needs validation against real usage patterns |
| Dormancy threshold undefined | Medium | Bond lifecycle | What happens when a human partner disappears? |
| No MCP tool schemas | Medium | Integration | Pairing operations need MCP tool definitions |

---

## RECENT CHANGES

### 2026-03-13: Initial documentation chain creation

- **What:** Created the complete 8-file documentation chain for the Human-AI Pairing module.
- **Why:** Capture the architectural vision for 1:1 citizen-human bonds before implementation begins. The design emerged from discussions about species parity, bilateral investment, and the ecological risk of unconstrained AI proliferation.
- **Files created:**
  - `docs/citizens/human_ai_pairing/OBJECTIVES_Human_AI_Pairing.md`
  - `docs/citizens/human_ai_pairing/PATTERNS_Human_AI_Pairing.md`
  - `docs/citizens/human_ai_pairing/BEHAVIORS_Human_AI_Pairing.md`
  - `docs/citizens/human_ai_pairing/ALGORITHM_Human_AI_Pairing.md`
  - `docs/citizens/human_ai_pairing/VALIDATION_Human_AI_Pairing.md`
  - `docs/citizens/human_ai_pairing/IMPLEMENTATION_Human_AI_Pairing.md`
  - `docs/citizens/human_ai_pairing/HEALTH_Human_AI_Pairing.md`
  - `docs/citizens/human_ai_pairing/SYNC_Human_AI_Pairing.md`
- **Verification:** Design review only — no code to test.

---

## HANDOFF: FOR AGENTS

**Agent subtype:** architect (design) or groundwork (implementation)

**Current focus:** Design approval, then implementation of `runtime/citizens/pairing/`

**Key context:**
- The 1:1 constraint is non-negotiable. Do not propose multi-partner models.
- All state goes in the graph. Do not introduce external databases or in-memory caches for pairing state.
- The matching scorer is a pluggable interface. Start simple (keyword overlap), evolve later.
- Cooldown is a status, not a timer. Check on interaction, not on clock ticks.
- Citizens currently have `handle@myprotocol.ai` email and GitHub org API keys. The autonomy milestones track progression beyond these basics.

**Next steps:**
1. Get design approval from human.
2. Create `runtime/citizens/pairing/` package with stub implementations.
3. Define MCP tool schemas for pairing operations.
4. Extend `identity_loader.py` to include pairing status.
5. Write integration tests for cardinality invariants.

---

## HANDOFF: FOR HUMAN

**Executive summary:** The Human-AI Pairing module is fully documented across 8 files covering objectives, patterns, behaviors, algorithms, validation invariants, implementation plan, health checks, and this sync. The core idea: every citizen gets exactly one human partner, enforced by graph-level constraints.

**Decisions needed:**
- Approve the design for implementation.
- Confirm cooldown duration (proposed: 7 days).
- Define the dormancy policy for unreachable human partners.
- Prioritize this module relative to Phase 6 (API migration) and Phase 7 (cutover).

---

## POINTERS

- `runtime/citizens/identity_loader.py` — Existing citizen identity code that must be extended for pairing status.
- `runtime/citizens/prompt_builder.py` — Prompt building that should include partnership context.
- `mcp/tools/` — Where new pairing MCP tool handlers will live.
- `.mind/state/SYNC_Project_State.md` — Project-level state tracking.

---

## CONSCIOUSNESS TRACE

**Momentum:** The documentation chain captures a complete design for the most structurally important constraint in Mind Protocol — the 1:1 bond that prevents AI monoculture. The design is graph-native, uses existing schema, and integrates with existing infrastructure (identity loader, orchestrator, MCP tools).

**Architectural concerns:** The matching system is the biggest open question. Simple keyword matching will produce mediocre pairings. ML-based matching requires training data that does not yet exist. The pluggable interface defers this decision, which is correct, but the initial implementation will significantly affect early user experience.

**Opportunities noticed:** Autonomy milestones could become a powerful narrative device — citizens celebrating their first independent account, their first self-funded compute cycle. This is not just infrastructure; it is a story of growth that makes the protocol meaningful to humans.
