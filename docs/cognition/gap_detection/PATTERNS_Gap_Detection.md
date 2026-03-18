# Gap Detection — Patterns: Structural Immune System for the Graph

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Gap_Detection.md
THIS:            PATTERNS_Gap_Detection.md (you are here)
BEHAVIORS:       ./BEHAVIORS_Gap_Detection.md
ALGORITHM:       ./ALGORITHM_Gap_Detection.md
VALIDATION:      ./VALIDATION_Gap_Detection.md
HEALTH:          ./HEALTH_Gap_Detection.md
IMPLEMENTATION:  ./IMPLEMENTATION_Gap_Detection.md
SYNC:            ./SYNC_Gap_Detection.md

IMPL:            runtime/cognition/gap_detector.py (to be created)
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read the linked IMPL source file

**After modifying this doc:**
1. Update the IMPL source file to match, OR
2. Add a TODO in SYNC_Gap_Detection.md: "Docs updated, implementation needs: {what}"
3. Run tests: `pytest tests/cognition/test_gap_detector.py`

**After modifying the code:**
1. Update this doc chain to match, OR
2. Add a TODO in SYNC_Gap_Detection.md: "Implementation changed, docs need: {what}"
3. Run tests: `pytest tests/cognition/test_gap_detector.py`

---

## THE PROBLEM

A graph grows through ingestion: conversations become moments, people become actors, places become spaces. But ingestion is messy. A citizen mentions "we discussed it at the Arsenal" and the moment gets created but nobody links it to the Arsenal space. A human partner gets ingested twice from two different platforms and ends up as two separate Actor nodes with split histories. A citizen asks "who understands FalkorDB?" and the search returns nothing because nobody has written about it yet, but this blind spot is invisible.

Without gap detection, these problems accumulate silently. The graph looks large and rich but is structurally hollow: moments float without context, identities fragment across duplicates, and the graph can't answer questions it should be able to answer. Over time, search quality degrades, citizen context assembly becomes incoherent, and physics propagation hits dead ends at orphaned nodes.

---

## THE PATTERN

The gap detector is a **periodic scanner** that traverses the graph looking for structural incompleteness and produces **tasks** to fix what it finds. It is modeled after an immune system: it patrols the graph, identifies anomalies, and tags them for repair by the appropriate citizen.

Three scan passes, each independent:

1. **Missing link scan** — Traverses Moment nodes and checks for required link types (Actor, Space, conditionally Thing). Missing links produce tasks with the moment's content as context so the citizen can answer "where did this happen?" or "who was involved?" without re-searching.

2. **Duplicate candidate scan** — Compares embedding vectors within the same node type (Actor-to-Actor, Space-to-Space) looking for cosine similarity above threshold. Candidates are packaged into tasks with both nodes' content, links, and platform handles so the citizen can decide "same entity or genuinely different?".

3. **Empty query gap scan** — Hooks into the search system's return path. When `graph_query` returns zero results or all results fall below a resonance threshold, a gap marker is created. Gap markers accumulate; repeated gaps on the same topic raise priority. This connects the query system to the knowledge acquisition system.

The key insight: **the detector only creates tasks, never modifies the graph directly.** Tasks are Narrative nodes with type `task`, routed through the existing task physics system (urgency accumulation, citizen routing, completion cascade). If nobody cares about a gap, L7 forgetting decays the task naturally. The gap detector doesn't need its own cleanup logic.

---

## BEHAVIORS SUPPORTED

- B1 (Missing link tasks carry context) — The scan extracts moment content and passes it into the task synthesis so citizens can resolve without additional queries
- B2 (Duplicate candidates include comparison data) — Both nodes' content, link counts, and platform handles are included in the task
- B3 (Empty query gaps accumulate priority) — Repeated failed queries on the same topic increase the gap marker's energy

## BEHAVIORS PREVENTED

- A1 (Gap detector modifying the graph) — The detector is read-only except for task creation. No link creation, no node merging, no node deletion.
- A2 (Duplicate false positive flood) — Cosine threshold (0.85) and deduplication of existing gap tasks prevent creating thousands of duplicate-detection tasks for the same pair.

---

## PRINCIPLES

### Principle 1: Detection Is Separate From Resolution

The gap detector identifies problems. Citizens fix them. This separation means the detector can be aggressive (surface everything that looks wrong) without risk (bad suggestions decay, they don't corrupt the graph). It also means the detector stays simple: it scans and creates tasks. No complex merging logic, no link creation heuristics, no content generation.

### Principle 2: Tasks Carry Enough Context To Resolve

A gap task that says "Moment X is missing an Actor link" is useless if the citizen has to re-read the moment, understand what it's about, and figure out who was involved. The task must carry the moment's content, existing links, and any entities mentioned in the text. The citizen should be able to resolve the task from the task itself, not from a separate investigation.

### Principle 3: Physics Handles Lifecycle

The detector doesn't manage task lifecycle. Created tasks enter the task physics system: urgency accumulates from CONTRIBUTES_TO links, citizens are routed by embedding similarity, completion cascades fire when resolved, and L7 forgetting prunes unresolved tasks that nobody cares about. The detector fires and forgets.

---

## DATA

| Source | Type | Purpose / Description |
|--------|------|-----------------------|
| L1 brain graph | graph | Source of Moment, Actor, Space, Thing nodes to scan |
| `graph_queries_search.py` results | runtime | Search return values that trigger empty query gaps |
| Embedding vectors on nodes | graph field | Used for duplicate detection via cosine similarity |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `runtime/organization/task_physics.py` | `create_task()` to create gap tasks in the graph |
| `runtime/physics/graph/graph_queries_search.py` | Hook into search return path for empty query detection |
| `runtime/infrastructure/embeddings/` | Cosine similarity computation for duplicate detection |
| L7 forgetting (physics tick) | Handles decay of unresolved gap tasks |

---

## INSPIRATIONS

- **Immune system analogy** — Patrol, detect, tag for repair. The detector is the innate immune system; citizens doing the resolution are the adaptive immune system.
- **Database constraint violations** — Relational databases surface constraint violations at insert time. We do the same but periodically, because graph ingestion is too messy to enforce at write time.
- **Search engine feedback loops** — Google's "did you mean?" and related searches are a form of gap detection: the system notices when queries fail and suggests alternatives. Empty query gaps are the graph equivalent.

---

## SCOPE

### In Scope

- Scanning Moment nodes for missing Actor, Space, Thing links
- Scanning Actor and Space nodes for potential duplicates via embedding similarity
- Creating gap markers from failed/low-resonance `graph_query` calls
- Creating Narrative(type='task') nodes with category='gap_detection' for each detected gap
- Packaging enough context into the task synthesis that citizens can resolve without re-querying

### Out of Scope

- **Merging duplicate nodes** — see: identity resolution module (future)
- **Creating links** — the detector never writes links, only tasks asking citizens to create them
- **Content quality** — whether a node's synthesis is well-written is not a structural gap
- **L3 universe graph scanning** — gap detection operates on L1 brain graphs. L3 has its own integrity checks (see `auto_task_taxonomy.yaml` / `graph_integrity`)
- **Real-time enforcement** — gap detection is periodic or on-demand, not inline with ingestion

---

## MARKERS

<!-- @mind:proposition Consider whether gap detection should also scan Narrative nodes for missing CONTRIBUTES_TO links (narratives that don't connect to any objective). This would bridge gap detection with the planning system. -->
