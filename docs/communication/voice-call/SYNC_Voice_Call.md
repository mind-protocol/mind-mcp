# Voice Call — Sync

```
LAST_UPDATED: 2026-03-19
UPDATED_BY: @dev
STATUS: IMPLEMENTED — not fully tested
```

## Current State

- `/call @citizen` in Telegram: implemented, wired into bridge
- `/call` default to partner: implemented, partner cache from profile.json
- Voice message STT (Whisper): implemented, not tested live
- Buffer + silence detection (4s): implemented, moved BEFORE group filter
- Claude -p processing: implemented, runs in citizen dir
- TTS response (ElevenLabs): implemented, not tested live
- Transcript file: implemented, writes to `citizens/{handle}/calls/live_{chat_id}.md`
- `/endcall`: implemented
- MCP `/call` tool (file watcher): implemented, separate from TG bridge
- Standalone `voice_call_tg.py`: implemented, alternative entry point
- `call_bridge_tg.py` / `call_bridge_wa.py`: implemented, file→platform bridges

## Recent Changes

| Date | Change |
|------|--------|
| 2026-03-18 23:30 | Created call_file_watcher.py (MCP /call tool) |
| 2026-03-18 23:35 | Created voice_call_tg.py (standalone script) |
| 2026-03-18 23:40 | Created call_bridge_tg.py + call_bridge_wa.py |
| 2026-03-18 23:45 | Integrated /call into telegram_bridge.py |
| 2026-03-19 00:25 | Fixed partner routing (@mind for NLR) |
| 2026-03-19 00:29 | Fixed call routing BEFORE group filter (messages were dropped) |
| 2026-03-19 00:35 | Created doc chain (this file) |

## Known Issues

- [ ] Silence threshold hardcoded at 4.0s — should be env var
- [ ] No latency tracking
- [ ] No stuck processing detection
- [ ] Voice messages not tested live (need OPENAI_API_KEY + ELEVENLABS_API_KEY)
- [ ] WhatsApp call not wired (only file bridge script exists)
- [ ] No health senses wired to graph
- [ ] `_active_calls` lost on server restart (ephemeral, by design)

## TODO

- [ ] Test live voice call end-to-end
- [ ] Wire H1-H6 health senses
- [ ] Add DOCS pointers in telegram_bridge.py source
- [ ] Make silence threshold configurable
- [ ] Add latency metrics
- [ ] Wire WhatsApp call into bridge (not just standalone script)
