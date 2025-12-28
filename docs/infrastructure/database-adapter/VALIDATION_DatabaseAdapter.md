# DatabaseAdapter — Validation

```
STATUS: DESIGNING
VERSION: v0.1
CREATED: 2025-12-26
```

---

## CHAIN

```
OBJECTIVES:     ./OBJECTIVES_DatabaseAdapter.md
PATTERNS:       ./PATTERNS_DatabaseAdapter.md
BEHAVIORS:      ./BEHAVIORS_DatabaseAdapter.md
ALGORITHM:      ./ALGORITHM_DatabaseAdapter.md
THIS:           VALIDATION_DatabaseAdapter.md (you are here)
IMPLEMENTATION: ./IMPLEMENTATION_DatabaseAdapter.md
HEALTH:         ./HEALTH_DatabaseAdapter.md
SYNC:           ./SYNC_DatabaseAdapter.md
```

---

## PURPOSE

Invariants that must hold for the DatabaseAdapter to be correct. Testable properties.

---

## INVARIANTS

### I1: Singleton Instance

```
INVARIANT: Only one adapter instance exists per process

CHECK:
  adapter1 = get_database_adapter()
  adapter2 = get_database_adapter()
  ASSERT adapter1 is adapter2
```

### I2: Backend Isolation

```
INVARIANT: No FalkorDB or Neo4j imports in application code

CHECK:
  grep -r "from falkordb" mind/ --include="*.py" | grep -v "infrastructure/database"
  grep -r "import neo4j" mind/ --include="*.py" | grep -v "infrastructure/database"
  ASSERT both return empty
```

### I3: Result Normalization

```
INVARIANT: Query results are always List[Dict[str, Any]]

CHECK:
  result = adapter.query("MATCH (n) RETURN n LIMIT 1")
  ASSERT isinstance(result, list)
  ASSERT all(isinstance(r, dict) for r in result)
  ASSERT no Node or Relationship objects in result
```

### I4: Cypher Portability

```
INVARIANT: Common Cypher subset works on both backends

CHECK:
  # Same query on both
  falkor_result = falkor_adapter.query("MATCH (n:Actor) RETURN n.id")
  neo4j_result = neo4j_adapter.query("MATCH (n:Actor) RETURN n.id")
  ASSERT same_content(falkor_result, neo4j_result)
```

### I5: Transaction Atomicity

```
INVARIANT: Multi-operation transactions are atomic

CHECK:
  # Failing transaction
  TRY:
    with adapter.transaction() as tx:
      tx.execute("CREATE (n:Test {id: 'tx_test'})")
      RAISE Exception("Force rollback")
  EXCEPT: pass

  # Node should not exist
  result = adapter.query("MATCH (n:Test {id: 'tx_test'}) RETURN n")
  ASSERT len(result) == 0
```

### I6: Configuration Switch

```
INVARIANT: Changing config.backend changes adapter type

CHECK:
  # With backend: falkordb
  adapter1 = get_database_adapter()
  ASSERT isinstance(adapter1, FalkorDBAdapter)

  # Reset singleton, change config to neo4j
  _instance = None
  adapter2 = get_database_adapter()
  ASSERT isinstance(adapter2, Neo4jAdapter)
```

### I7: Health Check Non-Throwing

```
INVARIANT: health_check() never raises exception

CHECK:
  # Even with bad connection
  adapter.close()
  result = adapter.health_check()
  ASSERT result in [True, False]  # No exception
```

### I8: Parameter Safety

```
INVARIANT: Parameters are properly escaped (no injection)

CHECK:
  malicious = "'; DROP (n); '"
  adapter.query("MATCH (n) WHERE n.name = $name RETURN n", {"name": malicious})
  # Should not execute DROP, just search for literal string
```

---

## TEST MATRIX

| Invariant | FalkorDB Test | Neo4j Test | Integration Test |
|-----------|---------------|------------|------------------|
| I1: Singleton | Unit | Unit | N/A |
| I2: Isolation | Static | Static | CI grep |
| I3: Normalization | Unit | Unit | Both backends |
| I4: Portability | N/A | N/A | Both backends same data |
| I5: Atomicity | Unit | Unit | Both backends |
| I6: Config Switch | Integration | Integration | Full cycle |
| I7: Health Check | Unit | Unit | Both backends |
| I8: Param Safety | Unit | Unit | Both backends |

---

## CRITICAL TESTS

```python
# test_database_adapter.py

def test_singleton():
    """I1: Same instance returned."""
    a1 = get_database_adapter()
    a2 = get_database_adapter()
    assert a1 is a2

def test_no_direct_imports():
    """I2: Application code doesn't import backends directly."""
    import subprocess
    result = subprocess.run(
        ["grep", "-r", "from falkordb", "mind/", "--include=*.py"],
        capture_output=True, text=True
    )
    # Filter out infrastructure/database
    lines = [l for l in result.stdout.split("\n")
             if l and "infrastructure/database" not in l]
    assert len(lines) == 0, f"Direct imports found: {lines}"

def test_result_normalization():
    """I3: Results are plain dicts."""
    adapter = get_database_adapter()
    result = adapter.query("MATCH (n) RETURN n LIMIT 1")
    assert isinstance(result, list)
    for row in result:
        assert isinstance(row, dict)
        for v in row.values():
            assert not hasattr(v, 'labels')  # No Node objects
            assert not hasattr(v, 'relation')  # No Edge objects

def test_transaction_rollback():
    """I5: Failed transaction rolls back."""
    adapter = get_database_adapter()
    test_id = f"rollback_test_{uuid.uuid4()}"

    try:
        with adapter.transaction() as tx:
            tx.execute(f"CREATE (n:Test {{id: '{test_id}'}})")
            raise ValueError("Force rollback")
    except ValueError:
        pass

    result = adapter.query(f"MATCH (n:Test {{id: '{test_id}'}}) RETURN n")
    assert len(result) == 0

def test_health_check_no_throw():
    """I7: health_check never throws."""
    adapter = get_database_adapter()
    # This should return bool, not raise
    result = adapter.health_check()
    assert isinstance(result, bool)
```

---

## VERIFICATION

- [ ] All invariants have check procedures
- [ ] Test matrix covers both backends
- [ ] Critical tests documented

