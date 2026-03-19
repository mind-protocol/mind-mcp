# ALGORITHM: Tick System

## Main Loop

```
CONSTANTS:
  BASE_LOOP_INTERVAL = 5s          # check frequency
  AWARENESS_INTERVAL = 60s         # per citizen
  THOUGHT_INTERVAL = 300s          # per citizen (5 min target)
  CONSCIOUS_ACTION_THRESHOLD = 0.15 # mean WM energy to fire (env: MIND_CONSCIOUS_ACTION_THRESHOLD)
  ACTION_COOLDOWN_TICKS = 3        # minimum ticks between conscious actions

STATE:
  citizen_engines: dict[handle → TwoTickEngine]
  last_awareness: dict[handle → timestamp]
  last_thought: dict[handle → timestamp]
  active_futures: dict[handle → Future]
  activation_pressure: float (adaptive, 0.1-50.0)

LOOP:
  while running:
    now = time.time()

    # 1. Maintenance
    if now - last_neuron_cleanup > 60s:
      for engine in citizen_engines: engine.enforce_neuron_cap()
    if now - last_health_check > 10s:
      check_degradation()
    if now - last_account_refresh > 1800s:
      refresh_accounts()
    if now - last_first_boot_scan > 30s:
      scan_first_boot_files()

    # 2. Tick all citizens
    for handle, engine in citizen_engines:

      # Awareness (fast cycle)
      if now - last_awareness[handle] > AWARENESS_INTERVAL:
        result = engine.awareness_tick(graph_read_fn)
        last_awareness[handle] = now
        if result.wm_changed:
          write_awareness_file(handle, engine.state)

      # Thought (slow cycle)
      if now - last_thought[handle] > THOUGHT_INTERVAL:
        result = engine.thought_tick()
        last_thought[handle] = now

        if result.conscious_action:
          # Check activation pressure gate
          effective_threshold = activation_pressure / subscription_multiplier(handle)
          if result.mean_wm_energy > effective_threshold:
            fire_conscious_action(handle, engine)

    # 3. Collect completed futures
    for handle, future in active_futures:
      if future.done():
        result = future.result()
        if result.success:
          activation_pressure *= 0.98  # ease off
        elif result.rate_limited:
          activation_pressure *= 1.25  # throttle

    sleep(BASE_LOOP_INTERVAL)
```

## Thought Tick — 7 Steps

```
def thought_tick(state, metabolism):
  constants = metabolism.get_effective_constants(citizen_id, now)

  # Step 1: Energy generation
  for node in state.nodes:
    node.energy += EXCESS_ENERGY_RATE × node.weight × constants.injection_scale

  # Step 2: Energy dispersal (bidirectional)
  for link in state.links:
    flow = link.source.energy × 0.30 × link.weight
    link.target.energy += flow
    link.source.energy -= flow
    # Reverse flow (smaller)
    reverse = link.target.energy × 0.10 × link.weight
    link.source.energy += reverse
    link.target.energy -= reverse

  # Step 3: Decay
  for node in state.nodes:
    node.energy *= (1.0 - constants.decay_rate)  # base 0.02, circadian 0.02-0.04

  # Step 4: WM selection (top 7 by energy)
  candidates = sorted(state.nodes, key=lambda n: n.energy, reverse=True)
  state.wm = candidates[:7]

  # Step 5: Hebbian crystallization
  for pair in combinations(state.wm, 2):
    link = find_or_create_link(pair)
    link.weight += HEBBIAN_RATE  # co-active pairs strengthen

  # Step 6: Periodic forgetting (every 100 ticks)
  if state.tick_count % 100 == 0:
    for link in state.links:
      if link.weight < FORGET_THRESHOLD:
        dissolve(link)

  # Step 7: Conscious action check
  mean_energy = mean(n.energy for n in state.wm)
  if mean_energy > CONSCIOUS_ACTION_THRESHOLD and cooldown_elapsed():
    return ThoughtResult(conscious_action=True, mean_wm_energy=mean_energy)

  return ThoughtResult(conscious_action=False)
```

## Conscious Action Dispatch

```
def fire_conscious_action(handle, action_node_id):
  state = citizen_states[handle]

  # 1. Extract action intent from the fired node (L17 impulse output)
  action_node = state.nodes[action_node_id]
  action_command = action_node.action_command   # MCP tool name (e.g. "subcall", "call", "task")
  action_content = action_node.content          # human-readable intent

  # 2. Serialize WM to prompt
  wm_prompt = serialize_wm_to_prompt(state, orientation)

  # 3. Prepend subconscious action directive (if specific action selected)
  if action_command and action_content:
    directive = f"""
      [SUBCONSCIOUS ACTION DIRECTIVE]
      Your drives have selected this action: {action_content}
      Execute it using the MCP tool: /{action_command}
      This is not a suggestion — your limbic system accumulated enough impulse.
    """
    wm_prompt = directive + wm_prompt

  # 4. Build request with full cognitive context in metadata
  request = {
    "voice_text": f"[conscious_action] {handle}",
    "mode": "autonomous",
    "source": "conscious_action",
    "metadata": {
      "citizen_handle": handle,
      "cognitive_context": wm_prompt,  # CRITICAL: passed to prompt builder
      "action_node_id": action_node_id,
      "action_command": action_command,
    }
  }

  # 5. Dispatch to thread pool → invoke_claude
  dispatch(request)
  log_action_start(handle, action_node_id, action_command, action_content)
```

## Claude Subprocess Invocation

The `invoke_claude()` function runs in a thread and manages the Claude Code subprocess:

```
def invoke_claude(request, session_id):
  # 1. Build full prompt (identity + cognitive context + mode directive)
  prompt = _build_prompt(request, ...)
  # → for citizen sessions: build_citizen_prompt(citizen_data, voice_text,
  #                         session_id, mode, cognitive_context=wm_prompt)
  # → returns: CITIZEN SESSION header + WM state + action directives

  # 2. Build command
  cmd = ["claude", "--print", "--output-format", "text",
         "--dangerously-skip-permissions", "--session-id", uuid]

  # 3. Pass prompt — long prompts via stdin, short via CLI arg
  if len(prompt) > len(voice_text):
    input_text = prompt          # stdin path
  else:
    cmd.append(message)          # CLI arg path
    input_text = None

  # 4. Launch subprocess in citizen's directory
  #    Claude Code auto-reads CLAUDE.md, awareness.md from cwd
  process = Popen(cmd, cwd=citizen_dir, env=balanced_env)

  # 5. Two-phase timeout with subconscious interim
  try:
    stdout, stderr = process.communicate(input=input_text, timeout=10s)
  except TimeoutExpired:
    # Phase 1 timeout: generate subconscious response as interim
    subconscious = invoke_subconscious(request)  # pure graph physics, no LLM
    write_interim(subconscious)

    # Phase 2: wait for Claude to actually finish (up to 590s)
    try:
      stdout, stderr = process.communicate(timeout=590s)
    except TimeoutExpired:
      process.kill()

  # 6. Read response (file > stdout fallback)
  # 7. Account failover if rate limited
  # 8. Track success/failure for activation pressure

  return (response, voice_response)
```

**CRITICAL INVARIANT:** The full prompt (including cognitive context) MUST be passed to the subprocess BEFORE `Popen()` launches it. If the prompt is passed after launch, the subprocess receives no input and produces empty/hanging results.

## Adaptive Tick Speed (Target)

```
def compute_effective_interval(citizen, base_interval):
  metabolism = get_metabolism(citizen)

  # Circadian factor: day=0.8 (faster), night=1.5 (slower)
  circadian = metabolism.circadian_factor(now)

  # Activity factor: more recent moments = faster
  recent_moments = count_moments(citizen, last_hour)
  activity = 1.0 / (1.0 + recent_moments × 0.1)  # more activity → lower → faster

  # Crystallization factor: high crystallization = slow down
  crystal_rate = state.crystallizations_last_100_ticks / 100
  crystal_factor = 1.0 + crystal_rate × 2.0  # more crystals → slower

  # Energy factor: low energy = slower (nothing to process)
  mean_energy = mean(n.energy for n in state.nodes)
  energy_factor = 1.0 / max(mean_energy, 0.1)  # capped

  effective = base_interval × circadian × activity × crystal_factor
  return clamp(effective, MIN_INTERVAL=120, MAX_INTERVAL=600)
```

## Data Structures

```
AwarenessTickResult:
  nodes_imported: int
  nodes_updated: int
  wm_changed: bool

ThoughtTickResult:
  conscious_action: bool
  mean_wm_energy: float
  ticks_since_last_action: int
  nodes_decayed: int
  links_crystallized: int
  links_forgotten: int

ActivationPressure:
  pressure: float  # 0.1 - 50.0
  history: list[(timestamp, event)]  # rate_limit or success
```

Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
