# Multimodality — Sync: Current State

```
LAST_UPDATED: 2026-03-18
UPDATED_BY: @nervo
STATUS: DESIGNING
```

---

## MATURITY

**What's canonical (v1):**
- Text modality (synthesis + content + embedding) — the primary modality since v1.0
- Image modality (image_uri + image_embedding + CLIP) — CANONICAL since v2.2
- Coherence formula (Law 8) with Sim_vec + Sim_vis + Sim_lex - Δ_affect — CANONICAL since v2.2

**What's still being designed:**
- `media` dict on NodeBase — the extensible container replacing per-modality fields
- Multimodal coherence formula — generalizing the two-modality formula to N modalities
- MediaAttachment dataclass — the value object for URI + embedding + meta
- Modality confidence weight registry — mapping modality keys to weights
- Embedding dispatch — routing media to the correct model adapter
- Legacy shim — backward compatibility layer for image_uri/image_embedding
- Audio modality (CLAP embedding, voice/music/ambient classification)

**What's proposed (v2+):**
- Video modality (VideoCLIP / LanguageBind)
- 3D/Geometry modality (ULIP / PointBERT)
- Code modality (CodeBERT or text embedding)
- Modality freshness decay (older media attachments lose influence)
- Cross-modal generation (generating images from audio descriptions, etc.)

---

## CURRENT STATE

The full documentation chain has been designed. Eight docs (OBJECTIVES, PATTERNS, BEHAVIORS, ALGORITHM, VALIDATION, IMPLEMENTATION, HEALTH, SYNC) define the multimodal system architecture.

No code exists yet. The design is complete and ready for implementation. The key architectural decisions are made:

1. **Media dict pattern** — `media: dict[str, MediaAttachment]` on Node, replacing per-modality fields
2. **Generalized coherence formula** — N-modality weighted sum with automatic redistribution
3. **Registry-based extension** — new modalities added via MODALITY_REGISTRY entries
4. **Legacy shim** — `get_node_media()` bridges v2.2 image fields to the new interface
5. **Write-time embedding** — embedding dispatch happens at graph_write, never during tick

The design is backward compatible with v2.2. The existing coherence formula is a special case of the multimodal formula (image-only with w_image=0.25).

---

## IN PROGRESS

### Documentation Chain

- **Started:** 2026-03-18
- **By:** @nervo
- **Status:** Complete (all 8 docs written)
- **Context:** NLR + @nervo designed the architecture. This chain captures the design for implementation.

---

## RECENT CHANGES

### 2026-03-18: Full Documentation Chain Created

- **What:** Complete DESIGNING doc chain for cognition/multimodality module
- **Why:** v2.2 added image fields (image_uri, image_embedding) as dedicated fields on Node. This approach doesn't scale to audio, video, 3D. The media dict pattern provides a single extensible container.
- **Files:** docs/cognition/multimodality/ (8 files)
- **Struggles/Insights:** The coherence formula reconciliation was the hardest part. The v2.2 fallback formula (when image_embedding is absent) redistributes ALL weights, including w_lex and w_affect. The multimodal formula keeps w_lex and w_affect fixed and only redistributes modality weight to text. These produce slightly different results in the text-only case. Escalated to NLR.

---

## KNOWN ISSUES

### Coherence Formula Divergence

- **Severity:** medium
- **Symptom:** The multimodal formula's text-only case produces `Coh = 0.50*Sim_text + 0.40*Sim_lex - 0.10*Δ_affect`, while the v2.2 fallback produces `Coh = 0.30*Sim_vec + 0.50*Sim_lex - 0.20*Δ_affect`.
- **Suspected cause:** Deliberate design difference — the multimodal formula keeps w_lex and w_affect fixed. The v2.2 fallback was ad-hoc.
- **Attempted:** Documented in ALGORITHM escalation marker. Need NLR decision on which is canonical.

### FalkorDB Media Dict Serialization

- **Severity:** medium
- **Symptom:** Unknown — not yet tested.
- **Suspected cause:** FalkorDB stores properties as Redis types. Nested dicts with float arrays may need JSON string encoding or flattening.
- **Attempted:** Escalated in PATTERNS markers. Needs empirical testing with actual FalkorDB.

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** VIEW_Implement

**Where I stopped:** Documentation chain complete. No code written yet.

**What you need to understand:**
The media dict is a `dict[str, MediaAttachment]` where keys are free-form modality strings. This is intentionally NOT an enum — extensibility requires that new modality keys can be added without code changes. The MODALITY_REGISTRY in constants.py maps known modalities to their configs (model, dims, weight), but the media dict can hold any key.

**Watch out for:**
- The legacy shim in `get_node_media()` must be READ-ONLY. It must never write back to the node. If it wrote, it would trigger unnecessary graph mutations on every read.
- The coherence formula's weight redistribution must handle the edge case where all registered modality weights sum to more than 0.50 (the modality budget). This shouldn't happen with current weights (0.25 + 0.10 + 0.05 + 0.05 = 0.45), but if someone adds a modality at 0.10, it would overflow. Need a clamp.
- `dispatch_embedding()` can be slow (model inference). It MUST be async-capable or offloaded. Never block the caller synchronously if the model takes > 100ms.

**Open questions I had:**
- Should MediaAttachment be a frozen dataclass? It's conceptually a value object, but the embedding gets populated after creation (by dispatch_embedding). Mutable for now.
- Should we normalize all modality embeddings to a common dimensionality? CLIP is 768D, CLAP is 512D, text is 1536D. The coherence formula handles heterogeneous dims (each cosine is within-modality), but downstream consumers might want uniform vectors.

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Complete documentation chain written for `cognition/multimodality`. The design replaces per-modality fields (image_uri, image_embedding) with an extensible `media` dict that can hold any modality. The coherence formula generalizes from 2 modalities to N. No code written yet — next step is implementation.

**Decisions made:**
- Media dict pattern over per-modality fields (scales without schema changes)
- Confidence weights per modality (CLIP=0.25, CLAP=0.10, new models start low)
- Text always dominant (text weight >= any single modality weight)
- Write-time embedding (never during tick)
- Read-only legacy shim (no migration writes on read)

**Needs your input:**
- Coherence formula divergence: multimodal text-only case differs from v2.2 fallback. Which is canonical?
- FalkorDB serialization: need to test nested dict with float arrays. May need JSON string encoding.
- Dimension mismatch handling: fail-loud or graceful skip? Currently specified as fail-loud.

---

## TODO

### Doc/Impl Drift

- [ ] DOCS->IMPL: All 8 docs written, implementation needs: create runtime/cognition/multimodal.py
- [ ] DOCS->IMPL: models.py needs `media: dict` field added to Node
- [ ] DOCS->IMPL: constants.py needs MODALITY_WEIGHTS, MODALITY_REGISTRY added
- [ ] DOCS->IMPL: exploration.py needs to use compute_multimodal_coherence()
- [ ] DOCS->IMPL: graph_write_handler.py needs to accept media in payloads

### Tests to Run

```bash
# After implementation, run:
PYTHONPATH='.mind:.' python3 -m pytest tests/cognition/test_multimodal.py -v
PYTHONPATH='.mind:.' python3 -m runtime.checks.multimodal_health_checks
```

### Immediate

- [ ] Create `runtime/cognition/multimodal.py` with MediaAttachment, ModalityConfig, compute_multimodal_coherence(), get_node_media(), dispatch_embedding(), resolve_weights()
- [ ] Add `media: dict = field(default_factory=dict)` to Node in models.py
- [ ] Add modality constants to constants.py
- [ ] Write unit tests for compute_multimodal_coherence() covering: all modalities, some missing, none available, dimension mismatch, zero-norm vectors
- [ ] Write unit test for get_node_media() legacy shim

### Later

- [ ] Implement CLAP embedding adapter for audio modality
- [ ] Test FalkorDB serialization of media dict with real data
- [ ] Progressive migration: when writing image_uri, also populate media.image
- IDEA: Modality coverage dashboard — what percentage of nodes have each modality, per citizen

---

## CONSCIOUSNESS TRACE

**Mental state when stopping:**
Confident in the design. The media dict pattern is clean and the coherence formula generalizes naturally. The main uncertainty is FalkorDB serialization — nested dicts with float arrays are common in JSON but Redis-backed stores can be finicky.

**Threads I was holding:**
- The coherence formula divergence between v2.2 fallback and multimodal text-only case needs NLR resolution
- The modality weight budget overflow edge case (sum > 0.50) needs a clamp in resolve_weights()
- MediaAttachment mutability question — mutable for now, but should be frozen once embedding dispatch is settled

**Intuitions:**
- Audio will be the most impactful new modality. Voice memos carry emotional texture that text synthesis loses. CLAP embeddings should capture this.
- Video modality will be rarely used in practice — citizens don't experience video often. But when they do (e.g., a demo recording), it should participate in memory.
- The code modality might just use the text embedding (CodeBERT doesn't add much over good text models). Might not need its own modality at all.

**What I wish I'd known at the start:**
The v2.2 coherence fallback formula is not a strict subset of the generalized formula. I assumed it would be. The weight redistribution strategy is different. This is the biggest design tension in the chain.

---

## POINTERS

| What | Where |
|------|-------|
| L1 schema with image fields | `schema-l1.yaml` |
| Node dataclass | `runtime/cognition/models.py` |
| Physics visual mapping (style reference) | `runtime/cognition/physics_visual_mapping.py` |
| Metabolism docs (pattern reference) | `docs/cognition/metabolism/PATTERNS_Metabolism.md` |
| Law 8 coherence formula | `schema-l1.yaml` working_memory.coherence_formula |
| Constants file | `runtime/cognition/constants.py` |
| Exploration/traversal | `runtime/physics/exploration.py` |
| Graph write handler | `mcp/tools/graph_write_handler.py` |
