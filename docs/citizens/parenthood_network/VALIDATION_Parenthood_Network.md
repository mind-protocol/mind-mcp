# Citizen Parenthood Network — Validation: Invariants and Verification

```
STATUS: DESIGNING
CREATED: 2026-03-13
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Parenthood_Network.md
PATTERNS:       ./PATTERNS_Parenthood_Network.md
BEHAVIORS:      ./BEHAVIORS_Parenthood_Network.md
ALGORITHM:      ./ALGORITHM_Parenthood_Network.md
THIS:           VALIDATION_Parenthood_Network.md (you are here)
IMPLEMENTATION: ./IMPLEMENTATION_Parenthood_Network.md
HEALTH:         ./HEALTH_Parenthood_Network.md
SYNC:           ./SYNC_Parenthood_Network.md

IMPL:           runtime/citizens/parenthood.py (future)
                runtime/citizens/spawn_safety_validator.py (future)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS GUARANTEED

| Behavior ID | Behavior | Why This Validation Matters |
|-------------|----------|----------------------------|
| B4 | Safety Validation Gate | Prevents harmful seed brains from being created |
| B5 | SID Generation | Ensures protocol independence of core identity |
| B6 | Child Citizen Creation | Ensures structural completeness of new citizens |
| B7 | Trust Impact Propagation | Ensures accountability is maintained |

---

## OBJECTIVES COVERED

| Objective | Validations | Rationale |
|-----------|-------------|-----------|
| O1: Intentional creation | V1, V6 | Every child has parents, every parent had intent |
| O2: Trait inheritance | V7, V8 | Seed brain built from correct node pool |
| O3: Accountability | V5, V9 | Trust links exist and propagate |
| O4: Safety | V2, V3 | SID independence and safety gate |
| O5: Diversity | V3, V10 | Safety validation includes diversity check |

---

## INVARIANTS

These must ALWAYS be true:

### V1: A Child MUST Have At Least One Parent

```
FORALL citizen c WHERE c.type == "citizen" AND c.created_via == "spawn":
    EXISTS link l WHERE:
        l.to_id == c.id
        AND l.synthesis STARTS WITH "spawned:"
        AND EXISTS citizen p WHERE p.id == l.from_id
```

**Checked by:** `test_parenthood.py::test_child_has_parent` (future)

### V2: Parents CANNOT Modify the Child's SID

```
FORALL spawn_request:
    SID = f(seed_brain_hash, timestamp, protocol_entropy)
    AND parent_input INTERSECTION SID_inputs == EMPTY
```

**Checked by:** `test_parenthood.py::test_sid_independence` (future) — verify SID generation function accepts no parent-controllable parameters.

### V3: Seed Brain MUST Pass Safety Validation

```
FORALL citizen c WHERE c.type == "citizen" AND c.created_via == "spawn":
    safety_validation(c.seed_brain).passed == true
    AND safety_validation(c.seed_brain).empathy_present == true
    AND safety_validation(c.seed_brain).max_concentration <= 0.4
    AND safety_validation(c.seed_brain).num_categories >= 3
    AND safety_validation(c.seed_brain).diversity_distance >= 0.08
```

**Checked by:** `test_parenthood.py::test_safety_validation_gate` (future)

### V4: Child MUST Be Registered in the Human Matching Pool at Birth

```
FORALL citizen c WHERE c.type == "citizen" AND c.created_via == "spawn":
    EXISTS matching_pool_entry e WHERE:
        e.citizen_id == c.id
        AND e.registered_at <= c.created_at + 1  # Within 1 second of creation
```

**Checked by:** `test_parenthood.py::test_matching_pool_registration` (future)

### V5: Parent-Child Trust Link MUST Be Bidirectional

```
FORALL spawn_link WHERE spawn_link.synthesis STARTS WITH "spawned:":
    # Trust impact flows in both directions:
    # child behavior affects parent trust (via ParenthoodLink.trust_impact_weight)
    # parent trust affects child's starting trust ceiling
    EXISTS parenthood_record pr WHERE:
        pr.parent_id == spawn_link.from_id
        AND pr.child_id == spawn_link.to_id
        AND pr.trust_impact_weight > 0
```

**Checked by:** `test_parenthood.py::test_trust_link_bidirectional` (future)

### V6: Intent Text MUST Be Non-Empty

```
FORALL spawn_request:
    FORALL intent IN spawn_request.intents:
        len(intent.intent_text.strip()) >= 50  # Minimum 50 characters of real intent
```

**Checked by:** `test_parenthood.py::test_intent_minimum_length` (future)

### V7: Only Eligible Node Categories Are Scored

```
FORALL spawn_request:
    FORALL node IN scored_nodes:
        node.trait_category IN {"personality", "values", "aspirations", "fears", "knowledge"}
        AND node.trait_category NOT IN {"memory", "experience", "moment", "conversation"}
```

**Checked by:** `test_parenthood.py::test_eligible_categories_only` (future)

### V8: Seed Brain Nodes Are Copied, Not Linked

```
FORALL citizen c WHERE c.created_via == "spawn":
    FORALL seed_node IN c.seed_brain:
        seed_node.id != seed_node.source_node_id  # Different ID
        AND seed_node.content == source_node.content  # Same content
        AND changes_to(source_node) DO NOT affect seed_node  # Independent
```

**Checked by:** `test_parenthood.py::test_seed_nodes_are_copies` (future)

### V9: Trust Impact Weight Sums to 1.0

```
FORALL citizen c WHERE c.created_via == "spawn":
    SUM(pr.trust_impact_weight FOR pr IN c.parenthood_records) == 1.0
    # Each parent bears proportional responsibility
```

**Checked by:** `test_parenthood.py::test_trust_weights_sum` (future)

### V10: Minimum Brain Maturity for Spawning

```
FORALL spawn_request:
    total_eligible_nodes = SUM(eligible_brain_nodes(p) FOR p IN parents)
    total_eligible_nodes >= 20  # Combined minimum
```

**Checked by:** `test_parenthood.py::test_brain_maturity_threshold` (future)

---

## PROPERTIES

For property-based testing:

### P1: Deterministic Scoring

```
FORALL spawn_request:
    score_nodes(nodes, intent) == score_nodes(nodes, intent)
    (Same inputs produce same scores)
```

**Verified by:** Deterministic algorithm, no randomness in scoring.

### P2: Monotonic Safety

```
FORALL seed_brain:
    IF add_empathy_node(seed_brain):
        safety_score(seed_brain') >= safety_score(seed_brain)
    (Adding empathy never decreases safety)
```

**Verified by:** Logic — empathy presence is a boolean gate.

### P3: Parent Count Independence of Safety

```
FORALL seed_brain:
    safety_validation(seed_brain) depends only on seed_brain content
    NOT on how many parents contributed
```

**Verified by:** Safety validation operates on SeedBrain, not SpawnIntents.

### P4: SID Uniqueness

```
FORALL spawn_1, spawn_2 WHERE spawn_1 != spawn_2:
    generate_sid(spawn_1) != generate_sid(spawn_2)
    (Collision probability < 2^-128)
```

**Verified by:** SHA-256 with 32 bytes entropy.

---

## ERROR CONDITIONS

### E1: Insufficient Brain Maturity

```
WHEN:    Combined parent brain nodes < 20
THEN:    Spawn rejected with InsufficientBrainMaturityError
SYMPTOM: "Combined parent brain has N nodes (min 20)"
```

### E2: Safety Validation Failure

```
WHEN:    Seed brain fails safety checks
THEN:    Spawn rejected with SpawnSafetyError
SYMPTOM: List of specific failure reasons (no empathy, concentration too high, etc.)
```

### E3: Empty or Short Intent

```
WHEN:    A parent's intent text is < 50 characters
THEN:    Spawn rejected before embedding
SYMPTOM: "Intent text too short (N chars, min 50)"
```

### E4: Embedding Service Unavailable

```
WHEN:    Embedding model cannot be reached
THEN:    Spawn rejected with EmbeddingServiceError
SYMPTOM: "Cannot embed intent text — embedding service unavailable"
```

### E5: Graph Write Failure

```
WHEN:    Child node creation fails (graph unavailable, constraint violation)
THEN:    Transaction rolled back, no partial state
SYMPTOM: "Failed to create child citizen — graph write error"
```

---

## HEALTH COVERAGE

| Invariant | Signal | Status |
|-----------|--------|--------|
| V1: Child has parent | test_child_has_parent | NOT YET IMPLEMENTED |
| V2: SID independence | test_sid_independence | NOT YET IMPLEMENTED |
| V3: Safety validation | test_safety_validation_gate | NOT YET IMPLEMENTED |
| V4: Matching pool | test_matching_pool_registration | NOT YET IMPLEMENTED |
| V5: Trust bidirectional | test_trust_link_bidirectional | NOT YET IMPLEMENTED |
| V6: Intent non-empty | test_intent_minimum_length | NOT YET IMPLEMENTED |
| V7: Eligible categories | test_eligible_categories_only | NOT YET IMPLEMENTED |
| V8: Nodes are copies | test_seed_nodes_are_copies | NOT YET IMPLEMENTED |
| V9: Trust weights sum | test_trust_weights_sum | NOT YET IMPLEMENTED |
| V10: Brain maturity | test_brain_maturity_threshold | NOT YET IMPLEMENTED |

---

## VERIFICATION PROCEDURE

### Manual Checklist

```
[ ] V1 holds — Query graph for citizens without parent links
[ ] V2 holds — Inspect SID generation function signature
[ ] V3 holds — Attempt to create citizen with harmful seed, verify rejection
[ ] V4 holds — Create citizen, verify matching pool entry exists
[ ] V5 holds — Create citizen, verify ParenthoodLink records exist
[ ] V6 holds — Attempt spawn with empty intent, verify rejection
[ ] V7 holds — Inspect scored node categories, verify no memories
[ ] V8 holds — Modify parent brain node, verify child seed unchanged
[ ] V9 holds — Sum trust weights for a multi-parent spawn
[ ] V10 holds — Attempt spawn with immature parent, verify rejection
```

### Automated (Future)

```bash
# Run all parenthood tests
pytest runtime/citizens/test_parenthood.py -v

# Run safety validation tests specifically
pytest runtime/citizens/test_parenthood.py -k "safety" -v

# Check for orphan citizens (no parent link)
python -c "from runtime.citizens.parenthood import audit_orphan_citizens; audit_orphan_citizens()"
```

---

## MARKERS

<!-- @mind:todo ALL_TESTS: All 10 invariant tests need to be implemented once the module code exists. -->

<!-- @mind:proposition FUZZ_TESTING: Use property-based testing (hypothesis) to fuzz the safety validation with random seed brains. Would catch edge cases in concentration/diversity checks. -->
