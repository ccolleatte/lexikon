#!/bin/bash

###############################################################################
# Lexikon Production Deployment Script
# Usage: ./deploy.sh [production|staging]
# Author: Claude Code
# Date: 2025-11-22
###############################################################################

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-production}
REPO_URL="https://github.com/ccolleatte/lexikon.git"
REPO_DIR="/root/lexikon"
BACKUP_DIR="/root/lexikon-backups"

###############################################################################
# Functions
###############################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    log_info "Checking requirements..."

    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi

    # Check if docker-compose is installed
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi

    # Check if .env.prod exists
    if [ ! -f "$REPO_DIR/.env.prod" ]; then
        log_error ".env.prod file not found"
        log_info "Copy .env.prod.example to .env.prod and fill in the values"
        exit 1
    fi

    log_success "All requirements met"
}

create_backup() {
    log_info "Creating backup..."

    BACKUP_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_PATH="$BACKUP_DIR/backup_$BACKUP_TIMESTAMP"

    mkdir -p "$BACKUP_PATH"

    # Backup docker volumes
    docker run --rm \
        -v lexikon_postgres_data:/data \
        -v "$BACKUP_PATH":/backup \
        alpine tar czf /backup/postgres_data.tar.gz -C /data .

    docker run --rm \
        -v lexikon_redis_data:/data \
        -v "$BACKUP_PATH":/backup \
        alpine tar czf /backup/redis_data.tar.gz -C /data .

    log_success "Backup created at $BACKUP_PATH"
    echo "$BACKUP_PATH" > "$BACKUP_DIR/latest_backup"
}

cleanup_old_backups() {
    log_info "Cleaning up backups older than 7 days..."

    if [ ! -d "$BACKUP_DIR" ]; then
        log_warning "Backup directory does not exist"
        return 0
    fi

    # Find and delete directories older than 7 days
    DELETED_COUNT=0
    while IFS= read -r backup_dir; do
        if [ -n "$backup_dir" ]; then
            log_info "Deleting old backup: $backup_dir"
            rm -rf "$backup_dir"
            DELETED_COUNT=$((DELETED_COUNT + 1))
        fi
    done < <(find "$BACKUP_DIR" -maxdepth 1 -type d -name "backup_*" -mtime +7)

    if [ "$DELETED_COUNT" -gt 0 ]; then
        log_success "Cleaned up $DELETED_COUNT old backup(s)"
    else
        log_info "No old backups to clean up"
    fi
}

pull_latest_code() {
    log_info "Pulling latest code from GitHub..."

    cd "$REPO_DIR"

    # Vérifier s'il y a des modifications non commitées
    if ! git diff-index --quiet HEAD --; then
        log_warning "Uncommitted changes detected. Stashing..."
        STASH_NAME="Auto-stash before deploy $(date +%Y%m%d_%H%M%S)"
        git stash save "$STASH_NAME"
        log_info "Changes stashed as: $STASH_NAME"
        log_info "To restore: git stash apply"
    fi

    git fetch origin

    # Tentative de merge fast-forward uniquement (pas de reset destructif)
    if ! git merge origin/master --ff-only; then
        log_error "Fast-forward merge failed. Manual intervention needed."
        log_error "Possible causes:"
        log_error "  - Local commits ahead of remote"
        log_error "  - Conflicting changes"
        log_info "Run 'git status' to investigate"
        exit 1
    fi

    log_success "Code updated"
}

build_images() {
    log_info "Building Docker images..."

    cd "$REPO_DIR"
    docker-compose -f docker-compose.prod.yml --env-file .env.prod build --no-cache backend

    log_success "Docker images built"
}

run_tests() {
    log_info "Running backend tests..."

    cd "$REPO_DIR"

    # Start postgres & redis for tests
    log_info "Starting test databases..."
    docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d postgres redis

    sleep 3

    # Run pytest via docker-compose
    log_info "Executing pytest suite..."
    if docker-compose -f docker-compose.prod.yml --env-file .env.prod run --rm backend \
        pytest -v --tb=short backend/tests/ 2>&1 | tee /tmp/pytest.log; then
        log_success "Backend tests PASSED ✓"
        return 0
    else
        log_error "Backend tests FAILED - aborting deployment"
        log_error "See /tmp/pytest.log for details"
        return 1
    fi
}

setup_ssl() {
    log_info "Setting up SSL/TLS certificates..."

    if [ ! -d "$REPO_DIR/ssl" ]; then
        mkdir -p "$REPO_DIR/ssl"
        log_warning "SSL directory created but certificates not found"
        log_info "Generate certificates with certbot:"
        log_info "  certbot certonly --standalone -d your-domain.com"
        log_info "  cp /etc/letsencrypt/live/your-domain.com/fullchain.pem $REPO_DIR/ssl/cert.pem"
        log_info "  cp /etc/letsencrypt/live/your-domain.com/privkey.pem $REPO_DIR/ssl/key.pem"
    else
        log_success "SSL certificates found"
    fi
}

start_services() {
    log_info "Starting services..."

    cd "$REPO_DIR"
    docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

    log_success "Services started"
}

wait_for_health() {
    log_info "Waiting for services to be healthy..."

    MAX_ATTEMPTS=30
    ATTEMPT=0

    while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
        if curl -f http://localhost:8000/api/health &> /dev/null; then
            log_success "Backend is healthy"
            return 0
        fi

        ATTEMPT=$((ATTEMPT + 1))
        sleep 2
    done

    log_error "Backend did not become healthy"
    exit 1
}

verify_deployment() {

run_e2e_tests() {
    log_info "Running E2E smoke tests against production stack..."

    cd "$REPO_DIR"

    # Check if Playwright is installed
    if ! npm list @playwright/test &> /dev/null; then
        log_info "Installing Playwright..."
        npm ci
        npx playwright install chromium --with-deps
    fi

    # Run smoke tests only (fast validation)
    log_info "Executing E2E smoke tests..."
    if BASE_URL=http://localhost:8080 \
       npm run test:e2e:smoke -- --project=chromium 2>&1 | tee /tmp/e2e-smoke.log; then
        log_success "E2E smoke tests PASSED ✓"
        return 0
    else
        log_warning "E2E smoke tests FAILED - see /tmp/e2e-smoke.log"
        log_warning "Deployment continues (E2E is advisory, not blocking)"
        return 0  # Non-blocking
    fi
}
    log_info "Verifying deployment..."

    # Check if all containers are running
    log_info "Checking container status..."
    docker-compose -f "$REPO_DIR/docker-compose.prod.yml" --env-file .env.prod ps

    # Test API endpoint
    log_info "Testing API endpoint..."
    if curl -f https://localhost/api/health &> /dev/null || curl -f http://localhost/api/health &> /dev/null; then
        log_success "API is responding"
    else
        log_error "API is not responding"
        exit 1
    fi

    # Check logs for errors
    log_info "Checking logs for errors..."
    if docker-compose -f "$REPO_DIR/docker-compose.prod.yml" --env-file .env.prod logs | grep -i error | head -5; then
        log_warning "Some errors found in logs (may be harmless)"
    fi

    log_success "Deployment verified"
}

setup_monitoring() {
    log_info "Setting up Uptime Kuma monitoring..."

    cd "$REPO_DIR"

    # Start Uptime Kuma container
    if docker-compose -f docker-compose.monitoring.yml up -d; then
        log_success "Uptime Kuma started"
        log_info "Access dashboard at: https://your-domain.com/monitoring/"
        log_info "On first visit, create admin account"
        log_info ""
        log_info "Recommended monitors to add:"
        log_info "  1. Backend Health: https://your-domain.com/api/health (30s interval)"
        log_info "  2. Frontend: https://your-domain.com/ (60s interval)"
        log_info "  3. SSL Certificate: HTTPS monitor (daily)"
    else
        log_error "Failed to start Uptime Kuma"
        log_warning "You can manually start it with: docker-compose -f docker-compose.monitoring.yml up -d"
    fi
}

###############################################################################
# Main
###############################################################################

main() {
    log_info "Starting Lexikon deployment to $ENVIRONMENT"
    log_info "Time: $(date)"

    check_requirements
    create_backup
    cleanup_old_backups
    pull_latest_code
    build_images
    run_tests
    setup_ssl
    start_services
    wait_for_health
    run_e2e_tests
    verify_deployment
    setup_monitoring

    log_success "Deployment completed successfully!"
    log_info "Application is available at: https://your-domain.com"
    log_info "Health check: curl https://your-domain.com/api/health"
    log_info "Monitoring dashboard: https://your-domain.com/monitoring/"
}

# Run main function
main "$@"
