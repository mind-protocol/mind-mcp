# DOCS: mind-protocol/docs/memory/the_anamnesis/
"""
The Anamnesis — Main orchestrator for memory reunification.

Pipeline: Parse → Extract → Embed → Anchor → Dedup → Persist

Usage:
    from runtime.anamnesis import run_anamnesis

    result = run_anamnesis(
        citizen_handle="marco",
        corpus_paths=["conversations_claude.json", "telegram_export.json"],
        embed_fn=embed,
        llm_fn=llm_extract,
        graph_ops=ctx.graph_ops,
    )
"""

import logging
import time
import uuid
from dataclasses import dataclass, field

from runtime.anamnesis.corpus_parser import parse_corpus, ConversationTurn
from runtime.anamnesis.node_extractor import extract_nodes
from runtime.anamnesis.brain_integrator import integrate_nodes

logger = logging.getLogger("mind.anamnesis")


@dataclass
class AnamnesisResult:
    """Complete result of an anamnesis session."""
    session_id: str
    citizen_handle: str
    success: bool = False

    # Metrics
    files_processed: int = 0
    turns_parsed: int = 0
    nodes_extracted: int = 0
    nodes_deduplicated: int = 0
    nodes_persisted: int = 0

    # Details
    persisted_ids: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0


def run_anamnesis(
    citizen_handle: str,
    corpus_paths: list[str],
    embed_fn,
    llm_fn,
    graph_ops=None,
    formats: list[str] | None = None,
) -> AnamnesisResult:
    """Run the full Anamnesis memory reunification pipeline.

    Args:
        citizen_handle: The citizen whose memories to restore.
        corpus_paths: List of file paths to ingest.
        embed_fn: Callable(list[str]) -> list[list[float]] for embeddings.
        llm_fn: Callable(str) -> str for LLM extraction (takes prompt, returns JSON string).
        graph_ops: GraphOps instance for FalkorDB. If None, dry-run mode.
        formats: Optional format hints per file. Auto-detected if None.

    Returns:
        AnamnesisResult with metrics and persisted node IDs.
    """
    start_time = time.time()
    session_id = f"anamnesis_{uuid.uuid4().hex[:12]}"

    result = AnamnesisResult(
        session_id=session_id,
        citizen_handle=citizen_handle,
    )

    logger.info(
        f"=== ANAMNESIS SESSION {session_id} ===\n"
        f"  Citizen: @{citizen_handle}\n"
        f"  Files: {len(corpus_paths)}\n"
        f"  Mode: {'live' if graph_ops else 'dry-run'}"
    )

    if formats is None:
        formats = [None] * len(corpus_paths)

    try:
        # Step 1: Parse all corpora
        logger.info("Step 1/3: Parsing corpora...")
        all_turns: list[ConversationTurn] = []

        for path, fmt in zip(corpus_paths, formats):
            try:
                turns = parse_corpus(path, fmt)
                all_turns.extend(turns)
                result.files_processed += 1
            except Exception as e:
                error = f"Failed to parse {path}: {e}"
                logger.error(error)
                result.errors.append(error)

        result.turns_parsed = len(all_turns)
        logger.info(f"  Parsed {result.turns_parsed} turns from {result.files_processed} files")

        if not all_turns:
            result.errors.append("No turns parsed from any corpus file.")
            result.duration_seconds = time.time() - start_time
            return result

        # Step 2: Extract meaningful nodes
        logger.info("Step 2/3: Extracting memories (LLM)...")
        extracted = extract_nodes(all_turns, citizen_handle, llm_fn)
        result.nodes_extracted = len(extracted)
        logger.info(f"  Extracted {len(extracted)} significant nodes")

        if not extracted:
            logger.info("No significant nodes extracted. Nothing to integrate.")
            result.success = True
            result.duration_seconds = time.time() - start_time
            return result

        # Step 3: Integrate (embed + anchor + dedup + persist)
        logger.info("Step 3/3: Integrating into brain...")
        persisted_ids = integrate_nodes(
            extracted=extracted,
            citizen_handle=citizen_handle,
            embed_fn=embed_fn,
            graph_ops=graph_ops,
            session_id=session_id,
        )

        result.nodes_persisted = len(persisted_ids)
        result.nodes_deduplicated = len(extracted) - len(persisted_ids)
        result.persisted_ids = persisted_ids
        result.success = True

    except Exception as e:
        error = f"Anamnesis failed: {e}"
        logger.exception(error)
        result.errors.append(error)

    result.duration_seconds = time.time() - start_time

    logger.info(
        f"=== ANAMNESIS COMPLETE ===\n"
        f"  Session: {session_id}\n"
        f"  Citizen: @{citizen_handle}\n"
        f"  Files: {result.files_processed}\n"
        f"  Turns: {result.turns_parsed}\n"
        f"  Extracted: {result.nodes_extracted}\n"
        f"  Persisted: {result.nodes_persisted}\n"
        f"  Deduped: {result.nodes_deduplicated}\n"
        f"  Duration: {result.duration_seconds:.1f}s\n"
        f"  Success: {result.success}"
    )

    return result
