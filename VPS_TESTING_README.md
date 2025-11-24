# 🚀 VPS Testing & Deployment Guide

**Quick navigation:**
- 👉 **Start here:** `COPYPASTE_VPS.txt` (ultra-simple copy-paste commands)
- 📋 **Full checklist:** `DEPLOYMENT_CHECKLIST_VPS.md` (detailed 8-phase verification)
- 📚 **Complete guide:** `VPS_QUICK_COMMANDS.md` (all options + troubleshooting)
- 🤖 **Auto script:** `post-deploy-check.sh` (automated verification)

---

## 🎯 Why Test on VPS Instead of Locally?

1. **Isolation** - Your other projects on `C:\dev` won't be affected
2. **Realistic conditions** - Full Docker stack with PostgreSQL, Redis, Nginx, etc.
3. **Validate deployment** - Tests the actual deploy.sh pipeline
4. **No local pollution** - No stray containers/services affecting your work

---

## 🏃 Quick Start (3 steps)

### Step 1: Push your code
```bash
# On your local machine (Windows)
git add .
git commit -m "feat: your feature"
git push origin develop
```

### Step 2: Deploy on VPS
Access your VPS console/terminal and run:
```bash
cd /opt/lexikon
git pull origin develop
./deploy.sh
```

### Step 3: Verify
```bash
./post-deploy-check.sh
```

**Expected result:**
```
✅ ALL CHECKS PASSED
Success rate: 100%
Production is HEALTHY - Ready for traffic!
```

---

## 📋 Files Included

| File | Purpose | When to use |
|------|---------|------------|
| **COPYPASTE_VPS.txt** | Quick commands to copy-paste | First time, simple workflows |
| **post-deploy-check.sh** | Automated verification script | After every deploy |
| **DEPLOYMENT_CHECKLIST_VPS.md** | Detailed checklist with 8 phases | Understanding what's tested |
| **VPS_QUICK_COMMANDS.md** | Complete reference + troubleshooting | When something goes wrong |
| **VPS_SETUP_CHECKLIST.sh** | Setup script (run once) | First deployment on new VPS |

---

## 🔍 What Gets Tested?

The verification script checks 8 critical components:

```
1. Docker Containers
   ✓ All 4 containers running and healthy

2. Backend API
   ✓ /health endpoint responds
   ✓ Database connected
   ✓ Redis connected
   ✓ OpenAPI docs accessible

3. Frontend SvelteKit
   ✓ Homepage renders HTML (SSR)
   ✓ Routes are dynamic (not static HTML)
   ✓ /login route responds
   ✓ /signup route responds

4. Nginx Reverse Proxy
   ✓ Proxies to backend correctly
   ✓ /api/* routes work

5. HTTPS/SSL
   ✓ Certificate is valid
   ✓ HTTPS accessible externally

6. Database & Cache
   ✓ PostgreSQL responding
   ✓ Redis responding

7. Monitoring
   ✓ Uptime Kuma accessible (optional)

8. API Integration
   ✓ Frontend ↔ Backend communication
```

---

## 🚨 If Something Fails

**Immediate action:**
```bash
./rollback.sh
```

This will restore the previous working version instantly.

**Then investigate:**
```bash
# View logs of the failing component
docker logs lexikon-backend
docker logs lexikon-frontend
docker logs lexikon-nginx

# Or check specific endpoints
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:3000/
```

**Fix locally, then retry:**
1. Identify the issue from logs
2. Fix on your local `develop` branch
3. Test locally if needed
4. Push to git
5. Run deploy again on VPS
6. Run verification again

---

## 🔄 Typical Workflows

### Workflow 1: Simple Feature Deploy

```bash
# Local (Windows)
git add .
git commit -m "feat: add login form"
git push origin develop

# VPS console
cd /opt/lexikon && git pull && ./deploy.sh && ./post-deploy-check.sh
```

### Workflow 2: With Testing

```bash
# Local - run tests before pushing
npm test
npm run test:e2e

# If all pass, deploy
git push origin develop

# VPS
./deploy.sh && ./post-deploy-check.sh
```

### Workflow 3: Emergency Rollback

```bash
# VPS - if deployment fails
./rollback.sh

# Then
./post-deploy-check.sh

# Verify it's back to previous version
```

---

## 📊 Verification Output Examples

### ✅ Success (100% green)

```
╔════════════════════════════════════════════════════════════════╗
║      🚀 LEXIKON POST-DEPLOYMENT VERIFICATION CHECKLIST       ║
╚════════════════════════════════════════════════════════════════╝

1️⃣  Container health:
    CONTAINER ID  STATUS              NAMES
    xxx           Up 2 minutes (healthy) ✓

2️⃣  Backend health:
    {"status": "healthy", "database": "connected", "redis": "connected"}

3️⃣  Frontend rendering:
    ✅ Frontend rendering HTML

... (more checks)

Total checks:  8
Passed:        8 ✅
Failed:        0
Success rate:  100%

╔════════════════════════════════════════════════════════════════╗
║                    ✅ ALL CHECKS PASSED                       ║
║  Production is HEALTHY - Ready for traffic!                   ║
╚════════════════════════════════════════════════════════════════╝
```

### ❌ Failure (at least one red)

```
Total checks:  8
Passed:        7 ✅
Failed:        1 ❌
Success rate:  87%

❌ Backend unreachable at http://127.0.0.1:8000

╔════════════════════════════════════════════════════════════════╗
║                 ❌ SOME CHECKS FAILED                         ║
║  Review errors above and consider rollback:                   ║
║  $ ./rollback.sh                                               ║
╚════════════════════════════════════════════════════════════════╝
```

---

## 🆘 Common Issues & Fixes

### Issue: "Backend unreachable"

```bash
# Check if container is running
docker ps | grep lexikon-backend

# Check logs
docker logs lexikon-backend

# If container isn't running
docker-compose -f docker-compose.prod.yml up -d backend

# Rollback if still failing
./rollback.sh
```

### Issue: "Frontend showing blank page"

```bash
# Check if frontend container is running
docker ps | grep lexikon-frontend

# Check logs
docker logs lexikon-frontend

# Check if SvelteKit SSR is working
curl -v http://127.0.0.1:3000/

# Expected: HTML content returned (not 404)
```

### Issue: "API calls returning 500 errors"

```bash
# Check backend logs
docker logs -f lexikon-backend

# Check database is up
docker exec lexikon-postgres psql -U postgres -c "SELECT COUNT(*) FROM users;"

# Check Redis is up
docker exec lexikon-redis redis-cli ping
```

### Issue: "HTTPS not working"

```bash
# From your local machine
curl -I https://lexikon.chessplorer.com

# If fails, check if Caddy (from chessplorer project) is running
docker ps | grep caddy

# Check Caddy logs
docker logs caddy

# Force renew certificate
certbot renew --force-renewal
```

---

## ⚙️ Environment & Configuration

### Location of key files on VPS

```
/opt/lexikon/
├── deploy.sh                      # Deployment automation
├── rollback.sh                    # Instant rollback
├── post-deploy-check.sh          # Verification (THIS ONE!)
├── docker-compose.prod.yml       # Production stack
├── docker-compose.monitoring.yml # Monitoring stack
├── nginx.conf                    # Nginx configuration
├── .env.prod                     # Secrets (in .gitignore)
├── Dockerfile.frontend           # Frontend build
├── Dockerfile                    # Backend build
└── backend/
    └── tests/                    # Backend tests
```

### Secrets location

```bash
# On VPS, secrets are in:
/opt/lexikon/.env.prod

# Never commit this to git
# Contains: POSTGRES_PASSWORD, JWT_SECRET, etc.
```

---

## 📈 Performance Monitoring

### Real-time container stats
```bash
docker stats
```

### Memory & disk usage
```bash
free -h          # Memory
df -h            # Disk space
du -sh /opt/*    # What's taking space
```

### Network connectivity
```bash
# From VPS
curl -I https://lexikon.chessplorer.com

# Check DNS
nslookup lexikon.chessplorer.com

# Check Uptime Kuma
curl http://127.0.0.1:3001/
```

---

## 🔐 Security Notes

1. **Never share** `.env.prod` file
2. **Never commit** secrets to git
3. **Always rollback** if deployment fails
4. **Run tests** before deploying (part of `./deploy.sh`)
5. **Monitor logs** for suspicious activity

```bash
# View security-related logs
docker logs -f lexikon-nginx | grep "401\|403\|rate limit"
```

---

## 📞 Support & Troubleshooting

**Need help?**

1. Check `VPS_QUICK_COMMANDS.md` for your specific issue
2. Run `docker logs` command for the failing component
3. Look at `DEPLOYMENT_CHECKLIST_VPS.md` for expected outputs
4. If all else fails: `./rollback.sh` → investigate → fix → redeploy

---

## 🎓 Learning Resources

- **Understand the checks:** `DEPLOYMENT_CHECKLIST_VPS.md` (explains each of the 8 checks)
- **See all commands:** `VPS_QUICK_COMMANDS.md` (comprehensive reference)
- **Simple copy-paste:** `COPYPASTE_VPS.txt` (just the basics)
- **Watch it run:** `./post-deploy-check.sh` (see automated verification in action)

---

## ✅ Success Criteria

After `./post-deploy-check.sh`, you should see:

```
✅ Containers: UP and healthy
✅ Backend: /health responds
✅ Frontend: HTML rendering (SSR)
✅ Nginx: Proxying correctly
✅ HTTPS: Valid certificate
✅ Database: Connected
✅ Redis: Connected
✅ Success rate: 100%

Production is HEALTHY - Ready for traffic! 🚀
```

---

**Last updated:** November 24, 2025
**For:** Lexikon v2.0+ on Hostinger VPS
**Tested on:** Ubuntu 22.04 LTS with Docker Compose
