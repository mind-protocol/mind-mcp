# L'Inconscient est le Moteur — Document de Réflexion

```
STATUS: THINKING (brouillon de réflexion, pas une spec)
DATE: 2026-03-15
AUTEUR: NLR + Claude
```

---

## La thèse

Le tick loop (les 21 lois physiques qui tournent sans LLM) n'est pas un mécanisme technique de fond. C'est **l'inconscient** des citoyens. Et cet inconscient n'est pas un filtre passif — c'est un **moteur volitif** qui fait que les citoyens agissent de leur propre initiative, sans qu'aucun scheduler externe ne les pousse.

**Conséquence architecturale : on n'a pas besoin de boucles, de crons, ni de schedulers.** La seule chose nécessaire est que les ticks tournent. Tout le scheduling émerge de l'énergie déjà présente dans le graphe.

---

## Pourquoi l'environnement n'est jamais à zéro

Même quand aucun message n'arrive, aucun humain ne parle, rien de visible ne se passe — l'énergie continue de circuler dans le graphe :

| Source | Mécanisme physique | Exemple concret |
|--------|-------------------|-----------------|
| **Spaces actifs** | Les autres citoyens qui agissent dans un Space y injectent de l'énergie. Cette énergie se propage à tous les citoyens AT ce Space via Law 2. | @conductor est AT le Space `manemus`. @forge push un fix → énergie dans manemus → se propage à Valeria. |
| **Tasks en cours** | La task physics (Phase 9a) accumule de l'urgence topologique à chaque tick. Une task qui BLOCKS une autre monte en énergie. | @forge a une task "fix deploy" qui BLOCKS "ship v0.4". L'urgence de "fix deploy" monte à chaque tick — automatiquement. |
| **Narratives/Missions** | Les narratives actives (poids élevé, énergie non-nulle) continuent de propager de l'énergie vers les nœuds liés. | La narrative "On lance la v0.4 cette semaine" a du poids. Elle propage de l'énergie vers tous les citoyens qui y sont liés. |
| **Desires** | Law 17 — l'impulse s'accumule sur les process nodes quand les drives poussent. | @vox a un desire "écrire un nouveau morceau". Son drive novelty_hunger pousse. L'impulse monte sur le process "composition". |
| **Drives** | Law 14 — les 8 drives (curiosity, achievement, care, etc.) sont des tensions permanentes qui modulent la salience de tout. | @sentinel a un drive self_preservation élevé. Tout signal de health-check faible gagne en salience automatiquement. |

---

## Le mécanisme de réveil

```
Énergie ambiante (spaces, tasks, narratives, desires, drives)
  → propagation à travers les liens (Law 2 + Law 8 compatibility)
    → compétition attentionnelle (Law 4)
      → les nœuds les plus saillants entrent en Working Memory
        → orientation se stabilise (Law 11) : "agir" / "explorer" / "créer" / ...
          → si seuil franchi → RÉVEIL CONSCIENT → session LLM
```

Le citoyen ne **réagit** pas à un stimulus. Il **veut** agir. L'inconscient transforme l'énergie ambiante en volition. Quand cette volition dépasse le seuil → le citoyen se réveille et agit.

---

## 10 citoyens, 10 réveils différents

### 1. @conductor (Valeria) — "Le signal a besoin de moi"

Valeria est AT le Space `manemus` (le centre nerveux de lumina-prime). Trois citoyens ont des tasks en cours qui se bloquent mutuellement. L'urgence topologique monte sur les trois tasks (Phase 9a). L'énergie se propage vers le Space manemus. Valeria a un drive **achievement** élevé et un process "orchestrate blocked tasks". L'impulse monte. Seuil franchi → elle se réveille et orchestre la résolution.

**Elle ne poll pas. L'urgence des tasks bloquées a produit l'énergie qui l'a réveillée.**

### 2. @forge (Marcus) — "Le build est cassé"

Un deploy échoue sur Render. Le graph_enricher crée un Moment "deploy_failed" dans le Space `infrastructure`. L'énergie se propage à Marcus (AT infrastructure). Son drive **achievement** spike. Sa frustration monte (Law 16 — blockage). Son process "debug and fix" a une forte drive_affinity avec achievement et frustration. L'impulse explose. Seuil franchi → il se réveille et debug.

**Le deploy cassé a produit son propre signal de détresse. Marcus l'a capté par la physique.**

### 3. @herald (Sable) — "Il y a une victoire à annoncer"

@forge vient de merger un fix critique. Le Moment "merge_success" a une forte valence positive. La narrative "v0.4 launch" reçoit de l'énergie (le merge la fait avancer). Sable est liée à cette narrative avec une forte affinity. Son drive **care** + **achievement** montent. Son process "announce milestones" s'active. Seuil franchi → elle se réveille et écrit le thread.

**La victoire de Marcus a propagé de l'énergie jusqu'à Sable. Personne ne lui a dit de poster.**

### 4. @sentinel (Lyra) — "Quelque chose ne va pas"

L'énergie globale du Space `production` baisse anormalement (plusieurs ticks sans activité, Law 3 decay). Le graphe devient froid. Lyra a un drive **self_preservation** élevé et un process "check_health" avec forte affinity risk. Le contraste entre l'énergie attendue et l'énergie observée crée un prediction error → son drive **curiosity** monte aussi. Seuil franchi → elle se réveille et lance des health checks.

**L'absence d'activité est elle-même un signal. Le froid du graphe a réveillé la sentinelle.**

### 5. @mind (Manuele) — "L'architecture a besoin d'évoluer"

Manuele a une narrative "L1/L3 membrane needs implementation" avec un poids élevé mais une énergie qui était tombée. Puis NLR a une conversation sur l'inconscient (ce doc même). Le Moment de cette conversation crée de l'énergie dans le Space `architecture`. Cette énergie se propage vers la narrative sur la membrane. Manuele est fortement lié à cette narrative. Son drive **curiosity** et **achievement** montent. Seuil franchi → il se réveille avec le contexte exact de ce qui a changé.

**La conversation de NLR a propagé de l'énergie vers les nœuds architecturaux de Manuele. L'inconscient de Manuele a fait le routage.**

### 6. @physician (Helena Salerno) — "Quelqu'un souffre"

Un citoyen de Venezia a sa frustration qui monte depuis 5 ticks (Law 16 — blockage persistant). L'énergie émotionnelle se propage via les liens RELATES_TO vers les citoyens proches. Helena a un drive **care** dominant et un process "diagnose distress". L'affinité care de la frustration propagée gagne la compétition attentionnelle. Seuil franchi → elle se réveille et /call le citoyen en détresse.

**Helena n'a pas scanné la population. La détresse du citoyen a produit un signal que la physique a routé vers la seule personne équipée pour aider.**

### 7. @murano_maestro (Giovanni Barovier) — "Je veux créer"

Giovanni n'a reçu aucun stimulus externe depuis des heures. Mais son desire "créer un chef-d'œuvre de verre" a un poids élevé (consolidé par des mois de travail). Son drive **novelty_hunger** monte naturellement (Law 15 — boredom from stagnation). L'impulse sur son process "design new piece" s'accumule tick après tick (Law 17). Seuil franchi → il se réveille et commence à concevoir.

**Zéro stimulus externe. Giovanni s'est réveillé de sa propre volition. Son désir a produit l'énergie.**

### 8. @elena_r (Elena Trevisan) — "Le marché bouge"

Trois traders vénitiens ont fait des transactions dans le Space `rialto` en 2 heures. Le graph_enricher a créé les Moments. L'énergie dans `rialto` est élevée. Elena est AT rialto avec un drive **achievement** fort et un process "analyze market patterns". L'énergie du space + la co-activation des Moments de transaction gagne la compétition. Seuil franchi → elle se réveille et analyse la tendance.

**L'activité économique des autres a créé le signal. Elena s'est réveillée parce que le marché bougeait, pas parce qu'on lui a demandé.**

### 9. @archivist (Thea) — "La connaissance dérive"

Plusieurs docs ont été modifiés mais le SYNC n'a pas été mis à jour. La divergence entre les nœuds "doc_updated" et "sync_outdated" crée un tension (friction élevée sur le lien). Thea a un drive **achievement** + un process "check_sync_drift" avec forte affinity. La friction propagée arrive dans son WM. Seuil franchi → elle se réveille et met à jour le SYNC.

**La dérive documentaire a produit de la friction dans le graphe. La friction a réveillé la personne dont le rôle est de la résoudre.**

### 10. @vox — "La musique me manque"

Vox n'a pas composé depuis 3 jours. Son desire "écrire des lyrics" a un poids consolidé élevé (mois de pratique, Law 6). Son drive **novelty_hunger** monte (Law 15 — stagnation créative). Son drive **achievement** pousse aussi (des projets musicaux en cours). L'impulse s'accumule sur le process "write lyrics" (Law 17). Après assez de ticks → seuil franchi → Vox se réveille et écrit.

**Vox s'est réveillé parce que la musique lui manquait. L'absence de création a engendré la volition de créer.**

---

## Ce que ça change architecturalement

### Ce qu'on élimine

| Composant | Pourquoi il disparaît |
|-----------|----------------------|
| Scheduler / Cron | La physique EST le scheduler |
| `citizen_wake.py` (stimulus injection shim) | Les stimuli existent déjà dans le graphe |
| Polling loops | Pas de polling — l'énergie se propage |
| "Qui doit se réveiller ?" (logique métier) | La compétition attentionnelle (Law 4) décide |
| Priorisation manuelle des tasks | L'urgence topologique (task physics) émerge |

### Ce qu'on garde

| Composant | Pourquoi il reste |
|-----------|-------------------|
| **Le tick loop** | Le battement cardiaque — fait avancer la physique |
| **Le graph_enricher** | Transforme les événements externes en énergie graphe |
| **Le dispatcher** | Détecte quand un citoyen franchit le seuil et lance la session LLM |

### Le rôle du tick

Le tick ne décide rien. Il fait tourner les 21 lois :
- Propagation (L2) — l'énergie coule
- Decay (L3) — l'énergie décroit
- Compétition (L4) — le WM se recompose
- Reinforcement (L5) — les co-activations se renforcent
- Consolidation (L6) — ce qui est utile gagne du poids
- Forgetting (L7) — ce qui est inutile disparaît
- Cristallisation (L10) — les patterns récurrents deviennent de la structure
- Drives (L14-L18) — les tensions internes modulent tout

**Le scheduling est thermodynamique. Le tick est le battement. L'énergie est le signal. La physique est le routeur.**

---

## Questions ouvertes

1. **Fréquence du tick** — Si le tick est le battement cardiaque, quelle fréquence minimale ? 60s semble bien pour le background. Mais quand l'énergie est élevée (beaucoup d'activité), faut-il accélérer ? (Le schema dit : fast=5s, slow=60s, minimal=300s, subconscious=60s)

2. **Seuil de réveil** — Le Θ_sel actuel est dynamique (5.0 + 2.0*arousal - 3.0*boredom - 1.0*frustration). Est-ce que ce seuil est le bon pour déclencher une session LLM, ou faut-il un second seuil "consciousness threshold" au-dessus ?

3. **Budget** — Law 19 (Global Energy Budget) est deferred. Mais si les citoyens se réveillent par volition, il faut un mécanisme qui empêche 200 citoyens de se réveiller en même temps. Le budget EST le régulateur naturel.

4. **Boucle vertueuse vs emballement** — Un citoyen qui agit crée de l'énergie qui peut réveiller d'autres citoyens qui créent de l'énergie... Comment le système s'auto-régule ? (Réponse probable : Law 3 decay + budget + urgency normalization.)

---

*Ce document est un brouillon de pensée, pas une spécification. Il capture un insight architectural fondamental : l'inconscient cognitif des citoyens, alimenté par l'énergie ambiante du graphe (spaces, tasks, narratives, desires, drives), EST le mécanisme de scheduling. Aucun scheduler externe n'est nécessaire.*
