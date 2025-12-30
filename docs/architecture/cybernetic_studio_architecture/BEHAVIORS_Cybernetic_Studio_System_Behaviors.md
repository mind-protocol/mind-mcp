# ARCHITECTURE — Cybernetic Studio — Behaviors: System Observable Effects

```
STATUS: DESIGNING
CREATED: 2025-12-20
VERIFIED: N/A
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Cybernetic_Studio_Architecture.md
THIS:            BEHAVIORS_Cybernetic_Studio_System_Behaviors.md (you are here)
ALGORITHM:       ./ALGORITHM_Cybernetic_Studio_Process_Flow.md
VALIDATION:      ./VALIDATION_Cybernetic_Studio_Architectural_Invariants.md
IMPLEMENTATION:  ./IMPLEMENTATION_Cybernetic_Studio_Code_Structure.md
HEALTH:          ./HEALTH_Cybernetic_Studio_Health_Checks.md
SYNC:            ./SYNC_Cybernetic_Studio_Architecture_State.md

IMPL:            N/A (Conceptual Architecture Document)
SOURCE:          ../../../data/ARCHITECTURE — Cybernetic Studio.md
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS

The Cybernetic Studio architecture defines high-level observable behaviors across its component repositories (mind, blood-ledger) and the shared graph service (owned by `mind`). These behaviors focus on the interactions and outcomes at the system level, rather than internal component logic.

### B1: Artifacts are Canonical in Repos, Meaning in Graph

```
GIVEN:  A file (code, asset, SYNC markdown) exists in either the 'mind' or 'blood-ledger' repository.
WHEN:   The system operates (e.g., agents process files, game runs).
THEN:   The content of this file is considered the single source of truth for the artifact.
AND:    The graph service stores references (EvidenceRefs) to these artifacts, along with derived meaning, memory, and context, but never duplicates the file content itself.
```

### B2: Graph Physics Responds to Stimuli and Surfaces Salient Information

```
GIVEN:  An L1 raw stimulus (e.g., commit, file_change, exec/test_run) is produced in a connected repository.
WHEN:   The Studio Platform (mind) ingests this stimulus and derives L2 stimuli.
THEN:   Energy is injected into relevant Things, Narratives, and Places within the graph service.
AND:    The graph's physics tick computes pressure, decays energy, and surfaces candidates by salience (W * E * focus).
AND:    When adaptive gates trigger, relevant information or moments are "flipped" and canonized (e.g., via THEN chains, narrative updates).
```

### B3: Places Facilitate Contextual Interaction and State Management

```
GIVEN:  A user or agent interacts with a SYNC file, a UI room (e.g., manager, narrator), or a VIEW/protocol.
WHEN:   Information is exchanged or state is modified within that interaction context.
THEN:   This interaction occurs within a defined "Place" (e.g., place://sync/Project_State, place://ui/manager, VIEW_Implement).
AND:    The Place's constraints shape what context is loaded, what patterns are considered canonical, and what outputs are allowed.
AND:    Updates to repo-backed Places (like SYNC files) create Moments and distill Narratives in the graph, reflecting the current state.
```

### B4: Dev Agents Operate as Modes, Not Independent Personalities

```
GIVEN:  A development agent is tasked with implementing, verifying, or integrating changes within the Studio Platform.
WHEN:   The agent performs its assigned task.
THEN:   It operates as a "Mode" or "SubEntity" within a single citizen graph, sharing foundational context.
AND:    Separation into distinct characters (e.g., Manager, Builder, Validator) only occurs when justified by explicit boundaries like privilege separation, hard isolation of context, institutionalized disagreement, or auditability.
```

---

## INPUTS / OUTPUTS

At the architectural level, inputs are stimuli from various sources, and outputs are changes in graph state, surfaced information, and agent actions.

### Primary Interactions:

**Inputs:**
- **L1 Raw Stimuli:** Commits, file changes (read/write), command executions, test runs, backend errors, self-observations, conversations. (From repos, IDE plugins, external systems).
- **User/Agent Actions:** Commands issued in CLI, modifications to SYNC files, direct graph queries.

**Outputs:**
- **Graph State Changes:** New nodes (Characters, Places, Things, Narratives, Moments), new edges (BELIEF, THEN, PRESENT, ATTACHED_TO, NARRATIVE_LINK), changes to Weight/Energy.
- **Surfaced Information:** Candidates presented to agents/humans based on salience (W * E * focus).
- **Canonized Narratives/Moments:** Stable, shareable representations of knowledge or events.
- **Agent Actions:** Code modifications, test executions, documentation updates.
- **UI Updates:** Changes reflected in Manager UI, Narrator UI, or Player UI.

**Side Effects:**
- **Energy Injection:** Stimuli consistently inject energy into the graph.
- **Energy Decay:** Energy levels within the graph nodes naturally decay over time.
- **Pressure Computation:** Contradictions and energy concentration lead to computed "pressure."
- **Adaptive Gate Triggers:** System thresholds dynamically adapt, triggering "flips" when conditions are met.

---

## EDGE CASES

### E1: Graph Service Unavailability

```
GIVEN:  The `mind` Studio Platform or `blood-ledger` Game Cartridge attempts to interact with an unavailable graph service.
THEN:   Repo-backed operations (file reads/writes, git commands) should proceed where possible.
AND:    Graph-dependent operations (stimulus injection, salience computations) should gracefully handle the unavailability, potentially queueing stimuli for later processing or operating in a degraded mode.
```

### E2: Conflicting Beliefs / High Pressure

```
GIVEN:  Multiple high-confidence beliefs about narratives contradict each other, leading to high computed pressure.
THEN:   The system should surface these contradictions with high salience to relevant Places (e.g., Triage UI, Manager UI) for agent/human resolution.
AND:    Adaptive gates may trigger "flips" to promote reconciliation or new narratives based on the intensity of the pressure.
```

---

## ANTI-BEHAVIORS

What should NOT happen in the Cybernetic Studio architecture:

### A1: Graph Duplicates Repo Content

```
GIVEN:   A file artifact (e.g., code, asset) exists in a repository.
WHEN:    The graph service processes information related to this artifact.
MUST NOT: The graph service store the *content* of the file directly as a node property or embedded data.
INSTEAD:  The graph MUST only store EvidenceRefs pointing to the artifact's location (repo, path, sha, range).
```

### A2: Arbitrary Constants Govern System Dynamics

```
GIVEN:   A critical system threshold or decay rate needs to be defined (e.g., for salience, energy decay, flip triggers).
WHEN:    An agent or human defines this threshold.
MUST NOT: It be set as a fixed, arbitrary constant without justification or adaptation.
INSTEAD:  Thresholds MUST be implemented as adaptive gates (rolling quantiles / EMAs), with seeds only as warmup floors, allowing percentiles to take over as data accumulates.
```

---

## MARKERS

<!-- @mind:todo Clarify the exact contract and API for L1/L2 stimulus ingestion between `mind` and `blood-ledger` (or other potential integrations). -->
<!-- @mind:proposition Explore mechanisms for "pre-computation" or caching of salience scores for frequently accessed Places to improve UI responsiveness. -->
<!-- @mind:escalation How are "focus" weights in the salience computation (W * E * focus) dynamically determined or set by the active Place/VIEW? -->
