# 📊 Uptime Kuma - Production Monitoring Setup

**Status:** Deployed & Ready for Configuration
**Version:** 1.0
**Last Updated:** 2025-11-27
**Responsible Team:** DevOps, Infrastructure

---

## Overview

**Uptime Kuma** is a self-hosted monitoring and status page solution running in your Docker infrastructure.

- **Deployment:** Docker container at `https://lexikon.chessplorer.com/monitoring/`
- **Access:** Web UI on port 3001 (proxied via Nginx)
- **Database:** SQLite (persistent volume)
- **Configuration:** Manual via Web UI (no code/API required)

### What We Monitor

| Monitor | Target | Type | Critical |
|---------|--------|------|----------|
| Backend Health | FastAPI `/health` endpoint | HTTP | ✅ Yes |
| Frontend Homepage | SvelteKit SSR landing page | HTTP | ✅ Yes |
| PostgreSQL Database | Docker health check | TCP/Container | ✅ Yes |
| Backend Container | Docker health status | Container | ✅ Yes |
| Frontend Container | Docker health status | Container | ✅ Yes |
| SSL Certificate | Hostinger VPS certificate | Certificate | ⚠️ Warning |
| Disk Space | VPS `/` partition usage | Script/SSH | ⚠️ Warning |

**Total:** 7 monitors, ~2 hours setup time

---

## Initial Setup (First Time)

### Step 1: Access Uptime Kuma

1. **Open browser:** `https://lexikon.chessplorer.com/monitoring/`
2. **Expected:** Uptime Kuma welcome page
3. **If redirected to setup:** Continue to Step 2 (first time)
4. **If login screen:** Use admin credentials (already created)

### Step 2: Create Admin Account (First Time Only)

If this is your first access, create admin account:

1. **Username:** `admin` (or your preferred username)
2. **Password:** Use strong password (≥16 chars, mix of upper/lower/numbers/symbols)
   - ⚠️ **Save this password securely** (password manager)
   - ❌ Do NOT use VPS admin password
   - ❌ Do NOT commit to git

3. **Click:** "Create Admin"
4. **Wait:** Kuma initializes database (5-10 seconds)
5. **Result:** Dashboard appears with 0 monitors

### Step 3: Log In (If Already Set Up)

1. **Open:** `https://lexikon.chessplorer.com/monitoring/`
2. **Username:** admin
3. **Password:** [your secure password from Step 2]
4. **Click:** Login
5. **Dashboard:** Shows all configured monitors

---

## Configuring Monitors (Manual UI)

### Monitor #1: Backend API Health

**Purpose:** Ensure FastAPI is responding to requests

**Configuration:**

1. **Click:** "+ Add Monitor" button
2. **Monitor Type:** HTTP(s)
3. **Name:** `Backend Health`
4. **URL:** `http://backend:8000/health`
   - ℹ️ Internal Docker hostname (resolved via Nginx)
   - For external testing: `http://lexikon.chessplorer.com/api/health`
5. **Method:** GET
6. **Expected Status Code:** 200
7. **Interval:** 60 seconds (check every minute)
8. **Timeout:** 10 seconds
9. **Retries:** 1 (retry once before alerting)
10. **Tags:** `api`, `backend`, `critical`
11. **Click:** Save
12. **Result:** Shows "UP" in green (or "DOWN" if backend not running)

**Manual Test:**
```bash
curl -i http://backend:8000/health
# Expected: 200 OK with response body
```

---

### Monitor #2: Frontend Homepage

**Purpose:** Ensure SvelteKit SSR is rendering pages

**Configuration:**

1. **Click:** "+ Add Monitor" button
2. **Monitor Type:** HTTP(s)
3. **Name:** `Frontend Homepage`
4. **URL:** `http://frontend:3000`
   - ℹ️ Internal Docker hostname
   - External: `https://lexikon.chessplorer.com`
5. **Method:** GET
6. **Expected Status Code:** 200
7. **Interval:** 60 seconds
8. **Timeout:** 10 seconds
9. **Retries:** 1
10. **Tags:** `frontend`, `sveltekit`, `critical`
11. **Advanced Options:**
    - ✅ **Check Keyword:** Add text to search response
    - Keyword: `Lexikon` (or other text from homepage)
    - This ensures not just 200 OK, but correct content rendering
12. **Click:** Save
13. **Result:** Shows "UP" if SvelteKit renders successfully

**Manual Test:**
```bash
curl -s http://frontend:3000 | grep -i "lexikon"
# Should find the keyword in HTML
```

---

### Monitor #3: PostgreSQL Database Container

**Purpose:** Ensure database container is healthy and accessible

**Configuration:**

1. **Click:** "+ Add Monitor" button
2. **Monitor Type:** TCP
3. **Name:** `PostgreSQL Container`
4. **Hostname:** `postgres` (Docker service name)
5. **Port:** 5432 (PostgreSQL default)
6. **Interval:** 60 seconds
7. **Timeout:** 10 seconds
8. **Retries:** 2
9. **Tags:** `database`, `postgres`, `critical`
10. **Click:** Save
11. **Result:** "UP" if port 5432 is accessible

**Why TCP?** Checks if the container is running and listening, without needing authentication.

**Manual Test (from Docker host):**
```bash
docker exec -it postgres pg_isready -h localhost
# Expected: accepting connections
```

---

### Monitor #4: Backend Container Health

**Purpose:** Monitor Docker health status of FastAPI backend

**Configuration:**

1. **Click:** "+ Add Monitor" button
2. **Monitor Type:** Docker
3. **Name:** `Backend Container`
4. **Docker Host:** `unix:///var/run/docker.sock`
   - ℹ️ Uptime Kuma container has volume mount for this
5. **Container ID/Name:** `lexikon-backend` (or full container ID)
   - Run: `docker ps --filter "name=backend"` to find exact name
6. **Expected Status:** `running`
7. **Interval:** 60 seconds
8. **Tags:** `backend`, `container`, `critical`
9. **Click:** Save
10. **Result:** Shows health status (running, exited, etc.)

**Note:** Requires Docker socket access - Uptime Kuma container must have volume mount to `/var/run/docker.sock`

**Verify Volume Mounted:**
```bash
docker inspect lexikon-uptime-kuma | grep -A 5 "Mounts"
# Should show: /var/run/docker.sock
```

---

### Monitor #5: Frontend Container Health

**Purpose:** Monitor Docker health of SvelteKit frontend

**Configuration:**

1. **Click:** "+ Add Monitor" button
2. **Monitor Type:** Docker
3. **Name:** `Frontend Container`
4. **Docker Host:** `unix:///var/run/docker.sock`
5. **Container ID/Name:** `lexikon-frontend`
   - Run: `docker ps --filter "name=frontend"` to find exact name
6. **Expected Status:** `running`
7. **Interval:** 60 seconds
8. **Tags:** `frontend`, `container`, `critical`
9. **Click:** Save

---

### Monitor #6: SSL Certificate Expiration

**Purpose:** Alert before SSL certificate expires

**Configuration:**

1. **Click:** "+ Add Monitor" button
2. **Monitor Type:** HTTP(s)
3. **Name:** `SSL Certificate`
4. **URL:** `https://lexikon.chessplorer.com`
5. **Method:** GET
6. **Interval:** Daily (86400 seconds)
   - ℹ️ Certificate checks less frequently (slow operation)
7. **Timeout:** 30 seconds (long timeout for certificate validation)
8. **Tags:** `ssl`, `certificate`, `warning`
9. **Advanced Options:**
    - ✅ **Check Certificate Expiration**
    - Days to warn before expiration: `14` (alert 2 weeks before)
10. **Click:** Save
11. **Result:** Shows "UP" if valid, "CERT_EXPIRING" if < 14 days

**Important:** Caddy auto-renews certificates, but this monitor warns you if renewal fails.

**Manual Check:**
```bash
openssl s_client -connect lexikon.chessplorer.com:443 -showcerts < /dev/null | grep -A1 "Not After"
# Shows expiration date
```

---

### Monitor #7: Disk Space Usage

**Purpose:** Alert if VPS runs out of disk space

**Configuration (Simple HTTP-based):**

This uses a simple health check endpoint created on the VPS.

1. **First:** Create health check script on VPS (one-time setup):

```bash
# SSH to VPS
ssh user@lexikon.chessplorer.com

# Create monitoring directory
mkdir -p /opt/monitoring

# Create disk space check script
cat > /opt/monitoring/diskspace.sh << 'SCRIPT'
#!/bin/bash
# Check disk usage on root partition

USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')

if [ "$USAGE" -gt 90 ]; then
    echo "CRITICAL"
    exit 1
elif [ "$USAGE" -gt 80 ]; then
    echo "WARNING"
    exit 2
else
    echo "OK - ${USAGE}% used"
    exit 0
fi
SCRIPT

chmod +x /opt/monitoring/diskspace.sh

# Test it
/opt/monitoring/diskspace.sh
```

2. **In Uptime Kuma UI:**
   - **Monitor Type:** HTTP(s)
   - **Name:** `Disk Space`
   - **URL:** `https://lexikon.chessplorer.com/api/health`
     - ℹ️ For now, use generic health endpoint
     - Later: implement custom /api/metrics endpoint if needed
   - **Interval:** 3600 seconds (check hourly)
   - **Tags:** `infrastructure`, `disk`, `warning`
   - **Click:** Save

**Alternative (Advanced):** Set up Prometheus metrics endpoint for detailed disk monitoring - see Advanced section below.

---

## Notifications Setup

### Email Notifications

1. **Settings:** Click gear icon (⚙️) top right
2. **Notifications:** Select "Notifications"
3. **Add Notification:**
   - **Type:** Email
   - **SMTP Server:** Your email provider (e.g., Gmail)
   - **SMTP Port:** 587 or 465
   - **Sender Email:** monitoring@lexikon.chessplorer.com (or your email)
   - **Password:** Use app-specific password (if 2FA enabled)
   - **Recipients:** Your email address
   - **Test:** Click "Test" to verify
4. **Save**

**Example Gmail Setup:**
- **SMTP Server:** smtp.gmail.com
- **Port:** 587 (TLS)
- **Email:** your-google-account@gmail.com
- **Password:** [Generate App Password in Google Account → Security](https://myaccount.google.com/apppasswords)

### Alert Rules

1. **For each Monitor:**
   - Click monitor → **Edit**
   - **Notification:** Select Email
   - **Down (Alert):** ✅ Enabled
   - **Up (Recovery):** ✅ Enabled
   - **Save**

2. **Alert Conditions:**
   - **Down:** 2+ consecutive failed checks (2 minutes)
   - **Up:** 1 successful check

---

## Dashboard & Status Page

### Main Dashboard

1. **View Monitors:** All monitors show at-a-glance status
   - 🟢 UP = green, normal
   - 🔴 DOWN = red, alert
   - 🟡 PENDING = checking
   - ⚪ PAUSED = disabled

2. **Statistics:**
   - Uptime % (last 7 days, 30 days)
   - Response times
   - Downtime incidents
   - Last check time

### Public Status Page

1. **Settings** → **Status Page**
2. **Create Public Status Page:**
   - **Domain:** status.lexikon.chessplorer.com (optional)
   - **Description:** "Lexikon Platform Status"
   - **Add Monitors:** Select which monitors to display
   - **Theme:** Choose color scheme
   - **Enable:** Publish

3. **Share URL:** `https://lexikon.chessplorer.com/monitoring/status/[page-id]`

---

## Maintenance & Operations

### Daily Operations

**Every Morning:**
1. Check Uptime Kuma dashboard: `https://lexikon.chessplorer.com/monitoring/`
2. Review any alerts (red status = investigate)
3. Check email notifications
4. If DOWN: Check service logs and restart if needed

### Backup & Recovery

**Backup Database:**

Uptime Kuma uses SQLite database stored in Docker volume:

```bash
# Backup
docker cp lexikon-uptime-kuma:/app/data/kuma.db ./kuma.db.backup

# Restore (if needed)
docker cp ./kuma.db.backup lexikon-uptime-kuma:/app/data/kuma.db
docker restart lexikon-uptime-kuma
```

**Schedule Automated Backups:**

```bash
# On VPS, create cron job
0 2 * * * docker cp lexikon-uptime-kuma:/app/data/kuma.db /backups/kuma.db.$(date +\%Y\%m\%d).bak
```

---

## Troubleshooting

### Monitor Shows "DOWN" But Service is Running

**Checklist:**

1. **Verify service is actually running:**
   ```bash
   docker ps | grep backend
   docker logs lexikon-backend  # Check for errors
   ```

2. **Verify port accessibility (from Uptime Kuma container):**
   ```bash
   docker exec lexikon-uptime-kuma curl -v http://backend:8000/health
   # Should get 200 response
   ```

3. **Check Uptime Kuma logs:**
   ```bash
   docker logs lexikon-uptime-kuma | tail -20
   # Look for connection errors
   ```

4. **Network issues:**
   - Ensure both containers are on same Docker network: `lexikon-network`
   - Check: `docker network inspect lexikon-network`

### Email Notifications Not Sending

**Debug SMTP:**

1. Test SMTP credentials manually:
   ```bash
   docker exec lexikon-uptime-kuma telnet smtp.gmail.com 587
   # Should connect
   ```

2. Check Kuma logs:
   ```bash
   docker logs lexikon-uptime-kuma | grep -i "mail\|smtp"
   ```

3. Verify credentials:
   - Gmail: Use 16-character app password (not account password)
   - Other providers: Check SMTP settings

### High CPU/Memory Usage

**Uptime Kuma consuming resources?**

1. **Reduce check frequency:**
   - Click each monitor
   - Increase interval (e.g., 120 sec instead of 60)
   - Especially for "warning" level monitors

2. **Reduce retention:**
   - Settings → Data Retention
   - Purge old data (> 30 days)

3. **Restart container:**
   ```bash
   docker restart lexikon-uptime-kuma
   ```

---

## Advanced Configuration

### Prometheus Integration

For detailed metrics (response times, uptime %, SLA):

1. **Install Prometheus** (separate container)
2. **Uptime Kuma Settings** → Prometheus
3. **Expose metrics at:** `http://uptime-kuma:3001/metrics`
4. **Scrape in Prometheus config:**
   ```yaml
   scrape_configs:
     - job_name: 'uptime-kuma'
       static_configs:
         - targets: ['uptime-kuma:3001']
   ```

### Custom Health Check Endpoint

If you need custom metrics beyond HTTP/TCP:

1. **Backend API endpoint** (in FastAPI):
   ```python
   @app.get("/api/metrics/health")
   async def health_metrics():
       return {
           "status": "healthy",
           "db_connected": True,
           "cache_hit_rate": 0.92,
           "uptime_seconds": 86400,
       }
   ```

2. **Monitor this endpoint:**
   - Monitor Type: HTTP(s)
   - URL: `http://backend:8000/api/metrics/health`
   - Method: GET
   - Check Keyword: "healthy"

### Database Monitoring

If you want to monitor database performance:

1. **Connect directly to PostgreSQL** (if exposed):
   - Monitor Type: PostgreSQL
   - Host: postgres (Docker hostname)
   - Port: 5432
   - Database: lexikon
   - Credentials: from docker-compose.prod.yml
   - Query: SELECT 1 (simple health check)

---

## Escalation & Incidents

### Critical Alert Response

**If Backend DOWN:**
1. Check error: `docker logs lexikon-backend | tail -50`
2. Restart: `docker restart lexikon-backend`
3. Verify: Wait 60 seconds, check if monitor returns UP
4. Investigate root cause if repeated downtime

**If Frontend DOWN:**
1. Check: `docker logs lexikon-frontend | tail -50`
2. Restart: `docker restart lexikon-frontend`
3. Verify: Check monitor after 60 seconds

**If Database DOWN:**
1. Check: `docker logs lexikon-postgres`
2. If data corruption: Contact DevOps team
3. Last resort: Restore from backup

### Incident Documentation

When incident occurs:

1. **Note time, severity, duration**
2. **Document root cause**
3. **Update status page** (if public)
4. **Send email to stakeholders** (if critical)

---

## Performance Expectations

| Monitor | Expected Response Time | Check Interval |
|---------|------------------------|--------------​--|
| HTTP checks | < 500ms | 60 sec |
| TCP checks | < 100ms | 60 sec |
| Container checks | < 1000ms | 60 sec |
| SSL certificate | < 2000ms | Daily |
| Overall dashboard load | < 1 sec | Realtime |

---

## Security Notes

⚠️ **Important:**
- ✅ Access Uptime Kuma only via HTTPS (`https://lexikon.chessplorer.com/monitoring/`)
- ✅ Use strong admin password (≥16 characters)
- ✅ Limit access: Add HTTP auth in Nginx if needed
- ✅ Store credentials securely (password manager, not notes)
- ❌ Never expose metrics endpoint publicly (only internal IPs)
- ❌ Never commit Uptime Kuma credentials to git

**Optional: Restrict Nginx Access**

```nginx
location /monitoring/ {
    auth_basic "Restricted Access";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://uptime-kuma:3001/;
}
```

---

## Related Documentation

- **Docker Compose Setup:** `docker-compose.prod.yml`
- **Nginx Reverse Proxy:** `nginx.conf`
- **Deployment Guide:** `DEPLOYMENT_HOSTINGER.md`
- **Infrastructure as Code:** `_docs/infrastructure/`
- **Alerting Strategy:** This document

---

## Support & Resources

- **Uptime Kuma Docs:** https://uptime.kuma.pet/
- **GitHub Issues:** https://github.com/louislam/uptime-kuma/issues
- **Community Discord:** https://discord.gg/Ug9bQVJmn6

---

**Document Version:** 1.0
**Last Updated:** 2025-11-27
**Maintainers:** DevOps Team, Infrastructure Team
**Estimated Setup Time:** 2 hours (first-time configuration of 7 monitors)
