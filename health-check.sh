#!/bin/bash

###############################################################################
# Lexikon Health Check Script
# Verifies all services are running and healthy
###############################################################################

set -e

REPO_DIR="/opt/lexikon"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_ok() { echo -e "${GREEN}✓${NC} $1"; }
log_fail() { echo -e "${RED}✗${NC} $1"; }
log_info() { echo -e "${BLUE}ℹ${NC} $1"; }
log_warn() { echo -e "${YELLOW}⚠${NC} $1"; }

check_container() {
    local name=$1
    if docker ps | grep -q "$name"; then
        log_ok "Container $name is running"
        return 0
    else
        log_fail "Container $name is NOT running"
        return 1
    fi
}

check_service_health() {
    local service=$1
    local port=$2
    local path=${3:-/}

    log_info "Checking $service on port $port..."
    if curl -sf "http://localhost:$port$path" > /dev/null 2>&1; then
        log_ok "$service is healthy"
        return 0
    else
        log_fail "$service is NOT healthy"
        return 1
    fi
}

check_db_connectivity() {
    log_info "Checking PostgreSQL connectivity..."
    if docker exec lexikon-postgres pg_isready -U lexikon &> /dev/null; then
        log_ok "PostgreSQL is accessible"
        return 0
    else
        log_fail "PostgreSQL is NOT accessible"
        return 1
    fi
}

check_redis_connectivity() {
    log_info "Checking Redis connectivity..."
    if docker exec lexikon-redis redis-cli ping &> /dev/null; then
        log_ok "Redis is accessible"
        return 0
    else
        log_fail "Redis is NOT accessible"
        return 1
    fi
}

check_neo4j_connectivity() {
    log_info "Checking Neo4j connectivity..."
    if docker exec lexikon-neo4j cypher-shell -u neo4j "RETURN 1" &> /dev/null; then
        log_ok "Neo4j is accessible"
        return 0
    else
        log_fail "Neo4j is NOT accessible"
        return 1
    fi
}

main() {
    echo "═══════════════════════════════════════════════════════════════"
    echo "Lexikon Health Check - $(date)"
    echo "═══════════════════════════════════════════════════════════════"
    echo

    cd "$REPO_DIR"

    FAILED=0

    # Check containers
    echo "Checking containers..."
    check_container "lexikon-postgres" || ((FAILED++))
    check_container "lexikon-neo4j" || ((FAILED++))
    check_container "lexikon-redis" || ((FAILED++))
    check_container "lexikon-backend" || ((FAILED++))
    check_container "lexikon-nginx" || ((FAILED++))
    echo

    # Check service health
    echo "Checking service health..."
    check_db_connectivity || ((FAILED++))
    check_redis_connectivity || ((FAILED++))
    check_neo4j_connectivity || ((FAILED++))
    check_service_health "Backend API" 8000 "/api/health" || ((FAILED++))
    check_service_health "Nginx" 80 "/health" || ((FAILED++))
    echo

    # Check disk space
    echo "Checking disk space..."
    DISK_USAGE=$(df -h "$REPO_DIR" | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$DISK_USAGE" -lt 80 ]; then
        log_ok "Disk usage is $DISK_USAGE% (healthy)"
    elif [ "$DISK_USAGE" -lt 90 ]; then
        log_warn "Disk usage is $DISK_USAGE% (warning)"
    else
        log_fail "Disk usage is $DISK_USAGE% (critical)"
        ((FAILED++))
    fi
    echo

    # Docker status
    echo "Docker Compose status:"
    docker-compose -f docker-compose.prod.yml ps
    echo

    # Summary
    echo "═══════════════════════════════════════════════════════════════"
    if [ $FAILED -eq 0 ]; then
        log_ok "All checks passed!"
        echo "═══════════════════════════════════════════════════════════════"
        exit 0
    else
        log_fail "$FAILED checks failed!"
        echo "═══════════════════════════════════════════════════════════════"
        exit 1
    fi
}

main "$@"
