# SYNC — Database Adapter

```
STATUS: DESIGNING
LAST_UPDATED: 2025-12-27
UPDATED_BY: agent_claude
```

---

## Current State

**Phase**: Initial planning complete. No implementation yet.

The DatabaseAdapter module has been designed to enable switching between FalkorDB and Neo4j via project configuration. The PATTERNS document defines the architecture.

---

## Maturity

| Component | State | Notes |
|-----------|-------|-------|
| PATTERNS doc | CANONICAL | Design approach finalized |
| Adapter infrastructure | NOT_STARTED | `mind/physics/graph/adapters/` |
| FalkorDBAdapter | NOT_STARTED | Extract from current code |
| Neo4jAdapter | NOT_STARTED | New implementation |
| MockAdapter | NOT_STARTED | For testing |
| GraphQueries refactor | NOT_STARTED | Injection pattern |
| GraphOps refactor | NOT_STARTED | Injection pattern |
| Config schema | NOT_STARTED | `physics_config.yaml` update |

---

## Files Requiring Changes

### Direct FalkorDB Imports (14 files)

These files contain `from falkordb import FalkorDB` and must be refactored:

| File | Priority | Complexity | Status |
|------|----------|------------|--------|
| `mind/physics/graph/graph_queries.py` | HIGH | Medium | Pending |
| `mind/physics/graph/graph_ops.py` | HIGH | Medium | Pending |
| `mind/physics/graph/graph_ops_read_only_interface.py` | HIGH | Low | Pending |
| `mind/infrastructure/api/graphs.py` | MEDIUM | Low | Pending |
| `mind/init_db.py` | MEDIUM | Low | Pending |
| `mind/graph/health/test_schema.py` | MEDIUM | Low | Pending |
| `mind/graph/health/lint_terminology.py` | MEDIUM | Low | Pending |
| `mind/migrations/migrate_to_content_field.py` | LOW | Low | Pending |
| `mind/migrations/migrate_temporal_v171.py` | LOW | Low | Pending |
| `mind/migrations/migrate_to_v2_schema.py` | LOW | Low | Pending |
| `mind/migrations/migrate_tick_to_tick_created.py` | LOW | Low | Pending |
| `mind/migrations/migrate_001_schema_alignment.py` | LOW | Low | Pending |
| `app/api/connectome/tick/route.ts` | LOW | Low | Pending |
| `.next/server/app/api/connectome/tick/route.js` | LOW | Low | Auto-generated |

### Indirect Graph Usage (68+ files)

These files use `self.graph` or `.graph.` patterns but don't import FalkorDB directly. They will work once the core adapters are in place:

- `mind/physics/exploration.py`
- `mind/physics/tick_v1_2.py`
- `mind/physics/graph/graph_queries_search.py`
- `mind/physics/graph/graph_queries_moments.py`
- `mind/physics/graph/graph_ops_apply.py`
- `mind/physics/graph/graph_ops_moments.py`
- `mind/physics/graph/graph_ops_links.py`
- `mind/moment_graph/queries.py`
- `mind/moment_graph/traversal.py`
- `mind/moment_graph/surface.py`
- `mind/infrastructure/orchestration/world_runner.py`
- `mind/infrastructure/tempo/tempo_controller.py`
- `mind/infrastructure/memory/moment_processor.py`
- `mind/connectome/persistence.py`
- `mind/connectome/steps.py`
- `mind/connectome/runner.py`
- ... and 50+ more (see PATTERNS doc for grep command)

---

## Implementation Order

### Phase 1: Adapter Infrastructure
1. Create `mind/physics/graph/adapters/` directory
2. Implement `base.py` with `GraphAdapter` ABC
3. Implement `falkordb_adapter.py` (extract from current code)
4. Implement `__init__.py` with factory function

### Phase 2: Core Refactor
5. Refactor `graph_queries.py` to accept adapter
6. Refactor `graph_ops.py` to accept adapter
7. Update `graph_ops_read_only_interface.py`

### Phase 3: Config & Factory
8. Add `database` section to `physics_config.yaml`
9. Create adapter factory that reads config

### Phase 4: Neo4j Support
10. Implement `neo4j_adapter.py`
11. Test with Neo4j instance

### Phase 5: Testing
12. Implement `mock_adapter.py`
13. Update tests to use MockAdapter

### Phase 6: Migration Scripts
14. Update all migration scripts to use factory

---

## Decisions Made

| Decision | Rationale | Date |
|----------|-----------|------|
| Use Protocol + Adapters | Matches existing GraphClient Pattern | 2025-12-27 |
| Config in physics_config.yaml | Consistent with other physics config | 2025-12-27 |
| Inject adapter, don't inherit | Composition over inheritance | 2025-12-27 |
| Standard Cypher only | Avoid vendor lock-in | 2025-12-27 |

---

## Open Questions

1. **Vector search API**: FalkorDB and Neo4j have different vector search APIs. Should adapters expose a unified `vector_search()` method, or keep it backend-specific?

2. **Connection pooling**: Neo4j driver handles pooling internally. FalkorDB may need manual pooling. How to abstract this?

3. **Transaction support**: Neo4j has explicit transactions. FalkorDB auto-commits. Should adapters expose transaction context managers?

---

## Handoff Notes

**For next agent:**
- PATTERNS doc is complete with full change inventory
- Start with Phase 1: create `mind/physics/graph/adapters/` structure
- FalkorDBAdapter should just extract current code from graph_queries.py `_connect()` and `_query()`
- Test with existing FalkorDB first before adding Neo4j

**For human review:**
- Confirm backend: Neo4j 4.x or 5.x? (Driver API differs)
- Confirm auth pattern: env vars or config file for credentials?
- Confirm scope: Just query abstraction, or also schema management?
