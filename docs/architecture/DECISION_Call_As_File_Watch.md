# DECISION: Call = File Watch

DATE: 2026-03-18
DECIDED_BY: NLR
STATUS: CANONICAL
SUPERSEDES: MCP call tool (direct citizen invocation)

## What /call Does

/call "path/file.md": write to file → background → watch for modifications → return diffs → back to background.

Multiple actors can call the same location. Can call a folder. TG/WH routes to citizen's default folder, prefers active calls. Diffs spoken with citizen's voice (TTS).

A call is not an invocation. A call is a shared place where actors write and listen.
