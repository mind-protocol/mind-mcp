"""
[SPEAK] Media — Generate images, synthesize voice, send files.

Actions:
  imagine  — Generate an image (Gemini or Ideogram)
  speak    — Synthesize voice from text (ElevenLabs)
  send_file — Send a file or photo to a platform

All bridge imports are lazy — missing dependencies return clear errors, not crashes.

Usage via MCP:
    media(action="imagine", prompt="A sunset over Venice in 1525")
    media(action="imagine", prompt="...", backend="ideogram", style="REALISTIC")
    media(action="speak", text="Buongiorno, cittadino.", output_path="/tmp/greeting.mp3")
    media(action="send_file", platform="telegram", file_path="/tmp/image.png", caption="Here it is")
"""

import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("mind.media")

PROJECT_ROOT = Path(os.getenv("MIND_PROJECT_ROOT", Path(__file__).parent.parent.parent))


TOOL_SCHEMA = {
    "name": "media",
    "description": (
        "[SPEAK] Generate images, synthesize voice, or send files to platforms. "
        "Use action='imagine' for image generation (Gemini/Ideogram), "
        "'speak' for text-to-speech (ElevenLabs), "
        "'send_file' to send a file or photo to Telegram/Discord/WhatsApp."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["imagine", "speak", "send_file"],
                "description": "What to do: generate an image, synthesize voice, or send a file.",
            },
            # ── imagine params ──
            "prompt": {
                "type": "string",
                "description": "Image generation prompt (for action='imagine').",
            },
            "backend": {
                "type": "string",
                "enum": ["auto", "gemini", "ideogram"],
                "description": "Image backend (default: auto — tries Gemini first, falls back to Ideogram).",
            },
            "style": {
                "type": "string",
                "enum": ["AUTO", "GENERAL", "REALISTIC", "DESIGN", "FICTION"],
                "description": "Image style for Ideogram (default: AUTO).",
            },
            "aspect_ratio": {
                "type": "string",
                "description": "Aspect ratio (e.g., '16:9', '1:1', '9:16'). Default: 1:1.",
            },
            "resolution": {
                "type": "string",
                "enum": ["1K", "2K", "4K"],
                "description": "Image resolution for Gemini (default: 1K).",
            },
            "num_images": {
                "type": "integer",
                "description": "Number of images to generate (default: 1).",
            },
            # ── speak params ──
            "text": {
                "type": "string",
                "description": "Text to synthesize as speech (for action='speak').",
            },
            "output_path": {
                "type": "string",
                "description": "Where to save the audio file (default: /tmp/mind_voice.mp3).",
            },
            "voice_id": {
                "type": "string",
                "description": "ElevenLabs voice ID (uses default citizen voice if omitted).",
            },
            # ── send_file params ──
            "platform": {
                "type": "string",
                "enum": ["telegram", "discord", "whatsapp"],
                "description": "Platform to send the file to (for action='send_file').",
            },
            "file_path": {
                "type": "string",
                "description": "Local path of the file to send.",
            },
            "file_url": {
                "type": "string",
                "description": "URL of the file to send (alternative to file_path, Discord/WhatsApp).",
            },
            "caption": {
                "type": "string",
                "description": "Caption for the file/photo.",
            },
            "chat_id": {
                "type": "string",
                "description": "Target chat/channel ID. Defaults to Nicolas's Telegram chat.",
            },
        },
        "required": ["action"],
    },
}


def handle_media(args: Dict[str, Any]) -> Dict[str, Any]:
    """Dispatch media actions."""
    action = args.get("action")

    if action == "imagine":
        return _imagine(args)
    elif action == "speak":
        return _speak(args)
    elif action == "send_file":
        return _send_file(args)
    else:
        return _err(f"Unknown action '{action}'. Use: imagine, speak, send_file.")


# ── Imagine ─────────────────────────────────────────────────────────────────

def _imagine(args: Dict[str, Any]) -> Dict[str, Any]:
    """Generate an image using Gemini or Ideogram."""
    prompt = args.get("prompt")
    if not prompt:
        return _err("'prompt' is required for action='imagine'.")

    backend = args.get("backend", "auto")
    style = args.get("style", "AUTO")
    aspect_ratio = args.get("aspect_ratio", "1:1")
    resolution = args.get("resolution", "1K")
    num_images = args.get("num_images", 1)

    # Lazy import from project scripts
    image_gen_path = PROJECT_ROOT / "scripts" / "image_gen.py"
    if not image_gen_path.exists():
        return _err(f"image_gen.py not found at {image_gen_path}. Is MIND_PROJECT_ROOT set?")

    try:
        scripts_dir = str(PROJECT_ROOT / "scripts")
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        # Also add project root for any internal imports
        project_str = str(PROJECT_ROOT)
        if project_str not in sys.path:
            sys.path.insert(0, project_str)

        from image_gen import generate_image

        paths = generate_image(
            prompt=prompt,
            style_type=style,
            aspect_ratio=aspect_ratio,
            rendering_speed="DEFAULT",
            num_images=num_images,
            backend=backend,
            resolution=resolution,
        )

        if not paths:
            return _err("Image generation returned no results.")

        # Try to get CDN URLs
        urls = []
        try:
            from image_gen import get_image_url
            for p in paths:
                url = get_image_url(p)
                if url:
                    urls.append(url)
        except ImportError:
            pass

        lines = [f"Generated {len(paths)} image(s):"]
        for i, p in enumerate(paths):
            lines.append(f"  {i+1}. {p}")
            if i < len(urls) and urls[i]:
                lines.append(f"     URL: {urls[i]}")

        lines.append(f"\nBackend: {backend} | Style: {style} | Aspect: {aspect_ratio}")
        return _ok("\n".join(lines))

    except Exception as e:
        logger.exception("Image generation failed")
        return _err(f"Image generation failed: {e}")


# ── Speak ───────────────────────────────────────────────────────────────────

def _speak(args: Dict[str, Any]) -> Dict[str, Any]:
    """Synthesize speech from text using ElevenLabs."""
    text = args.get("text")
    if not text:
        return _err("'text' is required for action='speak'.")

    output_path = args.get("output_path", "/tmp/mind_voice.mp3")
    voice_id = args.get("voice_id") or os.getenv("ELEVENLABS_VOICE_ID", "oPo4t55LBdLAECiAx1JD")

    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        return _err("ELEVENLABS_API_KEY not set in environment.")

    try:
        import requests

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.75,
                "similarity_boost": 0.85,
                "style": 0.3,
                "use_speaker_boost": True,
            },
        }

        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        if not resp.ok:
            return _err(f"ElevenLabs API error: {resp.status_code} — {resp.text[:200]}")

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_bytes(resp.content)

        size_kb = len(resp.content) / 1024
        return _ok(f"Voice synthesized: {output_path} ({size_kb:.1f} KB)\nVoice ID: {voice_id}")

    except Exception as e:
        logger.exception("Voice synthesis failed")
        return _err(f"Voice synthesis failed: {e}")


# ── Send File ───────────────────────────────────────────────────────────────

def _send_file(args: Dict[str, Any]) -> Dict[str, Any]:
    """Send a file or photo to a platform."""
    platform = (args.get("platform") or "").lower()
    file_path = args.get("file_path")
    file_url = args.get("file_url")
    caption = args.get("caption")
    chat_id = args.get("chat_id")

    if not platform:
        return _err("'platform' is required for action='send_file'.")
    if not file_path and not file_url:
        return _err("'file_path' or 'file_url' is required for action='send_file'.")

    if platform == "telegram":
        return _send_file_telegram(file_path, caption, chat_id)
    elif platform == "discord":
        return _send_file_discord(file_path, file_url, caption, chat_id)
    elif platform == "whatsapp":
        return _send_file_whatsapp(file_path, file_url, caption, chat_id)
    else:
        return _err(f"Platform '{platform}' not supported for file sending. Use: telegram, discord, whatsapp.")


def _send_file_telegram(file_path: str, caption: str, chat_id: str) -> Dict[str, Any]:
    """Send file/photo via Telegram Bot API."""
    import json
    import requests

    if not file_path or not Path(file_path).exists():
        return _err(f"File not found: {file_path}")

    # Load TG config
    config_file = PROJECT_ROOT / "shrine" / "state" / "telegram_config.json"
    try:
        config = json.loads(config_file.read_text()) if config_file.exists() else {}
    except (json.JSONDecodeError, OSError):
        config = {}

    bot_token = config.get("bot_token")
    if not bot_token:
        return _err("Telegram not configured. No bot_token in telegram_config.json.")

    chat_id = chat_id or "1864364329"  # Default: Nicolas

    # Detect if image or document
    ext = Path(file_path).suffix.lower()
    is_image = ext in (".png", ".jpg", ".jpeg", ".gif", ".webp")

    if is_image:
        endpoint = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
        files = {"photo": open(file_path, "rb")}
    else:
        endpoint = f"https://api.telegram.org/bot{bot_token}/sendDocument"
        files = {"document": open(file_path, "rb")}

    data = {"chat_id": chat_id}
    if caption:
        data["caption"] = caption[:1024]

    try:
        resp = requests.post(endpoint, data=data, files=files, timeout=30)
        if resp.ok:
            msg_id = resp.json()["result"]["message_id"]
            kind = "Photo" if is_image else "Document"
            return _ok(f"{kind} sent to Telegram chat {chat_id}. (message_id: {msg_id})")
        else:
            return _err(f"Telegram API error: {resp.status_code} — {resp.text[:200]}")
    except requests.exceptions.RequestException as e:
        return _err(f"Network error: {e}")


def _send_file_discord(file_path: str, file_url: str, caption: str, channel_id: str) -> Dict[str, Any]:
    """Send file via Discord webhook."""
    if not channel_id:
        return _err("'chat_id' (Discord channel ID) is required for Discord file sending.")

    try:
        scripts_dir = str(PROJECT_ROOT / "scripts")
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)

        from discord_bridge import send_as_citizen_file

        result = send_as_citizen_file(
            handle=None,  # auto-detect
            channel_id=int(channel_id),
            file_path=file_path,
            file_url=file_url,
            text=caption or "",
        )

        if result:
            return _ok(f"File sent to Discord channel {channel_id}.")
        else:
            return _err("Discord file send returned no result.")

    except ImportError:
        return _err("Discord bridge not available. Check MIND_PROJECT_ROOT.")
    except Exception as e:
        return _err(f"Discord file send failed: {e}")


def _send_file_whatsapp(file_path: str, file_url: str, caption: str, chat_id: str) -> Dict[str, Any]:
    """Send file/image via WhatsApp (WAHA)."""
    if not chat_id:
        return _err("'chat_id' is required for WhatsApp file sending.")

    try:
        scripts_dir = str(PROJECT_ROOT / "scripts")
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)

        # Detect if image
        is_image = False
        if file_path:
            ext = Path(file_path).suffix.lower()
            is_image = ext in (".png", ".jpg", ".jpeg", ".gif", ".webp")
        elif file_url:
            is_image = any(file_url.lower().endswith(e) for e in (".png", ".jpg", ".jpeg", ".gif", ".webp"))

        if is_image:
            from whatsapp_bridge import send_image
            result = send_image(
                chat_id=chat_id,
                image_url=file_url,
                local_path=file_path,
                caption=caption,
            )
        else:
            from whatsapp_bridge import send_file
            result = send_file(
                chat_id=chat_id,
                file_path=file_path,
                caption=caption,
            )

        if result:
            kind = "Image" if is_image else "File"
            return _ok(f"{kind} sent to WhatsApp chat {chat_id}.")
        else:
            return _err("WhatsApp send returned no result.")

    except ImportError:
        return _err("WhatsApp bridge not available. Check MIND_PROJECT_ROOT.")
    except Exception as e:
        return _err(f"WhatsApp send failed: {e}")


# ── Response helpers ────────────────────────────────────────────────────────

def _ok(text: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": text}]}


def _err(msg: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": f"Error: {msg}"}]}
