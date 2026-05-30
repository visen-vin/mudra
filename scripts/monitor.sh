#!/bin/bash
# Health check and monitoring script for Mudra
# Usage: ./scripts/monitor.sh
# Add to crontab: */5 * * * * /opt/mudra/scripts/monitor.sh (check every 5 minutes)

set -e

# Configuration
APP_DIR="/opt/mudra"
LOG_FILE="/var/log/mudra/monitor.log"
HEALTHCHECK_URL="http://localhost:8000/health"
HEALTHCHECK_WEBHOOK=""  # Optional: Set to Healthchecks.io URL for monitoring

# Create log directory
mkdir -p /var/log/mudra
touch "$LOG_FILE"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log_error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1" >> "$LOG_FILE"
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Check if Docker container is running
check_container() {
    if docker-compose -f "$APP_DIR/docker-compose.prod.yml" ps | grep -q "mudra-app.*Up"; then
        log_info "✓ Container is running"
        return 0
    else
        log_error "Container is not running"
        restart_container
        return 1
    fi
}

# Check health endpoint
check_health() {
    RESPONSE=$(curl -s -w "\n%{http_code}" "$HEALTHCHECK_URL" 2>/dev/null || echo "000")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)

    if [ "$HTTP_CODE" = "200" ]; then
        log_info "✓ Health check passed (HTTP $HTTP_CODE)"
        return 0
    else
        log_error "Health check failed (HTTP $HTTP_CODE)"
        restart_container
        return 1
    fi
}

# Check disk space
check_disk() {
    USAGE=$(df /opt/mudra | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$USAGE" -gt 90 ]; then
        log_error "Disk usage critical: ${USAGE}%"
        return 1
    elif [ "$USAGE" -gt 80 ]; then
        log_error "Disk usage warning: ${USAGE}%"
        return 1
    else
        log_info "✓ Disk usage OK: ${USAGE}%"
        return 0
    fi
}

# Check memory
check_memory() {
    MEMORY=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100)}')
    if [ "$MEMORY" -gt 90 ]; then
        log_error "Memory usage critical: ${MEMORY}%"
        return 1
    elif [ "$MEMORY" -gt 80 ]; then
        log_error "Memory usage warning: ${MEMORY}%"
        return 1
    else
        log_info "✓ Memory usage OK: ${MEMORY}%"
        return 0
    fi
}

# Restart container
restart_container() {
    log_info "Attempting to restart container..."
    cd "$APP_DIR"

    if docker-compose -f docker-compose.prod.yml restart mudra-app; then
        log_info "✓ Container restarted successfully"
        sleep 10

        # Re-check health after restart
        if check_health; then
            log_info "✓ Application recovered"
            return 0
        else
            log_error "Application failed to recover after restart"
            return 1
        fi
    else
        log_error "Failed to restart container"
        return 1
    fi
}

# Send webhook notification
send_webhook() {
    if [ -n "$HEALTHCHECK_WEBHOOK" ]; then
        curl -s -m 10 "$HEALTHCHECK_WEBHOOK" > /dev/null 2>&1 || true
    fi
}

# Main monitoring loop
main() {
    log_info "========== Health Check =========="

    STATUS=0

    # Run checks
    check_container || STATUS=$((STATUS + 1))
    check_health || STATUS=$((STATUS + 1))
    check_disk || STATUS=$((STATUS + 1))
    check_memory || STATUS=$((STATUS + 1))

    log_info "========== End Health Check =========="

    # Send webhook notification (success = ping webhook)
    if [ "$STATUS" -eq 0 ]; then
        send_webhook
    fi

    return $STATUS
}

# Run main function
main
exit $?
