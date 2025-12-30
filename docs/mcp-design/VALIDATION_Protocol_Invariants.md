# mind Framework — Validation: Protocol Invariants

```
STATUS: STABLE
CREATED: 2024-12-15
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Bidirectional_Documentation_Chain_For_AI_Agents.md
BEHAVIORS:       ./BEHAVIORS_Observable_Protocol_Effects.md
ALGORITHM:       ./ALGORITHM_Protocol_Core_Mechanics.md
THIS:            VALIDATION_Protocol_Invariants.md
IMPLEMENTATION:  ./IMPLEMENTATION_Protocol_System_Architecture.md
TEST:            ./TEST_Protocol_Test_Cases.md
SYNC:            ./SYNC_Protocol_Current_State.md
```

---

## INVARIANTS

### V1: Every Implementation Has a Doc Reference

```
FOR EACH implementation file in {area}/{module}.py:
    ASSERT: File header contains "DOCS:" or path to docs folder
    ASSERT: Referenced docs folder exists
```

**Checked by:** Manual review or `scripts/check_doc_refs.py` (to be implemented)

### V2: Every Module Doc Folder Has Minimum Files

```
FOR EACH docs/{area}/{module}/ folder:
    ASSERT EXISTS: PATTERNS_*.md
    ASSERT EXISTS: SYNC_*.md
```

**Checked by:** Manual review or `scripts/check_doc_completeness.py`

### V3: All CHAIN Links Are Valid

```
FOR EACH .md file in docs/:
    FOR EACH path in CHAIN section:
        ASSERT: File at path EXISTS
```

**Checked by:** `scripts/check_chain_links.py` (to be implemented)

### V4: SYNC Files Are Recent

```
FOR EACH SYNC_*.md file:
    ASSERT: LAST_UPDATED date exists
    ASSERT: LAST_UPDATED is within reasonable time of last code change
```

**Checked by:** Compare git history with SYNC dates

### V5: No Orphan Implementation Files

```
FOR EACH implementation file:
    ASSERT: Corresponding docs/{area}/{module}/ exists
    OR: File is utility/helper not requiring full docs
```

**Checked by:** `scripts/check_orphans.py` (to be implemented)

### V6: Project SYNC Exists and Is Current

```
ASSERT EXISTS: ...mind/state/SYNC_Project_State.md
ASSERT: LAST_UPDATED is recent
```

**Checked by:** Manual check

### V7: All VIEWs Reference Existing File Types

```
FOR EACH VIEW_*.md file:
    FOR EACH file path referenced:
        ASSERT: Path pattern is valid
        ASSERT: Path uses correct naming conventions
```

**Checked by:** Manual review

---

## PROPERTIES

### P1: Bidirectional Navigation

```
FORALL implementation I with docs D:
    following_path(I → D → I) returns to original I
    following_path(D → I → D) returns to original D
```

**Tested by:** Manual spot check

### P2: SYNC Reflects Reality

```
FORALL SYNC file S:
    claims_in(S) match observable_state()
```

**Tested by:** Review during changes

### P3: VIEW Sufficiency

```
FORALL task T and VIEW V for T:
    following(V) provides sufficient context to complete T
    without needing unlisted files
```

**Tested by:** Agent feedback / iteration

---

## ERROR CONDITIONS

### E1: Missing Doc Reference in Implementation

```
WHEN:    Implementation file has no DOCS reference
THEN:    Navigation from code to docs is broken
SYMPTOM: Agent can't find design rationale
FIX:     Add DOCS reference to file header
```

### E2: Stale SYNC

```
WHEN:    SYNC hasn't been updated after code changes
THEN:    Next agent gets incorrect state
SYMPTOM: Agent repeats work or makes wrong assumptions
FIX:     Update SYNC after every change
```

### E3: Dead Chain Link

```
WHEN:    CHAIN section references non-existent file
THEN:    Navigation is broken
SYMPTOM: 404 when following documentation chain
FIX:     Create missing file or fix link
```

### E4: Orphan Module

```
WHEN:    Implementation exists without docs
THEN:    Agent has no design context
SYMPTOM: Changes violate unknown patterns
FIX:     Create minimum docs (PATTERNS, SYNC)
```

---

## HEALTH COVERAGE

| Requirement | Test / Check | Status |
|-------------|--------------|--------|
| V1: Doc refs | Manual / script | ⚠ Script not implemented |
| V2: Min files | Manual / script | ⚠ Script not implemented |
| V3: Chain links | Manual / script | ⚠ Script not implemented |
| V4: SYNC recent | Manual | Manual only |
| V5: No orphans | Manual / script | ⚠ Script not implemented |
| V6: Project SYNC | Manual | Manual only |
| V7: VIEW validity | Manual | Manual only |

---

## VERIFICATION PROCEDURE

### Manual Checklist

For a given module:

```
[ ] Implementation has DOCS reference in header
[ ] docs/{area}/{module}/ exists
[ ] PATTERNS_*.md exists and describes design
[ ] SYNC_*.md exists and is current
[ ] All CHAIN links in docs are valid
[ ] No dead references
```

For project:

```
[ ] .mind/ folder exists
[ ] PROTOCOL.md is present
[ ] All VIEW files are present
[ ] Project SYNC is current
[ ] CLAUDE.md references protocol
[ ] AGENTS.md references protocol (mirrors .mind/CLAUDE.md)
[ ] AGENTS.md includes Codex guidance, starting with protocol-first reading, verbose outputs, and parallel-work awareness
```

### Automated (To Be Implemented)

```bash
# Check all invariants
python scripts/validate_protocol.py

# Check specific invariant
python scripts/validate_protocol.py --check V1

# Check specific module
python scripts/validate_protocol.py --module {area}/{module}
```

---

## SYNC STATUS

```
LAST_VERIFIED: 2024-12-15
VERIFIED_AGAINST: Protocol design complete
VERIFIED_BY: Initial creation
RESULT:
    V1-V7: Design specified, scripts not yet implemented
    P1-P3: Properties defined, testing manual
```

---

## MARKERS

<!-- @mind:todo Implement check_doc_refs.py -->
<!-- @mind:todo Implement check_chain_links.py -->
<!-- @mind:todo Implement check_orphans.py -->
<!-- @mind:todo Implement validate_protocol.py (umbrella script) -->
<!-- @mind:todo CI integration for validation -->
<!-- @mind:proposition Pre-commit hook for SYNC update reminder -->
<!-- @mind:escalation
title: "How strict should validation be? Warn vs block?"
priority: 5
response:
  status: resolved
  choice: "Persist valid, return precise errors"
  behavior: "Never block entirely. Persist everything persistable. Return structured errors with exact fix instructions. Output optimized for agent consumption — machine-parseable, actionable."
  notes: "2025-12-23: CLI is for agents. Be maximally helpful. Decided by Nicolas."
-->
