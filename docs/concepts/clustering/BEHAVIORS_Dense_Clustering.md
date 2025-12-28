# BEHAVIORS: Dense Clustering

## Observable Effects

### B1: Document Ingestion Creates Multiple Nodes

**Given:** A HEALTH doc with 4 indicators, 2 docks, 3 checkers, 3 TODOs
**When:** Doctor ingests the doc
**Then:** ~20+ nodes created in graph

```
Input:  1 file (HEALTH_Schema.md)
Output: 23 nodes, 44 links
```

### B2: Health Indicators Become Queryable

**Given:** HEALTH_Schema.md defines `schema_compliance` indicator
**When:** After ingestion
**Then:** Can query:
```cypher
MATCH (h:Narrative {type: 'health', name: 'schema_compliance'})
RETURN h
```

### B3: Validations Get Coverage Links

**Given:** Health indicator says "verifies V1"
**When:** After ingestion
**Then:** Link exists:
```cypher
MATCH (h:Narrative {name: 'schema_compliance'})-[r:RELATES {direction: 'verifies'}]->(v:Narrative {name: 'V1'})
RETURN h, r, v
```

### B4: Docks Point to Code

**Given:** Dock defined at `check_health.py:272`
**When:** After ingestion
**Then:** Dock node has uri and line:
```yaml
thing_DOCK_schema-compliance-input:
  uri: "mind/graph/health/check_health.py::GraphOps._query"
  line: 272
  direction: input
```

### B5: TODOs Extracted from Markers

**Given:** Doc contains `@mind:todo Add physics range checks (V2)`
**When:** After ingestion
**Then:** TODO node exists with link to V2:
```cypher
MATCH (t:Narrative {type: 'todo'})-[:RELATES {direction: 'about'}]->(v:Narrative {name: 'V2'})
RETURN t.content
```

### B6: Moments Record Extraction

**Given:** Doc ingested at timestamp T
**When:** After ingestion
**Then:** Moment exists:
```cypher
MATCH (m:Moment {type: 'ingest'})-[:ABOUT]->(f:Thing {type: 'file'})
WHERE f.name = 'HEALTH_Schema.md'
RETURN m.created_at_s, m.text
```

### B7: Re-ingestion Updates, Not Duplicates

**Given:** Doc already ingested, then modified and re-ingested
**When:** Doctor runs again
**Then:**
- Node count stable (no duplicates)
- Changed properties updated
- New content added as new nodes

### B8: Coverage Gaps Queryable

**Given:** Some validations have no health coverage
**When:** Query for orphans
**Then:** Returns list:
```cypher
MATCH (v:Narrative {type: 'validation'})
WHERE NOT (h:Narrative {type: 'health'})-[:RELATES {direction: 'verifies'}]->(v)
RETURN v.name as uncovered_validation
```

### B9: Impact Analysis Works

**Given:** File `check_health.py` has docks pointing to it
**When:** Query for dependents
**Then:** Returns health indicators that would break:
```cypher
MATCH (f:Thing {name: 'check_health.py'})<-[:RELATES {direction: 'observes'}]-(d:Thing {type: 'dock'})<-[:ATTACHED_TO]-(h:Narrative {type: 'health'})
RETURN h.name as affected_health_indicator
```

### B10: Doc Chain Links Exist

**Given:** HEALTH doc references VALIDATION and IMPLEMENTATION docs
**When:** After ingestion
**Then:** Links exist:
```cypher
MATCH (health:Thing {name: 'HEALTH_Schema.md'})-[:RELATES {direction: 'implements'}]->(val:Thing {name: 'VALIDATION_Schema.md'})
RETURN health, val
```

## Error Behaviors

### E1: Malformed YAML Skipped

**Given:** Doc has invalid YAML block
**When:** Ingestion runs
**Then:**
- Warning logged
- Valid parts still extracted
- Error recorded in moment

### E2: Unresolved Reference Creates Stub

**Given:** Doc references "V99" which doesn't exist
**When:** Ingestion runs
**Then:**
- Stub node created: `narrative_VALIDATION_V99`
- Link created to stub
- Stub marked as `stub: true`

### E3: Duplicate Marker Merged

**Given:** Same TODO appears twice in doc
**When:** Ingestion runs
**Then:** One node created (deduplicated by content hash)

## Related

- ALGORITHM_Dense_Clustering.md — How these behaviors are achieved
- VALIDATION_Dense_Clustering.md — Invariants these behaviors must maintain
