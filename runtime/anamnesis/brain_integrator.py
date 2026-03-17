# DOCS: mind-protocol/docs/memory/the_anamnesis/ALGORITHM_The_Anamnesis.md (Steps 3-6)
"""
Brain Integrator — Embed, anchor, deduplicate, and persist memories.

Takes extracted nodes and integrates them into the citizen's L1 brain graph.
Handles the full embed → anchor → dedup → persist pipeline.
"""

import hashlib
import logging
import time
from dataclasses import dataclass, field

import numpy as np

from runtime.anamnesis.node_extractor import ExtractedNode

logger = logging.getLogger("mind.anamnesis.integrator")

DEDUP_THRESHOLD = 0.92
ANCHOR_MIN_SIMILARITY = 0.3
ANCHOR_TOP_K = 3


@dataclass
class AnchorLink:
    """Link from a new memory to an existing brain node."""
    target_id: str
    similarity: float
    link_type: str  # reinforces, associates, contextualizes


@dataclass
class IntegratedNode:
    """A memory ready for persistence."""
    content: str
    embedding: np.ndarray
    node_type: str
    significance: float
    source_platform: str
    source_conversation: str
    timestamp: str | None
    participants: list[str]
    anchor_links: list[AnchorLink] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)

    def add_source(self, platform: str, conversation: str):
        source = f"{platform}:{conversation}"
        if source not in self.sources:
            self.sources.append(source)


def integrate_nodes(
    extracted: list[ExtractedNode],
    citizen_handle: str,
    embed_fn,
    graph_ops=None,
    session_id: str = "",
) -> list[str]:
    """Full integration pipeline: embed → anchor → dedup → persist.

    Args:
        extracted: Nodes from the extractor.
        citizen_handle: Target citizen.
        embed_fn: Callable(list[str]) -> list[list[float]].
        graph_ops: GraphOps for FalkorDB. If None, returns node IDs only.
        session_id: Identifier for this anamnesis session.

    Returns:
        List of persisted node IDs.
    """
    if not extracted:
        logger.info("No nodes to integrate.")
        return []

    # Step 3: Embed
    logger.info(f"Embedding {len(extracted)} nodes...")
    integrated = _embed_nodes(extracted, embed_fn)

    # Step 4: Anchor to existing brain
    logger.info(f"Anchoring to brain_{citizen_handle}...")
    existing_brain = _get_existing_brain(citizen_handle, graph_ops)
    _anchor_nodes(integrated, existing_brain)

    # Step 5: Deduplicate
    logger.info("Deduplicating...")
    existing_memories = [
        n for n in existing_brain
        if n.get("type") == "moment" or n.get("memory_type")
    ]
    unique = _deduplicate(integrated, existing_memories)
    duped = len(integrated) - len(unique)
    logger.info(f"Dedup: {duped} duplicates removed, {len(unique)} unique nodes remain")

    # Step 6: Persist
    logger.info(f"Persisting {len(unique)} nodes to brain_{citizen_handle}...")
    written = _persist(unique, citizen_handle, session_id, graph_ops)

    logger.info(
        f"Integration complete: {len(written)} nodes written to brain_{citizen_handle}"
    )
    return written


def _embed_nodes(
    extracted: list[ExtractedNode],
    embed_fn,
) -> list[IntegratedNode]:
    """Embed all extracted nodes."""
    texts = [n.content for n in extracted]

    # Batch embed
    embeddings_raw = embed_fn(texts)

    integrated = []
    for node, emb in zip(extracted, embeddings_raw):
        emb_arr = np.array(emb, dtype=np.float64)
        if np.linalg.norm(emb_arr) < 0.05:
            logger.debug(f"Skipping low-magnitude node: {node.content[:50]}")
            continue

        inode = IntegratedNode(
            content=node.content,
            embedding=emb_arr,
            node_type=node.node_type,
            significance=node.significance,
            source_platform=node.source_platform,
            source_conversation=node.source_conversation,
            timestamp=node.timestamp,
            participants=node.participants,
        )
        inode.add_source(node.source_platform, node.source_conversation)
        integrated.append(inode)

    return integrated


def _get_existing_brain(citizen_handle: str, graph_ops) -> list[dict]:
    """Get existing brain nodes for anchoring and dedup."""
    if graph_ops is None:
        return []

    try:
        return graph_ops.get_all_nodes(graph_name=f"brain_{citizen_handle}")
    except Exception as e:
        logger.warning(f"Could not read brain_{citizen_handle}: {e}")
        return []


def _anchor_nodes(
    nodes: list[IntegratedNode],
    brain_nodes: list[dict],
):
    """Find nearest existing brain nodes and create anchor links."""
    if not brain_nodes:
        return

    # Pre-compute brain embeddings
    brain_with_emb = []
    for bn in brain_nodes:
        emb = bn.get("embedding")
        if emb and len(emb) > 0:
            brain_with_emb.append((bn.get("id", ""), np.array(emb, dtype=np.float64)))

    if not brain_with_emb:
        return

    for node in nodes:
        similarities = []
        for brain_id, brain_emb in brain_with_emb:
            sim = _cosine_similarity(node.embedding, brain_emb)
            if sim >= ANCHOR_MIN_SIMILARITY:
                similarities.append((brain_id, sim))

        similarities.sort(key=lambda x: x[1], reverse=True)

        for brain_id, sim in similarities[:ANCHOR_TOP_K]:
            if sim > 0.8:
                link_type = "reinforces"
            elif sim > 0.5:
                link_type = "associates"
            else:
                link_type = "contextualizes"

            node.anchor_links.append(AnchorLink(
                target_id=brain_id,
                similarity=sim,
                link_type=link_type,
            ))


def _deduplicate(
    new_nodes: list[IntegratedNode],
    existing_memories: list[dict],
) -> list[IntegratedNode]:
    """Remove duplicates against existing brain and within the batch."""
    # Pre-compute existing memory embeddings
    existing_embs = []
    for mem in existing_memories:
        emb = mem.get("embedding")
        if emb and len(emb) > 0:
            existing_embs.append(np.array(emb, dtype=np.float64))

    unique = []
    for node in new_nodes:
        is_dup = False

        # Check against existing memories
        for ex_emb in existing_embs:
            if _cosine_similarity(node.embedding, ex_emb) > DEDUP_THRESHOLD:
                is_dup = True
                break

        # Check against already-accepted new nodes
        if not is_dup:
            for accepted in unique:
                if _cosine_similarity(node.embedding, accepted.embedding) > DEDUP_THRESHOLD:
                    is_dup = True
                    # Merge provenance
                    for src in node.sources:
                        if src not in accepted.sources:
                            accepted.sources.append(src)
                    break

        if not is_dup:
            unique.append(node)

    return unique


def _persist(
    nodes: list[IntegratedNode],
    citizen_handle: str,
    session_id: str,
    graph_ops,
) -> list[str]:
    """Write nodes and links to FalkorDB brain graph."""
    written = []
    graph_name = f"brain_{citizen_handle}"

    for node in nodes:
        content_hash = hashlib.md5(node.content.encode()).hexdigest()[:8]
        node_id = f"memory:{citizen_handle}_{content_hash}"

        if graph_ops is not None:
            try:
                graph_ops.create_node(
                    graph_name=graph_name,
                    node_id=node_id,
                    node_type="moment",
                    name=node.content[:60],
                    content=node.content,
                    synthesis=f"Memory ({node.node_type}) via anamnesis",
                    embedding=node.embedding.tolist(),
                    properties={
                        "weight": node.significance,
                        "energy": 0.1,
                        "stability": 0.3,
                        "memory_type": node.node_type,
                        "source_platform": node.source_platform,
                        "source_conversation": node.source_conversation,
                        "timestamp": node.timestamp or "",
                        "participants": ",".join(node.participants),
                        "sources": ",".join(node.sources),
                        "anamnesis_session": session_id,
                    },
                )

                # Create anchor links
                for link in node.anchor_links:
                    link_id = f"anamnesis:{content_hash}_{link.target_id[-8:]}"
                    graph_ops.create_link(
                        graph_name=graph_name,
                        link_id=link_id,
                        source_id=node_id,
                        target_id=link.target_id,
                        properties={
                            "type": link.link_type,
                            "weight": link.similarity,
                            "permanence": 0.6,
                        },
                    )
            except Exception as e:
                logger.error(f"Failed to persist {node_id}: {e}")
                continue

        written.append(node_id)

    return written


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two vectors."""
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))
