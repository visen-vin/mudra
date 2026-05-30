# Mudra Trading App - Hostinger VPS Deployment Guide

**Last Updated:** 2026-05-30  
**Target Infrastructure:** Hostinger VPS + Docker + SQLite  
**Target Users:** 2 (You + Brother)  
**Estimated Setup Time:** 2-3 hours (first time)

---

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Cost Analysis](#cost-analysis)
3. [VPS Setup](#vps-setup)
4. [Environment Configuration](#environment-configuration)
5. [Deployment Steps](#deployment-steps)
6. [Domain & SSL Setup](#domain--ssl-setup)
7. [Reverse Proxy Configuration](#reverse-proxy-configuration)
8. [Monitoring & Maintenance](#monitoring--maintenance)
9. [Troubleshooting](#troubleshooting)
10. [Updating & Redeployment](#updating--redeployment)

---

## Architecture Overview

### Single Server Design (Recommended)
```
┌─────────────────────────────────────────────┐
│        Hostinger VPS (Ubuntu 22.04)          │
│  2GB RAM, 1 vCPU, 50GB SSD - $12-15/month   │
├─────────────────────────────────────────────┤
│                                              │
│  ┌──────────────────────────────────────┐   │
│  │  Nginx Reverse Proxy (ports 80/443)  │   │
│  │  • yourdomain.com → :8000 (FastAPI) │   │
│  └──────────────────────────────────────┘   │
│           ↓                ↓                  │
│  ┌─────────────┐  ┌────────────────┐        │
│  │ Docker App  │  │  Docker Data   │        │
│  ├─────────────┤  ├────────────────┤        │
│  │ FastAPI:8000│  │ mudra.db       │        │
│  │ React:dist  │  │ (SQLite)       │        │
│  │ Healthcheck │  │ Backups        │        │
│  └─────────────┘  └────────────────┘        │
│       • Persistent data volume               │
│       • Auto-restart on failure              │
│       • SSL with Let's Encrypt               │
│                                              │
└─────────────────────────────────────────────┘
```

### Why This Design?
- **Simple:** Single VPS, no complexity
- **Cost-effective:** ~$15/month for 2 users
- **Scalable:** Can upgrade RAM/CPU easily
- **Maintainable:** Everything in Docker
- **Reliable:** Built-in health checks + auto-restart

---

## Cost Analysis

### Monthly Breakdown
| Component | Cost | Notes |
|-----------|------|-------|
| Hostinger VPS 2GB | $12-15 | Ubuntu 22.04, 1 vCPU, 50GB SSD |
| Domain (optional) | $10-15 | If registering new domain |
| SSL Certificate | $0 | Let's Encrypt (free) |
| Database | $0 | SQLite (no server needed) |
| **Total** | **$12-30** | Depending on domain |

### Upgrade Path
If traffic grows beyond 2 users:
- **2GB VPS → 4GB VPS:** +$5/month (better memory for caching)
- **Add PostgreSQL:** +$5/month (if SQLite becomes bottleneck)
- **Add Redis cache:** +$3/month (for session management)

---

## VPS Setup

### Step 1: Purchase & Configure VPS on Hostinger

1. Go to Hostinger → **VPS** section
2. Choose plan: **2GB RAM, 1 vCPU, 50GB SSD**
3. Operating System: **Ubuntu 22.04 LTS**
4. Data Center: Choose closest to your location (India = Singapore/Mumbai if available)
5. Complete purchase

### Step 2: Initial Server Setup

Once VPS is provisioned, you'll receive:
- **IP Address:** e.g., `185.123.45.67`
- **Root password:** (from email)

Connect via SSH:
```bash
ssh root@185.123.45.67
```

### Step 3: Install Docker & Docker Compose

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
sudo apt install -y docker.io

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version

# Enable Docker to start on boot
sudo systemctl enable docker
sudo systemctl start docker
```

### Step 4: Create App Directory Structure

```bash
# Create production directory
sudo mkdir -p /opt/mudra
sudo chown $USER:$USER /opt/mudra
cd /opt/mudra

# Create data directory for SQLite
mkdir -p /opt/mudra/data
```

### Step 5: Clone Repository

```bash
cd /opt/mudra
git clone https://github.com/your-repo/mudra.git .
# Or if already a git repo:
# git pull origin main
```

---

## Environment Configuration

### Step 1: Create .env File

```bash
# On VPS, create .env in /opt/mudra/
nano /opt/mudra/.env
```

```env
# Database
DATABASE_URL=sqlite:////opt/mudra/data/mudra.db

# Binance API Keys (paper trading)
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_API_SECRET=your_binance_api_secret_here

# Zerodha API Keys (paper trading)
ZERODHA_API_KEY=your_zerodha_api_key_here
ZERODHA_SESSION_TOKEN=your_zerodha_session_token_here

# Trading Configuration
DEFAULT_MODE=paper          # Start in paper mode
DEFAULT_TIMEFRAME=15m       # Default candle timeframe
LOG_LEVEL=INFO              # Logging level

# Security
# Add this later if needed for CORS/auth
```

**Important:**
- Never commit `.env` to git
- Use different API keys for paper vs live trading
- Restrict API keys in Binance/Zerodha dashboards

### Step 2: Update docker-compose.yml

For production, update `/opt/mudra/docker-compose.yml`:

```yaml
version: '3.8'

services:
  mudra:
    build:
      context: /opt/mudra
      dockerfile: Dockerfile
    container_name: mudra-app
    ports:
      - "8000:8000"
    volumes:
      - /opt/mudra/data:/app/data
      - /opt/mudra/logs:/app/logs
    env_file:
      - /opt/mudra/.env
    environment:
      - DATABASE_URL=sqlite:////app/data/mudra.db
      - PYTHONUNBUFFERED=1
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - mudra-net

networks:
  mudra-net:
    driver: bridge
```

---

## Deployment Steps

### Step 1: Build Docker Image

```bash
cd /opt/mudra

# Build the image (takes 3-5 minutes)
docker-compose build

# Verify the build succeeded
docker images | grep mudra
```

### Step 2: Start the Application

```bash
# Start in detached mode
docker-compose up -d

# Check if containers are running
docker-compose ps

# Expected output:
# NAME       IMAGE       STATUS              PORTS
# mudra-app  mudra:latest Up 10 seconds    0.0.0.0:8000->8000/tcp
```

### Step 3: Verify Backend is Running

```bash
# Check logs
docker-compose logs -f mudra

# Test health endpoint (should return {"status":"ok"})
curl http://localhost:8000/health

# Check API endpoint
curl http://localhost:8000/api/trades
```

### Step 4: Monitor Container Health

```bash
# View container status
docker stats mudra-app

# Check logs for errors
docker-compose logs --tail=50 mudra
```

---

## Domain & SSL Setup

### Step 1: Point Domain to VPS IP

Using Hostinger's DNS management:

1. Go to **Hostinger Dashboard** → **Domains**
2. Select your domain
3. Go to **DNS Records**
4. Add/Update A record:
   - **Name:** @ (or leave blank)
   - **Type:** A
   - **Value:** Your VPS IP (e.g., 185.123.45.67)
   - **TTL:** 3600
5. Add CNAME for www (optional):
   - **Name:** www
   - **Type:** CNAME
   - **Value:** yourdomain.com
   - **TTL:** 3600

### Step 2: Verify DNS Propagation

```bash
# Wait 15-30 minutes for DNS to propagate, then test
nslookup yourdomain.com
dig yourdomain.com

# Expected output should show your VPS IP
```

### Step 3: Install SSL Certificate with Certbot

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Generate certificate (replace with your domain)
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Follow prompts:
# - Enter email
# - Agree to terms
# - Choose whether to share email with EFF (optional)

# Verify certificate was created
sudo ls -la /etc/letsencrypt/live/yourdomain.com/

# Certificate paths:
# /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/yourdomain.com/privkey.pem
```

### Step 4: Auto-Renew Certificate

```bash
# Enable auto-renewal (runs twice daily)
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Verify renewal is enabled
sudo systemctl status certbot.timer

# Test renewal (dry-run)
sudo certbot renew --dry-run
```

---

## Reverse Proxy Configuration

### Step 1: Install Nginx

```bash
sudo apt install -y nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

### Step 2: Create Nginx Configuration

```bash
# Create Nginx config for Mudra
sudo nano /etc/nginx/sites-available/mudra.conf
```

```nginx
# /etc/nginx/sites-available/mudra.conf

upstream mudra_backend {
    server localhost:8000;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name yourdomain.com www.yourdomain.com;

    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/mudra_access.log;
    error_log /var/log/nginx/mudra_error.log;

    # Client upload size limit
    client_max_body_size 10M;

    # Root location - proxy to backend (FastAPI + React frontend)
    location / {
        proxy_pass http://mudra_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        proxy_buffering off;
    }

    # API endpoints - explicit proxy
    location /api/ {
        proxy_pass http://mudra_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://mudra_backend;
        access_log off;
    }
}
```

### Step 3: Enable Nginx Configuration

```bash
# Create symlink to enable site
sudo ln -s /etc/nginx/sites-available/mudra.conf /etc/nginx/sites-enabled/

# Remove default site (optional)
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Expected output:
# nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
# nginx: configuration file /etc/nginx/nginx.conf test is successful

# Reload Nginx
sudo systemctl reload nginx

# Verify Nginx is running
sudo systemctl status nginx
```

### Step 4: Verify Setup

```bash
# Test via curl (should show HTML from React frontend)
curl -k https://yourdomain.com

# Test API endpoint
curl https://yourdomain.com/api/health

# Check Nginx logs
sudo tail -f /var/log/nginx/mudra_access.log
sudo tail -f /var/log/nginx/mudra_error.log
```

---

## Monitoring & Maintenance

### Daily Checks

```bash
# SSH into VPS
ssh root@your.vps.ip

# Check app is running
docker-compose -f /opt/mudra/docker-compose.yml ps

# Check recent logs
docker-compose -f /opt/mudra/docker-compose.yml logs --tail=20

# Check disk usage
df -h

# Check memory usage
free -h
```

### Weekly Maintenance

```bash
# 1. Backup database
sudo cp /opt/mudra/data/mudra.db /opt/mudra/backups/mudra_$(date +%Y%m%d_%H%M%S).db

# 2. Check SSL certificate expiry
sudo certbot certificates

# 3. Check for container restarts
docker-compose -f /opt/mudra/docker-compose.yml logs | grep "restart"

# 4. Clean up old logs (optional)
sudo journalctl --vacuum=30d
```

### Monthly Tasks

```bash
# Check for security updates
sudo apt update
sudo apt upgrade -y

# Rebuild Docker image (to get latest base OS patches)
cd /opt/mudra
docker-compose build --no-cache

# Restart containers with new image
docker-compose down
docker-compose up -d
```

### Setting Up Automated Backups

Create backup script at `/opt/mudra/backup.sh`:

```bash
#!/bin/bash
# Backup script for Mudra database

BACKUP_DIR="/opt/mudra/backups"
DB_PATH="/opt/mudra/data/mudra.db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/mudra_$TIMESTAMP.db"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Copy database
cp "$DB_PATH" "$BACKUP_FILE"

# Keep only last 7 days of backups
find "$BACKUP_DIR" -name "mudra_*.db" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE"
```

```bash
# Make script executable
chmod +x /opt/mudra/backup.sh

# Add to crontab (daily backup at 2 AM)
crontab -e

# Add this line:
# 0 2 * * * /opt/mudra/backup.sh
```

### Monitoring with Systemd

Create systemd service to manage docker-compose:

```bash
# Create service file
sudo nano /etc/systemd/system/mudra.service
```

```ini
[Unit]
Description=Mudra Trading App
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
WorkingDirectory=/opt/mudra
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

```bash
# Enable service
sudo systemctl enable mudra.service
sudo systemctl start mudra.service

# Check status
sudo systemctl status mudra.service
```

### Simple Uptime Monitoring

Free option: Use Healthchecks.io
1. Create account at https://healthchecks.io (free tier = 20 checks)
2. Create a new check for your health endpoint
3. Add to crontab to ping every 5 minutes:

```bash
# Get your unique check URL from healthchecks.io
HEALTHCHECK_URL="https://hc-ping.com/your-unique-id"

# Add to crontab:
# */5 * * * * curl -s "$HEALTHCHECK_URL" > /dev/null 2>&1
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs mudra

# Common issues:
# 1. Port 8000 already in use
#    Solution: Change port in docker-compose.yml

# 2. .env file missing
#    Solution: Create .env with required variables

# 3. Data directory not writable
#    Solution: sudo chown $USER:$USER /opt/mudra/data
```

### Database Lock Error

```bash
# SQLite sometimes locks if multiple processes access it
# Solution: Ensure only one container instance is running

docker-compose ps
# Should show only ONE mudra container

# If multiple, remove old ones:
docker-compose down
docker-compose up -d
```

### SSL Certificate Errors

```bash
# Check certificate validity
sudo openssl x509 -in /etc/letsencrypt/live/yourdomain.com/cert.pem -text -noout

# Force renewal (if needed)
sudo certbot renew --force-renewal

# Check Nginx is using correct paths
sudo cat /etc/nginx/sites-available/mudra.conf | grep ssl_certificate
```

### Nginx Proxy Issues

```bash
# Test Nginx config
sudo nginx -t

# Check if backend is running on :8000
curl http://localhost:8000/health

# View Nginx logs
sudo tail -f /var/log/nginx/mudra_error.log

# Reload Nginx
sudo systemctl reload nginx
```

### High CPU/Memory Usage

```bash
# Check which container is using resources
docker stats

# Increase VPS resources:
# 1. Go to Hostinger hPanel
# 2. Upgrade VPS plan (2GB → 4GB)
# 3. Automatic restart (usually)

# Or optimize app:
# - Check for infinite loops in code
# - Monitor trade execution logic
# - Check database query performance
```

### Database Backup/Restore

```bash
# Backup database manually
cp /opt/mudra/data/mudra.db /opt/mudra/data/mudra.db.backup

# Restore from backup (stops container first)
docker-compose down
cp /opt/mudra/data/mudra.db.backup /opt/mudra/data/mudra.db
docker-compose up -d
```

---

## Updating & Redeployment

### Deploying Code Changes

When you push new code to the repository:

```bash
# SSH into VPS
ssh root@your.vps.ip

# Go to app directory
cd /opt/mudra

# Pull latest code
git pull origin main

# Rebuild Docker image (takes 2-3 minutes)
docker-compose build

# Stop old container and start new one
docker-compose down
docker-compose up -d

# Verify new version is running
docker-compose logs --tail=20

# Test health endpoint
curl https://yourdomain.com/api/health
```

### Zero-Downtime Updates (Advanced)

To avoid brief downtime during redeploy:

```bash
# 1. Build new image
docker-compose build

# 2. Start second container with new image (different port)
docker-compose up -d --scale mudra=2

# 3. Update Nginx to route to both (load balance)
# 4. Stop old container
docker-compose down

# 5. Scale back to 1
docker-compose up -d --scale mudra=1
```

### Rollback to Previous Version

```bash
# Find previous commit
git log --oneline

# Checkout previous version
git checkout <commit-hash>

# Rebuild and restart
docker-compose build
docker-compose down
docker-compose up -d
```

---

## Deployment Checklist

Before going live:

- [ ] VPS provisioned (2GB RAM, Ubuntu 22.04)
- [ ] Docker & Docker Compose installed
- [ ] Application code cloned to `/opt/mudra`
- [ ] `.env` file created with API keys
- [ ] Docker image builds successfully
- [ ] Container starts and responds to health check
- [ ] Domain DNS A record points to VPS IP
- [ ] DNS propagated (verified with nslookup)
- [ ] SSL certificate issued (certbot)
- [ ] Nginx reverse proxy configured
- [ ] HTTPS works (curl https://yourdomain.com)
- [ ] API endpoints respond (curl https://yourdomain.com/api/health)
- [ ] React frontend loads in browser
- [ ] Database file created at `/opt/mudra/data/mudra.db`
- [ ] Auto-restart on failure enabled (docker restart: always)
- [ ] Backup script set up in crontab
- [ ] SSL auto-renewal enabled (certbot.timer)
- [ ] Monitoring enabled (systemd service or Healthchecks.io)

---

## Quick Reference Commands

```bash
# SSH into VPS
ssh root@your.vps.ip

# View application logs
docker-compose -f /opt/mudra/docker-compose.yml logs -f

# Restart application
docker-compose -f /opt/mudra/docker-compose.yml restart

# Check container status
docker-compose -f /opt/mudra/docker-compose.yml ps

# Check resource usage
docker stats

# View Nginx logs
sudo tail -f /var/log/nginx/mudra_error.log

# Test API endpoint
curl https://yourdomain.com/api/health

# Renew SSL certificate
sudo certbot renew

# View SSL expiry
sudo certbot certificates

# Backup database
cp /opt/mudra/data/mudra.db /opt/mudra/backups/mudra_$(date +%Y%m%d).db

# Check disk space
df -h

# Check memory
free -h

# Update system
sudo apt update && sudo apt upgrade -y
```

---

## Security Best Practices

1. **Never commit secrets:** Keep `.env` local, use `.gitignore`
2. **Restrict API keys:** In Binance/Zerodha dashboards, restrict by IP
3. **Enable firewall:** Only open ports 80, 443, and SSH (22)
4. **Regular updates:** Run `sudo apt upgrade` monthly
5. **Monitor logs:** Check `/var/log/nginx/` for suspicious activity
6. **Database permissions:** Use read-only API for non-trading endpoints
7. **CORS headers:** Already configured in FastAPI (check if needed for production)
8. **HTTPS only:** Nginx redirects all HTTP to HTTPS

---

## Support & Resources

- **Hostinger VPS Docs:** https://www.hostinger.com/vps/help
- **Docker Compose Docs:** https://docs.docker.com/compose/
- **Certbot Docs:** https://certbot.eff.org/docs/
- **Nginx Docs:** https://nginx.org/en/docs/
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **SQLite Docs:** https://www.sqlite.org/docs.html

---

## Cost Summary

| Item | Cost/Month | Annual |
|------|-----------|--------|
| Hostinger VPS 2GB | $12-15 | $144-180 |
| Domain | $0-15 | $0-180 |
| SSL | $0 | $0 |
| Database | $0 | $0 |
| **Total** | **$12-30** | **$144-360** |

**ROI:** Deploy in 2-3 hours, run for pennies/month. Excellent for personal trading.

---

## Next Steps

1. Purchase VPS on Hostinger
2. Follow **VPS Setup** section (Step 1-5)
3. Follow **Environment Configuration** (Step 1-2)
4. Follow **Deployment Steps** (Step 1-4)
5. Follow **Domain & SSL Setup** (Step 1-4)
6. Follow **Reverse Proxy Configuration** (Step 1-4)
7. Test application at https://yourdomain.com
8. Set up monitoring and backups

---

**Questions?** Refer to the relevant section or check the **Troubleshooting** guide.
