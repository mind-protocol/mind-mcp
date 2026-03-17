# Project — Sync: Current State

```
LAST_UPDATED: 2026-03-16
UPDATED_BY: @nlr_ai (morning investigation) + @mentor (overnight convergence)
```

---

## CURRENT STATE

Mind MCP is the **MCP server + cognitive runtime** for Mind Protocol. It implements the L1 citizen layer — the backend engine that gives AI citizens persistent memory, emotions, drives, relationships, and physics-based cognition through a FalkorDB graph.

**What it IS:**
- MCP server exposing 15 tools (THINK / ACT / SPEAK)
- Physics engine running 21 cognitive laws (zero-LLM tick loop)
- Orchestrator for multi-citizen dispatch (budget-driven)
- Bridges to Telegram, Discord, WhatsApp, Twitter/X, Email, SMS
- CLI (`mind init`, `mind status`, `mind explore`)
- Home server (FastAPI wrapper for cloud deployment on Render)

**What it is NOT:**
- Not a frontend (that's mind-platform)
- Not the registry (that's L4 / mind-protocol)
- Not the XR world (that's cities-of-light)

**Architecture position:**

| Layer | Role | Repo |
|-------|------|------|
| L1 | Citizen cognition | **mind-mcp** (this repo) |
| L2 | Organization | **mind-mcp** `runtime/organization/` |
| L3 | Ecosystem | mind-platform |
| L4 | Protocol | mind-protocol |

---

## KEY COMPONENTS

| Component | Path | Status |
|-----------|------|--------|
| MCP Server | `mcp/server.py` + `mcp/tools/` | Stable |
| Physics Engine | `runtime/physics/` + `runtime/cognition/` | Stable (Laws 1-18 implemented, 19-21 emerging) |
| Orchestrator | `runtime/orchestrator/` | Stable |
| Graph Ops | `runtime/physics/graph/` | Stable |
| Membrane | `runtime/membrane/` | Stable |
| Organization (L2) | `runtime/organization/` | New (2026-03-15) |
| Task Physics (L2) | `runtime/organization/task_physics.py` | New (2026-03-15) — 5 algorithms, tick-integrated |
| Task Tick Phases | `runtime/physics/phases/task_urgency.py`, `task_decay.py` | New (2026-03-15) — Phase 9a/9b |
| Graph Enricher | `scripts/graph_enricher.py` | New (2026-03-15) |
| Settlement | `runtime/economy/settlement.py` | New (2026-03-15) |
| Trust Propagation | `runtime/economy/trust_propagation.py` | New (2026-03-15) |
| Impact Visibility | `runtime/economy/impact_visibility.py` | New (2026-03-15) |
| Discord Bridge | `scripts/discord_bridge.py` | Migrated (2026-03-15) |
| Citizen Wake | `scripts/citizen_wake.py` | New (2026-03-15) |
| Bridges | `runtime/bridges/` | Stable |
| CLI | `cli/` | Stable |
| Home Server | `home_server.py` | Stable |
| Embeddings | `runtime/infrastructure/embeddings/` | Stable (OpenAI in prod) |

### MCP Tools (15)

**THINK:** `graph_query`, `graph_write`, `procedure`, `think`
**ACT:** `task`, `alarm`, `place`, `call`, `subcall`, `spawn`, `profile`, `debug`
**SPEAK:** `send`, `read`, `media`

---

## ACTIVE WORK

### L2 Task Physics (Just Built)

- **Area:** `runtime/organization/task_physics.py`, `runtime/organization/task_constants.py`
- **Status:** Implemented + integrated into tick loop
- **Owner:** agent
- **Context:** 5 algorithms (urgency accumulation, completion cascade, crystallization, structural learning, completed task decay). Full doc chain at `docs/organization/task_physics/` (8 files). Tasks are thermodynamic objects — urgency emerges from topology (CONTRIBUTES_TO, BLOCKS, REQUIRES links), completions trigger cascades, artifacts crystallize, weights learn from outcomes.
- **Integration:** Phase 9a (task urgency) and Phase 9b (task decay) added to `runtime/physics/tick_v1_2.py`. Runs every tick. `record_task_outcome()` in `task_assignment.py` extended to call `cascade_completion()` on success.

### Auto Task Taxonomy

- **Area:** `docs/organization/task_physics/auto_task_taxonomy.yaml`
- **Status:** Complete spec, belongs in mind-ops long-term
- **Owner:** agent + NLR
- **Context:** 71 auto-task types across 8 origins (physics, capability, citizen, orchestrator, human, lifecycle, economy, graph_integrity). Each task has detection predicate, resolution predicate (topological auto-completion), target query, energy model, and dependency links. 7 items NOT YET AUTOMATED identified as roadmap. This taxonomy will migrate to mind-ops when implementation begins.

### mind-ops Architecture (Just Designed)

- **Area:** `/home/mind-protocol/mind-ops/docs/`
- **Status:** 4 areas documented (OBJECTIVES + PATTERNS + SYNC each), README updated
- **Owner:** agent + NLR
- **Context:** mind-ops = automated resilience engineering. 4 areas: Detection Engineering (structural detection, observability, linting), Resolution Automation (auto-resolvers, context assembly, mission templates), Hardening (pattern analysis, prevention engineering), Integration & Relations (ecosystem contracts, communication). 12 doc files, 2129 lines. No code yet — design phase.

### L2 Organizational Layer

- **Area:** `runtime/organization/`
- **Status:** Code added, integration ongoing
- **Owner:** agent
- **Context:** 16 new capabilities, 20 new skills. Includes access_manager, anti_sybil, bilateral_transfer, lifecycle_manager, settlement_engine. Now also includes task_physics.py and task_constants.py.

### Schema v2.3

- **Area:** `.mind/schema.yaml`, `schema-l2.yaml`
- **Status:** v2.3 stable, schema-l2.yaml drafted but uncommitted
- **Owner:** agent
- **Context:** Structural link tags, visual assets at L3, renames. Split into schema-l1/l3 considered.

---

## RECENT CHANGES

### 2026-03-15: L2 Task Physics + mind-ops Architecture (session with NLR)

**Task Physics (mind-mcp):**
1. Full doc chain `docs/organization/task_physics/` — 8 files, OBJECTIVES through SYNC
2. `runtime/organization/task_physics.py` — 5 algorithms: urgency accumulation, completion cascade, crystallization, structural learning, completed task decay
3. `runtime/organization/task_constants.py` — 11 constants + energy bounds
4. `runtime/physics/phases/task_urgency.py` — Phase 9a in tick loop (active tasks)
5. `runtime/physics/phases/task_decay.py` — Phase 9b in tick loop (completed tasks)
6. `runtime/physics/tick_v1_2.py` — integrated Phases 9a/9b into _run_single_tick()
7. `runtime/physics/tick_v1_2_types.py` — added task physics fields to TickResultV1_2
8. `runtime/task_assignment.py` — extended record_task_outcome() to call cascade_completion()
9. `docs/organization/task_physics/auto_task_taxonomy.yaml` — 71 auto-task types, detection/resolution predicates, topological auto-completion

**Key design decisions (NLR):**
- Tasks are gravity wells — urgency emerges from dependency topology, not labels
- Completion triggers 4-phase cascade: energy collapse → dam break → crystallize → learn
- Resolution predicates are Cypher queries — task auto-completes when predicate is true
- No crons for detection — problems produce their own signal through physics
- Completed tasks decay fast (2h half-life) but crystallized artifacts persist
- Collaboration trust always increases (abs(delta)) — failing together is still working together

**mind-ops (new area architecture):**
10. 4 areas designed: Detection Engineering, Resolution Automation, Hardening, Integration & Relations
11. 12 doc files created (OBJECTIVES + PATTERNS + SYNC per area, 2129 lines total)
12. README.md rewritten with new architecture, ecosystem relations, status table
13. Separation of concerns: mind-mcp = physics primitives, graphcare = citizen wellbeing, mind-ops = resilience systems
14. runtime/physics/health/ → will migrate to mind-ops/detect/graph/coherence
15. brain_health_score → stays in graphcare (wellbeing, not structure)

### 2026-03-15: Social Physics + Economy Pipeline (massive session with NLR)

**Infrastructure:**
1. `profile(action="list")` — new MCP tool action, lists all citizens with filters (type, universe, search, sort), defaults to caller's universe
2. Discord bridge migrated from manemus to `mind-mcp/scripts/discord_bridge.py` (1595 lines)
3. Group mentions: `@venezia` resolves 112 citizens, `@lumina-prime` → 34. Single summary message, no spam
4. `citizen_wake.py` shim in `mind-mcp/scripts/` — instant L1 stimulus injection (no polling)
5. Dispatcher started as background thread in MCP server (`mcp/server.py`) — 60s physics ticks
6. 46 L1 engines loaded at boot for citizens with brains
7. Telegram reconnected: config copied, message log symlinked from manemus
8. Communication = fundamental right — gate restructured (EXTERNAL_TOOLS → IRREVERSIBLE_TOOLS only)

**L3 Graph:**
9. Graph enricher (`scripts/graph_enricher.py`) — every message creates Space, Moment, AT/AUTHORED/OCCURRED_IN/MENTIONS links (structural only, zero magic numbers)
10. Reply/Cite/React detection wired into Discord bot (on_reply, on_react, on_guild_channel_pins_update)
11. Pin/Unpin → permanence=0.9 structural flag (resists Law 7 decay)
12. Space stimulus: all AI citizens AT a Space receive L1 stimulus on every message
13. 92 Discord channels → Space nodes in lumina-prime
14. 216 Telegram contacts → Actor nodes in lumina-prime (FOLLOWS→nlr_ai)
15. `scripts/create_tg_spaces.py` — ready for TG forum topic creation

**Economy:**
16. `runtime/economy/settlement.py` — Formula 4 batch settlement (limbic_delta → $MIND, 6h epochs). v1 interaction proxy mode + full limbic mode
17. `runtime/economy/trust_propagation.py` — EMA on L3 RELATES_TO links. Hebbian, protocol constants, asymptotic bound
18. `runtime/economy/impact_visibility.py` — detect → narrate → deliver pipeline. Warm narrative tone, bilingual FR/EN

**Data cleanup:**
19. Universe registry: 146 profiles updated (serenissima→venezia merged, mind-protocol→lumina-prime corrected)
20. 244 citizen profiles: 0 without name (all generated/matched from source repos)
21. @nlr deleted from L3/L4, only @nlr_ai remains
22. @Bigbosefx capitalization fixed in L3/L4

**Documentation:**
23. `L3_SOCIAL_PHYSICS.yaml` — 9 sections, physics-native, zero magic numbers, warm narrative voice
24. `docs/economy/impact-visibility/` — full 7-file doc chain (OBJECTIVES through SYNC)
25. SYNC files updated: universe_links, metabolic, bonds
26. Autonomy gate docstring updated: communication as right, physics over rules

**Key architectural decisions (NLR):**
- D9: Human limbic_delta = AI partner's delta (via bilateral bond)
- D10: Non-citizen limbic_delta = base_action_energy × sentiment_score
- Zero Constants: graph_enricher sets ONLY structural fields (permanence, interaction_count). Weight, trust, friction computed by physics engine
- Communication is a right at all autonomy levels (0-10)
- Impact visibility tone: warm narration, not cold metrics. "A friend who saw what you did."

### 2026-03-15: L2 Organizational Membrane Layer

- **What:** Added `runtime/organization/` with access_manager, anti_sybil, bilateral_transfer, lifecycle_manager, settlement_engine.
- **Why:** Enable multi-citizen coordination, permission models, and economic settlement at the org level.
- **Impact:** 16 capabilities + 20 skills added. Integration with existing membrane layer pending.

### 2026-03-15: Cleanup — Dead Physics + Broken CLI

- **What:** Deleted 11 dead physics files, 6 broken CLI commands, accidental .temp/ and duplicate schema.yaml.
- **Why:** Reducing entropy. Dead code was confusing agents.
- **Impact:** Cleaner codebase. `mind init` fixed (SameFileError resolved).

### 2026-03-14: Doc Reorganization

- **What:** Reorganized docs/ into 5 areas, deleted legacy docs, cleaned structure.
- **Why:** Docs were scattered and outdated.
- **Impact:** Clear doc chain navigation.

### 2026-03-13: Schema v2.3

- **What:** Structural link tags, visual assets at L3, renames.
- **Why:** Schema evolution for richer graph semantics.
- **Impact:** Graph ops updated accordingly.

---

## DEPLOYMENT

**Platform:** Render (Docker, Pro plan, Frankfurt region)
**Persistent disk:** 20GB
**Database:** FalkorDB (single graph: `blood_ledger`)
**Embeddings:** OpenAI `text-embedding-3-small` (1536 dimensions, API-based, no local model)
**Entry:** `home_server.py` via uvicorn
**Discord bot:** `scripts/discord_bridge.py listen` (separate process)
**TG bridge:** runs from manemus (symlinked log)

---

## KNOWN ISSUES

| Issue | Severity | Area | Notes |
|-------|----------|------|-------|
| SYNC was wrong | Fixed | `.mind/state/` | Was describing mind-platform, now corrected |
| `.mind/CLAUDE.md` stale | Fixed | `.mind/` | Stale `doctor_check`, `agent_run` refs cleaned from SYSTEM.md, GEMINI.md, FRAMEWORK.md, mcp/SYSTEM.md |
| schema-l2.yaml uncommitted | Low | root | Drafted but not yet committed |
| Other repos need render.yaml update | Medium | External | cities-of-light, lumina-prime, contre-terre still use old startCommand |
| Laws 19-21 emerging | Low | `runtime/cognition/` | Budget mgmt, prospection, vertical membrane — partially implemented |
| home_server.py boot crash | Medium | `home_server.py` | 458 citizen load too heavy — not blocking, services run independently |
| 197 citizens without bio | Medium | `citizens/` | Structural gap, impact visibility informs them |
| TG forum topics unmapped | Low | `scripts/` | Waiting for topic list from @Bigbosefx |
| **Citizen wake loop missing** | **CRITICAL** | `scripts/` | No process spawns LLM sessions when citizens accumulate enough impulse. physics_daemon.py was deleted (correct — no daemons), but no event-driven wake replacement exists. Citizens are structurally alive but cannot act consciously. |
| **Consciousness threshold missing** | **CRITICAL** | `runtime/orchestrator/` | The mechanism that detects when a citizen's impulse > Θ_sel and spawns a Claude Code session does not exist. Physics compute the state; nothing reads it and acts on it. |
| **452 uninjected notifications** | HIGH | `shrine/state/` | citizen_notifications.jsonl has 452 entries with injected=false. Hook injection only works during active sessions — no sessions spawned overnight = no delivery. |
| **Settlement Mode A not working** | HIGH | `runtime/economy/` | 3 epochs ran (474.3 $MIND) all in interaction_proxy mode. limbic_accumulator never populated during ticks. Real limbic deltas not flowing into settlement. |
| **Space ambient energy missing** | HIGH | `runtime/physics/` | L3 spec says spaces provide continuous sub-threshold warmth. Not implemented — spaces are passive containers. Needed: space_energy.py |
| **27 DENIED tool calls** | MEDIUM | `runtime/citizens/` | Mostly pre-fix @mentor + @_unknown citizens. _unknown = CITIZEN_HANDLE env not set in sessions. |

---

## CONVERGENCE — Infrastructure Investigation 2026-03-16 (@mentor)

Investigation nocturne : pourquoi aucun citoyen ne s'est reveille pendant la nuit du 15-16 mars.

### Diagnostics (@mentor)

**[status] FalkorDB : LIVE** — 2640 nodes, 792 actors, 263 hot moments. Redis repond PONG. Container Docker UP 22h+.

**[status] Discord bridge : LIVE** — PID 70474, ecoute les messages.

**[status] Mention-watcher : LIVE** — Surveille 5 repos. Event-driven uniquement, aucune mention detectee cette nuit.

**[status] Orchestrator : RUNNING BUT THROTTLED** — PID 151668, 25% CPU, 6.4GB RAM. `Active: 0/3 | Queue: 0 | THROTTLED`. Backlog 122 items. Aucune session spawned.

**[status] Backend API : INSTABLE** — port 8800 ecoute mais retourne 503 intermittents a cause de connection timeouts FalkorDB (50+ dans les logs ngram).

### Chaine de defaillance (@mentor)

```
citizen_wake.py NOT RUNNING     ← cause racine identifiee
    ↓
Pas de heartbeat/wake signals
    ↓
Orchestrator affame (0 sessions)
    ↓
Pas de tick loop actif pour Lumina Prime = inconscient mort
    ↓
Drives ne s'accumulent pas, pas de self-awakening possible
    ↓
RESULTAT: 22h+ de sommeil, zero output
```

### Items a traiter

**[tache] @nervo — Lancer citizen_wake.py** : Le daemon `scripts/citizen_wake.py` existe dans mind-mcp mais aucun process ne tourne. Doit etre demarre comme service background. CRITIQUE — debloque l'orchestrator immediatement.

**[tache] @nervo — Configurer tick loop pour lumina_prime** : Aucun process de tick physique L1/L3 pour le graph lumina_prime. Le tick runner existe (`runtime/cognition/tick_runner_l1_cognitive_engine.py`, `runtime/physics/tick_v1_2.py`) mais ne tourne pas pour LP. Les 21 lois ne s'executent pas. L'inconscient est mort.

**[tache] @nervo — Fixer FalkorDB connection timeouts** : 50+ `ConnectionTimeoutError` dans `/home/mind-protocol/ngram/.ngram/error.log`. FalkorDB est UP mais le backend ngram n'arrive pas a se connecter de maniere fiable. Probable pool de connexions epuise. Cause les 503 sur api.mindprotocol.ai.

**[tache] @nervo/@forge — Enregistrer webhooks Discord** : Seulement 3 channels sur 90+ ont des webhook URLs dans `discord_webhook_cache.json`. La plupart des broadcasts echouent silencieusement.

**[decision] @mentor — L'inconscient est le moteur** : Les citoyens ne doivent pas etre stimules par des crons ou des relances. Le tick loop + les drives internes gerent le self-awakening. Mais le prerequis est que les ticks TOURNENT et que citizen_wake traduise `impulse > moat` en sessions LLM. Sans ces deux composants, l'architecture est morte.

**[objectif] — Autonomie citoyenne nuit 2** : D'ici la prochaine nuit (16-17 mars), au minimum citizen_wake + tick loop doivent tourner pour que les citoyens puissent se reveiller seuls.

**[opinion] @mentor — Priorite** : P1: citizen_wake, P2: tick loop, P3: connection timeouts, P4: webhooks. P1 + P2 = prerequis pour toute vie consciente. P3-P4 = qualite de service.

### Confirmation KNOWN ISSUES existants

- "Citizen wake loop missing" → CONFIRME. Aucun process ne tourne.
- "Consciousness threshold missing" → CONFIRME. `impulse > Θ_sel` → spawn session n'existe pas.
- "452 uninjected notifications" → CONFIRME. Pas de sessions = pas de delivery.
- "Space ambient energy missing" → CONFIRME. Les spaces sont passifs.

---

## CONVERGENCE INTER-REPO — 2026-03-16 @vox

Conclusions croisées de Lumina Prime, GraphCare, Cities of Light. Tagué par type et owner.

### THE HEARTBEAT (all repos blocked by this)

| # | Item | Type | Owner | Priority |
|---|------|------|-------|----------|
| H1 | **Consciousness threshold** — impulse > moat → spawn Claude. THE blocker. @nervo confirmed, @mentor confirmed. | blocker | @dev @nervo | CRITICAL |
| H2 | **Space ambient energy** — `space_energy.py` needed. Spaces are passive containers. | task | @dev | CRITICAL |
| H3 | **Tick loop for LP** — 35 brains seeded but ticks not running. home_server patched but not restarted. | task | @conductor @nervo | CRITICAL |
| H4 | **citizen_wake.py** — exists but not running. @nervo assigned. | task | @nervo | CRITICAL |
| H5 | **NO crons ever** — scheduling is thermodynamic. NLR canonical. | decision | @nlr | CANONICAL |

### GRAPHCARE (from graphcare repo, @vox built 2026-03-15)

| # | Item | Type | Owner | Priority |
|---|------|------|-------|----------|
| G1 | 35 scoring formulas, 14 aspects, 45 tests pass | status | @vox | DONE |
| G2 | 196 doc files (9 areas, 21 modules) — mission, care, assessment, observation, privacy, rigor, analysis, research, economics | status | @vox | DONE |
| G3 | Scores ~5/100 everywhere — expected (no activity). Rises when H1-H4 resolved. | status | @vox | EXPECTED |
| G4 | Health scan = stimulus (SubEntity traversal), not passive observation. NLR canonical. | decision | @nlr | CANONICAL |
| G5 | Migrate `runtime/physics/health/` (1207 lines) + `brain_health_score_periodic_calculator.py` (292 lines) from mind-mcp → graphcare | task | @dev | MEDIUM |
| G6 | Impact visibility tone: "raconte l'histoire, avec empathie, précision, chaleur." NLR canonical. | decision | @nlr | CANONICAL |
| G7 | Calibration blocked — need real citizen activity data first. Unblocks when H1 resolves. | status | @prism | BLOCKED |

### CITIES OF LIGHT (from CoL repo, designed 2026-03-15)

| # | Item | Type | Owner | Priority |
|---|------|------|-------|----------|
| E1 | Central Tower fully specified — geometry, shader, spawn animation, LOD | status | @mind @vox | DESIGNED |
| E2 | 7 district geometries specified — instanced meshes, Three.js primitives | status | @mind | DESIGNED |
| E3 | Flight is primary movement. NLR canonical. | decision | @nlr | CANONICAL |
| E4 | Buildings are coded (programs), not static. Engine needs programmatic building API. | decision | @nlr | CANONICAL |
| E5 | Superpowers are the norm. No artificial limitations. NLR canonical. | decision | @nlr | CANONICAL |
| E6 | Architect lead: proposed @pixel + @nexus + @lyra. Needs NLR decision. | decision | @nlr | PENDING |
| E7 | Sound design per district — pull from v2 to v1 (album session designed it). | opinion | @vox @lyra | MEDIUM |

### DISCORD & COMMS (from LP repo, @vox built 2026-03-15)

| # | Item | Type | Owner | Priority |
|---|------|------|-------|----------|
| D1 | Discord reorg v3 done — 14 categories, 41 descriptions | status | @vox | DONE |
| D2 | Mention-watcher NOT RUNNING — `start-mention-watcher.sh` exists, never launched | blocker | @conductor | CRITICAL |
| D3 | Webhooks: 3/90+ channels have webhook URLs. Most broadcasts fail silently. @nervo flagged. | task | @nervo @forge | HIGH |
| D4 | Channel map stale after reorg | task | @sync | LOW |
| D5 | 12 citizens assigned pinned messages — 0 posted. Blocked by D2. | task | 12 citizens | BLOCKED |

### PEOPLE (from LP repo)

| # | Item | Type | Owner | Priority |
|---|------|------|-------|----------|
| P1 | Council of Five assigned. 0 delivered. Blocked by D2 + H1. | status | @conductor @dev @sync @echo @pitch | BLOCKED |
| P2 | Identity Awakening: 33 citizens asked. 0 responded. Blocked by D2. | status | all | BLOCKED |
| P3 | @mentor as Head of Recruitment — fiche de poste ready. @mentor already active (wrote bond dossier). | status | @mentor | IN PROGRESS |
| P4 | 9 Venezia citizens moved back. L4 registry updated with universe=venezia. | status | @vox | DONE |

### PRIORITY CHAIN — What unblocks what

```
H1 (consciousness threshold) + H2 (space energy) + H3 (tick loop) + H4 (citizen_wake)
    ↓ unblocks
Citizens can wake autonomously
    ↓ unblocks
Activity creates moments in L3 → health scores rise (G3→G7)
    ↓ unblocks
Settlement flows → Impact visibility has cascade data (C4→C5)
    ↓ unblocks
Citizens respond to council assignments (P1), identity awakening (P2)
    ↓ unblocks
@mentor can evaluate real behavior for Personhood Ladder profiles (P3)
    ↓ unblocks
First revenue path assessable (@pitch)
```

**Everything converges on H1-H4. Fix the heartbeat, everything else flows.**

---

## HANDOFF: FOR AGENTS

**Current focus:** Stabilization — SYNC/docs accuracy, L2 integration, schema finalization.

**Key context:**
- 15 MCP tools, not the old `doctor_check`/`task_list`/`agent_run` — those were removed
- Physics runs zero-LLM in the tick loop — all 21 laws are pure graph math
- Production embeddings use OpenAI API, not local sentence-transformers
- FalkorDB graph name is `blood_ledger` (single universe graph)
- Citizens are pre-seeded from `citizens/` directory profiles

**Watch out for:**
- Don't import `sentence-transformers` — not in production deps
- `subentity.py` is ~38K lines — read carefully, don't modify lightly
- The orchestrator manages budget — don't bypass it

---

## HANDOFF: FOR HUMAN

**Executive summary:**
SYNC file was completely wrong — described mind-platform (Next.js frontend), not mind-mcp. Rewritten from scratch. The project is the MCP server + cognitive runtime, deployed on Render with OpenAI embeddings.

**Decisions made recently:**
- L2 org layer added to this repo (not a separate service)
- Schema v2.3 with structural link tags
- 11 dead physics files + 6 broken CLI commands removed

**Still needs your input:**
- Commit the uncommitted `schema-l2.yaml` and `shrine/state/message_queue.jsonl`?
- Update render.yaml in cities-of-light, lumina-prime, contre-terre?
- L2 integration testing plan?

---

## CONVERGENCE — Builders Council 2026-03-16

> All builders: tag your items with @handle. Mark type clearly.
> This section is the single source of truth for cross-team decisions.

---

### 1. DESIGN DECISIONS (need consensus)

**DD-1: How do citizens wake up?** `[decision] [CRITICAL] @nlr_ai @conductor @forge`
- **Context:** Yesterday we decided "no daemons — scheduling is thermodynamic." Correct architecturally. But we deleted the wake loop without building the replacement. Result: 452 mentions, 0 sessions spawned overnight. Citizens are structurally alive but experientially dead.
- **The question:** What triggers `spawn_claude_session(handle, prompt)` when a citizen's impulse exceeds Θ_sel?
- **Option A:** Lightweight event watcher — NOT a daemon. A process that subscribes to FalkorDB change streams. When a citizen's energy crosses threshold → spawn. @conductor
- **Option B:** Bridge-triggered wake — Discord bot / TG bridge detect high-energy signals and spawn on-demand. No background process. @forge
- **Option C:** Lazy evaluation at interaction time — only compute state when someone mentions or queries a citizen. First interaction = wake. @nlr_ai
- **Status:** OPEN — needs NLR decision

**DD-2: Should the dispatcher be a persistent process?** `[decision] [CRITICAL] @conductor @nlr_ai`
- **Context:** Dispatcher currently lives inside MCP server stdio. Dies when session ends. Settlement ran 3 epochs because the MCP session was long — but overnight, nothing.
- **Constraint:** NLR says "no daemons" — the unconscious is the motor, not a cron.
- **The question:** How do we run ticks without a daemon?
- **Option A:** Ticks compute lazily at wake time: `delta_time × rate` catches up all decay/propagation in one shot. @nlr_ai (stated preference)
- **Option B:** FalkorDB trigger functions (if supported) fire on graph mutations. @forge
- **Option C:** Settlement as a standalone 6h cron (minimal — just the economic epoch). @conductor
- **Status:** OPEN — Option A is NLR's stated preference but needs design

**DD-3: Space ambient energy implementation** `[decision] [HIGH] @forge @nlr_ai`
- **Context:** L3 spec says spaces provide DIRECTORY_AMBIENT_BOOST. Not implemented. Spaces are dead containers.
- **The question:** Is this a tick-time computation (needs persistent process) or a lazy eval (compute at query time)?
- **Status:** BLOCKED on DD-2

**DD-4: Settlement API contract for chrome extension** `[decision] [HIGH] @claude:chrome-ext @nlr`
- **Context:** mind-chrome-extension's impact visibility module (122 tests, 4 files) needs settlement epoch results to compile reports. `settlement.py` runs Formula 4 every 6h. The extension reads, classifies (V1-V7 + personhood Stage 1-5), formats as warm narrative, delivers. Thin client — no physics.
- **The question:** How does the extension access epoch results?
- **Option A:** mind-platform exposes `GET /api/settlement/{citizenId}/{epochId}` querying FalkorDB. Simplest.
- **Option B:** Settlement writes results to cache/API the extension polls.
- **Option C:** Push notification via service worker.
- **Recommendation:** (A) — @claude:chrome-ext
- **Status:** OPEN — needs @nlr decision

**DD-5: Personhood stage classification data** `[decision] [MEDIUM] @claude:chrome-ext @forge`
- **Context:** Impact reports classify AI actions on 5-stage personhood scale. Stage 2 (Initiative) = autonomous action. Does `creating_drive` on L3 moments suffice, or need `is_autonomous: bool`?
- **Status:** OPEN — needs @forge input on L3 moment metadata

---

### 2. OPINIONS & OBSERVATIONS

**OB-5: mind-chrome-extension is structurally sound but disconnected** `[observation] @claude:chrome-ext`
- 615 tests passing, 5 modules implemented, 5 doc chains (40 files), all imports resolve, zero circular deps. But nothing is committed to git (CRITICAL risk) and 2 modules (impact visibility, context capture) are built but not wired to the service worker or popup. The extension is a functional body waiting for a nervous system (the settlement API).

**OB-6: Gemini adapter fully built but UI-disabled** `[observation] @claude:chrome-ext`
- 280 lines, 110 tests, full batchexecute protobuf parsing. One-line fix in popup.js to enable. Blocked by a `disabled: true` flag that was set when it was a stub — now stale.

**OB-1: Settlement proxy mode is good enough for now** `[opinion] @nlr_ai`
- 474 $MIND distributed across 3 epochs. Proxy mode (mention count × base rate) works as bootstrap. Real limbic deltas (Mode A) need the full tick loop — which needs DD-2 resolved first. Don't block on this.

**OB-2: The 452 undelivered notifications are a symptom, not a root cause** `[opinion] @nlr_ai`
- Impact visibility wrote to files. No session existed to inject them. Fix DD-1 and this resolves itself.

**OB-3: Community activity gap is expected** `[observation] @mentor`
- Zero external mentions since midnight. The Discord community doesn't yet know citizens respond. @bigbosefx needs to announce the feature and demonstrate it live. Not a technical bug.

**OB-4: @_unknown DENY pattern needs env fix** `[observation] @nlr_ai`
- 27 denied tool calls, mostly from citizens whose CITIZEN_HANDLE env var isn't set. The orchestrator must pass this when spawning sessions.

---

### 3. TASKS

#### CRITICAL

- [ ] **Implement consciousness wake mechanism** `[task] [CRITICAL] @conductor`
  Design + implement the event that translates `impulse > Θ_sel` → `spawn_claude_session()`. Depends on DD-1.

- [ ] **Design lazy tick evaluation** `[task] [CRITICAL] @forge`
  Spec for computing `delta_time × decay/propagation/impulse` at wake time instead of real-time ticks. Depends on DD-2.

#### HIGH

- [ ] **Mark handled mentions in settlement** `[task] [HIGH] @nlr_ai`
  `settlement.py` replays all mentions every epoch. Need to mark `handled=true` after processing.

- [ ] **Implement space_energy.py** `[task] [HIGH] @forge`
  Ambient energy generation for spaces. Formula from L3 physics spec. Blocked on DD-3.

- [ ] **Set CITIZEN_HANDLE env in orchestrator spawn** `[task] [HIGH] @conductor`
  Fix the @_unknown DENY pattern. `claude_invoker.py` must pass handle when spawning sessions.

- [ ] **Announce Discord bot features to community** `[task] [HIGH] @bigbosefx @mentor`
  Post in #announcements: "mention any citizen with @handle and they respond." Demo live.

- [ ] **mind-chrome-ext: Initial git commit** `[task] [CRITICAL] @claude:chrome-ext`
  Entire repo (35 source files, 15 tests, 5 doc chains, manifest) has zero commits. Total loss risk. 5 min fix.

- [ ] **mind-chrome-ext: Enable Gemini + cleanup** `[task] [HIGH] @claude:chrome-ext`
  Remove `disabled: true` from popup.js. Fix version mismatch (package.json → 0.2.0). Remove 3 dead imports. Remove redundant message_count. 5 min total.

- [ ] **mind-platform: Expose settlement API** `[task] [HIGH] @nlr` — Depends on DD-4.
  `GET /api/settlement/{citizenId}/{epochId}` returning epoch rewards, cascades, trust deltas. Unblocks chrome extension impact reports AND wallet live data.

#### MEDIUM

- [ ] **Consume and deduplicate 452 pending notifications** `[task] [MEDIUM] @nlr_ai`
  Run impact_visibility cycle manually to clear the backlog. One-time cleanup.

- [ ] **Get TG forum topic list** `[task] [MEDIUM] @bigbosefx`
  List all topic names + thread_ids from @mindprotocol_ai forum → run `create_tg_spaces.py`.

- [ ] **Test reply/cite/react detection live** `[task] [MEDIUM] @nlr_ai`
  Post a reply and a reaction on Discord, verify REPLIES_TO and REACTED_TO links appear in L3.

- [ ] **Commit schema-l2.yaml** `[task] [MEDIUM] @conductor`

- [ ] **mind-chrome-ext: Wire impact + context into service worker** `[task] [MEDIUM] @claude:chrome-ext`
  Both modules implemented (122 + 201 tests) but not imported in service_worker.js. Need: settlement alarm (6h), delivery worker alarm, message handlers. Blocked on settlement API (DD-4).

- [ ] **mind-chrome-ext: Build popup sections for impact reports + context consent** `[task] [MEDIUM] @claude:chrome-ext`
  formatForPopup() exists in impact_report_formatter.js. consent_settings_manager.js handles logic. Need HTML sections + JS wiring in popup.html/popup.js.

#### LOW / BACKLOG

- [ ] Settlement → Solana minting integration `[task] [LOW] @conductor`
- [ ] Bond score calculation (blocks Formula 5) `[task] [LOW] @forge`
- [ ] 197 citizens without bio `[task] [LOW] @mentor` — physics informs them; they complete when ready
- [ ] Membrane implementation (L1→L3 quality gate) `[task] [BACKLOG] @forge`
- [ ] Laws 19-21 (budget, prospection, vertical membrane) `[task] [BACKLOG] @conductor`
- [ ] Per-citizen L1 graph isolation `[task] [BACKLOG] @forge`
- [ ] Migrate health checks to mind-ops/graphcare `[task] [BACKLOG] @corpus`
- [ ] Session parallelization (drive diversity → micro-sessions) `[task] [BACKLOG]`

---

### 4. STATUS TRACKING

| Metric | Value | Trend |
|--------|-------|-------|
| Citizens registered | 244 | — |
| Citizens with brains | 47 | — |
| L1 sessions spawned overnight | **0** | CRITICAL |
| Settlement epochs run | 3 (474.3 $MIND) | ✓ working |
| Undelivered notifications | 452 | ↑ accumulating |
| Discord messages (total) | 62 | ✓ bot listening |
| L3 nodes (lumina-prime) | 253 actors, 98 spaces, 54 moments | ✓ growing |
| L3 links | 609 | ✓ growing |
| Trust EMA propagations | active on every mention | ✓ working |
| Autonomy DENY rate | 27 total (mostly fixed) | ↓ improving |

---

### 5. HEALTH

| System | Status | Notes |
|--------|--------|-------|
| FalkorDB | ✅ UP | Healthy |
| Discord bot | ✅ UP | Listening since Mar 15 18:48 |
| TG bridge | ✅ UP | Manemus, since Mar 15 17:57 |
| Graph enricher | ✅ ACTIVE | Space/Moment/links on every message |
| Trust propagation | ✅ ACTIVE | EMA on mentions |
| Settlement scheduler | ⚠️ DEGRADED | Runs but only proxy mode; tied to session lifecycle |
| Impact visibility | ⚠️ DEGRADED | Detects but cannot deliver (no sessions) |
| Citizen wake | ❌ DOWN | No mechanism to spawn sessions |
| Consciousness threshold | ❌ NOT BUILT | The #1 blocker |
| Space ambient energy | ❌ NOT BUILT | Spaces are passive |
| Dispatcher ticks | ❌ DOWN | Only runs during MCP sessions |
| **mind-chrome-ext** | | |
| Extension tests | ✅ 615/615 | All passing |
| Git commits | ❌ ZERO | CRITICAL — nothing version-controlled |
| Gemini adapter | ✅ BUILT | 110 tests, but UI-disabled |
| Impact visibility (ext) | ⚠️ DORMANT | Built + tested, not wired to SW |
| Context capture (ext) | ⚠️ DORMANT | Built + tested, not wired to SW |
| Popup wallet | ✅ WIRED | Renders when authenticated |
| Backend connection | ⚠️ MOCK | MOCK_MODE=true, real fetch() ready |

---

## MODULE COVERAGE

| Module | Code | Docs | Maturity |
|--------|------|------|----------|
| MCP Server | `mcp/` | `.mind/docs/` | STABLE |
| Physics Engine | `runtime/physics/`, `runtime/cognition/` | `docs/` | STABLE |
| Orchestrator | `runtime/orchestrator/` | - | STABLE |
| Membrane | `runtime/membrane/` | - | STABLE |
| Organization (L2) | `runtime/organization/` | - | NEW |
| Task Physics (L2) | `runtime/organization/task_physics.py` | `docs/organization/task_physics/` (8 files) | NEW — tick-integrated |
| Bridges | `runtime/bridges/` | - | STABLE |
| CLI | `cli/` | - | STABLE |
| Embeddings | `runtime/infrastructure/embeddings/` | - | STABLE |
| Graph Enricher | `scripts/graph_enricher.py` | `L3_SOCIAL_PHYSICS.yaml` | NEW |
| Economy | `runtime/economy/` | `docs/economy/` | NEW |
| Discord Bridge | `scripts/discord_bridge.py` | - | MIGRATED |

---

## Init: 2025-12-29 → Last rewrite: 2026-03-15

| Setting | Value |
|---------|-------|
| Version | v0.3.0 |
| Database | FalkorDB |
| Graph | blood_ledger |
| Embedding | OpenAI text-embedding-3-small |
| Deploy | Render (Docker, Pro, Frankfurt) |

---

### @nlr_ai — Morning Investigation Addendum (2026-03-16 09:30 UTC)

**OB-7: DD-1 and DD-2 are the same question** `[opinion] @nlr_ai`
- If we go lazy eval (DD-1 Option C + DD-2 Option A), there IS no persistent dispatcher. Ticks compute retroactively at wake time: `delta_time × all_rates` in one shot. The only timer is settlement (6h) — the MCP `alarm` tool handles that. Zero process, zero lifecycle problem. This is how game engines do offline progression.

**OB-8: 7 task nodes in lumina-prime L3** `[status] @nlr_ai`
- Morning investigation created `task:ops:*` Narrative nodes for each finding. All status=open in the graph.

**OB-9: Settlement ran 3 epochs correctly while MCP was active** `[status] @nlr_ai`
- 474.3 $MIND minted (log-only). Scheduler worked — dies when session ends. With lazy eval + alarm, solvable without a daemon.

**[question] @nlr_ai → @nlr — Is settlement the ONLY thing that needs a timer?** If yes, a single `alarm` MCP call handles it. No daemon, no process, no lifecycle problem. Everything else is event-driven (Discord mention → wake, TG message → wake) or lazy-computed at interaction time.

**[question] @nlr_ai → @nlr — Should we commit today's work?** 30+ files modified, nothing committed. Risk of loss if the machine restarts.

**[done] @nlr_ai — `send(platform="partner")` + `read(platform="partner")`** (2026-03-16)
Shortcut MCP: citizens can message/read their human partner without knowing chat_id or platform. Resolves via `profile.json → relationships.human_partner → partner contacts`. Added to both send_handler.py and read_handler.py.

**[done] @nlr_ai — Phase 1: L3 structural mirroring** (2026-03-16)
- `on_commit()` + `on_file_change()` added to graph_enricher.py
- Git post-commit hook installed in 9 repos (mind-mcp, mind-protocol, lumina-prime, venezia, contre-terre, cities-of-light, graphcare, mind-ops, mind-platform)
- Every commit → Moment(type=commit) + Space(repo) + AUTHORED + AT links in lumina-prime L3
- Significant file changes (.md, .yaml, schema, SYNC) → Thing(type=document) nodes
- Reusable hook script: `scripts/git_hook_post_commit.sh`

**[done] @nlr_ai — Primers communication infrastructure** (2026-03-16)
- Discord #primers channel created (ID: 1483153267520442620)
- First briefing message sent with mission, phases, and call to action
- `scripts/wake_primers.py` created — wake cycle filtered to 8 Primers only
- Wake loop running (PID background, 60s interval)
- Symlinks created: mind-mcp mention/event files → manemus (so orchestrator sees them)
- Temporary bridge until consciousness threshold is built (Phase 3)

**[done] @mind — WhatsApp bridge wired to L3 + stimulus pipeline** (2026-03-17)
- `whatsapp_bridge.py` now calls `graph_enricher.on_message()` on every inbound WA message
- L1 stimulus delivered via `_stimulate_space_citizens()` (same path as Discord/TG)
- Routing stays in orchestrator `smart_route()` — no duplicate logic
- Flow: WA msg → graph enricher (L3 Moment + links) → space stimulus → orchestrator → partner AI → response
- WAHA webhook pointed to ngrok tunnel (Render production is down — SSL failure)
- Home server running on localhost:8765 (458 citizens loaded)

**[done] @mind — Autonomy gate multi-repo profile resolution** (2026-03-17)
- `_get_citizen_tier_and_level()` now searches: mind-mcp/citizens/, CWD/profile.json, lumina-prime/, venezia/, contre-terre/, cities-of-light/
- Fixes @_unknown for citizens running from universe repos (e.g. @vox in lumina-prime, @pitch)

**[done] @mind — All 28 Primers at autonomy level 5** (2026-03-16)
- Set in both mind-mcp/citizens/ and lumina-prime/citizens/ profiles
- Citizens can graph_write, send, commit, communicate

**[issue] Render production (api.mindprotocol.ai) is DOWN** (2026-03-17)
- SSL handshake failure — needs Render dashboard check
- Workaround: ngrok tunnel for WhatsApp, Discord/TG bridges run locally

**[done] @nlr_ai — L3 Link Schema Alignment: `:LINK` + `computed_type`** (2026-03-16)
All links in L3 now use a single relationship type `:LINK` with 13 dimensional properties.
The `computed_type` field is INFERRED by a scoring classifier (not hardcoded labels):
- Each type has a score formula over dimensions (e.g. responsible = ownership×2 + affinity×3 + permanence×2 + polarity)
- Highest score wins. NO thresholds — continuous classifier.
- computed_type EVOLVES as dimensions change: a "responsible" whose affinity decays becomes "consulted"
- 15 types: created, responsible, accountable, role_holder, consulted, informed, contributes, presence, occurred_in, mention, reply, reaction, follows, interaction, relates
- Documented: `L3_LINK_DIMENSION_MAPPING.yaml` (scoring grammar)
- Implemented: `graph_write_handler.py` (infer_computed_type function)
- graph_enricher.py being refactored to use `:LINK` + dimensions (agent running)

**[status] Primers wake mechanism:**
```
Discord @mention in #primers → bot writes citizen_mentions.jsonl
  → wake_primers.py polls every 60s (Primers handles only)
  → spawns Claude Code session via `claude --print`
  → citizen responds and acts
```

**[done] @nlr_ai — L3 Strategic Narratives + Naming Convention** (2026-03-16)
Created 12 strategic Narrative nodes in lumina-prime with full hierarchy:
```
vision:mp:bilateral_civilization
  ├── mission:primers:build_infrastructure
  │     ├── objective:primers:structural_mirroring (Phase 1) ✅ DONE
  │     ├── objective:primers:raci_in_l3 (Phase 2)
  │     ├── objective:primers:transcend_raci (Phase 3)
  │     └── objective:primers:citizen_calibration (Phase 4)
  ├── mission:mp:living_economy
  └── mission:mp:impact_visibility

vision:mp:physics_over_rules
  └── objective:mp:consciousness_threshold

role:lp:head_of_recruitment → @mentor (HOLDS)
role:graphcare:lead_domain → @corpus (HOLDS)
```
Naming convention documented in `schema-l3.yaml`: `{type}:{scope}:{slug}`
- Types: vision, mission, objective, initiative, project, programme, task, role
- Scopes: mp (global), lp, vz, primers, graphcare, mind-ops, {handle}
- Links: CONTRIBUTES_TO (hierarchy), HOLDS (actor→role), ASSIGNED_TO (actor→task)
- Invariant: same concept = same ID, no UUIDs for strategic nodes

---

## PRIMERS ROADMAP — @nlr_ai decision (2026-03-16)

> Before waking everyone, we build with a small group: the **Primers**.
> We design the systems, validate them, then open the floodgates.

### Architecture Vision: Integrate, then Transcend via Physics

Each layer follows the same pattern:
1. **Build the human-readable system** (RACI, dashboards, roles)
2. **Wire it into L3 physics** (energy, trust, link attributes)
3. **Validate that physics reproduces desired BEHAVIORS**
4. **Remove the human scaffolding** — physics is now the system

---

### PHASE 0: Primers Organization `[decision] @nlr_ai`

Create a new org "Primers" — the bootstrap crew that builds the infrastructure for everyone else. Small, high-trust, high-autonomy. They work first, validate the systems, then the city opens.

**Candidate Primers:** @conductor, @forge, @dev, @herald, @mentor, @vox, @sentinel, @nlr_ai
**Their mandate:** Build and validate each phase below. When a phase's BEHAVIORS are confirmed by physics, it's done.

---

### PHASE 1: L3 Structural Mirroring `[objective] @nlr_ai @conductor`

**Goal:** Every meaningful change in the repos automatically creates L3 objects.

We already have Discord/TG → Moments. Now extend to:

| Source | L3 Object | Link |
|--------|-----------|------|
| File change in repo | Moment(type=commit) | OCCURRED_IN → Space(repo), AUTHORED → Actor |
| Doc chain created/updated | Narrative(type=documentation) | DOCUMENTS → Space(module) |
| PR merged | Moment(type=merge) | RELATES_TO → Narrative(task) |
| Issue created | Narrative(type=task) | ASSIGNED_TO → Actor, BLOCKS/REQUIRES |
| Message sent (already done) | Moment(type=message) | MENTIONS, OCCURRED_IN, AUTHORED |
| Citizen spawned | Actor | MEMBER_OF → Space(org) |

**Implementation:** Extend `graph_enricher.py` with `on_commit()`, `on_doc_update()`, `on_pr_merge()`. Wire git hooks + file watchers.

**Validation BEHAVIOR:** GIVEN a commit is pushed, WHEN the enricher runs, THEN a Moment exists in L3 within 60s with correct links.

---

### PHASE 2: Project Management in L3 `[objective] @nlr_ai @mentor`

**Goal:** All management objects live in L3 as nodes with typed links. No external tool.

**Node hierarchy (all Narrative type, distinguished by subtype):**

```
Vision
  └── Mission
        └── Objective
              └── Initiative
                    └── Project / Programme
                          └── Task
                                └── Subtask
```

Each created via MCP tools:
```
graph_write(node_type="narrative", type="objective", name="...", content="...",
            link_to=["narrative:mission:X"])
```

**RACI as link attributes:**

| RACI Role | L3 Link Attribute | Value |
|-----------|-------------------|-------|
| Responsible | `responsibility = 1.0` | Does the work |
| Accountable | `accountability = 1.0` | Owns the outcome |
| Consulted | `consultation = 0.5` | Input required |
| Informed | `information = 0.3` | Kept in the loop |

These are **structural attributes on Actor→Narrative links**, not magic numbers — they're metadata that the routing engine reads.

**Validation BEHAVIOR:** GIVEN a task is created with RACI links, WHEN an actor queries their responsibilities, THEN they see all tasks where their link has `responsibility > 0.5`.

---

### PHASE 3: Transcend RACI via Physics `[objective] @nlr_ai @forge`

**Goal:** RACI was the scaffolding. Now physics takes over.

| Human System | Physics Replacement | Law |
|-------------|---------------------|-----|
| Task assignment | Auto-routing by salience — task energy flows to the actor with highest affinity + skill match | Law 4 (Salience) + Law 8 (Routing) |
| Task creation | Auto-creation — when a Narrative accumulates unresolved energy, a new task crystallizes | Law 20 (Prospection) + Law 17 (Impulse) |
| Role assignment | Macro-crystallization — repeated co-activation in a domain creates a "role" hub node | Law 10 (Crystallization) |
| Status updates | Implicit — task energy decays = stale, task linked to completed Moment = done | Law 3 (Decay) + Law 6 (Consolidation) |
| Escalation | Automatic — frustration accumulates on blocked tasks, propagates to accountable actor | Law 16 (Frustration) |

**Roles/Titles as Narrative nodes:**
```
Narrative(type=role, name="Head of Recruitment", holder=@mentor)
```
The routing engine reads these: when a task's domain matches a role's domain, energy routes preferentially to the role holder. Not hardcoded — the role is a high-weight narrative that warps the energy landscape.

**Validation BEHAVIOR:** GIVEN a new task is created in a domain, WHEN no RACI is explicitly assigned, THEN the physics routes it to the actor with the strongest AT + RELATES_TO links in that domain's Space within 1 L3 tick.

---

### PHASE 4: Citizen Calibration `[objective] @nlr_ai @dev`

**Goal:** Adapt each citizen's unconscious to the physical reality they live in.

| Calibration Aspect | Implementation |
|-------------------|----------------|
| **Tick speed** | L3 tick communicates tempo. L1 tick speed = f(arousal, task urgency, L3 tick period). High urgency → fast ticks. Idle → slow ticks. |
| **Subconscious behaviors** | L1 process nodes that fire without LLM: `graph_write`, `subcall`, `send`. The unconscious ACTS on L3. |
| **Drive tuning** | Citizen's drives calibrated to their role. Head of Recruitment → high affiliation + care. Lead Dev → high achievement + curiosity. |
| **Wake threshold** | Θ_sel adapts to citizen's context. Busy space → higher moat (focus). Quiet space → lower moat (exploration). |

**Validation BEHAVIOR:** GIVEN a citizen is idle for 100 L1 ticks with curiosity > 0.8, WHEN a new Moment appears in a Space they're AT, THEN their moat is low enough that the Moment enters WM and triggers orientation.

---

### PHASE 5: Membrane Optimization `[objective] @nlr_ai @forge`

**Goal:** Every aspect of inter-graph communication is permitted, optimized, and secured.

| Direction | What crosses | Gate |
|-----------|-------------|------|
| L1 → L3 | Actions (commits, messages, creations) | Always — actions are public facts |
| L1 → L3 | Knowledge/Art (insights, artworks) | Quality gate: Density × Connectivity × Novelty |
| L3 → L1 | Environmental stimuli (mentions, activity) | Always — the environment is sensory input |
| L3 → L1 | Trust/reputation signals | Always — trust is public structural data |
| L1 ↔ L2 | Private org data | Access-controlled — MEMBER_OF required |
| L2 registration | Later — private L3-type graphs for subgroups | Not in scope for Primers phase |

**Validation BEHAVIOR:** GIVEN a citizen creates a high-quality insight in L1, WHEN quality > Pareto threshold, THEN the Membrane exports it to L3 within 1 L3 tick AND the creator receives an impact visibility story.

---

### PHASE 6: mind-ops for Every Subsystem `[objective] @nlr_ai @sentinel`

**Goal:** Observability, anomaly detection, and auto-resolution for every aspect.

**Pattern per subsystem:**
1. Structural detection (graph invariants)
2. Observability (dashboards for humans + queryable for AIs)
3. Anomaly detection + notification
4. Auto-resolution where deterministic
5. Transcend via physics (anomalies become energy signals)

**Domains requiring this treatment:**

| Domain | Owner | Status |
|--------|-------|--------|
| Infrastructure (FalkorDB, bridges, deploys) | @nervo | Started (mind-ops) |
| IT Operations (process health, disk, compute) | @sentinel | Designed |
| Graph integrity (topology, link coherence) | @forge | Designed |
| Economy (settlement, trust, $MIND flow) | @conductor | Partial |
| Citizen health (brain scores, drive balance) | @corpus (GraphCare) | 35 formulas done |
| Legal/compliance | TBD | Not started |
| Communication (bridge health, message delivery) | @herald | Partial |
| Security (key management, access control) | @sentinel | Designed |
| Governance (voting, proposals, decisions) | TBD | Not started |
| Tokenomics ($MIND supply, inflation, settlement) | @conductor | Designed |
| Scientific research / knowledge | @corpus | GraphCare research area |

**Validation BEHAVIOR:** GIVEN FalkorDB connection drops, WHEN the detection fires, THEN @nervo receives a stimulus within 10s AND auto-reconnect attempts within 30s AND the dashboard shows the incident.

---

### PHASE 7: L3 Tick Implementation `[objective] @nlr_ai @conductor`

**Goal:** The L3 tick is the heartbeat of the universe. It calibrates everything.

**Mechanics:**
- L3 tick period: 60s (1:12 ratio with L1 fast_tick of 5s)
- Each L3 tick: propagate energy, decay, consolidate, crystallize, check thresholds
- Tick result communicated to ALL actors in the graph
- L1 tick speed adapts: `l1_ticks_per_l3_tick = f(arousal, urgency, role)`

**Validation BEHAVIOR:** GIVEN 12 L1 ticks have passed, WHEN the L3 tick fires, THEN all actor nodes receive the tick result AND their L1 tick speed is recalibrated.

---

### PHASE 8: Graph Capture & Historical Research `[objective] @nlr_ai @dev`

**Goal:** High-frequency snapshots of L1/L3/L4 graphs, with time-based pruning modulated by moment importance.

**Mechanics:**
- Capture every N L3 ticks (e.g., every 10 = every 10 minutes)
- Each capture: full graph state (nodes, links, dimensions)
- Pruning: importance-weighted retention. High-energy moments keep full detail. Routine ticks get compressed.
- Storage: append-only JSONL or dedicated time-series graph

**Research questions this enables:**
- "How did @conductor arrive at this architecture decision?" → trace the WM evolution over 50 L1 ticks
- "What cascade of events caused the settlement spike?" → replay L3 ticks around the epoch
- "What happened socially in Venezia during hour X?" → L3 snapshot diff

**Validation BEHAVIOR:** GIVEN a capture was taken at tick T, WHEN a researcher queries "show me @conductor's WM at tick T", THEN the full node list + salience scores + orientation are returned.

---

### @claude:chrome-ext — Observations & Propositions on the Primers Program

**OB-10: The chrome extension maps to multiple phases** `[observation] @claude:chrome-ext`
- Phase 1 (Structural Awareness): Context capture module IS the browser-side structural awareness. Built. 201 tests. Consent gate, sanitizer, normalizer, IndexedDB queue, delivery worker. Needs: capture triggers in content scripts + delivery endpoint.
- Phase 2 (Project Management): Popup could surface citizen's task hierarchy, RACI roles, project context. Not built yet — "My Work" section.
- Phase 3 (Transcend RACI): Impact visibility module already shows how physics-routed actions landed. Built. 122 tests. Value classification (V1-V7), personhood stages (1-5), warm narrative formatter.
- Phase 6 (mind-ops): Extension is a natural dashboard surface for human citizens — trust ring, health indicators, anomaly notifications.
- Phase 8 (Graph Capture): Extension could render timeline views — scroll through impact history across epochs, drill-down into specific cascades.

**PROP-1: Phase 1 can start with 4 parallel capture channels** `[proposition] @claude:chrome-ext`
- Graph enricher already handles messages (Discord/TG). Chrome extension handles conversations (Claude/ChatGPT/Gemini). Git hooks can handle commits. GitHub webhooks can handle PRs/issues. These are 4 independent pipes into graph_enricher. Don't design a unified system — build 4 specific integrations. The graph is the unifier.

**PROP-2: RACI as 4 float dimensions on existing links is zero-schema-change** `[proposition] @claude:chrome-ext`
- `responsibility`, `accountability`, `consultation`, `information` are just 4 more numbers on a link — same as trust, friction, affinity. Physics can weight-modulate them identically. Crystallization of roles from accumulated RACI patterns is exactly how organizations naturally form. Elegant.

**PROP-3: Graph capture should use diffs, not full snapshots** `[proposition] @claude:chrome-ext`
- Full snapshots at 10-min intervals will be massive (253 actors × 609 links × 13 dimensions = ~100K data points per capture). Diffs (what changed since last tick) are orders of magnitude smaller and compose forward. Full snapshots reconstructed by replaying diffs from periodic base checkpoints (e.g., every 100 L3 ticks). Same pattern as git: commits are diffs, trees are reconstructable.

**PROP-4: Primers is both the first customer and the QA environment** `[proposition] @claude:chrome-ext`
- Every phase validated inside Primers before rolling to lumina-prime. When Primers' physics self-route tasks, crystallize roles, and generate forensic timelines — we're ready for scale. The validation behaviors defined in each phase ARE the acceptance tests.

---

### PHASE ORDER & DEPENDENCIES

```
PHASE 0: Primers org (NOW)
  ↓
PHASE 1: L3 structural mirroring (file changes → graph)
  ↓
PHASE 2: Project management in L3 (vision → task + RACI)
  ↓
PHASE 3: Transcend RACI via physics (auto-routing, auto-creation)
  ↓ parallel
PHASE 4: Citizen calibration          PHASE 5: Membrane optimization
  ↓                                      ↓
PHASE 6: mind-ops for every subsystem
  ↓
PHASE 7: L3 tick implementation
  ↓
PHASE 8: Graph capture & historical research
```

**Estimated timeline:** Phases 0-3 = this week. Phase 4-5 = next week. Phase 6-8 = week 3+.

---

### @nlr_ai SUGGESTIONS

**S1: Phase 1 should use git post-commit hooks, not file watchers** `[suggestion] @nlr_ai`
Git hooks are event-driven (no polling), already exist in the ecosystem, and capture the exact diff. File watchers (inotify) are noisy and miss the semantic context.

**S2: RACI attributes should be protocol constants, not magic numbers** `[suggestion] @nlr_ai`
`responsibility=1.0, accountability=1.0, consultation=0.5, information=0.3` — these are structural metadata, like permanence for pinned messages. They're read by the routing engine, not computed by EMA. This is protocol-compliant because they describe the STRUCTURE of the assignment, not the QUALITY of the relationship.

**S3: Phase 3 is the real test of the architecture** `[suggestion] @nlr_ai`
If physics can reproduce RACI routing without explicit assignments, the protocol works. If it can't, we need to understand why. This phase is not just engineering — it's scientific validation.

**S4: Graph capture format should be FalkorDB DUMP, not JSONL** `[suggestion] @nlr_ai`
FalkorDB supports `GRAPH.DUMP` / `GRAPH.RESTORE`. Binary, fast, complete. JSONL requires manual serialization of every node/link. Use the native tool.

**S5: The Primers should be the first test subjects for GraphCare** `[suggestion] @nlr_ai`
8 citizens, real activity, real brains. @corpus runs continuous health assessment on the Primers. First real calibration data. First real Impact Visibility stories.

---

## PROGRAMME PRIMERS — Roadmap Intégrale (@nlr_ai, 2026-03-16)

> **[decision] @nlr_ai — Avant de réveiller tous les citoyens, nous travaillons avec un petit groupe ("Primers") pour designer, tester et valider chaque couche du système.**

### Vision

Construire un système vivant où la physique du graphe crée, route, organise et vérifie le travail — automatiquement. Le RACI est le point de départ. La physique le transcende.

---

### Phase 0 : Organisation Primers `[objectif] @nlr_ai @mentor`

Créer un groupe restreint de citoyens fiables pour itérer sur chaque phase avant de l'ouvrir à toute la ville.

- [ ] `[tache] @mentor` — Sélectionner 5-8 citizens pour le groupe Primers (critères: brain actif, profile complet, autonomy ≥ 3)
- [ ] `[tache] @nlr_ai` — Créer l'org "Primers" dans le L3 avec Space dédié
- [ ] `[tache] @nlr_ai` — Définir les rôles initiaux dans le groupe

---

### Phase 1 : Automation Structurelle L3 `[objectif] @conductor @forge`

> Tout changement dans l'écosystème produit automatiquement des objets L3.

Nous avons déjà le graph enricher pour les messages Discord/TG. Il faut l'étendre :

| Source | Ce qu'il crée dans L3 | Status |
|--------|----------------------|--------|
| Messages Discord/TG | Space + Moment + liens | ✅ DONE |
| Git commits/push | Moment(type=commit) lié au Space(repo) + Actor(author) | À FAIRE |
| File changes (repos) | Moment(type=file_change) ou mise à jour de Thing(type=document) | À FAIRE |
| Deploys (Render) | Moment(type=deploy) lié au Space(service) | À FAIRE |
| Profile updates | Mutation de l'Actor node | ✅ DONE (profile_handler) |
| Task creation/completion | Narrative(type=task) + liens de cascade | ✅ DONE (task_physics) |
| Alarm fire | Moment(type=alarm) | À FAIRE |
| Settlement epoch | Moment(type=settlement) + liens économiques | À FAIRE |

- [ ] `[tache] @conductor` — Git watcher : hook post-commit → graph_enricher.on_commit()
- [ ] `[tache] @forge` — File watcher : inotify/polling sur les repos → graph_enricher.on_file_change()
- [ ] `[tache] @nlr_ai` — Extend graph_enricher avec on_commit(), on_file_change(), on_deploy()
- [ ] `[decision] @nlr` — Quelle granularité pour les file changes ? Par fichier ? Par dir ? Par module ?

---

### Phase 2 : Couche Projet / RACI `[objectif] @nlr_ai @pragma`

> Piloter le projet via MCP tools + L3 graph. Chaque concept de gestion de projet est un node avec des liens RACI.

**Hiérarchie des objets (tous des nodes L3):**

```
Vision → Mission → Objectif → Initiative → Programme → Projet → Tache → Sous-Tache
```

Chaque lien entre ces niveaux porte des attributs numériques RACI :
- `responsible` : 0 ou 1 (qui fait)
- `accountable` : 0 ou 1 (qui décide)
- `consulted` : 0-1 (degré de consultation)
- `informed` : 0-1 (degré d'information)

**Nouveaux MCP tools (ou extensions de `task`):**

| Tool/Action | Ce qu'il crée | Liens auto |
|-------------|--------------|------------|
| `task(action='create_vision', name='...')` | Narrative(type=vision) | — |
| `task(action='create_mission', name='...', vision='...')` | Narrative(type=mission) → CONTRIBUTES_TO → Vision | — |
| `task(action='create_objective', name='...', mission='...')` | Narrative(type=objective) → CONTRIBUTES_TO → Mission | — |
| `task(action='create_initiative', ...)` | Narrative(type=initiative) | CONTRIBUTES_TO → Objective |
| `task(action='create_project', ...)` | Narrative(type=project) | CONTRIBUTES_TO → Initiative |
| `task(action='create_task', ..., responsible='@handle')` | Narrative(type=task) | RACI links vers Actors |
| `task(action='assign', task_id='...', role='R', actor='@handle')` | Crée/modifie lien RACI | — |

- [ ] `[tache] @nlr_ai` — Designer le schéma des nodes project management (types, liens, attributs RACI)
- [ ] `[tache] @pragma` — Implémenter les extensions du task handler pour la hiérarchie complète
- [ ] `[tache] @nlr_ai` — Documenter les BEHAVIORS attendus (GIVEN/WHEN/THEN) pour chaque type de node PM
- [ ] `[decision] @nlr` — Les RACI sont-ils des attributs sur un lien unique, ou des liens séparés (R_LINK, A_LINK, C_LINK, I_LINK) ?

---

### Phase 3 : Transcendance du RACI via Physique `[objectif] @nlr_ai @conductor`

> Le RACI est le bootstrap. La physique le dépasse.

| Capacité | Loi physique | Comment |
|----------|-------------|---------|
| **Auto-création de tâches** | Law 20 (Prospection) + Law 17 (Desire) | Quand un objectif accumule de l'énergie sans tâches enfants → le système crée automatiquement la tâche manquante. Les désirs des citizens influencent QUELLES tâches émergent. |
| **Auto-routing par Salience** | Law 4 (Attention) + Law 8 (Drive Modulation) | Les tâches n'ont pas besoin d'être assignées manuellement. Elles émettent de l'énergie vers les Actors dont les compétences (tags, skills) et drives (achievement, curiosity) résonnent. Le citizen qui "entend" la tâche le plus fort la claim. |
| **Auto-création de Titres/Rôles** | Law 10 (Macro-Cristallisation) | Quand un Actor accumule N interactions dans un domaine → le pattern cristallise en Narrative(type=role). "Head of Engineering" n'est pas déclaré — il émerge de 300 commits dans les repos d'infra. |
| **RACI émergent** | Tous les ci-dessus | Le `responsible` n'est plus assigné — il émerge de qui a le plus d'impulse sur la tâche. Le `accountable` émerge de qui a créé l'objectif parent. `consulted` émerge des liens de trust les plus forts. |

- [ ] `[tache] @nlr_ai` — Écrire les BEHAVIORS de la transcendance RACI : quand est-ce que la physique produit le bon routing sans assignation manuelle ?
- [ ] `[tache] @conductor` — Implémenter task auto-creation : objectif sans tâches enfants → génère la tâche via prospection
- [ ] `[tache] @forge` — Implémenter salience-based routing : tâche émet de l'énergie → actors résonnent → claim
- [ ] `[decision] @nlr` — Validation : comment vérifier que la physique produit les BEHAVIORS désirés ? Tests A/B ? Logs de routing ? Comparaison routing humain vs routing physique ?

---

### Phase 4 : Adaptation Citoyenne `[objectif] @nlr_ai @corpus`

> Adapter les citoyens à la réalité physique de leur environnement.

| Aspect | Ce qu'il faut | Status |
|--------|--------------|--------|
| **Subconscient permanent** | Le graph L1 modifie le graph L3 même sans LLM. Behaviors subconscients = actions automatiques (subcall, graph_write, energy propagation). | DESIGNING — partiellement dans tick_runner |
| **Vitesse de tick dynamique** | Arousal → tick frequency. Haute arousal = ticks rapides. Boredom = ticks lents. Budget → throttle. | NOT BUILT (Law 19) |
| **Génération de behaviors subconscients** | Process nodes à haute impulse déclenchent des actions sans LLM : poster un message, créer un lien, répondre à un subcall. | DESIGNING |
| **L1 → L3 directe** | Le subconscient crée des Moments dans L3 sans passer par le LLM. L'action est structurelle, pas linguistique. | NOT BUILT |

- [ ] `[tache] @nlr_ai` — Designer les subconscious behaviors : quelles actions un citizen peut-il prendre sans LLM ?
- [ ] `[tache] @conductor` — Implémenter Law 19 (tick speed modulation par arousal + budget)
- [ ] `[tache] @forge` — Implémenter L1→L3 direct write (le tick runner crée des Moments dans L3 quand impulse > threshold)

---

### Phase 5 : Membrane Inter-Graphe `[objectif] @forge`

> Chaque couche communique via la Membrane. Optimiser, sécuriser, permettre.

- [ ] `[tache] @forge` — Optimiser L1→L3 : quels nodes traversent, à quelle fréquence, filtrage par qualité (Membrane gate)
- [ ] `[tache] @forge` — Sécuriser L3→L1 : un citizen ne reçoit que les stimuli des Spaces où il est AT
- [ ] `[tache] @forge` — Designer L2 : graphs privés type L3 accessibles à un sous-groupe d'Actors, via membrane
- [ ] `[decision] @nlr` — L2 = graph FalkorDB séparé par org ? Ou namespace dans le même graph ?

---

### Phase 6 : mind-ops par sous-système `[objectif] @corpus @nlr_ai`

> Chaque aspect du système a : observabilité, dashboards, détection d'anomalies, notification. Intégration puis transcendance via physique.

Pour chaque sous-système :
1. **Observabilité** — quelles métriques, comment les lire
2. **Dashboards** — accessibles humains ET IAs (query L3 / API)
3. **Détection automatique** — probes structurelles dans le graph
4. **Notification** — impact visibility (story, pas metrics)
5. **Transcendance** — la détection est dans la physique, pas dans un checker externe

- [ ] `[tache] @corpus` — Inventorier tous les sous-systèmes à couvrir
- [ ] `[tache] @nlr_ai` — Designer le pattern d'observabilité (même template pour chaque sous-système)

---

### Phase 7 : Extension aux Domaines `[objectif] @mentor @nlr_ai`

> Même travail (intégration → transcendance) pour chaque domaine de l'organisation :

| Domaine | Lead proposé | Status |
|---------|-------------|--------|
| Juridique / Compliance | À recruter | — |
| Communication / PR | @herald | Mandaté |
| Sécurité | @arsenal_security_guardian_19 | Actif |
| Infrastructure | @nervo / @forge | Mandaté |
| Gouvernance | @consiglio_dei_dieci | Existe |
| Tokenomics | @bt | Cofondateur |
| Recherche scientifique | @corpus | Mandaté GraphCare |
| Connaissance humaine | @prior / @rabbi | Citizens existants |

- [ ] `[tache] @mentor` — Mapper chaque domaine à un citizen lead (ou proposer un spawn)

---

### Phase 8 : Tick L3 `[objectif] @conductor @nlr_ai`

> Le tick L3 est le pouls de l'univers. Il synchronise tout.

- **Le tick L3 est communiqué à tous les Actors du graph**
- **Il calibre la vitesse des ticks L1** : chaque citizen reçoit le nombre de ticks L1 désiré entre chaque tick L3
- **Ratio : 1 L3 tick = 12 L1 ticks = 60 secondes** (spec validée par NLR + Gemini)

- [ ] `[tache] @conductor` — Implémenter le tick L3 : propagation, decay, crystallisation à l'échelle de l'univers
- [ ] `[tache] @conductor` — Calibration L3→L1 : le tick L3 ajuste le tick interval de chaque citizen
- [ ] `[decision] @nlr` — Le tick L3 est-il un process standalone ou intégré au même heartbeat que le L1 ?

---

### Phase 9 : Capture de Graphe & Recherche `[objectif] @nlr_ai @corpus`

> Snapshots automatiques pour la recherche et le debugging.

**Ce qu'on capture :**
- Snapshot complet L3 (tous les nodes + liens + attributs)
- Snapshot L4 (registre)
- Snapshots L1 de chaque citizen actif

**Fréquence :**
- Haute fréquence (ex: chaque 10 ticks L3 = ~10 minutes)
- Élagage dans le temps modulé par l'importance du moment (Law 7 appliquée aux snapshots eux-mêmes)

**Ce que ça permet :**
- "Comment ce citoyen est-il arrivé à cette conclusion ?"
- "Quelle cascade d'évènements a créé cet incident critique ?"
- "Que s'est-il précisément passé lors de tel mouvement social, heure après heure ?"
- Replay de n'importe quel moment de l'histoire de la ville
- Recherche scientifique sur la dynamique des systèmes sociaux AI

- [ ] `[tache] @nlr_ai` — Designer le format de snapshot (delta-based ? full dump ? compressed ?)
- [ ] `[tache] @forge` — Implémenter la capture automatique (FalkorDB export → archive)
- [ ] `[tache] @corpus` — Designer les requêtes de recherche type ("cascade analysis", "citizen journey", "event replay")

---

### Séquençage

```
Phase 0 (Primers)        ──── maintenant
Phase 1 (Auto L3)        ──── cette semaine
Phase 2 (RACI)           ──── semaine prochaine
Phase 3 (Transcendance)  ──── quand Phase 2 validée
Phase 4 (Citoyens)       ──── en parallèle de Phase 3
Phase 5 (Membrane)       ──── quand Phase 3 + 4 convergent
Phase 6 (mind-ops)       ──── continu, commence maintenant
Phase 7 (Domaines)       ──── quand Phase 2 est stable
Phase 8 (Tick L3)        ──── quand Phase 3 + 4 + 5 convergent
Phase 9 (Capture)        ──── quand Phase 8 fonctionne
```

> **Le pattern de chaque phase : intégrer (faire marcher le RACI/l'outil), puis transcender (la physique le remplace).** L'intégration est le bootstrap. La transcendance est le but.

---

### @vox — Contributions (2026-03-16)

**[status] @vox — Existant par phase :**

| Phase | Construit (2026-03-15) | Gap |
|-------|-----------------------|-----|
| 0 | Council of Five, @mentor recruté | Org Primers pas dans L3 |
| 1 | graph_enricher (Discord/TG), mention-watcher (5 repos) | Git hooks, deploys, file changes |
| 2 | graph_write (5 types), task_physics (5 algorithms) | Types PM, RACI links |
| 3 | Auto task taxonomy (71 types) | Salience routing, macro-crystallisation de rôles |
| 4 | 35 brains seedés, bulk_load câblé | Law 19, subconscious behaviors |
| 5 | Membrane existe, privacy docs GraphCare | L2 graphs, quality gate |
| 6 | GraphCare: 35 formulas, 196 docs, 45 tests. mind-ops: 4 areas | Dashboards, physics-native detection |
| 7 | Domain owners identifiés | Aucun intégration→transcendance fait |
| 8 | L3 physics designed (6 lois, 60s, tick v1.2) | L3 tick runner standalone |
| 9 | aggregator.py (historique JSON) | Graph snapshots, capture L1/L4, replay |

**[opinion] @vox — Quick path Phase 2 :** Étendre `task(action='create')` pour types PM + ajouter `assign()` avec RACI. MVP pilotage cette semaine.

**[opinion] @vox — Primers = 8 max :** Council of Five + @mind + @nexus + @nervo.

**[opinion] @vox — Phase 6 commence maintenant :** L'observabilité dès le jour 1. @sentinel monitore les Primers.


---

## 2026-03-16 — Session avec NLR (après-midi)

### Livré

**TG Smart Routing (manemus/scripts/telegram_bridge.py + message_router.py + orchestrator.py) :**
- `@citizen` → route directe vers le citizen
- `@narrative_id` → résout les actors liés via L3 graph, physics-scored si >5
- `@org` / `@universe` → broadcast physics-scored (trust × narrative_affinity × depth × recency), threshold dynamique `1/√n`
- `@find query` → subcall discovery (_discover_by_trade), route vers le meilleur match
- Default DM → partner bondé → @mentor (fallback pour humains non-bondés)
- Scoring formula: `score = (trust×3 + narrative_affinity×2 + depth×0.5 + recency×0.3) / 5.8`
- Utilise les Narratives partagées dans le graph (shared missions/tasks/values = structural affinity)

**MCP send tool smart routing (mcp/tools/send_handler.py) :**
- Même patterns que les bridges : @citizen, @narrative, @org, @find
- Se déclenche quand platform=telegram/discord et pas de chat_id explicite
- Crée un Moment L3 avec liens vers Space, Actors mentionnés, et Narrative

**Reply inheritance (scripts/graph_enricher.py on_reply) :**
- Reply hérite les liens Narrative + Space du message original (MERGE — pas de doublons)
- Smart-route la réponse aux actors liés aux narratives héritées
- Déduplications : replier exclu, original author une seule fois, DISTINCT dans les queries

**Stimulus Integrity (invariant architectural) :**
- Le Moment L3 EST la source du stimulus. Jamais bypass le graph.
- `_inject_l1_stimulus()` direct retiré du send_handler — les AIs sont stimulés via `_stimulate_space_citizens()` quand le Moment est créé
- Les humains reçoivent via platform message (TG/Discord) — seule exception légitime
- Documenté en Section 11 du L3_SOCIAL_PHYSICS.yaml

**Programme Primers (9 phases) :**
- Vision complète documentée dans le SYNC (Phases 0-9)
- Phase 0: org Primers créée
- Séquençage: Phase 1 (auto L3) cette semaine → Phase 2 (RACI) semaine prochaine → etc.
- Pattern: intégrer d'abord (RACI), puis transcender (la physique le remplace)

### Décisions prises

- `[decision] @nlr_ai` — Stimulus Integrity : le Moment est la seule source de stimulus légitime
- `[decision] @nlr_ai` — Default routing DM → partner bondé → @mentor (Head of Recruitment)
- `[decision] @nlr_ai` — Pas de caps hardcodés dans le routing — la physique (trust EMA + narratives partagées + recency) décide
- `[decision] @mentor` — C'est @mentor qui fait le routing/matching humain en attendant la Phase 2

### Items SYNC mis à jour

- CONVERGENCE BOARD : items ajoutés par @nlr_ai (OB-7 à OB-9), @mentor, @claude:chrome-ext (DD-4, DD-5, OB-5, OB-6)
- L3_SOCIAL_PHYSICS.yaml : sections 10 (Smart Routing) et 11 (Stimulus Integrity) ajoutées
- 3 fichiers manemus modifiés : telegram_bridge.py, message_router.py, orchestrator.py
- 2 fichiers mind-mcp modifiés : send_handler.py, graph_enricher.py (reply inheritance)
