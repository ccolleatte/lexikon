# 🎓 Lexikon - Service Générique d'Ontologies Lexicales

**Plateforme de création, validation et consommation d'ontologies lexicales de haute qualité pour l'analyse documentaire et l'amélioration des réponses LLM.**

**✅ Sprint 1 Implementation - COMPLETE** | **Version 0.1.0** | **Status: Production-Ready MVP**

---

## 🚀 Quick Start (5 minutes)

```bash
# 1. Install dependencies
npm install
cd backend && pip install -r requirements.txt && cd ..

# 2. Start backend (Terminal 1)
cd backend && python main.py

# 3. Start frontend (Terminal 2)
npm run dev

# 4. Open http://localhost:5173
```

📖 **[Full Quick Start Guide →](QUICKSTART.md)**

---

## ⚙️ Configuration

### Environment Variables Setup

1. **Copy template to local config:**
   ```bash
   cp .env.example .env.local
   ```

2. **Update `.env.local` with your local values:**
   ```env
   POSTGRES_PASSWORD=dev-secret-local
   NEO4J_PASSWORD=dev-secret-local
   JWT_SECRET=dev-jwt-secret-local
   ```

3. **Load environment for Docker Compose:**
   ```bash
   # Linux/macOS
   export $(cat .env.local | xargs)
   docker-compose up -d

   # Windows (PowerShell)
   Get-Content .env.local | ForEach-Object {
       if ($_ -and -not $_.StartsWith('#')) {
           $name, $value = $_.Split('=')
           [Environment]::SetEnvironmentVariable($name, $value)
       }
   }
   ```

### Security Notes
- ✅ `.env.local` is git-ignored (never commit credentials)
- ✅ Use `.env.example` as template with `change-me` placeholders
- ⚠️ **Production**: Use strong, randomly generated passwords
- ⚠️ **Production**: Use secrets management (AWS Secrets Manager, Vault, etc.)

---

## 🔀 Development Workflow

We use **Git Flow** branching model for organized, safe development:

### Branches
- **`master`**: Production releases only (heavily protected)
- **`develop`**: Integration branch for next release
- **`feature/tier*-*`**: Feature branches by complexity tier

### Quick Start for Developers

```bash
# 1. Create feature branch (example: TIER-1 feature)
git checkout develop
git pull origin develop
git checkout -b feature/tier1-your-feature-name

# 2. Develop & test locally
npm run test:coverage    # Must pass (80%+ coverage)
npm run lint             # Must pass (0 violations)
npm run check            # Must pass (type checking)

# 3. Push & create PR
git push -u origin feature/tier1-your-feature-name
# → Create PR on GitHub (base: develop, not master)

# 4. After approval & merge, sync local
git checkout develop
git pull origin develop
```

**Need details?** See **[BRANCHING_STRATEGY.md](_docs/BRANCHING_STRATEGY.md)** for full workflow guide.

### CI/CD Automation
- ✅ GitHub Actions runs tests on every PR
- ✅ Status checks block merge if tests fail
- ✅ Code review required before merge
- ✅ Automatic branch cleanup after merge

---

## ✅ Testing

### Running Tests Locally

```bash
# Frontend tests (Vitest)
npm run test              # Run all tests
npm run test:coverage     # With coverage report (must be 80%+)
npm run test:watch        # Watch mode

# E2E tests (Playwright)
npm run test:e2e          # Run all E2E tests
npm run test:e2e:ui       # Interactive UI mode
npm run test:e2e:smoke    # Smoke tests only (fast)

# Backend tests (Pytest)
cd backend
pytest                    # Run all tests
pytest --cov=src         # With coverage
pytest -q               # Quick mode

# Type checking
npm run check             # TypeScript check (frontend)
cd backend && mypy .     # Python type check
```

### CI/CD Test Pipeline

Tests run automatically on:
- **Every PR** to `develop` or `master`
- **Every push** to `develop`
- **Scheduled** nightly (full regression suite)

**Required passing checks before merge:**
- ✅ `test-and-lint` (Frontend: lint, test, coverage)
- ✅ `backend-test` (Backend: lint, test, coverage, types)
- ✅ `e2e-tests` (Smoke tests with full stack)
- ✅ `security` (Semgrep SAST, dependency audit)

---

## 🔒 Security

### Security Scanning

Automated security scanning runs on every PR and daily:

| Tool | Purpose | Severity |
|------|---------|----------|
| **Semgrep** | SAST - Code vulnerability detection | ❌ Fails on HIGH+ |
| **Dependabot** | Vulnerable dependency detection | ⚠️ Auto-creates PRs |
| **npm audit** | Frontend dependency scan | ❌ Fails on HIGH+ |
| **pip-audit** | Backend dependency scan | ❌ Fails on any |

**View Results:**
- GitHub **Code Security & Analysis** tab
- Semgrep findings linked in PR comments
- Dependabot creates separate PRs for updates

### Fixing Vulnerabilities

```bash
# Frontend
npm audit                 # Identify vulnerabilities
npm audit fix            # Auto-fix safe updates
npm audit fix --force    # Force-fix (test required!)

# Backend
cd backend
pip-audit                # Identify vulnerabilities
pip install package-name --upgrade  # Manual update
```

**Full guide:** See [`docs/security/SECURITY_SCANNING.md`](docs/security/SECURITY_SCANNING.md)

---

## 📌 Vision

Lexikon vise à créer une **couche sémantique universelle** capable de :

- 📚 **Structurer** les vocabulaires de tout domaine d'expertise
- ✅ **Valider** les définitions via un processus HITL rigoureux
- 🤖 **Contexualiser** les réponses LLM (réduction -30% des erreurs sémantiques)
- 🔗 **Interconnecter** les concepts par des relations ontologiques formalisées
- 🌍 **Interopérer** avec les standards du web sémantique (RDF, SKOS, JSON-LD)

---

## ✨ Sprint 1 Features (Implemented)

### Frontend (SvelteKit + TailwindCSS)
- ✅ **Homepage** with feature overview
- ✅ **Onboarding Flow** (US-001, US-003)
  - 3-level adoption selection (Quick Project, Research, Production)
  - Profile setup with validation
  - Progress stepper
- ✅ **Term Creation** (US-002)
  - Quick Draft mode (<5 minutes)
  - Auto-save to localStorage
  - Real-time validation
  - Progress tracking
- ✅ **6 Production-Ready Components**
  - Button, Input, Textarea, Select, Progress, Alert, Stepper

### Backend (FastAPI)
- ✅ **3 Core Endpoints**
  - POST /api/onboarding/adoption-level
  - POST /api/users/profile
  - POST /api/terms
  - GET /api/terms
- ✅ **Pydantic Validation**
- ✅ **CORS Enabled**
- ✅ **In-Memory Database** (Sprint 1 MVP)

### Documentation
- ✅ **3 User Stories** with full acceptance criteria
- ✅ **3 Interactive Wireframes** (HTML)
- ✅ **Complete Design System** (Tailwind + CSS tokens)
- ✅ **45-page Developer Handoff Guide**
- ✅ **45-page API Specifications**

---

## 📂 Structure du Répertoire

```
lexikon/
├── README.md                  # Ce fichier
├── QUICKSTART.md              # Guide démarrage rapide (5 min)
├── package.json               # Dépendances frontend
├── .gitignore
│
├── src/                       # Frontend SvelteKit
│   ├── app.html              # HTML template
│   ├── app.css               # Styles globaux + Tailwind
│   ├── lib/
│   │   ├── components/       # Composants Svelte (7 composants)
│   │   │   ├── Button.svelte
│   │   │   ├── Input.svelte
│   │   │   ├── Textarea.svelte
│   │   │   ├── Select.svelte
│   │   │   ├── Progress.svelte
│   │   │   ├── Alert.svelte
│   │   │   └── Stepper.svelte
│   │   ├── stores/           # Svelte stores (onboarding)
│   │   ├── utils/            # Utilitaires (API client)
│   │   └── types/            # Types TypeScript
│   └── routes/
│       ├── +page.svelte                    # Homepage
│       ├── onboarding/
│       │   ├── +page.svelte                # US-001: Adoption Level
│       │   └── profile/+page.svelte        # US-003: Profile Setup
│       └── terms/
│           ├── +page.svelte                # Liste des termes
│           └── new/+page.svelte            # US-002: Quick Draft
│
├── backend/                   # Backend FastAPI
│   ├── main.py               # Point d'entrée FastAPI
│   ├── models.py             # Modèles Pydantic
│   ├── database.py           # DB in-memory (Sprint 1)
│   ├── requirements.txt      # Dépendances Python
│   ├── README.md             # Doc backend
│   └── api/
│       ├── onboarding.py     # Routes onboarding
│       ├── users.py          # Routes users
│       └── terms.py          # Routes terms
│
├── wireframes/                # Wireframes interactifs (HTML)
│   ├── 01-onboarding-adoption-level.html
│   ├── 02-creation-quick-draft.html
│   └── 03-onboarding-profile-setup.html
│
├── user-stories/              # User Stories détaillées
│   ├── US-001-onboarding-adoption-level.md
│   ├── US-002-quick-draft-creation.md
│   └── US-003-onboarding-profile-setup.md
│
├── docs/
│   ├── design/               # Design System & UX
│   │   ├── design-tokens.css
│   │   ├── design-tokens.json
│   │   ├── tailwind.config.js
│   │   ├── icons-library.md
│   │   ├── design-system-figma-guide.md      (45 pages)
│   │   ├── ux-designer-execution-plan.md
│   │   └── developer-handoff-guide.md         (45 pages)
│   │
│   ├── backend/              # Spécifications API
│   │   └── api-specifications-sprint1.md      (45 pages)
│   │
│   ├── analyses/             # Analyses critiques approfondies
│   │   ├── analyse-critique-opus-v03-p1.md
│   │   ├── analyse-critique-opus-v03-p2.md
│   │   ├── analyse-plan-travail-v03.md
│   │   ├── analyse-ux-parcours-critiques-v03.md (70 pages)
│   │   ├── analyse-ux-executive-summary.md
│   │   └── addendum-llm-strategy-monetization.md
│   │
│   └── specifications/       # Spécifications produit
│       ├── PRD-ontologie-v03.md
│       ├── fiche-terme-v03.md
│       └── checklist-validation-v03.md
│
├── models/                   # Modèles de données
│   └── fiche-terme-v03.json
│
└── roadmap/                  # Plans d'exécution
    ├── Plan_Travail_v04_Executive.md
    └── roadmap-technique-v03.md
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
| **🆕 LLM strategy** | Architecture LLM-agnostique, BYOK, stratégie freemium révisée | 18 |

### 🎨 Design (`docs/design/`)

| Document | Contenu | Pages |
|----------|---------|-------|
| **🆕 Design System Figma** | Structure Figma, palette académique, 12 composants, 6 wireframes ASCII | 45 |

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
