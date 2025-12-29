# SYNC: MCP Tools

```
LAST_UPDATED: 2025-12-29
UPDATED_BY: Claude (V2 documentation update)
STATUS: CANONICAL
```

---

## Current State

### V2 Interface (Canonical)

**graph_query:**
- Input: `queries` (array) + `intent` (optional string)
- Behavior: SubEntity exploration per query
- Output: Best narrative match with content

**procedure_start/continue/abort:**
- Structured dialogues via YAML procedures
- Session-based with atomic commit

**agent_list/spawn/status:**
- Work agent orchestration
- One agent running at a time

**doctor_check:**
- Health checks with agent assignment
- Auto-fix for small schema issues

**task_list:**
- Pending tasks grouped by objective

---

## Implemented Components

| Component | Status | Location |
|-----------|--------|----------|
| MCP Server | V2 | `mcp/server.py` |
| SubEntity exploration | Working | `runtime/physics/exploration.py` |
| SubEntity class | Working | `runtime/physics/subentity.py` |
| ConnectomeRunner | Working | `runtime/connectome/runner.py` |
| Session management | Working | `runtime/connectome/session.py` |
| Graph operations | Working | `runtime/physics/graph/` |
| Procedures | Working | `.mind/procedures/*.yaml` |

---

## Documentation Chain

| Doc | Status | Notes |
|-----|--------|-------|
| OBJECTIVES | V2 | Simplified query interface goals |
| PATTERNS | V2 | Two tools: graph_query + procedures |
| BEHAVIORS | V2 | Observable effects with GIVEN/WHEN/THEN |
| ALGORITHM | V2 | SubEntity exploration + procedure flow |
| VALIDATION | V2 | Invariants for all tool types |
| IMPLEMENTATION | V2 | Code structure and data flow |
| SYNC | V2 | This file |

---

## Key Changes (V2)

1. **Removed from graph_query:**
   - `top_k` - system determines
   - `expand` - always explores
   - `format` - always formatted response
   - `include_membrane` - separate concern

2. **Added to graph_query:**
   - `intent` - affects SubEntity traversal weights

3. **Link type:**
   - All links are `:link` type
   - No EXPRESSES, THEN, WITNESSED, etc.
   - Semantics in link properties

4. **Response format:**
   - Returns best narrative content
   - Cleaned of path artifacts
   - Prefers existing over crystallized

---

## Handoff

**For agents:**
- MCP tools: `mcp/server.py`
- SubEntity logic: `runtime/physics/subentity.py`
- Exploration orchestration: `runtime/physics/exploration.py`
- Procedures: `.mind/procedures/`

**For testing:**
```bash
# Test MCP server
python3 -m mcp.server

# Test graph_query via MCP
# Use mcp__mind__graph_query tool
```

---

## CHAIN

- **Prev:** IMPLEMENTATION_MCP_Tools.md
- **Doc root:** OBJECTIVES_MCP_Tools.md
