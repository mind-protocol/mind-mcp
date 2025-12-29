# VALIDATION: Project Health Doctor

**Invariants and verification for the doctor command.**

---

## INVARIANTS

### I1: Deterministic Results

**Given the same project state, doctor produces the same output.**

- No randomness in check execution
- File traversal order is sorted (alphabetical)
- Timestamps use file modification time, not current time
- Git operations use explicit references

### I2: No False Positives on Clean Projects

**A project following all conventions should score 100.**

- Empty project with just `.mind/` = 100
- Project with all docs complete = 100
- All checks have clear pass criteria

### I3: Severity Is Monotonic

**Critical > Warning > Info, always.**

- Critical issues always deduct more than warnings
- Warnings always deduct more than info
- No configuration can invert this

### I4: Score Is Bounded

**0 <= score <= 100, always.**

```python
assert 0 <= calculate_score(results) <= 100
```

### I5: Exit Code Reflects Criticality

**Exit 0 iff no critical issues.**

```python
if results["critical"]:
    assert exit_code == 1
else:
    assert exit_code == 0
```

### I6: Ignore Patterns Are Respected

**Ignored paths never appear in issues.**

```python
for issue in all_issues:
    for pattern in config["ignore"]:
        assert not fnmatch(issue.path, pattern)
```

### I7: Disabled Checks Don't Run

**Disabled checks produce no issues.**

```python
for issue in all_issues:
    assert issue.type not in config["disabled_checks"]
```

### I8: Doc Template Drift Threshold

**Section content below 50 characters is flagged.**

```python
for section in required_sections:
    if len(section_text) < 50:
        assert "DOC_TEMPLATE_DRIFT" in issues_for_doc
```

### I9: Doc Tags Respect Deferrals

**Postponed dates in the future suppress issues; past dates do not.**

```python
if postponed_until >= today:
    assert issue_not_reported
else:
    assert issue_reported
```

---

## CHECK CORRECTNESS

### Monolith Check

| Input | Expected |
|-------|----------|
| 499 line file, threshold 500 | No issue |
| 500 line file, threshold 500 | No issue |
| 501 line file, threshold 500 | Critical issue |
| 1000 line file in ignore pattern | No issue |

### Stale SYNC Check

| Input | Expected |
|-------|----------|
| SYNC updated today | No issue |
| SYNC updated 13 days ago, threshold 14 | No issue |
| SYNC updated 14 days ago, threshold 14 | Warning issue |
| SYNC with no LAST_UPDATED | Warning issue |
| SYNC in ignored path | No issue |

### Undocumented Check

| Input | Expected |
|-------|----------|
| src/foo/ with mapping in modules.yaml | No issue |
| src/foo/ with no mapping | Critical issue |
| src/foo/ mapped but docs path missing | Critical issue |
| vendor/ (common ignore) | No issue |

### Placeholder Check

| Input | Expected |
|-------|----------|
| Doc with `{TEMPLATE}` | Critical issue |
| Doc with `{anything}` in code block | No issue (code blocks excluded) |
| Doc with literal `{` in text | No issue (must be uppercase pattern) |

---

## OUTPUT FORMAT CORRECTNESS

### JSON Format

Must be valid JSON:
```python
json.loads(doctor_output)  # Should not raise
```

Must contain required fields:
```python
output = json.loads(doctor_output)
assert "score" in output
assert "issues" in output
assert "summary" in output
```

### Markdown Format

Must be valid markdown:
- Headers use `#` syntax
- Code blocks are fenced
- Tables are properly formatted

### Text Format

Must be readable in terminal:
- Lines under 80 chars (soft limit)
- ANSI colors only when stdout is TTY
- Clear visual hierarchy

---

## EDGE CASES

### Empty Project

```
.mind/
└── (default files)
```

Expected: Score 100, no issues.

### No Code Directories

Project with docs but no src/, lib/, etc.

Expected: MM check skipped, no false positives.

### Circular CHAIN Links

```
PATTERNS → BEHAVIORS → PATTERNS
```

Expected: Detected as issue, not infinite loop.

### Binary Files

Large binary files in src/.

Expected: Skipped (not counted as monolith).

### Symlinks

Symlinks in project structure.

Expected: Followed once, no infinite loops.

### Permission Errors

Unreadable files in project.

Expected: Warning logged, check continues.

---

## PERFORMANCE BOUNDS

| Project Size | Expected Time |
|--------------|---------------|
| Small (<100 files) | <1 second |
| Medium (<1000 files) | <5 seconds |
| Large (<10000 files) | <30 seconds |

Checks should be O(n) in file count, not O(n²).

---

## VERIFICATION COMMANDS

```bash
# Verify determinism
diff <(mind doctor) <(mind doctor)

# Verify exit codes
mind doctor && echo "Clean" || echo "Issues found"

# Verify JSON validity
mind doctor --format json | python -m json.tool

# Verify ignore patterns
mind doctor --format json | jq '.issues[][] | .path' | grep -v vendor/
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Project_Health_Doctor.md
BEHAVIORS:       ./BEHAVIORS_Project_Health_Doctor.md
ALGORITHM:       ./ALGORITHM_Project_Health_Doctor.md
VALIDATION:      THIS
IMPLEMENTATION:  ./IMPLEMENTATION_Project_Health_Doctor.md
HEALTH:          ./HEALTH_Project_Health_Doctor.md
SYNC:            ./SYNC_Project_Health_Doctor.md
```
