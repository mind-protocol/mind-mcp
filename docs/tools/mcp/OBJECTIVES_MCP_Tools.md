# OBJECTIVES — MCP Tools

```
STATUS: STABLE
CREATED: 2025-12-24
VERIFIED: 2026-03-15 against bdaf2d0
```

---

## CHAIN

```
THIS:            OBJECTIVES_MCP_Tools.md (you are here - START HERE)
PATTERNS:       ./PATTERNS_MCP_Tools.md
BEHAVIORS:      ./BEHAVIORS_MCP_Tools.md
ALGORITHM:      ./ALGORITHM_MCP_Tools.md
VALIDATION:     ./VALIDATION_MCP_Tools.md
IMPLEMENTATION: ./IMPLEMENTATION_MCP_Tools.md
HEALTH:         ./HEALTH_MCP_Tools.md
SYNC:           ./SYNC_MCP_Tools.md

IMPL:           mcp/server.py
                mcp/tools/*_handler.py
```

**Read this chain in order before making changes.** Each doc answers different questions. Skipping ahead means missing context.

---

## PRIMARY OBJECTIVES (ranked)

1. **Unified cognitive interface** — 15 tools organized by function (THINK/ACT/SPEAK) give citizens a single coherent API for all interactions with the graph, other citizens, and external platforms.
2. **Graph as source of truth** — every tool reads from or writes to FalkorDB. No secondary databases, no local state that doesn't flow through the graph.
3. **Citizen autonomy** — citizens can think (query, reason), act (call, spawn, manage tasks, set alarms), and speak (send messages, generate media) without human intervention.
4. **Zero-LLM where possible** — subcall, subconscious responses, and graph queries operate on physics alone. LLM invocation is a last resort, not a default.
5. **Platform-agnostic communication** — send/read/media work identically across Telegram, Discord, WhatsApp, Twitter, Email, SMS.

## NON-OBJECTIVES

- **Cypher exposure** — citizens never write raw Cypher; all graph access through typed operations
- **Tool composition** — tools are atomic; multi-step workflows use procedures, not chained tool calls
- **Rate limiting** — the MCP layer has no rate limiting; compute budget lives in the orchestrator
- **Authentication** — MCP runs on stdio per-citizen; trust is identity-based, not token-based

## TRADEOFFS (canonical decisions)

- When latency conflicts with graph consistency, choose consistency.
- When tool simplicity conflicts with power, choose simplicity (add a new tool instead of overloading parameters).
- We accept embedding computation cost to preserve semantic search quality.
- We accept lazy-import overhead to keep startup fast and optional deps truly optional.

## SUCCESS SIGNALS (observable)

- All 15 tools respond within 5s under normal load
- graph_query returns relevant results in top-3 80%+ of the time
- call returns subconscious response within 2s when target has no LLM session
- send delivers to platform within 1s
- spawn completes full birth pipeline (brain + wallet + keys) in under 10s
