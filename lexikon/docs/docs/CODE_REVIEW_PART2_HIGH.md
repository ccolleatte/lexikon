# Code Review Production - Partie 2: Issues HIGH Priority

**Date:** 2025-11-22
**Scope:** 11 issues HIGH priority (à corriger avant production)
**Status:** 🟠 **FIX REQUIRED** - Correctifs obligatoires avant mise en prod

---

## HIGH Priority Issues (11)

### HIGH-001: Absence de rate limiting au niveau nginx

**Severity:** 🟠 HIGH
**Impact:** Vulnérable à DDoS, brute force auth, API abuse
**Effort:** 30 min
**Risk:** ÉLEVÉ
**Dépend de :** Aucune (indépendant)

#### Problème

Le nginx ne possède **aucun rate limiting** configuré. Cela permet :
- Brute force massif sur endpoints `/api/auth/login`
- DDoS sur endpoints publiques
- Scraping/abuse API sans limitation
- Exploitation des endpoints de reset password

**Code actuel** (`nginx.conf`) :
```nginx
# Pas de limites définiesdans ngx_http_limit_req_module
```

#### Solution

```nginx
# Au niveau http{} ou server{}
limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/m;
limit_req_zone $binary_remote_addr zone=api:10m rate=30r/m;
limit_req_zone $binary_remote_addr zone=general:10m rate=100r/m;

server {
    # Endpoints sensibles : 5 req/min max
    location /api/auth/login {
        limit_req zone=auth burst=2 nodelay;
        proxy_pass http://backend;
    }

    location /api/auth/register {
        limit_req zone=auth burst=2 nodelay;
        proxy_pass http://backend;
    }

    location /api/auth/refresh {
        limit_req zone=auth burst=5 nodelay;
        proxy_pass http://backend;
    }

    # API générale : 30 req/min
    location /api/ {
        limit_req zone=api burst=10 nodelay;
        proxy_pass http://backend;
    }

    # Autres : 100 req/min
    location / {
        limit_req zone=general burst=20 nodelay;
        proxy_pass http://backend;
    }
}
```

**Tests** :
```bash
# Tester limite auth
for i in {1..10}; do
    curl -X POST http://localhost/api/auth/login \
        -H "Content-Type: application/json" \
        -d '{"email":"test@test.com","password":"test"}'
    sleep 1
done
# 6ème+ requête devrait retourner 429 Too Many Requests
```

---

### HIGH-002: Absence de CSP (Content-Security-Policy)

**Severity:** 🟠 HIGH
**Impact:** Vulnérable à XSS, injection JavaScript
**Effort:** 20 min
**Risk:** ÉLEVÉ
**Dépend de :** Aucune

#### Problème

Pas de header `Content-Security-Policy` → Frontend vulnérable à :
- Injection JavaScript malveillant
- XSS (même stocké)
- Chargement scripts non autorisés
- Exfiltration données via image requests

#### Solution

**nginx.conf** :
```nginx
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'wasm-unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https:; frame-ancestors 'none';" always;

add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "DENY" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

**Validation** :
```bash
curl -I https://your-domain.com | grep -i "content-security-policy"
# Devrait afficher la politique complète
```

---

### HIGH-003: DATABASE_URL peut fallback à SQLite en production

**Severity:** 🟠 HIGH
**Impact:** Données stockées en fichier local (exposé)
**Effort:** 15 min
**Risk:** ÉLEVÉ
**Dépend de :** Configuration .env.prod

#### Problème

**Fichier:** `backend/database/config.py` ou similaire

Le code peut contenir une logique de fallback type :
```python
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lexikon.db")
```

En production sur Hostinger, si `DATABASE_URL` n'est pas défini, cela utilisera SQLite local (fichier). C'est **inacceptable** car :
- Données non persistantes (docker restart = loss)
- Pas de replication/backup
- Performance très faible en production
- Pas de connection pooling

#### Solution

```python
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable MUST be set in production. "
        "Format: postgresql://user:password@host:port/dbname"
    )

if DATABASE_URL.startswith("sqlite"):
    raise ValueError(
        "SQLite database NOT allowed in production. "
        "Configure proper PostgreSQL connection via DATABASE_URL"
    )
```

**Validation .env.prod** :
```bash
# Avant déploiement
grep "^DATABASE_URL=" .env.prod
# Doit retourner: DATABASE_URL=postgresql://...
```

---

### HIGH-004: JWT_SECRET et API_KEY_SECRET faibles par défaut

**Severity:** 🟠 HIGH
**Impact:** Authentification compromisable
**Effort:** 5 min (mais impact critique)
**Risk:** TRÈS ÉLEVÉ
**Dépend de :** .env.prod

#### Problème

Les fichiers de configuration utilisent des **exemples faibles** :

**.env.prod.example** :
```bash
JWT_SECRET=your-jwt-secret-key-here
API_KEY_SECRET=your-api-key-secret-here
```

Si ces valeurs par défaut sont utilisées en production, les tokens JWT et API keys sont **cassables**.

#### Solution

1. **Mettre à jour .env.prod.example** avec instructions claires :
```bash
# Generate with: openssl rand -hex 32
JWT_SECRET=must-be-32-random-hex-characters
API_KEY_SECRET=must-be-32-random-hex-characters
```

2. **Ajouter validation au startup** (`backend/main.py` ou `config.py`):
```python
JWT_SECRET = os.getenv("JWT_SECRET")
API_KEY_SECRET = os.getenv("API_KEY_SECRET")

WEAK_DEFAULTS = [
    "your-jwt-secret-key-here",
    "your-api-key-secret-here",
    "dev-secret-change-in-production",
    "changeme",
    ""
]

if JWT_SECRET in WEAK_DEFAULTS or len(JWT_SECRET or "") < 32:
    raise ValueError(
        "JWT_SECRET is missing or weak. "
        "Generate with: openssl rand -hex 32"
    )

if API_KEY_SECRET in WEAK_DEFAULTS or len(API_KEY_SECRET or "") < 32:
    raise ValueError(
        "API_KEY_SECRET is missing or weak. "
        "Generate with: openssl rand -hex 32"
    )

logger.info("✓ Secrets validation passed (32+ hex chars detected)")
```

3. **Validation avant déploiement** :
```bash
# Script de pré-déploiement
grep "JWT_SECRET=your-" .env.prod && {
    echo "ERROR: JWT_SECRET uses weak default"
    exit 1
}
```

---

### HIGH-005: Absence de monitoring/alerting externes

**Severity:** 🟠 HIGH
**Impact:** Pas de visibilité sur pannes, downtime non détecté
**Effort:** 1-2h
**Risk:** ÉLEVÉ
**Dépend de :** Déploiement infrastructure

#### Problème

Actuellement :
- Health check local uniquement (./health-check.sh)
- Pas de monitoring externe
- Pas d'alertes automatiques
- Downtime peut durer heures sans notification

#### Solution recommandée

**Option 1 : UptimeRobot (gratuit)** :
```bash
# Configurer UptimeRobot
- Monitor HTTP: https://your-domain.com/api/health (5 min)
- Expect: {"status": "ok"}
- Alerter sur: Email, Slack, Discord
```

**Option 2 : Datadog (payant mais complet)** :
```bash
# Agent Datadog dans docker-compose.prod.yml
monitoring:
  image: gcr.io/datadoghq/agent:latest
  environment:
    DD_API_KEY: ${DATADOG_API_KEY}
    DD_SITE: datadoghq.com
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock:ro
    - /proc:/host/proc:ro
    - /sys/fs/cgroup/:/host/sys/fs/cgroup:ro
```

---

### HIGH-006: Logs peuvent contenir secrets (tokens, emails)

**Severity:** 🟠 HIGH
**Impact:** Secrets leakés via logs
**Effort:** 45 min
**Risk:** ÉLEVÉ
**Dépend de :** Code backend + Configuration logging

#### Problème

Les logs peuvent contenir :
- JWT tokens (si logged dans exceptions)
- Emails utilisateurs (si logged dans queries)
- API keys (si logged en debug)
- Password reset tokens

#### Solution

1. **Implémenter log sanitization** :
```python
# backend/logging_config.py
import logging
import re

class SanitizingFormatter(logging.Formatter):
    PATTERNS = [
        (r'Bearer\s+[^\s]+', 'Bearer [REDACTED]'),
        (r'Authorization:\s*[^\s]+', 'Authorization: [REDACTED]'),
        (r'(lxk_)[^\s]+', r'\1[REDACTED]'),
        (r'email[\'"]?\s*:\s*[^\s,}]+', 'email: [REDACTED]'),
        (r'password[\'"]?\s*:\s*[^\s,}]+', 'password: [REDACTED]'),
        (r'secret[\'"]?\s*:\s*[^\s,}]+', 'secret: [REDACTED]'),
    ]

    def format(self, record):
        msg = super().format(record)
        for pattern, replacement in self.PATTERNS:
            msg = re.sub(pattern, replacement, msg, flags=re.IGNORECASE)
        return msg
```

2. **Appliquer au logging** :
```python
handler = logging.StreamHandler()
handler.setFormatter(SanitizingFormatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
logger.addHandler(handler)
```

3. **Audit logs existants** :
```bash
# Chercher patterns suspects
docker-compose logs backend | grep -i "password\|token\|secret\|@"
```

---

### HIGH-007: Redis sans authentification

**Severity:** 🟠 HIGH
**Impact:** Redis accessible sans mot de passe
**Effort:** 15 min
**Risk:** MOYEN-ÉLEVÉ
**Dépend de :** docker-compose.prod.yml

#### Problème

Redis est sur réseau interne mais **sans authentication** :

**docker-compose.prod.yml** :
```yaml
redis:
  image: redis:7-alpine
  command: redis-server
  # Manque: --requirepass ${REDIS_PASSWORD}
```

#### Solution

```yaml
redis:
  image: redis:7-alpine
  command: redis-server --requirepass ${REDIS_PASSWORD:-redis-default-password-change}
  environment:
    REDIS_PASSWORD: ${REDIS_PASSWORD}
  # ...
```

**Dans .env.prod** :
```bash
REDIS_PASSWORD=$(openssl rand -hex 16)
```

**Validation** :
```bash
# Vérifier Redis demande password
redis-cli ping
# → (error) NOAUTH Authentication required
```

---

### HIGH-008: Backup script ne teste pas restoration

**Severity:** 🟠 HIGH
**Impact:** Backups corrompus non détectés jusqu'à besoin réel
**Effort:** 45 min
**Risk:** MOYEN
**Dépend de :** deploy.sh

#### Problème

`deploy.sh` crée backups mais **ne teste jamais la restoration**. Un backup corrompu n'est découvert que lors d'un vrai incident.

#### Solution

Ajouter `test_backup()` fonction :
```bash
test_backup() {
    log_info "Testing backup integrity..."

    BACKUP_PATH="$1"
    TEMP_TEST_VOLUME="test_restore_$$"

    # Test PostgreSQL
    log_info "Testing PostgreSQL backup..."
    docker volume create "$TEMP_TEST_VOLUME"
    docker run --rm \
        -v "$TEMP_TEST_VOLUME":/data \
        -v "$BACKUP_PATH":/backup \
        alpine tar tzf /backup/postgres_data.tar.gz > /dev/null

    if [ $? -eq 0 ]; then
        log_success "PostgreSQL backup is valid"
    else
        log_error "PostgreSQL backup is corrupted"
        docker volume rm "$TEMP_TEST_VOLUME"
        return 1
    fi

    docker volume rm "$TEMP_TEST_VOLUME"
    return 0
}

# Appeler après create_backup()
create_backup() {
    # ... existing code ...
    test_backup "$BACKUP_PATH" || {
        log_error "Backup validation failed. Aborting deployment."
        exit 1
    }
}
```

---

### HIGH-009: Pas de connection pooling PostgreSQL

**Severity:** 🟠 HIGH
**Impact:** Connections exhausted sous charge
**Effort:** 30 min
**Risk:** MOYEN
**Dépend de :** Code backend

#### Problème

FastAPI + SQLAlchemy sans pool configuration. Sous charge (>10 concurrent requests) :
- Connections épuisées
- Queries mises en attente
- Timeout utilisateurs

#### Solution

**backend/database/config.py** :
```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,  # Vérifier connection avant use
    pool_recycle=3600,  # Recycle après 1h (prevent idle timeout)
)
```

**Validation** :
```bash
# Tester sous charge
ab -n 100 -c 20 http://localhost:8000/api/health
# Ne devrait pas avoir de timeouts
```

---

### HIGH-010: Rollback script ne vérifie pas existence backups

**Severity:** 🟠 HIGH
**Impact:** Rollback échoue à moment critique
**Effort:** 20 min
**Risk:** MOYEN
**Dépend de :** rollback.sh

#### Problème

**rollback.sh** lignes 75-82 commence à arrêter les services AVANT de vérifier que les backups existent :

```bash
# MAUVAIS : arrête services en premier
docker-compose -f docker-compose.prod.yml down

# PUIS essaie de restaurer backup qui n'existe peut-être pas
docker run --rm \
    -v lexikon_postgres_data:/data \
    -v "$LATEST_BACKUP":/backup \  # ← Peut ne pas exister
    alpine tar xzf /backup/postgres_data.tar.gz -C /data
```

Si backup corrompu/inexistant → Services arrêtés + pas de restoration = downtime complète.

#### Solution

```bash
rollback() {
    # 1. VÉRIFIER D'ABORD les backups
    log_info "Verifying backup integrity..."

    if [ ! -f "$LATEST_BACKUP/postgres_data.tar.gz" ]; then
        log_error "PostgreSQL backup file not found: $LATEST_BACKUP/postgres_data.tar.gz"
        exit 1
    fi

    if [ ! -f "$LATEST_BACKUP/redis_data.tar.gz" ]; then
        log_error "Redis backup file not found: $LATEST_BACKUP/redis_data.tar.gz"
        exit 1
    fi

    # 2. Tester extraction tar
    log_info "Testing backup extraction..."
    if ! tar tzf "$LATEST_BACKUP/postgres_data.tar.gz" > /dev/null 2>&1; then
        log_error "PostgreSQL backup is corrupted"
        exit 1
    fi

    if ! tar tzf "$LATEST_BACKUP/redis_data.tar.gz" > /dev/null 2>&1; then
        log_error "Redis backup is corrupted"
        exit 1
    fi

    log_success "All backups verified"

    # 3. MAINTENANT arrêter les services
    log_info "Stopping services..."
    docker-compose -f docker-compose.prod.yml down

    # 4. Procéder à la restoration
    # ... reste du code inchangé
}
```

---

### HIGH-011: Neo4j password en plaintext dans docker-compose

**Severity:** 🟠 HIGH
**Impact:** Secrets exposés dans configuration versionée
**Effort:** 20 min
**Risk:** MOYEN
**Dépend de :** docker-compose.prod.yml

#### Problème

**docker-compose.prod.yml** contient :
```yaml
neo4j:
  environment:
    NEO4J_AUTH: neo4j/password-plaintext
```

Le password est :
- Visible en clair dans le fichier
- Versioné dans git
- Exposé via `docker inspect`

#### Solution

1. **Utiliser variables d'environnement** :
```yaml
neo4j:
  environment:
    NEO4J_AUTH: neo4j/${NEO4J_PASSWORD}
  # Plus sûr : utiliser Docker secrets
```

2. **Ou Docker secrets (meilleure approche)** :
```yaml
neo4j:
  environment:
    NEO4J_INITIAL_dbms_security_auth__admin_password__change_required: "false"
    NEO4J_AUTH: neo4j/file:/run/secrets/neo4j_password
  secrets:
    - neo4j_password

secrets:
  neo4j_password:
    file: /opt/lexikon/secrets/neo4j_password.txt
```

3. **Avant déploiement** :
```bash
mkdir -p /opt/lexikon/secrets
openssl rand -hex 16 > /opt/lexikon/secrets/neo4j_password.txt
chmod 600 /opt/lexikon/secrets/neo4j_password.txt
```

---

## Résumé HIGH Priority

| Issue | Effort | Risk | Fix Before? |
|-------|--------|------|------------|
| HIGH-001 (Rate limit) | 30 min | ÉLEVÉ | OUI |
| HIGH-002 (CSP headers) | 20 min | ÉLEVÉ | OUI |
| HIGH-003 (DATABASE_URL) | 15 min | ÉLEVÉ | OUI |
| HIGH-004 (Secrets validation) | 5 min | TRÈS ÉLEVÉ | OUI |
| HIGH-005 (Monitoring) | 1-2h | ÉLEVÉ | OUI |
| HIGH-006 (Log sanitization) | 45 min | ÉLEVÉ | NON (acceptable en jour 1) |
| HIGH-007 (Redis auth) | 15 min | MOYEN-ÉLEVÉ | OUI |
| HIGH-008 (Backup test) | 45 min | MOYEN | NON (acceptable j+1) |
| HIGH-009 (Connection pooling) | 30 min | MOYEN | NON (acceptable j+1) |
| HIGH-010 (Rollback verify) | 20 min | MOYEN | NON (acceptable j+1) |
| HIGH-011 (Neo4j secrets) | 20 min | MOYEN | OUI |

**Total effort estimé :**
- **Critique (doit faire)** : 105 minutes (HIGH-001 → 005, 007, 011)
- **Acceptable post-prod** : 135 minutes (HIGH-006 → 010)

---

## Priorisation pour déploiement

### Phase 1 : Avant déploiement (MANDATORY)
1. HIGH-001 : Rate limiting nginx
2. HIGH-002 : CSP headers
3. HIGH-003 : DATABASE_URL validation
4. HIGH-004 : Secrets validation at startup
5. HIGH-005 : Monitoring setup (UptimeRobot minimum)
6. HIGH-007 : Redis password
7. HIGH-011 : Neo4j secrets via docker-compose

**Durée estimée:** 2-3 heures

### Phase 2 : Jour 1-2 post-prod (SHOULD)
8. HIGH-006 : Log sanitization
9. HIGH-008 : Backup verification
10. HIGH-009 : Connection pooling

**Durée estimée:** 2 heures

### Phase 3 : Semaine 1 (NICE-TO-HAVE)
11. HIGH-010 : Rollback script verification

**Durée estimée:** 20 minutes

---

**Fin Partie 2 - Issues HIGH Priority**

👉 **Voir CODE_REVIEW_PART3_MEDIUM_LOW.md pour issues MEDIUM/LOW + Points positifs**
