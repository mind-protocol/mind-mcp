# Voice Call — Health

## Senses (continuous monitoring)

### H1: Call Transcript Written
**What**: Every human message and citizen response appears in the transcript file.
**How**: After each `_process_voice_call_buffer`, verify the transcript file has the expected new lines.
**Signal**: transcript_line_count increases by 2 (human + citizen) per exchange.
**Failure**: Lines missing → buffer processing failed silently.

### H2: STT Success Rate
**What**: Voice messages are successfully transcribed.
**How**: Count transcribe calls vs successful transcriptions.
**Signal**: success_rate > 0.9 (90%+ of voice messages produce text).
**Failure**: Whisper API down, OGG download failed, or audio too short.

### H3: TTS Success Rate
**What**: Citizen responses are successfully synthesized.
**How**: Count TTS calls vs successful audio files.
**Signal**: success_rate > 0.95 (text fallback catches the rest).
**Failure**: ElevenLabs API down, voice_id invalid, ffmpeg missing.

### H4: Response Latency
**What**: Time from silence detection to voice message sent.
**How**: timestamp diff between buffer flush and sendVoice.
**Signal**: p95 < 15s (Whisper ~2s + Claude ~5-10s + TTS ~2s + send ~1s).
**Failure**: > 30s means something is stuck (Claude timeout, API down).

### H5: Call Routing Correctness
**What**: Messages during active call are captured by call handler, not leaked to normal processing.
**How**: During active call, no messages should reach the normal enqueue path.
**Signal**: Zero messages enqueued while call is active for that chat_id.
**Failure**: Call routing is AFTER filters (the bug we just fixed).

### H6: Partner Resolution
**What**: `/call` without handle resolves to the correct partner citizen.
**How**: partner_cache maps telegram_id → citizen handle correctly.
**Signal**: Cache build logs show correct bonds. `/call` responds with correct citizen name.
**Failure**: Profile missing telegram_id, wrong human_partner field, or cache not rebuilt.

## Monitoring

| Check | Frequency | Source |
|-------|-----------|--------|
| Active calls count | Every poll (2s) | `len(_active_calls)` |
| Buffer size per call | Every poll | `len(call["buffer"])` |
| Processing flag stuck | Every 30s | `call["processing"]` True for > 60s = stuck |
| Transcript file growing | On each exchange | File mtime changes |

@mind:TODO Wire H1-H6 as continuous senses in the graph
@mind:TODO Add latency tracking (start_time in buffer, measure at send)
@mind:TODO Add stuck processing detection (watchdog thread)
