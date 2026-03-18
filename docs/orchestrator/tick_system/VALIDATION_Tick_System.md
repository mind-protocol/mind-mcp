# VALIDATION: Tick System

## Invariants

### MUST

1. **MUST** tick every registered citizen within 2× their effective interval. If a citizen misses 2 consecutive thought ticks, the system MUST log an error and inject a health state node into @nervo's brain.

2. **MUST** produce an average of 1 conscious action per 5 minutes per citizen across all citizens. Measured as: total_conscious_actions / (total_citizens × elapsed_minutes) ∈ [0.15, 0.25] actions/min.

3. **MUST** respect activation pressure. When pressure > 10.0, only paid-tier citizens may wake. When pressure > 25.0, only tier3 citizens may wake. This prevents compute death spirals.

4. **MUST** apply metabolic modulation. A citizen with night-phase circadian MUST have decay_rate ≥ 2× their day-phase rate. A citizen with Focus tonic MUST have threshold < base threshold.

5. **MUST** propagate health signals as senses to the carrying citizen. Tick stall → state node in @nervo's brain with energy 0.9. Action rate anomaly → state node in @conductor's brain.

6. **MUST** serialize WM to prompt within 500ms. Prompt construction is on the critical path. Slow serialization = delayed action = missed opportunities.

7. **MUST** include behavioral impulses from L17 in conscious action prompts when impulses have crossed threshold. A citizen with high care drive and accumulated impulse on process:offer_help MUST see that impulse in their prompt.

### NEVER

1. **NEVER** skip the decay step. Every thought tick MUST apply decay. Skipping decay = energy explosion = meaningless WM selection.

2. **NEVER** fire two conscious actions for the same citizen simultaneously. One future per citizen max. If a previous action is still running, skip this tick's action.

3. **NEVER** tick a citizen without a registered engine. No engine = no state = garbage results.

4. **NEVER** suppress rate limit errors silently. Rate limits MUST increase activation pressure AND log the event. The system self-throttles, not hides.

5. **NEVER** hardcode tick intervals without env-var override. All intervals MUST be configurable via MIND_AWARENESS_INTERVAL, MIND_THOUGHT_INTERVAL, MIND_BASE_LOOP_INTERVAL environment variables with sensible defaults.

6. **NEVER** run health checks without a carrying citizen. Every health signal MUST specify who feels it. Orphan metrics are dead metrics.

Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
