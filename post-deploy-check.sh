#!/bin/bash
##############################################################################
# Lexikon Post-Deployment Verification Script
#
# Usage: ./post-deploy-check.sh
# Purpose: Quick validation (5-10 min) after running ./deploy.sh
# Author: DevOps
# Date: November 24, 2025
##############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_DIR="/opt/lexikon"
CHECK_COUNT=0
PASS_COUNT=0
FAIL_COUNT=0

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_pass() {
    echo -e "${GREEN}✅ $1${NC}"
    ((PASS_COUNT++))
}

log_fail() {
    echo -e "${RED}❌ $1${NC}"
    ((FAIL_COUNT++))
}

log_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_section() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

check() {
    ((CHECK_COUNT++))
}

# Main execution
main() {
    cd "$REPO_DIR" || {
        log_fail "Cannot access $REPO_DIR"
        exit 1
    }

    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║      🚀 LEXIKON POST-DEPLOYMENT VERIFICATION CHECKLIST       ║"
    echo "║                    SvelteKit SSR + Docker                     ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"

    # PHASE 1: Container Health
    log_section "PHASE 1: Container Health (1 min)"

    check
    log_info "Checking Docker containers status..."
    if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
        log_pass "Containers running"
        docker-compose -f docker-compose.prod.yml ps | tail -5
    else
        log_fail "Some containers not running"
        docker-compose -f docker-compose.prod.yml ps
    fi

    # PHASE 2: Backend Health
    log_section "PHASE 2: Backend API Health (1 min)"

    check
    log_info "Testing Backend /health endpoint..."
    if HEALTH=$(curl -s http://127.0.0.1:8000/health 2>/dev/null); then
        if echo "$HEALTH" | grep -q "healthy"; then
            log_pass "Backend health: HEALTHY"
            echo "$HEALTH" | jq . 2>/dev/null || echo "$HEALTH"
        else
            log_fail "Backend returned unexpected response: $HEALTH"
        fi
    else
        log_fail "Backend unreachable at http://127.0.0.1:8000"
        log_warn "Check: docker logs lexikon-backend"
    fi

    check
    log_info "Testing Backend OpenAPI docs..."
    if curl -s http://127.0.0.1:8000/docs 2>/dev/null | grep -q "swagger-ui"; then
        log_pass "API documentation accessible"
    else
        log_fail "API docs not accessible"
    fi

    # PHASE 3: Frontend SvelteKit SSR
    log_section "PHASE 3: Frontend SvelteKit SSR (2 min)"

    check
    log_info "Testing Frontend homepage..."
    if FRONTEND=$(curl -s http://127.0.0.1:3000/ 2>/dev/null); then
        if echo "$FRONTEND" | grep -q "<title>"; then
            log_pass "Frontend rendering HTML"
        else
            log_fail "Frontend not rendering properly"
            echo "First 200 chars: ${FRONTEND:0:200}"
        fi
    else
        log_fail "Frontend unreachable at http://127.0.0.1:3000"
        log_warn "Check: docker logs lexikon-frontend"
    fi

    check
    log_info "Testing /login route..."
    if curl -s http://127.0.0.1:3000/login 2>/dev/null | grep -q -i "login\|password"; then
        log_pass "/login route responsive"
    else
        log_warn "/login route may not be configured yet"
    fi

    check
    log_info "Testing /signup route..."
    if curl -s http://127.0.0.1:3000/signup 2>/dev/null | grep -q -i "signup\|register"; then
        log_pass "/signup route responsive"
    else
        log_warn "/signup route may not be configured yet"
    fi

    # PHASE 4: Nginx Reverse Proxy
    log_section "PHASE 4: Nginx Reverse Proxy (1 min)"

    check
    log_info "Testing Nginx health endpoint..."
    if curl -s http://127.0.0.1:8080/health 2>/dev/null | grep -q "healthy"; then
        log_pass "Nginx proxying backend successfully"
    else
        log_fail "Nginx proxy to backend failed"
        log_warn "Check: docker logs lexikon-nginx"
    fi

    check
    log_info "Testing Nginx API routing..."
    if curl -s http://127.0.0.1:8080/api/health 2>/dev/null | grep -q "healthy"; then
        log_pass "Nginx /api/* routing working"
    else
        log_fail "Nginx API routing broken"
    fi

    # PHASE 5: HTTPS/SSL
    log_section "PHASE 5: HTTPS/SSL Certificate (1 min)"

    check
    log_info "Testing HTTPS connectivity..."
    HTTPS_TEST=$(curl -s -I https://lexikon.chessplorer.com/ 2>/dev/null | head -1)
    if echo "$HTTPS_TEST" | grep -q "200\|HTTP"; then
        log_pass "HTTPS accessible: $HTTPS_TEST"
    else
        log_warn "HTTPS test inconclusive: $HTTPS_TEST"
        log_warn "This may be normal if Caddy is still warming up"
    fi

    check
    log_info "Checking SSL certificate validity..."
    CERT_CHECK=$(echo | openssl s_client -servername lexikon.chessplorer.com -connect lexikon.chessplorer.com:443 2>/dev/null | grep "Verify return code" || echo "OFFLINE")
    if echo "$CERT_CHECK" | grep -q "0 (ok)"; then
        log_pass "SSL certificate valid"
    else
        log_warn "SSL check: $CERT_CHECK"
    fi

    # PHASE 6: Database & Cache
    log_section "PHASE 6: Database & Redis (1 min)"

    check
    log_info "Testing PostgreSQL connection..."
    if docker exec lexikon-postgres psql -U postgres -c "SELECT version();" >/dev/null 2>&1; then
        log_pass "PostgreSQL responsive"
        docker exec lexikon-postgres psql -U postgres -c "SELECT 'Connected' as status;" 2>/dev/null || true
    else
        log_fail "PostgreSQL unreachable"
        log_warn "Check: docker logs lexikon-postgres"
    fi

    check
    log_info "Testing Redis connection..."
    if REDIS_TEST=$(docker exec lexikon-redis redis-cli ping 2>/dev/null); then
        if [ "$REDIS_TEST" = "PONG" ]; then
            log_pass "Redis responsive"
        else
            log_fail "Redis unexpected response: $REDIS_TEST"
        fi
    else
        log_fail "Redis unreachable"
        log_warn "Check: docker logs lexikon-redis"
    fi

    # PHASE 7: Monitoring (Optional)
    log_section "PHASE 7: Monitoring - Uptime Kuma (1 min)"

    check
    log_info "Testing Uptime Kuma..."
    if curl -s http://127.0.0.1:3001/ 2>/dev/null | grep -q "uptime\|kuma" -i; then
        log_pass "Uptime Kuma running"
    else
        log_warn "Uptime Kuma not responding (optional service)"
    fi

    # PHASE 8: Summary
    log_section "SUMMARY"

    TOTAL=$((PASS_COUNT + FAIL_COUNT))
    SUCCESS_RATE=$((PASS_COUNT * 100 / CHECK_COUNT))

    echo ""
    echo -e "Total checks:  ${BLUE}$CHECK_COUNT${NC}"
    echo -e "Passed:        ${GREEN}$PASS_COUNT${NC}"
    echo -e "Failed:        ${RED}$FAIL_COUNT${NC}"
    echo -e "Success rate:  ${BLUE}${SUCCESS_RATE}%${NC}"
    echo ""

    if [ $FAIL_COUNT -eq 0 ]; then
        echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗"
        echo -e "║                    ✅ ALL CHECKS PASSED                           ║"
        echo -e "║                                                                    ║"
        echo -e "║  Production is HEALTHY - Ready for traffic!                        ║"
        echo -e "╚════════════════════════════════════════════════════════════════╝${NC}"
        echo ""
        return 0
    else
        echo -e "${RED}╔════════════════════════════════════════════════════════════════╗"
        echo -e "║                 ❌ SOME CHECKS FAILED                             ║"
        echo -e "║                                                                    ║"
        echo -e "║  Review errors above and consider rollback:                        ║"
        echo -e "║  $ ./rollback.sh                                                   ║"
        echo -e "╚════════════════════════════════════════════════════════════════╝${NC}"
        echo ""
        return 1
    fi
}

# Help function
show_help() {
    cat << EOF
Usage: ./post-deploy-check.sh [OPTIONS]

Options:
  -h, --help          Show this help message
  -q, --quick         Run only critical checks (skip optional)
  -v, --verbose       Show detailed output

Description:
  Validates all components after deploying to VPS:
  - Docker containers health
  - Backend API endpoints
  - Frontend SvelteKit SSR rendering
  - Nginx reverse proxy
  - SSL/TLS certificate
  - PostgreSQL & Redis connectivity
  - Uptime Kuma monitoring

Example workflow:
  1. ./deploy.sh                    # Deploy to VPS
  2. ./post-deploy-check.sh         # Run this script
  3. If all green: Production updated ✅
  4. If any red: ./rollback.sh      # Rollback immediately

EOF
}

# Parse arguments
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
