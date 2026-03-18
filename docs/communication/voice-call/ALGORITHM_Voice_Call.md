# Voice Call — Algorithm

## Telegram Bridge Integration

```
process_update(update):
    extract chat_id, text, voice from message

    IF chat_id in _active_calls:
        IF voice message:
            download → transcribe (Whisper) → buffer.append(transcript)
            last_voice = now()
            RETURN handled

        IF text (not /command):
            buffer.append(text)
            last_voice = now()
            RETURN handled

        IF text == "/endcall":
            _handle_endcall(chat_id)
            RETURN handled

    ... normal message processing continues ...
```

## Silence Detection (in polling loop)

```
_listener_loop():
    WHILE running:
        poll_updates()
        process_each(update)

        FOR each active_call:
            IF buffer non-empty AND not processing:
                IF now() - last_voice > 4.0s:
                    SPAWN thread → _process_voice_call_buffer(chat_id)

        sleep(poll_interval)  # 2s
```

## Buffer Processing

```
_process_voice_call_buffer(chat_id):
    call = _active_calls[chat_id]
    call.processing = True

    full_text = " ".join(call.buffer)
    call.buffer.clear()

    # Write human turn to transcript
    append_to_file(call.call_path, f"@human: {full_text}")

    # Think
    send_typing(chat_id)
    response = subprocess.run(["claude", "-p", full_text], cwd=citizen_dir)

    # Write citizen turn to transcript
    append_to_file(call.call_path, f"@{citizen}: {response}")

    # Speak
    mp3 = elevenlabs_tts(response, voice_id)
    ogg = ffmpeg_convert(mp3, opus)
    telegram_send_voice(chat_id, ogg, caption=response[:200])

    call.processing = False
```

## Partner Resolution

```
/call (no handle):
    _build_partner_cache()  # scan all citizen profiles once
    partner = _partner_cache[user_telegram_id]
    IF partner: start_call(partner)
    ELSE: "No partner found"
```

Partner cache: scan `{CITIZENS_DIR}/*/profile.json`, find AI citizens with `relationships.human_partner` set, reverse-map the human's `telegram_id` to the AI citizen handle.
