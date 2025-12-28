# ARCHITECTURE — Cybernetic Studio — Algorithm: Stimulus-to-Surface Flow

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
THIS:            ALGORITHM_Cybernetic_Studio_Process_Flow.md (you are here)
VALIDATION:      ./VALIDATION_Cybernetic_Studio_Architectural_Invariants.md
IMPLEMENTATION:  ./IMPLEMENTATION_Cybernetic_Studio_Code_Structure.md
HEALTH:          ./HEALTH_Cybernetic_Studio_Health_Checks.md
SYNC:            ./SYNC_Cybernetic_Studio_Architecture_State.md

IMPL:            N/A (Conceptual Architecture Document)
SOURCE:          ../../../data/ARCHITECTURE — Cybernetic Studio.md
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

This algorithm describes the system-level flow from stimuli in the repos to surfaced, canonized knowledge in the shared graph. It is conceptual and applies across `mind` and `blood-ledger` with the graph as the physics layer.

---

## DATA STRUCTURES

### Stimulus

```
Type: L1 (raw) or L2 (derived)
Sources: commit, file_read, file_write, exec/test_run, backend_error, conversation
Fields (conceptual): type, timestamp, evidence_refs[], metadata
```

### EvidenceRef

```
repo, commit_sha, path, range (optional), fingerprint (optional), run_id/test_id (optional)
```

### Graph Primitives

```
Nodes: Character, Place, Thing, Narrative, Moment
Links: BELIEF, NARRATIVE_LINK, THEN, PRESENT, ATTACHED_TO, ABOUT
```

### Gate

```
Adaptive threshold (rolling quantile/EMA) that triggers flips or surfacing
```

---

## ALGORITHM: Stimulus-to-Surface Flow

### Step 1: Capture L1 Stimuli

Collect raw stimuli from repo events (read/write/commit/exec) or system events (backend error, conversation). Attach EvidenceRefs when available.

### Step 2: Derive L2 Stimuli

Normalize L1 inputs into intent/incident forms that the physics layer can route (e.g., intent.reconcile_beliefs, incident.backend_error).

### Step 3: Inject Energy

Inject energy into:
- Things referenced by EvidenceRefs
- Narratives ABOUT those Things
- The active Place (SYNC/UI/VIEW)

### Step 4: Route Energy

Propagate energy along allowed channels (BELIEF, THEN, ABOUT, PRESENT, ATTACHED_TO). Avoid generic relationship links.

### Step 5: Compute Pressure

Compute pressure from contradictory narratives with high-confidence beliefs and energy concentration.

### Step 6: Decay Energy

Apply universal energy decay to prevent saturation and maintain recency contrast.

### Step 7: Surface Candidates

Surface candidates by salience (W * E * focus), biased by the active Place.

### Step 8: Flip and Canonize

When adaptive gates trigger, flip candidates into stable narratives/moments (THEN chain, narrative updates) and present them in relevant Places.

---

## KEY DECISIONS

### D1: Repo vs Graph Separation

```
IF data is an artifact (code, asset, SYNC file):
    store in repo and reference via EvidenceRef
ELSE:
    store as meaning/structure in the graph
```

### D2: No Arbitrary Thresholds

```
IF a threshold is needed:
    use adaptive gate (quantile/EMA)
ELSE:
    do not introduce fixed constants
```

---

## DATA FLOW

```
repo stimuli / system events
    ↓
L1 stimuli capture
    ↓
L2 derivation
    ↓
energy injection → graph nodes/links
    ↓
route + pressure + decay
    ↓
salience surfacing
    ↓
flip + canonize → Places
```

---

## COMPLEXITY

**Time:** O(V + E) per tick in the conceptual model (graph size dependent).

**Space:** O(V + E) for graph state, plus O(S) for recent stimuli.

**Bottlenecks:**
- High-degree nodes during routing
- Pressure computation across dense contradiction clusters

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| `mind` | stimulus ingestion | L1/L2 stimuli |
| graph service | graph ops | node/link updates |
| `blood-ledger` | runtime events | stimuli + EvidenceRefs |

---

## MARKERS

<!-- @mind:todo Formalize weight evolution rules (W updates and pruning policy). -->
<!-- @mind:todo Define canonicalization policy for dev narratives vs local moments. -->
<!-- @mind:proposition Add reference implementation notes once graph ops API is finalized. -->
<!-- @mind:escalation How should Place focus weights be computed across UI contexts? -->
