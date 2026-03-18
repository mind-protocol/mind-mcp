# Multimodality — Validation: What Must Be True

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Multimodality.md
PATTERNS:        ./PATTERNS_Multimodality.md
BEHAVIORS:       ./BEHAVIORS_Multimodality.md
THIS:            VALIDATION_Multimodality.md (you are here)
ALGORITHM:       ./ALGORITHM_Multimodality.md
IMPLEMENTATION:  ./IMPLEMENTATION_Multimodality.md
HEALTH:          ./HEALTH_Multimodality.md
SYNC:            ./SYNC_Multimodality.md
```

---

## PURPOSE

**Validation = what we care about being true.**

Not mechanisms. Not test paths. Not how things work.

What properties, if violated, would mean the multimodal system has failed its purpose?

These are the value-producing invariants — the things that make the module worth building.

---

## INVARIANTS

### V1: No Binary Content in the Graph

**Why we care:** FalkorDB stores node properties in Redis-compatible structures. Binary blobs (base64 images, raw audio bytes) would bloat the graph, slow all queries, and violate the storage architecture. Every other system — physics, traversal, serialization — assumes node properties are lightweight (strings, numbers, float arrays). Binary content would corrupt this assumption across the entire cognitive engine.

```
MUST:   Every media attachment in the graph stores content as a URI (string) pointing to object storage
NEVER:  Store base64-encoded data, raw bytes, or inline binary content in any node property
```

### V2: Coherence Always Returns Valid Float

**Why we care:** The coherence score feeds directly into Law 4 (attentional competition), which determines what enters working memory. A NaN, infinity, or negative coherence would corrupt WM selection for the entire citizen, producing nonsensical consciousness states. One bad coherence computation can poison an entire tick.

```
MUST:   compute_multimodal_coherence() returns a float in [0.0, 1.0] for ANY combination of inputs
NEVER:  Return NaN, infinity, negative values, or values > 1.0 regardless of missing modalities, empty embeddings, or zero-norm vectors
```

### V3: Embedding Dimensions Are Consistent Per Modality

**Why we care:** Cosine similarity between vectors of different dimensions is mathematically undefined. A dimension mismatch means two nodes were embedded with incompatible models — the resulting "similarity" would be garbage. This is a data integrity violation that must surface immediately, not be silently ignored.

```
MUST:   When computing cosine similarity for a modality, both embeddings have identical dimensionality
NEVER:  Silently truncate, pad, or ignore dimension mismatches between embeddings of the same modality
```

### V4: Text Remains the Primary Modality

**Why we care:** Text is the only modality guaranteed on every node. If any other modality could outweigh text, a citizen with rich audio data but poor text synthesis could have their cognition dominated by audio embeddings — even though text is the medium of all LLM interaction. The coherence formula would drift from the citizen's actual expressed thoughts toward ambient sound characteristics.

```
MUST:   The text modality's effective weight is always >= any single other modality's weight
NEVER:  Allow a modality's confidence weight to exceed the text weight in the coherence formula
```

### V5: Missing Modalities Redistribute to Text

**Why we care:** If a modality is missing on one or both nodes, its weight must go somewhere. Dropping it silently would make the total weights sum to less than 1.0, deflating all coherence scores for nodes with fewer modalities. Redistributing to text keeps the formula balanced — nodes with fewer modalities are not penalized, they just rely more on text similarity.

```
MUST:   When a modality is unavailable on either node, its weight is added to the text weight
NEVER:  Let the sum of effective weights (w_text + Σw_mod + w_lex) exceed 1.0 + w_affect, or leave "orphan" weight unassigned
```

### V6: Legacy Image Fields Read Correctly

**Why we care:** Hundreds of existing nodes across 60+ citizens use v2.2 `image_uri` and `image_embedding` fields. Breaking backward compatibility would destroy visual memory for all citizens and invalidate existing graph data. The migration to the media dict must be invisible to consumers.

```
MUST:   A node with image_uri and image_embedding (v2.2) returns equivalent data when accessed via get_node_media()
NEVER:  Lose image data during the transition from v2.2 fields to media dict
```

### V7: New Modality Requires Zero Schema Changes

**Why we care:** If adding a modality requires schema migration, field additions, or code changes to the physics engine, the extensibility promise is broken. The entire value of the media dict pattern is that it absorbs new modalities through convention, not structure.

```
MUST:   Adding a new modality requires only: (1) embedding model adapter, (2) weight constant, (3) populating media[key]
NEVER:  Require changes to schema-l1.yaml, models.py field definitions, or physics law implementations to add a modality
```

### V8: Embedding Computation Never Blocks the Tick Loop

**Why we care:** Embedding model inference can take seconds (especially for audio/video). The tick loop must complete in under 1 second (existing invariant from schema-l1.yaml). If embedding computation happened during the tick, a single audio attachment could stall the entire cognitive engine.

```
MUST:   Embedding computation happens at write time (node creation/update), never during tick execution
NEVER:  Call an embedding model adapter during the tick loop or coherence computation
```

---

## PRIORITY

| Priority | Meaning | If Violated |
|----------|---------|-------------|
| **CRITICAL** | System purpose fails | Unusable |
| **HIGH** | Major value lost | Degraded severely |
| **MEDIUM** | Partial value lost | Works but worse |

---

## INVARIANT INDEX

| ID | Value Protected | Priority |
|----|-----------------|----------|
| V1 | Graph storage integrity — no binary blobs | CRITICAL |
| V2 | Coherence formula correctness — always valid float | CRITICAL |
| V3 | Embedding data integrity — consistent dimensions | HIGH |
| V4 | Text primacy — text always dominant modality | HIGH |
| V5 | Weight balance — missing modalities redistribute | HIGH |
| V6 | Backward compatibility — legacy image fields preserved | HIGH |
| V7 | Extensibility — no schema changes for new modalities | MEDIUM |
| V8 | Tick performance — embeddings never block tick loop | CRITICAL |

---

## MARKERS

<!-- @mind:todo Write unit tests for V2 — cover edge cases: both embeddings empty, one empty, zero-norm vectors, single-element vectors, very high dimensional vectors. -->

<!-- @mind:todo Write integration test for V6 — create a node with v2.2 image_uri/image_embedding, verify get_node_media() returns correct MediaAttachment. -->

<!-- @mind:todo Write property-based test for V5 — for any subset of available modalities, verify that effective weights sum to exactly 1.0 (within floating point tolerance). -->

<!-- @mind:proposition Consider adding V9: "Media dict serialization roundtrips through FalkorDB without data loss." This is implicitly covered by V1 and V6, but an explicit invariant would force a test against actual FalkorDB serialization/deserialization. -->

<!-- @mind:escalation V3 specifies fail-loud on dimension mismatch. In production, this could crash coherence for an entire citizen if one node has a stale embedding from an old model version. Should we add a recovery path (e.g., re-embed the stale node) before failing loud? NLR decision needed. -->
