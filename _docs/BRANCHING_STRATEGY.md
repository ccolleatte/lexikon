# 🔀 Stratégie de Branching & Merge/Rebase - Lexikon

**Date**: 2025-11-16
**Auteur**: Claude Code
**Status**: Recommandations actives
**Version**: 1.0

---

## 📊 Analyse de l'État Actuel

### État du Repository
```
Total commits:        23
Branches actives:     1 (master)
Tags:                 4 (v0.0.1-dev, v0.1.0, v0.1.0-rc, v0.2.0)
Test coverage:        85%
Statut:               Production-ready MVP (v0.2.0)
```

### Chronologie des Releases
```
v0.0.1-dev (initial)     → Prototype
v0.1.0-rc               → Release candidate (TIER-1)
v0.1.0                  → Production-ready MVP
v0.2.0 (current HEAD)   → Documentation reorganization
```

### Observations Critiques
1. **Tous les commits sont sur `master`** → Risque zéro séparation
2. **Tags de release existent** → Mais pas d'historique de branches de release
3. **Roadmap en 4 tiers documentée** → Mais pas d'implémentation branch
4. **85% test coverage** → Besoin de protection pour les nouvelles features

---

## 🎯 Stratégie Recommandée: Git Flow Adapté

### Branches Permanentes

#### 1️⃣ **`master`** (Production)
- **Protection**: ✅ OBLIGATOIRE
- **Source de truth**: Dernière version stable en production
- **Merge from**: `release/` branches uniquement
- **Policy**:
  - ✅ Require PR review (2 approvals)
  - ✅ Require status checks (tests + linting)
  - ✅ Require branches to be up to date
  - ✅ Dismiss stale reviews

#### 2️⃣ **`develop`** (Intégration)
- **Protection**: ✅ RECOMMANDÉ
- **Source de truth**: Prochaine version (next release)
- **Merge from**: `feature/`, `bugfix/`, `hotfix/` branches
- **Policy**:
  - ✅ Require PR review (1 approval minimum)
  - ✅ Require status checks (tests + linting)
  - ✅ Auto-delete head branches after merge

---

## 🌿 Branches par Type de Tâche

### Pattern Naming: `<type>/<tier>-<description>`

```
feature/tier1-jwt-authentication
feature/tier2-oauth-integration
feature/tier3-error-tracking
feature/tier4-neo4j-evaluation

bugfix/critical-password-validation
bugfix/tier2-rate-limiting-edge-case

hotfix/security-cors-bypass
hotfix/production-payment-logic

release/v0.1.0
release/v0.2.0-hotfix-1
```

---

## 📋 Workflow par Type de Fonctionnalité

### 🟢 TIER-1 Features (BLOCKER - Critical Path)
**Format**: `feature/tier1-<description>`

**Exemple**: `feature/tier1-jwt-authentication`

#### Création
```bash
git checkout develop
git pull origin develop
git checkout -b feature/tier1-jwt-authentication
```

#### Développement
- ✅ Commits atomiques avec messages clairs
- ✅ Couvrir avec des tests (viser 90%+)
- ✅ Lancer `npm run test:coverage` localement avant commit
- ✅ **Pas de commits directement sur master**

#### Code Review & Merge
```
1. Push branch: git push -u origin feature/tier1-jwt-authentication
2. Créer PR sur develop (pas master)
3. Description du PR: Include acceptance criteria from TIER-1 doc
4. Reviewers: Min 2 approvals (lead + security person)
5. Checks:
   - ✅ Tests pass (80%+ coverage)
   - ✅ Linting passes
   - ✅ Type checking passes
6. Merge strategy: SQUASH + REBASE (voir détail ci-dessous)
```

#### Merge Decision Tree
```
Branch: feature/tier1-* → Merge TO: develop

Est-ce un BUGFIX dans une feature?
└─ OUI  → REBASE + MERGE (préserver historique commits logiques)
└─ NON  → SQUASH + MERGE (1 commit logique = 1 feature)

Après merge:
└─ AUTO-DELETE la branche (GitHub setting)
```

---

### 🟡 TIER-2 Features (IMPORTANT - MVP Viability)
**Format**: `feature/tier2-<description>`

**Exemple**: `feature/tier2-postgresql-persistence`

#### Workflow
```
Same as TIER-1 but:
- Min 1 approval (can be faster)
- Test coverage: 80% minimum
- Merge strategy: SQUASH + MERGE
```

---

### 🟠 TIER-3 Features (POLISH - Production Hardening)
**Format**: `feature/tier3-<description>`

**Exemple**: `feature/tier3-sentry-integration`

#### Workflow
```
Same as TIER-2 but:
- Can use REBASE + MERGE if cleanly separable
- Test coverage: 70% acceptable for non-critical paths
```

---

### 💚 TIER-4 & Post-Launch
**Format**: `feature/tier4-<description>`

**Exemple**: `feature/tier4-neo4j-evaluation`

#### Workflow
```
Same as TIER-3
- Lower review requirements
- Experimental code allowed (with @experimental comments)
```

---

### 🔴 Bugfixes (Production Issues)
**Format**: `bugfix/<description>` ou `hotfix/<description>`

#### Severity Levels

**HIGH (Production down)**
```
Branch: hotfix/critical-<description>
Merge to: master DIRECTLY (emergency protocol)
Approval: 1 (can be verbal in Slack)
Strategy: MERGE COMMIT (preserve hotfix history)
Process:
  1. After merge to master, IMMEDIATELY cherry-pick to develop
  2. git cherry-pick master-commit-sha
  3. Resolve any conflicts
  4. Push to develop
```

**MEDIUM (Feature broken)**
```
Branch: bugfix/<description>
Merge to: develop
Approval: 1
Strategy: REBASE + MERGE
```

**LOW (Minor issues)**
```
Branch: bugfix/<description>
Merge to: develop
Approval: 1
Strategy: SQUASH + MERGE
```

---

## 🔄 Merge vs Rebase Decision Matrix

| Situation | Strategy | Raison |
|-----------|----------|--------|
| Feature complete & tested | **SQUASH + MERGE** | 1 commit = 1 feature dans master |
| Bugfix avec commits logiques | **REBASE + MERGE** | Historique détaillé utile |
| Emergency hotfix | **MERGE COMMIT** | Préserver trace temporelle |
| Documentation update | **SQUASH + MERGE** | Pas besoin de commits détaillés |
| Refactoring large | **REBASE + MERGE** | Commits atomiques importants |
| DB migration | **REBASE + MERGE** | Ordre des migrations critique |

### Commandes Git Correspondantes

#### SQUASH + MERGE (Recommended for features)
```bash
git checkout develop
git pull origin develop
git merge --squash feature/tier1-jwt-authentication
git commit -m "feat(auth): Integrate JWT authentication

- Add JWT token generation with passlib
- Implement token refresh endpoints
- Add auth middleware for protected routes

Closes #123"

git push origin develop
```

#### REBASE + MERGE (For logical commits)
```bash
git checkout develop
git pull origin develop
git rebase -i feature/tier1-jwt-authentication  # Clean up commits if needed
git merge --ff-only feature/tier1-jwt-authentication
git push origin develop
```

#### MERGE COMMIT (For hotfixes only)
```bash
git checkout master
git pull origin master
git merge --no-ff hotfix/security-cors-bypass -m "merge: hotfix security CORS bypass

Closes #456"

git push origin master
git tag v0.1.1  # If applicable
git push origin v0.1.1

# Cherry-pick to develop
git checkout develop
git cherry-pick master-commit-sha
```

---

## 🛡️ Protection Rules par Branche

### `master` (STRICT)
```
✅ Require pull request reviews before merging
   └─ Dismiss stale pull request approvals: YES
   └─ Require code owner reviews: YES (create CODEOWNERS file)

✅ Require status checks to pass before merging
   └─ npm test (tests must pass)
   └─ npm run lint (linting must pass)
   └─ npm run check (type checking must pass)

✅ Require branches to be up to date before merging
   └─ Auto-update from base branch when new commits added

✅ Require linear history
   └─ Forces all merges to be MERGE COMMIT or REBASE

✅ Dismiss stale pull request approvals when new commits are pushed
```

### `develop` (MODERATE)
```
✅ Require pull request reviews before merging
   └─ Min 1 approval
   └─ Dismiss stale: YES

✅ Require status checks to pass
   └─ npm test
   └─ npm run lint
   └─ npm run check

✅ Auto-delete head branches after merge
   └─ Clean up feature branches automatically
```

---

## 📅 Workflow pour Release

### v0.1.0 → v0.1.1 (Bugfix Release)

```bash
# 1. Créer branche de release depuis develop
git checkout develop
git pull origin develop
git checkout -b release/v0.1.1

# 2. Versions bumps & changelog
# → Update package.json version: "0.1.1"
# → Update CHANGELOG.md
git add package.json CHANGELOG.md
git commit -m "chore(release): Bump to v0.1.1"

# 3. Créer PR vers master
git push -u origin release/v0.1.1
# → Créer PR: release/v0.1.1 → master

# 4. Après merge à master
git checkout master
git pull origin master
git tag -a v0.1.1 -m "Version 0.1.1 - Bugfix release"
git push origin v0.1.1

# 5. Synchroniser develop
git checkout develop
git merge --no-ff master  # Important: keep merge commit
git push origin develop
```

### v0.1.0 → v0.2.0 (Major Release)

```
Same process but:
- Use release/v0.2.0 branch
- Ensure all TIER-2 features are merged to develop first
- Longer testing phase in release/ branch
```

---

## ⚠️ Situations Dangereuses & Solutions

### Situation 1: Master et Develop Divergent
**Symptôme**: Master a des commits que develop n'a pas (ou vice-versa)

**Solution**:
```bash
# 1. Diagnostic
git log master --oneline --not develop
git log develop --oneline --not master

# 2. Si hotfix sur master: cherry-pick vers develop
git checkout develop
git pull origin develop
git cherry-pick <hotfix-commit-sha>
git push origin develop

# 3. Si accidentellement fusionné incomplet: Revert
git revert -m 1 <bad-merge-commit>
git push origin develop
```

### Situation 2: Feature Branch Trop Vieille
**Symptôme**: feature/tier1-old a divergé depuis 10 jours, develop a beaucoup changé

**Solution**:
```bash
# 1. Rebase the feature onto develop
git checkout feature/tier1-old
git fetch origin
git rebase origin/develop

# 2. Résoudre conflits si nécessaire
# ... résoudre conflits ...
git add <files>
git rebase --continue

# 3. Force push (ATTENTION: Feature branch seulement!)
git push origin feature/tier1-old --force-with-lease

# 4. Tests locaux
npm run test
npm run lint
```

### Situation 3: Accidental Commit on Master
**Symptôme**: Oups! `git push` depuis master par erreur

**Solution**:
```bash
# 1. STOP - ne pas faire git push --force
git log master origin/master  # Vérifie quoi a été poussé

# 2. Créer nouvelle branche avec le commit
git branch feature/recover-accidental-commit <commit-sha>

# 3. Reset master
git reset --hard origin/master
git push origin master --force-with-lease

# 4. Ouvrir PR pour feature/recover-accidental-commit → develop
```

---

## ✅ Checklist Pre-Merge

**À faire AVANT de merger une PR**:

### Code Quality
- [ ] Tests pass locally: `npm run test:coverage`
- [ ] Linting passes: `npm run lint`
- [ ] Type checking passes: `npm run check`
- [ ] No console.log() left (except intentional logging)
- [ ] No TODO comments without ticket reference

### Tests
- [ ] New tests added for new code
- [ ] No tests skipped (`.skip`, `.only` removed)
- [ ] Coverage maintained or improved (min 80%)
- [ ] E2E tests pass if UI changed

### Security
- [ ] No hardcoded secrets/passwords
- [ ] No direct `eval()` calls
- [ ] No SQL injection risks (using Pydantic validation)
- [ ] CORS properly configured
- [ ] Dependencies checked: `npm audit`

### Documentation
- [ ] Code comments for complex logic
- [ ] JSDoc/docstrings for functions
- [ ] CHANGELOG updated (if user-facing change)
- [ ] ADR updated (if architectural impact)

### Commit Message
- [ ] Follows convention: `type(scope): subject`
  - Types: feat, fix, docs, style, refactor, test, chore
  - Example: `feat(auth): Add JWT refresh token endpoint`
- [ ] Includes ticket reference: `Closes #123`

---

## 🎓 Training: Exemplaire Workflow

### Implémentation d'une TIER-1 Feature

```bash
# ===== DAY 1: SETUP =====
cd /path/to/lexikon
git checkout develop
git pull origin develop

# Créer feature branch
git checkout -b feature/tier1-jwt-authentication

# ===== DAYS 2-3: DEVELOPMENT =====
# Code, commit, test
git add backend/auth/jwt.py
git commit -m "feat(auth): Add JWT token generation

- Implement access token generation with 15min expiry
- Implement refresh token generation with 7 day expiry
- Use PyJWT library with HS256 algorithm"

npm run test:coverage  # 85% coverage for auth module
npm run lint
npm run check

# Repeat for each feature component...

# ===== DAY 4: CLEANUP & PUSH =====
# Squash related commits if needed
git rebase -i develop

git push -u origin feature/tier1-jwt-authentication

# ===== GitHub Web UI =====
# 1. Create PR: feature/tier1-jwt-authentication → develop
# 2. Fill description:
#    - Which TIER-1 task does this complete?
#    - Testing done?
#    - Any concerns?
# 3. Request reviewers (2 minimum)
# 4. Address review comments with new commits
# 5. Approve merge

# ===== DAY 5: MERGE =====
# After 2 approvals, merge in GitHub UI
# Select: "Squash and merge"
# Auto-delete branch after merge

# ===== LOCAL SYNC =====
git checkout develop
git pull origin develop
git branch -d feature/tier1-jwt-authentication
```

---

## 📈 Metriques de Santé du Repository

**À monitorer mensuellement**:

| Métrique | Objectif | Alerte |
|----------|----------|--------|
| Avg branch lifetime | < 7 days | > 14 days |
| PR review time | < 24h | > 48h |
| Master deployment frequency | 2x/week | < 1x/week |
| Test coverage master | 80%+ | < 75% |
| Linting violations | 0 | > 5 |
| Mean time to recovery | < 1h | > 2h |

---

## 🚨 CI/CD Integration (GitHub Actions)

### Fichier requis: `.github/workflows/test.yml`

```yaml
name: Test & Lint

on:
  push:
    branches: [develop, master]
  pull_request:
    branches: [develop, master]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm run test:coverage

      - name: Run linting
        run: npm run lint

      - name: Type checking
        run: npm run check

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/coverage-final.json
```

---

## 🎯 Roadmap de Mise en Place

### Week 1: Setup Infrastructure
- [ ] Enable branch protection on master
- [ ] Enable branch protection on develop (lighter)
- [ ] Create `.github/workflows/test.yml`
- [ ] Create `CODEOWNERS` file

### Week 2: Team Training
- [ ] Share this guide with team
- [ ] Walk through example workflow
- [ ] Practice with non-critical feature branch
- [ ] Document team-specific conventions

### Week 3: Monitor & Iterate
- [ ] Start TIER-2 features on branches
- [ ] Monitor PR metrics
- [ ] Adjust if needed

### Week 4+: Optimize
- [ ] Refine based on team feedback
- [ ] Update ADRs if needed
- [ ] Document special cases

---

## 📞 FAQ

### Q: Combien de branches feature simultanées?
**A**: 1-2 par développeur max. Plus = trop compliqué à gérer.

### Q: Quand créer une branche release/?
**A**: Quand ready à release. Typiquement:
- TIER-1 complete → v0.1.0-rc
- TIER-2 complete → v0.1.1 ou v0.2.0

### Q: Quand force push?
**A**: JAMAIS sur master. Seulement sur feature/ branches avec `--force-with-lease`.

### Q: Que faire si je supprime ma branche par erreur?
**A**:
```bash
git reflog  # Find the commit
git checkout -b recovery-branch <commit-sha>
```

### Q: Comment récupérer un code d'une branche supprimée?
**A**: Voir réponse précédente - git reflog est ton ami.

---

## 📚 Ressources

- **Git Flow** : https://nvie.com/posts/a-successful-git-branching-model/
- **Conventional Commits** : https://www.conventionalcommits.org/
- **GitHub Protected Branches** : https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches

---

**Dernière mise à jour**: 2025-11-16
**Prochaine révision**: Après TIER-1 completion (2025-11-23)
