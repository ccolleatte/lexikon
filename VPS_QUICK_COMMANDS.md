# 🚀 VPS Quick Commands - Copy & Paste

Since SSH is having issues, use these direct commands on your VPS terminal/console.

---

## 📋 BEFORE DEPLOYING

### 1️⃣ Ensure repository is up to date

```bash
cd /opt/lexikon
git fetch origin
git pull origin develop
```

**Expected output:**
```
From github.com:your-repo/lexikon
 * branch            develop    -> FETCH_HEAD
Already up to date.
```

---

## 🚀 DEPLOYMENT PROCESS

### 2️⃣ Run deployment script

```bash
cd /opt/lexikon
./deploy.sh
```

**This will:**
- Run backend tests (pytest)
- Build Docker images
- Start containers
- Health checks

**Watch for:**
```
✅ Backend tests PASSED
✅ Building Docker images
✅ Starting containers...
✅ All health checks passed
```

**If anything fails:**
```bash
./rollback.sh
```

---

## ✅ POST-DEPLOYMENT VERIFICATION (5-10 min)

### 3️⃣ Run the verification checklist

```bash
cd /opt/lexikon
./post-deploy-check.sh
```

**Expected output:**
```
╔════════════════════════════════════════════════════════════════╗
║      🚀 LEXIKON POST-DEPLOYMENT VERIFICATION CHECKLIST       ║
║                    SvelteKit SSR + Docker                     ║
╚════════════════════════════════════════════════════════════════╝

Total checks:  X
Passed:        X ✅
Failed:        0
Success rate:  100%

╔════════════════════════════════════════════════════════════════╗
║                    ✅ ALL CHECKS PASSED                        ║
║                                                                 ║
║  Production is HEALTHY - Ready for traffic!                    ║
╚════════════════════════════════════════════════════════════════╝
```

---

## 🔍 MANUAL VERIFICATION (if you prefer)

If the script doesn't work, run these individual checks:

### Container Status
```bash
docker-compose -f docker-compose.prod.yml ps
```

**Expected: All 4 containers `Up` and `healthy`**

---

### Backend Health

```bash
curl http://127.0.0.1:8000/health
```

**Expected output:**
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected"
}
```

---

### Frontend Check

```bash
curl http://127.0.0.1:3000/
```

**Expected: HTML page with `<title>` tag (SvelteKit rendered)**

---

### Nginx Proxy Check

```bash
curl http://127.0.0.1:8080/health
```

**Expected: Same JSON as backend (proxied successfully)**

---

### Database Check

```bash
docker exec lexikon-postgres psql -U postgres -c "SELECT version();"
```

**Expected: PostgreSQL version output**

---

### Redis Check

```bash
docker exec lexikon-redis redis-cli ping
```

**Expected output:**
```
PONG
```

---

### HTTPS/SSL Check (from your local computer)

```bash
curl -I https://lexikon.chessplorer.com
```

**Expected: HTTP/2 200**

---

## 🛠️ TROUBLESHOOTING

### If containers are not running

```bash
# Check what's wrong
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs frontend
docker-compose -f docker-compose.prod.yml logs nginx
docker-compose -f docker-compose.prod.yml logs postgres
```

### If tests failed during deploy

```bash
# Run tests manually to see what failed
cd /opt/lexikon
docker-compose -f docker-compose.prod.yml up -d postgres redis
docker-compose -f docker-compose.prod.yml run --rm backend pytest -v
```

### If frontend is blank

```bash
# Check frontend logs
docker logs lexikon-frontend

# Check if SvelteKit is running
curl -v http://127.0.0.1:3000/
```

### If API calls fail

```bash
# Check backend logs
docker logs lexikon-backend

# Check database connection
docker exec lexikon-postgres psql -U postgres -c "SELECT COUNT(*) FROM users;"
```

---

## 📊 CHECKING LOGS

### Real-time logs (follow mode)

```bash
# Backend logs (follow)
docker logs -f lexikon-backend

# Frontend logs (follow)
docker logs -f lexikon-frontend

# Nginx logs (follow)
docker logs -f lexikon-nginx

# Exit with Ctrl+C
```

### Last 50 lines

```bash
docker logs --tail=50 lexikon-backend
docker logs --tail=50 lexikon-frontend
docker logs --tail=50 lexikon-nginx
```

### Last 100 lines with timestamps

```bash
docker logs -t --tail=100 lexikon-backend
```

---

## 🔄 ROLLBACK PROCEDURE

If anything goes wrong:

```bash
cd /opt/lexikon
./rollback.sh
```

This will:
- Stop current containers
- Restore previous database backup
- Restart with previous code version

**Verify rollback:**
```bash
docker-compose -f docker-compose.prod.yml ps
curl http://127.0.0.1:8000/health
```

---

## 📈 MONITORING & HEALTH CHECKS

### Check Uptime Kuma (if deployed)

```bash
curl http://127.0.0.1:3001/
```

### Access Uptime Kuma via web

```
https://lexikon.chessplorer.com/monitoring/
```

### Manual health check loop (useful for monitoring)

```bash
while true; do
  echo "=== $(date) ==="
  curl -s http://127.0.0.1:8000/health | jq .
  sleep 30
done
```

Press `Ctrl+C` to stop

---

## 📚 USEFUL DOCKER COMMANDS

### See all running containers

```bash
docker ps
```

### Stop all services

```bash
cd /opt/lexikon
docker-compose -f docker-compose.prod.yml down
```

### Restart all services

```bash
cd /opt/lexikon
docker-compose -f docker-compose.prod.yml up -d
```

### Remove all containers (WARNING: use with caution)

```bash
cd /opt/lexikon
docker-compose -f docker-compose.prod.yml down -v
```

### Clean up old Docker images/containers

```bash
docker system prune -a
```

---

## 🚨 QUICK REFERENCE CARD

**After `./deploy.sh` succeeds:**
```bash
# Run this ONE command to verify everything
./post-deploy-check.sh
```

**If you see:**
- ✅ ALL GREEN → Production is ready!
- ❌ ANY RED → Run `./rollback.sh` immediately

---

## 📝 VPS File Locations

```
/opt/lexikon/
├── deploy.sh                           # Main deployment script
├── rollback.sh                         # Rollback script
├── post-deploy-check.sh               # Verification script
├── docker-compose.prod.yml            # Production stack
├── docker-compose.monitoring.yml      # Monitoring stack
├── nginx.conf                         # Nginx config
├── .env.prod                          # Production secrets
└── backend/
    └── tests/                         # Backend tests
```

---

## ⚡ Speed Optimization

**Fastest verification (30 seconds):**
```bash
cd /opt/lexikon && ./post-deploy-check.sh
```

**If that doesn't work, quick manual check (2 minutes):**
```bash
docker-compose -f docker-compose.prod.yml ps && \
curl http://127.0.0.1:8000/health && \
curl http://127.0.0.1:3000/ | head -1
```

---

**Last updated:** November 24, 2025
**For:** Lexikon v2.0+ deployment on Hostinger VPS
