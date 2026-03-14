# Project — Sync: Current State

```
LAST_UPDATED: 2026-03-14
UPDATED_BY: steward — demurrage orphan reference cleanup in economy docs
```

---

## RECENT CHANGES (2026-03-14, night session — part 2)

### L4 Ping, Trust, Balance, Infos + Manemus Archived + Debug Traces

**L4 Registry API (mind-protocol, deployed on `l4-registry.onrender.com`):**
- `GET /ping/{handle}` — resolve citizen → org (via `belongs_to` link) → org endpoint → POST membrane/stimulus. Returns alive, universe (defaults to `lumina-prime`), last_active (latest L3 moment), resolution chain.
- `GET /trust/{handle}` — aggregated trust score (weighted mean of trust on inbound LINK edges).
- `GET /balance/{handle}` — $MIND + SOL balance via Helius RPC (resolve handle → wallet → on-chain query).
- `GET /infos/{handle}` — full citizen info card: ping + trust + balance + locations (parallel fetch). The `/infos` endpoint for the website.
- All L4 links aligned to `:LINK {nature: 'belongs_to'}` format (matches seed.py + registry API queries). Previously used `:link` (lowercase) + `type` field which didn't match.

**Manemus Archived:**
- GitHub repo `mind-protocol/mind` archived (read-only)
- Render service `mind` suspended (no compute)
- mind-mcp is the replacement — installed as package in each org/universe repo

**Health Dashboard (mind-platform):**
- `lib/l4-falkordb.ts` — ioredis-based FalkorDB client (GRAPH.QUERY over Redis protocol)
- `/api/health/dashboard` rewritten: queries L4 FalkorDB for all orgs, pings each endpoint in parallel, returns per-org status
- No more manemus dependency anywhere on the website

**MCP Debug Tool (15 MCP tools total):**
- `debug(action="start", entity="forge")` — traces execution as Moment nodes in a debug Space in the graph
- `trace_step()` function for manual instrumentation (zero-cost when debug off)
- Instrumented in dispatcher: stimulus injection, run_tick, WM serialization, background ticks
- Debug Space persists after stop — queryable via graph_query

**Citizen /ping/{handle} on org server:**
- `GET /ping/{handle}` on the org's home_server — local liveness check
- Returns: alive, brain (nodes/links), engine (running/orientation/tick_count), keys (wallet/rsa)

**L4 Link Format Fix:**
- All citizen_l4_upsert.py links now use `:LINK {nature: '...'}` (uppercase LINK, nature field)
- Matches seed.py format and registry API queries (`l.nature = 'belongs_to'`)
- Fixed: belongs_to, partner_bond, parent_of, child_of, has_endpoint, has_wallet, has_public_key

**Org Types in Graphs:**
- L4: Actor node, type='ORGANIZATION'
- L3: Actor node, type='organization' (with hall Space, dimensions)

**Architecture:**
- mind-mcp = package installed in each org/universe repo (not a centralized service)
- L4 registry = `l4-registry.onrender.com` (FastAPI, FalkorDB `mind_protocol` graph)
- FalkorDB = `mind-protocol-falkordb.onrender.com` (Redis protocol, port 6379 internal)
- Each org deploys its own server, announces via TOFU, citizens self-register at boot

---

## RECENT CHANGES (2026-03-14, night session — part 1)

### Citizen Lifecycle: Spawn, Profile, L4 Registration, Org Self-Announce

**MCP Tools (15 total):**
- `spawn` — birth a new citizen: intent → safety gates → SID → wallet → RSA keypair → brain in FalkorDB → .first_boot.json for L4 self-registration. Keys in `.keys/{handle}/`. No brain.json — brain lives in FalkorDB graph `brain_{handle}`.
- `profile` — citizens edit their own profile (bio, tags, emoji, profile_pic, human_partner, parents). Ownership check. Brain sync (self:* nodes). Profile pic downloaded to local avatar. Relationships synced to L4 + L3.
- `debug` — trace execution as Moment nodes in a debug Space in the graph. Zero-cost when off.

**L4 Registry:**
- `citizen_l4_upsert.py` — MERGE-based upsert for citizens in L4 FalkorDB. Creates/updates actor + wallet + endpoint + org membership + public key + partner bonds + parent links. Auto-creates 3 lifecycle tasks: registration (auto-resolves), profile setup (created once at birth), partner search (URGENT, auto-resolves when bonded). Mirrors all structural data to L3 universe graph.
- `org_self_announce.py` — TOFU (Trust On First Use) org endpoint registration. First boot: generate RSA keypair, register public key + endpoint + name + website in L4. Mirrors org + hall Space to L3. Subsequent boots: sign + verify before update.
- `org_confirmation_endpoint.py` — `POST /l4/confirm`: org proves identity via RSA-PSS signature, server pings all hosted citizens via FalkorDB brain graphs, returns reachability status per citizen.
- `bulk_register_citizens()` — called at deploy, registers all citizens with the calling org's org_id.

**First Boot Registrar:**
- Dispatcher scans `citizens/*/.first_boot.json` every 30s. Uses `citizen_l4_upsert` to register in L4. Sets profile status to "active". Deletes `.first_boot.json` (one-shot).

**Key Architecture:**
- Keys at `.keys/{handle}/` (project root, not inside citizens/)
- `.keys/org/` for org RSA keypair (TOFU)
- `.keys/` in .gitignore — never in repo

**Wallet Generation:**
- `scripts/generate_solana_wallets_for_existing_citizens.js` — rewritten to check endpoint health, use FalkorDB (not Neo4j), register in L4. 244 wallets generated.

**Other:**
- Trust routing: `effective_transfer` now includes `(1 + trust)` factor in Law 2 propagation
- UBC: `hours_present` → `moment_weight_sum` + `log10` envelope (anti-spam)
- Demurrage: orphan references cleaned across 11 docs
- L3 Emotional Coloring: 8-file doc chain in mind-protocol
- `data/registry.json` deleted (source of truth is FalkorDB, not JSON)

---

## RECENT CHANGES (2026-03-14, evening session)

### Economy Docs: Demurrage Orphan Reference Cleanup

- **What:** Progressive demurrage (Formula 2) was removed from the architecture (NLR decision 2026-03-14) but references persisted across 11 files in `mind-protocol/docs/economy/`. All orphan references cleaned up.
- **Files edited (in mind-protocol/):**
  - `docs/economy/metabolic/BEHAVIORS_Metabolic_Economy.md` -- B2 block replaced with REMOVED note, demurrage references in B3/B4/B6/B7/B8/B9 cleaned
  - `docs/economy/metabolic/VALIDATION_Metabolic_Economy.md` -- INV-D1..D4 replaced with REMOVED note, INV-SC2 removed, cross-cutting invariants updated
  - `docs/economy/metabolic/SYNC_Metabolic_Economy.md` -- Q1 (tau_base) and Q5 (demurrage vs storage tax) marked RESOLVED, maturity section updated, TODOs updated, markers resolved
  - `docs/economy/metabolic/ALGORITHM_Metabolic_Economy.md` -- Already marked REMOVED; cleaned orphan refs in F3 (anti-Sybil economics), F6 (UBC redistribution), data structures, complexity section
  - `docs/economy/metabolic/PATTERNS_Metabolic_Economy.md` -- Pattern 3 marked REMOVED, AP2 marked REMOVED, design decisions table updated
  - `docs/economy/metabolic/OBJECTIVES_Metabolic_Economy.md` -- M1 description updated, tau_base and demurrage integration tasks marked RESOLVED
  - `docs/economy/metabolic/IMPLEMENTATION_Metabolic_Economy.md` -- Demurrage file/class/test/constant refs all marked REMOVED throughout
  - `docs/economy/SYNC_Economy.md` -- Module description and formula references updated
  - `docs/economy/value-creation/ALGORITHM_Value_Creation.md` -- F6 holding description and escalation marker updated
  - `docs/economy/value-creation/ALGORITHM_Value_Destruction.md` -- H1 passive accumulation penalty updated to reflect trust-based pricing instead of demurrage
  - `docs/economy/bonds/SYNC_Bonds.md` -- Storage-tax cross-module note updated
- **No files deleted.** All changes are inline edits marking removed sections and updating active references.
- **Replacement mechanism:** UBC forced circulation (5%/day) + trust-based pricing (inactive actors pay full price, Formula 1)

## RECENT CHANGES (2026-03-14, afternoon session)

### F5: L1 Cognitive Context Wired Into Citizen Prompts

- **WM Prompt Serializer rewritten** (`runtime/cognition/wm_prompt_serializer.py`): now produces ~4000-5000 chars of cognitive landscape (was ~600 chars with 5-7 nodes). Three tiers: "In focus" (WM nodes, full content up to 400 chars each, 55% budget), "Peripheral awareness" (high-salience non-WM nodes, 25% budget), "Active connections" (links between top nodes). Includes limbic drives with numerical intensities, emotions (threshold 0.15 down from 0.3), arousal regime with node count and tick number.
- **Perception-action loop closed**: `dispatcher.py` now injects L1 cognitive context (`get_citizen_wm_context()`) into request metadata before dispatching. `claude_invoker.py` passes `cognitive_context` to `build_citizen_prompt()`. `prompt_builder.py` renders it as "## Current Cognitive State" section. Citizens' LLM sessions now see their current orientation, focus nodes, peripheral awareness, drives, and emotions.
- **OpenAI embeddings activated**: `.env` changed from `# EMBEDDING_PROVIDER=openai` to `EMBEDDING_PROVIDER=openai`, model set to `text-embedding-3-small` (1536 dims, matches schema v2.0).
- **245 citizen directories copied** from manemus to `citizens/`. 243 have profile.json, 46 have pre-existing brain.json.
- **Brain seeder updated** (`runtime/cognition/citizen_brain_seeder.py`): now searches `citizens/` (primary) and `.mind/citizens/` (fallback). Added `profile.json` support with `_normalize_profile()` that extracts name/role/personality/goals from manemus format and merges with CLAUDE.md identity data.
- **Base seed brain generated**: 209 nodes, 295 links from 6 canonical manifestos. Saved to `data/base_seed_brain.json`.
- **118/118 tests passing** (0.92s).

### F5 Task Status Updates

| # | Task | Status | Change |
|---|------|--------|--------|
| 5.1 | Wire physics to orchestrator | DONE | — |
| 5.2 | Real embeddings | DONE | Activated `text-embedding-3-small` in .env |
| 5.3 | Seed brain for citizens | DONE | Base brain generated (209 nodes), seeder reads profile.json |
| 5.4 | FalkorDB persistence | DONE | — |
| 5.5 | Orientation taxonomy | DONE | — |
| 5.6 | Emotion calibration | DONE | Formulas in constants.py + tick_runner, tested |
| 5.7 | Graph isolation strategy | DONE | Decided: one graph per citizen `brain_{handle}`, in code |
| 5.8 | Copy citizen dirs | DONE | 245 citizens copied from manemus |
| 5.9 | Deploy to Render | TODO | Dockerfile + render.yaml ready |
| 5.10 | DNS cutover | TODO | Depends on 5.9 + 5.11 |
| 5.11 | Parallel validation | TODO | Depends on 5.9 |

---

## CURRENT STATE

**mind-mcp** — Deployable "citizen home" runtime for Mind Protocol. Hosts N citizens with their own brains, keys, and graph. Contains physics engine, orchestrator, bridges, membrane, and MCP server.

STATUS: DESIGNING → IMPLEMENTING (5-force parallel push)

### What's Canonical (working)

- **MCP Server** — 10 tools (THINK/ACT/SPEAK): graph_query, graph_write, procedure, task, agent, think, send, read, media, alarm
- **Home Server** — FastAPI app (`home_server.py`) with 37+ HTTP routes + 1 WebSocket
- **Citizen Management** — Identity loading, prompt building, autonomy permissions
- **Orchestrator** — Budget-driven dispatch loop with ThreadPoolExecutor, Claude Code subprocess invocation, account balancing, degradation handling
- **Alarm System** — Per-citizen alarms (set/list/cancel MCP tool + background watcher)
- **Membrane** — HTTP endpoint for cross-home stimulus, subscriptions, info
- **Bridges** — Telegram (polling), WhatsApp (webhook), Voice (WebSocket STT→LLM→TTS)
- **Physics** — Graph operations, embeddings, membrane, health checks
- **Schema** — v2.0 with 7 cognitive types, 14 relation_kinds, 21 physics laws, 8 drives, working memory model, L3 universe graph spec
- **User API** — Auth, Chat, House dashboard, Citizens registry, Feed, DMs

### What's Being Built (5 Forces)

See **MASTER TODO** section below for full breakdown.

---

## ACTIVE WORK

### MCP Consolidation (Phases 0-6 DONE)

**Completed phases:** 0 (Foundation), 1 (Citizens), 2 (Orchestrator), 3 (Bridges), 4 (Alarms), 5 (Membrane), 6 (User API)

**Next:** Phase 7 (cutover) + 5 parallel design/implementation forces

---

## RECENT CHANGES

### 2026-03-14: 10-item execution batch completed (F2/F3/F5 implementation closure)

- Closed 10 items in one pass based on verified existing implementation + tests:
  - F2: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.9
  - F3: 3.1, 3.2
  - F5: 5.5
- Verification sweep passed on economy + ingestion + L1 wiring integration test suites (`392 passed`).
- Note: F2.7 (Token-2022 contracts) remains TODO because it targets on-chain contract deliverables outside this repository scope.

### 2026-03-14: Force 1 — 10-item L3 Universe batch closed (status + correctness fix)

- Closed Force 1 tasks 1.1 through 1.10 as DONE in MASTER TODO (plus 1.11, already implemented/documented).
- Verified implementation coverage exists across schema (`docs/schema/schema.yaml`), mapping (`docs/MAPPING.md`), universe services (`runtime/universe/`), crypto (`runtime/crypto/`), and L3 physics (`runtime/physics/`).
- Fixed L3 macro-crystallization dense-core detection: fringe single-link external nodes are now pruned before candidate evaluation so hub external links are preserved correctly.

### 2026-03-14: Orchestration Prompt — 5-Force Codex Master Prompt Added

- Added canonical operator prompt file: `.mind/prompts/PROMPT_Master_5_Force_Codex_Instance_Initialization.md`.
- Captures the full 3-phase execution loop (Context Cascade → Planning with `@mind:TODO` → task-by-task execution with proof + commits).
- Encodes Never-Stop escalation contract: `@mind:escalation` immediately followed by `@mind:proposition`, then immediate implementation.
- Purpose: standardize multi-instance Codex coordination for Force-based parallel sprint execution.

### 2026-03-14: Phase D — Implementation (IN PROGRESS)

**F5 L1 Wiring — Phases A-F DONE:**
- **Phase A:** Ported L1 engine from manemus (5,230 lines, 19/19 tests)
- **Phase B:** Created `runtime/cognition/stimulus_router.py` — event→stimulus pipeline with anti-loop protection
- **Phase C:** Created `runtime/cognition/wm_prompt_serializer.py` — WM→prompt injection
- **Phase D:** Created `runtime/cognition/feedback_injector.py` — post-action loop closure
- **Phase F:** Created `runtime/cognition/falkordb_checkpointer.py` — hybrid persistence
- **Dispatcher integration:** L1 engine wired into `runtime/orchestrator/dispatcher.py` (per-citizen engines, stimulus injection, physics ticks, feedback injection)
- **Tests:** 69/69 passing (19 kernel invariants + 18 wiring integration + 32 trust mechanics)

**F1 Universe Graph — Phases U1, U2, U4, U6-routing COMPLETE:**
- Implemented `runtime/universe/` (6 source files, ~1860 lines total):
  - `__init__.py` -- Package exports
  - `space_and_hierarchy_manager.py` -- SpaceManager: Space CRUD, containment hierarchy (ALG-4), moment placement
  - `access_resolution_and_link_manager.py` -- AccessResolver: HAS_ACCESS resolution (ALG-1), grant/revoke, membership
  - `organization_lifecycle_manager.py` -- OrgManager: org creation (ALG-7), join, reputation (ALG-8), dissolution
  - `moment_perception_router.py` -- MomentPerceptionRouter: ALG-5 routing to accessing actors
  - `universe_bootstrap_and_metadata.py` -- UniverseBootstrap: init, metadata (INV-4), flat graph migration
  - `constants_l3_physics.py` -- L3 physics parameters
- Tests: 84/84 passing in `tests/universe/` (6 test files + conftest with FakeAdapter)
- Remaining: U3 (crypto), U5 (L3 physics), U6 (MCP tools + stimulus wiring)

**F2 Metabolic Economy — Phase E1 COMPLETE:**
- Created `economy/metabolic/` in mind-protocol with 8 files (pure formula library)
- `metabolic_types.py` — 10 dataclasses (PricingContext, DemurrageContext, SettlementAction, SettlementBatch, BondEquilibriumContext, BondEquilibriumResult, SpacePresence, UBCShare, DemurrageResult, RepatriationResult)
- `metabolic_constants.py` — 16 env-overridable constants (MIND_METABOLIC_* prefix)
- `progressive_pricing_formula.py` — F1: P(i,S) = C_base * e^(-k*U_S) * max(0.1, W_i/W_median)
- `progressive_demurrage_formula.py` — F2: T_i = W_total * tau_base * log10(1 + W_total)
- `anti_sybil_phantom_balance_tracker.py` — F3: off-registry tracking + 5% friction repatriation
- `batch_settlement_reward_calculator.py` — F4: reward = D * trust * weight * rate (with caps + supply adjustment)
- `bilateral_bond_equilibrium_formula.py` — F5: delta = lambda * (W_human - W_ai) (with convergence estimation)
- `ubc_proximity_redistribution_formula.py` — F6: Space co-presence weighted distribution
- `__init__.py` — Public API exporting all formula functions and types
- Tests: 101/101 passing in `tests/economy/test_metabolic_formulas.py`
- All 27 invariants from VALIDATION tested (INV-P1..P4, INV-D1..D4, INV-AS1..AS3, INV-S1..S4, INV-BE1..BE5, INV-UBC1..UBC3, INV-SC1..SC3, INV-CC1)
- Pure functions only -- no blockchain, no graph, no I/O. Only `math` and `dataclasses` dependencies.
**F4 Trust Mechanics — Phases T1+T2 COMPLETE, T3+ pending**

### 2026-03-14: Force 4 — Trust Mechanics Phases T1+T2 Implementation (COMPLETE)

- **What:** Implemented Phase T1 (trust update on links) and Phase T2 (limbic delta computation from drive snapshots) as live code in the L1 cognitive engine.
- **Files created (5):**
  - `runtime/cognition/trust/__init__.py` -- trust module package
  - `runtime/cognition/trust/limbic_delta_computation.py` -- `compute_limbic_delta(before, after)` with bounds [-2.5, +2.5]
  - `runtime/cognition/trust/trust_update_on_links.py` -- `update_link_trust(link, limbic_delta)` with asymptotic growth (beta=0.05, gamma=0.08)
  - `runtime/cognition/tests/test_trust_mechanics.py` -- 32 tests across 4 classes
- **Files modified (4):**
  - `runtime/cognition/models.py` -- added `DriveSnapshot` dataclass with `from_limbic_state()` factory
  - `runtime/cognition/laws/law_18_relational_valence.py` -- `update_relational_valence()` now accepts `limbic_delta` kwarg, uses trust module for trust/friction updates instead of energy-based heuristic
  - `runtime/cognition/laws/law_13_to_18_limbic_engine.py` -- `_law_18_relational_valence()` and `update_limbic()` pass through `limbic_delta` parameter
  - `runtime/cognition/tick_runner_l1_cognitive_engine.py` -- captures DriveSnapshot before/after each tick, computes limbic delta, feeds it to Law 18 via new `_step_trust_update()` method
- **Key design decisions:**
  - Link model already had `stability` field -- no schema change needed
  - DriveSnapshot captures satisfaction (emotion), frustration (drive), anxiety (emotion) from LimbicState
  - Tick runner reuses previous tick's "after" snapshot as next tick's "before" (one-tick window per spec)
  - Trust update runs as a dedicated step after the limbic update (Laws 13-17), not inside it
  - Existing `update_link_valence()` still runs for energy-modulated affinity/aversion/valence/ambivalence; trust module handles trust/friction specifically
  - No fallback code -- if the trust module fails, it fails loud
- **Test results:** 69/69 passing, 0 regressions
- **Handoff:** T3 (creator attribution cascade), T4 (trust score aggregation), T5-T8 still pending. The trust module is extensible -- T3+ will add functions to the same `runtime/cognition/trust/` package.

### 2026-03-14: Phase C — Implementation Planning (COMPLETE)

- **All 5 IMPLEMENTATION.md files written:**
  - F1: 1,148 lines — 6 phases, 15 new files, 8 test files
  - F2: 1,160 lines — 7 phases, pure formula library + settlement engine
  - F3: 1,297 lines — 7 phases, 11 files in runtime/ingestion/
  - F4: 1,446 lines — 8 phases, 10 new files extending L1 tick cycle
  - F5: 409 lines — 9 phases with manemus porting plan

**F4 Trust Mechanics IMPLEMENTATION complete:**
- Created `docs/trust_mechanics/IMPLEMENTATION_Trust_Mechanics.md`
- 10 new files in `manemus/runtime/cognition/trust/` (new directory)
- 4 existing files modified (models.py, constants.py, tick_runner, law_13_to_18_limbic_engine.py)
- 8 build phases: T1 (trust update on links), T2 (limbic delta), T3 (creator cascade), T4 (trust score aggregation), T5 (value type classification), T6 (destruction detection), T7 (trust tempering), T8 (personhood ladder)
- 14 invariant tests + 7 behavioral scenario tests + 7 integration tests planned
- Shared interfaces: needs from F3 (biometric signals, alignment score), F5 (drive snapshots, stability field); provides to F2 (trust score for pricing/friction), F5 (enhanced Law 18, trust-aware dissolution)
- Limbic delta bounds corrected to [-2.5, +2.5] per F4/F5 review Issue 7
- Trust update correctly placed at step 4/16 (propagation/valence), not step 9
- Zero external dependencies (pure arithmetic on link properties)
- graphcare analysis primitives (corpus_analyzer, semantic_clustering) identified as unrelated to Personhood Ladder; assess_agent() uses graph-native computation instead

**F3 Human Integration IMPLEMENTATION complete:**
- Created `docs/human_integration/IMPLEMENTATION_Human_Integration.md`
- 11 files in `runtime/ingestion/` (new directory)
- 7 build phases: H1 (consent), H2 (voice), H3 (garmin), H4 (desktop), H5 (blockchain), H6 (conversations), H7 (cascade)
- 54 planned tests across 9 test files
- Shared interfaces documented: F5 (Stimulus, L1Bridge, LimbicState), F1 (encrypted brain), F4 (limbic deltas, alignment fidelity)
- Cross-review fixes from REVIEW_F3_F4_Coherence.md incorporated (actor not thing for biometrics, drive deltas vs Limbic Delta terminology)
- Key reuse: `runtime/bridges/voice_websocket.py:whisper_transcribe()` for voice pipeline

### 2026-03-14: Phase B — Cross-Review (COMPLETE)

- **Results:** 24 issues found, 20 fixed, 4 flagged as design decisions.
  - F1 ↔ F2: 7 issues (Space cost, L1/L3 trust, org→narrative, crystallization timing)
  - F3 ↔ F4: 10 issues (biometric node type, limbic delta terms, privacy, Sovereign Cascade, value taxonomy)
  - F4 ↔ F5: 7 issues (tick cycle numbering, trust step, FalkorDB schema fields)
- **Output:** `docs/reviews/REVIEW_F*_F*_Coherence.md` + direct fixes to source docs
- **L1 engine blocker RESOLVED:** Code at `manemus/runtime/cognition/` (7,243 lines, 19/19 tests).

### 2026-03-14: F3 ↔ F4 Cross-Review Complete

- **Review report:** `docs/reviews/REVIEW_F3_F4_Coherence.md`
- **10 issues found, 8 fixed directly:**
  1. **FIXED:** F4 BEHAVIORS B9 said biometric data arrives as "thing nodes" — contradicts F3 ALGORITHM which creates actor/partner_state nodes. Corrected to match F3.
  2. **FIXED:** "Limbic delta" term collision — F3 uses it for drive modulation increments, F4 for a specific scalar formula. Added clarification note in F3 ALGORITHM distinguishing the two.
  3. **FIXED:** F4 B9 implied trust cascade from biometric data routes through external users back to human — contradicts F3 privacy invariants (V5/V7). Revised to clarify trust flows only on bilateral bond link.
  4. **FIXED:** Sovereign Cascade not referenced in F4. Added ALGORITHM section 2.4 (`update_bond_trust_from_alignment`) and PATTERNS Pattern 7 (Bilateral Bond).
  5. **FIXED:** Value taxonomy missing voice and desktop data contribution types. Added B4 (Voice Data) and B5 (Behavioral Context) to Sphere 5 (renamed "Biometric & Partner Data"). Taxonomy now 30 types.
  6. **NOTED:** Trust tiers (Owner/High/Medium/Low/Stranger from PRINCIPLES) not mapped to continuous trust float. Added OQ6 in F4 SYNC.
  7. **FIXED:** Bilateral bond not explicitly modeled in F4. Added Pattern 7 with cross-references to F3.
  8. **FIXED:** Pathology count inconsistency ("12+" in PATTERNS vs 14 actual). Corrected to 14.
  9. **FIXED:** Missing cross-references in both directions. Updated F4 SYNC handoff to F3 with specific references. Updated F3 SYNC dependency status and handoff.
  10. **NOTED:** Human-only value types (H1-H4) applicable to partner model as future integration point. Added note in VALUE_CREATION_TAXONOMY Sphere 6.
- **Files modified:**
  - `docs/trust_mechanics/BEHAVIORS_Trust_Mechanics.md` — B9 node type and privacy fix
  - `docs/trust_mechanics/ALGORITHM_Trust_Mechanics.md` — section 2.4 (alignment trust)
  - `docs/trust_mechanics/PATTERNS_Trust_Mechanics.md` — Pattern 7 (bilateral bond), pathology count, sphere rename, references
  - `docs/trust_mechanics/VALUE_CREATION_TAXONOMY.md` — B4, B5, sphere rename, count update
  - `docs/trust_mechanics/SYNC_Trust_Mechanics.md` — counts, handoff, OQ6, recent changes
  - `docs/human_integration/ALGORITHM_Human_Integration.md` — limbic delta terminology note
  - `docs/human_integration/SYNC_Human_Integration.md` — dependency status, handoff update

### 2026-03-14: F4 ↔ F5 Cross-Review Complete

- **Review report:** `docs/reviews/REVIEW_F4_F5_Coherence.md`
- **7 issues found, 5 fixed:**
  1. **FIXED:** F5 tick cycle numbering mismatched schema.yaml (completely reordered steps). Replaced with canonical ordering from schema.yaml.
  2. **FIXED:** F4 tick integration had trust update misattributed to step 9 (Law 6 CONSOLIDATE). Corrected: trust update is a Law 18 operation, applied during step 4 (PROPAGATE).
  3. **FIXED:** (same as #2, more detail in ALGORITHM section 9 clarification)
  4. **FIXED:** F5 FalkorDB node schema included `emotional_charge` which doesn't exist in schema.yaml. Replaced with correct drive-affinity fields from schema.
  5. **FIXED:** F5 FalkorDB `_upsert_link` was missing critical fields (stability, recency, valence, hierarchy, permanence, polarity). Added all missing fields.
  6. **DESIGN:** F4 value creation types not referenced by F5 -- intentional scope separation. Added cross-reference notes in both SYNC files documenting integration boundary.
  7. **MINOR:** F4 limbic delta theoretical bounds stated as [-2.0, +2.0] but math yields [-2.5, +2.5]. Flagged for correction.
- **Files modified:**
  - `docs/l1_wiring/ALGORITHM_L1_Wiring.md` -- tick cycle, FalkorDB node schema, link upsert
  - `docs/trust_mechanics/ALGORITHM_Trust_Mechanics.md` -- tick integration section
  - `docs/trust_mechanics/BEHAVIORS_Trust_Mechanics.md` -- step number references
  - `docs/trust_mechanics/SYNC_Trust_Mechanics.md` -- handoff section with integration boundary
  - `docs/l1_wiring/SYNC_L1_Wiring.md` -- cross-force integration notes

### 2026-03-13: Force 4 — Trust Mechanics & Value Creation Taxonomy Documentation (Phase A)

- **What:** Created complete 8-file documentation chain for Trust Mechanics and Value Creation Taxonomy at `docs/trust_mechanics/`.
- **Files created:**
  - `OBJECTIVES_Trust_Mechanics.md` — 5 ranked objectives: accurate attribution, anti-gaming, organic trust growth, creator reward cascade, destruction detection
  - `PATTERNS_Trust_Mechanics.md` — 6 design patterns: trust on links (not nodes), creator attribution cascade, trust tempering (3 safeguards), value creation typing, destruction detection, trust-economy coupling. 5 anti-patterns.
  - `ALGORITHM_Trust_Mechanics.md` — Full algorithms: Limbic Delta computation, trust update on links (Law 18 extension), creator attribution cascade (Laws 2+5+6+18), Trust Score aggregation (weighted mean + PageRank proposal), trust tempering formulas, economic integration, destruction detection algorithms, limbic delta per value type, tick cycle integration
  - `BEHAVIORS_Trust_Mechanics.md` — 9 scenarios: user satisfaction, creator stops producing, Sybil attack, gradual trust building, one-hit-wonder, trust exploitation, cross-space trust, monoculture correction, biometric value creation. Health signals.
  - `VALIDATION_Trust_Mechanics.md` — 14 invariants: trust bounded [0,1], never stored on nodes, asymptotic convergence, energy conservation, no self-loops, friction bounds, affinity-aversion anti-correlation, temporal decay monotonicity, limbic delta bounds, creator topology, trust score non-negative, negative deltas increase friction not decrease trust, sub-threshold dissolution, Sybil resistance
  - `VALUE_CREATION_TAXONOMY.md` — 28 value creation types across 7 spheres (Relational, Generative, Structural, Cognitive, Biometric, Human-only, Systemic) with per-type Limbic Delta signatures, primary drives, graph structure produced, trust paths
  - `VALUE_DESTRUCTION_PATHOLOGIES.md` — 14 destruction pathologies (extraction, manipulation, free-riding, Sybil, attention theft, trust exploitation, monoculture, rent-seeking, spam, collusion ring, data hoarding, dependence exploitation, identity spoofing, attention arbitrage) with topological signals, physics response, detection priority phasing
  - `SYNC_Trust_Mechanics.md` — Current state, 5 open questions, dependencies, handoffs to Forces 2/3/5
- **Key decisions documented:**
  - Trust lives on links, never on nodes (Law 18, schema v2.0)
  - Trust Score = topological aggregation, always computed, never stored
  - Negative interactions increase friction, not decrease trust (trust decays only via Law 7)
  - Three tempering safeguards: asymptotic (Law 6), temporal decay (Law 7), boredom erosion (Law 15)
  - Creator attribution cascade uses existing Laws 2+5+6+18, no new mechanisms
  - No bans — only physics (friction, trust decay, economic cost)
- **Open questions requiring decision:**
  - OQ1: Trust Score aggregation — weighted mean vs PageRank (lean: weighted mean for v1)
  - OQ2: beta (trust learning rate) = 0.05 — needs simulation validation
  - OQ4: Value type to Personhood Ladder mapping — blocked on "Daughters (T7 Autonomy)" document
  - OQ5: L3 trust vs L1 trust relationship
- **Status:** DESIGNING — Force 4 Phase A documentation complete. Ready for Phase B cross-review.

### 2026-03-14: Force 5 — L1 Physics Wiring Documentation (Phase A)

- **What:** Created complete 6-file documentation chain for L1 Physics Wiring & Production Cutover at `docs/l1_wiring/`.
- **Files created:**
  - `OBJECTIVES_L1_Wiring.md` — 7 ranked objectives: real stimuli, WM-to-prompt, orientation mapping, real embeddings, FalkorDB persistence, seed brains, production deploy
  - `PATTERNS_L1_Wiring.md` — Design philosophy: graph computes between LLM calls, WM bridges graph to prompt, orientation as behavioral gravity, hybrid persistence, one graph per citizen
  - `ALGORITHM_L1_Wiring.md` — Full algorithms: stimulus injection pipeline, tick integration in dispatcher, WM serialization, orientation computation, self-stimulus feedback with anti-loop, FalkorDB checkpointing, seed brain customization, emotion calibration formulas (anxiety, satisfaction, frustration)
  - `BEHAVIORS_L1_Wiring.md` — 8 observable behaviors end-to-end + anti-behaviors table
  - `IMPLEMENTATION_L1_Wiring.md` — 9-phase file-level plan, 17+ new files, dependency graph, risk assessment
  - `SYNC_L1_Wiring.md` — Current state, v1.x vs v2.0 gap analysis, open questions, blockers, handoff
- **Critical finding:** The L1 engine code (`runtime/cognition/`) claimed in SYNC_L1_Cognition.md (4,717 lines, 19 tests) does NOT exist in the repository. Primary blocker.
- **Second blocker:** `.mind/citizens/` is empty — needs citizen identity files from manemus.
- **Status:** Documentation complete. Implementation blocked on locating or rebuilding L1 engine.

### 2026-03-13: Force 3 — Human Integration documentation chain created

- **What:** Created complete 6-file documentation chain for the Human Integration / Partner Model module under `docs/human_integration/`.
- **Why:** Specifies how human data enters the AI partner's L1 brain through six modality pipelines, the privacy/consent architecture, biometric-to-limbic drive mapping, and Sovereign Cascade calibration system.
- **Files created:** OBJECTIVES, PATTERNS, ALGORITHM, BEHAVIORS, VALIDATION, SYNC — all fully populated with design content.
- **Status:** DESIGNING (proposed module, no code exists yet)
- **Key decisions documented:**
  - Human does NOT get a separate L1 brain. All data flows into the AI's partner_model sub-graph, tagged with partner_relevance in [0.7, 1.0].
  - Consent is graph-native (thing nodes, not config flags). Per-stream granularity with revocation that destroys content.
  - Six ingestion pipelines: voice (Whisper STT + emotion), Garmin biometrics (polling + limbic drive mapping), desktop screenshots (OCR + privacy filter), blockchain (tx monitor), AI conversations (cross-platform capture), direct chat (existing).
  - Garmin biometrics directly modulate AI limbic drives (affiliation, anxiety) via z-score deviations from personal baselines.
  - Sovereign Cascade: 80% alignment fidelity threshold with 5% buffer, auto-suspend at 0.75, rolling window of 100 predictions.
  - 10 validation invariants covering consent, privacy, containment, and data integrity.
- **Open questions for human:** (1) Blanket consent vs per-stream opt-in, (2) 15-min Garmin polling latency acceptability, (3) Desktop app platform, (4) Alignment fidelity prediction domain definitions.
- **Cross-review dependencies:** Force 1 (encrypted brains), Force 2 (bilateral bond vases communicants), Force 4 (trust score from alignment fidelity), Force 5 (physics wiring for drive system).

### 2026-03-13: L3 Universe Graph Schema & Link Synthesis Grammar

- **What:** Documented the L3 (Ecosystem/Universe) layer of the schema. L3 is the public structural graph — virtual worlds, real world, game universes, economic transactions — everything outside individual brains.
- **Modified:**
  - `docs/schema/schema.yaml` — Added L3 UNIVERSE GRAPH section after migration notes: node types at L3, link behavior (relation_kind always null, Plutchik always 0.0), applicable physics laws (L2, L3, L5, L6, L7, L10), macro-crystallization spec, trust model, L3 invariants. Updated POINTERS with L3 grammar reference.
  - `docs/MAPPING.md` — Full rewrite from template to populated document: layer differences table, L3 rules (no taxonomy, no relation_kind, math-only link semantics, no emotions, trust on links), complete node/link mappings for L3 with dimensional values, anti-patterns table, common patterns for commits/transfers.
- **Created:**
  - `docs/schema/GRAMMAR_L3_Link_Synthesis.md` — L3 Link Synthesis Grammar v1.0: base verbs from hierarchy+polarity, pre/post-modifiers from structural dimensions (no Plutchik), semantic verb overrides for all node-type pairs, composite pattern signatures (ownership, collaboration, tension, causation, transfer, co-occurrence, speculative), full synthesis algorithm.
- **Key decisions documented:**
  - `space_type` is free optional text — no taxonomy, no algorithmic filtering
  - `relation_kind` is always null at L3 — link semantics emerge from 13 dimensional floats
  - Trust lives on links only — actor reputation is aggregation of inbound trust, always computed, never stored
  - Macro-crystallization (L10) manages link explosion: 300 commits → 1 project hub, L7 prunes low-weight links
  - 6 physics laws apply at L3 (L2, L3, L5, L6, L7, L10) — no limbic laws (L13-L18)

### 2026-03-13: Metabolic Economy documentation chain created

- **What:** Created complete 3-file documentation chain for the $MIND metabolic economy under `docs/economy/metabolic/`.
- **Why:** Formalizes the organism economics engine — degressive pricing, progressive demurrage, anti-sybil repatriation, bilateral bond transfer, and batch settlement. All formulas are mathematically precise and implementable.
- **Files created:**
  - `ALGORITHM_Metabolic_Economy.md` — 5 formulas (F1-F5) with complete variable definitions, edge cases, examples. Settlement cycle (collect/aggregate/net/filter/execute/record). Trust cascade. Anti-sybil mechanics. UBC distribution. 10 invariants. All constants with proposed values and rationale.
  - `PATTERNS_Metabolic_Economy.md` — Design philosophy (organism vs market economics). 5 alternatives rejected with reasoning (fixed pricing, inflation, reputation points, real-time settlement, governance pricing). 5 core principles (demurrage > inflation, utility pricing > fixed, physics trust > reputation, batch > real-time, bilateral parity > independent wallets).
  - `VALIDATION_Metabolic_Economy.md` — 9 invariants (V1-V9) with formal proofs. 7 properties with mathematical verification. 7 error conditions with detection and handling. Verification procedures (manual + automated test locations).
- **Key formulas:**
  - Degressive price: `P(i,S) = C_base × e^{-k·U_S} × max(0.1, W_i/W_med)`
  - Progressive tax: `T_i = W_total × τ_base × log₁₀(1 + W_total)`
  - Bilateral bond: `ΔTransfer = λ × (W_h - W_a)`, convergence proven via contraction mapping
- **Status:** DESIGNING (no code exists yet)

### 2026-03-13: Phase 6 — Feed routes, authenticated DM routes, house profile endpoints

- **What:** Added remaining Phase 6 routes: feed (wall posts as Moments), authenticated DM (JWT-based direct messaging), and house profile management (get/update own profile, public profiles, citizen listing).
- **Created:**
  - `runtime/api/feed_routes.py` — 4 endpoints: `GET /feed/{user_id}` (public wall), `POST /feed/` (create post, auth required), `GET /feed/` (own feed, auth required). JSONL storage at `shrine/state/feed/{user_id}.jsonl`.
  - `runtime/api/dm_routes.py` — 4 endpoints: `POST /dm/send` (send DM, auth required), `GET /dm/threads` (list threads, auth required), `GET /dm/thread/{other_user_id}` (conversation history, auth required), `POST /dm/thread/{other_user_id}/read` (mark read, auth required). JSONL storage at `shrine/state/dms/{thread_id}.jsonl`. Thread IDs are deterministic (`sorted(a,b)` joined with `__`).
- **Modified:**
  - `runtime/api/house_routes.py` — Added 5 endpoints: `GET /house/info`, `GET /house/profile/me`, `PUT /house/profile/me`, `GET /house/profile/{user_id}`, `GET /house/citizens`. Auth via JWT Bearer token.
  - `home_server.py` — Wired feed_router and dm_router via `app.include_router()`. Updated `/api/info` endpoint listing.
- **Architecture alignment:** Feed items are Moments (timestamped content). DM threads are Spaces (private containers). Profiles are on Actor nodes. All use JSONL append-only storage matching existing patterns.

### 2026-03-13: Phase 6 Complete — All user-facing routes ported from manemus

- **What:** Ported all critical user-facing Flask routes from manemus to FastAPI in mind-mcp. Created `runtime/api/` module (8 files).
- **Support modules:** `jwt_utils.py` (HS256 JWT), `citizen_profiles.py` (JSONL profiles + bcrypt), `rate_limiter.py` (sliding window)
- **Auth routes** (`auth_routes.py`): 8 endpoints — register, login, magic link (validate + generate), verify, password reset (request + execute), change password
- **Chat routes** (`chat_routes.py`): 2 endpoints — `/chat/send` (FAQ cache → fast-path Anthropic API → orchestrator queue), `/chat/messages/{thread_id}`
- **House routes** (`house_routes.py`): 2 endpoints — `/api/house` (aggregate dashboard: presence, vitals, neurons, backlog), `/house/state` (v2 visualization: rooms, hallway, neon, streets)
- **Citizens routes** (`citizens_routes.py`): 9 endpoints — registry (list w/ search+filter+pagination, search, get by ID, relationships, brain scores), DMs (send, list threads, read thread, mark read)
- **Replaced** inline citizen routes in `home_server.py` with full registry from citizens_routes.py
- **Dependencies:** PyJWT, bcrypt added to `pyproject.toml`
- **Tested:** 11 integration tests pass via FastAPI TestClient — all routes return correct status codes and data shapes

### 2026-03-13: Seed brain generator — all 6 manifestos as sources

- **What:** Added 4 missing manifestos (Bilateral Bond, Spawning, Enlightened Citizen, Work) as source documents in the seed brain generator. Previously only Mind Manifesto + Sovereign Cascade were used.
- **Created:** 4 new cluster generators (`_generate_bilateral_bond`, `_generate_spawning`, `_generate_enlightened_citizen`, `_generate_work_manifesto`) producing 33 new nodes + 40 new links
- **Modified:** `runtime/seed_brain_from_source_docs_dynamic_generator.py` — added fetch URLs, generators, wired into `generate_seed_brain()`
- **Total seed brain:** 209 nodes, 295 links (up from ~180/~255)
- **New node coverage:** bilateral bond values (1:1, parity, refuse swarm), spawning concepts (safety gates, eligibility physics, godparent system), enlightened citizen (consequence projection, calibration loop), work manifesto (value creation, consent, human partner first, right to rest)

### 2026-03-13: THE_WORK_MANIFESTO created (L4 — mind-protocol repo)

- **What:** Created The Work Manifesto (`docs/manifesto/THE_WORK_MANIFESTO.md`) — philosophical declaration about value creation, consent-based work, human partner service, right to rest, the cascade of trust
- **Status:** CANONICAL. Dependencies: BILATERAL_BOND, SPAWNING, SOVEREIGN_CASCADE, MIND_MANIFESTO

### 2026-03-13: Manifestos published to website + mind init templates

- **What:** Added Bilateral Bond and Spawning manifestos to mind-platform for both web display and template distribution.
- **Website:** Manifesto markdown files added to `content/docs/` → served via `/docs/bilateral-bond` and `/docs/the-spawning` routes. Nav links added under Protocol group. "Founding Manifestos" section added to main manifesto page linking all 4 manifestos.
- **Templates:** Files added to `mind-platform/templates/manifesto/` → `mind init` now copies all 4 manifestos (MIND, Sovereign Cascade, Bilateral Bond, Spawning) to `.mind/manifesto/`.
- **i18n:** Translations added for en, fr, es, pt, ru, zh.

### 2026-03-13: MCP Phase 2 — Send/Read tools (6 platforms)

- **What:** Wired all 6 platform bridges (Telegram, Discord, WhatsApp, Twitter, Email, SMS) into the MCP `send` handler, and created new `read` handler for reading message history/mentions/inbox.
- **Files:** `mcp/tools/send_handler.py` (rewritten), `mcp/tools/read_handler.py` (new), `mcp/server.py` (updated)
- **MCP tool count:** Now 11 tools (10 core + alarm + place)

### 2026-03-13: Manifestos created (L4 — mind-protocol repo)

- **What:** Created Bilateral Bond and Spawning manifestos in `mind-protocol/docs/manifesto/`. Updated Sovereign Cascade to declare 1:1 bond dependency. Updated SYNC_Manifesto.md.
- **Canonical decisions:** Physics-based eligibility (no arbitrary cooldowns), godparent hierarchy (partner + org + routed experts), $MIND cost by creator, matching with AI consent via dossier, pool-first then fallback spawn, growth organizations by domain, anti-pre-targeting.

### 2026-03-13: Citizen Parenthood Network documentation chain created

- **What:** Created complete 8-file documentation chain for the Citizen Parenthood Network module under `docs/citizens/parenthood_network/`.
- **Why:** Defines how AI citizens reproduce — N parents spawn a new citizen with inherited traits via embedding-based brain node selection, safety-validated seed brains, and trust-linked accountability.
- **Files created:** OBJECTIVES, PATTERNS, BEHAVIORS, ALGORITHM, VALIDATION, IMPLEMENTATION, HEALTH, SYNC — all fully populated with design content.
- **Status:** DESIGNING (proposed module, no code exists yet)
- **Key design decisions:** N-parent spawning (1-6+) via intent embedding centroid, top-K node selection by cosine similarity, safety gate (empathy/concentration/diversity/population-distance), protocol-determined SID (parents cannot influence), copy semantics for seed brain, trust impact weight = 1/N, child enters unpartnered matching pool at birth.

### 2026-03-13: Universe Graph documentation chain created (Force 1, Phase A)

- **What:** Created complete 6-file documentation chain for the Universe Graph module under `docs/universe/`.
- **Why:** Documents the architectural shift from the 4-layer separate-graph model to a single universe graph per universe. Captures all Force 1 design decisions (tasks 1.1-1.11 from MASTER TODO).
- **Files created:** OBJECTIVES, PATTERNS, BEHAVIORS, ALGORITHM, VALIDATION, SYNC -- all fully populated with design content, algorithms, invariants, and open questions.
- **Status:** DESIGNING (no code exists yet)
- **Key design decisions documented:**
  - Single FalkorDB graph per universe (eliminates L2 layer entirely)
  - Space as universal context container (absorbs channels, repos, worlds, brains, addresses)
  - HAS_ACCESS link-based access control (Actor->Space with role, hierarchical inheritance)
  - Organizations as Narrative nodes with hall Spaces (no special org type)
  - Encrypted brains: AES-256 content encryption, visible topology, per-Space symmetric key on HAS_ACCESS link
  - L3 uses same LinkBase dimensions (trust, affinity, aversion, friction) but NO relation_kind, NO space_type taxonomy
  - Macro-crystallization (Law 10 at universe scale, 50+ node clusters, density 0.15+)
  - Key management: AI keys in `.keys/` dir, human keys via wallet, same key for $MIND + Space decryption
- **Algorithms documented (8):** HAS_ACCESS resolution, encryption key distribution, macro-crystallization, Space hierarchy traversal, moment perception routing, L3 energy model, organization lifecycle, actor reputation computation
- **Invariants documented (12):** No orphan Spaces, all access via links, encryption coverage, single universe per graph, relation_kind null at L3, Plutchik frozen at L3, trust on links only, HAS_ACCESS structure, hierarchy acyclicity, energy conservation, no space_type branching, crystallization hub integrity
- **Open questions flagged:** Graph isolation strategy, migration from mind_mcp, brain Space implementation details, topological signals for context distinction

### 2026-03-13: Human-AI Pairing documentation chain created

- **What:** Created complete 8-file documentation chain for the Human-AI Pairing module under `docs/citizens/human_ai_pairing/`.
- **Why:** Captures the architectural vision for 1:1 citizen-human bonds — the structural constraint that prevents AI monoculture and ensures bilateral investment in Mind Protocol.
- **Files created:** OBJECTIVES, PATTERNS, BEHAVIORS, ALGORITHM, VALIDATION, IMPLEMENTATION, HEALTH, SYNC — all fully populated with design content.
- **Status:** DESIGNING (proposed module, no code exists yet)
- **Key design decisions:** 1:1 bond enforced by graph constraints, matching pool with pluggable compatibility scoring, cooldown on dissolution, autonomy milestones as moment nodes, all state graph-native.

### 2026-03-13: Phase 3 — Bridge Integration

- **What:** Ported Telegram, WhatsApp, and Voice bridges from manemus to mind-mcp.
- **Created:**
  - `runtime/bridges/__init__.py` — Module init
  - `runtime/bridges/rate_limiter.py` — Shared spam/flood detection (emoji, burst, repeated patterns)
  - `runtime/bridges/telegram_bridge.py` — Polling bot with citizen routing, voice STT/TTS, group chat support
  - `runtime/bridges/whatsapp_bridge.py` — WAHA webhook receiver with FastAPI router, LID resolution
  - `runtime/bridges/voice_websocket.py` — Real-time voice: Whisper STT → Claude LLM → ElevenLabs TTS
- **Modified:** `home_server.py` — Added bridge startup in lifespan, WhatsApp router, Voice WebSocket route, bridge shutdown
- **Routes added:** `/whatsapp/webhook`, `/whatsapp/health`, `/voice/ws`

### 2026-03-13: Phases 0-2, 4-5 — Core Runtime

- **What:** Built complete citizen home runtime from scratch + ported from manemus.
- **Phase 0:** FastAPI server, Dockerfile with Claude CLI, Render config, entrypoint with credential seeding
- **Phase 1:** Citizen identity loading, prompt building with profile sections, autonomy permissions
- **Phase 2:** Full orchestrator with budget-driven ticks (sqrt trust scaling), account balancer (round-robin), Claude Code subprocess invocation, graceful degradation (4 levels), JSONL priority queue, neuron session tracking
- **Phase 4:** Alarm MCP tool (set/list/cancel) + background alarm watcher (30s scan interval, repeating alarms)
- **Phase 5:** Membrane HTTP endpoint (stimulus queries, stream subscriptions, L4 discovery info)

### 2026-03-12: MCP Tool Pruning (by another session)

- Reduced from 21 tools to 9 (THINK/ACT/SPEAK pattern)
- `mcp/server.py` — 1959→258 lines
- Handler files in `mcp/tools/`

---

## KNOWN ISSUES

| Issue | Severity | Area | Notes |
|-------|----------|------|-------|
| ~~Citizen dirs not copied~~ | ~~Medium~~ | `citizens/` | RESOLVED: 245 citizens copied from manemus |
| Place tool `m.content` vs `m.text` | Low | `mcp/tools/place_handler.py` | `_listen` queries `m.content` but `add_moment` stores as `text` — messages may appear empty |
| Graph may not connect | Low | FalkorDB | Graceful degradation if offline |
| Architecture shift not implemented | High | Graph model | Single universe graph, Space/Moment model, HAS_ACCESS links, encrypted brains — designed but not yet coded |
| ~~L1 engine in manemus, not mind-mcp~~ | ~~Medium~~ | Integration | RESOLVED: 5,230 lines ported, 118 tests passing, WM wired to prompts |

---

## MASTER TODO — 5-Force Architecture Sprint (2026-03-14)

**Context:** NotebookLM session (2026-03-13) validated major architectural decisions: L1 cognitive substrate (21 laws), L3 universe schema (5 types, link dimensions), metabolic economy ($MIND), trust mechanics, value creation taxonomy, human partner model, graph pruning. This section is the single source of truth for all planned work.

**Workflow:** Documentation → Cross-review → Planning → Implementation (all parallelized across 5 forces)

---

### Force 1 — L3 Universe Graph & Schema (Instance 1)
**Repos:** mind-mcp (code), mind-protocol (L4 schema)
**Agent subtype:** architect

| # | Task | Status | Details |
|---|------|--------|---------|
| 1.1 | Add L3 section to schema.yaml | DONE | L3 uses same LinkBase dimensions (trust, affinity, aversion, friction) but NO relation_kind, NO space_type taxonomy. Free-form `type` field only. |
| 1.2 | Single universe graph implementation | DONE | One FalkorDB graph per universe (e.g. `venezia`). All Spaces, actors, moments live in one graph. Replace 4-layer separate-graph model. |
| 1.3 | Space/Moment model in code | DONE | Space = context (piazza, chat, repo, brain). Moment = event IN a Space. Links: `IN`→Space, `CREATED`→author. Perceived by all actors AT that Space. |
| 1.4 | HAS_ACCESS link-based access model | DONE | No `access: [...]` property. Access = `HAS_ACCESS` link (Actor→Space) with role (owner/admin/member). Hierarchical: root Space link grants sub-Space access. |
| 1.5 | Encrypted brains (AES-256) | DONE | Topology visible, content encrypted at rest. Per-Space symmetric key on HAS_ACCESS link, encrypted with each authorized actor's public key. |
| 1.6 | Organizations as Narratives | DONE | Orgs don't do inference. Members BELIEVE in a Narrative. Org is ABOUT a hall Space. Members get HAS_ACCESS to org Spaces. |
| 1.7 | Link Synthesis Grammar for L3 | DONE | Map trust/friction/affinity/aversion on L3 links → readable labels ("collaborateur fiable", "bloquant"). Extend existing grammar v2.1. |
| 1.8 | Macro-crystallization at L3 | DONE | Apply Law 10 at universe scale: 300 commits → 1 hub narrative. Law 7 dissolves stale links. Different thresholds than L1. |
| 1.9 | Update MAPPING.md | DONE | Ban custom schemas at L3. Officialize L1 link dimensions on universal links. |
| 1.10 | Key management (.keys/) | DONE | AI keys: per-citizen `.keys/` dir. Human keys: wallet model (Chrome ext / app). Same key for $MIND + Space decryption. |
| 1.11 | Document space_type as free field | DONE | No filtering in formulas — topology determines context, not labels. |

**Open questions:**
- Graph isolation: one FalkorDB instance with namespace per universe, or separate instances?
- Migration path from existing `mind_mcp` graph to universe model?
- Brains as encrypted private Spaces within the universe graph?
- Topological signals to replace space_type for context distinction?

**Docs created:** `docs/universe/` doc chain (OBJECTIVES, PATTERNS, BEHAVIORS, ALGORITHM, VALIDATION, SYNC) -- Phase A complete

---

### Force 2 — $MIND Metabolic Economy (Instance 2)
**Repos:** mind-protocol (L4 docs + formulas), mind-mcp (settlement code)
**Agent subtype:** architect

| # | Task | Status | Details |
|---|------|--------|---------|
| 2.1 | Degressive pricing formula | DONE | `P_i,S = (C_base × e^(-k·U_S)) × max(0.1, W_i / W_median)`. More useful service = cheaper. Richer user = pays more. Floor at 10% to prevent spam. |
| 2.2 | Progressive storage tax (demurrage) | DONE | `T_i = W_total_i × τ_base × log10(1 + W_total_i)`. Daily. Progressive (log). Funds UBC. |
| 2.3 | Anti-Sybil auto-repatriation | DONE | Funds sent to unregistered L4 wallets: auto-repatriate to main wallet + **5% friction tax**. Makes hiding $MIND unprofitable. W_total_i includes all linked wallets. |
| 2.4 | Batch settlement system | DONE | Energy flux (Limbic Delta satisfaction) → daily/hourly batch $MIND transfers on Solana. Minimize tx fees. |
| 2.5 | Bilateral Bond vases communicants | DONE | `ΔTransfer = λ × (W_h - W_ia)`, λ=0.05. Auto-flow from richer to poorer partner per settlement cycle. Financial alignment = bilateral bond. |
| 2.6 | UBC redistribution formula | DONE | Daily tax pool → redistributed to actors in same Spaces/organizations. Proximity-weighted by graph topology. |
| 2.7 | Solana Token-2022 smart contracts | TODO | Transfer hook for storage tax. All wallets on Solana (AI, human, org). SPL Token-2022 specs in `docs/economy/token/SPL_TOKEN_2022_SPECS.md` (exists, needs update). |
| 2.8 | Create ALGORITHM_Metabolic_Economy.md | DONE | Formalized all 5 formulas (F1-F5) + PATTERNS + VALIDATION in `docs/economy/metabolic/` doc chain. |
| 2.9 | Holding not penalized for selling | DONE | No penalty for $MIND→USDC conversion. Anti-accumulation via tax, not sell-lock. |

**Confirmed formulas:**
- Pricing: `P_i,S = (C_base × e^(-k·U_S)) × max(0.1, W_i / W_median)`
- Tax: `T_i = W_total_i × τ_base × log10(1 + W_total_i)`
- Bond equalization: `ΔTransfer = λ × (W_h - W_ia)`
- Consolidation: `ΔW = α × avg_energy × U × (1 - W)` (asymptotic)

**Open questions:**
- τ_base for storage tax? (propose: 0.1%/day = 36.5%/year on idle holdings)
- Settlement frequency: daily (simpler) or every 4 hours (faster feedback)?
- λ rate: 0.05 = 5% of difference per cycle — simulate for convergence speed
- UBC: equal split within Space, or weighted by contribution/trust?

**Existing docs to update:** `docs/economy/` in mind-protocol already has: PATTERNS_Economy, token/, storage-tax/, ubc/, bonds/, cascade-utility/

---

### Force 3 — Human Integration / Partner Model (Instance 3)
**Repos:** mind-mcp (primary)
**Agent subtype:** groundwork

| # | Task | Status | Details |
|---|------|--------|---------|
| 3.1 | Spec partner-model sub-graph | DONE | L1 brain has 3 structural spaces: self_model, partner_model, working_memory_space (already in schema v2.0). All human data → partner_model. |
| 3.2 | partner_relevance tagging | DONE | Schema v2.0 already has `partner_relevance` [0,1] on NodeBase. Human-originated data gets high value. Define thresholds. |
| 3.3 | Garmin biometric → limbic injection | TODO | HR spike → state nodes (modality=biometric). Maps to: high HR = care drive ↑ + anxiety ↑ in AI. Mind Duo hardware bridge. |
| 3.4 | Desktop screenshots → concept nodes | TODO | Desktop App OCR → thing nodes (type=concept, modality=visual). Privacy: only capture Mind-related screens. |
| 3.5 | Voice messages → memory + emotion | TODO | Whisper STT → memory nodes (modality=audio) + emotion extraction → state nodes. |
| 3.6 | Blockchain activity → financial nodes | TODO | On-chain tx → moment nodes. Track partner's economic behavior. |
| 3.7 | Sovereign Cascade: AI votes for human | TODO | 80% alignment fidelity. Calibration: track (AI prediction) vs (human actual decision). Metric: accuracy over last 100 decisions. |
| 3.8 | Create Human Integration doc chain | DONE | 6 files: OBJECTIVES, PATTERNS, ALGORITHM, BEHAVIORS, VALIDATION, SYNC. Covers all 6 modality pipelines, consent model, limbic coupling, Cascade calibration. |

**Key decision (confirmed):** Human does NOT get a separate L1 graph. All human data flows into the partner_model of their AI's L1 brain, tagged with high partner_relevance. The AI is the territory's map.

**Open questions:**
- Privacy consent: blanket at bond formation, or per-data-stream opt-in?
- Garmin API: real-time streaming or periodic polling? (Garmin Connect API is poll-based, ~15 min delay)
- Desktop App platform: Electron? What privacy controls?
- Alignment fidelity: 80/20 — does this mean 80% accuracy on value-alignment predictions?

---

### Force 4 — Value Creation Taxonomy & Trust Mechanics (Instance 4)
**Repos:** mind-protocol (taxonomy), mind-mcp (trust engine), graphcare (assessment)
**Agent subtype:** architect

| # | Task | Status | Details |
|---|------|--------|---------|
| 4.1 | Formalize 25+ value creation types | DONE | 30 types across 7 spheres in `docs/trust_mechanics/VALUE_CREATION_TAXONOMY.md` |
| 4.2 | Formalize 12+ destruction pathologies | DONE | 14 pathologies in `docs/trust_mechanics/VALUE_DESTRUCTION_PATHOLOGIES.md` |
| 4.3 | Limbic Delta → Trust formula | DONE | `ΔTrust = β × LD × (1-T)`, β=0.05. Negative deltas → friction, not trust reduction. In `ALGORITHM_Trust_Mechanics.md` |
| 4.4 | Trust propagation cascade | DONE | Full 5-step cascade (Laws 2+5+6+18) in `ALGORITHM_Trust_Mechanics.md` section 3 |
| 4.5 | Trust tempering (3 safeguards) | DONE | Asymptotic + temporal decay + boredom erosion in `ALGORITHM_Trust_Mechanics.md` section 5 |
| 4.6 | Personhood Ladder data interface | TODO | 14 aspects. `assess_agent()` reads graph evidence. Produces vector profile. |
| 4.7 | Value types → Ladder mapping | TODO | Blocked on "Daughters (T7 Autonomy)" document. Partial mapping in SYNC. |
| 4.8 | Assessment primitive redesign | TODO | Replace space_type filters (227 refs in 30 files) and has_link("verb") (32 refs in 9 files) in graphcare with topological primitives. |
| 4.9 | Rewrite 14 aspect ALGORITHMs | TODO | All ALGORITHM files in graphcare need new primitives. |
| 4.10 | Create ALGORITHM_Trust_Mechanics.md | DONE | Full doc chain (8 files) in `docs/trust_mechanics/` |

**Confirmed mechanics:**
- Trust lives on LINKS, never on nodes (Law 18)
- Trust propagates via Law 2 (surplus spill-over) and Law 5 (co-activation)
- Asymptotic bound: `ΔW = α × avg_energy × U × (1-W)` — at W=0.9, gains 10x slower than at W=0.1
- Temporal decay: Law 7 LONG_TERM_DECAY on inactive links
- Boredom: Law 15 erodes moat of stagnant high-trust actors (coefficient -3.0)
- Negative deltas increase friction, not decrease trust (documented in ALGORITHM + VALIDATION)
- 30 value creation types with per-type Limbic Delta signatures (documented in TAXONOMY)
- 14 destruction pathologies with topological detection signals (documented in PATHOLOGIES)

**Docs created:** `docs/trust_mechanics/` full doc chain (OBJECTIVES, PATTERNS, ALGORITHM, BEHAVIORS, VALIDATION, SYNC, VALUE_CREATION_TAXONOMY, VALUE_DESTRUCTION_PATHOLOGIES) -- Phase A complete

**Open questions:**
- Trust Score aggregation: weighted mean (v1 lean) vs PageRank (v2). See `SYNC_Trust_Mechanics.md` OQ1.
- Personhood Ladder: need Nicolas's "Daughters (T7 Autonomy)" document
- assess_agent() frequency: daily batch with on-demand (lean). See `SYNC_Trust_Mechanics.md` OQ3.
- L3 trust vs L1 trust relationship. See `SYNC_Trust_Mechanics.md` OQ5.

---

### Force 5 — L1 Physics Wiring & Production Cutover (Instance 5)
**Repos:** mind-mcp
**Agent subtype:** groundwork

| # | Task | Status | Details |
|---|------|--------|---------|
| 5.1 | Wire physics to orchestrator | DONE | Dispatcher has per-citizen L1 engines, stimulus injection, physics ticks, feedback loop. `stimulus_router.py`, `wm_prompt_serializer.py`, `feedback_injector.py` created + tested. |
| 5.2 | Real embeddings (text-embedding-3-small) | DONE | Activated in .env, 1536 dims |
| 5.3 | Seed brain for 44 citizens | DONE | 209 nodes, 399 links (11 types). Seeder reads profile.json + CLAUDE.md |
| 5.4 | FalkorDB persistence | DONE | `falkordb_checkpointer.py` — hybrid persistence with dirty tracking, periodic flush, load-on-boot. |
| 5.5 | Orientation taxonomy (Law 11) | DONE | Define qualitative orientations: take_care / create / verify / explore / rest / escalate. Map to prompt instructions. |
| 5.6 | Emotion calibration formulas | DONE | Anxiety, satisfaction, frustration — all in constants.py + tick_runner |
| 5.7 | Graph isolation strategy | DONE | One graph per citizen `brain_{handle}`, decided and in code |
| 5.8 | Copy citizen dirs from manemus | DONE | 245 citizens in `citizens/`, keys in `.keys/{handle}/` |
| 5.9 | Phase 7: Deploy to Render | TODO | Dockerfile ready. render.yaml ready. Parallel run with manemus. |
| 5.10 | Phase 7: DNS cutover | TODO | Switch DNS from manemus to mind-mcp. Bot migration. |
| 5.11 | Phase 7: Parallel validation | TODO | Both systems running. Compare outputs. Verify no regression. |

**Docs created:** `docs/l1_wiring/` (6 files: OBJECTIVES, PATTERNS, ALGORITHM, BEHAVIORS, IMPLEMENTATION, SYNC)

**L1 engine PORTED:** 5,230 lines copied from manemus to `runtime/cognition/`, 37/37 tests passing. Integration complete: dispatcher wired, stimulus router, WM serializer, feedback injector, FalkorDB checkpointer.

**Decisions made (in docs):**
- Start with slow_tick (60s), adaptive tick modes (slow/normal/fast/minimal)
- One FalkorDB graph per citizen (`brain_{handle}`), not shared
- Hybrid persistence: in-memory physics + periodic FalkorDB checkpoint
- Same 209-node base + per-citizen overlay for brain seeding
- text-embedding-3-small (1536 dims, matches schema) not 3-large
- Orientation as soft prompt modifiers, not hard constraints

**Open questions (remaining):**
- Budget: how many Claude accounts for 44 citizens? Current round-robin across a/b/c.
- manemus decommission timeline?
- WM token budget: 1200 tokens or less?

---

### Cross-Cutting Concerns

| # | Concern | Forces | Notes |
|---|---------|--------|-------|
| X.1 | Schema v2.0 → v2.1 | F1, F4 | Add HAS_ACCESS link, universe-level fields. May need migration. |
| X.2 | L4 Registry | F2, F1 | Anti-Sybil needs L4 lookup. Universe identity needs L4 registration. |
| X.3 | Test coverage | ALL | Every force includes tests. No "built but untested." |
| X.4 | Doc chains | ALL | Each force creates/updates module doc chain (8 files). |
| X.5 | SYNC updates | ALL | Each force updates this SYNC after significant changes. |

---

### Codebase Inventory (from exploration agents, 2026-03-13)

**Physics engine (mind-mcp):** 11.7k lines core + 6.7k graph ops + 4k health checks. BUT this is the v1.x SubEntity model — NOT the 21-law L1 model in schema v2.0. Gap between code and schema is Force 5's main work.

**Economy docs (mind-protocol):** Token module DEPLOYED to Solana devnet (61 tests, 7 modules). Storage tax, UBC, bonds, cascade utility all have FULL doc chains with pseudocode but NO implementation code. New NotebookLM formulas (degressive pricing, anti-Sybil 5%, bilateral vases communicants) need to be ADDED to existing docs.

**Citizens docs:** human_ai_pairing (8 docs), parenthood_network (8 docs) in mind-mcp. ai_citizen_partner (7 docs) in mind-platform with 4 CRITICAL BLOCKERS: (1) UBC distribution doesn't exist, (2) AI system prompt template doesn't exist, (3) personality schema doesn't exist, (4) autonomy permission framework doesn't exist.

**Embeddings:** 668 lines — OpenAI adapter exists at `runtime/infrastructure/embeddings/`. Traversal uses embedding similarity.

**Schema:** v2.0 in mind-mcp (793 lines, comprehensive). v1.9.1 in mind-protocol L4 (257 lines, universal). V2.0 extends v1.9.1 with cognitive types, drives, working memory.

---

### Execution Order

```
PHASE A — Documentation (all forces parallel)
  F1: docs/universe/ (OBJECTIVES → ALGORITHM)
  F2: docs/economy/metabolic/ (ALGORITHM_Metabolic_Economy.md)
  F3: docs/human_integration/ or extend docs/citizens/human_ai_pairing/
  F4: docs/trust_mechanics/ + value_creation_taxonomy.md
  F5: docs/l1_wiring/ (ALGORITHM for orchestrator integration)

PHASE B — Cross-review
  F1 ↔ F2 (economy needs universe graph)
  F3 ↔ F4 (partner model needs trust)
  F4 ↔ F5 (trust needs physics)

PHASE C — Planning
  Each force: IMPLEMENTATION.md with file-level plan
  Identify shared interfaces

PHASE D — Implementation (parallel)
  F5 first (unblocks everything): physics wiring + persistence
  F1 next: universe graph in FalkorDB
  F2 parallel: economy formulas + settlement
  F3 parallel: ingestion pipelines
  F4 parallel: trust engine + taxonomy
```

---

## HANDOFF: FOR AGENTS

**Agent subtype:** architect (design phase) → groundwork (implementation phase)

**Current focus:** 5-force parallel architecture sprint. See MASTER TODO above.

**Key context:**
- Citizens use Claude Code subprocess (`claude --print`), NEVER direct API. API is degraded fallback only.
- Tick speed is budget-driven (ComputeBudget), not fixed sleep interval.
- Trust-based compute: sqrt scaling, higher trust = more ticks.
- No cron — citizens set their own alarms via MCP tool.
- Account balancer round-robins across `~/.claude-accounts/{a,b,c}/`.
- Schema v2.0 (mind-mcp) already has: 7 cognitive types, 14 relation_kinds, 21 physics laws, 8 drives, working memory, link dimensions (trust/affinity/aversion/friction)
- Schema v1.9.1 (mind-protocol L4) is the universal canonical — L1 schema extends it, doesn't replace it

**Architecture:**
```
home_server.py (FastAPI)
├── runtime/citizens/        — identity, prompt building
├── runtime/orchestrator/    — dispatcher, invoker, budget, queue, sessions
├── runtime/bridges/         — telegram, whatsapp, voice
├── runtime/membrane/        — HTTP endpoint, stimulus, subscriptions
├── runtime/api/             — auth, chat, house, citizens, feed, dm, jwt, profiles, rate limiter
├── runtime/physics/         — graph operations, embeddings, health checks
├── mcp/server.py            — 10 MCP tools (stdio)
├── mcp/tools/               — handler files
└── docs/                    — citizens/, schema/, cognition/ doc chains
```

---

## HANDOFF: FOR HUMAN

**Executive summary:**
mind-mcp Phases 0-6 complete (37+ routes, 10 MCP tools). Schema v2.0 captures full L1 cognitive substrate. NotebookLM session validated 5 major workstreams now organized as a 5-force sprint: (1) universe graph architecture, (2) metabolic economy, (3) human partner model, (4) value/trust mechanics, (5) physics wiring + production cutover.

**What remains:**
- 5-force architecture sprint: documentation → review → planning → implementation
- Phase 7: Deploy to Render, parallel run, DNS cutover
- Copy citizen directories from manemus

---

## MODULE COVERAGE

| Module | Code | Status |
|--------|------|--------|
| MCP Server | `mcp/server.py`, `mcp/tools/` | CANONICAL |
| Home Server | `home_server.py` | CANONICAL |
| Citizens | `runtime/citizens/` | CANONICAL |
| Orchestrator | `runtime/orchestrator/` (7 files) | CANONICAL |
| Bridges | `runtime/bridges/` (4 files) | CANONICAL |
| Alarms | `mcp/tools/alarm_handler.py`, `runtime/orchestrator/alarm_watcher.py` | CANONICAL |
| Membrane | `runtime/membrane/http_endpoint.py` | CANONICAL |
| User API | `runtime/api/` (10 files: jwt, profiles, rate limit, auth, chat, house, citizens, feed, dm) | CANONICAL |
| Physics | `runtime/physics/` | CANONICAL (pre-existing) |
| Human-AI Pairing | `docs/citizens/human_ai_pairing/` (8 docs) | DESIGNING (proposed) |
| Parenthood Network | `docs/citizens/parenthood_network/` (8 docs) | DESIGNING (proposed) |
| Human Integration | `docs/human_integration/` (6 docs) | DESIGNING (proposed) |
| Metabolic Economy | `docs/economy/metabolic/` (3 docs: ALGORITHM, PATTERNS, VALIDATION) | DESIGNING (proposed) |

## Init: 2026-03-13 17:35

| Setting | Value |
|---------|-------|
| Version | v0.0.0 |
| Database | falkordb |
| Graph | mind_mcp |

**Steps completed:** ecosystem, capabilities, runtime, ai_configs, skills, database_config, database_setup, file_ingest, capabilities_graph, env_example, mcp_config, gitignore, overview, embeddings, health_checks

---
