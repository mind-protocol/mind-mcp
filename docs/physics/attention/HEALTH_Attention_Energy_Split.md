# Physics — Health: Attention Energy Split

```
STATUS: DRAFT
CREATED: 2025-12-21
```

---

## CHECKS

- Attention split conserves budget (sum alloc == E).
- Lagging inputs produce deterministic outputs.
- No sinks outside the neighborhood are allocated.

---

## AUTOMATED

```bash
pytest mind/tests/test_physics_mechanisms.py -k attention
```

