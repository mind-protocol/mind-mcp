# Data Models — Implementation: Pydantic Code Architecture

```
STATUS: DRAFT
CREATED: 2025-12-20
UPDATED: 2025-12-20
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Models.md
BEHAVIORS:       ./BEHAVIORS_Models.md
ALGORITHM:       ./ALGORITHM_Models.md
VALIDATION:      ./VALIDATION_Models.md
THIS:            IMPLEMENTATION_Models.md
HEALTH:          ./HEALTH_Models.md
SYNC:            ./SYNC_Models.md

IMPL:            mind/models/
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

```
mind/models/__init__.py  # Module exports and high-level docs
mind/models/base.py      # Enums, shared sub-models (e.g., Skills, Atmosphere)
mind/models/nodes.py     # Character, Place, Thing, Narrative, Moment models
mind/models/links.py     # CharacterNarrative, PlacePlace, etc. models
```

### File Responsibilities

| File | Purpose | Key Functions/Classes | Lines | Status |
|------|---------|----------------------|-------|--------|
| `runtime/models/__init__.py` | Module aggregation | Exports all models | ~90 | OK |
| `runtime/models/base.py` | Core enums & shared types | `CharacterType`, `Modifier`, `GameTimestamp` | ~300 | OK |
| `runtime/models/nodes.py` | Graph node definitions | `Character`, `Place`, `Thing`, `Narrative`, `Moment` | ~300 | OK |
| `runtime/models/links.py` | Graph link definitions | `CharacterNarrative`, `PlacePlace` | ~200 | OK |

**Size Thresholds:**
- **OK** (<400 lines): Healthy size, easy to understand
- **WATCH** (400-700 lines): Getting large, consider extraction opportunities
- **SPLIT** (>700 lines): Too large, must split before adding more code

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Domain Model / Anemic Domain Model (with rich properties).

**Why this pattern:** The models primarily focus on data structure and validation (anemic), but also include rich `@property` methods and `embeddable_text` functions that provide some behavior. This balances strict data representation with domain-specific utility.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Pydantic `BaseModel` | All models | Schema definition, validation, serialization |
| Python `enum Enum` | All `*Type` fields | Type-safe enumeration of valid choices |
| `@property` decorator | `CharacterPlace is_present` | Derived attributes for clear state querying |
| `default_factory` | `List` fields, nested models | Ensure mutable defaults are independent per instance |

### Anti-Patterns to Avoid

- **Logic Sprawl**: Avoid adding complex business logic directly into models; defer to services (e.g., `GraphOps`, `Orchestrator`).
- **Redundant Validation**: Do not re-implement Pydantic's native validation checks with custom `@validator` functions unless truly necessary.
- **Circular Dependencies**: Structure files to avoid `A imports B` and `B imports A` loops, especially between `runtime/models/nodes.py`, `runtime/models/links.py`, `runtime/models/base.py`.

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Data Models | Schema definition, basic validation, derived properties | Graph operations, API endpoints, game logic | Pydantic instances (dict, JSON) |

---

## SCHEMA

The primary schema is the sum of all Pydantic models in this module. Refer to individual model definitions in `runtime/models/nodes.py`, `runtime/models/links.py`, and `runtime/models/base.py` for full details. High-level schema contracts for specific domains (e.g., Moment Graph) are documented in `docs/schema/`.

---

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| Model instantiation | `runtime/models/nodes.py:Character(...)` | World scraping, API, Orchestrator |
| `GameTimestamp.parse()` | `runtime/models/base.py:284` | Parsing game event strings |
| `embeddable_text()` | `runtime/models/nodes.py:100` | `EmbeddingService` for vectorization |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

### Data Ingestion: Raw Input → Validated Model

This flow describes how raw data (from files, API, etc.) is transformed into validated Python objects.

```yaml
flow:
  name: model_ingestion
  purpose: Ensure all data conforms to the defined schema and types.
  scope: Raw Data -> Pydantic Validation -> Model Instance
  steps:
    - id: step_1_load_raw
      description: Receive raw data (dict, JSON, ORM object).
      file: N/A
      function: N/A
      input: raw_data
      output: dict/object
      trigger: API call, file read, ORM query
      side_effects: none
    - id: step_2_instantiate_model
      description: Pass raw data to Pydantic model constructor.
      file: mind/models/nodes.py (e.g., Character)
      function: __init__ / parse_obj
      input: raw_data
      output: Pydantic model instance
      trigger: code calling model constructor
      side_effects: `ValidationError` on failure
  docking_points:
    guidance:
      include_when: data enters or leaves the system
    available:
      - id: raw_data_input
        type: custom
        direction: input
        file: mind/models/nodes.py (e.g., Character)
        function: __init__
        trigger: various (API, scraper)
        payload: dict
        async_hook: optional
        needs: none
        notes: Entry point for unstructured data
      - id: validated_model_output
        type: custom
        direction: output
        file: mind/models/nodes.py (e.g., Character)
        function: __init__
        trigger: successful instantiation
        payload: Pydantic model instance
        async_hook: not_applicable
        needs: none
        notes: Guaranteed schema compliance
    health_recommended:
      - dock_id: validated_model_output
        reason: Critical for ensuring downstream systems receive valid data.
```

---

## LOGIC CHAINS

### LC1: `GameTimestamp` Comparison

**Purpose:** Allow chronological ordering and comparison of game timestamps.

```
GameTimestamp instance (`ts1`)
  → `ts1 < ts2` (or `<=`, `>`, `>=`)
    → mind/models/base.py:GameTimestamp.__lt__ (or __le__, __gt__, __ge__)
      → Compares `day`, then `TimeOfDay` enum order
        → Boolean result
```

**Data transformation:**
- Input: Two `GameTimestamp` instances.
- Output: Boolean indicating the chronological relationship.

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
mind/models/__init__.py
    ├── imports → .base
    ├── imports → .nodes
    └── imports → .links

mind/models/nodes.py
    └── imports → .base (for enums and sub-models)

mind/models/links.py
    └── imports → .base (for enums)
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `pydantic` | Core data modeling | All files in `runtime/models/` |
| `enum` | Enumerated types | `runtime/models/base.py` |
| `datetime` | Date/time fields | `runtime/models/base.py` |
| `typing` | Type hints | All files in `runtime/models/` |

---

## STATE MANAGEMENT

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| Model Data | Pydantic model instance | Per-instance | Matches object lifecycle |

### State Transitions

- Models are generally immutable once instantiated (Pydantic's default behavior).
- Updates typically involve creating a new model instance with modified data.

---

## RUNTIME BEHAVIOR

### Model Instantiation

When data is loaded from various sources (e.g., API requests, database queries, YAML files), it is passed to the Pydantic model constructors. This process immediately triggers validation and type coercion. Invalid data will raise a `ValidationError` early in the data pipeline, preventing corrupted state from propagating.

### Property Access

Derived properties are computed dynamically upon access. These computations are typically lightweight and do not involve side effects, ensuring efficient querying of model state.

### Serialization

Models are frequently serialized to dictionaries or JSON (e.g., for API responses, database storage). This process respects `Field` configurations (like `exclude=True`) to ensure only relevant data is exposed.

---

## CONCURRENCY MODEL

| Component | Model | Notes |
|-----------|-------|-------|
| Model Validation | Synchronous | Pydantic validation is typically blocking |

**Considerations:**
- `default_factory` for mutable defaults ensures thread-safe independent instances.
- No shared mutable state within the module itself, minimizing concurrency risks at the model layer.

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `Config allow_population_by_field_name` | `Moment` model in `runtime/models/nodes.py` | `True` | Allows `tick` to be set via `tick_created` alias. |
| `Field(ge=..., le=...)` | Various fields | N/A | Numeric range constraints. |
| `Field(default_factory=list)` | `List` fields | `[]` | Ensures unique mutable defaults. |

---

## BIDIRECTIONAL LINKS

### Code → Docs

| File | Line | Reference |
|------|------|-----------|
| `runtime/models/__init__.py` | 5 | `docs/schema/models/PATTERNS_Pydantic_Schema_Models.md` |
| `runtime/models/base.py` | 5 | `docs/mind/models/VALIDATION_Models.md` |
| `runtime/models/nodes.py` | 5 | `docs/mind/models/PATTERNS_Models.md` |

### Docs → Code

| Doc Section | Implemented In |
|-------------|----------------|
| Character model | `runtime/models/nodes.py:Character` |
| Place model | `runtime/models/nodes.py:Place` |
| `GameTimestamp` operations | `runtime/models/base.py:GameTimestamp` |

---

## MARKERS

### Missing Implementation

<!-- @mind:todo Custom validation for mutually exclusive fields (e.g., `Narrative source` vs. `Narrative detail`). -->
<!-- @mind:todo More robust `__eq__` and `__hash__` methods for all models to enable reliable set/dict usage. -->

### Ideas

<!-- @mind:proposition Generate JSON Schema for all models and use it for API documentation and frontend validation. -->
<!-- @mind:proposition Implement `Config.extra = 'forbid'` to prevent accidental inclusion of unknown fields. -->

### Questions

<!-- @mind:todo
title: "Implement schema migration system"
priority: medium
decision: "2025-12-23: Option B chosen — migration scripts. On schema change, ALL graphs are migrated immediately. Deprecated fields removed, renamed fields renamed. No backwards compat cruft. Implement: 1) version field in graph metadata, 2) migration registry, 3) CLI command `mind migrate`."
-->
<!-- @mind:escalation
title: "Should Moment's tick property (alias for tick_created) be removed?"
priority: 5
response:
  status: resolved
  choice: "Yes, remove"
  task_description: "Migration script at mind/migrations/migrate_tick_to_tick_created.py"
  behavior: "All code uses tick_created directly. No backwards compat alias."
  notes: "2025-12-23: Implemented same session."
-->
