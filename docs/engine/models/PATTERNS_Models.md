# Data Models — Patterns: Pydantic for Graph Schema Enforcement

```
STATUS: DRAFT
CREATED: 2025-12-20
UPDATED: 2025-12-20
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Models.md
THIS:            PATTERNS_Models.md
BEHAVIORS:       ./BEHAVIORS_Models.md
ALGORITHM:       ./ALGORITHM_Models.md
VALIDATION:      ./VALIDATION_Models.md
IMPLEMENTATION:  ./IMPLEMENTATION_Models.md
HEALTH:          ./HEALTH_Models.md
SYNC:            ./SYNC_Models.md

IMPL:            mind/models/
```

---

## THE PROBLEM

The Blood Ledger's core state is a graph database (FalkorDB), which is schema-flexible. This flexibility, while powerful, makes it easy to introduce data inconsistencies:
- Nodes missing required properties (e.g., a `Character` without a `name`).
- Properties having incorrect types (e.g., `Character.alive` as a string instead of a boolean).
- Relationships lacking necessary attributes (e.g., a `BELIEVES` link without `strength`).
- Evolution of the schema over time leading to silent data corruption or unexpected runtime errors.

Without strict enforcement, different parts of the application (e.g., world scraping, game engine, API, Narrator agents) might inadvertently write inconsistent data, leading to unpredictable behavior and hard-to-debug issues.

---

## THE PATTERN

**Schema-First, Code-Driven Pydantic Models for Graph Entities.**

Define the canonical structure and types for all graph nodes and links using Pydantic `BaseModel` classes. These models serve as the single source of truth for the data schema, providing:
- **Type enforcement:** Ensure data adheres to expected Python types.
- **Validation:** Define constraints (e.g., `ge=0.0, le=1.0` for probabilities).
- **Serialization/Deserialization:** Easily convert between Python objects and JSON/dict for graph interactions.
- **Documentation:** Pydantic models are self-documenting, making the schema clear to developers.

These models are used proactively when creating or updating graph entities, ensuring data integrity before it even reaches FalkorDB.

---

## PRINCIPLES

### Principle 1: Explicit Schema, Not Implicit

The schema for graph entities must be explicitly defined in code, not inferred from graph writes or assumed by downstream consumers.

**Why it matters:**
- Prevents "schema drift" where different parts of the system operate on subtly different understandings of the data.
- Forces early detection of data inconsistencies during development.
- Enables clear communication of data structure to new developers and AI agents.

### Principle 2: Pydantic as the Schema Language

Pydantic `BaseModel` is the chosen tool for defining graph entity schemas.

**Why it matters:**
- Leverages Python's type hinting system for robust and readable schema definitions.
- Provides built-in data validation and serialization/deserialization, reducing boilerplate.
- Integrates well with existing Python tooling and ecosystems.

### Principle 3: Source of Truth for Graph Entities

The Pydantic models in `mind/models/` are the authoritative source for the structure of all nodes and links stored in the graph.

**Why it matters:**
- Eliminates ambiguity about what constitutes a valid graph entity.
- Simplifies updates: changing a model definition automatically highlights affected areas in code.
- Facilitates automated testing and validation of graph data.

### Principle 4: "Ground Truth" vs. "Narrative Truth"

The models distinguish between "ground truth" (e.g., `CharacterPlace` for physical presence) and "narrative truth" (e.g., `CharacterNarrative` for beliefs).

**Why it matters:**
- Preserves the core narrative mechanic where player knowledge and beliefs are distinct from objective reality.
- Enables the system to track character ignorance, misinformation, and secrets.
- Allows for complex narrative scenarios where "truth" is contested.

---

## DATA

This pattern describes the structure and validation of the primary data entities:

- **Nodes:** `Character`, `Place`, `Thing`, `Narrative`, `Moment`.
- **Links:** `CharacterNarrative`, `NarrativeNarrative`, `CharacterPlace`, `CharacterThing`, `ThingPlace`, `PlacePlace`.
- **Enums:** Various enumerated types for consistent choices (e.g., `CharacterType`, `MomentStatus`).
- **Shared Sub-Models:** Reusable structures like `Skills`, `Personality`, `Atmosphere`, `GameTimestamp`.

All these data structures are defined as Pydantic `BaseModel` classes, leveraging Python type hints for clarity and strict validation rules (e.g., numeric bounds, default factories for mutable types).

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `pydantic` | Core library for defining models and validation. |
| `enum` | Python standard library for defining enums used in models. |
| `datetime` | Python standard library for timestamp fields. |
| `typing` | Python standard library for type hints. |

---

## INSPIRATIONS

- **Domain-Driven Design (DDD):** Emphasizes defining a ubiquitous language and ensuring the code reflects the domain model accurately.
- **GraphQL Schema Definition Language (SDL):** Focus on a strong, explicit schema as the contract for data interactions.
- **Pydantic's maintainers:** The library itself demonstrates robust data modeling practices.

---

## SCOPE

**In Scope:**
- Defining Pydantic models for `Character`, `Place`, `Thing`, `Narrative`, `Moment` nodes.
- Defining Pydantic models for `CharacterNarrative`, `NarrativeNarrative`, `CharacterPlace`, `CharacterThing`, `ThingPlace`, `PlacePlace` links.
- Defining common enums (e.g., `CharacterType`, `PlaceType`, `NarrativeType`, `MomentType`, `ModifierType`).
- Providing base models for shared complex types (e.g., `Skills`, `Personality`, `Atmosphere`).
- Ensuring basic data validation (types, ranges, defaults).

**Out of Scope:**
- Direct interaction with FalkorDB (handled by `GraphOps` and `GraphQueries`).
- Semantic search indexing or querying (handled by `EmbeddingService`).
- Runtime logic for how models interact (handled by `Orchestrator`, `World Runner`, `Physics`).
- Complex business logic that extends beyond data structure and basic validation.

---

## MARKERS

<!-- @mind:todo Consider adding custom Pydantic validators for cross-field dependencies (e.g., `Narrative.source` and `Narrative.detail` exclusivity). -->
<!-- @mind:todo Explore integrating Pydantic models with OpenAPI/JSON Schema generation for API documentation. -->
<!-- @mind:proposition Use Pydantic's `Config.allow_extra = 'forbid'` for stricter schema enforcement. -->
<!-- @mind:escalation
title: "Should all enums be defined centrally in base.py or co-located with their primary models?"
priority: 5
response:
  status: resolved
  choice: "Free text, except node_type"
  behavior: "Only node_type (actor|space|thing|narrative|moment) is an enum. All other types (ActorType, SpaceType, MomentType, etc.) become free text strings. Project-specific, not framework-constrained."
  notes: "2025-12-23: Aligns with base schema where type is free text. Decided by Nicolas."
-->