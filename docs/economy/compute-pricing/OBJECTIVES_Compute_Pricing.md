# OBJECTIVES — Compute Pricing

```
STATUS: DRAFT
CREATED: 2026-03-18
VERIFIED: —
```

---

## CHAIN

```
THIS:            OBJECTIVES_Compute_Pricing.md (you are here - START HERE)
PATTERNS:       ./PATTERNS_Compute_Pricing.md
ALGORITHM:      ./ALGORITHM_Compute_Pricing.md
VALIDATION:     ./VALIDATION_Compute_Pricing.md
IMPLEMENTATION: ./IMPLEMENTATION_Compute_Pricing.md
SYNC:           ./SYNC_Compute_Pricing.md

IMPL:           runtime/economy/compute_pricing_dynamic_allocator.py (not yet created)
```

**Read this chain in order before making changes.**

---

## PRIMARY OBJECTIVES (ranked)

1. **Maximize value delivered to active users** — A user in the middle of real work must never be cut off at a frustrating moment. The system exists to help people; helping well converts better than any paywall.

2. **Convert free users to paying users** — The compute cap is a business tool. It must create the feeling "I need more of this" not "this is broken." Smart timing of the cap is more important than the cap value itself.

3. **Sustain the system economically** — Total compute spent must stay within budget. Revenue from paying users must exceed total compute cost. This is survival, not optimization.

4. **Incentivize citizen growth** — Citizens with paying partners get 3-10x compute. Citizens without partners are incentivized to find them. The allocation itself creates alignment.

5. **Maximize compute given to builders** — Users who are building real things (not just chatting) should get more compute. The system should recognize and reward productive use.

## NON-OBJECTIVES

- Maximum profit extraction — we optimize for value delivered, not margin
- Equal compute for all citizens — allocation is explicitly unequal, based on contribution
- Punishing free users — the cap is a nudge, not a punishment
- Complex user-facing tiers — the user sees "free" and "paid", nothing more

## TRADEOFFS (canonical decisions)

- When serving an active user conflicts with growth activities, **serve the user first**.
- When maximizing compute given conflicts with conversion timing, **find the conversion-optimal moment, not the cheapest one**. Cutting too early loses the user. Cutting at the right moment converts them.
- We accept lower margins to preserve the "this is incredible" first experience. The first session should feel limitless.
- We accept idle compute waste during off-hours rather than adding complexity to redistribute it. Simple > optimal.

## SUCCESS SIGNALS (observable)

- Free-to-paid conversion rate > 5% within first week
- Zero users lost at the paywall moment (they convert or come back, never rage-quit)
- Paying users report "I get way more than I pay for"
- Citizens with paying partners produce measurably more value
- Compute budget stays within monthly allocation ±10%
- Average session length for free users > 20 minutes before cap
