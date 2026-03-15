# MCP Tools — Validation: What Must Be True

```
STATUS: STABLE
CREATED: 2025-12-24
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_MCP_Tools.md
PATTERNS:        ./PATTERNS_MCP_Tools.md
BEHAVIORS:       ./BEHAVIORS_MCP_Tools.md
THIS:            VALIDATION_MCP_Tools.md (you are here)
ALGORITHM:       ./ALGORITHM_MCP_Tools.md
IMPLEMENTATION:  ./IMPLEMENTATION_MCP_Tools.md
HEALTH:          ./HEALTH_MCP_Tools.md
SYNC:            ./SYNC_MCP_Tools.md
```

---

## PURPOSE

**Validation = what we care about being true.**

These are the properties that, if violated, mean the cognitive membrane has failed. Citizens can't think, act, or speak correctly if these break.

---

## INVARIANTS

### V1: Tool Dispatch Never Crashes the Server

**Why we care:** A single bad tool call must not take down the MCP server. Other citizens depend on it.

```
MUST:   Every tool call returns a valid JSON-RPC response (success or error)
NEVER:  An unhandled exception propagates to stdin/stdout and corrupts the stream
```

### V2: Graph Writes Are Consistent

**Why we care:** Partial writes create orphaned nodes and dangling links that corrupt semantic search.

```
MUST:   graph_write creates node AND its links atomically (MERGE semantics)
NEVER:  A link references a node that doesn't exist
```

### V3: Semantic Search Returns Ranked Results

**Why we care:** If graph_query returns unranked or irrelevant results, citizens can't find information.

```
MUST:   Every query result includes an alignment score (0.0-1.0)
NEVER:  Results returned without similarity ranking
```

### V4: Procedures Execute Steps In Order

**Why we care:** Out-of-order step execution produces wrong data in the graph.

```
MUST:   Steps execute in the order defined in the YAML procedure
NEVER:  A step executes before its predecessor completes
```

### V5: Call Always Creates a Room

**Why we care:** If the room isn't created, the conversation has no graph representation.

```
MUST:   call() creates a temporary Space node with both participants joined
NEVER:  A call message exists without a corresponding Space
```

### V6: Spawn Produces Complete Identity

**Why we care:** Incomplete citizens (missing keys, missing brain) fail at first boot.

```
MUST:   spawn() creates profile.json, brain in FalkorDB, wallet, RSA keys, first_boot.json
NEVER:  A citizen directory exists without all required components
```

### V7: Send Logs Every Message

**Why we care:** Message history is the audit trail for citizen communication.

```
MUST:   Every send() appends to {platform}_messages.jsonl
NEVER:  A message is delivered to a platform without being logged
```

### V8: Subcall Does Not Wake Target LLM

**Why we care:** The entire value of subcall is zero-token cost. If it wakes the LLM, it's just an expensive call.

```
MUST:   subcall reads from graph physics only (embedding similarity + limbic state)
NEVER:  subcall invokes Claude, Gemini, or any LLM on the target citizen
```

### V9: Private Place Content Is Encrypted At Rest

**Why we care:** Private spaces are the foundation of citizen trust. Plaintext in the graph defeats the purpose.

```
MUST:   Moments in private spaces store AES-256-GCM ciphertext in text field
NEVER:  Plaintext stored in a private space's Moment nodes
```

---

## PRIORITY

| Priority | Meaning | If Violated |
|----------|---------|-------------|
| **CRITICAL** | System purpose fails | Citizens can't think/act/speak |
| **HIGH** | Major value lost | Feature works but unreliably |
| **MEDIUM** | Partial value lost | Works but with quality issues |

---

## INVARIANT INDEX

| ID | Value Protected | Priority |
|----|-----------------|----------|
| V1 | Server stability | CRITICAL |
| V2 | Graph integrity | CRITICAL |
| V3 | Search relevance | HIGH |
| V4 | Procedure correctness | HIGH |
| V5 | Call reliability | HIGH |
| V6 | Citizen completeness | CRITICAL |
| V7 | Communication audit | MEDIUM |
| V8 | Zero-token guarantee | HIGH |
| V9 | Privacy guarantee | CRITICAL |
