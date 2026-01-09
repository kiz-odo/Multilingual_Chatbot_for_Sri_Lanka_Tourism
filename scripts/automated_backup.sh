#!/bin/bash
#
# Automated Backup and Disaster Recovery System
# Production-ready MongoDB backup with retention and monitoring
#

set -euo pipefail

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/backups/mongodb}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
MONGODB_HOST="${MONGODB_HOST:-localhost}"
MONGODB_PORT="${MONGODB_PORT:-27017}"
MONGODB_USER="${MONGODB_USER:-admin}"
MONGODB_PASS="${MONGODB_PASS:-}"
DATABASE_NAME="${DATABASE_NAME:-sri_lanka_tourism_bot}"
S3_BUCKET="${S3_BUCKET:-}"
SLACK_WEBHOOK="${SLACK_WEBHOOK:-}"
ENABLE_COMPRESSION="${ENABLE_COMPRESSION:-true}"
ENABLE_ENCRYPTION="${ENABLE_ENCRYPTION:-false}"
ENCRYPTION_KEY="${ENCRYPTION_KEY:-}"

# Logging
LOG_FILE="${BACKUP_DIR}/backup.log"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="tourism_backup_${DATE}"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "${LOG_FILE}"
}

log_error() {
    echo -e "${RED}[ERROR] $*${NC}" | tee -a "${LOG_FILE}"
}

log_success() {
    echo -e "${GREEN}[SUCCESS] $*${NC}" | tee -a "${LOG_FILE}"
}

log_warning() {
    echo -e "${YELLOW}[WARNING] $*${NC}" | tee -a "${LOG_FILE}"
}

# Send notification to Slack
notify_slack() {
    local message="$1"
    local status="${2:-info}"
    
    if [ -n "${SLACK_WEBHOOK}" ]; then
        local color="good"
        [ "${status}" = "error" ] && color="danger"
        [ "${status}" = "warning" ] && color="warning"
        
        curl -X POST "${SLACK_WEBHOOK}" \
            -H 'Content-Type: application/json' \
            -d "{
                \"attachments\": [{
                    \"color\": \"${color}\",
                    \"title\": \"MongoDB Backup Notification\",
                    \"text\": \"${message}\",
                    \"footer\": \"Tourism Chatbot Backup System\",
                    \"ts\": $(date +%s)
                }]
            }" 2>&1 | tee -a "${LOG_FILE}"
    fi
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check mongodump availability
    if ! command -v mongodump &> /dev/null; then
        log_error "mongodump not found. Please install MongoDB tools."
        exit 1
    fi
    
    # Create backup directory
    mkdir -p "${BACKUP_DIR}"
    
    # Check disk space (require at least 10GB free)
    available_space=$(df -BG "${BACKUP_DIR}" | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "${available_space}" -lt 10 ]; then
        log_error "Insufficient disk space. Available: ${available_space}GB, Required: 10GB"
        notify_slack "Backup failed: Insufficient disk space (${available_space}GB available)" "error"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Perform MongoDB backup
perform_backup() {
    log "Starting MongoDB backup: ${BACKUP_NAME}"
    
    # Build mongodump command
    MONGODUMP_CMD="mongodump"
    MONGODUMP_CMD+=" --host=${MONGODB_HOST}"
    MONGODUMP_CMD+=" --port=${MONGODB_PORT}"
    
    if [ -n "${MONGODB_USER}" ]; then
        MONGODUMP_CMD+=" --username=${MONGODB_USER}"
    fi
    
    if [ -n "${MONGODB_PASS}" ]; then
        MONGODUMP_CMD+=" --password=${MONGODB_PASS}"
    fi
    
    MONGODUMP_CMD+=" --db=${DATABASE_NAME}"
    MONGODUMP_CMD+=" --out=${BACKUP_PATH}"
    MONGODUMP_CMD+=" --gzip"
    
    # Execute backup
    if eval "${MONGODUMP_CMD}" 2>&1 | tee -a "${LOG_FILE}"; then
        log_success "MongoDB backup completed: ${BACKUP_PATH}"
    else
        log_error "MongoDB backup failed"
        notify_slack "MongoDB backup failed for ${DATABASE_NAME}" "error"
        exit 1
    fi
}

# Compress backup
compress_backup() {
    if [ "${ENABLE_COMPRESSION}" = "true" ]; then
        log "Compressing backup..."
        
        tar -czf "${BACKUP_PATH}.tar.gz" -C "${BACKUP_DIR}" "${BACKUP_NAME}"
        
        if [ $? -eq 0 ]; then
            rm -rf "${BACKUP_PATH}"
            log_success "Backup compressed: ${BACKUP_PATH}.tar.gz"
            
            # Calculate size
            backup_size=$(du -h "${BACKUP_PATH}.tar.gz" | cut -f1)
            log "Backup size: ${backup_size}"
        else
            log_error "Compression failed"
            notify_slack "Backup compression failed" "error"
            exit 1
        fi
    fi
}

# Encrypt backup
encrypt_backup() {
    if [ "${ENABLE_ENCRYPTION}" = "true" ]; then
        log "Encrypting backup..."
        
        if [ -z "${ENCRYPTION_KEY}" ]; then
            log_error "ENCRYPTION_KEY not set"
            exit 1
        fi
        
        openssl enc -aes-256-cbc -salt \
            -in "${BACKUP_PATH}.tar.gz" \
            -out "${BACKUP_PATH}.tar.gz.enc" \
            -pass pass:"${ENCRYPTION_KEY}"
        
        if [ $? -eq 0 ]; then
            rm "${BACKUP_PATH}.tar.gz"
            log_success "Backup encrypted"
        else
            log_error "Encryption failed"
            notify_slack "Backup encryption failed" "error"
            exit 1
        fi
    fi
}

# Upload to S3
upload_to_s3() {
    if [ -n "${S3_BUCKET}" ]; then
        log "Uploading backup to S3..."
        
        local backup_file="${BACKUP_PATH}.tar.gz"
        [ "${ENABLE_ENCRYPTION}" = "true" ] && backup_file="${backup_file}.enc"
        
        if command -v aws &> /dev/null; then
            aws s3 cp "${backup_file}" "s3://${S3_BUCKET}/mongodb-backups/" \
                --storage-class STANDARD_IA \
                2>&1 | tee -a "${LOG_FILE}"
            
            if [ $? -eq 0 ]; then
                log_success "Backup uploaded to S3"
            else
                log_error "S3 upload failed"
                notify_slack "S3 upload failed" "error"
            fi
        else
            log_warning "AWS CLI not found. Skipping S3 upload."
        fi
    fi
}

# Clean old backups
cleanup_old_backups() {
    log "Cleaning up old backups (retention: ${RETENTION_DAYS} days)..."
    
    find "${BACKUP_DIR}" -name "tourism_backup_*" -type f -mtime +${RETENTION_DAYS} -exec rm -f {} \;
    
    deleted_count=$(find "${BACKUP_DIR}" -name "tourism_backup_*" -type f -mtime +${RETENTION_DAYS} | wc -l)
    
    if [ "${deleted_count}" -gt 0 ]; then
        log "Deleted ${deleted_count} old backup(s)"
    else
        log "No old backups to delete"
    fi
}

# Verify backup integrity
verify_backup() {
    log "Verifying backup integrity..."
    
    local backup_file="${BACKUP_PATH}.tar.gz"
    [ "${ENABLE_ENCRYPTION}" = "true" ] && backup_file="${backup_file}.enc"
    
    if [ -f "${backup_file}" ]; then
        file_size=$(stat -f%z "${backup_file}" 2>/dev/null || stat -c%s "${backup_file}")
        
        if [ "${file_size}" -gt 1000 ]; then
            log_success "Backup verification passed (size: ${file_size} bytes)"
            return 0
        else
            log_error "Backup file too small (${file_size} bytes)"
            return 1
        fi
    else
        log_error "Backup file not found"
        return 1
    fi
}

# Generate backup report
generate_report() {
    log "Generating backup report..."
    
    local backup_file="${BACKUP_PATH}.tar.gz"
    [ "${ENABLE_ENCRYPTION}" = "true" ] && backup_file="${backup_file}.enc"
    
    local file_size=$(du -h "${backup_file}" | cut -f1)
    local backup_count=$(find "${BACKUP_DIR}" -name "tourism_backup_*" -type f | wc -l)
    
    cat > "${BACKUP_DIR}/backup_report_${DATE}.txt" << EOF
========================================
MongoDB Backup Report
========================================
Date: $(date)
Backup Name: ${BACKUP_NAME}
Database: ${DATABASE_NAME}
Backup Size: ${file_size}
Compression: ${ENABLE_COMPRESSION}
Encryption: ${ENABLE_ENCRYPTION}
S3 Upload: $([ -n "${S3_BUCKET}" ] && echo "Yes (${S3_BUCKET})" || echo "No")
Total Backups: ${backup_count}
Retention Period: ${RETENTION_DAYS} days
Status: SUCCESS
========================================
EOF
    
    log_success "Backup report generated"
}

# Main execution
main() {
    log "========================================
"
    log "MongoDB Automated Backup System Started"
    log "========================================"
    
    # Run backup process
    check_prerequisites
    perform_backup
    compress_backup
    encrypt_backup
    
    if verify_backup; then
        upload_to_s3
        cleanup_old_backups
        generate_report
        
        log_success "Backup completed successfully!"
        notify_slack "MongoDB backup completed successfully: ${BACKUP_NAME}" "good"
        exit 0
    else
        log_error "Backup verification failed"
        notify_slack "Backup verification failed: ${BACKUP_NAME}" "error"
        exit 1
    fi
}

# Run main function
main "$@"
