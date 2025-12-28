# Membrane Modulation — Sync: Current State

```
LAST_UPDATED: 2025-12-20
UPDATED_BY: codex
STATUS: DESIGNING
```

---

## MATURITY

**What's canonical (v1):**
- Membrane is defined as a modulation layer only (no canon writes).

**What's still being designed:**
- Modulation frame schema and bounds.
- Runtime hook points for frame application.
- Dynamic modulation functions and membrane context fields.

**What's proposed (v2+):**
- Health check automation for modulation drift.

---

## CURRENT STATE

Docs for membrane modulation (pattern, behaviors, algorithm, validation, health)
exist, but there is no implementation hook yet.

Membrane scoping is now defined as per-place modulation.
The PATTERN now also captures the dynamic modulation function strategy so a single doc remains canonical.

---

## RECENT CHANGES

### 2025-12-21: Consolidated membrane PATTERNS

- **What:** Merged the dynamic modulation function reasoning into `PATTERNS_Membrane_Scoping.md`, dropped the redundant duplicate doc, and refreshed the attention energy doc so references resolve to the single membrane PATTERN.
- **Why:** Prevent doc duplication in the membrane folder so every behavior has one authoritative PATTERN.
- **Impact:** Documentation is aligned with the "one solution per problem" principle; no runtime code changed.
- **Files:** `docs/mind/membrane/PATTERNS_Membrane_Scoping.md`, `docs/physics/attention/PATTERNS_Attention_Energy_Split.md`, `docs/mind/membrane/SYNC_Membrane_Modulation.md`
- **Verification:** `mind validate`

### 2025-12-20: Added membrane scoping pattern

- **What:** Added `PATTERNS_Membrane_Scoping.md`.
- **Why:** Make modulation scope explicit (per-place) and prevent global leakage.
- **Impact:** Documentation only; no runtime changes.

### 2025-12-20: Added implementation stub

- **What:** Added `IMPLEMENTATION_Membrane_Modulation.md`.
- **Why:** Close the doc chain and reserve implementation hooks.
- **Impact:** Documentation only; no runtime changes.

### 2025-12-20: Algorithm updated for per-place scoping

- **What:** Updated `ALGORITHM_Membrane_Modulation.md` with place_id scoping and compute skeleton.
- **Why:** Make per-place keying explicit at algorithm layer and define v0 compute shape.
- **Impact:** Documentation only; no runtime changes.

---

## IN PROGRESS

### Membrane Modulation Doc Chain

- **Started:** 2025-12-20
- **By:** codex
- **Status:** in progress
- **Context:** Establish contract before wiring runtime hooks.

---

## TODO

### Doc/Impl Drift

<!-- @mind:todo DOCS→IMPL: Add a membrane provider and apply a modulation frame in runtime. -->

### Tests to Run

```bash
mind validate
```

### Immediate

<!-- @mind:todo Define ModulationFrame bounds. -->
<!-- @mind:todo Decide injection point for frame computation. -->
<!-- @mind:todo Specify dynamic functions for threshold/decay/transfer. -->

### Later

<!-- @mind:todo Add health check script for bounds/idempotency. -->

---

## POINTERS

| What | Where |
|------|-------|
| Pattern | `docs/mind/membrane/PATTERNS_Membrane_Modulation.md` |
| Behaviors | `docs/mind/membrane/BEHAVIORS_Membrane_Modulation.md` |
| Scoping | `docs/mind/membrane/PATTERNS_Membrane_Scoping.md` |
