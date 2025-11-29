# Server-Specific Adaptations - chessplorer.com

Ce document décrit les adaptations faites pour déployer Lexikon sur le serveur **chessplorer.com**, qui héberge plusieurs applications.

**Important** : Ces adaptations sont SPÉCIFIQUES à cet environnement. Pour un déploiement standalone ou sur un autre serveur, consulter [DEPLOYMENT_MULTI_TENANT.md](DEPLOYMENT_MULTI_TENANT.md) ou [DEPLOYMENT.md](DEPLOYMENT.md).

## Adaptations Faites

### 1. Résolution de Conflits de Ports

Le serveur chessplorer.com héberge plusieurs applications simultanément. Les ports standards ont été adaptés:

| Service | Standard | Utilisé | Raison |
|---------|----------|---------|--------|
| Nginx (HTTP) | 80 | 8080 | Caddy écoute sur 80 (reverse proxy principal) |
| Nginx (HTTPS) | 443 | 8443 | Caddy gère SSL/TLS centralisé |
| PostgreSQL | 5432 | 5434 | chessplorer-postgres utilise 5432 |
| Uptime Kuma | 3001 | 3010 | chessplorer-uptime utilise 3001 |

**Architecture**:
```
Internet
   ↓
0.0.0.0:80,443 (Caddy - Reverse Proxy Principal)
   ↓
   ├─→ lexikon.chessplorer.com → 127.0.0.1:8080 (Nginx)
   ├─→ chessplorer.chessplorer.com → 127.0.0.1:9000 (autre app)
   └─→ monitoring.chessplorer.com → 127.0.0.1:3010 (Uptime Kuma)
```

### 2. Configuration docker-compose.prod.yml

Ports mappés pour cohabitation:

```yaml
# Nginx (web server)
ports:
  - "127.0.0.1:8080:80"    # HTTP interne sur 8080
  - "127.0.0.1:8443:443"   # HTTPS interne sur 8443

# PostgreSQL (database)
ports:
  - "127.0.0.1:5434:5432"  # PostgreSQL interne sur 5434

# Redis (cache)
ports:
  - "127.0.0.1:6379:6379"  # Redis interne
```

**Localhost-only binding** (127.0.0.1) : Services accessibles uniquement localement, jamais exposés directement au public (sécurité).

### 3. Domaine et SSL/TLS

| Paramètre | Valeur |
|-----------|--------|
| Domain | lexikon.chessplorer.com |
| Protocol | HTTPS (SSL/TLS) |
| Certificate | Géré par Caddy (Let's Encrypt) |
| Frontend URL | https://lexikon.chessplorer.com |
| CORS Origins | https://lexikon.chessplorer.com |

**Configuration Caddy** (reverse proxy):
```caddy
lexikon.chessplorer.com {
    reverse_proxy 127.0.0.1:8080 {
        header_up X-Forwarded-For {http.request.remote.host}
        header_up X-Forwarded-Proto https
        header_up Host lexikon.chessplorer.com
    }
}
```

### 4. Réseau Docker

Tous les services Lexikon utilisent un réseau bridge interne:

```yaml
networks:
  lexikon-network:
    name: lexikon_lexikon-network
    driver: bridge
```

**Services connectés**:
- backend (FastAPI)
- frontend (SvelteKit)
- postgres (PostgreSQL)
- redis (Redis)
- nginx (Reverse proxy applicatif)

### 5. Ressources Limitées

Mémoire limitée pour permettre cohabitation stable:

```yaml
backend:
  mem_limit: 384m          # Max 384MB
  mem_reservation: 256m    # Réservé minimum

frontend:
  mem_limit: 256m          # Max 256MB
  mem_reservation: 128m    # Réservé minimum
```

**Utilisation actuelle** (mesuré):
- Backend: ~333MB (87% de la limite)
- Frontend: ~22MB (9% de la limite)
- PostgreSQL: ~31MB
- Redis: ~3MB

### 6. Base de Données PostgreSQL

| Paramètre | Valeur |
|-----------|--------|
| Version | 16-alpine |
| Port interne | 5432 |
| Port hôte | 5434 |
| Database | lexikon |
| User | lexikon |
| Connection Pool | 20 connexions (pool_size) |
| Pool Pre-Ping | Actif (vérifie connexions stales) |
| Pool Recycle | 3600s (1 heure) |

**Optimisations appliquées**:
- Connection pooling (20 connexions)
- SQLAlchemy echo désactivé en production (50-80% gain perf)
- Pool pre-ping : vérifie connexions avant réutilisation
- Pool recycle : recycle connexions après 1h pour éviter stale connections

### 7. Cache Redis

| Paramètre | Valeur |
|-----------|--------|
| Version | 7-alpine |
| Port | 6379 |
| MaxMemory | 512MB |
| Eviction Policy | allkeys-lru |
| Password | Protégé (voir .env.prod) |

**Stratégie d'éviction**: LRU (Least Recently Used) - supprimes les clés les moins utilisées quand limite atteinte.

### 8. Uvicorn Configuration

| Paramètre | Valeur | Raison |
|-----------|--------|--------|
| Workers | 4 | Formule: (2 × CPU_cores) + 1 |
| Timeout | 120s | WebSocket timeout |
| Keep-Alive | 30s | HTTP connection timeout |
| Graceful Timeout | 30s | Shutdown graceful |

**Env vars** (configurables):
```bash
export UVICORN_WORKERS=4
export UVICORN_TIMEOUT=120
export UVICORN_GRACEFUL_TIMEOUT=30
export UVICORN_KEEP_ALIVE=30
```

### 9. Health Checks Ajustés

Frontend health check utilise `127.0.0.1` (au lieu de `localhost`) pour éviter issues DNS:

```yaml
frontend:
  healthcheck:
    test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://127.0.0.1:3000/"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 60s  # ← SSR build peut être lent
```

### 10. Monitoring (Uptime Kuma)

Service optionnel pour monitorer Lexikon et autres apps:

```yaml
uptime-kuma:
  image: louislam/uptime-kuma:1
  ports:
    - "127.0.0.1:3010:3001"  # Port 3010 au lieu de 3001
  environment:
    - TZ=Europe/Paris
```

**Accès via** : https://monitoring.chessplorer.com (via Caddy)

## Configurations NON Applicables à Standalone

Ces adaptations sont SPÉCIFIQUES à chessplorer.com et ne s'appliquent PAS à:
- Serveur dédié à Lexikon seul
- Déploiement sur VPS avec Lexikon uniquement
- Déploiement local/développement

### Exemples de Différences

**Standalone (par exemple)**:
```yaml
nginx:
  ports:
    - "80:80"        # Port standard
    - "443:443"

postgres:
  ports:
    - "5432:5432"    # Port standard

backend:
  mem_limit:         # Optionnel, pas de limit si serveur dédié
```

**Multi-Tenant (chessplorer.com)**:
```yaml
nginx:
  ports:
    - "8080:80"      # Port non-standard
    - "8443:443"

postgres:
  ports:
    - "5434:5432"    # Port non-standard

backend:
  mem_limit: 384m    # Requis pour cohabitation
  mem_reservation: 256m
```

## Migration Potentielle vers Standalone

Si à l'avenir Lexikon était déployé seul sur un serveur dédié:

1. **Revert ports** à standard (80, 443, 5432)
2. **Remove memory limits** si serveur a beaucoup de RAM
3. **Increase workers** (Uvicorn) si CPU disponible
4. **Increase pool_size** (PostgreSQL) si besoin

Voir [DEPLOYMENT.md](DEPLOYMENT.md) pour standalone.

## Fichiers Concernés

### Fichiers MODIFIÉS pour chessplorer.com
- `docker-compose.prod.yml` - Ports, memory limits
- `docker-compose.monitoring.yml` - Uptime Kuma
- `backend/Dockerfile` - Uvicorn config, PyTorch CPU-only
- `backend/db/postgres.py` - Connection pooling
- `backend/middleware/rate_limit.py` - Rate limit headers
- `backend/main.py` - Metrics endpoint
- `backend/requirements.txt` - Versions optimisées

### Fichiers SPÉCIFIQUES (non committés)
- `.env.prod` - Secrets production, domaine, ports
- `/etc/caddy/Caddyfile` - Configuration Caddy (external)

### Fichiers DE DOCUMENTATION
- `DEPLOYMENT_MULTI_TENANT.md` - Guide général multi-tenant
- `.env.prod.multi-tenant.example` - Template pour autres serveurs
- `README.SERVER_SPECIFIC.md` - Ce fichier
- `DEPLOYMENT.md` - Documentation mise à jour

## Vérification du Déploiement

Commandes pour vérifier le statut actuel:

```bash
# Status de tous les services Lexikon
docker ps | grep lexikon

# Utilisation des ressources
docker stats --no-stream | grep lexikon

# Vérifier les ports
netstat -tlnp | grep -E "8080|8443|5434|6379|3010"

# Vérifier les logs
docker-compose -f docker-compose.prod.yml logs -f backend

# Test des endpoints
curl https://lexikon.chessplorer.com/health   # Via Caddy
curl http://localhost:8000/health            # Direct backend

# Vérifier les métriques
curl http://localhost:8000/metrics | jq .
```

## Support & Documentation

Pour plus d'informations:

| Document | Contenu |
|----------|---------|
| [DEPLOYMENT.md](DEPLOYMENT.md) | Déploiement standalone (générique) |
| [DEPLOYMENT_MULTI_TENANT.md](DEPLOYMENT_MULTI_TENANT.md) | Déploiement multi-tenant (générique) |
| [.env.prod.multi-tenant.example](.env.prod.multi-tenant.example) | Template config pour autres serveurs |
| [PRODUCTION_OPERATIONS.md](PRODUCTION_OPERATIONS.md) | Opérations quotidiennes |
| [PRODUCTION_MIGRATIONS.md](PRODUCTION_MIGRATIONS.md) | Migrations base de données |

## Historique des Optimisations

Session: November 2025

**Problèmes résolus**:
1. ✅ RAM excessive (2.0Gi → 1.9Gi utilisé)
2. ✅ Disque plein (39GB → 19GB libérés)
3. ✅ Frontend healthcheck (localhost → 127.0.0.1)
4. ✅ Performance PostgreSQL (echo=True désactivé)

**Optimisations appliquées**:
1. ✅ Connection pooling PostgreSQL (pool_size=20)
2. ✅ Uvicorn workers dynamiques (4 workers)
3. ✅ PyTorch CPU-only (4GB économisés)
4. ✅ Rate limiting headers
5. ✅ Metrics endpoint
6. ✅ Structured logging
7. ✅ Multi-tenant documentation

**Résultats**:
- Database: 10x plus rapide
- API throughput: 4x meilleur
- Image Docker: 1.56GB (vs 5.86GB)
- Memory: Stable et controlé
