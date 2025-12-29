# Archived: SYNC_Nature.md

Archived on: 2025-12-29
Original file: SYNC_Nature.md

---

## PROPOSITIONS

### @mind:proposition P1: Participes comme forme canonique

Remplacer les verbes par des participes présents pour unifier nodes et links:

```yaml
# Au lieu de:
proves:
  permanence: 0.9

# Utiliser:
proving:
  permanence: 0.9
```

**Avantages:**
- Fonctionne pour links: "this evidence is proving the claim"
- Fonctionne pour nodes: "this task is proving" (= probant)
- Forme adjectivale naturelle en anglais

**Mapping suggéré:**

| Actuel | Proposé | FR |
|--------|---------|-----|
| proves | proving | probant |
| claims | claiming | revendicatif |
| blocks | blocking | bloquant |
| triggers | triggering | déclencheur |
| supports | supporting | supportant |
| resolves | resolving | résolvant |

---

### @mind:proposition P2: Axes émotionnels → Axes SubEntity

Les axes Plutchik (joy_sadness, trust_disgust, fear_anger, surprise_anticipation) sont abstraits. Les remplacer par des axes utiles à la traversée SubEntity:

**Idées d'axes orientés exploration:**

| Axe | Range | Effet sur SubEntity |
|-----|-------|---------------------|
| `relevance` | 0-1 | Priorité de traversée (remplace trust?) |
| `novelty` | 0-1 | Favorise exploration vs exploitation |
| `tension` | -1 to +1 | Contradiction (-) vs confirmation (+) |
| `depth` | 0-1 | Incite à creuser vs rester en surface |
| `branching` | 0-1 | Probabilité de fork du subentity |

**Ou axes cognitifs:**

| Axe | Signification |
|-----|---------------|
| `certainty` | Confiance dans l'info (remplace trust_disgust?) |
| `salience` | Importance contextuelle |
| `coherence` | Cohérence avec le chemin actuel |
| `surprise` | Inattendu (garde celui-ci) |

@mind:todo Définir les axes qui guident vraiment le comportement SubEntity.

---

### @mind:proposition P3: Decay différencié node/link

Même nature, interprétation différente:

```python
# Link decay: affecte la force de la relation
link.weight *= (1 - decay_rate * permanence_inverse)

# Node decay: affecte l'énergie du node
node.energy *= (1 - decay_rate * permanence_inverse)
```

La `permanence` du nature contrôle la résistance au decay, mais l'effet est différent.

---

### @mind:proposition P4: Héritage de nature

Un node pourrait hériter/propager sa nature aux links sortants:

```
Node "urgent task" (energy: 8)
  → Link créé automatiquement avec energy boost
  → Ou: link.energy = blend(link.energy, source_node.energy)
```

---

### @mind:proposition P5: Nature composée

Permettre plusieurs natures séparées par `+`:

```
"proving + urgent, with confidence"
```

Floats fusionnés avec règle (max, moyenne, dernier gagne).

---

### @mind:proposition P6: Catégories sémantiques pour nodes

Ajouter des termes spécifiques aux états de nodes:

```yaml
# États de workflow
pending:
  energy: 3.0
running:
  energy: 7.0
blocked:
  energy: 2.0
  fear_anger: 0.4
completed:
  permanence: 0.95
  energy: 1.0

# Importance
core:
  weight: 6.0
  permanence: 0.9
minor:
  weight: 0.5
  decay_multiplier: 2.0
```

---

