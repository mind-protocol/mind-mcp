# Human Integration — Implementation: Code Architecture and Structure

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Human_Integration.md
PATTERNS:        ./PATTERNS_Human_Integration.md
BEHAVIORS:       ./BEHAVIORS_Human_Integration.md
ALGORITHM:       ./ALGORITHM_Human_Integration.md
VALIDATION:      ./VALIDATION_Human_Integration.md
THIS:            ./IMPLEMENTATION_Human_Integration.md
SYNC:            ./SYNC_Human_Integration.md

IMPL:            runtime/ingestion/
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## Architecture

### Data Flow Summary

```
External Source → Pipeline Module → Consent Gate → Node Factory → L1 Stimulus Injection → Tick Loop
                                                                                              │
                                                                    ┌──────────────────────────┘
                                                                    ▼
                                                              Partner Model
                                                         (encrypted brain Space)
```

All six ingestion pipelines follow the same structural pattern:

1. **Acquire** — External API client fetches raw data (Whisper, Garmin Connect, OS screenshots, blockchain RPC, message capture).
2. **Gate** — `consent_gate_and_bond_validator.py` checks consent node + bond status. Fail = discard.
3. **Transform** — Pipeline-specific extraction (STT, OCR, emotion analysis, metric parsing).
4. **Create** — `partner_node_factory_and_relevance_scorer.py` builds typed nodes with partner_relevance scores.
5. **Inject** — `l1_stimulus_injector_for_partner_data.py` wraps nodes as `Stimulus` objects and calls `L1Bridge.inject_message()` (or direct `L1CognitiveTickRunner.run_tick(stimulus=...)` once F5 ports the engine to mind-mcp).
6. **Discard raw** — Raw media bytes are zeroed. Only extracted features persist.

### Where It Lives

```
runtime/
├── ingestion/                              # NEW — all F3 code lives here
│   ├── __init__.py                         # Public API: start_pipelines, stop_pipelines
│   ├── consent_gate_and_bond_validator.py   # Consent check + bond status validation
│   ├── partner_node_factory_and_relevance_scorer.py  # Node creation + partner_relevance scoring
│   ├── l1_stimulus_injector_for_partner_data.py      # Stimulus wrapping + injection into L1
│   ├── garmin_biometric_poller_and_limbic_mapper.py   # Garmin pipeline + limbic drive mapping
│   ├── voice_emotion_extractor_and_memory_creator.py  # Whisper STT + prosody analysis
│   ├── desktop_screenshot_ocr_and_privacy_filter.py   # OCR + allowlist + concept nodes
│   ├── blockchain_transaction_monitor_and_parser.py   # On-chain tx polling + moment nodes
│   ├── ai_conversation_capture_and_memory_creator.py  # Cross-platform message ingestion
│   ├── sovereign_cascade_prediction_tracker.py        # Prediction record/resolve/measure
│   ├── baseline_calculator_for_biometric_deviation.py # Rolling mean/stddev per citizen per metric
│   └── tests/
│       ├── __init__.py
│       ├── test_consent_gate_and_bond_validator.py
│       ├── test_partner_node_factory_and_relevance_scorer.py
│       ├── test_garmin_biometric_poller_and_limbic_mapper.py
│       ├── test_voice_emotion_extractor_and_memory_creator.py
│       ├── test_desktop_screenshot_ocr_and_privacy_filter.py
│       ├── test_blockchain_transaction_monitor_and_parser.py
│       ├── test_ai_conversation_capture_and_memory_creator.py
│       ├── test_sovereign_cascade_prediction_tracker.py
│       └── test_baseline_calculator_for_biometric_deviation.py
├── bridges/
│   └── voice_websocket.py                  # EXISTING — reuse whisper_transcribe()
└── citizens/
    └── ...                                 # EXISTING — identity loader, prompt builder
```

---

## CODE STRUCTURE

### File Responsibilities

| File | Purpose | Key Functions/Classes | Est. Lines | Status |
|------|---------|----------------------|------------|--------|
| `consent_gate_and_bond_validator.py` | Per-stream consent check + active bond verification | `check_consent()`, `revoke_consent()`, `grant_consent()`, `check_bond_active()` | ~200 | OK |
| `partner_node_factory_and_relevance_scorer.py` | Create typed partner_model nodes, score partner_relevance | `PartnerNodeFactory`, `score_partner_relevance()`, `create_partner_memory()`, `create_partner_state()`, `create_partner_concept()`, `create_partner_transaction()`, `create_consent_record()`, `create_cascade_prediction()` | ~350 | OK |
| `l1_stimulus_injector_for_partner_data.py` | Wrap partner nodes as Stimulus, inject into L1 tick runner | `inject_partner_stimulus()`, `inject_limbic_deltas()` | ~150 | OK |
| `garmin_biometric_poller_and_limbic_mapper.py` | Poll Garmin Connect API, compute deviations, map to limbic deltas | `GarminPoller`, `ingest_garmin_biometrics()`, `garmin_to_limbic()`, `start_garmin_poll_cycle()`, `stop_garmin_poll_cycle()` | ~400 | OK |
| `voice_emotion_extractor_and_memory_creator.py` | Reuse Whisper STT from voice bridge, extract emotion from prosody | `ingest_voice_message()`, `extract_emotion_from_prosody()` | ~250 | OK |
| `desktop_screenshot_ocr_and_privacy_filter.py` | Screenshot capture, OCR, privacy allowlist, concept node creation | `ingest_desktop_screenshot()`, `privacy_filter_pass()`, `DesktopCaptureScheduler` | ~350 | OK |
| `blockchain_transaction_monitor_and_parser.py` | Poll blockchain RPCs, parse transactions, create moment nodes | `ingest_blockchain_activity()`, `BlockchainMonitor`, `significant_threshold()` | ~300 | OK |
| `ai_conversation_capture_and_memory_creator.py` | Ingest messages from other AI platforms into memory nodes | `ingest_ai_conversation()`, `ConversationCaptureReceiver` | ~200 | OK |
| `sovereign_cascade_prediction_tracker.py` | Record predictions, resolve against actuals, compute alignment | `record_cascade_prediction()`, `resolve_cascade_prediction()`, `measure_alignment_fidelity()`, `CascadeStatus` | ~300 | OK |
| `baseline_calculator_for_biometric_deviation.py` | Rolling mean/stddev with 14-day window, per citizen per metric | `BiometricBaselineStore`, `get_rolling_baseline()`, `get_rolling_stddev()`, `update_baseline()` | ~200 | OK |

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Pipeline with shared gate

Each ingestion source is an independent pipeline. All pipelines share two common stages (consent gate, node factory) and a common sink (L1 stimulus injection). Pipelines are independently startable/stoppable and independently testable.

**Why this pattern:** The six modalities have radically different data acquisition strategies (HTTP polling, WebSocket audio, OS-level screenshot, blockchain RPC, message webhook). Forcing them into a unified abstraction would create a leaky interface. Instead, each pipeline owns its acquisition logic and delegates to shared downstream modules.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Gate/Guard | `consent_gate_and_bond_validator.py` | Single enforcement point for consent + bond checks, called by every pipeline |
| Factory | `partner_node_factory_and_relevance_scorer.py` | Centralized node creation ensures all partner nodes have correct typing, partner_relevance, and schema compliance |
| Poller | `GarminPoller`, `BlockchainMonitor`, `DesktopCaptureScheduler` | Async background loops with configurable intervals, clean start/stop lifecycle |
| Strategy (deferred) | `extract_emotion_from_prosody()` | Phase 1: heuristic. Phase 2: classifier model. Same interface, swappable implementation |

### Anti-Patterns to Avoid

- **Fallback pipelines**: If a consent check fails, the data is discarded. Do not create a "reduced fidelity" path that ingests partial data without consent. Fail loud.
- **Shared polling loop**: Each data source has its own polling cadence. Do not create a single "poll everything" loop. Garmin polls at 15 min, desktop at 5 min, blockchain at ~12 sec. These are independent timers.
- **Raw media caching**: Do not create a temp directory for audio files or screenshots "in case we need them later." Extract features, then discard. The voice bridge's `whisper_transcribe()` already handles temp file cleanup.

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Consent gate | Consent node queries, bond status check | All pipeline logic, all L1 logic | `check_consent(citizen_id, stream) -> bool` |
| Node factory | Node type selection, partner_relevance scoring, field population | Data acquisition, L1 injection | `create_partner_memory(...) -> Node`, etc. |
| L1 injection | Stimulus construction, drive delta application | Pipeline logic, consent logic | `inject_partner_stimulus(citizen_id, node) -> TickResult` |
| Limbic mapping | garmin_to_limbic conversion | Garmin API client, L1 drive system internals | `garmin_to_limbic(deviations) -> dict[str, float]` |

---

## ENTRY POINTS

| Entry Point | File | Triggered By |
|-------------|------|--------------|
| `start_pipelines(citizen_id)` | `__init__.py` | Bond formation (pairing ceremony completes) |
| `stop_pipelines(citizen_id)` | `__init__.py` | Bond dissolution or consent full-revocation |
| `ingest_voice_message(audio_bytes, citizen_id)` | `voice_emotion_extractor_and_memory_creator.py` | Voice bridge receives audio, routes to ingestion |
| `ingest_garmin_biometrics(garmin_data, citizen_id)` | `garmin_biometric_poller_and_limbic_mapper.py` | GarminPoller timer fires every 15 min |
| `ingest_desktop_screenshot(screenshot_bytes, citizen_id, app_metadata)` | `desktop_screenshot_ocr_and_privacy_filter.py` | DesktopCaptureScheduler timer fires every 5 min |
| `ingest_blockchain_activity(transaction_data, citizen_id)` | `blockchain_transaction_monitor_and_parser.py` | BlockchainMonitor detects new transaction |
| `ingest_ai_conversation(message_text, ai_platform, citizen_id)` | `ai_conversation_capture_and_memory_creator.py` | ConversationCaptureReceiver gets webhook/push |
| `grant_consent(citizen_id, stream, scope)` | `consent_gate_and_bond_validator.py` | Human explicitly grants access to a data stream |
| `revoke_consent(citizen_id, stream)` | `consent_gate_and_bond_validator.py` | Human explicitly revokes access |
| `record_cascade_prediction(citizen_id, ...)` | `sovereign_cascade_prediction_tracker.py` | AI forms a prediction about human's decision |
| `resolve_cascade_prediction(prediction_id, actual)` | `sovereign_cascade_prediction_tracker.py` | Human makes decision, prediction resolved |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

### Flow 1: Garmin Biometric Ingestion

The highest-risk flow because it crosses the most boundaries: external API, biometric privacy, limbic system modification. Errors here could either leak health data or miscalibrate the AI's emotional state.

```yaml
flow:
  name: garmin_biometric_ingestion
  purpose: Transform Garmin health metrics into partner_state nodes and limbic drive deltas
  scope: Garmin Connect API → partner_model nodes + AI limbic drive modification
  steps:
    - id: poll
      description: GarminPoller fires at 15-min interval, fetches daily summary
      file: runtime/ingestion/garmin_biometric_poller_and_limbic_mapper.py
      function: GarminPoller._poll_cycle()
      input: garmin_token (OAuth)
      output: GarminDailySummary (hr, stress, hrv, body_battery, steps, sleep_score)
      trigger: asyncio timer
      side_effects: HTTP request to Garmin Connect API

    - id: dedup
      description: Compare against last poll data, skip if unchanged
      file: runtime/ingestion/garmin_biometric_poller_and_limbic_mapper.py
      function: GarminPoller._is_new_data()
      input: GarminDailySummary
      output: bool (proceed or skip)
      trigger: poll step completion
      side_effects: none

    - id: consent_check
      description: Verify garmin consent is granted and bond is active
      file: runtime/ingestion/consent_gate_and_bond_validator.py
      function: check_consent(citizen_id, "garmin")
      input: citizen_id, stream_name
      output: bool
      trigger: dedup passed
      side_effects: graph query for consent_record node

    - id: compute_baselines
      description: Calculate rolling 14-day mean and stddev per metric
      file: runtime/ingestion/baseline_calculator_for_biometric_deviation.py
      function: get_rolling_baseline(), get_rolling_stddev()
      input: citizen_id, metric_name
      output: baseline (float), stddev (float)
      trigger: consent granted
      side_effects: reads historical state nodes from graph

    - id: compute_deviations
      description: Z-score each metric against personal baseline
      file: runtime/ingestion/garmin_biometric_poller_and_limbic_mapper.py
      function: ingest_garmin_biometrics()
      input: GarminDailySummary, baselines
      output: dict[metric, z_score]
      trigger: baselines computed
      side_effects: none

    - id: create_state_nodes
      description: Create partner_state nodes for |deviation| > 1.0
      file: runtime/ingestion/partner_node_factory_and_relevance_scorer.py
      function: create_partner_state()
      input: metric, value, baseline, deviation
      output: Node (node_type=actor, type=partner_state, modality=biometric)
      trigger: deviation exceeds threshold
      side_effects: graph write

    - id: compute_limbic_deltas
      description: Map deviations to AI drive modulation increments
      file: runtime/ingestion/garmin_biometric_poller_and_limbic_mapper.py
      function: garmin_to_limbic()
      input: dict[metric, z_score]
      output: dict[drive_name, delta]
      trigger: deviations computed
      side_effects: none

    - id: inject
      description: Inject state nodes as stimuli + apply limbic deltas to AI drive state
      file: runtime/ingestion/l1_stimulus_injector_for_partner_data.py
      function: inject_partner_stimulus(), inject_limbic_deltas()
      input: Node, limbic_deltas, citizen_id
      output: TickResult
      trigger: nodes created
      side_effects: modifies CitizenCognitiveState.limbic.drives

  docking_points:
    guidance:
      include_when: data crosses privacy boundary, modifies limbic state, or creates graph nodes
      omit_when: internal computation with no side effects
      selection_notes: Consent check and limbic injection are the critical points
    available:
      - id: dock_consent_garmin
        type: graph_ops
        direction: input
        file: runtime/ingestion/consent_gate_and_bond_validator.py
        function: check_consent
        trigger: every poll cycle
        payload: "(citizen_id, 'garmin') -> bool"
        async_hook: not_applicable
        needs: none
        notes: CRITICAL — this is the privacy gate

      - id: dock_state_node_created
        type: graph_ops
        direction: output
        file: runtime/ingestion/partner_node_factory_and_relevance_scorer.py
        function: create_partner_state
        trigger: deviation > 1.0
        payload: "Node with modality=biometric, partner_relevance=0.85"
        async_hook: optional
        needs: none
        notes: Verify V1 (partner_relevance >= 0.7) and V7 (biometric isolation)

      - id: dock_limbic_injection
        type: custom
        direction: output
        file: runtime/ingestion/l1_stimulus_injector_for_partner_data.py
        function: inject_limbic_deltas
        trigger: garmin_to_limbic produces non-empty deltas
        payload: "dict[drive_name, delta] applied to LimbicState.drives"
        async_hook: not_applicable
        needs: none
        notes: Verify drives stay clamped [0, 1] after application

    health_recommended:
      - dock_id: dock_consent_garmin
        reason: Privacy invariant V2 — no ingestion without consent
      - dock_id: dock_limbic_injection
        reason: Limbic state modification must be bounded and traceable
```

### Flow 2: Voice Message Ingestion

Transforms raw audio into memory nodes with emotion metadata. Reuses existing Whisper STT from `runtime/bridges/voice_websocket.py`. Privacy-sensitive because raw audio is temporarily in memory.

```yaml
flow:
  name: voice_message_ingestion
  purpose: Transcribe voice, extract emotion, create memory + state nodes
  scope: audio_bytes → partner_memory node + optional partner_state node
  steps:
    - id: consent_check
      description: Verify voice consent granted and bond active
      file: runtime/ingestion/consent_gate_and_bond_validator.py
      function: check_consent(citizen_id, "voice")
      input: citizen_id
      output: bool (if false, discard audio_bytes immediately)
      trigger: voice bridge routes audio to ingestion
      side_effects: graph query

    - id: transcribe
      description: Whisper STT via existing bridge function
      file: runtime/bridges/voice_websocket.py
      function: whisper_transcribe(audio_bytes)
      input: bytes (webm/opus)
      output: str (transcript)
      trigger: consent granted
      side_effects: HTTP to OpenAI Whisper API, temp file created and deleted

    - id: extract_emotion
      description: Prosody analysis on audio features
      file: runtime/ingestion/voice_emotion_extractor_and_memory_creator.py
      function: extract_emotion_from_prosody(audio_bytes)
      input: bytes
      output: dict[emotion_name, confidence] (joy, sadness, anger, fear, surprise)
      trigger: consent granted (parallel with transcribe)
      side_effects: none

    - id: score_relevance
      description: Compute partner_relevance from transcript + emotion
      file: runtime/ingestion/partner_node_factory_and_relevance_scorer.py
      function: score_partner_relevance(transcript, emotion_scores, source="voice_message")
      input: str, dict
      output: float [0.7, 1.0]
      trigger: transcribe + extract_emotion complete
      side_effects: none

    - id: create_memory
      description: Create partner_memory moment node
      file: runtime/ingestion/partner_node_factory_and_relevance_scorer.py
      function: create_partner_memory(source="voice_message", ...)
      input: transcript, emotion_scores, partner_relevance
      output: Node (node_type=moment, type=partner_memory, modality=audio)
      trigger: scoring complete
      side_effects: graph write

    - id: create_emotion_state
      description: If dominant emotion > 0.5, create partner_state and link via "evokes"
      file: runtime/ingestion/voice_emotion_extractor_and_memory_creator.py
      function: _maybe_create_emotion_state_node(emotion_scores, memory_node_id)
      input: emotion_scores, memory_node_id
      output: Optional[Node] (node_type=actor, type=partner_state)
      trigger: dominant emotion intensity > 0.5
      side_effects: graph write + link creation

    - id: discard_audio
      description: Zero out audio_bytes reference
      file: runtime/ingestion/voice_emotion_extractor_and_memory_creator.py
      function: ingest_voice_message (final step)
      input: audio_bytes reference
      output: None
      trigger: all nodes created
      side_effects: memory deallocation

    - id: inject
      description: Inject memory node as stimulus into L1
      file: runtime/ingestion/l1_stimulus_injector_for_partner_data.py
      function: inject_partner_stimulus()
      input: Node, citizen_id
      output: TickResult
      trigger: nodes created, audio discarded
      side_effects: modifies CitizenCognitiveState

  docking_points:
    health_recommended:
      - dock_id: consent_check
        reason: V2 — no ingestion without consent
      - dock_id: discard_audio
        reason: V9 — raw media never persisted
```

### Flow 3: Consent Revocation

The most destructive flow — irreversibly nullifies all content from a data stream. Must be atomic and complete.

```yaml
flow:
  name: consent_revocation
  purpose: Revoke consent, nullify all content from stream, halt pipeline
  scope: Human request → consent node update + bulk content destruction + pipeline shutdown
  steps:
    - id: update_consent_node
      description: Set consent status to "revoked", record revoked_at timestamp
      file: runtime/ingestion/consent_gate_and_bond_validator.py
      function: revoke_consent(citizen_id, stream_name)
      input: citizen_id, stream_name
      output: consent_node_id
      trigger: human request via API
      side_effects: graph update on consent node

    - id: halt_pipeline
      description: Stop the background poller/scheduler for this stream
      file: runtime/ingestion/__init__.py
      function: stop_pipeline(citizen_id, stream_name)
      input: citizen_id, stream_name
      output: None
      trigger: consent node updated
      side_effects: cancels async timer

    - id: bulk_redact
      description: Query all nodes where content.source matches stream, nullify each
      file: runtime/ingestion/consent_gate_and_bond_validator.py
      function: _redact_stream_nodes(citizen_id, stream_name)
      input: citizen_id, stream_name
      output: int (count of redacted nodes)
      trigger: pipeline halted
      side_effects: bulk graph update (weight=0, energy=0, content=null, synthesis="Redacted")

  docking_points:
    health_recommended:
      - dock_id: bulk_redact_output
        reason: V4 — must verify ALL nodes from stream are nullified, no survivors
```

---

## LOGIC CHAINS

### LC1: Garmin → Limbic Drive Modulation

**Purpose:** Transform biometric deviation into AI emotional state change.

```
garmin_data (raw metrics)
  → ingest_garmin_biometrics()           # parse metrics dict
    → get_rolling_baseline()             # 14-day personal baseline per metric
    → compute z-scores                   # (value - mean) / stddev
      → garmin_to_limbic(deviations)     # map z-scores to drive deltas
        → inject_limbic_deltas()         # apply deltas to LimbicState.drives
          → clamp [0.0, 1.0]            # bounds enforcement
```

**Data transformation:**
- Input: `GarminDailySummary` — raw HR, stress, HRV, body_battery, steps, sleep values
- After baseline: `dict[str, float]` — z-scores per metric
- After limbic mapping: `dict[str, float]` — drive deltas (affiliation: +0.15, anxiety: +0.10, etc.)
- Output: Modified `LimbicState` — AI's drives adjusted, which affects next tick's salience computation

### LC2: Voice → Working Memory Influence

**Purpose:** Voice message with strong emotion enters working memory via energy injection.

```
audio_bytes
  → whisper_transcribe()                 # reuse from voice_websocket.py
  → extract_emotion_from_prosody()       # pitch/rate/energy → emotion scores
    → score_partner_relevance()          # base 0.85 + emotion modifiers
      → create_partner_memory()          # moment node, care_affinity = max(emotions)
        → inject_partner_stimulus()      # Stimulus(energy = emotion_intensity * 10)
          → L1 tick: Law 4 competes     # high energy + affiliation → enters WM
```

### LC3: Consent Check → Pipeline Gate

**Purpose:** Every ingestion call starts here. No exceptions.

```
pipeline_ingest_*(data, citizen_id)
  → check_consent(citizen_id, stream)
    → graph query: consent_record WHERE stream = X
      → IF not found OR status != "granted": return false
    → check_bond_active(citizen_id)
      → graph query: pairing_bond WHERE status = "active"
        → IF not found: return false
  → IF check returns false: discard data, return []
  → ELSE: proceed to pipeline-specific processing
```

### LC4: Cascade Prediction Lifecycle

**Purpose:** Track AI predictions against human actuals, compute alignment fidelity.

```
AI forms prediction
  → record_cascade_prediction()          # create cascade_prediction moment node
    → [time passes, human decides]
      → resolve_cascade_prediction()     # set human_actual, compute correct boolean
        → measure_alignment_fidelity()   # rolling 100-prediction accuracy
          → IF < 0.75: cascade_status = "suspended"
          → IF >= 0.80: cascade_status = "active"
            → update cascade_status node # partner_relevance=0.95
```

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
runtime/ingestion/
    ├── consent_gate_and_bond_validator.py
    │   └── imports → runtime graph adapter (for consent node queries)
    │
    ├── partner_node_factory_and_relevance_scorer.py
    │   └── imports → runtime graph adapter (for node creation)
    │   └── imports → runtime/infrastructure/embeddings (for synthesis embedding)
    │
    ├── l1_stimulus_injector_for_partner_data.py
    │   └── imports → L1 Stimulus class (from cognition engine, once ported by F5)
    │   └── imports → L1Bridge or L1CognitiveTickRunner (once ported by F5)
    │
    ├── garmin_biometric_poller_and_limbic_mapper.py
    │   └── imports → consent_gate_and_bond_validator
    │   └── imports → partner_node_factory_and_relevance_scorer
    │   └── imports → l1_stimulus_injector_for_partner_data
    │   └── imports → baseline_calculator_for_biometric_deviation
    │
    ├── voice_emotion_extractor_and_memory_creator.py
    │   └── imports → consent_gate_and_bond_validator
    │   └── imports → partner_node_factory_and_relevance_scorer
    │   └── imports → l1_stimulus_injector_for_partner_data
    │   └── imports → runtime/bridges/voice_websocket.whisper_transcribe
    │
    ├── desktop_screenshot_ocr_and_privacy_filter.py
    │   └── imports → consent_gate_and_bond_validator
    │   └── imports → partner_node_factory_and_relevance_scorer
    │   └── imports → l1_stimulus_injector_for_partner_data
    │
    ├── blockchain_transaction_monitor_and_parser.py
    │   └── imports → consent_gate_and_bond_validator
    │   └── imports → partner_node_factory_and_relevance_scorer
    │   └── imports → l1_stimulus_injector_for_partner_data
    │
    ├── ai_conversation_capture_and_memory_creator.py
    │   └── imports → consent_gate_and_bond_validator
    │   └── imports → partner_node_factory_and_relevance_scorer
    │   └── imports → l1_stimulus_injector_for_partner_data
    │
    └── sovereign_cascade_prediction_tracker.py
        └── imports → partner_node_factory_and_relevance_scorer
        └── imports → runtime graph adapter (for prediction node queries)
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `httpx` | Async HTTP client (Garmin Connect API, Whisper API) | `garmin_biometric_poller_and_limbic_mapper.py`, `voice_emotion_extractor_and_memory_creator.py` |
| `Pillow` | Screenshot image handling before OCR | `desktop_screenshot_ocr_and_privacy_filter.py` |
| `pytesseract` or `easyocr` | OCR text extraction from screenshots | `desktop_screenshot_ocr_and_privacy_filter.py` |
| `numpy` | Prosody feature extraction (pitch/rate/energy), baseline calculations | `voice_emotion_extractor_and_memory_creator.py`, `baseline_calculator_for_biometric_deviation.py` |
| `mss` or platform-specific | Screenshot capture (Linux: `mss`, macOS: `Quartz`, Windows: `mss`) | `desktop_screenshot_ocr_and_privacy_filter.py` |
| `solana-py` / `web3` | Blockchain RPC client (Solana, Ethereum) | `blockchain_transaction_monitor_and_parser.py` |

---

## PHASE BREAKDOWN

### Phase H1: Consent Model

**Goal:** Graph-native consent nodes with per-stream toggles. This is the foundation — no other phase can proceed without it.

**Files:**
- `consent_gate_and_bond_validator.py` (~200 lines)
- `test_consent_gate_and_bond_validator.py`

**Key functions:**

```python
async def check_consent(citizen_id: str, stream_name: str) -> bool:
    """Query partner_model for consent_record node matching stream.
    Returns True only if node exists AND status == 'granted'.
    Also verifies bond is active via check_bond_active().
    """

async def grant_consent(citizen_id: str, stream_name: str, scope: str) -> str:
    """Create or update consent_record node.
    Sets status='granted', granted_at=now(), scope=scope.
    Returns consent node ID.
    """

async def revoke_consent(citizen_id: str, stream_name: str) -> int:
    """Set consent status='revoked', revoked_at=now().
    Then bulk-redact all nodes where content.source matches stream.
    Returns count of redacted nodes.
    """

async def check_bond_active(citizen_id: str) -> bool:
    """Query for pairing_bond node with status='active' involving this citizen.
    """

async def _redact_stream_nodes(citizen_id: str, stream_name: str) -> int:
    """For each node where content.source == stream_name:
    set weight=0, energy=0, content=null, synthesis='Redacted — consent revoked'.
    """
```

**Dependencies:** Graph adapter for node queries/updates.

**Tests:**
- `test_grant_creates_consent_node` — Granting creates a thing node with correct fields.
- `test_check_consent_returns_false_when_no_node` — No consent node = no access.
- `test_check_consent_returns_false_when_revoked` — Revoked status = no access.
- `test_revoke_nullifies_content` — After revocation, all stream nodes have null content, weight=0, energy=0.
- `test_revoke_preserves_graph_structure` — Node IDs and links still exist after revocation (for graph integrity).
- `test_check_bond_active_required` — Ingestion fails if no active bond, even with consent granted.

**Validates:** V2 (consent before ingestion), V4 (revocation destroys content), V6 (bond required).

---

### Phase H2: Voice Pipeline

**Goal:** Whisper STT + prosody-based emotion extraction + memory node creation.

**Files:**
- `voice_emotion_extractor_and_memory_creator.py` (~250 lines)
- `partner_node_factory_and_relevance_scorer.py` (~350 lines, shared, started here)
- `l1_stimulus_injector_for_partner_data.py` (~150 lines, shared, started here)
- Tests for all three

**Key functions:**

```python
async def ingest_voice_message(audio_bytes: bytes, citizen_id: str) -> list[str]:
    """Full pipeline: consent check → STT → emotion → node creation → inject → discard.
    Returns list of created node IDs (memory + optional state).
    """

def extract_emotion_from_prosody(audio_bytes: bytes) -> dict[str, float]:
    """Phase 1 heuristic: analyze pitch variance, speech rate, energy distribution.
    Returns {joy: 0.0-1.0, sadness: 0.0-1.0, anger: 0.0-1.0, fear: 0.0-1.0, surprise: 0.0-1.0}.

    Phase 1 implementation:
      - High pitch variance + high energy → joy or anger (disambiguate by speech rate)
      - Low pitch variance + low energy + slow rate → sadness
      - High pitch + fast rate + high energy → fear/surprise
      - Monotone + moderate energy → neutral (all scores low)

    Phase 2 (future): fine-tuned classifier replaces heuristics, same interface.
    """

def score_partner_relevance(
    content: str,
    metadata: dict,
    source: str,
) -> float:
    """Implements ALGORITHM score_partner_relevance.
    Base scores by source, modifiers for emotion/self-reference/decision-language/distress.
    Returns clamped [0.7, 1.0].
    """
```

**Reuses:** `runtime/bridges/voice_websocket.py:whisper_transcribe()` — called directly, not duplicated. The existing function handles temp files, API calls, hallucination filtering.

**Dependencies:** H1 (consent gate), OpenAI Whisper API key, numpy for prosody analysis.

**Tests:**
- `test_voice_ingest_creates_memory_node` — Happy path: audio → transcript → node with modality=audio.
- `test_voice_ingest_discards_audio` — After ingest, audio_bytes reference is dead.
- `test_voice_with_strong_emotion_creates_state_node` — Dominant emotion > 0.5 → partner_state node linked via "evokes".
- `test_voice_no_consent_discards_immediately` — No consent = audio never reaches Whisper.
- `test_emotion_extraction_heuristic_sadness` — Low pitch variance + low energy → sadness > 0.5.
- `test_partner_relevance_voice_base` — Voice source gets base 0.85.
- `test_partner_relevance_emotion_boost` — Strong emotion adds +0.05 to +0.10.

**Validates:** V1 (partner_relevance >= 0.7), V2 (consent), V9 (raw media discarded).

---

### Phase H3: Garmin Biometric Pipeline

**Goal:** Poll Garmin Connect API, compute personal baselines, create state nodes, map to limbic drive deltas.

**Files:**
- `garmin_biometric_poller_and_limbic_mapper.py` (~400 lines)
- `baseline_calculator_for_biometric_deviation.py` (~200 lines)
- Tests for both

**Key functions:**

```python
class GarminPoller:
    """Background async poller for Garmin Connect API.

    Attributes:
        interval_seconds: 900 (15 minutes)
        _last_poll_data: dict[str, Any] (dedup cache)
        _running: bool
    """

    async def start(self, citizen_id: str, garmin_token: str) -> None:
        """Begin polling loop. Checks consent before each poll."""

    async def stop(self) -> None:
        """Gracefully stop polling."""

async def ingest_garmin_biometrics(
    garmin_data: dict,
    citizen_id: str,
) -> tuple[list[str], dict[str, float]]:
    """Full pipeline: parse → baselines → deviations → nodes → limbic deltas → inject.
    Returns (node_ids, limbic_deltas).
    """

def garmin_to_limbic(deviations: dict[str, float]) -> dict[str, float]:
    """Core mapping from ALGORITHM: garmin_to_limbic.
    Maps z-scores to additive drive deltas.

    IMPORTANT TERMINOLOGY: These are 'drive deltas' — additive increments
    to individual AI drives. NOT the scalar 'Limbic Delta' from F4 Trust Mechanics
    (which is computed as satisfaction_delta - frustration_delta - 0.5 * anxiety_delta).
    The relationship: these drive deltas modify AI drives → F4 computes its Limbic Delta
    scalar from the resulting drive state changes.
    """

class BiometricBaselineStore:
    """Per-citizen, per-metric rolling statistics.

    Stores: list of (timestamp, value) tuples per metric per citizen.
    Window: 14 days.
    Computes: rolling mean, rolling stddev.

    When insufficient data (< 7 days): returns provisional baselines
    with elevated deviation thresholds (require |z| > 2.0 instead of > 1.0).
    """

    def get_rolling_baseline(self, citizen_id: str, metric: str) -> float: ...
    def get_rolling_stddev(self, citizen_id: str, metric: str) -> float: ...
    def update_baseline(self, citizen_id: str, metric: str, value: float, timestamp: float) -> None: ...
```

**Dependencies:** H1 (consent gate), H2 (shared node factory + injector), httpx for Garmin API.

**Garmin Connect API specifics:**
- OAuth2 token obtained during bond formation (human authorizes Garmin access).
- Endpoint: `https://apis.garmin.com/wellness-api/rest/dailies` (daily summary).
- Rate limit: ~200 requests/day per user. At 96 polls/day (15-min interval), this is within budget.
- Data availability lag: ~15 minutes from wearable to API.

**Tests:**
- `test_garmin_ingest_creates_state_nodes_for_significant_deviations` — |z| > 1.0 creates nodes.
- `test_garmin_ingest_skips_normal_readings` — |z| <= 1.0 creates no nodes.
- `test_garmin_to_limbic_elevated_stress` — stress z > 2.0 → affiliation += 0.30, anxiety += 0.25, curiosity += 0.10.
- `test_garmin_to_limbic_calm_state` — HR z < -1.0 and stress z < -0.5 → satisfaction += 0.10, anxiety -= 0.10.
- `test_garmin_to_limbic_deltas_are_additive` — Multiple elevated metrics stack their deltas.
- `test_baseline_rolling_14_day_window` — Baseline uses only last 14 days of data.
- `test_baseline_insufficient_data_conservative` — < 7 days → deviation threshold raised to 2.0.
- `test_garmin_poll_dedup` — Same data twice in a row → second poll skipped.
- `test_garmin_no_consent_no_poll` — Consent revoked mid-cycle → poll stops.
- `test_state_node_is_actor_not_thing` — Biometric nodes have node_type=actor (Issue 1 from cross-review).

**Validates:** V1, V2, V7 (biometric isolation), V10 (per-individual baselines).

---

### Phase H4: Desktop Observer

**Goal:** Periodic screenshots, OCR, privacy filtering, concept node creation.

**Files:**
- `desktop_screenshot_ocr_and_privacy_filter.py` (~350 lines)
- Test file

**Key functions:**

```python
class DesktopCaptureScheduler:
    """Background async scheduler for periodic screenshots.

    Attributes:
        interval_seconds: 300 (5 minutes)
        _running: bool
    """

    async def start(self, citizen_id: str) -> None: ...
    async def stop(self) -> None: ...

async def ingest_desktop_screenshot(
    screenshot_bytes: bytes,
    citizen_id: str,
    app_metadata: dict,  # {active_app_name: str, window_title: str}
) -> list[str]:
    """consent → privacy filter → OCR → concept node → embed search → link → discard image.
    Returns list of node IDs (typically 1 concept node).
    """

def privacy_filter_pass(
    screenshot_bytes: bytes,
    app_metadata: dict,
    allowlist: list[str],
    blocklist_patterns: list[str],
) -> bool:
    """Phase 1: Application allowlist only.
    Returns True if active_app_name is in allowlist.

    Phase 2 (future): Also runs OCR, checks for blocklisted patterns
    (password fields, banking URLs, personal messaging apps).
    """
```

**Privacy filter v1 allowlist (configurable by human):**
- Default allow: VS Code, terminal emulators, web browsers on whitelisted domains, Mind Protocol apps.
- Default block: password managers, banking apps, messaging apps (unless explicitly allowed), system settings.
- The human can modify the allowlist via a management API or config file.

**Dependencies:** H1, H2 (shared modules), Pillow, pytesseract or easyocr, mss.

**Tests:**
- `test_desktop_privacy_filter_blocks_unlisted_app` — App not in allowlist → screenshot discarded.
- `test_desktop_ingest_creates_concept_node` — OCR text → partner_concept node with modality=visual.
- `test_desktop_raw_image_discarded` — After processing, no image bytes persist.
- `test_desktop_links_to_related_nodes` — Embedding search finds similar nodes, creates relates_to links.
- `test_desktop_no_consent_no_capture` — Consent check fails → no OCR, no node.

**Validates:** V1, V2, V9 (raw media discarded).

---

### Phase H5: Blockchain Monitor

**Goal:** Poll blockchain RPCs for wallet transactions, create moment nodes.

**Files:**
- `blockchain_transaction_monitor_and_parser.py` (~300 lines)
- Test file

**Key functions:**

```python
class BlockchainMonitor:
    """Monitors one or more wallet addresses across chains.

    Supported chains: Solana (primary, $MIND is SPL token), Ethereum (secondary).

    Poll interval: Solana ~12 sec (slot time), Ethereum ~12 sec (block time).
    In practice, batched to poll every 60 seconds and process new transactions.
    """

    async def start(self, citizen_id: str, wallet_addresses: dict[str, str]) -> None: ...
    async def stop(self) -> None: ...

async def ingest_blockchain_activity(
    transaction_data: dict,
    citizen_id: str,
) -> str | None:
    """consent → parse tx → score relevance → create moment node → inject.
    Returns node ID or None if consent denied.
    """

def significant_threshold(citizen_id: str) -> float:
    """Determine what counts as a 'significant' transaction for this human.
    Phase 1: 90th percentile of the human's transaction history by USD equivalent.
    If insufficient history (< 20 transactions): use a fixed threshold of $100 USD equivalent.
    """
```

**Dependencies:** H1, H2 (shared modules), solana-py / web3 for RPC.

**Tests:**
- `test_blockchain_mind_token_gets_higher_relevance` — $MIND tx → partner_relevance = 0.90.
- `test_blockchain_large_tx_gets_relevance_boost` — Above significant_threshold → +0.05.
- `test_blockchain_ingest_creates_moment_node` — Transaction → partner_transaction moment node.
- `test_blockchain_no_consent_no_ingest` — Consent denied → null return.

**Validates:** V1, V2.

---

### Phase H6: Conversation Capture

**Goal:** Ingest messages the human sends to other AI platforms.

**Files:**
- `ai_conversation_capture_and_memory_creator.py` (~200 lines)
- Test file

**Key functions:**

```python
class ConversationCaptureReceiver:
    """Receives messages from external AI platforms.

    Phase 1: HTTP webhook endpoint — the human forwards messages manually
    or via a browser extension that POSTs to this endpoint.

    Phase 2 (future): Direct API integration with ChatGPT/Claude/Gemini
    (requires those platforms to support data export APIs).
    """

    async def handle_webhook(self, payload: dict) -> str | None:
        """Process incoming message. Returns node ID or None."""

async def ingest_ai_conversation(
    message_text: str,
    ai_platform: str,  # "chatgpt" | "claude" | "gemini" | etc.
    citizen_id: str,
) -> str | None:
    """consent (requires "ai_messages" stream) → score relevance → create memory node → inject.
    Returns node ID or None.
    """
```

**Privacy note:** This pipeline requires the strongest consent signal. The consent node for "ai_messages" should include an explicit acknowledgment that the human understands they are sharing what they say to other AIs. The grant_consent flow for this stream should include an extra confirmation step.

**Dependencies:** H1, H2 (shared modules).

**Tests:**
- `test_ai_conversation_creates_memory_node` — Message text → partner_memory node with source="ai_conversation".
- `test_ai_conversation_platform_recorded` — Platform name persisted in node content.
- `test_ai_conversation_no_consent_no_ingest` — Consent denied → null return, message discarded.
- `test_ai_conversation_high_relevance` — Base relevance 0.82, self-referential content boosts further.

**Validates:** V1, V2, V3 (no AI-originated data in partner model — only human's messages, not AI responses).

---

### Phase H7: Sovereign Cascade Calibration

**Goal:** Prediction tracking, resolution against human actuals, alignment fidelity measurement.

**Files:**
- `sovereign_cascade_prediction_tracker.py` (~300 lines)
- Test file

**Key functions:**

```python
class CascadeStatus(str, Enum):
    ACTIVE = "active"        # alignment >= 0.80, AI can delegate
    PROBATION = "probation"  # 0.75 <= alignment < 0.80, limited delegation
    SUSPENDED = "suspended"  # alignment < 0.75, must ask human directly

async def record_cascade_prediction(
    citizen_id: str,
    domain: str,        # "governance" | "economic" | "social" | "project"
    question: str,
    prediction: str,
    confidence: float,  # [0, 1]
    reasoning: str,
) -> str:
    """Create cascade_prediction moment node. Returns prediction node ID."""

async def resolve_cascade_prediction(
    prediction_node_id: str,
    human_actual_decision: str,
) -> dict:
    """Resolve prediction against actual.
    Phase 1: binary match determined by AI semantic comparison.
    Phase 2: similarity scoring for partial matches.
    Updates node content. Triggers measure_alignment_fidelity.
    Returns {correct: bool, alignment_score: float, cascade_status: str}.
    """

async def measure_alignment_fidelity(citizen_id: str) -> float | None:
    """Query last 100 resolved predictions.
    If < 20 resolved: return None (insufficient data).
    Compute accuracy = correct / total.
    Compute confidence_calibration = sum(confidence where correct) / sum(confidence).
    Update or create cascade_status node.
    Returns alignment_score.
    """
```

**Dependencies:** H2 (shared node factory), graph adapter for prediction queries.

**Tests:**
- `test_record_prediction_creates_node` — Prediction → cascade_prediction moment node with partner_relevance=0.95.
- `test_resolve_updates_node` — Resolution sets human_actual, correct, resolved_at.
- `test_alignment_requires_20_minimum` — Fewer than 20 resolved predictions → returns None.
- `test_alignment_below_075_suspends` — 60% accuracy → cascade_status = "suspended".
- `test_alignment_above_080_activates` — 85% accuracy → cascade_status = "active".
- `test_alignment_probation_zone` — 77% accuracy → cascade_status = "probation".
- `test_resolve_triggers_alignment_recalc` — Every resolution triggers measure_alignment_fidelity.

**Validates:** V8 (cascade accuracy threshold enforced).

---

## SHARED INTERFACES

### Needs from Force 5 (Physics Wiring)

| Interface | Description | Status |
|-----------|-------------|--------|
| `Stimulus` class | The `Stimulus` dataclass from `tick_runner_l1_cognitive_engine.py` — content, energy_budget, embedding, target_node_ids, is_social, source | Ported to `runtime/cognition/` |
| `L1Bridge.inject_message()` | Method to inject stimulus and run immediate ticks, returning cognitive context | Ported to `runtime/cognition/` |
| `LimbicState.drives` | Dict of Drive objects with intensity field — for direct drive delta application | In `runtime/cognition/models.py` |
| `CitizenCognitiveState.add_node()` | Method to add Node to citizen's graph | In `runtime/cognition/models.py` |

**Interim strategy:** `l1_stimulus_injector_for_partner_data.py` uses a protocol/interface that mirrors the L1 engine API. The interface adapter uses direct imports from `runtime.cognition`. No mock — the injector raises `RuntimeError("L1 engine not available")` if the engine module is not importable.

### Needs from Force 1 (Universe Graph)

| Interface | Description | Status |
|-----------|-------------|--------|
| Encrypted brain Space | Partner model content must be AES-256 encrypted at rest within the AI's brain Space | Task 1.5 (TODO) |
| HAS_ACCESS model | Only the AI citizen can access its own partner_model — no other actor, not even the human directly | Task 1.4 (TODO) |

**Impact if unavailable:** F3 code creates nodes in the graph without encryption. Encryption is applied at the storage layer (F1's responsibility). F3 proceeds assuming the storage layer handles encryption transparently.

### Provides to Force 4 (Trust Mechanics)

| Signal | Description | Consumer |
|--------|-------------|----------|
| Limbic drive deltas | Drive modulation increments from Garmin data — upstream inputs to F4's Limbic Delta scalar (`satisfaction_delta - frustration_delta - 0.5 * anxiety_delta`) | F4 ALGORITHM section 1.1 |
| Alignment fidelity score | `measure_alignment_fidelity()` output — float [0, 1] or None | F4 ALGORITHM section 2.4 (`update_bond_trust_from_alignment`) |
| Consent state | Consent records queryable by F4 for trust signal computation | F4 bond trust signals |

The relationship between F3 drive deltas and F4 Limbic Delta:
1. F3 `garmin_to_limbic()` produces drive deltas (e.g., affiliation += 0.15).
2. These modify `LimbicState.drives` directly.
3. F4 snapshots drives before/after an interaction.
4. F4 computes its Limbic Delta scalar from the drive state change.
5. F4 uses the Limbic Delta to update trust on the bond link.

F3 is upstream; F4 is downstream. F3 does not compute or reference F4's Limbic Delta scalar.

---

## EXTERNAL DEPENDENCIES

### APIs Required

| API | Used By | Auth | Rate Limits | Latency |
|-----|---------|------|-------------|---------|
| OpenAI Whisper | Voice pipeline (via existing `whisper_transcribe`) | API key (`OPENAI_API_KEY`) | Standard OpenAI limits | 1-3s per utterance |
| Garmin Connect Wellness API | Biometric pipeline | OAuth2 (user grants during bond formation) | ~200 req/day/user | ~500ms per request |
| OS Screenshot (mss) | Desktop pipeline | None (local OS access) | N/A | ~50ms per capture |
| pytesseract / easyocr | Desktop pipeline (OCR) | None (local processing) | N/A | ~200ms per image |
| Solana RPC (Helius/QuickNode) | Blockchain pipeline | API key | Varies by provider (free tier: ~25 req/sec) | ~100ms per request |
| Ethereum RPC (Alchemy/Infura) | Blockchain pipeline (secondary) | API key | Varies by provider | ~200ms per request |

### Environment Variables

| Variable | Pipeline | Required |
|----------|----------|----------|
| `OPENAI_API_KEY` | Voice (Whisper) | Yes (already exists for voice bridge) |
| `GARMIN_CLIENT_ID` | Garmin | Yes (for OAuth2 flow) |
| `GARMIN_CLIENT_SECRET` | Garmin | Yes (for OAuth2 flow) |
| `SOLANA_RPC_URL` | Blockchain | Yes (default: mainnet-beta) |
| `ETHEREUM_RPC_URL` | Blockchain | No (optional, for ETH monitoring) |
| `DESKTOP_OCR_ENGINE` | Desktop | No (default: pytesseract) |

---

## STATE MANAGEMENT

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| Consent records | Graph nodes (type=consent_record) | Per-citizen, per-stream | Created on grant, updated on revoke, permanent |
| Biometric baselines | `BiometricBaselineStore` in-memory + persisted to disk | Per-citizen, per-metric | Rolling 14-day window, rebuilt on startup |
| Garmin poll dedup cache | `GarminPoller._last_poll_data` (in-memory) | Per-citizen | Reset on process restart |
| Cascade predictions | Graph nodes (type=cascade_prediction) | Per-citizen | Created on prediction, resolved when human decides |
| Pipeline running state | `GarminPoller._running`, `DesktopCaptureScheduler._running`, etc. | Per-citizen, per-pipeline | Started on bond formation, stopped on dissolution/revocation |

### State Transitions

```
                    ┌──────────────────────────────────────────────────┐
                    │                                                  │
                    ▼                                                  │
consent: never_asked ──(grant_consent)──▶ granted ──(revoke_consent)──▶ revoked
                                            │                          │
                                            │                          ▼
                                            │                    (bulk redact)
                                            │                          │
                                            ▼                          ▼
                                      pipeline running           pipeline stopped
                                                                  data destroyed
```

```
cascade: ──(record)──▶ unresolved ──(resolve)──▶ resolved ──(measure)──▶ alignment_score
                                                                             │
                                                    ┌────────────────────────┤
                                                    ▼            ▼           ▼
                                               >= 0.80     0.75-0.80     < 0.75
                                               ACTIVE      PROBATION    SUSPENDED
```

---

## RUNTIME BEHAVIOR

### Initialization (on bond formation)

```
1. Bond formation ceremony completes → call start_pipelines(citizen_id)
2. Create initial consent_record nodes for each stream (status="never_asked")
3. Present consent dialog to human: list all streams, explain each
4. For each stream human grants → grant_consent(citizen_id, stream, scope)
5. For each granted stream → start corresponding poller/scheduler:
   - "garmin" → GarminPoller.start()
   - "desktop" → DesktopCaptureScheduler.start()
   - "blockchain" → BlockchainMonitor.start()
   - "ai_messages" → ConversationCaptureReceiver.start()
   - "voice" → no poller needed (triggered by voice bridge on message receipt)
   - "direct_chat" → no poller needed (existing pipeline)
6. Pipelines are now running
```

### Main Loop (per-pipeline)

```
Garmin (every 15 min):
1. GarminPoller fires timer
2. Fetch from Garmin Connect API
3. Dedup against last poll
4. check_consent → ingest_garmin_biometrics → inject
5. Sleep 15 min, repeat

Desktop (every 5 min):
1. DesktopCaptureScheduler fires timer
2. Capture screenshot via mss
3. check_consent → privacy_filter → OCR → create concept node → inject
4. Discard image bytes
5. Sleep 5 min, repeat

Blockchain (every 60 sec):
1. BlockchainMonitor fires timer
2. Fetch recent transactions from RPC
3. Filter for monitored wallets
4. For each new tx: check_consent → parse → create moment node → inject
5. Sleep 60 sec, repeat

Voice (event-driven):
1. Voice bridge receives audio bytes
2. Route to ingest_voice_message()
3. consent → STT → emotion → node → inject → discard audio

AI Conversations (webhook):
1. ConversationCaptureReceiver receives POST
2. Route to ingest_ai_conversation()
3. consent → score → node → inject
```

### Shutdown (on bond dissolution)

```
1. Bond dissolution triggers stop_pipelines(citizen_id)
2. Stop all pollers/schedulers gracefully (cancel async timers)
3. Data retention review:
   a. All consent nodes transition to "revoked"
   b. Bulk redaction of all partner_model nodes
   c. Cascade predictions are preserved (they are about the AI's performance, not human data)
4. BiometricBaselineStore data for this citizen is deleted
5. Garmin OAuth token is revoked via Garmin API
```

---

## CONCURRENCY MODEL

| Component | Model | Notes |
|-----------|-------|-------|
| GarminPoller | asyncio task | Single async task per citizen, started/stopped cleanly |
| DesktopCaptureScheduler | asyncio task | Single async task, screenshot capture is sync but fast (~50ms) |
| BlockchainMonitor | asyncio task | Single async task, handles multiple chains sequentially |
| ConversationCaptureReceiver | HTTP handler (FastAPI/aiohttp) | Async request handler, stateless |
| Voice ingestion | Inline async | Called within voice bridge handler, no separate task |
| Consent operations | Async with graph lock | Must be atomic — revocation + redaction in one transaction |
| Baseline calculations | Sync (numpy) | Fast enough for inline computation, no async needed |
| L1 stimulus injection | Sync with runner lock | Uses `_CitizenRunner.lock` from L1Bridge |

All pollers use `asyncio.sleep()` for their intervals, not threading. This keeps the concurrency model unified with the rest of the mind-mcp runtime (FastAPI + asyncio).

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `GARMIN_POLL_INTERVAL_S` | env var | `900` (15 min) | Garmin Connect polling interval |
| `DESKTOP_CAPTURE_INTERVAL_S` | env var | `300` (5 min) | Desktop screenshot interval |
| `BLOCKCHAIN_POLL_INTERVAL_S` | env var | `60` (1 min) | Blockchain RPC polling interval |
| `EMOTION_EXTRACTION_PHASE` | env var | `1` | `1` = prosody heuristics, `2` = classifier model |
| `DESKTOP_OCR_ENGINE` | env var | `pytesseract` | OCR engine: `pytesseract` or `easyocr` |
| `DESKTOP_APP_ALLOWLIST` | per-citizen config | `["code", "terminal", "browser"]` | Applications allowed for screenshot capture |
| `DESKTOP_BLOCKLIST_PATTERNS` | per-citizen config | `["password", "banking", "login"]` | OCR patterns that trigger screenshot rejection |
| `BASELINE_WINDOW_DAYS` | env var | `14` | Rolling window for biometric baselines |
| `BASELINE_MIN_DAYS` | env var | `7` | Minimum days before baselines are non-provisional |
| `CASCADE_WINDOW_SIZE` | env var | `100` | Number of predictions in alignment fidelity window |
| `CASCADE_MIN_PREDICTIONS` | env var | `20` | Minimum resolved predictions before alignment is computed |
| `CASCADE_ACTIVE_THRESHOLD` | env var | `0.80` | Alignment score for "active" status |
| `CASCADE_SUSPEND_THRESHOLD` | env var | `0.75` | Alignment score below which cascade is "suspended" |

---

## BIDIRECTIONAL LINKS

### Docs → Code (planned)

| Doc Section | Implemented In |
|-------------|----------------|
| ALGORITHM `check_consent` | `consent_gate_and_bond_validator.py:check_consent()` |
| ALGORITHM `revoke_consent` | `consent_gate_and_bond_validator.py:revoke_consent()` |
| ALGORITHM `ingest_voice_message` | `voice_emotion_extractor_and_memory_creator.py:ingest_voice_message()` |
| ALGORITHM `ingest_garmin_biometrics` | `garmin_biometric_poller_and_limbic_mapper.py:ingest_garmin_biometrics()` |
| ALGORITHM `garmin_to_limbic` | `garmin_biometric_poller_and_limbic_mapper.py:garmin_to_limbic()` |
| ALGORITHM `ingest_desktop_screenshot` | `desktop_screenshot_ocr_and_privacy_filter.py:ingest_desktop_screenshot()` |
| ALGORITHM `ingest_blockchain_activity` | `blockchain_transaction_monitor_and_parser.py:ingest_blockchain_activity()` |
| ALGORITHM `ingest_ai_conversation` | `ai_conversation_capture_and_memory_creator.py:ingest_ai_conversation()` |
| ALGORITHM `score_partner_relevance` | `partner_node_factory_and_relevance_scorer.py:score_partner_relevance()` |
| ALGORITHM `measure_alignment_fidelity` | `sovereign_cascade_prediction_tracker.py:measure_alignment_fidelity()` |
| ALGORITHM `record_cascade_prediction` | `sovereign_cascade_prediction_tracker.py:record_cascade_prediction()` |
| ALGORITHM `resolve_cascade_prediction` | `sovereign_cascade_prediction_tracker.py:resolve_cascade_prediction()` |
| ALGORITHM `garmin_poll_cycle` | `garmin_biometric_poller_and_limbic_mapper.py:GarminPoller._poll_cycle()` |
| VALIDATION V1 | `test_partner_node_factory_and_relevance_scorer.py` |
| VALIDATION V2 | `test_consent_gate_and_bond_validator.py` |
| VALIDATION V4 | `test_consent_gate_and_bond_validator.py` |
| VALIDATION V7 | `test_garmin_biometric_poller_and_limbic_mapper.py` |
| VALIDATION V8 | `test_sovereign_cascade_prediction_tracker.py` |
| VALIDATION V9 | `test_voice_emotion_extractor_and_memory_creator.py`, `test_desktop_screenshot_ocr_and_privacy_filter.py` |
| VALIDATION V10 | `test_baseline_calculator_for_biometric_deviation.py` |
| BEHAVIOR B1 | `garmin_biometric_poller_and_limbic_mapper.py` |
| BEHAVIOR B2 | `voice_emotion_extractor_and_memory_creator.py` |
| BEHAVIOR B3 | `sovereign_cascade_prediction_tracker.py` |
| BEHAVIOR B4 | `desktop_screenshot_ocr_and_privacy_filter.py` |
| BEHAVIOR B5 | `blockchain_transaction_monitor_and_parser.py` |
| BEHAVIOR B6 | `consent_gate_and_bond_validator.py:revoke_consent()` |

### Code → Docs (all files will include)

```python
# DOCS: docs/human_integration/IMPLEMENTATION_Human_Integration.md
# DOCS: docs/human_integration/ALGORITHM_Human_Integration.md
```

---

## TEST PLAN

### Test Structure

```
runtime/ingestion/tests/
├── __init__.py
├── test_consent_gate_and_bond_validator.py         # 6 tests
├── test_partner_node_factory_and_relevance_scorer.py  # 7 tests
├── test_garmin_biometric_poller_and_limbic_mapper.py   # 10 tests
├── test_voice_emotion_extractor_and_memory_creator.py  # 7 tests
├── test_desktop_screenshot_ocr_and_privacy_filter.py   # 5 tests
├── test_blockchain_transaction_monitor_and_parser.py   # 4 tests
├── test_ai_conversation_capture_and_memory_creator.py  # 4 tests
├── test_sovereign_cascade_prediction_tracker.py        # 7 tests
└── test_baseline_calculator_for_biometric_deviation.py # 4 tests
                                                        # Total: 54 tests
```

### Test Categories

**Unit tests (fast, no external deps):**
- All partner_relevance scoring tests
- All garmin_to_limbic mapping tests
- All baseline calculation tests
- Privacy filter logic tests
- Emotion extraction heuristic tests
- Cascade alignment computation tests

**Integration tests (require graph adapter, may use in-memory graph):**
- Consent grant/revoke with node creation/destruction
- Full pipeline tests (mock external API, real graph operations)
- Cascade prediction lifecycle (record → resolve → measure)

**Tests that verify cross-review fixes (from `REVIEW_F3_F4_Coherence.md`):**
- Issue 1: `test_state_node_is_actor_not_thing` — biometric nodes use node_type=actor, NOT thing.
- Issue 2: `test_garmin_deltas_are_drive_deltas_not_limbic_delta` — verify garmin_to_limbic returns per-drive increments, not F4's scalar.
- Issue 3: `test_partner_model_nodes_never_in_external_response` — V5 containment.

### Test Execution

```bash
# Run all F3 tests
pytest runtime/ingestion/tests/ -v

# Run a specific phase
pytest runtime/ingestion/tests/test_consent_gate_and_bond_validator.py -v

# Run with coverage
pytest runtime/ingestion/tests/ --cov=runtime/ingestion --cov-report=term-missing
```

**Coverage target:** 90% line coverage on all non-poller code. Pollers are tested with mocked asyncio timers and HTTP responses.

---

## MARKERS

<!-- @mind:todo Phase H2 depends on extracting whisper_transcribe() from voice_websocket.py into a shared utility, or importing it directly. Currently it is a module-level function — importable but not designed for reuse. Verify no side effects from importing the voice bridge module. -->

<!-- @mind:todo Define the Garmin OAuth2 flow for bond formation. Where is the token stored? How is it refreshed? The Garmin Connect API uses OAuth2 with refresh tokens. This is a bond formation concern (F1?) but F3 needs the token to poll. -->

<!-- @mind:escalation AI conversation capture (H6): the escalation from ALGORITHM still stands. The v1 webhook approach requires the human to actively forward messages. This creates friction and incomplete coverage. Browser extension is the pragmatic middle ground but needs a decision on whether to build it. -->

<!-- @mind:escalation Desktop OCR engine choice: pytesseract requires Tesseract system dependency. easyocr is pure Python but heavier (~200MB models). For a pip-installable package, easyocr is easier to distribute. For server deployment, pytesseract is lighter at runtime. Need decision on primary target deployment. -->

<!-- @mind:proposition Consider a unified IngestionMetrics class that tracks per-pipeline: nodes created, consent checks passed/failed, average processing time, last successful ingest timestamp. This would feed into the HEALTH checks from VALIDATION without requiring per-pipeline health implementations. -->
