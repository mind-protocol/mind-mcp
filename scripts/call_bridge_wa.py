#!/usr/bin/env python3
"""Bridge a /call file to WhatsApp with TTS via WAHA.

Watches a call file for new citizen lines, generates voice via ElevenLabs,
sends text + audio to the citizen's WhatsApp chat via WAHA.

Usage:
    python3 scripts/call_bridge_wa.py @silas citizens/silas/calls/aurore.md
"""

import base64
import json
import logging
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("call_bridge_wa")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORLD_ROOT = PROJECT_ROOT.parent
TMP_DIR = Path(tempfile.gettempdir()) / "mind_call_bridge"
TMP_DIR.mkdir(exist_ok=True)

# ── WAHA API ─────────────────────────────────────────────────────────────────

WAHA_URL = os.environ.get("WAHA_URL", "http://localhost:3002")
WAHA_SESSION = os.environ.get("WAHA_SESSION", "default")
WAHA_API_KEY = os.environ.get("WAHA_API_KEY", "")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")


def waha_headers() -> dict:
    """Build WAHA API headers."""
    headers = {"Content-Type": "application/json"}
    if WAHA_API_KEY:
        headers["X-Api-Key"] = WAHA_API_KEY
    return headers


def send_text(chat_id: str, text: str):
    """Send text message via WAHA."""
    if not WAHA_URL:
        logger.error("WAHA_URL not configured")
        return

    # Ensure @c.us suffix for personal chats
    if not chat_id.endswith("@c.us") and not chat_id.endswith("@g.us"):
        chat_id = f"{chat_id}@c.us"

    try:
        resp = requests.post(
            f"{WAHA_URL}/api/sendText",
            headers=waha_headers(),
            json={"session": WAHA_SESSION, "chatId": chat_id, "text": text},
            timeout=15,
        )
        if resp.status_code not in (200, 201):
            logger.error(f"WAHA sendText failed {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        logger.error(f"WAHA sendText error: {e}")


def send_audio(chat_id: str, ogg_path: Path):
    """Send audio file via WAHA sendFile endpoint."""
    if not WAHA_URL:
        logger.error("WAHA_URL not configured")
        return

    # Ensure @c.us suffix
    if not chat_id.endswith("@c.us") and not chat_id.endswith("@g.us"):
        chat_id = f"{chat_id}@c.us"

    # WAHA accepts base64-encoded files via sendFile
    try:
        audio_bytes = ogg_path.read_bytes()
        audio_b64 = base64.b64encode(audio_bytes).decode("ascii")

        resp = requests.post(
            f"{WAHA_URL}/api/sendFile",
            headers=waha_headers(),
            json={
                "session": WAHA_SESSION,
                "chatId": chat_id,
                "file": {
                    "mimetype": "audio/ogg; codecs=opus",
                    "filename": "voice.ogg",
                    "data": f"data:audio/ogg;base64,{audio_b64}",
                },
            },
            timeout=30,
        )
        if resp.status_code not in (200, 201):
            logger.error(f"WAHA sendFile failed {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        logger.error(f"WAHA sendFile error: {e}")


# ── ElevenLabs TTS ───────────────────────────────────────────────────────────

def generate_tts(text: str, voice_id: str) -> Path | None:
    """Generate OGG voice note via ElevenLabs."""
    if not ELEVENLABS_API_KEY:
        logger.warning("ELEVENLABS_API_KEY not set, skipping TTS")
        return None
    if not text.strip():
        return None

    # Truncate for TTS
    if len(text) > 2000:
        text = text[:2000]

    mp3_path = TMP_DIR / f"tts_{int(time.time() * 1000)}.mp3"
    ogg_path = mp3_path.with_suffix(".ogg")

    try:
        resp = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={
                "xi-api-key": ELEVENLABS_API_KEY,
                "Content-Type": "application/json",
            },
            json={
                "text": text,
                "model_id": "eleven_turbo_v2_5",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
            },
            timeout=30,
        )
        if resp.status_code != 200 or len(resp.content) < 1000:
            logger.error(f"ElevenLabs TTS failed: {resp.status_code}")
            return None
        mp3_path.write_bytes(resp.content)
    except Exception as e:
        logger.error(f"ElevenLabs TTS error: {e}")
        return None

    # Convert MP3 -> OGG (WhatsApp voice notes need Opus in OGG)
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(mp3_path), "-c:a", "libopus", "-b:a", "64k", str(ogg_path)],
            capture_output=True, timeout=30,
        )
        mp3_path.unlink(missing_ok=True)
        if ogg_path.exists() and ogg_path.stat().st_size > 0:
            return ogg_path
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        logger.error(f"ffmpeg conversion failed: {e}")

    return None


# ── Profile Loading ──────────────────────────────────────────────────────────

def load_profile(handle: str) -> dict:
    """Load citizen profile.json. Returns {} on failure."""
    clean = handle.lstrip("@")
    for base in [WORLD_ROOT, PROJECT_ROOT]:
        pf = base / "citizens" / clean / "profile.json"
        if pf.exists():
            try:
                return json.loads(pf.read_text())
            except (json.JSONDecodeError, OSError) as e:
                logger.warning(f"Failed to read {pf}: {e}")
    return {}


def get_voice_id(handle: str, profile: dict) -> str:
    """Resolve ElevenLabs voice_id from profile or env."""
    clean = handle.lstrip("@").upper()
    env_key = f"ELEVENLABS_VOICE_ID_{clean}"
    if os.environ.get(env_key):
        return os.environ[env_key]

    voice = profile.get("voice", {})
    if isinstance(voice, dict) and voice.get("elevenlabs_voice_id"):
        return voice["elevenlabs_voice_id"]

    # Default voice
    return os.environ.get("ELEVENLABS_VOICE_ID", "oPo4t55LBdLAECiAx1JD")


def get_chat_id(handle: str, profile: dict) -> str:
    """Resolve WhatsApp chat_id (phone number) from profile or env."""
    clean = handle.lstrip("@").upper()
    env_key = f"WA_CHAT_ID_{clean}"
    if os.environ.get(env_key):
        return os.environ[env_key]

    # Check contacts array for whatsapp entry
    for c in profile.get("contacts", []):
        if isinstance(c, dict) and c.get("type") == "whatsapp":
            return str(c["value"])

    # Check phone field
    if profile.get("phone"):
        return str(profile["phone"])

    # Fallback: OWNER_WHATSAPP_PHONE
    fallback = os.environ.get("OWNER_WHATSAPP_PHONE", "")
    if fallback:
        logger.warning(f"No WA chat_id for {handle}, falling back to OWNER_WHATSAPP_PHONE")
        return fallback

    return ""


# ── File Watcher ─────────────────────────────────────────────────────────────

def watch_call_file(handle: str, call_file: Path):
    """Watch a call file and bridge citizen lines to WhatsApp."""
    clean = handle.lstrip("@")
    prefix = f"@{clean}:"

    profile = load_profile(handle)
    voice_id = get_voice_id(handle, profile)
    chat_id = get_chat_id(handle, profile)

    if not chat_id:
        logger.error(f"No WhatsApp chat_id found for {handle}. Set WA_CHAT_ID_{clean.upper()} env var.")
        sys.exit(1)

    logger.info(f"Bridging {call_file} -> WhatsApp chat {chat_id}")
    logger.info(f"Citizen: {handle}, voice_id: {voice_id}")

    if not call_file.exists():
        logger.error(f"Call file not found: {call_file}")
        sys.exit(1)

    # Read existing lines to avoid replaying history
    seen_lines = set()
    with open(call_file, "r") as f:
        for line in f:
            seen_lines.add(line.rstrip("\n"))

    last_mtime = call_file.stat().st_mtime
    logger.info(f"Watching... ({len(seen_lines)} existing lines skipped)")

    while True:
        time.sleep(1)

        try:
            mtime = call_file.stat().st_mtime
        except OSError:
            continue

        if mtime <= last_mtime:
            continue

        last_mtime = mtime

        # Read all lines, find new ones
        with open(call_file, "r") as f:
            current_lines = [line.rstrip("\n") for line in f]

        for line in current_lines:
            if line in seen_lines or not line.strip():
                continue
            seen_lines.add(line)

            # Check if this line is from the citizen
            if line.startswith(prefix) or line.startswith(f"{clean}:"):
                text = line.split(":", 1)[1].strip() if ":" in line else line
                if not text:
                    continue

                logger.info(f"[{clean}] {text[:80]}...")

                # Send text
                send_text(chat_id, f"*{clean}:* {text}")

                # Generate and send TTS
                ogg = generate_tts(text, voice_id)
                if ogg:
                    send_audio(chat_id, ogg)
                    try:
                        ogg.unlink()
                    except OSError:
                        pass


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 scripts/call_bridge_wa.py @handle path/to/call_file.md")
        print("Example: python3 scripts/call_bridge_wa.py @silas citizens/silas/calls/aurore.md")
        sys.exit(1)

    handle = sys.argv[1]
    call_file = Path(sys.argv[2])

    # Resolve relative paths from project root
    if not call_file.is_absolute():
        call_file = PROJECT_ROOT / call_file

    try:
        watch_call_file(handle, call_file)
    except KeyboardInterrupt:
        logger.info("Bridge stopped.")


if __name__ == "__main__":
    main()
