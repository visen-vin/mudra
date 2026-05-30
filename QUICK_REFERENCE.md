# Mudra VPS - Quick Reference Card

Keep this handy for daily operations.

---

## Connection

```bash
# SSH into VPS
ssh root@<YOUR_VPS_IP>

# Go to app directory
cd /opt/mudra
```

---

## Container Management

```bash
# Status
docker-compose ps

# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart mudra-app

# Rebuild (after code changes)
docker-compose build
docker-compose down
docker-compose up -d
```

---

## Logs

```bash
# Follow logs (real-time)
docker-compose logs -f mudra-app

# Last 50 lines
docker-compose logs --tail=50

# Errors only
docker-compose logs | grep -i error

# Nginx errors
sudo tail -f /var/log/nginx/mudra_error.log

# Nginx access
sudo tail -f /var/log/nginx/mudra_access.log

# Monitor script logs
tail -f /var/log/mudra/monitor.log
```

---

## Health Checks

```bash
# API health
curl https://yourdomain.com/api/health

# Local API
curl http://localhost:8000/health

# Frontend
curl https://yourdomain.com

# Check container
docker-compose ps (should show "Up")

# Docker stats
docker stats mudra-app
```

---

## Database

```bash
# Backup manually
cp /opt/mudra/data/mudra.db /opt/mudra/backups/mudra_$(date +%Y%m%d_%H%M%S).db

# List backups
ls -lh /opt/mudra/backups/

# Restore from backup
docker-compose down
cp /opt/mudra/backups/mudra_YYYYMMDD_HHMMSS.db /opt/mudra/data/mudra.db
docker-compose up -d

# Direct SQLite access
sqlite3 /opt/mudra/data/mudra.db

# SQLite query example
sqlite3 /opt/mudra/data/mudra.db "SELECT COUNT(*) FROM trades;"
```

---

## System Status

```bash
# Disk usage
df -h

# Memory usage
free -h

# CPU usage
top -b -n 1 | head -20

# VPS uptime
uptime

# Running processes
ps aux | grep mudra

# Open ports
sudo ss -tlnp | grep -E "80|443|8000"
```

---

## Nginx/SSL

```bash
# Nginx status
sudo systemctl status nginx

# Restart Nginx
sudo systemctl reload nginx

# Nginx test config
sudo nginx -t

# SSL certificate info
sudo certbot certificates

# Force SSL renewal
sudo certbot renew --force-renewal

# Check SSL expiry
echo | openssl s_client -servername yourdomain.com -connect yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates
```

---

## Deployment

```bash
# Deploy new code
cd /opt/mudra
git pull origin main
docker-compose build
docker-compose down
docker-compose up -d

# Or use deploy script
/opt/mudra/scripts/deploy.sh production

# View deployment logs
docker-compose logs --tail=50
```

---

## Backup

```bash
# Manual backup
/opt/mudra/scripts/backup.sh

# Verify backups exist
ls -lh /opt/mudra/backups/

# Find old backups
find /opt/mudra/backups -name "*.db" -mtime +7
```

---

## Monitoring

```bash
# Run monitoring check
/opt/mudra/scripts/monitor.sh

# View monitor logs
tail -f /var/log/mudra/monitor.log

# Check cron jobs
crontab -l

# View system cron logs
sudo journalctl -u cron | tail -20
```

---

## Environment & Secrets

```bash
# View .env (show only keys, not values)
cat /opt/mudra/.env | cut -d= -f1

# Update .env (DO NOT commit to git)
nano /opt/mudra/.env

# Verify .env is not tracked
git status
git log --all --full-history -- .env

# Reload environment (restart container)
docker-compose restart mudra-app
```

---

## Emergency Procedures

### Container Crashed
```bash
# Check what happened
docker-compose logs --tail=50

# Restart
docker-compose restart mudra-app

# If restart doesn't help, full restart
docker-compose down
docker-compose up -d

# If still broken, rebuild
docker-compose build --no-cache
docker-compose up -d
```

### Disk Full
```bash
# Check space
df -h

# Find large files
du -sh /opt/mudra/*

# Clean Docker (WARNING: removes unused images)
docker system prune -a

# Remove old backups
find /opt/mudra/backups -name "*.db" -mtime +30 -delete
```

### Database Corrupted
```bash
# Restore from latest backup
docker-compose down
ls -lh /opt/mudra/backups/ | tail -1
cp /opt/mudra/backups/mudra_LATEST.db /opt/mudra/data/mudra.db
docker-compose up -d
```

### High Memory Usage
```bash
# Check what's using memory
docker stats

# Restart container
docker-compose restart mudra-app

# Check for memory leaks
docker-compose logs | grep -i "memory\|leak"

# As last resort, reboot VPS
sudo reboot
```

---

## Common Issues & Fixes

| Issue | Command | Notes |
|-------|---------|-------|
| API returns 502 | `docker-compose logs \| tail -20` | Backend crashed, check logs |
| Slow response | `docker stats` | Check CPU/memory usage |
| Port 8000 in use | Change in docker-compose.yml | Rebuild and restart |
| DNS not resolving | `nslookup yourdomain.com` | Wait 30 min or check DNS records |
| SSL certificate error | `sudo certbot certificates` | Check if expired or misconfigured |
| Nginx 404 errors | `sudo tail /var/log/nginx/mudra_error.log` | Check backend is running |
| Database locked | `docker-compose restart mudra-app` | SQLite file locked, restart resolves |
| Can't SSH | Reboot VPS in hPanel | SSH daemon may have crashed |

---

## File Locations

```
/opt/mudra/                  # Application root
├── Dockerfile              # Docker build file
├── docker-compose.yml      # Dev compose
├── docker-compose.prod.yml # Production compose
├── .env                    # Environment variables (DO NOT COMMIT)
├── requirements.txt        # Python dependencies
├── backend/                # FastAPI backend code
├── frontend/               # React frontend code
├── data/                   # SQLite database
│   └── mudra.db            # Database file (auto-created)
├── backups/                # Database backups
├── logs/                   # Application logs
└── scripts/                # Helper scripts
    ├── deploy.sh           # Deployment script
    ├── backup.sh           # Backup script
    ├── monitor.sh          # Health check script
    └── logs.sh             # Log viewer script

/etc/nginx/sites-available/mudra.conf    # Nginx configuration
/etc/letsencrypt/live/yourdomain.com/    # SSL certificates
/var/log/nginx/                          # Nginx logs
/var/log/mudra/                          # Monitor logs
```

---

## Useful URLs

```
Frontend:       https://yourdomain.com
API Base:       https://yourdomain.com/api
Health Check:   https://yourdomain.com/api/health
Trades:         https://yourdomain.com/api/trades
```

---

## Hostinger Tools

```bash
# Hostinger hPanel (web interface)
https://hpanel.hostinger.com/

# Access from command line (if needed)
# SSH directly to VPS using IP address
ssh root@<YOUR_VPS_IP>
```

---

## Support Resources

- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **SQLite Guide:** https://www.sqlite.org/cli.html
- **Docker Docs:** https://docs.docker.com/
- **Nginx Guide:** https://nginx.org/en/docs/
- **Certbot Help:** https://certbot.eff.org/

---

## Key Metrics to Monitor

```bash
# CPU usage
top -bn1 | head -20

# Memory
free -h && docker stats

# Disk
df -h && du -sh /opt/mudra/*

# Network (if needed)
netstat -tuln | grep -E "80|443|8000"

# Database size
du -h /opt/mudra/data/mudra.db

# Backup age
ls -lh /opt/mudra/backups/ | tail -3
```

---

## Before Committing Code

```bash
# Always check .env not included
git status | grep .env

# Check no secrets in code
git diff | grep -i "api_key\|secret\|token\|password"

# If added by mistake, remove from git history
git rm --cached .env
git commit --amend
```

---

## Deployment Timeline

1. **Code push to main:** 0 min
2. **SSH to VPS:** 1 min
3. **Git pull:** 1-2 min
4. **Docker build:** 3-5 min (depends on image size)
5. **Container restart:** 10-15 sec
6. **Health check:** < 1 min
7. **Total:** 5-10 minutes

**During deployment:** Users may see brief 502 errors while old container stops and new starts.

---

**Last Updated:** 2026-05-30  
**Version:** 1.0  
**For:** Mudra Trading App on Hostinger VPS
