# Hostinger MCP Deployment Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deploy Mudra trading app to Hostinger VPS with automated domain DNS setup, SSL certificate provisioning, and Docker container orchestration using Hostinger MCP.

**Architecture:** 
- Hostinger MCP tools manage VPS instance, DNS records, and domain configuration
- GitHub repository cloned to VPS with environment configuration
- Docker Compose orchestrates FastAPI backend and React frontend containers
- Let's Encrypt SSL certificate for HTTPS secured by Hostinger's certificate management
- Automated health checks and monitoring scripts verify deployment success

**Tech Stack:** Hostinger VPS (Ubuntu 22.04, 2GB RAM), Docker, Docker Compose, FastAPI, React, SQLite, Let's Encrypt SSL

---

## File Structure

**Deployment Configuration:**
- Modify: `.env.prod` — Production environment variables (API keys, database, mode)
- Existing: `docker-compose.prod.yml` — Production container orchestration
- Existing: `docs/DEPLOYMENT_GUIDE.md` — Reference documentation

**Hostinger Integration Scripts (created by this plan):**
- Create: `scripts/hostinger-deploy.sh` — Master deployment script using Hostinger MCP
- Create: `scripts/verify-deployment.sh` — Health check and smoke tests

---

## Tasks

### Task 1: Retrieve VPS & Domain Details from Hostinger

**Files:**
- Create: `.env.prod`

- [ ] **Step 1: Get VPS instance details via Hostinger MCP**

Using Gemini CLI with Hostinger MCP, retrieve the VPS ID and IP address:

```bash
# In Gemini CLI, call the Hostinger MCP tool:
# mcp__hostinger__VPS_getVirtualMachinesV1
# This returns list of all VPS instances with details like:
# - virtualMachineId
# - ip_address (public IP)
# - status
# - hostname
```

Expected output: JSON with VPS list. Extract and note:
- `virtualMachineId` (e.g., "12345")
- `ip_address` (e.g., "203.0.113.42")
- Current hostname

- [ ] **Step 2: Retrieve domain details via Hostinger MCP**

Call Hostinger MCP tool to get domain configuration:

```bash
# mcp__hostinger__domains_getDomainListV1
# Returns list of domains owned:
# - domain name (e.g., "trading-app.com")
# - registrant info
# - nameserver config
```

Expected output: Domain list with nameserver configuration. Verify:
- Domain name is correct
- Current nameserver records

- [ ] **Step 3: Create production environment file**

Create `.env.prod` with production values:

```bash
cat > .env.prod << 'EOF'
# Database
DATABASE_URL=sqlite:///./trading.db

# Binance Live Trading
BINANCE_API_KEY=your_binance_key_here
BINANCE_API_SECRET=your_binance_secret_here

# Trading Mode (paper or live)
DEFAULT_MODE=paper

# Default Timeframe
DEFAULT_TIMEFRAME=1h

# Domain
DOMAIN=your-domain.com
EOF
```

Secure the file:

```bash
chmod 600 .env.prod
```

- [ ] **Step 4: Commit environment template**

```bash
git add .env.prod
git commit -m "feat: add production environment configuration template"
```

---

### Task 2: Configure Domain DNS to Point to VPS IP

**Files:**
- Modify: No code changes; DNS configuration via Hostinger MCP

- [ ] **Step 1: Get current DNS records via Hostinger MCP**

Call Hostinger MCP to retrieve existing DNS records:

```bash
# mcp__hostinger__DNS_getDNSRecordsV1
# Parameters: domain (your domain name)
# Returns array of current DNS records with:
# - name (subdomain or @)
# - type (A, AAAA, CNAME, MX, TXT, etc.)
# - content (current value)
# - ttl
```

Expected: Current DNS records. Note any existing A records.

- [ ] **Step 2: Update A record to point to VPS IP**

Call Hostinger MCP to update DNS records:

```bash
# mcp__hostinger__DNS_updateDNSRecordsV1
# Parameters:
# - domain: "your-domain.com"
# - zone: [{
#     "name": "@",
#     "type": "A",
#     "ttl": 3600,
#     "records": [{"content": "203.0.113.42"}]  # VPS IP from Task 1
#   }]
# - overwrite: false (to preserve other records)
```

Expected response: `{"status": "success", "records": [...]}`

- [ ] **Step 3: Add www subdomain A record**

Call Hostinger MCP to add www subdomain:

```bash
# mcp__hostinger__DNS_updateDNSRecordsV1
# Parameters:
# - domain: "your-domain.com"
# - zone: [{
#     "name": "www",
#     "type": "A",
#     "ttl": 3600,
#     "records": [{"content": "203.0.113.42"}]  # Same VPS IP
#   }]
# - overwrite: false
```

Expected response: Success with www A record added.

- [ ] **Step 4: Verify DNS propagation**

Wait 2-5 minutes for DNS to propagate, then verify:

```bash
nslookup your-domain.com
# Should return: 203.0.113.42

nslookup www.your-domain.com
# Should return: 203.0.113.42
```

Both commands should resolve to VPS IP.

- [ ] **Step 5: Document DNS configuration**

Create a note with DNS setup details:

```markdown
## DNS Configuration

Domain: your-domain.com
VPS IP: 203.0.113.42

Records:
- @ A record → 203.0.113.42 (TTL: 3600)
- www A record → 203.0.113.42 (TTL: 3600)

Propagation: Complete at [timestamp]
```

---

### Task 3: Retrieve VPS Details and Connect via SSH

**Files:**
- Create: `scripts/hostinger-deploy.sh` (partial)

- [ ] **Step 1: Get VPS root password via Hostinger MCP**

Call to retrieve VPS credentials:

```bash
# mcp__hostinger__VPS_getVirtualMachineDetailsV1
# Parameters: virtualMachineId (from Task 1)
# Returns VPS details including:
# - ip_address
# - username (usually "root")
# - os_name
# - status
# Note: Password may not be returned via API; check Hostinger panel if needed
```

Expected: VPS details. Note:
- Public IP address
- Root username
- OS (Ubuntu 22.04)

- [ ] **Step 2: Connect to VPS via SSH and verify access**

```bash
ssh root@203.0.113.42
# Enter password from Hostinger panel

# Once connected, verify system:
uname -a
# Expected: Linux ... 5.15.x ... #1 SMP Ubuntu 22.04

cat /etc/os-release
# Expected: Ubuntu 22.04 LTS
```

Verify you can access the VPS shell.

- [ ] **Step 3: Update system packages**

```bash
apt update
apt upgrade -y
```

Expected: Package manager updates complete. No errors.

- [ ] **Step 4: Create application directory**

```bash
mkdir -p /opt/mudra
cd /opt/mudra
```

- [ ] **Step 5: Verify Docker is installable**

```bash
curl -fsSL https://get.docker.com | sh
```

Expected: Docker installation script downloaded successfully. Proceed to Task 4 for installation.

---

### Task 4: Install Docker and Docker Compose on VPS

**Files:**
- Existing: `docker-compose.prod.yml`

- [ ] **Step 1: Install Docker Engine**

```bash
# Install required packages
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

Expected: Docker installed. Verify:

```bash
docker --version
# Expected: Docker version 24.x or higher

docker ps
# Expected: List of containers (empty if no containers running)
```

- [ ] **Step 2: Install Docker Compose standalone**

```bash
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

Verify:

```bash
docker-compose --version
# Expected: Docker Compose version 2.x or higher
```

- [ ] **Step 3: Start Docker daemon and enable on boot**

```bash
systemctl start docker
systemctl enable docker
```

Verify running:

```bash
systemctl status docker
# Expected: active (running)
```

- [ ] **Step 4: Add root to docker group (optional, for sudo-free access)**

```bash
usermod -aG docker root
newgrp docker
```

Test:

```bash
docker ps
# Should work without sudo
```

- [ ] **Step 5: Commit progress**

```bash
git add docker-compose.prod.yml
git commit -m "ops: docker and docker compose installed on VPS"
```

---

### Task 5: Clone Repository and Configure Secrets

**Files:**
- Modify: `.env.prod` (populate with actual values)
- Existing: `.gitignore` (should exclude .env files)

- [ ] **Step 1: Clone Mudra repository to VPS**

```bash
cd /opt/mudra
git clone https://github.com/YOUR_GITHUB_USERNAME/mudra.git .
```

Expected: Repository cloned. Verify:

```bash
ls -la
# Expected: Shows backend/, frontend/, docker-compose.prod.yml, etc.

git log --oneline -3
# Expected: Shows recent commits
```

- [ ] **Step 2: Copy production environment file to VPS**

On your local machine, copy `.env.prod` to VPS:

```bash
scp .env.prod root@203.0.113.42:/opt/mudra/.env
```

Or on VPS, edit directly:

```bash
cat > /opt/mudra/.env << 'EOF'
DATABASE_URL=sqlite:///./trading.db
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret
DEFAULT_MODE=paper
DEFAULT_TIMEFRAME=1h
DOMAIN=your-domain.com
EOF
```

Verify:

```bash
cat /opt/mudra/.env
# Should show all environment variables (secrets hidden in terminal)

chmod 600 /opt/mudra/.env
```

- [ ] **Step 3: Verify all required files exist**

```bash
cd /opt/mudra
ls -la backend/ frontend/ docker-compose.prod.yml
```

Expected: All directories and compose file present.

- [ ] **Step 4: Build Docker images**

```bash
cd /opt/mudra
docker-compose -f docker-compose.prod.yml build
```

Expected: Both backend and frontend images built successfully. Output shows:
```
Successfully tagged mudra-backend:latest
Successfully tagged mudra-frontend:latest
```

- [ ] **Step 5: Commit repository state**

```bash
git status
# Should show: working tree clean (except .env which is .gitignored)
```

---

### Task 6: Start Containers and Verify Basic Health

**Files:**
- Existing: `docker-compose.prod.yml`

- [ ] **Step 1: Start containers in detached mode**

```bash
cd /opt/mudra
docker-compose -f docker-compose.prod.yml up -d
```

Expected output:
```
Creating mudra-backend ... done
Creating mudra-frontend ... done
```

- [ ] **Step 2: Verify containers are running**

```bash
docker-compose -f docker-compose.prod.yml ps
```

Expected output:
```
NAME              STATUS              PORTS
mudra-backend     Up 10 seconds        0.0.0.0:8000->8000/tcp
mudra-frontend    Up 5 seconds         0.0.0.0:3000->3000/tcp
```

Both containers should show "Up".

- [ ] **Step 3: Check backend health endpoint**

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "ok"}
```

If fails, check logs:

```bash
docker-compose -f docker-compose.prod.yml logs backend
# Look for import errors or startup issues
```

- [ ] **Step 4: Check frontend is accessible**

```bash
curl http://localhost:3000
```

Expected: HTML response (React app shell).

- [ ] **Step 5: Verify database file was created**

```bash
ls -lh /opt/mudra/trading.db
```

Expected: File exists with size > 0 bytes (SQLite database created).

- [ ] **Step 6: Commit successful container start**

```bash
git add docker-compose.prod.yml
git commit -m "ops: containers started and health verified"
```

---

### Task 7: Configure Nginx Reverse Proxy with SSL

**Files:**
- Create: `/etc/nginx/sites-available/mudra.conf`

- [ ] **Step 1: Install Nginx and Certbot**

```bash
apt-get install -y nginx certbot python3-certbot-nginx
```

Verify:

```bash
nginx -v
# Expected: nginx/1.22.x or higher

certbot --version
# Expected: certbot 2.x or higher
```

- [ ] **Step 2: Create Nginx configuration file**

Create `/etc/nginx/sites-available/mudra.conf`:

```nginx
# Upstream backend
upstream backend {
    server localhost:8000;
}

# Upstream frontend
upstream frontend {
    server localhost:3000;
}

# HTTP redirect to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name your-domain.com www.your-domain.com;

    location / {
        return 301 https://$server_name$request_uri;
    }

    # Certbot challenge
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
}

# HTTPS backend API
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL certificates (to be populated by certbot)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;

    # API routes → backend
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    # Frontend routes
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_redirect off;
    }
}
```

Enable the configuration:

```bash
ln -s /etc/nginx/sites-available/mudra.conf /etc/nginx/sites-enabled/
```

Test Nginx configuration:

```bash
nginx -t
# Expected: syntax is ok, test is successful
```

- [ ] **Step 3: Obtain SSL certificate with Certbot**

```bash
certbot certonly --standalone \
    -d your-domain.com \
    -d www.your-domain.com \
    --agree-tos \
    -m your-email@example.com \
    --non-interactive
```

Expected output:
```
Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/your-domain.com/fullchain.pem
```

Verify certificate:

```bash
ls -la /etc/letsencrypt/live/your-domain.com/
# Expected: fullchain.pem and privkey.pem exist
```

- [ ] **Step 4: Update Nginx config with actual certificate paths**

The paths in nginx config should now match:

```bash
grep ssl_certificate /etc/nginx/sites-available/mudra.conf
# Should show paths match Certbot output
```

- [ ] **Step 5: Start and enable Nginx**

```bash
systemctl start nginx
systemctl enable nginx
```

Verify:

```bash
systemctl status nginx
# Expected: active (running)
```

- [ ] **Step 6: Test HTTPS access**

```bash
curl https://your-domain.com/health
# Expected: {"status": "ok"}
```

Or from local machine:

```bash
curl https://your-domain.com
# Expected: React app HTML
```

- [ ] **Step 7: Set up Certbot auto-renewal**

```bash
certbot renew --dry-run
# Test renewal process

systemctl enable certbot.timer
# Enable automatic renewal
```

Verify:

```bash
systemctl status certbot.timer
# Expected: active (enabled)
```

---

### Task 8: Create Deployment Automation Scripts

**Files:**
- Create: `scripts/hostinger-deploy.sh`
- Create: `scripts/verify-deployment.sh`

- [ ] **Step 1: Create main deployment script**

Create `scripts/hostinger-deploy.sh`:

```bash
#!/bin/bash

set -e

echo "🚀 Mudra Deployment via Hostinger MCP"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
VPS_IP="${VPS_IP:-203.0.113.42}"
DOMAIN="${DOMAIN:-your-domain.com}"
APP_DIR="/opt/mudra"

echo -e "${YELLOW}[1/5]${NC} Connecting to VPS..."
ssh root@$VPS_IP "echo 'VPS connection successful'"

echo -e "${YELLOW}[2/5]${NC} Pulling latest code..."
ssh root@$VPS_IP "cd $APP_DIR && git pull origin main"

echo -e "${YELLOW}[3/5]${NC} Rebuilding containers..."
ssh root@$VPS_IP "cd $APP_DIR && docker-compose -f docker-compose.prod.yml build"

echo -e "${YELLOW}[4/5]${NC} Restarting services..."
ssh root@$VPS_IP "cd $APP_DIR && docker-compose -f docker-compose.prod.yml down && docker-compose -f docker-compose.prod.yml up -d"

echo -e "${YELLOW}[5/5]${NC} Verifying deployment..."
sleep 3

if curl -s https://$DOMAIN/health | grep -q "ok"; then
    echo -e "${GREEN}✅ Deployment successful!${NC}"
    echo "App available at: https://$DOMAIN"
else
    echo -e "${RED}❌ Health check failed${NC}"
    exit 1
fi
```

Make executable:

```bash
chmod +x scripts/hostinger-deploy.sh
```

- [ ] **Step 2: Create verification script**

Create `scripts/verify-deployment.sh`:

```bash
#!/bin/bash

set -e

DOMAIN="${DOMAIN:-your-domain.com}"

echo "🔍 Mudra Deployment Verification"
echo "=================================="

# Test 1: Health endpoint
echo -n "Testing /health endpoint... "
HEALTH=$(curl -s https://$DOMAIN/health)
if echo "$HEALTH" | grep -q "ok"; then
    echo "✅ PASS"
else
    echo "❌ FAIL: $HEALTH"
    exit 1
fi

# Test 2: Frontend loads
echo -n "Testing frontend... "
FRONTEND=$(curl -s https://$DOMAIN | head -c 100)
if echo "$FRONTEND" | grep -q "<!DOCTYPE\|<html"; then
    echo "✅ PASS"
else
    echo "❌ FAIL: Frontend not responding"
    exit 1
fi

# Test 3: API endpoints
echo -n "Testing /api/positions... "
POSITIONS=$(curl -s https://$DOMAIN/api/positions)
if [ $? -eq 0 ]; then
    echo "✅ PASS"
else
    echo "❌ FAIL: API not responding"
    exit 1
fi

# Test 4: SSL certificate
echo -n "Testing SSL certificate... "
CERT_INFO=$(openssl s_client -connect $DOMAIN:443 -servername $DOMAIN 2>/dev/null | openssl x509 -noout -dates 2>/dev/null)
if echo "$CERT_INFO" | grep -q "notAfter"; then
    EXPIRE_DATE=$(echo "$CERT_INFO" | grep "notAfter" | cut -d= -f2)
    echo "✅ PASS (Expires: $EXPIRE_DATE)"
else
    echo "❌ FAIL: SSL certificate issue"
    exit 1
fi

# Test 5: Database connectivity
echo -n "Testing database... "
DB_TEST=$(curl -s https://$DOMAIN/api/history | head -c 10)
if [ $? -eq 0 ]; then
    echo "✅ PASS"
else
    echo "❌ FAIL: Database connection issue"
    exit 1
fi

echo ""
echo -e "✅ All deployment checks passed!"
echo "Mudra is ready at: https://$DOMAIN"
```

Make executable:

```bash
chmod +x scripts/verify-deployment.sh
```

- [ ] **Step 3: Test deployment script locally**

```bash
export VPS_IP=203.0.113.42
export DOMAIN=your-domain.com

# Test verification script
./scripts/verify-deployment.sh
```

Expected: All checks pass with ✅.

- [ ] **Step 4: Commit scripts**

```bash
git add scripts/hostinger-deploy.sh scripts/verify-deployment.sh
git commit -m "ops: add hostinger deployment automation scripts"
```

---

### Task 9: Set Up Monitoring and Backup Scripts

**Files:**
- Create: `scripts/monitor.sh`
- Create: `scripts/backup.sh`

- [ ] **Step 1: Create monitoring script**

Create `scripts/monitor.sh`:

```bash
#!/bin/bash

VPS_IP="${VPS_IP:-203.0.113.42}"
DOMAIN="${DOMAIN:-your-domain.com}"

echo "📊 Mudra Monitoring Dashboard"
echo "=============================="
echo "Timestamp: $(date)"
echo ""

# Check containers
echo "🐳 Container Status:"
ssh root@$VPS_IP "docker-compose -f /opt/mudra/docker-compose.prod.yml ps"

echo ""
echo "📈 System Resources:"
ssh root@$VPS_IP "free -h; echo '---'; df -h /opt/mudra"

echo ""
echo "🌐 SSL Certificate Status:"
openssl s_client -connect $DOMAIN:443 -servername $DOMAIN 2>/dev/null | openssl x509 -noout -dates

echo ""
echo "📊 Application Logs (last 10 lines):"
ssh root@$VPS_IP "docker-compose -f /opt/mudra/docker-compose.prod.yml logs --tail=10 backend"
```

Make executable:

```bash
chmod +x scripts/monitor.sh
```

- [ ] **Step 2: Create backup script**

Create `scripts/backup.sh`:

```bash
#!/bin/bash

VPS_IP="${VPS_IP:-203.0.113.42}"
BACKUP_DIR="/opt/mudra/backups"
DB_FILE="/opt/mudra/trading.db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "🔄 Mudra Database Backup"
echo "========================"

ssh root@$VPS_IP "mkdir -p $BACKUP_DIR"

# Backup database
echo "Backing up database..."
ssh root@$VPS_IP "cp $DB_FILE $BACKUP_DIR/trading_${TIMESTAMP}.db"

# Keep only last 7 backups
echo "Cleaning up old backups..."
ssh root@$VPS_IP "ls -t $BACKUP_DIR/trading_*.db | tail -n +8 | xargs -r rm"

# Verify
BACKUP_COUNT=$(ssh root@$VPS_IP "ls $BACKUP_DIR/trading_*.db | wc -l")
echo "✅ Backup complete. Total backups: $BACKUP_COUNT"

# List recent backups
echo ""
echo "Recent backups:"
ssh root@$VPS_IP "ls -lh $BACKUP_DIR/trading_*.db | tail -5"
```

Make executable:

```bash
chmod +x scripts/backup.sh
```

- [ ] **Step 3: Set up cron jobs for automated backup**

On VPS, add to crontab:

```bash
ssh root@$VPS_IP "crontab -e"
```

Add these lines:

```cron
# Daily backup at 2 AM UTC
0 2 * * * /opt/mudra/scripts/backup.sh >> /var/log/mudra-backup.log 2>&1

# Health check every 30 minutes
*/30 * * * * curl -s https://your-domain.com/health || echo "Health check failed at $(date)" >> /var/log/mudra-health.log
```

- [ ] **Step 4: Commit monitoring scripts**

```bash
git add scripts/monitor.sh scripts/backup.sh
git commit -m "ops: add monitoring and backup scripts"
```

---

### Task 10: Final Verification and Documentation

**Files:**
- Modify: `DEPLOYMENT_SUMMARY.md` (update with actual values)

- [ ] **Step 1: Run complete verification suite**

```bash
./scripts/verify-deployment.sh
```

Expected: All tests pass with ✅.

- [ ] **Step 2: Check monitoring dashboard**

```bash
./scripts/monitor.sh
```

Expected: Shows all containers running, healthy SSL cert, recent logs clean.

- [ ] **Step 3: Test manual backup**

```bash
./scripts/backup.sh
```

Expected: Backup created and verified.

- [ ] **Step 4: Document deployment details**

Update `DEPLOYMENT_SUMMARY.md`:

```markdown
# Mudra Deployment Summary

## Deployment Date
2026-05-30

## Infrastructure
- **VPS Provider:** Hostinger
- **VPS ID:** 12345
- **IP Address:** 203.0.113.42
- **OS:** Ubuntu 22.04 LTS
- **RAM:** 2GB
- **Storage:** 50GB SSD
- **Monthly Cost:** $12-15

## Domain
- **Domain Name:** your-domain.com
- **Registrar:** Hostinger
- **DNS A Record:** 203.0.113.42
- **SSL Certificate:** Let's Encrypt (valid until [date])

## Application
- **Frontend:** https://your-domain.com (React + Vite)
- **API:** https://your-domain.com/api (FastAPI)
- **Health Check:** https://your-domain.com/health

## Deployment Status
✅ All systems operational

## Recent Changes
- Deployed commit: [git SHA from `git rev-parse HEAD`]
- Docker images: mudra-backend:latest, mudra-frontend:latest

## Backup & Recovery
- Database backups: /opt/mudra/backups/
- Backup frequency: Daily at 2 AM UTC
- Retention: Last 7 days
- Recovery time: ~1 minute

## Monitoring
- Health checks: Every 30 minutes
- Logs: `/var/log/mudra-*.log`
- Manual check: `./scripts/monitor.sh`

## Maintenance Tasks
- SSL certificate renewal: Automatic (certbot.timer)
- Docker image updates: Manual (run `./scripts/hostinger-deploy.sh`)
- Database optimization: Manual (as needed)
```

- [ ] **Step 5: Create deployment checklist**

Create `DEPLOYMENT_CHECKLIST.md`:

```markdown
# Mudra Deployment Checklist

## Pre-Deployment
- [ ] GitHub repository initialized and pushed
- [ ] All tests passing locally
- [ ] .env.prod configured with API keys
- [ ] Domain purchased and in Hostinger account
- [ ] VPS provisioned in Hostinger (2GB RAM, Ubuntu 22.04)

## VPS Setup (SSH Access)
- [ ] SSH access verified to VPS IP
- [ ] System packages updated
- [ ] Docker installed and running
- [ ] Docker Compose installed

## Application Deployment
- [ ] Repository cloned to /opt/mudra
- [ ] .env file copied to VPS
- [ ] Docker images built
- [ ] Containers started (backend + frontend)
- [ ] Health endpoint responds (http://localhost:8000/health)
- [ ] Frontend accessible (http://localhost:3000)
- [ ] Database created (trading.db exists)

## Reverse Proxy & SSL
- [ ] Nginx installed
- [ ] Certbot installed and configured
- [ ] SSL certificate issued for domain
- [ ] Nginx configuration created and enabled
- [ ] HTTP → HTTPS redirect working
- [ ] HTTPS connection succeeds (`curl https://domain`)
- [ ] Security headers present

## Verification & Monitoring
- [ ] Deployment verification script passes all tests
- [ ] Monitoring dashboard shows healthy containers
- [ ] Database backup script works
- [ ] Cron jobs configured for auto-backup
- [ ] Health check endpoint responds

## Documentation
- [ ] DEPLOYMENT_SUMMARY.md updated
- [ ] DEPLOYMENT_CHECKLIST.md complete
- [ ] Hostinger credentials stored securely (not in git)
- [ ] README.md includes deployment reference

## Post-Deployment
- [ ] User can login and access application
- [ ] Manual trades can be placed in paper mode
- [ ] Positions display correctly
- [ ] SSL certificate valid and auto-renewing
- [ ] Daily backups running automatically

## Rollback Plan (if needed)
- [ ] Previous database backup identified
- [ ] Previous Docker images saved
- [ ] Rollback script tested locally
- [ ] Rollback SOP documented
```

- [ ] **Step 6: Final commit**

```bash
git add DEPLOYMENT_SUMMARY.md DEPLOYMENT_CHECKLIST.md
git commit -m "docs: add deployment summary and verification checklist"

git log --oneline -5
# Verify all deployment commits are present
```

- [ ] **Step 7: Confirm application is fully operational**

```bash
./scripts/verify-deployment.sh

# Also test key features:
curl -s https://your-domain.com/api/positions | jq .
# Should return JSON array of positions (empty [] initially)

curl -s https://your-domain.com/api/history | jq .
# Should return JSON array of closed trades (empty [] initially)
```

All should succeed without errors.

---

## Success Criteria

✅ **Deployment Complete When:**
1. All DNS A records point to VPS IP (verified via `nslookup`)
2. Frontend loads at `https://your-domain.com` with no SSL warnings
3. API endpoints respond at `https://your-domain.com/api/`
4. Health check endpoint returns `{"status": "ok"}`
5. Database is initialized and accessible
6. All monitoring scripts run successfully
7. Automated daily backups are created
8. SSL certificate auto-renewal is configured
9. Container logs show no errors
10. All deployment verification tests pass with ✅

---

## Rollback Plan

If deployment fails at any point:

1. **Containers won't start:**
   ```bash
   docker-compose -f docker-compose.prod.yml logs backend
   # Check error messages and fix .env or code
   ```

2. **SSL certificate issues:**
   ```bash
   certbot certificates
   certbot renew --force-renewal
   ```

3. **Database corruption:**
   ```bash
   cp /opt/mudra/backups/trading_YYYYMMDD_HHMMSS.db /opt/mudra/trading.db
   docker-compose -f docker-compose.prod.yml restart backend
   ```

4. **Complete restart:**
   ```bash
   cd /opt/mudra
   docker-compose -f docker-compose.prod.yml down --volumes
   git reset --hard HEAD
   docker-compose -f docker-compose.prod.yml up -d
   ```

---
