# Plan d'Action Détaillé - Développeur Junior
## Projet Lexikon - Sprint de Déblocage et Lancement Beta

**Version** : 1.0
**Date** : 2025-11-17
**Durée totale** : 4 semaines
**Niveau requis** : Développeur junior (connaissances Python/JavaScript de base)

---

## 📋 Vue d'Ensemble

Ce plan d'action vous guide pas à pas pour débloquer les 4 problèmes critiques du projet Lexikon et préparer le lancement en beta. Chaque tâche est décomposée en étapes détaillées avec des commandes exactes à exécuter.

### 🎯 Objectifs

**Semaine 1** : Débloquer les 4 problèmes critiques (Niveau 0)
- Activer la base de données PostgreSQL (données persistantes)
- Intégrer l'authentification JWT (login/logout fonctionnels)
- Corriger les vulnérabilités de sécurité
- Ajouter les tests backend

**Semaine 2** : Préparer le lancement beta (Niveau 1)
- Automatiser les tests E2E dans CI/CD
- Activer la stratégie Git Flow
- Ajouter le rate limiting (protection contre abus)
- Implémenter le logging structuré
- Créer les tests d'intégration

**Semaines 3-4** : Renforcer la production (Niveau 2)
- Finaliser OAuth (GitHub/Google)
- Ajouter le monitoring avec Sentry
- Containeriser l'application
- Tester Neo4j à l'échelle
- Instrumenter les métriques LLM

### 📊 Métriques de Succès

| Critère | Avant | Après Semaine 1 | Après Semaine 2 | Après Semaine 4 |
|---------|-------|-----------------|-----------------|-----------------|
| Persistence données | ❌ In-memory | ✅ PostgreSQL | ✅ PostgreSQL | ✅ PostgreSQL |
| Auth fonctionnelle | ❌ Factice | ✅ JWT | ✅ JWT | ✅ JWT + OAuth |
| Tests backend | ❌ 0% | ✅ 80%+ | ✅ 80%+ | ✅ 80%+ |
| Sécurité | ❌ Vulnérabilités | ✅ Corrigée | ✅ Corrigée | ✅ Hardening |
| Tests E2E auto | ❌ Manuel | ❌ Manuel | ✅ CI/CD | ✅ CI/CD |
| Monitoring | ❌ Aucun | ❌ Logs basiques | ✅ Logging | ✅ Sentry |
| Prêt beta | ❌ Non | 🟡 Presque | ✅ Oui | ✅ Production |

---

## 📚 Structure des Guides

Ce plan est divisé en plusieurs documents pour faciliter la lecture :

### Documents Principaux

1. **[Semaine 1 - Déblocage Critique](./guides-junior/SEMAINE-1-BLOCKERS.md)** (2-3 jours)
   - Jour 1-2 : PostgreSQL + JWT
   - Jour 3 : Sécurité
   - Jour 4-5 : Tests backend + CI

2. **[Semaine 2 - Lancement Beta](./guides-junior/SEMAINE-2-LAUNCH-READINESS.md)** (5 jours)
   - Jour 1 : Tests E2E en CI
   - Jour 2 : Git Flow
   - Jour 3 : Rate limiting
   - Jour 4 : Logging structuré
   - Jour 5 : Tests d'intégration

3. **[Semaines 3-4 - Production](./guides-junior/SEMAINES-3-4-PRODUCTION.md)** (10 jours)
   - Jours 1-3 : OAuth complet
   - Jours 4-5 : Monitoring Sentry
   - Jours 6-8 : Containerisation
   - Jours 9-10 : Tests charge Neo4j

### Documents de Référence

4. **[Annexe A - Commandes Git](./guides-junior/ANNEXE-A-GIT.md)**
   - Commandes de base
   - Résolution de conflits
   - Bonnes pratiques

5. **[Annexe B - Debugging](./guides-junior/ANNEXE-B-DEBUGGING.md)**
   - Erreurs fréquentes et solutions
   - Outils de débogage
   - Logs et traces

6. **[Annexe C - Tests](./guides-junior/ANNEXE-C-TESTS.md)**
   - Écrire des tests unitaires
   - Tests d'intégration
   - Tests E2E avec Playwright

---

## 🚀 Comment Utiliser Ce Guide

### Avant de Commencer

1. **Lisez d'abord ce document** pour comprendre la vue d'ensemble
2. **Configurez votre environnement** (voir section suivante)
3. **Suivez les guides semaine par semaine** dans l'ordre
4. **Ne sautez pas les vérifications** à chaque étape
5. **Demandez de l'aide** si vous êtes bloqué >30 minutes

### Convention de Notation

- 🎯 **Objectif** : Ce que vous allez accomplir
- ⏱️ **Durée estimée** : Temps prévu
- 📋 **Prérequis** : Ce qui doit être fait avant
- ⚠️ **Attention** : Points importants
- ✅ **Vérification** : Comment valider que ça marche
- 💡 **Conseil** : Astuces pour aller plus vite
- 🐛 **Debug** : Que faire si ça ne marche pas

### Exemple de Bloc d'Instruction

```markdown
### Étape 1 : Installer les dépendances

🎯 **Objectif** : Installer les packages Python nécessaires
⏱️ **Durée** : 5 minutes

**Commandes à exécuter**
```bash
cd backend
pip install -r requirements.txt
```

✅ **Vérification**
```bash
pip list | grep fastapi
# Devrait afficher : fastapi 0.104.1 (ou supérieur)
```

🐛 **Si erreur "pip: command not found"**
- Solution : `python3 -m pip install -r requirements.txt`
```

---

## ⚙️ Configuration de l'Environnement

### Prérequis Système

Avant de commencer, assurez-vous d'avoir :

#### Logiciels Requis

| Logiciel | Version minimale | Vérification | Installation |
|----------|------------------|--------------|--------------|
| **Git** | 2.30+ | `git --version` | [git-scm.com](https://git-scm.com/) |
| **Node.js** | 18.0+ | `node --version` | [nodejs.org](https://nodejs.org/) |
| **npm** | 8.0+ | `npm --version` | Inclus avec Node.js |
| **Python** | 3.10+ | `python3 --version` | [python.org](https://python.org/) |
| **Docker** | 20.0+ | `docker --version` | [docker.com](https://docker.com/) |
| **Docker Compose** | 2.0+ | `docker compose version` | Inclus avec Docker |

#### Éditeur de Code Recommandé

- **VS Code** avec extensions :
  - Python (Microsoft)
  - Svelte for VS Code
  - ESLint
  - Prettier
  - GitLens

### Configuration Initiale du Projet

#### 1. Cloner le dépôt (si pas déjà fait)

```bash
# Naviguer vers votre dossier de projets
cd ~/projects  # Ou votre dossier préféré

# Si le projet n'est pas encore cloné
git clone https://github.com/ccolleatte/lexikon.git
cd lexikon

# Vérifier que vous êtes au bon endroit
pwd
# Devrait afficher : /home/user/lexikon (ou votre chemin)
```

#### 2. Installer les dépendances Frontend

```bash
# Depuis la racine du projet
npm install

# Vérification
npm list --depth=0
# Devrait afficher la liste des packages sans erreurs
```

✅ **Vérification** : Le dossier `node_modules/` doit être créé avec ~500+ packages

#### 3. Installer les dépendances Backend

```bash
# Créer un environnement virtuel Python
cd backend
python3 -m venv venv

# Activer l'environnement virtuel
# Sur Linux/Mac :
source venv/bin/activate
# Sur Windows :
# venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Vérification
pip list | grep -E "fastapi|sqlalchemy|alembic"
# Devrait afficher :
# fastapi         0.104.1
# sqlalchemy      2.0.23
# alembic         1.12.1
```

✅ **Vérification** : Le prompt doit afficher `(venv)` au début de la ligne

#### 4. Démarrer les services Docker

```bash
# Depuis la racine du projet
docker compose up -d

# Vérifier que les conteneurs tournent
docker compose ps
# Devrait afficher :
# NAME         IMAGE           STATUS
# postgres     postgres:16     Up (healthy)
# neo4j        neo4j:5.14      Up (healthy)
```

✅ **Vérification** : Les deux conteneurs doivent avoir le statut "healthy"

🐛 **Si erreur "Cannot connect to Docker daemon"**
- Solution : Démarrer Docker Desktop
- Attendre que l'icône Docker soit verte

#### 5. Créer le fichier .env

```bash
# Copier le template
cp backend/.env.example backend/.env

# Éditer avec votre éditeur
code backend/.env  # VS Code
# OU
nano backend/.env  # Terminal
```

**Contenu minimal du fichier `.env`** :

```env
# Base de données PostgreSQL
DATABASE_URL=postgresql://lexikon:dev-secret@localhost:5432/lexikon

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=dev-secret

# JWT Secret (TEMPORAIRE - sera changé à la Semaine 1)
JWT_SECRET=CHANGE-ME-IN-WEEK-1

# Environnement
ENVIRONMENT=development
```

⚠️ **Important** : Le `JWT_SECRET` sera généré aléatoirement à la Semaine 1, Jour 3

#### 6. Tester que tout fonctionne

**Test Frontend**
```bash
# Depuis la racine
npm run dev

# Ouvrir http://localhost:5173 dans le navigateur
# Vous devriez voir la page d'accueil Lexikon

# Arrêter avec Ctrl+C
```

**Test Backend**
```bash
# Depuis backend/ avec venv activé
cd backend
source venv/bin/activate  # Si pas déjà fait
uvicorn main:app --reload

# Dans un autre terminal, tester l'API
curl http://localhost:8000/
# Devrait afficher : {"message": "Lexikon API v0.2.0"}

# Arrêter avec Ctrl+C
```

**Test Base de Données**
```bash
# Tester PostgreSQL
docker compose exec postgres psql -U lexikon -d lexikon -c "SELECT version();"
# Devrait afficher la version de PostgreSQL 16

# Tester Neo4j
docker compose exec neo4j cypher-shell -u neo4j -p dev-secret "RETURN 'OK' as status;"
# Devrait afficher : status
#                    "OK"
```

✅ **Checkpoint Final** : Si tous ces tests passent, votre environnement est prêt !

---

## 📅 Planning Détaillé

### Semaine 1 : Déblocage Critique (Priorité P0)

**Durée totale** : 14-23h (2-3 jours ingénieur)
**Statut requis** : ✅ Obligatoire avant beta

| Jour | Tâches | Durée | Fichiers modifiés |
|------|--------|-------|-------------------|
| **Jour 1** | PostgreSQL : Migrations + Intégration | 4-6h | `backend/main.py`, migrations |
| **Jour 2** | JWT : Intégration complète | 3-5h | `backend/api/auth.py` |
| **Jour 3** | Sécurité : Audit + Corrections | 4-8h | `.env`, CORS, secrets |
| **Jour 4** | Tests Backend : pytest setup | 2-3h | `backend/tests/` |
| **Jour 5** | Tests Backend : Écriture + CI | 1-2h | `pytest.ini`, CI workflow |

**Livrables** :
- ✅ Données persistantes dans PostgreSQL
- ✅ Login/logout fonctionnels avec JWT
- ✅ Vulnérabilités sécurité corrigées
- ✅ 80%+ couverture tests backend
- ✅ CI/CD strict (pas de `continue-on-error`)

**Lien** : [📖 Guide détaillé Semaine 1](./guides-junior/SEMAINE-1-BLOCKERS.md)

---

### Semaine 2 : Lancement Beta (Priorité P1)

**Durée totale** : ~25-30h (4-6 jours ingénieur)
**Statut requis** : ✅ Obligatoire pour beta publique

| Jour | Tâches | Durée | Objectif |
|------|--------|-------|----------|
| **Jour 1** | Tests E2E en CI/CD | 4-6h | Automatiser Playwright |
| **Jour 2** | Git Flow activation | 2-3h | Créer `develop` + protection |
| **Jour 3** | Rate limiting | 4-6h | Protéger endpoints |
| **Jour 4** | Logging structuré | 3-4h | Debug production possible |
| **Jour 5** | Tests d'intégration | 6-8h | Frontend ↔ Backend |

**Livrables** :
- ✅ 37 tests E2E automatisés dans GitHub Actions
- ✅ Branch `develop` créée avec protection
- ✅ 100 req/min par IP, 1000/h par user
- ✅ Logs JSON avec `structlog`
- ✅ Flow complet Register → Login → Create Term testé

**Lien** : [📖 Guide détaillé Semaine 2](./guides-junior/SEMAINE-2-LAUNCH-READINESS.md)

---

### Semaines 3-4 : Production Hardening (Priorité P2)

**Durée totale** : ~60-80h (2-3 semaines ingénieur)
**Statut requis** : 🟡 Recommandé pour production robuste

| Période | Tâches | Durée | Objectif |
|---------|--------|-------|----------|
| **Jours 1-3** | OAuth GitHub + Google | 8-12h | Login social fonctionnel |
| **Jours 4-5** | Monitoring Sentry | 2-3h | Error tracking temps réel |
| **Jours 6-8** | Containerisation | 1-2 jours | Docker Compose complet |
| **Jours 9-10** | Tests charge Neo4j | 2-3 jours | Valider ADR-0001 |
| **Jours 11-12** | Métriques LLM | 1-2 jours | Mesurer -30% erreurs |
| **Jours 13-14** | Component tests | 3-4h | Réactiver 74 tests |

**Livrables** :
- ✅ OAuth fonctionnel (GitHub + Google)
- ✅ Sentry configuré (frontend + backend)
- ✅ App complète dans Docker
- ✅ Décision Neo4j vs PostgreSQL
- ✅ Métriques LLM instrumentées

**Lien** : [📖 Guide détaillé Semaines 3-4](./guides-junior/SEMAINES-3-4-PRODUCTION.md)

---

## 🎯 Critères de Validation

### Après Semaine 1 : Minimum Viable Product

Vous devez pouvoir :
1. Créer un compte utilisateur
2. Vous connecter
3. Créer un terme
4. Vous déconnecter
5. Vous reconnecter et voir vos termes sauvegardés
6. Redémarrer le serveur et retrouver vos données

**Tests à exécuter** :
```bash
# Tests unitaires backend
cd backend
pytest --cov=. --cov-report=term

# Vérifier couverture ≥80%
# Exemple de sortie attendue :
# TOTAL                           1234    123    90%

# Tests unitaires frontend
cd ..
npm run test:coverage

# Vérifier couverture ≥80%
```

### Après Semaine 2 : Beta Ready

En plus de la Semaine 1, vous devez avoir :
1. Tests E2E qui tournent automatiquement dans CI/CD
2. Branch `develop` avec règles de protection
3. API protégée contre les abus (rate limiting)
4. Logs structurés pour debug production
5. Tests d'intégration qui valident les flows complets

**Tests à exécuter** :
```bash
# Vérifier CI/CD
git push origin develop
# → GitHub Actions doit tourner et passer au vert

# Tester rate limiting
for i in {1..150}; do curl http://localhost:8000/api/terms; done
# → Devrait bloquer après 100 requêtes avec erreur 429

# Vérifier logs
tail -f backend/logs/app.log
# → Devrait afficher JSON structuré
```

### Après Semaines 3-4 : Production Ready

En plus des semaines précédentes :
1. OAuth fonctionnel (peut se connecter avec GitHub/Google)
2. Sentry capture les erreurs automatiquement
3. App complète tourne dans Docker
4. Décision Neo4j documentée avec benchmarks
5. Métriques LLM collectées

**Tests à exécuter** :
```bash
# Tester OAuth
# Ouvrir http://localhost:5173/login
# Cliquer "Login with GitHub"
# → Devrait rediriger et créer session

# Tester Sentry
# Déclencher une erreur volontaire
curl -X POST http://localhost:8000/api/debug/error
# → Erreur devrait apparaître dans dashboard Sentry

# Tester Docker
docker compose up
# → Frontend + Backend + Postgres + Neo4j doivent tous démarrer
```

---

## 🆘 Besoin d'Aide ?

### Ressources de Documentation

**Documentation Projet**
- `/home/user/lexikon/README.md` - Vue d'ensemble
- `/home/user/lexikon/QUICKSTART.md` - Démarrage rapide
- `/home/user/lexikon/docs/` - Documentation complète

**Documentation Technique**
- [FastAPI Docs](https://fastapi.tiangolo.com/) - Backend
- [SvelteKit Docs](https://kit.svelte.dev/) - Frontend
- [PostgreSQL Docs](https://www.postgresql.org/docs/) - Base de données
- [Playwright Docs](https://playwright.dev/) - Tests E2E

### Erreurs Fréquentes

Consultez **[Annexe B - Debugging](./guides-junior/ANNEXE-B-DEBUGGING.md)** pour :
- Erreurs de connexion à la base de données
- Erreurs d'import Python
- Erreurs de compilation TypeScript
- Erreurs Docker
- Erreurs Git

### Points de Contrôle

À la fin de chaque journée, posez-vous ces questions :

1. ✅ **Ai-je exécuté toutes les vérifications** listées dans le guide ?
2. ✅ **Est-ce que tous les tests passent** (`npm test` et `pytest`) ?
3. ✅ **Ai-je commité mon code** avec un message clair ?
4. ✅ **Est-ce que je peux expliquer** ce que j'ai fait à quelqu'un ?
5. ✅ **Ai-je documenté** les problèmes rencontrés et solutions ?

Si vous répondez "Non" à l'une de ces questions, **ne passez pas au jour suivant**. Résolvez d'abord le problème.

---

## 📝 Journal de Bord (Template)

Créez un fichier `JOURNAL-SEMAINE-X.md` pour noter votre progression :

```markdown
# Journal de Bord - Semaine X

## Jour 1 - [Date]

### Tâches Prévues
- [ ] Tâche 1
- [ ] Tâche 2

### Tâches Réalisées
- [x] Tâche 1 (2h) - RAS
- [~] Tâche 2 (3h) - Bloqué sur erreur PostgreSQL

### Problèmes Rencontrés
- Erreur "connection refused" lors de `alembic upgrade head`
- Solution : Redémarrer Docker Compose

### Notes
- La migration `001_initial_schema` crée 5 tables
- JWT token expiry = 1h (configurable dans jwt.py)

### Pour Demain
- Finir Tâche 2
- Commencer Tâche 3
```

---

## 🎓 Apprentissage

### Compétences que Vous Allez Acquérir

**Semaine 1**
- Migrations de base de données avec Alembic
- Authentification JWT (tokens, middleware)
- Sécurité web (CORS, secrets, hashing)
- Tests unitaires Python avec pytest

**Semaine 2**
- CI/CD avec GitHub Actions
- Git Flow (branching strategy)
- Rate limiting et protection API
- Logging structuré
- Tests d'intégration

**Semaines 3-4**
- OAuth 2.0 (GitHub, Google)
- Monitoring et error tracking (Sentry)
- Containerisation Docker
- Tests de charge et benchmarking
- Métriques et instrumentation

### Concepts Clés à Comprendre

**Avant la Semaine 1**
- [ ] Qu'est-ce qu'une migration de base de données ?
- [ ] Comment fonctionne JWT ?
- [ ] Pourquoi CORS est important ?
- [ ] Différence entre tests unitaires et intégration ?

**Avant la Semaine 2**
- [ ] Qu'est-ce que CI/CD ?
- [ ] Pourquoi Git Flow ?
- [ ] Qu'est-ce que le rate limiting ?
- [ ] Pourquoi des logs structurés ?

**Avant les Semaines 3-4**
- [ ] Comment fonctionne OAuth 2.0 ?
- [ ] Qu'est-ce que Sentry fait ?
- [ ] Avantages de Docker ?
- [ ] Comment tester la performance ?

---

## 🚦 Feu Tricolore de Progression

Utilisez ce système pour évaluer votre progression :

### 🟢 Vert : Tout va bien
- Toutes les vérifications passent
- Tests au vert
- Vous comprenez ce que vous avez fait
- **Action** : Continuez au rythme actuel

### 🟡 Orange : Ralentir
- Certaines vérifications échouent
- Vous ne comprenez pas complètement
- Vous êtes bloqué >30 minutes
- **Action** : Relisez la documentation, consultez l'Annexe B

### 🔴 Rouge : Arrêt
- Tests cassés depuis >2h
- Vous ne comprenez pas du tout
- Vous avez peur de casser quelque chose
- **Action** : Demandez de l'aide, ne forcez pas

---

## ✅ Checklist Finale

Avant de dire "J'ai fini la Semaine X", vérifiez :

### Semaine 1 - Déblocage Critique
- [ ] PostgreSQL tourne et contient des données
- [ ] `alembic history` montre les migrations appliquées
- [ ] Login/logout fonctionnent avec de vrais JWT tokens
- [ ] Fichier `.env` a un JWT_SECRET aléatoire
- [ ] `pytest --cov` montre ≥80% couverture
- [ ] CI backend passe au vert sans `continue-on-error`
- [ ] Redémarrage serveur conserve les données

### Semaine 2 - Lancement Beta
- [ ] `npm run test:e2e` passe localement
- [ ] GitHub Actions exécute tests E2E automatiquement
- [ ] Branch `develop` existe avec protection activée
- [ ] Rate limiting bloque après 100 req/min
- [ ] Logs sont en format JSON structuré
- [ ] Tests d'intégration couvrent Register → Login → Create Term

### Semaines 3-4 - Production
- [ ] Login avec GitHub fonctionne
- [ ] Login avec Google fonctionne
- [ ] Sentry dashboard montre les erreurs
- [ ] `docker compose up` démarre toute la stack
- [ ] Benchmarks Neo4j vs PostgreSQL documentés
- [ ] Dashboard métriques LLM affiche des données

---

## 🎯 Prochaines Étapes

Vous êtes prêt à commencer ! Voici l'ordre recommandé :

1. **Vérifiez votre environnement** (section "Configuration de l'Environnement")
2. **Lisez le guide Semaine 1** entièrement une fois avant de commencer
3. **Créez votre journal de bord** pour suivre votre progression
4. **Commencez Jour 1** en suivant chaque étape
5. **Ne sautez pas les vérifications** ✅
6. **Demandez de l'aide** si vous êtes bloqué >30 minutes

**Bon courage ! 🚀**

---

## 📚 Index des Documents

| Document | Description | Quand le lire |
|----------|-------------|---------------|
| **Ce fichier** | Vue d'ensemble et setup | Maintenant ✅ |
| [Semaine 1](./guides-junior/SEMAINE-1-BLOCKERS.md) | Déblocage critique (PostgreSQL, JWT, Sécurité, Tests) | Avant de commencer |
| [Semaine 2](./guides-junior/SEMAINE-2-LAUNCH-READINESS.md) | Lancement beta (E2E, Git Flow, Rate limiting, Logging) | Après Semaine 1 |
| [Semaines 3-4](./guides-junior/SEMAINES-3-4-PRODUCTION.md) | Production (OAuth, Sentry, Docker, Neo4j) | Après Semaine 2 |
| [Annexe A - Git](./guides-junior/ANNEXE-A-GIT.md) | Commandes Git et résolution de conflits | Quand besoin |
| [Annexe B - Debugging](./guides-junior/ANNEXE-B-DEBUGGING.md) | Erreurs fréquentes et solutions | Quand bloqué |
| [Annexe C - Tests](./guides-junior/ANNEXE-C-TESTS.md) | Écrire et exécuter des tests | Jour 4-5 Semaine 1 |

---

**Version** : 1.0
**Dernière mise à jour** : 2025-11-17
**Auteur** : Analyse Multi-Rôle Lexikon
**Licence** : Interne au projet
