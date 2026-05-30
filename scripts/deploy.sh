#!/bin/bash
# Deploy script for Mudra VPS deployment
# Usage: ./scripts/deploy.sh [staging|production]
# Requires: Docker, Docker Compose, Git

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DEPLOY_ENV="${1:-production}"
APP_DIR="/opt/mudra"
COMPOSE_FILE="docker-compose.prod.yml"
BACKUP_DIR="$APP_DIR/backups"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Pre-deployment checks
log_info "Starting Mudra deployment ($DEPLOY_ENV)..."

if [ ! -d "$APP_DIR" ]; then
    log_error "Application directory not found: $APP_DIR"
    exit 1
fi

if [ ! -f "$APP_DIR/.env" ]; then
    log_error ".env file not found in $APP_DIR"
    exit 1
fi

log_info "✓ Application directory found"
log_info "✓ .env file found"

# Create backups directory
mkdir -p "$BACKUP_DIR"

# Backup current database
if [ -f "$APP_DIR/data/mudra.db" ]; then
    BACKUP_FILE="$BACKUP_DIR/mudra_$(date +%Y%m%d_%H%M%S).db"
    cp "$APP_DIR/data/mudra.db" "$BACKUP_FILE"
    log_info "✓ Database backed up: $BACKUP_FILE"
else
    log_warn "No existing database found (new deployment)"
fi

# Stop current containers
log_info "Stopping current containers..."
cd "$APP_DIR"
docker-compose -f "$COMPOSE_FILE" down || true

# Pull latest code
log_info "Pulling latest code..."
git pull origin main

# Build Docker image
log_info "Building Docker image (this may take 2-3 minutes)..."
docker-compose -f "$COMPOSE_FILE" build --no-cache

# Start containers
log_info "Starting containers..."
docker-compose -f "$COMPOSE_FILE" up -d

# Wait for app to be healthy
log_info "Waiting for application to start..."
sleep 10

# Check health
HEALTH_CHECK=$(curl -s http://localhost:8000/health || echo '{"error":"timeout"}')
if echo "$HEALTH_CHECK" | grep -q "ok"; then
    log_info "✓ Application health check passed"
else
    log_error "Application health check failed. Output: $HEALTH_CHECK"
    log_error "Checking logs..."
    docker-compose -f "$COMPOSE_FILE" logs --tail=30
    exit 1
fi

# Verify containers are running
log_info "Verifying containers..."
docker-compose -f "$COMPOSE_FILE" ps

# Summary
log_info ""
log_info "=========================================="
log_info "Deployment completed successfully!"
log_info "=========================================="
log_info "Environment: $DEPLOY_ENV"
log_info "App Directory: $APP_DIR"
log_info "Backup Location: $BACKUP_FILE"
log_info ""
log_info "Next steps:"
log_info "1. Verify frontend: https://yourdomain.com"
log_info "2. Check API: https://yourdomain.com/api/health"
log_info "3. View logs: docker-compose logs -f mudra"
log_info ""
log_info "Deployment complete!"
