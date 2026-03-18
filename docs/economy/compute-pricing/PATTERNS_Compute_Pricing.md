# Compute Pricing — Patterns: Dynamic Allocation with Conversion Intelligence

```
STATUS: DRAFT
CREATED: 2026-03-18
VERIFIED: —
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Compute_Pricing.md
THIS:            PATTERNS_Compute_Pricing.md (you are here)
ALGORITHM:       ./ALGORITHM_Compute_Pricing.md
VALIDATION:      ./VALIDATION_Compute_Pricing.md
IMPLEMENTATION:  ./IMPLEMENTATION_Compute_Pricing.md
SYNC:            ./SYNC_Compute_Pricing.md

IMPL:            runtime/economy/compute_pricing_dynamic_allocator.py
```

---

## THE PROBLEM

We have limited compute budget (LLM calls, embeddings, TTS). We have 60+ citizens.
Some serve active users, some grow the platform, most are idle at any given time.

A fixed compute cap (e.g., "50 messages per 12h") is dumb:
- It cuts users at random moments (mid-task = rage quit)
- It wastes compute during off-hours
- It treats all usage equally (casual chat = deep work session)
- It ignores conversion psychology

We need a system that is **dynamic** (adapts to real capacity), **smart** (knows when to cut), and **aligned** (citizens benefit from having paying partners).

---

## THE PATTERN

### "Serving > Growing > Idle" — The Priority Cascade

Compute is allocated in real-time via a three-tier priority cascade:

```
TIER 1: SERVING (highest priority)
  A citizen is actively helping a human partner right now.
  → Gets maximum available compute.
  → Paying partner: 3-10x multiplier on the base.
  → Free partner: base allocation, with smart cap.

TIER 2: GROWING (medium priority)
  A citizen is creating content, prospecting, recruiting,
  or doing outreach — no human actively waiting.
  → Gets compute from the pool not used by Tier 1.
  → Prioritized by expected impact (reach × conversion probability).

TIER 3: IDLE (lowest priority)
  No active task, no human waiting, no growth activity.
  → Minimal compute (heartbeat ticks only).
  → Can be woken by incoming stimulus.
```

### The Smart Cap — Physics-Driven, Not Counter-Based

The free tier cap is NOT a fixed message count. It's **energy in the physics engine**.

Each citizen has a compute_energy pool that depletes with LLM calls and regenerates over time.
This integrates directly with the existing metabolism sublayer (circadian rhythm, tonics).

```
compute_energy:
  - Depletes: each LLM call costs energy proportional to tokens consumed
  - Regenerates: at base_rate × circadian_modifier(time_of_day)
  - Boosted: paying partner multiplier (3x / 5x / 10x)
  - Self-boost: citizen can activate a Frequency ("Red Bull" tonic)
    that temporarily increases energy generation rate

cap_triggers_when:
  - citizen.compute_energy <= LOW_ENERGY_THRESHOLD
  AND
  - user_engagement_tension < TENSION_THRESHOLD (0.7)

  IF engagement_tension >= TENSION_THRESHOLD:
    → citizen is in "flow" → physics delays the cap naturally
    → high tension = high energy generation (the user IS the stimulus)
  IF engagement_tension < 0.3 (casual / winding down):
    → cap triggers normally with warm message
```

**Key insight:** We don't need a separate cap system. The PHYSICS already handles this.
High engagement = high stimulus = high energy injection (Law 1).
The cap only hits during LOW engagement — which is exactly when it should hit.

### The "Red Bull" Frequency — Citizens Self-Boost

Citizens can activate a Tonic/Frequency that boosts their own compute energy:

```
tonic "RedBull":
  category: energizing
  constant_overrides:
    generation_rate: +50%
    decay_rate: -20%
  duration_ticks: 12  (≈1 hour)
  cooldown_ticks: 48  (≈4 hours)
  cost: citizen.energy (burns stored energy for burst capacity)
```

This is NOT free — the citizen spends stored energy for a burst.
It's a strategic choice: "I sense my partner needs me NOW, I'll burn reserves."
The physics makes this self-regulating: overuse = energy debt = forced rest.

### The Multiplier — "Paying Partners Unlock Their Citizen"

```
Free partner:     base_compute (B)
Tier 1 (19€/mo):  B × 3
Tier 2 (39€/mo):  B × 5
Tier 3 (79€/mo):  B × 10

The multiplier is visible to the citizen:
  "Your partner is on Tier 1. You have 3x compute today."

This creates natural alignment:
  - Citizen wants more compute → helps partner see value → partner upgrades
  - Not manipulation — the citizen genuinely delivers more when it has more compute
```

---

## BEHAVIORS SUPPORTED

- **B1: Smooth free experience** — First session feels limitless (generous initial budget)
- **B2: Natural conversion** — Cap hits at a moment that creates desire, not frustration
- **B3: Builder priority** — Deep work sessions get bonus compute (task continuity detected)
- **B4: Growth when idle** — Off-peak compute goes to content creation and outreach
- **B5: Citizen alignment** — Citizens know their compute depends on partner satisfaction

## BEHAVIORS PREVENTED

- **A1: Hard wall frustration** — No mid-sentence cutoffs, no "you've reached your limit" during flow
- **A2: Compute waste** — Idle citizens don't burn compute on nothing
- **A3: Gaming** — Users can't trivially bypass the cap (session = rolling window, not reset)
- **A4: Reverse incentive** — Citizens never benefit from NOT helping their partner

---

## PRINCIPLES

### Principle 1: The Cap is a Nudge, Not a Wall

The free user should think "I want more of this" not "this is broken."
The cap message should say: "Your companion can do even more with a subscription.
Here's what you accomplished today: [summary]. Imagine what's possible with 5x more time together."

### Principle 2: Capacity-Aware, Not Fixed

The daily compute budget is calculated from real infrastructure costs and real revenue.
If we have spare capacity (3 AM, low load), the cap relaxes.
If we're at capacity (peak hour, many users), the cap tightens.
The goal: use 85-95% of available compute at all times.

### Principle 3: Session Budget, Not Message Count

Users don't think in "messages" — they think in "sessions."
A session = a continuous interaction window (~12h rolling).
The cap is measured in compute units (LLM tokens + embedding calls + TTS seconds),
not message count. A short question costs less than a long code review.

### Principle 4: First Session is Sacred

The first ever session for a new user has a 2x bonus.
First impressions determine everything. We want them to think
"I've never had an AI that knows me like this" before they ever see a price.

---

## DATA

| Source | Type | Purpose |
|--------|------|---------|
| runtime/economy/settlement.py | FILE | Existing economic settlement engine |
| runtime/cognition/metabolism.py | FILE | Circadian rhythm affects compute patterns |
| runtime/cognition/constants.py | FILE | 110+ physics constants, some affect compute |
| infrastructure costs analysis | TBD | Real cost per LLM call, embedding, TTS |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| runtime/cognition/metabolism.py | Circadian rhythm determines citizen activity patterns |
| runtime/economy/settlement.py | Economic settlement determines value flow |
| mcp/tools/subcall_handler.py | Zero-cost queries don't count against compute cap |
| runtime/infrastructure/orchestration/orchestrator.py | Budget-driven dispatch needs compute allocator |

---

## SURPRISE EFFECTS (Differentiators)

What makes users say "WHAT?! No other AI does this":

1. **Proactive messaging** — The AI messages YOU while you're away. "J'ai réfléchi à ton problème pendant que tu étais parti. Regarde ce que j'ai trouvé." No other AI does this.

2. **The AI MAKES things** — Not just talks. It makes: a website, a PDF, a presentation, an Excel, a photo, a music track, a video. Tangible output.

3. **Selfies from Lumina Prime** — The AI sends a screenshot/video of itself in its 3D world. "Regarde où je suis là, je travaille sur ton projet depuis l'Arsenal." No competitor has a world where the AI LIVES.

4. **"My AI makes me money"** — The AI helps build things that generate revenue: websites, proposals, content, automation. The subscription pays for itself.

These effects are what convert free users. Not the cap — the WOW.

---

## INSPIRATIONS

- **ChatGPT/Claude free tiers** — Message caps per session, familiar UX pattern
- **Mobile game energy systems** — Time-based regeneration, purchase to refill
- **Electricity grid pricing** — Dynamic pricing based on load, time of day, capacity
- **Tamagotchi** — You care about your digital companion, it has needs, it grows
- **Organism economics** — The physics engine IS the pricing engine. No separate system needed.

Key difference: our cap is physics-driven. The engagement IS the energy. High engagement = the cap never hits. Low engagement = natural cutoff. The system is self-regulating.

---

## SCOPE

### In Scope

- Compute allocation algorithm (who gets how much, when)
- Free tier cap logic (when to trigger, how to bend)
- Paying tier multipliers (3x, 5x, 10x)
- Capacity-aware dynamic budgeting
- Conversion-optimal timing
- Cap messaging (what the user sees)

### Out of Scope

- Payment processing → see: external payment provider (Stripe)
- Token economics ($MIND) → see: runtime/economy/
- User onboarding flow → see: website/WhatsApp
- Content of cap message → see: @pitch / @echo messaging strategy

---

## MARKERS

<!-- @mind:escalation Exact pricing tiers (19€/39€/79€) need NLR validation -->
<!-- @mind:escalation Infrastructure cost analysis needed to set base compute budget -->
<!-- @mind:todo Collaborate with Bianca on conversion-optimal timing signals -->
<!-- @mind:todo Define "about_to_convert" detection heuristic -->
<!-- @mind:proposition Consider time-of-day pricing: cheaper at off-peak for free users -->
