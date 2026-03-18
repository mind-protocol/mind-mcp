# OBJECTIVES — Multimodality

```
STATUS: DESIGNING
CREATED: 2026-03-18
VERIFIED: —
```

---

## CHAIN

```
THIS:            OBJECTIVES_Multimodality.md (you are here - START HERE)
PATTERNS:       ./PATTERNS_Multimodality.md
BEHAVIORS:      ./BEHAVIORS_Multimodality.md
ALGORITHM:      ./ALGORITHM_Multimodality.md
VALIDATION:     ./VALIDATION_Multimodality.md
IMPLEMENTATION: ./IMPLEMENTATION_Multimodality.md
HEALTH:         ./HEALTH_Multimodality.md
SYNC:           ./SYNC_Multimodality.md

IMPL:           runtime/cognition/multimodal.py (to be created)
```

**Read this chain in order before making changes.** Each doc answers different questions. Skipping ahead means missing context.

---

## PRIMARY OBJECTIVES (ranked)

1. **Extensible media attachment without schema changes** — Adding a new modality (audio, video, 3D) must require only a new embedding model and a weight constant, not new fields on NodeBase or changes to the graph schema. The `media` dict pattern absorbs any future modality without structural migration.

2. **Multimodal embeddings participate in physics** — Non-text embeddings (CLIP, CLAP, ULIP, VideoCLIP) must contribute to the coherence formula (Law 8) as weighted bonuses. The physics laws see vectors, not modalities. A stressed voice recording and a tense text memory should resonate when their embeddings are close.

3. **URI-based storage, embedding-based physics** — Media content lives in object storage (S3/R2/local), referenced by URI. Embeddings live in the graph for physics participation. The graph never stores binary blobs. This separation keeps FalkorDB lean and the physics fast.

4. **Graceful degradation when modalities are absent** — If a node lacks an audio embedding, or the CLAP model is unavailable, the coherence formula skips that modality's term and redistributes weight to text. No crashes, no NaN, no silent corruption.

5. **Backward compatibility with existing image fields** — `image_uri` and `image_embedding` (v2.2) continue to work. The migration to `media.image.uri` / `media.image.embedding` is progressive. Old code reads old fields; new code reads the media dict with a fallback shim.

## NON-OBJECTIVES

- **Replacing text as primary modality** — Text (synthesis + content + embedding) remains the lingua franca. All other modalities are bonuses. A node with only text is fully functional. A node with only audio is not.
- **Real-time transcoding** — The multimodal system stores and embeds media. It does not transcode video formats, compress audio, or resize images. That is the responsibility of the upload pipeline (MCP `/media` tool or external processors).
- **Modality-specific physics laws** — No new laws. Law 8 (compatibility) already works with vectors. The multimodal extension adds modality terms to the coherence formula, but the formula is still Law 8's job. No "Law 22: Audio Resonance."
- **Cross-modal generation** — Generating audio from text or images from audio is out of scope. Each modality arrives independently and is embedded independently.

## TRADEOFFS (canonical decisions)

- When **backward compatibility** conflicts with **clean design**, choose backward compatibility. The `image_uri`/`image_embedding` shim stays until all consumers migrate. Progressive, not breaking.
- When **embedding model accuracy** conflicts with **latency**, choose latency. Use the fastest model that produces reasonable embeddings. A citizen's tick must never wait for a 10-second audio embedding.
- We accept **lower coherence signal quality** from immature modalities to preserve **extensibility**. CLAP audio embeddings are less reliable than CLIP image embeddings. We handle this via confidence weights, not by excluding the modality.
- We accept **storage cost** (URIs in object storage, embeddings in graph) to preserve **the invariant that no binary data ever enters FalkorDB**.

## SUCCESS SIGNALS (observable)

- A node with audio, image, and text attachments participates in coherence computation using all three modalities.
- Adding a hypothetical "tactile" modality requires only: (1) a new embedding model adapter, (2) a weight constant, (3) populating `media.tactile` on relevant nodes. Zero schema changes.
- Nodes with missing modality embeddings compute coherence correctly using available modalities with redistributed weights.
- Legacy `image_uri` / `image_embedding` fields read correctly via the backward compatibility shim.
- No binary blob (base64 image, raw audio bytes) ever appears in a FalkorDB node property.

---

<!-- @mind:todo Define the initial set of modality confidence weights for v1 (text, image, audio). Need empirical calibration once CLAP embeddings are available. -->
