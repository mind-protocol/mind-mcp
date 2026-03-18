# Multimodality — Implementation: Code Architecture and Structure

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
ALGORITHM:       ./ALGORITHM_Multimodality.md
VALIDATION:      ./VALIDATION_Multimodality.md
THIS:            IMPLEMENTATION_Multimodality.md (you are here)
HEALTH:          ./HEALTH_Multimodality.md
SYNC:            ./SYNC_Multimodality.md

IMPL:            runtime/cognition/multimodal.py (to be created)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

```
runtime/
├── cognition/
│   ├── multimodal.py                    # NEW — MediaAttachment, coherence, dispatch, shim
│   ├── models.py                        # MODIFIED — Node gains `media: dict` field
│   ├── constants.py                     # MODIFIED — modality weights added
│   └── laws/
│       └── (unchanged)                  # Laws are modality-agnostic
├── physics/
│   └── exploration.py                   # MODIFIED — uses multimodal coherence in traversal
mcp/
├── tools/
│   └── graph_write_handler.py           # MODIFIED — accepts media in node creation
```

### File Responsibilities

| File | Purpose | Key Functions/Classes | Lines | Status |
|------|---------|----------------------|-------|--------|
| `runtime/cognition/multimodal.py` | Multimodal data types, coherence, dispatch, legacy shim | `MediaAttachment`, `ModalityConfig`, `compute_multimodal_coherence()`, `get_node_media()`, `dispatch_embedding()`, `resolve_weights()` | ~250 | NEW |
| `runtime/cognition/models.py` | Node dataclass — gains `media` field | `Node.media` | ~360 (current) +5 | MODIFIED |
| `runtime/cognition/constants.py` | Global constants — gains modality weights | `MODALITY_WEIGHTS`, `W_LEX`, `W_AFFECT`, `MODALITY_REGISTRY` | +20 | MODIFIED |
| `runtime/physics/exploration.py` | SubEntity traversal — uses multimodal coherence | coherence call site | varies | MODIFIED |
| `mcp/tools/graph_write_handler.py` | Node creation API — accepts media payload | media validation | varies | MODIFIED |

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Pipeline with Registry

**Why this pattern:** The multimodal system has a natural pipeline shape: media arrives -> validated -> dispatched to the right embedding model -> stored -> later retrieved for coherence computation. The modality registry makes the pipeline extensible without code changes.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Registry | `MODALITY_REGISTRY` in constants.py | Maps modality keys to configs (model, dims, weight). Adding a modality = adding a registry entry. |
| Adapter | `EMBEDDING_ADAPTERS` in multimodal.py | Each embedding model implements a common interface. Dispatch routes to the right adapter. |
| Shim / Facade | `get_node_media()` | Presents v2.2 legacy fields and new media dict through a single interface. |
| Value Object | `MediaAttachment` dataclass | Immutable-ish data carrier. No behavior beyond holding uri/embedding/meta. |

### Anti-Patterns to Avoid

- **Modality-specific branches in physics laws**: Don't add `if modality == "audio":` inside Law 8 or any other law. The coherence formula works with vectors. Modality is resolved before the formula runs.
- **Eager embedding**: Don't compute embeddings during node read or tick. Embedding is a write-time concern. The tick loop must never wait for model inference.
- **Inline model inference**: Don't import model libraries (torch, transformers) at module level in multimodal.py. Model adapters are lazy-loaded and may run in separate processes.

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Multimodal module | MediaAttachment, coherence formula, dispatch routing, legacy shim | Embedding model inference, media upload, object storage | `compute_multimodal_coherence()`, `get_node_media()`, `dispatch_embedding()` |
| Physics laws | Coherence score consumption | How coherence is computed (multimodal or not) | `coherence: float` return value |
| graph_write | Node creation with media dict | How media is embedded | `media: dict` in node payload |

---

## SCHEMA

### MediaAttachment

```yaml
MediaAttachment:
  required:
    - uri: str                    # Object storage URI (s3://, r2://, file://)
  optional:
    - embedding: list[float]      # Modality-specific embedding vector
    - meta: dict[str, any]        # Free-form metadata (duration_s, type, resolution, etc.)
  constraints:
    - uri must start with a valid scheme (s3://, r2://, file://, https://)
    - embedding, if present, must be a non-empty list of floats
    - embedding dimensions must match MODALITY_REGISTRY[key].embedding_dim
```

### Node.media (addition to NodeBase)

```yaml
Node.media:
  type: dict[str, MediaAttachment]
  default: {}
  description: "Multimodal attachments. Key = modality string, value = MediaAttachment."
  constraints:
    - keys must be valid modality strings (lowercase, alphanumeric)
    - values must be valid MediaAttachment instances
```

### ModalityConfig (in MODALITY_REGISTRY)

```yaml
ModalityConfig:
  required:
    - key: str                    # e.g., "image", "voice"
    - embedding_model: str        # Name of adapter
    - embedding_dim: int          # Expected dimensionality
    - confidence_weight: float    # Weight in coherence formula
  constraints:
    - confidence_weight in [0.0, 0.50)
    - confidence_weight < w_text for any realistic configuration
```

---

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| `compute_multimodal_coherence()` | `runtime/cognition/multimodal.py` | Law 8 coherence computation during tick (via exploration.py) |
| `get_node_media()` | `runtime/cognition/multimodal.py` | Any code reading a node's media (coherence, context assembly, UI) |
| `dispatch_embedding()` | `runtime/cognition/multimodal.py` | graph_write when a media attachment lacks an embedding |
| `resolve_weights()` | `runtime/cognition/multimodal.py` | compute_multimodal_coherence() internally |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

### Media Write Flow: Attaching Media to a Node

Explain: when a caller creates or updates a node with media, the attachment is validated, optionally embedded, and stored. This flow is the primary write path for multimodal data.

```yaml
flow:
  name: media_write
  purpose: "Store media attachments on nodes with validated URIs and optional embedding computation"
  scope: "graph_write API -> node in FalkorDB"
  steps:
    - id: step_1
      description: "Caller sends node creation/update with media dict in payload"
      file: mcp/tools/graph_write_handler.py
      function: handle_graph_write()
      input: "dict with node fields + media: {modality: {uri, embedding?, meta?}}"
      output: "validated node payload"
      trigger: "MCP graph_write tool call"
      side_effects: "none"
    - id: step_2
      description: "Validate each MediaAttachment: URI scheme, embedding dims if present"
      file: runtime/cognition/multimodal.py
      function: validate_media_attachment()
      input: "MediaAttachment + modality key"
      output: "validated MediaAttachment or error"
      trigger: "called by step_1"
      side_effects: "none"
    - id: step_3
      description: "If embedding missing and auto-embed enabled, dispatch to model adapter"
      file: runtime/cognition/multimodal.py
      function: dispatch_embedding()
      input: "MediaAttachment with URI, modality key"
      output: "MediaAttachment with embedding populated"
      trigger: "called by step_2 when embedding is empty"
      side_effects: "network call to embedding model (potentially slow)"
    - id: step_4
      description: "Store node with media dict in FalkorDB"
      file: runtime/graph/write.py
      function: upsert_node()
      input: "complete node with media dict"
      output: "stored node"
      trigger: "called by step_1 after validation"
      side_effects: "FalkorDB write"
  docking_points:
    guidance:
      include_when: "validation failures, embedding dimension mismatches, URI scheme violations"
      omit_when: "successful pass-through with no anomalies"
      selection_notes: "Focus on step_2 (validation) and step_3 (dispatch) as they can fail"
    available:
      - id: dock_media_validation
        type: api
        direction: input
        file: runtime/cognition/multimodal.py
        function: validate_media_attachment()
        trigger: "graph_write with media payload"
        payload: "MediaAttachment + modality key"
        async_hook: not_applicable
        needs: none
        notes: "Validation failures should surface immediately with clear error messages"
      - id: dock_embedding_dispatch
        type: api
        direction: output
        file: runtime/cognition/multimodal.py
        function: dispatch_embedding()
        trigger: "missing embedding on attachment"
        payload: "MediaAttachment with populated embedding"
        async_hook: optional
        needs: "add async hook if embedding becomes background job"
        notes: "Potentially slow (model inference). Must never happen during tick."
    health_recommended:
      - dock_id: dock_media_validation
        reason: "Catches URI format violations and dimension mismatches before they enter the graph"
```

### Coherence Computation Flow: Multimodal Coherence During Tick

Explain: during the tick loop, Law 8 computes coherence between nodes. This flow extends coherence to include multimodal embeddings.

```yaml
flow:
  name: multimodal_coherence
  purpose: "Compute coherence score incorporating all available modality embeddings"
  scope: "physics tick -> coherence score -> WM selection"
  steps:
    - id: step_1
      description: "Retrieve media dicts for both nodes (or stimulus + WM context)"
      file: runtime/cognition/multimodal.py
      function: get_node_media()
      input: "Node"
      output: "dict[str, MediaAttachment]"
      trigger: "called by coherence computation"
      side_effects: "none (read-only, includes legacy shim)"
    - id: step_2
      description: "Identify available modalities (present on both sides with non-empty embeddings)"
      file: runtime/cognition/multimodal.py
      function: compute_multimodal_coherence() step 1
      input: "two media dicts"
      output: "list of available modality keys"
      trigger: "internal"
      side_effects: "none"
    - id: step_3
      description: "Resolve effective weights (redistribute missing modality weight to text)"
      file: runtime/cognition/multimodal.py
      function: resolve_weights()
      input: "available modalities + registry"
      output: "dict of modality -> effective weight"
      trigger: "internal"
      side_effects: "none"
    - id: step_4
      description: "Compute per-modality cosine similarities and final coherence score"
      file: runtime/cognition/multimodal.py
      function: compute_multimodal_coherence() steps 2-4
      input: "embeddings, weights, text embeddings, lexical data, valence"
      output: "float in [0, 1]"
      trigger: "internal"
      side_effects: "none"
  docking_points:
    guidance:
      include_when: "coherence returns unexpected values, dimension mismatches, weight distribution anomalies"
      omit_when: "normal coherence computation with valid inputs"
      selection_notes: "Step 4 output is the critical dock — the coherence score drives WM selection"
    available:
      - id: dock_coherence_output
        type: graph_ops
        direction: output
        file: runtime/cognition/multimodal.py
        function: compute_multimodal_coherence()
        trigger: "Law 8 during tick"
        payload: "float coherence score"
        async_hook: not_applicable
        needs: none
        notes: "Must always return valid float. NaN/infinity would corrupt entire tick."
      - id: dock_weight_resolution
        type: graph_ops
        direction: output
        file: runtime/cognition/multimodal.py
        function: resolve_weights()
        trigger: "internal to coherence computation"
        payload: "dict of modality -> weight"
        async_hook: not_applicable
        needs: none
        notes: "Weights must sum to 1.0 (within float tolerance). Useful for debugging weight drift."
    health_recommended:
      - dock_id: dock_coherence_output
        reason: "Coherence score directly drives WM selection — invalid values corrupt consciousness"
      - dock_id: dock_weight_resolution
        reason: "Weight balance invariant (V5) — verify redistribution logic is correct"
```

---

## LOGIC CHAINS

### LC1: Media Attachment to Physics Participation

**Purpose:** Trace how a media file goes from upload to influencing working memory.

```
media file uploaded via /media MCP tool
  -> graph_write_handler.handle_graph_write()     # validate, extract media
    -> multimodal.validate_media_attachment()      # check URI, dims
    -> multimodal.dispatch_embedding()             # compute embedding if missing
      -> EMBEDDING_ADAPTERS[model].embed(uri)      # model inference
    -> graph.write.upsert_node()                   # store in FalkorDB
      -> (node persisted with media dict)

... later, during tick ...

physics tick step 4 (PROPAGATE, Law 8)
  -> exploration.compute_coherence()               # coherence for WM selection
    -> multimodal.get_node_media(node_a)           # read media (with shim)
    -> multimodal.get_node_media(node_b)           # read media (with shim)
    -> multimodal.compute_multimodal_coherence()   # N-modality formula
      -> multimodal.resolve_weights()              # weight distribution
      -> cosine_similarity() per modality          # per-modality scores
      -> weighted sum                              # final coherence
    -> coherence score used by Law 4               # WM selection
```

**Data transformation:**
- Input: raw media file (audio, image, etc.)
- After upload: URI in object storage
- After embedding: MediaAttachment(uri, embedding, meta)
- After storage: node property in FalkorDB
- After coherence: float in [0, 1] contributing to WM selection

### LC2: Legacy Shim Read Path

**Purpose:** How a v2.2 node's image data surfaces through the new interface.

```
node with image_uri + image_embedding (v2.2 format)
  -> multimodal.get_node_media(node)
    -> check node.media.get("image"): None
    -> check node.image_uri: "s3://..."
    -> construct MediaAttachment(uri=node.image_uri, embedding=node.image_embedding, meta={})
    -> return {"image": <MediaAttachment>}
  -> consumer sees standard media dict
```

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
runtime/cognition/multimodal.py
    └── imports → runtime/cognition/constants.py (MODALITY_WEIGHTS, W_LEX, W_AFFECT)
    └── imports → runtime/cognition/models.py (Node, MediaAttachment types)

runtime/physics/exploration.py
    └── imports → runtime/cognition/multimodal.py (compute_multimodal_coherence, get_node_media)

mcp/tools/graph_write_handler.py
    └── imports → runtime/cognition/multimodal.py (validate_media_attachment, dispatch_embedding)
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `math` | `sqrt` for cosine similarity | `runtime/cognition/multimodal.py` |
| (no external deps) | — | Embedding model adapters are separate packages, lazily imported |

---

## STATE MANAGEMENT

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| Media attachments | `Node.media` dict in FalkorDB | Per-node | Created on write, persists until node deleted |
| Modality registry | `MODALITY_REGISTRY` in constants.py | Global (module-level) | Loaded at import, immutable at runtime |
| Legacy image fields | `Node.image_uri`, `Node.image_embedding` | Per-node | v2.2 existing, read by shim, eventually migrated |

### State Transitions

```
Node created (text only) ──graph_write with media──> Node with media dict ──tick──> Coherence uses multimodal
                                                                                        |
Node with legacy image_uri ──get_node_media()──> Shim returns media dict ──coherence──> Same path
```

---

## RUNTIME BEHAVIOR

### Initialization

```
1. Module imported: MODALITY_REGISTRY loaded from constants.py
2. EMBEDDING_ADAPTERS populated (lazy — adapters register themselves)
3. Ready to serve get_node_media(), compute_multimodal_coherence(), dispatch_embedding()
```

### Main Loop / Request Cycle

```
1. graph_write receives node with media
2. validate_media_attachment() checks each attachment
3. dispatch_embedding() computes missing embeddings (if auto-embed)
4. Node stored in FalkorDB
---
5. During tick, Law 8 calls compute_multimodal_coherence()
6. get_node_media() reads media (with shim if needed)
7. resolve_weights() computes effective weights
8. Cosine similarity per modality
9. Weighted sum -> coherence score
```

### Shutdown

```
1. No special cleanup needed — all state is in FalkorDB
2. Embedding model adapters may need cleanup (GPU memory) — adapter-specific
```

---

## CONCURRENCY MODEL

| Component | Model | Notes |
|-----------|-------|-------|
| `compute_multimodal_coherence()` | sync | Called within tick loop, must be fast, no I/O |
| `get_node_media()` | sync | Pure read from node properties, no I/O |
| `dispatch_embedding()` | async-capable | Model inference can be slow — may run in background worker |
| `validate_media_attachment()` | sync | Pure validation, no I/O |

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `MODALITY_WEIGHTS["image"]` | `constants.py` | `0.25` | CLIP image confidence weight |
| `MODALITY_WEIGHTS["voice"]` | `constants.py` | `0.10` | CLAP audio confidence weight |
| `MODALITY_WEIGHTS["video"]` | `constants.py` | `0.05` | VideoCLIP video confidence weight |
| `MODALITY_WEIGHTS["geometry"]` | `constants.py` | `0.05` | ULIP 3D confidence weight |
| `W_LEX` | `constants.py` | `0.40` | Lexical similarity weight (fixed) |
| `W_AFFECT` | `constants.py` | `0.10` | Affective incongruence penalty weight (fixed) |
| `AUTO_EMBED` | env | `false` | Whether dispatch_embedding() auto-runs on missing embeddings |

---

## BIDIRECTIONAL LINKS

### Code -> Docs

Files that reference this documentation:

| File | Line | Reference |
|------|------|-----------|
| `runtime/cognition/multimodal.py` | TBD | `# DOCS: docs/cognition/multimodality/PATTERNS_Multimodality.md` |

### Docs -> Code

| Doc Section | Implemented In |
|-------------|----------------|
| ALGORITHM multimodal coherence | `runtime/cognition/multimodal.py:compute_multimodal_coherence()` |
| ALGORITHM embedding dispatch | `runtime/cognition/multimodal.py:dispatch_embedding()` |
| ALGORITHM legacy shim | `runtime/cognition/multimodal.py:get_node_media()` |
| BEHAVIOR B1 | `mcp/tools/graph_write_handler.py` (media acceptance) |
| BEHAVIOR B2 | `runtime/cognition/multimodal.py:compute_multimodal_coherence()` |
| BEHAVIOR B3 | `runtime/cognition/multimodal.py:resolve_weights()` |
| BEHAVIOR B4 | `runtime/cognition/multimodal.py:get_node_media()` (legacy shim) |
| VALIDATION V1 | `runtime/cognition/multimodal.py:validate_media_attachment()` |
| VALIDATION V2 | `runtime/cognition/multimodal.py:compute_multimodal_coherence()` (clamp) |

---

## EXTRACTION CANDIDATES

No extraction needed yet — the module is new and estimated at ~250 lines.

---

## MARKERS

<!-- @mind:todo Create runtime/cognition/multimodal.py with MediaAttachment, ModalityConfig, compute_multimodal_coherence(), get_node_media(), dispatch_embedding(), resolve_weights() -->

<!-- @mind:todo Add `media: dict` field to Node dataclass in runtime/cognition/models.py with default {} -->

<!-- @mind:todo Add MODALITY_WEIGHTS, W_LEX, W_AFFECT, MODALITY_REGISTRY to runtime/cognition/constants.py -->

<!-- @mind:todo Modify runtime/physics/exploration.py to call compute_multimodal_coherence() instead of current two-modality coherence -->

<!-- @mind:todo Modify mcp/tools/graph_write_handler.py to accept and validate media dict in node payloads -->

<!-- @mind:todo Write backward compat migration: when a node is written with image_uri/image_embedding, also populate media.image. Progressive, not breaking. -->

<!-- @mind:proposition Consider a separate file for embedding model adapters (runtime/cognition/multimodal_embedding_adapters.py) if the adapter registry grows beyond 3 models. For now, keep in multimodal.py. -->
