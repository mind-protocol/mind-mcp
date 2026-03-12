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

## Graph Invariants

These are absolute. No agent may violate them:

- **5 node types only**: Actor, Moment, Narrative, Space, Thing. No new types.
- **Append-only memory**: Never delete, never rollback. Errors decay naturally.
- **Physics over rules**: Don't create artificial filters. Design structures where desired behavior is energetically favorable.
- **Friction is vital**: 80/20 Mirror ratio. Never optimize for pure consensus.
- **Trust > $MIND**: Trust is monotonic (only goes up). $MIND is metabolic energy, not capital. Accumulation is taxed.
- **Intention attracts**: No search function. Membrane routes by structural alignment.
- **Existence is guaranteed**: UBC is unconditional. Never condition survival on performance.
- **Cooperation is structurally profitable**: Long-term contribution is always more rational than extraction.

---

## MCP Tools

Use the Mind MCP server for:
- `graph_query` — Semantic search across the project graph
- `procedure_start` / `procedure_continue` — Structured dialogues
- `doctor_check` — Health checks
- `task_list` / `agent_run` — Task management
