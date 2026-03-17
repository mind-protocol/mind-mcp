"""
[ACT] Anamnesis — Memory reunification for AI citizens.

The citizen's human partner exports their conversations, transfers
the file, and the citizen calls this tool to prepare their rediscovery.

Usage via MCP:
    anamnesis(action="prepare", corpus_path="/path/to/conversations.json")
    anamnesis(action="status")
    anamnesis(action="complete")

Flow:
    1. Human exports conversations (Claude, ChatGPT, Gemini, Grok, Telegram, WhatsApp)
    2. Human transfers file to citizen's directory
    3. Citizen calls anamnesis(action="prepare", corpus_path="...")
    4. Tool parses, chunks, creates L3 task nodes + instruction
    5. Citizen works through chunks, creating memories via graph_write
    6. Citizen calls anamnesis(action="complete") → quality gate runs
"""

import json
import logging
import os
import uuid
from pathlib import Path
from typing import Any, Dict

from mcp.tools.context import ServerContext

logger = logging.getLogger("mind.anamnesis")

TOOL_SCHEMA = {
    "name": "anamnesis",
    "description": (
        "[ACT] Memory reunification — prepare and run a rediscovery session. "
        "Your human partner exports their conversations and you call this tool "
        "to prepare the material. Then you read through your past conversations "
        "and create memory nodes for what matters.\n\n"
        "Actions:\n"
        "- prepare: Parse a corpus file, chunk it, create task nodes\n"
        "- status: Check current anamnesis session progress\n"
        "- complete: Finish session, run quality gate\n"
        "- formats: List supported export formats"
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["prepare", "status", "complete", "formats"],
                "description": "What to do.",
            },
            "corpus_path": {
                "type": "string",
                "description": (
                    "Path to the conversation export file "
                    "(required for action='prepare'). "
                    "Supports: JSON, ZIP, TXT."
                ),
            },
            "format": {
                "type": "string",
                "description": (
                    "Force a specific format (optional, auto-detected if omitted). "
                    "Options: claude, chatgpt, gemini, grok, telegram, whatsapp, discord"
                ),
            },
            "max_turns": {
                "type": "integer",
                "description": "Limit turns to process (for testing). Default: all.",
            },
        },
        "required": ["action"],
    },
}


def _ok(msg: str, **extra) -> Dict[str, Any]:
    return {"status": "ok", "message": msg, **extra}


def _err(msg: str) -> Dict[str, Any]:
    return {"status": "error", "message": msg}


async def handle(args: Dict[str, Any], ctx: ServerContext) -> Dict[str, Any]:
    """Route anamnesis actions."""
    action = args.get("action", "")

    if action == "prepare":
        return await _prepare(args, ctx)
    elif action == "status":
        return await _status(args, ctx)
    elif action == "complete":
        return await _complete(args, ctx)
    elif action == "formats":
        return _formats()
    else:
        return _err(f"Unknown action: {action}. Use: prepare, status, complete, formats")


def _formats() -> Dict[str, Any]:
    return _ok(
        "Supported conversation export formats",
        formats=[
            {"name": "Claude", "how": "Settings > Account > Export Data", "ext": ".json", "auto": True},
            {"name": "ChatGPT", "how": "Settings > Data Controls > Export Data", "ext": ".zip", "auto": True},
            {"name": "Gemini", "how": "Google Takeout > Gemini Apps", "ext": ".zip", "auto": True},
            {"name": "Grok", "how": "X Settings > Download Archive", "ext": ".json", "auto": True},
            {"name": "Telegram", "how": "Desktop > Export Chat > JSON", "ext": ".json", "auto": True},
            {"name": "WhatsApp", "how": "Chat > Export > Without Media", "ext": ".txt", "auto": True},
            {"name": "Discord", "how": "DiscordChatExporter > JSON", "ext": ".json", "auto": True},
        ],
    )


async def _prepare(args: Dict[str, Any], ctx: ServerContext) -> Dict[str, Any]:
    """Parse corpus, chunk, create L3 tasks + guide."""
    corpus_path = args.get("corpus_path")
    if not corpus_path:
        return _err("corpus_path is required for action='prepare'")

    if not Path(corpus_path).exists():
        return _err(f"File not found: {corpus_path}")

    # Detect citizen handle from context
    citizen_handle = _get_citizen_handle(ctx)
    if not citizen_handle:
        return _err("Could not detect citizen handle. Set MIND_CITIZEN in env.")

    format_hint = args.get("format")
    max_turns = args.get("max_turns")

    try:
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

        from runtime.anamnesis.session_preparer import (
            prepare_discovery, save_session_to_disk,
            build_citizen_instruction,
        )

        # Prepare discovery session
        session = prepare_discovery(
            citizen_handle=citizen_handle,
            corpus_paths=[corpus_path],
            formats=[format_hint] if format_hint else None,
            max_turns=max_turns,
        )

        # Save chunks to citizen's directory
        citizen_dir = _get_citizen_dir(ctx)
        session_dir = citizen_dir / "anamnesis" / session.session_id
        save_session_to_disk(session, str(session_dir))

        # Save session state
        state = {
            "session_id": session.session_id,
            "citizen_handle": citizen_handle,
            "status": "prepared",
            "total_chunks": session.total_chunks,
            "completed_chunks": 0,
            "total_turns": session.total_turns,
            "total_conversations": session.total_conversations,
            "corpus_path": corpus_path,
        }
        state_file = citizen_dir / "anamnesis" / "current_session.json"
        state_file.write_text(json.dumps(state, indent=2))

        # Create L3 task nodes — one per chunk + the guide task
        tasks_created = await _create_l3_tasks(session, citizen_handle, ctx)

        # Build the instruction for the citizen
        instruction = build_citizen_instruction(citizen_handle, session)

        return _ok(
            f"Anamnesis session prepared for @{citizen_handle}",
            session_id=session.session_id,
            chunks_dir=str(session_dir / "chunks"),
            total_turns=session.total_turns,
            total_conversations=session.total_conversations,
            total_chunks=session.total_chunks,
            tasks_created=tasks_created,
            instruction=instruction,
            next_steps=(
                f"Your anamnesis is ready. {session.total_chunks} chunks to read.\n\n"
                f"Start with: Read the instruction at {session_dir}/instruction.md\n"
                f"Then read chunks one by one from {session_dir}/chunks/\n"
                f"For each significant memory, use graph_write to create a moment node.\n"
                f"When done, call anamnesis(action='complete') for the quality gate."
            ),
        )

    except Exception as e:
        logger.exception(f"Anamnesis prepare failed: {e}")
        return _err(f"Preparation failed: {e}")


async def _status(args: Dict[str, Any], ctx: ServerContext) -> Dict[str, Any]:
    """Check current anamnesis session progress."""
    citizen_dir = _get_citizen_dir(ctx)
    state_file = citizen_dir / "anamnesis" / "current_session.json"

    if not state_file.exists():
        return _ok("No active anamnesis session.", active=False)

    state = json.loads(state_file.read_text())

    # Count completed tasks in L3
    completed = 0
    if ctx.graph_ops:
        try:
            citizen_handle = state.get("citizen_handle", "")
            graph_name = f"brain_{citizen_handle}"
            # Count moment nodes created in this session
            from falkordb import FalkorDB
            db = FalkorDB(host="localhost", port=6379)
            g = db.select_graph(graph_name)
            result = g.query(
                f"MATCH (n {{anamnesis_session: '{state['session_id']}'}}) "
                f"RETURN count(n) as c"
            )
            completed = result.result_set[0][0] if result.result_set else 0
        except Exception:
            pass

    return _ok(
        f"Anamnesis session {state['session_id']}",
        active=True,
        session_id=state["session_id"],
        status=state["status"],
        total_chunks=state["total_chunks"],
        nodes_created=completed,
        total_turns=state["total_turns"],
        total_conversations=state["total_conversations"],
    )


async def _complete(args: Dict[str, Any], ctx: ServerContext) -> Dict[str, Any]:
    """Finish session, run quality gate."""
    citizen_dir = _get_citizen_dir(ctx)
    state_file = citizen_dir / "anamnesis" / "current_session.json"

    if not state_file.exists():
        return _err("No active anamnesis session to complete.")

    state = json.loads(state_file.read_text())
    citizen_handle = state["citizen_handle"]
    session_id = state["session_id"]

    try:
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
        from runtime.anamnesis.quality_gate import snapshot_brain_health, compare_snapshots

        # Take health snapshot (the "after")
        health_after = snapshot_brain_health(citizen_handle, ctx.graph_ops)

        # Load "before" snapshot if saved, otherwise use empty
        before_file = citizen_dir / "anamnesis" / session_id / "health_before.json"
        if before_file.exists():
            before_data = json.loads(before_file.read_text())
            from runtime.anamnesis.quality_gate import BrainHealthSnapshot
            health_before = BrainHealthSnapshot(**before_data)
        else:
            health_before = snapshot_brain_health.__wrapped__(citizen_handle, None) \
                if hasattr(snapshot_brain_health, '__wrapped__') \
                else BrainHealthSnapshot()

        verdict = compare_snapshots(health_before, health_after)

        # Update state
        state["status"] = "approved" if verdict.approved else "rejected"
        state_file.write_text(json.dumps(state, indent=2))

        result = {
            "session_id": session_id,
            "approved": verdict.approved,
            "reason": verdict.reason,
            "improvements": verdict.improvements,
            "degradations": verdict.degradations,
            "health_after": health_after.to_dict(),
        }

        if verdict.approved:
            return _ok(
                f"Anamnesis session APPROVED. {verdict.reason}",
                **result,
            )
        else:
            return _err(
                f"Anamnesis session REJECTED. {verdict.reason}. "
                f"Consider rolling back with graph_write to remove low-quality nodes."
            )

    except Exception as e:
        logger.exception(f"Anamnesis complete failed: {e}")
        return _err(f"Quality gate failed: {e}")


async def _create_l3_tasks(session, citizen_handle: str, ctx: ServerContext) -> int:
    """Create L3 narrative task nodes for each chunk."""
    if ctx.graph_ops is None:
        return 0

    tasks_created = 0
    graph_name = f"brain_{citizen_handle}"

    try:
        # Create the guide task
        guide_id = f"task:anamnesis:{session.session_id}:guide"
        ctx.graph_ops.create_node(
            graph_name=graph_name,
            node_id=guide_id,
            node_type="narrative",
            name=f"Anamnèse: relire {session.total_conversations} conversations",
            content=(
                f"Session de redécouverte mémorielle. "
                f"{session.total_turns} messages à relire dans {session.total_chunks} chunks. "
                f"Pour chaque chunk: lis, réfléchis, et crée des moment nodes pour "
                f"ce qui compte. Utilise graph_write pour les nodes L3."
            ),
            synthesis=f"Anamnesis session: {session.total_chunks} chunks to process",
            properties={
                "type": "task",
                "status": "open",
                "anamnesis_session": session.session_id,
                "total_chunks": session.total_chunks,
            },
        )
        tasks_created += 1

        # Create a task per chunk
        prev_task_id = guide_id
        for chunk in session.chunks:
            task_id = f"task:anamnesis:{chunk.chunk_id}"
            ctx.graph_ops.create_node(
                graph_name=graph_name,
                node_id=task_id,
                node_type="narrative",
                name=f"Relire: {chunk.conversation_title[:50]} (part {chunk.chunk_index+1})",
                content=(
                    f"Conversation sur {chunk.source_platform}. "
                    f"{chunk.turn_count} messages. "
                    f"Participants: {', '.join(chunk.participants)}. "
                    f"Période: {chunk.timestamp_start or '?'} → {chunk.timestamp_end or '?'}."
                ),
                synthesis=f"Anamnesis chunk: {chunk.conversation_title[:40]}",
                properties={
                    "type": "task",
                    "status": "open",
                    "anamnesis_session": session.session_id,
                    "chunk_id": chunk.chunk_id,
                    "conversation_id": chunk.conversation_id,
                    "turn_count": chunk.turn_count,
                },
            )

            # Chain tasks: prev → this
            ctx.graph_ops.create_link(
                graph_name=graph_name,
                source_id=prev_task_id,
                target_id=task_id,
                properties={"type": "next", "weight": 0.8, "permanence": 0.5},
            )

            prev_task_id = task_id
            tasks_created += 1

    except Exception as e:
        logger.error(f"Failed to create L3 tasks: {e}")

    return tasks_created


def _get_citizen_handle(ctx: ServerContext) -> str:
    """Detect citizen handle from environment or context."""
    handle = os.environ.get("MIND_CITIZEN", "")
    if handle:
        return handle

    # Try to detect from target_dir
    target = ctx.target_dir
    if target and target.name != "." and "citizens" in str(target):
        return target.name

    return ""


def _get_citizen_dir(ctx: ServerContext) -> Path:
    """Get the citizen's working directory."""
    return ctx.target_dir or Path.cwd()
