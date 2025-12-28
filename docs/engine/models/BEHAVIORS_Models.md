# Data Models — Behaviors: Consistent Data Interactions

```
STATUS: DRAFT
CREATED: 2025-12-20
UPDATED: 2025-12-20
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Models.md
THIS:            BEHAVIORS_Models.md
ALGORITHM:       ./ALGORITHM_Models.md
VALIDATION:      ./VALIDATION_Models.md
IMPLEMENTATION:  ./IMPLEMENTATION_Models.md
HEALTH:          ./HEALTH_Models.md
SYNC:            ./SYNC_Models.md

IMPL:            mind/models/
```

---

## OVERVIEW

This document describes the observable behaviors of the data models within the `mind/models/` module. It focuses on how these Pydantic models behave when instantiated, validated, and converted, ensuring a consistent and predictable data contract across the game engine.

---

## BEHAVIORS

### B1: Strict Type Enforcement on Instantiation

**Description:** When a Pydantic model is instantiated, all fields are strictly coerced to their defined types. If a value cannot be coerced or is missing for a required field, a `ValidationError` is raised.

**Inputs:** Dictionary or keyword arguments matching the model's schema.

**Outputs:** A valid Pydantic model instance or a `ValidationError`.

**Edge Cases:**
- `None` for optional fields is allowed.
- `None` for required fields raises `ValidationError`.
- Incorrect types that cannot be coerced raise `ValidationError`.

**Anti-Behaviors:**
- Silent type coercion that hides data issues.
- Accepting invalid data without raising an error.

### B2: Default Values Are Applied Automatically

**Description:** For any field with a specified default value (e.g., `Field(default=...)` or `default_factory`), if the field is not provided during instantiation, the default value is automatically assigned.

**Inputs:** Partial dictionary or keyword arguments omitting fields with defaults.

**Outputs:** A model instance with default values correctly applied.

**Edge Cases:**
- `default_factory` is called every time a new instance is created, ensuring mutable defaults (like lists) are independent.

**Anti-Behaviors:**
- `None` being used as a default when a non-`None` default is intended.
- Mutable defaults being shared across instances if `default_factory` is not used.

### B3: Serialization to Dictionary (and JSON)

**Description:** Pydantic models can be reliably converted into a Python dictionary (and subsequently JSON) that mirrors the schema, with aliases (if defined) respected.

**Inputs:** A valid Pydantic model instance.

**Outputs:** A Python `dict` where keys are field names (or aliases) and values are the model's data.

**Edge Cases:**
- `exclude=True` fields are omitted from the serialized output.
- `by_alias=True` uses defined aliases for keys.

**Anti-Behaviors:**
- Inconsistent dictionary representation (e.g., mixing aliases and original field names).
- Failing to exclude sensitive or computed fields from serialization.

### B4: Custom Property Methods Reflect Derived State

**Description:** `@property` methods on models compute derived attributes (e.g., `is_present` on `CharacterPlace`). These properties reflect the current state based on other model fields.

**Inputs:** Internal model state.

**Outputs:** Computed value (e.g., boolean, float).

**Edge Cases:**
- Properties should be idempotent and not cause side effects.
- Computation should be lightweight.

**Anti-Behaviors:**
- Properties performing heavy computation without caching.
- Properties causing unexpected mutations to the model state.

## MARKERS

<!-- @mind:todo Should `Config.extra = 'forbid'` be used consistently across all models to prevent unknown fields? -->
<!-- @mind:todo How should custom serialization for complex types (e.g., `datetime` objects) be documented or enforced? -->
<!-- @mind:proposition Add an explicit behavior for handling nested Pydantic models within other models. -->
<!-- @mind:escalation Are there specific Pydantic features (e.g., discriminated unions, generics) that could simplify certain schema definitions? -->