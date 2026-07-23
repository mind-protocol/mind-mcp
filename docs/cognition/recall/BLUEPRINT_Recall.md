# Blueprint — Recall L1

```yaml
title: Recall L1
version: 0.1
status: implemented
implementationStatus: core_runtime
scope: L1 cognition
canonicalLayer: L2 Mind Protocol
risk: medium
reversible: true
```

## Intention

Permettre au Citizen AI de poser une question à son propre L1 et de laisser sa
physique cognitive retrouver ce qui résonne, sans réduire la mémoire à une
recherche vectorielle ni transformer un résultat de rappel en vérité.

`recall` crée un événement cognitif réel. La question devient un `Moment`,
ce Moment devient le centre énergétique d'un stimulus contenant la fermeture
complète du `Space` interrogé, puis une `SubEntity` explore le graphe depuis ce
contexte.

```text
question
  ↓
Moment:Recall — centre sémantique et énergétique
  ↓
stimulus = graphe induit complet du Space
  ↓
sélection de la SubEntity active la plus compatible
  ↓
SubEntity enfant dédiée au recall
  ↓
ticks d'exploration et propagation d'énergie
  ↓
nœuds résonants + provenance + incertitude
```

## Décisions structurantes

1. **Le stimulus est un sous-graphe, pas une chaîne de texte.** Il contient le
   Moment-question, toutes les nodes de la fermeture du Space et tous les liens
   dont les deux extrémités appartiennent à cette fermeture.
2. **La question reste centrale.** Elle porte l'intention principale,
   l'embedding directeur et la totalité de l'énergie nouvellement injectée.
3. **Être présent dans le stimulus ne signifie pas recevoir de l'énergie
   nouvelle.** Les nodes contextuelles conservent leur énergie antérieure ;
   la physique décide ensuite lesquelles reçoivent le flux propagé.
4. **Le recall rejoint l'activité cognitive en cours sans la détourner.** Il
   sélectionne la SubEntity active la plus pertinente, puis crée une enfant
   dédiée plutôt que de remplacer la requête ou l'intention de sa parente.
5. **La mémoire répond par résonance, pas par autorité.** Les résultats sont des
   candidats sourcés avec leurs scores et leur statut épistémique.
6. **Le Space complet est une exigence logique, pas une exigence de copie.**
   L'implémentation peut matérialiser paresseusement ses nodes et liens, mais ne
   peut ni sampler, ni tronquer, ni substituer silencieusement un top-k au
   contexte complet.
7. **Les projections L1 antérieures aux nodes Space restent rappelables.** Le
   graphe L1 privé entier est alors représenté par un `L1GraphSpace` virtuel.
   Cette compatibilité est explicite dans le résultat et ne prétend pas qu'un
   ancien nœud Space existait déjà.
8. **L'absence de modèle sémantique dégrade, mais ne simule pas son absence.**
   Le runtime utilise une projection lexicale hashée déterministe et retourne
   `embeddingMethod: lexical_hash_fallback`.

## Invariants

1. Chaque invocation valide crée exactement un nouveau `Moment:Recall`.
2. Le Moment-question appartient au Space interrogé et devient
   `origin_moment` de l'exploration créée pour ce recall.
3. Le stimulus référence chaque node comprise dans la fermeture du Space au
   même snapshot logique.
4. Aucun voisin extérieur au Space n'entre implicitement dans le stimulus.
5. Le Moment-question est l'unique source d'énergie exogène du recall.
6. Le budget énergétique total ne dépend jamais du nombre de nodes du Space.
7. La question pèse davantage que le centroïde du Space dans le centroïde du
   stimulus.
8. La proximité sémantique pèse davantage que l'activation dans le routage vers
   une SubEntity, mais les deux facteurs sont nécessaires.
9. Une SubEntity active existante ne voit jamais sa requête, son intention ou
   son `origin_moment` réécrit par `recall`.
10. L'absence de SubEntity compatible crée une racine dédiée ; elle ne force
    pas un rattachement hors sujet.
11. Les ticks s'arrêtent par convergence, satisfaction, fatigue, absence de
    chemin ou plafond de sécurité — jamais parce qu'un nombre fixe de réponses
    a été fabriqué.
12. `no_match`, `unknown`, `missing_embedding` et `execution_failed` restent
    distincts.
13. Un résultat rappelé ne devient ni `confirmed`, ni décision, ni fait du seul
    fait de son activation.
14. `recall` ne quitte pas le L1 souverain du Citizen et ne sonde aucun autre
    citoyen.

## Ontologie

### Moment central

```yaml
id: moment:recall:{citizenId}:{timestamp}:{nonce}
nodeType: Moment
semanticType: Recall
subtype: recall_query
status: created | running | completed | no_match | failed
question: string
intention: string
embedding: vector
spaceId: string
stimulusSnapshotId: string
energyBudget: number
selectedSubentityId: string | null
selectionSemanticScore: number | null
selectionActivationScore: number | null
selectionCombinedScore: number | null
resultNodeIds: [string]
resultScores: object
epistemicStatus: inquiry
createdAt: datetime
completedAt: datetime | null
```

Le Moment est une question, pas une assertion. `epistemicStatus: inquiry`
empêche sa formulation interrogative d'être interprétée comme une croyance.

### Fermeture du Space

Pour un Space `S`, la fermeture utilisée par le stimulus est :

```text
Nodes(S) =
  toutes les nodes directement contenues dans S
  ∪ toutes les nodes contenues transitivement dans ses sous-Spaces
  ∪ le Moment:Recall

Links(S) =
  tous les liens dont source ∈ Nodes(S) et target ∈ Nodes(S)
```

Les liens vers l'extérieur définissent la frontière du Space mais ne sont pas
suivis pendant ce recall, sauf future décision explicite de franchissement de
membrane.

Pour une projection L1 historique sans nodes `Space` :

```text
Space virtuel = space:l1-graph:{graphName}
Nodes(Space virtuel) = toutes les nodes du graphe L1 privé
Links(Space virtuel) = tous ses liens internes
```

Le premier recall matérialise uniquement l'ancre `L1GraphSpace` et la relation
`Moment:Recall -[:OCCURS_IN]-> L1GraphSpace`. Il ne crée pas une arête
`CONTAINS` par node : l'appartenance reste définie par la frontière du graphe
privé pendant cette migration.

### Attachement à une SubEntity

```text
SubEntity parent sélectionnée
  └── SubEntity enfant de recall
        parent_id = selectedSubentity.id
        origin_moment = recallMoment.id
        query = recallMoment.question
        query_embedding = recallMoment.embedding
        intention = recallMoment.intention
        intention_embedding = embed(intention)
        start_position = recallMoment.id
```

Si aucune parent compatible n'existe, la même SubEntity est créée comme racine
avec `parent_id = null`.

## Physique

### Centroïde du stimulus

Le centroïde sert au routage de l'exploration, mais la question doit rester
dominante :

```text
spaceCentroid =
  normalized weighted mean of embeddings in Nodes(S) excluding RecallMoment

stimulusCentroid =
  normalize(
    questionCentrality × questionEmbedding
    + (1 - questionCentrality) × spaceCentroid
  )

CONSTRAINT:
  0.5 < questionCentrality <= 1.0
```

Si le Space ne contient aucun autre embedding exploitable,
`stimulusCentroid = questionEmbedding`. Les valeurs numériques finales sont des
paramètres de physique à calibrer par benchmark ; elles ne sont pas ratifiées
par ce blueprint L2.

### Sélection de la SubEntity

Pour chaque SubEntity active :

```text
semantic =
  max(0, cosine(stimulusCentroid, subentity.crystallization_embedding))

activation =
  normalizeActivation(subentity.currentActivation)

selectionScore =
  semantic ^ semanticExponent
  × activation ^ activationExponent

CONSTRAINTS:
  semanticExponent > activationExponent > 0
  semantic >= minimumSemanticCompatibility
```

La combinaison est multiplicative : une forte activation ne compense pas une
absence de rapport sémantique, et une correspondance purement théorique ne
capture pas automatiquement le recall si elle n'est pas cognitivement active.

Le gagnant est le score admissible maximal. En cas d'égalité dans la tolérance
numérique, la récence d'activation départage ; l'identifiant stable ne sert que
de dernier départage déterministe.

### Injection et propagation d'énergie

```text
recallEnergy =
  clamp(minRecallEnergy, maxRecallEnergy,
        baseRecallEnergy × questionCriticality)

RecallMoment.energy += recallEnergy
```

Cette quantité est l'intégralité de l'énergie exogène ajoutée par l'appel.
Aucune boucle du type `for node in Space: node.energy += recallEnergy` n'est
permise.

Les autres nodes du stimulus :

- conservent leur énergie préexistante ;
- sont immédiatement disponibles à la propagation ;
- reçoivent éventuellement de l'énergie par les lois normales de compatibilité,
  polarité, capacité des liens, friction et conservation ;
- gardent les traces thermiques ou consolidations produites par la physique
  normale.

Cette décision rend le coût énergétique indépendant de la taille du Space et
maintient une causalité lisible : l'énergie vient de la question, le contexte
détermine où elle circule.

### Arrêt

Le recall avance par ticks ou étapes de SubEntity jusqu'au premier état terminal
applicable :

1. satisfaction suffisante ;
2. aucun lien admissible ;
3. stagnation détectée par la fatigue ;
4. convergence des résultats pendant la fenêtre configurée ;
5. plafond de sécurité atteint ;
6. erreur d'exécution explicite.

Le plafond protège le runtime ; il ne transforme pas un résultat incomplet en
succès.

## Target behaviors

### B1 — Une question crée un Moment cognitif

**Pourquoi :** une question adressée à la mémoire est un événement vécu par le
Citizen. Sans Moment, son origine, son contexte et ses effets énergétiques
disparaissent après la réponse.

```text
GIVEN:  une question non vide et un Space L1 accessible
WHEN:   recall est invoqué
THEN:   un nouveau Moment:Recall est créé dans ce Space
AND:    il conserve question, intention, embedding, date et provenance
AND:    son statut épistémique est inquiry
```

### B2 — Le stimulus contient tout le Space

**Pourquoi :** la pertinence d'un souvenir dépend aussi de connexions faibles ou
inattendues. Un top-k préalable déciderait de la réponse avant que la physique
ait pu travailler.

```text
GIVEN:  le Space résolu contient N nodes dans sa fermeture transitive
WHEN:   le stimulus est assemblé
THEN:   les N nodes sont membres logiques du stimulus
AND:    tous leurs liens internes appartiennent au graphe induit
NEVER:  un sampling, une limite top-k ou une troncature silencieuse
```

### B3 — Le snapshot du Space est cohérent

**Pourquoi :** assembler chaque partie à une révision différente produirait un
contexte qui n'a jamais réellement existé.

```text
GIVEN:  le Space peut évoluer pendant l'appel
WHEN:   le stimulus est assemblé
THEN:   nodes, liens et énergies observées portent le même snapshot logique
AND:    les mutations ultérieures suivent les règles normales de concurrence
```

### B4 — La question demeure le centre sémantique

**Pourquoi :** le Space donne la situation, mais c'est la question qui définit
ce que le Citizen cherche maintenant.

```text
GIVEN:  questionEmbedding et spaceCentroid sont disponibles
WHEN:   stimulusCentroid est calculé
THEN:   questionCentrality est strictement supérieure à 0.5
AND:    la contribution de la question dépasse celle du contexte agrégé
```

### B5 — La question demeure le centre topologique

**Pourquoi :** la propagation doit avoir une cause identifiable, plutôt qu'un
nuage de nodes contextuelles sans point d'entrée.

```text
GIVEN:  le stimulus complet est construit
WHEN:   l'exploration commence
THEN:   le Moment:Recall est start_position et origin_moment
AND:    chaque chemin de recall peut être retracé jusqu'à lui
```

### B6 — Le recall injecte une énergie bornée et conservée

**Pourquoi :** injecter la même quantité dans chaque node ferait croître
l'énergie avec la taille du Space et favoriserait artificiellement les grands
Spaces.

```text
GIVEN:  un budget énergétique de recall E
WHEN:   le stimulus est activé
THEN:   E est injecté dans le Moment-question
AND:    les nodes contextuelles ne reçoivent aucune énergie exogène directe
AND:    toute énergie ultérieure reçue par elles vient de la propagation
```

### B7 — Le routage combine sens et activation

**Pourquoi :** l'activation seule choisit ce qui occupe déjà l'attention ; la
sémantique seule ignore l'état cognitif présent. Leur produit trouve la facette
à la fois concernée et disponible.

```text
GIVEN:  une ou plusieurs SubEntities actives
WHEN:   recall choisit une parent
THEN:   chacune est scorée par compatibilité sémantique et activation
AND:    la sémantique a le poids dominant
AND:    le score et ses deux composantes sont observables
```

### B8 — Le recall ne détourne pas une SubEntity active

**Pourquoi :** remplacer la requête d'une SubEntity détruirait la continuité de
la pensée déjà en cours.

```text
GIVEN:  une SubEntity active compatible est sélectionnée
WHEN:   l'exploration de recall est créée
THEN:   une SubEntity enfant dédiée est attachée à la parent
AND:    la parent conserve query, intention, origin_moment et position
```

### B9 — L'absence de parent compatible crée une racine

**Pourquoi :** une question nouvelle doit pouvoir ouvrir un nouveau courant
cognitif au lieu d'être forcée dans la facette active la moins mauvaise.

```text
GIVEN:  aucune SubEntity active ne franchit la compatibilité minimale
WHEN:   recall démarre
THEN:   une SubEntity racine est créée depuis le Moment:Recall
AND:    selectedSubentityId reste null pour la parent
```

### B10 — Le recall fait tourner la physique jusqu'à un arrêt honnête

**Pourquoi :** un nombre fixe de ticks peut être excessif pour une réponse
évidente et insuffisant pour une association profonde.

```text
GIVEN:  l'exploration de recall est active
WHEN:   les ticks s'exécutent
THEN:   elle continue tant qu'il existe du progrès admissible
AND:    elle s'arrête par satisfaction, épuisement, fatigue, convergence ou plafond
AND:    la cause d'arrêt est retournée
```

### B11 — Les résultats gardent leur provenance

**Pourquoi :** le Citizen doit pouvoir distinguer ce qui a réellement résonné
de la narration éventuellement produite ensuite.

```text
GIVEN:  des nodes résonnent pendant l'exploration
WHEN:   recall retourne ses résultats
THEN:   chaque résultat expose nodeId, Space, chemin, score sémantique,
        énergie avant/après et statut épistémique disponible
AND:    le Moment:Recall conserve les IDs et scores, pas une copie désourcée
```

### B12 — Une résonance n'est pas une vérité

**Pourquoi :** énergie, similarité et consolidation mesurent l'accessibilité
cognitive, pas l'exactitude du contenu.

```text
GIVEN:  un souvenir fortement activé
WHEN:   il est retourné par recall
THEN:   son statut épistémique original est conservé
NEVER:  inferred, reported, conflicting ou stale devient confirmed implicitement
```

### B13 — L'absence de résultat reste explicite

**Pourquoi :** « rien n'a résonné », « donnée absente » et « moteur en panne »
ne signifient pas la même chose.

```text
GIVEN:  le recall ne retourne aucune node
WHEN:   l'appel se termine
THEN:   status=no_match si l'exploration a fonctionné sans résonance
OR:     status=failed avec cause si l'exécution a échoué
AND:    missing_embedding est signalé séparément lorsqu'il a réduit la perception
```

### B14 — Les effets cognitifs normaux persistent

**Pourquoi :** poser une question modifie réellement l'attention et peut
renforcer des chemins, mais seul le moteur cognitif doit décider de ces effets.

```text
GIVEN:  l'énergie du Moment se propage dans le Space
WHEN:   des nodes et liens sont traversés
THEN:   énergie, traces thermiques, poids et consolidations évoluent selon les lois normales
NEVER:  recall écrit directement une consolidation ou une croyance de résultat
```

### B15 — Le contexte complet peut être matérialisé paresseusement

**Pourquoi :** un grand Space ne doit pas forcer une copie mémoire massive, mais
l'optimisation ne doit pas changer la sémantique.

```text
GIVEN:  un Space trop grand pour une matérialisation eager efficace
WHEN:   le runtime utilise index, curseurs, partitions ou chargement paresseux
THEN:   toute node du Space reste éligible à la propagation et à la visite
AND:    l'ordre de chargement ne devient pas un filtre de pertinence
```

### B16 — Le recall respecte la souveraineté L1

**Pourquoi :** questionner sa propre mémoire et sonder le cerveau d'un autre
Citizen sont deux permissions différentes.

```text
GIVEN:  recall est invoqué par un Citizen
WHEN:   le Space est résolu
THEN:   il appartient à son L1 et lui est accessible
NEVER:  recall traverse L3 ou le L1 d'un autre Citizen
```

### B17 — Recall-question et rappel d'un Moment restent distincts

**Pourquoi :** le runtime possède déjà un mécanisme de réactivation d'un Moment
connu. Le nouveau recall part d'une question ouverte et explore un Space.

```text
GIVEN:  une question ouverte sur le contenu du L1
WHEN:   recall(question=...) est utilisé
THEN:   la physique cherche les nodes qui résonnent dans le Space

GIVEN:  l'identifiant d'un Moment historique précis
WHEN:   recall_moment(momentId=...) est utilisé
THEN:   un nouveau Moment référence explicitement ce Moment historique
```

## Contrat MCP proposé

```yaml
name: recall
description: >
  Pose une question au L1 du Citizen courant. Crée un Moment-question,
  construit un stimulus couvrant le Space complet, injecte de l'énergie,
  route vers une SubEntity et retourne les nodes qui résonnent.
inputSchema:
  type: object
  required: [question]
  properties:
    question:
      type: string
    intention:
      type: string
    spaceId:
      type: string
      description: Space L1 interrogé; le Space cognitif actif est utilisé par défaut.
    energy:
      type: number
      description: Intensité demandée, bornée par la politique L1.
    maxTicks:
      type: integer
      description: Plafond de sécurité, pas objectif de durée.
    topK:
      type: integer
      description: Limite de restitution uniquement; ne limite jamais le stimulus.
```

`topK` peut compresser la réponse rendue au caller, mais toutes les nodes restent
dans le stimulus et toutes les résonances doivent rester comptabilisées dans le
Moment.

## Résultat proposé

```yaml
momentId: string
spaceId: string
stimulusNodeCount: integer
stimulusLinkCount: integer
injectedEnergy: number
parentSubentityId: string | null
recallSubentityId: string
selection:
  semantic: number | null
  activation: number | null
  combined: number | null
ticksRun: integer
stopReason: satisfied | exhausted | fatigued | converged | safety_limit | failed
status: completed | no_match | failed
results:
  - nodeId: string
    score: number
    path: [string]
    energyBefore: number
    energyAfter: number
    epistemicStatus: string
missingEmbeddingCount: integer
embeddingMethod: configured | sentence_transformer | lexical_hash_fallback
```

## Justification du design

### Pourquoi inclure toutes les nodes du Space ?

Parce que sélectionner les nodes avant la propagation confondrait récupération
et réponse. Les associations faibles, les contradictions et les souvenirs peu
actifs font partie de ce que le recall doit pouvoir découvrir. Le Space fournit
la frontière de souveraineté et de contexte ; la physique fournit la sélection.

### Pourquoi injecter uniquement dans la question ?

Parce que l'énergie représente une cause. Si chaque node contextuelle recevait
une injection, un Space deux fois plus grand recevrait deux fois plus d'énergie
pour la même question. En concentrant l'injection sur le Moment-question, le
budget reste stable et le chemin de causalité reste explicable.

### Pourquoi mélanger question et centroïde du Space ?

La question seule perd les implicites de la situation ; le Space seul dilue
l'intention présente. Un centroïde dominé par la question conserve le but tout
en donnant au routage la couleur du contexte cognitif courant.

### Pourquoi choisir une SubEntity par sens et activation ?

La proximité sémantique désigne la facette compétente ; l'activation indique la
facette actuellement disponible dans la dynamique cognitive. Le produit impose
que les deux soient présentes et évite qu'une facette très active mais hors
sujet capture toutes les questions.

### Pourquoi créer une enfant ?

Une SubEntity active possède déjà une continuité : origine, intention, chemin
et cristallisation en cours. La réécrire détruirait cette continuité. Une enfant
permet au recall de bénéficier de son contexte tout en gardant une trajectoire
et une provenance propres.

### Pourquoi un Moment persistant ?

Le recall est lui-même une expérience : le Citizen a posé cette question à cet
instant, dans ce contexte, avec cette intensité, et certains souvenirs ont
réagi. Le Moment permet de se rappeler ultérieurement non seulement la réponse,
mais aussi le fait d'avoir cherché et les chemins que cette recherche a activés.

## Non-objectifs

- Produire automatiquement une réponse en langage naturel faisant autorité.
- Interroger le L3 ou le L1 d'un autre Citizen ; cela relève de `subcall`.
- Réactiver un Moment historique connu ; cela relève de `recall_moment`.
- Échantillonner le Space avant la physique.
- Déclarer vraies les nodes les plus énergétiques.
- Ratifier ici les constantes numériques finales de routage ou d'énergie.

## État d'implémentation

Le cœur est implémenté et exposé par le serveur MCP.

Primitives réutilisables déjà présentes :

- `runtime/physics/subentity.py` : `origin_moment`, `parent_id`,
  `query_embedding`, `intention_embedding`, `crystallization_embedding`,
  énergie et arbre de SubEntities ;
- `runtime/physics/exploration.py` : exploration, propagation, fatigue et arrêts ;
- `mcp/tools/subcall_handler.py` : précédent de stimulus multi-segments ;
- `runtime/infrastructure/canon/canon_holder.py` : rappel d'un Moment précis,
  à conserver comme opération distincte.

Implémentation Recall :

- `runtime/cognition/recall.py` : fermeture déjà résolue, centroïdes, routage
  SubEntity, stimulus central, propagation, décroissance, compétition et arrêt ;
- `mcp/tools/recall_handler.py` : résolution du L1 et du Space, snapshot complet,
  compatibilité `L1GraphSpace`, embeddings dégradables, création/persistance du
  Moment, mise à jour énergétique et réponse MCP ;
- `mcp/server.py` : enregistrement de l'outil `recall` ;
- `tests/test_recall.py` : couverture du stimulus complet, de l'énergie centrale,
  du routage, de la fermeture transitive, de la persistance et du contrat MCP.
