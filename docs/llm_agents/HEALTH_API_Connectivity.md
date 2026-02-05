# Health Indicator: API Connectivity

```
PARENT: HEALTH_LLM_Agent_Coverage.md
CREATED: 2025-12-30
```

---

## PURPOSE

This indicator makes sure the adapter never starts streaming without the credentials or client it needs, and that any failures remain bounded.

---

## VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: api_connectivity
  client_value: Prevents the CLI from assuming Gemini is reachable by surfacing missing or invalid GEMINI_API_KEY instances before streaming can start.
  validation:
    - validation_id: V1
      criteria: Missing credentials emit a structured JSON error and exit code 1 before a Gemini request is sent.
    - validation_id: V4
      criteria: Diagnostic logs live on stderr so stdout stays reserved for structured chunks even during retries.
```

---

## HEALTH REPRESENTATION

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

---

## DOCKS SELECTED

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

---

## ALGORITHM / CHECK MECHANISM

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

---

## INDICATOR

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

---

## THROTTLING STRATEGY

```yaml
throttling:
  trigger: mind agent/work invocation with Gemini provider
  max_frequency: 5/min
  burst_limit: 10
  backoff: exponential starting at 15s to avoid repeated auth failures.
```

---

## FORWARDINGS & DISPLAYS

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

---

## MANUAL RUN

```yaml
manual_run:
  command: GEMINI_API_KEY= python3 -m mind.llms.gemini_agent -p "health ping" --output-format text
  notes: Run without GEMINI_API_KEY to confirm the structured exit path and rerun with the key set to verify the OK state.
```

The binary representation of this indicator surfaces in CLI banners and doctor dashboards, so running the command without the key quickly exposes the error path while restoring the key demonstrates the green state before streaming begins.
