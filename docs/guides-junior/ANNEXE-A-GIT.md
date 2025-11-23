# Annexe A - Commandes Git Essentielles
## Guide Rapide pour Développeur Junior

---

## 🌿 Workflow Git Flow

### Branches Principales

```
master (production)
  │
  ├─ develop (intégration)
  │   │
  │   ├─ feature/ma-fonctionnalite
  │   ├─ feature/autre-fonctionnalite
  │   └─ bugfix/correction-bug
  │
  └─ hotfix/urgence-production
```

---

## 📝 Commandes de Base

### Créer une Feature Branch

```bash
# 1. Se mettre sur develop et récupérer les dernières modifications
git checkout develop
git pull origin develop

# 2. Créer une nouvelle branche
git checkout -b feature/nom-de-ma-feature

# 3. Travailler sur le code...
# (éditer des fichiers)

# 4. Voir les modifications
git status
git diff

# 5. Ajouter les fichiers modifiés
git add .
# OU spécifiquement :
git add backend/main.py src/lib/components/Button.svelte

# 6. Créer un commit
git commit -m "feat: Description de la fonctionnalité"

# 7. Pousser vers GitHub
git push -u origin feature/nom-de-ma-feature
```

### Mettre à Jour sa Branche

```bash
# Récupérer les modifications de develop
git checkout develop
git pull origin develop

# Revenir sur sa branche
git checkout feature/nom-de-ma-feature

# Intégrer les modifications de develop
git merge develop

# OU (préféré pour garder un historique propre)
git rebase develop
```

---

## 🔀 Résolution de Conflits

### Quand un Conflit Arrive

```bash
$ git merge develop
Auto-merging backend/main.py
CONFLICT (content): Merge conflict in backend/main.py
Automatic merge failed; fix conflicts and then commit the result.
```

### Étapes de Résolution

**1. Voir les fichiers en conflit**
```bash
git status
# Affiche :
# Unmerged paths:
#   both modified:   backend/main.py
```

**2. Ouvrir le fichier en conflit**
```python
<<<<<<< HEAD
# Votre version
from fastapi import FastAPI
=======
# Version de develop
from fastapi import FastAPI, HTTPException
>>>>>>> develop
```

**3. Résoudre manuellement**
```python
# Garder les deux imports
from fastapi import FastAPI, HTTPException
```

**4. Marquer comme résolu**
```bash
git add backend/main.py
git commit -m "merge: Resolve conflict in main.py"
```

### Annuler un Merge en Cours

```bash
# Si vous êtes perdu pendant un merge
git merge --abort

# Revient à l'état avant le merge
```

---

## ⏮️ Annuler des Modifications

### Annuler des Modifications Non Commitées

```bash
# Annuler les modifications d'un fichier
git checkout -- backend/main.py

# Annuler toutes les modifications
git reset --hard HEAD
```

### Annuler le Dernier Commit (non pushé)

```bash
# Garder les modifications en local
git reset --soft HEAD~1

# Supprimer les modifications
git reset --hard HEAD~1
```

### Modifier le Dernier Commit

```bash
# Ajouter des fichiers oubliés
git add fichier-oublie.py
git commit --amend --no-edit

# Changer le message du commit
git commit --amend -m "Nouveau message"
```

⚠️ **Ne jamais amender un commit déjà pushé !**

---

## 🏷️ Conventions de Messages de Commit

### Format Standard

```
type(scope): description courte

Description longue optionnelle

Fixes #123
```

### Types de Commits

| Type | Usage | Exemple |
|------|-------|---------|
| `feat` | Nouvelle fonctionnalité | `feat(auth): Add JWT authentication` |
| `fix` | Correction de bug | `fix(api): Correct CORS configuration` |
| `docs` | Documentation | `docs: Update README with setup guide` |
| `test` | Ajout/modification de tests | `test(auth): Add login endpoint tests` |
| `refactor` | Refactoring (pas de changement fonctionnel) | `refactor(db): Simplify query logic` |
| `chore` | Maintenance | `chore: Update dependencies` |
| `style` | Formatage | `style: Fix linting errors` |

### Exemples de Bons Commits

```bash
# ✅ Bon : Court et descriptif
git commit -m "feat(auth): Add password reset functionality"

# ✅ Bon : Avec description longue
git commit -m "fix(db): Prevent connection leak

Sessions were not being closed properly, leading to
connection pool exhaustion after ~100 requests.

Fixes #456"

# ❌ Mauvais : Trop vague
git commit -m "fix bug"

# ❌ Mauvais : Trop long dans la première ligne
git commit -m "Add a new feature that allows users to reset their password by clicking on a link sent to their email address"
```

---

## 🔍 Commandes Utiles

### Voir l'Historique

```bash
# Historique simple
git log --oneline

# Historique avec graphe
git log --oneline --graph --all

# Historique d'un fichier
git log --follow backend/main.py

# Chercher dans les commits
git log --grep="auth"
```

### Voir les Différences

```bash
# Différences non commitées
git diff

# Différences entre branches
git diff develop..feature/ma-branch

# Différences d'un commit spécifique
git show abc1234
```

### Stasher des Modifications

```bash
# Mettre de côté temporairement
git stash

# Voir les stash
git stash list

# Réappliquer le dernier stash
git stash pop

# Réappliquer un stash spécifique
git stash apply stash@{1}
```

---

## 🚨 Commandes d'Urgence

### J'ai Commité sur la Mauvaise Branche

```bash
# 1. Noter le hash du commit
git log --oneline -1
# abc1234 feat: Ma fonctionnalité

# 2. Annuler le commit (garder les modifications)
git reset --soft HEAD~1

# 3. Aller sur la bonne branche
git checkout feature/la-bonne-branche

# 4. Recommiter
git add .
git commit -m "feat: Ma fonctionnalité"
```

### J'ai Pushé des Secrets (.env) par Erreur

```bash
# ⚠️ Ne suffit PAS de juste supprimer le fichier !
# Le fichier est dans l'historique Git

# Solution 1 : Supprimer de l'historique (DANGEREUX)
git filter-branch --index-filter 'git rm --cached --ignore-unmatch backend/.env' HEAD

# Solution 2 : Utiliser BFG Repo-Cleaner
# https://rtyley.github.io/bfg-repo-cleaner/

# Solution 3 (RECOMMANDÉE) :
# 1. Changer IMMÉDIATEMENT les secrets (mots de passe, clés API)
# 2. Ajouter .env au .gitignore
# 3. Créer un nouveau commit
git add .gitignore
git commit -m "chore: Add .env to gitignore"
```

### J'ai Tout Cassé, Je Veux Revenir en Arrière

```bash
# Revenir au dernier commit
git reset --hard HEAD

# Revenir à l'état du remote
git fetch origin
git reset --hard origin/develop

# Revenir à un commit spécifique
git reset --hard abc1234
```

---

## 📚 Ressources

**Documentation Officielle** :
- Git Book : https://git-scm.com/book/en/v2
- Git Flow : https://nvie.com/posts/a-successful-git-branching-model/

**Outils Interactifs** :
- Learn Git Branching : https://learngitbranching.js.org/
- Visualiser Git : https://git-school.github.io/visualizing-git/

**Cheat Sheets** :
- https://education.github.com/git-cheat-sheet-education.pdf

---

**Retour** : [Plan d'Action Principal](../PLAN-ACTION-DEVELOPPEUR-JUNIOR.md)
