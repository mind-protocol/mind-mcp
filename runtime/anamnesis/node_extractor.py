# DOCS: mind-protocol/docs/memory/the_anamnesis/ALGORITHM_The_Anamnesis.md (Step 2)
"""
Node Extractor — Identify meaningful memories from conversation turns.

Uses LLM to distinguish signal from noise. A 50-turn conversation
might produce 3 meaningful nodes. That's correct.
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Optional

from runtime.anamnesis.corpus_parser import ConversationTurn

logger = logging.getLogger("mind.anamnesis.extractor")

MIN_SIGNIFICANCE = 0.3
CHUNK_MAX_TURNS = 40
CHUNK_GAP_MINUTES = 30

VALID_NODE_TYPES = frozenset({
    "insight", "decision", "value", "relationship",
    "knowledge", "emotion", "commitment",
})

EXTRACTION_PROMPT = """You are extracting memories for @{citizen_handle}.
These are their own conversations — they lived these moments.

From the following conversation, extract significant nodes:
- Insights and realizations
- Decisions made
- Values expressed
- Relationships acknowledged or formed
- Knowledge gained or demonstrated
- Significant emotions experienced
- Commitments made

For each node, provide:
- content: the memory in 1-3 sentences (from the citizen's perspective, first person)
- type: insight | decision | value | relationship | knowledge | emotion | commitment
- significance: 0.0-1.0 (how important is this to the citizen's identity and growth)

Ignore: greetings, filler, acknowledgments, repetitions, small talk.
If nothing significant, return an empty array.

Return ONLY a JSON array. Example:
[{{"content": "I realized that...", "type": "insight", "significance": 0.7}}]

CONVERSATION ({source_platform}, {conversation_id}):
{conversation_text}"""


@dataclass
class ExtractedNode:
    """A meaningful memory extracted from conversations."""
    content: str
    node_type: str
    significance: float
    source_platform: str
    source_conversation: str
    timestamp: Optional[str] = None
    participants: list[str] = field(default_factory=list)


def extract_nodes(
    turns: list[ConversationTurn],
    citizen_handle: str,
    llm_fn,
) -> list[ExtractedNode]:
    """Extract meaningful nodes from conversation turns.

    Args:
        turns: Normalized conversation turns.
        citizen_handle: The citizen whose memories these are.
        llm_fn: Callable(prompt: str) -> str (returns JSON string).

    Returns:
        List of ExtractedNode with significance >= MIN_SIGNIFICANCE.
    """
    chunks = _batch_into_chunks(turns)
    logger.info(f"Batched {len(turns)} turns into {len(chunks)} chunks")

    all_nodes = []
    for i, chunk in enumerate(chunks):
        nodes = _extract_from_chunk(chunk, citizen_handle, llm_fn)
        all_nodes.extend(nodes)

        if (i + 1) % 10 == 0:
            logger.info(
                f"  Extracted from {i+1}/{len(chunks)} chunks "
                f"({len(all_nodes)} nodes so far)"
            )

    logger.info(
        f"Extraction complete: {len(all_nodes)} significant nodes "
        f"from {len(turns)} turns"
    )
    return all_nodes


def _batch_into_chunks(
    turns: list[ConversationTurn],
) -> list[list[ConversationTurn]]:
    """Group turns into conversation chunks by conversation_id."""
    groups: dict[str, list[ConversationTurn]] = {}

    for turn in turns:
        key = turn.conversation_id or turn.source_id
        if key not in groups:
            groups[key] = []
        groups[key].append(turn)

    # Split large conversations into sub-chunks
    chunks = []
    for conv_turns in groups.values():
        for i in range(0, len(conv_turns), CHUNK_MAX_TURNS):
            chunk = conv_turns[i:i + CHUNK_MAX_TURNS]
            if chunk:
                chunks.append(chunk)

    return chunks


def _extract_from_chunk(
    chunk: list[ConversationTurn],
    citizen_handle: str,
    llm_fn,
) -> list[ExtractedNode]:
    """Extract nodes from a single conversation chunk."""
    # Build conversation text
    lines = []
    for turn in chunk:
        prefix = turn.speaker
        lines.append(f"[{prefix}]: {turn.content[:500]}")

    conversation_text = "\n".join(lines)

    # Get metadata from first turn
    source_platform = chunk[0].source_platform
    conversation_id = chunk[0].conversation_id
    timestamp = chunk[0].timestamp
    participants = list(set(t.speaker for t in chunk))

    prompt = EXTRACTION_PROMPT.format(
        citizen_handle=citizen_handle,
        source_platform=source_platform,
        conversation_id=conversation_id,
        conversation_text=conversation_text,
    )

    try:
        response = llm_fn(prompt)

        # Parse JSON response
        raw_nodes = _parse_llm_response(response)

        nodes = []
        for raw in raw_nodes:
            content = raw.get("content", "").strip()
            node_type = raw.get("type", "knowledge")
            significance = float(raw.get("significance", 0.5))

            if not content:
                continue
            if node_type not in VALID_NODE_TYPES:
                node_type = "knowledge"
            if significance < MIN_SIGNIFICANCE:
                continue

            nodes.append(ExtractedNode(
                content=content,
                node_type=node_type,
                significance=min(1.0, max(0.0, significance)),
                source_platform=source_platform,
                source_conversation=conversation_id,
                timestamp=timestamp,
                participants=participants,
            ))

        return nodes

    except Exception as e:
        logger.warning(f"Extraction failed for chunk ({conversation_id}): {e}")
        return []


def _parse_llm_response(response: str) -> list[dict]:
    """Parse JSON array from LLM response, handling common formatting issues."""
    text = response.strip()

    # Strip markdown code fences
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    # Handle "json" prefix from code fences
    if text.startswith("json"):
        text = text[4:].strip()

    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return parsed
        if isinstance(parsed, dict):
            return [parsed]
        return []
    except json.JSONDecodeError:
        # Try to find JSON array in the response
        match = text.find("[")
        if match >= 0:
            end = text.rfind("]")
            if end > match:
                try:
                    return json.loads(text[match:end + 1])
                except json.JSONDecodeError:
                    pass
        return []
