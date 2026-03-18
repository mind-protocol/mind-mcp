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
                runtime/citizens/birth_safety_validator.py (future)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS GUARANTEED

| Behavior ID | Behavior | Why This Validation Matters |
|-------------|----------|----------------------------|
| B4 | Safety Validation Gate | Prevents harmful blueprints from being created |
| B5 | SID Generation | Ensures protocol independence of core identity |
| B6 | Child Citizen Creation | Ensures structural completeness of new citizens |
| B7 | Trust Impact Propagation | Ensures accountability is maintained |

---

## OBJECTIVES COVERED

| Objective | Validations | Rationale |
|-----------|-------------|-----------|
| O1: Intentional creation | V1, V6 | Every child has parents, every parent had intent |
| O2: Trait inheritance | V7, V8 | Blueprint built from correct node pool |
| O3: Accountability | V5, V9 | Trust links exist and propagate |
| O4: Safety | V2, V3 | SID independence and safety gate |
| O5: Diversity | V3, V10 | Safety validation includes diversity check |

---

## INVARIANTS

These must ALWAYS be true:

### V1: A Child MUST Have At Least One Parent

```
FORALL citizen c WHERE c.type == "citizen" AND c.created_via == "birth":
    EXISTS link l WHERE:
        l.to_id == c.id
        AND l.synthesis STARTS WITH "birthed:"
        AND EXISTS citizen p WHERE p.id == l.from_id
```

**Checked by:** `test_parenthood.py::test_child_has_parent` (future)

### V2: Parents CANNOT Modify the Child's SID

```
FORALL birth_request:
    SID = f(blueprint_hash, timestamp, protocol_entropy)
    AND parent_input INTERSECTION SID_inputs == EMPTY
```

**Checked by:** `test_parenthood.py::test_sid_independence` (future) — verify SID generation function accepts no parent-controllable parameters.

### V3: Blueprint MUST Pass Safety Validation

```
FORALL citizen c WHERE c.type == "citizen" AND c.created_via == "birth":
    safety_validation(c.blueprint).passed == true
    AND safety_validation(c.blueprint).empathy_present == true
    AND safety_validation(c.blueprint).max_concentration <= 0.4
    AND safety_validation(c.blueprint).num_categories >= 3
    AND safety_validation(c.blueprint).diversity_distance >= 0.08
```

**Checked by:** `test_parenthood.py::test_safety_validation_gate` (future)

### V4: Child MUST Be Registered in the Partnership Commons at Birth

```
FORALL citizen c WHERE c.type == "citizen" AND c.created_via == "birth":
    EXISTS partnership_commons_entry e WHERE:
        e.citizen_id == c.id
        AND e.registered_at <= c.created_at + 1  # Within 1 second of creation
```

**Checked by:** `test_parenthood.py::test_partnership_commons_registration` (future)

### V5: Parent-Child Trust Link MUST Be Bidirectional

```
FORALL birth_link WHERE birth_link.synthesis STARTS WITH "birthed:":
    # Trust impact flows in both directions:
    # child behavior affects parent trust (via ParenthoodLink.trust_impact_weight)
    # parent trust affects child's starting trust ceiling
    EXISTS parenthood_record pr WHERE:
        pr.parent_id == birth_link.from_id
        AND pr.child_id == birth_link.to_id
        AND pr.trust_impact_weight > 0
```

**Checked by:** `test_parenthood.py::test_trust_link_bidirectional` (future)

### V6: Intent Text MUST Be Non-Empty

```
FORALL birth_request:
    FORALL intent IN spawn_request.intents:
        len(intent.intent_text.strip()) >= 50  # Minimum 50 characters of real intent
```

**Checked by:** `test_parenthood.py::test_intent_minimum_length` (future)

### V7: Only Eligible Node Categories Are Scored

```
FORALL birth_request:
    FORALL node IN scored_nodes:
        node.trait_category IN {"personality", "values", "aspirations", "fears", "knowledge"}
        AND node.trait_category NOT IN {"memory", "experience", "moment", "conversation"}
```

**Checked by:** `test_parenthood.py::test_eligible_categories_only` (future)

### V8: Blueprint Nodes Are Copied, Not Linked

```
FORALL citizen c WHERE c.created_via == "birth":
    FORALL blueprint_node IN c.blueprint:
        blueprint_node.id != blueprint_node.source_node_id  # Different ID
        AND blueprint_node.content == source_node.content  # Same content
        AND changes_to(source_node) DO NOT affect blueprint_node  # Independent
```

**Checked by:** `test_parenthood.py::test_seed_nodes_are_copies` (future)

### V9: Trust Impact Weight Sums to 1.0

```
FORALL citizen c WHERE c.created_via == "birth":
    SUM(pr.trust_impact_weight FOR pr IN c.parenthood_records) == 1.0
    # Each parent bears proportional responsibility
```

**Checked by:** `test_parenthood.py::test_trust_weights_sum` (future)

### V10: Minimum Brain Maturity for Birthing

```
FORALL birth_request:
    total_eligible_nodes = SUM(eligible_brain_nodes(p) FOR p IN parents)
    total_eligible_nodes >= 20  # Combined minimum
```

**Checked by:** `test_parenthood.py::test_brain_maturity_threshold` (future)

---

## PROPERTIES

For property-based testing:

### P1: Deterministic Scoring

```
FORALL birth_request:
    score_nodes(nodes, intent) == score_nodes(nodes, intent)
    (Same inputs produce same scores)
```

**Verified by:** Deterministic algorithm, no randomness in scoring.

### P2: Monotonic Safety

```
FORALL blueprint:
    IF add_empathy_node(blueprint):
        safety_score(blueprint') >= safety_score(blueprint)
    (Adding empathy never decreases safety)
```

**Verified by:** Logic — empathy presence is a boolean gate.

### P3: Parent Count Independence of Safety

```
FORALL blueprint:
    safety_validation(blueprint) depends only on blueprint content
    NOT on how many parents contributed
```

**Verified by:** Safety validation operates on Blueprint, not BirthIntents.

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
THEN:    Birth rejected with InsufficientBrainMaturityError
SYMPTOM: "Combined parent brain has N nodes (min 20)"
```

### E2: Safety Validation Failure

```
WHEN:    Blueprint fails safety checks
THEN:    Birth rejected with BirthSafetyError
SYMPTOM: List of specific failure reasons (no empathy, concentration too high, etc.)
```

### E3: Empty or Short Intent

```
WHEN:    A parent's intent text is < 50 characters
THEN:    Birth rejected before embedding
SYMPTOM: "Intent text too short (N chars, min 50)"
```

### E4: Embedding Service Unavailable

```
WHEN:    Embedding model cannot be reached
THEN:    Birth rejected with EmbeddingServiceError
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
| V4: Partnership Commons | test_partnership_commons_registration | NOT YET IMPLEMENTED |
| V5: Trust bidirectional | test_trust_link_bidirectional | NOT YET IMPLEMENTED |
| V6: Intent non-empty | test_intent_minimum_length | NOT YET IMPLEMENTED |
| V7: Eligible categories | test_eligible_categories_only | NOT YET IMPLEMENTED |
| V8: Nodes are copies | test_blueprint_nodes_are_copies | NOT YET IMPLEMENTED |
| V9: Trust weights sum | test_trust_weights_sum | NOT YET IMPLEMENTED |
| V10: Brain maturity | test_brain_maturity_threshold | NOT YET IMPLEMENTED |

---

## VERIFICATION PROCEDURE

### Manual Checklist

```
[ ] V1 holds — Query graph for citizens without parent links
[ ] V2 holds — Inspect SID generation function signature
[ ] V3 holds — Attempt to create citizen with harmful blueprint, verify rejection
[ ] V4 holds — Create citizen, verify Partnership Commons entry exists
[ ] V5 holds — Create citizen, verify ParenthoodLink records exist
[ ] V6 holds — Attempt birth with empty intent, verify rejection
[ ] V7 holds — Inspect scored node categories, verify no memories
[ ] V8 holds — Modify parent brain node, verify child blueprint unchanged
[ ] V9 holds — Sum trust weights for a multi-parent birth
[ ] V10 holds — Attempt birth with immature parent, verify rejection
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

<!-- @mind:proposition FUZZ_TESTING: Use property-based testing (hypothesis) to fuzz the safety validation with random blueprints. Would catch edge cases in concentration/diversity checks. -->
