# Custom Senses — Algorithm: YAML Filter Evaluation Pipeline

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Custom_Senses.md
BEHAVIORS:       ./BEHAVIORS_Custom_Senses.md
PATTERNS:        ./PATTERNS_Custom_Senses.md
THIS:            ALGORITHM_Custom_Senses.md (you are here)
VALIDATION:      ./VALIDATION_Custom_Senses.md
HEALTH:          ./HEALTH_Custom_Senses.md
IMPLEMENTATION:  ./IMPLEMENTATION_Custom_Senses.md
SYNC:            ./SYNC_Custom_Senses.md

IMPL:            runtime/cognition/exteroception.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

Custom senses operate through two phases: **Load** and **Evaluate**. Loading happens once per engine lifetime (lazy, on first tick). Evaluation happens every tick. The load phase queries the citizen's `->perceives_with->` links for Thing(type=sense) nodes, parses their YAML content, and registers a SensoryChannel per sense. The evaluate phase iterates over loaded senses, checks channel gating, builds and executes a Cypher query based on the sense's scan scope, applies filter conditions and keyword matching against returned nodes, and produces stimulus candidate tuples that enter the standard exteroception gating pipeline.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| O1: Citizen-defined perception | B1, B2, B5 | The load/evaluate cycle is how sense definitions become active perception |
| O3: Two-tier complexity (YAML) | B2 | YAML filter evaluation is the declarative tier's core algorithm |
| O4: Seamless integration | B3, B6 | Candidates produced here flow into the same gating as built-in channels |

---

## DATA STRUCTURES

### Parsed Sense Definition

```
dict with fields:
  _sense_id: str        # injected — Thing node ID
  _name: str            # injected — Thing node name or ID fallback
  source: str           # "narrative", "moment", "actor", "thing", "space"
  scan: str             # "spaces_i_am_in", "all", or specific space ID
  filter: dict          # field -> condition string mapping
  keywords: list[str]   # keyword patterns for synthesis+name matching
  stimulus: dict        # {template, energy, source}
  priority: int         # channel priority (default: 50)
  refractory_ticks: int # min ticks between firings (default: 20)
```

### Stimulus Candidate Tuple

```
tuple(priority: int, channel_name: str, content: str, energy: float, extra: dict)
  priority:     from sense definition (default 50)
  channel_name: "custom_{sense_id}"
  content:      template with {node.name} and {node.synthesis} substituted
  energy:       from sense stimulus config (default 0.3)
  extra:        {"source_override": sense_name}
```

### Filter Condition

```
str with one of these formats:
  "> N"        — field must be strictly greater than N (float comparison)
  "< N"        — field must be strictly less than N
  ">= N"       — field must be greater or equal to N
  "<= N"       — field must be less or equal to N
  "contains X" — field must contain X as substring (case-insensitive)
```

---

## ALGORITHM: _load_custom_senses()

### Step 1: Query Graph for Linked Senses

Query the citizen's `->perceives_with->` links for Thing nodes with `type=sense`. The query uses the standard LINK edge type (all edges in the mind schema are LINK). Limited to 10 results.

```
MATCH (a:Actor {id: $cid})-[:LINK]->(s:Thing)
WHERE s.type = 'sense'
RETURN s.id, s.name, s.content
LIMIT 10
```

### Step 2: Parse YAML Content

For each returned row, skip if content is empty. Parse the content field via `yaml.safe_load()`. If the result is not a dict, skip. Inject `_sense_id` and `_name` into the definition dict for downstream identification.

### Step 3: Register SensoryChannel

For each valid definition, create a SensoryChannel with name `"custom_{sense_id}"`, priority from the definition (default 50), and refractory_ticks from the definition (default 20). Register it in `self.channels` only if not already present (avoids duplicate registration on hypothetical re-load).

### Step 4: Mark Loaded

Set `self._custom_senses_loaded = True`. Append valid definitions to `self._custom_senses`. Log the count at debug level.

### Error Handling

Any exception during YAML parsing for a single sense is caught, logged at debug level, and that sense is skipped. Other senses continue loading. This ensures one malformed sense cannot break the entire custom sense system.

---

## ALGORITHM: _evaluate_custom_senses()

### Step 1: Early Exit

If `self._custom_senses` is empty, return an empty list immediately. Zero overhead for citizens without custom senses.

### Step 2: Iterate Senses

For each loaded sense definition:

**2a. Check Channel Gating**

Look up the SensoryChannel by name `"custom_{sense_id}"`. If the channel does not exist or `can_fire(tick)` returns False (refractory period not elapsed), skip this sense.

**2b. Build Cypher Query**

Capitalize the `source` field to get the FalkorDB label (e.g., "narrative" -> "Narrative"). Select the query pattern based on `scan`:

```
IF scan == "spaces_i_am_in":
    MATCH (a:Actor {id: $cid})-[:LINK]->(s:Space)<-[:LINK]-(n:{Source})
    RETURN n.id, n.name, n.synthesis, n.energy, n.weight, n.friction
    ORDER BY n.energy DESC LIMIT 20
    params = {cid: citizen_id}

ELIF scan == "all":
    MATCH (n:{Source})
    RETURN n.id, n.name, n.synthesis, n.energy, n.weight, n.friction
    ORDER BY n.energy DESC LIMIT 20
    params = {}

ELSE (specific space ID):
    MATCH (n:{Source})-[:LINK]->(s:Space {id: $space})
    RETURN n.id, n.name, n.synthesis, n.energy, n.weight, n.friction
    ORDER BY n.energy DESC LIMIT 20
    params = {space: scan}
```

**2c. Execute Query and Filter**

Execute via `_safe_query()`. For each returned row, extract node data (id, name, synthesis, energy, weight, friction) into a dict. Apply `_match_filters()` — if any filter condition fails, skip the node. Apply keyword matching — if keywords are defined and none appear in (synthesis + " " + name).lower(), skip the node.

**2d. Produce Candidate**

For the first matching node, build the stimulus content by substituting `{node.name}` and `{node.synthesis}` (truncated to 60 chars) into the template string. Create the candidate tuple. Break — only one match per sense per tick.

### Step 3: Return Candidates

Return the accumulated list of candidate tuples. These are appended to the main candidates list in `tick()` and sorted/gated together with built-in channel candidates.

---

## ALGORITHM: _match_filters()

### Logic

Iterate over each (field, condition) pair in the filters dict:

1. Look up the field value in node_data. If None, return False (missing field fails the filter).
2. Parse the condition string:
   - `">= N"` — convert value and N to float, check `value >= N`
   - `"<= N"` — convert to float, check `value <= N`
   - `"> N"` — convert to float, check `value > N`
   - `"< N"` — convert to float, check `value < N`
   - `"contains X"` — check `X.lower() in str(value).lower()`
3. The order of checks matters: `>=` and `<=` are checked before `>` and `<` to avoid `">="` being parsed as `">"` with `"= N"` remainder.
4. If any conversion fails (ValueError, TypeError), return False.
5. If all conditions pass, return True.

---

## KEY DECISIONS

### D1: One Match Per Sense Per Tick

```
IF a node matches all filters and keywords for a sense:
    produce one candidate, then break
    WHY: Prevents a single prolific sense from flooding the candidate list.
         The sense can fire again after its refractory period elapses.
ELSE:
    continue to next node (up to LIMIT 20)
```

### D2: Lazy Loading vs Per-Tick Refresh

```
IF _custom_senses_loaded is False:
    load senses from graph
    WHY: Avoids a graph query every tick. Senses are assumed to change
         infrequently. One query at initialization is sufficient.
ELSE:
    skip loading, use cached definitions
    WHY: Performance — graph queries for sense definitions every tick
         would add unnecessary latency for a rarely-changing configuration.
LIMITATION: Adding or removing ->perceives_with-> links requires engine
            restart or manual reset of _custom_senses_loaded.
```

### D3: Source Type Capitalization

```
source field value is lowercased in YAML (e.g., "narrative")
Cypher label requires capitalized form (e.g., "Narrative")
DECISION: .capitalize() in _evaluate_custom_senses
WHY: Matches FalkorDB label convention. Citizens write lowercase in YAML,
     engine handles the conversion.
```

---

## DATA FLOW

```
Actor ->perceives_with-> Thing(type=sense) [in graph]
    |
    v
_load_custom_senses() -- Cypher query, YAML parse, channel register [once]
    |
    v
_evaluate_custom_senses() -- per tick
    |
    v
For each sense: check gating -> build Cypher -> query L3 -> filter nodes -> keyword match
    |
    v
First matching node -> template substitution -> candidate tuple
    |
    v
Appended to main candidates list in tick()
    |
    v
Priority sort + channel gating (shared with built-in channels)
    |
    v
Stimulus output (max 3 per tick total)
```

---

## COMPLEXITY

**Time:** O(S * N) per tick, where S = number of custom senses (max 10), N = nodes returned per sense query (max 20). Worst case: 10 senses * 20 nodes * filter evaluation = 200 filter evaluations per tick. Filter evaluation is O(F) where F = number of filter conditions (typically 1-3). Total: O(10 * 20 * 3) = O(600) simple comparisons per tick.

**Space:** O(S) for cached sense definitions. O(N) per sense for query results (not accumulated across senses).

**Bottlenecks:**
- Graph queries: one query per sense per tick (up to 10 queries). Each is a simple Cypher scan with LIMIT 20. Typically <5ms each.
- YAML parsing: happens once during loading, not per tick. Cost is negligible.
- Filter evaluation: pure Python float/string comparisons. Negligible compared to graph query latency.

---

## HELPER FUNCTIONS

### `_safe_query(query_fn, cypher, params)`

**Purpose:** Execute a Cypher query with error swallowing. Returns empty list on any exception.

**Logic:** Call query_fn(cypher, params). If exception, return []. If None, return [].

### `_match_filters(node_data, filters)`

**Purpose:** Evaluate all filter conditions against a node's data fields. Returns True only if all conditions pass.

**Logic:** See ALGORITHM: _match_filters() section above.

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| FalkorDB (via query_fn) | Cypher queries for sense loading and node scanning | Result sets of Thing and source-type nodes |
| `yaml` (PyYAML) | `yaml.safe_load(content)` | Parsed dict from YAML string |
| `ExteroceptionEngine.channels` | Register/lookup SensoryChannel | Channel gating state (can_fire, fire, try_rearm) |

---

## MARKERS

<!-- @mind:todo Design the Python (programmatic) sense evaluation step — would replace _evaluate_custom_senses for senses with media.code.uri -->
<!-- @mind:todo Consider adding a sense-level scan interval (evaluate every N ticks, not every tick) to reduce graph query load for expensive senses -->
<!-- @mind:proposition The 20-node LIMIT per sense query is hardcoded — consider making it configurable per sense in the YAML definition -->
