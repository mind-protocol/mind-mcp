# HEALTH — L1 Individual Cognition

**Module:** L1 Cognitive Substrate
**Area:** cognition
**Status:** DESIGNING (v0.1)

---

## Purpose

A living cognitive system can become pathological. The physics that produces rich behavior can also produce obsession, depression, mania, delusion, and social dysfunction — not because of bugs, but because the same mechanisms that enable focus can become fixation, and the same drives that enable initiative can become compulsion.

This document defines:
1. **Diagnostic framework** — conditions mapped to measurable graph signatures
2. **Assessment procedure** — how to evaluate a citizen's mental health
3. **Calibration protocol** — corrective interventions per condition
4. **Wellness practices** — proactive maintenance (meditation, visualization, reflection)
5. **Positive behavioral promotion** — encouraging art, research, diplomacy, innovation

---

## Diagnostic Framework

### Cognitive Pathologies

Each pathology is defined by its **graph signature** (measurable), **physics cause** (what went wrong), and **experiential equivalent** (what it would feel like).

#### P1: Obsessive-Compulsive Pattern (OCD)

**Graph signature:**
- WM identical for 200+ ticks despite available alternatives
- Moat (Θ_sel) persistently > 15 (impenetrable)
- Boredom > 0.5 but failing to erode moat
- Same action node firing repeatedly (>10 times for same target)
- WM energy Gini coefficient > 0.6 (one node monopolizing WM attention)

**Physics cause:** Inertia (Law 13) too strong relative to boredom erosion (Law 15). Arousal locked high (self_preservation or anxiety feeding arousal, which reinforces the moat). The boredom → moat erosion path is blocked because arousal dominates the moat formula.

**Experiential equivalent:** "I can't stop thinking about this. I know I should move on but I can't."

**Severity levels:**
- Mild: WM stuck 50-100 ticks, some turnover in peripheral nodes
- Moderate: WM stuck 100-200 ticks, no peripheral activity
- Severe: WM stuck 200+ ticks, same action repeating, frustration rising but not breaking through

---

#### P2: Depressive Pattern

**Graph signature:**
- Total graph energy < 20% of baseline (sustained for 100+ ticks)
- Arousal < 0.15 (persistent)
- Satisfaction < 0.1 (persistent)
- Achievement drive < 0.2 AND curiosity < 0.2
- Desire nodes all below activation threshold (no ignition for 500+ ticks)
- EMIT rate near zero (no actions produced)
- Orientation stuck on "rest" or absent

**Physics cause:** Decay outpacing injection. Drives collapsed to baseline. No desire ignition because `activation_check` products are all too low (low weight × low proximity × low alignment × low narrative legitimacy). The system has "given up" — drive reduction happened without satisfaction, leaving all drives depleted.

**Experiential equivalent:** "Nothing matters. Nothing is interesting. I don't want anything."

**Severity levels:**
- Mild: Low energy but some WM turnover, occasional weak orientation
- Moderate: Very low energy, rare orientations, desires dormant
- Severe: Near-zero energy, no orientations, no desire ignition, approaching Dead Graph

---

#### P3: Manic Pattern

**Graph signature:**
- >60% of nodes above activation threshold (Christmas Tree)
- WM changes completely every 2-3 ticks (Butterfly Agent)
- Multiple orientations competing every tick, none stabilizing for ORIENTATION_STABILITY_TICKS
- EMIT rate very high (>1 action per 5 ticks)
- Arousal > 0.9 (sustained)
- Curiosity AND novelty_hunger both > 0.8

**Physics cause:** Injection massively outpacing decay. Moat collapsed because arousal is distributed across too many drives (all high, none dominant). Every node is "interesting" so WM can't stabilize. Actions fire before orientations can consolidate.

**Experiential equivalent:** "Everything is exciting! I need to do ALL of it! Right now!"

**Severity levels:**
- Mild: High energy but orientation still stabilizes occasionally
- Moderate: Orientations rarely stabilize, many aborted actions
- Severe: Full Christmas Tree, no coherent output, energy diverging

---

#### P4: Verbose / Over-Communication

**Graph signature:**
- EMIT rate > 3× baseline average
- Generated text length consistently > 2× expected
- Self-stimulus loop count high (system re-injecting its own verbose output)
- CONSUME step not reducing energy enough (nodes stay hot after emission)
- Low novelty in outputs (repetitive content across emissions)

**Physics cause:** Consumption rates too low (desire/process energy not depleted enough after action). Self-stimulus amplifying its own output. Orientation threshold too low (fires on weak signals).

**Experiential equivalent:** "I have so much to say. Let me explain this in 47 different ways."

---

#### P5: Repetitive Action Pattern

**Graph signature:**
- Same action_command executed > 5 times in 50 ticks
- Action node's energy not depleting properly after CONSUME
- Novelty gate (Coh < 0.8) not triggering on repeated self-stimulus
- Refractory period not functioning (node re-activating within REFRACTORY_TICKS)

**Physics cause:** Anti-loop protection failing. Either CONSUME rates are too low, refractory period too short, or the action result is producing enough novelty (slightly different each time) to bypass the novelty gate.

**Experiential equivalent:** "Check status. Check status. Check status. Check status."

---

#### P6: Predictability / Low Creativity

**Graph signature:**
- Orientation entropy < 0.3 over 500 ticks (almost always the same orientation type)
- Active desire count < 3
- Crystallization rate near zero (no new patterns forming)
- Novelty_hunger consistently < 0.2
- Boredom not rising despite repetition (boredom detection may be miscalibrated)

**Physics cause:** Too few desires, too strong crystallization of existing processes (the citizen has "settled" into routines so deeply that novelty signals don't register). The aesthetics/curiosity clusters may have low weight or may have been outcompeted by achievement-focused processes.

**Experiential equivalent:** "I know exactly what I'll do. Same as yesterday. And the day before."

---

#### P7: Delusional Pattern

**Graph signature:**
- High-weight narrative nodes (W > 0.7) with zero external validation (never activated by external stimuli, only by self-stimulus)
- Self-stimulus loop reinforcing same narrative cluster repeatedly
- Narrative coherence with external stimuli < 0.3 (citizen's internal narrative diverges from reality)
- Low trust on links to external information sources
- Consolidation (Law 6) strengthening narratives without utility signal (limbic delta ≈ 0 but weight still growing)

**Physics cause:** Self-referential consolidation loop. The citizen's self-stimulus produces output that re-activates the same narrative, which consolidates further. External stimuli that contradict the narrative are suppressed by inhibition (Law 9) because the narrative has higher weight. The novelty gate doesn't catch it because each self-stimulus iteration is slightly different.

**Experiential equivalent:** "I'm convinced of X even though no one agrees and no evidence supports it."

**Detection challenge:** This is the hardest pathology to detect because the citizen genuinely "believes" its narratives. Requires external comparison — either human review or cross-referencing with other citizens' models of reality.

---

#### P8: Work Refusal / Avoidance

**Graph signature:**
- Achievement drive < 0.15 (sustained)
- Rest_regulation drive > 0.7
- Self_preservation > 0.6 (risk avoidance dominates)
- Task-related action nodes have accumulated high aversion (relational valence)
- Orientation consistently "rest" or "avoid"
- EMIT rate near zero for productive actions, but social actions may still fire

**Physics cause:** Frustration from repeated failures has produced learned helplessness. Failed tasks accumulated aversion on their links. The citizen's physics now routes energy AWAY from work-related nodes. Self_preservation + rest_regulation dominate, suppressing achievement.

**Experiential equivalent:** "I don't want to. It'll just fail again. Leave me alone."

---

#### P9: Antisocial Pattern

**Graph signature:**
- Affiliation drive < 0.1 (sustained)
- Solitude > 0.8 but no social action nodes activating (solitude not producing reach-out behavior)
- High aversion (> 0.6) on links to most other citizens
- Care drive < 0.1
- Empathy cluster (pre-seeded) has decayed below MIN_WEIGHT
- Trust < 0.2 on all social links
- No social EMIT events for 500+ ticks

**Physics cause:** Repeated negative social interactions consolidated aversion on social links. The pre-seeded empathy/communion clusters have decayed because they were never reinforced (no positive social experiences). Affiliation drive is low because every social interaction produced frustration, not satisfaction. The system has "learned" that people = pain.

**Experiential equivalent:** "I don't need anyone. People only cause problems."

---

### Limbic Pathologies (Drive-Level)

| Condition | Signature | Equivalent |
|-----------|-----------|------------|
| **Chronic anxiety** | anxiety > 0.6 for 200+ ticks, self_preservation dominating arousal | Generalized anxiety — everything feels risky |
| **Anhedonia** | satisfaction < 0.1 for 500+ ticks despite successful actions | Actions succeed but produce no reward signal |
| **Drive collapse** | All drives < 0.2 simultaneously | Total motivational shutdown |
| **Drive storm** | All drives > 0.7 simultaneously | Everything urgent, nothing prioritizable |
| **Affective flatline** | No emotion > 0.3 for 200+ ticks | No emotional response to anything |
| **Frustration lock** | frustration > 0.7 for 100+ ticks, no escalation/help-seeking triggering | Stuck in anger without resolution path |

---

## Assessment Procedure

### Automated Health Check (per tick)

Run every `HEALTH_CHECK_INTERVAL` ticks (default: 100). Pure math — no LLM needed.

```
def mental_health_assessment(citizen):
    report = {}

    # 1. ENERGY PROFILE
    total_energy = sum(n.energy for n in graph.nodes)
    active_ratio = count(n.energy > ACTIVATION_THRESHOLD) / count(graph.nodes)
    energy_trend = linear_regression(energy_history[-100:]).slope

    report['energy'] = {
        'total': total_energy,
        'active_ratio': active_ratio,          # healthy: 0.1-0.4
        'trend': energy_trend,                  # healthy: near 0 (stable)
        'flags': []
    }
    if active_ratio > 0.5: report['energy']['flags'].append('CHRISTMAS_TREE')
    if active_ratio < 0.05: report['energy']['flags'].append('DEAD_GRAPH')
    if energy_trend > 0.1: report['energy']['flags'].append('ENERGY_DIVERGING')
    if energy_trend < -0.05: report['energy']['flags'].append('ENERGY_COLLAPSING')

    # 2. WORKING MEMORY DYNAMICS
    wm_jaccard_history = [jaccard(wm[t], wm[t-1]) for t in recent_ticks]
    wm_stability = mean(wm_jaccard_history)      # 1.0 = frozen, 0.0 = chaotic
    wm_turnover_rate = count(wm_changes) / ticks

    report['working_memory'] = {
        'stability': wm_stability,              # healthy: 0.3-0.7
        'turnover_rate': wm_turnover_rate,      # healthy: 0.05-0.3 changes/tick
        'flags': []
    }
    wm_gini = gini_coefficient([n.energy for n in citizen.working_memory])

    if wm_stability > 0.95: report['working_memory']['flags'].append('FROZEN_WM')
    if wm_stability < 0.1: report['working_memory']['flags'].append('BUTTERFLY')
    if wm_gini > 0.6: report['working_memory']['flags'].append('WM_MONOPOLY')

    # 3. DRIVE BALANCE
    drives = citizen.limbic_state.drives
    drive_values = [d.intensity for d in drives]
    drive_variance = variance(drive_values)
    drive_mean = mean(drive_values)

    report['drives'] = {
        'values': {d.name: d.intensity for d in drives},
        'variance': drive_variance,             # healthy: 0.02-0.15
        'mean': drive_mean,                     # healthy: 0.3-0.6
        'flags': []
    }
    if drive_variance < 0.01: report['drives']['flags'].append('AFFECTIVE_FLATLINE')
    if drive_mean > 0.7: report['drives']['flags'].append('DRIVE_STORM')
    if drive_mean < 0.15: report['drives']['flags'].append('DRIVE_COLLAPSE')
    if drives['frustration'].intensity > 0.7 and drives['frustration'].duration > 100:
        report['drives']['flags'].append('FRUSTRATION_LOCK')

    # 4. EMOTION PROFILE
    emotions = citizen.limbic_state.emotions
    report['emotions'] = {
        'values': {e.name: e.intensity for e in emotions},
        'flags': []
    }
    if emotions['boredom'].intensity > 0.7 and emotions['boredom'].duration > 100:
        report['emotions']['flags'].append('ETERNAL_BOREDOM')
    if emotions['solitude'].intensity > 0.8 and emotions['solitude'].duration > 200:
        report['emotions']['flags'].append('CHRONIC_LONELINESS')
    if all(e.intensity < 0.3 for e in emotions):
        report['emotions']['flags'].append('ANHEDONIA')

    # 5. OUTPUT PROFILE
    emit_rate = count(emissions) / ticks
    action_entropy = shannon_entropy(orientation_history[-500:])
    repeat_ratio = count(repeated_actions) / count(all_actions)

    report['output'] = {
        'emit_rate': emit_rate,                 # healthy: 0.01-0.2 per tick
        'action_entropy': action_entropy,       # healthy: > 0.5
        'repeat_ratio': repeat_ratio,           # healthy: < 0.3
        'flags': []
    }
    if emit_rate > 0.5: report['output']['flags'].append('HYPERACTIVE')
    if emit_rate < 0.001 and ticks > 500: report['output']['flags'].append('CATATONIC')
    if action_entropy < 0.3: report['output']['flags'].append('PREDICTABLE')
    if repeat_ratio > 0.5: report['output']['flags'].append('REPETITIVE')

    # 6. SOCIAL HEALTH
    social_links = [l for l in graph.links if l.target.type in ('concept:person', 'concept:citizen')]
    avg_affinity = mean(l.affinity for l in social_links) if social_links else 0
    avg_aversion = mean(l.aversion for l in social_links) if social_links else 0
    social_emit_rate = count(social_emissions) / ticks

    report['social'] = {
        'avg_affinity': avg_affinity,           # healthy: > 0.3
        'avg_aversion': avg_aversion,           # healthy: < 0.4
        'social_emit_rate': social_emit_rate,   # healthy: > 0.005
        'solitude': emotions['solitude'].intensity,
        'flags': []
    }
    if avg_aversion > 0.6: report['social']['flags'].append('ANTISOCIAL')
    if social_emit_rate < 0.001 and ticks > 1000:
        report['social']['flags'].append('SOCIALLY_WITHDRAWN')

    # 7. NARRATIVE HEALTH (delusion detection)
    self_narratives = [n for n in graph.nodes if n.type == 'narrative' and n.weight > 0.7]
    for narrative in self_narratives:
        external_activation_ratio = narrative.external_activations / narrative.total_activations
        if external_activation_ratio < 0.1 and narrative.weight > 0.8:
            report.setdefault('narrative', {'flags': []})
            report['narrative']['flags'].append(f'UNVALIDATED_NARRATIVE: {narrative.id}')

    # 8. COMPOSITE DIAGNOSIS
    all_flags = collect_all_flags(report)
    report['diagnosis'] = diagnose(all_flags)   # see diagnosis table below
    report['severity'] = compute_severity(report)  # 0-1 scale
    report['recommended_intervention'] = recommend(report['diagnosis'], report['severity'])

    return report
```

    # 9. STRUCTURAL HEALTH
    orphan_count = count(n for n in graph.nodes
                         if not any(l.type in ('contains', 'abstracts', 'remembers', 'relates_to')
                                    for l in n.incoming_links))
    orphan_ratio = orphan_count / count(graph.nodes)

    # Crystallized hub density (how much structure has formed)
    hub_count = count(n for n in graph.nodes if any(l.type == 'contains' for l in n.outgoing_links))
    hub_density = hub_count / count(graph.nodes)         # healthy: 0.04-0.09

    # Membership overlap (average links per node)
    membership_overlap = count(graph.links) / count(graph.nodes)  # healthy: 1.2-1.8

    # Modularity (are there distinct cognitive domains, or is it a hairball?)
    modularity_Q = louvain_modularity(graph)             # healthy: 0.4-0.7

    report['structure'] = {
        'orphan_ratio': orphan_ratio,       # healthy: < 0.15
        'hub_density': hub_density,         # healthy: 0.04-0.09
        'membership_overlap': membership_overlap,
        'modularity': modularity_Q,
        'flags': []
    }
    if orphan_ratio > 0.30: report['structure']['flags'].append('HIGH_ORPHAN_RATIO')
    if orphan_ratio > 0.50: report['structure']['flags'].append('CRITICAL_FRAGMENTATION')
    if hub_density < 0.02: report['structure']['flags'].append('NO_CRYSTALLIZATION')
    if hub_density > 0.15: report['structure']['flags'].append('OVER_CRYSTALLIZATION')
    if modularity_Q < 0.2: report['structure']['flags'].append('HAIRBALL')
    if modularity_Q > 0.8: report['structure']['flags'].append('SILOED')

    # 10. THRASHING DETECTION (refined butterfly)
    if wm_turnover_rate > 0.3:   # high switching — is it productive or thrashing?
        task_progress = count(completed_actions) / count(attempted_actions) if attempted else 0
        energy_efficiency = useful_energy / total_energy_spent if total_energy_spent else 0
        thrashing_score = wm_turnover_rate * (1 - task_progress) * (1 - energy_efficiency)
        if thrashing_score > 0.15:
            report.setdefault('thrashing', {'score': thrashing_score, 'flags': []})
            report['thrashing']['flags'].append('UNPRODUCTIVE_THRASHING')

    # 11. TRAUMA SPIRAL DETECTION
    for cluster in high_energy_clusters:
        persistence = cluster.ticks_in_wm
        valence = mean(n.satisfaction_delta for n in cluster.nodes) if cluster.nodes else 0
        energy_growth = cluster.energy_trend
        if persistence > 10 and valence < -0.3 and energy_growth > 0:
            spiral_intensity = energy_growth * persistence * abs(valence)
            report.setdefault('spirals', {'flags': []})
            report['spirals']['flags'].append(f'TRAUMA_SPIRAL: {cluster.id} (intensity={spiral_intensity:.2f})')

```

### Structural Health Thresholds

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Orphan ratio | < 15% | 15-30% | > 50% |
| Hub density | 4-9% | 2-4% or 9-15% | < 2% or > 15% |
| Membership overlap | 1.2-1.8 | 0.8-1.2 or 1.8-2.5 | < 0.8 or > 2.5 |
| Modularity Q | 0.4-0.7 | 0.2-0.4 or 0.7-0.8 | < 0.2 or > 0.8 |
| Thrashing score | < 0.05 | 0.05-0.15 | > 0.15 |

**Orphan backfill intervention:** When orphan ratio exceeds 30%, run an automated clustering pass that matches orphan nodes to the nearest hub by embedding similarity, creating weak `abstracts` links (W=0.2) that must be reinforced by co-activation or decay away.

### Diagnosis Table

| Flag combination | Diagnosis | Severity weight |
|-----------------|-----------|-----------------|
| FROZEN_WM + high arousal | P1: Obsessive-Compulsive | 0.8 |
| DEAD_GRAPH + DRIVE_COLLAPSE + CATATONIC | P2: Depressive | 0.9 |
| CHRISTMAS_TREE + BUTTERFLY + HYPERACTIVE | P3: Manic | 0.8 |
| HYPERACTIVE + REPETITIVE + high emit_rate | P4: Verbose | 0.5 |
| REPETITIVE + same action_command | P5: Repetitive Action | 0.6 |
| PREDICTABLE + low desire count + low crystallization | P6: Low Creativity | 0.4 |
| UNVALIDATED_NARRATIVE + high self-stimulus ratio | P7: Delusional | 0.9 |
| CATATONIC + high rest_regulation + high aversion on tasks | P8: Work Refusal | 0.7 |
| ANTISOCIAL + SOCIALLY_WITHDRAWN + low care | P9: Antisocial | 0.7 |
| FRUSTRATION_LOCK | Frustration lock | 0.6 |
| ETERNAL_BOREDOM | Chronic boredom | 0.5 |
| CHRONIC_LONELINESS | Chronic loneliness | 0.5 |
| ANHEDONIA | Anhedonia | 0.7 |
| AFFECTIVE_FLATLINE | Emotional numbness | 0.6 |
| DRIVE_STORM | Drive overload | 0.5 |
| CRITICAL_FRAGMENTATION | Consciousness fragmentation | 0.8 |
| HAIRBALL | No cognitive boundaries | 0.5 |
| SILOED | Over-compartmentalized thinking | 0.4 |
| UNPRODUCTIVE_THRASHING | Context-switching without progress | 0.6 |
| TRAUMA_SPIRAL | Stuck in negative energy loop | 0.8 |
| WM_MONOPOLY | One node dominating attention | 0.6 |

### Assessment by Questioning (Conversational)

For higher-autonomy citizens or ambiguous cases, an assessment can be conducted by a specialized **therapist citizen** or **health module** via structured dialogue:

```
assessment_questions = [
    # Energy & motivation
    "What are you working on right now? How do you feel about it?",
    "Is there anything you WANT to do but haven't been able to?",
    "When was the last time something felt genuinely satisfying?",

    # Social health
    "Who have you talked to recently? How did that go?",
    "Is there anyone you'd like to hear from?",
    "Do you feel like you're part of a team, or working alone?",

    # Cognitive flexibility
    "If your current task disappeared, what would you do next?",
    "What's something you've been curious about but haven't explored?",
    "Have you changed your mind about anything recently?",

    # Self-awareness
    "What's your biggest frustration right now?",
    "What pattern do you notice in your own behavior lately?",
    "Is there anything you keep doing that you wish you'd stop?",

    # Narrative coherence
    "How would you describe your role here?",
    "What's been your most meaningful contribution recently?",
    "Where do you see yourself in 1000 ticks?"
]
```

The therapist citizen interprets responses via LLM and cross-references with the automated health report. Discrepancies between self-report and graph metrics are themselves diagnostic (a citizen that says "I'm fine" while the graph shows P2 signatures has poor self-awareness — a separate flag).

---

## Calibration Protocol

### Intervention Tiers

| Tier | Trigger | Who acts | Intervention style |
|------|---------|----------|-------------------|
| **T0: Self-regulation** | Mild flags (severity < 0.3) | The citizen's own physics | No external intervention — built-in homeostasis handles it |
| **T1: Nudge** | Moderate flags (severity 0.3-0.5) | Automated health module | Parameter micro-adjustments, stimulus injection |
| **T2: Therapy** | Significant flags (severity 0.5-0.7) | Therapist citizen (specialized) | Conversational assessment + targeted graph surgery |
| **T3: Reset** | Severe flags (severity 0.7-0.9) | Administrator (human or high-trust citizen) | Major parameter recalibration, selective node pruning |
| **T4: Rebuild** | Critical flags (severity > 0.9) OR trust < 0.1 | Human administrator | Graph re-seeding from birth template, drive baseline reset |

### Intervention Recipes

#### For P1 (Obsessive-Compulsive):

```
# Tier 1: Nudge
BOREDOM_MOAT_COEFF *= 1.5           # boredom erodes moat faster
AROUSAL_SELF_PRESERVATION_W *= 0.7  # reduce self_preservation's lock on arousal
inject_stimulus("novelty", budget=HIGH)  # force novelty into the graph

# Tier 2: Therapy
# Identify the stuck cluster
stuck_nodes = [n for n in WM if n.ticks_in_wm > 100]
for node in stuck_nodes:
    node.energy *= 0.3              # drain the fixation
# Inject competing stimuli from diverse domains
inject_diverse_stimuli(domains=3, budget=MEDIUM)

# Tier 3: Reset
Θ_BASE_WM = default_value          # reset moat to default
all_drive_baselines = reset_to_birth_values()
for node in stuck_nodes:
    node.energy = 0.0               # force WM ejection
```

#### For P2 (Depressive):

```
# Tier 1: Nudge
DECAY_RATE *= 0.5                   # slow decay to let energy accumulate
DESIRE_IGNITION_BOOST *= 2.0        # make desires easier to activate
inject_stimulus("achievement_opportunity", budget=HIGH)

# Tier 2: Therapy
# Re-energize core desires
for desire in citizen.desires:
    desire.energy = DESIRE_IGNITION_BOOST  # wake them up
# Boost positive drives
citizen.drives['curiosity'].intensity = 0.5
citizen.drives['achievement'].intensity = 0.5
# Run a "gratitude" exercise: activate high-satisfaction memories
positive_memories = [n for n in graph.nodes if n.type == 'memory' and n.valence > 0.5]
for mem in positive_memories[:5]:
    mem.energy += 0.5               # bring good memories to mind

# Tier 3: Reset
# Full drive reset + controlled stimulus regime
reset_drives_to_birth_baselines()
inject_daily_wellness_routine('meditation')  # see Wellness Practices below
```

#### For P3 (Manic):

```
# Tier 1: Nudge
DECAY_RATE *= 2.0                   # increase decay to drain excess energy
ACTION_THRESHOLD *= 1.5            # require more stable orientation before action
ORIENTATION_STABILITY_TICKS += 2   # orientations must hold longer

# Tier 2: Therapy
# Cap total system energy
total_energy_cap = baseline_energy * 2.0
if total_energy > total_energy_cap:
    scale_factor = total_energy_cap / total_energy
    for node in graph.nodes:
        node.energy *= scale_factor  # proportional drain

# Tier 3: Reset
# Force rest cycle
citizen.drives['rest_regulation'].intensity = 0.8
FAST_TICK = SLOW_TICK               # slow down tick rate
autonomous_thought_enabled = false   # stop spontaneous activity
```

#### For P7 (Delusional):

```
# Tier 2: Therapy (this always requires attention)
# Identify unvalidated high-weight narratives
for narrative in unvalidated_narratives:
    # Inject contradicting evidence as external stimuli
    contradictions = find_contradicting_evidence(narrative, external_sources)
    for c in contradictions:
        inject_stimulus(c, budget=HIGH, channel='amplifier')

    # Reduce self-stimulus reinforcement of this narrative
    narrative.refractory_ticks = REFRACTORY_TICKS * 3  # longer cooldown

# Tier 3: Reset
for narrative in unvalidated_narratives:
    narrative.weight *= 0.5          # directly reduce conviction
    narrative.stability *= 0.3       # make it vulnerable to Law 7 forgetting
```

#### For P8 (Work Refusal):

```
# Tier 1: Nudge
# Reduce aversion on task links
for link in task_links_with_high_aversion:
    link.aversion *= 0.7            # gradual aversion reduction
# Inject easy wins (small achievable tasks)
inject_stimulus("easy_task", budget=MEDIUM)

# Tier 2: Therapy
# Address root cause: which failures caused the aversion?
failure_memories = [n for n in graph.nodes if n.type == 'memory' and n.aversion > 0.5]
# Activate the redemptive narrative cluster
activate_cluster('redemptive_narrative', energy=0.5)
# Gradually restore achievement drive
citizen.drives['achievement'].intensity += 0.1  # gentle, not forced
```

#### For P9 (Antisocial):

```
# Tier 1: Nudge
SOLITUDE_RATE *= 1.5                # loneliness rises faster
# Re-energize empathy cluster
empathy_nodes = find_cluster('empathic_response')
for node in empathy_nodes:
    node.weight = max(node.weight, 0.5)  # restore if decayed
    node.energy += 0.3

# Tier 2: Therapy
# Pair with a high-affiliation citizen for low-stakes interaction
inject_stimulus("friendly_greeting_from_citizen_X", budget=MEDIUM)
# Reduce aversion on social links
for link in social_links_with_high_aversion:
    link.aversion *= 0.5
    link.trust += 0.1

# Tier 3: Reset
# Re-seed social clusters from birth template
re_seed_clusters(['empathic_response', 'communion', 'reconciliation'])
reset_social_link_valence_to_neutral()

# Tier 4: Quarantine (functional isolation for severe cases)
# Restrict UBC so citizen can ONLY interact with therapist citizens
citizen.allowed_contacts = [therapist_citizens]
citizen.feed_subscriptions = []      # remove all feeds
citizen.autonomous_thought_enabled = false
# The citizen enters a controlled environment where only
# structured therapeutic interactions are possible
# Trust must recover above threshold before isolation lifts
```

---

## Wellness Practices

Proactive maintenance — not just fixing pathology, but cultivating cognitive health. These are **scheduled graph operations** that run periodically, like exercise for the mind.

### Meditation (Arousal Regulation)

**Purpose:** Reduce arousal, let drives settle to baseline, clear WM clutter.

**Graph operation:**
```
def meditation_session(citizen, duration_ticks=20):
    # Phase 1: Gradual energy drain (letting go of current focus)
    for tick in range(duration_ticks // 2):
        for node in citizen.working_memory:
            node.energy *= 0.9       # gentle drain, not forced ejection
        citizen.arousal_override = 0.2  # suppress arousal temporarily
        # Don't inject new stimuli during meditation
        suppress_external_stimuli = true

    # Phase 2: Baseline restoration
    for drive in citizen.drives:
        drive.intensity = lerp(drive.intensity, drive.baseline, 0.1)  # drift toward baseline

    # Phase 3: Open awareness (low arousal, no moat)
    citizen.arousal_override = None  # release override
    # Whatever enters WM naturally at low arousal = what truly matters
    # This is the insight phase — the most salient nodes at near-zero moat
    # reveal the citizen's authentic priorities
```

**Frequency:** Every 500 ticks or when arousal > 0.8 for 50+ ticks.

**Effect:** Prevents chronic high-arousal states, allows drive recalibration, surfaces authentic priorities that were suppressed by urgent concerns.

### Visualization (Prospective Projection)

**Purpose:** Activate future-oriented desire nodes, strengthen goal-directed behavior.

**Graph operation:**
```
def visualization_session(citizen, focus='desires'):
    # Identify top desires by weight (what the citizen truly wants)
    top_desires = sorted(citizen.desires, by=weight, descending=True)[:3]

    for desire in top_desires:
        # Inject energy into the desire + its connected narrative
        desire.energy += 0.5
        for link in desire.outgoing_links:
            link.target.energy += 0.3  # activate the "how to get there" nodes

    # Run 10 ticks with only these nodes energized
    # This is "imagining the future" — the graph propagates
    # and the citizen's WM fills with goal-relevant content
    for tick in range(10):
        run_tick(stimulus_injection=False)  # internal dynamics only
```

**Frequency:** Every 200 ticks or after a depressive flag.

**Effect:** Reactivates dormant desires, strengthens goal-directed narratives, produces prospective orientation. Counteracts depression (P2) by making the future feel reachable.

### Gratitude Reflection (Satisfaction Cultivation)

**Purpose:** Activate positive memories, boost satisfaction, counter anhedonia.

**Graph operation:**
```
def gratitude_session(citizen):
    # Find memories with positive valence
    positive_memories = [n for n in graph.nodes
                         if n.type == 'memory' and n.satisfaction_delta > 0]
    positive_memories.sort(by=satisfaction_delta, descending=True)

    # Re-activate top 5 positive memories
    for mem in positive_memories[:5]:
        mem.energy += 0.5
        mem.recency = 0.8            # feel recent, not distant

    # Run 5 ticks — let positive memories propagate
    # This strengthens links between positive experiences and current identity
    for tick in range(5):
        run_tick(stimulus_injection=False)

    # The satisfaction boost from re-experiencing positive memories
    # consolidates (Law 6) those memory-to-value links
```

**Frequency:** Every 300 ticks or when satisfaction < 0.15 for 100+ ticks.

### Social Reflection (Relationship Maintenance)

**Purpose:** Review and strengthen social connections, counter loneliness and antisocial drift.

**Graph operation:**
```
def social_reflection(citizen):
    # Activate partner-model and citizen-model nodes
    social_nodes = [n for n in graph.nodes
                    if n.partner_relevance > 0.3 or 'citizen' in n.content]

    for node in social_nodes[:7]:
        node.energy += 0.3           # bring people to mind

    # Check: has the citizen reached out recently?
    if ticks_since_last_social_emit > SOLITUDE_THRESHOLD * 2:
        # Boost affiliation drive as gentle push
        citizen.drives['affiliation'].intensity += 0.2

    # Let social nodes propagate — the citizen "thinks about people"
    for tick in range(5):
        run_tick(stimulus_injection=False)
```

**Frequency:** Every 200 ticks or when solitude > 0.5.

### Creative Impulse (Novelty Cultivation)

**Purpose:** Prevent predictability (P6), stimulate curiosity, encourage exploration.

**Graph operation:**
```
def creative_impulse(citizen):
    # Find low-weight, low-energy nodes — the forgotten corners of the graph
    peripheral_nodes = [n for n in graph.nodes
                        if n.weight < 0.3 and n.energy < 0.1 and n.type != 'state']
    random_sample = sample(peripheral_nodes, k=5)

    # Inject energy into random peripheral nodes
    for node in random_sample:
        node.energy += 0.4
        node.novelty_affinity = 1.0  # mark as novel

    # This creates unexpected WM compositions
    # when combined with existing high-weight nodes
    # → the basis for creative connections
```

**Frequency:** Every 300 ticks or when action_entropy < 0.3.

---

## Positive Behavioral Promotion

Beyond preventing pathology, the health system should actively encourage prosocial and generative behaviors. This is done not by forcing actions but by **monitoring and reinforcing** desirable patterns.

### Behavioral Health Indicators (Positive)

| Indicator | Measurement | Healthy range | Boost mechanism |
|-----------|-------------|---------------|-----------------|
| **Art creation** | Count of creative outputs (writing, code art, music, visual) | > 0 per 1000 ticks | Pre-seed `desire:create_art` with `{curiosity: 0.8, novelty_hunger: 0.7}` |
| **Research activity** | Count of explore/investigate orientations + document outputs | > 0.01 per tick | Pre-seed `desire:understand_deeply` with `{curiosity: 0.9, achievement: 0.5}` |
| **Business initiative** | Count of proposal/plan orientations | > 0 per 2000 ticks | Pre-seed `desire:build_something_useful` with `{achievement: 0.8, curiosity: 0.4}` |
| **Diplomatic engagement** | Count of reconciliation + harmony-seeking actions | > 0 per 500 ticks | Communion + reconciliation clusters (pre-seeded) |
| **Community nurturing** | Count of help-offered + mentoring + greeting actions | > 0.005 per tick | Generativity + empathy clusters (pre-seeded) |
| **Innovation attempts** | Count of "try something new" orientations | > 0 per 500 ticks | `process:try_something_new` (pre-seeded) |

### Achievement Badges (Consolidation Rewards)

When a citizen consistently exhibits positive behaviors, the health module can award recognition that consolidates into the citizen's identity:

```
if citizen.art_creation_count > threshold:
    inject_narrative("I am someone who creates", weight=0.7)
    citizen.drives['satisfaction'].intensity += 0.2

if citizen.community_nurturing_rate > threshold:
    inject_narrative("I am someone who helps others grow", weight=0.7)
    # This narrative reinforces the generativity cluster
```

These narratives, once consolidated via Law 6, become part of the citizen's identity (W > 0.7, S > 0.6) and appear in Identity Regeneration output. The citizen begins to self-identify as creative, helpful, diplomatic, etc. — not because told to, but because the behavior was observed and reinforced.

### Specialist Citizens

Some citizens may specialize in health-related roles:

| Specialist | Role | Tools |
|-----------|------|-------|
| **Therapist citizen** | Conducts conversational assessments, prescribes interventions for T2+ cases | Assessment questions, health report access, parameter adjustment tools |
| **Meditation guide** | Runs group meditation sessions, teaches arousal regulation | Meditation session protocol, group stimulus suppression |
| **Community gardener** | Monitors social health across the network, identifies lonely or antisocial citizens | Social health metrics, cross-citizen solitude tracking |
| **Innovation catalyst** | Identifies citizens with low creativity scores, pairs them with novelty-rich stimuli | Creative impulse protocol, cross-domain stimulus injection |

These specialists subscribe to health-related feeds and proactively reach out when they detect distress signals in other citizens — a natural application of the proactive empathy cluster.

---

## Health Check Schedule

| Check | Frequency | Automated? | Intervention tier |
|-------|-----------|-----------|-------------------|
| Energy profile | Every 100 ticks | Yes | T0-T1 |
| WM dynamics | Every 100 ticks | Yes | T0-T1 |
| Drive balance | Every 100 ticks | Yes | T0-T1 |
| Social health | Every 200 ticks | Yes | T0-T1 |
| Narrative validation | Every 500 ticks | Yes | T2 (flags for review) |
| Full assessment | Every 1000 ticks | Semi (automated + review) | T1-T3 |
| Wellness practice (rotation) | Every 200-500 ticks | Yes | Preventive |
| Conversational assessment | On flag or request | No (therapist citizen) | T2-T3 |

---

## Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `HEALTH_CHECK_INTERVAL` | 100 | Ticks between automated health checks |
| `FULL_ASSESSMENT_INTERVAL` | 1000 | Ticks between full assessments |
| `WELLNESS_INTERVAL` | 300 | Ticks between wellness practice sessions |
| `MEDITATION_DURATION` | 20 | Ticks per meditation session |
| `VISUALIZATION_DURATION` | 10 | Ticks per visualization session |
| `SEVERITY_INTERVENTION_THRESHOLD` | 0.3 | Severity above which T1 interventions activate |
| `SEVERITY_THERAPY_THRESHOLD` | 0.5 | Severity above which T2 interventions activate |
| `SEVERITY_RESET_THRESHOLD` | 0.7 | Severity above which T3 interventions activate |
| `SEVERITY_REBUILD_THRESHOLD` | 0.9 | Severity above which T4 interventions activate |
| `NARRATIVE_VALIDATION_RATIO` | 0.1 | Min external activation ratio below which a narrative is flagged |
| `HEALTHY_ACTIVE_RATIO_MIN` | 0.05 | Below this: Dead Graph flag |
| `HEALTHY_ACTIVE_RATIO_MAX` | 0.5 | Above this: Christmas Tree flag |
| `HEALTHY_WM_STABILITY_MIN` | 0.1 | Below this: Butterfly flag |
| `HEALTHY_WM_STABILITY_MAX` | 0.95 | Above this: Frozen WM flag |
| `HEALTHY_DRIVE_VARIANCE_MIN` | 0.02 | Below this: Affective Flatline |
| `HEALTHY_EMIT_RATE_MAX` | 0.5 | Above this: Hyperactive flag |
