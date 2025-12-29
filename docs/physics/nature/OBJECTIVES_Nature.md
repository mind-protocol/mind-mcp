# Nature — Objectives

```
STATUS: CANONICAL
MODULE: physics/nature
```

---

## CHAIN

```
THIS:            OBJECTIVES_Nature.md (you are here)
PATTERNS:        ./PATTERNS_Nature.md
```

---

## PURPOSE

Convert semantic "nature" strings into physics floats that drive graph simulation.

**Universal vocabulary:** Same nature applies to both nodes AND links.

Agents write human-readable nature like `"suddenly proves, with admiration"`.
The system derives physics: `{permanence: 0.9, trust_disgust: 0.8, surprise_anticipation: 0.8}`.

The entity (node or link) interprets these floats in its context:
- **Link:** How the relationship behaves (decay, propagation, weight)
- **Node:** How the entity behaves (energy, decay, activation)

---

## OBJECTIVES

### O1: Semantic Expressiveness

**Priority: CRITICAL**

Agents express relationship nuance through controlled vocabulary.

| Requirement | Rationale |
|-------------|-----------|
| Rich verb taxonomy | Different relationships need different physics |
| Modifier composition | Intensity, certainty, emotion layered on verbs |
| Conflict detection | Contradictory modifiers flagged, not silently merged |

### O2: Physics Determinism

**Priority: CRITICAL**

Same nature string always produces same physics floats.

| Requirement | Rationale |
|-------------|-----------|
| No randomness | Reproducible simulation |
| Explicit defaults | Missing values have known defaults |
| Longest match first | Unambiguous verb detection |

### O3: Extensibility

**Priority: HIGH**

Vocabulary grows without code changes.

| Requirement | Rationale |
|-------------|-----------|
| YAML-driven definitions | Edit nature.yaml, not Python |
| Hot reload | `reload_nature()` updates without restart |
| Category organization | Verbs grouped by semantic domain |

### O4: Type Hints

**Priority: MEDIUM**

Verbs hint at valid node type pairs.

| Requirement | Rationale |
|-------------|-----------|
| type_a/type_b fields | `proves` hints thing→narrative |
| Advisory, not enforced | Agents can override |
| Enables validation | Tools can warn on mismatches |

---

## NON-OBJECTIVES

| Explicitly Out | Why |
|----------------|-----|
| Natural language parsing | Structured vocab only, not free text |
| Physics simulation | We produce floats, simulation is separate |
| Semantic inference | Exact match only, no "similar to" |
| Runtime enforcement | Type hints advisory, not blocked |

---

## SUCCESS METRICS

| Metric | Target |
|--------|--------|
| Verb coverage | 60+ verbs across all node type combinations |
| Parse success rate | 100% for valid nature strings |
| Conflict detection | All contradictory modifiers flagged |
| Load time | <10ms for nature.yaml |
