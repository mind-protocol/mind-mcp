# Agent System — Objectives

```
STATUS: CANONICAL
UPDATED: 2025-12-30
```

---

## Primary Objective

Enable AI agents to autonomously detect and fix project issues while maintaining full observability of their actions.

---

## Ranked Goals

1. **Autonomous Execution** — Agents work independently after task assignment
2. **Full Observability** — Every agent action is captured in the graph
3. **Session Awareness** — Know which agents are running at any moment
4. **Conversation Memory** — Agent reasoning preserved for debugging/learning
5. **Context Tracking** — Agent's working directory and focus maintained

---

## Tradeoffs

| Decision | Chosen | Alternative | Rationale |
|----------|--------|-------------|-----------|
| Session detection | File-based (.sessionId) | Process monitoring | Simpler, works across restarts |
| Conversation storage | Batched moments | Single large moment | Manageable moment sizes |
| Turn grouping | 5 per batch | Dynamic sizing | Predictable, easy to navigate |
| Tool output | Truncate to 200 chars | Full capture | Avoid moment explosion |
| Thinking blocks | Full capture | Truncate | Reasoning is valuable |

---

## Non-Goals

- Real-time streaming of agent output (batch capture is sufficient)
- Cross-agent communication (agents work independently)
- Agent training from conversation history (future consideration)
