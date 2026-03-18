# Voice Call — Patterns

## Design: Buffer → Silence → Process → Respond

The call is NOT real-time streaming. It's chunked:
1. Human sends voice messages (can be multiple back-to-back)
2. Messages are transcribed (Whisper) and accumulated in a buffer
3. When silence >4s is detected, the buffer is flushed
4. The full buffer is sent to `claude -p` in the citizen's directory
5. Claude's response is synthesized (ElevenLabs TTS)
6. Voice message sent back to Telegram

This is closer to walkie-talkie than phone call.

## Design: Call = File

The transcript file (`citizens/{handle}/calls/live_{chat_id}.md`) is the single source of truth. Format:
```
[HH:MM:SS] @human: transcribed text
[HH:MM:SS] @citizen: response text
```

Any process can read/write this file. The MCP `/call` tool watches it. The TG bridge writes to it. They don't need to know about each other.

## Design: Active Call State in Memory

`_active_calls` dict in the Telegram bridge process. Key = chat_id. Lost on restart. This is acceptable because:
- Calls are ephemeral (minutes, not hours)
- The transcript file persists regardless
- The human can `/call` again to restart

## Dependencies
- OpenAI Whisper API (STT)
- ElevenLabs API (TTS)
- ffmpeg (MP3→OGG conversion)
- Claude CLI (`claude -p`)
- Telegram Bot API

## Anti-patterns avoided
- No WebSocket streaming (too complex for MVP)
- No real-time VAD (voice activity detection) — uses message-level chunking
- No persistent call state (memory only, no DB)
