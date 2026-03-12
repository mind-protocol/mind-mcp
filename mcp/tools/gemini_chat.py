"""
Gemini Chat Tool — Send messages to Gemini with session management and image support.

Usage via MCP:
    gemini_chat(message="Analyse ce texte...", system_prompt="Tu es un éditeur littéraire.")
    gemini_chat(message="Continue.", session_id="abc123")
    gemini_chat(message="Décris cette image.", images=["/path/to/image.png"])
"""

import base64
import json
import logging
import mimetypes
import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("mind.gemini")

# In-memory session store: session_id -> {"history": [...], "config": {...}, "created": float}
_sessions: Dict[str, Dict[str, Any]] = {}

# Session TTL: 2 hours
SESSION_TTL = 7200

# Default model from env, fallback to gemini-2.5-flash
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


# ── Tool Schema (for _handle_list_tools) ──────────────────────────────────────

TOOL_SCHEMA = {
    "name": "gemini_chat",
    "description": (
        "Send a message to Google Gemini. Supports system prompts, multi-turn sessions, "
        "image/file attachments, and configurable generation parameters. "
        "Returns Gemini's response text. Use session_id to continue a conversation."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "The message to send to Gemini."
            },
            "system_prompt": {
                "type": "string",
                "description": "System instruction that guides Gemini's behavior for this session."
            },
            "session_id": {
                "type": "string",
                "description": (
                    "Continue an existing session. If provided, message is appended to conversation history. "
                    "Omit to start a new session."
                )
            },
            "images": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of file paths (images, PDFs, text files) to include with the message."
            },
            "model": {
                "type": "string",
                "description": f"Gemini model to use (default: {DEFAULT_MODEL}). Examples: gemini-2.5-pro, gemini-2.5-flash"
            },
            "temperature": {
                "type": "number",
                "description": "Sampling temperature 0.0-2.0 (default: 1.0). Lower = more deterministic."
            },
            "max_tokens": {
                "type": "integer",
                "description": "Maximum output tokens (default: 8192)."
            },
            "json_mode": {
                "type": "boolean",
                "description": "If true, Gemini returns valid JSON (sets responseMimeType to application/json)."
            },
            "list_sessions": {
                "type": "boolean",
                "description": "If true, returns list of active sessions instead of sending a message."
            },
            "end_session": {
                "type": "string",
                "description": "End/delete a session by ID."
            }
        }
    }
}


# ── Implementation ────────────────────────────────────────────────────────────

def _get_client():
    """Lazy-init Gemini client."""
    from google import genai
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set in environment")
    return genai.Client(api_key=api_key)


def _load_file_as_part(file_path: str) -> dict:
    """Load a file and return it as a Gemini Part dict."""
    from google.genai import types

    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    mime_type, _ = mimetypes.guess_type(str(path))
    if not mime_type:
        # Fallback by extension
        ext = path.suffix.lower()
        mime_map = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".pdf": "application/pdf",
            ".txt": "text/plain",
            ".md": "text/markdown",
            ".json": "application/json",
            ".csv": "text/csv",
            ".py": "text/x-python",
            ".js": "text/javascript",
            ".ts": "text/typescript",
            ".html": "text/html",
            ".xml": "text/xml",
            ".svg": "image/svg+xml",
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav",
            ".mp4": "video/mp4",
        }
        mime_type = mime_map.get(ext, "application/octet-stream")

    data = path.read_bytes()
    return types.Part.from_bytes(data=data, mime_type=mime_type)


def _prune_expired_sessions():
    """Remove sessions older than TTL."""
    now = time.time()
    expired = [sid for sid, s in _sessions.items() if now - s["created"] > SESSION_TTL]
    for sid in expired:
        del _sessions[sid]


def _build_contents(message: str, images: Optional[List[str]] = None) -> list:
    """Build a contents list with text and optional file parts."""
    parts = []
    if images:
        for img_path in images:
            parts.append(_load_file_as_part(img_path))
    parts.append(message)
    return parts


def handle_gemini_chat(args: Dict[str, Any]) -> Dict[str, Any]:
    """Main handler for the gemini_chat tool."""
    from google.genai import types

    # ── List sessions ──
    if args.get("list_sessions"):
        _prune_expired_sessions()
        if not _sessions:
            return _ok("No active sessions.")
        lines = ["**Active Gemini Sessions:**\n"]
        for sid, s in _sessions.items():
            age = int(time.time() - s["created"])
            turns = len(s["history"]) // 2
            model = s["config"].get("model", DEFAULT_MODEL)
            lines.append(f"- `{sid}` — {turns} turns, {age}s old, model: {model}")
        return _ok("\n".join(lines))

    # ── End session ──
    end_id = args.get("end_session")
    if end_id:
        if end_id in _sessions:
            del _sessions[end_id]
            return _ok(f"Session `{end_id}` ended.")
        return _ok(f"Session `{end_id}` not found.")

    # ── Validate message ──
    message = args.get("message")
    if not message:
        return _err("'message' is required (unless using list_sessions or end_session).")

    system_prompt = args.get("system_prompt")
    session_id = args.get("session_id")
    images = args.get("images")
    model = args.get("model", DEFAULT_MODEL)
    temperature = args.get("temperature")
    max_tokens = args.get("max_tokens", 8192)
    json_mode = args.get("json_mode", False)

    _prune_expired_sessions()

    try:
        client = _get_client()

        # ── Build config ──
        config_kwargs = {}
        if system_prompt and not session_id:
            config_kwargs["system_instruction"] = system_prompt
        if temperature is not None:
            config_kwargs["temperature"] = temperature
        if max_tokens:
            config_kwargs["max_output_tokens"] = max_tokens
        if json_mode:
            config_kwargs["response_mime_type"] = "application/json"

        config = types.GenerateContentConfig(**config_kwargs) if config_kwargs else None

        # ── Continue existing session ──
        if session_id:
            if session_id not in _sessions:
                return _err(f"Session `{session_id}` not found. Active sessions: {list(_sessions.keys())}")

            session = _sessions[session_id]

            # Build user content
            user_content = _build_contents(message, images)

            # Append to history
            session["history"].append(types.Content(
                role="user",
                parts=[types.Part.from_text(text=message)] if not images else [
                    _load_file_as_part(p) for p in (images or [])
                ] + [types.Part.from_text(text=message)]
            ))

            # Rebuild config with session's system prompt
            session_config_kwargs = dict(session["config"].get("config_kwargs", {}))
            if temperature is not None:
                session_config_kwargs["temperature"] = temperature
            if max_tokens:
                session_config_kwargs["max_output_tokens"] = max_tokens
            if json_mode:
                session_config_kwargs["response_mime_type"] = "application/json"

            session_config = types.GenerateContentConfig(**session_config_kwargs) if session_config_kwargs else None
            session_model = session["config"].get("model", model)

            response = client.models.generate_content(
                model=session_model,
                contents=session["history"],
                config=session_config,
            )

            # Append assistant response
            response_text = response.text or "(empty response)"
            session["history"].append(types.Content(
                role="model",
                parts=[types.Part.from_text(text=response_text)]
            ))

            return _ok(response_text, session_id=session_id, model=session_model)

        # ── New conversation ──
        user_parts = _build_contents(message, images)

        response = client.models.generate_content(
            model=model,
            contents=user_parts,
            config=config,
        )

        response_text = response.text or "(empty response)"

        # Create session for future continuation
        new_session_id = uuid.uuid4().hex[:12]
        _sessions[new_session_id] = {
            "history": [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=message)] if not images else [
                        _load_file_as_part(p) for p in (images or [])
                    ] + [types.Part.from_text(text=message)]
                ),
                types.Content(
                    role="model",
                    parts=[types.Part.from_text(text=response_text)]
                ),
            ],
            "config": {
                "model": model,
                "config_kwargs": config_kwargs,
            },
            "created": time.time(),
        }

        return _ok(response_text, session_id=new_session_id, model=model, new_session=True)

    except Exception as e:
        logger.exception("Gemini chat failed")
        return _err(f"Gemini error: {e}")


# ── Response helpers ──────────────────────────────────────────────────────────

def _ok(text: str, session_id: str = None, model: str = None, new_session: bool = False) -> Dict[str, Any]:
    """Format a successful response."""
    meta_parts = []
    if session_id:
        if new_session:
            meta_parts.append(f"session: `{session_id}` (new — use this ID to continue)")
        else:
            meta_parts.append(f"session: `{session_id}`")
    if model:
        meta_parts.append(f"model: {model}")

    meta_line = f"\n\n---\n*{' | '.join(meta_parts)}*" if meta_parts else ""

    return {"content": [{"type": "text", "text": f"{text}{meta_line}"}]}


def _err(msg: str) -> Dict[str, Any]:
    """Format an error response."""
    return {"content": [{"type": "text", "text": f"Error: {msg}"}]}
