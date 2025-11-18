# Annexe B - Guide de Debugging
## Erreurs Fréquentes et Solutions

---

## 🐛 Erreurs de Développement

### 1. PostgreSQL

#### Erreur : `connection refused`
```
psycopg2.OperationalError: could not connect to server: Connection refused
```

**Causes** :
- PostgreSQL n'est pas démarré
- Port 5432 déjà utilisé

**Solutions** :
```bash
# Vérifier que Docker tourne
docker compose ps
# → postgres doit être "Up (healthy)"

# Si pas démarré
docker compose up -d postgres

# Si port conflit
docker compose down
sudo lsof -i :5432  # Trouver le processus
# Tuer le processus ou changer le port dans docker-compose.yml
```

#### Erreur : `relation "users" does not exist`
```
sqlalchemy.exc.ProgrammingError: relation "users" does not exist
```

**Cause** : Migrations Alembic pas exécutées

**Solution** :
```bash
cd backend
alembic upgrade head

# Vérifier
docker compose exec postgres psql -U lexikon -d lexikon -c "\dt"
# → Devrait afficher : users, terms, relationships
```

---

### 2. JWT / Authentication

#### Erreur : `Invalid token`
```json
{"detail": "Invalid token"}
```

**Causes** :
- Token expiré (>1h pour access token)
- JWT_SECRET changé entre création et vérification
- Token corrompu

**Solutions** :
```bash
# 1. Vérifier JWT_SECRET cohérent
cat backend/.env | grep JWT_SECRET
# Doit être le même que celui utilisé au démarrage du serveur

# 2. Créer un nouveau token (login à nouveau)
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123"}'

# 3. Vérifier expiration du token
# Décoder le token sur https://jwt.io/
# Regarder le champ "exp" (timestamp Unix)
# Si < maintenant → expiré
```

#### Erreur : `Not authenticated`
```json
{"detail": "Not authenticated"}
```

**Cause** : Header `Authorization` manquant ou mal formaté

**Solution** :
```bash
# ❌ Mauvais
curl -X POST http://localhost:8000/api/terms \
  -H "Authorization: TOKEN_ICI"

# ✅ Bon
curl -X POST http://localhost:8000/api/terms \
  -H "Authorization: Bearer TOKEN_ICI"
#                    ^^^^^^^ Mot-clé "Bearer" obligatoire
```

---

### 3. Frontend / SvelteKit

#### Erreur : `Cannot find module '@sveltejs/kit'`
```
Error: Cannot find module '@sveltejs/kit'
```

**Cause** : `node_modules` pas installés

**Solution** :
```bash
npm install
# Si erreur persiste :
rm -rf node_modules package-lock.json
npm install
```

#### Erreur : `Failed to fetch` (dans le navigateur)
```
TypeError: Failed to fetch
```

**Causes** :
- Backend pas démarré
- CORS bloqué
- URL incorrecte

**Solutions** :
```bash
# 1. Vérifier que backend tourne
curl http://localhost:8000/
# → Doit retourner {"message": "Lexikon API v0.2.0"}

# 2. Vérifier CORS dans backend/main.py
# allow_origins doit inclure http://localhost:5173

# 3. Vérifier dans src/lib/utils/api.ts
# const API_URL = 'http://localhost:8000'  # Doit être correct
```

---

### 4. Tests

#### Erreur : `ModuleNotFoundError: No module named 'pytest'`
```
ModuleNotFoundError: No module named 'pytest'
```

**Cause** : pytest pas installé

**Solution** :
```bash
cd backend
source venv/bin/activate  # ⚠️ IMPORTANT !
pip install pytest pytest-cov
```

#### Erreur : Tests passent localement mais échouent en CI
```
FAILED tests/test_auth.py::test_register_success
```

**Causes** :
- Environnement différent (variables d'env)
- Base de données pas initialisée
- Dépendances manquantes

**Solutions** :
```bash
# 1. Vérifier les variables d'environnement dans CI
# .github/workflows/*.yml doit définir :
# - DATABASE_URL
# - JWT_SECRET
# - Etc.

# 2. Vérifier que migrations tournent en CI
# Dans le workflow, ajouter :
# - name: Run migrations
#   run: cd backend && alembic upgrade head

# 3. Comparer les versions de dépendances
pip freeze > requirements-local.txt
# Comparer avec requirements.txt
```

---

### 5. Docker

#### Erreur : `Cannot connect to Docker daemon`
```
Cannot connect to the Docker daemon at unix:///var/run/docker.sock
```

**Cause** : Docker Desktop pas démarré

**Solution** :
- macOS/Windows : Démarrer Docker Desktop
- Linux : `sudo systemctl start docker`

#### Erreur : `Port is already allocated`
```
Error starting userland proxy: listen tcp 0.0.0.0:5432: bind: address already in use
```

**Cause** : Port déjà utilisé par un autre processus

**Solution** :
```bash
# Trouver le processus
sudo lsof -i :5432

# Tuer le processus OU changer le port dans docker-compose.yml
ports:
  - "5433:5432"  # Utiliser 5433 au lieu de 5432
```

---

## 🔧 Commandes de Debug Utiles

### Logs Backend
```bash
# Voir les logs en temps réel
cd backend
uvicorn main:app --reload --log-level debug

# Logs avec plus de détails
PYTHONPATH=/home/user/lexikon/backend python -m uvicorn main:app --reload
```

### Logs Frontend
```bash
# Mode verbose
npm run dev -- --debug

# Voir les requêtes réseau dans le navigateur
# Ouvrir DevTools → Network → Filtrer XHR
```

### Logs PostgreSQL
```bash
# Voir les logs du conteneur
docker compose logs postgres -f

# Requêtes SQL en temps réel
docker compose exec postgres psql -U lexikon -d lexikon
# Puis dans psql :
\set ECHO_QUERIES on
SELECT * FROM users;
```

### Logs Docker
```bash
# Voir tous les logs
docker compose logs -f

# Logs d'un service spécifique
docker compose logs backend -f
docker compose logs postgres -f
```

---

## 🧪 Tests de Diagnostic

### Vérifier la Stack Complète
```bash
#!/bin/bash
# Créer ce script : debug-stack.sh

echo "🔍 Vérification de la stack Lexikon..."

echo ""
echo "1. Docker Compose"
docker compose ps
if [ $? -eq 0 ]; then
  echo "✅ Docker Compose OK"
else
  echo "❌ Docker Compose ERREUR"
fi

echo ""
echo "2. PostgreSQL"
docker compose exec postgres psql -U lexikon -d lexikon -c "SELECT 1;" > /dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "✅ PostgreSQL OK"
else
  echo "❌ PostgreSQL ERREUR"
fi

echo ""
echo "3. Backend API"
curl -s http://localhost:8000/ > /dev/null
if [ $? -eq 0 ]; then
  echo "✅ Backend API OK"
else
  echo "❌ Backend API ERREUR (pas démarré ?)"
fi

echo ""
echo "4. Frontend"
curl -s http://localhost:5173/ > /dev/null
if [ $? -eq 0 ]; then
  echo "✅ Frontend OK"
else
  echo "❌ Frontend ERREUR (npm run dev pas démarré ?)"
fi

echo ""
echo "5. Tests Backend"
cd backend
source venv/bin/activate
pytest --co -q > /dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "✅ Tests Backend OK"
else
  echo "❌ Tests Backend ERREUR (pytest pas configuré ?)"
fi
```

**Utilisation** :
```bash
chmod +x debug-stack.sh
./debug-stack.sh
```

---

## 📚 Ressources de Debug

### Documentation Officielle
- FastAPI : https://fastapi.tiangolo.com/tutorial/debugging/
- SvelteKit : https://kit.svelte.dev/docs/errors
- PostgreSQL : https://www.postgresql.org/docs/current/runtime.html
- Alembic : https://alembic.sqlalchemy.org/en/latest/tutorial.html

### Outils Recommandés

**VS Code Extensions** :
- Python (Microsoft)
- Svelte for VS Code
- Docker
- PostgreSQL (Chris Kolkman)
- REST Client (pour tester les API)

**Outils en ligne de commande** :
```bash
# Pretty-print JSON
echo '{"key":"value"}' | jq

# Tester API avec HTTPie (alternative à curl)
pip install httpie
http POST http://localhost:8000/api/auth/login email=test@example.com password=test

# Surveiller les fichiers
watch -n 1 'docker compose ps'

# Logs avec couleurs
docker compose logs -f | grep --color -E 'ERROR|WARNING|$'
```

---

## 🆘 Quand Demander de l'Aide

### Préparer Votre Question

Avant de demander de l'aide, rassemblez :

1. **Description du problème**
   - Qu'essayez-vous de faire ?
   - Qu'est-ce qui se passe au lieu de ça ?

2. **Message d'erreur complet**
   - Copier/coller tout le traceback
   - Ne pas juste dire "ça ne marche pas"

3. **Ce que vous avez essayé**
   - Lister les solutions tentées
   - Montrer que vous avez cherché

4. **Contexte d'environnement**
   ```bash
   # Versions
   python --version
   node --version
   docker --version

   # OS
   uname -a  # Linux/Mac
   # OU
   systeminfo  # Windows
   ```

5. **Code reproduisant le problème**
   - Minimal, complet, vérifiable
   - Pas de screenshot, du texte copiable

### Template de Question

```markdown
## Problème
J'essaie de [OBJECTIF] mais j'obtiens l'erreur [ERREUR].

## Message d'erreur complet
```
[Copier/coller ici]
```

## Ce que j'ai essayé
1. [Solution A] → Résultat : [...]
2. [Solution B] → Résultat : [...]

## Environnement
- OS : Ubuntu 22.04
- Python : 3.10.8
- Node : 18.16.0
- Docker : 24.0.5

## Code reproduisant le problème
```python
[Code minimal ici]
```

## Fichiers de configuration pertinents
- backend/.env : [...]
- docker-compose.yml : [...]
```

---

**Retour** : [Plan d'Action Principal](../PLAN-ACTION-DEVELOPPEUR-JUNIOR.md)
