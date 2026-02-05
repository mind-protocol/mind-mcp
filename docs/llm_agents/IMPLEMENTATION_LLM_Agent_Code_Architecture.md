# mind LLM Agents — Implementation: Code Architecture

```
STATUS: DRAFT
CREATED: 2025-12-19
VERIFIED: 2025-12-19 against commit ad538f8
UPDATED: 2025-12-30 (compressed for clarity)
```

---

## CHAIN

```
OBJECTIVES:        ./OBJECTIVES_Llm_Agents_Goals.md
BEHAVIORS:        ./BEHAVIORS_Gemini_Agent_Output.md
PATTERNS:         ./PATTERNS_Provider_Specific_LLM_Subprocesses.md
ALGORITHM:        ./ALGORITHM_Gemini_Stream_Flow.md
VALIDATION:       ./VALIDATION_Gemini_Agent_Invariants.md
HEALTH:           ./HEALTH_LLM_Agent_Coverage.md
SYNC:             ./SYNC_LLM_Agents_State.md
THIS:             ./IMPLEMENTATION_LLM_Agent_Code_Architecture.md
IMPL:             mind/llms/gemini_agent.py
```

---

## CODE STRUCTURE

```
mind/
└── llms/
    └── gemini_agent.py  # provider subprocess adapter that isolates Gemini SDK usage
```

`gemini_agent.py` owns the entire subprocess lifecycle. Currently ~270 lines - manageable but watching for growth.

### File Responsibilities

| File | Purpose | Key Functions | Lines | Status |
|------|---------|--------------| -------|--------|
| `mind/llms/gemini_agent.py` | Launches Gemini subprocess, configures SDK, streams structured JSON, shields CLI from provider SDKs | `main`, tool helper definitions, `tool_map`, streaming loop | ~270 | OK |

Tool helper definitions are first candidates for extraction if additional providers are added.

---

## DESIGN PATTERNS

**Architecture:** Subprocess isolation pipeline

**Why:** Running each provider in its own subprocess keeps heavy dependencies (SDKs, network I/O, credentials) isolated from the main CLI process. UI only communicates via stdin/stdout.

### Code Patterns

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Strategy | `tool_map` | Allows Gemini response to invoke different helper functions by name |
| Functional pipeline | Tool helpers | Wraps external effects into predictable tool results |

### Anti-Patterns to Avoid

- **God Function:** Keep `main` focused; new tools/providers go in separate helpers
- **Shared SDK imports:** Never import provider SDKs into `agent_cli.py` - adapter owns all third-party dependencies
- **Implicit state mutation:** Tool helpers log JSON payloads explicitly; no silent global state changes

---

## SCHEMA

### StreamMessage

```yaml
required:
  - type: string          # "assistant", "tool_result", or "error"
  - message: object       # text content or metadata
optional:
  - name: string          # tool name for tool output
  - result: object        # payload returned by tool helper
```

### ToolInvocationPayload

```yaml
required:
  - name: string          # helper function name in gemini_agent
  - args: object          # matches helper signature
optional:
  - description: string   # for logging
```

---

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| `main()` | `mind/llms/gemini_agent.py:14` | `mind/agent_cli.py` launches `python -m mind.llms.gemini_agent` for gemini provider |

---

## DATA FLOW SUMMARY

See `ALGORITHM_Gemini_Stream_Flow.md` for detailed flow specifications.

**Key flows:**
1. **Prompt-to-Stream:** CLI → subprocess launch → GenAI client auth → chat.send_message() → stream response parts → JSON output
2. **Tool Invocation:** Gemini tool call → tool_map lookup → helper execution → structured result → function_response back to model

---

## MODULE DEPENDENCIES

### Internal
```
mind/agent_cli.py
    └── spawns → mind.llms.gemini_agent
```

### External

| Package | Used For |
|---------|----------|
| `google.genai` | Gemini API client, chat streaming, tool wiring |
| `dotenv` | .env file loading for credentials |
| `argparse` | CLI flag parsing |
| `subprocess`, `glob`, `shutil`, `urllib` | Tool helpers (filesystem, web fetch) |
| `json`, `os`, `sys`, `re` | Logging, environment, error handling |

---

## STATE & RUNTIME

**State:** Per-process variables in gemini_agent.py
- `history`: [] → [system, user prompts...] → discarded on exit
- `tool_map`: Helper name-to-function registry, built once at startup
- `google_search_base_url`: Loaded from .env/env vars

**Lifecycle:** Parse args & load .env → auth with GEMINI_API_KEY → build tool_map → seed history → send prompt → iterate response parts (emit JSON, run tools) → flush & exit

**Concurrency:** Single-threaded, synchronous subprocess. No async/threading - relies on OS process management. Tool helpers run sequentially.

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `GEMINI_API_KEY` | --api-key, .env, env var | None (required) | Authentication for Gemini SDK |
| `MIND_GOOGLE_SEARCH_URL` | .env, env var | `https://www.google.com/search` | Base URL for search helper |
| `--output-format` | CLI flag | `stream-json` | Structured streaming vs plain text |
| `--allowed-tools` | CLI flag | None | Tool whitelist (reserved for future gating) |
| `--model-name` | CLI flag, GEMINI_MODEL env | `gemini-3-flash-preview` | Model selection |

---

## BIDIRECTIONAL LINKS

### Code → Docs

| File | Line | Reference |
|------|------|-----------|
| `mind/llms/gemini_agent.py` | 2 | `# DOCS: docs/llm_agents/PATTERNS_Provider_Specific_LLM_Subprocesses.md` |

### Docs → Code

| Doc Section | Implemented In |
|-------------|----------------|
| ALGORITHM stream loop | `mind/llms/gemini_agent.py:main` |
| PATTERNS subprocess boundary | `mind/llms/gemini_agent.py` tool helper registry |
| HEALTH coverage assertions | `mind/llms/gemini_agent.py` tool helper error handling |

---

## EXTRACTION CANDIDATES

| File | Current | Target | Extract To | What to Move |
|------|---------|--------|------------|--------------|
| `mind/llms/gemini_agent.py` | ~270L | <250L | `mind/llms/tool_helpers.py` | Tool helper definitions (read, list, glob, shell, search, etc.) |

---

## MARKERS

<!-- @mind:todo Gate stderr model listing so CLI doesn't parse noisy diagnostics -->
<!-- @mind:todo Honor --allowed-tools flag by filtering tool_map before passing to genai.Client -->
<!-- @mind:proposition Introduce shared adapter base for other providers to keep tooling/streaming consistent -->
<!-- @mind:proposition Persist tool_result payloads to .mind/state/agent_memory.jsonl for replay/audits -->
<!-- @mind:escalation Should adapters expose health metrics for tool execution latency? -->
<!-- @mind:escalation Do we need common JSON schema validator before emitting stream to guard against SDK drift? -->
