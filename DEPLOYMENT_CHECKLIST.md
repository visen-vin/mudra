# Mudra Deployment Checklist

**Deployment Date:** ________  
**Deployed By:** ________  
**VPS IP:** ________  
**Domain:** ________  

---

## Phase 1: VPS Provisioning (Day 1 - 30 minutes)

### Hostinger Account Setup
- [ ] Create Hostinger account (or login to existing)
- [ ] Verify email address
- [ ] Add payment method

### VPS Purchase
- [ ] Navigate to Hostinger VPS section
- [ ] Select plan: **2GB RAM, 1 vCPU, 50GB SSD**
- [ ] Operating System: **Ubuntu 22.04 LTS**
- [ ] Data Center: **Closest to your location**
- [ ] Complete payment
- [ ] Record VPS IP: ________________

### Initial SSH Access
- [ ] Receive VPS credentials email
- [ ] SSH into VPS: `ssh root@<IP>`
- [ ] Change root password (optional but recommended)
- [ ] [ ] Update system: `sudo apt update && sudo apt upgrade -y`

---

## Phase 2: Docker Setup (Day 1 - 1 hour)

### Install Docker
- [ ] Install Docker: `sudo apt install -y docker.io`
- [ ] Install Docker Compose: `curl -L ... | sudo tee /usr/local/bin/docker-compose`
- [ ] Make executable: `sudo chmod +x /usr/local/bin/docker-compose`
- [ ] Verify: `docker --version` and `docker-compose --version`
- [ ] Enable Docker service: `sudo systemctl enable docker && sudo systemctl start docker`

### Create App Directory
- [ ] Create directory: `sudo mkdir -p /opt/mudra`
- [ ] Change ownership: `sudo chown $USER:$USER /opt/mudra`
- [ ] Create data dir: `mkdir -p /opt/mudra/data /opt/mudra/logs /opt/mudra/backups`

### Clone Repository
- [ ] Clone repo: `cd /opt/mudra && git clone <repo> .`
- [ ] Verify files: `ls -la /opt/mudra/ | grep -E "Dockerfile|docker-compose|requirements"`

---

## Phase 3: Environment Configuration (Day 1 - 15 minutes)

### Create .env File
- [ ] Copy template: `cp .env.example .env`
- [ ] Edit .env: `nano /opt/mudra/.env`
- [ ] Add Binance API Key: `BINANCE_API_KEY=...`
- [ ] Add Binance API Secret: `BINANCE_API_SECRET=...`
- [ ] Add Zerodha API Key: `ZERODHA_API_KEY=...`
- [ ] Add Zerodha Session Token: `ZERODHA_SESSION_TOKEN=...`
- [ ] Set mode to paper: `DEFAULT_MODE=paper`
- [ ] Set log level: `LOG_LEVEL=INFO`
- [ ] Verify .env is NOT in git: `cat .gitignore | grep ".env"`

### Verify Environment
- [ ] Check .env exists: `ls -la /opt/mudra/.env`
- [ ] Check file permissions: `stat /opt/mudra/.env` (should be readable)
- [ ] Check .env syntax: `cat /opt/mudra/.env`

---

## Phase 4: Docker Build & Test (Day 1 - 30 minutes)

### Build Docker Image
- [ ] Navigate to app dir: `cd /opt/mudra`
- [ ] Build image: `docker-compose build` (takes 3-5 minutes)
- [ ] Verify build: `docker images | grep mudra`
- [ ] Record image ID: ________________

### Start Container
- [ ] Start app: `docker-compose up -d`
- [ ] Check status: `docker-compose ps` (should show "Up")
- [ ] Wait 10 seconds for startup

### Test Backend
- [ ] Test health endpoint: `curl http://localhost:8000/health`
- [ ] Expected response: `{"status":"ok"}`
- [ ] Test API endpoint: `curl http://localhost:8000/api/trades`
- [ ] Check logs: `docker-compose logs --tail=20`
- [ ] Look for errors: Any "error" or "exception" messages?

### Verify Database
- [ ] Check database created: `ls -la /opt/mudra/data/mudra.db`
- [ ] Check size: `du -h /opt/mudra/data/mudra.db`

---

## Phase 5: Domain Setup (Day 1-2 - 30 minutes + 15min wait)

### Register/Transfer Domain
- [ ] Domain already owned? Yes / No
- [ ] Domain registrar: ________________
- [ ] Domain name: ________________
- [ ] Registrar supports custom DNS? Yes / No

### Point Domain to VPS
- [ ] Go to domain registrar dashboard
- [ ] Find DNS Records section
- [ ] Add A record:
  - [ ] Name: `@` or leave blank
  - [ ] Type: `A`
  - [ ] Value: VPS IP (________________)
  - [ ] TTL: `3600`
- [ ] Add CNAME for www (optional):
  - [ ] Name: `www`
  - [ ] Type: `CNAME`
  - [ ] Value: `yourdomain.com`
  - [ ] TTL: `3600`
- [ ] Save DNS records

### Verify DNS Propagation
- [ ] Wait 15-30 minutes for DNS to propagate
- [ ] Test DNS: `nslookup yourdomain.com`
- [ ] Expected output includes VPS IP
- [ ] Test with dig: `dig yourdomain.com`
- [ ] Verify A record: `dig yourdomain.com +short` (should show IP)

---

## Phase 6: SSL Certificate (Day 2 - 20 minutes)

### Install Certbot
- [ ] Install certbot: `sudo apt install -y certbot python3-certbot-nginx`
- [ ] Verify installation: `certbot --version`

### Generate SSL Certificate
- [ ] Stop Nginx if running: `sudo systemctl stop nginx`
- [ ] Generate cert: `sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com`
- [ ] Enter email when prompted
- [ ] Agree to terms (A)
- [ ] Share email? (Y/N) - your preference

### Verify Certificate
- [ ] Check certificate created: `sudo ls -la /etc/letsencrypt/live/yourdomain.com/`
- [ ] Verify files exist:
  - [ ] `fullchain.pem` (public certificate)
  - [ ] `privkey.pem` (private key)
- [ ] Check expiry: `sudo certbot certificates`
- [ ] Record expiry date: ________________

### Auto-Renewal Setup
- [ ] Enable certbot timer: `sudo systemctl enable certbot.timer`
- [ ] Start timer: `sudo systemctl start certbot.timer`
- [ ] Verify enabled: `sudo systemctl status certbot.timer`
- [ ] Test renewal (dry-run): `sudo certbot renew --dry-run`

---

## Phase 7: Nginx Reverse Proxy (Day 2 - 30 minutes)

### Install Nginx
- [ ] Install nginx: `sudo apt install -y nginx`
- [ ] Verify installation: `nginx -v`
- [ ] Enable auto-start: `sudo systemctl enable nginx`

### Create Nginx Configuration
- [ ] Edit nginx config: `sudo nano /etc/nginx/sites-available/mudra.conf`
- [ ] Copy content from DEPLOYMENT_GUIDE.md "Reverse Proxy Configuration" section
- [ ] Replace `yourdomain.com` with actual domain (3 places)
- [ ] Save file (Ctrl+X, Y, Enter)

### Enable Nginx Site
- [ ] Create symlink: `sudo ln -s /etc/nginx/sites-available/mudra.conf /etc/nginx/sites-enabled/`
- [ ] Verify symlink: `ls -la /etc/nginx/sites-enabled/mudra.conf`
- [ ] Remove default site: `sudo rm /etc/nginx/sites-enabled/default`

### Test Nginx Configuration
- [ ] Test syntax: `sudo nginx -t`
- [ ] Expected: "syntax is ok" and "configuration file test is successful"
- [ ] If errors, review file: `sudo cat /etc/nginx/sites-available/mudra.conf | head -20`

### Start Nginx
- [ ] Reload nginx: `sudo systemctl reload nginx`
- [ ] Check status: `sudo systemctl status nginx`
- [ ] Should show "active (running)"

---

## Phase 8: Test HTTPS & Frontend (Day 2 - 15 minutes)

### Test HTTP Redirect
- [ ] Test redirect: `curl -I http://yourdomain.com`
- [ ] Should show: `301 Moved Permanently` to HTTPS

### Test HTTPS
- [ ] Test HTTPS: `curl -I https://yourdomain.com`
- [ ] Check response: Should show `200 OK` and HTML content
- [ ] Test API: `curl https://yourdomain.com/api/health`
- [ ] Expected response: `{"status":"ok"}`

### Test in Browser
- [ ] Open browser: https://yourdomain.com
- [ ] Check for SSL certificate:
  - [ ] Click lock icon (top left)
  - [ ] Verify certificate is from Let's Encrypt
  - [ ] Check expiry date matches certbot output
- [ ] Check frontend loads:
  - [ ] Page title shows "Mudra Trading"
  - [ ] No CORS errors in console (F12 → Console)
  - [ ] No network errors (F12 → Network)

### Test API Functionality
- [ ] Open browser DevTools (F12)
- [ ] Go to Network tab
- [ ] Try API endpoint: https://yourdomain.com/api/trades
- [ ] Should show successful API response
- [ ] No 401/403 errors

---

## Phase 9: System Configuration (Day 2 - 30 minutes)

### Create Backup Script
- [ ] Copy backup script: Already in `/opt/mudra/scripts/backup.sh`
- [ ] Make executable: `chmod +x /opt/mudra/scripts/backup.sh`
- [ ] Test backup: `/opt/mudra/scripts/backup.sh`
- [ ] Verify backup created: `ls -la /opt/mudra/backups/`

### Setup Automated Backups (Crontab)
- [ ] Edit crontab: `crontab -e`
- [ ] Add line: `0 2 * * * /opt/mudra/scripts/backup.sh` (daily 2 AM)
- [ ] Verify added: `crontab -l | grep backup.sh`

### Setup Monitoring Script
- [ ] Copy monitor script: Already in `/opt/mudra/scripts/monitor.sh`
- [ ] Make executable: `chmod +x /opt/mudra/scripts/monitor.sh`
- [ ] Test monitor: `/opt/mudra/scripts/monitor.sh`
- [ ] Create log directory: `sudo mkdir -p /var/log/mudra`
- [ ] Set permissions: `sudo chown $USER:$USER /var/log/mudra`

### Setup Monitoring Cron (Optional)
- [ ] Edit crontab: `crontab -e`
- [ ] Add line: `*/5 * * * * /opt/mudra/scripts/monitor.sh` (every 5 minutes)
- [ ] Verify: `crontab -l | grep monitor.sh`

### Setup Systemd Service (Optional but Recommended)
- [ ] Create service: `sudo nano /etc/systemd/system/mudra.service`
- [ ] Copy content from DEPLOYMENT_GUIDE.md "Monitoring with Systemd" section
- [ ] Save file
- [ ] Enable service: `sudo systemctl enable mudra.service`
- [ ] Start service: `sudo systemctl start mudra.service`
- [ ] Verify: `sudo systemctl status mudra.service`

---

## Phase 10: Final Verification (Day 2 - 15 minutes)

### Health Checks
- [ ] Container running: `docker-compose ps`
- [ ] Database file exists: `ls -la /opt/mudra/data/mudra.db`
- [ ] Nginx running: `sudo systemctl status nginx`
- [ ] Certbot timer enabled: `sudo systemctl status certbot.timer`
- [ ] Health endpoint working: `curl https://yourdomain.com/api/health`

### Security Checks
- [ ] .env file not in git: `git log --all --full-history -- .env`
- [ ] No API keys in git history: `git log --all --grep="BINANCE\|ZERODHA"`
- [ ] SSH key installed for remote access? (if applicable)
- [ ] Firewall rules configured? (check with host provider)

### Database Tests
- [ ] Database accessible: `sqlite3 /opt/mudra/data/mudra.db "SELECT count(*) FROM sqlite_master;"`
- [ ] Can create tables: Application startup succeeded
- [ ] Backup exists: `ls -la /opt/mudra/backups/ | wc -l` (should be > 0)

### Performance Check
- [ ] Memory usage: `free -h` (should be < 1.5GB)
- [ ] Disk usage: `df -h /opt/mudra` (should be < 50%)
- [ ] Container stats: `docker stats mudra-app`

### Logs Review
- [ ] Application logs clean: `docker-compose logs --tail=20 | grep -i error` (should be empty or warnings only)
- [ ] Nginx logs clean: `sudo tail -20 /var/log/nginx/mudra_error.log` (should be empty)

---

## Phase 11: Deployment Handoff (Day 2)

### Documentation
- [ ] DEPLOYMENT_GUIDE.md reviewed
- [ ] Quick reference commands tested
- [ ] Troubleshooting section reviewed

### Team Notification
- [ ] Notify team of deployment
- [ ] Share domain: ________________
- [ ] Share important endpoints:
  - [ ] Frontend: `https://yourdomain.com`
  - [ ] API: `https://yourdomain.com/api/`
  - [ ] Health: `https://yourdomain.com/api/health`

### Monitoring Setup
- [ ] Healthchecks.io account created? (optional)
- [ ] Monitoring webhook configured? (if applicable)
- [ ] Team alerted to uptime dashboard? (if applicable)

### Post-Deployment Tasks
- [ ] Set calendar reminder for SSL renewal (day 85 after issue date)
- [ ] Document any custom configuration made
- [ ] Create runbook for team

---

## Troubleshooting During Deployment

### If Container Won't Start
- [ ] Check logs: `docker-compose logs mudra`
- [ ] Common issue: Port 8000 in use
- [ ] Solution: Change port in docker-compose.yml, rebuild

### If DNS Doesn't Resolve
- [ ] Wait 30 minutes (propagation delay)
- [ ] Verify A record in registrar dashboard
- [ ] Try flush DNS: `sudo systemctl restart systemd-resolved`
- [ ] Test again: `nslookup yourdomain.com`

### If SSL Certificate Fails
- [ ] Ensure DNS is pointing to VPS
- [ ] Ensure port 80 is accessible: `curl http://yourdomain.com`
- [ ] Check Nginx not blocking port 80
- [ ] Try again: `sudo certbot certonly --standalone -d yourdomain.com`

### If API Returns 502 Bad Gateway
- [ ] Backend not running: `docker-compose ps`
- [ ] Container crashed: `docker-compose logs`
- [ ] Port 8000 not accessible: `curl http://localhost:8000/health`
- [ ] Restart: `docker-compose down && docker-compose up -d`

---

## Post-Deployment Maintenance

### Weekly Tasks
- [ ] Check backup exists: `ls -la /opt/mudra/backups/ | head -3`
- [ ] Review error logs: `docker-compose logs | grep -i error`
- [ ] Verify SSL renewal (should happen automatically)

### Monthly Tasks
- [ ] System updates: `sudo apt update && sudo apt upgrade -y`
- [ ] Review disk usage: `df -h`
- [ ] Test backup restore process (manually once)
- [ ] Check for container memory leaks: `docker stats`

### Quarterly Tasks
- [ ] Review security settings
- [ ] Update dependencies: `docker-compose build --no-cache`
- [ ] Plan capacity upgrades if needed

---

## Deployment Summary

**Deployment Completed:** ________  
**Total Setup Time:** ________ hours  
**Issues Encountered:** 
```
[None / List here]
```

**Notes:**
```
[Add any important notes here]
```

**Verified By:** ________________ **Date:** ________

---

## Quick Links

- **Hostinger Dashboard:** https://hpanel.hostinger.com/
- **Domain DNS Management:** [Your registrar dashboard]
- **SSL Certificate Status:** https://www.ssllabs.com/ssltest/analyze.html?d=yourdomain.com
- **Deployment Guide:** See DEPLOYMENT_GUIDE.md
- **Application Health:** https://yourdomain.com/api/health
- **Application Frontend:** https://yourdomain.com/

---

**Checklist completed successfully!** Your Mudra trading app is now deployed and running on Hostinger VPS.
