# Custom Senses — Implementation: Code Architecture and Structure

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
ALGORITHM:       ./ALGORITHM_Custom_Senses.md
VALIDATION:      ./VALIDATION_Custom_Senses.md
THIS:            IMPLEMENTATION_Custom_Senses.md (you are here)
HEALTH:          ./HEALTH_Custom_Senses.md
SYNC:            ./SYNC_Custom_Senses.md

IMPL:            runtime/cognition/exteroception.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

```
runtime/cognition/
└── exteroception.py    # ExteroceptionEngine — built-in channels + custom senses
```

Custom senses are implemented as three methods within the existing ExteroceptionEngine class in exteroception.py. There is no separate file for custom senses — they are integrated directly into the exteroception module.

### File Responsibilities

| File | Purpose | Key Functions/Classes | Lines | Status |
|------|---------|----------------------|-------|--------|
| `runtime/cognition/exteroception.py` | External sensory awareness: built-in channels, custom sense loading/evaluation, awareness text | `ExteroceptionEngine`, `_load_custom_senses()`, `_evaluate_custom_senses()`, `_match_filters()`, `SensoryChannel`, `PerceivedNode` | ~580 | WATCH |

**Size Thresholds:**
- **OK** (<400 lines): Healthy size, easy to understand
- **WATCH** (400-700 lines): Getting large, consider extraction opportunities
- **SPLIT** (>700 lines): Too large, must split before adding more code

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Extension within Pipeline

Custom senses are not a separate module — they are an extension point within the exteroception tick pipeline. The tick() method calls _evaluate_custom_senses() after processing built-in channels, appends the results to the shared candidates list, and lets the standard gating sort and filter everything together.

**Why this pattern:** Custom senses must compete with built-in channels for the same attention budget. Keeping them in the same file and pipeline guarantees they flow through the same gating. A separate module would risk divergent gating logic.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Lazy initialization | `_custom_senses_loaded` flag | Defer graph query until first tick, avoid startup cost |
| Data-driven dispatch | YAML sense definitions | Scan scope, filter conditions, and stimulus templates are data, not code paths |
| Strategy via dict | `scan` field selects Cypher pattern | Three query patterns selected by string value, not if/elif |
| Null object | Empty list return | `_evaluate_custom_senses` returns [] when no senses loaded — caller does not special-case |

### Anti-Patterns to Avoid

- **Separate custom sense pipeline**: Do not create a parallel stimulus output path. Custom candidates must enter the same candidates list as built-in channels.
- **Per-tick sense reloading**: Do not query the graph for sense definitions every tick. The lazy load + cache pattern exists for performance.
- **eval/exec for filter conditions**: Do not add dynamic Python evaluation for filter expressions. The _match_filters function handles a fixed set of operators.

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Custom sense system | YAML parsing, filter evaluation, channel registration | Sense creation, link management, graph topology | `_load_custom_senses()`, `_evaluate_custom_senses()` called from `tick()` |
| Filter evaluation | Comparison operators, keyword containment | Complex boolean logic, nested conditions, regex | `_match_filters(node_data, filters) -> bool` |

---

## SCHEMA

### Thing(type=sense) — Graph Node

```yaml
ThingSense:
  required:
    - id: string           # unique Thing node ID
    - type: "sense"        # discriminator
    - content: string      # YAML filter definition
  optional:
    - name: string         # human-readable sense name
    - media.code.uri: string  # Python script URI (v2, not yet implemented)
  relationships:
    - ->created_by->: Actor   # authorship/credit
    - <-perceives_with<-: Actor  # citizens using this sense
```

### YAML Sense Definition (in content field)

```yaml
SenseDefinition:
  required:
    - source: enum         # narrative|moment|actor|thing|space
  optional:
    - name: string         # display name (overrides Thing name)
    - scan: string         # spaces_i_am_in (default) | all | {space_id}
    - filter: dict         # {field: condition_string}
    - keywords: list       # [string] for synthesis+name matching
    - stimulus: dict       # {template, energy, source}
    - priority: int        # channel priority (default: 50)
    - refractory_ticks: int # min ticks between firings (default: 20)
  constraints:
    - filter conditions must be one of: "> N", "< N", ">= N", "<= N", "contains X"
    - stimulus.template may use {node.name} and {node.synthesis} placeholders
```

---

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| `_load_custom_senses()` | `exteroception.py:352` | First call from `tick()` when `_custom_senses_loaded` is False |
| `_evaluate_custom_senses()` | `exteroception.py:391` | Every call from `tick()`, after built-in channel processing |
| `_match_filters()` | `exteroception.py:549` | Called by `_evaluate_custom_senses()` per node per sense |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

### Sense Loading Flow: Graph to Cache

Loads sense definitions from graph links into the engine's in-memory cache. Runs once per engine lifetime. Matters because it establishes the citizen's custom perceptual field.

```yaml
flow:
  name: sense_loading
  purpose: Populate custom sense cache from graph topology
  scope: Actor's ->perceives_with-> links to Thing(type=sense) nodes
  steps:
    - id: query_links
      description: Query graph for linked Thing(type=sense) nodes
      file: runtime/cognition/exteroception.py
      function: _load_custom_senses
      input: citizen_id, query_fn
      output: list of (id, name, content) tuples
      trigger: tick() when _custom_senses_loaded is False
      side_effects: none (read-only graph query)
    - id: parse_yaml
      description: Parse YAML content from each Thing node
      file: runtime/cognition/exteroception.py
      function: _load_custom_senses
      input: content string
      output: dict (sense definition)
      trigger: query returns rows
      side_effects: none
    - id: register_channels
      description: Create SensoryChannel per sense in self.channels
      file: runtime/cognition/exteroception.py
      function: _load_custom_senses
      input: sense definition dict
      output: SensoryChannel instance
      trigger: valid YAML parsed
      side_effects: modifies self.channels, self._custom_senses
  docking_points:
    available:
      - id: sense_load_output
        type: graph_ops
        direction: output
        file: runtime/cognition/exteroception.py
        function: _load_custom_senses
        trigger: first tick
        payload: list[dict] (parsed sense definitions)
        async_hook: not_applicable
        needs: none
        notes: Observable by checking len(self._custom_senses) after first tick
    health_recommended:
      - dock_id: sense_load_output
        reason: Verifies that sense definitions are correctly parsed from graph
```

### Sense Evaluation Flow: Cache to Candidates

Evaluates loaded senses against L3 nodes each tick. Matters because this is where perception actually happens — matching graph state to sense filters.

```yaml
flow:
  name: sense_evaluation
  purpose: Produce stimulus candidates from custom sense filter evaluation
  scope: Per-tick evaluation of all loaded custom senses
  steps:
    - id: check_gating
      description: Check if each sense's channel can fire this tick
      file: runtime/cognition/exteroception.py
      function: _evaluate_custom_senses
      input: tick number, SensoryChannel state
      output: boolean (can_fire)
      trigger: every tick
      side_effects: none
    - id: query_nodes
      description: Execute Cypher query based on sense scan scope
      file: runtime/cognition/exteroception.py
      function: _evaluate_custom_senses
      input: scan scope, source type, citizen_id
      output: list of node rows (up to 20)
      trigger: channel can fire
      side_effects: none (read-only)
    - id: filter_match
      description: Apply filter conditions and keywords to each node
      file: runtime/cognition/exteroception.py
      function: _match_filters
      input: node_data dict, filters dict
      output: boolean (matches)
      trigger: query returns rows
      side_effects: none
    - id: produce_candidate
      description: Build stimulus candidate tuple from first matching node
      file: runtime/cognition/exteroception.py
      function: _evaluate_custom_senses
      input: sense definition, matching node data
      output: candidate tuple
      trigger: filter match succeeds
      side_effects: none
  docking_points:
    available:
      - id: eval_candidates_output
        type: event
        direction: output
        file: runtime/cognition/exteroception.py
        function: _evaluate_custom_senses
        trigger: every tick
        payload: list[tuple] (candidate tuples)
        async_hook: not_applicable
        needs: none
        notes: Observable by inspecting return value of _evaluate_custom_senses
      - id: filter_match_result
        type: custom
        direction: output
        file: runtime/cognition/exteroception.py
        function: _match_filters
        trigger: per node per sense
        payload: bool
        async_hook: not_applicable
        needs: none
        notes: Low-level dock — useful for verifying filter correctness
    health_recommended:
      - dock_id: eval_candidates_output
        reason: Verifies that loaded senses produce expected candidates when matching nodes exist
```

---

## LOGIC CHAINS

### LC1: Sense Definition to Stimulus

**Purpose:** Trace the full path from a graph-stored sense definition to a stimulus delivered to the citizen.

```
Thing(type=sense).content [YAML in graph]
  -> yaml.safe_load()                           # parse to dict
    -> _load_custom_senses()                    # register channel + cache
      -> _evaluate_custom_senses()              # per tick
        -> _safe_query(scan_cypher)             # get L3 nodes
          -> _match_filters(node_data, filters) # test conditions
            -> template.replace()               # build content string
              -> candidate tuple                # (priority, ch, content, energy, extra)
                -> tick() candidates list       # merged with built-in
                  -> priority sort + gating     # standard pipeline
                    -> Stimulus output          # injected into Law 1
```

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
runtime/cognition/exteroception.py
    └── imports -> runtime/cognition/tick_runner_l1_cognitive_engine (Stimulus dataclass)
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `yaml` (PyYAML) | Parsing YAML content from Thing nodes | `_load_custom_senses()` (late import) |
| `time` | Timestamp for scan window | `tick()` |
| `logging` | Debug-level logging for sense loading/parsing | throughout |

---

## STATE MANAGEMENT

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| `_custom_senses` | `ExteroceptionEngine` instance | per-citizen | loaded once on first tick, cached for engine lifetime |
| `_custom_senses_loaded` | `ExteroceptionEngine` instance | per-citizen | False at init, True after first load |
| `channels["custom_*"]` | `ExteroceptionEngine.channels` dict | per-citizen | created during load, gating state updated per tick |

### State Transitions

```
_custom_senses_loaded=False --[first tick]--> _custom_senses_loaded=True, _custom_senses populated
channels --[load]--> new "custom_{id}" entries added
channels["custom_{id}"].is_armed=True --[fire]--> is_armed=False --[try_rearm after refractory]--> is_armed=True
```

---

## RUNTIME BEHAVIOR

### Initialization

```
1. ExteroceptionEngine.__init__() sets _custom_senses=[], _custom_senses_loaded=False
2. No graph queries at init time — all loading deferred to first tick
```

### Main Loop (Per Tick)

```
1. tick() processes built-in channels (6 channels)
2. tick() checks _custom_senses_loaded — if False, calls _load_custom_senses()
3. tick() calls _evaluate_custom_senses() — returns candidate list
4. candidates from custom + built-in are merged, sorted, gated
5. MAX_STIMULI_PER_TICK stimuli emitted
6. all channels (built-in + custom) rearmed via try_rearm()
```

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| MAX_STIMULI_PER_TICK | `exteroception.py:31` | 3 | Max stimuli emitted per tick (shared budget) |
| LIMIT in loading query | `exteroception.py:358` | 10 | Max custom senses loaded per citizen |
| LIMIT in eval query | `exteroception.py:417` | 20 | Max nodes scanned per sense per tick |
| Default priority | `exteroception.py:379` | 50 | Channel priority when not specified in YAML |
| Default refractory_ticks | `exteroception.py:380` | 20 | Refractory period when not specified in YAML |

---

## BIDIRECTIONAL LINKS

### Code -> Docs

| File | Line | Reference |
|------|------|-----------|
| `runtime/cognition/exteroception.py` | 4 | `DOCS: docs/cognition/exteroception/` (general exteroception docs) |

### Docs -> Code

| Doc Section | Implemented In |
|-------------|----------------|
| ALGORITHM: _load_custom_senses | `exteroception.py:352` (_load_custom_senses) |
| ALGORITHM: _evaluate_custom_senses | `exteroception.py:391` (_evaluate_custom_senses) |
| ALGORITHM: _match_filters | `exteroception.py:549` (_match_filters) |
| BEHAVIOR B1: sense loading | `exteroception.py:352-389` |
| BEHAVIOR B2: filter evaluation | `exteroception.py:391-475` |
| BEHAVIOR B3: standard gating | `exteroception.py:234-246` (in tick()) |
| VALIDATION V6: safe YAML | `exteroception.py:368` (yaml.safe_load) |

---

## EXTRACTION CANDIDATES

exteroception.py is at WATCH status (~580 lines). If custom senses grow significantly (Python tier, additional filter operators, sense validation), extraction would be warranted:

| File | Current | Target | Extract To | What to Move |
|------|---------|--------|------------|--------------|
| `exteroception.py` | ~580L | <400L | `custom_sense_evaluator.py` | `_load_custom_senses`, `_evaluate_custom_senses`, `_match_filters` (~130L) |

Not urgent — the file is within WATCH range and the custom sense code is well-contained within the class. Extract only if the Python sense tier adds significant complexity.

---

## MARKERS

<!-- @mind:todo Add DOCS: comment to exteroception.py pointing to this doc chain (docs/cognition/custom_senses/) -->
<!-- @mind:todo Create runtime/cognition/custom_senses.py when Python sense tier is implemented — currently OBJECTIVES references it as "to be created" -->
<!-- @mind:proposition If the Python tier is added, extracting the three custom sense methods into a separate file becomes necessary to stay under WATCH threshold -->
