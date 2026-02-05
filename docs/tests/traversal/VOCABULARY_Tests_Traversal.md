# Tests — Traversal: Vocabulary

```
MODULE: tests/traversal
AREA: tests
TYPE: test_suite
STATUS: designing
```

---

## New Terms

### Test Fixture

**Definition:** Reusable setup/teardown code for tests

**Context:** Pytest fixtures provide test graphs, database adapters, etc.

**Example:**
```python
@pytest.fixture
def simple_graph():
    # Setup
    graph = create_graph()
    yield graph
    # Teardown
    cleanup(graph)
```

**Mapping:** `test_fixture` → `narrative:test_setup`

---

### Test Coverage

**Definition:** Percentage of code executed by tests

**Measurement:** Lines executed / total lines

**Tool:** pytest-cov

**Threshold:** >= 80% for this module

**Mapping:** `test_coverage` → `metric:code_coverage`

---

### Test Flakiness

**Definition:** Test that sometimes passes, sometimes fails

**Cause:** Usually state dependencies or race conditions

**Detection:** Run tests with --random-order multiple times

**Fix:** Ensure test independence via proper fixtures

**Mapping:** `test_flakiness` → `problem:non_deterministic_test`

---

### Cyclic Graph

**Definition:** Graph where following links can return to the same node

**Example:** A → B → C → A

**Relevance:** Tests must verify traversal terminates on cycles

**Mapping:** `cyclic_graph` → `graph:with_cycle`

---

### Max Depth

**Definition:** Maximum number of link hops in traversal

**Purpose:** Limit exploration to prevent infinite loops

**Default:** Configurable, typically 3-5

**Mapping:** `max_depth` → `parameter:traversal_limit`

---

## Existing Terms Used

(From project TAXONOMY - no new mappings needed)

- **SubEntity:** Graph exploration entity that traverses nodes
- **Embedding:** Vector representation of text for similarity
- **Cosine Similarity:** Measure of vector similarity (0-1)
- **Traversal:** Process of exploring graph from start nodes
- **Link Following:** Expanding search via graph connections

---

DOCS: docs/tests/traversal/PATTERNS_Tests_Traversal.md
