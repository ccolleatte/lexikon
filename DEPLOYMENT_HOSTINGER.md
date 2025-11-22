# Lexikon Deployment Guide - Hostinger VPS

**Date:** 2025-11-22
**Target:** Hostinger VPS
**Setup:** Docker + nginx + SSL/TLS
**Duration:** ~30-45 minutes

---

## 📋 Pre-Deployment Checklist

### 1. Hostinger VPS Setup
- [ ] VPS provisioned (recommended: 2GB RAM, 2vCPU, 50GB storage minimum)
- [ ] SSH access verified
- [ ] Root or sudo access available
- [ ] Ubuntu 22.04 LTS or similar

### 2. Domain & DNS
- [ ] Domain purchased
- [ ] DNS A record points to VPS IP
- [ ] DNS propagated (test with `nslookup your-domain.com`)
- [ ] SSL certificate domain ready

### 3. Secrets Generated
- [ ] `POSTGRES_PASSWORD` (32+ chars): `openssl rand -hex 32`
- [ ] `NEO4J_PASSWORD` (32+ chars): `openssl rand -hex 32`
- [ ] `JWT_SECRET` (32+ chars): `openssl rand -hex 32`
- [ ] `API_KEY_SECRET` (32+ chars): `openssl rand -hex 32`

### 4. Files Ready
- [ ] `.env.prod` filled (copy from `.env.prod.example`)
- [ ] Deploy scripts executable (`chmod +x deploy.sh health-check.sh rollback.sh`)

---

## 🚀 Step 1: Initial VPS Setup (10 min)

SSH into your Hostinger VPS:

```bash
ssh root@your-vps-ip
```

### Update system
```bash
apt update && apt upgrade -y
```

### Create lexikon user (recommended, not root)
```bash
useradd -m -s /bin/bash lexikon
usermod -aG sudo lexikon
```

### Create directories
```bash
mkdir -p /opt/lexikon
mkdir -p /opt/lexikon-backups
chown lexikon:lexikon /opt/lexikon
chown lexikon:lexikon /opt/lexikon-backups
```

### Install Docker (as root)
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Add lexikon user to docker group
usermod -aG docker lexikon

# Verify installation
docker --version
docker-compose --version
```

---

## 🔑 Step 2: Generate Secrets & Create .env.prod (5 min)

Switch to lexikon user:
```bash
su - lexikon
```

Generate secrets:
```bash
# Copy and run these commands
POSTGRES_PASSWORD=$(openssl rand -hex 32)
NEO4J_PASSWORD=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)
API_KEY_SECRET=$(openssl rand -hex 32)

echo "POSTGRES_PASSWORD=$POSTGRES_PASSWORD"
echo "NEO4J_PASSWORD=$NEO4J_PASSWORD"
echo "JWT_SECRET=$JWT_SECRET"
echo "API_KEY_SECRET=$API_KEY_SECRET"
```

Create `.env.prod`:
```bash
cd /opt/lexikon
cat > .env.prod << 'EOF'
# Database
POSTGRES_DB=lexikon
POSTGRES_USER=lexikon
POSTGRES_PASSWORD=<PASTE_POSTGRES_PASSWORD>

# Neo4j
NEO4J_PASSWORD=<PASTE_NEO4J_PASSWORD>

# JWT & Security
JWT_SECRET=<PASTE_JWT_SECRET>
API_KEY_SECRET=<PASTE_API_KEY_SECRET>

# Application
FRONTEND_URL=https://your-domain.com
CORS_ORIGINS=https://your-domain.com

# OAuth (leave empty if not using)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=

GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
GITHUB_REDIRECT_URI=
EOF
```

⚠️ **IMPORTANT:** Replace `<PASTE_*>` values with actual secrets!

Secure the file:
```bash
chmod 600 .env.prod
```

---

## 🔒 Step 3: Setup SSL/TLS Certificates (10 min)

Install certbot:
```bash
sudo apt install certbot python3-certbot-nginx -y
```

Get certificate from Let's Encrypt:
```bash
sudo certbot certonly --standalone -d your-domain.com --agree-tos -m your-email@example.com
```

Copy certificates to Lexikon directory:
```bash
sudo mkdir -p /opt/lexikon/ssl
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem /opt/lexikon/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem /opt/lexikon/ssl/key.pem
sudo chown lexikon:lexikon /opt/lexikon/ssl -R
```

### Auto-renew certificate (cron job)
```bash
# As root:
sudo crontab -e

# Add this line:
0 2 * * * certbot renew --quiet && cp /etc/letsencrypt/live/your-domain.com/*.pem /opt/lexikon/ssl/
```

---

## 📦 Step 4: Clone Repository & Deploy (15 min)

As lexikon user:
```bash
cd /opt/lexikon

# Initialize git (first time only)
git init
git remote add origin https://github.com/ccolleatte/lexikon.git
git fetch origin
git reset --hard origin/master
```

### Or if already cloned:
```bash
cd /opt/lexikon
git pull origin master
```

Make scripts executable:
```bash
chmod +x deploy.sh health-check.sh rollback.sh
```

Run deployment:
```bash
./deploy.sh
```

This script will:
1. Check requirements (Docker, .env.prod)
2. Create backup
3. Pull latest code
4. Build Docker images
5. Run tests
6. Setup SSL
7. Start services
8. Verify deployment

---

## ✅ Step 5: Verify Deployment

Check health:
```bash
./health-check.sh
```

Test API endpoint:
```bash
curl https://your-domain.com/api/health
```

View logs:
```bash
docker-compose -f docker-compose.prod.yml logs -f backend
```

Check running containers:
```bash
docker-compose -f docker-compose.prod.yml ps
```

---

## 🔄 Maintenance & Monitoring

### Daily backup cron job (as root)
```bash
# Add to crontab:
0 3 * * * /opt/lexikon/deploy.sh >> /var/log/lexikon-deploy.log 2>&1
```

### View logs
```bash
# Real-time logs
docker-compose -f /opt/lexikon/docker-compose.prod.yml logs -f

# Last 100 lines
docker-compose -f /opt/lexikon/docker-compose.prod.yml logs --tail=100
```

### Update application
```bash
cd /opt/lexikon
git pull origin master
./deploy.sh
```

### Check disk usage
```bash
df -h /opt/lexikon
```

### Monitor memory/CPU
```bash
docker stats
```

---

## 🚨 Emergency: Rollback

If something goes wrong:

```bash
cd /opt/lexikon
./rollback.sh
```

This will:
1. Stop all services
2. Restore previous database backup
3. Restore previous Redis backup
4. Revert git to previous commit
5. Restart services

---

## 🔧 Troubleshooting

### Port 80/443 already in use
```bash
# Find what's using the port
sudo lsof -i :80
sudo lsof -i :443

# Kill the process
sudo kill <PID>
```

### Docker daemon not responding
```bash
sudo systemctl restart docker
```

### Certificate renewal failed
```bash
# Check certificate status
sudo certbot certificates

# Renew manually
sudo certbot renew --force-renewal
```

### Database won't start
```bash
# Check PostgreSQL logs
docker logs lexikon-postgres

# Reset database (WARNING: data loss)
docker volume rm lexikon_postgres_data
docker-compose -f docker-compose.prod.yml up -d postgres
```

### Backend won't start
```bash
# Check logs
docker logs lexikon-backend

# Rebuild image
docker-compose -f docker-compose.prod.yml build --no-cache backend

# Restart
docker-compose -f docker-compose.prod.yml restart backend
```

---

## 📊 Production Best Practices

### 1. Backups
- Daily automated backups (via deploy.sh)
- Store offsite (Hostinger backup, S3, etc.)
- Test restore quarterly

### 2. Monitoring
- Check health daily: `./health-check.sh`
- Monitor disk usage: `df -h`
- Review logs weekly: `docker logs`

### 3. Security
- Firewall enabled (Hostinger panel)
- SSH key-only access (disable password login)
- Keep Docker images updated
- Rotate secrets annually

### 4. Performance
- Monitor Redis memory: `docker exec lexikon-redis redis-cli INFO`
- Check database size: `docker exec lexikon-postgres psql -U lexikon -c '\dt+'`
- Monitor CPU/RAM: `docker stats`

### 5. Updates
- Update Docker regularly: `docker system prune`
- Update Ubuntu: `sudo apt upgrade`
- Update application: `git pull && ./deploy.sh`

---

## 📞 Support

### Logs location
```bash
/opt/lexikon/docker-compose.prod.yml # Docker config
/opt/lexikon/nginx.conf # Nginx config
/opt/lexikon/ssl/ # SSL certificates
/opt/lexikon-backups/ # Backup files
```

### Common commands
```bash
# Status
docker-compose -f /opt/lexikon/docker-compose.prod.yml ps

# Logs
docker-compose -f /opt/lexikon/docker-compose.prod.yml logs backend

# Restart all services
docker-compose -f /opt/lexikon/docker-compose.prod.yml restart

# Stop all services
docker-compose -f /opt/lexikon/docker-compose.prod.yml down

# Full system prune
docker system prune -a --volumes
```

---

## ✨ Next Steps

After deployment:
1. [ ] Access application at https://your-domain.com
2. [ ] Create admin account
3. [ ] Test key features
4. [ ] Setup monitoring
5. [ ] Document any customizations
6. [ ] Schedule regular backups

---

**Last Updated:** 2025-11-22
**Status:** Production Ready ✅

