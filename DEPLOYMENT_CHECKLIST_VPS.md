# 🚀 Post-Deployment Verification Checklist - Lexikon VPS

**Purpose:** Quick validation (5-10 minutes) after running `./deploy.sh` on production VPS
**When to run:** After every deployment
**Duration:** ~5-10 minutes
**Failure mode:** If ANY check fails → rollback immediately with `./rollback.sh`

---

## 📋 PHASE 1: Container Health (1 min)

### ✅ SSH into VPS
```bash
ssh lexikon@lexikon.chessplorer.com
# or
ssh root@YOUR_VPS_IP
```

### ✅ Check all containers are running
```bash
cd /opt/lexikon
docker-compose -f docker-compose.prod.yml ps
```

**Expected output:** All 4 containers in `Up` state
```
CONTAINER ID  IMAGE                    STATUS              NAMES
xxx           postgres:16-alpine       Up 2 minutes (healthy) ✓
xxx           redis:7-alpine           Up 2 minutes (healthy) ✓
xxx           backend:latest           Up 2 minutes (healthy) ✓
xxx           nginx:alpine             Up 2 minutes (healthy) ✓
```

**If ANY container is down:**
```bash
docker-compose -f docker-compose.prod.yml logs [container-name]
./rollback.sh
```

---

## 📋 PHASE 2: Backend API Health (1 min)

### ✅ Backend health endpoint
```bash
curl -s http://127.0.0.1:8000/health | jq .
```

**Expected response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected"
}
```

**If fails:**
```bash
docker logs lexikon-backend
./rollback.sh
```

### ✅ Backend API docs (verify OpenAPI loaded)
```bash
curl -s http://127.0.0.1:8000/docs | grep -q "swagger-ui" && echo "✓ API docs accessible" || echo "✗ API docs missing"
```

---

## 📋 PHASE 3: Frontend SvelteKit SSR (2 min)

### ✅ Frontend homepage loads
```bash
curl -s http://127.0.0.1:3000/ | grep -q "<title>" && echo "✓ Frontend rendering" || echo "✗ Frontend broken"
```

### ✅ Check for server-side rendering (NOT static HTML)
```bash
curl -s http://127.0.0.1:3000/ | grep -q "svelte-kit" || head -20
# Should see HTML with actual content, not just empty placeholders
```

### ✅ Login page accessible
```bash
curl -s http://127.0.0.1:3000/login | grep -q "login" && echo "✓ /login routable" || echo "✗ /login broken"
```

**If frontend issues:**
```bash
docker logs lexikon-frontend
./rollback.sh
```

---

## 📋 PHASE 4: Reverse Proxy (Nginx) (1 min)

### ✅ Nginx reverse proxy working
```bash
curl -s http://127.0.0.1:8080/health | jq .
```

**Expected:** Same health response as direct backend

### ✅ API routing via Nginx
```bash
curl -s http://127.0.0.1:8080/api/health | jq .
```

**If nginx fails:**
```bash
docker logs lexikon-nginx
cat /opt/lexikon/nginx.conf | grep -A 5 "upstream backend"
./rollback.sh
```

---

## 📋 PHASE 5: HTTPS/SSL (1 min)

### ✅ HTTPS accessible from outside VPS
```bash
# From your local machine (NOT from VPS)
curl -s -I https://lexikon.chessplorer.com/ | head -5
```

**Expected:** HTTP/2 200 with valid SSL certificate
```
HTTP/2 200
content-type: text/html
...
```

### ✅ Check SSL certificate validity
```bash
# From your local machine
echo | openssl s_client -servername lexikon.chessplorer.com -connect lexikon.chessplorer.com:443 2>/dev/null | grep "Verify return code"
```

**Expected:** `Verify return code: 0 (ok)`

**If SSL fails:**
- Check Caddy (from chessplorer project): `docker -H unix:///var/run/docker-chessplorer.sock ps`
- Verify domain DNS: `nslookup lexikon.chessplorer.com`
- Manually renew cert: `certbot renew --force-renewal`

---

## 📋 PHASE 6: Database & Redis (1 min)

### ✅ PostgreSQL responding
```bash
docker exec lexikon-postgres psql -U postgres -c "SELECT version();" 2>/dev/null && echo "✓ PostgreSQL OK" || echo "✗ PostgreSQL failed"
```

### ✅ Redis responding
```bash
docker exec lexikon-redis redis-cli ping
```

**Expected:** `PONG`

---

## 📋 PHASE 7: Monitoring (1 min - Optional)

### ✅ Uptime Kuma accessible
```bash
curl -s http://127.0.0.1:3001/ | grep -q "uptime-kuma" && echo "✓ Monitoring OK" || echo "✗ Monitoring check failed"
```

### ✅ Check monitoring via Nginx
```bash
curl -s http://127.0.0.1:8080/monitoring/ | grep -q "uptime" && echo "✓ Monitoring routed" || echo "⚠ Monitoring unreachable"
```

---

## 📋 PHASE 8: Test API Integration (2 min - Optional)

### ✅ Test backend ↔ frontend communication

**Option A: Via local curl**
```bash
# Create test user (backend)
curl -X POST http://127.0.0.1:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TempPass123!"}'

# Expected: 200 or 409 (already exists)
```

**Option B: Via browser**
- Navigate to https://lexikon.chessplorer.com/
- Verify no console errors (F12 → Console)
- Try signup/login form

---

## 🚨 ROLLBACK PROCEDURE

If ANY check fails, **abort immediately**:

```bash
# From VPS, in /opt/lexikon directory
./rollback.sh

# Verify rollback successful
docker-compose -f docker-compose.prod.yml ps
curl -s http://127.0.0.1:8000/health | jq .
```

**After rollback:**
1. Check logs: `docker logs lexikon-backend`
2. Review commits: `git log --oneline -5`
3. Identify issue
4. Fix locally on `develop` branch
5. Re-test on VPS after fix

---

## 📊 Quick Check Script (Copy & Paste)

```bash
#!/bin/bash
# Run this entire script after deploying to VPS

set -e
cd /opt/lexikon

echo "🔍 Running Lexikon post-deployment checks..."
echo ""

# Phase 1: Containers
echo "1️⃣  Container health:"
docker-compose -f docker-compose.prod.yml ps | tail -5

# Phase 2: Backend
echo -e "\n2️⃣  Backend health:"
curl -s http://127.0.0.1:8000/health | jq . || echo "❌ Backend unreachable"

# Phase 3: Frontend
echo -e "\n3️⃣  Frontend rendering:"
curl -s http://127.0.0.1:3000/ | head -30 | grep -o "<title>.*</title>" || echo "❌ Frontend not rendering"

# Phase 4: Nginx
echo -e "\n4️⃣  Nginx proxy:"
curl -s http://127.0.0.1:8080/health | jq . || echo "❌ Nginx unreachable"

# Phase 5: HTTPS
echo -e "\n5️⃣  HTTPS status:"
curl -s -I https://lexikon.chessplorer.com/ | head -1

# Phase 6: Database
echo -e "\n6️⃣  PostgreSQL:"
docker exec lexikon-postgres psql -U postgres -c "SELECT 'Connected' as status;" 2>/dev/null || echo "❌ PostgreSQL unreachable"

echo -e "\n✅ Post-deployment checks complete!"
```

**To use this script:**
```bash
# Save to: /opt/lexikon/post-deploy-check.sh
# Then run:
chmod +x /opt/lexikon/post-deploy-check.sh
./post-deploy-check.sh
```

---

## 📝 Log Files to Check (if something fails)

```bash
# Container logs
docker logs lexikon-backend         # Most issues are here
docker logs lexikon-frontend
docker logs lexikon-nginx
docker logs lexikon-postgres

# System logs (on VPS)
tail -50 /var/log/syslog | grep docker
tail -50 /var/log/docker.log (if exists)

# Application logs (inside backend container)
docker exec lexikon-backend tail -50 /app/logs/app.log
```

---

## ✨ Success Indicators

After running all checks, you should see:

```
✅ All 4 containers UP
✅ Backend /health returns JSON
✅ Frontend homepage renders (HTML with content)
✅ Nginx proxies requests correctly
✅ HTTPS works (HTTP/2 200)
✅ PostgreSQL & Redis connected
✅ API responds to requests
```

---

## 🔄 Typical Workflow

```bash
# 1. On your local machine
git add .
git commit -m "feat: Add new feature"
git push origin develop

# 2. SSH to VPS
ssh lexikon@lexikon.chessplorer.com
cd /opt/lexikon

# 3. Deploy
./deploy.sh

# 4. Verify (this checklist)
./post-deploy-check.sh

# 5. If all green → production is updated ✅
# 6. If any red → rollback immediately
./rollback.sh
```

---

**Last updated:** November 24, 2025
**Applies to:** Lexikon v2.0+ (SvelteKit SSR + Docker Compose)
