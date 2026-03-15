# MCP Tools — Algorithm: Tool Dispatch and Execution Logic

```
STATUS: STABLE
CREATED: 2025-12-24
VERIFIED: 2026-03-15 against bdaf2d0
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_MCP_Tools.md
BEHAVIORS:       ./BEHAVIORS_MCP_Tools.md
PATTERNS:        ./PATTERNS_MCP_Tools.md
THIS:            ALGORITHM_MCP_Tools.md (you are here)
VALIDATION:      ./VALIDATION_MCP_Tools.md
HEALTH:          ./HEALTH_MCP_Tools.md
IMPLEMENTATION:  ./IMPLEMENTATION_MCP_Tools.md
SYNC:            ./SYNC_MCP_Tools.md

IMPL:            mcp/server.py
                 mcp/tools/*_handler.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

The MCP server receives JSON-RPC requests on stdin, dispatches to 15 tool handlers via a static lookup table, and returns responses on stdout. Each handler is a pure function: `(args, ctx?) → response`. The server manages graph connections, procedure runner, and capability manager as shared state in `ServerContext`.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| Unified cognitive interface | B1, B3, B5 | Dispatch routes any tool to its handler in O(1) |
| Zero-LLM where possible | B2 | subcall algorithm uses physics, not LLM |
| Graph as source of truth | B1, B4 | All tools read/write through GraphOps |

---

## ALGORITHM: Tool Dispatch

### Step 1: Parse Request

JSON-RPC request arrives on stdin. Extract `method`, `params`, `id`.

### Step 2: Route Method

```
IF method == "initialize":     → return protocol version + capabilities
IF method == "tools/list":     → return TOOL_SCHEMAS array
IF method == "tools/call":     → dispatch to handler
ELSE:                          → error -32601 (method not found)
```

### Step 3: Dispatch Tool

```
tool_name = params["name"]
handler_fn, needs_ctx = TOOL_DISPATCH[tool_name]

IF needs_ctx:
    result = handler_fn(args, server.ctx)
ELSE:
    result = handler_fn(args)
```

Stateless tools (think, send, read, media, alarm) don't need `ServerContext`.

---

## ALGORITHM: graph_query

### Step 1: Resolve Actor

From args or detect from env/cwd/graph HUMAN lookup.

### Step 2: Run Concurrent Exploration

```
FOR EACH query IN queries (parallel via asyncio.gather):
    1. Create Moment node for the query
    2. Link Moment to actor
    3. Run SubEntity exploration:
       - Embed query text
       - Traverse graph following highest-scored links
       - Track satisfaction (increases on narrative finds)
       - Stop on satisfaction > threshold OR max steps
    4. Format results via cluster_presentation
```

### Step 3: Return Results

Markdown-formatted cluster with node content, alignment scores, and connected nodes.

---

## ALGORITHM: subcall (Zero-LLM Telepathy)

### Step 1: Build Stimulus

```
stimulus = {
    query_text,
    caller_wm_nodes (top 3-5),
    scenario_limbic_profile (arousal, drives)
}
```

### Step 2: Select Targets

```
IF target == "@handle":     → single citizen
IF target == "team":        → all linked citizens
IF target == "trade:X":     → all with role X
IF target == "random:N":    → random sample of N
IF target omitted:          → auto-select 3-5 diverse citizens
```

### Step 3: Inject and Read Resonance

```
FOR EACH target citizen:
    1. Connect to brain_{handle} graph
    2. Embed stimulus text
    3. Find resonating nodes (vector similarity)
    4. Read limbic state (arousal, drives)
    5. Compute thermodynamic resonance formula
    6. Return: activated nodes, emotional response, images
```

### Step 4: Aggregate

```
IF mode == "best":     → return strongest single resonance
IF mode == "top3":     → return top 3 citizens
IF mode == "all":      → return every citizen who resonated
IF mode == "centroid": → compute average across all
```

---

## ALGORITHM: call

### Step 1: Create Room

Generate room_id, create temporary Space node, join caller and target.

### Step 2: Send Opening Message

Create Moment node with caller's message, link to room.

### Step 3: Notify Target

```
IF target is human:          → send Telegram notification
IF target has active session: → inject into pending_messages_{session_id}.txt
ELSE:                         → queue wake-up in message_queue.jsonl
```

### Step 4: Get Subconscious Response

```
result = invoke_subconscious(message, target_handle)
IF result:
    create response Moment in room (subconscious=true)
```

---

## ALGORITHM: spawn

### Step 1: Generate Identity

handle = lowercase(name), citizen_id = f"citizen_{handle}_{uuid[:8]}"

### Step 2: Generate Cryptographic Material

Solana Ed25519 wallet + RSA-2048 keypair. Private keys stored at `.keys/{handle}/` with mode 0o400.

### Step 3: Build Seed Brain

Load 209-node base brain from `data/base_seed_brain.json`. Add overlay nodes: citizen_identity, founding_purpose, parent actors.

### Step 4: Persist

Brain → FalkorDB (`brain_{handle}` graph). Profile → `citizens/{handle}/profile.json`. CLAUDE.md → citizen dir. first_boot.json → citizen dir.

---

## DATA FLOW

```
stdin (JSON-RPC)
    ↓
MindServer.handle_request()
    ↓
TOOL_DISPATCH lookup
    ↓
handler_fn(args, ctx?)
    ↓
GraphOps / bridges / APIs
    ↓
{"content": [{"type": "text", "text": "..."}]}
    ↓
stdout (JSON-RPC response)
```

---

## KEY DECISIONS

### D1: Shared vs Per-Request httpx Client

```
IF engine proxy is called:
    use shared _httpx_client (lazy-init singleton)
    WHY: avoid connection overhead per request
```

### D2: Subconscious Before LLM

```
IF call target has no active LLM session:
    invoke_subconscious() returns graph physics response
    WHY: zero tokens, instant, always available
ELSE:
    inject into active session for full LLM response
```

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| `runtime/physics/graph/GraphOps` | add_narrative, add_moment, _query | Node/link creation, Cypher results |
| `runtime/explore_cmd` | run_exploration | ExplorationResult with narratives |
| `runtime/connectome/runner` | start, continue_session, abort | Procedure session state |
| `runtime/identity` | resolve_actor_id | Canonical actor ID |
| `google.genai` | generate_content | Gemini response text |
| Platform bridges | send_as_citizen, read_channel | Message delivery/retrieval |
