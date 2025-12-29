# Archived: SYNC_Procedure.md

Archived on: 2025-12-29
Original file: SYNC_Procedure.md

---

## MATURITY

**STATUS: READY FOR IMPLEMENTATION (V2.0)**

| Layer | State | Notes |
|-------|-------|-------|
| Docs (this chain) | READY | All 9 files created (VOCABULARY added), V2.0 complete |
| YAML procedures | CANONICAL | Procedures in `.mind/procedures/` |
| MCP tools | STABLE | `procedure_start`, `procedure_continue` in mcp/server.py |
| Graph execution | NOT STARTED | Planned: `runtime/connectome/procedure_runner.py` |
| Physics integration | NOT STARTED | Energy flips via MERGE |

### What's Canonical (v2.0)

- **Steps are self-contained guides** — no runtime doc chain loading
- Step content includes What/Why/How/Watch out sections
- Validation spec embedded in step content
- Template immutability principle
- Deterministic API (`start`, `continue`, `end`)
- YAML procedure definitions
- MCP tool interface
- **IMPLEMENTS direction (bottom → top):** Health → Implementation → Validation → Algorithm → Behaviors → Vocabulary → Patterns → Objectives
- **Verbs:** `acts on` / `receives from`
- **Executors:** agent, code, actor, hybrid
- **File location:** `runtime/connectome/`
- **Link updates:** MERGE + SET (existing persistence API)
- **Validation types:** `node_exists`, `link_exists` only
- **Timestamps:** ISO-8601 string

### What's Proposed (v3)

- Conditional branching via graph links
- Procedure composition (nesting)
- Physics-based routing (SubEntity follows energy)
- Parallel step execution
- Additional validation types (`content_matches`, `count_range`, `custom`)

---


## RESOLVED DECISIONS

All blocking escalations have been resolved:

| ID | Question | Decision | Rationale |
|----|----------|----------|-----------|
| E1 | Runtime doc chain loading | **Removed** — steps are self-contained guides | Simple runtime, complex authoring |
| E2 | IMPLEMENTS direction | Bottom → top (Health implements Implementation...) | Lower layers implement higher layers |
| E3 | File location | `runtime/connectome/` | Follow existing convention |
| E4 | Persistence API | MERGE + SET exists | No new method needed |
| E5 | Validation types | `node_exists`, `link_exists` | YAGNI, expand when needed |
| E6 | Transition atomicity | MERGE is atomic + recovery | Recovery handles edge cases |
| E7 | Link update mechanism | Use existing MERGE | Preserves link identity |
| E8 | V4 strictness | WARNING for V1 | Don't block on missing guide sections |
| E9 | Verb semantics | Keep `acts on` / `receives from` | Defined in grammar |
| E10 | Mutation detection | Periodic audit | Low overhead |
| E11 | Timestamp format | ISO-8601 | Human readable, sortable |
| E12 | Executor types | agent/code/actor/hybrid | Four types cover all use cases |

---


## RECENT CHANGES

### 2025-12-29 (v2.0)

**Major V2 Simplification:**
- **Removed runtime doc chain loading** — steps are self-contained guides
- Added VOCABULARY_Procedure.md (9 files total)
- Step content now includes What/Why/How/Watch out sections
- Renamed IMPLEMENTED_IN → IMPLEMENTS with bottom→top direction
- Added executor types: agent, code, actor, hybrid
- Health checker `doc_chain_completeness` → `guide_completeness`

**Updated all files:**
- OBJECTIVES: O1 changed to "Steps Are Self-Contained"
- PATTERNS: Added "Steps Are Guides" pattern, removed walk_implemented_in
- BEHAVIORS: B1 changed to "Step Is Self-Contained Guide"
- VOCABULARY: New file with terms, executors, imports
- ALGORITHM: Removed doc chain loading, simplified API returns step_content
- VALIDATION: V4 changed to "Step Contains Complete Guide"
- IMPLEMENTATION: Removed doc_chain.py, updated flows
- HEALTH: Changed doc_chain_completeness to guide_completeness

### 2025-12-29 (v1.0)

**Created:**
- Full doc chain (8 files)
- 3-layer architecture (Context/Trace/Flow)
- Deterministic API spec
- 7 validation invariants
- 4 health checkers

---

