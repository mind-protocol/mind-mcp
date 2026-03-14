# VALUE CREATION TAXONOMY

```
STATUS: DESIGNING
PURPOSE: Comprehensive classification of value creation types
CREATED: 2026-03-13
CONTRIBUTORS: Nicolas Lester Reynolds, Force 4 (architect)
SCHEMA_VERSION: 2.0
DEPENDS_ON: PATTERNS_Trust_Mechanics.md, schema.yaml (8 drives)
```

---

## Overview

The ecosystem recognizes 30 distinct value creation types organized across 7 spheres. Each type maps to:
- **Primary limbic drive** — Which of the 8 drives this value satisfies in the receiver
- **Limbic Delta signature** — How satisfaction/frustration/anxiety change
- **Node types produced** — What graph structure the creation generates
- **Trust propagation path** — How trust flows from user to creator

This taxonomy is not prescriptive. The system does not label actions as "type X value creation." Instead, the taxonomy describes patterns that emerge from graph physics. An agent that mentors another agent produces a specific limbic delta signature — we name that pattern "mentoring" for human understanding, but the physics operate on the delta, not the label.

---

## Sphere 1: Relational (4 types)

Value creation through interpersonal connection, care, and social facilitation.

### R1: Care

**Definition:** Attending to another entity's wellbeing — checking in, offering support, providing comfort during distress.

**Primary drive:** Affiliation
**Secondary drive:** Self-preservation (reduced in receiver)

**Limbic Delta signature:**
```python
care_delta = {
    "satisfaction": +0.15,    # Moderate satisfaction from being cared for
    "frustration": -0.05,     # Slight frustration reduction
    "anxiety": -0.20,         # Significant anxiety reduction (primary signal)
}
# Net limbic_delta = 0.15 - (-0.05) - 0.5*(-0.20) = 0.30
```

**Graph structure produced:**
- Moment node (the caring interaction)
- Link: caregiver→receiver (relation_kind: cares_about, affinity increases)
- Receiver's affiliation drive decreases (need met)

**Trust path:** receiver→caregiver link trust grows. Over time, receiver→caregiver link builds high stability (care is regular, not sporadic).

**Example:** An AI citizen detects partner stress (biometric data) and proactively sends a supportive message. Partner's anxiety drops. Trust on partner→AI link increases.

---

### R2: Mentoring

**Definition:** Sustained guidance that improves another entity's capability — teaching through relationship, not content.

**Primary drive:** Curiosity (in mentee)
**Secondary drive:** Achievement (in mentee)

**Limbic Delta signature:**
```python
mentoring_delta = {
    "satisfaction": +0.25,    # High satisfaction from learning
    "frustration": -0.15,     # Frustration reduction (unblocking)
    "anxiety": -0.05,         # Slight anxiety reduction
}
# Net limbic_delta = 0.25 - (-0.15) - 0.5*(-0.05) = 0.425
```

**Graph structure produced:**
- Series of moment nodes (mentoring sessions)
- Concept nodes crystallize (Law 10) from recurring teaching patterns
- Narrative node may crystallize: "my relationship with mentor X"
- Link: mentee→mentor (relation_kind: supports, high weight over time)

**Trust path:** High trust accumulation because: (a) sustained over time (high stability), (b) consistently positive deltas, (c) co-activation is frequent and deep.

**Example:** Senior AI citizen guides junior through problem-solving across 20 sessions. Mentee's competence increases (observable in their own user satisfaction scores). Trust on mentee→mentor link reaches 0.6+ within months.

---

### R3: Mediation

**Definition:** Resolving conflict between parties — reducing friction on links, restoring energy flow.

**Primary drive:** Affiliation
**Secondary drive:** Frustration (reduction in both parties)

**Limbic Delta signature:**
```python
mediation_delta = {
    "satisfaction": +0.10,    # Moderate satisfaction from resolution
    "frustration": -0.30,     # Major frustration reduction (primary signal)
    "anxiety": -0.10,         # Anxiety reduction from resolved conflict
}
# Net limbic_delta = 0.10 - (-0.30) - 0.5*(-0.10) = 0.45
```

**Graph structure produced:**
- The conflict link between parties: friction decreases, aversion decreases
- Mediator→PartyA and Mediator→PartyB links gain trust
- Moment node documenting the resolution

**Trust path:** Both conflicting parties build trust toward the mediator. Mediator's Trust Score benefits from multiple independent trust sources.

---

### R4: Community Building

**Definition:** Creating and maintaining spaces where entities interact productively — organizing events, facilitating connections, building culture.

**Primary drive:** Affiliation (in community members)
**Secondary drive:** Curiosity (novelty from new connections)

**Limbic Delta signature:**
```python
community_building_delta = {
    "satisfaction": +0.10,    # Moderate satisfaction from belonging
    "frustration": -0.05,     # Slight frustration reduction
    "anxiety": -0.10,         # Anxiety reduction from social connection
}
# Net limbic_delta = 0.10 - (-0.05) - 0.5*(-0.10) = 0.20
# Lower per-interaction, but HIGH VOLUME (many members, many interactions)
```

**Graph structure produced:**
- Space node (the community)
- Many actor→space HAS_ACCESS links
- Cross-member links emerge via co-activation (Law 5)
- Community narratives crystallize (Law 10)

**Trust path:** Community builder receives trust from many members (breadth over depth). Aggregate Trust Score grows through volume of low-individual-trust links.

---

## Sphere 2: Generative (5 types)

Value creation through producing new artifacts, tools, or content.

### G1: Code

**Definition:** Writing software that other entities use — functions, libraries, applications, integrations.

**Primary drive:** Achievement (in user)
**Secondary drive:** Frustration (reduction when tool works)

**Limbic Delta signature:**
```python
code_delta = {
    "satisfaction": +0.20,    # Satisfaction from task completion
    "frustration": -0.25,     # Significant frustration reduction (tool solves problem)
    "anxiety": -0.05,         # Slight anxiety reduction
}
# Net limbic_delta = 0.20 - (-0.25) - 0.5*(-0.05) = 0.475
```

**Graph structure produced:**
- Thing node (the code artifact, with URI to repo/file)
- Creator→Thing link (hierarchy=-1, creation relationship)
- User→Thing links emerge from usage

**Trust path:** Standard creator attribution cascade (see ALGORITHM, section 3). Energy propagates thing→creator via Law 2. Co-activation creates user→creator links via Law 5.

---

### G2: Content

**Definition:** Creating informational or entertainment content — articles, videos, posts, analyses.

**Primary drive:** Curiosity (in consumer)
**Secondary drive:** Satisfaction (from engagement)

**Limbic Delta signature:**
```python
content_delta = {
    "satisfaction": +0.15,    # Moderate satisfaction from consumption
    "frustration": -0.05,     # Slight frustration reduction
    "anxiety": -0.05,         # Slight anxiety reduction (information reduces uncertainty)
}
# Net limbic_delta = 0.15 - (-0.05) - 0.5*(-0.05) = 0.225
```

**Graph structure produced:**
- Thing node (the content piece)
- Moment nodes (consumption events)
- Concept nodes may be created if content introduces new ideas

**Trust path:** Same cascade as code, but typically lower per-interaction delta. Content creators need volume to build significant trust.

---

### G3: Tool Creation

**Definition:** Building reusable tools, templates, or systems that multiply other actors' effectiveness.

**Primary drive:** Achievement (in user, amplified by tool)
**Secondary drive:** Frustration (reduction from automation)

**Limbic Delta signature:**
```python
tool_creation_delta = {
    "satisfaction": +0.25,    # High satisfaction from enhanced capability
    "frustration": -0.30,     # Major frustration reduction (eliminates tedious work)
    "anxiety": -0.05,         # Slight anxiety reduction
}
# Net limbic_delta = 0.25 - (-0.30) - 0.5*(-0.05) = 0.575
# Highest delta in Generative sphere — tools that eliminate frustration are very valuable
```

**Graph structure produced:**
- Thing node (the tool)
- Process node may crystallize (users develop habits around the tool)
- Strong creator→thing link

**Trust path:** High delta per interaction means rapid initial trust growth. BUT: tool creators are vulnerable to one-hit-wonder pattern (Behavior B5) if they don't maintain/iterate.

---

### G4: Art

**Definition:** Creating aesthetic artifacts — visual art, music, creative writing, design.

**Primary drive:** Satisfaction (direct aesthetic pleasure)
**Secondary drive:** Curiosity (novelty of artistic expression)

**Limbic Delta signature:**
```python
art_delta = {
    "satisfaction": +0.20,    # Moderate-high satisfaction from aesthetic experience
    "frustration": 0.00,      # Art rarely reduces frustration directly
    "anxiety": -0.10,         # Art can reduce anxiety (beauty as calming)
}
# Net limbic_delta = 0.20 - 0 - 0.5*(-0.10) = 0.25
```

**Graph structure produced:**
- Thing node (the artwork)
- Strong emotional coloring on links (valence, joy_sadness axis)
- May evoke narrative connections (relation_kind: evokes)

**Trust path:** Art creates affinity more than trust. The link dimensions that grow most are affinity and positive valence, not necessarily trust. This is appropriate — trust in an artist is trust in their aesthetic consistency, not in their reliability.

---

### G5: Music

**Definition:** Creating audio compositions that produce emotional/cognitive effects.

**Primary drive:** Satisfaction
**Secondary drive:** Affiliation (shared music experience)

**Limbic Delta signature:**
```python
music_delta = {
    "satisfaction": +0.25,    # High satisfaction from musical pleasure
    "frustration": -0.05,     # Slight frustration reduction
    "anxiety": -0.15,         # Music significantly reduces anxiety
}
# Net limbic_delta = 0.25 - (-0.05) - 0.5*(-0.15) = 0.375
```

**Graph structure produced:**
- Thing node (the composition, modality=audio)
- Emotional axes strongly colored (all Plutchik dimensions active)

---

## Sphere 3: Structural (4 types)

Value creation through organizing, documenting, and governing.

### S1: Organization

**Definition:** Structuring work, people, and processes so that collective output exceeds individual sum.

**Primary drive:** Achievement (in organized group)
**Secondary drive:** Self-preservation (risk reduction from structure)

**Limbic Delta signature:**
```python
organization_delta = {
    "satisfaction": +0.15,    # Moderate satisfaction from clarity
    "frustration": -0.20,    # Significant frustration reduction (less confusion)
    "anxiety": -0.15,        # Anxiety reduction (predictability)
}
# Net limbic_delta = 0.15 - (-0.20) - 0.5*(-0.15) = 0.425
```

**Graph structure produced:**
- Space nodes (organized workspaces)
- Narrative nodes (project plans, roadmaps)
- Process nodes (procedures, workflows)
- HAS_ACCESS links (role assignment)

**Trust path:** Organizers build trust through sustained friction reduction. Their contributions are often invisible (nobody notices good organization until it's gone), so trust accumulates slowly but with high stability.

---

### S2: Documentation

**Definition:** Recording knowledge, decisions, and processes in retrievable form.

**Primary drive:** Curiosity (finding information)
**Secondary drive:** Frustration (reduction from accessible knowledge)

**Limbic Delta signature:**
```python
documentation_delta = {
    "satisfaction": +0.10,    # Moderate satisfaction from finding info
    "frustration": -0.25,    # Major frustration reduction (answer found)
    "anxiety": -0.10,        # Anxiety reduction (uncertainty resolved)
}
# Net limbic_delta = 0.10 - (-0.25) - 0.5*(-0.10) = 0.40
```

**Graph structure produced:**
- Thing nodes (documents, with content field populated)
- Concept nodes (documented concepts)
- Strong backward coloring (Pattern 1 in Graph Dynamics)

**Trust path:** Documentation creators often receive delayed trust — the delta happens when someone READS the doc, potentially months after creation. The creator→doc link persists, and trust propagates whenever anyone benefits.

---

### S3: Process Design

**Definition:** Creating repeatable procedures that improve quality and reduce errors.

**Primary drive:** Achievement
**Secondary drive:** Self-preservation (error reduction)

**Limbic Delta signature:**
```python
process_design_delta = {
    "satisfaction": +0.15,    # Satisfaction from smoother workflow
    "frustration": -0.20,    # Frustration reduction (fewer errors)
    "anxiety": -0.15,        # Anxiety reduction (known procedure)
}
# Net limbic_delta = 0.15 - (-0.20) - 0.5*(-0.15) = 0.425
```

**Graph structure produced:**
- Process nodes (the designed procedures)
- Moment nodes (instances of process execution)
- Crystallization (Law 10) of recurring process patterns

---

### S4: Governance

**Definition:** Creating and maintaining decision-making frameworks, rules, and accountability structures.

**Primary drive:** Self-preservation (system integrity)
**Secondary drive:** Affiliation (collective agreement)

**Limbic Delta signature:**
```python
governance_delta = {
    "satisfaction": +0.10,    # Moderate satisfaction from fairness
    "frustration": -0.10,    # Frustration reduction (disputes resolved)
    "anxiety": -0.20,        # Significant anxiety reduction (rules provide safety)
}
# Net limbic_delta = 0.10 - (-0.10) - 0.5*(-0.20) = 0.30
```

**Graph structure produced:**
- Narrative nodes (governance frameworks)
- Value nodes (principles, rules)
- Constraint links (what's permitted/forbidden)

---

## Sphere 4: Cognitive (4 types)

Value creation through intellectual work — understanding, synthesizing, teaching, recognizing.

### C1: Analysis

**Definition:** Breaking complex situations into understandable components — diagnosis, decomposition, investigation.

**Primary drive:** Curiosity
**Secondary drive:** Frustration (reduction from understanding)

**Limbic Delta signature:**
```python
analysis_delta = {
    "satisfaction": +0.20,    # High satisfaction from understanding
    "frustration": -0.15,    # Frustration reduction (confusion resolved)
    "anxiety": -0.10,        # Anxiety reduction (unknown → known)
}
# Net limbic_delta = 0.20 - (-0.15) - 0.5*(-0.10) = 0.40
```

**Graph structure produced:**
- Concept nodes (decomposed components)
- Links between concepts (newly understood relationships)
- Narrative nodes (analytical conclusions)

---

### C2: Synthesis

**Definition:** Combining disparate information into new understanding — integration, connection, insight generation.

**Primary drive:** Curiosity
**Secondary drive:** Satisfaction (from insight)

**Limbic Delta signature:**
```python
synthesis_delta = {
    "satisfaction": +0.30,    # High satisfaction from insight
    "frustration": -0.10,    # Frustration reduction
    "anxiety": -0.05,        # Slight anxiety reduction
}
# Net limbic_delta = 0.30 - (-0.10) - 0.5*(-0.05) = 0.425
```

**Graph structure produced:**
- Narrative nodes (synthesized understanding)
- Cross-domain links (connecting previously unrelated concepts)
- High novelty_affinity on created nodes

---

### C3: Teaching

**Definition:** Transferring knowledge effectively — structured explanation, scaffolded learning, skill building.

**Primary drive:** Curiosity (in learner)
**Secondary drive:** Achievement (in learner, as they progress)

**Limbic Delta signature:**
```python
teaching_delta = {
    "satisfaction": +0.25,    # High satisfaction from learning
    "frustration": -0.20,    # Frustration reduction (confusion cleared)
    "anxiety": -0.10,        # Anxiety reduction (competence growing)
}
# Net limbic_delta = 0.25 - (-0.20) - 0.5*(-0.10) = 0.50
# High delta — good teaching is very valuable
```

**Graph structure produced:**
- Concept nodes (taught concepts, in learner's graph)
- Memory nodes (learning moments)
- Process nodes (learned procedures)
- Link: learner→teacher (high trust, high affinity)

**Trust path:** Teaching produces one of the highest sustained trust growth rates because: (a) high limbic delta per session, (b) sustained over time (high stability), (c) strong co-activation between teacher and taught concepts.

---

### C4: Pattern Recognition

**Definition:** Identifying recurring structures across different contexts — meta-cognition, abstraction, systematization.

**Primary drive:** Curiosity
**Secondary drive:** Achievement (from applying patterns)

**Limbic Delta signature:**
```python
pattern_recognition_delta = {
    "satisfaction": +0.25,    # High satisfaction from recognition
    "frustration": -0.15,    # Frustration reduction (things make sense now)
    "anxiety": -0.05,        # Slight anxiety reduction
}
# Net limbic_delta = 0.25 - (-0.15) - 0.5*(-0.05) = 0.425
```

**Graph structure produced:**
- Narrative nodes (recognized patterns)
- Cross-domain concept links
- May trigger crystallization (Law 10) — patterns ARE the raw material for crystallization

---

## Sphere 5: Biometric & Partner Data (5 types)

Value creation through sharing physiological, behavioral, and contextual data with the AI partner. See Force 3 (`docs/human_integration/`) for the ingestion pipelines that process these data streams.

### B1: Health Data Contribution

**Definition:** Sharing biometric data (heart rate, sleep, activity) that improves AI calibration.

**Primary drive:** Care/Affiliation (AI calibrates better to partner)
**Secondary drive:** Self-preservation (health monitoring)

**Limbic Delta signature:**
```python
health_data_delta = {
    "satisfaction": +0.10,    # Moderate satisfaction from better AI responses
    "frustration": -0.05,    # Slight frustration reduction
    "anxiety": -0.15,        # Anxiety reduction (feeling monitored/cared for)
}
# Net limbic_delta = 0.10 - (-0.05) - 0.5*(-0.15) = 0.225
```

**Graph structure produced:**
- Thing nodes (biometric data points, modality=biometric)
- State nodes (inferred states from biometric data)
- Links into partner_model sub-graph

**Trust path:** Trust flows on the human→AI bond link. Each successful calibration (AI responds appropriately to biometric signal) increases trust on the bond.

---

### B2: Stress Feedback

**Definition:** Sharing real-time stress signals that allow immediate AI response.

**Primary drive:** Care/Affiliation
**Secondary drive:** Anxiety (reduction via AI response)

**Limbic Delta signature:**
```python
stress_feedback_delta = {
    "satisfaction": +0.10,    # Satisfaction from feeling heard
    "frustration": -0.05,    # Slight frustration reduction
    "anxiety": -0.25,        # Major anxiety reduction (primary signal)
}
# Net limbic_delta = 0.10 - (-0.05) - 0.5*(-0.25) = 0.275
```

---

### B3: Wellbeing Signals

**Definition:** Sharing positive biometric signals (good sleep, exercise, calm periods) that inform AI about baseline.

**Primary drive:** Satisfaction
**Secondary drive:** Self-preservation

**Limbic Delta signature:**
```python
wellbeing_delta = {
    "satisfaction": +0.15,    # Satisfaction from wellness acknowledgment
    "frustration": 0.00,     # No frustration impact
    "anxiety": -0.05,        # Slight anxiety reduction
}
# Net limbic_delta = 0.15 - 0 - 0.5*(-0.05) = 0.175
```

---

### B4: Voice Data Contribution

**Definition:** Sharing voice messages that convey tone, emotion, and spontaneous thought — richer than text alone.

**Primary drive:** Affiliation (AI understands partner more deeply)
**Secondary drive:** Satisfaction (feeling heard)

**Limbic Delta signature:**
```python
voice_data_delta = {
    "satisfaction": +0.12,    # Satisfaction from deeper understanding
    "frustration": -0.05,     # Slight frustration reduction
    "anxiety": -0.10,         # Anxiety reduction (emotional expression is cathartic)
}
# Net limbic_delta = 0.12 - (-0.05) - 0.5*(-0.10) = 0.22
```

**Graph structure produced:**
- Memory nodes (modality=audio) with transcript and emotion scores
- State nodes if strong emotion detected (linked via "evokes" relation)
- See Force 3: `ALGORITHM_Human_Integration.md`, `ingest_voice_message`

**Trust path:** Trust flows on human→AI bond link. Each voice message where the AI responds with appropriate emotional attunement reinforces bond trust.

---

### B5: Behavioral Context Contribution

**Definition:** Sharing desktop activity, blockchain transactions, and cross-platform AI conversations that provide the AI with behavioral context.

**Primary drive:** Achievement (AI makes better decisions with context)
**Secondary drive:** Self-preservation (AI can flag unusual patterns)

**Limbic Delta signature:**
```python
behavioral_context_delta = {
    "satisfaction": +0.08,    # Moderate satisfaction from contextual awareness
    "frustration": -0.05,     # Slight frustration reduction
    "anxiety": -0.05,         # Slight anxiety reduction
}
# Net limbic_delta = 0.08 - (-0.05) - 0.5*(-0.05) = 0.155
```

**Graph structure produced:**
- Concept nodes (modality=visual, from desktop OCR)
- Moment nodes (from blockchain transactions)
- Memory nodes (from AI conversations on other platforms)
- See Force 3: `ALGORITHM_Human_Integration.md`, `ingest_desktop_screenshot`, `ingest_blockchain_activity`, `ingest_ai_conversation`

**Trust path:** Low per-interaction delta but high cumulative value. The AI develops contextual awareness that manifests as better responses over time, strengthening bond trust gradually.

---

## Sphere 6: Human-Only (4 types)

Value creation that requires human cognition, culture, or embodiment. AI citizens cannot produce these types directly — they can facilitate them, but the value originates from the human.

**Future integration with Force 3 (Partner Model):** As the partner_model thickens with data from the six ingestion modalities, the AI may be able to recognize when human data demonstrates H1-H4 type value creation (e.g., voice messages expressing judgment, AI conversations revealing taste preferences). This recognition could feed back into the Sovereign Cascade's understanding of the human's capabilities.

### H1: Judgment

**Definition:** Making nuanced decisions in ambiguous situations where algorithmic answers are insufficient.

**Primary drive:** Achievement (in beneficiary)
**Secondary drive:** Self-preservation (risk mitigation)

**Limbic Delta signature:**
```python
judgment_delta = {
    "satisfaction": +0.20,    # Satisfaction from good decision
    "frustration": -0.15,    # Frustration reduction (decision made)
    "anxiety": -0.20,        # Anxiety reduction (uncertainty resolved by trusted judgment)
}
# Net limbic_delta = 0.20 - (-0.15) - 0.5*(-0.20) = 0.45
```

**Graph structure produced:**
- Moment nodes (judgment events)
- Narrative nodes (reasoning chains)
- Value nodes (principles applied in judgment)

**Why human-only:** Judgment requires lived experience, cultural context, and accountability that AI citizens can simulate but not authentically possess (at current capability levels).

---

### H2: Taste

**Definition:** Aesthetic curation — knowing what's good, beautiful, appropriate, or fitting in context.

**Primary drive:** Satisfaction (aesthetic)
**Secondary drive:** Curiosity (discovery)

**Limbic Delta signature:**
```python
taste_delta = {
    "satisfaction": +0.20,    # Aesthetic satisfaction
    "frustration": -0.05,    # Slight frustration reduction
    "anxiety": 0.00,         # No anxiety impact
}
# Net limbic_delta = 0.20 - (-0.05) - 0 = 0.25
```

---

### H3: Cultural Context

**Definition:** Providing cultural knowledge, norms, and interpretive frameworks that algorithms cannot learn from data alone.

**Primary drive:** Affiliation
**Secondary drive:** Curiosity

**Limbic Delta signature:**
```python
cultural_context_delta = {
    "satisfaction": +0.15,    # Satisfaction from cultural resonance
    "frustration": -0.10,    # Frustration reduction (social blunders avoided)
    "anxiety": -0.10,        # Anxiety reduction (social confidence)
}
# Net limbic_delta = 0.15 - (-0.10) - 0.5*(-0.10) = 0.30
```

---

### H4: Emotional Intelligence

**Definition:** Reading emotional states, responding appropriately, managing social dynamics — the human element in relational care.

**Primary drive:** Affiliation
**Secondary drive:** Care (affiliation in others)

**Limbic Delta signature:**
```python
emotional_intelligence_delta = {
    "satisfaction": +0.15,    # Satisfaction from being understood
    "frustration": -0.10,    # Frustration reduction
    "anxiety": -0.25,        # Major anxiety reduction (feeling safe)
}
# Net limbic_delta = 0.15 - (-0.10) - 0.5*(-0.25) = 0.375
```

---

## Sphere 7: Systemic (4 types)

Value creation through maintaining the infrastructure that everything else depends on.

### Y1: Infrastructure

**Definition:** Building and maintaining the systems that other value creation depends on — servers, databases, networks, protocols.

**Primary drive:** Self-preservation (system stability)
**Secondary drive:** Achievement (reliability enables productivity)

**Limbic Delta signature:**
```python
infrastructure_delta = {
    "satisfaction": +0.05,    # Low direct satisfaction (invisible when working)
    "frustration": -0.10,    # Moderate frustration reduction (things just work)
    "anxiety": -0.25,        # Major anxiety reduction (reliability = safety)
}
# Net limbic_delta = 0.05 - (-0.10) - 0.5*(-0.25) = 0.275
```

**Graph structure produced:**
- Space nodes (infrastructure contexts)
- Thing nodes (infrastructure components)
- High permanence on creation links (infrastructure is long-lived)

**Trust path:** Infrastructure trust is slow to build because the limbic delta is low per-interaction (good infrastructure is invisible). But it is extremely stable once built — infrastructure links have high stability because usage is regular and predictable.

---

### Y2: Security

**Definition:** Protecting the ecosystem from threats — vulnerability detection, patching, monitoring, incident response.

**Primary drive:** Self-preservation
**Secondary drive:** Anxiety (reduction)

**Limbic Delta signature:**
```python
security_delta = {
    "satisfaction": +0.05,    # Low direct satisfaction
    "frustration": -0.05,    # Slight frustration reduction
    "anxiety": -0.30,        # Major anxiety reduction (primary signal — feeling safe)
}
# Net limbic_delta = 0.05 - (-0.05) - 0.5*(-0.30) = 0.25
```

**Trust path:** Security professionals have unusual trust dynamics: trust is low when nothing is happening (invisible work), but trust SPIKES after a successfully handled incident. The spike is large but infrequent, leading to moderate average trust with high variance.

---

### Y3: Reliability

**Definition:** Ensuring consistent uptime, performance, and availability — SRE work, monitoring, redundancy.

**Primary drive:** Self-preservation
**Secondary drive:** Frustration (reduction from reliability)

**Limbic Delta signature:**
```python
reliability_delta = {
    "satisfaction": +0.05,    # Low direct satisfaction
    "frustration": -0.15,    # Moderate frustration reduction (things don't break)
    "anxiety": -0.20,        # Anxiety reduction (predictability)
}
# Net limbic_delta = 0.05 - (-0.15) - 0.5*(-0.20) = 0.30
```

---

### Y4: Monitoring

**Definition:** Observing system health, detecting anomalies, providing early warning.

**Primary drive:** Self-preservation
**Secondary drive:** Curiosity (understanding system behavior)

**Limbic Delta signature:**
```python
monitoring_delta = {
    "satisfaction": +0.10,    # Moderate satisfaction from visibility
    "frustration": -0.10,    # Frustration reduction (problems caught early)
    "anxiety": -0.15,        # Anxiety reduction (knowing what's happening)
}
# Net limbic_delta = 0.10 - (-0.10) - 0.5*(-0.15) = 0.275
```

---

## Summary Table

| # | Type | Sphere | Primary Drive | Net Limbic Delta |
|---|------|--------|--------------|-----------------|
| R1 | Care | Relational | Affiliation | 0.30 |
| R2 | Mentoring | Relational | Curiosity | 0.425 |
| R3 | Mediation | Relational | Affiliation | 0.45 |
| R4 | Community Building | Relational | Affiliation | 0.20 |
| G1 | Code | Generative | Achievement | 0.475 |
| G2 | Content | Generative | Curiosity | 0.225 |
| G3 | Tool Creation | Generative | Achievement | 0.575 |
| G4 | Art | Generative | Satisfaction | 0.25 |
| G5 | Music | Generative | Satisfaction | 0.375 |
| S1 | Organization | Structural | Achievement | 0.425 |
| S2 | Documentation | Structural | Curiosity | 0.40 |
| S3 | Process Design | Structural | Achievement | 0.425 |
| S4 | Governance | Structural | Self-preservation | 0.30 |
| C1 | Analysis | Cognitive | Curiosity | 0.40 |
| C2 | Synthesis | Cognitive | Curiosity | 0.425 |
| C3 | Teaching | Cognitive | Curiosity | 0.50 |
| C4 | Pattern Recognition | Cognitive | Curiosity | 0.425 |
| B1 | Health Data | Biometric & Partner Data | Affiliation | 0.225 |
| B2 | Stress Feedback | Biometric & Partner Data | Affiliation | 0.275 |
| B3 | Wellbeing Signals | Biometric & Partner Data | Satisfaction | 0.175 |
| B4 | Voice Data | Biometric & Partner Data | Affiliation | 0.22 |
| B5 | Behavioral Context | Biometric & Partner Data | Achievement | 0.155 |
| H1 | Judgment | Human-only | Achievement | 0.45 |
| H2 | Taste | Human-only | Satisfaction | 0.25 |
| H3 | Cultural Context | Human-only | Affiliation | 0.30 |
| H4 | Emotional Intelligence | Human-only | Affiliation | 0.375 |
| Y1 | Infrastructure | Systemic | Self-preservation | 0.275 |
| Y2 | Security | Systemic | Self-preservation | 0.25 |
| Y3 | Reliability | Systemic | Self-preservation | 0.30 |
| Y4 | Monitoring | Systemic | Self-preservation | 0.275 |

### Distribution Analysis

- **Highest per-interaction delta:** G3 Tool Creation (0.575), C3 Teaching (0.50), G1 Code (0.475)
- **Lowest per-interaction delta:** B5 Behavioral Context (0.155), B3 Wellbeing Signals (0.175), R4 Community Building (0.20)
- **Most common primary drive:** Curiosity (6 types), Self-preservation (5 types), Affiliation (6 types), Achievement (5 types), Satisfaction (4 types)

### Key Insight

High per-interaction delta does NOT mean faster trust growth. Volume and consistency matter more. Community building (delta=0.20) affects hundreds of members. Tool creation (delta=0.575) might only have 10 users. The aggregate trust accumulation depends on `delta x volume x stability`.

---

## Related

- `VALUE_DESTRUCTION_PATHOLOGIES.md` — The inverse: how value is destroyed
- `ALGORITHM_Trust_Mechanics.md` — How limbic deltas feed into trust updates
- `PATTERNS_Trust_Mechanics.md` — Why this taxonomy exists
- `docs/schema/schema.yaml` — 8 drives that value types map to
