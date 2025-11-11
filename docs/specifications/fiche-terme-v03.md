# Modèle de Fiche-Terme v0.3

## Métadonnées Administratives

**ID** : `<UUID auto-généré>`
**Version** : `<numéro de version>`
**Statut** : `draft | proposed | in_review | validated | deprecated`
**Domaine Principal** : `<Domaine (ex: SHS, Juridique, Médical, Informatique)>`
**Sous-domaine** : `<Spécialisation optionnelle>`
**Auteur de la fiche** : `<nom, email>`
**Date de création** : `<YYYY-MM-DD HH:MM:SS>`
**Dernière modification** : `<YYYY-MM-DD HH:MM:SS>`
**Dernière validation** : `<YYYY-MM-DD HH:MM:SS>`
**Validateurs** : `<liste des validateurs avec dates>`

---

## 1. Identification du Terme

### 1.1 Terme Principal
**Label** : `<Terme en français>`
**Slug** : `<terme-en-minuscules-avec-tirets>`
**Langue** : `fr | en | de | es | ...`
**Prononciation** : `[API optionnel]`

### 1.2 Variantes et Synonymes

| Terme | Type | Langue | Contexte | Période | Note |
|-------|------|---------|----------|---------|------|
| `<terme>` | `synonym\|variant\|abbreviation\|antonym\|translation` | `<code>` | `<région/école>` | `<années>` | `<précision>` |

**Exemples** :
| Terme | Type | Langue | Contexte | Période | Note |
|-------|------|---------|----------|---------|------|
| Entfremdung | translation | de | - | - | Terme original chez Marx |
| Estrangement | translation | en | Anglo-saxon | - | Usage philosophique |
| Réification | synonym | fr | Lukács | 1920-1970 | Extension du concept |

---

## 2. Définitions

### 2.1 Définition Courte
> `<Une phrase claire et concise, max 200 caractères, accessible au grand public>`

**Critères** :
- ✅ Sans jargon technique
- ✅ Compréhensible hors contexte
- ✅ Essence du concept

### 2.2 Définition Longue
> `<Développement détaillé du concept, 200-500 mots>`

**Structure recommandée** :
1. Définition générale
2. Nuances et distinctions
3. Évolution historique
4. Applications contemporaines

### 2.3 Définition Contextuelle (Multi-écoles)

| École/Auteur | Définition Spécifique | Période | Différence Clé |
|--------------|----------------------|---------|----------------|
| `<nom>` | `<définition adaptée>` | `<années>` | `<vs définition générale>` |

**Exemple** :
| École/Auteur | Définition Spécifique | Période | Différence Clé |
|--------------|----------------------|---------|----------------|
| Marx | Perte de contrôle du travailleur sur sa production | 1844-1867 | Focus économique |
| Hegel | Moment du développement de l'Esprit | 1807 | Focus métaphysique |
| Lukács | Transformation des rapports sociaux en choses | 1923 | Focus réification |

---

## 3. Contexte d'Usage

### 3.1 Domaines d'Application
- **Primaire** : `<domaine principal d'utilisation>`
- **Secondaires** : `<liste des domaines connexes>`
- **Interdisciplinaire** : `<ponts avec autres domaines>`

### 3.2 Usage et Précautions
- **Usage local/spécifique** : `oui | non`
- **Risques de confusion** : `<homographes, faux-amis>`
- **Ne pas confondre avec** : `<termes proches mais distincts>`
- **Précisions critiques** : `<nuances importantes>`

### 3.3 Indicateurs de Pertinence
- **Fréquence corpus** : `<score 0-100>`
- **Centralité réseau** : `<score 0-100>`
- **Demande utilisateurs** : `<nombre de recherches>`
- **Score priorité** : `<calculé automatiquement>`

---

## 4. Relations Ontologiques

### 4.1 Relations Hiérarchiques

| Type | Direction | Terme Cible | Force | Note |
|------|-----------|-------------|-------|------|
| `is_a` | ↑ | `<terme parent>` | `0.0-1.0` | `<justification>` |
| `has_subclass` | ↓ | `<terme enfant>` | `0.0-1.0` | `<spécialisation>` |
| `part_of` | ↑ | `<terme englobant>` | `0.0-1.0` | `<tout/partie>` |

### 4.2 Relations Associatives

| Type | Terme Cible | Force | Symétrique | Temporel | Note |
|------|-------------|-------|------------|----------|------|
| `related_to` | `<terme>` | `0.0-1.0` | ✓ | - | `<nature du lien>` |
| `employs` | `<concept utilisé>` | `0.0-1.0` | ✗ | - | `<comment>` |
| `opposes` | `<concept opposé>` | `0.0-1.0` | ✓ | - | `<antinomie>` |

### 4.3 Relations Causales et Temporelles

| Type | Terme Cible | Force | Période | Note |
|------|-------------|-------|---------|------|
| `causes` | `<effet>` | `0.0-1.0` | `<période>` | `<mécanisme>` |
| `results_from` | `<cause>` | `0.0-1.0` | `<période>` | `<processus>` |
| `precedes` | `<successeur>` | `0.0-1.0` | `<dates>` | `<évolution>` |
| `influenced_by` | `<source>` | `0.0-1.0` | `<période>` | `<nature influence>` |

### 4.4 Inférences Possibles
```
SI [ce terme] is_a [A] ET [A] is_a [B]
ALORS [ce terme] is_a [B] (transitivité)

SI [ce terme] opposes [X]
ALORS [X] opposes [ce terme] (symétrie)
```

---

## 5. Auteurs et Écoles de Pensée

### 5.1 Auteurs Associés

| Auteur | Rôle | Période | École | Contribution | Sources |
|--------|------|---------|-------|--------------|---------|
| `<nom complet>` | `creator\|contributor\|critic\|popularizer` | `<années>` | `<école>` | `<apport spécifique>` | `<refs>` |

### 5.2 Écoles et Courants

| École | Période | Approche | Divergences | Représentants |
|-------|---------|----------|-------------|---------------|
| `<nom>` | `<années>` | `<description>` | `<vs autres écoles>` | `<auteurs clés>` |

---

## 6. Citations et Sources

### 6.1 Citations Fondatrices
> « `<citation textuelle importante>` »
> — **Auteur**, *Titre de l'œuvre*, Éditeur, Année, p. XX.

### 6.2 Sources Primaires
1. **[Auteur, Année]** *Titre complet*, Éditeur, Lieu.
   - Pages : `<pages pertinentes>`
   - DOI/URL : `<lien>`
   - Contexte : `<importance pour le terme>`

### 6.3 Sources Secondaires
- Analyses et commentaires
- Articles académiques récents
- Entrées encyclopédiques de référence

### 6.4 Ressources Numériques
- **Wikidata** : `<QID si existant>`
- **DBpedia** : `<URI si existant>`
- **VIAF** : `<ID si auteur>`
- **DOI** : `<liste des DOI pertinents>`

---

## 7. Questions de Compétence (CQ)

### 7.1 Questions de Validation

| Niveau | Question | Réponse Attendue | Critères Évaluation |
|--------|----------|------------------|---------------------|
| **Base** | `<question simple>` | `<réponse>` | `<points clés>` |
| **Intermédiaire** | `<question contexte>` | `<réponse>` | `<nuances>` |
| **Avancé** | `<question critique>` | `<réponse>` | `<analyse>` |

### 7.2 Tests de Désambiguïsation
- **Prompt ambigu** : `<exemple de phrase ambiguë>`
- **Interprétations possibles** : `<liste>`
- **Résolution avec ontologie** : `<comment l'ontologie aide>`

---

## 8. Validation HITL

### 8.1 Checklist de Validation

**Critères Automatiques** :
- [ ] Définition courte < 200 caractères
- [ ] Définition longue > 50 mots
- [ ] Au moins 1 citation source
- [ ] Au moins 1 relation ontologique
- [ ] Pas de relation circulaire
- [ ] Domaine assigné
- [ ] Slug unique dans le domaine

**Critères Experts** :
- [ ] Définitions exactes et nuancées
- [ ] Relations ontologiques cohérentes
- [ ] Sources fiables et pertinentes
- [ ] Contexte historique correct
- [ ] Distinctions claires avec termes proches
- [ ] Absence de biais idéologique non signalé
- [ ] Complétude pour le niveau visé

### 8.2 Historique de Validation

| Date | Validateur | Décision | Score | Commentaires |
|------|------------|----------|-------|--------------|
| `<YYYY-MM-DD>` | `<nom>` | `approved\|rejected\|needs_work` | `<0-100>` | `<notes>` |

### 8.3 Conflits et Résolutions

| Date | Nature du Conflit | Validateurs Impliqués | Résolution | Arbitre |
|------|-------------------|----------------------|------------|---------|
| `<date>` | `<description>` | `<noms>` | `<décision finale>` | `<nom>` |

---

## 9. Métadonnées Techniques

### 9.1 Embeddings
- **Modèle** : `sentence-transformers/all-mpnet-base-v2`
- **Dimensions** : `768`
- **Texte source** : `<définition longue + contexte>`
- **Dernière génération** : `<timestamp>`

### 9.2 Métriques d'Usage
- **Consultations API** : `<nombre total>`
- **Injections LLM** : `<nombre>`
- **Recherches** : `<nombre>`
- **Dernière utilisation** : `<timestamp>`

### 9.3 Versioning
- **Version actuelle** : `<n.n.n>`
- **Versions précédentes** : `<liste avec dates>`
- **Changelog** : `<modifications majeures>`

---

## 10. Notes et Annotations

### 10.1 Notes Éditoriales
`<Commentaires pour les futurs éditeurs, points d'attention, débats en cours>`

### 10.2 Suggestions d'Amélioration
- [ ] `<amélioration suggérée 1>`
- [ ] `<amélioration suggérée 2>`

### 10.3 Liens avec Autres Projets
- **Projets connexes** : `<liste>`
- **Intégrations** : `<systèmes utilisant ce terme>`

---

## Template JSON Correspondant

```json
{
  "id": "UUID",
  "version": "1.0.0",
  "term": {
    "label": "string",
    "slug": "string",
    "language": "fr"
  },
  "definitions": {
    "short": "string < 200 chars",
    "long": "string 200-500 words",
    "contextual": [
      {
        "school": "string",
        "definition": "string",
        "period": "string",
        "key_difference": "string"
      }
    ]
  },
  "domain": {
    "primary": "string",
    "secondary": ["string"],
    "interdisciplinary": ["string"]
  },
  "relations": [
    {
      "type": "enum[is_a, part_of, related_to, employs, etc.]",
      "target_id": "UUID",
      "target_label": "string",
      "strength": 0.0-1.0,
      "symmetric": boolean,
      "temporal": {
        "from": "date",
        "to": "date"
      },
      "note": "string"
    }
  ],
  "authors": [
    {
      "name": "string",
      "role": "enum[creator, contributor, critic, popularizer]",
      "period": "string",
      "school": "string",
      "contribution": "string"
    }
  ],
  "citations": [
    {
      "quote": "string",
      "author": "string",
      "title": "string",
      "publisher": "string",
      "year": integer,
      "page": "string",
      "doi": "string",
      "url": "string"
    }
  ],
  "synonyms": [
    {
      "term": "string",
      "type": "enum[synonym, variant, abbreviation, antonym, translation]",
      "language": "string",
      "context": "string",
      "period": "string",
      "note": "string"
    }
  ],
  "validation": {
    "status": "enum[draft, proposed, in_review, validated, deprecated]",
    "last_validation": "datetime",
    "validators": [
      {
        "name": "string",
        "date": "datetime",
        "decision": "enum[approved, rejected, needs_work]",
        "score": 0-100,
        "comments": "string"
      }
    ],
    "quality_score": 0-100,
    "priority_score": 0-100
  },
  "embeddings": {
    "model": "string",
    "vector": [float],
    "dimensions": integer,
    "generated_at": "datetime"
  },
  "metadata": {
    "created_at": "datetime",
    "updated_at": "datetime",
    "created_by": "string",
    "usage_count": integer,
    "last_accessed": "datetime"
  }
}
```

---

*Modèle de Fiche-Terme v0.3 - Service Générique d'Ontologies Lexicales*
*Ce modèle est extensible et doit être adapté selon les besoins spécifiques de chaque domaine*