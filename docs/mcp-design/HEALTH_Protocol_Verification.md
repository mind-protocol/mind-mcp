# mind Framework — Health: Protocol Verification and Mechanics

```
STATUS: STABLE
CREATED: 2025-12-20
```

---

## PURPOSE OF THIS FILE

This file defines the health verification mechanics for the mind protocol itself. It ensures the bidirectional documentation chain remains intact, invariants are respected, and the protocol remains useful for AI agents across different project structures.

It safeguards:
- **Structural Integrity:** Ensuring the `PATTERNS` → `BEHAVIORS` → `ALGORITHM` → `VALIDATION` → `IMPLEMENTATION` → `HEALTH` → `SYNC` chain is never broken.
- **Agent Context:** Ensuring that `DOCS:` references in code always lead to valid, high-quality documentation.
- **Maturity Tracking:** Ensuring that `SYNC` files accurately reflect the current state and maturity of each module.

Boundaries:
- This file covers the protocol's structural health.
- It does not verify the implementation logic of the CLI (covered in `docs/cli/HEALTH_CLI_Coverage.md`).

---

## WHY THIS PATTERN

HEALTH is separate from tests because it verifies real system health without changing implementation files. For the protocol, "implementation files" are the documentation files themselves. HEALTH monitoring ensures the docs don't drift from the reality of the code they describe.

- **Failure mode avoided:** "Documentation rot" where the protocol is present but the links are broken, leading to agent hallucinations.
- **Docking-based checks:** Uses `mind validate` as the primary verification engine.
- **Throttling:** Checks are lightweight enough to run on every agent interaction but can be throttled for very large codebases.

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Bidirectional_Documentation_Chain_For_AI_Agents.md
BEHAVIORS:       ./BEHAVIORS_Observable_Protocol_Effects.md
ALGORITHM:       ./ALGORITHM_Protocol_Core_Mechanics.md
VALIDATION:      ./VALIDATION_Protocol_Invariants.md
IMPLEMENTATION:  ./IMPLEMENTATION_Protocol_System_Architecture.md
THIS:            HEALTH_Protocol_Verification.md
SYNC:            ./SYNC_Protocol_Current_State.md

IMPL:            mind/validate.py
```

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: protocol_installation
    purpose: Ensures the protocol is correctly placed in the target project.
    triggers:
      - type: manual
        source: cli:mind init
    frequency:
      expected_rate: 1/project
      peak_rate: 10/min
    risks:
      - V-PROT-INIT: Broken .mind/ structure
    notes: Foundations for all other flows.

  - flow_id: chain_verification
    purpose: Validates bidirectional links between docs and code.
    triggers:
      - type: event
        source: cli:mind validate or agent startup
    frequency:
      expected_rate: 100/day
      peak_rate: 10/sec
    risks:
      - V-PROT-LINK: Dead references in CHAIN or DOCS: markers
    notes: The most frequent and critical health check.
```

---

## HEALTH INDICATORS SELECTED

```yaml
health_indicators:
  - name: chain_completeness
    flow_id: chain_verification
    priority: high
    rationale: Missing links in the documentation chain blind the AI agent.
  - name: reference_validity
    flow_id: chain_verification
    priority: high
    rationale: Broken links cause agents to fail or lose context.
```

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: ...mind/state/SYNC_Project_Health.md
  result:
    representation: binary
    value: 1
    updated_at: 2025-12-20T00:00:00Z
    source: chain_verification
```

---

## DOCK TYPES (COMPLETE LIST)

- `file` (all markdown files in docs/)
- `cli` (mind validate output)

---

## CHECKER INDEX

```yaml
checkers:
  - name: protocol_invariant_checker
    purpose: Runs all validation checks from VALIDATION_Protocol_Invariants.md.
    status: active
    priority: high
  - name: chain_link_checker
    purpose: Specifically verifies that all files listed in CHAIN headers exist.
    status: active
    priority: high
  - name: doc_link_integrity_checker
    purpose: Ensures every implementation file (e.g., `runtime/prompt.py`) points to the correct doc chain and vice versa (`docs/cli/prompt/*`). Now enforced by `mind doctor`.
    status: active
    priority: med
  - name: code_doc_delta_coupling
    purpose: Flags implementation changes without matching doc chain or SYNC updates (critical for modules like `prompt` with explicit health indicators). Now enforced by `mind doctor`.
    status: active
    priority: high
```

---

## INDICATOR: Chain Completeness

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: chain_completeness
  client_value: Agents have a full, logical path from high-level patterns to low-level implementation.
  validation:
    - validation_id: V-PROT-COMPLETE
      criteria: Every module must have at least PATTERNS, IMPLEMENTATION, and SYNC.
```

### HEALTH REPRESENTATION

```yaml
representation:
  allowed:
    - float_0_1
  selected:
    - float_0_1
  semantics:
    float_0_1: Percentage of modules that have a full documentation chain.
```

---

## HOW TO RUN

```bash
# Verify protocol health for the current project
mind validate

# Verify a specific module
mind validate --dir docs/cli
```

---

## KNOWN GAPS

<!-- @mind:todo Automated check for "doc quality" (e.g., minimum character counts per section). -->
<!-- @mind:todo Check for duplicate documentation across different modules. -->

---

## MARKERS

<!-- @mind:todo Add `mind doctor` checks for protocol-specific drift. -->
<!-- @mind:escalation Should `validate` warn about non-canonical doc types (e.g. `CONCEPT_`)? -->
