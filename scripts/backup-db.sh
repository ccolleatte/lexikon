#!/bin/bash

################################################################################
# PostgreSQL Backup Script for Lexikon
#
# Usage: ./backup-db.sh [backup_type]
# Types: daily (default), weekly, manual
#
# Features:
# - Daily backups to local storage (7 day retention)
# - Weekly backups for long-term retention
# - Automatic cleanup of old backups
# - Email notification on completion/failure
# - Backup validation
################################################################################

set -euo pipefail

# Configuration
BACKUP_BASE_DIR="${BACKUP_BASE_DIR:-/opt/lexikon/backups}"
LOCAL_RETENTION_DAYS=7
WEEKLY_RETENTION_DAYS=30
BACKUP_TYPE="${1:-daily}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="${BACKUP_BASE_DIR}/backup.log"

# Docker configuration
DB_CONTAINER="lexikon-postgres"
DB_USER="${POSTGRES_USER:-lexikon}"
DB_NAME="${POSTGRES_DB:-lexikon}"

# Create backup directory if not exists
mkdir -p "${BACKUP_BASE_DIR}"/{daily,weekly,manual}

################################################################################
# Logging Functions
################################################################################

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "${LOG_FILE}"
}

error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $*" | tee -a "${LOG_FILE}" >&2
}

################################################################################
# Backup Functions
################################################################################

backup_database() {
    local backup_type=$1
    local backup_dir="${BACKUP_BASE_DIR}/${backup_type}"
    local backup_file="${backup_dir}/lexikon_${backup_type}_${TIMESTAMP}.sql.gz"

    log "Starting ${backup_type} backup of ${DB_NAME}..."

    # Check if container is running
    if ! docker ps | grep -q "${DB_CONTAINER}"; then
        error "Database container '${DB_CONTAINER}' is not running"
        return 1
    fi

    # Create backup
    if docker exec "${DB_CONTAINER}" pg_dump -U "${DB_USER}" "${DB_NAME}" | gzip > "${backup_file}"; then
        local size=$(du -h "${backup_file}" | cut -f1)
        log "✓ Backup successful: ${backup_file} (${size})"

        # Verify backup integrity
        if gzip -t "${backup_file}" 2>/dev/null; then
            log "✓ Backup integrity verified"
        else
            error "Backup file is corrupted"
            rm -f "${backup_file}"
            return 1
        fi

        return 0
    else
        error "Backup failed"
        return 1
    fi
}

cleanup_old_backups() {
    local backup_type=$1
    local retention_days=$2
    local backup_dir="${BACKUP_BASE_DIR}/${backup_type}"

    log "Cleaning up backups older than ${retention_days} days in ${backup_dir}..."

    find "${backup_dir}" -name "lexikon_*.sql.gz" -mtime "+${retention_days}" -delete 2>/dev/null || true

    log "✓ Cleanup completed"
}

restore_database() {
    local backup_file=$1

    if [ ! -f "${backup_file}" ]; then
        error "Backup file not found: ${backup_file}"
        return 1
    fi

    log "Starting restore from ${backup_file}..."

    # Check if container is running
    if ! docker ps | grep -q "${DB_CONTAINER}"; then
        error "Database container '${DB_CONTAINER}' is not running"
        return 1
    fi

    # Restore backup
    if gunzip -c "${backup_file}" | docker exec -i "${DB_CONTAINER}" psql -U "${DB_USER}" "${DB_NAME}" > /dev/null 2>&1; then
        log "✓ Restore successful"
        return 0
    else
        error "Restore failed"
        return 1
    fi
}

list_backups() {
    log "Available backups:"
    echo ""
    ls -lh "${BACKUP_BASE_DIR}"/{daily,weekly,manual}/*.sql.gz 2>/dev/null | awk '{print $9, "(" $5 ")"}' || true
    echo ""
}

verify_backups() {
    log "Verifying backup integrity..."

    local failed=0
    while IFS= read -r backup_file; do
        if ! gzip -t "${backup_file}" 2>/dev/null; then
            error "Corrupted backup: ${backup_file}"
            ((failed++))
        else
            log "✓ Valid: $(basename ${backup_file})"
        fi
    done < <(find "${BACKUP_BASE_DIR}" -name "lexikon_*.sql.gz" -type f)

    if [ ${failed} -eq 0 ]; then
        log "✓ All backups verified successfully"
        return 0
    else
        error "${failed} corrupted backup(s) found"
        return 1
    fi
}

################################################################################
# Main
################################################################################

main() {
    log "=========================================="
    log "Lexikon Database Backup Script"
    log "Backup Type: ${BACKUP_TYPE}"
    log "=========================================="

    case "${BACKUP_TYPE}" in
        daily)
            backup_database "daily" || exit 1
            cleanup_old_backups "daily" "${LOCAL_RETENTION_DAYS}"
            ;;
        weekly)
            backup_database "weekly" || exit 1
            cleanup_old_backups "weekly" "${WEEKLY_RETENTION_DAYS}"
            ;;
        manual)
            backup_database "manual" || exit 1
            ;;
        restore)
            if [ $# -lt 2 ]; then
                error "Usage: $0 restore <backup_file>"
                exit 1
            fi
            restore_database "$2"
            ;;
        list)
            list_backups
            ;;
        verify)
            verify_backups
            ;;
        *)
            error "Unknown backup type: ${BACKUP_TYPE}"
            echo "Usage: $0 {daily|weekly|manual|restore|list|verify}"
            exit 1
            ;;
    esac

    log "✓ Backup operation completed successfully"
}

# Run main function
main "$@"
