# Multimodality — Patterns: URI + Embedding Per Modality

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Multimodality.md
THIS:            PATTERNS_Multimodality.md (you are here)
BEHAVIORS:       ./BEHAVIORS_Multimodality.md
ALGORITHM:       ./ALGORITHM_Multimodality.md
VALIDATION:      ./VALIDATION_Multimodality.md
HEALTH:          ./HEALTH_Multimodality.md
IMPLEMENTATION:  ./IMPLEMENTATION_Multimodality.md
SYNC:            ./SYNC_Multimodality.md

IMPL:            runtime/cognition/multimodal.py (to be created)
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read the linked IMPL source file

**After modifying this doc:**
1. Update the IMPL source file to match, OR
2. Add a TODO in SYNC_Multimodality.md: "Docs updated, implementation needs: {what}"

**After modifying the code:**
1. Update this doc chain to match, OR
2. Add a TODO in SYNC_Multimodality.md: "Implementation changed, docs need: {what}"

---

## THE PROBLEM

Nodes currently support two content modalities: text (via `synthesis`, `content`, `embedding`) and images (via `image_uri`, `image_embedding` added in v2.2). But knowledge is not just text and images.

A citizen who heard a voice, watched a video, explored a 3D environment — these experiences must participate in the physics. A stressed voice should resonate when a similar emotional context arises in working memory. A 3D space layout should influence spatial reasoning during traversal.

The v2.2 approach of adding dedicated fields per modality (`image_uri`, `image_embedding`) does not scale. Adding audio would require `audio_uri`, `audio_embedding`, `audio_duration`, `audio_type`. Adding video would require another set. Each new modality means a schema migration, new fields on NodeBase, and new code paths in every system that touches nodes.

This is a structural problem, not an incremental one. The current approach fragments multimodal data across ad-hoc fields. The physics engine must special-case each modality. The coherence formula has hardcoded terms. None of this extends.

---

## THE PATTERN

Every media attachment follows the same shape: **URI + Embedding + Metadata**.

- **URI** points to object storage (S3/R2/local). Binary content never enters FalkorDB.
- **Embedding** puts the content into the physics space. The laws do not know whether it is audio or video — they see a vector. Cosine similarity works identically across modalities.
- **Metadata** carries modality-specific information (duration for audio, resolution for images, vertex count for 3D) that enrichers or UIs may need but the physics engine ignores.

Instead of separate fields per modality, NodeBase gains a single `media` dict. The key is the modality name (a string, not an enum — extensible). The value is a `MediaAttachment` containing `uri`, `embedding`, and free-form `meta`:

```yaml
media:
  image:
    uri: "s3://minds/citizen/nervo/avatar.png"
    embedding: [0.12, -0.34, ...]    # CLIP 768D
    meta: {}
  voice:
    uri: "s3://minds/citizen/nervo/intro.mp3"
    embedding: [0.08, 0.22, ...]     # CLAP 512D
    meta:
      duration_s: 12.5
      type: "speech"
  geometry:
    uri: "s3://minds/spaces/arsenal/model.glb"
    embedding: [0.15, -0.07, ...]    # ULIP
    meta:
      vertices: 14200
```

The coherence formula (Law 8) generalizes from the current two-modality form to an N-modality form. Each modality contributes a weighted similarity term. The weight reflects model confidence — mature models (CLIP) get higher weight than emerging ones (ULIP). When a modality is absent on either node, its term is skipped and weight redistributes to text.

The key insight: **the physics laws already work with vectors. Modality is transparent to the physics.** The only place modality matters is (1) choosing the right embedding model, and (2) setting the right confidence weight. Everything downstream — propagation, coherence, traversal — operates on vectors without caring what generated them.

---

## BEHAVIORS SUPPORTED

- **B1** (Media Attachment Stored) — any modality can be attached to any node via the media dict
- **B2** (Multimodal Coherence Computed) — Law 8 coherence uses all available modality embeddings
- **B3** (Graceful Fallback on Missing Modality) — missing modalities are skipped, weights redistributed
- **B4** (Backward Compatibility Preserved) — `image_uri`/`image_embedding` still readable via shim
- **B5** (New Modality Added Without Schema Change) — only embedding model + weight required

## BEHAVIORS PREVENTED

- **A1** (Binary Blob in Graph) — URIs only; base64/binary is structurally impossible via the MediaAttachment type
- **A2** (Hardcoded Modality Fields) — no `audio_uri`, `video_uri` fields; everything through media dict
- **A3** (Modality-Specific Laws) — no new physics laws for specific modalities

---

## PRINCIPLES

### Principle 1: URI + Embedding, Always

Storage is URI, physics is embedding. These are the two faces of every media attachment. The URI tells you WHERE the content lives. The embedding tells you WHAT the content means in physics space. Neither is optional for a complete attachment (though an attachment can exist with URI only if embedding hasn't been computed yet — it just won't participate in physics).

### Principle 2: Text is the Lingua Franca

Text (synthesis + content + embedding) remains the primary modality. It is the only modality that is REQUIRED on every node. All other modalities are bonuses that enrich the coherence signal but never replace it. A node with only text is fully functional. A node with only audio metadata and no text synthesis is incomplete.

### Principle 3: Model Confidence Weights

Each modality's embedding model has a confidence weight reflecting its reliability. CLIP (images) is well-validated, so `w_image = 0.25`. CLAP (audio) is less mature, so `w_audio = 0.10`. A hypothetical new 3D model might start at `w_3d = 0.05`. These weights determine how much influence the modality's similarity score has on the overall coherence computation. As models improve, weights can increase without code changes — just update the weight constant.

### Principle 4: The Graph Stays Lean

FalkorDB stores node properties as JSON-serializable values. Embeddings are float arrays — acceptable. URIs are strings — acceptable. Binary blobs, base64 strings, or inline media content — never acceptable. The media dict must serialize cleanly to graph properties. If a modality produces embeddings larger than 2048 dimensions, consider dimensionality reduction before storage.

### Principle 5: Extensibility Through Convention, Not Schema

Adding a new modality is a convention, not a schema change. The convention: (1) choose a modality key name, (2) implement an embedding model adapter that produces a vector, (3) register a confidence weight, (4) populate `media[key]` on relevant nodes. No migration scripts. No new fields. No code changes to the physics engine.

---

## DATA

| Source | Type | Purpose / Description |
|--------|------|-----------------------|
| `schema-l1.yaml` | FILE | L1 schema — defines NodeBase with current `image_uri`/`image_embedding` fields |
| `runtime/cognition/models.py` | FILE | Node dataclass — will gain `media: dict` field |
| `runtime/cognition/physics_visual_mapping.py` | FILE | Physics-to-visual mapping — style reference for physics integration |
| `runtime/cognition/constants.py` | FILE | Global constants — modality weights will be added here |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `runtime/cognition/models.py` | Node dataclass must carry the `media` dict |
| `runtime/cognition/constants.py` | Modality confidence weights stored as constants |
| `runtime/physics/exploration.py` | SubEntity traversal uses coherence — must accept multimodal coherence |
| `mcp/tools/graph_write_handler.py` | Node creation API must accept media attachments |
| `mcp/tools/media_handler.py` | `/media` MCP tool stores results as media attachments |

---

## INSPIRATIONS

**CLIP (Contrastive Language-Image Pre-training).** OpenAI's demonstration that images and text can share a latent space via contrastive learning. This is the proof that modality-agnostic physics is viable: if embeddings live in compatible spaces, cosine similarity works across modalities.

**CLAP (Contrastive Language-Audio Pre-training).** Microsoft's extension of the CLIP paradigm to audio. The same insight — a stressed voice and the text "I feel stressed" produce embeddings that are close in the shared space. This is how audio participates in cognitive physics.

**Multimodal Large Language Models.** GPT-4V, Gemini, and Claude demonstrate that multimodal understanding emerges from representing different modalities in compatible embedding spaces. Mind Protocol's approach is simpler — we don't need a giant model, just per-modality encoders that produce compatible vectors for physics.

**Biological multisensory integration.** The brain doesn't have separate physics for vision and hearing. Multisensory neurons in the superior colliculus respond to coincident stimuli from any modality. The response is additive — visual + auditory > either alone. This is exactly the coherence formula's behavior: more modalities = richer coherence signal.

---

## SCOPE

### In Scope

- `MediaAttachment` dataclass (uri, embedding, meta)
- `media` dict on Node (key = modality string, value = MediaAttachment)
- Multimodal coherence formula (extending Law 8's Coh computation)
- Modality confidence weight registry (constants)
- Embedding dispatch (routing media to the correct embedding model)
- Backward compatibility shim for `image_uri` / `image_embedding`
- Integration with `graph_write` (accepting media on node creation/update)

### Out of Scope

- **Media upload/storage pipeline** — how files get to S3/R2 is the `/media` tool's responsibility, not this module's. See: `mcp/tools/media_handler.py`
- **Embedding model implementation** — the actual CLIP/CLAP/ULIP model inference. This module dispatches to model adapters; it does not implement them.
- **Transcoding** — converting audio formats, resizing images. Preprocessing happens before this module.
- **Cross-modal generation** — generating images from audio or vice versa. Each modality is independent.
- **Real-time streaming** — processing live audio/video streams. This module handles stored, completed media.

---

## MARKERS

<!-- @mind:todo Decide on embedding dimension normalization strategy. CLIP produces 768D, CLAP 512D, text embeddings are 1536D. Should we project all to a common dimensionality, or let the coherence formula handle heterogeneous dimensions via per-modality cosine? -->

<!-- @mind:proposition Consider a "modality freshness" concept where older media attachments decay in influence. A voice memo from 6 months ago might be less relevant than one from yesterday. This could be handled via recency on the MediaAttachment itself. v2+ territory. -->

<!-- @mind:escalation The media dict serialization to FalkorDB needs validation. FalkorDB stores node properties as Redis-compatible types. A nested dict with float arrays may need flattening or JSON string encoding. Need to test with actual FalkorDB before committing to the schema. -->
