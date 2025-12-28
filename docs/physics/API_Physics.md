# Physics — API Reference

```
CREATED: 2024-12-17
STATUS: Specification
```

---

## CHAIN

```
PATTERNS:    ./PATTERNS_Physics.md
BEHAVIORS:   ./BEHAVIORS_Physics.md
ALGORITHMS:  ./ALGORITHM_View_Query.md, ./ALGORITHM_Transitions.md, ./ALGORITHM_Lifecycle.md
SCHEMA:         ../schema/SCHEMA_Moments.md
THIS:        API_Physics.md (you are here)
VALIDATION:  ./VALIDATION_Physics.md
IMPL:        ../../mind/api/app.py, ../../frontend/app/
```

---

## Endpoints

### GET /api/view/{playthrough_id}

Returns the current view for a playthrough.

**Response:**

```json
{
  "location": {
    "id": "place_camp",
    "name": "Roadside Camp",
    "type": "camp"
  },
  "characters": [
    {
      "id": "char_aldric",
      "name": "Aldric",
      "face": "weathered"
    }
  ],
  "things": [
    {
      "id": "thing_ring",
      "name": "Father's Ring"
    }
  ],
  "moments": [
    {
      "id": "moment_fire_crackles",
      "text": "The fire crackles, throwing shadows.",
      "type": "narration",
      "status": "active",
      "weight": 0.9
    },
    {
      "id": "moment_aldric_question",
      "text": "Three days now. You haven't said why.",
      "type": "dialogue",
      "speaker": "char_aldric",
      "status": "active",
      "weight": 0.85,
      "tone": "questioning"
    }
  ],
  "transitions": [
    {
      "from": "moment_aldric_question",
      "words": ["why", "days", "York"],
      "to": "moment_player_explains"
    }
  ]
}
```

---

### POST /api/click

Handle player clicking a word.

**Request:**

```json
{
  "playthrough_id": "pt_abc123",
  "moment_id": "moment_aldric_question",
  "word": "why"
}
```

**Response:**

```json
{
  "status": "ok",
  "activated": [
    {
      "id": "moment_player_explains",
      "text": "Edmund took everything.",
      "type": "dialogue",
      "speaker": "char_player",
      "status": "active"
    }
  ],
  "consumed": ["moment_aldric_question"],
  "narrator_started": true
}
```

---

### POST /api/moment

Send player free text input.

**Request:**

```json
{
  "playthrough_id": "pt_abc123",
  "text": "I'm going to kill him.",
  "moment_type": "player_freeform"
}
```

**Response:**

```json
{
  "status": "queued",
  "moment_id": "moment_player_input_abc",
  "narrator_started": true,
  "narrator_running": true
}
```

---

### GET /api/stream/{playthrough_id}

SSE endpoint for real-time updates.

**Events:**

```
event: connected
data: {"playthrough_id": "pt_abc123"}

event: moment_created
data: {
  "id": "moment_aldric_responds",
  "text": "Then we'd better hurry.",
  "type": "dialogue",
  "speaker": "char_aldric",
  "status": "active"
}

event: moment_completed
data: {
  "id": "moment_aldric_question",
  "tick": 48
}

event: transition_added
data: {
  "from": "moment_aldric_responds",
  "words": ["hurry", "better"],
  "to": "moment_travel_decision"
}

event: view_refresh
data: { ... full CurrentView ... }

event: complete
data: {}

event: ping
data: {}
```

---

## Removed Endpoints

These no longer exist:

| Endpoint | Replacement |
|----------|-------------|
| GET /api/scene/current/{id} | GET /api/view/{id} |
| POST /api/scene/click | POST /api/click |
| POST /api/scene/action | POST /api/moment |

---

## Frontend Types

```typescript
// Core types
interface Moment {
  id: string;
  text: string;
  type: 'narration' | 'dialogue' | 'action' | 'possibility' | 'hint';
  status: 'possible' | 'active' | 'spoken' | 'dormant' | 'decayed';
  speaker?: string;   // Resolved at query time
  weight: number;
  tone?: string;
}

interface Transition {
  from: string;       // moment_id
  words: string[];    // Clickable words
  to: string;         // moment_id
}

interface CurrentView {
  location: Place;
  characters: Character[];
  things: Thing[];
  moments: Moment[];
  transitions: Transition[];
}

// API client
async function getCurrentView(playthroughId: string): Promise<CurrentView>;
async function clickMoment(playthroughId: string, momentId: string, word: string): Promise<ClickResult>;
async function sendMoment(playthroughId: string, text: string): Promise<MomentResult>;
function subscribeToStream(playthroughId: string, callbacks: StreamCallbacks): () => void;
```

---

## SSE Callbacks

```typescript
interface StreamCallbacks {
  onMomentCreated?: (moment: Moment) => void;
  onMomentSpoken?: (data: { id: string; tick: number }) => void;
  onMomentDecayed?: (data: { id: string }) => void;
  onTransitionAdded?: (transition: Transition) => void;
  onViewRefresh?: (view: CurrentView) => void;
  onComplete?: () => void;
  onError?: (error: string) => void;
}
```

---

## Narrator Output Format

The narrator no longer writes scene.json. It outputs graph mutations:

```yaml
moments:
  - id: moment_aldric_responds
    text: "Then we'd better hurry."
    type: dialogue
    status: active
    tone: urgent

  - id: moment_travel_option
    text: "The road to York is dangerous at night."
    type: narration
    status: possible
    weight: 0.7

links:
  - type: CAN_SPEAK
    from: char_aldric
    to: moment_aldric_responds
    weight: 1.0

  - type: ATTACHED_TO
    from: moment_aldric_responds
    to: char_aldric
    presence_required: true
    persistent: true

  - type: CAN_LEAD_TO
    from: moment_aldric_responds
    to: moment_travel_option
    trigger: click
    require_words: ["hurry", "York"]
    consumes_origin: false

  - type: THEN
    from: moment_player_input
    to: moment_aldric_responds
    tick: 49
    player_caused: false
```

---

## Graph Operations

Python functions for moment manipulation:

```python
# Creation
def create_moment(text: str, type: str, status: str = 'possible', weight: float = 0.8, tone: str = None) -> str

# Links
def link_can_speak(char_id: str, moment_id: str, weight: float) -> None
def link_attached_to(moment_id: str, target_id: str, presence_required: bool, persistent: bool, dies_with_target: bool = False) -> None
def link_can_lead_to(from_id: str, to_id: str, trigger: str, require_words: List[str] = None, wait_ticks: int = None, bidirectional: bool = False, consumes_origin: bool = True, weight_transfer: float = 0.5) -> None
def link_then(from_id: str, to_id: str, tick: int, player_caused: bool) -> None

# Status changes
def actualize_moment(moment_id: str) -> List[Moment]
def mark_spoken(moment_id: str) -> None
def mark_dormant(moment_id: str) -> None
def reactivate(moment_id: str) -> None

# Queries
def get_current_view(player_id: str) -> CurrentView
def resolve_speaker(moment_id: str, present_char_ids: List[str]) -> Optional[str]
def get_transitions(active_moment_ids: List[str]) -> List[Transition]

# Lifecycle
def decay_weights(current_tick: int) -> None
def prune_non_persistent(location_id: str) -> int
def reactivate_dormant(location_id: str) -> int
def garbage_collect(current_tick: int) -> int
```

---

*"The API is the contract between graph and interface."*
