# Multimodality — Algorithm: Coherence Extension, Embedding Dispatch, and Fallback Logic

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Multimodality.md
BEHAVIORS:       ./BEHAVIORS_Multimodality.md
PATTERNS:        ./PATTERNS_Multimodality.md
THIS:            ALGORITHM_Multimodality.md (you are here)
VALIDATION:      ./VALIDATION_Multimodality.md
HEALTH:          ./HEALTH_Multimodality.md
IMPLEMENTATION:  ./IMPLEMENTATION_Multimodality.md
SYNC:            ./SYNC_Multimodality.md

IMPL:            runtime/cognition/multimodal.py (to be created)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

This module implements three algorithms:

1. **Multimodal Coherence** — extends Law 8's coherence formula from a fixed two-modality form (text + image) to an N-modality form where each available modality contributes a weighted cosine similarity term. Missing modalities are gracefully skipped with weight redistribution.

2. **Embedding Dispatch** — routes a media attachment to the correct embedding model based on its modality key. Returns a vector that is stored on the MediaAttachment and participates in physics.

3. **Legacy Shim** — reads v2.2 `image_uri`/`image_embedding` fields and presents them as a media dict entry, enabling backward compatibility without data migration.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| Extensible media (O1) | B1, B5 | Media dict absorbs any modality without schema change |
| Multimodal physics (O2) | B2, B6 | Coherence formula includes all available modality embeddings |
| URI-based storage (O3) | B1 | MediaAttachment enforces URI + embedding separation |
| Graceful degradation (O4) | B3 | Missing modalities redistributed, never crash |
| Backward compat (O5) | B4 | Legacy shim bridges v2.2 to media dict |

---

## DATA STRUCTURES

### MediaAttachment

```
MediaAttachment:
  uri: str                    # Required. URI to object storage.
  embedding: list[float]      # Optional. Embedding vector from modality-specific model.
  meta: dict[str, any]        # Optional. Modality-specific metadata (duration_s, type, etc.)
```

A MediaAttachment without an embedding is valid (the content exists but has not been embedded yet). It will not participate in coherence computation until embedded.

### ModalityConfig

```
ModalityConfig:
  key: str                    # e.g., "image", "voice", "geometry"
  embedding_model: str        # Name of the embedding model adapter
  embedding_dim: int          # Expected dimensionality of the embedding
  confidence_weight: float    # Weight in coherence formula (0.0 - 1.0)
```

Registered in `MODALITY_REGISTRY`, a dict keyed by modality string.

### Supported Modalities (v1)

| Modality Key | Embedding Model | Dimensions | Confidence Weight | Status |
|-------------|-----------------|------------|-------------------|--------|
| `text` | sentence-transformers | 1536 | (dynamic, see formula) | CANONICAL |
| `image` | CLIP / SigLIP | 768 | 0.25 | CANONICAL |
| `voice` | CLAP / AudioCLIP | 512 | 0.10 | DESIGNING |
| `video` | VideoCLIP / LanguageBind | 768 | 0.05 | PROPOSED |
| `geometry` | ULIP / PointBERT | 512 | 0.05 | PROPOSED |
| `code` | CodeBERT or text embed | 1536 | via text | PROPOSED |

---

## ALGORITHM: Multimodal Coherence

### Step 1: Identify Available Modalities

Given two nodes (or a stimulus and WM context), enumerate the modalities that have non-empty embeddings on BOTH sides. Text is always available (it is required on every node).

```
available_modalities = []
for key in MODALITY_REGISTRY:
    if key == "text":
        continue  # text handled separately
    if key in media_a and media_a[key].embedding and len(media_a[key].embedding) > 0:
        if key in media_b and media_b[key].embedding and len(media_b[key].embedding) > 0:
            available_modalities.append(key)
```

### Step 2: Compute Per-Modality Similarity

For each available modality, compute cosine similarity between the two embedding vectors. Validate that dimensions match — if they do not, raise an error (fail loud, per V3).

```
modality_scores = {}
for key in available_modalities:
    emb_a = media_a[key].embedding
    emb_b = media_b[key].embedding
    assert len(emb_a) == len(emb_b), f"Dimension mismatch for {key}: {len(emb_a)} vs {len(emb_b)}"
    modality_scores[key] = cosine_similarity(emb_a, emb_b)
```

### Step 3: Compute Weight Distribution

Start with the base weights. Sum the weights of AVAILABLE modalities. Compute the weight of UNAVAILABLE modalities (those in the registry but not available on both nodes). Redistribute unavailable weight to text.

```
base_weights = {key: MODALITY_REGISTRY[key].confidence_weight for key in MODALITY_REGISTRY if key != "text"}
available_weight = sum(base_weights[k] for k in available_modalities)
unavailable_weight = sum(base_weights[k] for k in base_weights if k not in available_modalities)

# Fixed terms
w_lex = 0.40   # lexical similarity weight (unchanged from v2.2)
w_affect = 0.10 # affective incongruence penalty (unchanged from v2.2)

# Text gets its base share plus all unavailable modality weight
w_text = (1.0 - w_lex - w_affect - available_weight) + unavailable_weight
# Simplification: w_text = 1.0 - w_lex - w_affect - available_weight + unavailable_weight
# Which equals: w_text = 1.0 - w_lex - w_affect - sum(available modality weights only)
# Wait — let me be precise:

# Total budget = 1.0
# Reserved: w_lex (0.40) + w_affect (0.10) = 0.50
# Remaining for text + modalities: 0.50
# If all registered modalities available: text gets 0.50 - sum(all modality weights)
# If some missing: text gets 0.50 - sum(available modality weights only)
# This naturally redistributes missing modality weight to text.

remaining = 1.0 - w_lex - w_affect  # = 0.50
w_text = remaining - sum(base_weights[k] for k in available_modalities)
```

This ensures:
- When no modalities are available: `w_text = 0.50` (the v2.2 fallback behavior: `Coh = 0.30*Sim_vec + 0.50*Sim_lex - 0.20*Δ_affect` where 0.30 = w_text when image was present at 0.25, but now without image w_text absorbs it to become 0.50... actually let me reconcile with the current formula).

**Reconciliation with v2.2 formula:**

Current (v2.2):
```
Coh = 0.25*Sim_vec + 0.25*Sim_vis + 0.40*Sim_lex - 0.10*Δ_affect
```

Fallback (no image):
```
Coh = 0.30*Sim_vec + 0.50*Sim_lex - 0.20*Δ_affect
```

The v2.2 fallback changes ALL weights, not just text. The multimodal formula generalizes differently — it keeps w_lex and w_affect fixed and only redistributes modality weight to text. This is a deliberate simplification:

**Multimodal formula (canonical):**
```
Coh = w_text * Sim_text
    + sum(w_mod * Sim_mod for mod in available_modalities)
    + w_lex * Sim_lex
    - w_affect * Δ_affect
```

Where:
- `w_lex = 0.40` (fixed)
- `w_affect = 0.10` (fixed)
- `w_text = 0.50 - sum(w_mod for mod in available_modalities)` (absorbs missing modality weight)
- `w_mod` from `MODALITY_REGISTRY[mod].confidence_weight`

**Examples:**

All modalities available (image=0.25, voice=0.10):
```
w_text = 0.50 - 0.25 - 0.10 = 0.15
Coh = 0.15*Sim_text + 0.25*Sim_image + 0.10*Sim_voice + 0.40*Sim_lex - 0.10*Δ_affect
```

Only image available:
```
w_text = 0.50 - 0.25 = 0.25
Coh = 0.25*Sim_text + 0.25*Sim_image + 0.40*Sim_lex - 0.10*Δ_affect
```

This matches the current v2.2 formula exactly. Backward compatible.

No modalities available (text only):
```
w_text = 0.50
Coh = 0.50*Sim_text + 0.40*Sim_lex - 0.10*Δ_affect
```

### Step 4: Compute Final Coherence

```
Coh = w_text * cosine(stimulus_text_embedding, context_text_embedding)
    + sum(w_mod * modality_scores[mod] for mod in available_modalities)
    + w_lex * lexical_similarity(stimulus_names, wm_names)
    - w_affect * abs(stimulus_valence - wm_mean_valence)

Coh = max(0.0, min(1.0, Coh))  # clamp to [0, 1]
```

---

## ALGORITHM: Embedding Dispatch

### Step 1: Identify Modality

Look up the modality key in `MODALITY_REGISTRY`. If not found, raise an error — unknown modalities cannot be embedded.

```
if modality_key not in MODALITY_REGISTRY:
    raise ValueError(f"Unknown modality: {modality_key}. Register in MODALITY_REGISTRY first.")
config = MODALITY_REGISTRY[modality_key]
```

### Step 2: Load Model Adapter

Each modality has a registered model adapter name. The dispatcher resolves the adapter from a registry of embedding functions.

```
adapter = EMBEDDING_ADAPTERS.get(config.embedding_model)
if adapter is None:
    raise RuntimeError(f"No adapter for model: {config.embedding_model}")
```

### Step 3: Compute Embedding

Call the adapter with the media URI. The adapter downloads the content (if needed), runs the model, and returns a vector.

```
embedding = adapter.embed(uri=attachment.uri)
assert len(embedding) == config.embedding_dim, f"Expected {config.embedding_dim}D, got {len(embedding)}D"
attachment.embedding = embedding
```

---

## ALGORITHM: Legacy Shim

### Step 1: Check for media Dict

If the node already has a `media` dict with an `image` key, return it as-is. The node has been migrated.

### Step 2: Check for Legacy Fields

If the node has `image_uri` set (non-None, non-empty), construct a MediaAttachment:

```
if node.image_uri and not node.media.get("image"):
    node_media["image"] = MediaAttachment(
        uri=node.image_uri,
        embedding=node.image_embedding if node.image_embedding else [],
        meta={},
    )
```

### Step 3: Return Merged Media

Return the node's `media` dict merged with any legacy shim entries. The shim is read-only — it never writes back to the node.

---

## KEY DECISIONS

### D1: Weight Redistribution Strategy

```
IF all registered modalities are available on both nodes:
    Each modality gets its confidence weight
    Text gets the remainder (0.50 - sum of modality weights)
ELSE:
    Missing modality weights are absorbed by text
    w_text grows to fill the gap
    w_lex and w_affect stay fixed
```

Why: Text is always available and always meaningful. It is the safest recipient of redistributed weight. Redistributing to other modalities could amplify noise.

### D2: Dimensionality Mismatch Handling

```
IF embedding dimensions differ for the same modality on two nodes:
    Raise ValueError (fail loud)
    Log both dimensions and both node IDs
ELSE:
    Proceed with cosine similarity
```

Why: Dimension mismatch indicates a model version inconsistency. Silently skipping would hide a data integrity problem. Fail loud forces the operator to fix the inconsistency.

### D3: Empty Embedding vs Missing Key

```
IF modality key exists in media dict but embedding is empty ([]):
    Treat as unavailable for coherence (no physics participation)
    URI is preserved (content exists, just not embedded)
IF modality key does not exist in media dict:
    Treat as unavailable for coherence
```

Why: Both cases mean "no embedding to compute similarity with." The difference matters for the upload pipeline (empty embedding = needs embedding computation), but not for coherence.

---

## DATA FLOW

```
Node creation (graph_write)
    |
    | media attachments included in payload
    v
MediaAttachment validation
    |
    | URI format validated, embedding dimensions checked
    v
[Optional] Embedding dispatch
    |
    | If embedding not provided, route to model adapter
    v
Node stored in FalkorDB
    |
    | media dict serialized as node property
    v
Physics tick (Law 8)
    |
    | compute_multimodal_coherence() called
    v
Coherence score
    |
    | used by Law 4 (attentional competition) for WM selection
    v
Working Memory updated
```

---

## COMPLEXITY

**Time:** O(M * D) per coherence computation — where M = number of available modalities and D = max embedding dimensionality. Cosine similarity is O(D). With M <= 5 modalities and D <= 2048, this is trivially fast (microseconds).

**Space:** O(M * D) per node — each media attachment stores one embedding vector. With M=3 and D=1536, that's ~18K floats per node. At 8 bytes each, ~144KB per fully-loaded node. Most nodes will have 0-1 modalities, so average is much lower.

**Bottlenecks:**
- Embedding computation (dispatch) is the expensive part — model inference can take seconds for audio/video. This happens at write time, not at tick time. The tick loop never waits for embedding models.
- FalkorDB serialization of nested dicts with large float arrays. Needs benchmarking with real data volumes.

---

## HELPER FUNCTIONS

### `cosine_similarity(a, b)`

**Purpose:** Compute cosine similarity between two vectors of equal length.

**Logic:** `dot(a, b) / (norm(a) * norm(b))`. Returns 0.0 if either vector has zero norm.

### `get_node_media(node)`

**Purpose:** Extract the media dict from a node, applying the legacy shim if needed.

**Logic:** If `node.media` exists and has entries, return it. Else, check `node.image_uri` / `node.image_embedding` and construct a shim dict. Return the merged result.

### `resolve_weights(available_modalities, modality_registry)`

**Purpose:** Compute the effective weight distribution for a given set of available modalities.

**Logic:** Sum weights of available modalities. Compute w_text as the remainder of the 0.50 budget. Return dict of modality -> weight, plus w_text, w_lex, w_affect.

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| `runtime/cognition/models.py` | `Node.media`, `Node.image_uri`, `Node.image_embedding` | Media data and legacy fields |
| `runtime/cognition/constants.py` | `MODALITY_WEIGHTS`, `W_LEX`, `W_AFFECT` | Weight constants |
| `runtime/physics/exploration.py` | Called BY exploration for coherence | We provide the coherence score |
| `mcp/tools/graph_write_handler.py` | Called BY graph_write for validation | We validate MediaAttachment structure |

---

## MARKERS

<!-- @mind:todo Implement the EMBEDDING_ADAPTERS registry. Initially can be a dict mapping model name to callable. For v1, only CLIP adapter is needed (image). CLAP adapter is DESIGNING. -->

<!-- @mind:todo Write the cosine_similarity helper. Do not use numpy — keep the dependency minimal. Pure Python with math.sqrt is sufficient for vectors under 2048D. -->

<!-- @mind:proposition Consider caching modality weight resolution per tick. If many nodes are compared in a single tick, the available modalities may be similar and the weight computation is redundant. Micro-optimization, but the tick loop is hot path. -->

<!-- @mind:escalation The v2.2 fallback formula (Coh = 0.30*Sim_vec + 0.50*Sim_lex - 0.20*Δ_affect) does NOT match the multimodal formula's text-only case (Coh = 0.50*Sim_text + 0.40*Sim_lex - 0.10*Δ_affect). The v2.2 fallback redistributes ALL weights differently. Which is canonical — the v2.2 fallback or the generalized multimodal formula? NLR decision needed. The multimodal formula is cleaner (fixed w_lex and w_affect) but changes fallback behavior. -->
