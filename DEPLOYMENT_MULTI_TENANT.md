# Déploiement Multi-Tenant (Serveur Partagé)

## Contexte

Ce guide s'adresse aux déploiements de Lexikon sur un serveur hébergeant **plusieurs applications** (multi-tenant).

Contrairement au déploiement standalone (voir [DEPLOYMENT.md](DEPLOYMENT.md)), les serveurs partagés nécessitent des adaptations pour éviter les conflits de ressources et de ports.

## Adaptations Nécessaires

### 1. Gestion des Ports (Conflits d'Écoute)

Sur un serveur multi-tenant, plusieurs applications écoutent simultanément. Les ports standards doivent être ajustés.

#### Lexikon Ports Standards
```
HTTP:       80      → 8080   (éviter conflit reverse proxy)
HTTPS:      443     → 8443   (éviter conflit reverse proxy)
PostgreSQL: 5432    → 5434   (éviter conflit autres DBs)
Monitoring: 3001    → 3010   (éviter conflit autres services)
```

#### Raisons
- **80/443** : Généralement réservés au reverse proxy principal (Caddy, Nginx, HAProxy)
- **5432** : Port PostgreSQL standard, souvent utilisé par d'autres projets
- **3001** : Port commun pour monitoring (Uptime Kuma, Grafana, etc.)

#### Configuration dans docker-compose.prod.yml

```yaml
services:
  nginx:
    ports:
      - "8080:80"      # Host:Container
      - "8443:443"

  postgres:
    ports:
      - "5434:5432"

  # Monitoring (si utilisé)
  uptime-kuma:
    ports:
      - "3010:3001"
```

### 2. Architecture Multi-Tenant Recommandée

```
┌─────────────────────────────────────────────────────┐
│         Reverse Proxy Principal (Caddy)             │
│  Écoute: 0.0.0.0:80 et 0.0.0.0:443 (SSL/TLS)      │
└─────────────────────────────────────────────────────┘
                         ↓
    ┌────────────────────┬─────────────────────┐
    ↓                    ↓                     ↓
lexikon.domain.com   app2.domain.com    monitoring.domain.com
(Nginx 8080→80)     (autre app)          (Uptime Kuma 3010→3001)
    ↓
┌───────────────────┐
│  Lexikon Services │
├───────────────────┤
│ Backend   8000    │ (interne)
│ Frontend  3000    │ (interne)
│ PostgreSQL 5434   │ (interne)
│ Redis     6379    │ (interne)
└───────────────────┘
```

### 3. Configuration Réseau Docker

**Avantage** : Services dans le même réseau Docker peuvent communiquer directement par DNS.

```yaml
networks:
  lexikon-network:
    driver: bridge
```

**Utilisation** :
```yaml
backend:
  networks:
    - lexikon-network

postgres:
  networks:
    - lexikon-network
```

Les conteneurs se résolvent par nom :
- `postgresql://postgres:5432` (au lieu de localhost)
- `redis:6379` (au lieu de localhost)

### 4. Ressources Limitées (Cohabitation)

Sur serveur partagé avec ressources contraintes, définir des limits.

#### Memory Limits
```yaml
backend:
  mem_limit: 384m          # Max autorisé
  mem_reservation: 256m    # Réservé en priorité

frontend:
  mem_limit: 256m
  mem_reservation: 128m
```

#### Rationale
- Évite un service de monopoliser la RAM
- Empêche OOM (Out of Memory) kills
- Permet cohabitation stable

#### Calcul des Limites
```
RAM Serveur: 8GB
OS + Services critiques: 2GB
Available for apps: 6GB

Distribution (exemple):
- Lexikon: 0.8GB (backend 384MB + frontend 256MB + DB 200MB)
- App2:    2GB
- Cache/Buffers: 3.2GB
```

### 5. Configuration .env.prod Multi-Tenant

Créer `.env.prod` en adaptant le template :

```bash
# === Application ===
FRONTEND_URL=https://lexikon.votre-domaine.com
CORS_ORIGINS=https://lexikon.votre-domaine.com

# === Database ===
POSTGRES_DB=lexikon
POSTGRES_USER=lexikon
POSTGRES_PASSWORD=$(openssl rand -hex 32)
DATABASE_URL=postgresql://lexikon:${POSTGRES_PASSWORD}@postgres:5432/lexikon

# === Redis ===
REDIS_PASSWORD=$(openssl rand -hex 32)

# === Security ===
JWT_SECRET=$(openssl rand -hex 32)
API_KEY_SECRET=$(openssl rand -hex 32)

# === OAuth (optionnel) ===
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
```

**Important** : `.env.prod` ne doit PAS être versionné (ajouté à `.gitignore`)

### 6. Health Checks Ajustés

Sur conteneurs multi-tenant, les health checks doivent être robustes.

#### Frontend Health Check (SSR)
```yaml
frontend:
  healthcheck:
    test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://127.0.0.1:3000/"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 60s  # ← SSR build peut être lent
```

#### Backend Health Check
```yaml
backend:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 30s  # ← Plus rapide que frontend
```

### 7. Logging Structuré (Observabilité)

Activé par défaut pour debug en production partagée.

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"      # 30MB max par service
```

**Avantage** : Logs centralisés, faciles à rechercher/monitorer.

## Déploiement Étape par Étape

### 1. Préparer l'Environnement

```bash
# Clone ou pull
git clone https://github.com/ccolleatte/lexikon.git
cd lexikon

# Copier template multi-tenant
cp .env.prod.multi-tenant.example .env.prod

# Éditer .env.prod avec valeurs serveur
nano .env.prod

# Vérifier que .env.prod est ignoré par git
grep ".env.prod" .gitignore  # Doit afficher: .env.prod
```

### 2. Builder l'Image Backend (CPU-Only)

```bash
# Important: PyTorch CPU-only pour économiser ~4GB
docker build -t lexikon_backend:latest -f backend/Dockerfile backend/

# Vérifier la taille
docker images | grep lexikon_backend
# Attendu: ~1.5GB (vs 5.8GB avec CUDA)
```

### 3. Démarrer les Services

```bash
# Vérifier ports disponibles
netstat -tlnp | grep -E "8080|8443|5434|3010"

# Démarrer Lexikon
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# Vérifier statut
docker ps | grep lexikon

# Vérifier logs
docker-compose -f docker-compose.prod.yml logs -f backend
```

### 4. Tester les Services

```bash
# Health check backend
curl http://localhost:8000/health

# Health check frontend
curl http://localhost:3000/

# Tester API
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","first_name":"Test","last_name":"User"}'
```

### 5. Configurer le Reverse Proxy

Si Caddy est le reverse proxy principal :

```caddy
# /etc/caddy/Caddyfile
lexikon.votre-domaine.com {
    reverse_proxy localhost:8080 {
        header_up X-Forwarded-For {http.request.remote.host}
        header_up X-Forwarded-Proto {http.request.proto}
    }
}
```

Recharger Caddy :
```bash
sudo systemctl reload caddy
```

## Considérations de Performance

### 1. Connection Pooling

PostgreSQL utilise un pool de 20 connexions (configurable via `pool_size`).

**Pour très petit serveur** (< 1GB RAM) :
```python
pool_size=10,  # Réduit au lieu de 20
max_overflow=5,
```

### 2. Uvicorn Workers

Par défaut, 4 workers sont lancés (configurable via `UVICORN_WORKERS`).

**Formule recommandée** :
```
workers = (2 × CPU_cores) + 1
```

**Pour serveur partagé** :
```bash
# Réduire si CPU limité
export UVICORN_WORKERS=2  # Au lieu de 4
```

### 3. Cache Redis

Redis limite mémoire à 512MB avec éviction LRU.

**Monitorer** :
```bash
docker exec lexikon-redis redis-cli INFO memory
```

## Monitoring & Observabilité

### 1. Métriques Lexikon

Disponible sur `/metrics` endpoint :

```bash
curl http://localhost:8000/metrics | jq .
```

Retourne :
```json
{
  "requests": {
    "total": 123,
    "successful": 120,
    "failed": 3,
    "error_rate": 2.44
  },
  "cache": {
    "hits": 456,
    "misses": 89,
    "hit_rate": 83.67
  },
  "database": {
    "queries": 1234
  }
}
```

### 2. Uptime Kuma (Optional)

Pour monitorer Lexikon et autres services :

```bash
# Démarrer Uptime Kuma
docker-compose -f docker-compose.monitoring.yml up -d

# Accéder via reverse proxy
# https://monitoring.votre-domaine.com (via Caddy)
```

### 3. Logs Centralisés

Tous les services produisent des logs structurés (JSON).

```bash
# Voir les logs backend
docker logs lexikon-backend | jq .

# Voir les erreurs seulement
docker logs lexikon-backend | jq 'select(.level=="ERROR")'
```

## Troubleshooting Multi-Tenant

### Problème: Port Déjà Utilisé

```bash
# Identifier le processus
lsof -i :8080

# Solution: Changer port dans docker-compose.prod.yml
# 8080:80 → 8081:80 (puis reboot)
```

### Problème: Conteneur OOM Kill

```bash
# Vérifier mémoire utilisée
docker stats lexikon-backend

# Solution: Augmenter mem_limit
# mem_limit: 384m → 512m (dans docker-compose.prod.yml)
```

### Problème: Base de Données Lente

```bash
# Vérifier connexions PostgreSQL
docker exec lexikon-postgres psql -U lexikon -c "SELECT count(*) FROM pg_stat_activity;"

# Vérifier pool utilisation
# Voir logs backend pour "waiting for connection"

# Solution: Augmenter pool_size dans backend/db/postgres.py
```

### Problème: Frontend Not Responsive

```bash
# Vérifier santé du frontend
curl -v http://localhost:3000/

# Vérifier mémoire Node.js
docker stats lexikon-frontend

# Vérifier logs de build
docker logs lexikon-frontend | grep -i "error\|warn"
```

## Checklist Pré-Production

- [ ] Ports vérifiés et disponibles (8080, 8443, 5434, 3010)
- [ ] .env.prod créé avec secrets générés (`openssl rand -hex 32`)
- [ ] .env.prod ajouté à .gitignore
- [ ] Backend image built avec PyTorch CPU-only
- [ ] Tous les services démarrent sans erreur
- [ ] Health checks passent
- [ ] API endpoints répondent correctement
- [ ] Reverse proxy configuré (Caddy/Nginx)
- [ ] SSL/TLS fonctionne (https://lexikon.votre-domaine.com)
- [ ] Logs sont lisibles et structurés
- [ ] Monitoring (Uptime Kuma) configuré
- [ ] Backups PostgreSQL planifiés
- [ ] Plan de rollback documenté

## Ressources Additionnelles

- [DEPLOYMENT.md](DEPLOYMENT.md) - Déploiement standalone
- [PRODUCTION_OPERATIONS.md](PRODUCTION_OPERATIONS.md) - Opérations quotidiennes
- [.env.prod.multi-tenant.example](.env.prod.multi-tenant.example) - Template configuration
- [README.SERVER_SPECIFIC.md](README.SERVER_SPECIFIC.md) - Adaptations chessplorer.com

## Support

Pour questions spécifiques au multi-tenant :
1. Consulter ce guide
2. Vérifier les logs : `docker logs lexikon-*`
3. Vérifier les métriques : `curl localhost:8000/metrics`
4. Consulter DEPLOYMENT.md pour déploiement standalone
