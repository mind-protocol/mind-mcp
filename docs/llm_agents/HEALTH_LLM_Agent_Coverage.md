# mind LLM Agents — Health: Verification Mechanics and Coverage

```
STATUS: STABLE
CREATED: 2025-12-20
```

---

## PURPOSE OF THIS FILE

This file defines the health verification mechanics for the mind LLM Agents (primarily the Gemini adapter). It ensures that the communication between the mind core and the underlying LLM provider is robust, correctly formatted, and resilient to failures.

It safeguards:
- **Output Correctness:** Ensuring streaming JSON or plain text formats match expectations.
- **Error Handling:** Ensuring API failures or missing credentials are surfaced correctly.
- **Performance:** Monitoring for excessive latency or token consumption issues.

Boundaries:
- This file covers the provider-specific subprocess behavior.
- It does not verify the quality of the LLM responses (subjective).
- It does not verify the CLI logic that calls these agents (covered in `docs/cli/HEALTH_CLI_Coverage.md`).

---

## WHY THIS PATTERN

HEALTH is separate from tests because it verifies real system health without changing implementation files. For LLM agents, this allows monitoring real-world interactions and detecting provider-side drift or API changes without modifying the core adapter code.

- **Failure mode avoided:** Provider API updates that change the JSON schema, leading to silent failures in the TUI.
- **Docking-based checks:** Uses the subprocess stdout/stderr and exit codes as docking points.
- **Throttling:** Prevents excessive API costs by running heavy verification checks at a low cadence.

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Provider_Specific_LLM_Subprocesses.md
BEHAVIORS:       ./BEHAVIORS_Gemini_Agent_Output.md
ALGORITHM:       ./ALGORITHM_Gemini_Stream_Flow.md
VALIDATION:      ./VALIDATION_Gemini_Agent_Invariants.md
IMPLEMENTATION:  ./IMPLEMENTATION_LLM_Agent_Code_Architecture.md
THIS:            HEALTH_LLM_Agent_Coverage.md
SYNC:            ./SYNC_LLM_Agents_State.md

IMPL:            mind/llms/gemini_agent.py
```

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: gemini_stream_flow
    purpose: Main interaction loop with the LLM. Failure breaks all AI functionality.
    triggers:
      - type: event
        source: cli:mind work or tui:manager
    frequency:
      expected_rate: 5/min
      peak_rate: 50/min
      burst_behavior: throttled by provider rate limits
    risks:
      - V-GEMINI-JSON: Invalid JSON streaming format
    notes: Heavily dependent on GEMINI_API_KEY being set.
```

---

## HEALTH INDICATORS SELECTED

```yaml
health_indicators:
  - name: stream_validity
    flow_id: gemini_stream_flow
    priority: high
    rationale: TUI depends on parsing every JSON chunk correctly.
  - name: api_connectivity
    flow_id: gemini_stream_flow
    priority: high
    rationale: Detects missing credentials or network issues immediately.
```

---

## OBJECTIVES COVERAGE

| Objective | Indicators | Why These Signals Matter |
|-----------|------------|--------------------------|
| Preserve the streaming contract so every chunk the TUI consumes stays parseable and complete | stream_validity | Guards the core inference channel by confirming chunk shape, tool_message pairings, and final result blocks before downstream UI/agents render anything; the doctor reads this table to correlate the health ratio with observed stream noise, making drift easy to detect. |
| Lock in provider connectivity so credentials or network failures are caught before the CLI assumes Gemini is reachable | api_connectivity | Keeps the CLI/TUI reliable by surfacing missing API keys, bad client instantiations, and diagnostic noise as structured errors that operators can act on quickly; the health tracker turns the binary flag into a quick dashboard ping so missing keys show up as connection outages instead of silent stream gaps. |

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: ...mind/state/SYNC_Project_Health.md
  result:
    representation: binary
    value: 1
    updated_at: 2025-12-20T00:00:00Z
    source: gemini_stream_flow
```

---

## DOCK TYPES (COMPLETE LIST)

- `process` (gemini_agent.py subprocess)
- `stream` (stdout JSON chunks)
- `auth` (GEMINI_API_KEY environment variable)

---

## HOW TO USE THIS TEMPLATE

- Start by documenting the flow you intend to monitor (transport, auth, output).
- Describe the invariant you are guarding, the docking points you observe, and how often the signal should be sampled.
- Populate the indicator, status, and gap fields with precise expectations so doctor can validate the template.

Each checker listed below maps directly to a high-priority indicator so the execution surface stays tethered to the ABI contract.

## CHECKER INDEX

```yaml
checkers:
  - name: json_format_checker
    purpose: Validates that every chunk is a valid JSON object of the correct type.
    status: active
    priority: high
  - name: auth_credential_checker
    purpose: Verifies that required API keys are available and valid.
    status: active
    priority: high
```

---

## INDICATOR: Stream Validity

This indicator keeps the streaming JSON surface deterministic so the toolchain never misparses ambiguous chunks.

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: stream_validity
  client_value: The CLI/TUI pipeline can parse each Gemini output chunk immediately without needing retries or manual intervention.
  validation:
    - validation_id: V-GEMINI-JSON
      criteria: Chunks must be valid newline-delimited JSON with 'type' and 'content' fields, and tool messages must arrive as matched pairs.
    - validation_id: V5
      criteria: Tool-related payloads use `tool_code`/`tool_result` objects so downstream tooling gets consistent metadata.
```

### HEALTH REPRESENTATION

```yaml
representation:
  allowed:
    - float_0_1
  selected:
    - float_0_1
  semantics:
    float_0_1: Ratio of parseable chunks versus total emitted chunks across the last completed session.
  aggregation:
    method: Minimum-of-weighted-streams so critical parse failures are not averaged away.
    display: The CLI health banner surfaces the float score with a green/amber/red mapping so operators see severity at a glance.
```

### DOCKS SELECTED

```yaml
docks:
  input:
    id: model_response_parts
    method: main
    location: mind/llms/gemini_agent.py:205-235
  output:
    id: assistant_chunks
    method: main
    location: mind/llms/gemini_agent.py:205-235
```

### ALGORITHM / CHECK MECHANISM

```yaml
mechanism:
  summary: Parse every stream-json chunk printed by `main` and compare against VALIDATION V2/V5 so the JSON schema stays locked and tool payloads remain paired.
  steps:
    - Read `response.candidates[0].content.parts` and capture text/call payloads in sequence.
    - Serialize each chunk as JSON with explicit `type`/`message` fields while tracking parseability counts.
    - Emit the session success ratio and mark the indicator ERROR if parse failures exceed the established threshold.
  data_required: `model.candidates[0].content.parts`, `args.output_format`, and the `assistant_chunks` stream for both `assistant` and `tool_result` records.
  failure_mode: Streaming output misses the `type`, `message`, or tool payload keys, so downstream parsers raise decoding exceptions.
```

### INDICATOR

```yaml
indicator:
  error:
    - name: stream_parse_fail
      linked_validation: [V-GEMINI-JSON]
      meaning: The chunk failed to parse or lacked the required fields, leaving the stream unusable.
      default_action: stop
  warning:
    - name: stream_chunk_truncated
      linked_validation: [V-GEMINI-JSON]
      meaning: The chunk emitted partial JSON that requires retries, slowing the session.
      default_action: warn
  info:
    - name: stream_parse_ok
      linked_validation: [V-GEMINI-JSON, V5]
      meaning: Chunks remain parseable and the float score stays above 95%, so downstream clients stay smooth.
      default_action: log
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: gemini_stream_flow chunk emission
  max_frequency: 10/min
  burst_limit: 20
  backoff: linear 10s between health checks when parse errors spike
```

### FORWARDINGS & DISPLAYS

```yaml
forwarding:
  targets:
    - location: ...mind/state/SYNC_Project_Health.md
      transport: file
      notes: Doctor inspects this stream score through the canonical health log before surfacing drift tickets.
display:
  locations:
    - surface: CLI health banner
      location: Repair/TUI diagnostics screen
      signal: green/amber/red float_0_1
      notes: The palette mirrors the float ratio semantics so operators see severity at a glance.
```

### MANUAL RUN

```yaml
manual_run:
  command: python3 -m mind.llms.gemini_agent -p "health check" --output-format stream-json
  notes: Verify the JSON parsing indicator after any Gemini API update or schema refresh by scanning for consistent `type` keys.
```

The CLI health banner ingests this float score so operators see a continuous status even when the streamer is quiet; if the ratio falls or JSON parsing starts erroring, the banner flips amber or red and the doctor can replay the log with the same command to capture the offending chunk.

---
## INDICATOR: api_connectivity

This indicator makes sure the adapter never starts streaming without the credentials or client it needs, and that any failures remain bounded.

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: api_connectivity
  client_value: Prevents the CLI/TUI from assuming Gemini is reachable by surfacing missing or invalid GEMINI_API_KEY instances before streaming can start.
  validation:
    - validation_id: V1
      criteria: Missing credentials emit a structured JSON error and exit code 1 before a Gemini request is sent.
    - validation_id: V4
      criteria: Diagnostic logs live on stderr so stdout stays reserved for structured chunks even during retries.
```

### HEALTH REPRESENTATION

```yaml
representation:
  allowed:
    - enum
  selected:
    - enum
  semantics:
    enum: OK=key validated, WARN=client created with diagnostics, ERROR=key missing or client creation failed.
  aggregation:
    method: worst_case
    display: CLI log and doctor summary
```

### DOCKS SELECTED

```yaml
docks:
  input:
    id: auth_check
    method: mind.llms.gemini_agent.main
    location: mind/llms/gemini_agent.py:32-48
  output:
    id: auth_error
    method: mind.llms.gemini_agent.main
    location: mind/llms/gemini_agent.py:43-45
```

### ALGORITHM / CHECK MECHANISM

```yaml
mechanism:
  summary: Validate `GEMINI_API_KEY` sources, instantiate `genai.Client`, and flag any failure before assistant chunks are emitted.
  steps:
    - Resolve `--api-key`, `.env`, and environment variables for GEMINI_API_KEY in priority order.
    - Emit the JSON `{"error": ...}` payload and exit 1 if the key is missing, blocking streaming entirely.
    - When a key exists, instantiate `genai.Client` and log diagnostics on stderr; surface exceptions as WARN-level connectivity signals.
  data_required: CLI args, dotenv/env lookups, constructor success flags, and exit metadata.
  failure_mode: Missing credentials halt the subprocess so the CLI observes a structured error instead of random chunks, while client exceptions become WARN signals.
```

### INDICATOR

```yaml
indicator:
  error:
    - name: missing_credentials
      linked_validation: [V1]
      meaning: GEMINI_API_KEY lookup failed and the adapter refused to start, preventing downstream activity.
      default_action: stop
  warning:
    - name: client_init_warning
      linked_validation: [V4]
      meaning: `genai.Client` creation emitted stderr diagnostics, indicating degraded connectivity even though the key exists.
      default_action: warn
  info:
    - name: credential_probe
      linked_validation: [V1, V4]
      meaning: API key is present and client instantiation succeeded, so downstream streaming can begin.
      default_action: log
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: mind agent/work invocation with Gemini provider
  max_frequency: 5/min
  burst_limit: 10
  backoff: exponential starting at 15s to avoid repeated auth failures.
```

### FORWARDINGS & DISPLAYS

```yaml
forwarding:
  targets:
    - location: ...mind/state/SYNC_Project_Health.md
      transport: file
      notes: Doctor consumes this indicator to flag missing credentials before streaming begins.
display:
  locations:
    - surface: CLI stderr
      location: `mind llms gemini` startup path
      signal: warn
      notes: Displays structured credential failures and diagnostics for operators.
```

### MANUAL RUN

```yaml
manual_run:
  command: GEMINI_API_KEY= python3 -m mind.llms.gemini_agent -p "health ping" --output-format text
  notes: Run without GEMINI_API_KEY to confirm the structured exit path and rerun with the key set to verify the OK state.
```

The binary representation of this indicator surfaces in CLI banners and doctor dashboards, so running the command without the key quickly exposes the error path while restoring the key demonstrates the green state before streaming begins.

---

## HOW TO RUN

```bash
# Manual verification of stream JSON
python3 -m mind.llms.gemini_agent -p "ping" --output-format stream-json

# Manual verification of plain text
python3 -m mind.llms.gemini_agent -p "ping" --output-format text
``` 

---

## KNOWN GAPS

<!-- @mind:todo No automated check for response latency. -->
<!-- @mind:todo No check for provider-side rate limit errors (429). -->
<!-- @mind:todo No automated unit tests for `gemini_agent.py` internals. -->

---

## MARKERS

<!-- @mind:todo Add a "health probe" prompt to quickly verify API connectivity. -->
<!-- @mind:escalation Should we monitor token usage per-session in HEALTH? -->
