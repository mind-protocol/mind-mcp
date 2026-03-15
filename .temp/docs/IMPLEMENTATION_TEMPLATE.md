# IMPLEMENTATION: {Module_Name}

<!-- STATUS: DRAFT | REVIEW | STABLE -->
<!-- UPDATED: YYYY-MM-DD -->

## CHAIN

```
  OBJECTIVES_{Module_Name}.md
    PATTERNS_{Module_Name}.md
      BEHAVIORS_{Module_Name}.md
        ALGORITHM_{Module_Name}.md
          VALIDATION_{Module_Name}.md
→           IMPLEMENTATION (you are here)
              → HEALTH_{Module_Name}.md
                → SYNC_{Module_Name}.md

IMPL: {path/to/primary/code.py}
```

---

## CODE STRUCTURE

```
{module_root}/
├── {file_1.py}           # {responsibility}
├── {file_2.py}           # {responsibility}
├── {subdir}/
│   ├── {file_3.py}       # {responsibility}
│   └── {file_4.py}       # {responsibility}
└── tests/
    └── {test_file.py}    # {what it tests}
```

## FILE RESPONSIBILITIES

| File | Purpose | Key functions/classes | Lines | Status |
|------|---------|----------------------|-------|--------|
| {file.py} | {what it does} | {main symbols} | {N} | OK / WATCH / SPLIT |

**Size thresholds:** <400 = OK, 400–700 = WATCH, >700 = SPLIT

## DESIGN PATTERNS

### Architecture pattern

{What pattern the code follows and why — e.g., pipeline, event-driven, tick-based.}

### Code patterns in use

- {Pattern 1}: {where and why}
- {Pattern 2}: {where and why}

### Anti-patterns to avoid

- {Anti-pattern 1}: {why it's bad here}
- {Anti-pattern 2}: {why}

## SCHEMA USAGE

How the code interacts with the graph schema (schema.yaml v2.2).

### Node operations

| Operation | Node type | Fields read | Fields written | Cypher pattern |
|-----------|-----------|-------------|----------------|----------------|
| {create/read/update} | {actor/moment/narrative/space/thing} | {NodeBase fields} | {NodeBase fields} | {MERGE/MATCH pattern} |

### Link operations

| Operation | Link dimensions used | Cypher pattern |
|-----------|---------------------|----------------|
| {create/read/update} | {weight, energy, trust, ...} | {pattern} |

### Cognitive type mapping (if L1)

| Code symbol | Schema cognitive_type | Universal node_type | type field value |
|-------------|----------------------|--------------------|--------------------|
| {class/var} | {memory/concept/...} | {moment/thing/...} | {string value} |

## ENTRY POINTS

| Entry point | Trigger | Schema types consumed | Schema types produced |
|-------------|---------|----------------------|----------------------|
| {function/endpoint} | {what triggers it} | {node/link types read} | {node/link types created/modified} |

## DATA FLOW AND DOCKING

### Flow: {Flow name}

```
{source} → [{transform_1}] → [{transform_2}] → {destination}
```

1. **{step}:** {what happens — schema fields involved}
2. **{step}:** {what happens}
3. **{step}:** {what happens}

**Docking points:**
- Input: {where data enters — API, graph query, stimulus, tick step}
- Output: {where results go — graph write, WM update, drive update}

**Health recommendation:** {which HEALTH check should monitor this flow}

## TICK INTEGRATION

How this code participates in the 17-step tick cycle (Law 12).

| Tick step | Law | Function called | Schema fields touched |
|-----------|-----|-----------------|----------------------|
| {N} | L{N} | {function_name()} | {fields read/written} |

## MODULE DEPENDENCIES

### Internal

```
{this_module}
├── imports {internal_module_1}     # {what for}
└── imports {internal_module_2}     # {what for}
```

### External

| Package | Version | Purpose |
|---------|---------|---------|
| {package} | {version} | {why needed} |

## STATE MANAGEMENT

| State | Location | Scope | Lifecycle | Schema backing |
|-------|----------|-------|-----------|----------------|
| {state name} | {where — graph, memory, file} | {per-tick / per-session / persistent} | {created/updated/destroyed when} | {NodeBase/LinkBase field or N/A} |

## RUNTIME BEHAVIOR

### Initialization

{What happens at startup — graph connections, seed loading, etc.}

### Main loop / tick participation

{How this module runs — called per tick, event-driven, on-demand.}

### Shutdown

{Cleanup, state persistence, etc.}

## CONFIGURATION

| Key | Location | Default | Description | Schema impact |
|-----|----------|---------|-------------|---------------|
| {config_key} | {file/env} | {value} | {what it controls} | {which schema fields it affects} |

## BIDIRECTIONAL LINKS

### Code → Docs

Files should contain `DOCS:` markers pointing to their documentation:

```python
# DOCS: docs/{area}/{module}/PATTERNS_{Module_Name}.md
```

### Docs → Code

| Doc | Code reference | Symbols |
|-----|---------------|---------|
| PATTERNS | {file.py} | {functions, classes} |
| ALGORITHM | {file.py} | {functions implementing the algorithm} |

## EXTRACTION CANDIDATES

Files approaching WATCH/SPLIT threshold.

| File | Current lines | Status | Extraction target |
|------|--------------|--------|-------------------|
| {file.py} | {N} | WATCH | {what to extract and where} |

<!-- @mind:TODO — -->
<!-- @mind:proposition — -->
<!-- @mind:escalation — -->
