# Scene Memory System — Implementation: Moment Processing Architecture

```
STATUS: DRAFT
CREATED: 2025-12-19
UPDATED: 2025-12-19
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Scene_Memory.md
BEHAVIORS:       ./BEHAVIORS_Scene_Memory.md
ALGORITHM:       ./ALGORITHM_Scene_Memory.md
VALIDATION:      ./VALIDATION_Scene_Memory.md
THIS:            IMPLEMENTATION_Scene_Memory.md
TEST:            ./TEST_Scene_Memory.md
SYNC:            ./SYNC_Scene_Memory.md
ARCHIVE:         ./archive/SYNC_archive_2024-12.md

IMPL:            runtime/infrastructure/memory/moment_processor.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

```
runtime/infrastructure/memory/
├── runtime/infrastructure/memory/__init__.py          # Exports MomentProcessor for external use
└── runtime/infrastructure/memory/moment_processor.py  # Moment creation + transcript management
```

### File Responsibilities

| File | Purpose | Key Functions/Classes | Lines | Status |
|------|---------|----------------------|-------|--------|
| `runtime/infrastructure/memory/__init__.py` | Module export surface | `MomentProcessor` | ~11 | OK |
| `runtime/infrastructure/memory/moment_processor.py` | Create moments, manage transcript, connect to GraphOps | `MomentProcessor`, `get_moment_processor` | ~585 | WATCH |

**Size Thresholds:** OK <400 lines, WATCH 400-700 lines, SPLIT >700 lines.

---

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| `MomentProcessor` | `runtime/infrastructure/memory/moment_processor.py:17` | Orchestration setup for a playthrough |
| `set_context` | `runtime/infrastructure/memory/moment_processor.py:108` | Scene start / location change |
| `process_dialogue` | `runtime/infrastructure/memory/moment_processor.py:126` | Narrator dialogue line |
| `process_narration` | `runtime/infrastructure/memory/moment_processor.py:191` | Narrator narration line |
| `process_player_action` | `runtime/infrastructure/memory/moment_processor.py:252` | Player click/freeform/choice |
| `process_hint` | `runtime/infrastructure/memory/moment_processor.py:319` | Hint or whispered line |
| `create_possible_moment` | `runtime/infrastructure/memory/moment_processor.py:380` | Pre-seed possible moments |
| `link_moments` | `runtime/infrastructure/memory/moment_processor.py:450` | Connect moments for traversal |
| `link_narrative_to_moments` | `runtime/infrastructure/memory/moment_processor.py:483` | Attribute narratives to moments |
| `get_moment_processor` | `runtime/infrastructure/memory/moment_processor.py:559` | Convenience factory |

---

## DATA FLOW (SUMMARY)

```
Narrator/Player text
        │
        ▼
MomentProcessor.process_*()
        │
        ├─ _append_to_transcript()  # persist transcript.json + line number
        ├─ embed_fn()               # only if text > 20 chars
        ▼
GraphOps.add_moment()              # persist Moment node + links
```

---

## LOGIC CHAINS

Moment ingestion follows a strict sequence: set context, normalize speaker
identity, append transcript, optional embed, then graph insert and linking. The
chain deliberately orders persistence before linking so transcript line numbers
are stable for downstream attribution and replay tooling.

---

## CONCURRENCY MODEL

MomentProcessor is designed for single-playthrough use and assumes serialized
calls per playthrough. File-backed transcript writes are not locked across
processes, so concurrent writes must be prevented by orchestration to avoid
interleaved line numbers or partial JSON writes.

---

## MODULE DEPENDENCIES

### Internal

```
runtime/infrastructure/memory/moment_processor.py
    └── imports → engine.physics.graph.graph_ops.GraphOps
    └── imports → engine.infrastructure.embeddings.service.get_embedding_service
```

### External

| Package | Used For |
|---------|----------|
| `json` | Transcript persistence |
| `logging` | Processor diagnostics |
| `pathlib` | Playthrough paths |
| `datetime` | Transcript timestamps |

---

## BIDIRECTIONAL LINKS

### Code → Docs

| File | Line | Reference |
|------|------|-----------|
| `runtime/infrastructure/memory/moment_processor.py` | 1 | `DOCS: docs/infrastructure/scene-memory/` |

### Docs → Code

| Doc Section | Implemented In |
|-------------|----------------|
| Spoken moment creation | `runtime/infrastructure/memory/moment_processor.py:126` |
| Player action processing | `runtime/infrastructure/memory/moment_processor.py:252` |
| Possible moment seeding | `runtime/infrastructure/memory/moment_processor.py:380` |
| Transcript persistence | `runtime/infrastructure/memory/moment_processor.py:66` |

---

## MARKERS

### Extraction Candidates

| File | Current | Target | Extract To | What to Move |
|------|---------|--------|------------|--------------|
| `runtime/infrastructure/memory/moment_processor.py` | ~585L | <400L | internal transcript helpers (stay in `runtime/infrastructure/memory/moment_processor.py`) | `_load_transcript_line_count`, `_write_transcript`, `_append_to_transcript` |
| `runtime/infrastructure/memory/moment_processor.py` | ~585L | <400L | internal ID helpers (stay in `runtime/infrastructure/memory/moment_processor.py`) | `_generate_id`, `_tick_to_time_of_day` |

### Questions

<!-- @mind:escalation Should transcript IO move behind a storage interface to support streaming or append-only logs? -->
