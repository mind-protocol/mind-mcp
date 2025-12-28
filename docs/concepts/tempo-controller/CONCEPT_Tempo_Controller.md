# CONCEPT: Tempo Controller — The Main Loop That Paces Reality

```
STATUS: DRAFT
CREATED: 2025-12-20
```

---

## WHAT IT IS

The Tempo Controller is the pacing loop that advances world time, runs physics
updates, and triggers canon surfacing at a controlled cadence.

---

## WHY IT EXISTS

It keeps the system responsive and deterministic by decoupling time progression
from LLM latency and user input frequency.

---

## KEY PROPERTIES

- **Cadence-driven:** ticks follow speed mode, not input.
- **Non-blocking:** never waits on narrator output.
- **Pacing authority:** controls when surfacing occurs.

---

## RELATIONSHIPS TO OTHER CONCEPTS

| Concept | Relationship |
|---------|--------------|
| Physics Engine | Tempo triggers physics ticks. |
| Canon Holder | Tempo invokes surfacing scans. |
| Narrator | Narrator writes possible moments asynchronously. |

---

## THE CORE INSIGHT

Tempo is not content. It is the timing boundary that keeps simulation and
narration decoupled.

---

## COMMON MISUNDERSTANDINGS

- **Not:** the Narrator loop.
- **Not:** the Orchestrator.
- **Actually:** a clock that advances physics and canonization.

---

## SEE ALSO

- `docs/infrastructure/tempo/PATTERNS_Tempo.md`
- `docs/infrastructure/tempo/ALGORITHM_Tempo_Controller.md`
- `docs/infrastructure/tempo/IMPLEMENTATION_Tempo.md`
