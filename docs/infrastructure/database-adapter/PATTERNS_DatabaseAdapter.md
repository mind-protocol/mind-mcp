# DatabaseAdapter — Patterns

```
STATUS: DESIGNING
VERSION: v0.1
CREATED: 2025-12-26
```

---

## CHAIN

```
OBJECTIVES:     ./OBJECTIVES_DatabaseAdapter.md
THIS:           PATTERNS_DatabaseAdapter.md (you are here)
BEHAVIORS:      ./BEHAVIORS_DatabaseAdapter.md
ALGORITHM:      ./ALGORITHM_DatabaseAdapter.md
VALIDATION:     ./VALIDATION_DatabaseAdapter.md
IMPLEMENTATION: ./IMPLEMENTATION_DatabaseAdapter.md
HEALTH:         ./HEALTH_DatabaseAdapter.md
SYNC:           ./SYNC_DatabaseAdapter.md
```

---

## PURPOSE

Design decisions for the DatabaseAdapter module. Why this shape, what's in scope, what's out.

---

## CORE PATTERN: Strategy + Factory

The adapter uses two patterns:

1. **Strategy Pattern**: Each backend implements the same interface
2. **Factory Pattern**: Configuration determines which implementation is instantiated

```python
# Factory creates the right adapter based on config
adapter = get_database_adapter()  # Reads from config

# All consumers use the same interface
result = adapter.query("MATCH (n) RETURN n LIMIT 10")
```

---

## DESIGN DECISIONS

### D1: Single Abstract Base Class

**Decision:** One `DatabaseAdapter` ABC defines the contract.

**Why:**
- Clear interface for all backends
- Type hints work correctly
- Easy to verify implementation completeness

**Alternative rejected:** Duck typing — harder to verify, no IDE support.

```python
class DatabaseAdapter(ABC):
    @abstractmethod
    def query(self, cypher: str, params: dict = None) -> List[Dict]:
        """Execute Cypher query, return results as dicts."""
        pass

    @abstractmethod
    def execute(self, cypher: str, params: dict = None) -> None:
        """Execute Cypher mutation, no return."""
        pass
```

---

### D2: Configuration via YAML + Environment

**Decision:** Backend selection in `.mind/database_config.yaml`, overridable by env vars.

**Why:**
- Easy to change per environment
- Environment variables for secrets
- Human-readable defaults

**Defaults:**
- Backend: FalkorDB
- Graph name: Repository name (e.g., `my-project` → `my_project`)

```yaml
# .mind/database_config.yaml
database:
  backend: "falkordb"  # or "neo4j"

  falkordb:
    host: "localhost"
    port: 6379
    graph_name: null  # Defaults to repo name

  neo4j:
    uri: "bolt://localhost:7687"
    user: "neo4j"
    password: ""
    database: null  # Defaults to repo name
```

**Environment overrides:**
```bash
DATABASE_BACKEND=neo4j
FALKORDB_GRAPH=custom_name
NEO4J_DATABASE=custom_db
```

See `.env.mind.example` for all options.

---

### D3: Cypher Dialect Handling

**Decision:** Adapter normalizes queries when needed.

**Why:** FalkorDB and Neo4j have Cypher differences:
- FalkorDB: No `CALL {}` subqueries, limited `FOREACH`
- Neo4j: Full Cypher 5 support
- Both: Core MATCH/CREATE/MERGE work identically

**Implementation:**
```python
class Neo4jAdapter(DatabaseAdapter):
    def query(self, cypher: str, params: dict = None) -> List[Dict]:
        # Neo4j can run as-is
        return self._execute_raw(cypher, params)

class FalkorDBAdapter(DatabaseAdapter):
    def query(self, cypher: str, params: dict = None) -> List[Dict]:
        # May need to rewrite some patterns
        normalized = self._normalize_cypher(cypher)
        return self._execute_raw(normalized, params)
```

---

### D4: Connection Lifecycle

**Decision:** Adapter manages its own connection lifecycle.

**Why:** Different backends have different patterns:
- FalkorDB: Redis connection, reconnect on failure
- Neo4j: Driver with session pool, explicit close

```python
class FalkorDBAdapter(DatabaseAdapter):
    def __init__(self, config):
        self.db = FalkorDB(host=config.host, port=config.port)
        self.graph = self.db.select_graph(config.graph_name)

class Neo4jAdapter(DatabaseAdapter):
    def __init__(self, config):
        self.driver = GraphDatabase.driver(
            config.uri,
            auth=(config.user, config.password)
        )

    def close(self):
        self.driver.close()
```

---

### D5: Result Normalization

**Decision:** All results returned as `List[Dict[str, Any]]`.

**Why:** Different backends return different result types:
- FalkorDB: Returns result sets with node/relationship objects
- Neo4j: Returns Records with Node/Relationship objects

Both must be converted to plain dicts for consumers.

---

### D6: Index Abstraction

**Decision:** Common index operations, backend-specific syntax.

**Why:** Both support indexes but syntax differs:
- FalkorDB: `CREATE INDEX FOR (n:Label) ON (n.property)`
- Neo4j: `CREATE INDEX label_property FOR (n:Label) ON (n.property)`

```python
def create_index(self, label: str, property: str) -> None:
    # Backend-specific implementation
    pass
```

---

## SCOPE

### In Scope

| Capability | Notes |
|------------|-------|
| Cypher query execution | Core operation |
| Connection management | Per-backend |
| Result normalization | To plain dicts |
| Transaction support | Begin/commit/rollback |
| Index creation | Portable subset |
| Health check | Ping/verify |

### Out of Scope

| Capability | Why Excluded |
|------------|--------------|
| Graph algorithms (PageRank, etc.) | Backend-specific, use their libs |
| Full-text search | Different implementations |
| Vector search | FalkorDB only currently |
| Triggers/procedures | Too different |

---

## COMPATIBILITY NOTES

### FalkorDB Specifics
- Uses Redis protocol (port 6379)
- Graph is selected, not database
- Limited Cypher (no subqueries)
- Vector operations built-in

### Neo4j Specifics
- Uses Bolt protocol (port 7687)
- Database concept (multi-db support)
- Full Cypher 5
- Requires APOC for some operations

### Common Ground
- MATCH/WHERE/RETURN
- CREATE/MERGE/SET/DELETE
- Node labels, relationship types
- Properties (primitives, lists)
- Parameters ($param syntax)

---

## VERIFICATION

- [ ] Design decisions are justified
- [ ] Scope is clear
- [ ] Backend differences documented
