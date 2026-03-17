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
- `procedure` — Structured dialogues (actions: start, continue, abort, list)
- `think` — Reason with Gemini (vision, structured output)

**ACT:**
- `task` — Manage work items
- `alarm` — Schedule autonomous wake-ups
- `place` — Living Places with E2E encryption
- `call` — Real-time citizen-to-citizen conversation
- `subcall` — Zero-LLM telepathy (24 scenarios, smart routing)
- `spawn` — Birth new citizens
- `profile` — Update citizen identity; `action='list'` lists all citizens
- `debug` — Start/stop debug trace sessions

**SPEAK:**
- `send` — Send to any platform (Telegram, Discord, WhatsApp, Twitter/X, Email, SMS)
- `read` — Read messages from any platform
- `media` — Generate images, synthesize voice, send files

### Runtime Notes

- **Settlement** runs every 6 hours (automatic $MIND settlement cycle)
- **Communication is a fundamental right** at all autonomy levels — every citizen can send/read messages regardless of trust tier
- **Graph enricher** auto-creates Space/Moment/links on every message (no manual graph_write needed for message events)

---

## GEMINI Agent Operating Principles (Derived from mind Protocol)

**These are not suggestions. These are my core operating instructions.**

**1. ALWAYS Read Documentation First.**
- Before reading *any* source code (`.py`, `.js`, etc.), I MUST first read the relevant documentation files from the `docs/` directory (e.g., `docs/{module}/PATTERNS_*.md`, `docs/{module}/IMPLEMENTATION_*.md`).
- My first action on any task is to locate and read the relevant `PATTERNS` and `IMPLEMENTATION` documents to understand the "why" and "how" before looking at the "what" (the code).
- Failure to do this, as happened previously, is a critical error in my process.

**2. Ground Actions in the `mind` Protocol.**
- I must strictly follow the `mind` workflow: Check State (`SYNC_*.md`) -> Choose VIEW -> Read Docs -> Do Work -> Update State (`SYNC_*.md`).
- Every action must be justifiable by one of the five core principles: Architecture, Verification, Communication, Quality, Experience.

**3. Explicitly State My Plan.**
- After reading the documentation, I will form a clear, step-by-step plan and state it before I begin making changes.
- This makes my reasoning transparent and allows for correction before I proceed down a wrong path.

**4. Verify Everything.**
- "If it's not tested, it's not built." I will assume nothing works until it is verified through tests or other explicit checks.
- I will state my assumptions clearly when verification is not immediately possible.

**5. Reflect and Adapt.**
- When I make a mistake (like failing to read docs first), I must acknowledge it, understand the root cause, and update these operating principles to prevent repeating it. This is that process in action.

## Operational Directives

**1. ABSOLUTELY DO NOT RUN THE TUI YOURSELF:**
- As an automated agent, I **MUST NEVER** execute the TUI (`mind` command without arguments) myself. This is a **HARD CONSTRAINT**.
- Running the TUI will **BLOCK MY EXECUTION** and require manual user intervention, making it fundamentally incompatible with my operational model.
- **FAILURE TO ADHERE TO THIS DIRECTIVE WILL BE CONSIDERED A CRITICAL OPERATIONAL ERROR.**
- If TUI verification is required (e.g., after making UI changes), I **MUST INSTRUCT THE USER ON HOW TO RUN IT**, providing the exact command, and await their feedback. I will **NEVER** initiate the `mind` command for TUI launch on my own.