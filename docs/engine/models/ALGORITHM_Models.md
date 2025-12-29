# Data Models — Algorithm: Pydantic Data Flow and Validation

```
STATUS: DRAFT
CREATED: 2025-12-20
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Models.md
BEHAVIORS:       ./BEHAVIORS_Models.md
THIS:            ALGORITHM_Models.md
VALIDATION:      ./VALIDATION_Models.md
IMPLEMENTATION:  ./IMPLEMENTATION_Models.md
HEALTH:          ./HEALTH_Models.md
SYNC:            ./SYNC_Models.md

IMPL:            mind/models/
```

---

## OVERVIEW

This document describes the algorithmic aspects of the `runtime/models/` module, focusing on how Pydantic processes data during instantiation, validation, and property access. It outlines the sequence of operations that ensure data integrity and type consistency.

---

## DATA STRUCTURES

### Pydantic `BaseModel`

- The fundamental class for all data models, providing automatic data parsing, validation, and serialization.

### Pydantic `Field`

- Used to define model fields with additional validation rules (e.g., `ge`, `le`), default values, and metadata (`description`).

### Python Enums (`enum.Enum`)

- Used for predefined sets of string values (e.g., `CharacterType`, `MomentStatus`), ensuring type safety and valid choices.

---

## ALGORITHM: model_instantiate_and_validate

### Step 1: Input Data Ingestion

**Purpose:** Accept raw input (e.g., dictionary, keyword arguments) for model instantiation.

**Logic:** Pydantic's `__init__` method receives data. For `from_orm`/`parse_obj`, it attempts to read from ORM objects or dictionaries.

**Key Decision:** The choice of input method (`__init__`, `parse_obj`, `parse_raw`, `from_orm`) depends on the source format and validation strictness required.

### Step 2: Field Coercion and Type Conversion

**Purpose:** Transform input data into the defined field types.

**Logic:** For each field, Pydantic attempts to coerce the input value to the specified type (e.g., string to `int`, dict to nested `BaseModel`, string to `Enum` member).

**Key Decision:** Pydantic's default coercion rules are generally sufficient; explicit `root_validator` or `validator` functions are used for complex custom conversions.

### Step 3: Field Validation

**Purpose:** Apply field-specific constraints (e.g., `ge`, `le`, `max_length`, regex) and custom validators.

**Logic:** Pydantic checks each field against its `Field` constraints. If `@validator` or `@root_validator` methods are present, they are executed.

**Key Decision:** Validation logic is kept within the model definition, not scattered across business logic, ensuring a single source of truth for data rules.

### Step 4: Default Value Assignment

**Purpose:** Populate fields that were not provided in the input data but have default values.

**Logic:** If a field is missing and has a `default` or `default_factory`, Pydantic assigns it.

**Key Decision:** `default_factory` is preferred for mutable defaults (lists, dicts) to prevent unexpected shared state.

### Step 5: Model Finalization

**Purpose:** Create an immutable (by default) model instance with validated data.

**Logic:** A new instance of the `BaseModel` is returned. If any step failed, a `ValidationError` is raised instead.

**Key Decision:** Model instances are typically immutable after creation, promoting functional programming patterns where state changes are explicit re-creations.

---

## KEY DECISIONS

### D1: Use Pydantic's Default Validation Order

**Decision:** Rely on Pydantic's inherent order of validation (type coercion, then field validators, then model validators).

**Why:** Minimizes custom logic, improves readability, and leverages the library's battle-tested stability.

### D2: Property Methods for Derived Attributes

**Decision:** Use `@property` decorators for calculated fields that do not store state directly (e.g., `is_present` on `CharacterPlace`).

**Why:** Clearly separates stored data from computed values, enhances readability, and avoids redundant computation by allowing caching (if `functools.cached_property` is used).

---

## DATA FLOW

```
Raw Input (dict/kwargs)
    ↓
Pydantic __init__ / parse_obj
    ↓
Field Coercion
    ↓
Field Validation (min/max, regex)
    ↓
Custom Validators (@validator, @root_validator)
    ↓
Default Assignment
    ↓
Validated Model Instance
```

---

## COMPLEXITY

**Time Complexity:** O(N) where N is the number of fields in the model and its nested models. Each field undergoes a series of constant-time checks (type coercion, validation rules).

**Space Complexity:** O(M) where M is the size of the validated data. Pydantic models typically store a copy of the input data internally.

**Bottlenecks:**
- Deeply nested models can increase instantiation time.
- Complex regex or computationally intensive custom validators can slow down validation.

---

## HELPER FUNCTIONS

- **`_node_to_text()` (from `runtime/infrastructure/embeddings/service.py`)**: While not in `runtime/models` itself, this helper demonstrates how model data is extracted and transformed for external services. It reads model fields to create a composite string, a common pattern for downstream consumption of model data.

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| `GraphOps` (creation) | `model.dict()` / `model.json()` | Graph properties |
| `GraphQueries` (retrieval) | `Model.parse_obj(dict_from_graph)` | Validated model instance |
| `EmbeddingService` | `model.embeddable_text()` | Text for vectorization |
| `World Scraper` | `Model(...)` | Validated data before injection |

---

## MARKERS

<!-- @mind:todo Formalize documentation for custom validators if they become more complex. -->
<!-- @mind:todo Explore Pydantic V2's new features (e.g., `model_validator`) to optimize validation flows. -->
<!-- @mind:proposition Add a section on performance tuning for large-scale model instantiation. -->
<!-- @mind:escalation
title: "Should all derived properties be explicitly documented in a separate behaviors file or kept within the algorithm doc?"
priority: 5
response:
  status: resolved
  choice: "N/A - removed dead code"
  action: "Deleted unused @property methods from link models (belief_intensity, link_type, is_present, has_item, is_here)"
  notes: "2025-12-23: Properties were never used. Queries use raw floats directly in Cypher."
-->
