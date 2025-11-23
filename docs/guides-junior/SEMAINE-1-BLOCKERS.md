# Semaine 1 - Déblocage Critique
## Guide Détaillé pour Développeur Junior

**Durée** : 2-3 jours (14-23h)
**Priorité** : 🔴 P0 - CRITIQUE
**Objectif** : Débloquer les 4 problèmes qui empêchent le lancement beta

---

## 📋 Vue d'Ensemble Semaine 1

### Problèmes à Résoudre

| # | Problème | Impact | Solution |
|---|----------|--------|----------|
| 1 | **Données perdues** au redémarrage | 🔴 Critique | Activer PostgreSQL |
| 2 | **Auth cassée** (fake tokens) | 🔴 Critique | Intégrer JWT |
| 3 | **Vulnérabilités** sécurité | 🔴 Critique | Corriger audit |
| 4 | **Backend non testé** (0% coverage) | 🟡 Majeur | Ajouter pytest |

### Planning de la Semaine

| Jour | Matin (4h) | Après-midi (4h) | Livrables |
|------|------------|-----------------|-----------|
| **Jour 1** | PostgreSQL : Migrations | PostgreSQL : Intégration | DB persistante ✅ |
| **Jour 2** | JWT : Code review | JWT : Intégration | Login/logout ✅ |
| **Jour 3** | Sécurité : Audit | Sécurité : Corrections | Vulnérabilités corrigées ✅ |
| **Jour 4** | Tests : Setup pytest | Tests : Écriture tests auth | 20+ tests backend ✅ |
| **Jour 5** | Tests : Tests terms | Tests : CI/CD | 80%+ coverage ✅ |

---

## 📅 JOUR 1 - PostgreSQL : Persistence des Données

### Matin : Migrations Alembic (4h)

#### 🎯 Objectif
Créer le schéma de base de données PostgreSQL en exécutant les migrations Alembic

#### 📋 Prérequis
- [ ] Docker Compose tourne (`docker compose ps` montre postgres en "healthy")
- [ ] Backend venv activé (`source backend/venv/bin/activate`)
- [ ] Fichier `.env` existe avec `DATABASE_URL` correct

#### Étape 1.1 : Comprendre les Migrations (15 min)

**Qu'est-ce qu'une migration ?**
Une migration est un script qui modifie la structure de la base de données (créer/modifier/supprimer des tables).

**Lire la migration initiale**
```bash
cd /home/user/lexikon/backend
cat db/migrations/versions/001_initial_schema.py
```

💡 **Ce que vous devez comprendre** :
- Quelles tables seront créées ? (users, terms, relationships, etc.)
- Quelles colonnes chaque table aura ?
- Quelles sont les clés étrangères ?

**Questions à vous poser** :
1. Combien de tables seront créées ?
2. Quelle table stocke les utilisateurs ?
3. Quelle table stocke les termes ?

#### Étape 1.2 : Vérifier la Configuration Alembic (10 min)

**Vérifier `alembic.ini`**
```bash
cat alembic.ini | grep sqlalchemy.url
```

✅ **Vérification attendue** :
```
sqlalchemy.url = postgresql://lexikon:dev-secret@localhost:5432/lexikon
```

⚠️ **Si la ligne est commentée ou différente** :
```bash
# Éditer le fichier
nano alembic.ini

# Chercher la ligne sqlalchemy.url et la mettre à :
sqlalchemy.url = postgresql://lexikon:dev-secret@localhost:5432/lexikon

# Sauvegarder : Ctrl+O puis Entrée, Quitter : Ctrl+X
```

**Vérifier que PostgreSQL est accessible**
```bash
docker compose exec postgres psql -U lexikon -d lexikon -c "SELECT 1;"
```

✅ **Sortie attendue** :
```
 ?column?
----------
        1
(1 row)
```

🐛 **Si erreur "connection refused"** :
```bash
# Redémarrer les conteneurs
docker compose down
docker compose up -d

# Attendre 10 secondes que postgres démarre
sleep 10

# Réessayer
docker compose exec postgres psql -U lexikon -d lexikon -c "SELECT 1;"
```

#### Étape 1.3 : Exécuter les Migrations (30 min)

**Vérifier les migrations disponibles**
```bash
cd /home/user/lexikon/backend
source venv/bin/activate  # Si pas déjà fait

alembic current
```

✅ **Sortie attendue** :
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
```
(Aucune version actuelle car migrations pas encore appliquées)

**Lister les migrations disponibles**
```bash
alembic history
```

✅ **Sortie attendue** :
```
<base> -> 001 (head), initial schema
```

**Exécuter les migrations**
```bash
alembic upgrade head
```

✅ **Sortie attendue** :
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 001, initial schema
```

🐛 **Si erreur "Table 'users' already exists"** :
```bash
# La base existe déjà, on la reset
docker compose exec postgres psql -U lexikon -d lexikon -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Réessayer la migration
alembic upgrade head
```

#### Étape 1.4 : Vérifier les Tables Créées (15 min)

**Lister les tables**
```bash
docker compose exec postgres psql -U lexikon -d lexikon -c "\dt"
```

✅ **Sortie attendue** :
```
             List of relations
 Schema |     Name      | Type  | Owner
--------+---------------+-------+---------
 public | users         | table | lexikon
 public | terms         | table | lexikon
 public | relationships | table | lexikon
 public | alembic_version | table | lexikon
```

💡 **Ce que signifient ces tables** :
- `users` : Stocke les comptes utilisateurs
- `terms` : Stocke les termes de l'ontologie
- `relationships` : Stocke les relations entre termes
- `alembic_version` : Suivi des migrations (interne Alembic)

**Vérifier la structure de la table `users`**
```bash
docker compose exec postgres psql -U lexikon -d lexikon -c "\d users"
```

✅ **Vous devriez voir** :
- Colonnes : id, email, username, hashed_password, created_at, etc.
- Index sur email (pour recherche rapide)
- Contrainte unique sur email

**Vérifier qu'il n'y a pas encore de données**
```bash
docker compose exec postgres psql -U lexikon -d lexikon -c "SELECT COUNT(*) FROM users;"
```

✅ **Sortie attendue** :
```
 count
-------
     0
```

#### Étape 1.5 : Comprendre le Code de Persistence (30 min)

**Ouvrir le fichier `backend/db/postgres.py`**
```bash
code backend/db/postgres.py
# OU
cat backend/db/postgres.py
```

💡 **Ce que vous devez identifier** :
1. **get_db()** : Fonction qui crée une session de base de données
2. **User**, **Term**, **Relationship** : Modèles SQLAlchemy (classes = tables)
3. **create_user()**, **get_user()** : Fonctions CRUD (Create, Read, Update, Delete)

**Questions à vous poser** :
- Comment crée-t-on un utilisateur ?
- Comment récupère-t-on un utilisateur par email ?
- Quelle est la différence entre `User` (modèle) et `UserProfileRequest` (Pydantic) ?

**Tester une insertion manuelle** (optionnel mais recommandé)
```bash
# Ouvrir un shell Python
cd /home/user/lexikon/backend
source venv/bin/activate
python3

# Dans le shell Python, taper :
```

```python
from db.postgres import get_db, User
from sqlalchemy.orm import Session
from passlib.context import CryptContext

# Créer une session
db = next(get_db())

# Créer un hash de mot de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed_pwd = pwd_context.hash("test123")

# Créer un utilisateur de test
test_user = User(
    email="test@example.com",
    username="testuser",
    hashed_password=hashed_pwd,
    full_name="Test User"
)

# Ajouter à la DB
db.add(test_user)
db.commit()

print(f"✅ Utilisateur créé avec ID: {test_user.id}")

# Vérifier qu'il existe
user = db.query(User).filter(User.email == "test@example.com").first()
print(f"✅ Utilisateur récupéré: {user.username}")

# Fermer la session
db.close()
exit()
```

✅ **Sortie attendue** :
```
✅ Utilisateur créé avec ID: 1
✅ Utilisateur récupéré: testuser
```

**Vérifier dans PostgreSQL**
```bash
docker compose exec postgres psql -U lexikon -d lexikon -c "SELECT id, email, username FROM users;"
```

✅ **Sortie attendue** :
```
 id |       email        | username
----+--------------------+----------
  1 | test@example.com   | testuser
```

🎉 **Checkpoint Matin Jour 1** : PostgreSQL est prêt avec les tables et vous savez insérer des données !

---

### Après-midi : Intégration PostgreSQL dans l'API (4h)

#### 🎯 Objectif
Remplacer le stockage in-memory (dictionnaires Python) par PostgreSQL dans `backend/main.py`

#### Étape 1.6 : Analyser le Code Actuel (30 min)

**Ouvrir `backend/main.py`**
```bash
code backend/main.py
# OU pour voir juste les lignes concernées :
grep -n "data_store" backend/main.py
```

💡 **Ce que vous devez trouver** (vers ligne 50) :
```python
# In-memory storage (temporary for MVP)
data_store = {
    "users": {},
    "terms": {},
    "onboarding": {}
}
```

⚠️ **Problème** : Quand le serveur redémarre, `data_store` est réinitialisé → perte de données !

**Identifier toutes les utilisations de `data_store`**
```bash
grep -n "data_store\[" backend/main.py
```

✅ **Vous devriez voir** :
- Ligne ~80 : `data_store["onboarding"][user_id] = ...`
- Ligne ~100 : `data_store["users"][user_id] = ...`
- Ligne ~150 : `data_store["terms"][term_id] = ...`

💡 **Stratégie** : Remplacer chaque accès à `data_store` par un appel à la DB PostgreSQL

#### Étape 1.7 : Modifier l'Endpoint `/api/users/profile` (60 min)

**Localiser l'endpoint**
```bash
grep -A 20 "@app.post(\"/api/users/profile\")" backend/main.py
```

**Code actuel** (approximatif) :
```python
@app.post("/api/users/profile")
async def create_user_profile(profile: UserProfileRequest):
    user_id = str(uuid.uuid4())

    # ❌ IN-MEMORY (à remplacer)
    data_store["users"][user_id] = {
        "id": user_id,
        "full_name": profile.full_name,
        "email": profile.email,
        # ...
    }

    return {"message": "Profile created", "user_id": user_id}
```

**Nouveau code avec PostgreSQL** :

1. **Ajouter les imports en haut du fichier**
```python
# Trouver la ligne : from fastapi import FastAPI, HTTPException
# Ajouter après :
from sqlalchemy.orm import Session
from db.postgres import get_db, User, create_user
from passlib.context import CryptContext
```

2. **Créer un contexte de hachage de mot de passe** (après les imports)
```python
# Après : app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
```

3. **Modifier l'endpoint** :
```python
@app.post("/api/users/profile")
async def create_user_profile(
    profile: UserProfileRequest,
    db: Session = Depends(get_db)  # ✅ Injection de dépendance
):
    # Vérifier si l'email existe déjà
    existing_user = db.query(User).filter(User.email == profile.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hasher le mot de passe (si fourni, sinon générer temporaire)
    hashed_password = pwd_context.hash(profile.email)  # Temporaire

    # Créer l'utilisateur via la fonction CRUD
    new_user = User(
        email=profile.email,
        username=profile.email.split('@')[0],  # Utiliser partie avant @
        hashed_password=hashed_password,
        full_name=profile.full_name,
        primary_domain=profile.primary_domain,
        organization=profile.organization
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Récupérer l'ID auto-généré

    return {
        "message": "Profile created",
        "user_id": str(new_user.id),
        "email": new_user.email
    }
```

⚠️ **Important - Ajouter l'import Depends** :
```python
# En haut du fichier, modifier :
from fastapi import FastAPI, HTTPException, Depends
```

#### Étape 1.8 : Modifier l'Endpoint `/api/terms` (60 min)

**Localiser l'endpoint**
```bash
grep -A 20 "@app.post(\"/api/terms\")" backend/main.py
```

**Modifier l'endpoint** :
```python
@app.post("/api/terms")
async def create_term(
    term_request: CreateTermRequest,
    db: Session = Depends(get_db)
):
    # Pour l'instant, on crée un user_id fictif
    # (sera remplacé par le vrai user JWT à Jour 2)
    user_id = 1  # ID du user de test créé ce matin

    # Créer le terme
    new_term = Term(
        user_id=user_id,
        term=term_request.term,
        definition=term_request.definition,
        domain=term_request.domain,
        level=term_request.level,
        status="draft",
        context=term_request.context,
        usage_example=term_request.usage_example
    )

    db.add(new_term)
    db.commit()
    db.refresh(new_term)

    return {
        "message": "Term created successfully",
        "term_id": str(new_term.id),
        "term": new_term.term
    }
```

**Ajouter l'import Term** :
```python
# En haut, modifier :
from db.postgres import get_db, User, Term
```

#### Étape 1.9 : Tester l'Intégration PostgreSQL (60 min)

**Démarrer le serveur backend**
```bash
cd /home/user/lexikon/backend
source venv/bin/activate
uvicorn main:app --reload
```

✅ **Vérification** : Le serveur doit démarrer sans erreurs
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

🐛 **Si erreur "ModuleNotFoundError: No module named 'db'"** :
```bash
# Ajouter le chemin backend au PYTHONPATH
export PYTHONPATH=/home/user/lexikon/backend:$PYTHONPATH
uvicorn main:app --reload
```

**Tester l'endpoint de création de profil**

Dans un autre terminal :
```bash
curl -X POST http://localhost:8000/api/users/profile \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Jane Doe",
    "email": "jane@example.com",
    "primary_domain": "Computer Science",
    "organization": "Test University"
  }'
```

✅ **Réponse attendue** :
```json
{
  "message": "Profile created",
  "user_id": "2",
  "email": "jane@example.com"
}
```

**Vérifier dans PostgreSQL**
```bash
docker compose exec postgres psql -U lexikon -d lexikon -c "SELECT id, email, full_name FROM users;"
```

✅ **Sortie attendue** :
```
 id |       email        |  full_name
----+--------------------+------------
  1 | test@example.com   | Test User
  2 | jane@example.com   | Jane Doe
```

🎉 **Si vous voyez 2 users, bravo ! La persistence fonctionne !**

**Tester la création de terme**
```bash
curl -X POST http://localhost:8000/api/terms \
  -H "Content-Type: application/json" \
  -d '{
    "term": "Ontology",
    "definition": "A formal representation of knowledge",
    "domain": "Computer Science",
    "level": "intermediate",
    "context": "Semantic Web",
    "usage_example": "RDF is an ontology language"
  }'
```

✅ **Réponse attendue** :
```json
{
  "message": "Term created successfully",
  "term_id": "1",
  "term": "Ontology"
}
```

**Vérifier dans PostgreSQL**
```bash
docker compose exec postgres psql -U lexikon -d lexikon -c "SELECT id, term, definition FROM terms;"
```

✅ **Sortie attendue** :
```
 id |   term   |           definition
----+----------+---------------------------------
  1 | Ontology | A formal representation of...
```

#### Étape 1.10 : Test de Persistence (15 min)

**Test crucial : Redémarrage du serveur**

1. Arrêter le serveur backend (Ctrl+C dans le terminal uvicorn)

2. Redémarrer
```bash
uvicorn main:app --reload
```

3. Vérifier que les données existent toujours
```bash
docker compose exec postgres psql -U lexikon -d lexikon -c "SELECT COUNT(*) FROM users;"
docker compose exec postgres psql -U lexikon -d lexikon -c "SELECT COUNT(*) FROM terms;"
```

✅ **Résultat attendu** :
```
 count
-------
     2      <- Les 2 users existent toujours !
```

🎉 **Checkpoint Après-midi Jour 1** : Les données survivent au redémarrage ! ✅

---

## 📅 JOUR 2 - JWT : Authentification Réelle

### Matin : Code Review et Compréhension JWT (4h)

#### 🎯 Objectif
Comprendre comment fonctionne JWT et le code existant dans `backend/auth/jwt.py`

#### Étape 2.1 : Apprendre JWT (Théorie - 60 min)

**Qu'est-ce que JWT ?**
JWT (JSON Web Token) est un standard pour créer des tokens d'authentification.

**Analogie** : Imaginez un badge d'entreprise
- Vous vous identifiez à la réception (login) → On vous donne un badge (JWT token)
- Vous utilisez le badge pour entrer dans les salles (requêtes API)
- Le badge a une date d'expiration (token expiry)
- Si perdu, vous en redemandez un (refresh token)

**Structure d'un JWT** :
```
eyJhbGci.eyJzdWIi.SflKxwRJ  <- 3 parties séparées par des points
│         │        │
Header    Payload  Signature
```

- **Header** : Type de token et algorithme (HS256)
- **Payload** : Données (user_id, email, expiration)
- **Signature** : Preuve que le token n'a pas été modifié

**Lire la documentation officielle** (optionnel mais recommandé)
- [jwt.io](https://jwt.io/) - Décodeur interactif
- Essayez de décoder un token exemple

#### Étape 2.2 : Analyser `backend/auth/jwt.py` (90 min)

**Ouvrir le fichier**
```bash
code backend/auth/jwt.py
# OU
cat backend/auth/jwt.py
```

**Identifier les fonctions principales** :

1. **create_access_token()**
```python
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=1)  # 1h expiry
    to_encode.update({"exp": expire, "type": "access"})

    encoded_jwt = jose.jwt.encode(
        to_encode,
        JWT_SECRET,
        algorithm="HS256"
    )
    return encoded_jwt
```

💡 **Ce que fait cette fonction** :
- Prend des données (ex: `{"user_id": 123, "email": "test@example.com"}`)
- Ajoute une expiration (1 heure)
- Encode avec le secret JWT
- Retourne le token (string)

2. **create_refresh_token()**
```python
def create_refresh_token(data: dict) -> str:
    # Similaire mais expiration = 7 jours
```

💡 **Différence access vs refresh** :
- **Access token** : Courte durée (1h), utilisé pour chaque requête API
- **Refresh token** : Longue durée (7 jours), utilisé pour obtenir un nouvel access token

3. **verify_token()**
```python
def verify_token(token: str) -> dict:
    try:
        payload = jose.jwt.decode(
            token,
            JWT_SECRET,
            algorithms=["HS256"]
        )
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

💡 **Ce que fait cette fonction** :
- Décode le token
- Vérifie la signature (pas modifié ?)
- Vérifie l'expiration (pas expiré ?)
- Retourne les données si valide, sinon erreur 401

**Questions à vous poser** :
1. Où est défini `JWT_SECRET` ? (Réponse : dans `.env`)
2. Que se passe-t-il si le token est expiré ?
3. Comment obtient-on le user_id depuis un token ?

**Tester les fonctions manuellement**
```bash
cd /home/user/lexikon/backend
source venv/bin/activate
python3

# Dans le shell Python :
```

```python
from auth.jwt import create_access_token, verify_token
import os

# Simuler le JWT_SECRET (normalement depuis .env)
os.environ["JWT_SECRET"] = "test-secret-key"

# Créer un token
token = create_access_token({"user_id": 123, "email": "test@example.com"})
print(f"Token créé : {token[:50]}...")  # Afficher les 50 premiers caractères

# Vérifier le token
payload = verify_token(token)
print(f"Payload décodé : {payload}")
# Devrait afficher : {'user_id': 123, 'email': 'test@example.com', 'exp': ...}

exit()
```

✅ **Vérification** : Vous devez comprendre le flow :
1. Login → create_access_token() → Token envoyé au client
2. Client envoie le token dans chaque requête
3. Backend appelle verify_token() → Récupère user_id

#### Étape 2.3 : Analyser `backend/auth/middleware.py` (60 min)

**Ouvrir le fichier**
```bash
code backend/auth/middleware.py
# OU
cat backend/auth/middleware.py
```

**Fonction principale : `get_current_user()`**
```python
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    # 1. Vérifier le token
    payload = verify_token(token)

    # 2. Extraire user_id
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(401, "Invalid token")

    # 3. Récupérer l'utilisateur depuis la DB
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(401, "User not found")

    return user
```

💡 **Ce middleware sera utilisé comme** :
```python
@app.get("/api/protected-route")
async def protected_route(current_user: User = Depends(get_current_user)):
    # current_user est automatiquement récupéré depuis le token !
    return {"message": f"Hello {current_user.email}"}
```

**Concept clé : Dependency Injection**
- `Depends(get_current_user)` est magique en FastAPI
- FastAPI appelle automatiquement `get_current_user()`
- Le résultat est passé comme paramètre `current_user`

🎉 **Checkpoint Matin Jour 2** : Vous comprenez JWT et le code existant !

---

### Après-midi : Intégration JWT dans l'API (4h)

#### 🎯 Objectif
Brancher les fonctions JWT dans les endpoints `/api/auth/register` et `/api/auth/login`

#### Étape 2.4 : Créer l'Endpoint de Register (60 min)

**Ouvrir `backend/api/auth.py`** (s'il n'existe pas, le créer)
```bash
# Créer le fichier si nécessaire
touch backend/api/auth.py
code backend/api/auth.py
```

**Code complet de `/api/auth/register`** :
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from db.postgres import get_db, User
from auth.jwt import create_access_token, create_refresh_token
from passlib.context import CryptContext

router = APIRouter(prefix="/api/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str  # Minimum 8 caractères
    full_name: str


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    # 1. Vérifier si l'email existe déjà
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 2. Valider le mot de passe
    if len(request.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

    # 3. Hasher le mot de passe
    hashed_password = pwd_context.hash(request.password)

    # 4. Créer l'utilisateur
    new_user = User(
        email=request.email,
        username=request.email.split('@')[0],  # Ex: john@example.com → john
        hashed_password=hashed_password,
        full_name=request.full_name
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 5. Créer les tokens JWT
    token_data = {"user_id": new_user.id, "email": new_user.email}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    # 6. Retourner les tokens
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "full_name": new_user.full_name
        }
    }
```

#### Étape 2.5 : Créer l'Endpoint de Login (60 min)

**Ajouter dans le même fichier `backend/api/auth.py`** :
```python
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    # 1. Récupérer l'utilisateur
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # 2. Vérifier le mot de passe
    if not pwd_context.verify(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # 3. Créer les tokens JWT
    token_data = {"user_id": user.id, "email": user.email}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    # 4. Retourner les tokens
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name
        }
    }
```

#### Étape 2.6 : Monter le Router dans `main.py` (15 min)

**Ouvrir `backend/main.py`**
```bash
code backend/main.py
```

**Ajouter en haut du fichier** :
```python
from api.auth import router as auth_router
```

**Ajouter après `app = FastAPI()`** :
```python
app = FastAPI(
    title="Lexikon API",
    version="0.2.0"
)

# Monter le router d'authentification
app.include_router(auth_router)
```

💡 **Ce que ça fait** : Toutes les routes de `auth_router` sont maintenant disponibles :
- POST `/api/auth/register`
- POST `/api/auth/login`

#### Étape 2.7 : Tester Register et Login (60 min)

**Redémarrer le serveur backend**
```bash
# Arrêter le serveur actuel (Ctrl+C)
# Redémarrer
cd /home/user/lexikon/backend
source venv/bin/activate
uvicorn main:app --reload
```

**Test 1 : Register**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "securepass123",
    "full_name": "Alice Wonderland"
  }'
```

✅ **Réponse attendue** :
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 3,
    "email": "alice@example.com",
    "full_name": "Alice Wonderland"
  }
}
```

💡 **Sauvegarder le `access_token` dans un fichier** :
```bash
# Copier le token (sans les guillemets)
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
echo $TOKEN > /tmp/token.txt
```

**Test 2 : Login**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "securepass123"
  }'
```

✅ **Réponse attendue** : Même structure que Register

🐛 **Si erreur "Invalid email or password"** :
- Vérifier l'email (faute de frappe ?)
- Vérifier le mot de passe (exactement "securepass123" ?)
- Vérifier que Register a fonctionné avant

**Test 3 : Login avec mauvais mot de passe**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "wrongpassword"
  }'
```

✅ **Réponse attendue** :
```json
{
  "detail": "Invalid email or password"
}
```

🎉 **Si erreur 401, c'est bon ! La sécurité fonctionne !**

#### Étape 2.8 : Protéger un Endpoint avec JWT (60 min)

**Modifier l'endpoint `/api/terms` pour exiger authentification**

**Ouvrir `backend/main.py`** et trouver l'endpoint POST `/api/terms`

**Ajouter l'import** :
```python
from auth.middleware import get_current_user
```

**Modifier l'endpoint** :
```python
@app.post("/api/terms")
async def create_term(
    term_request: CreateTermRequest,
    current_user: User = Depends(get_current_user),  # ✅ Exige authentification
    db: Session = Depends(get_db)
):
    # Utiliser le vrai user_id depuis le token
    new_term = Term(
        user_id=current_user.id,  # ✅ Plus de user_id fictif !
        term=term_request.term,
        definition=term_request.definition,
        domain=term_request.domain,
        level=term_request.level,
        status="draft"
    )

    db.add(new_term)
    db.commit()
    db.refresh(new_term)

    return {
        "message": "Term created successfully",
        "term_id": str(new_term.id),
        "term": new_term.term,
        "created_by": current_user.email  # ✅ Montrer qui a créé
    }
```

**Redémarrer le serveur**

**Test 1 : Sans token (doit échouer)**
```bash
curl -X POST http://localhost:8000/api/terms \
  -H "Content-Type: application/json" \
  -d '{
    "term": "JWT",
    "definition": "JSON Web Token",
    "domain": "Security",
    "level": "intermediate"
  }'
```

✅ **Réponse attendue** :
```json
{
  "detail": "Not authenticated"
}
```

🎉 **Erreur 401 = bon signe ! L'endpoint est protégé !**

**Test 2 : Avec token (doit marcher)**
```bash
# Utiliser le token sauvegardé
TOKEN=$(cat /tmp/token.txt)

curl -X POST http://localhost:8000/api/terms \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "term": "JWT",
    "definition": "JSON Web Token",
    "domain": "Security",
    "level": "intermediate"
  }'
```

✅ **Réponse attendue** :
```json
{
  "message": "Term created successfully",
  "term_id": "2",
  "term": "JWT",
  "created_by": "alice@example.com"
}
```

🎉 **Checkpoint Jour 2** : Authentification JWT complète et fonctionnelle ! ✅

---

## 📅 JOUR 3 - Sécurité : Audit et Corrections

### 🎯 Objectif
Corriger les vulnérabilités de sécurité identifiées dans l'audit

### Matin : Lire et Comprendre l'Audit (4h)

#### Étape 3.1 : Lire le Rapport d'Audit (60 min)

**Récupérer le commit de l'audit**
```bash
cd /home/user/lexikon
git show 0d2b342
```

💡 **Si le commit n'existe pas** :
Chercher dans les documents :
```bash
find docs/ -name "*security*" -o -name "*audit*"
```

**Lire le rapport** (si un fichier existe, sinon passer à l'étape suivante)

#### Étape 3.2 : Identifier les Vulnérabilités Communes (120 min)

Même sans rapport d'audit spécifique, voici les vulnérabilités typiques à corriger :

**Vulnérabilité #1 : JWT_SECRET faible**

🔴 **Risque** : Si le secret est "test" ou "dev-secret", un attaquant peut créer de faux tokens

**Vérifier le problème** :
```bash
cat backend/.env | grep JWT_SECRET
```

❌ **Mauvais exemples** :
```
JWT_SECRET=dev-secret        # Trop simple
JWT_SECRET=test              # Trop court
JWT_SECRET=CHANGE-ME         # Jamais changé
```

✅ **Solution : Générer un secret aléatoire**
```bash
# Générer un secret de 64 caractères aléatoires
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

**Copier la sortie et éditer `.env`** :
```bash
nano backend/.env

# Remplacer la ligne JWT_SECRET par :
JWT_SECRET=LA_LONGUE_CHAINE_ALEATOIRE_GENEREE_CI_DESSUS
```

⚠️ **Ne jamais commiter le fichier `.env` dans Git !**

**Vérifier que `.env` est bien dans `.gitignore`** :
```bash
grep "\.env" .gitignore
```

✅ **Doit afficher** : `.env` ou `.env*`

---

**Vulnérabilité #2 : CORS trop permissif**

🔴 **Risque** : `allow_origins=["*"]` permet à n'importe quel site web d'appeler votre API

**Vérifier le problème** :
```bash
grep -A 5 "CORSMiddleware" backend/main.py
```

❌ **Mauvais exemple** :
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ❌ N'importe qui peut appeler l'API !
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

✅ **Solution : Restreindre aux domaines autorisés**
```python
# En haut du fichier, importer os
import os

# Configurer CORS de manière sécurisée
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # ✅ Liste explicite
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # ✅ Méthodes explicites
    allow_headers=["Content-Type", "Authorization"],  # ✅ Headers explicites
)
```

**Ajouter dans `.env`** :
```bash
nano backend/.env

# Ajouter :
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

**Vulnérabilité #3 : Pas de validation de mot de passe fort**

🔴 **Risque** : Utilisateurs peuvent choisir "123456" comme mot de passe

**Améliorer la validation dans `backend/api/auth.py`** :
```python
import re

def validate_password(password: str) -> bool:
    """Valide qu'un mot de passe est fort"""
    # Au moins 8 caractères
    if len(password) < 8:
        return False

    # Au moins une majuscule
    if not re.search(r"[A-Z]", password):
        return False

    # Au moins une minuscule
    if not re.search(r"[a-z]", password):
        return False

    # Au moins un chiffre
    if not re.search(r"\d", password):
        return False

    return True


@router.post("/register")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    # ... (code existant)

    # ✅ Valider le mot de passe fort
    if not validate_password(request.password):
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters with uppercase, lowercase, and number"
        )

    # ... (suite du code)
```

---

**Vulnérabilité #4 : Pas de limite de tentatives de login**

🔴 **Risque** : Un attaquant peut tenter 1 million de mots de passe (brute force)

💡 **Solution : Rate limiting** (sera implémenté en Semaine 2, mais noter pour l'instant)

---

#### Étape 3.3 : Appliquer les Corrections (120 min)

**Checklist de sécurité** :

1. **JWT Secret**
   - [ ] Généré aléatoirement (64+ caractères)
   - [ ] Stocké dans `.env`
   - [ ] `.env` dans `.gitignore`
   - [ ] Jamais commité dans Git

2. **CORS**
   - [ ] `allow_origins` liste explicite
   - [ ] Pas de `*` (wildcard)
   - [ ] Configuration via variable d'environnement

3. **Mots de passe**
   - [ ] Validation forte (8+ caractères, majuscule, minuscule, chiffre)
   - [ ] Hashés avec bcrypt
   - [ ] Jamais stockés en clair

4. **Tokens**
   - [ ] Expiration courte (1h pour access, 7 jours pour refresh)
   - [ ] Signature vérifiée
   - [ ] Type de token vérifié

**Tester les corrections** :

**Test 1 : Mot de passe faible refusé**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "weak@example.com",
    "password": "weak",
    "full_name": "Weak Password"
  }'
```

✅ **Réponse attendue** :
```json
{
  "detail": "Password must be at least 8 characters with uppercase, lowercase, and number"
}
```

**Test 2 : Mot de passe fort accepté**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "strong@example.com",
    "password": "StrongPass123",
    "full_name": "Strong Password"
  }'
```

✅ **Réponse attendue** : 200 OK avec tokens

🎉 **Checkpoint Jour 3** : Vulnérabilités de sécurité corrigées ! ✅

---

## 📅 JOUR 4-5 - Tests Backend

### 🎯 Objectif
Atteindre 80%+ de couverture de tests backend avec pytest

### Jour 4 Matin : Setup pytest (4h)

#### Étape 4.1 : Configurer pytest (30 min)

**Créer `backend/pytest.ini`**
```bash
cd /home/user/lexikon/backend
nano pytest.ini
```

**Contenu** :
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --verbose
    --cov=.
    --cov-report=term-missing
    --cov-report=html
    --cov-exclude=venv/*
    --cov-exclude=tests/*
```

**Créer le dossier de tests**
```bash
mkdir -p tests
touch tests/__init__.py
```

#### Étape 4.2 : Créer les Fixtures de Test (60 min)

**Créer `backend/tests/conftest.py`** (fixtures partagées)
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.postgres import Base, get_db
from main import app

# Base de données de test (SQLite en mémoire)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Crée une base de données de test pour chaque test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Client de test avec DB de test"""
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    """Utilisateur de test"""
    from db.postgres import User
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=pwd_context.hash("TestPass123"),
        full_name="Test User"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@pytest.fixture
def auth_token(test_user):
    """Token JWT pour user de test"""
    from auth.jwt import create_access_token

    return create_access_token({
        "user_id": test_user.id,
        "email": test_user.email
    })
```

💡 **Ce que font ces fixtures** :
- `db` : Crée une base SQLite en mémoire pour chaque test (rapide, isolé)
- `client` : Client HTTP de test pour appeler l'API
- `test_user` : Utilisateur pré-créé pour les tests
- `auth_token` : Token JWT valide pour les tests

#### Étape 4.3 : Écrire les Tests d'Authentification (120 min)

**Créer `backend/tests/test_auth.py`**
```python
import pytest
from fastapi import status


class TestRegister:
    """Tests pour /api/auth/register"""

    def test_register_success(self, client):
        """Test : Register avec données valides"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "new@example.com",
                "password": "StrongPass123",
                "full_name": "New User"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "new@example.com"

    def test_register_duplicate_email(self, client, test_user):
        """Test : Register avec email déjà utilisé"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": test_user.email,  # Email existant
                "password": "StrongPass123",
                "full_name": "Duplicate"
            }
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"]

    def test_register_weak_password(self, client):
        """Test : Register avec mot de passe faible"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "weak@example.com",
                "password": "weak",  # Trop faible
                "full_name": "Weak"
            }
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Password must" in response.json()["detail"]

    def test_register_invalid_email(self, client):
        """Test : Register avec email invalide"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "not-an-email",  # Format invalide
                "password": "StrongPass123",
                "full_name": "Invalid"
            }
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestLogin:
    """Tests pour /api/auth/login"""

    def test_login_success(self, client, test_user):
        """Test : Login avec bonnes credentials"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user.email,
                "password": "TestPass123"  # Mot de passe du test_user
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "access_token" in data
        assert data["user"]["email"] == test_user.email

    def test_login_wrong_password(self, client, test_user):
        """Test : Login avec mauvais mot de passe"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user.email,
                "password": "WrongPassword123"
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client):
        """Test : Login avec utilisateur inexistant"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "ghost@example.com",
                "password": "AnyPass123"
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestProtectedEndpoint:
    """Tests pour endpoints protégés"""

    def test_access_without_token(self, client):
        """Test : Accès sans token (doit échouer)"""
        response = client.post(
            "/api/terms",
            json={
                "term": "Test",
                "definition": "Test definition",
                "domain": "Test",
                "level": "beginner"
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_access_with_token(self, client, auth_token):
        """Test : Accès avec token valide (doit marcher)"""
        response = client.post(
            "/api/terms",
            json={
                "term": "Test",
                "definition": "Test definition",
                "domain": "Test",
                "level": "beginner"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["term"] == "Test"

    def test_access_with_invalid_token(self, client):
        """Test : Accès avec token invalide"""
        response = client.post(
            "/api/terms",
            json={"term": "Test", "definition": "Test", "domain": "Test", "level": "beginner"},
            headers={"Authorization": "Bearer invalid-token"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
```

#### Étape 4.4 : Exécuter les Tests (30 min)

**Installer les dépendances de test**
```bash
cd /home/user/lexikon/backend
source venv/bin/activate
pip install pytest pytest-cov httpx
```

**Exécuter les tests**
```bash
pytest
```

✅ **Sortie attendue** :
```
tests/test_auth.py::TestRegister::test_register_success PASSED         [ 10%]
tests/test_auth.py::TestRegister::test_register_duplicate_email PASSED [ 20%]
tests/test_auth.py::TestRegister::test_register_weak_password PASSED   [ 30%]
tests/test_auth.py::TestRegister::test_register_invalid_email PASSED   [ 40%]
tests/test_auth.py::TestLogin::test_login_success PASSED               [ 50%]
tests/test_auth.py::TestLogin::test_login_wrong_password PASSED        [ 60%]
tests/test_auth.py::TestLogin::test_login_nonexistent_user PASSED      [ 70%]
tests/test_auth.py::TestProtectedEndpoint::test_access_without_token PASSED [ 80%]
tests/test_auth.py::TestProtectedEndpoint::test_access_with_token PASSED [ 90%]
tests/test_auth.py::TestProtectedEndpoint::test_access_with_invalid_token PASSED [100%]

========== 10 passed in 2.34s ==========
```

**Voir la couverture**
```bash
pytest --cov=. --cov-report=term
```

✅ **Objectif** : Couverture ≥80% pour `api/auth.py`

🎉 **Checkpoint Jour 4** : 10+ tests d'authentification passent ! ✅

---

### Jour 5 : Tests CRUD Terms + CI/CD (8h)

#### Étape 5.1 : Écrire les Tests de Termes (Voir Annexe C)

Par manque d'espace ici, voir **[Annexe C - Tests](./ANNEXE-C-TESTS.md)** pour :
- Tests CRUD complets (Create, Read, Update, Delete)
- Tests de validation
- Tests de relations entre termes

#### Étape 5.2 : Configurer CI/CD Strict (2h)

**Modifier `.github/workflows/backend-test.yml`**
```yaml
name: Backend - Test & Lint

on:
  push:
    branches: [develop, master]
  pull_request:
    branches: [develop, master]

jobs:
  test-and-lint:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          cache: 'pip'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov ruff mypy

      - name: Lint with ruff
        run: |
          cd backend
          ruff check .
        # ✅ RETIRER continue-on-error !

      - name: Run tests
        run: |
          cd backend
          pytest --cov=. --cov-report=xml --cov-report=term
        # ✅ RETIRER continue-on-error !

      - name: Check coverage
        run: |
          cd backend
          coverage report --fail-under=80

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml
```

**Pousser les changements**
```bash
git add .github/workflows/backend-test.yml
git commit -m "ci: Remove continue-on-error from backend tests"
git push
```

🎉 **Checkpoint Final Semaine 1** : Tous les blockers critiques sont résolus ! ✅

---

## ✅ Checklist Finale Semaine 1

Avant de passer à la Semaine 2, vérifiez :

- [ ] **PostgreSQL** : Données persistent après redémarrage serveur
- [ ] **JWT** : Login/logout fonctionnent avec vrais tokens
- [ ] **Sécurité** : JWT_SECRET aléatoire, CORS restreint, mots de passe forts
- [ ] **Tests** : ≥80% couverture backend, tous les tests passent
- [ ] **CI/CD** : Pas de `continue-on-error`, tests bloquent merge si échec

**Tests de validation** :
```bash
# 1. Tests unitaires
cd backend
pytest --cov=. --cov-report=term
# → Doit afficher ≥80% coverage

# 2. Flow complet
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"final@test.com","password":"FinalTest123","full_name":"Final Test"}'

# Sauvegarder le token
export TOKEN="<le token reçu>"

# Créer un terme
curl -X POST http://localhost:8000/api/terms \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"term":"MVP","definition":"Minimum Viable Product","domain":"Product","level":"beginner"}'

# Redémarrer le backend (Ctrl+C puis relancer)

# Vérifier que le terme existe toujours
docker compose exec postgres psql -U lexikon -d lexikon -c "SELECT * FROM terms WHERE term='MVP';"
# → Doit afficher le terme !
```

Si tout passe ✅ → **Bravo ! Vous pouvez passer à la Semaine 2** 🎉

---

**Prochaine étape** : [Semaine 2 - Launch Readiness](./SEMAINE-2-LAUNCH-READINESS.md)
