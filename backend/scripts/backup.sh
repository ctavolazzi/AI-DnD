#!/bin/bash
# Database backup script with compression and retention policy

BACKUP_DIR="backups"
DB_FILE="dnd_game.db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="dnd_game_$TIMESTAMP.db"

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

# Check if database exists
if [ ! -f "$DB_FILE" ]; then
    echo "Error: Database file $DB_FILE not found"
    exit 1
fi

echo "Creating backup: $BACKUP_NAME"

# Create backup
cp "$DB_FILE" "$BACKUP_DIR/$BACKUP_NAME"

if [ $? -ne 0 ]; then
    echo "Error: Failed to create backup"
    exit 1
fi

# Compress backup
echo "Compressing backup..."
gzip "$BACKUP_DIR/$BACKUP_NAME"

if [ $? -ne 0 ]; then
    echo "Warning: Failed to compress backup"
else
    echo "✓ Backup created and compressed: ${BACKUP_NAME}.gz"
fi

# Delete backups older than retention period (default: 30 days)
RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-30}
echo "Cleaning up backups older than $RETENTION_DAYS days..."

find "$BACKUP_DIR" -name "*.db.gz" -mtime +$RETENTION_DAYS -delete

if [ $? -eq 0 ]; then
    echo "✓ Old backups cleaned up"
fi

# Show current backups
echo ""
echo "Current backups:"
ls -lh "$BACKUP_DIR"/*.db.gz 2>/dev/null | awk '{print $9, "(" $5 ")"}'

echo ""
echo "✓ Backup complete"

