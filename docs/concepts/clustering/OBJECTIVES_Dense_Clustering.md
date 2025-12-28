# OBJECTIVES: Dense Clustering

## Primary Objective

**Make document structure queryable.**

Documents contain structure: health indicators, validations, TODOs, references to code. That structure is trapped in prose. Dense clustering extracts it into graph nodes and links so it can be queried, traversed, and reasoned about.

## Ranked Goals

| Priority | Goal | Metric |
|----------|------|--------|
| P0 | **Queryability** | Any relationship mentioned in docs can be found via graph query |
| P1 | **Traceability** | Path exists from any issue → explanation → code |
| P2 | **Coverage visibility** | Can query "which validations have no health coverage?" |
| P3 | **Impact analysis** | Can answer "what breaks if I delete this file?" |
| P4 | **Change tracking** | Moments record when structure entered/changed |

## Why This Order

1. **Queryability is foundational.** Without it, the graph is just storage. With it, the graph is a reasoning tool.

2. **Traceability enables debugging.** When something breaks, you need the path from symptom to cause to explanation.

3. **Coverage visibility prevents gaps.** You can't fix what you can't see. Querying for orphan validations reveals holes.

4. **Impact analysis prevents breakage.** Before deleting or changing, you know what depends on it.

5. **Change tracking is provenance.** Knowing when/how nodes entered helps debugging and auditing.

## Non-Goals

- **Minimal storage** — We optimize for queryability, not storage efficiency. 50 nodes per doc is fine.
- **Real-time sync** — Extraction runs on doctor scan, not on every file save.
- **Perfect parsing** — 90% extraction with explicit markers beats 99% extraction with brittle heuristics.

## Success Criteria

| Criterion | Test |
|-----------|------|
| One HEALTH doc creates ~20+ nodes | Count nodes after ingesting HEALTH_Schema.md |
| Health→Validation links exist | Query `(h:HEALTH)-[:verifies]->(v:VALIDATION)` returns results |
| TODOs link to what they're about | Query `(t:TODO)-[:about]->(target)` returns results |
| Moments have provenance | Every extraction creates moment with actor + targets |
| Re-ingestion updates, not duplicates | Same doc ingested twice doesn't double node count |

## Tradeoffs Accepted

| We Accept | To Get |
|-----------|--------|
| More nodes per doc | Full queryability |
| Extraction complexity | Explicit structure |
| Moment overhead | Change tracking |
| Dense linking | Impact analysis |

## Related

- PATTERNS_Dense_Clustering.md — Design philosophy
- ALGORITHM_Dense_Clustering.md — How extraction works
- VALIDATION_Dense_Clustering.md — Invariants
