# mind-mcp — Sync: Current State

```
LAST_UPDATED: 2025-12-28
UPDATED_BY: claude (opus-4.5)
STATUS: DESIGNING
```

---

## CURRENT STATE

mind-mcp is the open-source client/engine for the Mind Protocol. Split from ngram repo. Core physics and graph code migrated, **import paths now fixed** (engine.* → mind.*). CLI working. MCP server exists but needs testing with Neo4j Aura.

Package installable via `pip install -e .` - the `mind` command works globally.

---

## ARCHITECTURAL DECISION: CONNECTOME

**Decision (2025-12-28):** Connectome core lives here in mind-mcp. Platform imports from here.

### Rationale

Connectome visualizes engine internals (traversal, energy, physics). The engine lives here, so the visualization should too. Platform uses the same components with a different data adapter.

### Structure (To Be Implemented)

```
mind-mcp/
└── connectome/
    ├── core/                    # SHARED - React components
    │   ├── components/
    │   │   ├── node-kit/        # Node rendering
    │   │   ├── edge-kit/        # Edge rendering
    │   │   ├── canvas/          # Flow canvas
    │   │   └── panels/          # Log, health panels
    │   ├── types/               # FlowEvent, NodeData, etc.
    │   └── styles/              # CSS/tokens
    │
    ├── adapters/
    │   ├── local.ts             # Connects to local Neo4j (dev tool)
    │   └── remote.ts            # Connects to L4 API (for platform)
    │
    ├── lib/                     # Runtime (state store, engine)
    │   ├── state-store.ts
    │   ├── runtime-engine.ts
    │   └── event-model.ts
    │
    └── server/                  # Local dev server
        └── index.ts             # `mind connectome` CLI command
```

### Adapter Interface

```typescript
interface ConnectomeAdapter {
  // Graph data
  getNodes(): Promise<Node[]>
  getLinks(): Promise<Link[]>
  search(query: string, opts: SearchOpts): Promise<SearchResult>

  // Realtime
  subscribe(handler: (event: FlowEvent) => void): Unsubscribe

  // Dev-only (optional)
  nextStep?(): Promise<StepResult>
  restart?(): void
}
```

### Migration Path

1. Create `connectome/` directory structure
2. Move components from `mind-platform/app/connectome/components/`
3. Create adapter interface
4. Implement LocalAdapter (talks to local Neo4j)
5. Add `mind connectome` CLI command
6. Platform updates imports to use `mind-mcp/connectome/core`

---

## ACTIVE WORK

### Connectome Migration (IN PROGRESS)

- **Area:** `connectome/`
- **Status:** structure created, adapters defined
- **Owner:** agent
- **Context:** Moving shared Connectome components from mind-platform to here

**Created:**
- `connectome/package.json` — npm package config
- `connectome/core/types/adapter.ts` — ConnectomeAdapter interface
- `connectome/adapters/local.ts` — LocalAdapter skeleton
- `connectome/adapters/remote.ts` — RemoteAdapter skeleton
- `connectome/lib/index.ts` — lib placeholder
- `connectome/README.md` — documentation

**Next:**
- Move React components from mind-platform
- Implement LocalAdapter Neo4j connection
- Add TypeScript build config

### Core Engine Migration

- **Area:** `mind/`
- **Status:** imports fixed, testing needed
- **Owner:** agent
- **Context:** All `engine.*` and `ngram.*` imports migrated to `mind.*`. Basic imports verified working. ConnectomeRunner module not yet migrated (MCP membrane tools disabled until migrated).

---

## RECENT CHANGES

### 2025-12-28: Connectome Architecture Decision

- **What:** Decided Connectome core lives in mind-mcp, platform imports from here
- **Why:** Connectome visualizes engine internals; engine lives here
- **Impact:** Need to migrate components from mind-platform, create adapter pattern
- **Cross-repo:** Coordinated with mind-platform SYNC

### 2025-12-28: Import Path Migration

- **What:** Fixed all `engine.*` and `ngram.*` imports to use `mind.*`
- **Why:** Repo split left stale import references
- **Where:** `cli/commands/init.py`, `cli/commands/explore.py`, `cli/commands/doctor.py`, `mcp/server.py`, plus docstring refs in `mind/physics/`
- **Impact:** Basic imports now work. ConnectomeRunner marked as TODO (missing module).

### 2024-12-28: Repo Creation

- **What:** Split from ngram monorepo into dedicated mind-mcp repo
- **Why:** Clean separation of client engine from protocol/platform
- **Impact:** Fresh start, needs dependency verification

### 2024-12-28: CLI + Package Setup

- **What:** Added entry point, fixed pyproject.toml for hatch
- **Why:** Enable global `mind` command
- **Impact:** Can now run `mind init` from any directory

---

## KNOWN ISSUES

| Issue | Severity | Area | Notes |
|-------|----------|------|-------|
| Neo4j connection untested | high | `mind/physics/graph/` | Need to verify Aura connection |
| ConnectomeRunner missing | medium | `mcp/` | Module not migrated, membrane dialogues disabled |
| MCP server untested | medium | `mcp/` | Needs integration test |
| Duplicate GraphOps/GraphQueries | low | `mind/` | Exists in both `mind/graph/ops/` and `mind/physics/graph/` |
| Connectome not yet migrated | medium | `connectome/` | Components still in mind-platform |

---

## TODO

### High Priority — Connectome Migration

- [ ] Create `connectome/` directory structure
- [ ] Define adapter interface (`ConnectomeAdapter`)
- [ ] Move components from mind-platform
- [ ] Implement LocalAdapter (local Neo4j)
- [ ] Add `mind connectome` CLI command
- [ ] Create RemoteAdapter (L4 API) for platform use

### High Priority — Engine

- [ ] Test Neo4j Aura connection
- [x] Verify all imports work (engine.* → mind.* migration complete)
- [ ] Migrate ConnectomeRunner module from engine package
- [ ] Test MCP server with Claude Code
- [ ] Add missing dependencies to pyproject.toml

### Backlog

- [ ] Add comprehensive tests
- [ ] Document all MCP tools
- [ ] Add WebSocket client for L4 push
- IDEA: Add offline queue for disconnected mode

---

## AREAS

| Area | Status | Description |
|------|--------|-------------|
| `mind/` | migrated | Core physics, graph, models |
| `cli/` | working | CLI entry point |
| `mcp/` | untested | MCP server for AI agents |
| `templates/` | ready | .mind/ initialization templates |
| `connectome/` | **in progress** | Graph visualization — structure + adapters done, components pending |

---

## MODULE COVERAGE

**Mapped modules:**

| Module | Code | Description | Status |
|--------|------|-------------|--------|
| physics | `mind/physics/` | Graph physics engine | migrated |
| graph | `mind/physics/graph/` | Neo4j operations | migrated |
| models | `mind/models/` | Node/Link models | migrated |
| infrastructure | `mind/infrastructure/` | DB, embeddings, API | migrated |
| cli | `cli/` | Command line interface | working |
| mcp | `mcp/` | MCP server | untested |
| connectome | `connectome/` | Graph visualization | **planned** |

---

## HANDOFF: FOR AGENTS

**Current focus:** Connectome migration + Neo4j testing

**Key files to create:**
- `connectome/core/types/adapter.ts` — Adapter interface
- `connectome/adapters/local.ts` — Local graph adapter
- `connectome/server/index.ts` — CLI dev server

**Source files (in mind-platform):**
- `app/connectome/components/` — 22 React component files
- `docs/connectome/` — Extensive documentation

**Watch out for:**
- ConnectomeRunner not yet migrated (membrane tools won't work)
- Duplicate code: GraphOps exists in both `mind/graph/ops/` and `mind/physics/graph/`
- Components have TypeScript imports that need updating

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Connectome architecture decided: core lives here, platform imports. Next step is migration.

**Decisions made:**
- Connectome core → mind-mcp
- Adapter pattern for local (dev) vs remote (platform) data sources
- Platform will import shared components

**Needs your input:**
- Neo4j Aura credentials for testing
- Confirm MCP server tool list is complete

**Concerns:**
- ConnectomeRunner needs to be migrated for MCP membrane tools to work

---

## CROSS-REPO COORDINATION

**Agents are allowed to work across all 4 repos.** This is intentional — the repos form a single system.

### Repo Map

| Repo | Layer | Path | Access |
|------|-------|------|--------|
| `mind-mcp` | L1 Client | `/home/mind-protocol/mind-mcp` | open source |
| `mind-protocol` | L4 Law | `/home/mind-protocol/mind-protocol` | open source |
| `mind-platform` | L3 + UI | `/home/mind-protocol/mind-platform` | open source |
| `mind-ops` | Ops | `/home/mind-protocol/mind-ops` | private |

### This Repo's Role

**mind-mcp is the ENGINE + CONNECTOME CORE:**
- Graph physics, traversal, methodology
- Local membrane client
- MCP server for Claude
- CLI tools (`mind` command)
- **Connectome visualization core** (shared with platform)

**Exports to other repos:**
- `connectome/core/` → mind-platform imports for web UI
- `connectome/adapters/remote.ts` → platform uses for L4 connection

### Coordination Hub: mind-ops

**`mind-ops` is the main cross-repo organization point.**

- Cross-repo issues go in `mind-ops/runbooks/cross-repo/`
- Deployment orchestration in `mind-ops/ci/`
- Shared secrets configuration in `mind-ops/secrets/`
- Integration tests that span repos in `mind-ops/tests/integration/`

### Sync Protocol

When working across repos:
1. Update SYNC in the repo you're leaving
2. Update SYNC in the repo you're entering
3. Note the cross-repo context in both
