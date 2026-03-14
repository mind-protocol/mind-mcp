---
name: ecosystem_map_2026_03
description: Complete org map — universes, products, infra, archive status as of 2026-03-13. mind-mcp is becoming the universal citizen runtime.
type: project
---

## Org Map (confirmed 2026-03-13)

### Universes (each has citizens, physics, its own graph)

| Repo | Universe | Notes |
|------|----------|-------|
| venezia | 1525 Venice | serenissima migrating in. Venice Values. |
| the-blood-ledger | Blood Ledger | Adventure/sport. No Venice Values. Healthy breaks. |
| lumina-prime (new) | Lumina Prime | Futuristic AI city. Home for non-historical citizens. |
| contre-terre | Universe #4 | Was "the book", now becoming a universe. Lead documenting with 8 parallel sessions. |

### Products

| Repo | What |
|------|------|
| mind-app | Android + iPhone |
| mind-desktop | Desktop app (absorbing duoai — not done yet) |
| mind-platform | Web platform + L4 registry |
| mind-movie | Documentary/film |
| scopelock | Separate product |
| graphcare | Future product |
| scisense | Future product |
| babys | Future product |
| catland | Future product |
| playwise | Future product |
| beatfoundry | Music product |
| hri | HRI product |
| sillage | Future product |
| reynolds-vinet | Future product |
| synthetic-souls | Alive (canonical name, merge synthetics-souls into it) |

### Infrastructure / Core

| Repo | What | Notes |
|------|------|-------|
| **mind-mcp** | Universal citizen runtime — MCP + orchestrator + physics + membrane | THIS repo. Becoming the citizen home. |
| mind-ops | Team private ops — billing, wallets, secrets, infra, membrane routing, DeFi tooling | Must be private. Should absorb fluxbeam/meteora-*/raydium-*/lp-lock/mind-lp/mind-contracts |
| cities-of-light | Physics spec + docs | Code absorbed into mind-mcp |
| ngram | Context protocol | |

### Archive

| Repo | Why |
|------|-----|
| manemus | Orchestrator + bridges absorbed into mind-mcp |
| serenissima | Migrated to venezia |
| mind-protocol | Legacy website (replaced by mind-platform) |
| mind-protocol_legacy | Explicitly legacy |
| mind-protocol-org | Old org config |
| strange-loop, strange-loop-2 | Old experiments |
| FalkorDB-MCPServer, codex-mcp-gateway | Forks |
| mind-cognition | To delete |

### NOT yet archivable
- duoai — absorption into mind-desktop not done yet

## The Big Architectural Move

mind-mcp becomes the universal citizen runtime by absorbing:
1. From manemus: orchestrator, bridges (TG, WhatsApp, Twitter), account balancer, voice server
2. From cities-of-light: physics engine (tick_v1_2, phases, constants)
3. Adding: HTTP membrane endpoint (not just stdio MCP), L4 registry lookup for routing

**Why:** mind-mcp becomes deployable as a Render service — one instance per "citizen home." Each home runs N citizens with their own .mind/citizens/, graph, keys.

**How to apply:** All architecture decisions should move toward this consolidation. Don't build new infra in manemus or cities-of-light.
