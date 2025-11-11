# 🎓 Lexikon - Service Générique d'Ontologies Lexicales

**Plateforme de création, validation et consommation d'ontologies lexicales de haute qualité pour l'analyse documentaire et l'amélioration des réponses LLM.**

---

## 📌 Vision

Lexikon vise à créer une **couche sémantique universelle** capable de :

- 📚 **Structurer** les vocabulaires de tout domaine d'expertise
- ✅ **Valider** les définitions via un processus HITL rigoureux
- 🤖 **Contexualiser** les réponses LLM (réduction -30% des erreurs sémantiques)
- 🔗 **Interconnecter** les concepts par des relations ontologiques formalisées
- 🌍 **Interopérer** avec les standards du web sémantique (RDF, SKOS, JSON-LD)

---

## 📂 Structure du Répertoire

```
lexikon/
├── README.md (ce fichier)
├── .gitignore
│
├── docs/
│   ├── analyses/              # Analyses critiques approfondies
│   │   ├── analyse-critique-opus-v03-p1.md      (Forces & zones d'ombre)
│   │   ├── analyse-critique-opus-v03-p2.md      (Recommandations & architecture)
│   │   ├── analyse-plan-travail-v03.md          (Analyse du plan opérationnel)
│   │   ├── analyse-ux-parcours-critiques-v03.md (Analyse UX complète + parcours)
│   │   └── analyse-ux-executive-summary.md      (Résumé exécutif UX)
│   │
│   └── specifications/        # Spécifications produit et techniques
│       ├── PRD-ontologie-v03.md                 (Product Requirements Document complet)
│       ├── fiche-terme-v03.md                   (Modèle de fiche-terme enrichi)
│       └── checklist-validation-v03.md          (Critères HITL complets)
│
├── models/                    # Modèles de données
│   └── fiche-terme-v03.json                     (Exemple JSON : "aliénation" avec 9 relations)
│
└── roadmap/                   # Plans d'exécution
    ├── Plan_Travail_v04_Executive.md            (Executive summary 6 pages)
    └── roadmap-technique-v03.md                 (Roadmap 8 sprints détaillée)
```

---

## 🎯 Contenu des Documents

### 📊 Analyses (`docs/analyses/`)

| Document | Contenu | Pages |
|----------|---------|-------|
| **p1** | Forces de l'approche Gemini, zones d'ombre techniques | 80 |
| **p2** | Architecture détaillée, recommandations, modèle DB | 150 |
| **plan** | Critique du Plan_Travail_v0.3, points manquants | 50 |
| **🆕 UX parcours** | Analyse UX complète, 8 frictions, 7 recommandations, 3 niveaux d'adoption | 70 |
| **🆕 UX exec** | Résumé exécutif UX pour stakeholders (lecture 3 min) | 12 |

### 📋 Spécifications (`docs/specifications/`)

| Document | Contenu | Utilité |
|----------|---------|---------|
| **PRD v0.3** | Vision complète, roadmap, budget, risques | Référence produit |
| **Fiche-terme** | Modèle markdown + 10 sections structurées | Template création |
| **Checklist** | 60+ critères HITL auto + expert | Validation qualité |

### 🗄️ Modèles (`models/`)

- **fiche-terme-v03.json** : Exemple complet du terme "aliénation" avec relations typées

### 🚀 Roadmap (`roadmap/`)

| Document | Contenu |
|----------|---------|
| **Plan v0.4** | Executive summary actionnable (6 pages) |
| **Roadmap technique** | 8 sprints détaillés avec user stories |

---

## 🔑 Points Clés du Projet

### Architecture Technique

```yaml
Backend:    FastAPI + PostgreSQL + pgvector + Neo4j
Frontend:   SvelteKit + D3.js
Embeddings: sentence-transformers (768 dimensions)
Ops:        Docker + Kubernetes + GitHub Actions
```

### Phases de Développement

| Phase | Durée | Livrable | Budget |
|-------|-------|----------|--------|
| **v0.1** (Foundation) | 8 sem | API + 300 termes SHS | €80k |
| **v0.2** (Validation) | 8 sem | Interface HITL + 2 domaines | €80k |
| **v1.0** (Integration) | 8 sem | LLM integration prouvée | €98k |

**Budget total : €258k (6 mois)**

### Success Metrics

- ✅ **Qualité** : 80% termes validés HITL
- ✅ **Performance** : API latency < 200ms
- ✅ **Impact LLM** : -30% erreurs sémantiques
- ✅ **Adoption** : 100 utilisateurs beta

---

## 🚦 Status Actuél

- **Analyse critique** : ✅ Complète (v0.3)
- **Architecture technique** : ✅ Définie
- **Budget & Timeline** : ✅ Chiffré
- **Risques** : ✅ Identifiés et mitigés
- **Prêt exécution** : ✅ OUI

### Prochaines Étapes Immédiates

1. **POC technique** : Neo4j vs PostgreSQL (Week 1)
2. **Recrutement** : Backend developer senior (Week 1)
3. **Setup infra** : Docker, GitHub Actions (Week 2)
4. **Sprint 1** : Schéma DB + API core (Weeks 3-4)

---

## 📚 Comment Utiliser Ce Répertoire

### Pour Comprendre le Projet
1. Commencer par **Plan_Travail_v04_Executive.md** (6 pages)
2. Lire **PRD-ontologie-v03.md** pour la vision complète
3. Explorer **analyse-critique-opus-v03-p1.md** pour les forces/faiblesses

### Pour Implémenter
1. Consulter **roadmap-technique-v03.md** pour la structure
2. Utiliser **fiche-terme-v03.md** comme template
3. Appliquer **checklist-validation-v03.md** lors de la validation

### Pour Valider la Qualité
1. Vérifier les 60+ critères dans la checklist
2. Utiliser **fiche-terme-v03.json** comme référence
3. Suivre les KPIs définis dans PRD

---

## 🤝 Contributing

Ce projet suit une approche **HITL (Human-in-the-Loop)** strict :

- Toute validation doit être **sourcée** et **tracée**
- Les relations doivent être **justifiées**
- La qualité est **non-négociable**

Avant de contribuer, consultez :
- `docs/specifications/checklist-validation-v03.md`
- `docs/specifications/fiche-terme-v03.md`

---

## 📞 Contact

- **Project Lead** : Claude Opus (Analysis & Strategy)
- **GitHub** : [ccolleatte/lexikon](https://github.com/ccolleatte/lexikon)
- **Status** : Private Repository

---

## 📄 Licence

À définir (MIT recommandé pour open-source futur)

---

**Dernière mise à jour** : 2025-11-11
**Version** : v0.4 (Executive + Technical)
**Maturité** : 9/10 - Prêt pour exécution
