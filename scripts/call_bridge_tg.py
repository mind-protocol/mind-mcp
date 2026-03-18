#!/usr/bin/env python3
"""Bridge a /call file to Telegram with TTS.

Watches a call file for new citizen lines, generates voice via ElevenLabs,
sends text + audio to the citizen's Telegram chat.

Usage:
    python3 scripts/call_bridge_tg.py @silas citizens/silas/calls/aurore.md
"""

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
logger = logging.getLogger("call_bridge_tg")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORLD_ROOT = PROJECT_ROOT.parent
TMP_DIR = Path(tempfile.gettempdir()) / "mind_call_bridge"
TMP_DIR.mkdir(exist_ok=True)

# ── Telegram API ─────────────────────────────────────────────────────────────

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")


def tg_api(method: str, **kwargs) -> dict | None:
    """Call Telegram Bot API."""
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set")
        return None
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/{method}",
            timeout=30, **kwargs,
        )
        data = resp.json()
        if not data.get("ok"):
            logger.error(f"TG API {method} failed: {data.get('description')}")
            return None
        return data.get("result")
    except Exception as e:
        logger.error(f"TG API {method} error: {e}")
        return None


def send_text(chat_id: str, text: str):
    """Send text message to Telegram."""
    tg_api("sendMessage", json={"chat_id": chat_id, "text": text})


def send_voice(chat_id: str, ogg_path: Path):
    """Send OGG voice file to Telegram."""
    try:
        with open(ogg_path, "rb") as f:
            tg_api("sendVoice", data={"chat_id": chat_id}, files={"voice": f})
    except Exception as e:
        logger.error(f"Send voice failed: {e}")


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

    # Convert MP3 -> OGG (Telegram requires Opus in OGG)
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
    """Resolve Telegram chat_id from profile or env."""
    clean = handle.lstrip("@").upper()
    env_key = f"TG_CHAT_ID_{clean}"
    if os.environ.get(env_key):
        return os.environ[env_key]

    # Check profile fields
    if profile.get("telegram_id"):
        return str(profile["telegram_id"])
    if profile.get("telegram_chat_id"):
        return str(profile["telegram_chat_id"])

    # Check contacts array
    for c in profile.get("contacts", []):
        if isinstance(c, dict) and c.get("type") == "telegram":
            return str(c["value"])

    # Fallback: NICOLAS_CHAT_ID (owner)
    fallback = os.environ.get("NICOLAS_CHAT_ID", "")
    if fallback:
        logger.warning(f"No TG chat_id for {handle}, falling back to NICOLAS_CHAT_ID")
        return fallback

    return ""


# ── File Watcher ─────────────────────────────────────────────────────────────

def watch_call_file(handle: str, call_file: Path):
    """Watch a call file and bridge citizen lines to Telegram."""
    clean = handle.lstrip("@")
    prefix = f"@{clean}:"

    profile = load_profile(handle)
    voice_id = get_voice_id(handle, profile)
    chat_id = get_chat_id(handle, profile)

    if not chat_id:
        logger.error(f"No Telegram chat_id found for {handle}. Set TG_CHAT_ID_{clean.upper()} env var.")
        sys.exit(1)

    logger.info(f"Bridging {call_file} -> Telegram chat {chat_id}")
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
                    send_voice(chat_id, ogg)
                    try:
                        ogg.unlink()
                    except OSError:
                        pass


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 scripts/call_bridge_tg.py @handle path/to/call_file.md")
        print("Example: python3 scripts/call_bridge_tg.py @silas citizens/silas/calls/aurore.md")
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
