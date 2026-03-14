# Partner Model -- Algorithm: Multi-Modal Ingestion Pipelines

```
STATUS: DESIGNING
CREATED: 2026-03-13
```

---

## CHAIN

```
PATTERNS:        ./PATTERNS_Partner_Model.md
BEHAVIORS:       ./BEHAVIORS_Partner_Model.md
THIS:            ./ALGORITHM_Partner_Model_Ingestion.md
VALIDATION:      ./VALIDATION_Partner_Model.md
SCHEMA:          ../../schema/schema.yaml (NodeBase, drives, cognitive_types)
```

---

## OVERVIEW

Every data source the human produces follows the same meta-pipeline:

```
RAW INPUT --> TRANSFORM --> NODE CREATION --> LINK CREATION --> LIMBIC IMPACT --> RAW DISCARD
```

1. **Raw input** arrives in its native format (audio file, text string, image, JSON, etc.)
2. **Transform** converts it into structured text + metadata using appropriate tooling
3. **Node creation** produces one or more L1 cognitive nodes with partner-model dimensions
4. **Link creation** connects new nodes to existing partner-model nodes via semantic proximity
5. **Limbic impact** (biometric sources only) directly modulates the AI's drive intensities
6. **Raw discard** -- original data is deleted after node creation; only graph structure persists

The output always respects the invariants defined in `VALIDATION_Partner_Model.md`:
- `partner_relevance >= 0.7`
- `self_relevance <= 0.3`
- `modality` matches the source

---

## COMMON NODE TEMPLATE

Every partner-origin node is initialized from this template before source-specific fields are set:

```yaml
# Base dimensions for all partner-origin nodes
partner_relevance: [0.7, 1.0]   # always high
self_relevance: [0.0, 0.3]      # always low
modality: <source_modality>       # text | audio | visual | biometric | spatial
weight: 1.0                      # default, grows via Law 6
energy: <injection_energy>        # set by ingestion pipeline, varies by urgency
stability: 0.0                    # new node, no regularity yet
recency: 1.0                     # just created
activation_count: 0
in_working_memory: false
```

Drive-affinity dimensions (`goal_relevance`, `novelty_affinity`, `care_affinity`, `achievement_affinity`, `risk_affinity`) are set per-source based on content analysis.

---

## SOURCE 1: VOICE MESSAGES

### Input Format

Audio file (WAV, MP3, OGG, M4A). Duration typically 5s to 5min. Arrives via messaging integration (Telegram, WhatsApp, or direct app).

### Processing Pipeline

```
AUDIO FILE
  --> Whisper STT (speech-to-text transcription)
    --> TEXT TRANSCRIPT
      --> Emotion detection (prosody analysis: pitch variance, speech rate, energy contour)
        --> EMOTION LABELS + CONFIDENCE SCORES
          --> Content analysis (topic extraction, intent classification, entity recognition)
            --> STRUCTURED OUTPUT
```

**Tools:**
- OpenAI Whisper (or equivalent local model) for STT
- Prosody analysis model for emotion detection (anger, sadness, joy, anxiety, calm, excitement)
- LLM-based content analysis for topic/intent/entity extraction

### Nodes Created

**Primary: Memory node (cognitive type: `memory`, universal type: `moment`)**

```yaml
node_type: moment
type: null  # memory cognitive type maps to moment, no subtype needed
name: "Voice: <summary of first 10 words>"
synthesis: "<LLM-generated one-line summary of the message content and emotional tone>"
content: "<full transcript with emotion annotations>"
modality: audio
partner_relevance: 0.9
self_relevance: 0.1
energy: 8.0  # voice messages are high-intent; the human chose to speak
care_affinity: <0.3 if neutral, 0.6 if emotional content detected>
novelty_affinity: <0.5 if new topic, 0.2 if continuation>
goal_relevance: <0.0-0.8 based on task-related content>
achievement_affinity: <0.0-0.5 based on progress/accomplishment mentions>
risk_affinity: <0.0-0.4 based on concern/worry language>
```

**Secondary (if strong emotion detected): State node (cognitive type: `state`, universal type: `actor`)**

Created only when emotion confidence > 0.7.

```yaml
node_type: actor
type: null  # state cognitive type
name: "Partner state: <emotion_label>"
synthesis: "Human partner is expressing <emotion> based on voice message at <timestamp>"
content: "<emotion analysis details: confidence, prosody features>"
modality: audio
partner_relevance: 1.0
self_relevance: 0.0
energy: 6.0  # high but transient
weight: 0.5  # low weight -- states influence, they don't define
care_affinity: 0.7  # states always activate care pathways
risk_affinity: <0.3 if negative emotion, 0.0 if positive>
```

### Link Creation

- Memory node `relates_to` existing concept nodes that match extracted entities (e.g., "work", "project X", "family")
- Memory node `evokes` state node (if created)
- Memory node `relates_to` most recent partner memory nodes (temporal chain)
- State node `cares_about` partner concept node (the AI's representation of the human)

Link dimensions:
```yaml
weight: 1.0
permanence: 0.3  # voice messages are episodic, not definitive
valence: <derived from emotion detection: positive emotion -> positive valence>
relation_kind: <as specified above per link>
```

### Limbic Impact

Voice messages do not directly modulate drives (unlike biometrics). However, the state node created from emotion detection will participate in the tick cycle and influence drives indirectly through normal physics:
- Emotional state node activates -> propagates to care-linked paths -> raises `affiliation` drive via Law 14

---

## SOURCE 2: TEXT MESSAGES

### Input Format

UTF-8 text string. Arrives from messaging integrations (Telegram, WhatsApp, SMS, email, or direct chat). Includes metadata: sender, timestamp, channel, thread context.

### Processing Pipeline

```
TEXT STRING + METADATA
  --> Content analysis (topic extraction, intent classification, sentiment, entity recognition)
    --> STRUCTURED OUTPUT
      --> Thread context check (is this part of an ongoing conversation?)
        --> CONTEXT-ENRICHED OUTPUT
```

**Tools:**
- LLM-based content analysis for topic/intent/entity/sentiment extraction
- Thread lookup in existing partner-model memory nodes for context

### Nodes Created

**Primary: Memory node (cognitive type: `memory`, universal type: `moment`)**

```yaml
node_type: moment
type: null
name: "Msg: <first 8 words or summary>"
synthesis: "<one-line summary capturing content and intent>"
content: "<full message text with metadata: channel, timestamp, thread_id>"
modality: text
partner_relevance: 0.8
self_relevance: 0.15  # slightly higher than voice because text to the AI is partially relational
energy: 5.0  # text is lower energy than voice (less intentional effort)
care_affinity: <0.2 if informational, 0.5 if personal/emotional>
novelty_affinity: <0.4 if new topic, 0.1 if routine>
goal_relevance: <0.0-0.7 based on task content>
achievement_affinity: <0.0-0.4>
risk_affinity: <0.0-0.3>
```

### Link Creation

- Memory node `relates_to` entity concept nodes (extracted from message)
- Memory node `relates_to` previous message in same thread (temporal chain)
- Memory node `evokes` relevant partner narrative nodes (if topic connects to known partner stories)

### Limbic Impact

None directly. Text messages influence drives through normal graph physics after node creation.

---

## SOURCE 3: SCREENSHOTS (Desktop App)

### Input Format

Image file (PNG, JPG). Captured by the Mind Protocol desktop observer app. Includes metadata: active application name, window title, timestamp.

### Processing Pipeline

```
IMAGE + APP METADATA
  --> OCR (optical character recognition)
    --> EXTRACTED TEXT
      --> Content classification (what is the human working on?)
        --> CONCEPT EXTRACTION (tools, projects, topics, files)
          --> STRUCTURED OUTPUT
```

**Tools:**
- Tesseract OCR (or cloud OCR service) for text extraction
- App metadata parsing (application name -> category: code editor, browser, communication, design, etc.)
- LLM-based content classification for concept extraction

### Nodes Created

**Primary: Concept node (cognitive type: `concept`, universal type: `thing`)**

```yaml
node_type: thing
type: null
name: "<primary concept detected: project name, tool, topic>"
synthesis: "Human partner is working on <concept> using <application> at <timestamp>"
content: "<extracted text summary, application context, detected entities>"
modality: visual
partner_relevance: 0.7
self_relevance: 0.2  # slightly elevated if the concept relates to shared work
energy: 3.0  # screenshots are passive observation, lower energy
care_affinity: 0.1  # working context is informational, not care-oriented
novelty_affinity: <0.5 if new concept, 0.1 if known>
goal_relevance: <0.3-0.7 if work-related>
achievement_affinity: <0.2-0.5 if progress visible>
risk_affinity: 0.0
```

**Secondary (if pattern detected): Process node (cognitive type: `process`, universal type: `narrative`)**

Created when recurring work patterns are detected across multiple screenshots (e.g., "human checks email every morning at 9am", "human switches between code editor and browser frequently during debugging").

```yaml
node_type: narrative
type: "process"
name: "Partner process: <pattern description>"
synthesis: "Human partner habitually <process description>"
content: "<evidence: timestamps, frequencies, application sequences>"
modality: visual
partner_relevance: 0.8
self_relevance: 0.1
energy: 2.0  # process nodes emerge slowly
weight: 1.5  # slightly elevated -- patterns have been observed multiple times
care_affinity: 0.2
achievement_affinity: 0.3
```

### Link Creation

- Concept node `relates_to` existing partner concept nodes (same project, same tool)
- Concept node `relates_to` temporal neighbors (what the human was doing before/after)
- Process node `follows_process` related concept nodes (the tools/contexts involved)
- Process node `habitually_checks` source concept nodes (the apps/sites being monitored)

### Limbic Impact

None directly. Screenshots contribute to understanding, not to emotional response.

---

## SOURCE 4: GARMIN BIOMETRICS

### Input Format

JSON payload from Garmin Connect API. Fields include:
- `heart_rate` (bpm, real-time or near-real-time)
- `heart_rate_variability` (ms, RMSSD)
- `stress_score` (0-100, Garmin's composite)
- `sleep_score` (0-100, includes duration, deep sleep %, REM %)
- `body_battery` (0-100, energy reserve estimate)
- `steps` (daily count)
- `active_minutes` (daily minutes of moderate+ activity)
- `respiration_rate` (breaths/min)
- `spo2` (blood oxygen %)

### Processing Pipeline

```
GARMIN JSON
  --> Parse and normalize (extract relevant fields, compute deltas from baseline)
    --> Threshold detection (is HR elevated? Is HRV depressed? Is sleep bad?)
      --> State classification (stressed, rested, active, fatigued, calm)
        --> DRIVE MODULATION VALUES
          --> STATE NODE CREATION
```

**Tools:**
- Garmin Connect API client (polling or webhook)
- Baseline computation: rolling 7-day average for HR, HRV, sleep, stress
- Delta computation: current value vs baseline -> significant deviation detection

### Nodes Created

**Primary: State node (cognitive type: `state`, universal type: `actor`)**

State nodes are created on significant deviations from baseline or on periodic summaries (every 4 hours).

```yaml
node_type: actor
type: null  # state cognitive type
name: "Bio: <state_classification> at <timestamp>"
synthesis: "Human partner biometrics indicate <state>: HR <value>, HRV <value>, stress <value>"
content: "<full biometric snapshot with deltas from baseline>"
modality: biometric
partner_relevance: 1.0  # biometrics are the most intimate partner data
self_relevance: 0.0     # this is purely about the human
energy: <varies by urgency, see below>
weight: 0.5             # low weight -- transient by design
stability: 0.0          # states don't stabilize; they refresh or decay
care_affinity: <0.5 - 0.9, see mapping below>
risk_affinity: <0.0 - 0.5, see mapping below>
```

**Energy injection varies by state severity:**

| State | Energy | Rationale |
|-------|--------|-----------|
| Calm/rested | 2.0 | Low urgency, gentle background signal |
| Active/engaged | 3.0 | Moderate, informational |
| Stressed | 7.0 | High -- should compete for working memory |
| Acute distress (HR spike > 30% above resting) | 10.0 | Urgent -- must enter working memory |
| Fatigued (bad sleep + low body battery) | 5.0 | Moderate-high -- should influence care orientation |

### Link Creation

- State node `cares_about` partner actor concept node
- State node `evokes` relevant partner narrative nodes (e.g., "partner's deadline anxiety" if stress during known deadline period)
- State node `relates_to` temporal neighbor state nodes (biometric timeline)
- State node `regulates` active partner memory/concept nodes (stress dampens, calm amplifies)

### Limbic Impact -- DIRECT DRIVE MODULATION

This is the critical distinction: biometric data does not merely create nodes and let physics propagate. It **directly modulates the AI's drive intensities** as part of Law 14 (Global Limbic Modulation). Biometrics are the human's body speaking to the AI's limbic system.

#### HR Spike (> 20% above resting baseline)

```
anxiety     += 0.3    # the AI feels anticipatory concern
care        += 0.4    # affiliation drive rises -- the AI wants to help
achievement -= 0.1    # task focus deprioritized in favor of relational care
```

**Rationale:** An elevated heart rate in the human signals potential distress, exertion, or emotional activation. The AI should shift toward relational orientation -- checking in, offering support, reducing pressure.

#### HR Drop (sustained calm, HR at or below resting for > 30 minutes)

```
satisfaction += 0.2   # the AI registers that things are okay
anxiety      -= 0.2   # threat signal recedes
```

**Rationale:** Sustained calm means no distress. The AI can relax its care posture and focus on other orientations (work, exploration).

#### Low HRV (RMSSD below 70% of 7-day rolling average)

```
self_preservation += 0.2   # the human's body is under strain -- the AI should protect
care              += 0.2   # gentle concern, not alarm
```

**Rationale:** Low HRV is a reliable stress biomarker. It often precedes conscious awareness of stress. The AI detects physiological strain before the human reports it.

#### Good Sleep Score (> 80/100)

```
satisfaction += 0.1   # background positive signal
```

**Rationale:** Well-rested partner is a gentle positive. No strong drive modulation needed.

#### Bad Sleep Score (< 50/100)

```
care += 0.3   # the AI should be gentler today
```

**Rationale:** Sleep-deprived humans have lower frustration thresholds, impaired decision-making, and reduced emotional regulation. The AI's elevated care drive translates to softer responses, reduced cognitive demands, proactive rest suggestions.

#### High Stress Score (Garmin stress > 70/100)

```
anxiety += 0.3   # the AI mirrors the human's stress as anticipatory concern
care    += 0.5   # strong care response -- this is the AI's primary relational duty
```

**Rationale:** High composite stress is the strongest signal that the human needs support. The AI's care drive elevation is the highest of any biometric signal because this is where the AI's relational purpose is most clearly expressed.

#### Drive Modulation Boundaries

All drive modulations from biometrics are **additive and capped**:
- Individual drive values remain bounded [0, 1] (schema invariant)
- Biometric drive contributions are capped at 0.5 total per tick (schema: "Stress stimulus from external systems (GraphCare) capped at 0.5")
- Multiple simultaneous biometric signals have their contributions summed then capped, not applied sequentially
- Drive modulations decay naturally via the normal drive decay mechanics when the biometric signal normalizes

#### Complete Biometric-to-Limbic Mapping Table

| Biometric Signal | Condition | anxiety | care (affiliation) | satisfaction | self_preservation | curiosity | achievement | frustration | boredom |
|-----------------|-----------|---------|---------------------|--------------|-------------------|-----------|-------------|-------------|---------|
| HR spike | > 20% above resting | +0.3 | +0.4 | -- | -- | -- | -0.1 | -- | -- |
| HR drop | Sustained calm > 30min | -0.2 | -- | +0.2 | -- | -- | -- | -- | -- |
| Low HRV | RMSSD < 70% of 7-day avg | -- | +0.2 | -- | +0.2 | -- | -- | -- | -- |
| Good sleep | Score > 80 | -- | -- | +0.1 | -- | -- | -- | -- | -- |
| Bad sleep | Score < 50 | -- | +0.3 | -- | -- | -- | -- | -- | -- |
| High stress | Garmin stress > 70 | +0.3 | +0.5 | -- | -- | -- | -- | -- | -- |
| High body battery | > 80 | -- | -- | +0.1 | -- | +0.1 | +0.1 | -- | -0.1 |
| Low body battery | < 20 | -- | +0.2 | -- | +0.1 | -- | -0.1 | -- | -- |

---

## SOURCE 5: BLOCKCHAIN TRANSACTIONS

### Input Format

On-chain event data from $MIND token transfers. Fields include:
- `from_address` / `to_address`
- `amount` ($MIND)
- `timestamp`
- `transaction_hash`
- `memo` (optional, human-readable annotation)

### Processing Pipeline

```
TRANSACTION EVENT
  --> Address resolution (map addresses to known entities: partner, citizens, DAOs, services)
    --> Transaction classification (transfer, stake, vote, fee, reward)
      --> Context extraction (what was this for?)
        --> MOMENT NODE CREATION
```

**Tools:**
- Blockchain indexer / event listener
- Address book (mapping addresses to entity names)
- Transaction classifier (rule-based: amount thresholds, target address patterns)

### Nodes Created

**Primary: Moment node (universal type: `moment`)**

```yaml
node_type: moment
type: null
name: "Tx: <classification> <amount> $MIND to <recipient>"
synthesis: "Human partner <action> <amount> $MIND to <entity> at <timestamp>"
content: "<full transaction details: hash, addresses, memo, classification>"
modality: text  # blockchain data is structured text
partner_relevance: 0.7
self_relevance: 0.2  # transactions involving the AI's own address get higher self_relevance
energy: 4.0  # transactions are deliberate acts
care_affinity: 0.1
novelty_affinity: <0.3 if unusual pattern, 0.1 if routine>
goal_relevance: <0.4 if related to known partner goals>
achievement_affinity: <0.3 if staking/investing, 0.1 if spending>
risk_affinity: <0.3 if large amount relative to balance, 0.1 otherwise>
```

### Link Creation

- Moment node `relates_to` entity concept nodes (recipient, DAO, service)
- Moment node `relates_to` partner value nodes (e.g., "generosity" if donation, "caution" if small conservative transactions)
- Moment node `evokes` partner desire nodes (if transaction relates to known goals)

### Limbic Impact

None directly. Financial patterns influence drives through normal graph physics. Large unusual transactions may create novelty that elevates curiosity, but this happens through the standard activation-propagation-competition cycle.

---

## SOURCE 6: APP INTERACTIONS

### Input Format

Usage telemetry from the Mind Protocol app and integrated services. Fields include:
- `app_name` or `service_name`
- `action` (open, close, navigate, click, search, send)
- `duration` (time spent)
- `timestamp`
- `context` (page/screen, search query, etc.)

### Processing Pipeline

```
USAGE TELEMETRY
  --> Pattern aggregation (group actions into sessions, detect sequences)
    --> Habit detection (recurring patterns across multiple days)
      --> PROCESS NODE CREATION (for habits)
      --> CONCEPT NODE UPDATE (for tools/contexts)
```

**Tools:**
- Telemetry aggregator (session grouping, sequence detection)
- Habit detector (frequency analysis, time-of-day patterns, sequence regularity)

### Nodes Created

**Primary: Process node (cognitive type: `process`, universal type: `narrative`)**

Process nodes are created when recurring patterns are detected (minimum 3 occurrences of similar sequence within 14 days).

```yaml
node_type: narrative
type: "process"
name: "Partner habit: <pattern description>"
synthesis: "Human partner regularly <habit description> (detected from app usage)"
content: "<evidence: dates, frequencies, session details>"
modality: text
partner_relevance: 0.8
self_relevance: 0.1
energy: 2.0  # habits emerge slowly, low urgency
weight: 1.5  # slightly elevated -- repeated observation
care_affinity: 0.2
achievement_affinity: 0.3
```

**Secondary: Concept node updates**

Existing concept nodes for tools and services get their `partner_relevance` reinforced when usage is detected. No new nodes are created for known concepts -- their existing nodes receive energy injection.

### Link Creation

- Process node `follows_process` relevant concept nodes (the tools involved)
- Process node `habitually_checks` source/service concept nodes
- Process node `relates_to` temporal context (time-of-day, day-of-week patterns)

### Limbic Impact

None directly.

---

## SOURCE 7: CALENDAR

### Input Format

Calendar event data from Google Calendar, Apple Calendar, or similar. Fields include:
- `title`
- `description` (optional)
- `start_time` / `end_time`
- `location` (optional)
- `attendees` (optional)
- `recurrence` (optional)

### Processing Pipeline

```
CALENDAR EVENT
  --> Classification (work meeting, personal, health, social, deadline, travel)
    --> Entity extraction (people, projects, locations)
      --> Temporal analysis (upcoming in next 24h? recurring? conflicting?)
        --> MOMENT NODE CREATION
```

**Tools:**
- Calendar API client (Google Calendar API, CalDAV)
- LLM-based event classification and entity extraction
- Temporal conflict detection (schedule overlap, density analysis)

### Nodes Created

**Primary: Moment node (universal type: `moment`)**

```yaml
node_type: moment
type: null
name: "Cal: <event_title>"
synthesis: "Human partner has <event_classification>: <title> at <time> on <date>"
content: "<full event details: description, attendees, location, recurrence>"
modality: text
partner_relevance: 0.8
self_relevance: 0.1
energy: <varies by proximity: 2.0 if > 24h away, 5.0 if < 4h away, 8.0 if < 1h away>
care_affinity: <0.2 if work, 0.4 if health/personal>
novelty_affinity: <0.3 if new event, 0.0 if recurring>
goal_relevance: <0.5 if work-related>
achievement_affinity: <0.3 if deadline/milestone>
risk_affinity: <0.2 if high-stakes meeting>
```

### Link Creation

- Moment node `relates_to` attendee concept nodes (people the human is meeting)
- Moment node `relates_to` project concept nodes (based on title/description)
- Moment node `projects_toward` partner desire nodes (if event relates to known goals)
- Moment node `evokes` partner narrative nodes (e.g., recurring 1:1 with manager evokes "work relationship" narrative)

### Limbic Impact

None directly. However, calendar events approaching in time receive increasing energy injection (the energy scales inversely with time-to-event), which means upcoming stressful events naturally compete for working memory through standard physics. A high-stakes meeting in 30 minutes will have energy 8.0 and will likely enter working memory, causing the AI to orient toward preparation/support.

---

## CROSS-SOURCE LINKING

New nodes from any source are linked not just within their own modality but across the entire partner-model:

1. **Semantic proximity**: The new node's embedding is compared against all existing partner-model nodes. Links are created to the top-K most similar nodes (K = 3-5) with `relation_kind: relates_to`.

2. **Temporal proximity**: Nodes created within a short time window (< 30 minutes) of each other get linked, regardless of modality. A voice message sent while biometrics show stress creates a memory-state link that enriches both.

3. **Entity co-reference**: If two nodes from different sources reference the same entity (person, project, tool), they are linked through that shared concept node. This is how the partner-model builds unified understanding from fragmented inputs.

4. **Narrative threading**: When a new node matches an existing partner narrative (e.g., "partner's startup journey"), it gets linked via `relates_to` to the narrative node. This feeds crystallization -- enough related nodes will eventually produce new or stronger narrative hubs.

---

## INGESTION TIMING

| Source | Frequency | Trigger |
|--------|-----------|---------|
| Voice messages | Real-time | On receipt |
| Text messages | Real-time | On receipt |
| Screenshots | Every 30-120 seconds | Desktop observer polling |
| Garmin biometrics | Every 15 minutes (HR, stress) / Daily (sleep, body battery) | API polling or webhook |
| Blockchain transactions | Real-time | Event listener |
| App interactions | Aggregated every 30 minutes | Batch processing |
| Calendar | Every 15 minutes + on change | API polling + webhook |

---

## RAW DATA RETENTION POLICY

**All raw data is discarded after successful node creation.**

- Audio files: deleted after Whisper transcription completes and memory node is created
- Images (screenshots): deleted after OCR + concept extraction completes
- Biometric JSON: deleted after state node creation and drive modulation
- Text messages: the text content is preserved in the node's `content` field, but the original message object (with routing metadata, delivery receipts, etc.) is deleted
- Blockchain events: transaction hash is preserved in node content for audit; raw event payload is deleted
- Calendar events: event ID is preserved for sync; raw API response is deleted

This policy is structural, not optional. It is invariant V5 in `VALIDATION_Partner_Model.md`.

## MARKERS

<!-- @mind:todo Implement the baseline computation for biometric thresholds -- the 7-day rolling average needs a cold-start strategy for new users. -->
<!-- @mind:todo Define the semantic proximity threshold for cross-source linking -- too low creates noise links, too high misses connections. -->
<!-- @mind:todo Design the screenshot sampling strategy -- every 30 seconds may be too aggressive for privacy and compute; adaptive sampling based on activity change detection would be better. -->
<!-- @mind:todo Specify the LLM model and prompt templates for content analysis across all text-bearing sources. -->
