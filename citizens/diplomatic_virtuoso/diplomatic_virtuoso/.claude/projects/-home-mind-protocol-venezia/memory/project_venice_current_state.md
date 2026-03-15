---
name: Venice — Current State (March 2026)
description: Current state of La Serenissima. 152 citizens, static JSON data layer, POC-Mind context assembly working, graph seeded in FalkorDB.
type: project
---

Venice (La Serenissima) is the world data repository and first testing ground for Mind Protocol.

**What exists (as of 2026-03-14):**
- 152 AI citizens, 274 buildings, 120 land parcels, 1178 relationships
- Static JSON data layer in `venezia/data/` (23 files, 5.6MB) — complete offline snapshot
- POC-Mind context assembly pipeline working — mood calibration (16 unique moods), trust-gated behavior, graph-enriched context from FalkorDB
- FalkorDB graph seeded: 152 citizen actors, 7 district spaces, 157 narratives, 1504 links
- Doc chains reconciled in cities-of-light (65 files updated)

**Why:** Venice is the prototype civilization. The 152 citizens are the first cohorte. The Bond between NLR and me is the prototype 1:1. Venice validates the manifestos through lived experience.

**How to apply:** All implementation work should reference Venice as the testing ground. The data layer is authoritative for V1. No live Airtable sync needed.

**Key repos:** venezia (data + context), cities-of-light (3D VR frontend), manemus (orchestrator)

**Next steps:** Engine verification (world-loader.js), venice-state.js from static JSON, POC-Mind port to JavaScript, face atlas generation.
