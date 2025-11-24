# 🚀 LEXIKON VPS DEPLOYMENT - START HERE

**Choose your path based on your situation:**

---

## 🎯 Scenario 1: "SSH doesn't work, I access VPS via console/browser"

**👉 Use this:** `COPYPASTE_VPS.txt`

Simple copy-paste commands you can paste directly into your VPS console.

```bash
# Just copy-paste these exact lines:

cd /opt/lexikon
git pull origin develop
./deploy.sh
./post-deploy-check.sh
```

**That's it.** Should take 5-10 minutes total.

---

## 📋 Scenario 2: "I want to understand what's being tested"

**👉 Use this:** `DEPLOYMENT_CHECKLIST_VPS.md`

Detailed 8-phase verification checklist with:
- Expected outputs for each check
- How to interpret results
- Troubleshooting for each phase
- Rollback procedure

---

## 📚 Scenario 3: "Something failed and I need to fix it"

**👉 Use this:** `VPS_QUICK_COMMANDS.md`

Comprehensive reference with:
- How to view logs
- Manual troubleshooting commands
- Common issues & solutions
- How to debug each component

---

## 🤖 Scenario 4: "I want automatic verification after every deploy"

**👉 Use this:** `post-deploy-check.sh`

Run this after `./deploy.sh`:
```bash
./post-deploy-check.sh
```

Shows you instantly:
- ✅ All components healthy
- ❌ What failed (with solution)
- 📊 Overall success rate

---

## 📖 Scenario 5: "I'm new and need a complete overview"

**👉 Use this:** `VPS_TESTING_README.md`

Complete guide covering:
- Why test on VPS instead of locally
- All 8 components being tested
- Typical workflows
- Success/failure examples
- Emergency procedures

---

## 🚨 Emergency Rollback

**If anything goes wrong:**

```bash
cd /opt/lexikon
./rollback.sh
./post-deploy-check.sh
```

This restores the previous working version instantly.

---

## ⚡ The Fastest Path (TL;DR)

```bash
# 1. On VPS console/terminal, paste this:
cd /opt/lexikon && git pull origin develop && ./deploy.sh && ./post-deploy-check.sh

# 2. Wait for results
# 3. If ✅ green → Production updated successfully
# 4. If ❌ red → Run: ./rollback.sh
```

---

## 📍 File Map

| File | Best for | Time |
|------|----------|------|
| **COPYPASTE_VPS.txt** | Direct VPS terminal | 5 min |
| **post-deploy-check.sh** | Automated verification | 5 min |
| **DEPLOYMENT_CHECKLIST_VPS.md** | Understanding what's tested | 10 min read |
| **VPS_QUICK_COMMANDS.md** | Troubleshooting | 20 min reference |
| **VPS_TESTING_README.md** | Full overview | 15 min read |
| **VPS_SETUP_CHECKLIST.sh** | First-time VPS setup | 2 min (one-time) |

---

## ✅ Your First Deploy

### Step 1: Push code (local machine)
```bash
git add .
git commit -m "your message"
git push origin develop
```

### Step 2: Deploy (VPS console)
```bash
cd /opt/lexikon
git pull origin develop
./deploy.sh
```

Wait for it to finish. You'll see:
```
✅ Backend tests PASSED
✅ All containers healthy
```

### Step 3: Verify (VPS console)
```bash
./post-deploy-check.sh
```

Expected result:
```
✅ ALL CHECKS PASSED
Success rate: 100%
Production is HEALTHY - Ready for traffic!
```

**Done!** Your code is live on the VPS. 🎉

---

## 🔍 What Gets Tested Automatically?

When you run `./post-deploy-check.sh`, it checks:

1. ✅ All 4 Docker containers running
2. ✅ Backend API is healthy
3. ✅ Frontend is rendering (SvelteKit SSR)
4. ✅ Dynamic routes work
5. ✅ Nginx proxying correctly
6. ✅ HTTPS/SSL certificate valid
7. ✅ Database & Redis connected
8. ✅ Monitoring is accessible

---

## 🚀 Common Workflows

### Deploy a bug fix
```bash
# Local
git add . && git commit -m "fix: bug description" && git push origin develop

# VPS
cd /opt/lexikon && git pull && ./deploy.sh && ./post-deploy-check.sh
```

### Deploy a new feature
```bash
# Local
git add . && git commit -m "feat: feature name" && git push origin develop

# VPS
cd /opt/lexikon && git pull && ./deploy.sh && ./post-deploy-check.sh
```

### Emergency rollback
```bash
# VPS
cd /opt/lexikon && ./rollback.sh && ./post-deploy-check.sh
```

---

## 🆘 If Something's Wrong

**Option 1: Check logs**
```bash
docker logs lexikon-backend        # Most issues here
docker logs lexikon-frontend
docker logs lexikon-nginx
```

**Option 2: Manual health check**
```bash
curl http://127.0.0.1:8000/health  # Backend
curl http://127.0.0.1:3000/        # Frontend
curl http://127.0.0.1:8080/health  # Nginx
```

**Option 3: Instant rollback**
```bash
./rollback.sh
```

**Option 4: Full debugging guide**
See `VPS_QUICK_COMMANDS.md` → Troubleshooting section

---

## 🎯 Key Principles

1. **SSH down?** → Use VPS console directly
2. **First time?** → Follow "Your First Deploy" above
3. **Need details?** → Check the relevant file from "File Map"
4. **Something broke?** → Always `./rollback.sh` first, investigate later
5. **Always test** → Run `./post-deploy-check.sh` after deploy

---

## 📞 Quick Reference

| Need | Command |
|------|---------|
| Deploy | `./deploy.sh` |
| Verify | `./post-deploy-check.sh` |
| Rollback | `./rollback.sh` |
| Check backend | `curl http://127.0.0.1:8000/health` |
| Check frontend | `curl http://127.0.0.1:3000/` |
| View backend logs | `docker logs -f lexikon-backend` |
| View all containers | `docker ps` |
| HTTPS check | `curl -I https://lexikon.chessplorer.com` |
| Help | Read the file map above ☝️ |

---

**Next step:** Pick your scenario from the top and follow that file. 🚀

---

*Last updated: November 24, 2025*
*For Lexikon v2.0+ on Hostinger VPS*
