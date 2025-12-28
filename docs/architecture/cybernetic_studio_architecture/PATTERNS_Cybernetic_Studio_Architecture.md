# ARCHITECTURE — Cybernetic Studio (Game + Dev Framework + Graph Layer)

```
STATUS: DESIGNING
CREATED: 2025-12-20
VERIFIED: N/A
```

---

## CHAIN

```
THIS:            PATTERNS_Cybernetic_Studio_Architecture.md (you are here)
BEHAVIORS:       ./BEHAVIORS_Cybernetic_Studio_System_Behaviors.md
ALGORITHM:       ./ALGORITHM_Cybernetic_Studio_Process_Flow.md
VALIDATION:      ./VALIDATION_Cybernetic_Studio_Architectural_Invariants.md
IMPLEMENTATION:  ./IMPLEMENTATION_Cybernetic_Studio_Code_Structure.md
HEALTH:          ./HEALTH_Cybernetic_Studio_Health_Checks.md
SYNC:            ./SYNC_Cybernetic_Studio_Architecture_State.md

IMPL:            N/A (Conceptual Architecture Document)
SOURCE:          ../../../data/ARCHITECTURE — Cybernetic Studio.md
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Understand the high-level architecture before diving into specifics

**After modifying this doc:**
1. Update any linked implementation or related docs to match, OR
2. Add a TODO in SYNC_Cybernetic_Studio_Architecture_State.md: "Docs updated, related components need: {what}"
3. Run `mind validate` to check link consistency.

**After modifying related code/implementations:**
1. Update this doc chain to match, OR
2. Add a TODO in SYNC_Cybernetic_Studio_Architecture_State.md: "Implementation changed, docs need: {what}"
3. Run `mind validate` to check link consistency.

---

## 0) One-Sentence Summary

Build **two repos**: a **Studio Platform** (mind) that provides graph physics, stimulus ingestion, places, and agent orchestration; and a **Game Cartridge** (Blood Ledger) that provides world content + player experience—both attached to the **same graph service**, where the graph holds meaning and state, while the repo holds artifacts.

---

## 1) Validated Axioms (Non-Negotiable)

### 1.1 Repo is the Source of Truth (Repo-as-World)
- The filesystem/git repo is canonical for artifacts (code, tests, assets, SYNC markdown).
- The graph is **not** a second filesystem and must not duplicate file contents.
- The graph stores:
  - meaning, memory, context, salience, pressure computations,
  - references to artifacts (path/sha/range/log fingerprint),
  - and structured surfaces (Places) that humans/agents use to work.

### 1.2 Graph is Physics, Not Links-as-Glue
- Relationships are expressed as **Narratives**, not bare edges like RELATED_TO.
- Edges that exist are functional primitives (BELIEF, THEN, PRESENT, ATTACHED_TO, etc.).
- "Pressure" is not a node type; it is a **computed field** arising from:
  - conflicting beliefs about narratives,
  - narrative links marked contradicts/supports,
  - and energy concentration.

### 1.3 Weight > “Recent Commits”
- Low energy does **not** mean irrelevant.
- Weight is long memory / structural importance; Energy is current activation.
- Energy decays; Weight changes slowly (or via explicit pruning/gates).

### 1.4 No “Overmind” as a Separate System
- No always-on daemon with privileged “global control” logic.
- Instead: watchers produce **stimuli**; stimuli inject energy; physics surfaces and flips.

### 1.5 No Arbitrary Constants
- Thresholds are implemented as **adaptive gates** (rolling quantiles / EMAs).
- Seeds exist only as warmup floors; percentiles take over as data accumulates.

### 1.6 Places Are Real
- SYNC files are **Places** (stable “rooms” / chat spaces).
- UI surfaces to talk to Manager or Narrator are Places.
- Views/protocols are Places (context spaces), not “docs.”

### 1.7 Agents (Dev) Do Not Need Personalities (By Default)
- Story characters need distinct beliefs/memories for drama.
- Dev agents start as **Modes/SubEntities** within a single citizen graph.
- Separation is justified by boundaries (permissions, blast radius, disagreement, isolation), not theatrics.

---

## 2) Repo Topology (How Many Repos, What Owns What)

### 2.1 Repos (Now)
**Repo A: `mind` — Studio Platform**
Owns the *how*:
- graph schema primitives + physics tick + salience/flip logic
- stimulus ingestion + derivation (L1 → L2) + routing/attribution
- Places (manager UI, narrator UI, SYNC rooms), agent orchestration
- protocols/templates and “docs-as-navigation” scaffolding

**Repo B: `blood-ledger` — Game Cartridge**
Owns the *what*:
- world seeds (characters, places, narratives, initial beliefs)
- player UI (Scene / Map / Ledger / Faces / Chronicle)
- cartridge orchestration (moment generation, mutation application, rendering transforms)
- game-specific prompts, tone, and experience tests

### 2.2 Graph Service Ownership
The graph service is owned and operated by the `mind` platform. `blood-ledger` is a client of the graph, but does not own the service.

### 2.3 Optional Future Extraction (Only When Pain Appears)
**Repo C: `graph-physics-core`**
- Extract only if mind becomes too entangled and you need a stable kernel:
  - ontology primitives, tick kernel, stimulus envelope contracts, gate utilities

---

## 3) Linking Between Repos (Three Kinds of Links)

### 3.1 Runtime Dependency
- `blood-ledger` imports `mind` as a library (editable install in dev; versioned package later).

### 3.2 Tooling Relationship
- `mind` runs against `blood-ledger` as a target repo.
- `blood-ledger` includes `...mind-mcp/state/SYNC_*.md` which are repo-backed Places.

### 3.3 Graph Relationship (Meaning Layer)
- Both repos connect to the same graph service.
- Use domain separation:
  - `domain=game` (playthrough world state)
  - `domain=dev` (studio cognition: work, incidents, protocols, evidence, decisions)
- Cross-domain links are via **evidence refs** (commit sha, path, log fingerprints), not file content duplication.

---

## 4) Unified Ontology (Minimal Node/Link Set)

### 4.1 Node Types
- **Character**
  - story characters
  - humans
  - dev/maintenance “actors” (Doctor as a Character, not a subsystem)
- **Place**
  - story places (York Market)
  - dev places (UI rooms, SYNC rooms, Views)
- **Thing**
  - referable artifacts and concepts (module, file_ref, function_ref, test, prompt, incident fingerprint, PR)
  - a Thing may reference repo artifacts but does not duplicate them
- **Narrative**
  - relationships, issues, invariants, observations, commitments, ownership, claims
  - “Issue is a Narrative”
- **Moment**
  - utterances/actions/log lines/query results/agent responses/tool outputs (all are moments)
  - moments are attachable and can be canonized via THEN chains

### 4.2 Core Link Types (Supported)
- **BELIEF**: (Character) → (Narrative) with fields (believes/doubts/denies/etc.)
- **NARRATIVE_LINK**: (Narrative) → (Narrative) with contradicts/supports/etc.
- **THEN**: (Moment) → (Moment) for canon/history chain
- **PRESENT**: (Character) → (Place)
- **ATTACHED_TO**: (Moment) → (Place|Character|Thing) with presence rules
- **CAN_SPEAK** / **CAN_LEAD_TO**: moment surfacing & flow controls (game)
- **ABOUT**: (Moment) → (Any) for semantic anchoring / query results

> IMPORTANT: No generic RELATED_TO. Relationships are represented as Narratives + Beliefs.

---

## 5) Evidence References (How the Graph Touches the Repo Without Duplicating It)

### 5.1 EvidenceRef (portable convention)
An evidence reference is a string or structured object (implementation choice) that points to repo artifacts:

- repo: `mind` | `blood-ledger`
- commit_sha: `abc123`
- path: `mind/doctor_checks.py`
- range: `L120-L220` (optional)
- fingerprint: `stack_fingerprint:...` (optional)
- run_id / test_id (optional)

EvidenceRefs can be attached to:
- Moments (tool output produced this)
- Narratives (claim is supported by evidence)
- Things (this Thing is a file_ref or function_ref)

### 5.2 Thing Kinds (Examples)
- kind=file_ref (path + sha)
- kind=function_ref (path + symbol + sha)
- kind=module_concept (conceptual boundary holder)
- kind=test_ref, prompt_ref, incident_ref

---

## 6) Stimulus → Energy Injection (Granular, Bottom-Up, No Overmind)

### 6.1 L1 Raw Stimuli (examples)
- commit
- file_change
- file_read (editor/plugin)
- file_write
- exec/test_run
- backend_error
- self_observation
- conversation

### 6.2 L2 Derived Stimuli (examples)
- intent.reconcile_beliefs
- intent.protect_fix
- intent.consolidate_learning
- incident.backend_error
- intent.stabilize_narrative

### 6.3 Injection Rule (Validated)
Energy is injected on:
- file read
- file write
- commit
- execution/test run

Energy injection is routed to:
- Things referenced by evidence (file_ref/function_ref/module_concept)
- Narratives ABOUT those Things
- The active Place (current UI room / SYNC room / scene)

This replaces “doctor loop” and “overmind” with substrate-native observability.

---

## 7) Physics Loop (What Runs Every Tick)

### 7.1 State Variables
- Weight W(node): long-term importance
- Energy E(node): current activation

### 7.2 Tick Steps (Conceptual)
1) Inject (from stimuli)
2) Route (along allowed channels)
3) Compute pressure (from contradictions + energy concentration)
4) Decay energy (universal sink)
5) Surface candidates by salience (W * E * focus)
6) Flip when gates trigger (adaptive thresholds)
7) Canonize results (THEN chain, narrative updates, new moments)

### 7.3 Pressure (Computed, Not Stored)
Pressure emerges when:
- high-confidence beliefs support an invariant narrative
- and high-confidence beliefs support an observation narrative
- and these narratives contradict via narrative_link
- and energy concentrates around the involved Things/Places/Characters

Pressure is an input to salience and flip likelihood; not a persistent object.

---

## 8) Places (Rooms, Views, and SYNC as Living Surfaces)

### 8.1 Repo-Backed Place (SYNC as Place)
Each SYNC file defines a stable Place:
- Place ID: `place://sync/Project_State`
- Artifact: `...mind-mcp/state/SYNC_Project_State.md`
- Updates create Moments (“SYNC updated”) and distill Narratives (“current state is…”)- SYNC rooms behave like chat rooms: they’re where state is negotiated and handed off.

### 8.2 UI Rooms (Human ↔ AI)
- `place://ui/manager`
- `place://ui/narrator`
- `place://ui/player_scene`
- `place://ui/triage`

Switching rooms changes what gets surfaced (context bias, candidate selection).

### 8.3 Views/Protocols as Places
A “VIEW” is a Place whose constraints shape:
- what context is loaded
- what patterns are considered canonical
- what outputs are allowed
This reconciles:
- bottom-up emergence (physics)
- with precise circulation management (protocols/formats)

---

## 9) Agents and Identity (Story Characters vs Dev Agents)

### 9.1 Story Characters (Need Distinctness)
- distinct belief graphs
- distributed history
- contradiction is drama
- separation is the mechanic

### 9.2 Dev Agents (Start Unified; Separate by Boundary Need)
Default: one citizen graph with Modes/SubEntities:
- Manager (prioritization, canonicalization)
- Builder (edits + implementation)
- Validator/Sentinel (tests, invariants, adversarial verification)
- Archivist/Integrator (distillation to narratives, SYNC updates)

### 9.3 Why NOT share everything by default
- Moments are high-volume noise; global sharing saturates attention.
- Rule: **Moments are local to a Place unless promoted.**
- Promotion is a flip/distillation into a Narrative (shareable, stable).

### 9.4 What can be shared safely
- Evidence narratives (test outputs, build logs, commits)
- Shared narratives with separate belief weights per mode (Shared Evidence, Separate Opinions)

### 9.5 When to create separate dev Characters (justifications)
Only when you need one of:
- privilege separation (commit rights vs read-only)
- hard isolation of short-term context (parallel threads that must not contaminate)
- institutionalized disagreement (red team that stays skeptical by identity)
- auditability of decisions by distinct owners

---

## 10) Homeostasis and Safety (Prevent Runaway Refactors)

### 10.1 Proof Gates (Non-Negotiable)
- If it’s not tested, it’s not built.
- Repair/changes must pass verification gates (unit/integration/manual smoke as applicable).

### 10.2 Adaptive Gates (No Magic Constants)
- Flip thresholds and trigger points use QuantileGate/EMA strategies.
- Warmup floors exist only until distributions stabilize.

### 10.3 Budgets & Economics (Orthogonal Layer)
- Any economic/budgeting system (e.g., $MIND) must be orthogonal:
  - it clamps injection magnitude
  - it does not change physics evolution once injected
- Phase it in only if scarcity emerges; do not entangle with core physics.

---

## 11) Concrete Deliverables (What Gets Built Where)

### 11.1 In `mind` (Platform)
- graph kernel + schema
- gate utilities
- stimulus watchers + derivation + injection
- Places UI (manager room + triage room) and SYNC room integration
- tool orchestration for builder/validator modes

### 11.2 In `blood-ledger` (Cartridge)
- world seed YAML (Things, Places, Characters, Narratives, Beliefs)
- player UI (Scene/Map/Ledger/Faces/Chronicle)
- moment cluster generation + mutation application
- cartridge-specific narratorial rendering

---

## 12) Acceptance Criteria (V1)

### 12.1 Repo / Graph Separation
- Graph contains only references + derived meaning; no duplication of file contents.
- Any artifact pointer is an EvidenceRef, not embedded content.

### 12.2 Places Work
- SYNC file updates appear as Moments in the SYNC Place.
- Manager UI and Narrator UI are Places with distinct surfacing behavior.

### 12.3 Stimulus Injection Works
- commit / read / write / exec produce stimuli
- stimuli inject energy into referenced Things and ABOUT-narratives
- physics tick surfaces relevant moments and promotes when gates trigger

### 12.4 Dev Agent Model Works Without Personalities
- modes/subentities can complete:
  - implement a change
  - verify it
  - distill outcomes into narratives + SYNC
without needing separate “DEV/DESIGNER personalities.”

### 12.5 No Arbitrary Constants
- at least one critical threshold (flip/surface/decay gate) uses adaptive gating with warmup floors.

---

## 13) Open Questions (Explicitly Remaining)
- Weight evolution rules (how W increases/decreases over time; pruning policy).
- Canonization policy for dev narratives (what becomes stable vs stays local).
- Minimal EvidenceRef schema (string vs structured object; where stored).
- How to represent module boundaries: Thing(kind=module_concept) vs Narrative holder.
- How to map “boring game” signals into dev-side pressure without destabilizing work.

---

## Appendix A — Minimal YAML Examples (V1)

### A1) Thing: file_ref (no duplication)
- type: thing
  id: thing_repo_mind_doctor_checks
  name: "mind/doctor_checks.py"
  kind: file_ref
  repo: "mind"
  path: "mind/doctor_checks.py"
  head_sha: "abc123"

### A2) Narrative: issue/invariant/observation
- type: narrative
  id: narr_invariant_docs_must_link
  name: "Code must link to docs (bidirectional)"
  content: "Implementation files should reference their docs and docs should reference implementation."
  narrative_type: invariant
  about:
    things: [thing_repo_mind_doctor_checks]

- type: narrative
  id: narr_observation_broken_docs_ref
  name: "Broken docs reference observed"
  content: "DOCS header points to missing file."
  narrative_type: observation
  truth: 0.9
  about:
    things: [thing_repo_mind_doctor_checks]

### A3) Belief (distributed opinions)
- type: belief
  character: char_doctor
  narrative: narr_observation_broken_docs_ref
  believes: 0.95
  source: inferred

- type: belief
  character: char_builder
  narrative: narr_invariant_docs_must_link
  believes: 0.85
  source: taught

### A4) Moment (local output; attach to place + thing)
- type: moment
  id: mom_uuid_1
  text: "Fix docs link for doctor_checks.py (evidence: missing target)."
  moment_type: thought
  status: possible
  weight: 0.6
  energy: 0.7
  place_id: place://ui/triage

- type: attached_to
  moment: mom_uuid_1
  target: thing_repo_mind_doctor_checks
  presence_required: false
  persistent: true
  dies_with_target: false

---

END.
