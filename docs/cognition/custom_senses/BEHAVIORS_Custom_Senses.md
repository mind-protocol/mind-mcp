# Custom Senses — Behaviors: Observable Effects of Citizen-Defined Perception

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Custom_Senses.md
THIS:            BEHAVIORS_Custom_Senses.md (you are here)
PATTERNS:        ./PATTERNS_Custom_Senses.md
ALGORITHM:       ./ALGORITHM_Custom_Senses.md
VALIDATION:      ./VALIDATION_Custom_Senses.md
HEALTH:          ./HEALTH_Custom_Senses.md
IMPLEMENTATION:  ./IMPLEMENTATION_Custom_Senses.md
SYNC:            ./SYNC_Custom_Senses.md

IMPL:            runtime/cognition/exteroception.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS

### B1: Custom Senses Load From Graph Links

**Why:** A citizen's perceptual field should be defined by their graph relationships, not by configuration files or code changes. Loading senses from `->perceives_with->` links means adopting a new sense is a single graph link operation.

```
GIVEN:  an Actor has one or more ->perceives_with-> links to Thing(type=sense) nodes
WHEN:   exteroception engine initializes custom senses (_load_custom_senses)
THEN:   each linked Thing's content field is parsed as YAML
AND:    a SensoryChannel is registered per sense with the sense's priority and refractory_ticks
AND:    up to 10 custom senses are loaded (query LIMIT 10)
AND:    the _custom_senses_loaded flag is set to prevent re-loading
```

### B2: YAML Filter Conditions Produce Stimuli

**Why:** Citizens need to define what they notice without writing code. Declarative YAML filters specify source type, scan scope, field comparisons, and keyword patterns. When a node in L3 matches all conditions, a stimulus is produced.

```
GIVEN:  a custom sense defines source, scan, filter conditions, and keywords
WHEN:   _evaluate_custom_senses runs during the exteroception tick
THEN:   L3 nodes of the specified source type are queried from the specified scan scope
AND:    each node is tested against filter conditions (> N, < N, >= N, <= N, contains X)
AND:    each node is tested against keyword list (any keyword in synthesis + name)
AND:    the first matching node produces a stimulus using the sense's template
AND:    only one match per sense per tick (break after first)
```

### B3: Custom Stimuli Compete in Standard Gating

**Why:** Custom senses must not bypass the attention budget. They produce candidate tuples (priority, channel_name, content, energy, extra) that enter the same priority-sorted, channel-gated pipeline as built-in channels. The MAX_STIMULI_PER_TICK cap applies equally.

```
GIVEN:  custom senses have produced candidate stimuli
WHEN:   the exteroception tick processes all candidates (built-in + custom)
THEN:   all candidates are sorted by priority descending
AND:    each candidate's channel is checked for can_fire(tick)
AND:    only MAX_STIMULI_PER_TICK (3) stimuli are emitted total
AND:    custom channels are rearmed using the same try_rearm() logic as built-in channels
```

### B4: Senses Are Shareable Across Citizens

**Why:** Echo builds `gossip_radar`, Vox adopts it. The sense Thing node exists once in the graph; any Actor can link to it via `->perceives_with->`. Authorship is tracked via `->created_by->` on the Thing node. Multiple citizens can use the same sense definition simultaneously.

```
GIVEN:  citizen A creates a Thing(type=sense) with ->created_by-> A
WHEN:   citizen B creates a ->perceives_with-> link to that same Thing
THEN:   citizen B's exteroception engine loads and evaluates that sense
AND:    the sense definition is shared (same Thing node), not copied
AND:    citizen A receives attribution credit via the ->created_by-> link
```

### B5: Scan Scope Controls Query Breadth

**Why:** Different senses need different scanning breadths. Monitoring "narratives in my spaces" is narrow and cheap. Monitoring "all things in the graph" is broad and expensive. The `scan` field controls which Cypher query pattern is used.

```
GIVEN:  a sense defines scan as one of: "spaces_i_am_in", "all", or a specific space ID
WHEN:   the sense is evaluated
THEN:   scan="spaces_i_am_in" queries nodes linked to spaces the citizen is in
AND:    scan="all" queries nodes of the source type globally (ORDER BY energy DESC LIMIT 20)
AND:    scan="{space_id}" queries nodes linked to that specific space
```

### B6: Citizens Without Custom Senses Experience No Change

**Why:** The custom sense system must have zero overhead for citizens who do not use it. If no `->perceives_with->` links exist, the query returns empty, no parsing occurs, and no evaluation runs.

```
GIVEN:  a citizen has zero ->perceives_with-> links to Thing(type=sense) nodes
WHEN:   exteroception tick runs
THEN:   _load_custom_senses executes one graph query that returns empty
AND:    _custom_senses list remains empty
AND:    _evaluate_custom_senses returns immediately (empty list check)
AND:    no performance difference from a system without custom senses
```

---

## OBJECTIVES SERVED

| Behavior ID | Objective | Why It Matters |
|-------------|-----------|----------------|
| B1 | O1: Citizen-defined perception | Graph links = the mechanism for extending perception |
| B2 | O3: Two-tier complexity (YAML tier) | Declarative filters lower the barrier to sense creation |
| B3 | O4: Seamless integration | Standard gating prevents custom senses from overwhelming attention |
| B4 | O2: Shareability and credit | One sense, many users, authorship tracked |
| B5 | O1: Citizen-defined perception | Scan scope gives citizens control over perception breadth |
| B6 | O4: Seamless integration | Zero overhead for non-users preserves baseline performance |

---

## INPUTS / OUTPUTS

### Primary Function: `ExteroceptionEngine.tick()`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| citizen_id | str | Actor ID for the citizen being processed |
| tick | int | Current tick number |
| query_fn | Callable | Graph query function: (cypher, params) -> result_set |
| drives | dict (optional) | Current drive intensities for limbic bias |
| desires | list (optional) | Active desire node embeddings for goal alignment |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| stimuli | list[Stimulus] | Combined stimuli from built-in + custom channels (max 3 per tick) |

**Side Effects:**

- Loads custom sense definitions from graph on first tick (_custom_senses_loaded flag)
- Registers new SensoryChannel instances in self.channels dict for each loaded sense
- Updates channel last_fired_tick and is_armed state on fire/rearm

---

## EDGE CASES

### E1: Malformed YAML in Sense Content

```
GIVEN:  a Thing(type=sense) has content that is not valid YAML
THEN:   yaml.safe_load raises an exception
AND:    the exception is caught and logged at debug level
AND:    the malformed sense is skipped, remaining senses load normally
```

### E2: Empty Content Field

```
GIVEN:  a Thing(type=sense) has null or empty content
THEN:   the sense is skipped (continue in loop, before YAML parsing)
AND:    no error is logged — empty content is silently ignored
```

### E3: YAML Parses to Non-Dict

```
GIVEN:  content is valid YAML but parses to a list or scalar, not a dict
THEN:   the isinstance(definition, dict) check fails
AND:    the sense is skipped silently
```

### E4: Filter Field Not Present on Node

```
GIVEN:  a filter references a field (e.g., "friction") that is None on the queried node
THEN:   _match_filters returns False (node_data.get(field) is None -> return False)
AND:    the node is excluded from matches
```

### E5: Sense Channel Name Collision

```
GIVEN:  two different Thing(type=sense) nodes have the same ID
THEN:   impossible — IDs are unique in FalkorDB
AND:    channel names are "custom_{sense_id}", so collisions cannot occur
```

---

## ANTI-BEHAVIORS

### A1: Custom Senses Bypass Gating

```
GIVEN:   a custom sense produces a stimulus candidate
WHEN:    exteroception tick processes candidates
MUST NOT: inject the stimulus directly into the output list
INSTEAD:  add as candidate tuple, let priority sort + channel gating decide
```

### A2: Sense Loading Runs Every Tick

```
GIVEN:   custom senses have already been loaded (_custom_senses_loaded = True)
WHEN:    subsequent ticks execute
MUST NOT: re-query the graph for ->perceives_with-> links every tick
INSTEAD:  use the cached _custom_senses list until engine is reset
```

### A3: Unbounded Sense Count

```
GIVEN:   a citizen links to more than 10 Thing(type=sense) nodes
WHEN:    _load_custom_senses queries the graph
MUST NOT: load all linked senses without limit
INSTEAD:  the query uses LIMIT 10 to cap the number of loaded senses
```

### A4: Custom Senses Execute Arbitrary Python

```
GIVEN:   the current implementation is YAML-only
WHEN:    evaluating custom senses
MUST NOT: exec() or eval() any Python code from Thing content fields
INSTEAD:  parse YAML and evaluate filter conditions via _match_filters()
```

---

## MARKERS

<!-- @mind:todo Add a behavior for dynamic sense refresh — currently senses are loaded once and cached for the engine's lifetime -->
<!-- @mind:todo Define behavior for Python (programmatic) senses when the v2 tier is implemented -->
<!-- @mind:proposition Consider a B7 for sense-contributed awareness text — custom senses could contribute lines to the awareness text summary, not just stimuli -->
