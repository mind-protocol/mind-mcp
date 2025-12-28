# VALIDATION: Coverage Validation System
@mind:id: VALIDATION.COVERAGE.VALIDATION.SYSTEM

```
STATUS: DESIGNING
PURPOSE: Invariants that must hold for the coverage system
```

---

## V-COV-001: No Orphan Detections

**Priority:** HIGH

**Invariant:** Every detection in `doctor_workflow.detections` must reference a skill that exists in `skills`.

**Formal:**
```
∀ d ∈ detections: d.skill ∈ skills.keys()
```

**Failure mode:** Doctor detects a gap but has no skill to handle it. Gap goes unaddressed.

**Ensures:** B2 (Validate Detection → Skill Mapping)

---

## V-COV-002: No Orphan Skills

**Priority:** HIGH

**Invariant:** Every skill must be referenced by at least one detection.

**Formal:**
```
∀ s ∈ skills: ∃ d ∈ detections: d.skill == s.id
```

**Failure mode:** Dead code. Skill exists but never used.

**Ensures:** Code hygiene

---

## V-COV-003: No Empty Protocol Lists

**Priority:** HIGH

**Invariant:** Every skill must reference at least one protocol.

**Formal:**
```
∀ s ∈ skills: len(s.protocols) > 0
```

**Failure mode:** Skill claims to handle detection but does nothing.

**Ensures:** B3 (Validate Skill → Protocol Mapping)

---

## V-COV-004: Protocol References Valid

**Priority:** HIGH

**Invariant:** Every protocol referenced by a skill must exist in `protocols`.

**Formal:**
```
∀ s ∈ skills: ∀ p ∈ s.protocols: p ∈ protocols.keys()
```

**Failure mode:** Skill references non-existent protocol. Runtime error when invoked.

**Ensures:** B3 (Validate Skill → Protocol Mapping)

---

## V-COV-005: Protocol Files Exist

**Priority:** HIGH

**Invariant:** Every protocol's file path must exist on filesystem.

**Formal:**
```
∀ p ∈ protocols: exists(p.file)
```

**Failure mode:** Protocol defined in spec but file missing. Membrane can't load it.

**Ensures:** B4 (Validate Protocol Existence)

---

## V-COV-006: Protocol Has Ask Step

**Priority:** MED

**Invariant:** Every protocol must have at least one `ask` step.

**Formal:**
```
∀ p ∈ protocols: ∃ step ∈ p.steps: step.type == "ask"
```

**Failure mode:** Protocol runs without gathering input. Hardcoded behavior.

**Ensures:** B5 (Validate Protocol Completeness)

---

## V-COV-007: Protocol Has Create Step

**Priority:** HIGH

**Invariant:** Every protocol must have at least one `create` step.

**Formal:**
```
∀ p ∈ protocols: ∃ step ∈ p.steps: step.type == "create"
```

**Failure mode:** Protocol runs but creates nothing. No graph mutation.

**Ensures:** B5 (Validate Protocol Completeness)

---

## V-COV-008: Protocol Has Output Definition

**Priority:** MED

**Invariant:** Every protocol must define its output cluster (nodes and links).

**Formal:**
```
∀ p ∈ protocols: p.output.cluster.nodes != [] ∧ p.output.cluster.links != []
```

**Failure mode:** Protocol creates nodes but output undocumented. Can't trace what it produces.

**Ensures:** Traceability

---

## V-COV-009: No Circular Protocol Calls

**Priority:** HIGH

**Invariant:** The protocol call graph must be acyclic.

**Formal:**
```
¬∃ cycle in call_graph(protocols)
```

**Failure mode:** Infinite loop. Protocol A calls B calls A.

**Ensures:** B6 (Detect Circular Calls)

---

## V-COV-010: Call Targets Exist

**Priority:** HIGH

**Invariant:** Every `call_protocol` step must reference an existing protocol.

**Formal:**
```
∀ p ∈ protocols: ∀ step ∈ p.steps:
    step.type == "call_protocol" → step.protocol ∈ protocols.keys()
```

**Failure mode:** Protocol tries to call non-existent sub-protocol. Runtime error.

**Ensures:** Referential integrity

---

## V-COV-011: Detection IDs Unique

**Priority:** MED

**Invariant:** All detection IDs must be unique.

**Formal:**
```
∀ d1, d2 ∈ detections: d1 ≠ d2 → d1.id ≠ d2.id
```

**Failure mode:** Ambiguous references. Can't tell which detection triggered.

**Ensures:** Unambiguous identification

---

## V-COV-012: Skill IDs Unique

**Priority:** MED

**Invariant:** All skill IDs must be unique.

**Formal:**
```
∀ s1, s2 ∈ skills: s1 ≠ s2 → s1.id ≠ s2.id
```

**Failure mode:** Skill shadowing. Wrong skill loaded.

**Ensures:** Unambiguous identification

---

## Validation Matrix

| ID | Priority | Invariant | Behavior |
|----|----------|-----------|----------|
| V-COV-001 | HIGH | No orphan detections | B2 |
| V-COV-002 | HIGH | No orphan skills | - |
| V-COV-003 | HIGH | No empty protocol lists | B3 |
| V-COV-004 | HIGH | Protocol refs valid | B3 |
| V-COV-005 | HIGH | Protocol files exist | B4 |
| V-COV-006 | MED | Protocol has ask | B5 |
| V-COV-007 | HIGH | Protocol has create | B5 |
| V-COV-008 | MED | Protocol has output | B5 |
| V-COV-009 | HIGH | No circular calls | B6 |
| V-COV-010 | HIGH | Call targets exist | B6 |
| V-COV-011 | MED | Detection IDs unique | - |
| V-COV-012 | MED | Skill IDs unique | - |

---

## CHAIN

- **Prev:** ALGORITHM_Coverage_Validation.md
- **Next:** IMPLEMENTATION_Coverage_Validation.md
