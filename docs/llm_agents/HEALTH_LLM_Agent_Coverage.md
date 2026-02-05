# mind LLM Agents — Health: Verification Mechanics and Coverage

```
STATUS: STABLE
CREATED: 2025-12-20
UPDATED: 2025-12-30 (split into focused files)
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

- **Failure mode avoided:** Provider API updates that change the JSON schema, leading to silent failures in the CLI.
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
    rationale: CLI depends on parsing every JSON chunk correctly.
    details: ./HEALTH_Stream_Validity.md
  - name: api_connectivity
    flow_id: gemini_stream_flow
    priority: high
    rationale: Detects missing credentials or network issues immediately.
    details: ./HEALTH_API_Connectivity.md
```

---

## OBJECTIVES COVERAGE

| Objective | Indicators | Why These Signals Matter |
|-----------|------------|--------------------------|
| Preserve the streaming contract so every chunk the CLI consumes stays parseable and complete | stream_validity | Guards the core inference channel by confirming chunk shape, tool_message pairings, and final result blocks before downstream UI/agents render anything. |
| Lock in provider connectivity so credentials or network failures are caught before the CLI assumes Gemini is reachable | api_connectivity | Keeps the CLI reliable by surfacing missing API keys, bad client instantiations, and diagnostic noise as structured errors that operators can act on quickly. |

---

## DOCK TYPES (COMPLETE LIST)

- `process` (gemini_agent.py subprocess)
- `stream` (stdout JSON chunks)
- `auth` (GEMINI_API_KEY environment variable)

---

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

## HOW TO RUN

```bash
# Manual verification of stream JSON
python3 -m mind.llms.gemini_agent -p "ping" --output-format stream-json

# Manual verification of plain text
python3 -m mind.llms.gemini_agent -p "ping" --output-format text
```

---

## DETAILED INDICATOR SPECIFICATIONS

- **stream_validity**: See `./HEALTH_Stream_Validity.md` for complete specification
- **api_connectivity**: See `./HEALTH_API_Connectivity.md` for complete specification

---

## KNOWN GAPS

<!-- @mind:todo No automated check for response latency. -->
<!-- @mind:todo No check for provider-side rate limit errors (429). -->
<!-- @mind:todo No automated unit tests for `gemini_agent.py` internals. -->

---

## MARKERS

<!-- @mind:todo Add a "health probe" prompt to quickly verify API connectivity. -->
<!-- @mind:escalation Should we monitor token usage per-session in HEALTH? -->
