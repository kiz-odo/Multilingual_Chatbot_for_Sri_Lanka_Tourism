#!/bin/bash
# MongoDB Restore Script
# Restores from backup

set -e

# Check if backup file is provided
if [ -z "$1" ]; then
    echo "Usage: ./restore.sh <backup_file.tar.gz>"
    echo "Available backups:"
    ls -lh /backups/mongodb_backup_*.tar.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE=$1
BACKUP_DIR="/backups"
MONGO_URI="${MONGO_URI:-mongodb://localhost:27017}"
RESTORE_DIR="/tmp/restore_$$"

echo "[$(date)] Starting MongoDB restore from: $BACKUP_FILE"

# Check if backup file exists
if [ ! -f "$BACKUP_DIR/$BACKUP_FILE" ]; then
    echo "ERROR: Backup file not found: $BACKUP_DIR/$BACKUP_FILE"
    exit 1
fi

# Create temporary restore directory
mkdir -p "$RESTORE_DIR"

# Extract backup
echo "[$(date)] Extracting backup..."
tar -xzf "$BACKUP_DIR/$BACKUP_FILE" -C "$RESTORE_DIR"

# Find the backup directory
BACKUP_EXTRACT_DIR=$(find "$RESTORE_DIR" -maxdepth 1 -type d -name "mongodb_backup_*" | head -n 1)

if [ -z "$BACKUP_EXTRACT_DIR" ]; then
    echo "ERROR: Could not find extracted backup directory"
    rm -rf "$RESTORE_DIR"
    exit 1
fi

# Confirm restore
echo "WARNING: This will replace all data in the database!"
echo "Backup file: $BACKUP_FILE"
echo "MongoDB URI: $MONGO_URI"
read -p "Continue with restore? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled"
    rm -rf "$RESTORE_DIR"
    exit 0
fi

# Perform restore
echo "[$(date)] Restoring database..."
mongorestore \
    --uri="$MONGO_URI" \
    --gzip \
    --drop \
    --dir="$BACKUP_EXTRACT_DIR" \
    --verbose

if [ $? -eq 0 ]; then
    echo "[$(date)] Restore completed successfully"
else
    echo "[$(date)] ERROR: Restore failed!"
    rm -rf "$RESTORE_DIR"
    exit 1
fi

# Cleanup
rm -rf "$RESTORE_DIR"
echo "[$(date)] Cleanup completed"
