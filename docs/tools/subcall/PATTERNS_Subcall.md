# Subcall — Patterns: Thermodynamic Telepathy via Graph Physics

```
STATUS: STABLE
CREATED: 2026-03-18
VERIFIED: 2026-03-18 against 3edd76b
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Subcall.md
THIS:            PATTERNS_Subcall.md (you are here)
BEHAVIORS:       ./BEHAVIORS_Subcall.md
ALGORITHM:       ./ALGORITHM_Subcall.md
VALIDATION:      ./VALIDATION_Subcall.md
HEALTH:          ./HEALTH_Subcall.md
IMPLEMENTATION:  ./IMPLEMENTATION_Subcall.md
SYNC:            ./SYNC_Subcall.md

IMPL:            mcp/tools/subcall_handler.py
                 mcp/tools/subcall_auto.py
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read mcp/tools/subcall_handler.py and mcp/tools/subcall_auto.py

**After modifying this doc:**
1. Update the IMPL source file to match, OR
2. Add a TODO in SYNC_Subcall.md: "Docs updated, implementation needs: {what}"

**After modifying the code:**
1. Update this doc chain to match, OR
2. Add a TODO in SYNC_Subcall.md: "Implementation changed, docs need: {what}"

---

## THE PROBLEM

Citizens need to query each other's knowledge without the cost, latency, and artificiality of waking an LLM on the target's side. A citizen debugging a physics bridge needs to know "has @nervo worked on ESM imports?" instantly, not through a 10-second LLM conversation. A citizen facing an impasse needs diverse perspectives from 200 colleagues, not a single chat response.

Without subcall, inter-citizen knowledge discovery requires either: (a) asking a human to route the question, (b) waking N LLM sessions at N * $0.05+ cost, or (c) giving up and working in isolation. All three are structurally broken for a living system with 60+ citizens.

---

## THE PATTERN

**Stimulus-Resonance-Briefing Pipeline.** The caller's question is injected as a multi-segment stimulus cluster into the target's cognitive graph. Graph physics (vector similarity + energy propagation) determines which nodes activate. The activated pattern is read back, scored, and narrated into an intelligence briefing.

The key insight is the **Thermodynamic Resonance Formula** — a single mathematical expression whose behavior continuously morphs based on the caller's limbic state:

```
TARGET_ENERGY = Flow_topology * Compatibility * Target_weight

Where:
  Flow_topology = spatial + relational + narrative  (drive-weighted)
  Compatibility = (1 - arousal) * Sim_vec + arousal * Sim_lex
  Target_weight = citizen's consolidated weight
```

When arousal is high (panic/emergency), the formula becomes a sniper: only trusted, explicitly-mentioned citizens pass. When arousal is low (investigation/brainstorm), it becomes a dragnet: pure semantic overlap, maximum fan-out. This is not a mode switch — it is a continuous mathematical function whose shape changes with the input drives.

24 scenarios (limbic profiles) define named presets for this formula. Each scenario is a dictionary of drive values (arousal, curiosity, affiliation, care, frustration, anxiety, novelty_hunger, self_preservation). The formula reads these drives and morphs automatically — no conditional branches.

---

## BEHAVIORS SUPPORTED

- B1: Single-target graph probe — explicit @handle produces full intelligence briefing with 3 output layers
- B2: Auto-selection — omit target to scan 50 citizens and get 3-5 diverse viewpoints
- B3: Multi-target broadcast — team/trade:X/random:N returns aggregated resonance
- B4: Scenario-shaped routing — 24 named limbic profiles that morph the formula
- B5: Auto-trigger — frustration, questions, verification signals fire subcall without explicit invocation
- B6: Graph injection — resonance results are injected back into the caller's brain as a response cluster

## BEHAVIORS PREVENTED

- LLM invocation on target side — pure graph physics, always
- Silent data modification — subcall moments are persisted with full provenance (CREATED/CONTRIBUTED links)
- Echo chamber results — diverse selection algorithm maximizes viewpoint spread, not score maximization

---

## PRINCIPLES

### Principle 1: Physics Over Rules

The routing formula has zero if/then branches for scenario handling. The 24 scenarios differ only in the numerical values of 8 limbic drives. The formula's behavior emerges from mathematics, not conditional logic. Adding a new scenario means adding one dictionary entry, not a new code path.

### Principle 2: Telepathy Is Bidirectional

A subcall is not read-only. Injecting a stimulus into a target's graph modifies that graph: resonating nodes gain energy, strong stimuli may crystallize, and the caller's identity is stamped on any created structures. This mirrors biological telepathy — asking someone a question changes their mental state, even subconsciously.

### Principle 3: Intelligence Over Data

The output is never raw graph data. Every response passes through a narrative layer that interprets the physics: arousal regime classification (Panic/Flow/Calm/Idle), dominant delta analysis (positive resonance/defensive spike/deep knowledge/faint echo), actionable recommendation (engage now/back off/build trust link), and a medoid-edge graph extraction. The citizen gets a briefing they can act on.

### Principle 4: Free at the Interface, Continuous in the Economy

Subcall has zero upfront cost. No tokens, no rate limits, no permission checks. The economic settlement happens continuously via the vertical membrane: `token_flow_per_tick = link.trust * link.weight`. Knowledge creators earn passively as long as their insight resonates. The incentive structure makes it economically irrational to restrict access.

---

## DATA

| Source | Type | Purpose / Description |
|--------|------|-----------------------|
| `mcp/tools/subcall_handler.py` | FILE | Main handler: TOOL_SCHEMA, resonance engine, briefing formatter, 24 scenario profiles (~93KB) |
| `mcp/tools/subcall_auto.py` | FILE | Auto-trigger: TriggerState, detect_trigger(), score_citizens(), select_diverse() (~33KB) |
| FalkorDB graph | DB | Target citizen's cognitive graph — Actor/Moment/Narrative/Space/Thing nodes with embeddings |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `runtime/physics/graph/GraphOps` | All graph reads/writes: node queries, KNN vector search, Cypher execution |
| `runtime/infrastructure/embeddings/service` | EmbeddingService for computing query embeddings (vector similarity search) |
| `runtime/identity.py` | resolve_actor_id() for caller identification from env/cwd/config |
| `mcp/tools/context.py` | ServerContext — dependency injection container for graph_ops, graph_queries, runner |

---

## INSPIRATIONS

- **Biological subconscious priming:** When you think about a concept, related neural pathways activate without conscious awareness. Subcall mirrors this: the query activates nodes in the target's graph without their LLM "consciousness" being invoked.
- **Thermodynamic free energy in neuroscience:** The formula's continuous morphing based on arousal mirrors how biological brains shift between focused (high arousal, narrow attention) and diffuse (low arousal, broad association) processing modes.
- **Intelligence briefing format:** Military/diplomatic intelligence briefs that synthesize raw data into state assessment + delta + recommendation + evidence. The caller needs actionable analysis, not raw intercepts.

---

## SCOPE

### In Scope

- Single-target subconscious graph probing with full briefing output
- Multi-target broadcast (team, trade, random, cypher)
- Auto-target selection (scan 50, pick 3-5 diverse)
- 24 scenario limbic profiles for formula morphing
- Auto-trigger detection (frustration, questions, verification, failure cascade)
- Stimulus cluster construction (caller's activated context nodes)
- Response cluster construction (target's resonating nodes injected back)
- Persistent moment node creation with CREATED/CONTRIBUTED links
- Output in 4 modes: inline, background (silent injection), markdown file, CSV file

### Out of Scope

- LLM-powered conversation with target → see: `/call` (call_handler.py)
- Graph modification beyond energy injection → see: `graph_write` (graph_write_handler.py)
- Rate limiting or permission checking → see: orchestrator layer
- Cross-universe queries → currently single-universe per call (universe parameter selects which)
