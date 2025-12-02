#!/bin/bash

###############################################################################
# Lexikon External Health Check Script
# Monitors application health and sends alerts if down
# Setup cron job: */5 * * * * /opt/lexikon/monitoring/external-health-check.sh
###############################################################################

set -e

# Configuration
DOMAIN=${1:-"your-domain.com"}
SERVICE_NAME="Lexikon API"
HEALTH_ENDPOINT="https://${DOMAIN}/api/health"
TIMEOUT=10
MAX_RETRIES=2
LOG_FILE="/var/log/lexikon-health-check.log"
ALERT_EMAIL="${ALERT_EMAIL:-}"
WEBHOOK_URL="${WEBHOOK_URL:-}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Logging functions
log_info() { echo "[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1" | tee -a "$LOG_FILE"; }
log_success() { echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] SUCCESS: $1${NC}" | tee -a "$LOG_FILE"; }
log_error() { echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" | tee -a "$LOG_FILE"; }
log_warning() { echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}" | tee -a "$LOG_FILE"; }

check_health() {
    """Check if service is healthy by calling health endpoint"""
    log_info "Checking health endpoint: $HEALTH_ENDPOINT"

    # Retry logic
    ATTEMPT=0
    while [ $ATTEMPT -lt $MAX_RETRIES ]; do
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
            --connect-timeout "$TIMEOUT" \
            --max-time "$TIMEOUT" \
            "$HEALTH_ENDPOINT" 2>/dev/null || echo "000")

        if [ "$HTTP_CODE" = "200" ]; then
            log_success "Health check passed (HTTP $HTTP_CODE)"
            return 0
        fi

        ATTEMPT=$((ATTEMPT + 1))
        if [ $ATTEMPT -lt $MAX_RETRIES ]; then
            log_warning "Health check failed (HTTP $HTTP_CODE), retrying... (attempt $ATTEMPT/$MAX_RETRIES)"
            sleep 2
        fi
    done

    log_error "Health check failed after $MAX_RETRIES attempts (HTTP $HTTP_CODE)"
    return 1
}

send_email_alert() {
    """Send email alert if configured"""
    if [ -z "$ALERT_EMAIL" ]; then
        log_warning "No ALERT_EMAIL configured, skipping email alert"
        return
    fi

    local subject="[ALERT] $SERVICE_NAME is DOWN at $(date +'%Y-%m-%d %H:%M:%S')"
    local message="$SERVICE_NAME health check failed.\n\nEndpoint: $HEALTH_ENDPOINT\nTime: $(date)\n\nPlease investigate."

    echo -e "$message" | mail -s "$subject" "$ALERT_EMAIL" 2>/dev/null || log_error "Failed to send email alert"
}

send_webhook_alert() {
    """Send webhook alert if configured"""
    if [ -z "$WEBHOOK_URL" ]; then
        log_warning "No WEBHOOK_URL configured, skipping webhook alert"
        return
    fi

    local payload=$(cat <<EOF
{
  "service": "$SERVICE_NAME",
  "status": "down",
  "endpoint": "$HEALTH_ENDPOINT",
  "timestamp": "$(date -u +'%Y-%m-%dT%H:%M:%SZ')",
  "message": "$SERVICE_NAME health check failed"
}
EOF
)

    curl -s -X POST "$WEBHOOK_URL" \
        -H "Content-Type: application/json" \
        -d "$payload" 2>/dev/null || log_error "Failed to send webhook alert"
}

send_alerts() {
    """Send all configured alerts"""
    log_warning "Service is DOWN, sending alerts..."
    send_email_alert
    send_webhook_alert
}

main() {
    log_info "Starting health check for $SERVICE_NAME"
    log_info "Domain: $DOMAIN"

    if check_health; then
        exit 0
    else
        send_alerts
        exit 1
    fi
}

main "$@"
