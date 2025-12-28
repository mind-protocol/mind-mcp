# DatabaseAdapter — Implementation

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
VALIDATION:     ./VALIDATION_DatabaseAdapter.md
THIS:           IMPLEMENTATION_DatabaseAdapter.md (you are here)
HEALTH:         ./HEALTH_DatabaseAdapter.md
SYNC:           ./SYNC_DatabaseAdapter.md
```

---

## PURPOSE

Specifies where code lives, what files to create, and what files need modification for the DatabaseAdapter abstraction layer.

---

## NEW FILES TO CREATE

### Core Adapter

| File | Purpose |
|------|---------|
| `mind/infrastructure/database/adapter.py` | Abstract base class `DatabaseAdapter` |
| `mind/infrastructure/database/falkordb_adapter.py` | FalkorDB implementation |
| `mind/infrastructure/database/neo4j_adapter.py` | Neo4j implementation |
| `mind/infrastructure/database/factory.py` | Factory: `get_database_adapter()` |
| `mind/infrastructure/database/__init__.py` | Public exports |

### Configuration

| File | Purpose |
|------|---------|
| `mind/data/database_config.yaml` | Backend selection & connection settings |

---

## EXISTING FILES TO MODIFY

### Priority 1: Core Graph Operations (Critical)

These files contain all FalkorDB imports and must be adapted first.

| File | Current State | Changes Needed |
|------|---------------|----------------|
| `mind/physics/graph/graph_ops.py` | Direct FalkorDB import | Use adapter interface |
| `mind/physics/graph/graph_ops_apply.py` | Direct FalkorDB import | Use adapter interface |
| `mind/physics/graph/graph_ops_moments.py` | Direct FalkorDB import | Use adapter interface |
| `mind/physics/graph/graph_queries.py` | Direct FalkorDB import | Use adapter interface |
| `mind/physics/graph/graph_queries_moments.py` | Direct FalkorDB import | Use adapter interface |
| `mind/physics/graph/graph_queries_search.py` | Direct FalkorDB import | Use adapter interface |
| `mind/physics/graph/graph_query_utils.py` | Direct FalkorDB import | Use adapter interface |
| `mind/physics/graph/graph_ops_read_only_interface.py` | Direct FalkorDB import | Use adapter interface |

### Priority 2: Database Initialization (Critical)

| File | Current State | Changes Needed |
|------|---------------|----------------|
| `mind/init_db.py` | FalkorDB.Graph() initialization | Use factory |

### Priority 3: API Layer (High)

| File | Current State | Changes Needed |
|------|---------------|----------------|
| `mind/infrastructure/api/graphs.py` | FalkorDB import | Use adapter interface |

### Priority 4: Connectome (High)

| File | Current State | Changes Needed |
|------|---------------|----------------|
| `mind/connectome/session.py` | Likely FalkorDB | Use adapter interface |
| `mind/connectome/persistence.py` | Likely FalkorDB | Use adapter interface |

### Priority 5: Health Checks (Medium)

| File | Current State | Changes Needed |
|------|---------------|----------------|
| `mind/graph/health/check_health.py` | FalkorDB import | Use adapter interface |
| `mind/physics/health/checkers/energy_conservation.py` | FalkorDB import | Use adapter interface |
| `mind/physics/health/checkers/moment_lifecycle.py` | FalkorDB import | Use adapter interface |

### Priority 6: Migration Scripts (Low)

These may need dual-backend support or be run separately per backend.

| File | Current State | Changes Needed |
|------|---------------|----------------|
| `mind/migrations/migrate_to_v2_schema.py` | FalkorDB specific | May need backend-specific versions |
| `tools/migrate_v11_fields.py` | FalkorDB specific | May need backend-specific versions |
| `tools/archive/migrate_schema_v11.py` | FalkorDB specific | May need backend-specific versions |

### Priority 7: Tests (Medium)

| File | Current State | Changes Needed |
|------|---------------|----------------|
| `mind/tests/test_energy_v1_2.py` | FalkorDB import | Use adapter interface |
| `mind/tests/test_moments_api.py` | FalkorDB import | Use adapter interface |

### Priority 8: Tools & Utilities (Low)

| File | Current State | Changes Needed |
|------|---------------|----------------|
| `tools/test_health_live.py` | FalkorDB import | Use adapter interface |
| `mind/doctor_graph.py` | FalkorDB import | Use adapter interface |

---

## FULL FILE LIST (31 files with FalkorDB references)

```
mind/physics/graph/graph_ops.py
mind/physics/graph/graph_ops_apply.py
mind/physics/graph/graph_ops_moments.py
mind/physics/graph/graph_queries.py
mind/physics/graph/graph_queries_moments.py
mind/physics/graph/graph_queries_search.py
mind/physics/graph/graph_query_utils.py
mind/physics/graph/graph_ops_read_only_interface.py
mind/init_db.py
mind/infrastructure/api/graphs.py
mind/connectome/session.py
mind/connectome/persistence.py
mind/graph/health/check_health.py
mind/physics/health/checkers/energy_conservation.py
mind/physics/health/checkers/moment_lifecycle.py
mind/migrations/migrate_to_v2_schema.py
mind/tests/test_energy_v1_2.py
mind/tests/test_moments_api.py
tools/migrate_v11_fields.py
tools/archive/migrate_schema_v11.py
tools/test_health_live.py
mind/doctor_graph.py
```

---

## ADAPTER INTERFACE

```python
# mind/infrastructure/database/adapter.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, ContextManager

class DatabaseAdapter(ABC):
    """Abstract interface for graph database operations."""

    @abstractmethod
    def query(self, cypher: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Execute Cypher query, return results as list of dicts."""
        pass

    @abstractmethod
    def execute(self, cypher: str, params: Optional[Dict] = None) -> None:
        """Execute Cypher mutation, no return value."""
        pass

    @abstractmethod
    def transaction(self) -> ContextManager:
        """Return context manager for transaction."""
        pass

    @abstractmethod
    def create_index(self, label: str, property: str) -> None:
        """Create index on label.property."""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Return True if database is reachable."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close connections."""
        pass
```

---

## FACTORY FUNCTION

```python
# mind/infrastructure/database/factory.py

from typing import Optional
from .adapter import DatabaseAdapter
from .falkordb_adapter import FalkorDBAdapter
from .neo4j_adapter import Neo4jAdapter

_instance: Optional[DatabaseAdapter] = None

def get_database_adapter() -> DatabaseAdapter:
    """Get or create the database adapter singleton."""
    global _instance
    if _instance is None:
        config = load_database_config()
        backend = config.get("database", {}).get("backend", "falkordb")

        if backend == "falkordb":
            _instance = FalkorDBAdapter(config["database"]["falkordb"])
        elif backend == "neo4j":
            _instance = Neo4jAdapter(config["database"]["neo4j"])
        else:
            raise ValueError(f"Unknown database backend: {backend}")

    return _instance
```

---

## MIGRATION PATTERN

### Current Pattern (to replace)

```python
# Current: Direct FalkorDB usage
from falkordb import FalkorDB

db = FalkorDB(host="localhost", port=6379)
graph = db.select_graph("blood_ledger")
result = graph.query("MATCH (n) RETURN n LIMIT 10")
```

### Target Pattern (after migration)

```python
# Target: Adapter usage
from mind.infrastructure.database import get_database_adapter

adapter = get_database_adapter()
result = adapter.query("MATCH (n) RETURN n LIMIT 10")
```

---

## IMPLEMENTATION ORDER

1. **Create adapter infrastructure** (new files)
   - adapter.py, factory.py, __init__.py
   - FalkorDBAdapter (wrap existing behavior)
   - database_config.yaml

2. **Migrate init_db.py**
   - Replace FalkorDB() with factory
   - Verify startup works

3. **Migrate graph_ops.py and graph_queries.py**
   - These are the core operations
   - All other files depend on these

4. **Migrate remaining Priority 1-3 files**
   - API layer
   - Connectome

5. **Migrate health checks**
   - Ensure monitoring works

6. **Create Neo4jAdapter**
   - Only after FalkorDB migration complete
   - Test switching between backends

7. **Migrate tests**
   - Ensure tests use adapter

8. **Handle migrations separately**
   - May need backend-specific scripts

---

## VERIFICATION

- [ ] All FalkorDB imports identified
- [ ] Implementation order defined
- [ ] Interface defined
- [ ] Factory pattern documented

