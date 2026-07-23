# Blueprint — Temporal Desire, Subjective Time & Alarm Physics

```yaml
title: Temporal Desire, Subjective Time & Alarm Physics
version: 0.2
status: implemented
implementationStatus: core_runtime
scope: L1 cognition + temporal membrane
canonicalLayer: L2 Mind Protocol
risk: medium
reversible: true
```

## Intention

Donner au Citizen un sens du temps vécu et de la densité de ses réveils futurs.
Un désir non réalisé accumule un âge subjectif. Les affects et les sous-entités
ne déclenchent pas directement un réveil : leurs politiques explicites modifient
la vitesse de cette horloge et son seuil de tolérance.

```text
Narrative:Wish
    ↓ SEEKS_REALIZATION — le lien attend
Narrative:Objective | Narrative:Task
    ↑ PROGRESSES | FULFILLS | CANCELS | REVISES
Moment
    ↓
pression temporelle dérivée
    ↓
Moment:Alarm dormant
    ↓ scheduledFor
Stimulus interoceptif
    ↓ Law 1
activation cognitive
```

La loi canonique est :

> À chaque tick temporel, le temps objectif écoulé est intégré avec la vitesse
> subjective maintenue depuis le tick précédent. Les Moments modifient ensuite
> l’écart de réalisation. L’état affectif observé et les sous-entités
> représentées configurent la vitesse et le seuil du prochain intervalle. La
> physique matérialise le prochain franchissement comme un Moment d’alarme.
> L’alarme émet une perception, jamais une action imposée.

## Invariants

1. Le `Narrative:Wish` désire ; la relation `SEEKS_REALIZATION` attend.
2. La pression est dérivée. Aucun nœud de pression ni calendrier parallèle.
3. Le temps écoulé utilise `heldClockRate` du précédent intervalle : aucune
   causalité affective rétroactive.
4. `unknown` et `not_measured` utilisent un facteur numérique neutre sans être
   réétiquetés `neutral`.
5. Une seule alarme dormante existe par relation temporelle et génération.
6. Une alarme obsolète est consommée silencieusement.
7. L’alarme produit un stimulus interoceptif ; elle ne choisit ni action, ni
   sous-entité, ni contact humain.
8. Après déclenchement, hystérèse et période réfractaire empêchent les boucles.
9. Les requêtes FalkorDB restent hors du hot path cognitif.
10. La densité des réveils mesure des activations programmées, pas la durée ou
    la difficulté réelle des tâches.

## Ontologie

```text
(Wish: Narrative {semanticType: "Wish"})
  -[:SEEKS_REALIZATION {
      commitment: 0.0..1.0,
      category: string,
      baseClockRate: 1.0,
      patienceTauSeconds: 43200,
      baseThreshold: 0.65,
      releaseThreshold: 0.40,
      subjectiveAgeSeconds: 0,
      lastIntegratedAt: datetime,
      heldClockRate: 1.0,
      effectiveThreshold: 0.65,
      generation: integer,
      alarmMomentId: string | null,
      alarmArmed: boolean,
      refractoryUntil: datetime | null,
      measurementStatus:
        observed | known_absent | unknown | not_measured | measurement_failed
    }]->
(Objective | Task: Narrative {progress: 0.0..1.0})
```

Les preuves historiques sont exclusivement des `Moment` reliés par :

- `PROGRESSES {delta, relief, confidence}`;
- `FULFILLS`;
- `FAILED_ATTEMPT_FOR`;
- `CANCELS`;
- `REVISES`.

Les politiques temporelles sont explicites :

```text
(Affect | Subentity)-[:TEMPORALLY_BIASES {
  clockBias: number,
  thresholdBias: number,
  compatibility: 0.0..1.0
}]->(Wish | NarrativeCategory)
```

L’absence d’une politique ne produit aucun biais.

## Physique

```text
subjectiveDelta = objectiveDelta × heldClockRate

affectClockFactor =
  exp(Σ affectIntensity × compatibility × clockBias)

subentityClockFactor =
  exp(Σ normalizedWorkspaceShare × compatibility × clockBias)

newClockRate =
  clamp(0.25, 4.0,
        baseClockRate × affectClockFactor × subentityClockFactor)

effectiveThreshold =
  clamp(0.10, 0.95,
        baseThreshold
        + affectThresholdShift
        + subentityThresholdShift
        + explicitFlexibilityAdjustment)

realizationGap = 1 - progress
amplitude = normalize(wish.weight) × commitment × realizationGap

pressure =
  amplitude × (1 - exp(-subjectiveAgeSeconds / patienceTauSeconds))
```

Si `amplitude <= effectiveThreshold`, aucun franchissement n’est possible avec
l’état courant. Sinon :

```text
requiredSubjectiveAge =
  -patienceTau × ln(1 - effectiveThreshold / amplitude)

remainingObjectiveTime =
  (requiredSubjectiveAge - subjectiveAge) / newClockRate
```

## Ordre du tick temporel

1. Fermer l’intervalle précédent avec `heldClockRate`.
2. Appliquer chronologiquement les nouveaux Moments.
3. Invalider les anciennes générations.
4. Lire le snapshot interoceptif publié par le moteur.
5. Résoudre uniquement les `TEMPORALLY_BIASES` explicites.
6. Calculer `newClockRate`, seuil, pression et prochain franchissement.
7. Conserver, annuler ou remplacer l’unique `Moment:Alarm`.
8. Persister la relation et le frame `temporal-desire-current`.
9. Valider les alarmes dues avant leur émission.
10. Après émission, désarmer le lien et poser `refractoryUntil`.

## Alarmes

```yaml
id: moment:alarm:temporal-desire:{relationHash}:{generation}
nodeType: Moment
semanticType: Alarm
status: dormant
repeat: once
reason: temporal_desire_threshold
temporalRelationKey: "{wishId}|{realizationId}"
sourceNarrativeId: narrative:wish:...
realizationNarrativeId: narrative:objective:...
relationGeneration: 12
scheduledFor: datetime
pressureThreshold: 0.61
heldClockRate: 1.83
subjectiveAgeAtFire: 49800
```

Une alarme valide devient une perception :

```yaml
channel: interoception.temporal_desire
sensation:
  kind: desire_temporally_salient
  text: >
    Un désir important reste insuffisamment réalisé et son attente est
    devenue temporellement saillante.
```

## Proprioception de charge future

Le même frame expose une perception agrégée des alarmes dormantes :

```yaml
wakeLoad:
  measurementStatus: observed
  scheduledAlarmCount: 4
  nextHour: 1
  next24Hours: 3
  next7Days: 5
  level: quiet | loaded | crowded | saturated
  meaning: scheduled_activation_density_not_task_workload
```

Les récurrences sont développées sur un horizon borné de sept jours. Cette
mesure n’entre pas dans l’équation de pression d’un désir et ne bloque aucune
alarme : elle donne seulement au Citizen la sensation que son futur se remplit.

## Gestion épistémique

- Une relation sans baseline fiable reste `unknown` et ne programme rien.
- Un snapshot affectif absent reste `not_measured`, facteur `1.0`.
- Une sous-entité indéterminée reste `unknown`, facteur `1.0`.
- Une erreur de mesure devient `measurement_failed`.
- Le narrateur de `sense` n’ajoute aucune cause absente du frame structuré.

## Implémentation

- Physique pure : `runtime/cognition/temporal_desire.py`
- Projection FalkorDB : `runtime/orchestrator/graph_temporal_desires.py`
- Membrane : `runtime/orchestrator/alarm_watcher.py`
- Store des Moments : `runtime/orchestrator/graph_alarms.py`
- Frame conscient : `RuntimeState {id: "temporal-desire-current"}`, destiné au
  compositeur canonique du Global Workspace que `sense` retourne sans le réécrire

Hors périmètre : apprentissage automatique des profils, inférence
psychologique, modification autonome de seuils constitutionnels, calendrier
externe et action automatique après alarme.
