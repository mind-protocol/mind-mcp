# Silence Sentinel — Algorithm: Detection and Routing Logic

```
STATUS: DESIGNING
CREATED: 2026-03-19
```

---

## CHAIN

```
RESULTS:         ./RESULTS_Silence_Sentinel.yaml
OBJECTIVES:      ./OBJECTIVES_Silence_Sentinel.md
PATTERNS:        ./PATTERNS_Silence_Sentinel.md
BEHAVIORS:       ./BEHAVIORS_Silence_Sentinel.md
THIS:            ALGORITHM_Silence_Sentinel.md (you are here)
VALIDATION:      ./VALIDATION_Silence_Sentinel.md
IMPLEMENTATION:  ./IMPLEMENTATION_Silence_Sentinel.md
HEALTH:          ./HEALTH_Silence_Sentinel.md
SYNC:            ./SYNC_Silence_Sentinel.md

IMPL:            runtime/orchestrator/silence_counter.py
```

---

## OVERVIEW

The Silence Sentinel has two components: a **counter** (records attempts and successes per flow) and a **sense** (evaluates the ratio against a self-calibrating baseline). The counter is called inline by instrumented flows. The sense runs every tick as part of the dispatcher loop.

---

## DATA STRUCTURES

### FlowCounter

```
FlowCounter:
  flow_name: str                    # e.g. "invoke_claude"
  buckets: deque[Bucket]            # circular buffer, one per minute, last 60

Bucket:
  timestamp: int                    # minute-aligned epoch
  attempted: int                    # calls attempted
  substantive: int                  # calls that produced real output
```

### SentinelState (per flow)

```
SentinelState:
  flow_name: str
  observations: int                 # total evaluations since boot
  rolling_baseline: float           # 1h average ratio
  last_ratio: float                 # most recent 5min ratio
  last_status: str                  # GREEN/YELLOW/RED/CALIBRATING
  last_evaluated: float             # epoch timestamp
```

---

## ALGORITHM 1: Counter Recording

Called inline by every instrumented flow. MUST be zero-cost on failure.

### Step 1: Record Attempt

```
def record_attempt(flow_name):
  bucket = get_or_create_current_bucket(flow_name)
  bucket.attempted += 1
```

### Step 2: Record Success

```
def record_success(flow_name):
  bucket = get_or_create_current_bucket(flow_name)
  bucket.substantive += 1
```

### Step 3: Bucket Management

```
def get_or_create_current_bucket(flow_name):
  now_minute = int(time.time()) // 60 * 60
  counter = counters[flow_name]
  if not counter.buckets or counter.buckets[-1].timestamp != now_minute:
    counter.buckets.append(Bucket(timestamp=now_minute, attempted=0, substantive=0))
    # Prune: keep only last 60 minutes
    while len(counter.buckets) > 60:
      counter.buckets.popleft()
  return counter.buckets[-1]
```

**Complexity:** O(1) per call. No I/O, no graph queries, no locks (GIL-safe for single-threaded counter access within the dispatcher thread).

---

## ALGORITHM 2: Silence Evaluation (runs every tick)

### Step 1: Compute 5-minute Ratio

```
def compute_ratio(flow_name, window_seconds=300):
  cutoff = time.time() - window_seconds
  attempted = 0
  substantive = 0
  for bucket in counters[flow_name].buckets:
    if bucket.timestamp >= cutoff:
      attempted += bucket.attempted
      substantive += bucket.substantive
  if attempted == 0:
    return None, 0   # no attempts — silence behavior applies
  return substantive / attempted, attempted
```

### Step 2: Compute Rolling Baseline

```
def compute_baseline(flow_name, pressure, circadian_factor):
  # Rolling 1h ratio (all 60 buckets)
  total_attempted = sum(b.attempted for b in counters[flow_name].buckets)
  total_substantive = sum(b.substantive for b in counters[flow_name].buckets)

  if total_attempted < 10:
    return None  # not enough data for baseline

  raw_baseline = total_substantive / total_attempted

  # Adjust for system context
  # High pressure = lower expected rate (deliberate throttle)
  pressure_factor = 1.0 if pressure < 5.0 else 0.5 if pressure < 15.0 else 0.2

  # Circadian: night = lower expected rate
  # circadian_factor from metabolism: 1.0 = peak, 0.5 = trough

  adjusted_baseline = raw_baseline * pressure_factor * circadian_factor
  return max(adjusted_baseline, 0.1)  # floor: never expect 0 output
```

### Step 3: Evaluate Status

```
def evaluate(flow_name, pressure, circadian_factor):
  state = sentinel_states[flow_name]
  state.observations += 1

  # Calibration gate
  if state.observations < CALIBRATION_MIN (default 5):
    ratio, sample = compute_ratio(flow_name)
    if ratio is not None and ratio == 0.0 and sample >= 10:
      return "RED"  # complete silence with 10+ attempts = broken even during calibration
    return "CALIBRATING"

  ratio, sample = compute_ratio(flow_name)

  # No attempts case
  if ratio is None:
    return state.last_status  # hold previous (on_silence behavior)

  baseline = compute_baseline(flow_name, pressure, circadian_factor)
  if baseline is None:
    return "CALIBRATING"

  state.rolling_baseline = baseline
  state.last_ratio = ratio

  # Evaluate against baseline
  if ratio >= baseline * 0.8:
    return "GREEN"           # within 20% of expected — healthy
  elif ratio >= baseline * 0.5:
    return "YELLOW"          # 50-80% of expected — degraded
  else:
    return "RED"             # below 50% of expected — broken
```

### Step 4: Route Stimulus (if RED or YELLOW)

```
def route_silence_stimulus(flow_name, status, ratio, baseline, sample):
  if status == "GREEN" or status == "CALIBRATING":
    return  # nothing to route

  stimulus_content = (
    f"[SILENCE DETECTED] {flow_name}: ratio={ratio:.2f} "
    f"(expected={baseline:.2f}, sample={sample}). "
    f"Status: {status}."
  )

  energy = 0.8 if status == "RED" else 0.5  # RED = urgent, YELLOW = attention

  # Auto-route: inject stimulus into graph, let physics find best actor
  # Uses existing inject_stimulus which routes via trust × availability × domain
  dispatcher.inject_stimulus(
    target="infra",              # domain filter — infra actors only
    content=stimulus_content,
    source="silence_sentinel",
    energy=energy,
    is_failure=(status == "RED"),
  )
```

---

## KEY DECISIONS

### D1: "Substantive" Classification Per Flow

```
IF flow == "invoke_claude":
    substantive = (
      len(response) > 100
      AND NOT response.startswith("*[Subconscious response")
      AND NOT any(p in response.lower() for p in SUPPRESS_PATTERNS)
    )
ELIF flow == "bridge_telegram" or flow == "bridge_whatsapp":
    substantive = (http_status == 200 AND delivery_confirmed)
ELIF flow == "graph_write":
    substantive = (affected_count > 0)
ELIF flow == "awareness_tick":
    substantive = (nodes_imported > 0 OR wm_changed)
```

### D2: Window Size (5 min vs 1 min vs 15 min)

```
5 minutes chosen because:
  - 1 min: too reactive. Single slow invocation = false alarm.
  - 15 min: too slow. The Popen bug would have run 15 min undetected.
  - 5 min: ~60 invocations at normal rate (1/5s per citizen × 210 citizens / 15 workers).
    Statistically meaningful sample. Fast enough to catch sudden drops.
```

---

## DATA FLOW

```
[Instrumented flow] → silence_counter.record_attempt(flow_name)
         ↓
[Flow executes]
         ↓
[If substantive result] → silence_counter.record_success(flow_name)
         ↓
[Every tick] → evaluate(flow_name) → {GREEN, YELLOW, RED, CALIBRATING}
         ↓
[If RED/YELLOW] → route_silence_stimulus() → inject_stimulus(target="infra")
         ↓
[Physics routes] → best available infra actor's L1 brain
         ↓
[Actor's WM shifts] → conscious action fires → investigate + fix
```

---

## COMPLEXITY

**Counter recording:** O(1) time, O(60) space per flow (60 minute-buckets).

**Sense evaluation:** O(60) per flow per tick (scan 60 buckets). With 5 flows: O(300) per tick. Negligible vs the tick's other work.

**Total memory:** ~5 flows × 60 buckets × 16 bytes = ~5KB. Negligible.

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| orchestrator/dispatcher | inject_stimulus(target="infra") | Stimulus routed to best actor |
| cognition/metabolism | get_circadian_factor(now) | Float 0.5-1.0 for baseline adjustment |
| orchestrator/activation_pressure | get_pressure() | Float for baseline adjustment |

Co-Authored-By: AI Citizen (@mechanical_visionary) <mechanical_visionary@mindprotocol.ai>
