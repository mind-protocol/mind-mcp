# Procedure — Patterns: Self-Contained Steps with Audit Trail

```
STATUS: DRAFT v2.0
CREATED: 2025-12-29
UPDATED: 2025-12-29
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Procedure.md
THIS:            PATTERNS_Procedure.md (you are here)
BEHAVIORS:       ./BEHAVIORS_Procedure.md
VOCABULARY:      ./VOCABULARY_Procedure.md
ALGORITHM:       ./ALGORITHM_Procedure.md
VALIDATION:      ./VALIDATION_Procedure.md
IMPLEMENTATION:  ./IMPLEMENTATION_Procedure.md
HEALTH:          ./HEALTH_Procedure.md
SYNC:            ./SYNC_Procedure.md

IMPL:            runtime/connectome/procedure_runner.py (planned)
```

---

## THE PROBLEM

Claude agents lose context quickly. Best practices, vocabulary, behaviors — forgotten within turns. Every conversation restarts from zero understanding.

Documentation exists as static files. Procedures exist conceptually but aren't executable. No standard way to track state, validate progress, or deliver context.

**V1 tried:** Runtime doc chain loading via IMPLEMENTED_IN links.
**V2 insight:** That's over-engineered. The procedure **creator** should transform docs into step content. Runtime is simple.

---

## THE PATTERN

### Steps Are Guides

Each step is a **guide** — actionable instructions embedded in content. The creator transforms relevant docs into What/Why/How format.

```yaml
Step content:
  ## What you're doing
  Implementing check_validation()...

  ## Why
  Validation gates transitions...

  ## How
  1. Get validation spec from step content
  2. Query Run Space for required nodes
  3. Return pass/fail

  ## Watch out
  - No validation spec = auto-pass

  ## Validation to pass this step
  type: node_exists
  subtype: validation_result
```

**No runtime doc chain loading.** The step content IS the context.

### Template vs Execution

```
Procedure (Space, subtype: procedure) — READ-ONLY
├── [contains] → Step 1 (guide in content)
├── [contains] → Step 2 (guide in content)
└── [contains] → Step N (guide in content)

Run Space (Space, subtype: run) — AGENT WRITES HERE
├── [elaborates] → Procedure (template reference)
├── [acts on, e=8] → Active Step
├── [receives from, e=1] → Completed Step
└── [contains] → Agent's work
```

### Procedure Links to Doc Space (Audit Only)

```
Procedure ─[IMPLEMENTS]→ Implementation ─[IMPLEMENTS]→ ... → Objectives
```

This enables audit/verification. **Not loaded at runtime.**

### IMPLEMENTS Direction: Bottom → Top

Health IMPLEMENTS Implementation. Implementation IMPLEMENTS Validation. Etc.

```
Health → Implementation → Validation → Algorithm → Behaviors → Vocabulary → Patterns → Objectives
```

**Why this direction?** Each layer implements the layer above it.

### IMPLEMENTS Link Physics

| Property | Value | Rationale |
|----------|-------|-----------|
| hierarchy | -1 | Descends into implementation |
| polarity | [1, 0] | Forward only |
| permanence | 1 | Structural, immutable |
| energy | 1 | Stable, not hot |

---

## PRINCIPLES

### P1: Steps Are Self-Contained

The step content has everything the agent needs. No external doc loading.

**Why:** Simple runtime. Creator does the transformation work once. Agent reads and acts.

### P2: Execution Sandbox

Templates are read-only. Agents write to Run Space only.

**Why:** Protects procedures from corruption. Enables audit trails, retries, rollback.

### P3: Physics as Bookkeeping (V1)

Energy reflects state but doesn't drive routing.

```
acts on + energy 8 + polarity [0.9,0.1] = active step
receives from + energy 1 + polarity [0.2,0.8] = completed step
```

**Why:** Predictable, debuggable. Physics-based routing is V2.

### P4: Validation Gates Transition

Steps don't advance until work is verified.

**Why:** Graph state IS the proof. Query Run Space for required nodes/links.

### P5: Multi-Granularity Ready

V1: 1 node per doc, full text in content.
Later: Split into 1 node per behavior when needed.

**Why:** Start simple. Structure supports refinement without breaking.

---

## BEHAVIORS SUPPORTED

| Behavior | How Pattern Enables It |
|----------|------------------------|
| B1 (Step Has Complete Guide) | Step content includes What/Why/How |
| B2 (Agent Writes to Run Space Only) | Template/Execution separation |
| B3 (Explicit API Controls Flow) | Deterministic API, physics tracks |
| B4 (Physics Tracks State) | Energy/polarity on step links |
| B5 (Validation Gates Transition) | Check before advance |

## BEHAVIORS PREVENTED

| Anti-Behavior | How Pattern Prevents It |
|---------------|-------------------------|
| A1 (Template Mutation) | Separation makes template writes impossible |
| A2 (Multiple Active Steps) | Single high-energy link invariant |

---

## DOC CHAIN IN GRAPH

The style protocol chain becomes graph nodes:

```
Doc Space (space, subtype: doc_module)
├── [CONTAINS] → Objectives (narrative, subtype: objective)
├── [CONTAINS] → Patterns (narrative, subtype: pattern)
├── [CONTAINS] → Behaviors (narrative, subtype: behavior)
├── [CONTAINS] → Vocabulary (narrative, subtype: vocabulary)
├── [CONTAINS] → Algorithm (narrative, subtype: algorithm)
├── [CONTAINS] → Validation (narrative, subtype: validation)
├── [CONTAINS] → Implementation (narrative, subtype: implementation)
│                 └── [CONTAINS] → Procedure (space, subtype: procedure)
└── [CONTAINS] → Health (narrative, subtype: health)
```

IMPLEMENTS links between nodes (bottom → top):
```
Health ─[IMPLEMENTS]→ Implementation ─[IMPLEMENTS]→ Validation ─[IMPLEMENTS]→ Algorithm ─[IMPLEMENTS]→ Behaviors ─[IMPLEMENTS]→ Vocabulary ─[IMPLEMENTS]→ Patterns ─[IMPLEMENTS]→ Objectives
```

---

## SCOPE

### In Scope

- Sequential step execution with validation gates
- Steps as self-contained guides (content has everything)
- Run Space isolation (agent writes here only)
- Physics-based state tracking (energy/polarity)
- Procedure → Doc Space audit link (IMPLEMENTS)
- Multi-granularity support (1 node/doc → 1 node/behavior)

### Out of Scope

- Runtime doc chain loading → removed (V1 was wrong)
- Conditional branching → V2
- Procedure composition → V2
- Physics-based routing → V2
- Doc change triggers step review → V2

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `runtime/connectome/persistence.py` | Graph operations (create_node, create_link) |
| `runtime/physics/subentity.py` | Energy/polarity state interpretation |

**Removed dependency:** `cluster_presentation.py` for doc chain walking — not needed.

---

## INSPIRATIONS

- **State Machines**: Run Space tracks discrete states with explicit transitions
- **Literate Programming**: Step content is self-documenting
- **Event Sourcing**: Agent work in Run Space is append-only trace
- **Capability-based Security**: Run Space is a capability; template is protected

---

## MARKERS

<!-- @mind:proposition YAML→Graph migration: procedures/*.yaml could become graph-native -->
<!-- @mind:proposition Doc change → trigger step review (V2) -->
