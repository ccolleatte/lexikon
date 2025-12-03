# 🚀 Lexikon - Start Here

**Welcome! Your parcours utilisateur alignment is ready for VPS testing.**

## 📋 What Happened?

Your user journeys are now **deployable to production**. The backend was complete but not containerized. We've fixed that.

### Before
- ❌ Backend not running
- ❌ Frontend API calls returned 404
- ❌ No user data persisted

### After
- ✅ Backend containerized (Dockerfile ready)
- ✅ Frontend containerized (Dockerfile ready)
- ✅ Complete Docker Compose stack
- ✅ Automated VPS deployment script
- ✅ Comprehensive testing documentation

## 🎯 Quick Path to Testing

### Option A: Deploy to VPS (Recommended)

**Prerequisites**: VPS with Docker + domain name

```bash
# 1. SSH to VPS
ssh user@your-vps-ip

# 2. Clone & setup
cd /opt
git clone https://github.com/ccolleatte/lexikon.git
cd lexikon

# 3. Generate secrets (copy-paste output)
JWT_SECRET=$(openssl rand -hex 32)
API_KEY_SECRET=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -hex 32)
REDIS_PASSWORD=$(openssl rand -hex 32)

echo "Save these values:"
echo "JWT_SECRET=$JWT_SECRET"
echo "API_KEY_SECRET=$API_KEY_SECRET"
echo "POSTGRES_PASSWORD=$POSTGRES_PASSWORD"
echo "REDIS_PASSWORD=$REDIS_PASSWORD"

# 4. Create .env.prod
cp .env.prod.example .env.prod
nano .env.prod  # Paste secrets

# 5. Deploy (5 minutes)
chmod +x deploy-vps.sh
./deploy-vps.sh production

# 6. Access at https://your-domain.com
```

**Total time**: ~20 minutes

### Option B: Local Testing (Docker Desktop)

```bash
# On your machine
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Access at http://localhost:3000
# API at http://localhost:8000
```

## 📚 Documentation

Choose based on your needs:

### 🏃 I'm in a hurry
→ **QUICK_START_VPS.md** (2 min read)

### 🔧 I want step-by-step
→ **DEPLOYMENT_VPS.md** (15 min read, 25 min deploy)

### ✅ I want to test everything
→ **TEST_USER_JOURNEYS.md** (detailed test cases)

### 📊 I want to understand what happened
→ **IMPLEMENTATION_SUMMARY.md** (architecture overview)

## 🧪 What to Test

Once deployed, test these user journeys:

1. **Registration** - Create account
2. **Onboarding** - Select adoption level + profile
3. **Term Creation** - Create your first term (< 5 min)
4. **Login** - Log out, log back in
5. **Persistence** - Refresh page, data still there

See **TEST_USER_JOURNEYS.md** for detailed procedures with expected results.

## 🐛 Troubleshooting

### Services not starting?
```bash
docker-compose -f docker-compose.prod.yml logs
```

### API returns 502?
```bash
curl http://localhost:8000/health
docker-compose -f docker-compose.prod.yml logs lexikon-backend
```

### Database won't migrate?
```bash
docker-compose -f docker-compose.migrate.yml --env-file .env.prod logs
```

See **DEPLOYMENT_VPS.md** for detailed troubleshooting.

## 📁 Key Files Created

| File | Purpose |
|------|---------|
| `Dockerfile.frontend` | SvelteKit containerization |
| `Dockerfile.backend` | FastAPI containerization |
| `docker-compose.migrate.yml` | Database migrations |
| `deploy-vps.sh` | Automated deployment script |
| `DEPLOYMENT_VPS.md` | Complete guide (25 min read) |
| `QUICK_START_VPS.md` | TL;DR version (2 min read) |
| `TEST_USER_JOURNEYS.md` | All 8 test procedures |
| `IMPLEMENTATION_SUMMARY.md` | Architecture & decisions |

## ✨ What's Ready to Test

### User Journeys (All Specification-Compliant)
- ✅ **US-001**: Adoption level selection (radio buttons)
- ✅ **US-002**: Quick term creation (3 fields, < 5 min)
- ✅ **US-003**: Profile setup (8 fields, multi-step)
- ✅ **Auth**: Registration, login, logout
- ✅ **Token Management**: JWT refresh, expiry

### Not Yet Tested (But Code Ready)
- 🟡 OAuth Google (needs credentials configuration)
- 🟡 Email verification (needs SMTP)
- 🟡 Advanced term modes (Ready/Expert)
- 🟡 Neo4j integration (deferred for MVP)

## 🚦 Next Steps

### Right Now (5-10 min)
1. Read **QUICK_START_VPS.md** OR **DEPLOYMENT_VPS.md**
2. Decide: Deploy to VPS or test locally

### Today (20-30 min)
1. Deploy using `./deploy-vps.sh production`
2. Navigate to your domain
3. Test registration flow

### This Week (2-3 hours)
1. Run all tests from **TEST_USER_JOURNEYS.md**
2. Document any issues/gaps
3. Verify database persistence

### Next Steps (Future)
1. Configure OAuth Google
2. Setup email verification
3. Add advanced term modes
4. User acceptance testing

## 🎓 Architecture Highlights

```
VPS
├── nginx (reverse proxy, SSL)
├── Docker Compose
│   ├── Frontend (SvelteKit, port 3000)
│   ├── Backend (FastAPI, port 8000)
│   ├── PostgreSQL (database)
│   ├── Redis (cache)
│   └── Uptime Kuma (monitoring)
└── SSL/TLS (Let's Encrypt)
```

All data persisted in PostgreSQL. All traffic encrypted.

## 📞 Support

### Stuck on deployment?
See **DEPLOYMENT_VPS.md** → Troubleshooting section

### Stuck on testing?
See **TEST_USER_JOURNEYS.md** → Your specific journey

### Stuck on architecture?
See **IMPLEMENTATION_SUMMARY.md** → Complete overview

### Git related?
```bash
git log --oneline | head  # See commit history
git diff HEAD~1           # See latest changes
git reset --hard HEAD~1   # Rollback if needed
```

## ✅ Success Criteria

You'll know it's working when:

1. ✅ Can navigate to `https://your-domain.com`
2. ✅ Can create account at `/register`
3. ✅ Onboarding flow completes (3 steps)
4. ✅ Can create a term in < 5 minutes
5. ✅ Data persists after page refresh
6. ✅ API returns `{"status": "healthy"}` at `/api/health`

## 🎯 The Goal

**Align user journeys with specification by enabling production-like testing on VPS infrastructure.**

This implementation provides:
- Production-ready Docker configuration
- Automated deployment with safety checks
- Comprehensive testing procedures
- Clear rollback capability

All 8 user journeys are now testable end-to-end.

---

## 📖 Documentation Map

```
START_HERE.md (you are here)
├── For 2-min overview
│   └── QUICK_START_VPS.md
├── For complete guide
│   ├── DEPLOYMENT_VPS.md
│   ├── TEST_USER_JOURNEYS.md
│   └── IMPLEMENTATION_SUMMARY.md
└── To understand code
    ├── Dockerfile.frontend
    ├── Dockerfile.backend
    ├── deploy-vps.sh
    ├── docker-compose.prod.yml
    └── docker-compose.migrate.yml
```

## 🚀 Ready?

Pick your path:

**➜ QUICK_START_VPS.md** - Deploy in 20 minutes
**➜ DEPLOYMENT_VPS.md** - Full guidance, 25 min
**➜ IMPLEMENTATION_SUMMARY.md** - Understand what happened

---

**Questions? See the documentation files or check git history:**
```bash
git log --oneline -5
git show HEAD  # Latest changes
```

**Good luck! 🎉**
