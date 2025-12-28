# Data Models — Objectives

```
STATUS: DRAFT
VERSION: v0.1
CREATED: 2025-12-26
```

---

## CHAIN

```
THIS:           OBJECTIVES_Models.md (you are here)
PATTERNS:       ./PATTERNS_Models.md
BEHAVIORS:      ./BEHAVIORS_Models.md
ALGORITHM:      ./ALGORITHM_Models.md
VALIDATION:     ./VALIDATION_Models.md
IMPLEMENTATION: ./IMPLEMENTATION_Models.md
HEALTH:         ./HEALTH_Models.md
SYNC:           ./SYNC_Models.md
```

---

## PURPOSE

Define what the data models module optimizes for, ranked by priority. These objectives guide all design tradeoffs.

---

## OBJECTIVES

### O1: Type Safety at Write Time (Critical)

**What we optimize:** Invalid data is rejected before it reaches the graph.

**Why it matters:** FalkorDB is schema-flexible, which means it will happily store malformed data. Pydantic validation catches type errors, missing fields, and constraint violations at the Python layer, before persistence.

**Tradeoffs accepted:**
- Validation adds CPU overhead on writes
- Stricter than database requires
- Some data transformations forced at write time

**Measure:** Zero type errors in production graph data.

---

### O2: Single Source of Truth for Schema (Critical)

**What we optimize:** Pydantic models in mind/models/ define what valid data looks like.

**Why it matters:** Without a canonical schema definition, different parts of the system will assume different structures. The models are the contract that all code must honor.

**Tradeoffs accepted:**
- Schema changes require model updates
- No "ad hoc" fields outside the model
- Migration complexity for schema evolution

**Measure:** All graph read/write operations use model classes.

---

### O3: Ground Truth vs Narrative Truth Distinction (Critical)

**What we optimize:** Clear separation between objective facts and character beliefs.

**Why it matters:** The core narrative mechanic depends on characters having incomplete or wrong information. CharacterPlace (physical location) vs CharacterNarrative (beliefs about location) must be structurally distinct.

**Tradeoffs accepted:**
- More link types than a simpler model
- Queries must specify which truth they want
- Some redundancy in representation

**Measure:** No confusion between ground truth and beliefs in code.

---

### O4: Self-Documenting Schema (Important)

**What we optimize:** Model definitions are readable by developers and AI agents.

**Why it matters:** Pydantic models with type hints and docstrings serve as living documentation. New contributors understand the schema by reading the code.

**Tradeoffs accepted:**
- Verbose model definitions
- Explicit over implicit

**Measure:** New developer can understand schema from models alone.

---

### O5: Validation Constraints Are Explicit (Important)

**What we optimize:** Numeric bounds, enum values, and field constraints are in the model.

**Why it matters:** If validation lives outside models (in write functions, in queries), constraints scatter and diverge. Models should reject invalid data, not downstream code.

**Tradeoffs accepted:**
- Some Pydantic validator complexity
- Stricter than minimum viable

**Measure:** All field constraints defined in model classes.

---

### O6: Serialization Compatibility (Nice to have)

**What we optimize:** Models serialize cleanly to JSON/dict for graph operations.

**Why it matters:** Graph operations often work with dicts. Models that serialize/deserialize cleanly reduce friction in the read/write path.

**Tradeoffs accepted:**
- Some Pydantic config tweaks
- datetime/enum handling complexity

**Measure:** model.model_dump() → write to graph → read → Model(**data) roundtrips cleanly.

---

## OBJECTIVE CONFLICTS

| Conflict | Resolution |
|----------|------------|
| O1 vs write performance | Validation cost is acceptable for data integrity |
| O2 vs flexibility | Strict schema, evolve through migrations |
| O5 vs simplicity | Explicit constraints prevent subtle bugs |

---

## NON-OBJECTIVES

Things we explicitly do NOT optimize for:

- **Graph operations** — That belongs to GraphOps/GraphQueries
- **Semantic search** — That belongs to EmbeddingService
- **Business logic** — That belongs to Physics, Orchestrator, World Runner
- **API serialization** — FastAPI handles that layer

---

## VERIFICATION

- [ ] All objectives have measures
- [ ] Conflicts documented with resolutions
- [ ] Non-objectives make boundaries clear
