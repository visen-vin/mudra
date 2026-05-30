#!/bin/bash
# Database backup script for Mudra
# Usage: ./scripts/backup.sh
# Add to crontab: 0 2 * * * /opt/mudra/scripts/backup.sh (daily at 2 AM)

set -e

# Configuration
DB_PATH="/opt/mudra/data/mudra.db"
BACKUP_DIR="/opt/mudra/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/mudra_$TIMESTAMP.db"
RETENTION_DAYS=30

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

# Create backup directory
if [ ! -d "$BACKUP_DIR" ]; then
    mkdir -p "$BACKUP_DIR"
    log_info "Created backup directory: $BACKUP_DIR"
fi

# Check if database exists
if [ ! -f "$DB_PATH" ]; then
    log_error "Database not found: $DB_PATH"
    exit 1
fi

# Create backup
log_info "Starting database backup..."
log_info "Source: $DB_PATH"
log_info "Destination: $BACKUP_FILE"

if cp "$DB_PATH" "$BACKUP_FILE"; then
    log_info "✓ Backup completed successfully"
else
    log_error "Backup failed"
    exit 1
fi

# Verify backup
if [ -f "$BACKUP_FILE" ]; then
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    log_info "✓ Backup verified - Size: $SIZE"
else
    log_error "Backup file not found after creation"
    exit 1
fi

# Clean old backups
log_info "Cleaning backups older than $RETENTION_DAYS days..."
DELETED_COUNT=$(find "$BACKUP_DIR" -name "mudra_*.db" -mtime +$RETENTION_DAYS -delete -print | wc -l)
log_info "✓ Deleted $DELETED_COUNT old backup(s)"

# List recent backups
log_info "Recent backups:"
ls -lh "$BACKUP_DIR" | tail -5 | awk '{print "  " $9 " (" $5 ")"}'

log_info "Backup job completed successfully"
