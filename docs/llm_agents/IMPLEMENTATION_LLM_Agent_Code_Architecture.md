# mind LLM Agents — Implementation: Code Architecture

```
STATUS: DRAFT
CREATED: 2025-12-19
VERIFIED: 2025-12-19 against commit ad538f8
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

`gemini_agent.py` owns the entire subprocess lifecycle, so most of the implementation lives inside this single file. It is still under the 400-line threshold, but the dozens of inline tool helpers keep it close to the WATCH band.

### File Responsibilities

| File | Purpose | Key Functions/Classes | Lines | Status |
|------|---------|-----------------------|-------|--------|
| `runtime/llms/gemini_agent.py` | Launches the Gemini subprocess, configures the SDK, streams structured JSON, and shields CLI logic from provider SDKs. | `main`, the tool helper definitions, `tool_map`, streaming loop. | ~270 | OK |

The file is currently manageable, but the tool helper definitions are the first candidates for extraction if additional providers are folded into the same directory.

---

## MODULE LAYOUT

```
mind/llms/
└── gemini_agent.py         # CLI-invoked subprocess entry for Gemini
```

The CLI (`runtime/agent_cli.py`) builds `python -m mind.llms.gemini_agent` with the selected provider arguments. Because the entire adapter fits within `mind.llms`, no extra modules exist yet, but the CLI and adapter remain tightly coupled by the shared command-line schema.

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Subprocess isolation pipeline

**Why this pattern:** Running each provider in its own subprocess keeps heavy dependencies (SDKs, network I/O, credentials) isolated from the main CLI process so the UI only ever communicates via stdin/stdout.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Strategy | `tool_map` inside `runtime/llms/gemini_agent.py` | Allows the Gemini response to invoke different helper functions by name without inlining call handling logic. |
| Functional pipeline | The helper definitions for each tool | Wraps external effects (filesystem, search) into predictable tool results before sending them back to the chat loop. |

### Anti-Patterns to Avoid

- **God Function:** Avoid expanding `main` with additional responsibilities; any new tool or provider should live in its own helper or adapter to keep the entry point legible.
- **Shared SDK imports:** Resist importing provider SDKs into `agent_cli.py`; the adapter should bear all third-party dependencies to honor the subprocess boundary.
- **Implicit state mutation:** Tool helpers log their JSON payloads explicitly; silently mutating global state would make retrying responses impossible.

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| CLI ↔ Gemini adapter | Argument parsing, credential validation, tool helper wiring | agent_cli routing, downstream tool runners | CLI wraps `python -m mind.llms.gemini_agent` with flags and trusts the JSON stream. |

---

## SCHEMA

### StreamMessage

```yaml
StreamMessage:
  required:
    - type: string                # e.g., "assistant", "tool_result", or "error"
    - message: object             # carries text content or metadata for the CLI
  optional:
    - name: string                # tool name when the message describes tool output
    - result: object              # payload returned by the tool helper
  constraints:
    - type determines the structure of `message` so the CLI can render consistently.
```

### ToolInvocationPayload

```yaml
ToolInvocationPayload:
  required:
    - name: string                # name of the helper function defined in gemini_agent
    - args: object                # parameter structure that matches the helper signature
  optional:
    - description: string         # used for logging when available
  relationships:
    - tool helper → gemini_agent.py tool definitions
    - response → StreamMessage of type "tool_result"
```

---

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| `main()` | `runtime/llms/gemini_agent.py:14` | Called when `runtime/agent_cli.py` launches `python -m mind.llms.gemini_agent` for the `gemini` provider. |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

### Gemini Prompt Stream Flow

This flow tracks how a user prompt crosses the subprocess boundary, reaches the Gemini SDK, and returns a streamed JSON payload to the CLI. The flow matters because it spans configuration, network I/O, tool execution, and final output formatting.

```yaml
flow:
  name: gemini_prompt_stream
  purpose: Deliver prompts to Gemini, include tool results, and emit structured responses for the CLI.
  scope: [agent_cli subprocess launch, gemini_agent parsing, SDK chat loop, stdout stream]
  steps:
    - id: cli_launch
      description: CLI builds `python -m mind.llms.gemini_agent` with provider flags and environment-derived credentials.
      file: mind/agent_cli.py
      function: select_provider_callback
      input: CLI args + .env
      output: subprocess command string
      trigger: `provider == "gemini"`
      side_effects: opens new Python interpreter process
    - id: adapter_init
      description: Adapter parses args, loads `.env`, ensures `GEMINI_API_KEY`, and instantiates the GenAI client.
      file: mind/llms/gemini_agent.py
      function: main
      input: process argv, environment
      output: authenticated `genai.Client`
      trigger: entry point execution
      side_effects: network-auth handshake
    - id: streaming_loop
      description: Gemini responses are split into text parts; JSON messages and tool calls stream to stdout.
      file: mind/llms/gemini_agent.py
      function: chat response loop
      input: Gemini chat candidate parts
      output: stream-json lines with type `assistant` or `tool_result`
      trigger: `response.candidates` iterator
      side_effects: writes to stdout
  docking_points:
    guidance:
      include_when: cross-boundary outputs or inputs that need health monitoring
      omit_when: purely internal helper bookkeeping
      selection_notes: focus on stdout streams and tool_result acknowledgments for health checks.
    available:
      - id: dock_subprocess_invocation
        type: process
        direction: output
        file: mind/agent_cli.py
        function: select_provider_callback
        trigger: CLI decision to spin up Gemini
        payload: subprocess command
        async_hook: not_applicable
        needs: none
        notes: opportunity to log provider selection and env extraction for diagnostics.
      - id: dock_stream_json
        type: stdout
        direction: output
        file: mind/llms/gemini_agent.py
        function: response loop
        trigger: each text part or tool result
        payload: StreamMessage schema above
        async_hook: optional
        needs: health watcher to verify JSON validity under load
        notes: critical for CLI sanity checks.
      - id: dock_tool_result
        type: custom
        direction: output
        file: mind/llms/gemini_agent.py
        function: tool helper invocation
        trigger: Gemini invokes helper call
        payload: ToolInvocationPayload + helper result
        async_hook: optional
        needs: result verification and optional persistence to `.mind/state`
        notes: Tool calls mutate files or run shell commands, so schedulers should inspect them for safety.
    health_recommended:
      - dock_id: dock_stream_json
        reason: Ensures JSON stream remains valid for downstream consumers.
      - dock_id: dock_tool_result
        reason: Tool results may carry side effects; health should verify they succeeded.
```

---

## LOGIC CHAINS

### LC1: Prompt-To-Streamed-Response

**Purpose:** Drive the CLI prompt through Gemini and emit assistant/text chunks for the CLI.

```
agent_cli.py:select_provider → creates subprocess command
  → python -m mind.llms.gemini_agent → gemini_agent.main() parses args
    → Authenticate and start GenAI chat → send prompt via chat.send_message()
      → Iterate over `response.candidates[0].content.parts` → stream JSON lines or plain text
        → Exit once loop completes → CLI reads final stream
```

**Data transformation:**
- Input: `PromptArgs` from CLI — CLI command line, `.env`, defaults → structured subprocess invocation.
- After step 2: `genai.Client` + `tool_map` — ready to receive and act on Gemini output.
- After step 3: `Chat` object streaming `parts` — each part becomes a JSON `assistant` object for the CLI.
- Output: Streamed JSON lines (or plain text) delivered on stdout.

### LC2: Tool Invocation Handshake

**Purpose:** Accept tool calls from Gemini responses, run local helpers, and send structured replies back to the model for continued reasoning.

```
Gemini tool call → `tool_map[function_name](**args)` helper executes
  → Helper returns result dict → log `tool_result` JSON to stdout
    → `chat.send_message` with `function_response` resumes model reasoning
```

**Data transformation:**
- Input: Gemini tool call payload (`function_name`, `args`).
- After helper: `result` dict — sanitized, JSON serializable data with stdout/stderr or fetched content.
- Output: Structured `tool_result` message plus `function_response` posted back to `chat`.

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
mind/agent_cli.py
    └── spawns → mind.llms.gemini_agent
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `google.genai` | Gemini API client, chat streaming, tool wiring | `runtime/llms/gemini_agent.py` |
| `dotenv` | `.env` file loading for credentials and overrides | `runtime/llms/gemini_agent.py` |
| `argparse` | CLI flag parsing for prompts, output format, API key, and allowed tools | `runtime/llms/gemini_agent.py` |
| `subprocess`, `glob`, `shutil`, `urllib` | Tool helpers rely on file system commands, global matching, and web fetches | `runtime/llms/gemini_agent.py` |
| `json`, `os`, `sys`, `re` | Logging stream-json, environment inspection, error handling, regex search | `runtime/llms/gemini_agent.py` |

---

## STATE MANAGEMENT

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| `history` | `runtime/llms/gemini_agent.py` | Local (per process) | Initialized when `main` starts, extended with system prompt tokens, discarded after exit. |
| `tool_map` | `runtime/llms/gemini_agent.py` | Local helper registry | Built once after helper definitions, referenced for every tool invocation. |
| `google_search_base_url` | `runtime/llms/gemini_agent.py` | Local configuration state | Loaded once from `.env` / env vars to keep the helper deterministic. |

### State Transitions

```
history: [] ──(maybe add system prompt)──▶ history: [system role, assistant confirm] ──(prompt)──▶ history includes user prompt
tool_map: {} ──(populate)──▶ mapping of helper names to functions
google_search_base_url: default ──(env overrides)──▶ configured URL
```

---

## RUNTIME BEHAVIOR

### Initialization

```
1. Parse CLI args and load `.env` values.
2. Require `GEMINI_API_KEY`, instantiate `genai.Client`, and assemble `tool_map`.
3. Seed `history` with the optional system prompt and confirmation message.
```

### Main Loop / Request Cycle

```
1. Send the user prompt via `chat.send_message()` and wait for the candidate to arrive.
2. Iterate over each `part` in `response.candidates[0].content.parts`.
3. Emit JSON stream lines for text parts, run tool helpers when `part.call` exists, and reply to the model with tool results.
4. Break out of the loop when no more tool calls remain.
```

### Shutdown

```
1. Flush the final JSON stream (or newline for plain text).
2. Exit with status 0 on success or print structured error and exit 1 on exceptions.
```

---

## CONCURRENCY MODEL

| Component | Model | Notes |
|-----------|-------|-------|
| Gemini subprocess | Single-threaded, synchronous process | The entire adapter runs on the thread started by `python -m mind.llms.gemini_agent`; I/O is blocking but streaming flushes keep the CLI responsive. |
| Tool helpers | Synchronous helpers | Each tool runs one after another; long-running commands block the response but the stream and `tool_result` acknowledgments keep the multi-turn conversation consistent. |

No explicit async or threading constructs are present, so the adapter relies on the operating system to manage the subprocess lifecycle.

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `GEMINI_API_KEY` | CLI arg `--api-key`, `.env`, or environment variable | _None_ | Required for authenticating the Gemini SDK; failure exits with a JSON error. |
| `MIND_GOOGLE_SEARCH_URL` | `.env` or environment variable | `https://www.google.com/search` | Base URL for the Google search helper so tests can override it for offline runs. |
| `--output-format` | CLI flag | `stream-json` | Selects structured streaming vs plain text; stream-json is the default so the CLI can parse it deterministically. |
| `--allowed-tools` | CLI flag | _None_ | Comma-separated whitelist of helpers (currently unused but reserved for gating). |
| `--model-name` | CLI flag or `GEMINI_MODEL` env | `gemini-3-flash-preview` | Overrides the Gemini model used for the chat session. |

---

## BIDIRECTIONAL LINKS

### Code → Docs

| File | Line | Reference |
|------|------|-----------|
| `runtime/llms/gemini_agent.py` | 2 | `# DOCS: docs/llm_agents/PATTERNS_Provider_Specific_LLM_Subprocesses.md` |

### Docs → Code

| Doc Section | Implemented In |
|-------------|----------------|
| ALGORITHM_Gemini_Stream_Flow stream loop | `runtime/llms/gemini_agent.py:main` |
| PROVIDER PATTERNS subprocess boundary | `runtime/llms/gemini_agent.py` tool helper registry |
| HEALTH coverage assertions | `runtime/llms/gemini_agent.py` (tool helper error handling) |

---

## MARKERS

### Extraction Candidates

| File | Current | Target | Extract To | What to Move |
|------|---------|--------|------------|--------------|
| `runtime/llms/gemini_agent.py` | ~270L | <250L | `runtime/llms/tool_helpers.py` | Pull the repeated tool helper definitions (read, list, glob, shell, search, etc.) into a shared helper module to keep the adapter focused on wiring. |

### Missing Implementation

<!-- @mind:todo Gate the stderr model listing so the CLI does not parse noisy diagnostics when the Gemini SDK logs available models. -->
<!-- @mind:todo Honor the `--allowed-tools` flag by filtering `tool_map` before passing it to `genai.Client` for the next provider. -->

### Ideas

<!-- @mind:proposition Introduce a shared adapter base that other providers can subclass to keep tooling and streaming logic consistent. -->
<!-- @mind:proposition Persist `tool_result` payloads to `...mind/state/agent_memory.jsonl` when they mutate disks, enabling replay or audits. -->

### Questions

<!-- @mind:escalation Should adapters expose health metrics for tool execution latency so the doctor can flag slow helpers? -->
<!-- @mind:escalation Do we need a common JSON schema validator before emitting the stream to guard against SDK drift? -->
<!-- @mind:escalation Would tracking helper execution timestamps improve the concurrency diagnostics so we can spot helpers that block the stream longer than expected? -->
