# BEHAVIORS: Coverage Validation System
@mind:id: BEHAVIORS.COVERAGE.VALIDATION.SYSTEM

```
STATUS: DESIGNING
PURPOSE: Observable behaviors of the coverage validation system
```

---

## B1: Load Coverage Spec

**Trigger:** Validator starts

**Behavior:**
1. Read `specs/coverage.yaml`
2. Parse into structured data
3. If parse fails → exit with error

**Achieves:** S1 (Single Source of Truth)

**Observable:**
```
$ python validate_coverage.py
Loading specs/coverage.yaml...
Loaded: 15 detections, 6 skills, 17 protocols
```

---

## B2: Validate Detection → Skill Mapping

**Trigger:** Coverage spec loaded

**Behavior:**
1. For each detection in `doctor_workflow.detections`
2. Check `skill` field references existing skill in `skills`
3. If missing → record gap

**Achieves:** Primary (Complete path traceability)

**Observable:**
```
Checking detection mappings...
✓ D-UNDOC-CODE → mind.create_module_docs
✓ D-PLACEHOLDER-DOCS → mind.create_module_docs
✗ D-ORPHAN-DOCS → mind.unknown_skill (MISSING)
```

---

## B3: Validate Skill → Protocol Mapping

**Trigger:** Detection mapping validated

**Behavior:**
1. For each skill in `skills`
2. Check each protocol in `protocols` list exists in `protocols` section
3. If missing → record gap

**Achieves:** Primary (Complete path traceability)

**Observable:**
```
Checking skill → protocol mappings...
✓ mind.create_module_docs → [explore_space, create_doc_chain]
✗ mind.create_module_docs → create_doc_chain (PROTOCOL MISSING)
```

---

## B4: Validate Protocol Existence

**Trigger:** Skill mapping validated

**Behavior:**
1. For each protocol in `protocols`
2. Check `file` path exists on filesystem
3. If missing → record gap

**Achieves:** S2 (Machine-Checkable)

**Observable:**
```
Checking protocol files...
✓ explore_space → protocols/explore_space.yaml
✓ record_work → protocols/record_work.yaml
✗ create_doc_chain → protocols/create_doc_chain.yaml (FILE MISSING)
```

---

## B5: Validate Protocol Completeness

**Trigger:** Protocol file exists

**Behavior:**
1. Parse protocol YAML
2. Check for required step types (ask, create minimum)
3. Check output section defines nodes and links
4. If incomplete → record gap

**Achieves:** S2 (Machine-Checkable)

**Observable:**
```
Checking protocol completeness...
✓ explore_space: has ask, query, create
✓ record_work: has ask, branch, create
✗ incomplete_protocol: missing create step
```

---

## B6: Detect Circular Calls

**Trigger:** Protocol files validated

**Behavior:**
1. Build call graph from `call_protocol` steps
2. Check for cycles using DFS
3. If cycle found → record gap

**Achieves:** Anti-pattern A4 prevention

**Observable:**
```
Checking for circular calls...
✓ No circular dependencies found
```
or
```
✗ Circular dependency: protocol_a → protocol_b → protocol_a
```

---

## B7: Generate Coverage Report

**Trigger:** All validations complete

**Behavior:**
1. Aggregate all gaps
2. Calculate coverage percentage
3. Generate `COVERAGE_REPORT.md`

**Achieves:** S3 (Human-Readable Reports)

**Observable:**
```
Generating coverage report...
Coverage: 14/17 protocols (82%)
Gaps: 3
Report written to COVERAGE_REPORT.md
```

---

## B8: Exit with Status

**Trigger:** Report generated

**Behavior:**
1. If gaps == 0 → exit 0
2. If gaps > 0 → exit 1

**Achieves:** S2 (Machine-Checkable, CI gate)

**Observable:**
```
$ python validate_coverage.py && echo "OK" || echo "GAPS FOUND"
GAPS FOUND
```

---

## B9: Show Gap Details

**Trigger:** Gaps found

**Behavior:**
1. For each gap, show:
   - Layer (detection/skill/protocol)
   - ID of missing item
   - What references it
   - Suggested fix

**Achieves:** S4 (Incremental Development)

**Observable:**
```
GAP: Protocol 'create_doc_chain' missing
  Referenced by: skill mind.create_module_docs
  Fix: Create protocols/create_doc_chain.yaml
```

---

## Behavior Matrix

| Behavior | Input | Output | Achieves |
|----------|-------|--------|----------|
| B1 Load | specs/coverage.yaml | Parsed data | S1 |
| B2 Detection→Skill | Detections | Gaps list | Primary |
| B3 Skill→Protocol | Skills | Gaps list | Primary |
| B4 Protocol Exists | Protocol refs | Gaps list | S2 |
| B5 Protocol Complete | Protocol files | Gaps list | S2 |
| B6 Circular Calls | Call graph | Gaps list | A4 prevention |
| B7 Generate Report | All gaps | COVERAGE_REPORT.md | S3 |
| B8 Exit Status | Gaps count | Exit code | S2 |
| B9 Gap Details | Gaps list | Formatted output | S4 |

---

## CHAIN

- **Prev:** PATTERNS_Coverage_Validation.md
- **Next:** ALGORITHM_Coverage_Validation.md
