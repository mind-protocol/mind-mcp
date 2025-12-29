# Data Models — Sync: Current State

```
STATUS: DRAFT
UPDATED: 2025-12-20
```

## MATURITY

STATUS: DRAFT

What's canonical (v1):
- The Pydantic models for nodes, links are defined in `runtime/models/`.
- Basic type enforcement and field validation are in place.

## CURRENT STATE

The `runtime/models/` module provides the core data structures for the game. All major node and link types are defined using Pydantic, ensuring type safety and basic data validation. This module acts as the authoritative source for the game's graph schema.

## RECENT CHANGES

### 2025-12-20: Pending external implementation references

- **What:** Replaced stub file paths with pending import notes in implementation docs.
- **Why:** Remove broken impl links until upstream code is imported.

### 2025-12-20: Node Helper Properties Verified (Repair 12)

- **What:** Verified `is_core_type`, `tick`, `should_embed`, `is_active`, `is_spoken`, and `can_surface` in `runtime/models/nodes.py` already have concrete implementations; no code changes required for issue #16.
- **Why:** Repair 12 (INCOMPLETE_IMPL-models-nodes) flagged these helpers as incomplete.
- **Impact:** No functional changes; logged verification to prevent repeat flags.

### 2025-12-20: Link Helper Accessors Verified (Repair 11)

- **What:** Verified `belief_intensity`, `is_present`, `has_item`, and `is_here` in `runtime/models/links.py` already have concrete implementations; no code changes required for issue #16.
- **Why:** Repair 11 (INCOMPLETE_IMPL-models-links) flagged these accessors as incomplete.
- **Impact:** No functional changes; logged verification to prevent repeat flags.

### 2025-12-20: Base Timestamp Comparators Verified

- **What:** Verified `GameTimestamp.__str__`, `__le__`, and `__gt__` in `runtime/models/base.py` are fully implemented; no code changes required for issue #16.
- **Why:** Repair 10 (INCOMPLETE_IMPL-models-base) flagged empty implementations that are already present.
- **Impact:** No functional changes; reconfirmed during repair `10-INCOMPLETE_IMPL-models-base`.

### 2025-12-20: Initial Mind Documentation Creation

- **What:** Created `PATTERNS_Models.md`, `BEHAVIORS_Models.md`, `ALGORITHM_Models.md`, `VALIDATION_Models.md`, `IMPLEMENTATION_Models.md`, `HEALTH_Models.md`, and `SYNC_Models.md` for the `runtime/models` module.
- **Why:** To align with the `mind` framework and provide comprehensive documentation for the data models.
- **Impact:** The `runtime/models` module is now documented with a complete `mind` documentation chain.

## IN PROGRESS

- Currently, no active code development is ongoing for the `runtime/models` module. The focus is on completing and refining the documentation chain.

## KNOWN ISSUES

- The `embeddable_text` methods across models (e.g., `Character`, `Place`, `Thing`, `Narrative`) in `nodes.py` do not fully align with the `detail > 20, fallback to name` logic specified in `PATTERNS_Embeddings.md`.
- Custom validation for mutually exclusive fields (e.g., `Narrative.source` vs. `Narrative.detail`) is not yet implemented.

## HANDOFF: FOR AGENTS

Use VIEW_Implement_Write_Or_Modify_Code for any changes to the data models or their validation logic. Ensure that any new models or field updates are reflected across the entire documentation chain. Prioritize addressing the `embeddable_text` inconsistency.

## HANDOFF: FOR HUMAN

The core data models are well-defined and documented. Key areas for review involve aligning `embeddable_text` logic with embedding patterns and considering custom validators for complex field relationships.

## TODO

<!-- @mind:todo Add `runtime/models` mapping to `modules.yaml` (already done in previous step). -->
<!-- @mind:todo Implement unit tests for all Pydantic models, covering validation, defaults, and properties. -->
<!-- @mind:todo Refactor the `embeddable_text` methods across models in `nodes.py` to be consistent with the `PATTERNS_Embeddings.md` rules (detail > 20, fallback to name). -->

## CONSCIOUSNESS TRACE

Confidence in the model definitions themselves is high, as Pydantic handles much of the core validation. The remaining work is primarily about ensuring consistency with related modules (embeddings) and enhancing validation for complex narrative-specific constraints.

## POINTERS

- `docs/mind/models/PATTERNS_Models.md` for the Pydantic design philosophy.
- `runtime/models/` for the Python implementation of the data models.

## Agent Observations

### Remarks
- Base timestamp helper methods are already implemented; repair was verification-only.
- Link helper accessors are already implemented; repair was verification-only.
- Node helper properties in `nodes.py` are already implemented; repair was verification-only.
- Node helper properties are already implemented; repair was verification-only.

### Suggestions
<!-- @mind:todo None. -->

### Propositions
- None.

## GAPS
- **What was completed:** Identified an `ESCALATION` marker in `docs/mind/models/HEALTH_Models.md` regarding acceptable latency for model instantiation.
- **What remains to be done:** The `ESCALATION` marker needs to be converted to a `DECISION` and the relevant documentation updated based on a human decision.
- **Why you couldn't finish:** No human decisions were provided in the task description to resolve the escalation.

## CHAIN

```
THIS:            SYNC_Models.md (you are here)
PATTERNS:        ./PATTERNS_Models.md
BEHAVIORS:       ./BEHAVIORS_Models.md
ALGORITHM:       ./ALGORITHM_Models.md
VALIDATION:      ./VALIDATION_Models.md
IMPLEMENTATION:  ./IMPLEMENTATION_Models.md
HEALTH:          ./HEALTH_Models.md
```
