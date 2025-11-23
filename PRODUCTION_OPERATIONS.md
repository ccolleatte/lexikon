# Production Operations Guide - Lexikon

**Date:** 2025-11-23
**Environment:** Hostinger VPS Docker Production
**Target Audience:** DevOps, System Administrators, On-Call Engineers

---

## 📋 Quick Reference

### Critical Commands

```bash
# SSH into VPS
ssh lexikon@your-vps-ip

# Application directory
cd /opt/lexikon

# Status commands
docker-compose -f docker-compose.prod.yml ps          # Container status
docker-compose -f docker-compose.prod.yml logs backend # App logs
docker stats                                            # Resource usage

# Deployment
./deploy.sh                                             # Full deployment
./health-check.sh                                       # Health verification
./rollback.sh                                           # Emergency rollback
```

---

## 🔍 Monitoring & Health Checks

### Daily Health Checks (5 min)

```bash
# 1. Check all containers are running
docker-compose -f docker-compose.prod.yml ps
# Expected: All containers in "Up" status

# 2. Check application health
curl https://your-domain.com/api/health
# Expected: {"status": "healthy", "timestamp": "..."}

# 3. Check readiness (can accept traffic)
curl https://your-domain.com/api/ready
# Expected: {"status": "ready", "dependencies": {"database": "ok", "cache": "ok"}, ...}

# 4. Check certificate expiration
sudo certbot certificates
# Expected: "X days left" should be > 7 days

# 5. Check disk usage
df -h /opt/lexikon
# Expected: Usage < 80%
```

### Automated Health Check Script

```bash
# Run provided health check script
./health-check.sh

# Or create a cron job for daily checks:
sudo crontab -e

# Add:
0 9 * * * /opt/lexikon/health-check.sh > /var/log/lexikon-health.log 2>&1
```

---

## 📊 Monitoring Resources

### Memory & CPU Usage

```bash
# Real-time monitoring
docker stats

# Example output:
# CONTAINER            MEM USAGE / LIMIT    MEM %     CPU %
# lexikon-postgres     120MiB / 4GiB        3%        2%
# lexikon-redis        45MiB / 512MiB       8%        1%
# lexikon-backend      200MiB / 2GiB        10%       5%
```

### Database Disk Usage

```bash
# Connect to postgres
docker exec -it lexikon-postgres psql -U lexikon -c "
  SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
  FROM pg_tables
  WHERE schemaname != 'pg_catalog'
  ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

### Redis Memory Usage

```bash
docker exec lexikon-redis redis-cli info memory

# Key metric:
# used_memory_human:45.2M    <- Current usage
# maxmemory_human:512.0M     <- Limit (allkeys-lru policy)
```

### View Application Metrics

```bash
# Get detailed metrics
curl https://your-domain.com/api/metrics | jq

# Includes:
# - Request counts (total, success, failed)
# - Cache hit/miss rates
# - API response times
# - Database query counts
```

---

## 📝 Log Management

### View Live Logs

```bash
# Application logs (last 50 lines, follow)
docker-compose -f docker-compose.prod.yml logs -f --tail=50 backend

# Database logs
docker-compose -f docker-compose.prod.yml logs -f --tail=50 postgres

# All services
docker-compose -f docker-compose.prod.yml logs -f --tail=100
```

### View Historical Logs

```bash
# Last 1000 lines
docker logs lexikon-backend | tail -1000

# Search for errors
docker logs lexikon-backend 2>&1 | grep -i error

# Timestamp range (last 10 minutes)
docker logs lexikon-backend --since 10m
```

### Log File Location (Host)

```bash
# Docker logs are stored in JSON files
/var/lib/docker/containers/[container-id]/[container-id]-json.log

# Check available space
du -sh /var/lib/docker/

# Note: Logs are auto-rotated (max 10MB per file, 3 files kept)
# See docker-compose.prod.yml: logging.options.max-size
```

---

## 🚀 Deployment & Updates

### Standard Deployment

```bash
cd /opt/lexikon

# Pull latest code
git pull origin master

# Run deployment (includes backup, tests, deployment)
./deploy.sh

# Expected output:
# [SUCCESS] Deployment completed successfully!
# Application is available at: https://your-domain.com
```

### Deployment Steps (What ./deploy.sh Does)

1. ✅ Check requirements (Docker, .env.prod)
2. ✅ Create backup of databases
3. ✅ Clean up old backups (> 7 days)
4. ✅ Pull latest code from GitHub
5. ✅ Build Docker images
6. ✅ Run tests
7. ✅ Setup SSL/TLS certificates
8. ✅ Start services
9. ✅ Wait for health checks
10. ✅ Verify deployment

### Manual Deployment Steps (If Script Fails)

```bash
cd /opt/lexikon

# 1. Backup database
docker run --rm \
  -v lexikon_postgres_data:/data \
  -v /opt/lexikon-backups/manual_$(date +%s):/backup \
  alpine tar czf /backup/postgres_data.tar.gz -C /data .

# 2. Pull code
git pull origin master

# 3. Build images
docker-compose -f docker-compose.prod.yml build --no-cache backend

# 4. Start services
docker-compose -f docker-compose.prod.yml up -d

# 5. Verify
curl https://your-domain.com/api/health
```

### Rollback (Emergency)

```bash
cd /opt/lexikon

# Method 1: Use automated script
./rollback.sh

# Method 2: Manual rollback
docker-compose -f docker-compose.prod.yml down

# Restore database from backup
docker run --rm \
  -v /opt/lexikon-backups/latest_backup/postgres_data.tar.gz:/backup/data.tar.gz \
  -v lexikon_postgres_data:/data \
  alpine sh -c "cd /data && tar xzf /backup/data.tar.gz"

# Restart
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🔐 Certificate Management

### Check Certificate Status

```bash
# View all certificates
sudo certbot certificates

# Example output:
# Found the following certificates:
#   Certificate Name: your-domain.com
#     Expiry Date: 2026-02-20 (VALID: X days)
```

### Renew Certificate Manually

```bash
# Automatic renewal (runs daily via cron)
sudo certbot renew --quiet

# Manual renewal
sudo certbot certonly --standalone -d your-domain.com

# After renewal, copy to lexikon directory
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem /opt/lexikon/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem /opt/lexikon/ssl/key.pem
sudo chown lexikon:lexikon /opt/lexikon/ssl/*
```

### Verify HSTS Headers

```bash
# Check HSTS is configured
curl -I https://your-domain.com | grep Strict-Transport

# Expected:
# Strict-Transport-Security: max-age=63072000; includeSubDomains; preload

# Once HSTS is working, submit to preload list:
# https://hstspreload.org
```

---

## 🛡️ Security

### User & Access Management

```bash
# SSH key-only access (disable password login)
sudo sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl reload sshd

# Create sudo user (lexikon user)
sudo useradd -m -s /bin/bash lexikon
sudo usermod -aG sudo lexikon
sudo usermod -aG docker lexikon

# Copy SSH key for lexikon user
sudo mkdir -p /home/lexikon/.ssh
sudo cp ~/.ssh/authorized_keys /home/lexikon/.ssh/
sudo chown -R lexikon:lexikon /home/lexikon/.ssh
```

### Firewall Configuration (Hostinger Panel)

Required open ports:
- 22 (SSH, from your IP only)
- 80 (HTTP, redirect to 443)
- 443 (HTTPS, from anywhere)

All other ports should be closed.

### View Current Secrets

```bash
# Secrets are in .env.prod (NOT in git)
cat /opt/lexikon/.env.prod

# Check file permissions (should be readable by lexikon user only)
ls -la /opt/lexikon/.env.prod
# Expected: -rw------- 1 lexikon lexikon
```

### Rotate Secrets Annually

```bash
# 1. Generate new secrets
POSTGRES_PASSWORD=$(openssl rand -hex 32)
NEO4J_PASSWORD=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)
API_KEY_SECRET=$(openssl rand -hex 32)

# 2. Update .env.prod
sudo nano /opt/lexikon/.env.prod

# 3. Recreate database with new password
docker-compose -f docker-compose.prod.yml down postgres
docker volume rm lexikon_postgres_data
docker-compose -f docker-compose.prod.yml up -d postgres

# 4. Restart application
docker-compose -f docker-compose.prod.yml restart backend
```

---

## 💾 Backup & Recovery

### Backup Policy

- **Automatic:** Daily via `deploy.sh` cron job (3:00 AM UTC)
- **Retention:** 7 days (older backups auto-deleted)
- **Location:** `/opt/lexikon-backups/`

### Manual Backup

```bash
# Create backup now
docker run --rm \
  -v lexikon_postgres_data:/data \
  -v /opt/lexikon-backups/manual_$(date +%Y%m%d_%H%M%S):/backup \
  alpine tar czf /backup/postgres_data.tar.gz -C /data .

# Verify backup
ls -lh /opt/lexikon-backups/
```

### Restore from Backup

```bash
# 1. List available backups
ls -lh /opt/lexikon-backups/

# 2. Stop application
docker-compose -f docker-compose.prod.yml down

# 3. Restore database
BACKUP_DIR=/opt/lexikon-backups/backup_20251123_030000
docker run --rm \
  -v "$BACKUP_DIR/postgres_data.tar.gz":/backup/data.tar.gz \
  -v lexikon_postgres_data:/data \
  alpine sh -c "cd /data && tar xzf /backup/data.tar.gz"

# 4. Start services
docker-compose -f docker-compose.prod.yml up -d

# 5. Verify
curl https://your-domain.com/api/health
```

---

## 🔧 Troubleshooting

### Application Won't Start

```bash
# Check logs
docker logs lexikon-backend

# Common causes:
# 1. Database not ready - wait 10s and retry
sleep 10
docker-compose -f docker-compose.prod.yml restart backend

# 2. Configuration error - check .env.prod
docker-compose -f docker-compose.prod.yml config

# 3. Port already in use
sudo lsof -i :8000
sudo kill -9 <PID>
```

### Database Connection Error

```bash
# Check postgres is running
docker-compose -f docker-compose.prod.yml ps postgres

# Check logs
docker logs lexikon-postgres

# Verify connection
docker exec -it lexikon-postgres psql -U lexikon -c "SELECT 1"

# Check DATABASE_URL in .env.prod
grep DATABASE_URL /opt/lexikon/.env.prod
```

### Redis Connection Error

```bash
# Check redis is running
docker-compose -f docker-compose.prod.yml ps redis

# Test connection
docker exec lexikon-redis redis-cli ping
# Expected: PONG

# Check memory usage
docker exec lexikon-redis redis-cli info memory | grep used_memory_human
```

### Disk Space Issues

```bash
# Check usage
df -h /opt/lexikon

# If full:
# 1. Clean up old backups (only if recent backup exists)
rm -rf /opt/lexikon-backups/backup_*

# 2. Clean up Docker images/containers
docker system prune -a --volumes

# 3. Check logs aren't too large
du -sh /var/lib/docker/containers/

# 4. If still full, expand VPS disk (via Hostinger panel)
```

### High Memory Usage

```bash
# Check memory per service
docker stats --no-stream

# Reduce memory limits:
# Edit docker-compose.prod.yml and add:
# deploy:
#   resources:
#     limits:
#       memory: 512M

# Restart
docker-compose -f docker-compose.prod.yml restart
```

---

## 📞 Escalation Path

### Critical Issues (App Down)

1. **Immediate** (< 5 min): Run health check script
   ```bash
   ./health-check.sh
   ```

2. **Emergency Rollback** (< 10 min):
   ```bash
   ./rollback.sh
   ```

3. **Investigate** (< 30 min):
   ```bash
   docker logs lexikon-backend | tail -200
   docker-compose -f docker-compose.prod.yml ps
   ```

4. **Escalate** if above doesn't fix:
   - Check Hostinger VPS dashboard
   - Check network connectivity
   - Review recent deployments
   - Contact Hostinger support

### High-Severity Issues (Degraded Performance)

1. Check resource usage (CPU, memory, disk)
2. Review logs for errors
3. Check database query performance
4. Review recent code changes
5. Consider scaling resources (via Hostinger)

### Standard Issues (Can Wait Until Business Hours)

- Certificate renewals (check weekly)
- Backup retention cleanup (automatic)
- Security updates (deploy next scheduled window)
- Performance optimizations

---

## 📊 SLA & Monitoring Targets

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Uptime | 99.5% | < 99% weekly |
| Response Time | < 500ms | > 1000ms avg |
| Error Rate | < 0.1% | > 1% |
| CPU Usage | 20-40% | > 80% sustained |
| Memory Usage | 50-60% | > 85% |
| Disk Usage | < 70% | > 85% |

---

## 🔄 Maintenance Schedule

### Daily (Automated)

- ✅ Database backups (3:00 AM UTC)
- ✅ Log rotation
- ✅ Old backup cleanup (> 7 days)
- ✅ Health checks (via monitoring service)

### Weekly

- ✅ Certificate expiration check (Friday)
- ✅ Database size review
- ✅ Security update check

### Monthly

- ✅ Performance review
- ✅ Capacity planning
- ✅ Documentation updates
- ✅ Disaster recovery drill

### Quarterly

- ✅ Full backup test (restore to staging)
- ✅ Security audit
- ✅ Architecture review

### Annually

- ✅ Secrets rotation
- ✅ OS updates
- ✅ Dependency updates
- ✅ Capacity upgrade planning

---

## 📖 Related Documentation

- **DEPLOYMENT_HOSTINGER.md** - Initial VPS setup & deployment
- **PRODUCTION_MIGRATIONS.md** - Database schema version control
- **deploy.sh** - Automated deployment script
- **health-check.sh** - Automated health verification
- **rollback.sh** - Emergency rollback script

---

## 📞 Support & Contacts

**Team Communication:**
- Issues: GitHub Issues (linked to deployment status)
- Chat: Team Slack #ops-alerts
- Escalation: Team Lead (on-call rotation)

**External Support:**
- Hostinger: https://www.hostinger.com/support
- PostgreSQL: https://www.postgresql.org/
- Docker: https://docs.docker.com/

---

**Last Updated:** 2025-11-23
**Status:** Production Ready ✅
**Next Review:** 2025-12-23

