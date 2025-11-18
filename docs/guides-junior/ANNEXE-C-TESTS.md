# Annexe C - Guide des Tests
## Écrire et Exécuter des Tests

---

## 🧪 Types de Tests

| Type | Portée | Outils | Durée | Quand |
|------|--------|--------|-------|-------|
| **Unit** | Fonction isolée | pytest, Vitest | <1s | Toujours |
| **Integration** | Plusieurs composants | pytest + DB test | 1-5s | Features importantes |
| **E2E** | Application complète | Playwright | 10-30s | Flows utilisateurs |

---

## 🐍 Tests Backend (pytest)

### Structure d'un Test

```python
import pytest
from fastapi.testclient import TestClient

def test_example():
    # Arrange (Préparer)
    data = {"key": "value"}

    # Act (Agir)
    result = function_to_test(data)

    # Assert (Vérifier)
    assert result == expected_value
```

### Fixtures

**Ce que c'est** : Données ou objets réutilisables dans plusieurs tests

```python
# tests/conftest.py
@pytest.fixture
def client():
    """Client HTTP pour tester l'API"""
    from main import app
    return TestClient(app)

@pytest.fixture
def test_user(db):
    """Utilisateur de test"""
    user = User(email="test@example.com", ...)
    db.add(user)
    db.commit()
    return user
```

**Utilisation** :
```python
def test_login(client, test_user):
    # client et test_user sont automatiquement injectés
    response = client.post("/api/auth/login", json={
        "email": test_user.email,
        "password": "TestPass123"
    })
    assert response.status_code == 200
```

### Assertions Courantes

```python
# Égalité
assert actual == expected

# Contenu
assert "erreur" in response.json()["detail"]
assert response.json()["email"] == "test@example.com"

# Type
assert isinstance(result, dict)

# Exceptions
with pytest.raises(HTTPException):
    function_that_should_raise()

# Comparaisons
assert len(results) > 0
assert response.status_code == 200
assert user.id is not None
```

### Tester les Erreurs

```python
def test_login_wrong_password(client):
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "WrongPassword"
    })

    # Vérifier le code d'erreur
    assert response.status_code == 401

    # Vérifier le message
    assert "Invalid" in response.json()["detail"]
```

### Parameterized Tests

**Tester plusieurs cas avec le même code** :

```python
@pytest.mark.parametrize("email,password,expected_status", [
    ("valid@example.com", "StrongPass123", 200),  # OK
    ("invalid-email", "StrongPass123", 422),       # Email invalide
    ("valid@example.com", "weak", 400),            # Mot de passe faible
])
def test_register_validation(client, email, password, expected_status):
    response = client.post("/api/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Test"
    })
    assert response.status_code == expected_status
```

---

## 🎭 Tests E2E (Playwright)

### Structure d'un Test Playwright

```typescript
import { test, expect } from '@playwright/test';

test('user can register', async ({ page }) => {
  // 1. Naviguer
  await page.goto('http://localhost:5173/register');

  // 2. Remplir le formulaire
  await page.fill('[name="email"]', 'test@example.com');
  await page.fill('[name="password"]', 'TestPass123');
  await page.fill('[name="full_name"]', 'Test User');

  // 3. Soumettre
  await page.click('button[type="submit"]');

  // 4. Vérifier
  await expect(page).toHaveURL(/profile/);
  await expect(page.locator('h1')).toContainText('Welcome');
});
```

### Sélecteurs Courants

```typescript
// Par attribut name
page.fill('[name="email"]', 'test@example.com')

// Par ID
page.click('#submit-button')

// Par classe CSS
page.locator('.btn-primary')

// Par texte
page.getByText('Login')
page.getByRole('button', { name: 'Submit' })

// Par placeholder
page.getByPlaceholder('Enter your email')
```

### Attendre des Éléments

```typescript
// Attendre qu'un élément soit visible
await page.waitForSelector('.success-message');

// Attendre une navigation
await page.waitForURL(/dashboard/);

// Attendre un délai (éviter si possible)
await page.waitForTimeout(1000);

// Attendre une requête réseau
await page.waitForResponse(resp => resp.url().includes('/api/terms'));
```

### Tester les Erreurs

```typescript
test('shows error on invalid login', async ({ page }) => {
  await page.goto('http://localhost:5173/login');
  await page.fill('[name="email"]', 'wrong@example.com');
  await page.fill('[name="password"]', 'WrongPass123');
  await page.click('button[type="submit"]');

  // Vérifier message d'erreur
  await expect(page.locator('.error-message')).toBeVisible();
  await expect(page.locator('.error-message')).toContainText('Invalid');
});
```

---

## 📊 Couverture de Tests

### Mesurer la Couverture

```bash
# Backend
cd backend
pytest --cov=. --cov-report=html --cov-report=term

# Voir le rapport HTML
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Interpréter les Résultats

```
Name                 Stmts   Miss  Cover
----------------------------------------
api/auth.py             45      5    89%
api/terms.py            32      8    75%
db/postgres.py          28      2    93%
----------------------------------------
TOTAL                  105     15    86%
```

**Objectif** : ≥80% de couverture

**Zones rouges** : Lignes non testées (apparaissent en rouge dans le rapport HTML)

---

## 🎯 Stratégie de Tests

### Que Tester en Priorité ?

**P0 - Toujours tester** :
- ✅ Authentification (login, register, logout)
- ✅ CRUD opérations (create, read, update, delete)
- ✅ Validation des données (emails, mots de passe)
- ✅ Gestion des erreurs (404, 401, 500)

**P1 - Tester si important** :
- ⚡ Logique métier complexe
- ⚡ Calculs financiers/critiques
- ⚡ Intégrations externes (API, DB)

**P2 - Optionnel** :
- 🟡 Formatage de texte
- 🟡 Helpers simples
- 🟡 Constantes

### Pyramide de Tests

```
       /\
      /  \     E2E (peu, critiques)
     /----\    10 tests
    /      \
   /--------\  Integration (moyennement)
  /   50     \ 50 tests
 /------------\
/    Unit      \ Unit (beaucoup, rapides)
----------------
    200 tests
```

**Ratio recommandé** : 70% Unit, 20% Integration, 10% E2E

---

## 🚀 Bonnes Pratiques

### ✅ À Faire

```python
# ✅ Noms descriptifs
def test_login_with_valid_credentials_returns_token()

# ✅ Un assert par concept
def test_user_creation():
    user = create_user(...)
    assert user.id is not None
    assert user.email == "test@example.com"

# ✅ Tester les cas limites
def test_empty_email_rejected():
    response = client.post("/api/auth/register", json={"email": ""})
    assert response.status_code == 400
```

### ❌ À Éviter

```python
# ❌ Nom vague
def test_1()

# ❌ Trop de logique
def test_everything():
    # 100 lignes de test...

# ❌ Dépendances entre tests
def test_a():
    global user
    user = create_user()

def test_b():
    # Utilise 'user' du test précédent ❌
    assert user.email == "test@example.com"
```

---

## 🐛 Débugger des Tests qui Échouent

### Afficher plus d'Informations

```bash
# Mode verbose
pytest -v

# Afficher print() dans les tests
pytest -s

# Arrêter au premier échec
pytest -x

# Débugger avec pdb
pytest --pdb
```

### Exécuter un Seul Test

```bash
# Un fichier
pytest tests/test_auth.py

# Une classe
pytest tests/test_auth.py::TestLogin

# Un test spécifique
pytest tests/test_auth.py::TestLogin::test_login_success
```

### Comprendre les Erreurs

**Erreur fréquente** :
```
AssertionError: assert 401 == 200
```

**Signification** : Le code d'état HTTP est 401 (Unauthorized) au lieu de 200 (OK)

**Debug** :
```python
# Ajouter des prints
def test_login(client):
    response = client.post("/api/auth/login", json={...})
    print(f"Status: {response.status_code}")
    print(f"Body: {response.json()}")  # Voir le message d'erreur
    assert response.status_code == 200
```

---

## 📚 Ressources

**pytest** :
- Documentation : https://docs.pytest.org/
- Guide : https://realpython.com/pytest-python-testing/

**Playwright** :
- Documentation : https://playwright.dev/
- Exemples : https://playwright.dev/docs/writing-tests

**Coverage** :
- Guide : https://coverage.readthedocs.io/

---

**Retour** : [Plan d'Action Principal](../PLAN-ACTION-DEVELOPPEUR-JUNIOR.md)
