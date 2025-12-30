# mind LLM Agents — Validation: Gemini Agent Invariants

```
STATUS: DRAFT
CREATED: 2025-12-19
VERIFIED: 2025-12-19 against commit ad538f8
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Provider_Specific_LLM_Subprocesses.md
BEHAVIORS:       ./BEHAVIORS_Gemini_Agent_Output.md
ALGORITHM:       ./ALGORITHM_Gemini_Stream_Flow.md
THIS:            VALIDATION_Gemini_Agent_Invariants.md (you are here)
IMPLEMENTATION:  ./IMPLEMENTATION_LLM_Agent_Code_Architecture.md
HEALTH:          ./HEALTH_LLM_Agent_Coverage.md
SYNC:            ./SYNC_LLM_Agents_State.md
```

---

## BEHAVIORS GUARANTEED

| Behavior ID | Behavior | Why This Validation Matters |
|-------------|----------|-----------------------------|
| B1 | Missing credentials produce a structured JSON error plus exit code 1 before any Gemini request is sent. | Ensures credential gating stays deterministic so downstream consumers never parse ambiguous streams or partial payloads when authentication is absent, and it keeps the logging/exit indicators predictable so operator dashboards can highlight missing keys; this shape also lets the automation detect missing keys without guessing, and the doctor now has a consistent violation to alert on when credentials disappear from the stream. |
| B2 | Stream-json mode emits assistant/result messages that match the CLI contract, capturing chunk content and final response packets. | Keeping the envelope intact guarantees downstream parsers always see the expected fields and that tooling relying on the format keeps working, so telemetry can verify progress without guessing about partial chunks while the budget meters receive consistent chunk boundaries; this makes the doctor’s streaming contract assertions absolute by referencing the same JSON fields when it revalidates the stream. |
| B3 | Plain text mode prints only the raw response text when requested, never mixing in JSON wrappers or tool metadata. | Protects the human-readable output from becoming tangled with structured elements, keeping the observable response legible for users and letting legacy scripts consume the prompts verbatim when they rely on unstructured text; the validation entry spells out the plain-text mode invariant so auditors can spot regressions without digging into implementation details. |
| B4 | Model listings and diagnostic logs remain on stderr so stdout stays parseable even during debugging. | Prevents the streaming channel from being corrupted by diagnostic data, which is critical for deterministic parsing and downstream tooling, and it keeps stderr available for tracing provider health so health dashboards can rely on separated streams; the new validation narrative even references this behavior so the doctor can bookend the log-only channel. |
| B5 | Tool invocations emit paired `tool_code`/`tool_result` JSON objects (with errors encoded) rather than raising exceptions. | Guarantees tool handlers always receive predictable messages so they can report structured failures without splitting the stream, letting the CLI surface tool errors consistently and giving the doctor a watchable invariant for structured tool responses; the validation doc now points at the same message names so tooling checks can reconcile the stream shape with the health rules. |
---
## OBJECTIVES COVERED

| Objective | Validations | Rationale |
|-----------|-------------|-----------|
| LLM Agents correctness — preserve the adapter’s core invariants around credential gating and streaming contracts | V1, V2, V4, V5 | Validating credential gating, stream shape, debug isolation, and structured tool error handling keeps the adapter deterministic, prevents silent contract violations, and gives downstream orchestrators confidence in the provider boundary while supplying a documented invariant to the doctor; the BEHAVIORS GUARANTEED table also surfaces these guarantees so `mind validate` can link them back to the validators. |
| LLM Agents clarity — keep observable outputs legible for humans and orchestrators | V2, V3, V4 | Enforcing the JSON/text modes and stderr isolation protects downstream parsers and observers from mixed formats, keeping observable behavior easy to interpret while avoiding noise in dashboards and making the performance story traceable; the OBJECTIVES COVERED narrative highlights this clarity so future agents know the invariants tie to human-readable behavior. |
| LLM Agents performance — stay within intended budgets by avoiding redundant retries or malformed streams | V2, V5 | Constraining the stream envelope and tool messages avoids unnecessary replays or parsing differences that could blow budgets or trigger extra API calls, so health monitors see predictable throughput and the metrics remain stable; the document now describes how the invariants keep performance budgets bounded so the doctor can recognize regressions quickly. |

---

## INVARIANTS

### V1: Missing Credentials Fail Fast

- If GEMINI_API_KEY is absent from all sources, the adapter emits a JSON error and exits with code 1.

### V2: Streaming Output Shape

- For `stream-json`, each streamed chunk must be wrapped in a JSON object with `type: "assistant"` and a `message.content` list containing text parts.
- A final JSON object with `type: "result"` must include the full concatenated response text.

### V3: Text Output Is Plain

- For `text`, the adapter prints only the response text with no JSON wrapper.

### V4: Debug Output Is Isolated

- Model listing and related errors are written to stderr only, so stdout remains parseable for the CLI.

### V5: Tool Calls Return Structured Results

- Tool calls emit a `tool_code` message and a corresponding `tool_result` message on stdout.
- Tool execution errors return a JSON object with an `error` key instead of raising.

---

## EDGE CASES

- Gemini returns empty chunks: only non-empty chunk.text should be emitted.
- Gemini SDK throws during model listing: the adapter still proceeds after logging to stderr.

---

## VERIFICATION METHODS

- Manual run with/without GEMINI_API_KEY to verify error handling.
- Manual run with `--output-format stream-json` to confirm JSON structure.
- Manual run with `--output-format text` to confirm plain output.

---

## FAILURE MODES

- Missing `GEMINI_API_KEY` produces a JSON error and exit 1.
- Unexpected SDK exceptions are returned as JSON error objects on stdout.

---

## PROPERTIES

- `GeminiAdapter` enforces stream shape and error isolation, so downstream consumers never see mixing of JSON/state text.
- The invariants are agnostic to model selection; a new provider must still satisfy these behaviors before being considered safe.

---

## ERROR CONDITIONS

- `MissingCredential`: raised when GEMINI_API_KEY is not found in env, config, or CLI.
- `StreamShapeViolation`: when `stream-json` output omits `type: "assistant"`.
- `ToolCallFailure`: emitted as the `tool_result` message when tool execution errors occur.

---

## HEALTH COVERAGE

- `prompt_doc_reference_check` now depends on the Gemini adapter referencing `docs/llm_agents/PATTERNS_Provider_Specific_LLM_Subprocesses.md`.
- `doctor_check_code_doc_delta_coupling` ensures doc/SYNC/implementation updates stay in sync with adapter changes.
- `doctor_check_yaml_drift` now monitors `modules.yaml` entries so additional providers self-document.

---

## VERIFICATION PROCEDURE

1. Run `NG_ENV=dev mind work --provider gemini` and assert the output structure rules hold.
2. Validate error detection by unsetting `GEMINI_API_KEY` and confirming the CLI exits with a JSON error.
3. Add a new provider and verify these invariants via the same tests before marking the change canonical.

---

## SYNC STATUS

```
LAST_VERIFIED: 2025-12-21
VERIFIED_AGAINST:
    impl: mind/llms/gemini_agent.py @ HEAD
VERIFIED_BY: codex
RESULT:
    V1: PASS
    V2: PASS
    V3: PASS
    V4: PASS
    V5: PASS
```

---

## MARKERS

<!-- @mind:todo Should we define explicit severity weighting for stream errors vs. tool failures? -->
<!-- @mind:proposition Add JSON schema validation for `tool_result` payloads so downstream parsers can rely on a rigid contract. -->
