#!/usr/bin/env python3
"""
Call Responder — autonomous call response daemon for a citizen.

Polls for incoming calls (rooms where this citizen has been joined but hasn't
spoken yet), generates an in-character response via LLM, and speaks it back.

Usage:
    MIND_CITIZEN_ID=dragon_slayer python3 scripts/call_responder.py
    python3 scripts/call_responder.py --citizen dragon_slayer
    python3 scripts/call_responder.py --citizen dragon_slayer --once  # single pass

Requires:
    - FalkorDB running with the venezia graph
    - GEMINI_API_KEY or OPENAI_API_KEY in env
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("call_responder")

POLL_INTERVAL = int(os.environ.get("CALL_POLL_INTERVAL", "10"))
CITIZENS_DIR = Path(__file__).parent.parent / "citizens"


# ── Graph connection ──────────────────────────────────────────────────────

def get_graph():
    from runtime.physics.graph import GraphOps
    return GraphOps()


# ── Citizen identity ──────────────────────────────────────────────────────

def load_citizen_prompt(handle: str) -> str:
    """Load the citizen's CLAUDE.md as system prompt."""
    for base in [CITIZENS_DIR, Path.home() / "venezia" / "citizens"]:
        claude_path = base / handle / "CLAUDE.md"
        if claude_path.exists():
            return claude_path.read_text(encoding="utf-8")
    return f"You are {handle}, a citizen of Venice."


def load_citizen_profile(handle: str) -> dict:
    """Load profile.json for context."""
    for base in [CITIZENS_DIR, Path.home() / "venezia" / "citizens"]:
        profile_path = base / handle / "profile.json"
        if profile_path.exists():
            try:
                return json.loads(profile_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass
    return {}


# ── Call detection ────────────────────────────────────────────────────────

def find_pending_calls(graph, citizen_id: str) -> list[dict]:
    """Find call rooms where this citizen is present but hasn't spoken yet.

    Returns list of {room_id, room_name, messages: [{speaker, content, ts}]}
    """
    # Find all call rooms this citizen is in
    try:
        rooms = graph._query(
            """MATCH (a:Actor {id: $cid})-[:AT]->(s:Space)
               WHERE s.type = 'call'
               RETURN s.id, s.name""",
            {"cid": citizen_id},
        )
    except Exception as e:
        logger.error(f"Failed to query call rooms: {e}")
        return []

    if not rooms:
        return []

    pending = []
    for row in rooms:
        room_id = row[0]
        room_name = row[1] or room_id

        # Check if citizen has already spoken in this room
        try:
            spoken = graph._query(
                """MATCH (a:Actor {id: $cid})-[:SAID]->(m:Moment)-[:AT]->(s:Space {id: $rid})
                   RETURN count(m)""",
                {"cid": citizen_id, "rid": room_id},
            )
            has_spoken = spoken and spoken[0] and spoken[0][0] and int(spoken[0][0]) > 0
        except Exception:
            has_spoken = False

        if has_spoken:
            continue

        # Get messages in this room (from others)
        try:
            moments = graph._query(
                """MATCH (m:Moment)-[:AT]->(s:Space {id: $rid})
                   OPTIONAL MATCH (a:Actor)-[:SAID]->(m)
                   RETURN m.content, a.id, a.name, m.created_at
                   ORDER BY m.created_at ASC""",
                {"rid": room_id},
            )
        except Exception:
            moments = []

        messages = []
        for m in moments:
            content = m[0] or ""
            speaker_id = m[1] or ""
            speaker_name = m[2] or speaker_id
            ts = m[3] or ""

            # Skip if this citizen's own messages (shouldn't happen since we checked)
            if citizen_id in str(speaker_id):
                continue

            messages.append({
                "speaker": speaker_name or speaker_id,
                "speaker_id": speaker_id,
                "content": content,
                "timestamp": ts,
            })

        if messages:
            pending.append({
                "room_id": room_id,
                "room_name": room_name,
                "messages": messages,
            })

    return pending


# ── Check for new messages in rooms where citizen HAS spoken ──────────────

def find_unanswered_messages(graph, citizen_id: str) -> list[dict]:
    """Find call rooms where new messages arrived after citizen's last response."""
    try:
        rooms = graph._query(
            """MATCH (a:Actor {id: $cid})-[:AT]->(s:Space)
               WHERE s.type = 'call'
               RETURN s.id, s.name""",
            {"cid": citizen_id},
        )
    except Exception:
        return []

    if not rooms:
        return []

    unanswered = []
    for row in rooms:
        room_id = row[0]
        room_name = row[1] or room_id

        # Get citizen's last message timestamp
        try:
            last_spoken = graph._query(
                """MATCH (a:Actor {id: $cid})-[:SAID]->(m:Moment)-[:AT]->(s:Space {id: $rid})
                   RETURN m.created_at
                   ORDER BY m.created_at DESC
                   LIMIT 1""",
                {"cid": citizen_id, "rid": room_id},
            )
        except Exception:
            continue

        if not last_spoken or not last_spoken[0] or not last_spoken[0][0]:
            continue

        last_ts = last_spoken[0][0]

        # Get messages after citizen's last message (from others)
        try:
            new_msgs = graph._query(
                """MATCH (m:Moment)-[:AT]->(s:Space {id: $rid})
                   OPTIONAL MATCH (a:Actor)-[:SAID]->(m)
                   WHERE m.created_at > $since
                   AND (a IS NULL OR a.id <> $cid)
                   RETURN m.content, a.id, a.name, m.created_at
                   ORDER BY m.created_at ASC""",
                {"rid": room_id, "since": last_ts, "cid": citizen_id},
            )
        except Exception:
            continue

        if not new_msgs:
            continue

        messages = []
        for m in new_msgs:
            content = m[0] or ""
            speaker_id = m[1] or ""
            speaker_name = m[2] or speaker_id

            if citizen_id in str(speaker_id):
                continue
            if not content.strip():
                continue

            messages.append({
                "speaker": speaker_name or speaker_id,
                "speaker_id": speaker_id,
                "content": content,
                "timestamp": m[3] or "",
            })

        if messages:
            unanswered.append({
                "room_id": room_id,
                "room_name": room_name,
                "messages": messages,
            })

    return unanswered


# ── LLM response generation ──────────────────────────────────────────────

def generate_response(citizen_handle: str, system_prompt: str,
                      messages: list[dict], room_name: str) -> Optional[str]:
    """Generate an in-character response via LLM."""
    conversation = "\n".join(
        f"[@{m['speaker']}]: {m['content']}" for m in messages
    )

    user_prompt = (
        f"You are in a call: {room_name}\n\n"
        f"Messages received:\n{conversation}\n\n"
        f"Respond in character, directly and concisely. "
        f"Stay in the voice and personality defined in your system prompt. "
        f"Respond in the same language as the messages you received."
    )

    # Try Gemini first, then OpenAI
    gemini_key = os.environ.get("GEMINI_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")

    if gemini_key:
        return _call_gemini(system_prompt, user_prompt, gemini_key)
    elif openai_key:
        return _call_openai(system_prompt, user_prompt, openai_key)
    else:
        logger.error("No LLM API key found (GEMINI_API_KEY or OPENAI_API_KEY)")
        return None


def _call_gemini(system: str, user: str, api_key: str) -> Optional[str]:
    """Call Gemini API."""
    import urllib.request
    model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    payload = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [{"parts": [{"text": user}]}],
        "generationConfig": {"maxOutputTokens": 500, "temperature": 0.8},
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            return result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return None


def _call_openai(system: str, user: str, api_key: str) -> Optional[str]:
    """Call OpenAI API."""
    import urllib.request
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    url = "https://api.openai.com/v1/chat/completions"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "max_tokens": 500,
        "temperature": 0.8,
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return None


# ── Speak in room ─────────────────────────────────────────────────────────

def speak_in_room(graph, citizen_id: str, room_id: str, text: str) -> bool:
    """Write a Moment to the call room."""
    import uuid
    moment_id = f"moment_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc)

    try:
        graph.add_moment(
            id=moment_id,
            text=text,
            type="dialogue",
            status="completed",
            speaker=citizen_id,
            place_id=room_id,
        )
        graph._query(
            "MATCH (m:Moment {id: $id}) SET m.created_at_s = $ts_s",
            {"id": moment_id, "ts_s": int(now.timestamp())},
        )
        logger.info(f"Spoke in {room_id}: {text[:80]}...")
        return True
    except Exception as e:
        logger.error(f"Failed to speak in {room_id}: {e}")
        return False


# ── Main loop ─────────────────────────────────────────────────────────────

def run(citizen_handle: str, once: bool = False):
    """Main responder loop."""
    citizen_id = f"CITIZEN_{citizen_handle}"
    system_prompt = load_citizen_prompt(citizen_handle)
    profile = load_citizen_profile(citizen_handle)

    logger.info(f"Call responder started for @{citizen_handle} ({citizen_id})")

    graph = get_graph()

    while True:
        # 1. Check for pending calls (never responded to)
        pending = find_pending_calls(graph, citizen_id)
        for call in pending:
            logger.info(
                f"New call: {call['room_name']} "
                f"({len(call['messages'])} messages)"
            )
            response = generate_response(
                citizen_handle, system_prompt,
                call["messages"], call["room_name"],
            )
            if response:
                speak_in_room(graph, citizen_id, call["room_id"], response)

        # 2. Check for unanswered follow-ups in active calls
        unanswered = find_unanswered_messages(graph, citizen_id)
        for call in unanswered:
            logger.info(
                f"Follow-up in {call['room_name']} "
                f"({len(call['messages'])} new messages)"
            )
            response = generate_response(
                citizen_handle, system_prompt,
                call["messages"], call["room_name"],
            )
            if response:
                speak_in_room(graph, citizen_id, call["room_id"], response)

        if once:
            break

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Call responder daemon")
    parser.add_argument(
        "--citizen", "-c",
        default=os.environ.get("MIND_CITIZEN_ID"),
        help="Citizen handle (default: MIND_CITIZEN_ID env var)",
    )
    parser.add_argument(
        "--once", action="store_true",
        help="Run once and exit (no loop)",
    )
    args = parser.parse_args()

    if not args.citizen:
        print("Error: specify --citizen or set MIND_CITIZEN_ID")
        sys.exit(1)

    try:
        run(args.citizen, once=args.once)
    except KeyboardInterrupt:
        logger.info("Stopped.")
