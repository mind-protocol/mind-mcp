#!/usr/bin/env python3
"""Live voice call via Telegram — STT → Claude → TTS → voice message.

The bot listens for voice messages in a chat. When silence >4s is detected
(user stops sending voice messages), it chunks the conversation, runs Claude,
and responds with a voice message in the citizen's voice.

The call file is the transcript. Everything written there is visible to
any citizen watching it (/call). A citizen can add another citizen by
writing their handle in the call file.

Usage:
    python3 scripts/voice_call_tg.py @silas

Env vars:
    TELEGRAM_BOT_TOKEN     — Telegram bot token
    ELEVENLABS_API_KEY     — ElevenLabs API key
    OPENAI_API_KEY         — For Whisper STT (or use Gemini)
    CITIZENS_DIR           — Path to citizens/ directory
"""

import json
import logging
import os
import subprocess
import sys
import tempfile
import time
import threading
from datetime import datetime
from pathlib import Path

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger("voice_call")

# ── Config ───────────────────────────────────────────────────────────────────

TG_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
ELEVENLABS_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
WHISPER_KEY = os.environ.get("OPENAI_API_KEY", "")

SILENCE_THRESHOLD = 4.0  # seconds of no voice → process the chunk
POLL_INTERVAL = 1.0      # telegram polling interval
CLAUDE_TIMEOUT = 120     # max seconds for claude -p

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TMP_DIR = Path(tempfile.gettempdir()) / "mind_voice_call"
TMP_DIR.mkdir(exist_ok=True)


# ── Telegram API ─────────────────────────────────────────────────────────────

def tg_api(method, **params):
    """Call Telegram Bot API."""
    r = requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/{method}",
                      json=params, timeout=60)
    return r.json()


def tg_get_file(file_id):
    """Download a file from Telegram."""
    info = tg_api("getFile", file_id=file_id)
    file_path = info.get("result", {}).get("file_path", "")
    if not file_path:
        return None
    url = f"https://api.telegram.org/file/bot{TG_TOKEN}/{file_path}"
    r = requests.get(url, timeout=30)
    return r.content if r.status_code == 200 else None


def tg_send_voice(chat_id, ogg_path, caption=""):
    """Send a voice message on Telegram."""
    with open(ogg_path, "rb") as f:
        requests.post(
            f"https://api.telegram.org/bot{TG_TOKEN}/sendVoice",
            data={"chat_id": chat_id, "caption": caption[:200]},
            files={"voice": f},
            timeout=30,
        )


def tg_send_text(chat_id, text):
    """Send a text message."""
    tg_api("sendMessage", chat_id=chat_id, text=text)


def tg_send_typing(chat_id):
    """Show typing indicator."""
    tg_api("sendChatAction", chat_id=chat_id, action="record_voice")


# ── STT (Whisper) ────────────────────────────────────────────────────────────

def transcribe(audio_bytes, filename="voice.ogg"):
    """Transcribe audio using OpenAI Whisper API."""
    if not WHISPER_KEY:
        logger.warning("No OPENAI_API_KEY — skipping STT")
        return "(voice message — no STT configured)"

    tmp_path = TMP_DIR / filename
    tmp_path.write_bytes(audio_bytes)

    r = requests.post(
        "https://api.openai.com/v1/audio/transcriptions",
        headers={"Authorization": f"Bearer {WHISPER_KEY}"},
        files={"file": open(tmp_path, "rb")},
        data={"model": "whisper-1"},
        timeout=30,
    )
    if r.status_code == 200:
        return r.json().get("text", "")
    logger.error(f"Whisper error: {r.status_code} {r.text[:200]}")
    return "(transcription failed)"


# ── TTS (ElevenLabs) ─────────────────────────────────────────────────────────

def synthesize(text, voice_id):
    """Generate speech via ElevenLabs, return path to OGG file."""
    if not ELEVENLABS_KEY:
        logger.warning("No ELEVENLABS_API_KEY — skipping TTS")
        return None

    r = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        headers={
            "xi-api-key": ELEVENLABS_KEY,
            "Content-Type": "application/json",
        },
        json={
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.8},
        },
        timeout=30,
    )
    if r.status_code != 200:
        logger.error(f"ElevenLabs error: {r.status_code}")
        return None

    mp3_path = TMP_DIR / f"response_{int(time.time())}.mp3"
    mp3_path.write_bytes(r.content)

    # Convert MP3 → OGG (Telegram requires opus)
    ogg_path = mp3_path.with_suffix(".ogg")
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(mp3_path), "-c:a", "libopus", str(ogg_path)],
        capture_output=True, timeout=10,
    )
    return ogg_path if ogg_path.exists() else None


# ── Claude ───────────────────────────────────────────────────────────────────

def ask_claude(citizen_handle, text, citizens_dir):
    """Run claude -p in the citizen's directory."""
    citizen_dir = citizens_dir / citizen_handle
    if not citizen_dir.is_dir():
        return f"(citizen directory not found: {citizen_dir})"

    try:
        result = subprocess.run(
            ["claude", "-p", text],
            cwd=str(citizen_dir),
            capture_output=True,
            text=True,
            timeout=CLAUDE_TIMEOUT,
        )
        return result.stdout.strip() if result.returncode == 0 else f"(claude error: {result.stderr[:200]})"
    except subprocess.TimeoutExpired:
        return "(claude timed out)"
    except FileNotFoundError:
        return "(claude CLI not found)"


# ── Call File (transcript) ───────────────────────────────────────────────────

def append_to_call(call_path, speaker, text):
    """Append a line to the call transcript."""
    call_path.parent.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%H:%M:%S")
    with open(call_path, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] @{speaker}: {text}\n")


# ── Voice Call Loop ──────────────────────────────────────────────────────────

class VoiceCall:
    """Manages a live voice call session with a citizen."""

    def __init__(self, citizen_handle, chat_id, citizens_dir):
        self.citizen = citizen_handle
        self.chat_id = chat_id
        self.citizens_dir = citizens_dir
        self.call_path = citizens_dir / citizen_handle / "calls" / f"live_{chat_id}.md"
        self.voice_id = self._load_voice_id()
        self.buffer = []  # accumulated transcriptions
        self.last_voice_time = 0.0
        self.processing = False

    def _load_voice_id(self):
        """Load voice_id from profile.json or env."""
        env_key = f"ELEVENLABS_VOICE_ID_{self.citizen.upper()}"
        if os.environ.get(env_key):
            return os.environ[env_key]

        profile_path = self.citizens_dir / self.citizen / "profile.json"
        if profile_path.exists():
            try:
                profile = json.loads(profile_path.read_text())
                vid = (profile.get("voice", {}).get("elevenlabs_voice_id")
                       or profile.get("elevenlabs_voice_id", ""))
                if vid:
                    return vid
            except (json.JSONDecodeError, OSError):
                pass

        return os.environ.get("ELEVENLABS_DEFAULT_VOICE", "21m00Tcm4TlvDq8ikWAM")

    def on_voice_message(self, audio_bytes):
        """Process an incoming voice message."""
        self.last_voice_time = time.time()

        # Transcribe
        text = transcribe(audio_bytes)
        if text:
            self.buffer.append(text)
            append_to_call(self.call_path, "human", text)
            logger.info(f"Heard: {text[:80]}")

    def check_silence(self):
        """Check if silence threshold reached. If so, process buffer."""
        if not self.buffer:
            return
        if self.processing:
            return
        if time.time() - self.last_voice_time < SILENCE_THRESHOLD:
            return

        # Silence detected — process the buffer
        self.processing = True
        full_text = " ".join(self.buffer)
        self.buffer.clear()

        threading.Thread(target=self._process, args=(full_text,), daemon=True).start()

    def _process(self, text):
        """Process accumulated text: Claude → TTS → send."""
        try:
            tg_send_typing(self.chat_id)

            # Ask Claude
            response = ask_claude(self.citizen, text, self.citizens_dir)
            append_to_call(self.call_path, self.citizen, response)
            logger.info(f"@{self.citizen}: {response[:80]}")

            # TTS
            ogg_path = synthesize(response, self.voice_id)
            if ogg_path:
                tg_send_voice(self.chat_id, ogg_path, caption=response[:200])
            else:
                tg_send_text(self.chat_id, response)

        except Exception as e:
            logger.error(f"Process error: {e}")
            tg_send_text(self.chat_id, f"(error: {e})")
        finally:
            self.processing = False


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 voice_call_tg.py @citizen_handle")
        sys.exit(1)

    citizen = sys.argv[1].lstrip("@")

    # Resolve citizens dir
    citizens_dir = Path(os.environ.get("CITIZENS_DIR", ""))
    if not citizens_dir.is_dir():
        # Try sibling of mind-mcp
        for candidate in PROJECT_ROOT.parent.iterdir():
            test = candidate / "citizens" / citizen
            if test.is_dir():
                citizens_dir = candidate / "citizens"
                break

    if not citizens_dir.is_dir():
        print(f"Cannot find citizens directory with {citizen}")
        sys.exit(1)

    logger.info(f"Voice call with @{citizen}, citizens at {citizens_dir}")

    # Active calls: chat_id → VoiceCall
    calls = {}
    offset = 0

    while True:
        try:
            # Poll Telegram
            updates = tg_api("getUpdates", offset=offset, timeout=30, limit=10)
            for update in updates.get("result", []):
                offset = update["update_id"] + 1
                msg = update.get("message", {})
                chat_id = msg.get("chat", {}).get("id")
                if not chat_id:
                    continue

                # Start call on /start or first voice
                if chat_id not in calls:
                    calls[chat_id] = VoiceCall(citizen, chat_id, citizens_dir)
                    logger.info(f"Call started with chat {chat_id}")

                call = calls[chat_id]

                # Voice message
                voice = msg.get("voice") or msg.get("audio")
                if voice:
                    file_id = voice.get("file_id")
                    audio_bytes = tg_get_file(file_id)
                    if audio_bytes:
                        call.on_voice_message(audio_bytes)

                # Text message (also accepted)
                text = msg.get("text", "")
                if text and not text.startswith("/"):
                    call.buffer.append(text)
                    call.last_voice_time = time.time()
                    append_to_call(call.call_path, "human", text)

            # Check silence on all active calls
            for call in calls.values():
                call.check_silence()

        except Exception as e:
            logger.error(f"Poll error: {e}")
            time.sleep(5)

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
