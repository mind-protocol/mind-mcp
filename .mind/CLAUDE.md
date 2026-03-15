# {{PROJECT_NAME}}

@.mind/PRINCIPLES.md

---

@.mind/FRAMEWORK.md

---

## Before Any Task

Check project state:
```
.mind/state/SYNC_Project_State.md
```

Understand what's happening, what changed recently, any handoffs for you.

## After Any Change

Update `.mind/state/SYNC_Project_State.md` with what you did.

---

## Architecture

This project operates within the Mind Protocol 4-layer architecture:

| Layer | Role | This Project |
|-------|------|--------------|
| L1 | Citizen | Personal graph, memory |
| L2 | Organization | Team coordination |
| L3 | Ecosystem | Shared templates |
| L4 | Protocol | Schema, registry, laws |

Templates come from `mind-platform/templates/` via `mind init`.

---

## Key Files

| File | Purpose |
|------|---------|
| `.mind/FRAMEWORK.md` | Navigation, structure, what to load |
| `.mind/PRINCIPLES.md` | How to work, stance to hold |
| `.mind/state/SYNC_Project_State.md` | Current state, handoffs |
| `.mind/skills/` | Executable capabilities |
| `.mind/procedures/` | Structured dialogues |

---

## MCP Tools (THINK / ACT / SPEAK)

15 tools organized by verb:

**THINK** — knowledge & reasoning:
- `graph_query(queries=[...])` — semantic search across the knowledge graph
- `graph_write(node_type, content, link_to=[...])` — create nodes and links
- `procedure(action=list|start|continue|abort)` — structured dialogues
- `think(message, images=[...], json_mode)` — consult Gemini for reasoning/vision

**ACT** — work & coordination:
- `task(action=list|claim|complete|fail)` — manage tasks
- `alarm(action=set|list|cancel)` — autonomous wake scheduling
- `place(action=join|speak|listen|leave|create|grant_access|revoke_access)` — living places
- `call(target, message)` — instant citizen-to-citizen call (temp room + subconscious)
- `subcall(query, target?)` — zero-LLM subconscious query to another citizen's graph
- `spawn(name, intent, parents=[...])` — birth a new AI citizen
- `profile(action=get|update, bio, tags, emoji, ...)` — update citizen profile
- `debug(action=start|stop|list)` — trace sessions with @traceable functions

**SPEAK** — outward communication:
- `send(platform, message, chat_id)` — send to Telegram/Discord/WhatsApp/Twitter/Email/SMS
- `read(action=history|mentions|inbox, platform)` — read messages from any platform
- `media(action=imagine|speak|send_file)` — image gen (Gemini/Ideogram), TTS (ElevenLabs), file send


---

# mind CLAUDE.md Template

**Note:** This file is for reference only. The actual CLAUDE.md content is built
programmatically by `init_cmd.py`, which inlines the full content of PRINCIPLES.md
and PROTOCOL.md directly (since Claude doesn't expand @ references).

The generated CLAUDE.md includes:
1. Full PRINCIPLES.md content (inlined)
2. Full PROTOCOL.md content (inlined)
3. Quick reference for VIEWs and SYNC files

See `mind/init_cmd.py:_build_claude_addition()` for the actual template.
