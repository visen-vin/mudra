#!/bin/bash

VPS_IP="187.127.156.138"
BACKUP_DIR="/opt/mudra/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "🔄 Mudra Database Backup"
echo "========================"

ssh root@$VPS_IP "mkdir -p $BACKUP_DIR && docker exec mudra-app sqlite3 /app/data/mudra.db '.backup /app/data/backup_${TIMESTAMP}.db' && cp /var/lib/docker/volumes/mudra_mudra-data/_data/backup_${TIMESTAMP}.db $BACKUP_DIR/mudra_${TIMESTAMP}.db"

echo "✅ Backup complete: $BACKUP_DIR/mudra_${TIMESTAMP}.db"

# Cleanup: keep only last 7 days
ssh root@$VPS_IP "find $BACKUP_DIR -name 'mudra_*.db' -mtime +7 -delete"
