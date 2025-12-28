# Handoff — Rolling Window Architecture

```
CREATED: 2024-12-16
UPDATED: 2025-12-19
STATUS: Decision made, awaiting implementation
FOR: Backend developer
```

---

## Summary

Pre-generate one layer of clickable responses. As the player clicks, generate the next layer in the background and push updates via SSE. This avoids combinatorial explosion while keeping interactions instant.

---

## Core Decisions

- Use SSE for server -> client updates.
- Click actions remain HTTP POST.
- Cache scene trees per session; patch as new responses arrive.

---

## Interfaces (Minimal)

```
POST /api/scene/click
GET  /api/scene/stream  (SSE)
GET  /api/scene/{scene_id}
```

---

## Next Steps

1. Implement SSE endpoint and click handler.
2. Add background generation queue.
3. Frontend: patch scene tree from SSE events.

---

Full detail archived in `docs/agents/narrator/archive/SYNC_archive_2024-12.md`.
