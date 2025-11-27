# 🔒 Security Scanning & Vulnerability Management

**Status:** Active Production
**Last Updated:** 2025-11-27
**Responsible Team:** DevOps, Security

---

## Overview

Lexikon implements a **three-layer security scanning strategy** using automated tools integrated into the CI/CD pipeline:

| Layer | Tool | Purpose | Trigger |
|-------|------|---------|---------|
| **1. SAST** | Semgrep | Static code analysis (OWASP Top 10, CWE) | Every PR, Daily schedule |
| **2. Dependencies** | Dependabot + npm/pip-audit | Vulnerable dependency detection | Weekly (Dependabot), Every PR (audit) |
| **3. Code Review** | GitHub Security Dashboard | Central vulnerability tracking | Continuous |

---

## Workflow Triggers

### Automatic Security Scans

The `.github/workflows/security.yml` runs automatically on:

1. **Schedule**: Daily at **2 AM UTC**
   - Full Semgrep SAST scan
   - Complete dependency audit
   - All checks run independently

2. **Pull Requests** to `develop` or `master`
   - Semgrep SAST
   - Dependency review (Dependabot)
   - npm audit (frontend)
   - pip-audit (backend)
   - Fails PR if HIGH severity found ❌

3. **Push to develop**
   - Same as PR but non-blocking for visibility

4. **Manual Trigger** (`workflow_dispatch`)
   - Developers can trigger manually from GitHub UI
   - **Path**: Actions → Security Scanning → Run workflow

---

## Tool Configuration

### 1. Semgrep SAST

**What it does:** Static code analysis scanning for security vulnerabilities, code quality issues, and OWASP Top 10 patterns.

**Configuration:**
- **Rulesets:**
  - `p/security-audit` - Security best practices
  - `p/owasp-top-ten` - OWASP Top 10 vulnerabilities
  - `p/typescript` - TypeScript-specific checks
  - `p/nodejs` - Node.js security patterns
  - `p/python` - Python security patterns

- **Exclusions:** See `.semgrepignore`
  - `node_modules/`, `backend/.venv/` - Dependencies
  - `*.test.ts`, `test_*.py` - Test code
  - `.github/workflows/` - CI/CD (already trusted)
  - Build artifacts: `.svelte-kit/`, `dist/`, `build/`

- **SARIF Upload:** Findings uploaded to GitHub Security Dashboard
  - View: **Code Security & Analysis** tab on repository

**Result Interpretation:**

```
Semgrep scan complete

✅ 0 findings          → PASS (merge allowed)
⚠️ 1-5 findings        → WARNING (review findings)
❌ High/Critical level → FAIL (must fix)
```

### 2. Dependabot

**What it does:** Automated dependency vulnerability detection and update PRs.

**Configuration:** `.github/dependabot.yml`
- **npm** (frontend): Weekly Monday 2 AM
- **pip** (backend): Weekly Monday 3 AM
- **GitHub Actions**: Monthly Monday 4 AM
- **Limit:** Max 5 open PRs per ecosystem
- **Labels:** "dependencies", "frontend"/"backend"/"ci-cd", "security"

**Workflow:**
1. Dependabot detects vulnerable package version
2. Creates PR with dependency update + security details
3. Automatic checks run (test-and-lint, backend-test, e2e-tests)
4. If all checks pass → merge (fast track)
5. If checks fail → investigate and fix version conflicts

### 3. npm audit

**What it does:** Frontend dependency vulnerability scanning.

**Command (local):**
```bash
npm audit
npm audit --audit-level=high    # Only show HIGH+ severity
```

**BLOQUANT Policy:**
- Fails PR if HIGH or CRITICAL severity found
- Force-fix strategy: `npm audit fix --force` (use carefully)

**Fixing Vulnerabilities:**

```bash
# Automatic fix (first try)
npm audit fix

# Interactive fix (choose which to update)
npm audit fix --force

# Manual fix: Update specific package
npm install package-name@latest

# Check results
npm audit
```

### 4. pip-audit

**What it does:** Backend Python dependency vulnerability scanning.

**Installation:** Already in `backend/requirements.txt`
```
pip-audit>=2.6.0
```

**Command (local):**
```bash
cd backend
pip-audit                                    # Show all vulnerabilities
pip-audit --vulnerability-service osv       # Use OSV vulnerability database
pip-audit --format json > audit.json         # Export results
```

**BLOQUANT Policy:**
- Fails PR if any vulnerability found
- CLI exit code: 0 (safe), 1 (vulnerable)

**Fixing Vulnerabilities:**

```bash
cd backend

# Identify vulnerable package
pip-audit

# Update that specific package
pip install package-name --upgrade

# Verify fix
pip-audit
```

---

## GitHub Security Dashboard

### Accessing Results

**Code Security & Analysis** tab shows:

1. **Code Scanning** (Semgrep results)
   - Alert: Type + File + Line
   - Severity: Critical, High, Warning, Note
   - Auto-dismiss false positives
   - Track remediation status

2. **Dependabot Alerts**
   - Vulnerable package name + version
   - Suggested fix (usually auto-PR)
   - CVSS score + severity
   - Link to security advisory

3. **Secret Scanning** (if enabled)
   - Detected exposed API keys, tokens, credentials
   - Must be immediately rotated

### Interpreting Alerts

```
⛔ CRITICAL (CVSS 9.0-10.0)
├─ Immediate action required
├─ May allow complete system compromise
└─ Affects: Direct code + production

🔴 HIGH (CVSS 7.0-8.9)
├─ Priority fix before release
├─ Significant impact on security
└─ Affects: Direct code + dependencies

🟠 MEDIUM (CVSS 4.0-6.9)
├─ Should be fixed in next release
└─ Limited impact or workarounds exist

🟡 LOW (CVSS 0.1-3.9)
├─ Minor or theoretical risk
└─ Address opportunistically
```

---

## Fixing Vulnerabilities

### Triage Process

1. **Receive Alert**
   - Semgrep finding in PR check
   - Dependabot PR created
   - Manual `npm audit` / `pip-audit` run

2. **Assess Impact**
   - Is it in production code or dev-only?
   - Affected package: direct dependency or transitive?
   - Severity: CRITICAL/HIGH = urgent, MEDIUM/LOW = next sprint

3. **Fix Strategy**

   **For Dependencies:**
   ```bash
   # Frontend
   npm audit fix              # Auto-fix safe upgrades
   npm audit fix --force      # Allow breaking changes (test required!)

   # Backend
   pip install --upgrade package-name  # Manual update
   ```

   **For Code Issues (Semgrep):**
   - Review finding details in GitHub UI
   - Apply suggested fix
   - Create commit: `fix(security): Address Semgrep finding #123`
   - Run local verification: `npm run test:coverage`

4. **Verify Fix**
   - Re-run security scan: `npm audit`, `pip-audit`
   - Run full test suite: `npm run test:ci`, `npm run test:e2e`
   - For dependencies: Ensure no breaking changes

5. **Close/Dismiss Alert**
   - Merge fix PR → alert auto-closes
   - False positive? → Dismiss with reason in GitHub UI

---

## False Positives & Exceptions

### Handling False Positives

**In Semgrep:**
- False positive in Semgrep result?
- Add to `.semgrepignore` if pattern-based
- OR add code comment: `# nosemgrep: rule-id` (Semgrep comment syntax)
- Document reason in commit message

**In Dependabot:**
- Security issue not applicable to your code?
- Comment on PR: `@dependabot close` (closes PR)
- OR: `@dependabot recreate` (retry after fix)

### Emergency Override (Last Resort)

⚠️ **Only in true emergencies** (e.g., zero-day vulnerability, system down):

1. Merge without fixing
2. Create issue: `SECURITY: <vulnname> override justification`
3. Plan remediation: set deadline (≤2 weeks)
4. Document in PR: why override was necessary

**This is tracked and audited.**

---

## Local Security Scanning

### Before Committing

```bash
# Frontend
npm audit
npm run test:coverage

# Backend
cd backend
pip-audit
python -m pytest --cov=src

# Type checking
npm run check  # TypeScript
mypy backend/  # Python
```

### Full Local Verification

```bash
# Run all local checks (mirrors CI)
npm run lint
npm run test:ci
npm run test:e2e:smoke

# Manual Semgrep (if you have it installed)
semgrep --config p/security-audit src/ backend/
```

---

## Operational Procedures

### Daily Operations

**Morning (Check overnight scans):**
1. Review GitHub **Security tab** for new alerts
2. Prioritize any CRITICAL issues
3. Assign to team member if applicable
4. Update issue tracker if needed

**When Creating PR:**
- Ensure security checks pass before marking ready
- Review security tab comments on your PR
- If Semgrep finding: investigate, don't dismiss without understanding

### Weekly Operations

**Monday (Dependabot Day):**
- New dependency PRs likely created
- Review and test each PR
- Merge low-risk security updates quickly
- Flag high-risk changes for discussion

**End of Sprint:**
- Review **Dependabot Alert** list
- Ensure no HIGH/CRITICAL unaddressed
- Archive resolved alerts

---

## Troubleshooting

### Semgrep Not Detecting Issue

**Problem:** Known vulnerability not found by Semgrep
- Semgrep has limited coverage (not exhaustive)
- Solution: Enable additional rulesets in `security.yml`
- Fallback: Rely on dependency scanning (Dependabot + npm/pip-audit)

### npm audit Showing False Positives

**Problem:** `npm audit` says vulnerable, but unaffected code path

```bash
# View detailed advisory
npm audit --detail

# If truly false positive, force install
npm install package@version --save --force
```

### Dependabot PR Failing Tests

**Problem:** Dependabot upgrade breaks tests

```bash
# Test locally before approving
npm install package@version-from-pr
npm run test:ci

# If unfixable: close PR with reason
# @dependabot recreate (after you fix the issue)
```

### pip-audit Slow or Hanging

**Problem:** pip-audit takes 5+ minutes

```bash
# Check your internet connection
# Or use simpler config:
pip-audit --skip-editable

# If OSV service down, use alternative:
pip-audit --vulnerability-service pypa
```

---

## Performance & Reliability

| Check | Runtime | Frequency | Parallelized |
|-------|---------|-----------|--------------|
| Semgrep | 2-4 min | Every PR, daily | Yes (multiple files) |
| Dependabot | N/A | Weekly auto | N/A (GitHub service) |
| npm audit | 30 sec | Every PR | N/A (single package tree) |
| pip-audit | 1-2 min | Every PR | N/A (single package tree) |

**Total CI runtime impact:** ~5-7 minutes added (all in parallel)

---

## Related Documentation

- **Deployment Guide:** `DEPLOYMENT_HOSTINGER.md`
- **CI/CD Workflows:** `.github/workflows/`
- **Code Quality:** `README.md` → Testing section
- **Environment Setup:** `.env.example`, `QUICKSTART.md`

---

## Contacts & Support

- **Semgrep Issues:** Refer to https://semgrep.dev/docs
- **Dependabot:** GitHub documentation https://docs.github.com/en/code-security/dependabot
- **npm audit:** `npm help audit` or https://docs.npmjs.com/cli/v9/commands/npm-audit
- **pip-audit:** `pip-audit --help` or https://github.com/pypa/pip-audit
- **GitHub Security Tab:** Built-in documentation in Code Scanning UI

---

**Document Version:** 1.0
**Last Updated:** 2025-11-27
**Maintainers:** DevOps Team, Security Team
