# Archived: SYNC_Mind_Graph_System.md

Archived on: 2025-12-24
Original file: SYNC_Mind_Graph_System.md

---

## IMPLEMENTATION PHASES

| Phase | Goal | Value Delivered | Status |
|-------|------|-----------------|--------|
| 1. See Graph | Ingest docs → nodes | Docs queryable in graph | **NEXT** |
| 2. Active Context | Query active Narratives | Physics-driven relevance | — |
| 3. One Agent | Agent responds to Moment | Agent produces output | — |
| 4. Lasting Work | Agent creates Narratives | Knowledge growth | — |
| 5. Multi-Agent | 6 agents differentiate | Parallel work | — |
| 6. Continuous | World runs autonomously | Full vision | — |

### Phase 1 Scope

**Input:** `docs/building/*.md` + `mapping.yaml`
**Output:** Graph with Spaces, Narratives, Things
**Verify:** Query graph, see docs as nodes

Deliverables:
- `building/ingest/discover.py` — find files matching patterns
- `building/ingest/parse.py` — extract content, sections, markers
- `building/ingest/create.py` — call engine.create_* APIs
- `building/config/mapping.py` — load mapping.yaml

---

### What Exists

| Doc | Status | Content |
|-----|--------|---------|
| OBJECTIVES | Complete | 8 ranked objectives, non-objectives, tradeoffs |
| PATTERNS | Complete | 8 key decisions, invariants, open patterns |
| BEHAVIORS | Complete | 11 observable value behaviors, anti-behaviors |
| ALGORITHM | Complete | 4 client procedures (ingest, query, handler, create) |
| VALIDATION | Complete | 17 invariants across 6 categories |
| mapping.yaml | Complete | v2.0 repo-to-graph mapping |
| IMPLEMENTATION | Complete | Code structure, 3 flows with docking points |
| HEALTH | Not started | — |

### What's Designed

- **Graph structure:** 5 node types (Space, Actor, Narrative, Moment, Thing)
- **Link types:** 9 types per schema v1.2 (contains, expresses, about, relates, attached_to, leads_to, sequence, primes, can_become)
- **Physics:** Energy/weight/strength/conductivity fields defined
- **Client boundary:** Clear separation between client (us) and engine
- **Ingest pipeline:** mapping.yaml defines all transformations

### What's NOT Designed

- Agent prompts (base prompts, response format)
- Bootstrap sequence (first run procedure)
- Incremental ingest (file changes after bootstrap)
- Health checkers for this module
- Actual implementation code

---


## ENGINE API MAPPING (Verified)

### Node Creation

| mapping.yaml | Engine Method | Key Args |
|--------------|---------------|----------|
| `Space` | `GraphOps.add_place()` | `id, name, type, weight, energy` |
| `Narrative` | `GraphOps.add_narrative()` | `id, name, content, type, weight` |
| `Thing` | `GraphOps.add_thing()` | `id, name, type, weight, energy` |
| `Actor` | `GraphOps.add_character()` | `id, name, type, weight, energy` |

### Link Creation

| mapping.yaml | Engine Method | Notes |
|--------------|---------------|-------|
| `contains` (Space→Space) | `add_contains()` | Exists |
| `contains` (Space→Narrative) | Custom cypher | Need to add |
| `relates` | `add_narrative_link()` | `supports, contradicts, elaborates` |
| `about` | `add_about()` | `moment_id, target_id, weight` |

### Gap: Space→Narrative Containment

Current `add_contains()` only handles Space→Space. For Phase 1, add custom:

```python
def add_narrative_to_space(space_id: str, narrative_id: str):
    cypher = """
    MATCH (s:Space {id: $space_id})
    MATCH (n:Narrative {id: $narr_id})
    MERGE (s)-[:CONTAINS]->(n)
    """
```

---


## MARKERS

### Phase 1 TODOs

<!-- @mind:done Verify engine API exists and signatures -->
<!-- @mind:todo Create building/ package directory structure -->
<!-- @mind:todo Implement mapping.py with Pydantic models -->
<!-- @mind:todo Implement discover.py file pattern matching -->
<!-- @mind:todo Implement parse.py markdown + marker extraction -->
<!-- @mind:todo Implement create.py engine API calls -->
<!-- @mind:todo Add Space→Narrative containment link method -->
<!-- @mind:todo Test ingest with docs/building/ -->

### Phase 1 Escalations

<!-- @mind:resolved E1 Engine API verified — add_place, add_narrative, add_thing, add_character exist. Gap: Space→Narrative containment needs custom cypher. -->
<!-- @mind:resolved E2 Mapping parser — use Pydantic models for validation -->
<!-- @mind:resolved E3 Section granularity — start file-level, defer section extraction -->
<!-- @mind:resolved E4 Link timing — two-pass (all nodes, then all links) -->

### Future Phase TODOs

<!-- @mind:todo Create agents.yaml with initial agents (Phase 3) -->
<!-- @mind:todo Define physics constants (Phase 2) -->
<!-- @mind:todo Create HEALTH doc with runtime checkers (Phase 6) -->

### Propositions

<!-- @mind:proposition Create a "dry run" mode that logs what would be created without touching graph -->
<!-- @mind:proposition Start ingest with docs/building/ only, expand after verified -->

