# DatabaseAdapter — Objectives

```
STATUS: DESIGNING
VERSION: v0.1
CREATED: 2025-12-26
```

---

## CHAIN

```
THIS:           OBJECTIVES_DatabaseAdapter.md (you are here)
PATTERNS:       ./PATTERNS_DatabaseAdapter.md
BEHAVIORS:      ./BEHAVIORS_DatabaseAdapter.md
ALGORITHM:      ./ALGORITHM_DatabaseAdapter.md
VALIDATION:     ./VALIDATION_DatabaseAdapter.md
IMPLEMENTATION: ./IMPLEMENTATION_DatabaseAdapter.md
HEALTH:         ./HEALTH_DatabaseAdapter.md
SYNC:           ./SYNC_DatabaseAdapter.md
```

---

## PURPOSE

Define what the DatabaseAdapter module optimizes for, ranked by priority. Enable mind to work with multiple graph database backends (FalkorDB, Neo4j) via a single configurable abstraction.

---

## OBJECTIVES

### O1: Single Configuration Switch (Critical)

**What we optimize:** Switching database backend requires only a configuration change.

**Why it matters:** Different deployments may require different backends. Neo4j for managed cloud, FalkorDB for self-hosted. The application code should not know or care which backend is active.

**Tradeoffs accepted:**
- Some advanced backend-specific features may not be exposed
- Lowest common denominator for some operations
- Configuration complexity for multi-backend support

**Measure:** Change one config value → entire system uses new backend.

---

### O2: Zero Application Code Changes (Critical)

**What we optimize:** Consumers of the graph API never import backend-specific code.

**Why it matters:** Tight coupling to FalkorDB means every consumer needs refactoring when adding Neo4j. Abstract once at the adapter layer, not in 20+ files.

**Tradeoffs accepted:**
- Additional abstraction layer
- Some indirection cost
- Interface may not expose all backend features

**Measure:** grep for `from falkordb` or `import neo4j` in application code returns zero matches.

---

### O3: Cypher Compatibility Layer (Critical)

**What we optimize:** Both FalkorDB and Neo4j use Cypher, but with subtle differences.

**Why it matters:** FalkorDB's Cypher is Redis-based with some limitations vs Neo4j's full Cypher. The adapter must handle these differences transparently.

**Tradeoffs accepted:**
- May need query rewriting for some operations
- Feature detection at startup
- Some queries may be less optimal on one backend

**Measure:** Same Cypher query works on both backends via adapter.

---

### O4: Connection Pooling & Lifecycle (Important)

**What we optimize:** Efficient connection management for each backend.

**Why it matters:** FalkorDB uses Redis protocol (connection pooling via redis-py). Neo4j uses Bolt protocol (Driver manages sessions). Different patterns, same interface.

**Tradeoffs accepted:**
- Backend-specific connection code exists (inside adapter)
- May not fully optimize for each backend's strengths

**Measure:** Connection handling is invisible to consumers.

---

### O5: Transaction Support (Important)

**What we optimize:** Atomic multi-operation writes work on both backends.

**Why it matters:** Graph mutations often require multiple operations (create node, create links). Both backends support transactions but differently.

**Tradeoffs accepted:**
- Transaction semantics may differ slightly
- Isolation levels may vary

**Measure:** Multi-operation writes either fully succeed or fully rollback.

---

### O6: Schema & Index Management (Nice to have)

**What we optimize:** Index creation works on both backends.

**Why it matters:** Performance requires indexes. Each backend has different index syntax.

**Tradeoffs accepted:**
- Index types may differ
- Some index features not portable

**Measure:** Same logical index definition works on both.

---

## OBJECTIVE CONFLICTS

| Conflict | Resolution |
|----------|------------|
| O2 vs backend-specific features | Expose common denominator; advanced features via extension |
| O3 vs query performance | Accept some non-optimal queries for portability |
| O4 vs simplicity | Hide complexity in adapter, expose simple interface |

---

## NON-OBJECTIVES

Things we explicitly do NOT optimize for:

- **Backend-specific optimization** — Portability over performance
- **Graph algorithm library** — Use backend's built-in or external
- **Schema enforcement** — Pydantic models handle this
- **Query building DSL** — Raw Cypher is fine

---

## VERIFICATION

- [ ] All objectives have measures
- [ ] Conflicts documented with resolutions
- [ ] Non-objectives make boundaries clear
