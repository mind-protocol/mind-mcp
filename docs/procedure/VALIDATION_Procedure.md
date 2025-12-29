# Procedure — Validation: What Must Be True

```
STATUS: DRAFT v2.0
CREATED: 2025-12-29
UPDATED: 2025-12-29
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Procedure.md
PATTERNS:        ./PATTERNS_Procedure.md
BEHAVIORS:       ./BEHAVIORS_Procedure.md
VOCABULARY:      ./VOCABULARY_Procedure.md
ALGORITHM:       ./ALGORITHM_Procedure.md
THIS:            VALIDATION_Procedure.md (you are here)
IMPLEMENTATION:  ./IMPLEMENTATION_Procedure.md
HEALTH:          ./HEALTH_Procedure.md
SYNC:            ./SYNC_Procedure.md

IMPL:            runtime/connectome/procedure_runner.py (planned)
```

---

## PURPOSE

**Validation = what we care about being true.**

Not mechanisms. Not test paths. Not how things work.

What properties, if violated, would mean the system has failed its purpose?

These are the value-producing invariants — the things that make the Procedure module worth building.

---

## INVARIANTS

### V1: Schema Immutability

**Why we care:** If custom node types or fields are added, the fixed schema guarantee breaks. Embeddings become inconsistent. Retrieval fails. The entire ngram model degrades.

```
MUST:   Only use node types: actor, space, narrative, moment, thing
MUST:   All domain structure lives in content field
MUST:   Subtypes are strings in the subtype field
NEVER:  Create custom node types
NEVER:  Add fields to node schema beyond the canonical set
```

### V2: Template Protection

**Why we care:** If templates are modified during execution, subsequent runs are corrupted. Audit trails become meaningless. Rollback is impossible.

```
MUST:   Agent writes only to Run Space
MUST:   Procedure template nodes are read-only during execution
MUST:   All agent-created nodes link to Run Space via CONTAINS
NEVER:  Agent modifies Procedure template nodes
NEVER:  Agent creates links FROM Procedure nodes (only TO them)
NEVER:  Agent deletes or updates template content
```

### V3: Single Active Step

**Why we care:** If multiple steps are active, the agent doesn't know where it is. If zero steps are active, the procedure is in limbo. Unambiguous state is essential for crash recovery.

```
MUST:   Exactly one high-energy (e > 5) step link per active Run Space
MUST:   Completed steps have energy < 2 and polarity [0.2, 0.8]
MUST:   Active step has energy > 5 and polarity [0.9, 0.1]
NEVER:  Multiple high-energy step links (ambiguous state)
NEVER:  Zero high-energy step links while procedure status is "active"
```

### V4: Step Contains Complete Guide

**Why we care:** If a step lacks guide content, the agent operates without context. Steps must be self-contained.

```
MUST:   Every Step node has guide content (What/Why/How sections)
MUST:   Guide is embedded in step content field (no runtime loading)
MUST:   Validation spec included if step requires completion proof
NEVER:  Step that requires external doc loading to execute
NEVER:  Empty or placeholder step content
```

### V5: API Contract Fulfillment

**Why we care:** If the API returns incomplete data, agents can't function. The contract is the interface — breaking it breaks all callers.

```
MUST:   start_procedure returns Step 1 content (the guide)
MUST:   continue_procedure checks validation before advancing
MUST:   continue_procedure returns next step content (the guide)
MUST:   end_procedure marks run status as "completed"
MUST:   All API calls return consistent structure (run_id, step_content, status)
NEVER:  Advance step without validation check
NEVER:  Return step from wrong Run Space
```

### V6: Validation Spec Integrity

**Why we care:** If validation specs are malformed, steps can't transition. Procedures get stuck. Agents fail without actionable feedback.

```
MUST:   Validation specs in step content are parseable
MUST:   Validation types are from canonical set: node_exists, link_exists
MUST:   Validation failures return specific, actionable error messages
NEVER:  Silent validation failures (log but continue)
NEVER:  Undefined validation types (reject at parse time)
```

### V7: Actor-Run Relationship

**Why we care:** If actor links are wrong, we can't track who did what. Audit trails break. Permission models fail.

```
MUST:   Active Run Space has exactly one Actor linked via "occupies"
MUST:   Completed Run Space has Actor linked via "inhabits"
MUST:   Actor link energy reflects run state (high=active, low=complete)
NEVER:  Run Space without actor link
NEVER:  Multiple actors on same Run Space (V1 — collaborative runs are V2+)
```

---

## PRIORITY

| Priority | Meaning | If Violated |
|----------|---------|-------------|
| **CRITICAL** | System purpose fails | Unusable |
| **HIGH** | Major value lost | Degraded severely |
| **MEDIUM** | Partial value lost | Works but worse |

---

## INVARIANT INDEX

| ID | Value Protected | Priority |
|----|-----------------|----------|
| V1 | Schema coherence | CRITICAL |
| V2 | Template integrity | CRITICAL |
| V3 | Unambiguous state | CRITICAL |
| V4 | Context availability | HIGH |
| V5 | API reliability | HIGH |
| V6 | Transition correctness | HIGH |
| V7 | Audit trail | MEDIUM |

---

## RESOLVED DECISIONS

### RD1: V4 Strictness (Missing Doc Chain)

**Decision:** WARNING for V1, ERROR for V2.

If a step has no IMPLEMENTED_IN links:
- V1: Log warning, continue execution (graceful degradation)
- V2: Block execution (strict enforcement)

**Rationale:** Don't block on incomplete docs during early adoption. Tighten when procedures are mature.

### RD2: V6 Canonical Validation Types

**Decision:** V1 supports exactly two types:

| Type | Schema | Purpose |
|------|--------|---------|
| `node_exists` | `{in_space, subtype, min_count}` | Check node was created |
| `link_exists` | `{in_space, verb, min_count}` | Check link was created |

Add `content_matches`, `count_range`, `custom` in V2 when real procedures need them.

---

## MARKERS

<!-- @mind:proposition V8: "Run Space Expiration" — runs older than N days with status "active" should be auto-failed or flagged -->
