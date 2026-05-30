#!/bin/bash
# Log viewer script for Mudra
# Usage: ./scripts/logs.sh [follow|tail|errors|nginx]

COMMAND="${1:-follow}"
APP_DIR="/opt/mudra"

case "$COMMAND" in
    follow|f)
        echo "Following application logs (Ctrl+C to exit)..."
        cd "$APP_DIR"
        docker-compose -f docker-compose.prod.yml logs -f mudra
        ;;

    tail|t)
        echo "Last 50 lines of application logs..."
        cd "$APP_DIR"
        docker-compose -f docker-compose.prod.yml logs --tail=50 mudra
        ;;

    errors|e)
        echo "Error logs only..."
        cd "$APP_DIR"
        docker-compose -f docker-compose.prod.yml logs mudra | grep -i "error\|exception\|failed"
        ;;

    nginx|n)
        echo "Nginx error logs..."
        tail -f /var/log/nginx/mudra_error.log
        ;;

    access|a)
        echo "Nginx access logs..."
        tail -f /var/log/nginx/mudra_access.log
        ;;

    monitor|m)
        echo "Mudra monitoring logs..."
        tail -f /var/log/mudra/monitor.log
        ;;

    *)
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  follow, f       - Follow application logs in real-time"
        echo "  tail, t         - Show last 50 lines of application logs"
        echo "  errors, e       - Show error logs only"
        echo "  nginx, n        - Follow Nginx error logs"
        echo "  access, a       - Follow Nginx access logs"
        echo "  monitor, m      - Follow monitor script logs"
        echo ""
        echo "Examples:"
        echo "  $0 follow       - Follow app logs"
        echo "  $0 errors       - Show only errors"
        echo "  $0 nginx        - Show Nginx errors"
        exit 1
        ;;
esac
