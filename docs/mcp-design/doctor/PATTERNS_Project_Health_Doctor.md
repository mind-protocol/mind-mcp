# PATTERNS: Project Health Doctor

**Why a holistic health check instead of just validation?**

---

## THE PROBLEM

Validation checks correctness: "Do files exist? Are links valid?"

But projects have deeper health issues validation can't catch:
- Code that outgrew its structure (monoliths)
- Documentation that drifted from code
- Work that stalled without anyone noticing
- Patterns that eroded over time

These issues compound silently until they become crises.

---

## THE INSIGHT

**Health is about trajectory, not just state.**

A project can pass all validation checks and still be unhealthy:
- Every file exists, but half are stale
- Every link works, but the code moved on
- Every module is mapped, but three are abandoned

Health requires looking at:
1. **Size** — Is anything too big?
2. **Staleness** — Is anything too old?
3. **Coverage** — Is anything undocumented?
4. **Coherence** — Do docs match code?

---

## DESIGN DECISIONS

### Severity Tiers

Three tiers with clear criteria:

| Tier | Meaning | Action |
|------|---------|--------|
| **Critical** | Blocking issue, fix now | Breaks workflow |
| **Warning** | Should fix soon | Quality degrading |
| **Info** | Consider addressing | Opportunity |

Why tiers? So developers know what to prioritize. A monolith file is worse than a missing TEST doc.

### Health Score

A single number (0-100) that summarizes project health.

**Why a score?**
- Trackable over time
- Motivates improvement
- Quick gut check

**Scoring approach:**
- Start at 100
- Deduct for each issue (critical=-10, warning=-3, info=-1)
- Floor at 0

### Actionable Output

Every issue includes:
1. What's wrong (specific file/module)
2. Why it matters
3. How to fix (VIEW reference or command)

Don't just report problems — guide solutions.

### Thresholds

Configurable in `.mind/config.yaml`:

```yaml
doctor:
  monolith_lines: 500
  god_function_lines: 100
  stale_days: 14
  nesting_depth: 4
```

Why configurable? Projects have different tolerances. A CLI tool can have bigger files than a React app.

---

## WHAT WE CHECK

### Documentation Health
- **Undocumented code**: Code directories with no docs
- **Placeholder docs**: Files still containing `{template}`
- **Orphaned docs**: Docs pointing to deleted code
- **Stale SYNC**: Not updated recently
- **Incomplete chains**: Missing doc types

### Code Health
- **Monolith files**: Too many lines
- **God functions**: Functions too long
- **Deep nesting**: Complexity smell
- **No DOCS reference**: Code missing pointer to docs
- **Circular dependencies**: Module A→B→A

### Project Health
- **Stuck modules**: DESIGNING with no activity
- **TODO rot**: Backlog items aging out
- **Test gaps**: Modules with no tests

### Manifest Health
- **Missing mappings**: Code not in modules.yaml
- **Stale maturity**: CANONICAL but high churn
- **Missing deps**: Imports not in depends_on

---

## WHAT WE DON'T CHECK

**Runtime behavior** — We're static analysis only. No test execution.

**Code quality** — No linting, formatting, style. Use dedicated tools.

**Security** — No vulnerability scanning. Use security tools.

**Performance** — No profiling. Use profilers.

The doctor focuses on **structural health** — the shape of your project.

---

## ALTERNATIVES CONSIDERED

### Just extend validate

Rejected. Validate is pass/fail correctness. Doctor is advisory health. Different purposes, different UX.

### Integrate with existing linters

Rejected. Linters check code style. We check project structure. Orthogonal concerns.

### Machine learning for "health"

Rejected. Too opaque. Developers need to understand why something is flagged. Rules are transparent.

---

## CHAIN

```
PATTERNS:        THIS
BEHAVIORS:       ./BEHAVIORS_Project_Health_Doctor.md
ALGORITHM:       ./ALGORITHM_Project_Health_Doctor.md
VALIDATION:      ./VALIDATION_Project_Health_Doctor.md
HEALTH:          ./HEALTH_Project_Health_Doctor.md
SYNC:            ./SYNC_Project_Health_Doctor.md
```
