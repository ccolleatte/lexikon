# External Monitoring Setup - HIGH Priority

**Date:** 2025-11-23
**Issue:** HIGH-005 - External monitoring/alerting

## Quick Start (UptimeRobot - Recommended)

UptimeRobot is the simplest option for personal projects - free tier monitors every 5 minutes with email alerts.

### Step 1: Create UptimeRobot Monitor

1. Go to https://uptimerobot.com (free account)
2. Create new monitor:
   - **Monitor Type:** HTTP(s)
   - **URL:** `https://your-domain.com/api/health`
   - **Check Interval:** 5 minutes
   - **Timeout:** 10 seconds

### Step 2: Configure Alerts

Add notification channel:
- **Email:** Your email address
- **Slack:** (optional) Your Slack webhook

UptimeRobot will notify you within 5 minutes of downtime.

---

## Option 2: Self-Hosted Script

Use our provided script for more control:

### Setup

```bash
# On VPS
chmod +x /opt/lexikon/monitoring/external-health-check.sh

# Add cron job (check every 5 minutes)
sudo crontab -e

# Add this line:
*/5 * * * * /opt/lexikon/monitoring/external-health-check.sh your-domain.com >> /var/log/lexikon-health-check.log 2>&1
```

### Configure Alerts

```bash
# Email alerts
export ALERT_EMAIL="your-email@example.com"

# Or webhook (for Slack, Discord, etc.)
export WEBHOOK_URL="https://hooks.slack.com/services/..."

# Then test
/opt/lexikon/monitoring/external-health-check.sh your-domain.com
```

### Script Features

- Automatic retries (2 attempts, 2sec delay)
- Email alerts via `mail` command
- Webhook support (Slack, Discord, custom)
- Logging to `/var/log/lexikon-health-check.log`
- HTTP timeout: 10 seconds

---

## Option 3: Datadog (Premium)

For advanced monitoring with metrics, logs, and APM:

```bash
# Install Datadog agent
bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_agent.sh)" -- \
  --api-key $DATADOG_API_KEY --site datadoghq.com

# Configure uptime check in Datadog UI
```

---

## Verification

Test health endpoint manually:

```bash
# Should return {"status": "ok"} with HTTP 200
curl -v https://your-domain.com/api/health
```

---

## Next Steps

1. **Immediate:** Set up UptimeRobot (5 min)
2. **24h:** Test downtime alerting by stopping service
3. **Week 1:** Add Slack integration if desired
4. **Week 2:** Consider Datadog for deeper observability

---

## Monitoring Checklist

- [ ] UptimeRobot monitor created and configured
- [ ] Alert email working (test by checking website status)
- [ ] Health endpoint returns 200 OK
- [ ] External health check logs visible in `/var/log/`
- [ ] Slack webhook configured (optional)
- [ ] Downtime alert tested

**Completion Time:** 5-10 minutes (UptimeRobot) to 30 minutes (full setup)
