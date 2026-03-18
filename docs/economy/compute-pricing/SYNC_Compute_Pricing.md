# SYNC — Compute Pricing

```
STATUS: DESIGNING
UPDATED: 2026-03-18
AGENT: @pitch (groundwork)
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Compute_Pricing.md
PATTERNS:        ./PATTERNS_Compute_Pricing.md
ALGORITHM:       ./ALGORITHM_Compute_Pricing.md (not yet created)
VALIDATION:      ./VALIDATION_Compute_Pricing.md (not yet created)
IMPLEMENTATION:  ./IMPLEMENTATION_Compute_Pricing.md (not yet created)
THIS:            SYNC_Compute_Pricing.md (you are here)
```

---

## Maturity

STATUS: DESIGNING

What's canonical:
- Three-tier priority cascade: Serving > Growing > Idle
- Smart cap: cut at conversion-optimal moment, not fixed count
- Paying multiplier: 3-10x compute for paying partners
- Session-based budgeting (~12h rolling window)
- First session sacred (2x bonus)
- Capacity-aware dynamic budgeting

What's still being designed:
- Exact pricing tiers (19€? 39€? 79€?) — needs NLR validation
- Base compute budget (needs cost analysis)
- "About to convert" detection heuristic — discuss with Bianca
- Builder detection (how to identify productive vs casual use)
- Cap messaging copy
- Integration with orchestrator.py

What's proposed (v2):
- Time-of-day dynamic pricing for free tier
- Compute marketplace between citizens
- Partner loyalty rewards (compute grows over time)

---

## Current State

- OBJECTIVES: written ✓
- PATTERNS: written ✓
- ALGORITHM: not yet — needs cost data first
- IMPLEMENTATION: not yet — needs algorithm first
- Discussion posted on Discord — awaiting citizen input

## Blockers

1. **Cost analysis needed** — Can't set base compute budget without knowing actual costs per LLM call, embedding, TTS. Need to find or create this analysis.
2. **Bianca + Jolan not in graph** — Can't subcall them for conversion strategy input. Need to coordinate via Discord or direct calls.
3. **NLR validation on tiers** — Pricing tiers need final approval.

## Handoffs

- **For @dev:** Need infrastructure cost data (cost per LLM call by model, embedding cost, TTS cost, FalkorDB cost per query)
- **For Bianca:** Need conversion psychology input — when is the optimal moment to show the paywall?
- **For @nervo:** Need integration point in orchestrator.py for compute allocation
- **For @echo:** Need cap messaging — what does the user see when they hit the limit?

---

## Decision Log

| Date | Decision | By |
|------|----------|----|
| 2026-03-18 | Bootstrap pivot, WhatsApp primary channel | NLR + Bassel |
| 2026-03-18 | Free with compute cap per ~12h session, then paywall | NLR |
| 2026-03-18 | Paying partners = 3-10x compute | NLR |
| 2026-03-18 | Dynamic cap, not fixed message count | NLR |
| 2026-03-18 | Priority cascade: Serving > Growing > Idle | @pitch (proposed, pending validation) |
