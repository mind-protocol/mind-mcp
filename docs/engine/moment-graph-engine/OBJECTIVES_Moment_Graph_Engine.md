# Moment Graph Engine — Objectives

```
STATUS: DESIGNING
VERSION: v0.1
CREATED: 2025-12-26
```

---

## CHAIN

```
THIS:           OBJECTIVES_Moment_Graph_Engine.md (you are here)
PATTERNS:       ./PATTERNS_Instant_Traversal_Moment_Graph.md
BEHAVIORS:      ./BEHAVIORS_Traversal_And_Surfacing.md
ALGORITHM:      ./ALGORITHM_Click_Wait_Surfacing.md
VALIDATION:     ./VALIDATION_Moment_Traversal_Invariants.md
IMPLEMENTATION: ./IMPLEMENTATION_Moment_Graph_Runtime_Layout.md
SYNC:           ./SYNC_Moment_Graph_Engine.md
```

---

## PURPOSE

Define what the moment graph engine optimizes for, ranked by priority. These objectives guide all design tradeoffs.

---

## OBJECTIVES

### O1: Sub-50ms Response Time (Critical)

**What we optimize:** Player action to visible state change must complete within 50ms.

**Why it matters:** Narrative responsiveness is the core experience. Lag between click and result breaks immersion and creates uncertainty about whether the action registered.

**Tradeoffs accepted:**
- Limit complexity of per-click graph operations
- Defer expensive computations to async paths
- Sacrifice some graph expressiveness for speed

**Measure:** P99 latency of traversal operations < 50ms.

---

### O2: Deterministic State Transitions (Critical)

**What we optimize:** Same input state + action = same output state, always.

**Why it matters:** Non-determinism creates debugging nightmares and makes the narrative feel arbitrary rather than earned. State must be reproducible for testing, replay, and trust.

**Tradeoffs accepted:**
- No randomness in hot path operations
- No implicit ordering dependencies
- Explicit timestamp/ordering where needed

**Measure:** Replay any action sequence → identical final state.

---

### O3: No LLM in Hot Path (Critical)

**What we optimize:** Traversal and surfacing are pure graph operations.

**Why it matters:** LLM calls have variable latency (100ms-10s). Putting them in the hot path makes O1 impossible and creates unpredictable user experience.

**Tradeoffs accepted:**
- Narrative reasoning happens elsewhere (narrator agent, async)
- Hot path only does mechanical state updates
- Rich narrative emerges from graph structure, not per-click AI

**Measure:** Zero LLM API calls in traversal/surfacing code paths.

---

### O4: Graph-Derived Visibility (Important)

**What we optimize:** What the player sees is always computable from graph state.

**Why it matters:** If visibility rules live outside the graph (in UI state, session state, external configs), state diverges and becomes hard to debug. The graph is truth.

**Tradeoffs accepted:**
- All gating logic must be expressible as graph queries
- Some UI-convenient shortcuts are forbidden
- Visibility may require multi-hop queries

**Measure:** visible_moments() returns same result from any caller, any time.

---

### O5: Single Module Ownership (Important)

**What we optimize:** All traversal and surfacing logic lives in one place.

**Why it matters:** Scattered logic leads to inconsistent behavior, duplicate bugs, and unclear ownership. Callers should integrate with one module, not piece together operations.

**Tradeoffs accepted:**
- Module may grow larger than ideal
- Clear boundaries require explicit APIs
- Changes require single-point updates

**Measure:** No traversal/surfacing code outside mind/moment_graph/.

---

### O6: Testable in Isolation (Nice to have)

**What we optimize:** Traversal and surfacing can be tested without a running game or database.

**Why it matters:** Fast feedback loops require unit tests that don't need full infrastructure. Mock graph state should suffice.

**Tradeoffs accepted:**
- Some integration behaviors only visible in full tests
- Mock fidelity limits coverage

**Measure:** Unit tests run in < 1s without external dependencies.

---

## OBJECTIVE CONFLICTS

| Conflict | Resolution |
|----------|------------|
| O1 vs O4 (speed vs graph-derived) | Pre-compute visibility indexes; batch graph queries |
| O3 vs narrative richness | Narrative reasoning is async; hot path is mechanical |
| O5 vs modularity | Accept larger module for clearer ownership |

---

## NON-OBJECTIVES

Things we explicitly do NOT optimize for:

- **Maximum graph expressiveness** — Speed matters more than fancy queries
- **Real-time LLM narration** — That belongs to narrator agent
- **UI rendering concerns** — That belongs to frontend modules
- **Schema definition** — That belongs to docs/schema

---

## VERIFICATION

- [ ] All objectives have measures
- [ ] Conflicts documented with resolutions
- [ ] Non-objectives make boundaries clear
