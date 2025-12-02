# Semaine 2 - Lancement Beta
## Guide Détaillé pour Développeur Junior

**Durée** : 4-6 jours (25-30h)
**Priorité** : 🟡 P1 - IMPORTANT
**Objectif** : Préparer le projet pour un lancement beta public

---

## 📋 Vue d'Ensemble Semaine 2

### Objectifs

| Jour | Tâche Principale | Durée | Livrable |
|------|------------------|-------|----------|
| **Jour 1** | Tests E2E en CI/CD | 4-6h | Playwright automatisé ✅ |
| **Jour 2** | Git Flow activation | 2-3h | Branch `develop` + protection ✅ |
| **Jour 3** | Rate limiting | 4-6h | Protection endpoints ✅ |
| **Jour 4** | Logging structuré | 3-4h | Logs JSON ✅ |
| **Jour 5** | Tests d'intégration | 6-8h | Flow complet testé ✅ |

---

## 📅 JOUR 1 - Tests E2E en CI/CD

### 🎯 Objectif
Automatiser les 37 tests Playwright dans GitHub Actions

### Étape 1.1 : Comprendre les Tests E2E Existants (60 min)

**Lister les tests**
```bash
cd /home/user/lexikon
ls -la e2e/
```

✅ **Fichiers attendus** :
- `auth.spec.ts` (18 tests d'authentification)
- `user-journey.spec.ts` (19 tests de parcours utilisateur)
- `smoke.spec.ts` (tests de base)

**Lire un test exemple**
```bash
cat e2e/auth.spec.ts | head -50
```

💡 **Structure d'un test Playwright** :
```typescript
test('user can register', async ({ page }) => {
  // 1. Naviguer vers la page
  await page.goto('http://localhost:5173/register');

  // 2. Remplir le formulaire
  await page.fill('[name="email"]', 'test@example.com');
  await page.fill('[name="password"]', 'TestPass123');

  // 3. Soumettre
  await page.click('button[type="submit"]');

  // 4. Vérifier le résultat
  await expect(page).toHaveURL(/profile/);
});
```

### Étape 1.2 : Exécuter les Tests Localement (30 min)

**Installer Playwright browsers** (si pas déjà fait)
```bash
npx playwright install chromium
```

**Démarrer backend + frontend**

Terminal 1 (Backend) :
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

Terminal 2 (Frontend) :
```bash
npm run dev
```

**Exécuter les tests**

Terminal 3 :
```bash
npm run test:e2e
```

✅ **Sortie attendue** :
```
Running 37 tests using 3 workers

  ✓ auth.spec.ts:10:1 › user can register (2s)
  ✓ auth.spec.ts:25:1 › user can login (1s)
  ...
  37 passed (45s)
```

🐛 **Si des tests échouent** :
- Vérifier que backend tourne sur port 8000
- Vérifier que frontend tourne sur port 5173
- Vérifier que PostgreSQL est accessible

### Étape 1.3 : Créer une DB de Test pour CI (120 min)

**Problème** : CI/CD n'a pas de PostgreSQL par défaut

**Solution** : Ajouter un service PostgreSQL dans GitHub Actions

**Modifier `.github/workflows/test-and-lint.yml`**
```yaml
name: Frontend - Test & Lint

on:
  push:
    branches: [develop, master]
  pull_request:
    branches: [develop, master]

jobs:
  # Job existant pour tests unitaires
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      - run: npm ci
      - run: npm run check
      - run: npm run lint
      - run: npm run test:coverage

  # ✅ NOUVEAU JOB : Tests E2E
  e2e-tests:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: lexikon
          POSTGRES_PASSWORD: test-secret
          POSTGRES_DB: lexikon
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          cache: 'pip'

      - name: Install frontend dependencies
        run: npm ci

      - name: Install backend dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Run database migrations
        env:
          DATABASE_URL: postgresql://lexikon:test-secret@localhost:5432/lexikon
          JWT_SECRET: test-jwt-secret-for-ci
        run: |
          cd backend
          alembic upgrade head

      - name: Start backend
        env:
          DATABASE_URL: postgresql://lexikon:test-secret@localhost:5432/lexikon
          JWT_SECRET: test-jwt-secret-for-ci
          ENVIRONMENT: test
        run: |
          cd backend
          uvicorn main:app --host 0.0.0.0 --port 8000 &
          sleep 5

      - name: Install Playwright
        run: npx playwright install chromium --with-deps

      - name: Build frontend
        run: npm run build

      - name: Start frontend
        run: |
          npm run preview -- --port 5173 --host &
          sleep 5

      - name: Run E2E tests
        run: npm run test:e2e -- --project=chromium

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/
```

### Étape 1.4 : Tester le Workflow CI (30 min)

**Commit et push**
```bash
git add .github/workflows/test-and-lint.yml
git commit -m "ci: Add E2E tests to GitHub Actions"
git push origin claude/multi-role-quality-analysis-01WExLnvskU1bVjMd1AabmbB
```

**Vérifier dans GitHub** :
1. Aller sur https://github.com/ccolleatte/lexikon/actions
2. Trouver le workflow qui vient de se lancer
3. Regarder les logs en temps réel

✅ **Succès** : Toutes les étapes en vert
🐛 **Échec** : Lire les logs, corriger, re-push

🎉 **Checkpoint Jour 1** : Tests E2E automatisés ! ✅

---

## 📅 JOUR 2 - Git Flow Activation

### 🎯 Objectif
Créer la branche `develop` et configurer la protection des branches

### Étape 2.1 : Créer la Branche `develop` (15 min)

**Depuis `master` (ou main)**
```bash
cd /home/user/lexikon

# Vérifier la branche actuelle
git branch

# Créer develop depuis master
git checkout -b develop

# Pousser vers le remote
git push -u origin develop
```

✅ **Vérification** :
```bash
git branch -a
# Doit afficher :
# * develop
#   master
#   remotes/origin/develop
#   remotes/origin/master
```

### Étape 2.2 : Configurer la Protection des Branches (60 min)

**Suivre le guide** : `/home/user/lexikon/_docs/IMPLEMENTATION_CHECKLIST.md`

**Résumé des étapes (à faire sur GitHub.com)** :

1. **Aller sur GitHub** : `https://github.com/ccolleatte/lexikon/settings/branches`

2. **Protéger `master`** :
   - Cliquer "Add branch protection rule"
   - Branch name pattern : `master`
   - ✅ Require pull request reviews before merging (2 approvals)
   - ✅ Require status checks to pass (sélectionner : unit-tests, e2e-tests)
   - ✅ Require branches to be up to date
   - ✅ Dismiss stale reviews
   - ❌ Allow force pushes (décocher)
   - ❌ Allow deletions (décocher)
   - Cliquer "Create"

3. **Protéger `develop`** :
   - Même chose mais 1 approval au lieu de 2
   - ✅ Automatically delete head branches

### Étape 2.3 : Créer le Fichier CODEOWNERS (30 min)

**Créer `.github/CODEOWNERS`**
```bash
nano .github/CODEOWNERS
```

**Contenu** :
```
# Code owners pour Lexikon
# Ces personnes seront automatiquement demandées pour review

# Global owners
* @ccolleatte

# Backend
/backend/ @ccolleatte

# Frontend
/src/ @ccolleatte

# Documentation
/docs/ @ccolleatte

# CI/CD
/.github/ @ccolleatte
```

⚠️ Remplacer `@ccolleatte` par votre username GitHub réel

**Commit**
```bash
git add .github/CODEOWNERS
git commit -m "chore: Add CODEOWNERS file"
git push origin develop
```

### Étape 2.4 : Tester le Workflow Git Flow (60 min)

**Créer une feature branch**
```bash
# Depuis develop
git checkout develop
git pull origin develop

# Créer une branche de feature
git checkout -b feature/test-git-flow

# Faire un petit changement
echo "# Git Flow Test" >> docs/GIT_FLOW_TEST.md

# Commit
git add docs/GIT_FLOW_TEST.md
git commit -m "feat: Test Git Flow process"

# Push
git push -u origin feature/test-git-flow
```

**Créer une Pull Request**
```bash
# Utiliser gh CLI si disponible
gh pr create --base develop --title "Test Git Flow" --body "Testing the Git Flow setup"

# OU manuellement sur GitHub.com
```

**Vérifier** :
- [ ] CI/CD se lance automatiquement
- [ ] Status checks requis s'affichent
- [ ] Merge bloqué tant que checks ne passent pas
- [ ] Review requise (1 personne)

🎉 **Checkpoint Jour 2** : Git Flow activé ! ✅

---

## 📅 JOUR 3 - Rate Limiting

### 🎯 Objectif
Protéger l'API contre les abus (max 100 req/min par IP)

### Étape 3.1 : Installer slowapi (15 min)

```bash
cd /home/user/lexikon/backend
source venv/bin/activate
pip install slowapi
pip freeze > requirements.txt
```

### Étape 3.2 : Configurer slowapi (60 min)

**Modifier `backend/main.py`**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Créer le limiter
limiter = Limiter(key_func=get_remote_address)

# Configurer l'app
app = FastAPI(
    title="Lexikon API",
    version="0.2.0"
)

# Ajouter le limiter à l'app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Monter les routers (code existant)
app.include_router(auth_router)
```

### Étape 3.3 : Appliquer les Limites (90 min)

**Rate limits recommandés** :

| Endpoint | Limite | Raison |
|----------|--------|--------|
| `/api/auth/register` | 5/hour | Éviter spam de comptes |
| `/api/auth/login` | 10/hour | Éviter brute force |
| `/api/terms` (POST) | 100/hour | Usage normal |
| `/api/terms` (GET) | 1000/hour | Lecture intensive OK |

**Modifier `backend/api/auth.py`**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/register")
@limiter.limit("5/hour")  # ✅ Max 5 registrations/hour par IP
async def register(request: Request, data: RegisterRequest, db: Session = Depends(get_db)):
    # ... (code existant)
```

💡 **Ajouter `Request` aux paramètres** :
```python
from fastapi import Request  # Ajouter à l'import

@router.post("/login")
@limiter.limit("10/hour")
async def login(request: Request, data: LoginRequest, db: Session = Depends(get_db)):
    # ... (code existant)
```

### Étape 3.4 : Tester le Rate Limiting (60 min)

**Test 1 : Dépassement de limite**
```bash
# Envoyer 11 requêtes rapidement (devrait bloquer à la 11e)
for i in {1..11}; do
  echo "Requête $i:"
  curl -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"wrong"}' \
    --silent | jq '.detail' 2>/dev/null || echo "Rate limited"
  sleep 1
done
```

✅ **Résultat attendu** :
- Requêtes 1-10 : "Invalid email or password" (erreur 401)
- Requête 11 : "Rate limit exceeded" (erreur 429)

**Test 2 : Vérifier les headers**
```bash
curl -v -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"wrong"}' 2>&1 | grep -i "x-ratelimit"
```

✅ **Headers attendus** :
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 9
X-RateLimit-Reset: 1234567890
```

🎉 **Checkpoint Jour 3** : Rate limiting fonctionnel ! ✅

---

## 📅 JOUR 4 - Logging Structuré

### 🎯 Objectif
Implémenter des logs JSON pour faciliter le debug production

### Étape 4.1 : Installer structlog (15 min)

```bash
cd /home/user/lexikon/backend
source venv/bin/activate
pip install structlog python-json-logger
pip freeze > requirements.txt
```

### Étape 4.2 : Configurer structlog (90 min)

**Créer `backend/logger.py`**
```python
import structlog
import logging
import sys

def setup_logging():
    """Configure structlog pour logging JSON"""

    # Configuration de base
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )

    # Configuration structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()  # ✅ Output JSON
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

def get_logger(name: str):
    """Récupérer un logger"""
    return structlog.get_logger(name)
```

**Importer dans `backend/main.py`**
```python
from logger import setup_logging, get_logger

# Après app = FastAPI()
setup_logging()
logger = get_logger("lexikon.api")

# Exemple de log
logger.info("application_startup", version="0.2.0")
```

### Étape 4.3 : Ajouter des Logs dans les Endpoints (120 min)

**Modifier `backend/api/auth.py`**
```python
from logger import get_logger

logger = get_logger("lexikon.auth")

@router.post("/register")
@limiter.limit("5/hour")
async def register(request: Request, data: RegisterRequest, db: Session = Depends(get_db)):
    logger.info("register_attempt", email=data.email)

    # ... (vérifications)

    try:
        # ... (création user)
        logger.info("register_success", user_id=new_user.id, email=new_user.email)
        return { ... }
    except Exception as e:
        logger.error("register_failed", email=data.email, error=str(e))
        raise
```

**Logs recommandés** :

| Événement | Niveau | Champs |
|-----------|--------|--------|
| Requête API | INFO | method, path, ip, user_id |
| Auth success | INFO | user_id, email |
| Auth failure | WARNING | email, reason |
| Erreur 500 | ERROR | error, traceback |
| Création resource | INFO | resource_type, resource_id |

### Étape 4.4 : Tester les Logs (60 min)

**Démarrer le backend et regarder les logs**
```bash
cd /home/user/lexikon/backend
source venv/bin/activate
uvicorn main:app --reload | jq
```

💡 **`| jq` formate le JSON pour le rendre lisible**

**Faire une requête**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"logger@example.com","password":"LogTest123","full_name":"Logger Test"}'
```

✅ **Log attendu** (dans le terminal uvicorn) :
```json
{
  "event": "register_attempt",
  "email": "logger@example.com",
  "level": "info",
  "timestamp": "2025-11-17T10:30:45.123Z",
  "logger": "lexikon.auth"
}
{
  "event": "register_success",
  "user_id": 10,
  "email": "logger@example.com",
  "level": "info",
  "timestamp": "2025-11-17T10:30:45.456Z"
}
```

🎉 **Checkpoint Jour 4** : Logging structuré fonctionnel ! ✅

---

## 📅 JOUR 5 - Tests d'Intégration

### 🎯 Objectif
Tester le flow complet : Register → Login → Create Term → Logout

### Étape 5.1 : Créer les Tests d'Intégration (240 min)

**Créer `backend/tests/test_integration.py`**
```python
import pytest
from fastapi import status


class TestUserJourney:
    """Tests du parcours utilisateur complet"""

    def test_complete_user_journey(self, client):
        """Test : Parcours complet Register → Login → Create Term"""

        # 1. REGISTER
        register_response = client.post(
            "/api/auth/register",
            json={
                "email": "journey@example.com",
                "password": "JourneyTest123",
                "full_name": "Journey User"
            }
        )

        assert register_response.status_code == status.HTTP_200_OK
        register_data = register_response.json()
        assert "access_token" in register_data

        access_token = register_data["access_token"]
        user_id = register_data["user"]["id"]

        # 2. LOGIN (vérifier qu'on peut se reconnecter)
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": "journey@example.com",
                "password": "JourneyTest123"
            }
        )

        assert login_response.status_code == status.HTTP_200_OK
        login_data = login_response.json()
        assert login_data["user"]["id"] == user_id

        # 3. CREATE TERM (avec le token)
        term_response = client.post(
            "/api/terms",
            json={
                "term": "Integration Test",
                "definition": "A test that validates the full flow",
                "domain": "Testing",
                "level": "intermediate"
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert term_response.status_code == status.HTTP_200_OK
        term_data = term_response.json()
        assert term_data["term"] == "Integration Test"

        term_id = term_data["term_id"]

        # 4. GET TERM (vérifier qu'il existe)
        get_response = client.get(
            f"/api/terms/{term_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert get_response.status_code == status.HTTP_200_OK
        retrieved_term = get_response.json()
        assert retrieved_term["term"] == "Integration Test"
        assert retrieved_term["user_id"] == user_id

    def test_unauthorized_access(self, client):
        """Test : Accès sans token échoue"""

        # Tenter de créer un terme sans token
        response = client.post(
            "/api/terms",
            json={
                "term": "Unauthorized",
                "definition": "Should fail",
                "domain": "Test",
                "level": "beginner"
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_expired_token(self, client, test_user):
        """Test : Token expiré est rejeté"""
        from auth.jwt import create_access_token
        from datetime import timedelta

        # Créer un token déjà expiré
        expired_token = create_access_token(
            {"user_id": test_user.id, "email": test_user.email},
            expires_delta=timedelta(seconds=-60)  # Expiré il y a 1 minute
        )

        response = client.post(
            "/api/terms",
            json={"term": "Test", "definition": "Test", "domain": "Test", "level": "beginner"},
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
```

### Étape 5.2 : Exécuter les Tests (30 min)

```bash
cd /home/user/lexikon/backend
pytest tests/test_integration.py -v
```

✅ **Sortie attendue** :
```
tests/test_integration.py::TestUserJourney::test_complete_user_journey PASSED
tests/test_integration.py::TestUserJourney::test_unauthorized_access PASSED
tests/test_integration.py::TestUserJourney::test_expired_token PASSED

========== 3 passed in 3.45s ==========
```

🎉 **Checkpoint Jour 5** : Tests d'intégration passent ! ✅

---

## ✅ Checklist Finale Semaine 2

Avant de passer à la Semaine 3, vérifiez :

- [ ] **Tests E2E** : 37 tests automatisés dans GitHub Actions
- [ ] **Git Flow** : Branch `develop` créée avec protection
- [ ] **Rate Limiting** : 10/hour sur `/login`, 5/hour sur `/register`
- [ ] **Logging** : Logs JSON structurés avec structlog
- [ ] **Tests d'intégration** : Flow complet Register → Login → Create Term → Get Term testé

**Test de validation final** :
```bash
# 1. Tests E2E locaux
npm run test:e2e

# 2. Tests backend avec intégration
cd backend
pytest --cov=. --cov-report=term

# 3. Vérifier Git Flow
git checkout develop
git pull origin develop

# 4. Vérifier CI/CD
git push origin develop
# → GitHub Actions doit passer au vert
```

Si tout passe ✅ → **Bravo ! Prêt pour beta launch** 🚀

---

**Prochaine étape** : [Semaines 3-4 - Production Hardening](./SEMAINES-3-4-PRODUCTION.md)
