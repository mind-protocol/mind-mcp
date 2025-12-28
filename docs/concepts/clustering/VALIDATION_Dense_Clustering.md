# VALIDATION: Dense Clustering

## Invariants

### V-CLUSTER-ID-UNIQUE

**Every extracted node has a unique, deterministic ID.**

```
ID = "{node_type}_{TYPE}_{slug}"

Examples:
- narrative_HEALTH_schema-compliance
- thing_DOCK_schema-compliance-input
- narrative_TODO_add-physics-range-checks
```

**Why:** Enables upsert (MERGE). Same content re-extracted gets same ID, updates not duplicates.

**Check:**
```cypher
MATCH (n)
WITH n.id as id, count(*) as cnt
WHERE cnt > 1
RETURN id, cnt
-- Must return empty
```

### V-CLUSTER-PROVENANCE

**Every extraction creates a moment with links to created nodes.**

```
moment_INGEST_{doc}-{timestamp}
    ├── expresses ← actor (who did it)
    └── about → [all created/updated nodes]
```

**Why:** Audit trail. Can answer "when did this enter the graph?" and "what created this node?"

**Check:**
```cypher
MATCH (n) WHERE n.id STARTS WITH 'narrative_HEALTH'
MATCH (m:Moment)-[:ABOUT]->(n)
RETURN count(n) = count(m)
-- Should be true (every health has a creating moment)
```

### V-CLUSTER-REFERENCE-RESOLVED

**Every reference creates a link to an existing or stub node.**

When doc says "verifies V1":
- If V1 exists → link to it
- If V1 doesn't exist → create stub, link to stub

**Why:** No dangling references. Graph is always traversable.

**Check:**
```cypher
MATCH (h:Narrative {type: 'health'})-[r:RELATES {direction: 'verifies'}]->(v)
WHERE v IS NULL
RETURN h.name
-- Must return empty (all verifies links have targets)
```

### V-CLUSTER-FILE-NODE

**Every extracted document has a thing_FILE node.**

The doc itself is a node, not just the content extracted from it.

**Why:** Can link to the doc, track its changes, see what was extracted from it.

**Check:**
```cypher
MATCH (m:Moment {type: 'ingest'})-[:ABOUT]->(f:Thing {type: 'file'})
RETURN count(m) = count(DISTINCT f)
-- Every ingest moment links to exactly one file
```

### V-CLUSTER-CONTAINMENT

**Every extracted node belongs to a space.**

All nodes from a doc are contained in the module's space.

**Why:** Enables scope queries ("show all health indicators in engine module").

**Check:**
```cypher
MATCH (n:Narrative {type: 'health'})
WHERE NOT (s:Space)-[:CONTAINS]->(n)
RETURN n.name
-- Must return empty
```

### V-CLUSTER-DOCK-ATTACHMENT

**Every dock is attached to exactly one health indicator.**

Docks are observation points. They must point to what they observe.

**Why:** Dock without attachment is meaningless.

**Check:**
```cypher
MATCH (d:Thing {type: 'dock'})
WHERE NOT (d)-[:ATTACHED_TO]->(:Narrative {type: 'health'})
RETURN d.name
-- Must return empty
```

### V-CLUSTER-MARKER-SOURCE

**Every marker node tracks its source document and line.**

```yaml
narrative_TODO_xxx:
  source_doc: "thing_FILE_docs-schema-HEALTH-Schema-md"
  source_line: 45
```

**Why:** Can navigate from TODO back to where it was written.

**Check:**
```cypher
MATCH (t:Narrative) WHERE t.type IN ['todo', 'escalation', 'proposition']
WHERE t.source_doc IS NULL
RETURN t.id
-- Must return empty
```

### V-CLUSTER-UPSERT-IDEMPOTENT

**Re-extracting same doc produces same graph state.**

Running extraction twice on unchanged doc:
- No new nodes created
- No duplicate links
- Properties unchanged

**Why:** Doctor can run repeatedly without side effects.

**Check:**
```python
# Before extraction
count_before = graph.query("MATCH (n) RETURN count(n)")[0]

# Extract same doc twice
extract_document(doc)
extract_document(doc)

# After extraction
count_after = graph.query("MATCH (n) RETURN count(n)")[0]

# Second extraction should not increase count
assert count_after == count_before + expected_new_nodes
```

### V-CLUSTER-STUB-MARKED

**Stub nodes (created from unresolved references) are marked.**

```yaml
narrative_VALIDATION_V99:
  stub: true  # Created as reference target, not from source doc
```

**Why:** Can find and resolve stubs later. Distinguishes "defined here" from "referenced but undefined".

**Check:**
```cypher
MATCH (n) WHERE n.stub = true
RETURN n.id, n.type
-- Shows all stubs for resolution
```

## Threshold Violations

| Invariant | Severity | On Violation |
|-----------|----------|--------------|
| V-CLUSTER-ID-UNIQUE | CRITICAL | Data corruption, fix immediately |
| V-CLUSTER-PROVENANCE | WARNING | Missing audit trail, add moments |
| V-CLUSTER-REFERENCE-RESOLVED | ERROR | Broken traversal, resolve or stub |
| V-CLUSTER-FILE-NODE | ERROR | Missing doc node, re-extract |
| V-CLUSTER-CONTAINMENT | WARNING | Orphan nodes, assign to space |
| V-CLUSTER-DOCK-ATTACHMENT | ERROR | Meaningless dock, attach or delete |
| V-CLUSTER-MARKER-SOURCE | WARNING | Can't navigate to source, update |
| V-CLUSTER-UPSERT-IDEMPOTENT | CRITICAL | Non-deterministic, fix extractor |
| V-CLUSTER-STUB-MARKED | WARNING | Unclear node origin, mark stubs |

## Related

- HEALTH_Dense_Clustering.md — Runtime verification
- ALGORITHM_Dense_Clustering.md — How invariants are maintained
