# VALIDATION: Completion Verification System

```
STATUS: DESIGNING
CREATED: 2025-12-24
```

---

## PURPOSE

Define mandatory completion verification for each issue type. Agents are NOT considered done until verification passes. Failed verification triggers agent restart with `--continue` and detailed feedback.

**Principle: "If it's not verified, it's not complete."**

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_MCP_Tools.md
PATTERNS:        ./PATTERNS_MCP_Tools.md
THIS:            VALIDATION_Completion_Verification.md
IMPLEMENTATION:  ./IMPLEMENTATION_MCP_Tools.md
SYNC:            ./SYNC_MCP_Tools.md

IMPL:            mind/repair_verification.py (may not exist - needs verification)
```

---

## ARCHITECTURE

```
Agent completes work
        ↓
Run file-level checks (quick)
        ↓
Run membrane protocol (graph verification)
        ↓
Run tests/health if applicable
        ↓
All pass? → COMPLETE
        ↓
Any fail? → Restart agent with --continue + feedback
```

---

## VERIFICATION CHECKS BY ISSUE TYPE

### UNDOCUMENTED

**Membrane Protocol:** `define_space`

| Check | Type | Verification |
|-------|------|--------------|
| Space exists in graph | membrane | `query: { find: space, where: { id: "space_{module}" } }` returns 1+ |
| SYNC narrative exists | membrane | `query: { find: narrative, type: sync, in_space: "{space_id}" }` returns 1+ |
| modules.yaml entry | file | Module has `docs:` path that exists |
| DOCS: ref in code | file | At least one source file has `# DOCS:` pointing to module docs |

**Failure feedback:**
```
INCOMPLETE: Module not fully documented.
- [ ] Space node missing in graph → run procedure_start("define_space")
- [ ] SYNC narrative missing → run procedure_start("update_sync")
- [ ] modules.yaml missing docs path → add docs: path to module entry
- [ ] No DOCS: reference in code → add "# DOCS: docs/{area}/{module}/..." to main source file
```

---

### STALE_SYNC

**Membrane Protocol:** `update_sync`

| Check | Type | Verification |
|-------|------|--------------|
| SYNC narrative updated | membrane | `query: { find: narrative, type: sync, where: { last_updated: ">={today}" } }` |
| Moment created | membrane | `query: { find: moment, type: sync_update, where: { tick_created: ">={session_start}" } }` |
| LAST_UPDATED in file | file | SYNC file has `LAST_UPDATED: {today}` |
| STATUS accurate | file | STATUS field matches actual state |

**Failure feedback:**
```
INCOMPLETE: SYNC not properly updated.
- [ ] SYNC narrative not in graph → run procedure_start("update_sync")
- [ ] No update moment recorded → run procedure_start("update_sync")
- [ ] LAST_UPDATED not today → update the file header
- [ ] STATUS doesn't match reality → verify and update STATUS
```

---

### INCOMPLETE_CHAIN

**Membrane Protocol:** `create_doc_chain`

| Check | Type | Verification |
|-------|------|--------------|
| All chain files exist | file | OBJECTIVES, PATTERNS, BEHAVIORS, ALGORITHM, VALIDATION, IMPLEMENTATION, SYNC all exist |
| CHAIN section valid | file | Each doc has CHAIN section with valid prev/next links |
| Narratives in graph | membrane | Each doc type has corresponding narrative node |
| Links in graph | membrane | `sequence` links connect narrative nodes |

**Failure feedback:**
```
INCOMPLETE: Documentation chain incomplete.
Missing files: {list_missing}
- [ ] Create missing docs → run procedure_start("create_doc_chain")
- [ ] Fix broken CHAIN links → update CHAIN sections to link correctly
- [ ] Add narratives to graph → run membrane protocols for each doc type
```

---

### NO_DOCS_REF

**Membrane Protocol:** `add_implementation`

| Check | Type | Verification |
|-------|------|--------------|
| DOCS: comment present | file | Source file has `# DOCS:` or `// DOCS:` comment |
| DOCS: path valid | file | Path in DOCS: comment exists |
| File in IMPLEMENTATION | file | IMPLEMENTATION doc lists this source file |
| Thing node in graph | membrane | `query: { find: thing, where: { source_path: "{file}" } }` returns 1+ |

**Failure feedback:**
```
INCOMPLETE: Code not linked to documentation.
- [ ] Add DOCS: comment → add "# DOCS: {correct_path}" to file header
- [ ] Invalid DOCS path → fix path to point to existing IMPLEMENTATION doc
- [ ] File not in IMPLEMENTATION → add file to CODE STRUCTURE section
- [ ] No thing node → run procedure_start("add_implementation")
```

---

### STUB_IMPL / INCOMPLETE_IMPL

**Membrane Protocol:** `add_implementation`

| Check | Type | Verification |
|-------|------|--------------|
| No stub markers | file | No `NotImplementedError`, `TODO`, `pass` (alone), `...` in function bodies |
| Tests exist | file | Test file exists for module |
| Tests pass | command | `pytest {test_file}` exits 0 |
| Health passes | command | `mind doctor --module {module}` shows no critical issues |
| Implementation narrative | membrane | `query: { find: narrative, type: implementation, in_space: "{space}" }` |

**Failure feedback:**
```
INCOMPLETE: Implementation not verified.
- [ ] Stub markers remain → implement all TODO/NotImplementedError/pass stubs
- [ ] No tests → create tests in tests/{module}/
- [ ] Tests failing → fix code until tests pass
- [ ] Health issues → run mind doctor and fix critical issues
- [ ] No implementation narrative → run procedure_start("add_implementation")
```

---

### MISSING_TESTS

**Membrane Protocol:** `add_health_coverage`

| Check | Type | Verification |
|-------|------|--------------|
| Test file exists | file | `tests/{module}/test_*.py` or similar exists |
| Tests pass | command | `pytest {test_path}` exits 0 |
| Coverage adequate | command | Coverage >= 60% for module (if coverage tool available) |
| HEALTH doc exists | file | `docs/{area}/{module}/HEALTH_*.md` exists |
| Health indicators in graph | membrane | `query: { find: narrative, type: health, in_space: "{space}" }` |

**Failure feedback:**
```
INCOMPLETE: Test coverage not verified.
- [ ] Test file missing → create test file following project conventions
- [ ] Tests fail → fix tests until they pass
- [ ] Coverage low → add more test cases
- [ ] No HEALTH doc → create HEALTH doc with indicators
- [ ] No health narrative → run procedure_start("add_health_coverage")
```

---

### MONOLITH

**Membrane Protocol:** `add_cluster` (for new modules created by split)

| Check | Type | Verification |
|-------|------|--------------|
| File size reduced | file | Original file < 500 lines OR largest function < 200 lines |
| New file(s) created | file | At least one new file extracted |
| Imports valid | command | `python -c "import {module}"` succeeds |
| Tests pass | command | `pytest` for affected modules |
| IMPLEMENTATION updated | file | New file(s) listed in IMPLEMENTATION doc |
| modules.yaml updated | file | New file(s) have entries if they're new modules |

**Failure feedback:**
```
INCOMPLETE: Monolith not properly split.
- [ ] File still too large → extract more functions/classes
- [ ] No new files → create new module for extracted code
- [ ] Import errors → fix import paths
- [ ] Tests failing → update tests for new structure
- [ ] IMPLEMENTATION not updated → add new files to CODE STRUCTURE
- [ ] modules.yaml not updated → add new module entries
```

---

### ESCALATION

**Membrane Protocol:** `capture_decision`

| Check | Type | Verification |
|-------|------|--------------|
| Decision recorded | membrane | `query: { find: moment, type: decision, where: { conflict: "{conflict_id}" } }` |
| ESCALATION → DECISION | file | SYNC file shows DECISION, not ESCALATION for this item |
| Code/docs consistent | file | The resolved conflict is actually fixed (no contradictions) |

**Failure feedback:**
```
INCOMPLETE: Escalation not resolved.
- [ ] No decision recorded → run procedure_start("capture_decision")
- [ ] Still marked ESCALATION → change to DECISION in SYNC
- [ ] Contradiction remains → update code/docs to match decision
```

---

## GLOBAL VERIFICATION REQUIREMENTS

Every issue type MUST verify:

| Check | Type | Always Required |
|-------|------|-----------------|
| Git commit exists | git | HEAD changed during repair |
| SYNC updated | file | Module SYNC or Project SYNC has today's date |
| No new critical issues | command | `mind doctor` doesn't show new criticals |

---

## AGENT RESTART PROTOCOL

When verification fails:

```yaml
restart_protocol:
  max_retries: 3

  on_failure:
    - collect: verification_results
    - format: feedback_message
    - restart_agent:
        flag: --continue
        session: previous_session_id
        inject_prompt: |
          ## VERIFICATION FAILED

          Your previous attempt did not pass all verification checks.

          ### Failed Checks:
          {failed_checks_formatted}

          ### Required Actions:
          {required_actions}

          ### Membrane Protocols to Run:
          {membrane_protocols}

          Complete these actions, then verification will run again.

  on_max_retries:
    - mark: issue as BLOCKED
    - create: escalation in SYNC
    - notify: human review required
```

---

## IMPLEMENTATION NOTES

### Verification Runner

```python
@dataclass
class VerificationResult:
    check_name: str
    check_type: str  # file, membrane, command
    passed: bool
    message: str
    required_action: Optional[str] = None
    membrane_protocol: Optional[str] = None

def verify_completion(
    issue: DoctorIssue,
    target_dir: Path,
    membrane_client: MembraneClient,
) -> List[VerificationResult]:
    """Run all verification checks for an issue type."""
    checks = VERIFICATION_CHECKS[issue.issue_type]
    results = []

    for check in checks:
        if check.type == "file":
            result = run_file_check(check, target_dir)
        elif check.type == "membrane":
            result = run_membrane_check(check, membrane_client)
        elif check.type == "command":
            result = run_command_check(check, target_dir)
        results.append(result)

    return results
```

### Feedback Formatter

```python
def format_verification_feedback(results: List[VerificationResult]) -> str:
    """Format failed checks into agent-readable feedback."""
    failed = [r for r in results if not r.passed]

    lines = ["## VERIFICATION FAILED", ""]
    lines.append("### Failed Checks:")
    for r in failed:
        lines.append(f"- [ ] {r.check_name}: {r.message}")

    lines.append("")
    lines.append("### Required Actions:")
    for r in failed:
        if r.required_action:
            lines.append(f"- {r.required_action}")

    protocols = set(r.membrane_protocol for r in failed if r.membrane_protocol)
    if protocols:
        lines.append("")
        lines.append("### Membrane Protocols to Run:")
        for p in protocols:
            lines.append(f"- procedure_start(\"{p}\")")

    return "\n".join(lines)
```

---

## MARKERS

<!-- @mind:todo Implement repair_verification.py with VerificationResult dataclass -->
<!-- @mind:todo Add membrane query client for verification checks -->
<!-- @mind:todo Integrate verification into repair_core.py spawn_repair_agent_async -->
<!-- @mind:todo Add --continue support for agent restart -->
<!-- @mind:todo Track retry count per issue -->
