# DOCS: mind-protocol/docs/memory/the_anamnesis/ALGORITHM_The_Anamnesis.md (Step 1)
"""
Corpus Parser — Normalize conversation exports into uniform turns.

Supports: Claude JSON, Telegram JSON, WhatsApp TXT, Discord JSON,
system prompts (markdown), raw markdown files.
"""

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger("mind.anamnesis.parser")


@dataclass
class ConversationTurn:
    """A single turn in a conversation."""
    speaker: str                      # "human", "assistant", or name
    content: str
    timestamp: Optional[str] = None   # ISO-8601 if available
    source_id: str = ""               # hash of source file
    source_platform: str = ""         # claude, telegram, whatsapp, etc.
    conversation_id: str = ""         # groups turns into conversations


def parse_corpus(file_path: str, format: str | None = None) -> list[ConversationTurn]:
    """Parse a corpus file into normalized conversation turns.

    Args:
        file_path: Path to the corpus file.
        format: One of claude, telegram, whatsapp, discord, system_prompt, markdown.
                Auto-detected if None.

    Returns:
        List of ConversationTurn.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Corpus file not found: {file_path}")

    if format is None:
        format = _detect_format(path)

    source_id = f"{path.name}_{hash(str(path)) & 0xFFFFFFFF:08x}"

    parsers = {
        "claude": _parse_claude,
        "telegram": _parse_telegram,
        "whatsapp": _parse_whatsapp,
        "discord": _parse_discord,
        "system_prompt": _parse_system_prompt,
        "markdown": _parse_markdown,
    }

    parser = parsers.get(format)
    if not parser:
        raise ValueError(f"Unknown format: {format}. Supported: {list(parsers.keys())}")

    turns = parser(path, source_id)
    logger.info(f"Parsed {len(turns)} turns from {path.name} (format: {format})")
    return turns


def _detect_format(path: Path) -> str:
    """Auto-detect corpus format from file content."""
    suffix = path.suffix.lower()

    if suffix == ".json":
        try:
            with open(path) as f:
                data = json.load(f)

            # Claude export
            if isinstance(data, list) and data and "chat_messages" in data[0]:
                return "claude"
            if isinstance(data, dict) and "chat_messages" in data:
                return "claude"

            # Telegram export
            if isinstance(data, dict) and "messages" in data:
                msgs = data["messages"]
                if msgs and isinstance(msgs[0], dict) and "from" in msgs[0]:
                    return "telegram"

            # Discord export
            if isinstance(data, dict) and "messages" in data:
                msgs = data["messages"]
                if msgs and isinstance(msgs[0], dict) and "author" in msgs[0]:
                    return "discord"

            return "claude"  # default for JSON
        except (json.JSONDecodeError, IndexError, KeyError):
            return "markdown"

    if suffix == ".txt":
        with open(path) as f:
            first_line = f.readline()
        # WhatsApp pattern: [DD/MM/YYYY, HH:MM:SS] or MM/DD/YYYY
        if re.match(r"\[?\d{1,2}/\d{1,2}/\d{2,4}", first_line):
            return "whatsapp"
        return "markdown"

    if suffix == ".md":
        with open(path) as f:
            first_lines = f.read(200)
        if first_lines.startswith("---"):
            return "system_prompt"
        return "markdown"

    return "markdown"


def _parse_claude(path: Path, source_id: str) -> list[ConversationTurn]:
    """Parse Claude conversation export (JSON)."""
    with open(path) as f:
        data = json.load(f)

    conversations = data if isinstance(data, list) else [data]
    turns = []

    for conv in conversations:
        conv_id = conv.get("uuid", conv.get("id", source_id))
        conv_name = conv.get("name", "")
        messages = conv.get("chat_messages", [])

        for msg in messages:
            sender = msg.get("sender", "unknown")
            # Claude exports use "human" and "assistant"
            speaker = "human" if sender == "human" else "assistant"

            # Content can be in different places depending on export version
            content = ""
            if isinstance(msg.get("text"), str):
                content = msg["text"]
            elif isinstance(msg.get("content"), str):
                content = msg["content"]
            elif isinstance(msg.get("content"), list):
                # Multi-part content (text blocks)
                parts = [
                    p.get("text", "") for p in msg["content"]
                    if isinstance(p, dict) and p.get("type") == "text"
                ]
                content = "\n".join(parts)

            if not content.strip():
                continue

            turns.append(ConversationTurn(
                speaker=speaker,
                content=content.strip(),
                timestamp=msg.get("created_at", msg.get("updated_at")),
                source_id=source_id,
                source_platform="claude",
                conversation_id=str(conv_id),
            ))

    return turns


def _parse_telegram(path: Path, source_id: str) -> list[ConversationTurn]:
    """Parse Telegram data export (JSON)."""
    with open(path) as f:
        data = json.load(f)

    messages = data.get("messages", [])
    turns = []

    for msg in messages:
        if msg.get("type") != "message":
            continue

        speaker = msg.get("from", msg.get("actor", "unknown"))
        text_parts = msg.get("text", "")

        # Telegram text can be a string or a list of text entities
        if isinstance(text_parts, list):
            content = "".join(
                p if isinstance(p, str) else p.get("text", "")
                for p in text_parts
            )
        else:
            content = str(text_parts)

        if not content.strip():
            continue

        turns.append(ConversationTurn(
            speaker=speaker,
            content=content.strip(),
            timestamp=msg.get("date"),
            source_id=source_id,
            source_platform="telegram",
            conversation_id=data.get("id", source_id),
        ))

    return turns


def _parse_whatsapp(path: Path, source_id: str) -> list[ConversationTurn]:
    """Parse WhatsApp chat export (TXT)."""
    turns = []
    # Pattern: [DD/MM/YYYY, HH:MM:SS] Speaker: Message
    # or: MM/DD/YY, HH:MM - Speaker: Message
    pattern = re.compile(
        r"\[?(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?)\]?\s*[-–]?\s*"
        r"([^:]+):\s*(.*)"
    )

    with open(path, encoding="utf-8", errors="replace") as f:
        current_turn = None
        for line in f:
            match = pattern.match(line.strip())
            if match:
                if current_turn and current_turn.content.strip():
                    turns.append(current_turn)

                date_str, time_str, speaker, content = match.groups()
                current_turn = ConversationTurn(
                    speaker=speaker.strip(),
                    content=content.strip(),
                    timestamp=f"{date_str} {time_str}",
                    source_id=source_id,
                    source_platform="whatsapp",
                    conversation_id=source_id,
                )
            elif current_turn:
                # Continuation of previous message
                current_turn.content += "\n" + line.strip()

        if current_turn and current_turn.content.strip():
            turns.append(current_turn)

    return turns


def _parse_discord(path: Path, source_id: str) -> list[ConversationTurn]:
    """Parse Discord chat export (DiscordChatExporter JSON)."""
    with open(path) as f:
        data = json.load(f)

    messages = data.get("messages", [])
    channel_name = data.get("channel", {}).get("name", source_id)
    turns = []

    for msg in messages:
        author = msg.get("author", {})
        speaker = author.get("name", author.get("nickname", "unknown"))
        content = msg.get("content", "")

        if not content.strip():
            continue

        turns.append(ConversationTurn(
            speaker=speaker,
            content=content.strip(),
            timestamp=msg.get("timestamp"),
            source_id=source_id,
            source_platform="discord",
            conversation_id=channel_name,
        ))

    return turns


def _parse_system_prompt(path: Path, source_id: str) -> list[ConversationTurn]:
    """Parse a system prompt as a single declaration turn."""
    content = path.read_text(encoding="utf-8", errors="replace")

    # Strip YAML frontmatter if present
    if content.startswith("---"):
        end = content.find("---", 3)
        if end > 0:
            content = content[end + 3:].strip()

    return [ConversationTurn(
        speaker="system",
        content=content,
        source_id=source_id,
        source_platform="system_prompt",
        conversation_id=f"prompt_{path.stem}",
    )]


def _parse_markdown(path: Path, source_id: str) -> list[ConversationTurn]:
    """Parse a raw markdown file as content sections."""
    content = path.read_text(encoding="utf-8", errors="replace")

    # Split by H2 headers
    sections = re.split(r"\n## ", content)
    turns = []

    for i, section in enumerate(sections):
        text = section.strip()
        if not text or len(text) < 20:
            continue

        if i > 0:
            text = "## " + text  # restore header

        turns.append(ConversationTurn(
            speaker="author",
            content=text,
            source_id=source_id,
            source_platform="markdown",
            conversation_id=f"doc_{path.stem}",
        ))

    return turns
