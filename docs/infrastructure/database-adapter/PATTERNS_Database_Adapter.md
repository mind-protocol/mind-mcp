# Database Adapter — Patterns: Graph Backend Abstraction

```
STATUS: DESIGNING
CREATED: 2025-12-27
VERIFIED: Not yet verified
```

---

## CHAIN

```
THIS:            PATTERNS_Database_Adapter.md (you are here)
ALGORITHM:       ./ALGORITHM_Database_Adapter.md (pending)
VALIDATION:      ./VALIDATION_Database_Adapter.md (pending)
IMPLEMENTATION:  ./IMPLEMENTATION_Database_Adapter.md (pending)
SYNC:            ./SYNC_Database_Adapter.md

IMPL:            mind/physics/graph/adapters/
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read the linked IMPL source files

**After modifying this doc:**
1. Update the IMPL source file to match, OR
2. Add a TODO in SYNC_*.md: "Docs updated, implementation needs: {what}"
3. Run tests: `pytest mind/tests/test_graph_adapter.py`

---

## THE PROBLEM

The codebase is currently tightly coupled to FalkorDB. Every graph operation imports `from falkordb import FalkorDB` directly, making it impossible to:

1. **Switch databases** — Using Neo4j, ArangoDB, or other graph databases requires rewriting 14+ files
2. **Test in isolation** — Unit tests require a running FalkorDB instance
3. **Support hybrid deployments** — Some environments may need Neo4j (enterprise), others FalkorDB (lightweight)

### Current Coupling (14 files with direct FalkorDB imports):
- `mind/physics/graph/graph_ops.py`
- `mind/physics/graph/graph_queries.py`
- `mind/physics/graph/graph_ops_read_only_interface.py`
- `mind/infrastructure/api/graphs.py`
- `mind/graph/health/test_schema.py`
- `mind/graph/health/lint_terminology.py`
- `mind/migrations/migrate_to_content_field.py`
- `mind/migrations/migrate_temporal_v171.py`
- `mind/migrations/migrate_to_v2_schema.py`
- `mind/migrations/migrate_tick_to_tick_created.py`
- `mind/migrations/migrate_001_schema_alignment.py`
- `app/api/connectome/tick/route.ts` (via API calls)

### Secondary Coupling (82 files with `.graph.` / `self.graph` patterns):
Files that use the graph instance but don't directly import FalkorDB. These will work once the core adapters are fixed.

---

## THE PATTERN

### Strategy Pattern with Protocol-Based Contracts

1. **GraphClient Protocol** (already exists in `graph_interface.py`) defines the contract
2. **Adapter implementations** satisfy the protocol for each backend
3. **Factory function** creates the appropriate adapter based on configuration
4. **Configuration** lives in project config (e.g., `mind/data/physics_config.yaml`)

```
                    ┌─────────────────────┐
                    │   GraphClient       │
                    │   (Protocol)        │
                    └──────────┬──────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
    ┌───────▼───────┐  ┌───────▼───────┐  ┌───────▼───────┐
    │ FalkorAdapter │  │  Neo4jAdapter │  │  MockAdapter  │
    └───────────────┘  └───────────────┘  └───────────────┘
```

### Key Insight

The `GraphClient` Protocol already exists and is minimal. The problem is that concrete implementations (GraphQueries, GraphOps) directly instantiate FalkorDB instead of receiving an abstract connection.

**Solution**: Inject a connection adapter into GraphQueries/GraphOps, rather than creating FalkorDB inside them.

---

## BEHAVIORS SUPPORTED

- **B1** — Switch between FalkorDB and Neo4j via config without code changes
- **B2** — Run unit tests with MockAdapter (no database required)
- **B3** — Use the same GraphQueries/GraphOps interface regardless of backend

## BEHAVIORS PREVENTED

- **Anti-B1** — Direct FalkorDB instantiation in business logic
- **Anti-B2** — Cypher dialect differences leaking into query methods

---

## PRINCIPLES

### Principle 1: Connection Injection

GraphQueries and GraphOps receive an adapter, not a host/port pair.

```python
# Current (wrong)
class GraphQueries:
    def __init__(self, host="localhost", port=6379):
        self.db = FalkorDB(host=host, port=port)

# Target (right)
class GraphQueries:
    def __init__(self, adapter: GraphAdapter):
        self.adapter = adapter
```

**Why**: Allows swapping backends without changing GraphQueries/GraphOps code.

### Principle 2: Cypher Compatibility Layer

FalkorDB and Neo4j both use Cypher, but with dialect differences. The adapter handles translation.

| Feature | FalkorDB | Neo4j |
|---------|----------|-------|
| Connection | `FalkorDB(host, port)` | `GraphDatabase.driver(uri, auth)` |
| Graph selection | `db.select_graph(name)` | N/A (database-level) |
| Result format | `result.result_set` | `result.records()` |
| Headers | `result.header` | `result.keys()` |

**Why**: Query code stays the same; only adapter differs.

### Principle 3: Configuration-Driven Selection

```yaml
# mind/data/physics_config.yaml
database:
  backend: "falkordb"  # or "neo4j" or "mock"
  falkordb:
    host: "localhost"
    port: 6379
    graph_name: "blood_ledger"
  neo4j:
    uri: "bolt://localhost:7687"
    username: "neo4j"
    password: "${NEO4J_PASSWORD}"
    database: "neo4j"
```

**Why**: No code changes needed to switch backends; just change config.

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `mind/physics/graph/graph_interface.py` | GraphClient Protocol definition |
| `mind/data/physics_config.yaml` | Configuration for backend selection |

---

## SCOPE

### In Scope

- Graph connection abstraction (connect, disconnect, query)
- Cypher query execution with result normalization
- Configuration-based backend selection
- MockAdapter for testing

### Out of Scope

- Query optimization per backend (each adapter executes Cypher as-is)
- Schema migration between backends (separate tool)
- Multi-database transactions (single backend per deployment)

---

## REQUIRED CHANGES INVENTORY

### Phase 1: Core Adapter Infrastructure (Priority: HIGH)

| File | Change Required |
|------|-----------------|
| **NEW** `mind/physics/graph/adapters/__init__.py` | Adapter factory and base classes |
| **NEW** `mind/physics/graph/adapters/base.py` | `GraphAdapter` abstract base class |
| **NEW** `mind/physics/graph/adapters/falkordb_adapter.py` | FalkorDB implementation |
| **NEW** `mind/physics/graph/adapters/neo4j_adapter.py` | Neo4j implementation |
| **NEW** `mind/physics/graph/adapters/mock_adapter.py` | In-memory mock for testing |
| `mind/data/physics_config.yaml` | Add `database` section |

### Phase 2: Core Classes Refactor (Priority: HIGH)

| File | Change Required |
|------|-----------------|
| `mind/physics/graph/graph_queries.py` | Accept adapter via injection, remove FalkorDB import |
| `mind/physics/graph/graph_ops.py` | Accept adapter via injection, remove FalkorDB import |
| `mind/physics/graph/graph_ops_read_only_interface.py` | Use adapter factory |

### Phase 3: Infrastructure Updates (Priority: MEDIUM)

| File | Change Required |
|------|-----------------|
| `mind/infrastructure/api/graphs.py` | Use adapter factory |
| `mind/init_db.py` | Use adapter factory |
| `mind/graph/health/test_schema.py` | Use adapter factory |
| `mind/graph/health/lint_terminology.py` | Use adapter factory |

### Phase 4: Migration Scripts (Priority: LOW)

| File | Change Required |
|------|-----------------|
| `mind/migrations/migrate_to_content_field.py` | Use adapter factory |
| `mind/migrations/migrate_temporal_v171.py` | Use adapter factory |
| `mind/migrations/migrate_to_v2_schema.py` | Use adapter factory |
| `mind/migrations/migrate_tick_to_tick_created.py` | Use adapter factory |
| `mind/migrations/migrate_001_schema_alignment.py` | Use adapter factory |

### Phase 5: Result Format Normalization

FalkorDB and Neo4j return results differently. The adapter must normalize:

| Aspect | FalkorDB | Neo4j | Normalized |
|--------|----------|-------|------------|
| Result access | `result.result_set` | `result.records()` | `List[Dict]` |
| Headers | `result.header` (list of [type, name]) | `result.keys()` | `List[str]` |
| Node properties | Direct dict access | `node.items()` | `Dict[str, Any]` |
| Null handling | Python `None` | `neo4j.NULL` | Python `None` |

---

## CYPHER DIALECT DIFFERENCES

Both FalkorDB and Neo4j use Cypher, but there are minor differences:

| Feature | FalkorDB | Neo4j | Notes |
|---------|----------|-------|-------|
| `MERGE` | Supported | Supported | Same syntax |
| `UNWIND` | Supported | Supported | Same syntax |
| `apoc.*` | Limited | Full APOC | May need fallbacks |
| Vector search | Custom extension | `db.index.vector.queryNodes` | Different APIs |
| Full-text | Limited | `db.index.fulltext.queryNodes` | Different APIs |

**Strategy**: Use standard Cypher only. Advanced features (vector search, full-text) should be adapter-specific methods.

---

## MARKERS

<!-- @mind:todo Create mind/physics/graph/adapters/ directory structure -->
<!-- @mind:todo Implement FalkorDBAdapter with current functionality -->
<!-- @mind:todo Implement Neo4jAdapter with equivalent functionality -->
<!-- @mind:todo Add database config section to physics_config.yaml -->
<!-- @mind:todo Refactor GraphQueries to use adapter injection -->
<!-- @mind:todo Refactor GraphOps to use adapter injection -->
<!-- @mind:todo Create MockAdapter for unit testing -->
<!-- @mind:todo Update all migration scripts to use adapter factory -->
