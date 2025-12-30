# mind LLM Agents — Behaviors: Gemini Agent Output

```
STATUS: DRAFT
CREATED: 2025-12-19
VERIFIED: 2025-12-19 against commit ad538f8
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Provider_Specific_LLM_Subprocesses.md
THIS:            BEHAVIORS_Gemini_Agent_Output.md (you are here)
ALGORITHM:       ./ALGORITHM_Gemini_Stream_Flow.md
VALIDATION:      ./VALIDATION_Gemini_Agent_Invariants.md
IMPLEMENTATION:  ./IMPLEMENTATION_LLM_Agent_Code_Architecture.md
HEALTH:          ./HEALTH_LLM_Agent_Coverage.md
SYNC:            ./SYNC_LLM_Agents_State.md
```

---

## BEHAVIORS

### B1: Missing API Key

```
GIVEN:  The process is started without --api-key, GEMINI_API_KEY in .env, or GEMINI_API_KEY env var
WHEN:   The adapter initializes
THEN:   A JSON error message is printed to stdout
AND:    The process exits with code 1
```

### B2: Streaming JSON Output

```
GIVEN:  --output-format stream-json (default)
WHEN:   A Gemini response is streamed
THEN:   Each text chunk emits a JSON message with type=assistant
AND:    Each message includes content[{type: "text", text: <chunk>}]
AND:    A final JSON message with type=result includes the full response
```

### B3: Plain Text Output

```
GIVEN:  --output-format text
WHEN:   The adapter receives a Gemini response
THEN:   The response text is printed to stdout as plain text
```

### B4: Model Listing Debug Output

```
GIVEN:  The adapter starts successfully
WHEN:   The model list is requested
THEN:   Available model IDs are printed to stderr
AND:    Errors in listing models are printed to stderr
```

### B5: Tool Execution Output

```
GIVEN:  The Gemini response includes tool calls
WHEN:   The adapter processes tool calls
THEN:   A tool_code JSON message is emitted for each tool invocation
AND:    A tool_result JSON message is emitted with either data or an error
```

---

## NOTES

Input shaping for system prompts and tool use is documented in the ALGORITHM/VALIDATION docs to avoid duplication here.

We lean on those algorithm and validation references because they capture the request templates, tool schema, and fallback logic that underpin the streaming behaviors described below.

---

## OBJECTIVES SERVED

This adapter is tuned to measurable outputs that keep the CLI, and automation tooling aligned:

- Provide a fully parseable JSON stream whenever `--output-format stream-json` is selected so downstream tooling can consume assistant, tool, and result messages without brittle parsing workarounds.
- Offer a clean plain-text fallback when `--output-format text` is requested so scripts and humans that do not want JSON still receive only the assistant response text while diagnostics stay on stderr.
- Surface tool execution metadata (`tool_code`/`tool_result`) and credential errors alongside assistant messages so automation orchestrators can correlate each conversational step with its side effects and respond to missing keys promptly.

These objectives double down on streaming determinism, explicit error handling, and stderr hygiene so the adapter never surprises downstream orchestrators or human readers.
The validation doc's behavior table and objective coverage narrative now map back to these prose points so the living contract stays traceable.

---

## INPUTS / OUTPUTS

Before sending a request, these inputs determine credential sourcing, output formatting, and which tooling primitives are allowed to run, keeping the adapter behavior predictable.

### Inputs

- CLI args: `prompt` (required), `system_prompt` (optional), `output_format` (stream-json or text), `api_key` (optional), `allowed_tools` (currently unused).
- Environment: `GEMINI_API_KEY` from `.env` or process env when `--api-key` is absent.

### Outputs

- Stdout: JSON stream (`tool_code`, `tool_result`, `assistant`, `result`) for `stream-json`, or plain response text for `text`.
- Stderr: model listing output and model listing errors, leaving stdout parseable.
- Exit code: `1` on missing credentials; otherwise `0` on success.

The adapter keeps stdout stable for programmatic parsing and reserves stderr strictly for diagnostics so nothing interferes with the expected stream format.

---

## EDGE CASES

### E1: Empty stream chunks

```
GIVEN:  Gemini emits chunk objects with empty or missing text
THEN:   The adapter skips those chunks and does not emit empty assistant JSON
```

### E2: Model listing fails

```
GIVEN:  list_models() throws or returns unexpected errors
THEN:   The adapter logs the error to stderr and continues normal request flow
```

### E3: Tool handler errors

```
GIVEN:  A tool handler raises or returns an error payload
THEN:   A tool_result JSON message is emitted with an error field instead of crashing
```

---

## ANTI-BEHAVIORS

What should NOT happen:

### A1: Emitting JSON in text mode

```
GIVEN:   --output-format text
WHEN:    The adapter receives a response
MUST NOT: wrap the response in JSON or emit tool_code/tool_result messages
INSTEAD: print only the raw response text to stdout
```

### A2: Polluting stdout with debug logs

```
GIVEN:   The adapter lists models or encounters listing errors
WHEN:    The Gemini SDK returns data or errors
MUST NOT: write debug/model listing output to stdout
INSTEAD: write those logs to stderr to keep stdout parseable
```

### A3: Emitting empty assistant messages

```
GIVEN:   Streamed chunks with empty text
WHEN:    The adapter emits assistant messages
MUST NOT: emit JSON messages with empty content parts
INSTEAD: skip empty chunks entirely
```

---

## MARKERS

<!-- @mind:todo Add explicit documentation for tool schema fields (name, args, response) once the schema stabilizes. -->
<!-- @mind:escalation Should tool_result errors include a standardized code field for downstream UI handling? -->
