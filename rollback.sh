#!/bin/bash

###############################################################################
# Lexikon Rollback Script
# Rolls back to a previous backup in case of deployment failure
###############################################################################

set -e

REPO_DIR="/opt/lexikon"
BACKUP_DIR="/opt/lexikon-backups"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

list_backups() {
    log_info "Available backups:"
    ls -lrt "$BACKUP_DIR" | grep "^d" | awk '{print $NF}'
}

main() {
    log_warning "ROLLBACK IN PROGRESS - This will revert to a previous state"
    echo

    # Check if backup directory exists
    if [ ! -d "$BACKUP_DIR" ]; then
        log_error "No backups found"
        exit 1
    fi

    # Get latest backup
    LATEST_BACKUP=""
    if [ -f "$BACKUP_DIR/latest_backup" ]; then
        LATEST_BACKUP=$(cat "$BACKUP_DIR/latest_backup")
    fi

    if [ -z "$LATEST_BACKUP" ]; then
        log_error "No latest backup found"
        list_backups
        exit 1
    fi

    if [ ! -d "$LATEST_BACKUP" ]; then
        log_error "Latest backup directory does not exist: $LATEST_BACKUP"
        exit 1
    fi

    log_info "Using backup: $LATEST_BACKUP"
    echo

    # Ask for confirmation
    read -p "Are you sure you want to rollback? (yes/no): " -r CONFIRM
    if [ "$CONFIRM" != "yes" ]; then
        log_warning "Rollback cancelled"
        exit 0
    fi

    echo

    # Stop services
    log_info "Stopping services..."
    cd "$REPO_DIR"
    docker-compose -f docker-compose.prod.yml --env-file .env.prod down
    log_success "Services stopped"
    echo

    # Restore volumes
    log_info "Restoring database from backup..."
    docker volume rm lexikon_postgres_data 2>/dev/null || true
    docker volume create lexikon_postgres_data

    docker run --rm \
        -v lexikon_postgres_data:/data \
        -v "$LATEST_BACKUP":/backup \
        alpine tar xzf /backup/postgres_data.tar.gz -C /data

    log_success "PostgreSQL restored"
    echo

    log_info "Restoring Redis from backup..."
    docker volume rm lexikon_redis_data 2>/dev/null || true
    docker volume create lexikon_redis_data

    docker run --rm \
        -v lexikon_redis_data:/data \
        -v "$LATEST_BACKUP":/backup \
        alpine tar xzf /backup/redis_data.tar.gz -C /data

    log_success "Redis restored"
    echo

    # Git rollback
    log_info "Rolling back git to previous state..."
    cd "$REPO_DIR"
    git log --oneline -1
    git reset --hard HEAD~1
    log_success "Git rolled back"
    echo

    # Start services
    log_info "Starting services..."
    docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
    sleep 10

    # Wait for health
    log_info "Waiting for services to be healthy..."
    MAX_ATTEMPTS=30
    ATTEMPT=0

    while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
        if curl -f http://localhost:8000/api/health &> /dev/null; then
            log_success "Services are healthy"
            break
        fi
        ATTEMPT=$((ATTEMPT + 1))
        sleep 2
    done

    echo
    log_success "Rollback completed successfully!"
    log_info "Services are running on the previous version"
}

main "$@"
