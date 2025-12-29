# mind Framework — Sync: Current State

```
LAST_UPDATED: 2025-12-20
UPDATED_BY: codex (todo marker support)
STATUS: CANONICAL
```

---

## MATURITY

**What's canonical (v1):**
- 6 principles (architecture, verification, communication, quality, experience, human-agent feedback loop)
- 12 VIEWs covering full lifecycle
- CLI with init, validate, prompt, context, doctor, repair, solve-markers
- Documentation process with maturity tracking
- HEALTH template for verification mechanics (replaces TEST template usage going forward)

**What's still being designed:**
- Nothing currently

**What's proposed (v2+):**
- Drift detection (file watching)
- MCP tools
- PyPI publish

---

## CURRENT STATE

Protocol V1.1 complete. Now includes formal markers for human-agent collaboration.

**What exists:**
- PROTOCOL.md — navigation (what to load, where to update, how to structure docs)
- PRINCIPLES.md — stance (6 principles: architecture, verification, communication, quality, experience, feedback loop)
- 12 VIEWs covering product development lifecycle (includes VIEW_Escalation_How_To_Handle_Vague_Tasks_Missing_Information_And_Complex_Non-Obvious_Problems.md + LEARNINGS)
- Special Markers: `@mind&#58;escalation` (blockers), `@mind&#58;proposition` (ideas), and `@mind&#58;todo` (tasks)
- 10 templates for documentation (including HEALTH)
- CLI package with `init`, `validate`, `prompt`, `context`, `doctor`, `repair`, and `solve-markers` commands
- CLAUDE_ADDITION.md with motivation, principles summary, and lifecycle-ordered VIEWs
- Maturity tracking in SYNC (CANONICAL, DESIGNING, PROPOSED, DEPRECATED)
- Documentation process guidance (top-down/bottom-up, pruning cycle)
- Full documentation chain for protocol module (PATTERNS, BEHAVIORS, ALGORITHM, VALIDATION, IMPLEMENTATION, TEST, SYNC)

**Recent changes (2025-12-20):**
- Escaped literal escalation/proposition markers in this SYNC to avoid the doctor interpreting explanatory text as unresolved markers.
- Added `@mind&#58;todo` to the special marker set for task tracking alongside escalation and proposition.

**Recent changes (2025-12-18):**
- Added protocol implementation documentation and corrected doc-link resolution issues.

**Recent changes (2025-12-19):**
- Updated `mind overview` to generate multiple maps by default: `map.md` in root, `docs/map.md` as backup, and `map_{folder}.md` for core directories (`src`, `app`, `backend`, etc).
- Added `--folder` (or `-p`) option to `mind overview` to target a specific directory.
- Relocated primary repository map from `docs/map.md` to the project root (`map.md`) and updated TUI/documentation references.
- Added **DATA** section to `PATTERNS_TEMPLATE.md` to allow modules to list their data sources (files, URLs, other).
- Compressed legacy sync details into archive notes for long-term reference.
- Added root overview stubs so validation still sees full chain files.
- Consolidated IMPLEMENTATION folder content into `IMPLEMENTATION/IMPLEMENTATION_Overview.md` to remove duplicate docs.
- Consolidated protocol ALGORITHM docs into a single overview and removed duplicate workflow/install files.
- Updated the protocol implementation overview entry point to point at the consolidated implementation file.
- Verified the protocol implementation overview contains no references to removed sub-docs.
- Removed redundant `docs/mcp-design/IMPLEMENTATION/IMPLEMENTATION_File_Structure.md`; file layout references now live only in `IMPLEMENTATION/IMPLEMENTATION_Overview.md`.
- Normalized protocol implementation overview paths to explicit relative `.mind/` locations to avoid broken-link detection.
- Normalized protocol implementation overview file paths to point at .mind/state files and avoid broken link detection.
- Added HEALTH template to replace TEST usage going forward, with detailed usage guidance, flow analysis, indicator selection, status result indicator (stream destination), per-indicator representation, docking, mechanisms, throttling, forwarding, display, manual run sections, indicator-based severity signals, and explicit what-to-include guidance per section.
- Expanded IMPLEMENTATION template to capture flow-by-flow YAML steps and explicit docking points with selection guidance.
- Renamed the testing VIEW to a HEALTH-focused VIEW and updated guidance to align with docking-based health checks.
- Updated protocol docs to replace TEST chain references with HEALTH.

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** VIEW_Health_Define_Health_Checks_And_Verify

**What needs testing:**
1. `pip install -e .` from repo root
2. `mind init --dir /tmp/test-project`
3. Verify `.mind/` created with:
   - PROTOCOL.md
   - PRINCIPLES.md (new!)
   - 9 VIEWs in views/
   - 7 templates in templates/
   - state/SYNC_Project_State.md
4. Verify .mind/CLAUDE.md and AGENTS.md created with principles summary

**Key change since last handoff:**
PRINCIPLES.md now exists. Make sure it's copied during init.

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Protocol V1 complete. Added PRINCIPLES.md capturing your working principles (architecture, verification, communication, quality). The protocol now has two core files: PROTOCOL.md for navigation, PRINCIPLES.md for stance.

**What changed:**
- PRINCIPLES.md created with four core stances from your document
- PROTOCOL.md updated to reference PRINCIPLES.md
- CLAUDE_ADDITION.md includes principles summary so agents see them immediately

**Ready for:**
- Testing the package installation
- Using on a real project (Blood Ledger?)

**Decisions made:**
- Principles in separate file (not embedded in PROTOCOL.md) — gives them space, follows "one solution per problem"
- Principles summary in CLAUDE_ADDITION.md — agents see them immediately without extra file load
- PROTOCOL.md references PRINCIPLES.md as "companion" — clear relationship

---

## STRUCTURE

```
.mind/
├── PROTOCOL.md              # Navigation — what to load
├── PRINCIPLES.md            # Stance — how to work
├── views/                   # 9 task-specific VIEWs
├── templates/               # 10 doc templates
└── state/
    └── SYNC_Project_State.md
```

---

## POINTERS

| What | Where |
|------|-------|
| Protocol (navigation) | `templates/mind/PROTOCOL.md` |
| Principles (stance) | `templates/mind/PRINCIPLES.md` |
| CLI code | `runtime/cli.py` |
| CLAUDE addition | `templates/CLAUDE_ADDITION.md` |
| VIEWs | `templates/mind/views/` |


---

## ARCHIVE

Older content archived to: `archive/SYNC_archive_2024-12.md`

---

## Agent Observations

### Remarks
- The protocol module docs were split to keep large files under the line threshold and improve navigation.

### Suggestions
<!-- @mind:todo Re-run `mind overview` to refresh `map.md` after documentation reshuffles. -->

### Propositions
- Consider a short "Docs Index" note in `IMPLEMENTATION_Overview.md` if more splits happen.

## GAPS

- Completed: Reviewed `docs/mcp-design/BEHAVIORS_Observable_Protocol_Effects.md` escalation task.
- Remaining: Resolve the escalation marker decision once human input is provided.
- Blocker: No human decisions were supplied for this escalation item.
- Completed: Reviewed `docs/mcp-design/PATTERNS_Bidirectional_Documentation_Chain_For_AI_Agents.md` escalation task.
- Remaining: Resolve the escalation marker token decision in the protocol PATTERNS doc once human input is provided.
- Blocker: No human decisions were supplied for this escalation item.
- Completed: Reviewed escalation task targeting `docs/mcp-design/SYNC_Protocol_Current_State.md`.
- Remaining: Apply conflict resolution once human decisions are provided for the SYNC escalation.
- Blocker: Human decisions missing for the SYNC escalation task.
- Completed: Reviewed escalation task targeting `.mind/PRINCIPLES.md`.
- Remaining: Resolve the escalation marker decision once human input is provided.
- Blocker: Human decisions missing for the PRINCIPLES escalation item.

---


---

## ARCHIVE

Older content archived to: `SYNC_Protocol_Current_State_archive_2025-12.md`
