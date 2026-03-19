# Skill: `mind.eliminate_constants`
@mind:id: SKILL.QUALITY.ELIMINATE_CONSTANTS.DERIVE_FROM_SYSTEM

## Maps to VIEW
`VIEW_Review` (quality pass) or `VIEW_Implement` (during new code)

---

## Context

Constants are lies frozen in time.

A constant says "this value is correct forever." But systems evolve. Citizens are added. Ticks speed up. Pressure changes. Tiers are restructured. The constant stays the same while the world moves around it. Eventually the constant is wrong, and nobody knows it because nobody re-derives it.

```
Constant:  THRESHOLD = 0.5          # why 0.5? who decided? when? is it still right?
Derived:   threshold = mean - 2σ    # from the data's own distribution. Always right.
```

The difference matters because:

1. **Constants hide assumptions.** `RED_THRESHOLD = 0.5` assumes 50% is always the right boundary. But a flow with 99% baseline should alert at 95%. A flow with 70% baseline should alert at 50%. The constant treats both the same. The derivation treats each according to its own history.

2. **Constants duplicate knowledge.** `PRESSURE_BREAKPOINT = 15.0` duplicates the tier structure from `activation_pressure.py`. When the tiers change, this constant doesn't. Now two modules disagree about what "high pressure" means.

3. **Constants can't self-repair.** When a constant is wrong, it stays wrong until a human notices. A derived value auto-corrects because it reads from the source of truth every time it's evaluated.

4. **Constants resist composition.** Two modules with their own constants can't interoperate cleanly. Two modules that derive from shared state compose naturally — they agree because they read from the same source.

### The Mind Protocol principle

> "If behavior needs a hardcoded rule, the architecture is wrong.
> Design structures where desired behavior is energetically favorable."

Constants ARE hardcoded rules. Every constant is an opportunity to derive from system state instead. Not every constant CAN be eliminated (physical constants like pi exist for a reason), but every constant in a Mind Protocol codebase should be challenged: "Is this a property of the universe, or a property of our system? If it's our system, the system itself should define it."

### What replaces constants

| Constant type | Replacement strategy |
|---------------|---------------------|
| Thresholds (RED=0.5, etc.) | Statistical: mean ± Nσ from the data's own distribution |
| Time windows (300s, 60s) | Derived from the system's own rhythm (tick interval, attempt rate) |
| Capacity limits (max=15) | Derived from available resources (accounts, memory, CPU) |
| Pressure breakpoints | Read from the module that owns them (activation_pressure tiers) |
| Length/size checks (>100 chars) | Percentile from the data's own distribution (p5, p95) |
| Calibration counts (min=5) | Statistical confidence (std_error < threshold from the mean) |
| Debounce intervals | Derived from the consumer's processing speed (thought_interval) |
| Energy levels (0.8, 0.5) | Proportional to severity (continuous function of distance-to-baseline) |

---

## Purpose

Identify and eliminate hardcoded constants in Mind Protocol code, replacing each with a value derived from the system's own state, history, or structure. The goal: every threshold adapts to the system as it evolves, with zero manual tuning.

---

## Inputs

```yaml
target: "<file path or module path>"      # what to audit
scope: "file|module|area|full"            # how wide to search
```

## Outputs

```yaml
audit:
  constants_found: <int>
  constants_eliminated: <int>
  constants_kept: <int>                    # physical constants, true invariants
  replacements:
    - location: "<file:line>"
      was: "<constant and its value>"
      now: "<derivation and its source>"
      why: "<what assumption the constant hid>"
```

---

## Gates

- File or module must be read before auditing — no blind search-and-replace
- The doc chain for the module must exist — replacement sources must be documented
- Every replacement must be tested: run the module after changes and verify behavior doesn't break
- Constants that ARE physical/mathematical truths (pi, e, byte sizes) are kept — document why

---

## Process

### 1. Identify constants

Search the target for:

```yaml
patterns:
  - "^[A-Z_]+ = "                    # module-level ALL_CAPS assignments
  - "if .* [<>]=? \\d"               # numeric comparisons in conditionals
  - "default[=:].*\\d"               # default values in function signatures
  - "timeout.*\\d"                    # timeout values
  - "max.*\\d|min.*\\d"              # capacity limits
  - "threshold.*\\d"                 # threshold values
  - "\.get\(.*,.*[\"']\\d"          # os.environ.get with numeric defaults
```

For each constant found, ask:
1. **Is this a physical/mathematical constant?** (pi, byte sizes, HTTP status codes) → KEEP
2. **Is this a property of our system?** (thresholds, windows, limits) → REPLACE
3. **Does this value appear in more than one file?** → DEFINITELY REPLACE (knowledge duplication)

### 2. Find the source of truth

For each constant to replace, identify where the "right" value comes from:

| The constant controls... | The source of truth is... |
|--------------------------|--------------------------|
| A threshold for "good vs bad" | The data's own statistical distribution (mean, σ, percentiles) |
| A time interval | The system's own rhythm (tick_interval, thought_interval, attempt_rate) |
| A capacity limit | The system's available resources (account count, worker count) |
| A pressure/tier boundary | The module that owns that concept (activation_pressure, metabolism) |
| A size/length check | The historical distribution of sizes in that flow |
| A calibration requirement | Statistical confidence from the data (standard error) |

### 3. Write the derivation

Replace the constant with a function or expression that reads from the source:

```python
# BEFORE (constant)
RED_THRESHOLD = 0.5
if ratio < RED_THRESHOLD:
    return "RED"

# AFTER (derived)
def _is_red(ratio, history):
    mean = statistics.mean(history)
    std = statistics.stdev(history) if len(history) > 1 else mean * 0.1
    return ratio < mean - 2 * std   # 2σ below mean = outside 95% of normal
```

Rules for derivations:
- **Must be readable.** A derivation that nobody can understand is worse than a constant.
- **Must be cheap.** Derivations run on every evaluation. O(n) over a bounded history is fine. Graph queries per tick are not.
- **Must handle cold start.** When there's no history yet, the derivation must not crash or produce absurd values. Use a bootstrap strategy (accept higher uncertainty, use structural checks instead).
- **Must have a floor.** Zero-based derivations (empty history → threshold=0) make failures invisible. Always maintain a minimum expectation.

### 4. Update the doc chain

For each replacement:
- ALGORITHM: update pseudocode to show the derivation, not the constant
- VALIDATION: update invariants to reference the derivation source
- IMPLEMENTATION: update file map with new dependencies (if reading from other modules)
- SYNC: record the replacement in recent changes

### 5. Verify

After all replacements:
- Run the module — does it behave the same for typical inputs?
- Test edge cases: empty history, single data point, extreme values
- Verify cold start: does the module boot cleanly with no prior data?
- Check for circular dependencies: does module A read from B which reads from A?

---

## Anti-patterns

### Don't replace constants with configuration

```python
# BAD: moved the constant to an env var — still a constant, just harder to find
THRESHOLD = float(os.environ.get("MY_THRESHOLD", "0.5"))

# GOOD: derived from the data
threshold = _compute_threshold_from_history(flow_history)
```

Env vars are constants with extra steps. They still require a human to set the right value. The goal is values that are ALWAYS right because they come from the system itself.

### Don't over-derive

Some values ARE constants of the universe:
- HTTP 200 = success (protocol spec, not our system)
- 60 seconds per minute (physics, not our system)
- AES-256 key length (crypto spec, not our system)

Don't try to derive these. The test: "Would this value be different if our system worked differently?" If no → keep it. If yes → derive it.

### Don't create circular dependencies

If module A's threshold depends on module B's output, and module B's threshold depends on module A's output, both modules are stuck waiting for each other.

Break cycles by using time-lagged values: A reads B's PREVIOUS output (from last tick), not current.

---

## Evidence

- Constants: `file:line + value`
- Replacements: `file:line + derivation source + derivation formula`
- Verification: `test output before vs after`

## Markers

- `@mind:TODO constant:{file}:{line} — replace {CONSTANT} with derived value from {source}`
- `@mind:proposition constant:{file}:{line} — could derive from {idea} but needs {clarification}`
- `@mind:escalation constant:{file}:{line} — unsure if this is a system property or a physical constant`

## Never-stop

If unsure whether a value is a true constant or a system property → `@mind:escalation` with your reasoning + `@mind:proposition` with a derivation idea → proceed with the proposition, flag uncertainty. Better to derive and learn it's a true constant than to keep a wrong assumption frozen in code.
