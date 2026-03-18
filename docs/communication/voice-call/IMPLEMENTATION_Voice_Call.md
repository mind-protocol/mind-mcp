# Voice Call — Implementation

## Files

| File | Purpose |
|------|---------|
| `runtime/bridges/telegram_bridge.py` | Call routing, buffer management, silence detection, TTS response |
| `scripts/voice_call_tg.py` | Standalone voice call script (alternative to bridge integration) |
| `scripts/call_bridge_tg.py` | File watcher → TG bridge (watches call files, sends TTS diffs) |
| `scripts/call_bridge_wa.py` | File watcher → WA bridge (same for WhatsApp) |
| `mcp/tools/call_file_watcher.py` | MCP `/call` tool — file-based write/watch/diff |

## Code → Doc Pointers

In `telegram_bridge.py`:
```python
# DOCS: docs/communication/voice-call/PATTERNS_Voice_Call.md
# DOCS: docs/communication/voice-call/ALGORITHM_Voice_Call.md
```

## Key Symbols

| Symbol | File | Purpose |
|--------|------|---------|
| `_active_calls` | telegram_bridge.py | In-memory dict: chat_id → call state |
| `_handle_voice_call()` | telegram_bridge.py | /call command handler |
| `_handle_endcall()` | telegram_bridge.py | /endcall command handler |
| `_process_voice_call_buffer()` | telegram_bridge.py | Buffer → Claude → TTS → send (runs in thread) |
| `_build_partner_cache()` | telegram_bridge.py | Scan profiles for partner bonds |
| `handle_call_file_watcher()` | call_file_watcher.py | MCP /call tool entry point |
| `VoiceCall` | voice_call_tg.py | Standalone call session manager |

## Data Flow

```
Telegram voice message
  → getFile API → download OGG
    → _transcribe_voice (Whisper API) → text
      → buffer.append(text)
        → silence 4s detected
          → _process_voice_call_buffer (background thread)
            → write to transcript file
            → claude -p {text} (cwd=citizen dir)
            → response text
            → _generate_voice_note (ElevenLabs) → MP3
            → ffmpeg → OGG (opus)
            → sendVoice API → Telegram
            → write response to transcript file
```

## External Dependencies

| Dependency | Purpose | Env Var |
|------------|---------|---------|
| OpenAI Whisper | STT | OPENAI_API_KEY |
| ElevenLabs | TTS | ELEVENLABS_API_KEY |
| ffmpeg | MP3→OGG | (system binary) |
| Claude CLI | Citizen thinking | (PATH) |
| Telegram Bot API | Messaging | TELEGRAM_BOT_TOKEN |

@mind:TODO Add DOCS comments to telegram_bridge.py source code
