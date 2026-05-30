#!/bin/bash

set -e

echo "🚀 Mudra Deployment via Hostinger"
echo "========================================"

# Configuration
VPS_IP="187.127.156.138"
DOMAIN="mudra.kibm.in"
APP_DIR="/opt/mudra"

echo "[1/4] Connecting to VPS and pulling latest code..."
ssh root@$VPS_IP "cd $APP_DIR && git pull origin master"

echo "[2/4] Rebuilding containers..."
ssh root@$VPS_IP "cd $APP_DIR && docker compose -f docker-compose.prod.yml build"

echo "[3/4] Restarting services..."
ssh root@$VPS_IP "cd $APP_DIR && docker compose -f docker-compose.prod.yml up -d"

echo "[4/4] Verifying deployment..."
sleep 5

if curl -s https://$DOMAIN/health | grep -q "ok"; then
    echo "✅ Deployment successful! App available at: https://$DOMAIN"
else
    echo "❌ Health check failed"
    exit 1
fi
