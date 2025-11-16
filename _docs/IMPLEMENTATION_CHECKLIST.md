# ✅ Checklist Implémentation Stratégie Branching

**Date**: 2025-11-16
**Priorité**: 🔴 HIGH (TIER-1 blocker)
**Effort**: 4-6 heures (une personne)
**Deadline**: Avant début TIER-2

---

## 📋 Phase 1: GitHub Configuration (30 min)

### A. Créer branche `develop`

```bash
git checkout -b develop master
git push -u origin develop
```

**Checklist**:
- [ ] Branche develop créée et pushée
- [ ] Visible dans GitHub UI
- [ ] Tous les développeurs peuvent la voir

---

### B. Protéger `master` (10 min)

**Settings → Branches → Add rule**

```
Branch name pattern: master
```

Cocher:
- [ ] Require a pull request before merging
  - [ ] Require approvals: 2
  - [ ] Dismiss stale pull request approvals: YES
  - [ ] Require review from Code Owners: YES (optionnel)

- [ ] Require status checks to pass before merging
  - [ ] Require branches to be up to date before merging: YES
  - [ ] Status checks that must pass:
    - [ ] `npm test` (nom du check exact)
    - [ ] `npm run lint`
    - [ ] `npm run check`

- [ ] Require linear history: NO (optional, can enable later)
- [ ] Include administrators: YES (toi-même inclus)
- [ ] Allow force pushes: ❌ NO
- [ ] Allow deletions: ❌ NO

**Validations**:
- [ ] Test rule: Try to push directly to master (should fail)
- [ ] Try to merge PR without approval (should fail)

---

### C. Protéger `develop` (10 min)

**Settings → Branches → Add rule**

```
Branch name pattern: develop
```

Cocher (lighter than master):
- [ ] Require a pull request before merging
  - [ ] Require approvals: 1
  - [ ] Dismiss stale pull request approvals: YES

- [ ] Require status checks to pass before merging
  - [ ] Same 3 checks as master

- [ ] Automatically delete head branches: YES
- [ ] Include administrators: NO (allow you to override if needed)
- [ ] Allow deletions: ❌ NO

---

### D. Create CODEOWNERS file (5 min)

**File**: `.github/CODEOWNERS`

```
# Default reviewers for all PRs
* @your-github-username

# Tier-specific reviewers (optional)
docs/roadmap/ @your-github-username
backend/ @your-github-username
src/ @your-github-username
```

**Checklist**:
- [ ] `.github/CODEOWNERS` created
- [ ] Contains your GitHub username
- [ ] Pushed to develop

---

## 📋 Phase 2: CI/CD Setup (1 hour)

### A. Create GitHub Actions workflow

**File**: `.github/workflows/test-and-lint.yml`

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
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm run test -- --coverage

      - name: Run linting
        run: npm run lint

      - name: Type checking
        run: npm run check

      - name: Upload coverage (optional)
        if: always()
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/coverage-final.json
          fail_ci_if_error: false
```

**Checklist**:
- [ ] `.github/workflows/test-and-lint.yml` created
- [ ] File pushed to develop
- [ ] Actions tab shows workflow running
- [ ] Test job passes on develop
- [ ] Linting job passes
- [ ] Type checking passes

---

### B. Backend CI/CD (if needed)

**File**: `.github/workflows/backend-test.yml`

```yaml
name: Backend Tests

on:
  push:
    branches: [develop, master]
    paths:
      - 'backend/**'
  pull_request:
    branches: [develop, master]
    paths:
      - 'backend/**'

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          cache: 'pip'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Run tests
        run: |
          cd backend
          pytest -v --cov

      - name: Lint
        run: |
          cd backend
          ruff check .
```

**Checklist**:
- [ ] `.github/workflows/backend-test.yml` created (if applicable)
- [ ] File pushed to develop
- [ ] Backend tests pass

---

## 📋 Phase 3: Documentation (30 min)

### A. Create BRANCHING_STRATEGY.md (already done)

**File**: `_docs/BRANCHING_STRATEGY.md`

**Checklist**:
- [ ] Document exists and is comprehensive
- [ ] Team has read and understands it
- [ ] Linked from README.md

---

### B. Update README.md

Add section:

```markdown
## 🔀 Development Workflow

We use **Git Flow** branching model:
- **master**: Production-ready releases only
- **develop**: Integration branch for next release
- **feature/**: Feature branches

See [BRANCHING_STRATEGY.md](_docs/BRANCHING_STRATEGY.md) for detailed workflow.

### Quick Start for Developers

```bash
# 1. Create feature branch
git checkout develop
git pull origin develop
git checkout -b feature/tier1-your-feature

# 2. Develop & test
npm run test:coverage  # Must pass
npm run lint           # Must pass
npm run check          # Must pass

# 3. Push & create PR
git push -u origin feature/tier1-your-feature
# Create PR on GitHub (base: develop)

# 4. After merge
git checkout develop
git pull origin develop
```

See [BRANCHING_STRATEGY.md](_docs/BRANCHING_STRATEGY.md) for full details.
```

**Checklist**:
- [ ] README.md updated with development section
- [ ] Link to BRANCHING_STRATEGY.md works
- [ ] Instructions are clear

---

### C. Create .gitignore update (if needed)

Check existing `.gitignore` for:
- [ ] `node_modules/` ignored
- [ ] `.env` ignored (never commit secrets!)
- [ ] `dist/`, `build/` ignored
- [ ] Coverage reports ignored

If missing, add to `.gitignore`:
```
node_modules/
.env
.env.local
.env.*.local
dist/
build/
coverage/
.DS_Store
.vscode/
.idea/
*.swp
*.swo
__pycache__/
*.pyc
.pytest_cache/
venv/
```

**Checklist**:
- [ ] `.gitignore` is comprehensive
- [ ] No sensitive files can be accidentally committed

---

## 📋 Phase 4: Team Setup (1 hour)

### A. Share documentation

**Channels**:
- [ ] Send BRANCHING_STRATEGY.md to team (Slack, email)
- [ ] Post link in README
- [ ] Add to team wiki/docs

**Checklist**:
- [ ] All developers have read it
- [ ] Questions addressed
- [ ] Understood the branching names convention

---

### B. Training session (30 min)

Walk through example:

```bash
# Show the workflow
git log --graph --oneline --all master develop

# Create example branch
git checkout -b example/feature-demo develop

# Make a fake change
echo "# Example" >> README.md
git add README.md
git commit -m "docs(example): Add example section"

# Push and show PR interface
git push -u origin example/feature-demo

# Show GitHub PR creation
# → Merge it to demonstrate
# → Show auto-delete

# Clean up
git checkout develop
git pull origin develop
```

**Checklist**:
- [ ] Team comfortable with workflow
- [ ] Questions answered
- [ ] First real feature branch created

---

### C. Setup git hooks (optional, recommended)

**File**: `.git/hooks/pre-commit`

```bash
#!/bin/bash
# Run linting before commit

npm run lint --silent
LINT_RESULT=$?

if [ $LINT_RESULT != 0 ]; then
  echo "❌ Linting failed. Fix errors and try again."
  exit 1
fi

echo "✅ Pre-commit hook passed"
exit 0
```

**Setup**:
```bash
chmod +x .git/hooks/pre-commit
```

**Checklist**:
- [ ] Pre-commit hook installed (optional)
- [ ] Prevents committing with lint errors
- [ ] Team knows about it

---

## 📋 Phase 5: First Real Usage (2+ hours)

### Start TIER-1 Feature: JWT Authentication

**Estimated**: 3-4 days

```bash
# Day 1
git checkout develop
git pull origin develop
git checkout -b feature/tier1-jwt-authentication

# Days 2-3: Development
# [code commits...]

# Day 4: Push & PR
git push -u origin feature/tier1-jwt-authentication

# Create PR on GitHub:
# Title: feat(auth): Implement JWT authentication
# Description:
# - Closes #XXX (from TIER-1 doc)
# - Implements task 1-1 and 1-2
# - Tests pass with 90% coverage
# - No breaking changes

# Request 2 reviewers
# Address comments with new commits
# Merge to develop (squash + merge)
```

**Checklist**:
- [ ] Feature branch created from develop
- [ ] Code follows conventions
- [ ] PR created with good description
- [ ] 2 approvals obtained
- [ ] Merged successfully to develop
- [ ] Branch auto-deleted
- [ ] Local develop synced: `git pull origin develop`

---

## 📋 Phase 6: Monitoring (ongoing)

### Weekly Metrics Check

**Every Monday**:
- [ ] Review PRs merged in last week
  - Average time from PR creation to merge: target < 24h
  - Number of review rounds: target 1-2
- [ ] Check test coverage: must be ≥ 80%
- [ ] Check for any force pushes (should be 0)
- [ ] Verify no commits directly to master

**Checklist**:
- [ ] Metrics tracked
- [ ] Issues addressed quickly
- [ ] Team feedback incorporated

---

## 🎯 Success Criteria

### Phase 1-3: Infrastructure Ready
- [ ] master protected with 2 approvals required
- [ ] develop protected with 1 approval required
- [ ] GitHub Actions workflows passing
- [ ] Documentation complete and linked

### Phase 4: Team Ready
- [ ] All developers trained
- [ ] First feature branch created successfully
- [ ] At least one PR merged to develop

### Phase 5+: Sustainable
- [ ] Zero direct commits to master
- [ ] All PRs reviewed before merge
- [ ] Test coverage maintained ≥ 80%
- [ ] Release process smooth and repeatable

---

## 🚨 Common Issues & Solutions

### "My branch is out of date with develop"

```bash
git checkout feature/my-feature
git fetch origin
git rebase origin/develop
npm run test  # Verify nothing broke
git push origin feature/my-feature --force-with-lease
```

### "I accidentally committed to master"

```bash
# Don't panic! Do this:
git reset --hard origin/master
git checkout -b feature/recover-my-change <commit-sha>  # from git reflog
git push -u origin feature/recover-my-change
# Then create normal PR for the feature
```

### "My PR has conflicts"

```bash
git checkout feature/my-feature
git fetch origin
git rebase origin/develop
# Fix conflicts in your editor
git add .
git rebase --continue
git push origin feature/my-feature --force-with-lease
```

---

## 📞 Contacts & Support

- **Questions sur workflow**: See BRANCHING_STRATEGY.md
- **GitHub issues**: Use GitHub project board
- **Urgent problems**: Slack the team lead

---

**Created**: 2025-11-16
**Last updated**: 2025-11-16
**Status**: Ready for implementation
