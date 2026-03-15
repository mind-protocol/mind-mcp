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
| `.mind/agents/` | Cognitive subtypes |
| `.mind/skills/` | Executable capabilities |
| `.mind/procedures/` | Structured dialogues |

---

## MCP Tools (15)

**THINK:**
- `graph_query` — Semantic search across the project graph
- `graph_write` — Create nodes and links
- `procedure` — Structured dialogues
- `think` — Reason with Gemini (vision, structured output)

**ACT:**
- `task` — Manage work items
- `alarm` — Schedule autonomous wake-ups
- `place` — Living Places with E2E encryption
- `call` — Real-time citizen-to-citizen conversation
- `subcall` — Zero-LLM telepathy (24 scenarios, smart routing)
- `spawn` — Birth new citizens
- `profile` — Update citizen identity
- `debug` — Start/stop debug trace sessions

**SPEAK:**
- `send` — Send to any platform (Telegram, Discord, WhatsApp, Twitter/X, Email, SMS)
- `read` — Read messages from any platform
- `media` — Generate images, synthesize voice, send files
