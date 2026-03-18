# Voice Call — Behaviors

## B1: Start Call
GIVEN human sends `/call` or `/call @citizen` in Telegram
WHEN the citizen exists in CITIZENS_DIR
THEN a call transcript file is created at `citizens/{citizen}/calls/live_{chat_id}.md`
AND `_active_calls[chat_id]` is registered
AND bot responds "Voice call with @citizen started"

## B2: Voice Message During Call
GIVEN an active call exists for this chat_id
WHEN human sends a voice message
THEN the voice is downloaded from Telegram
AND transcribed via Whisper API
AND the transcript is appended to the buffer
AND `last_voice` timestamp is updated
AND the message is logged as "Call voice: {text}"

## B3: Text Message During Call
GIVEN an active call exists for this chat_id
WHEN human sends a text message (not starting with /)
THEN the text is appended to the buffer
AND `last_voice` timestamp is updated

## B4: Silence Detection → Process
GIVEN buffer is non-empty AND processing is False
WHEN `time.now() - last_voice > 4.0 seconds`
THEN a background thread is spawned
AND the buffer is joined into a single text
AND the text is written to the transcript: `[HH:MM:SS] @human: {text}`
AND `claude -p {text}` is run in `citizens/{citizen}/`
AND the response is written to the transcript: `[HH:MM:SS] @citizen: {response}`
AND the response is synthesized via ElevenLabs TTS
AND the voice message is sent back to Telegram

## B5: End Call
GIVEN an active call exists
WHEN human sends `/endcall`
THEN `--- Call ended ---` is written to transcript
AND `_active_calls[chat_id]` is removed
AND bot responds "Call ended"

## B6: Default Partner
GIVEN human sends `/call` without a handle
WHEN a partner bond exists (profile.json `relationships.human_partner`)
THEN the call starts with the bonded citizen

## B7: Call Routing Priority
GIVEN call routing check runs BEFORE group filter
WHEN any message arrives for a chat_id with an active call
THEN it is captured by the call handler
AND normal message processing is skipped
