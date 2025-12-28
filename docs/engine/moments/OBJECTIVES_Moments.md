# Moment Graph — Objectives

```
STATUS: DESIGNING
VERSION: v0.1
CREATED: 2025-12-26
```

---

## CHAIN

```
THIS:           OBJECTIVES_Moments.md (you are here)
PATTERNS:       ./PATTERNS_Moments.md
BEHAVIORS:      ./BEHAVIORS_Moment_Lifecycle.md
ALGORITHM:      ./ALGORITHM_Moment_Graph_Operations.md
VALIDATION:     ./VALIDATION_Moment_Graph_Invariants.md
IMPLEMENTATION: ./IMPLEMENTATION_Moment_Graph_Stub.md
SYNC:           ./SYNC_Moments.md
```

---

## PURPOSE

Define what the moment graph module optimizes for, ranked by priority. These objectives guide all design tradeoffs.

---

## OBJECTIVES

### O1: Schema Is Canon (Critical)

**What we optimize:** Schema definitions are the single source of truth for moment structure.

**Why it matters:** Without a canonical schema, different parts of the system (narrator, engine, API, frontend) will diverge in their understanding of what a moment is. Schema-first prevents silent incompatibilities.

**Tradeoffs accepted:**
- Schema changes require coordination across modules
- Implementation must match schema exactly, not "close enough"
- Some flexibility sacrificed for consistency

**Measure:** All moment operations validate against schema; no schema violations in production.

---

### O2: Graph Is Truth (Critical)

**What we optimize:** The moment graph is the authoritative record of narrative state.

**Why it matters:** If moment state lives elsewhere (session cache, frontend state, narrator memory), truth diverges. The graph must be the source that all systems read and write.

**Tradeoffs accepted:**
- Graph queries may be slower than local cache
- All mutations must go through graph operations
- No "convenient" local state that bypasses graph

**Measure:** Any moment query returns same result from any caller.

---

### O3: Single Module Owner (Critical)

**What we optimize:** All moment-graph logic lives in mind/moments/.

**Why it matters:** Scattered ownership leads to inconsistent behavior, duplicate bugs, and unclear responsibility. Callers integrate with one module.

**Tradeoffs accepted:**
- Module may be larger than ideal
- Clear APIs required at boundaries
- Other modules cannot "shortcut" around this one

**Measure:** No moment lifecycle code outside mind/moments/.

---

### O4: Atomic Player-Visible Units (Important)

**What we optimize:** Moments are the smallest unit of narrative that players interact with.

**Why it matters:** Moments define the player's interaction surface with the story. If moments are too granular (every sentence) or too coarse (entire scenes), the pacing and agency feel wrong.

**Tradeoffs accepted:**
- Some narrative richness is chunked into discrete moments
- Transitions between moments must be explicit

**Measure:** Player actions map cleanly to moment transitions.

---

### O5: Link Semantics Are Explicit (Important)

**What we optimize:** Links between moments have clear, documented meanings.

**Why it matters:** THEN, WAIT, ENABLES, BLOCKS — these link types drive engine behavior. Ambiguous link semantics lead to unpredictable traversal.

**Tradeoffs accepted:**
- Limited link vocabulary (no arbitrary link types)
- New link types require schema updates

**Measure:** Every link type has documented behavior in schema.

---

### O6: Stub Compatibility (Nice to have)

**What we optimize:** API shape is stable even before full implementation.

**Why it matters:** Other modules need to integrate before graph-backed implementation is complete. Stub preserves API contract while implementation evolves.

**Tradeoffs accepted:**
- Stub behavior may not match final behavior exactly
- Some tests will be integration-only

**Measure:** API signatures don't change during implementation.

---

## OBJECTIVE CONFLICTS

| Conflict | Resolution |
|----------|------------|
| O1 vs O6 (schema strictness vs stub flexibility) | Stub validates inputs even if it doesn't persist |
| O2 vs performance | Cache reads, not truth; graph remains source |
| O3 vs code reuse | Import utilities; don't duplicate moment logic elsewhere |

---

## NON-OBJECTIVES

Things we explicitly do NOT optimize for:

- **Traversal mechanics** — That belongs to moment-graph-engine module
- **UI rendering of moments** — That belongs to frontend modules
- **Narrative reasoning** — That belongs to narrator agent
- **API endpoint design** — That belongs to API docs

---

## VERIFICATION

- [ ] All objectives have measures
- [ ] Conflicts documented with resolutions
- [ ] Non-objectives make boundaries clear
