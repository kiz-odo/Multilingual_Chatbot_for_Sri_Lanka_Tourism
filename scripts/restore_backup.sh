#!/bin/bash
#
# Point-in-Time Recovery (PITR) Script
# Restores MongoDB backup from local or S3
#

set -euo pipefail

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/backups/mongodb}"
MONGODB_HOST="${MONGODB_HOST:-localhost}"
MONGODB_PORT="${MONGODB_PORT:-27017}"
MONGODB_USER="${MONGODB_USER:-admin}"
MONGODB_PASS="${MONGODB_PASS:-}"
DATABASE_NAME="${DATABASE_NAME:-sri_lanka_tourism_bot}"
S3_BUCKET="${S3_BUCKET:-}"
ENCRYPTION_KEY="${ENCRYPTION_KEY:-}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Functions
log() { echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"; }
log_error() { echo -e "${RED}[ERROR] $*${NC}"; }
log_success() { echo -e "${GREEN}[SUCCESS] $*${NC}"; }
log_warning() { echo -e "${YELLOW}[WARNING] $*${NC}"; }

# List available backups
list_backups() {
    log "Available local backups:"
    echo ""
    find "${BACKUP_DIR}" -name "tourism_backup_*.tar.gz*" -type f -exec ls -lh {} \; | \
        awk '{print $9, "(" $5 ")", $6, $7, $8}'
    echo ""
    
    if [ -n "${S3_BUCKET}" ] && command -v aws &> /dev/null; then
        log "Available S3 backups:"
        aws s3 ls "s3://${S3_BUCKET}/mongodb-backups/" --recursive | \
            grep "tourism_backup_"
    fi
}

# Download from S3
download_from_s3() {
    local backup_name="$1"
    
    log "Downloading backup from S3: ${backup_name}"
    
    aws s3 cp "s3://${S3_BUCKET}/mongodb-backups/${backup_name}" \
        "${BACKUP_DIR}/${backup_name}"
    
    if [ $? -eq 0 ]; then
        log_success "Backup downloaded from S3"
        return 0
    else
        log_error "S3 download failed"
        return 1
    fi
}

# Decrypt backup
decrypt_backup() {
    local encrypted_file="$1"
    local decrypted_file="${encrypted_file%.enc}"
    
    log "Decrypting backup..."
    
    openssl enc -aes-256-cbc -d \
        -in "${encrypted_file}" \
        -out "${decrypted_file}" \
        -pass pass:"${ENCRYPTION_KEY}"
    
    if [ $? -eq 0 ]; then
        log_success "Backup decrypted"
        echo "${decrypted_file}"
    else
        log_error "Decryption failed"
        exit 1
    fi
}

# Extract backup
extract_backup() {
    local backup_file="$1"
    local extract_dir="${BACKUP_DIR}/restore_temp"
    
    log "Extracting backup..."
    
    mkdir -p "${extract_dir}"
    tar -xzf "${backup_file}" -C "${extract_dir}"
    
    if [ $? -eq 0 ]; then
        log_success "Backup extracted to ${extract_dir}"
        echo "${extract_dir}"
    else
        log_error "Extraction failed"
        exit 1
    fi
}

# Perform restore
perform_restore() {
    local backup_path="$1"
    local target_db="${2:-${DATABASE_NAME}}"
    
    log "WARNING: This will restore database: ${target_db}"
    log "Current database will be overwritten!"
    
    read -p "Are you sure you want to continue? (yes/no): " confirm
    
    if [ "${confirm}" != "yes" ]; then
        log "Restore cancelled"
        exit 0
    fi
    
    log "Starting MongoDB restore..."
    
    # Build mongorestore command
    MONGORESTORE_CMD="mongorestore"
    MONGORESTORE_CMD+=" --host=${MONGODB_HOST}"
    MONGORESTORE_CMD+=" --port=${MONGODB_PORT}"
    
    if [ -n "${MONGODB_USER}" ]; then
        MONGORESTORE_CMD+=" --username=${MONGODB_USER}"
    fi
    
    if [ -n "${MONGODB_PASS}" ]; then
        MONGORESTORE_CMD+=" --password=${MONGODB_PASS}"
    fi
    
    MONGORESTORE_CMD+=" --db=${target_db}"
    MONGORESTORE_CMD+=" --drop"  # Drop existing collections
    MONGORESTORE_CMD+=" --gzip"
    MONGORESTORE_CMD+=" ${backup_path}/${DATABASE_NAME}"
    
    # Execute restore
    if eval "${MONGORESTORE_CMD}"; then
        log_success "MongoDB restore completed"
        return 0
    else
        log_error "MongoDB restore failed"
        return 1
    fi
}

# Main
main() {
    log "========================================"
    log "MongoDB Point-in-Time Recovery"
    log "========================================"
    
    # Check if backup name provided
    if [ $# -eq 0 ]; then
        list_backups
        echo ""
        read -p "Enter backup name to restore (e.g., tourism_backup_20250127_120000.tar.gz): " backup_name
    else
        backup_name="$1"
    fi
    
    # Check if file exists locally
    backup_file="${BACKUP_DIR}/${backup_name}"
    
    if [ ! -f "${backup_file}" ]; then
        log_warning "Backup not found locally"
        
        if [ -n "${S3_BUCKET}" ]; then
            download_from_s3 "${backup_name}"
        else
            log_error "Backup file not found"
            exit 1
        fi
    fi
    
    # Decrypt if needed
    if [[ "${backup_file}" == *.enc ]]; then
        backup_file=$(decrypt_backup "${backup_file}")
    fi
    
    # Extract backup
    extract_dir=$(extract_backup "${backup_file}")
    
    # Perform restore
    if perform_restore "${extract_dir}"; then
        log_success "Database restored successfully!"
        
        # Cleanup
        rm -rf "${extract_dir}"
        
        exit 0
    else
        log_error "Restore failed"
        exit 1
    fi
}

main "$@"
