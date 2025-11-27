# Lexikon - Production Deployment Guide

This guide explains how to deploy Lexikon in production.

## Prerequisites

- Docker and Docker Compose installed
- SSL certificates (for HTTPS)
- `.env.prod` file with production secrets

## 1. Production Deployment

### Step 1: Configure Environment

Create `.env.prod` file with your production secrets:

```bash
# Database
POSTGRES_DB=lexikon
POSTGRES_USER=lexikon
POSTGRES_PASSWORD=<your-strong-password>

# Redis
REDIS_PASSWORD=<your-strong-password>

# JWT & API
JWT_SECRET=<64-char-hex-string>
API_KEY_SECRET=<64-char-hex-string>

# Frontend
FRONTEND_URL=https://your-domain.com
CORS_ORIGINS=https://your-domain.com

# OAuth (optional)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
```

**Generate secure secrets:**
```bash
# Generate JWT_SECRET
openssl rand -hex 32

# Generate API_KEY_SECRET
openssl rand -hex 32

# Generate passwords
openssl rand -base64 32
```

### Step 2: Deploy Services

```bash
# Start all production services
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# Check status
docker-compose -f docker-compose.prod.yml --env-file .env.prod ps
```

### Step 3: Verify Deployment

```bash
# Check backend health
curl https://your-domain.com/api/health

# Check frontend
curl https://your-domain.com/

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

## 2. Monitoring (Optional)

Lexikon includes optional Uptime Kuma monitoring dashboard.

### Enable Monitoring

```bash
# Start monitoring service
docker-compose -f docker-compose.monitoring.yml up -d

# Connect to lexikon network
docker network connect lexikon_lexikon-network lexikon-uptime-kuma

# Access dashboard
open https://your-domain.com/monitoring/
```

### First-Time Setup

1. Navigate to `https://your-domain.com/monitoring/`
2. Create admin account (first-time only)
3. Add monitors for your services:
   - **Backend Health**: `https://your-domain.com/api/health`
   - **Frontend**: `https://your-domain.com/`
   - **Database**: Internal check via backend

### Configure Alerts

In Uptime Kuma dashboard:
1. Go to Settings → Notifications
2. Add email/Slack/Discord notifications
3. Configure alert thresholds

## 3. Maintenance

### Update Deployment

```bash
# Pull latest changes
git pull origin develop

# Rebuild and restart
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build

# Clean up old images
docker image prune -f
```

### Backup Data

```bash
# Backup PostgreSQL
docker exec lexikon-postgres pg_dump -U lexikon lexikon > backup.sql

# Backup Redis (if needed)
docker exec lexikon-redis redis-cli --rdb /data/dump.rdb

# Backup Uptime Kuma data (if using monitoring)
docker cp lexikon-uptime-kuma:/app/data ./uptime-kuma-backup
```

### View Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker logs lexikon-backend -f
docker logs lexikon-frontend -f
docker logs lexikon-postgres -f
```

## 4. Troubleshooting

### Services not starting

Check logs for errors:
```bash
docker-compose -f docker-compose.prod.yml logs
```

### Database connection issues

Verify PostgreSQL is healthy:
```bash
docker-compose -f docker-compose.prod.yml ps postgres
docker exec lexikon-postgres pg_isready -U lexikon
```

### Frontend not accessible

1. Check nginx logs: `docker logs lexikon-nginx`
2. Verify frontend is healthy: `docker-compose -f docker-compose.prod.yml ps frontend`
3. Test backend directly: `curl http://localhost:8000/health`

### Monitoring not accessible

1. Ensure monitoring service is running:
   ```bash
   docker ps | grep uptime-kuma
   ```

2. Check network connectivity:
   ```bash
   docker network inspect lexikon_lexikon-network
   ```

3. Verify nginx configuration:
   ```bash
   docker exec lexikon-nginx nginx -t
   ```

## 5. Security Checklist

- [ ] `.env.prod` file has strong, unique passwords
- [ ] `.env.prod` is NOT committed to git
- [ ] SSL certificates are valid and not expired
- [ ] Firewall allows only necessary ports (80, 443)
- [ ] Database ports (5432, 6379) are NOT exposed publicly
- [ ] Regular backups are configured
- [ ] Monitoring alerts are configured
- [ ] Application logs are reviewed regularly

## 6. Architecture

### Production Stack

```
┌─────────────────────────────────────────┐
│  Internet (HTTPS)                       │
└─────────────┬───────────────────────────┘
              │
         ┌────▼─────┐
         │  Caddy   │ (Reverse Proxy)
         │  (Host)  │
         └────┬─────┘
              │
         ┌────▼─────┐
         │  Nginx   │ (Port 8080/8443)
         └────┬─────┘
              │
        ┌─────┴─────────────────┐
        │                       │
   ┌────▼────┐           ┌──────▼──────┐
   │Frontend │           │   Backend   │
   │(Port    │           │   (Port     │
   │ 3000)   │           │    8000)    │
   └─────────┘           └──────┬──────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
               ┌────▼────┐           ┌──────▼──────┐
               │Postgres │           │   Redis     │
               │(5434)   │           │   (6379)    │
               └─────────┘           └─────────────┘

Optional Monitoring:
   ┌────────────┐
   │Uptime Kuma │ (Port 3001)
   │(/monitoring│
   │   route)   │
   └────────────┘
```

### Network Configuration

- **lexikon_lexikon-network**: Internal Docker network for service communication
- Only nginx exposes ports externally (8080, 8443)
- Database and Redis are only accessible within Docker network
- Monitoring is optional and can be disabled

## 7. Performance Tuning

### Database Optimization

For production workloads, consider:
- Increase PostgreSQL shared_buffers
- Enable connection pooling
- Configure appropriate work_mem

### Redis Configuration

- Set maxmemory policy: `allkeys-lru` (already configured)
- Monitor memory usage
- Enable persistence if needed

### Frontend/Backend

- Backend uses uvicorn workers (can be scaled)
- Frontend SSR is optimized with SvelteKit adapter-node
- Static assets are served with appropriate caching headers

---

**Need help?** Check the [monitoring guide](monitoring/MONITORING_SETUP_HIGH.md) or create an issue on GitHub.
