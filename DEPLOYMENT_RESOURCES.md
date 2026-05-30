# Mudra Deployment - Resource Index

**Quick Navigation Guide for Hostinger VPS Deployment**

---

## 📋 Documentation Files

### Core Deployment Guides

1. **DEPLOYMENT_GUIDE.md** (70 KB) — START HERE
   - **Purpose:** Complete step-by-step deployment instructions
   - **Content:**
     - 11 deployment phases (VPS setup → monitoring)
     - Code snippets for every step
     - Detailed configuration examples
     - Troubleshooting section with solutions
   - **Audience:** First-time deployers
   - **Time to Read:** 45 minutes
   - **When to Use:** During actual deployment

2. **DEPLOYMENT_CHECKLIST.md** (25 KB) — VERIFICATION
   - **Purpose:** Interactive checklist for deployment phases
   - **Content:**
     - 11 phases with checkboxes
     - Verification steps for each phase
     - Post-deployment maintenance schedule
     - Testing procedures
   - **Audience:** Project managers, verification
   - **Time to Use:** 2-3 hours (during deployment)
   - **When to Use:** Running through deployment, verifying completion

3. **DEPLOYMENT_SUMMARY.md** (20 KB) — OVERVIEW
   - **Purpose:** Architecture decision & cost analysis
   - **Content:**
     - Why single VPS (vs other options)
     - Cost breakdown and upgrade path
     - Risk management and mitigations
     - Timeline and resource requirements
   - **Audience:** Decision makers, project leads
   - **Time to Read:** 30 minutes
   - **When to Use:** Before purchasing VPS, understanding costs

4. **ARCHITECTURE.md** (25 KB) — VISUAL REFERENCE
   - **Purpose:** Visual architecture diagrams and data flow
   - **Content:**
     - High-level architecture diagrams (ASCII art)
     - Container architecture details
     - Directory structure on VPS
     - Networking and port mapping
     - Database schema
     - Monitoring & observability
   - **Audience:** Developers, architects, visual learners
   - **Time to Read:** 30 minutes
   - **When to Use:** Understanding system design, debugging network issues

5. **QUICK_REFERENCE.md** (15 KB) — DAILY OPERATIONS
   - **Purpose:** Commands and procedures for daily/weekly tasks
   - **Content:**
     - Connection commands
     - Container management shortcuts
     - Log viewing commands
     - Database operations
     - Monitoring and health checks
     - Emergency procedures
     - Common issues & fixes
   - **Audience:** Operators, DevOps
   - **Time to Reference:** 5-30 seconds per command
   - **When to Use:** Daily operations, troubleshooting, logging

### This File
6. **DEPLOYMENT_RESOURCES.md** (This file)
   - **Purpose:** Index and navigation guide
   - **Content:** What to read and when
   - **Audience:** Everyone
   - **Time to Read:** 15 minutes

---

## 🛠️ Configuration Files

### Docker Compose Files

1. **docker-compose.yml** (Existing)
   - **Purpose:** Local development compose file
   - **Status:** ✓ Already in repository
   - **Use:** Local testing only, do not use on VPS

2. **docker-compose.prod.yml** (New)
   - **Purpose:** Production deployment on VPS
   - **Location:** `/opt/mudra/docker-compose.prod.yml`
   - **Features:**
     - Volume persistence for data
     - Health checks enabled
     - Auto-restart on failure
     - Logging configured
     - Resource limits (commented out, enable if needed)
   - **Usage:** `docker-compose -f docker-compose.prod.yml up -d`
   - **Key Changes:**
     - Uses volume mounts (not host mounts)
     - Restart policy: always
     - Health check configured
     - JSON logging driver

### Nginx Configuration

See **DEPLOYMENT_GUIDE.md** → "Reverse Proxy Configuration" section
- **File Location:** `/etc/nginx/sites-available/mudra.conf`
- **Features:**
  - HTTP → HTTPS redirect
  - SSL/TLS configuration
  - Reverse proxy to FastAPI
  - Security headers (HSTS, X-Frame-Options, etc.)
  - Compression (gzip)
  - Logging configuration
- **Customization:** Replace `yourdomain.com` in 3 places

### Systemd Service

See **DEPLOYMENT_GUIDE.md** → "Monitoring with Systemd" section
- **File Location:** `/etc/systemd/system/mudra.service`
- **Purpose:** Auto-start Docker Compose on VPS boot
- **Features:**
  - Depends on docker.service
  - Starts/stops docker-compose
  - Auto-restart on failure
  - Logging to journalctl

### SSL Certificate

- **Source:** Let's Encrypt (free)
- **Tool:** Certbot (certbot.eff.org)
- **Location:** `/etc/letsencrypt/live/yourdomain.com/`
- **Files:**
  - `fullchain.pem` (public certificate)
  - `privkey.pem` (private key)
- **Auto-Renewal:** Via systemd timer (certbot.timer)
- **Renewal Check:** `sudo certbot certificates`

---

## 📜 Scripts

All scripts are in `/opt/mudra/scripts/` and are **already created**.

### 1. **deploy.sh** (Deployment Automation)
```bash
Usage: ./scripts/deploy.sh production
Time: 3-5 minutes
Features:
  ✓ Pre-deployment checks
  ✓ Database backup before deploy
  ✓ Git pull latest code
  ✓ Docker build
  ✓ Container restart
  ✓ Health check validation
  ✓ Colored output
```

### 2. **backup.sh** (Database Backup)
```bash
Usage: ./scripts/backup.sh
Time: < 1 second
Features:
  ✓ Creates timestamped backup
  ✓ Retention policy (30 days)
  ✓ Auto-cleanup of old backups
  ✓ Logging with timestamps
  ✓ Error handling
Cron: 0 2 * * * /opt/mudra/scripts/backup.sh
```

### 3. **monitor.sh** (Health Checks)
```bash
Usage: ./scripts/monitor.sh
Time: 5 seconds
Features:
  ✓ Container status check
  ✓ API health check
  ✓ Disk usage monitoring
  ✓ Memory usage monitoring
  ✓ Auto-restart on failure
  ✓ Optional webhook integration
Cron: */5 * * * * /opt/mudra/scripts/monitor.sh
```

### 4. **logs.sh** (Log Viewer)
```bash
Usage: ./scripts/logs.sh [command]
Commands:
  follow, f       - Follow app logs (real-time)
  tail, t         - Last 50 lines
  errors, e       - Errors only
  nginx, n        - Nginx error logs
  access, a       - Nginx access logs
  monitor, m      - Monitor script logs
```

---

## 📚 Reading Guide by Role

### For First-Time Deployers
**Time Commitment:** 3-4 hours total
1. Read DEPLOYMENT_SUMMARY.md (30 min) — Understand architecture
2. Read DEPLOYMENT_GUIDE.md (45 min) — Understand each step
3. Skim ARCHITECTURE.md (15 min) — Visual understanding
4. Follow DEPLOYMENT_CHECKLIST.md (2-3 hours) — Actual deployment
5. Keep QUICK_REFERENCE.md open — Reference during setup

### For DevOps/Technical Review
**Time Commitment:** 1 hour
1. Read ARCHITECTURE.md (30 min) — System design
2. Review docker-compose.prod.yml (10 min) — Container config
3. Review scripts/ directory (10 min) — Automation
4. Skim DEPLOYMENT_GUIDE.md (10 min) — Procedures

### For Project Managers
**Time Commitment:** 30 minutes
1. Read DEPLOYMENT_SUMMARY.md (30 min) — Cost, timeline, risks

### For Daily Operations
**Time Commitment:** 5-30 seconds per task
1. Use QUICK_REFERENCE.md — Commands lookup
2. Use DEPLOYMENT_CHECKLIST.md → "Weekly Maintenance" — Tasks schedule
3. Use scripts/ directory — Automate common tasks

### For Troubleshooting
**Time Commitment:** 5-15 minutes
1. Search QUICK_REFERENCE.md → "Common Issues & Fixes"
2. Search DEPLOYMENT_GUIDE.md → "Troubleshooting"
3. Check logs: `./scripts/logs.sh`
4. Run health check: `./scripts/monitor.sh`

---

## 🔄 Implementation Timeline

### Day 1 (2-3 hours)

**Reading & Planning** (30 min)
- [ ] Read DEPLOYMENT_SUMMARY.md
- [ ] Read ARCHITECTURE.md
- [ ] Review costs and timeline

**VPS Purchase** (15 min)
- [ ] Go to Hostinger
- [ ] Purchase 2GB VPS (Ubuntu 22.04)
- [ ] Record VPS IP

**VPS Setup** (1 hour)
- [ ] SSH into VPS
- [ ] Follow DEPLOYMENT_GUIDE.md → Phase 1-4
- [ ] Install Docker, clone code
- [ ] Create .env file
- [ ] Build and test locally

### Day 1-2 (30 min + DNS wait)

**Domain Setup** (30 min + wait)
- [ ] Follow DEPLOYMENT_GUIDE.md → Phase 5 (Domain & SSL)
- [ ] Point domain to VPS
- [ ] Wait 15-30 minutes for DNS
- [ ] Generate SSL certificate

### Day 2 (1 hour)

**Production Setup** (1 hour)
- [ ] Follow DEPLOYMENT_GUIDE.md → Phase 6-7
- [ ] Install Nginx
- [ ] Configure reverse proxy
- [ ] Test HTTPS access
- [ ] Setup backups & monitoring
- [ ] Run full checklist

---

## 📋 Essential Checklists

### Before Deployment
- [ ] Read DEPLOYMENT_SUMMARY.md
- [ ] Read DEPLOYMENT_GUIDE.md Phases 1-3
- [ ] VPS purchased and accessible
- [ ] Domain ready
- [ ] API keys obtained (Binance, Zerodha)

### During Deployment
- [ ] Follow DEPLOYMENT_CHECKLIST.md step-by-step
- [ ] Keep QUICK_REFERENCE.md nearby
- [ ] Keep DEPLOYMENT_GUIDE.md open
- [ ] Note any issues encountered

### After Deployment
- [ ] Run full verification checklist
- [ ] Test all endpoints
- [ ] Test backup/restore
- [ ] Monitor logs for 24 hours
- [ ] Document any customizations

### Weekly
- [ ] Check backups exist
- [ ] Review error logs
- [ ] Verify health checks passing

### Monthly
- [ ] Run `sudo apt upgrade`
- [ ] Review performance metrics
- [ ] Test backup restore

---

## 🔗 External Resources

### Required Tools
- **Docker:** https://docs.docker.com/install/
- **Docker Compose:** https://docs.docker.com/compose/install/
- **Certbot:** https://certbot.eff.org/instructions/
- **Nginx:** https://nginx.org/en/docs/

### Framework Documentation
- **FastAPI:** https://fastapi.tiangolo.com/
- **React:** https://react.dev/
- **SQLAlchemy:** https://docs.sqlalchemy.org/
- **SQLite:** https://www.sqlite.org/cli.html

### Hostinger Resources
- **VPS Help:** https://www.hostinger.com/vps/help
- **hPanel Dashboard:** https://hpanel.hostinger.com/
- **Domain Management:** https://hpanel.hostinger.com/domains
- **Support:** 24/7 chat in hPanel

### Monitoring (Optional)
- **Healthchecks.io:** https://healthchecks.io (free tier)
- **UptimeRobot:** https://uptimerobot.com (free tier)
- **SSL Labs:** https://www.ssllabs.com/ssltest/

---

## 🚨 Troubleshooting Quick Links

| Problem | Resource | Section |
|---------|----------|---------|
| Container won't start | DEPLOYMENT_GUIDE.md | Troubleshooting |
| DNS doesn't resolve | DEPLOYMENT_GUIDE.md | Domain & SSL Setup |
| SSL certificate error | QUICK_REFERENCE.md | SSL Certificate Errors |
| 502 Bad Gateway | QUICK_REFERENCE.md | Nginx Proxy Issues |
| Disk full | QUICK_REFERENCE.md | High Disk Usage |
| High memory usage | DEPLOYMENT_GUIDE.md | Troubleshooting |
| Database locked | QUICK_REFERENCE.md | Common Issues & Fixes |
| Can't SSH | QUICK_REFERENCE.md | Emergency Procedures |

---

## 📈 File Sizes & Read Times

| File | Size | Read Time | Best For |
|------|------|-----------|----------|
| DEPLOYMENT_GUIDE.md | 70 KB | 45 min | Detailed walkthrough |
| DEPLOYMENT_CHECKLIST.md | 25 KB | 2-3 hours | Verification |
| DEPLOYMENT_SUMMARY.md | 20 KB | 30 min | Overview & decisions |
| ARCHITECTURE.md | 25 KB | 30 min | System design |
| QUICK_REFERENCE.md | 15 KB | 5-30 sec | Daily operations |
| DEPLOYMENT_RESOURCES.md | This file | 15 min | Navigation |

---

## 🎯 Success Criteria

Deployment is **complete** when:

- ✅ VPS running and accessible
- ✅ Docker containers running healthily
- ✅ HTTPS working with valid SSL certificate
- ✅ Frontend loads at yourdomain.com
- ✅ API responds at yourdomain.com/api/health
- ✅ Database created and accessible
- ✅ Backups running daily
- ✅ Monitoring checks passing
- ✅ All checklist items verified
- ✅ Team trained on daily operations

---

## 📞 Getting Help

### Within Documentation
1. Check DEPLOYMENT_GUIDE.md → Troubleshooting section
2. Check QUICK_REFERENCE.md → Common Issues & Fixes
3. Search for keyword in all documents

### From Tools
1. Run `/opt/mudra/scripts/logs.sh` — View application logs
2. Run `/opt/mudra/scripts/monitor.sh` — Check system health
3. Run `docker-compose logs` — Check container logs

### From Community
1. **FastAPI Issues:** Stack Overflow, FastAPI GitHub
2. **Docker Issues:** Docker forums, Docker docs
3. **Nginx Issues:** Nginx docs, ServerFault
4. **Hostinger Issues:** Hostinger 24/7 support chat

### Emergency Contact
- Hostinger Support: Chat in hPanel (24/7)
- VPS Console Access: hPanel → Manage VPS → Console
- SSH Access: `ssh root@<your_vps_ip>`

---

## 📝 Version Control

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-05-30 | Initial deployment package |
| | | • 5 comprehensive guides |
| | | • 4 helper scripts |
| | | • Production-ready configs |
| | | • Checklists & references |

---

## 🔐 Security Checklist

Before going live, verify:
- [ ] .env file NOT in git (check .gitignore)
- [ ] No API keys in code or commits
- [ ] HTTPS enforced (HTTP → 301 redirect)
- [ ] SSL certificate valid and auto-renewing
- [ ] Firewall rules configured
- [ ] SSH key-based auth (no password auth)
- [ ] Regular updates scheduled
- [ ] Backups automated and tested
- [ ] Monitoring enabled
- [ ] Logs being written

---

## 🎓 Learning Resources

If you want to deepen your knowledge:

**Docker & Containerization**
- Official Docker Tutorial (30 min): https://docs.docker.com/
- Multi-stage builds (15 min): https://docs.docker.com/build/building/multi-stage/

**FastAPI**
- FastAPI Tutorial (2 hours): https://fastapi.tiangolo.com/tutorial/
- Deployment Guide (30 min): https://fastapi.tiangolo.com/deployment/

**Nginx**
- Nginx Beginner's Guide (30 min): https://nginx.org/en/docs/beginners_guide.html
- Reverse Proxy (15 min): https://nginx.org/en/docs/http/ngx_http_proxy_module.html

**SSL/TLS**
- Let's Encrypt How It Works (10 min): https://letsencrypt.org/how-it-works/
- Certbot Documentation (20 min): https://certbot.eff.org/docs/

---

## ✅ Final Checklist

Before declaring deployment complete:

- [ ] All documents have been reviewed
- [ ] Hardware has been purchased
- [ ] Scripts have been tested locally
- [ ] Deployment has been executed
- [ ] All verification steps passed
- [ ] Team has been trained
- [ ] Monitoring is active
- [ ] Backups are running
- [ ] Documentation has been customized with your domain
- [ ] Issue tracking setup (if applicable)
- [ ] Maintenance schedule established
- [ ] Success celebration scheduled 🎉

---

**Last Updated:** 2026-05-30  
**Ready to Deploy:** ✅ Yes  
**Estimated Time:** 3-4 hours for first deployment  
**Subsequent Deployments:** 5-10 minutes  

**Next Step:** Start with DEPLOYMENT_SUMMARY.md or DEPLOYMENT_GUIDE.md Phase 1!
