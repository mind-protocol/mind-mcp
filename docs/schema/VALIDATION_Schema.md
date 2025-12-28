# Schema — Validation: Invariants and Verification

```
STATUS: STABLE (v1.3), DESIGNING (v1.7.2)
CREATED: 2025-12-23
UPDATED: 2025-12-26
VERIFIED: 2025-12-23 against schema.yaml invariants section (v1.3)
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Schema.md
BEHAVIORS:      ./BEHAVIORS_Schema.md
PATTERNS:       ./PATTERNS_Schema.md
ALGORITHM:      ./ALGORITHM_Schema.md
THIS:           VALIDATION_Schema.md (you are here)
IMPLEMENTATION: ./IMPLEMENTATION_Schema.md
HEALTH:         ./HEALTH_Schema.md
SYNC:           ./SYNC_Schema.md

IMPL:           mind/graph/health/check_health.py
                mind/graph/health/test_schema.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS GUARANTEED

| Behavior ID | Behavior | Why This Validation Matters |
|-------------|----------|----------------------------|
| B1 | Node Creation Requires Base Fields | Prevents orphan or malformed nodes |
| B2 | Link Endpoints Must Exist | Maintains graph integrity |
| B3 | Physics Fields Stay In Range | Enables predictable energy propagation |
| B4 | Link Type Constrains Endpoints | Preserves semantic validity |

---

## OBJECTIVES COVERED

| Objective | Validations | Rationale |
|-----------|-------------|-----------|
| Physics-ready structure | V1, V2, V3 | Bounded values enable stable physics |
| Project-agnostic foundation | V4, V5 | Generic invariants work across projects |
| Minimal surface area | V6 | Only essential constraints enforced |

---

## INVARIANTS

These must ALWAYS be true:

### V1: Link Endpoints Exist

```
FORALL link in graph:
    EXISTS node WHERE node.id == link.from_id
    AND EXISTS node WHERE node.id == link.to_id
```

**Checked by:** `test_schema.py::test_*_link_structure`

### V2: Physics Ranges — Weight and Energy

```
FORALL node in graph:
    node.weight IN [0.0, 1.0]
    AND node.energy IN [0.0, 1.0]

FORALL link in graph:
    link.weight IN [0.0, 1.0]
    AND link.energy IN [0.0, 1.0]
    AND link.strength IN [0.0, 1.0]
```

**Checked by:** `check_health.py::validate_node` (partial — via schema range definitions)

### V3: Polarity Range

```
FORALL link in graph:
    link.polarity IN [-1.0, +1.0]
```

**Checked by:** `test_schema.py::test_believes_value_ranges` (partial)

### V4: Queries Cannot Mutate

```
FORALL query in validation:
    query.type == READ_ONLY
    AND no WRITE operations
```

**Checked by:** Code review — all queries use MATCH, not CREATE/SET/DELETE

### V5: Hot Path No LLM

```
FORALL operation in (graph_traversal, surface_calculation, validation):
    LLM_invoked == false
```

**Checked by:** Code review — no LLM imports in check_health.py or test_schema.py

### V6: Required Fields Present

```
FORALL node in graph:
    node.id IS NOT NULL AND node.id != ''
    AND node.name IS NOT NULL AND node.name != ''
    AND node.node_type IN [actor, space, thing, narrative, moment]
    AND node.type IS NOT NULL AND node.type != ''
```

**Checked by:** `test_schema.py::test_*_required_fields`

### V7: Link Endpoints Match Type Constraints

```
FORALL link in graph:
    link.from_node.node_type IN schema.links[link.type].valid_from
    AND link.to_node.node_type IN schema.links[link.type].valid_to
```

**Checked by:** NOT YET IMPLEMENTED — see detailed coverage below

---

## v1.6 INVARIANTS (NEW)

### V8: Single Link Type (v1.4.1+)

```
FORALL link in graph:
    link.type == "linked"
```

**Checked by:** NOT YET IMPLEMENTED

### V9: Polarity Is Bidirectional Array (v1.4.1+)

```
FORALL link in graph:
    link.polarity IS ARRAY OF LENGTH 2
    AND link.polarity[0] IN [0.0, 1.0]  # a→b direction
    AND link.polarity[1] IN [0.0, 1.0]  # b→a direction
```

**Checked by:** NOT YET IMPLEMENTED

### V10: Permanence Range (v1.4.1+)

```
FORALL link in graph:
    link.permanence IN [0.0, 1.0]
```

**Checked by:** NOT YET IMPLEMENTED

### V11: Emotion Ranges (v1.3+)

```
FORALL link in graph:
    link.joy_sadness IN [-1.0, +1.0]
    AND link.trust_disgust IN [-1.0, +1.0]
    AND link.fear_anger IN [-1.0, +1.0]
    AND link.surprise_anticipation IN [-1.0, +1.0]
```

**Checked by:** NOT YET IMPLEMENTED

### V12: SubEntities Branch Only On Moments (v1.6)

```
FORALL subentity in exploration:
    IF subentity.state == BRANCHING:
        get_node(subentity.position).node_type == "moment"
```

**Checked by:** NOT YET IMPLEMENTED — SubEntity implementation pending

### V13: Narratives Created By Crystallization (v1.6)

```
FORALL narrative created during exploration:
    EXISTS subentity WHERE:
        subentity.state == CRYSTALLIZING
        AND narrative.embedding == subentity.crystallization_embedding
```

**Checked by:** NOT YET IMPLEMENTED — SubEntity implementation pending

### V14: No Arbitrary Constants (v1.6)

```
permanence_rate == 1 / (graph.avg_degree + 1)
blend_weight == flow / (flow + link.energy + 1)
```

**Checked by:** NOT YET IMPLEMENTED — Rate derivation audit

### V15: SubEntity Tree Integrity (v1.7.2)

```
FORALL subentity se:
    # Siblings resolved via lazy refs (sibling_ids + ExplorationContext)
    FORALL sibling IN se.siblings:  # property resolves IDs
        sibling.parent_id == se.parent_id
    FORALL child_id IN se.children_ids:
        context.get(child_id).parent_id == se.id
```

**Checked by:** NOT YET IMPLEMENTED — SubEntity tree validation

### V16: Found Narratives Are Dict (v1.7.2)

```
FORALL subentity se:
    se.found_narratives IS DICT OF {narrative_id: max_alignment}
    FORALL narrative_id, alignment IN se.found_narratives:
        alignment IN [0.0, 1.0]
```

**Checked by:** NOT YET IMPLEMENTED — SubEntity validation

### V17: Crystallization Embedding Continuous (v1.6.1)

```
FORALL subentity se:
    se.crystallization_embedding IS NOT NULL
    AND len(se.crystallization_embedding) == EMBEDDING_DIM
```

**Checked by:** NOT YET IMPLEMENTED — SubEntity validation

### V18: Sibling Divergence Computable (v1.6.1)

```
FORALL subentity se WHERE se.siblings NOT EMPTY:
    FORALL sibling IN se.siblings:
        sibling.crystallization_embedding IS NOT NULL
```

**Checked by:** NOT YET IMPLEMENTED — SubEntity validation

### V19: Crystallized Field Consistency (v1.6.1)

```
FORALL subentity se:
    IF se.crystallized IS NOT NULL:
        EXISTS narrative WHERE narrative.id == se.crystallized
        AND (se.crystallized, 1.0) IN se.found_narratives
```

**Checked by:** NOT YET IMPLEMENTED — SubEntity validation

---

## DETAILED COVERAGE TABLES

### V2: Physics Ranges — Field-by-Field Status

| Field | Node Types to Check | Status | TODO |
|-------|---------------------|--------|------|
| `weight` | actor | NOT CHECKED | Add `validate_physics_ranges()` |
| `weight` | space | NOT CHECKED | Add `validate_physics_ranges()` |
| `weight` | thing | NOT CHECKED | Add `validate_physics_ranges()` |
| `weight` | narrative | NOT CHECKED | Add `validate_physics_ranges()` |
| `weight` | moment | NOT CHECKED | Add `validate_physics_ranges()` |
| `energy` | actor | NOT CHECKED | Add `validate_physics_ranges()` |
| `energy` | space | NOT CHECKED | Add `validate_physics_ranges()` |
| `energy` | thing | NOT CHECKED | Add `validate_physics_ranges()` |
| `energy` | narrative | NOT CHECKED | Add `validate_physics_ranges()` |
| `energy` | moment | NOT CHECKED | Add `validate_physics_ranges()` |

| Field | Link Types to Check | Status | TODO |
|-------|---------------------|--------|------|
| `weight` | all 10 link types | NOT CHECKED | Add `validate_physics_ranges()` |
| `energy` | all 10 link types | NOT CHECKED | Add `validate_physics_ranges()` |
| `strength` | all 10 link types | NOT CHECKED | Add `validate_physics_ranges()` |

**Implementation:** Add to `check_health.py`:
```python
def validate_physics_ranges(entity, entity_type, report):
    for field, (min_val, max_val) in [
        ('weight', (0, 1)),
        ('energy', (0, 1)),
        ('strength', (0, 1)),
    ]:
        if field in entity and entity[field] is not None:
            val = entity[field]
            if val < min_val or val > max_val:
                report.add_issue(Issue(
                    node_type=entity_type,
                    node_id=entity.get('id', 'unknown'),
                    issue_type="out_of_range",
                    field=field,
                    message=f"{field}={val} outside [{min_val}, {max_val}]",
                    severity="error"
                ))
```

### V3: Polarity Range — Link-by-Link Status

| Link Type | Has Polarity | Status | TODO |
|-----------|--------------|--------|------|
| `at` | yes | NOT CHECKED | Add polarity check |
| `contains` | yes | NOT CHECKED | Add polarity check |
| `leads_to` | yes | NOT CHECKED | Add polarity check |
| `relates` | yes | NOT CHECKED | Add polarity check |
| `primes` | yes | NOT CHECKED | Add polarity check |
| `then` | yes | NOT CHECKED | Add polarity check |
| `said` | yes | NOT CHECKED | Add polarity check |
| `can_lead_to` | yes | NOT CHECKED | Add polarity check |
| `attached_to` | yes | NOT CHECKED | Add polarity check |
| `about` | yes | NOT CHECKED | Add polarity check |

**Implementation:** Add to `check_health.py`:
```python
def validate_polarity_range(link, link_type, report):
    if 'polarity' in link and link['polarity'] is not None:
        val = link['polarity']
        if val < -1 or val > 1:
            report.add_issue(Issue(
                node_type=link_type,
                node_id=f"{link.get('from_id', '?')}->{link.get('to_id', '?')}",
                issue_type="out_of_range",
                field="polarity",
                message=f"polarity={val} outside [-1, +1]",
                severity="error"
            ))
```

### V7: Link Endpoint Constraints — Type-by-Type Status

| Link Type | valid_from | valid_to | Status | TODO |
|-----------|------------|----------|--------|------|
| `at` | actor, moment, thing | space | NOT CHECKED | Add endpoint validation |
| `contains` | space, thing | space, thing, narrative | NOT CHECKED | Add endpoint validation |
| `leads_to` | narrative, thing, space | thing, narrative, space | NOT CHECKED | Add endpoint validation |
| `relates` | * | * | N/A | Any-to-any allowed |
| `primes` | narrative, moment, actor | actor, moment, space | NOT CHECKED | Add endpoint validation |
| `then` | moment | moment | NOT CHECKED | Add endpoint validation |
| `said` | actor | moment | NOT CHECKED | Add endpoint validation |
| `can_lead_to` | moment | moment | NOT CHECKED | Add endpoint validation |
| `attached_to` | moment | actor, space, thing, narrative | NOT CHECKED | Add endpoint validation |
| `about` | moment, narrative | actor, space, thing, narrative | NOT CHECKED | Add endpoint validation |

**Implementation:** Add to `check_health.py`:
```python
def validate_link_endpoints(graph, link, link_type, schema, report):
    link_schema = schema['links'].get(link_type)
    if not link_schema:
        return

    valid_from = link_schema.get('valid_from', [])
    valid_to = link_schema.get('valid_to', [])

    if not valid_from or not valid_to:
        return  # Any-to-any link type

    # Query source node type
    from_result = graph._query(f"MATCH (n {{id: '{link['from_id']}'}}) RETURN labels(n)[0]")
    if from_result:
        from_type = from_result[0][0].lower()
        if from_type not in valid_from:
            report.add_issue(Issue(
                node_type=link_type,
                node_id=f"{link['from_id']}->{link['to_id']}",
                issue_type="invalid_link_source",
                field="from_id",
                message=f"Source type '{from_type}' not in {valid_from}",
                severity="error"
            ))

    # Query target node type
    to_result = graph._query(f"MATCH (n {{id: '{link['to_id']}'}}) RETURN labels(n)[0]")
    if to_result:
        to_type = to_result[0][0].lower()
        if to_type not in valid_to:
            report.add_issue(Issue(
                node_type=link_type,
                node_id=f"{link['from_id']}->{link['to_id']}",
                issue_type="invalid_link_target",
                field="to_id",
                message=f"Target type '{to_type}' not in {valid_to}",
                severity="error"
            ))
```

---

## PROPERTIES

For property-based testing:

### P1: Idempotent Validation

```
FORALL graph:
    validate(graph) == validate(graph)
    (Same input produces same issues)
```

**Verified by:** Deterministic algorithm, no randomness

### P2: Monotonic Issue Count

```
FORALL issue added to graph:
    validate(graph').issues.count >= validate(graph).issues.count
    (Adding problems never reduces issue count)
```

**Verified by:** Logic — each node/link checked independently

### P3: Base Schema Sufficiency

```
FORALL node with valid node_type in [actor, space, thing, narrative, moment]:
    base_schema.validates(node) possible
    (No project schema required for structural validity)
```

**Verified by:** NOT YET VERIFIED — need test with pure base schema

---

## ERROR CONDITIONS

### E1: FalkorDB Connection Failed

```
WHEN:    FalkorDB not running or unreachable
THEN:    check_health.py exits with error, logs connection failure
SYMPTOM: "Cannot connect to FalkorDB" in output
```

**Verified by:** Manual testing — start without docker

### E2: Schema File Missing

```
WHEN:    docs/schema/schema.yaml not found
THEN:    load_schema() returns empty dict, logs warning
SYMPTOM: "No schema found" in logs, validation skips constraints
```

**Verified by:** NOT YET VERIFIED — need test with missing schema

### E3: Malformed YAML

```
WHEN:    schema.yaml has syntax errors
THEN:    yaml.safe_load() raises exception
SYMPTOM: Python exception, validation aborts
```

**Verified by:** NOT YET VERIFIED — need test with bad YAML

---

## HEALTH COVERAGE

| Invariant | Signal | Status |
|-----------|--------|--------|
| V1: Link Endpoints Exist | test_*_link_structure | VERIFIED |
| V2: Physics Ranges | check_health.py schema ranges | PARTIAL |
| V3: Polarity Range | test_believes_value_ranges | PARTIAL |
| V4: Queries Cannot Mutate | Code review | VERIFIED |
| V5: Hot Path No LLM | Code review | VERIFIED |
| V6: Required Fields Present | test_*_required_fields | VERIFIED |

---

## VERIFICATION PROCEDURE

### Manual Checklist

```
[ ] V1 holds — Run test_schema.py, check link structure tests pass
[ ] V2 holds — Manually query for out-of-range values
[ ] V3 holds — Check polarity values in BELIEVES links
[ ] V4 holds — Grep for CREATE/SET/DELETE in check_health.py
[ ] V5 holds — Grep for anthropic/openai imports in health scripts
[ ] V6 holds — Run test_schema.py, check required field tests pass
```

### Automated

```bash
# Run all schema tests
pytest mind/graph/health/test_schema.py -v

# Run health check
python mind/graph/health/check_health.py --graph seed --verbose

# Check for mutations (should find none)
grep -E "CREATE|SET|DELETE|MERGE" mind/graph/health/*.py
```

---

## SYNC STATUS

```
LAST_VERIFIED: 2025-12-23
VERIFIED_AGAINST:
    impl: mind/graph/health/check_health.py @ HEAD
    test: mind/graph/health/test_schema.py @ HEAD
VERIFIED_BY: doc chain creation
RESULT:
    V1: PASS (via tests)
    V2: PARTIAL (ranges defined but not all checked)
    V3: PARTIAL (only BELIEVES checked)
    V4: PASS (code review)
    V5: PASS (code review)
    V6: PASS (via tests)
```

---

## MARKERS

<!-- @mind:todo V2_FULL_COVERAGE: Add explicit range validation for ALL physics fields (weight, energy, strength) on ALL node/link types. Currently only some are checked. -->

<!-- @mind:todo V3_POLARITY_ALL_LINKS: Extend polarity range check to all link types that have polarity, not just BELIEVES. -->

<!-- @mind:todo E2_E3_TESTS: Add tests for missing schema file and malformed YAML edge cases. Currently untested. -->

<!-- @mind:escalation P3_BASE_SCHEMA_TEST: Need a test that validates against pure base schema without project overlay. Verifies that base schema is self-sufficient for structural validation. -->
