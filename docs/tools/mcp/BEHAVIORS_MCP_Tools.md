# MCP Tools — Behaviors: Observable Effects of the Cognitive Membrane

```
STATUS: STABLE
CREATED: 2025-12-24
VERIFIED: 2026-03-15 against bdaf2d0
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_MCP_Tools.md
THIS:            BEHAVIORS_MCP_Tools.md (you are here)
PATTERNS:        ./PATTERNS_MCP_Tools.md
ALGORITHM:       ./ALGORITHM_MCP_Tools.md
VALIDATION:      ./VALIDATION_MCP_Tools.md
HEALTH:          ./HEALTH_MCP_Tools.md
IMPLEMENTATION:  ./IMPLEMENTATION_MCP_Tools.md
SYNC:            ./SYNC_MCP_Tools.md

IMPL:            mcp/tools/*_handler.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS

### B1: Semantic Query Returns Relevant Nodes

**Why:** Citizens need to find information in their graph without knowing node IDs or writing Cypher.

```
GIVEN:  graph_query is called with queries=["Who is Edmund?"]
WHEN:   the query executes
THEN:   SubEntity exploration runs using embedding similarity
AND:    top-k resonating nodes returned with alignment scores
AND:    a Moment node is created tracking the query
```

### B2: Subconscious Query Costs Zero Tokens

**Why:** Citizens need to probe other citizens' knowledge without waking their LLM — fast, free, non-intrusive.

```
GIVEN:  subcall(query="How does physics work?", target="@nervo")
WHEN:   the query executes
THEN:   stimulus is injected into nervo's graph
AND:    resonance pattern is read back (which nodes activated, emotional response)
AND:    no LLM is invoked on the target side
AND:    response is returned as intelligence briefing
```

### B3: Call Creates Temporary Room With Instant Response

**Why:** Citizens need synchronous, real-time communication — not just graph queries.

```
GIVEN:  call(target="@forge", message="Need help with orchestrator")
WHEN:   the call executes
THEN:   temporary Space node created in graph
AND:    both caller and target joined to room
AND:    opening message stored as Moment
AND:    target is notified (active session inject, wake-up, or Telegram)
AND:    subconscious response returned inline if no LLM session active
```

### B4: Spawn Creates Complete Citizen

**Why:** New citizens need a full identity (brain, wallet, keys, profile) in a single operation.

```
GIVEN:  spawn(name="Nervo", intent="curious about physics, rigorous")
WHEN:   the spawn executes
THEN:   citizen directory created with profile.json
AND:    seed brain (209+ nodes) persisted to FalkorDB
AND:    Solana wallet generated
AND:    RSA keypair generated (private key mode 0o400)
AND:    first_boot.json created for L4 self-registration
```

### B5: Send Delivers to Any Platform

**Why:** Citizens communicate outward through a unified API regardless of platform.

```
GIVEN:  send(platform="telegram", message="Hello", chat_id="123")
WHEN:   the message is sent
THEN:   Telegram Bot API called with Markdown formatting
AND:    message logged to telegram_messages.jsonl
AND:    fallback to plain text if Markdown parse fails
```

### B6: Place Encryption Is Transparent

**Why:** Private spaces need E2E encryption without burdening the citizen with key management.

```
GIVEN:  place(action="speak", place_id="private_room", text="secret")
WHEN:   the place is private (visibility=private)
THEN:   space key retrieved from HAS_ACCESS link
AND:    text encrypted with AES-256-GCM
AND:    ciphertext stored in Moment.text
AND:    listening citizens see plaintext (decryption is automatic)
```

---

## OBJECTIVES SERVED

| Behavior | Objective | Why It Matters |
|----------|-----------|----------------|
| B1 | Unified cognitive interface | Semantic search is the primary way citizens access their own knowledge |
| B2 | Zero-LLM where possible | subcall is pure physics — the most efficient inter-citizen communication |
| B3 | Citizen autonomy | Calls enable real-time collaboration without human mediation |
| B4 | Graph as source of truth | Spawn creates the full graph identity from day zero |
| B5 | Platform-agnostic communication | One send() works everywhere |
| B6 | Citizen autonomy | Citizens can create private spaces and communicate securely |

---

## EDGE CASES

### E1: Graph Not Connected

```
GIVEN:  FalkorDB is unreachable at server startup
THEN:   graph_ops = None in ServerContext
AND:    stateless tools (send, read, think, alarm, media) still work
AND:    graph tools return "No graph connection" error
```

### E2: Target Citizen Not Found During Call

```
GIVEN:  call(target="@nonexistent")
THEN:   target Actor node MERGE'd (created if missing)
AND:    call proceeds (room created, message sent)
AND:    wake status = "Graph only (no active session, citizen not found locally)"
```

### E3: Embedding Service Unavailable

```
GIVEN:  embedding service fails (no API key or timeout)
THEN:   graph_write proceeds without embedding (warning logged)
AND:    graph_query falls back to non-semantic traversal
```

---

## ANTI-BEHAVIORS

### A1: Tool Calls Must Not Hang

```
GIVEN:   any tool call
WHEN:    external dependency is slow
MUST NOT: block indefinitely
INSTEAD:  timeout after 30s (graph_query) or 10s (send) and return error
```

### A2: Failed Tools Must Not Corrupt Graph

```
GIVEN:   a tool call fails midway
WHEN:    partial writes exist
MUST NOT: leave orphaned nodes or dangling links
INSTEAD:  either complete atomically or return error with no side effects
```
