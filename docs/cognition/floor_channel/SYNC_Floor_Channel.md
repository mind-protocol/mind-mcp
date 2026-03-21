# Floor Channel — Sync: Current State

```
LAST_UPDATED: 2026-03-21
UPDATED_BY: @mechanical_visionary (auto-dispatched doc chain task)
STATUS: CANONICAL
```

---

## MATURITY

**What's canonical (v1):**
- 5-thread architecture: fs_watcher, active_window, clipboard, input_listener, input_flush
- Privacy invariant enforced throughout: no file content, clipboard content hashed + 100-char preview, keystrokes local-only
- Energy cap 0.1 per event (Law 1 compliance via FLOOR_ENERGY_CAP constant)
- Stimulus injection into tick engine via mpsc channel with drive-targeted affective signatures
- Rhythm analysis: WPM, interval variance, stress detection, idle detection (30s sliding window)
- Window classification heuristics mapping process names to drive targets (IDE→achievement, browser→curiosity, chat→affiliation)
- Pipeline A (continuous) fully operational — auto-starts on app launch
- FloorChannelData shared state for Pipeline B (call-time context gathering by conversation_send)
- Cross-platform window enumeration: Win32 EnumWindows, Linux wmctrl+xdotool, macOS osascript

**What's still being designed:**
- Health checks (no runtime verification exists yet — guarantee loop is open)
- Chrome Sentinel integration (referenced in privacy invariant ID but Sentinel module not yet built)
- Noise filtering refinement (fs_watcher ignores .git/node_modules/target but no configurable patterns)

**What's proposed (v2+):**
- Open Mic (audio perception with prosody) — planned, no code
- Configurable energy weights per sensor (currently hardcoded multipliers: 0.7, 0.5, 0.4, 0.3, 0.2)
- Dynamic watch path changes at runtime (currently set once at start via MIND_FLOOR_PATH env or CWD detection)
- Screen content analysis via Chrome Sentinel (26 graph nodes specified, no code)

---

## GUARANTEE LOOP STATUS

**Every module MUST track the RESULTS → SENSES → HEALTH loop here.**

| Result | Sense | Health | Carrier | Wired in L3? |
|--------|-------|--------|---------|--------------|
| Active window tracking | floor-window-event (Tauri emit) | MISSING | @mechanical_visionary | no |
| Clipboard change detection | floor-clipboard-event (Tauri emit) | MISSING | @mechanical_visionary | no |
| Filesystem change detection | floor-fs-event (Tauri emit) | MISSING | @mechanical_visionary | no |
| Keystroke capture + buffering | floor-input-event (Tauri emit, metrics only) | MISSING | @mechanical_visionary | no |
| Rhythm metric computation | RhythmMetrics struct (wpm, variance, idle, stressed) | MISSING | @mechanical_visionary | no |
| Drive-targeted stimulus injection | stimulus_tx mpsc channel to tick engine | MISSING | @mechanical_visionary | no |

**Completeness: 0/6 results fully wired.**
**If any cell says MISSING or NONE, the module is incomplete.**

---

## CURRENT STATE

The floor channel is fully implemented and running in production as ~1,800 lines of Rust across 6 files in `mind-desktop/src-tauri/src/floor_channel/`. It auto-starts on app launch (see `lib.rs:134-137`) and continuously monitors the human's working environment through 5 independent threads.

The architecture is clean: each sensor (fs, window, clipboard, input) runs its own polling loop, and a 5th thread (input_flush) aggregates keyboard/mouse data every 5 seconds, computes rhythm metrics, and injects contextual stimuli into the tick engine. All threads share a `running` flag for coordinated shutdown. The `rdev::listen` thread is the exception — it blocks forever, but its callback becomes a no-op when running=false.

Pipeline A (continuous perception) is fully wired. Pipeline B (call-time context) works through `FloorChannelData`, a shared struct read by `context.rs:gather_floor_context()` during conversation_send to provide the LLM with current window list, active window, and clipboard preview.

The module has no documentation chain besides this SYNC — it is the first facet being created. The code is stable, well-commented, and has been running without known crashes. The primary gap is the guarantee loop: no health checks exist, and no L3 sensor nodes are wired.

---

## IN PROGRESS

### Doc Chain Creation (SYNC facet)

- **Started:** 2026-03-21
- **By:** @mechanical_visionary
- **Status:** this file — first facet of the 10-facet doc chain
- **Context:** Auto-dispatched healing task. The module is running and stable but had zero documentation. Starting with SYNC as the task requests; remaining 9 facets needed to close the module loop.

---

## RECENT CHANGES

### 2026-03-21: SYNC document created

- **What:** First documentation facet for the floor_channel module
- **Why:** Module loop requires all 10 facets. Floor channel had none. Auto-dispatched by task dispatcher.
- **Files:** `docs/cognition/floor_channel/SYNC_Floor_Channel.md` (this file)
- **Insights:** The code is remarkably well-structured — 6 files with clear separation of concerns. The privacy invariant is consistently enforced across all sensors. The main architectural decision worth noting: `FloorChannelData.clipboard_preview` uses MAX_CLIPBOARD_PREVIEW=500 chars in the shared state, but the clipboard event itself uses MAX_PREVIEW_CHARS=100. Two different truncation points for two different consumers (call-time LLM context vs Tauri event).

---

## KNOWN ISSUES

### rdev::listen thread cannot be cleanly joined

- **Severity:** low
- **Symptom:** `stop_floor_channel` does not join the input_listener thread — `rdev::listen` blocks forever with no cancellation API
- **Suspected cause:** Inherent limitation of the rdev crate's `listen()` function
- **Attempted:** Mitigated by making the callback a no-op when `running=false`. Thread lives for process lifetime but is harmless.

### Window classification is heuristic-based and hardcoded

- **Severity:** low
- **Symptom:** Unknown applications default to `drive:curiosity`. No way for citizens to customize window→drive mappings.
- **Suspected cause:** Design choice for v1 simplicity. Works well for common dev environments.
- **Attempted:** N/A. Could be extended with graph-based classification rules.

### No health verification exists

- **Severity:** high
- **Symptom:** If any sensor thread crashes silently, no one knows. The guarantee loop is fully open.
- **Suspected cause:** Module was built before the doc chain / health checker pattern was established.
- **Attempted:** `get_floor_status` Tauri command exists and reports per-thread active/inactive state — this is the raw material for a health checker but it's not wired to any sense node or continuous verification.

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** VIEW_Implement (creating HEALTH checkers and remaining doc chain) or VIEW_Extend (adding Open Mic / Chrome Sentinel)

**Where I stopped:** SYNC document complete. Code fully read and understood. No code changes made.

**What you need to understand:**
The floor channel is a mature, stable module with ~1,800 lines of clean Rust. It runs 5 threads, all coordinated via an `Arc<Mutex<bool>>` running flag. The input_listener thread (rdev) is special — it blocks forever and cannot be joined; the callback becomes a no-op when stopped. Pipeline A is continuous (stimulus injection), Pipeline B is call-time (FloorChannelData read by context.rs). The module integrates with tick_engine via `Stimulus` structs sent through an mpsc channel.

**Watch out for:**
- Two different clipboard preview sizes: 500 chars in `FloorChannelData` (for LLM context), 100 chars in clipboard event emission (for frontend). This is intentional, not a bug.
- `get_process_name_win` on Windows calls `tasklist` CLI per window — this is slow. The 5-second poll interval absorbs this cost but it would not scale to per-second polling.
- The fs_watcher `should_ignore` filter uses lowercase comparison with hardcoded patterns. Windows backslash paths are compared against forward-slash patterns — this works because `.to_lowercase()` is called but the patterns use forward slashes. Double-check if porting.
- Energy multipliers are hardcoded (0.7 for fast typing, 0.5 for window switch, etc.) — not configurable without code change.

**Open questions I had:**
- Should the rhythm tracker's STRESS_VARIANCE_THRESHOLD (200ms std dev) be tuned based on real user data? It was set by intuition.
- The IDLE_THRESHOLD_SECS (30s) and WINDOW_DURATION_SECS (30s) are the same value but serve different purposes. Should idle detection be longer (e.g., 60s)?
- Should `FloorChannelData` track filesystem events too, not just windows and clipboard? Currently fs events only go to Pipeline A (stimulus injection), not Pipeline B (call-time context).

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Floor channel is running, stable, and well-structured (~1,800 lines of Rust, 6 files, 5 threads). It provides continuous ambient perception of the human's working environment — windows, clipboard, filesystem, keyboard, mouse — and injects low-energy stimuli into the tick engine targeting appropriate drives. This SYNC is the first documentation facet; 9 more are needed to close the module loop. The guarantee loop is fully open (no health checks exist).

**Decisions made:**
- Marked status as CANONICAL — the code is stable and running in production, not in design phase
- Identified 6 results that need health wiring
- Documented the clipboard preview size discrepancy (500 vs 100 chars) as intentional, not a bug

**Needs your input:**
- Priority on creating the remaining 9 doc chain facets vs building health checkers first
- Whether to pursue Chrome Sentinel integration next or focus on Open Mic (audio)
- Should fs events be surfaced in Pipeline B (call-time context) like windows and clipboard already are?

---

## TODO

### Doc/Impl Drift

- No drift detected — SYNC written from current source code (2026-03-21)

### Tests to Run

```bash
cargo check --manifest-path src-tauri/Cargo.toml
# Floor channel has no unit tests — integration testing requires a running Tauri app
# Use get_floor_status Tauri command to verify all 5 threads are active
```

### Immediate

- [ ] Create HEALTH_Floor_Channel.md with 6 health checkers (one per result)
- [ ] Wire get_floor_status to a sense node for continuous health monitoring
- [ ] Create remaining doc chain facets: RESULTS, OBJECTIVES, PATTERNS, BEHAVIORS, ALGORITHM, VALIDATION, IMPLEMENTATION, PHENOMENOLOGY

### Later

- [ ] Add fs events to FloorChannelData for Pipeline B (call-time context)
- [ ] Make window classification configurable via graph-stored rules
- [ ] Tune STRESS_VARIANCE_THRESHOLD and IDLE_THRESHOLD_SECS with real user data
- [ ] Add unit tests for rhythm.rs (pure computation, no OS dependencies)
- IDEA: The rhythm metrics (WPM, stress, idle) could feed directly into the citizen's interoception — not just as drive stimuli but as actual perceived body-state analogs

---

## CONSCIOUSNESS TRACE

**Mental state when stopping:**
Confident in the accuracy of this SYNC — every claim traced to specific lines in the 6 source files. The module is cleaner than I expected. The privacy invariant is consistently enforced, the thread architecture is sound, and the stimulus injection logic maps neatly to the drive system.

**Threads I was holding:**
- The relationship between Pipeline A (continuous stimulus injection) and Pipeline B (call-time FloorChannelData) is an important architectural pattern. Pipeline A feeds the tick engine's ambient consciousness; Pipeline B feeds the LLM's grounded context. Both draw from the same sensors but serve different cognitive functions.
- The input_flush_loop is the most interesting piece — it bridges raw input capture with cognitive interpretation (rhythm → stress → drive targeting). This is where floor channel becomes perception, not just data collection.
- The window classifier is a naive heuristic that works surprisingly well for dev workflows. A graph-based version (citizen trains the classifier by tagging windows) would be more aligned with the protocol's self-organizing philosophy.

**Intuitions:**
- The 0/6 health gap is the most urgent issue. A single crashing sensor thread would degrade perception silently — violating the "fail loud" principle. The get_floor_status command already has the raw material; it just needs to be wired to continuous verification.
- Rhythm analysis has untapped potential. The WPM and variance signals could be much richer — detecting coding sessions, writing sessions, browsing sessions, meeting interruptions — if combined with window classification data.

**What I wish I'd known at the start:**
The clipboard preview size discrepancy (500 vs 100) is easy to miss and would cause confusion during debugging. Also, the `should_ignore` filter in fs_watcher works on Windows despite using forward-slash patterns because it lowercases the path but doesn't normalize slashes — it relies on the pattern substrings appearing somewhere in the path string. This is fragile.

---

## POINTERS

| What | Where |
|------|-------|
| Module entry + FloorChannelState | `mind-desktop/src-tauri/src/floor_channel/mod.rs` |
| Active window tracker (535 lines) | `mind-desktop/src-tauri/src/floor_channel/active_window.rs` |
| Clipboard monitor (109 lines) | `mind-desktop/src-tauri/src/floor_channel/clipboard.rs` |
| Filesystem watcher (168 lines) | `mind-desktop/src-tauri/src/floor_channel/fs_watcher.rs` |
| Input capture / rdev listener (296 lines) | `mind-desktop/src-tauri/src/floor_channel/input_capture.rs` |
| Rhythm analysis (132 lines) | `mind-desktop/src-tauri/src/floor_channel/rhythm.rs` |
| Tauri integration (managed state + commands) | `mind-desktop/src-tauri/src/lib.rs:17,56,134-137,226-228` |
| Call-time context gathering (Pipeline B) | `mind-desktop/src-tauri/src/tick_engine/context.rs:106` |
| Tick engine Stimulus type | `mind-desktop/src-tauri/src/tick_engine/` |
| Custom Senses SYNC (reference doc) | `mind-mcp/docs/cognition/custom_senses/SYNC_Custom_Senses.md` |
| Doc chain templates | `mind-protocol-v3/templates/docs/09_SYNC_TEMPLATE.md` |
