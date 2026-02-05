# Health Indicator: Stream Validity

```
PARENT: HEALTH_LLM_Agent_Coverage.md
CREATED: 2025-12-30
```

---

## PURPOSE

This indicator keeps the streaming JSON surface deterministic so the toolchain never misparses ambiguous chunks.

---

## VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: stream_validity
  client_value: The CLI pipeline can parse each Gemini output chunk immediately without needing retries or manual intervention.
  validation:
    - validation_id: V-GEMINI-JSON
      criteria: Chunks must be valid newline-delimited JSON with 'type' and 'content' fields, and tool messages must arrive as matched pairs.
    - validation_id: V5
      criteria: Tool-related payloads use `tool_code`/`tool_result` objects so downstream tooling gets consistent metadata.
```

---

## HEALTH REPRESENTATION

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

---

## DOCKS SELECTED

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

---

## ALGORITHM / CHECK MECHANISM

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

---

## INDICATOR

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

---

## THROTTLING STRATEGY

```yaml
throttling:
  trigger: gemini_stream_flow chunk emission
  max_frequency: 10/min
  burst_limit: 20
  backoff: linear 10s between health checks when parse errors spike
```

---

## FORWARDINGS & DISPLAYS

```yaml
forwarding:
  targets:
    - location: ...mind/state/SYNC_Project_Health.md
      transport: file
      notes: Doctor inspects this stream score through the canonical health log before surfacing drift tickets.
display:
  locations:
    - surface: CLI health banner
      location: Repair/CLI diagnostics screen
      signal: green/amber/red float_0_1
      notes: The palette mirrors the float ratio semantics so operators see severity at a glance.
```

---

## MANUAL RUN

```yaml
manual_run:
  command: python3 -m mind.llms.gemini_agent -p "health check" --output-format stream-json
  notes: Verify the JSON parsing indicator after any Gemini API update or schema refresh by scanning for consistent `type` keys.
```

The CLI health banner ingests this float score so operators see a continuous status even when the streamer is quiet; if the ratio falls or JSON parsing starts erroring, the banner flips amber or red and the doctor can replay the log with the same command to capture the offending chunk.
