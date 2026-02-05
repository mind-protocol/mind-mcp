# LLM Agents — Sync: Current State

```
LAST_UPDATED: 2025-12-30
UPDATED_BY: Claude (steward)
STATUS: DESIGNING
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Provider_Specific_LLM_Subprocesses.md
BEHAVIORS:       ./BEHAVIORS_Gemini_Agent_Output.md
ALGORITHM:       ./ALGORITHM_Gemini_Stream_Flow.md
VALIDATION:      ./VALIDATION_Gemini_Agent_Invariants.md
IMPLEMENTATION:  ./IMPLEMENTATION_LLM_Agent_Code_Architecture.md
HEALTH:          ./HEALTH_LLM_Agent_Coverage.md
THIS:            SYNC_LLM_Agents_State.md (you are here)
```

---

## MATURITY

**What's canonical (v1):**
- `gemini_agent.py` provides a Gemini CLI wrapper for the CLI.
- Streamed JSON output matches the CLI expectations used by other agents.

**What's still being designed:**
- Shared abstractions for additional LLM providers.
- Expanded tool schema support and richer message formatting for Gemini.

**What's proposed (v2+):**
- A reusable adapter base class for multi-provider consistency.
- Configurable model selection via CLI flags.

---

## CURRENT STATE

`runtime/llms/gemini_agent.py` implements a standalone CLI process that authenticates with GEMINI_API_KEY (CLI arg, `.env`, or env var), sends a prompt to Gemini, streams JSON output for the CLI, and executes basic local tools (filesystem/search/web fetch). Google search requests use a configurable base URL via `MIND_GOOGLE_SEARCH_URL`. The CLI builds the subprocess invocation from `runtime/agent_cli.py` when the `gemini` provider is selected.

---

## IN PROGRESS

None. Documentation has been reorganized for clarity and size limits.

---

## KNOWN ISSUES

No confirmed defects are tracked; the stderr model listing noise is
noted in handoff context and has not been triaged yet.

---

## RECENT CHANGES

### 2025-12-30: Reorganized Documentation for Size Limits

- **What:**
  1. Split HEALTH_LLM_Agent_Coverage.md (401 → 154 lines) into focused files:
     - Main HEALTH file kept as overview/index
     - Created HEALTH_Stream_Validity.md (140 lines) for stream_validity indicator details
     - Created HEALTH_API_Connectivity.md (140 lines) for api_connectivity indicator details
  2. Compressed IMPLEMENTATION_LLM_Agent_Code_Architecture.md (377 → 190 lines):
     - Removed verbose docking point specifications (referenced ALGORITHM instead)
     - Merged State Management, Runtime Behavior, and Concurrency into single "STATE & RUNTIME" section
     - Kept essential info: code structure, dependencies, schema, links
  3. Created archives/ directory and moved archive files there
- **Why:** LARGE_DOC_MODULE health check flagged these files as exceeding 200-line limit. Protocol principle: docs should be focused and digestible.
- **Impact:** All llm_agents documentation files now under 200 lines. Detailed specifications extracted to focused reference files while main docs remain navigable.
- **Files:**
  - `HEALTH_LLM_Agent_Coverage.md` (compressed to 154 lines)
  - `HEALTH_Stream_Validity.md` (new, 140 lines)
  - `HEALTH_API_Connectivity.md` (new, 140 lines)
  - `IMPLEMENTATION_LLM_Agent_Code_Architecture.md` (compressed to 190 lines)
  - `archives/SYNC_LLM_Agents_State_archive_2025-12.md` (moved to archives)

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** `VIEW_Implement_Write_Or_Modify_Code.md`

**Where I stopped:** Documentation restructuring complete. No code changes.

**What you need to understand:**
- The Gemini adapter is a thin wrapper that isolates provider SDK usage
- Streams JSON chunks for CLI, supports basic local tool execution
- Default model: `gemini-3-flash-preview`
- Health indicator specs now in separate files (HEALTH_Stream_Validity.md, HEALTH_API_Connectivity.md)

**Watch out for:**
The adapter prints model listings to stderr unconditionally; consider gating if that output is noisy.

**Open questions I had:**
Should we standardize adapter helpers for streaming JSON and error handling?

---

## HANDOFF: FOR HUMAN

**Executive summary:**
LLM agent docs now exist for the Gemini adapter, with module mapping and a DOCS pointer added.

**Decisions made:**
Documented the module as DESIGNING and kept the chain minimal (PATTERNS + SYNC).

**Needs your input:**
None.

---

## CONSCIOUSNESS TRACE

**Mental state when stopping:**
Calm, focused on minimal documentation to satisfy mapping requirements.

**Threads I was holding:**
Whether to document the stderr model listing as a known issue and whether to add more doc chain files.

**Intuitions:**
A shared adapter helper will likely appear once a second provider is added.

**What I wish I'd known at the start:**
That only the Gemini adapter exists, so the docs should stay lean.

---

## POINTERS

| What | Where |
|------|-------|
| Gemini adapter | `runtime/llms/gemini_agent.py` |
| CLI integration | `runtime/agent_cli.py` |


---

## TODO

<!-- @mind:todo Capture telemetry for LLM adapters (usage counts, errors, sync updates) so doctor can surface trends and the SYNC reflects real-world load. -->

## ARCHIVE

Older content archived to: `SYNC_LLM_Agents_State_archive_2025-12.md`


---

## ARCHIVE

Older content archived to: `SYNC_LLM_Agents_State_archive_2025-12.md`
