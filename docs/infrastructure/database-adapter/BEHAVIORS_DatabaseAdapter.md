# DatabaseAdapter — Behaviors

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
THIS:           BEHAVIORS_DatabaseAdapter.md (you are here)
ALGORITHM:      ./ALGORITHM_DatabaseAdapter.md
VALIDATION:     ./VALIDATION_DatabaseAdapter.md
IMPLEMENTATION: ./IMPLEMENTATION_DatabaseAdapter.md
HEALTH:         ./HEALTH_DatabaseAdapter.md
SYNC:           ./SYNC_DatabaseAdapter.md
```

---

## PURPOSE

Observable behaviors of the DatabaseAdapter. What happens when you call it.

---

## BEHAVIOR TABLE

| ID | Trigger | Behavior | Observable Result |
|----|---------|----------|-------------------|
| B1 | `get_database_adapter()` called | Factory reads config, creates adapter | Singleton adapter returned |
| B2 | `adapter.query(cypher)` | Cypher executed on backend | List of dicts returned |
| B3 | `adapter.execute(cypher)` | Cypher mutation executed | No return, graph modified |
| B4 | `adapter.transaction()` used | Context manager opened | Multiple ops atomic |
| B5 | `adapter.health_check()` | Backend pinged | True/False returned |
| B6 | Config changed, restart | New adapter type created | Seamless backend switch |
| B7 | Invalid cypher sent | Backend error caught | Exception with message |
| B8 | Connection lost | Reconnect attempted | Transparent to caller |

---

## DETAILED BEHAVIORS

### B1: Factory Creates Singleton

```
GIVEN: database_config.yaml exists with backend: "falkordb"
WHEN: get_database_adapter() called
THEN: FalkorDBAdapter instance created and cached
AND: Same instance returned on subsequent calls
```

### B2: Query Returns Normalized Results

```
GIVEN: Valid Cypher query
WHEN: adapter.query("MATCH (n:Actor) RETURN n.id, n.name")
THEN: Returns [{"n.id": "actor_1", "n.name": "Claude"}, ...]
AND: Node/Relationship objects converted to dicts
AND: Backend-specific types normalized
```

### B3: Execute Mutates Without Return

```
GIVEN: Valid Cypher mutation
WHEN: adapter.execute("CREATE (n:Test {id: $id})", {"id": "test_1"})
THEN: Node created in graph
AND: No value returned
AND: Parameters safely interpolated
```

### B4: Transaction Provides Atomicity

```
GIVEN: Multiple operations needed atomically
WHEN:
  with adapter.transaction() as tx:
      tx.execute("CREATE ...")
      tx.execute("CREATE ...")
THEN: Both succeed or both rollback
AND: Isolation from other transactions
```

### B5: Health Check Verifies Connectivity

```
GIVEN: Adapter initialized
WHEN: adapter.health_check()
THEN: Returns True if backend reachable
OR: Returns False if connection failed
AND: Does not throw exception
```

### B6: Backend Switch on Restart

```
GIVEN: Application running with FalkorDB
AND: Config changed to neo4j
WHEN: Application restarted
THEN: Neo4jAdapter created instead
AND: All queries work unchanged
```

### B7: Cypher Error Handling

```
GIVEN: Invalid Cypher query
WHEN: adapter.query("INVALID SYNTAX")
THEN: DatabaseError raised
AND: Original error message preserved
AND: Connection not corrupted
```

### B8: Connection Recovery

```
GIVEN: Database connection lost
WHEN: Next query attempted
THEN: Reconnection attempted automatically
AND: Query retried if reconnect succeeds
OR: Error raised if reconnect fails
```

---

## CYPHER COMPATIBILITY BEHAVIORS

### Common Cypher (works on both)

```cypher
-- Node operations
MATCH (n:Label) WHERE n.prop = $value RETURN n
CREATE (n:Label {prop: $value})
MERGE (n:Label {id: $id}) SET n.updated = timestamp()
DELETE n

-- Relationship operations
MATCH (a)-[r:TYPE]->(b) RETURN r
CREATE (a)-[:TYPE {prop: $value}]->(b)

-- Aggregations
MATCH (n) RETURN count(n), collect(n.id)

-- Parameters
MATCH (n) WHERE n.id = $id RETURN n
```

### FalkorDB Limitations (adapter must handle)

```cypher
-- NO subqueries (Neo4j only)
CALL { MATCH (n) RETURN n }  -- Not supported

-- NO FOREACH (limited support)
FOREACH (x IN list | CREATE (:Node {id: x}))  -- Not supported

-- Limited APOC
CALL apoc.create.node(...)  -- Not available
```

---

## VERIFICATION

- [ ] All behaviors have trigger/result
- [ ] Cypher compatibility documented
- [ ] Error cases covered

