# Data Models — Validation: Pydantic Invariants and Properties

```
STATUS: DRAFT
CREATED: 2025-12-20
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Models.md
BEHAVIORS:       ./BEHAVIORS_Models.md
ALGORITHM:       ./ALGORITHM_Models.md
THIS:            VALIDATION_Models.md
IMPLEMENTATION:  ./IMPLEMENTATION_Models.md
HEALTH:          ./HEALTH_Models.md
SYNC:            ./SYNC_Models.md

IMPL:            mind/models/
```

---

## OVERVIEW

This document defines the invariants and properties that all Pydantic data models within the `runtime/models/` module must uphold. These validations ensure the structural integrity, type consistency, and logical correctness of the data before it is persisted in the graph or used by other engine components.

---

## INVARIANTS

These must ALWAYS be true for any instantiated model:

### V1: All Required Fields Are Present and Valid

```
For every model, all fields marked as required (i.e., no default value or `Optional`) must be present and conform to their defined type and constraints.
```

**Checked by:** Pydantic's automatic validation on model instantiation.

### V2: Enum Fields Use Valid Members

```
Any field defined as an `Enum` type (e.g., `CharacterType`, `MomentStatus`) must only accept values that are valid members of that enum.
```

**Checked by:** Pydantic's automatic validation for `Enum` types.

### V3: Numeric Fields Adhere to Bounds

```
Numeric fields with `ge` (greater than or equal) or `le` (less than or equal) constraints (e.g., `weight`, `energy` from 0.0 to 1.0) must respect these bounds.
```

**Checked by:** Pydantic's `Field` validation rules.

### V4: Immutable Defaults Are Truly Immutable

```
Default values for mutable types (e.g., `list`, `dict`) must be provided via `default_factory` to ensure each model instance gets its own independent copy.
```

**Checked by:** Manual code review; Pydantic does not enforce `default_factory` directly but warns against mutable defaults.

---

## PROPERTIES

These properties should hold true across various valid inputs:

### P1: Serialization is Reversible

```
FORALL model_instance:
    dict_representation = model_instance.dict()
    re_instantiated = Model.parse_obj(dict_representation)
    model_instance == re_instantiated
```

**Tested by:** `test_model_serialization_roundtrip` (pending)

### P2: Properties Reflect Current State

```
FORALL model_instance with derived properties (e.g., `is_present`):
    IF conditions for property are met:
        property_value IS TRUE
    ELSE:
        property_value IS FALSE
```

**Tested by:** `test_derived_properties_accuracy` (pending)

---

## ERROR CONDITIONS

### E1: `ValidationError` on Invalid Input

```
WHEN:    Attempt to instantiate a model with data that violates any required field, type, or constraint.
THEN:    A `pydantic.ValidationError` is raised.
SYMPTOM: Application crashes or logging indicates data validation failure.
```

**Tested by:** Unit tests specifically providing malformed data.

### E2: `ValueError` on Invalid Enum Member

```
WHEN:    Attempt to instantiate a model with a string value for an `Enum` field that does not correspond to a valid enum member.
THEN:    A `ValueError` is raised during type coercion.
SYMPTOM: Application crashes or logging indicates an invalid enum value.
```

**Tested by:** Unit tests with invalid enum strings.

---

## HEALTH COVERAGE

| Requirement | Test(s) | Status |
|-------------|---------|--------|
| V1: Required fields | Pydantic native | Automated |
| V2: Enum fields | Pydantic native | Automated |
| V3: Numeric bounds | Pydantic native | Automated |
| V4: Immutable defaults | `test_mutable_defaults` | Pending |
| P1: Serialization roundtrip | `test_serialization_roundtrip` | Pending |
| P2: Derived properties | `test_derived_properties_accuracy` | Pending |
| E1: `ValidationError` | `test_invalid_input_raises_error` | Pending |
| E2: Invalid Enum | `test_invalid_enum_raises_error` | Pending |

---

## VERIFICATION PROCEDURE

### Manual Checklist

```
[ ] Review all model definitions in `runtime/models/` for correct type hints, `Field` constraints, and enum usage.
[ ] Verify `default_factory` is used for all mutable default fields.
[ ] Inspect `@property` methods for correct derivation logic.
```

### Automated Tests (Python)

```bash
# Run all tests for data models
pytest tests/mind/models/ -v

# Run tests specifically for base models and enums
pytest tests/mind/models/test_base_models.py -v
```

---

## SYNC STATUS

This validation document ensures the declared schema invariants and properties are actively checked, either manually or via automated tests.

---

## MARKERS

<!-- @mind:todo Add explicit unit tests for `V4: Immutable Defaults Are Truly Immutable`. -->
<!-- @mind:todo Implement property-based tests for serialization roundtrip (P1) and derived properties (P2). -->
<!-- @mind:proposition Generate validation reports from Pydantic schema exports (e.g., JSON Schema) and compare against expectations. -->
<!-- @mind:escalation
title: "Should all models have an explicit __eq__ method for robust comparison in tests?"
priority: 5
response:
  status: resolved
  choice: "No"
  behavior: "Pydantic's default field-by-field comparison is sufficient. No custom __eq__ needed."
  notes: "2025-12-23: Decided by Nicolas."
-->
