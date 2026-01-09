#!/bin/bash
# Automated MongoDB Backup Script
# Runs daily backups with rotation

set -e

# Configuration
BACKUP_DIR="/backups"
RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-30}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="mongodb_backup_${TIMESTAMP}"
MONGO_URI="${MONGO_URI:-mongodb://localhost:27017}"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "[$(date)] Starting MongoDB backup..."

# Perform backup
mongodump \
    --uri="$MONGO_URI" \
    --out="$BACKUP_DIR/$BACKUP_NAME" \
    --gzip \
    --verbose

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo "[$(date)] Backup completed successfully: $BACKUP_NAME"
    
    # Compress backup
    cd "$BACKUP_DIR"
    tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME"
    rm -rf "$BACKUP_NAME"
    
    echo "[$(date)] Backup compressed: ${BACKUP_NAME}.tar.gz"
    
    # Calculate backup size
    BACKUP_SIZE=$(du -h "${BACKUP_NAME}.tar.gz" | cut -f1)
    echo "[$(date)] Backup size: $BACKUP_SIZE"
    
    # Upload to S3 if configured
    if [ -n "$BACKUP_S3_BUCKET" ] && [ -n "$BACKUP_S3_ACCESS_KEY" ]; then
        echo "[$(date)] Uploading backup to S3..."
        aws s3 cp "${BACKUP_NAME}.tar.gz" "s3://$BACKUP_S3_BUCKET/backups/" \
            --storage-class STANDARD_IA
        echo "[$(date)] Backup uploaded to S3"
    fi
    
    # Remove old backups
    echo "[$(date)] Cleaning up old backups (retention: $RETENTION_DAYS days)..."
    find "$BACKUP_DIR" -name "mongodb_backup_*.tar.gz" -type f -mtime +$RETENTION_DAYS -delete
    
    # Count remaining backups
    BACKUP_COUNT=$(find "$BACKUP_DIR" -name "mongodb_backup_*.tar.gz" -type f | wc -l)
    echo "[$(date)] Total backups retained: $BACKUP_COUNT"
    
    # Create backup log
    echo "$TIMESTAMP,$BACKUP_SIZE,$BACKUP_NAME.tar.gz" >> "$BACKUP_DIR/backup_log.csv"
    
else
    echo "[$(date)] ERROR: Backup failed!"
    exit 1
fi

echo "[$(date)] Backup process completed"
