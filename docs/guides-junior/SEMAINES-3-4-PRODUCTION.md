# Semaines 3-4 - Production Hardening
## Guide Condensé pour Développeur Junior

**Durée** : 2-3 semaines (60-80h)
**Priorité** : 🟢 P2 - RECOMMANDÉ
**Objectif** : Renforcer la robustesse pour production

---

## 📋 Vue d'Ensemble

| Tâches | Durée | Priorité |
|--------|-------|----------|
| OAuth GitHub + Google | 8-12h | P2 |
| Monitoring Sentry | 2-3h | P2 |
| Containerisation Docker | 1-2 jours | P2 |
| Tests charge Neo4j | 2-3 jours | P2 |
| Métriques LLM | 1-2 jours | P2 |

---

## 🔐 OAuth Implementation (Jours 1-3)

### Objectif
Permettre login avec GitHub et Google

### GitHub OAuth Setup

**1. Créer une OAuth App sur GitHub**
- Aller sur https://github.com/settings/developers
- "New OAuth App"
- Name: `Lexikon Development`
- Homepage URL: `http://localhost:5173`
- Callback URL: `http://localhost:5173/oauth/callback/github`
- Copier Client ID et Client Secret

**2. Configurer backend/.env**
```env
GITHUB_CLIENT_ID=votre_client_id
GITHUB_CLIENT_SECRET=votre_client_secret
```

**3. Implémenter dans backend/auth/oauth.py**
```python
from authlib.integrations.starlette_client import OAuth

oauth = OAuth()

oauth.register(
    name='github',
    client_id=os.getenv('GITHUB_CLIENT_ID'),
    client_secret=os.getenv('GITHUB_CLIENT_SECRET'),
    authorize_url='https://github.com/login/oauth/authorize',
    access_token_url='https://github.com/login/oauth/access_token',
    client_kwargs={'scope': 'user:email'},
)

@router.get("/oauth/github")
async def github_login(request: Request):
    redirect_uri = 'http://localhost:5173/oauth/callback/github'
    return await oauth.github.authorize_redirect(request, redirect_uri)

@router.get("/oauth/callback/github")
async def github_callback(request: Request, db: Session = Depends(get_db)):
    token = await oauth.github.authorize_access_token(request)
    user_data = await oauth.github.get('user', token=token)

    # Créer ou récupérer l'utilisateur
    email = user_data.get('email')
    existing_user = db.query(User).filter(User.email == email).first()

    if not existing_user:
        new_user = User(
            email=email,
            username=user_data.get('login'),
            full_name=user_data.get('name'),
            hashed_password="oauth-github"  # Pas de mot de passe pour OAuth
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        user = new_user
    else:
        user = existing_user

    # Créer JWT token
    access_token = create_access_token({"user_id": user.id, "email": user.email})
    refresh_token = create_refresh_token({"user_id": user.id, "email": user.email})

    # Rediriger vers frontend avec token
    return RedirectResponse(
        url=f"http://localhost:5173/oauth/success?token={access_token}"
    )
```

### Google OAuth (similaire)

Même approche mais avec :
- Google Cloud Console : https://console.cloud.google.com/
- Créer un projet → APIs & Services → Credentials → OAuth 2.0 Client ID
- Scopes : `openid email profile`

**Test** :
1. Cliquer sur "Login with GitHub" dans le frontend
2. Autoriser l'app GitHub
3. Être redirigé vers le profil avec session active

---

## 📊 Monitoring Sentry (Jours 4-5)

### Objectif
Capturer les erreurs en production

### Setup Sentry

**1. Créer un compte sur Sentry.io**
- https://sentry.io/signup/
- Créer un projet "Lexikon Backend" (Python/FastAPI)
- Créer un projet "Lexikon Frontend" (JavaScript/SvelteKit)
- Copier les DSN (Data Source Name)

**2. Backend Integration**
```bash
cd backend
pip install sentry-sdk[fastapi]
pip freeze > requirements.txt
```

**backend/main.py** :
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

# Initialiser Sentry
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN_BACKEND"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,  # 10% des transactions
    environment=os.getenv("ENVIRONMENT", "development"),
)

# Tester avec un endpoint debug
@app.get("/debug/error")
async def trigger_error():
    1 / 0  # Erreur volontaire pour tester Sentry
```

**3. Frontend Integration**
```bash
npm install @sentry/sveltekit
```

**src/hooks.client.ts** :
```typescript
import * as Sentry from '@sentry/sveltekit';

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  integrations: [
    new Sentry.BrowserTracing(),
    new Sentry.Replay()
  ],
  tracesSampleRate: 0.1,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
});
```

**Test** :
```bash
# Déclencher une erreur
curl http://localhost:8000/debug/error

# Vérifier dans Sentry dashboard
# → Erreur doit apparaître avec traceback complet
```

---

## 🐳 Containerisation (Jours 6-8)

### Objectif
Tout l'environnement dans Docker

### Backend Dockerfile

**backend/Dockerfile** :
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Dépendances système
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code de l'app
COPY . .

# Migrations au démarrage
CMD alembic upgrade head && \
    uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend Dockerfile

**Dockerfile** (racine) :
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:18-alpine

WORKDIR /app

COPY --from=builder /app/build ./build
COPY --from=builder /app/package.json ./

RUN npm ci --production

CMD ["node", "build"]
```

### Docker Compose Complet

**docker-compose.yml** (décommenter les services commentés) :
```yaml
version: '3.8'

services:
  postgres:
    # ... (existant)

  neo4j:
    # ... (existant)

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://lexikon:dev-secret@postgres:5432/lexikon
      NEO4J_URI: bolt://neo4j:7687
      JWT_SECRET: ${JWT_SECRET}
    depends_on:
      postgres:
        condition: service_healthy
      neo4j:
        condition: service_healthy
    volumes:
      - ./backend:/app

  frontend:
    build: .
    ports:
      - "3000:3000"
    environment:
      VITE_API_URL: http://backend:8000
    depends_on:
      - backend
```

**Test** :
```bash
# Build
docker compose build

# Démarrer
docker compose up

# Vérifier
curl http://localhost:8000/
curl http://localhost:3000/
```

---

## 🧪 Tests de Charge Neo4j (Jours 9-10)

### Objectif
Valider ADR-0001 : Neo4j vs PostgreSQL

### Setup Locust

**Installer Locust**
```bash
pip install locust
```

**Créer tests/load/locustfile.py** :
```python
from locust import HttpUser, task, between

class LexikonUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # Login
        response = self.client.post("/api/auth/login", json={
            "email": "load@test.com",
            "password": "LoadTest123"
        })
        self.token = response.json()["access_token"]

    @task(3)
    def create_term(self):
        self.client.post("/api/terms", json={
            "term": f"Term-{self.random_id()}",
            "definition": "Load test definition",
            "domain": "Testing",
            "level": "beginner"
        }, headers={"Authorization": f"Bearer {self.token}"})

    @task(7)
    def get_terms(self):
        self.client.get("/api/terms", headers={"Authorization": f"Bearer {self.token}"})

    def random_id(self):
        import random
        return random.randint(1, 100000)
```

**Exécuter** :
```bash
# Démarrer backend
cd backend && uvicorn main:app

# Dans un autre terminal
locust -f tests/load/locustfile.py

# Ouvrir http://localhost:8089
# - Number of users: 100
# - Spawn rate: 10/s
# - Host: http://localhost:8000

# Lancer et observer :
# - Requêtes/sec
# - Temps de réponse moyen
# - Erreurs
```

### Benchmarking Neo4j vs PostgreSQL

**Scénario de test** :
1. Générer 5000 termes avec relations
2. Requête : "Trouver tous les termes liés à 'Intelligence Artificielle' sur 3 niveaux"
3. Mesurer temps de réponse

**PostgreSQL (WITH RECURSIVE)** :
```sql
WITH RECURSIVE term_tree AS (
  SELECT id, term, 1 as depth
  FROM terms
  WHERE term = 'Intelligence Artificielle'

  UNION ALL

  SELECT t.id, t.term, tt.depth + 1
  FROM terms t
  JOIN relationships r ON t.id = r.target_id
  JOIN term_tree tt ON r.source_id = tt.id
  WHERE tt.depth < 3
)
SELECT * FROM term_tree;
```

**Neo4j (MATCH ... DEPTH)** :
```cypher
MATCH path = (start:Term {name: "Intelligence Artificielle"})-[:RELATED_TO*1..3]->(related)
RETURN related.name, length(path)
```

**Décision** :
- Si Neo4j <50ms et PostgreSQL >200ms → Garder Neo4j
- Si Neo4j ~100ms et PostgreSQL ~120ms → Migrer vers PostgreSQL (simplifier stack)

---

## 📈 Métriques LLM (Jours 11-12)

### Objectif
Mesurer l'impact sur la qualité LLM (-30% erreurs sémantiques)

### Setup Prometheus + Grafana

**docker-compose.yml** (ajouter) :
```yaml
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
```

### Instrumenter le Code

**backend/main.py** :
```python
from prometheus_client import Counter, Histogram, generate_latest

# Métriques
llm_requests = Counter('llm_requests_total', 'Total LLM requests', ['model', 'endpoint'])
llm_errors = Counter('llm_semantic_errors', 'Semantic errors detected', ['type'])
llm_latency = Histogram('llm_response_time', 'LLM response time')

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")

# Utiliser dans les endpoints
@llm_latency.time()
async def call_llm(prompt: str):
    llm_requests.labels(model="gpt-4", endpoint="validate_term").inc()
    # ... appel LLM
    if semantic_error_detected:
        llm_errors.labels(type="ambiguous_definition").inc()
```

### Dashboard Grafana

1. Ouvrir http://localhost:3001
2. Login: admin / admin
3. Add data source → Prometheus (http://prometheus:9090)
4. Create dashboard :
   - Graphe : `rate(llm_requests_total[5m])`
   - Graphe : `rate(llm_semantic_errors[1h])`
   - Calcul : `(llm_semantic_errors / llm_requests_total) * 100` → % erreurs

---

## ✅ Checklist Finale Semaines 3-4

- [ ] OAuth GitHub fonctionnel
- [ ] OAuth Google fonctionnel
- [ ] Sentry capture les erreurs
- [ ] Docker Compose démarre toute la stack
- [ ] Benchmarks Neo4j vs PostgreSQL documentés
- [ ] Métriques LLM collectées dans Grafana

**Test final** :
```bash
# 1. Docker Compose complet
docker compose up

# 2. Login avec GitHub
# Ouvrir http://localhost:3000/login → Cliquer GitHub → Succès

# 3. Déclencher erreur Sentry
curl http://localhost:8000/debug/error
# → Vérifier dans Sentry dashboard

# 4. Vérifier métriques
curl http://localhost:8000/metrics
# → Devrait afficher métriques Prometheus
```

🎉 **Production Ready !** ✅

---

**Annexes** : [Debugging Guide](./ANNEXE-B-DEBUGGING.md)
