# OBJECTIVES — Procedure

```
STATUS: DRAFT v2.0
CREATED: 2025-12-29
UPDATED: 2025-12-29
```

---

## CHAIN

```
THIS:            OBJECTIVES_Procedure.md (you are here)
PATTERNS:        ./PATTERNS_Procedure.md
BEHAVIORS:       ./BEHAVIORS_Procedure.md
VOCABULARY:      ./VOCABULARY_Procedure.md
ALGORITHM:       ./ALGORITHM_Procedure.md
VALIDATION:      ./VALIDATION_Procedure.md
IMPLEMENTATION:  ./IMPLEMENTATION_Procedure.md
HEALTH:          ./HEALTH_Procedure.md
SYNC:            ./SYNC_Procedure.md
```

---

## PRIMARY OBJECTIVES (ranked)

1. **O1: Steps Are Self-Contained** — CRITICAL
   Each step has everything the agent needs in its content (the guide). No runtime doc chain loading. The procedure creator transforms relevant docs into actionable instructions embedded in the step.

2. **O2: Agent Writes in Sandbox Only** — CRITICAL
   Procedures are templates (read-only). Agents execute in Run Spaces. All agent work (nodes, links) goes into the Run Space. This enables audit trails, safe retries, and rollback.

3. **O3: Fixed Schema, Rich Content** — HIGH
   ngram schema is FIXED (5 node types). No custom fields. No new node types. All domain-specific structure lives in `content` field. Subtypes enable filtering. Embeddings enable retrieval.

4. **O4: Deterministic Flow (V1)** — HIGH
   Explicit API calls control flow: `start_procedure`, `continue_procedure`, `end_procedure`. No physics-based routing for V1. Physics tracks state (active/completed) but doesn't route.

5. **O5: Multi-Granularity Ready** — MEDIUM
   Start with 1 node per doc. Structure supports splitting later (1 per behavior, 1 per entry point) without breaking anything.

## NON-OBJECTIVES

- **Dynamic branching (V1)**: Procedures are linear sequences. Conditional paths are V2+.
- **Self-modifying procedures**: Templates never change at runtime.
- **Physics-based discovery**: V1 uses explicit API calls, not energy gradients for routing.
- **Nested procedures**: Procedures don't call other procedures in V1.
- **Parallel steps**: Steps execute sequentially, not in parallel.

## TRADEOFFS (canonical decisions)

- When **predictability** conflicts with **flexibility**, choose predictability.
  We accept linear-only sequences to ensure debuggable, testable execution.

- When **simplicity** conflicts with **power**, choose simplicity for V1.
  We accept explicit API routing over physics-based discovery to ship faster.

- When **isolation** conflicts with **convenience**, choose isolation.
  We accept Run Space overhead to protect template integrity.

## SUCCESS SIGNALS (observable)

- Step content includes What/Why/How guide — agent doesn't need external docs
- Run Space contains agent-created nodes; Procedure template has zero modifications
- API calls return step content directly (no doc chain assembly at runtime)
- Graph state shows exactly one high-energy step link per active Run Space
- Procedure links to doc space via IMPLEMENTS for audit trail

## MARKERS

<!-- @mind:proposition V2 SCOPE: Consider physics-based routing when V1 is stable -->
<!-- @mind:proposition BRANCHING: Options for V2 — new link type or step conditions field -->
<!-- @mind:proposition Consider procedure composition (A calls B) for V2 -->
<!-- @mind:proposition Doc change → trigger step review (V2) -->
