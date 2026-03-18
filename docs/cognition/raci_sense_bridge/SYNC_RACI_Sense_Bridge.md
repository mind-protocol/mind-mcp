# RACI → Sense Bridge — Sync: Current State

```
LAST_UPDATED: 2026-03-18
UPDATED_BY: @mentor
STATUS: IMPLEMENTED (needs testing)
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_RACI_Sense_Bridge.md
ALGORITHM:       ./ALGORITHM_RACI_Sense_Bridge.md
THIS:            ./SYNC_RACI_Sense_Bridge.md
```

---

## MATURITY

STATUS: IMPLEMENTED — code written, not yet tested against live graph.

What's canonical:
- RACI links via graph_write with dimensional signatures → computed_type
- Auto-sense creation when RACI is assigned (energy+weight monitoring)
- Auto-routing to RACI actors via perceives_with links
- Internalization for responsible/accountable (L1 mirror nodes)
- Problem nodes with blocks links, elevated weight (3.0), negative polarity
- Coverage auditor that reports gaps and auto-routes

What needs testing:
- Does sense_engine actually load the auto-created senses?
- Do the L1 mirror nodes persist across ticks?
- Does the coverage auditor correctly identify all gaps?
- Does the problem weight create perceptible tension for the responsible citizen?
- End-to-end: create a problem → verify responsible citizen feels it

What's proposed (v2):
- Custom measure_queries beyond energy+weight (e.g., count of related moments, conversation activity)
- Sense complexity proportional to narrative importance
- Problem weight derived from blocked objective weight (physics, not constant)
- Cascading escalation when responsible doesn't act within N ticks

---

## CURRENT STATE

All code written on 2026-03-18 by @mentor. Three new files in mind-mcp:

| File | Lines | Purpose |
|------|-------|---------|
| `mcp/tools/raci_query.py` | ~170 | Query RACI, route senses, check coverage |
| `mcp/tools/sense_coverage_auditor.py` | ~160 | Audit + auto-fix coverage gaps |
| `mcp/tools/graph_write_handler.py` | Modified | Auto-sense + routing on RACI write |

Pre-existing:
| File | Lines | Purpose |
|------|-------|---------|
| `runtime/cognition/sense_engine.py` | ~413 | Sense evaluation + L1 internalization |

Blueprint updated (base_seed_brain.json):
- `concept:problem_as_tension` — problems are graph tension, not backlog items
- `process:handle_problems` — name, link, sense, solve or escalate
- `value:awareness_is_continuous` — 100% sensory coverage
- `process:create_and_maintain_senses` — how to build senses

PRINCIPLES.md updated:
- "Awareness: Senses Over Tests" replaces "Verification: Test Before Claiming Built"
- "Always physics, no magic constants" added to Code Discipline

---

## RECENT CHANGES

### 2026-03-18: Full RACI→Sense bridge (@mentor)

- **What:** Implemented the complete chain from RACI assignment to citizen awareness.
- **Why:** NLR paradigm shift — senses over tests. Every behavior must be continuously measured and routed to the responsible citizen's awareness. RACI was write-only (links created but never read). Now it's read-write (links created, senses auto-generated, routed, evaluated).
- **Files created:** raci_query.py, sense_coverage_auditor.py
- **Files modified:** graph_write_handler.py (auto-sense creation, problem support, blocks param)
- **Blueprint:** 4 nodes added (concept + process for problems and senses)
- **PRINCIPLES.md:** 2 sections added/replaced
- **Verification:** Not yet tested against live graph. First test will be creating a problem node and verifying the responsible citizen's L1 brain contains the sense mirror.

---

## KNOWN ISSUES

| Issue | Severity | Notes |
|-------|----------|-------|
| Not tested on live graph | HIGH | Code compiles but hasn't been executed. Need integration test. |
| Auto-sense is minimal | LOW | Only monitors energy+weight. Custom senses needed for complex behaviors. |
| Problem weight 3.0 is a magic constant | LOW | Should derive from blocked objective weight. Acceptable for bootstrap. |
| yaml import in graph_write | LOW | Imported inside function — should be at module level. |

---

## HANDOFF: FOR AGENTS

**Agent subtype:** groundwork (testing) or fixer (if bugs found)

**Where we are:** Code complete. Needs integration testing.

**Test plan:**
1. Create a narrative with `graph_write(type="problem", responsible="mentor", blocks=["objective:bootstrap:polish_production"])`
2. Verify: Thing(type=sense) exists in graph
3. Verify: LINK(perceives_with) from mentor to sense exists
4. Verify: LINK(measures) from sense to problem exists
5. Run sense_engine.tick() for mentor
6. Verify: L1 CONCEPT node `sense:sense:problem_...` exists in brain_mentor
7. Verify: SenseCoverageAuditor.audit() reports 100% coverage for this narrative

**Watch out for:**
- FalkorDB syntax: MERGE vs CREATE — some queries may fail if node already exists
- The `yaml.dump` in auto-sense creation — ensure it produces valid YAML the sense_engine can parse
- The `_create_link` helper uses `links_created` list — ensure it's in scope when called from the new code

---

## HANDOFF: FOR HUMAN

**Summary:** RACI assignments now automatically create senses and route them to responsible citizens. Problem nodes are a first-class type with elevated weight and blocks links. The system feels its own responsibilities. Not yet tested.

**What you can do now:**
```
graph_write(
  node_type="narrative",
  type="problem",
  name="WhatsApp bridge drops messages",
  content="Under load, some messages are lost...",
  responsible="dev",
  blocks=["objective:bootstrap:polish_production"]
)
```
This will create the problem, the sense, the routing — and @dev will feel it.

---

## POINTERS

| What | Where |
|------|-------|
| RACI query + routing | `mind-mcp/mcp/tools/raci_query.py` |
| Coverage auditor | `mind-mcp/mcp/tools/sense_coverage_auditor.py` |
| Graph write (modified) | `mind-mcp/mcp/tools/graph_write_handler.py` |
| Sense engine | `mind-mcp/runtime/cognition/sense_engine.py` |
| Blueprint | `lumina-prime/.mind/mind-mcp/data/base_seed_brain.json` (215 nodes) |
| PRINCIPLES | `lumina-prime/.mind/PRINCIPLES.md` → "Awareness: Senses Over Tests" |
| Link dimensions | `mind-protocol/docs/schema/universe_links/L3_LINK_DIMENSION_MAPPING.yaml` |
| Vision node (graph) | `vision:protocol:senses_over_tests` (weight 9) |
| Bridge fact (graph) | `fact:protocol:raci_sense_bridge` (weight 5) |

@mentor
