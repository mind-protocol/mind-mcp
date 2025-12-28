# World Runner — Archive (2024-12)

```
CREATED: 2025-12-19
STATUS: ARCHIVED
```

---

## Purpose

This archive stores verbose examples and full schemas removed from the main docs to keep module size under limits.
The preserved narrative helps auditors verify the world-runner expectations and calibrate future archives before they replace the December 2024 snapshot.

## MATURITY

STATUS: ARCHIVED

The archived snapshot is frozen for historical reference and should never be treated as the canonical operational sync document because all live orchestration happens in the world-runner module’s main sync ledger.
This status line keeps the archive separated from active timelines while letting auditors trace why the example belongs in history rather than the working state.

## CURRENT STATE

This file now records the December 2024 examples that were removed from the live runner documentation and keeps them searchable for audits or historical comparisons.
Each section stresses that the payload is historical: no CLI commands read from this archive, and it exists to preserve reasoning samples, not to drive runtime logic.

## RECENT CHANGES

### 2026-01-07: Stabilize archive template coverage

- **What:** Added MATURITY, CURRENT STATE, KNOWN ISSUES, TODO, HANDOFF narratives, CONSCIOUSNESS TRACE, and POINTERS so the archive sync now satisfies the DOC_TEMPLATE_DRIFT template requirements while leaving the archived payloads untouched.
- **Why:** The archive previously lacked the mandatory template sections, so filling them ensures downstream agents can read a complete state snapshot, trust the structure, and see exactly where the live contracts live.
- **Verification:** `mind validate` confirms that the archive document now meets the template expectations along with the rest of the world-runner doc chain.
- **Legacy note:** Every added section includes a reminder that the December 2024 payloads are historical; leave the JSON samples and validation rules unchanged unless a new archival cut is authorized.

## IN PROGRESS

No active documentation or implementation work is happening inside this archive; the snapshot is frozen until a new historical cut needs recording.
The inert status is documented so future agents realize the file is read-only and does not expect runnable content.
Any future archival notes must go through a deliberate freeze process, so add them to the TODO list and RECENT CHANGES only after explicit approval from the module owner.
This keeps the archive from being treated as an evolving plan and preserves the December 2024 behavior cache for auditors rather than forcing it into the live workflow.

## KNOWN ISSUES

- None; this archive is intentionally static, but any future archival additions should be justified before touching the frozen content and should include a new `RECENT CHANGES` entry that describes how the history has evolved.

## HANDOFF: FOR AGENTS

Treat this file as a historical snapshot only. For active work on the world-runner module, follow `VIEW_Implement_Write_Or_Modify_Code.md` and update the canonical `docs/agents/world-runner/SYNC_World_Runner.md` instead.
This entry reminds agents to keep the operational contract in the live SYNC document so the archive does not drift into acting like a working plan.
Also use the added HANDOFF lines to skip this archive when verifying current behavior or refreshing the World Runner CLI.

## HANDOFF: FOR HUMAN

This archive now self-documents its maturity, state, and TODO items, so no immediate action is required; request human review only if new archival data must be added or referenced explicitly.
Please confirm any future archival cut before aging new narratives into this snapshot so the record stays consistent.

## TODO

<!-- @mind:todo Keep this archive synchronized with any future migrations of world-runner examples that need long-term preservation; otherwise, leave it untouched and note the reason for each freeze. -->

## CONSCIOUSNESS TRACE

Captured the archive-template drift by articulating why each new section exists and reminding future agents that this file’s purpose is record keeping rather than active orchestration.
The trace now explicitly says the archive is deterministic history, so agents do not expect it to evolve on each sprint.

## POINTERS

- `docs/agents/world-runner/SYNC_World_Runner.md` describes the current live work; use it whenever you need the active status.
- The CHAIN references below point to PATTERNS/BEHAVIORS/ALGORITHM/VALIDATION/IMPLEMENTATION/TEST docs that explain the live world-runner experience.
- Use `docs/agents/world-runner/archive/SYNC_archive_2024-12.md` to trace the 2024 payloads and the JSON schema samples linked above.
- Consider the archive’s `Purpose` and `MAINTENANCE` sections whenever you or future agents are asked to reference historical samples during debugging or audit reviews.

---

## Archived From TOOL_REFERENCE.md

### Complete Example
## Complete Example

```json
{
  "thinking": "Edmund's confrontation pressure flipped. Given Rolf's oath and Edmund's location in York, Edmund would have received word of Rolf's approach and made a preemptive political move. This creates new retaliation pressure.",

  "graph_mutations": {
    "new_narratives": [
      {
        "id": "narr_edmund_move",
        "name": "Edmund made his move",
        "content": "Edmund's allies in York have begun spreading word that Rolf's claim to Thornwick is illegitimate, based on documents Edmund 'discovered' among their father's effects.",
        "interpretation": "Edmund strikes first, using politics rather than steel.",
        "type": "account",
        "about": {
          "characters": ["char_edmund", "char_rolf"],
          "places": ["place_york"]
        },
        "tone": "cold",
        "truth": 0.3
      },
      {
        "id": "narr_thornwick_documents",
        "name": "The disputed documents",
        "content": "Documents purportedly from the old lord suggest Thornwick was always meant for Edmund alone.",
        "type": "claim",
        "about": {
          "characters": ["char_edmund"],
          "things": ["thing_thornwick_deed"],
          "places": ["place_thornwick"]
        },
        "tone": "cold",
        "truth": 0.1
      }
    ],

    "new_beliefs": [
      {
        "character": "char_wulfstan",
        "narrative": "narr_edmund_move",
        "heard": 1.0,
        "believes": 0.8,
        "source": "told",
        "from_whom": "char_merchant"
      },
      {
        "character": "char_gospatric",
        "narrative": "narr_edmund_move",
        "heard": 1.0,
        "believes": 0.3,
        "doubts": 0.6,
        "source": "told"
      }
    ],

    "pressure_updates": [
      {
        "id": "narr_confrontation",
        "pressure": 0.0,
        "resolved": true,
        "reason": "Confrontation occurred - Edmund acted first"
      }
    ],

    "new_pressure_points": [
      {
        "id": "narr_retaliation",
        "narratives": ["narr_edmund_move", "narr_rolf_oath"],
        "description": "Rolf will not accept Edmund's political attack quietly. His oath demands response.",
        "pressure": 0.4,
        "pressure_type": "hybrid",
        "breaking_point": 0.9,
        "base_rate": 0.002,
        "progression": [
          { "at": "Day 18", "pressure_floor": 0.5 },
          { "at": "Day 20", "pressure_floor": 0.7 }
        ],
        "narrator_notes": "Rolf's response will be physical, not political. He doesn't play Edmund's game."
      }
    ],

    "character_movements": [
      {
        "character": "char_edmund",
        "from": "place_york_hall",
        "to": "place_castle",
        "visible": false
      }
    ],

    "modifier_changes": [
      {
        "node": "char_messenger",
        "add": {
          "type": "exhausted",
          "severity": "moderate",
          "duration": "until rested",
          "source": "Hard riding from York"
        }
      },
      {
        "node": "place_york",
        "add": {
          "type": "tense",
          "severity": "mild",
          "source": "Rumors of the dispute spreading"
        }
      }
    ]
  },

  "world_injection": {
    "time_since_last": "2 days",

    "breaks": [
      {
        "narrative_id": "narr_confrontation",
        "narrative": "narr_edmund_move",
        "event": "Edmund's allies moved against Rolf's claim publicly in York",
        "location": "place_york",
        "player_awareness": "will_hear",
        "witnesses": ["char_wulfstan", "char_gospatric", "char_merchant"]
      }
    ],

    "news_arrived": [],

    "pressure_changes": {
      "narr_retaliation": "created at 0.4"
    },

    "interruption": null,

    "atmosphere_shift": "The road to York feels different now. Merchants pass without meeting your eyes.",

    "narrator_notes": "Player will learn of Edmund's move when they reach York or meet someone from there. The political landscape has shifted - Edmund has allies, Rolf has a harder path."
  }
}
```

---

## Validation Rules

1. **`thinking` is REQUIRED** — Reasoning must be traceable
2. **All IDs must be valid** — Character, place, narrative IDs must exist or be created
3. **`about` must reference existing nodes** — Or nodes being created in same mutation
4. **`truth` is director-only** — Characters never see this field
5. **Belief `heard` must be > 0 for other fields to matter**
6. **Pressure `narratives` must exist** — Or be created in same mutation
7. **`player_awareness` must be accurate** — Based on player location

---

## Processing Order

When applying mutations:

1. **New narratives first** — Create before referencing
2. **New beliefs second** — Now narratives exist to believe
3. **Pressure updates third** — Existing pressure modified
4. **New pressure points fourth** — New pressure clusters created
5. **Character movements fifth** — Physical state changes
6. **Modifier changes last** — Temporary states applied

---


### JSON Schema (for programmatic validation)
## JSON Schema (for programmatic validation)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["thinking", "graph_mutations", "world_injection"],
  "properties": {
    "thinking": { "type": "string" },
    "graph_mutations": {
      "type": "object",
      "properties": {
        "new_narratives": {
          "type": "array",
          "items": { "$ref": "#/definitions/newNarrative" }
        },
        "new_beliefs": {
          "type": "array",
          "items": { "$ref": "#/definitions/newBelief" }
        },
        "pressure_updates": {
          "type": "array",
          "items": { "$ref": "#/definitions/pressureUpdate" }
        },
        "new_tensions": {
          "type": "array",
          "items": { "$ref": "#/definitions/newTension" }
        },
        "character_movements": {
          "type": "array",
          "items": { "$ref": "#/definitions/characterMovement" }
        },
        "modifier_changes": {
          "type": "array",
          "items": { "$ref": "#/definitions/modifierChange" }
        }
      }
    },
    "world_injection": {
      "type": "object",
      "required": ["time_since_last", "breaks"],
      "properties": {
        "time_since_last": { "type": "string" },
        "breaks": {
          "type": "array",
          "items": { "$ref": "#/definitions/break" }
        },
        "news_arrived": { "type": "array" },
        "pressure_changes": { "type": "object" },
        "interruption": { "type": ["object", "null"] },
        "atmosphere_shift": { "type": "string" },
        "narrator_notes": { "type": "string" }
      }
    }
  },
  "definitions": {
    "newNarrative": {
      "type": "object",
      "required": ["id", "name", "content", "type", "about"],
      "properties": {
        "id": { "type": "string" },
        "name": { "type": "string" },
        "content": { "type": "string" },
        "interpretation": { "type": "string" },
        "type": { "type": "string" },
        "about": { "type": "object" },
        "tone": { "type": "string" },
        "truth": { "type": "number", "minimum": 0, "maximum": 1 },
        "focus": { "type": "number", "minimum": 0.1, "maximum": 3.0 }
      }
    },
    "newBelief": {
      "type": "object",
      "required": ["character", "narrative", "heard", "source"],
      "properties": {
        "character": { "type": "string" },
        "narrative": { "type": "string" },
        "heard": { "type": "number", "minimum": 0, "maximum": 1 },
        "believes": { "type": "number", "minimum": 0, "maximum": 1 },
        "doubts": { "type": "number", "minimum": 0, "maximum": 1 },
        "denies": { "type": "number", "minimum": 0, "maximum": 1 },
        "source": { "type": "string" },
        "from_whom": { "type": "string" }
      }
    },
    "pressureUpdate": {
      "type": "object",
      "required": ["id", "reason"],
      "properties": {
        "id": { "type": "string" },
        "pressure": { "type": "number", "minimum": 0, "maximum": 1 },
        "resolved": { "type": "boolean" },
        "reason": { "type": "string" }
      }
    },
    "newPressurePoint": {
      "type": "object",
      "required": ["id", "narratives", "description", "pressure", "pressure_type"],
      "properties": {
        "id": { "type": "string" },
        "narratives": { "type": "array", "items": { "type": "string" } },
        "description": { "type": "string" },
        "pressure": { "type": "number", "minimum": 0, "maximum": 1 },
        "pressure_type": { "enum": ["gradual", "scheduled", "hybrid"] },
        "breaking_point": { "type": "number", "minimum": 0, "maximum": 1 },
        "base_rate": { "type": "number" },
        "trigger_at": { "type": "string" },
        "progression": { "type": "array" },
        "narrator_notes": { "type": "string" }
      }
    },
    "characterMovement": {
      "type": "object",
      "required": ["character", "to"],
      "properties": {
        "character": { "type": "string" },
        "from": { "type": "string" },
        "to": { "type": "string" },
        "visible": { "type": "boolean" }
      }
    },
    "modifierChange": {
      "type": "object",
      "required": ["node"],
      "properties": {
        "node": { "type": "string" },
        "add": { "type": "object" },
        "remove": { "type": "string" }
      }
    },
    "break": {
      "type": "object",
      "required": ["narrative_id", "narrative", "event", "location", "player_awareness"],
      "properties": {
        "narrative_id": { "type": "string" },
        "narrative": { "type": "string" },
        "event": { "type": "string" },
        "location": { "type": "string" },
        "player_awareness": { "enum": ["witnessed", "encountered", "heard", "will_hear", "unknown"] },
        "witnesses": { "type": "array", "items": { "type": "string" } }
      }
    }
  }
}
```

---

## Archived From BEHAVIORS_World_Runner.md

### Injection as Markdown (Narrator Input)
## Injection as Markdown (Narrator Input)

The injection goes into the Narrator's context as **structured markdown** with full node details:

```markdown
# WORLD INJECTION
═════════════════

## Status: INTERRUPTED

**At minute:** 500 (8h 20m into journey)
**Remaining:** 2380 minutes (39h 40m)

---

## EVENT: Ambush on the Road

**Type:** ambush
**Location:** place_road_north

Three men block the road ahead. Armed. One carries a Norman sword.

---

## CLUSTER: Relevant Nodes

### Pressure (Flipped)

**narr_road_ambush**
- pressure: 0.95 → FLIPPED
- breaking_point: 0.90
- narratives: [narr_bandit_territory, narr_road_danger]

### Narratives

**narr_bandit_territory**
- content: "Wulfric's band controls this stretch of road. They take what they want from travelers."
- type: claim
- truth: 0.9
- weight: 0.72
- about: place_road_north, char_wulfric

**narr_road_danger**
- content: "The northern road is dangerous since the Normans stopped patrolling."
- type: rumor
- truth: 0.8
- weight: 0.65

### Characters Present

**char_wulfric** (bandit leader)
- name: "Wulfric"
- traits: [ruthless, practical, saxon_loyalist]
- current_location: place_road_north
- beliefs:
  - narr_norman_oppression: heard=1.0, believes=1.0
  - narr_bandit_territory: heard=1.0, believes=1.0

**char_bandit_1**
- name: "Osric"
- traits: [nervous, young]
- current_location: place_road_north

**char_bandit_2**
- name: "Godwin"
- traits: [cruel, scarred]
- current_location: place_road_north

### Place

**place_road_north**
- name: "The Northern Road"
- description: "A muddy track through dense forest. Easy to ambush."
- region: place_york_region
- atmosphere: tense, isolated

### Player Party

**char_player** (you)
- current_location: place_road_north (traveling)
- destination: place_york

**char_aldric** (companion)
- current_location: place_road_north (with player)
- beliefs about bandits:
  - narr_road_danger: heard=0.8, believes=0.6
- traits: [loyal, cautious, skilled_fighter]

---

## WORLD CHANGES (Background)

- narr_road_ambush: RESOLVED (flipped)
- narr_ambush_encounter: CREATED

---

## NEWS AVAILABLE

(none yet — player was traveling)

---
```

**Why markdown:**
- Narrator is an LLM — reads markdown naturally
- Node names are explicit (char_wulfric, place_road_north)
- All fields present for scene writing
- Structured but readable

---

## Injection: Completed

When player action finishes without interruption:

```typescript
{
  interrupted: false,
  completed: true,
  time_elapsed: 2880,      // Full 2 days
  world_changes: [
    { type: "narrative_created", id: "narr_edmund_move", summary: "Edmund moved politically in York" },
    { type: "pressure_resolved", id: "narr_confrontation" },
    { type: "pressure_created", id: "narr_retaliation", pressure: 0.4 }
  ],
  news_available: [
    { summary: "Edmund's allies spoke against you in York", source: "travelers", reliability: 0.7 },
    { summary: "Norman patrol passed through yesterday", source: "innkeeper", reliability: 0.9 }
  ]
}
```

**As markdown for Narrator:**

```markdown
# WORLD INJECTION
═════════════════

## Status: COMPLETED

**Time elapsed:** 2880 minutes (2 days)
**Action completed:** Travel to York

---

## WORLD CHANGES (While You Traveled)

### Narratives Created

**narr_edmund_move**
- content: "Edmund's allies in York have begun spreading word that Rolf's claim to Thornwick is illegitimate."
- type: account
- truth: 0.3
- about: char_edmund, char_rolf, place_york

### Pressure Resolved

**narr_confrontation** → RESOLVED
- Edmund acted first, politically

### Pressure Created

**narr_retaliation**
- pressure: 0.4
- narratives: [narr_edmund_move, narr_rolf_oath]
- description: "Rolf will not accept Edmund's attack quietly"

---

## NEWS AVAILABLE

| Summary | Source | Reliability |
|---------|--------|-------------|
| "Edmund's allies spoke against you in York" | travelers | 0.7 |
| "Norman patrol passed through yesterday" | innkeeper | 0.9 |

---

## ARRIVAL: York

**place_york**
- name: "York"
- description: "The great northern city. Norman banners fly from the walls."
- atmosphere: tense, watchful
- modifiers: [politically_charged]

---
```

**What Narrator does:** Writes arrival scene. Weaves in news naturally. Uses world_changes to inform what's different.

---


---

## Archived From INPUT_REFERENCE.md

### Complete Example Input
## Complete Example Input

```yaml
WORLD RUNNER INSTRUCTION
════════════════════════

You process flips detected by the graph tick.

TIME_SPAN: 2 days

FLIPS:
  - narrative_id: narr_confrontation
    pressure: 0.95
    breaking_point: 0.90
    trigger_reason: "Pressure accumulated over 2 days of travel. Rolf approaches York where Edmund is."
    narratives:
      - narr_edmund_betrayal
      - narr_rolf_oath
    involved_characters:
      - char_edmund
      - char_rolf
    location: place_york

GRAPH_CONTEXT:

  relevant_narratives:
    - id: narr_edmund_betrayal
      name: "Edmund's Betrayal"
      content: "Edmund stole Thornwick, forged documents, left Rolf to burn. Or so Rolf believes."
      type: enmity
      weight: 0.85
      tone: bitter
      truth: 0.6  # Truth is complicated
      believers: [char_rolf, char_aldric]
      about:
        characters: [char_edmund, char_rolf]
        places: [place_thornwick]
        things: [thing_thornwick_deed]

    - id: narr_rolf_oath
      name: "Rolf's Oath"
      content: "I swore to reclaim what Edmund took. To make him answer for Thornwick."
      type: oath
      weight: 0.78
      tone: cold
      truth: 1.0  # He did swear this
      believers: [char_rolf, char_aldric]
      about:
        characters: [char_rolf, char_edmund]

    - id: narr_edmund_defense
      name: "Edmund's Version"
      content: "Father meant Thornwick for me alone. The fire was Norman raiders, not me."
      type: belief
      weight: 0.4
      tone: defiant
      truth: 0.4  # Partly true
      believers: [char_edmund]
      about:
        characters: [char_edmund, char_rolf]

  character_locations:
    char_edmund: place_york
    char_rolf: place_road_to_york
    char_aldric: place_road_to_york
    char_wulfstan: place_york
    char_gospatric: place_york

  character_beliefs:
    char_rolf:
      narr_edmund_betrayal: { heard: 1.0, believes: 1.0 }
      narr_rolf_oath: { heard: 1.0, believes: 1.0 }
      narr_edmund_defense: { heard: 0.3, believes: 0.0, denies: 0.9 }

    char_edmund:
      narr_edmund_betrayal: { heard: 0.5, believes: 0.0, denies: 1.0 }
      narr_rolf_oath: { heard: 0.8, believes: 0.9 }
      narr_edmund_defense: { heard: 1.0, believes: 1.0 }

    char_aldric:
      narr_edmund_betrayal: { heard: 1.0, believes: 0.7, doubts: 0.3 }
      narr_rolf_oath: { heard: 1.0, believes: 1.0 }

PLAYER_CONTEXT:
  location: place_road_to_york
  engaged_with: char_aldric
  traveling_to: place_york
  recent_action: "Camping for the night, one day from York"

Determine what happened during this time span.
Consider:
- Edmund knows Rolf is coming (rumors travel)
- Edmund has allies in York
- What would Edmund do with a day's warning?

Output JSON matching WorldRunnerOutput schema.
```

---

## Processing Guidance

### What Caused the Flip?

| Flip Pattern | What to Consider |
|--------------|------------------|
| **Contradicting beliefs under pressure** | Believers in opposing narratives were forced together |
| **Oath at moment of truth** | Oath conditions became present |
| **Debt beyond tolerance** | Debt unresolved too long |
| **Secret under exposure** | Knower and subject in same location |
| **Power vacuum collapsing** | Multiple claims + claimants converging |

### Scale to Time Span

| Duration | What Can Happen |
|----------|-----------------|
| Minutes | Almost nothing changes |
| Hours | Local pressure might flip |
| A day | Regional events possible, news travels |
| Days | Multiple breaks, cascades likely |
| Weeks | World transforms significantly |

### Cascade Check

After determining the break, check if it destabilizes other pressure points:
- New contradictions created?
- Proximity changes that increase pressure?
- Belief changes that create conflicts?

Report cascades for the engine to process.

---

## CHAIN

PATTERNS:        ../PATTERNS_World_Runner.md
BEHAVIORS:       ../BEHAVIORS_World_Runner.md
ALGORITHM:       ../ALGORITHM_World_Runner.md
VALIDATION:      ../VALIDATION_World_Runner_Invariants.md
IMPLEMENTATION:  ../IMPLEMENTATION_World_Runner_Service_Architecture.md
TEST:            ../TEST_World_Runner_Coverage.md
INPUTS:          ../INPUT_REFERENCE.md
TOOLS:           ../TOOL_REFERENCE.md
SYNC:            ../SYNC_World_Runner.md
