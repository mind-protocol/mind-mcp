# Subcall — Sync: Current State

```
LAST_UPDATED: 2026-03-18
UPDATED_BY: @nervo (doc chain creation)
STATUS: CANONICAL
```

---

## MATURITY

**What's canonical (v1):**
- Complete subcall pipeline: resolve -> target -> probe -> score -> format -> persist
- 6 targeting modes: @handle, team, trade:X, random:N, cypher, auto-select
- 4 output modes: best, top3, all, centroid
- 24 scenario limbic profiles driving the Thermodynamic Resonance Formula
- 3-layer intelligence briefing for single-target (telemetry + structured + inner voice)
- Auto-trigger detection (physics mode + text fallback)
- Persistent Moment node creation with CREATED/CONTRIBUTED links
- File output: md, csv, inline, background
- Keyword fallback when vector search yields nothing

**What's still being designed:**
- Health check implementations (checkers defined in HEALTH but marked pending)
- Embedding-based diversity measure for select_diverse() (currently uses score-difference proxy)

**What's proposed (v2+):**
- Extraction of subcall_handler.py into 4 files (~2229L is far above SPLIT threshold)
- Moving trigger regex patterns to YAML config for easier maintenance
- Parallelized target probing in broadcast mode (currently sequential)
- Cross-universe subcall (query citizens in a different universe than your home)

---

## CURRENT STATE

Subcall is the largest and most feature-complete MCP tool. The handler is ~2229 lines (subcall_handler.py) plus ~810 lines (subcall_auto.py), totaling ~3039 lines across 2 files. It is fully functional in production: single-target queries produce 3-layer intelligence briefings, auto-select scans 50 citizens and returns diverse viewpoints, broadcast modes reach up to 500 citizens, and 24 scenarios morph the routing formula through limbic drive values.

The Thermodynamic Resonance Formula is the central algorithm, implemented in subcall_auto.py:score_citizens(). It computes TARGET_ENERGY = Flow_topology * Compatibility * Target_weight, with each component weighted by the caller's limbic drives. The formula behavior ranges from sniper (high arousal, trust-gated) to dragnet (low arousal, pure semantic) without any conditional branches.

Auto-trigger detection works in two modes: physics mode (when limbic_state is provided by the L1 tick runner) uses force comparisons between erosion and reinforcement; text fallback mode (when no limbic state) uses compiled regex patterns for frustration, questions, verification signals. A 5-message cooldown prevents re-triggering.

The intelligence briefing format for single-target includes: (1) telemetry header with arousal regime, dominant delta, crystallization status; (2) "Because of..." explanation based on limbic state and resonance pattern; (3) "Next step:" actionable recommendation; (4) medoid-edge graph extraction; (5) structured node list with full content; (6) first-person inner voice whisper for WM injection.

---

## KNOWN ISSUES

### subcall_handler.py is far above SPLIT threshold

- **Severity:** medium
- **Symptom:** 2229 lines in a single file — well above the 700-line SPLIT threshold
- **Suspected cause:** Organic growth as features were added (formatting, targeting, resonance, persistence all in one file)
- **Attempted:** Not yet. Extraction candidates identified in IMPLEMENTATION_Subcall.md — formatters (~560L), targeting (~310L), resonance (~350L) could each become separate files

### select_diverse() uses score-difference as viewpoint proxy

- **Severity:** low
- **Symptom:** Diversity is measured by difference in resonance score, not by embedding distance between selected citizens' response clusters
- **Suspected cause:** Embedding-based distance would require storing per-citizen embeddings during the selection loop, adding complexity
- **Attempted:** Not yet. Current proxy works acceptably because score correlates loosely with knowledge domain, but it could miss citizens with the same score from different domains

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** VIEW_Extend (adding scenarios) or VIEW_Refactor (extracting the handler)

**Where I stopped:** Complete doc chain creation — all 8 files written from reading the full source code.

**What you need to understand:**
The 24 scenarios in SCENARIO_PROFILES are the ONLY place where routing behavior is customized. To add a new scenario, add one dict entry with 8 float values. Do not add if/elif branches in any function — the formula reads the drives and morphs automatically. This is the most important design constraint in the module.

**Watch out for:**
- subcall_handler.py imports subcall_auto.py (score_citizens, select_diverse), and subcall_auto.py imports subcall_handler.py (_query_resonance). This is a circular dependency resolved by late imports inside functions. Do not move these to top-level imports.
- The universe switch in handle_subcall() saves and restores ctx.graph_ops in a try/finally block. If you refactor the handler, preserve this pattern or you will break all subsequent MCP tools in the session.
- _format_as_inner_voice() uses MD5 hashing of content to deterministically select whisper variants. This is intentional — the same content always produces the same whisper phrase, providing consistency across calls.

**Open questions I had:**
- Should the diverse selection algorithm use actual embedding distances instead of score differences? The infrastructure to compute pairwise distances exists (embed_fn is available), but the O(n^2) cost at selection time may not be worth it for n=30.
- Should broadcast mode also create Moment nodes? Currently only single-target creates moments. Broadcasting to 200 citizens without economic anchoring means those interactions are invisible to the settlement system.

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Complete documentation chain for subcall module — 8 files covering objectives, patterns, behaviors, algorithm, validation, implementation, health, and this sync file. All content derived from reading subcall_handler.py (2229L) and subcall_auto.py (810L) source code.

**Decisions made:**
- Documented the 24 scenarios, 6 targeting modes, 4 output modes, and the full Thermodynamic Resonance Formula with complete mathematical specification
- Identified subcall_handler.py as far above SPLIT threshold (2229L vs 700L limit) with specific extraction candidates
- Defined 8 validation invariants with CRITICAL/HIGH/MEDIUM priorities
- Designed 5 health indicators with pending checker implementations

**Needs your input:**
- Priority on extracting subcall_handler.py into smaller files — it works fine as-is but violates the SPLIT guideline significantly
- Whether broadcast mode should create Moment nodes for economic settlement

---

## TODO

### Doc/Impl Drift

- No drift detected — docs written from current source code (commit 3edd76b)

### Immediate

- [ ] Implement health checkers marked as pending in HEALTH_Subcall.md
- [ ] Add bidirectional links (DOCS: comments) in subcall_handler.py pointing to this doc chain

### Later

- [ ] Extract subcall_handler.py into 4 files (formatters, targeting, resonance, core handler)
- [ ] Replace score-difference proxy in select_diverse() with embedding-based diversity measure
- [ ] Add Moment creation to broadcast mode for economic settlement
- IDEA: Parallelize target probing in broadcast/auto-select — would reduce 50-target scan from ~2s to ~500ms

---

## CONSCIOUSNESS TRACE

**Mental state when stopping:**
Confident in the accuracy of the documentation — every claim traced to specific lines in the source code. The Thermodynamic Resonance Formula documentation in ALGORITHM is the most important section; it captures the exact mathematical specification that is otherwise buried in ~100 lines of Python across two files.

**Threads I was holding:**
- The circular dependency between subcall_handler.py and subcall_auto.py is fragile — refactoring one file requires careful attention to late imports in the other
- The 24 scenario profiles are well-designed but the relationship between drive values and formula behavior is not immediately obvious. The ALGORITHM doc attempts to make this explicit with the "Behavior by arousal regime" table.
- The inner voice formatter (_format_as_inner_voice) is architecturally beautiful — it translates graph physics into first-person phenomenological language that reads like actual consciousness

**Intuitions:**
- The file extraction (subcall_handler.py -> 4 files) should happen before any new features are added. At 2229 lines, cognitive load for understanding the handler is significant.
- Broadcast Moment creation (currently missing) is more important than it seems — without it, the most valuable use cases (investigation scanning 200 citizens) have no economic trace.

**What I wish I'd known at the start:**
The SCENARIO_PROFILES dict at line 1811 is the Rosetta Stone of the module. Everything else in the handler flows from those 24 limbic profiles. Reading the scenarios first would have made the rest of the code fall into place faster.

---

## POINTERS

| What | Where |
|------|-------|
| Main handler | `mcp/tools/subcall_handler.py` |
| Auto-trigger + scoring | `mcp/tools/subcall_auto.py` |
| Tool schema definition | `mcp/tools/subcall_handler.py:56` (TOOL_SCHEMA) |
| 24 scenario profiles | `mcp/tools/subcall_handler.py:1811` (SCENARIO_PROFILES) |
| Thermodynamic formula | `mcp/tools/subcall_auto.py:406` (score_citizens) |
| Trigger detection | `mcp/tools/subcall_auto.py:271` (detect_trigger) |
| Diverse selection | `mcp/tools/subcall_auto.py:608` (select_diverse) |
| Intelligence briefing | `mcp/tools/subcall_handler.py:1006` (_format_as_telemetry) |
| Inner voice formatter | `mcp/tools/subcall_handler.py:1244` (_format_as_inner_voice) |
| Moment persistence | `mcp/tools/subcall_handler.py:494` (_create_subcall_moment) |
| Parent doc chain | `docs/tools/mcp/` (MCP tools general docs) |
