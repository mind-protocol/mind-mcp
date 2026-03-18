# Voice Call — Validation

## Invariants

### MUST
- Call routing MUST execute BEFORE group filter and rate limiting in process_update()
- Every human utterance MUST be written to the transcript file before processing
- Every citizen response MUST be written to the transcript file after processing
- Buffer MUST be cleared atomically when processing starts (no partial reads)
- Silence threshold MUST be configurable (currently hardcoded at 4.0s)
- Voice ID MUST resolve from profile.json or env var — never fall back to a wrong voice
- Claude MUST run in the citizen's directory (`cwd=citizens/{handle}/`)
- TTS failures MUST fall back to text (never silent)

### NEVER
- NEVER process buffer while already processing (processing flag prevents re-entry)
- NEVER persist call state to disk — calls are ephemeral, transcript is the record
- NEVER send a response without writing it to the transcript first
- NEVER drop a voice message silently — log errors, notify user
- NEVER allow a call to block the main polling loop (always background thread)

## Test Scenarios

### T1: Basic text call
```
/call @mind → "Voice call started"
send "hello" → buffer captures → silence 4s → claude responds → voice message returned
/endcall → "Call ended"
```

### T2: Multi-message buffer
```
send "first part"
send "second part"  (within 4s)
silence 4s → both messages processed together as one prompt
```

### T3: Voice message
```
send voice message → Whisper transcribes → buffer captures → silence → process
```

### T4: Restart resilience
```
server restarts during call → _active_calls lost → user sends /call again → new session
transcript file still exists from before restart
```

### T5: Default partner
```
NLR sends /call (no handle) → partner cache resolves → @mind → call starts
```

@mind:TODO Implement automated test runner for T1-T5
@mind:TODO Make silence threshold configurable via env var MIND_CALL_SILENCE_THRESHOLD
