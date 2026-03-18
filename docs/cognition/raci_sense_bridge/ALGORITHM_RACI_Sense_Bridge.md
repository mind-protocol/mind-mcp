# RACI → Sense Bridge — Algorithm: The Full Chain

```
STATUS: CANONICAL
CREATED: 2026-03-18
BY: @mentor
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_RACI_Sense_Bridge.md
THIS:            ./ALGORITHM_RACI_Sense_Bridge.md
SYNC:            ./SYNC_RACI_Sense_Bridge.md

IMPL:
  - mind-mcp/mcp/tools/graph_write_handler.py  (auto-creation)
  - mind-mcp/mcp/tools/raci_query.py           (query + routing)
  - mind-mcp/mcp/tools/sense_coverage_auditor.py (audit)
  - mind-mcp/runtime/cognition/sense_engine.py  (evaluation)
```

---

## OVERVIEW

The bridge operates in two phases: **creation-time** (when graph_write runs) and **tick-time** (when sense_engine evaluates). Creation-time ensures every RACI-assigned narrative has a sense routed to the right citizens. Tick-time ensures the citizen continuously feels their responsibilities.

---

## ALGORITHM: Creation-Time (graph_write_handler.py)

### Step 1: Create RACI Links

When `graph_write` receives `responsible`, `accountable`, `consulted`, or `informed`:

```
For each RACI role:
  MERGE Actor node
  CREATE LINK from Actor → Narrative with dimensional signature:
    responsible: hierarchy=-1.0, affinity=0.8, permanence=0.8, polarity=1.0
    accountable: hierarchy=-1.0, permanence=1.0, polarity=1.0
    consulted:   trust=0.5, affinity=0.3, polarity=0.5
    informed:    affinity=0.1, polarity=0.3

  computed_type is inferred from dimensions via infer_computed_type()
```

### Step 2: Create Problem-Specific Links (if type=problem)

```
For each blocked_id in args.blocks:
  CREATE LINK from Problem → Blocked Narrative:
    polarity=-1.0, permanence=0.8, friction=0.5, hierarchy=1.0
  computed_type inferred → "blocks" or similar tension link
```

Problem nodes are born heavy: `weight=3.0, energy=1.5` (vs default 1.0/1.0).

### Step 3: Check Sense Coverage

```
coverage = ensure_sense_coverage(node_id, graph_ops)

IF no sense exists:
  → Step 4: Auto-create sense
ELIF sense exists but not routed:
  → Route existing sense to RACI actors
ELSE:
  → Fully covered, nothing to do
```

### Step 4: Auto-Create Sense

```
sense_id = f"sense:{node_id}"

sense_definition (YAML):
  measure_query: "MATCH (n {id: '{node_id}'}) RETURN n.energy, n.weight"
  variables: [energy, weight]
  outcomes: []
  score: first_outcome
  eval_interval: 20 ticks
  internalize: true

CREATE Thing node:
  id: sense_id
  type: sense
  content: YAML definition
  weight: 1.0
  energy: 1.0

CREATE LINK sense → narrative:
  computed_type: measures
  polarity: 1.0, permanence: 1.0
```

### Step 5: Route Sense to RACI Actors

```
route_sense_to_raci(sense_id, node_id, graph_ops):

  assigned = find_assigned_actors(node_id)  # queries computed_type

  FOR each (role, actors) in assigned:
    FOR each actor:
      MERGE LINK Actor → Thing(sense):
        computed_type: perceives_with
        affinity: 0.9 (R/A) or 0.4 (C/I)
        permanence: 0.9 (R/A) or 0.5 (C/I)
        internalize: true (R/A) or false (C/I)
```

---

## ALGORITHM: Tick-Time (sense_engine.py)

### Step 1: Load Senses

```
sense_engine._load_senses(citizen_id, query_fn):
  MATCH (a:Actor {id: citizen_id})-[:LINK]->(s:Thing {type: 'sense'})
  RETURN s.id, s.name, s.content, s.synthesis

  Parse YAML content → sense_definition dict
  Restore rolling state from synthesis JSON
```

### Step 2: Evaluate (every N ticks)

```
FOR each sense:
  IF tick - last_eval_tick < eval_interval: skip

  Run measure_query → get variables (energy, weight)
  Build Observation(variables, outcomes, score)
  Add to rolling history (max 200)
  Update rolling_score (EMA, alpha=0.2)
  Compute correlations (Pearson, if ≥5 observations)
  Generate insights (if |r| > 0.4)
```

### Step 3: Update L3 Sense Node

```
MATCH (s:Thing {id: sense_id})
SET s.synthesis = JSON{rolling_score, observations, insights, correlations}
SET s.energy = min(1.0, rolling_score)
SET s.weight = 0.1 + observation_count * 0.01
```

### Step 4: Internalize to L1 (if internalize=true)

```
mirror_id = f"sense:{sense_id}"

IF mirror exists in citizen's cognitive state:
  Update content with synthesis_text()
  Update energy with rolling_score
ELSE:
  Create L1 CONCEPT node:
    weight: 1.0 (heavy — stays in working memory)
    stability: 0.8 (resistant to decay)
    self_relevance: 0.8
```

The citizen now has a concept node in their brain that says:
"Score: 0.72 (15 observations) — energy positively correlated with weight (r=0.85)"

This is their **awareness** of the narrative they're responsible for.

---

## ALGORITHM: Audit (sense_coverage_auditor.py)

```
audit(graph_ops):
  Find ALL narratives with RACI links (responsible or accountable)
  FOR each narrative:
    Check: does a Thing(type=sense) with measures link exist?
    Check: is the sense linked to the responsible actor via perceives_with?
    Report: covered or gap (no_sense / no_routing / no_responsible)

  Return CoverageReport:
    coverage_ratio: covered / total
    gaps: list of {narrative_id, responsible, issue}

auto_route(graph_ops):
  Run audit
  FOR each gap with issue=no_routing:
    Find existing sense
    route_sense_to_raci()
  Return count of routes created
```

---

## DATA FLOW

```
graph_write(responsible="dev", type="problem", blocks=["obj:X"])
    │
    ├─► LINK(dev → narrative, computed_type=responsible)
    ├─► LINK(problem → obj:X, polarity=-1.0)  [blocks]
    ├─► Thing(type=sense) created
    ├─► LINK(sense → narrative, computed_type=measures)
    └─► LINK(dev → sense, computed_type=perceives_with, internalize=true)
             │
             ▼ (every 20 ticks)
        sense_engine.tick()
             │
             ├─► measure_query → {energy: 1.5, weight: 3.0}
             ├─► Observation added to history
             ├─► rolling_score updated (EMA)
             ├─► correlations computed
             ├─► L3 Thing updated (synthesis JSON)
             └─► L1 CONCEPT created/updated in dev's brain
                      │
                      ▼
                 Dev FEELS: "Problem X has energy 1.5, weight 3.0 — unresolved"
                      │
                      ▼ (when resolved)
                 Physics: energy decays → sense reports lower score → L1 node calms
```

---

## KEY DECISIONS

### D1: Auto-create vs Manual Sense

```
CHOSEN: Auto-create minimal sense (energy+weight monitoring)
WHY: A blind narrative is worse than a simple sense.
     Citizens can later upgrade to custom senses with richer queries.
     The auto-sense is a floor, not a ceiling.
```

### D2: Internalize for R/A, External for C/I

```
CHOSEN: responsible and accountable get L1 internalization (always felt)
        consulted and informed get L3 only (felt when near)
WHY: Responsible citizens must always feel their responsibilities.
     Consulted citizens need to notice when asked, not carry the weight.
     This maps to real-world RACI: R does the work, A owns the outcome,
     C provides input when asked, I just needs to know.
```

### D3: Problem Weight = 3.0

```
CHOSEN: Problems start at weight 3.0 (vs 1.0 default)
WHY: A problem must create immediate tension. If it starts at 1.0 like
     everything else, it's just another node. At 3.0, the responsible
     citizen feels it the moment it's created. The weight decays naturally
     if the problem is resolved. If not, it stays heavy.
NOTE: 3.0 is a bootstrap value. Could be derived from physics later
     (e.g., proportional to the weight of the blocked objective).
```

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|-------------|-------------|
| graph_write_handler | _create_link(), ctx.graph_ops._query() | RACI links + sense + routing |
| raci_query | find_assigned_actors(), route_sense_to_raci() | RACI resolution + routing |
| sense_engine | tick(), _load_senses() | Continuous evaluation + L1 injection |
| sense_coverage_auditor | audit(), auto_route() | Coverage report + gap fixing |
| graph physics (tick runner) | Energy decay, tension propagation | Problem resolution detection |
