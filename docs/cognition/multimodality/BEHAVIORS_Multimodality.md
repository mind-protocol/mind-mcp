# Multimodality — Behaviors: Observable Effects of Multimodal Attachments

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Multimodality.md
THIS:            BEHAVIORS_Multimodality.md (you are here)
PATTERNS:        ./PATTERNS_Multimodality.md
ALGORITHM:       ./ALGORITHM_Multimodality.md
VALIDATION:      ./VALIDATION_Multimodality.md
HEALTH:          ./HEALTH_Multimodality.md
IMPLEMENTATION:  ./IMPLEMENTATION_Multimodality.md
SYNC:            ./SYNC_Multimodality.md

IMPL:            runtime/cognition/multimodal.py (to be created)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS

### B1: Media Attachment Stored on Node

**Why:** Citizens experience the world through multiple senses. A voice memo, a photograph, a 3D scan — each must be persistable on the node that represents that experience. Without this, non-text experiences are second-class citizens in the cognitive graph.

```
GIVEN:  A node exists in the citizen's graph
WHEN:   A media attachment is added with modality key, URI, and optional embedding
THEN:   The node's media dict contains the attachment under the modality key
AND:    The URI points to object storage (never inline binary)
AND:    If an embedding was provided, it is stored as a float array
```

### B2: Multimodal Coherence Computed

**Why:** The coherence formula (Law 8) determines how well a stimulus fits the current working memory context. Without multimodal coherence, a node with a matching voice recording contributes nothing beyond its text — the physics is blind to the audio similarity.

```
GIVEN:  Two nodes each have media attachments with embeddings for overlapping modalities
WHEN:   Law 8 computes coherence between them (or between a stimulus and WM context)
THEN:   Each shared modality contributes w_mod * cosine(embedding_a, embedding_b) to Coh
AND:    The total coherence includes text, lexical, affect, AND all available modality terms
```

### B3: Missing Modality Gracefully Skipped

**Why:** Most nodes will not have all modalities. A text-only memory has no image, no audio. The coherence formula must handle heterogeneous nodes without crashing or producing NaN.

```
GIVEN:  Node A has media.image and media.voice embeddings
        Node B has media.image embedding only (no voice)
WHEN:   Coherence is computed between A and B
THEN:   The image modality contributes its weighted term
AND:    The voice modality term is skipped (not zero — skipped entirely)
AND:    The skipped weight is redistributed proportionally to text
AND:    The result is a valid float in [0, 1]
```

### B4: Legacy Image Fields Read via Shim

**Why:** Hundreds of existing nodes use `image_uri` and `image_embedding` (v2.2 fields). Breaking these would destroy visual memory for all existing citizens. The migration must be progressive.

```
GIVEN:  A node has image_uri and image_embedding set (v2.2 format) but no media dict
WHEN:   The multimodal system reads the node's media
THEN:   It returns a media dict with media.image populated from the legacy fields
AND:    No data is lost
AND:    No write is triggered (read-only shim)
```

### B5: New Modality Added Without Schema Change

**Why:** The entire point of the media dict pattern is extensibility. If adding "tactile" requires a migration, the pattern has failed.

```
GIVEN:  The system supports text, image, and audio modalities
WHEN:   A developer wants to add "tactile" modality support
THEN:   They implement an embedding model adapter for tactile data
AND:    They register a confidence weight (e.g., w_tactile = 0.05) in constants
AND:    They populate media.tactile on relevant nodes
AND:    The coherence formula automatically includes the tactile term
AND:    No schema migration is needed
AND:    No changes to models.py, graph schema, or physics laws
```

### B6: Embedding Dispatch Routes to Correct Model

**Why:** Each modality requires a different embedding model (CLIP for images, CLAP for audio, etc.). The dispatch must be automatic — callers should not need to know which model handles which modality.

```
GIVEN:  A media attachment with a URI and a known modality key
WHEN:   Embedding is requested for that attachment
THEN:   The dispatcher routes to the correct model adapter for that modality
AND:    The adapter returns an embedding vector
AND:    The vector is stored in the attachment's embedding field
```

---

## OBJECTIVES SERVED

| Behavior ID | Objective | Why It Matters |
|-------------|-----------|----------------|
| B1 | Extensible media attachment (O1) | The media dict is the extensible container |
| B2 | Multimodal embeddings in physics (O2) | Coherence formula uses modality embeddings |
| B3 | Graceful degradation (O4) | Missing modalities never crash the system |
| B4 | Backward compatibility (O5) | Existing image data continues to work |
| B5 | Extensible without schema change (O1) | Convention-based extension, no migration |
| B6 | Multimodal embeddings in physics (O2) | Correct model produces correct embeddings |

---

## INPUTS / OUTPUTS

### Primary Function: `compute_multimodal_coherence()`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `stimulus_embedding` | `list[float]` | Text embedding of the stimulus |
| `context_vector` | `list[float]` | Mean text embedding of current WM |
| `stimulus_media` | `dict[str, MediaAttachment]` | Media attachments on the stimulus node |
| `context_media` | `dict[str, MediaAttachment]` | Aggregated media embeddings of WM context |
| `stimulus_names` | `str` | Stimulus text for lexical matching |
| `wm_names` | `list[str]` | WM node names for lexical matching |
| `stimulus_valence` | `float` | Valence of stimulus |
| `wm_mean_valence` | `float` | Mean valence of WM |
| `modality_weights` | `dict[str, float]` | Confidence weight per modality |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| `coherence` | `float` | Coherence score in [0, 1], incorporating all available modalities |

**Side Effects:**

- None. Pure computation. No state mutation.

### Secondary Function: `get_node_media()`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `node` | `Node` | The node to extract media from |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| `media` | `dict[str, MediaAttachment]` | Media dict, with legacy shim applied if needed |

**Side Effects:**

- None. Read-only. Legacy fields are read but never written.

---

## EDGE CASES

### E1: Both Nodes Have Zero Shared Modalities Beyond Text

```
GIVEN:  Node A has media.voice only, Node B has media.geometry only
THEN:   Only text coherence and lexical match contribute
AND:    All modality weight redistributes to text
AND:    Coherence still returns a valid score
```

### E2: Media Dict Exists But All Embeddings Are Empty

```
GIVEN:  A node has media.image with a URI but embedding = []
THEN:   The image modality is treated as absent (no embedding = no physics participation)
AND:    The URI is preserved (the content exists, just not embedded yet)
```

### E3: Embedding Dimensionality Mismatch

```
GIVEN:  Node A has media.voice.embedding of 512D (CLAP)
        Node B has media.voice.embedding of 768D (different CLAP version)
THEN:   Coherence computation for that modality raises an error (fail loud)
AND:    The error is logged with both dimensions and both node IDs
```

### E4: Legacy Node With image_uri But No media Dict

```
GIVEN:  A v2.2 node has image_uri = "s3://..." and image_embedding = [...]
        No media dict exists
THEN:   get_node_media() returns {"image": MediaAttachment(uri=..., embedding=..., meta={})}
AND:    The original image_uri and image_embedding fields are unchanged
```

---

## ANTI-BEHAVIORS

### A1: Binary Content Stored in Graph

```
GIVEN:   A caller attempts to attach media to a node
WHEN:    The attachment contains base64 data or raw bytes instead of a URI
MUST NOT: Store the binary content in the graph
INSTEAD:  Raise a validation error with message indicating URI is required
```

### A2: Coherence Returns NaN on Missing Modality

```
GIVEN:   One or both nodes lack a modality present in the weight registry
WHEN:    Coherence is computed
MUST NOT: Return NaN, infinity, or a negative number
INSTEAD:  Skip the missing modality, redistribute its weight to text, return valid float
```

### A3: Schema Migration Required for New Modality

```
GIVEN:   A developer wants to add support for a new modality
WHEN:    They follow the convention (model adapter + weight + populate media dict)
MUST NOT: Require changes to schema-l1.yaml, models.py Node fields, or FalkorDB schema
INSTEAD:  The media dict absorbs the new modality via its key-value structure
```

### A4: Modality Weight Exceeds Text Weight

```
GIVEN:   A modality has a very mature embedding model
WHEN:    Its confidence weight is being set
MUST NOT: Set any single modality weight higher than the text weight
INSTEAD:  Text always has the highest individual weight — other modalities are bonuses
```

---

## MARKERS

<!-- @mind:todo Clarify behavior when the same modality key is attached twice (overwrite or error?). Current assumption: overwrite with latest. -->

<!-- @mind:proposition Consider a B7 behavior: "Media Attachment Triggers Embedding Job" — when a URI is attached without an embedding, automatically queue an embedding computation. This could be synchronous (block until embedded) or async (embed in background, physics participation deferred). -->

<!-- @mind:escalation E3 (dimensionality mismatch) currently specifies fail-loud. Should we instead gracefully skip the modality and log a warning? Fail-loud is safer but could be disruptive if model versions drift. NLR decision needed. -->
