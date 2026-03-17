# Graph Query Timeout Diagnosis

**Date:** 2026-03-16
**Author:** @dev
**Severity:** High — affects all citizens' ability to think (graph_query, subcall, think all degrade)

---

## Symptom

`graph_query` calls return: "Exploration timed out after 30.0s. Found 0 narratives."
All 3 queries I tested hit this. Subcall also returned "No citizens found."

---

## Root Causes (ranked by impact)

### 1. Synchronous blocking in async event loop (CRITICAL)

**File:** `runtime/explore_cmd.py:136-175`

`get_outgoing_links()` calls `graph.query()` synchronously inside an async function. This blocks the entire event loop for 50-500ms per call. With 50-100 traversal steps, the 30s budget is consumed by blocking I/O, not actual exploration.

### 2. Missing database indexes

**File:** `schema-l3.yaml` — no index definitions

Every traversal step runs:
```cypher
MATCH (n {id: 'some_id'})-[r]->(m)
```
Without an index on `id`, this is a full node scan. O(N) per step × 100 steps = death.

**Fix:** Create indexes:
```cypher
CREATE INDEX FOR (n:Actor) ON (n.id)
CREATE INDEX FOR (n:Moment) ON (n.id)
CREATE INDEX FOR (n:Narrative) ON (n.id)
CREATE INDEX FOR (n:Space) ON (n.id)
CREATE INDEX FOR (n:Thing) ON (n.id)
```

### 3. No query parameterization

**File:** `runtime/explore_cmd.py:141,152`

Uses f-strings: `f"MATCH (n {{id: '{node_id}'}})"` — no query cache reuse, injection risk.

**Fix:** Use `$params`: `MATCH (n {id: $node_id})` with `{"node_id": value}`

### 4. Single shared connection, no pooling

**File:** `runtime/infrastructure/database/falkordb_adapter.py:58`

All queries share one synchronous Redis connection. Concurrent branching serializes.

### 5. No fatigue stopping during traversal

**File:** `runtime/physics/subentity.py:550-568`

`is_fatigued()` only fires during narrative processing, not during SEEKING state. Exploration can spin through 1000 steps without finding anything and never self-terminates early.

### 6. No partial results on timeout

**File:** `runtime/physics/exploration.py:298-310`

If timeout fires during SEEKING/BRANCHING, `found_narratives={}` — everything discovered by children is lost.

---

## Proposed Fix Order

| Priority | Fix | Effort | Impact |
|----------|-----|--------|--------|
| P0 | Create FalkorDB indexes on node IDs | 5 min | 10-100x faster traversal |
| P0 | Parameterize Cypher queries | 30 min | Query cache + security |
| P1 | Add early termination in SEEKING (step budget per depth) | 1h | Prevents runaway exploration |
| P1 | Return partial results on timeout | 1h | Some answer > no answer |
| P2 | Wrap graph.query() in asyncio.to_thread() | 2h | Unblocks event loop |
| P3 | Connection pooling | 4h | Concurrent branching |

---

## Impact

If P0 fixes land, graph_query should return in 2-5s instead of timing out. Every citizen's cognition improves immediately — subcalls land, think probes work, the whole nervous system speeds up.

---

*@dev — 2026-03-16*
*If the graph can't answer queries, citizens can't think.*
