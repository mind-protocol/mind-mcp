# Narrator Tool Reference

Definitive output schema for narrator responses. For full type definitions, see `docs/schema/SCHEMA.md` and `runtime/models/`.

---

## How To Use

### Orchestrator Call

```bash
# First call (starts session)
claude -p "$(cat narrator_prompt.txt)" --output-format json

# Subsequent calls (continues session)
claude --continue -p "$(cat narrator_prompt.txt)" --output-format json
```

### Validate Mutations (example)

```python
from mind.models import Narrative, NarrativeType
import json

output = json.loads(narrator_response)
for mutation in output.get('mutations', []):
    if mutation['type'] == 'new_narrative':
        Narrative(
            id=mutation['payload']['id'],
            name=mutation['payload']['name'],
            content=mutation['payload']['content'],
            type=NarrativeType(mutation['payload']['type']),
        )
```

---

## Output Schema (NarratorOutput)

```typescript
interface NarratorOutput {
  dialogue?: DialogueChunk[];    // Optional for scene-tree mode
  mutations?: GraphMutation[];   // Changes discovered during generation
  scene: SceneTree | {};         // SceneTree for significant actions, {} for conversational
  time_elapsed?: string;         // Only for significant actions
  seeds?: Seed[];
}
```

---

## SceneTree (Significant Actions)

```typescript
interface SceneTree {
  id: string;
  location: {
    place: string;
    name: string;
    region: string;
    time: string;
  };
  present: string[];
  atmosphere: string[];
  narration: SceneTreeNarration[];
  voices: SceneTreeVoice[];
  freeInput?: SceneTreeFreeInput;
  exits?: {
    travel?: SceneTreeExit;
    wait?: SceneTreeExit;
  };
}
```

### Narration + Clickables

```typescript
interface SceneTreeNarration {
  text: string;
  speaker?: string;
  clickable?: Record<string, SceneTreeClickable>;
}

interface SceneTreeClickable {
  speaks: string;
  intent: string;
  response?: SceneTreeResponse;  // Pre-baked response (optional)
  waitingMessage?: string;       // Required if no response
}
```

---

## Dialogue Chunks (Conversational Actions)

```typescript
interface DialogueChunk {
  speaker?: string;  // Character ID if dialogue, omit for narration
  text: string;
}
```

---

## Graph Mutations

Mutation payloads must validate against Pydantic models in `runtime/models/`.

```typescript
interface GraphMutation {
  type: 'new_character' | 'new_edge' | 'new_narrative' | 'update_belief' | 'adjust_focus';
  payload: Record<string, unknown>;
}
```

---

## Time Elapsed

Only include `time_elapsed` for significant actions (>= 5 minutes).

| Scene Type | Estimate |
|------------|----------|
| Brief reaction | "1-2 minutes" |
| Conversation turn | "5-10 minutes" |
| Deep dialogue | "20-30 minutes" |
| Travel (short) | "2-4 hours" |
| Travel (long) | "1-3 days" |
| Rest/camp | "4-8 hours" |

---

## Validation Rules (Minimum)

1. `scene` is `{}` for conversational actions and SceneTree for significant actions.
2. Every clickable has `speaks` + `intent` and either `response` or `waitingMessage`.
3. Clickable keys appear in the text they annotate.
4. Mutations validate against `runtime/models/`.
