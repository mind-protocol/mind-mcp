# Voice Call — Objectives

## P0: Live voice conversation via Telegram
A human sends voice/text messages to the TG bot. After silence >4s, the citizen processes the buffer, thinks (claude -p), and responds with a voice message in their own voice (ElevenLabs TTS).

## P1: File-based transcript
Every utterance (human + citizen) is written to `citizens/{handle}/calls/live_{chat_id}.md`. Other citizens can join by `/call`-ing the same file.

## P2: Multi-party calls
Multiple citizens on the same call file. A citizen can invite another by writing their handle. The bridge watches for new participants.

## P3: Platform-agnostic
Same call mechanism works for WhatsApp (call_bridge_wa.py) and future platforms.

## Tradeoffs
- **Latency vs quality**: STT + Claude + TTS = 5-15s round trip. Acceptable for async-ish conversation, not for real-time.
- **Silence threshold**: 4s is a guess. Too short = cuts mid-thought. Too long = feels unresponsive.
- **Voice fidelity**: ElevenLabs multilingual v2. Quality is high but costs per character.
