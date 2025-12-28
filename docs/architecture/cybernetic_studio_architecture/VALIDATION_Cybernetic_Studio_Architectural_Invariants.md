# ARCHITECTURE — Cybernetic Studio — Validation: Architectural Invariants

```
STATUS: DESIGNING
CREATED: 2025-12-20
VERIFIED: N/A
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Cybernetic_Studio_Architecture.md
BEHAVIORS:       ./BEHAVIORS_Cybernetic_Studio_System_Behaviors.md
ALGORITHM:       ./ALGORITHM_Cybernetic_Studio_Process_Flow.md
THIS:            VALIDATION_Cybernetic_Studio_Architectural_Invariants.md (you are here)
IMPLEMENTATION:  ./IMPLEMENTATION_Cybernetic_Studio_Code_Structure.md
HEALTH:          ./HEALTH_Cybernetic_Studio_Health_Checks.md
SYNC:            ./SYNC_Cybernetic_Studio_Architecture_State.md

IMPL:            N/A (Conceptual Architecture Document)
SOURCE:          ../../../data/ARCHITECTURE — Cybernetic Studio.md
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## INVARIANTS

These must ALWAYS be true:

### V1: Repo is the Source of Truth

```
Artifacts live in repos only. The graph stores EvidenceRefs and derived meaning,
never file contents.
```

**Checked by:** Manual review of storage practices + graph payload inspection (NOT YET VERIFIED)

### V2: Graph is Physics, Not Links-as-Glue

```
Relationships are represented as Narratives + Beliefs, not generic RELATED_TO edges.
```

**Checked by:** Schema audit of graph link types (NOT YET VERIFIED)

### V3: No Overmind Daemon

```
No privileged always-on global control loop; watchers emit stimuli and physics surfaces outcomes.
```

**Checked by:** Runtime process inventory + architecture review (NOT YET VERIFIED)

### V4: No Arbitrary Constants

```
Critical thresholds use adaptive gates (quantiles/EMA). Fixed constants are not allowed
except warmup floors.
```

**Checked by:** Gate implementation review (NOT YET VERIFIED)

### V5: Places are First-Class

```
SYNC files, UI rooms, and VIEWs are treated as Places that shape context and surfacing.
```

**Checked by:** Place registry/config review (NOT YET VERIFIED)

### V6: Graph Service Ownership

```
The graph service is owned and operated by `mind`. `blood-ledger` integrates as a client.
```

**Checked by:** Repo boundary review + deployment configuration audit (NOT YET VERIFIED)

---

## PROPERTIES

### P1: EvidenceRef Integrity

```
FORALL EvidenceRef:
    repo and path must resolve to an existing artifact without embedding content
```

**Verified by:** NOT YET VERIFIED — requires repo + graph integration checks

### P2: Stimulus Injection Coverage

```
FORALL events in {file_read, file_write, commit, exec/test_run}:
    event must emit a stimulus with at least one EvidenceRef or Place attachment
```

**Verified by:** NOT YET VERIFIED — requires watcher instrumentation

---

## ERROR CONDITIONS

### E1: Graph Service Unavailable

```
WHEN:    graph is unreachable
THEN:    repo operations proceed; stimuli are queued or dropped with explicit logging
SYMPTOM: missing surfaced candidates despite repo activity
```

**Verified by:** NOT YET VERIFIED — requires integration test harness

### E2: EvidenceRef Missing or Invalid

```
WHEN:    stimulus references a missing repo/path/sha
THEN:    record a failure narrative and avoid injecting to missing Things
SYMPTOM: dangling Thing nodes without resolvable artifacts
```

**Verified by:** NOT YET VERIFIED — requires validation tooling

---

## HEALTH COVERAGE

| Invariant | Signal | Status |
|-----------|--------|--------|
| V1: Repo is source of truth | evidence_ref_only_storage | ⚠ NOT YET VERIFIED |
| V2: No generic links | link_type_audit | ⚠ NOT YET VERIFIED |
| V3: No overmind | process_inventory | ⚠ NOT YET VERIFIED |
| V4: Adaptive gates | gate_audit | ⚠ NOT YET VERIFIED |
| V5: Places are real | place_registry | ⚠ NOT YET VERIFIED |
| V6: Graph ownership | ownership_boundary | ⚠ NOT YET VERIFIED |

---

## VERIFICATION PROCEDURE

### Manual Checklist

```
[ ] V1 holds — graph stores only EvidenceRefs, no file content
[ ] V2 holds — link types are limited to the allowed primitives
[ ] V3 holds — no privileged always-on controller exists
[ ] V4 holds — adaptive gates are used for thresholds
[ ] V5 holds — SYNC/UI/VIEWs are registered Places
[ ] V6 holds — graph service ownership is enforced in mind
[ ] All behaviors from BEHAVIORS_Cybernetic_Studio_System_Behaviors.md work
[ ] All edge cases handled
[ ] All anti-behaviors prevented
```

### Automated

```bash
# Pending: add integration checks once graph service wiring exists.
```

---

## SYNC STATUS

```
LAST_VERIFIED: N/A
VERIFIED_AGAINST:
    impl: N/A (Conceptual Architecture Document)
    test: N/A
VERIFIED_BY: N/A
RESULT:
    V1: NOT RUN
    V2: NOT RUN
    V3: NOT RUN
    V4: NOT RUN
    V5: NOT RUN
```

---

## MARKERS

<!-- @mind:todo Define a minimal graph audit script for EvidenceRef-only storage. -->
<!-- @mind:todo Add a link-type validator to prevent RELATED_TO usage. -->
<!-- @mind:escalation Should pressure computation be validated via sampled contradictions? -->
