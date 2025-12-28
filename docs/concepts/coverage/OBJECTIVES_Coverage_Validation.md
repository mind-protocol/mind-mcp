# OBJECTIVES: Coverage Validation System
@mind:id: OBJECTIVES.COVERAGE.VALIDATION.SYSTEM

```
STATUS: DESIGNING
PURPOSE: Ensure complete traceability from doctor detections through skills to protocols to graph mutations
```

---

## Primary Objective

**Complete path traceability**: Every doctor detection must have a verified path to graph mutation.

```
Doctor Detection → Skill → Protocol(s) → Steps → Output Cluster
```

No orphan detections (gaps without skills).
No orphan skills (skills without protocols).
No orphan protocols (protocols without complete steps).
No orphan steps (steps without graph mutations).

---

## Secondary Objectives

### S1: Single Source of Truth

One YAML file defines the complete mapping. All other artifacts (docs, reports, validations) derive from it.

**Supports primary**: Prevents drift between spec and implementation.

### S2: Machine-Checkable Validation

Automated script validates coverage completeness. Runs in CI, blocks on gaps.

**Supports primary**: Catches coverage regressions before they ship.

### S3: Human-Readable Reports

Generated markdown shows current coverage state. Developers can see gaps at a glance.

**Supports primary**: Makes coverage visible and actionable.

### S4: Incremental Development

Can add detections, skills, protocols incrementally. Validator shows what's missing.

**Supports primary**: Supports iterative development without losing track.

---

## Non-Objectives

### N1: Runtime Coverage

This system validates *spec completeness*, not runtime behavior. Health checks handle runtime.

**Bounds S2**: We're checking "does the path exist?" not "did it execute correctly?"

### N2: Protocol Implementation Details

Coverage validation checks that protocols exist and have required step types. It doesn't validate step logic.

**Bounds S2**: Protocol correctness is a separate concern (tests, health checks).

### N3: Automatic Protocol Generation

We're validating coverage, not generating missing protocols. Gaps are reported for humans to fill.

**Bounds S4**: Generation is a future concern.

---

## Success Criteria

1. Every doctor detection has a mapped skill
2. Every skill has mapped protocols
3. Every protocol exists as a YAML file
4. Every protocol has: ask, create steps (minimum)
5. Validator reports 0 gaps for shipped versions

---

## CHAIN

- **Next:** PATTERNS_Coverage_Validation.md
- **Implements:** Membrane System goals (G5: Traceable, G6: Dependency-aware)
