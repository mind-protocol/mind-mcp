# mind LLM Agents — Patterns: Provider-Specific LLM Subprocesses

```
STATUS: DRAFT
CREATED: 2025-12-19
VERIFIED: 2025-12-19 against commit ad538f8
```

---

## CHAIN

```
THIS:            PATTERNS_Provider_Specific_LLM_Subprocesses.md (you are here)
BEHAVIORS:       ./BEHAVIORS_Gemini_Agent_Output.md
ALGORITHM:       ./ALGORITHM_Gemini_Stream_Flow.md
VALIDATION:      ./VALIDATION_Gemini_Agent_Invariants.md
IMPLEMENTATION:  ./IMPLEMENTATION_LLM_Agent_Code_Architecture.md
HEALTH:          ./HEALTH_LLM_Agent_Coverage.md
SYNC:            ./SYNC_LLM_Agents_State.md

IMPL:            mind/llms/gemini_agent.py
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read the linked IMPL source file

**After modifying this doc:**
1. Update the IMPL source file to match, OR
2. Add a TODO in SYNC_*.md: "Docs updated, implementation needs: {what}"
3. Run tests: `{test command}`

**After modifying the code:**
1. Update this doc chain to match, OR
2. Add a TODO in SYNC_*.md: "Implementation changed, docs need: {what}"
3. Run tests: `{test command}`

---

## THE PROBLEM

The CLI needs to invoke different LLM providers with a consistent interface, but the provider SDKs and auth requirements are heterogeneous. Embedding those SDKs directly into the CLI would add heavy dependencies and blur responsibility for provider-specific behavior.

Without a dedicated adapter:
- CLI command construction would mix with provider SDK usage.
- Provider auth and output shaping would leak into core CLI logic.
- Each provider would require bespoke behavior scattered across the codebase.

---

## SCOPE

This pattern applies only to provider-specific subprocess wrappers that sit between the main CLI and external LLM SDKs. It covers adapter entry points, credential handling, prompt shaping, and JSON streaming output. It does not define core CLI routing, UI rendering, or multi-provider orchestration policies.

## DATA

Adapters consume CLI arguments, `.env` files, and environment variables for credentials and runtime options, plus a prompt/system prompt payload from the CLI. They emit structured JSON stream messages (tool_code, tool_result, text) and structured error payloads to stderr/stdout. Logs and debug output must be explicit so downstream clients can filter them safely.

---

## THE PATTERN

**Provider-specific subprocess adapters.**

Each provider gets its own small CLI wrapper that:
- Reads provider credentials from CLI args, `.env`, or environment variables.
- Adapts prompt/system prompt into the provider's expected input shape.
- Streams output in a normalized JSON format compatible with the TUI.
- Exits cleanly with structured errors when credentials or API calls fail.

The main CLI (`agent_cli.py`) builds a simple subprocess invocation and avoids SDK imports.

## BEHAVIORS SUPPORTED

This pattern guarantees the CLI can reliably launch each provider adapter without embedding provider SDKs or mixing credential loading into `agent_cli.py`.
- Provides endpoint adapters with a consistent streaming JSON shape and plain-text fallback so the TUI can parse either mode without format-guessing logic.
- Lets each adapter validate credentials, log errors, and emit structured output independently while the CLI keeps only a thin subprocess wrapper.

## BEHAVIORS PREVENTED

The subprocess boundary prevents the core CLI from importing heavyweight provider SDKs, keeping dependency management local to the adapter scripts.
- Keeps debug logs, model listings, and stack traces out of stdout so downstream consumers never parse mixed formats.
- Stops adapters from emitting mixed JSON/plain text sequences, ensuring every stream mode remains deterministic for the TUI.

---

## PRINCIPLES

### Principle 1: Keep provider SDKs out of core CLI

The CLI should not import provider SDKs directly. The adapter script owns the SDK usage and keeps the dependency surface isolated.

### Principle 2: Normalize streaming output

Adapters should emit JSON messages that mimic the expected streaming format so the TUI can consume output consistently, regardless of provider.

### Principle 3: Fail fast on missing credentials

Adapters should check for required API keys early and exit with explicit error messages to avoid confusing downstream failures.

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| google.generativeai | Gemini SDK used to make API calls |
| dotenv | Optional `.env` loading for GEMINI_API_KEY |
| argparse | CLI argument parsing |
| json | Stream JSON output for TUI |
| os | Environment variable access |

---

## INSPIRATIONS

- The Claude/Codex JSON stream format used by the TUI
- Unix-style subprocess boundaries for isolating dependencies

---

## WHAT THIS DOES NOT SOLVE

- Full tool schema translation or advanced tool routing for Gemini (only basic local tools are implemented)
- Model selection beyond the hard-coded default
- Conversation state management beyond the one-shot prompt flow

---

## MARKERS

<!-- @mind:todo Add a `--model` flag and document supported model IDs. -->
<!-- @mind:todo Decide whether the model listing debug output should be gated by a flag. -->
<!-- @mind:escalation Should adapters include a shared helper for JSON stream normalization? -->
