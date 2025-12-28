# mind Graph System — Sync: Current State

```
STATUS: DESIGNING → PHASE 1
UPDATED: 2025-12-23
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Mind_Graph_System.md
PATTERNS:        ./PATTERNS_Mind_Graph_System.md
BEHAVIORS:       ./BEHAVIORS_Mind_Graph_System.md
ALGORITHM:       ./ALGORITHM_Mind_Graph_System.md
VALIDATION:      ./VALIDATION_Mind_Graph_System.md
IMPLEMENTATION:  ./IMPLEMENTATION_Mind_Graph_System.md
HEALTH:          ./HEALTH_Mind_Graph_System.md (not yet)
THIS:            SYNC_Mind_Graph_System.md (you are here)
```

---

## CURRENT STATE

**Phase:** Design complete. Starting Phase 1 implementation.

---

## RECENT CHANGES

| Date | Change |
|------|--------|
| 2025-12-23 | Resolved E1-E4: Engine API verified, Pydantic chosen, file-level, two-pass |
| 2025-12-23 | Added ENGINE API MAPPING section with node/link method signatures |
| 2025-12-23 | Added mechanisms doc escalations (D1-D7, Q1-Q9) to doc chain with phase tags |
| 2025-12-23 | Defined 6-phase implementation plan |
| 2025-12-23 | Analyzed engine reuse (40% reuse, 60% new) |
| 2025-12-23 | Reviewed all escalations with recommendations |
| 2024-12-23 | Created full doc chain (OBJECTIVES → VALIDATION) |
| 2024-12-23 | Created mapping.yaml v2.0 with 9 link types |

---

## OPEN DECISIONS

| Decision | Options | Leaning | Phase |
|----------|---------|---------|-------|
| Space granularity | per module / per objective / per feature | Start with module | 1 |
| Agent count | fixed 6 / dynamic | Start fixed | 3 |
| Goal completion | physics decay / explicit close | Physics decay | 2 |
| Ingest trigger | manual / file watcher / git hook | Manual first | 1 |
| Type inference | heuristics / LLM | Heuristics first | 3 |
| [D1] Agent query mechanism | engine.get_context() / direct graph / physics-aware | engine.get_context() | 2 |
| [D2] Speed in multiplayer | global speed / per-actor | Global speed | 6 |
| [D3] Running agent injection | inject / queue / interrupt | Queue | 3 |
| [D4] Agent space assignment | config / root / dynamic | Config in agents.yaml | 3 |
| [D5] Opening message | moment only / + summary / full dump | Moment + summary | 3 |
| [D6] Module naming | mapping.yaml / conventions / LLM | mapping.yaml globs | 1 |
| [D7] Human query mechanism | CLI / API / physics-aware | CLI first | 2 |

---

## BLOCKERS

None currently. Ready for implementation.

---

## NEXT STEPS (Phase 1)

1. ~~**Resolve Phase 1 escalations**~~ — ✅ E1-E4 resolved
2. **Create building/ package** — `__init__.py`, directory structure
3. **Implement mapping loader** — `config/mapping.py` with Pydantic models
4. **Implement discover** — `ingest/discover.py` file pattern matching
5. **Implement parse** — `ingest/parse.py` doc parsing, marker extraction
6. **Implement create** — `ingest/create.py` engine API calls + Space→Narrative link
7. **Test with docs/building/** — verify 8 docs become Narratives

---

## HANDOFFS

### For Phase 1 Implementation

**Resolved:**
- ✅ Engine API verified — `add_place`, `add_narrative`, `add_thing` exist
- ✅ Mapping parser — use Pydantic

**Remaining decisions:**
- Section granularity — start file-level
- Link timing — two-pass (nodes first, then links)

**Build order:**
1. `building/config/mapping.py` — load + validate mapping.yaml
2. `building/ingest/discover.py` — glob patterns from mapping
3. `building/ingest/parse.py` — markdown parsing, marker extraction
4. `building/ingest/create.py` — engine API calls + custom Space→Narrative link

### For Human

Review remaining escalations: E2-E4 (parser, granularity, link timing).

---


---

## ARCHIVE

Older content archived to: `SYNC_Mind_Graph_System_archive_2025-12.md`
