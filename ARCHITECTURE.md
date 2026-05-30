# Mudra Trading App - Deployment Architecture

## High-Level Architecture

```
                                    Internet
                                      │
                                      │ HTTPS (443)
                                      ▼
                        ┌─────────────────────┐
                        │   Your Domain       │
                        │  yourdomain.com     │
                        └──────────┬──────────┘
                                   │
                      ┌────────────┴─────────────┐
                      │ DNS A Record (Hostinger) │
                      │ Points to VPS IP         │
                      └────────────┬─────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │    Hostinger VPS (2GB)      │
                    │  Ubuntu 22.04 LTS           │
                    │  IP: 185.123.45.67          │
                    └──────────────┬──────────────┘
                                   │
                  ┌────────────────┴────────────────┐
                  │                                 │
        ┌─────────▼──────────┐        ┌────────────▼────────┐
        │   Nginx (SSL/TLS)  │        │   Firewall/hPanel   │
        │  Ports: 80, 443    │        │   (Auto-configured) │
        │                    │        │                      │
        │  - Reverse Proxy   │        └────────────┬────────┘
        │  - HTTP→HTTPS      │                     │
        │  - Security Headers│                     │
        │  - Compression     │                     │
        └──────────┬─────────┘                     │
                   │                               │
         ┌─────────▼────────────────────────────────┘
         │
         │  HTTP (port 8000 - local only)
         │
    ┌────▼──────────────────────────┐
    │   Docker Container (mudra-app) │
    │   image: python:3.11-slim      │
    ├────────────────────────────────┤
    │  FastAPI Backend               │
    │  ├─ /api/* endpoints           │
    │  ├─ /trades                    │
    │  ├─ /health ✓                  │
    │  └─ Serves React dist/         │
    │                                │
    │  React Frontend                │
    │  ├─ Static HTML/CSS/JS         │
    │  ├─ Built from /frontend/      │
    │  └─ Vite production build      │
    │                                │
    │  Python Environment            │
    │  ├─ FastAPI 0.104.1            │
    │  ├─ SQLAlchemy 2.0.23          │
    │  ├─ Uvicorn 0.24.0             │
    │  └─ Pydantic 2.5.0             │
    └────────────────┬───────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
    ┌───▼──────────────┐   ┌──────▼────────────┐
    │   SQLite DB      │   │   Auto-Restart    │
    │  /app/data/      │   │   Health Checks   │
    │  mudra.db        │   │   (Every 30s)     │
    │                  │   │                   │
    │  Size: 50-500KB  │   │   Systemd Mgmt    │
    │  Backup: Daily   │   │   Auto-start      │
    │  Retention: 30d  │   │                   │
    └──────────────────┘   └───────────────────┘
```

---

## Data Flow

### User Request → Response

```
1. User opens browser: https://yourdomain.com
                         ↓
2. DNS lookup → VPS IP: 185.123.45.67
                         ↓
3. TLS Handshake (SSL cert from Let's Encrypt)
                         ↓
4. HTTP Request to Nginx (port 443)
   GET / HTTP/2
                         ↓
5. Nginx logs request
   ├─ Checks security headers
   └─ Routes to backend (port 8000)
                         ↓
6. FastAPI handles request
   ├─ Route: GET / → serves index.html
   ├─ Route: GET /api/health → {"status":"ok"}
   ├─ Route: POST /api/trades → creates trade
   └─ Route: GET /api/trades → returns all trades
                         ↓
7. Database query (if needed)
   SQLite: mudra.db
   ├─ SELECT * FROM trades
   ├─ INSERT INTO trades VALUES (...)
   └─ UPDATE trades SET ...
                         ↓
8. Response sent back through Nginx
                         ↓
9. Browser renders (React frontend)
                         ↓
10. User sees UI
```

---

## Container Architecture

### Single Container Approach (Chosen)

```
┌──────────────────────────────────────────────────────┐
│              Docker Container: mudra-app              │
│                  image: mudra:latest                  │
├──────────────────────────────────────────────────────┤
│                                                       │
│  ┌────────────────────────────────────────────────┐  │
│  │  Python 3.11-slim Base Image                   │  │
│  │  • Slim image = 130MB (vs 900MB full)         │  │
│  │  • No development tools                        │  │
│  │  • Fast startup                                │  │
│  └────────────────────────────────────────────────┘  │
│                      ↓                                 │
│  ┌────────────────────────────────────────────────┐  │
│  │  Multi-Stage Build                             │  │
│  │  Stage 1: Node.js                              │  │
│  │    • Build React frontend                      │  │
│  │    • Output: /dist folder                      │  │
│  │  Stage 2: Python                               │  │
│  │    • Copy built frontend                       │  │
│  │    • Install Python deps                       │  │
│  │    • Final image size: ~400-500MB              │  │
│  └────────────────────────────────────────────────┘  │
│                      ↓                                 │
│  ┌────────────────────────────────────────────────┐  │
│  │  Runtime (Uvicorn + FastAPI)                   │  │
│  │  • Listens on 0.0.0.0:8000                    │  │
│  │  • Serves /api/* endpoints                     │  │
│  │  • Serves static files (/dist)                 │  │
│  │  • Database access (SQLite)                    │  │
│  │  • Process: python backend/main.py             │  │
│  └────────────────────────────────────────────────┘  │
│                      ↓                                 │
│  ┌────────────────────────────────────────────────┐  │
│  │  Health Check                                  │  │
│  │  • Endpoint: GET /health                       │  │
│  │  • Interval: 30 seconds                        │  │
│  │  • Timeout: 10 seconds                         │  │
│  │  • Retries: 3 before marking unhealthy        │  │
│  │  • Auto-restart on failure                     │  │
│  └────────────────────────────────────────────────┘  │
│                                                       │
│  ┌────────────────────────────────────────────────┐  │
│  │  Volume Mounts                                 │  │
│  │  • /app/data ← /opt/mudra/data (persistent)   │  │
│  │  • /app/logs ← /opt/mudra/logs (persistent)   │  │
│  └────────────────────────────────────────────────┘  │
│                                                       │
│  ┌────────────────────────────────────────────────┐  │
│  │  Environment Variables                         │  │
│  │  From .env:                                    │  │
│  │  • DATABASE_URL                                │  │
│  │  • BINANCE_API_KEY                             │  │
│  │  • BINANCE_API_SECRET                          │  │
│  │  • ZERODHA_API_KEY                             │  │
│  │  • ZERODHA_SESSION_TOKEN                       │  │
│  │  • DEFAULT_MODE (paper/live)                   │  │
│  │  • LOG_LEVEL                                   │  │
│  └────────────────────────────────────────────────┘  │
│                                                       │
└──────────────────────────────────────────────────────┘
```

---

## Directory Structure on VPS

```
/opt/mudra/
├── Dockerfile                   # Multi-stage build definition
├── docker-compose.yml           # Dev compose (local only)
├── docker-compose.prod.yml      # Production compose (VPS)
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (DO NOT COMMIT)
├── .gitignore                   # Git ignore rules
│
├── backend/                     # FastAPI source code
│   ├── main.py                  # Application entry point
│   ├── config.py                # Configuration loader
│   ├── database.py              # Database initialization
│   ├── schemas.py               # Pydantic models
│   ├── api/
│   │   └── routes.py            # API endpoint definitions
│   ├── models/                  # SQLAlchemy ORM models
│   ├── services/                # Business logic
│   └── utils/                   # Utility functions
│
├── frontend/                    # React source code
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js           # Vite build configuration
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── components/
│   │   ├── pages/
│   │   └── api.js               # API client
│   └── public/
│
├── data/                        # Persistent data directory
│   ├── mudra.db                 # SQLite database (auto-created)
│   └── *.db.bak                 # Backup files (if manual backup)
│
├── logs/                        # Application logs
│   ├── app.log                  # FastAPI logs
│   └── access.log               # Request logs
│
├── backups/                     # Database backups
│   ├── mudra_20260530_020000.db # Daily backups (auto)
│   └── mudra_20260529_020000.db # Retention: 30 days
│
├── scripts/                     # Helper scripts
│   ├── deploy.sh                # Deployment automation
│   ├── backup.sh                # Database backup script
│   ├── monitor.sh               # Health check script
│   └── logs.sh                  # Log viewer utility
│
├── DEPLOYMENT_GUIDE.md          # Complete setup guide
├── DEPLOYMENT_CHECKLIST.md      # Verification checklist
├── QUICK_REFERENCE.md           # Daily operations guide
├── DEPLOYMENT_SUMMARY.md        # Architecture & strategy
├── ARCHITECTURE.md              # This file
└── README.md                    # Project overview
```

---

## Networking

### Port Mapping

```
External (Internet)          Internal (VPS)
─────────────────────────────────────────────

HTTP  (80)    ──────────────→  Nginx
HTTPS (443)   ──────────────→  Nginx  (SSL termination)
                               ↓
                           127.0.0.1:8000
                               ↓
                          Docker Container
                          (FastAPI app)


SSH (22)      ──────────────→  OpenSSH (for admin access)
              (Hostinger hPanel or your SSH key)
```

### Firewall Rules (Hostinger hPanel)

```
Direction  Protocol  Port(s)  Source         Action
──────────────────────────────────────────────────────
Inbound    TCP       80       0.0.0.0/0      Allow
Inbound    TCP       443      0.0.0.0/0      Allow
Inbound    TCP       22       [Your IP/All]  Allow
Inbound    TCP       8000     127.0.0.1      Allow (Local only)
Inbound    UDP       53       0.0.0.0/0      Allow (DNS)

Outbound   All       All      0.0.0.0/0      Allow (needed for API calls to Binance/Zerodha)
```

---

## Database Schema

### SQLite Database

```
mudra.db (SQLite file)
├── Tables
│   ├── trades
│   │   ├── id (INTEGER, PRIMARY KEY)
│   │   ├── symbol (TEXT)
│   │   ├── side (TEXT) - 'BUY' or 'SELL'
│   │   ├── entry_price (FLOAT)
│   │   ├── quantity (FLOAT)
│   │   ├── sl_price (FLOAT)
│   │   ├── tp_price (FLOAT)
│   │   ├── mode (TEXT) - 'paper' or 'live'
│   │   ├── status (TEXT) - 'open' or 'closed'
│   │   ├── pnl (FLOAT)
│   │   ├── created_at (DATETIME)
│   │   └── closed_at (DATETIME)
│   │
│   └── [Other tables as defined in models/]
│
├── Indexes (for performance)
│   ├── idx_trades_symbol
│   ├── idx_trades_mode
│   └── idx_trades_created_at
│
└── File Details
    ├── Location: /opt/mudra/data/mudra.db
    ├── Size: 50KB - 500KB (typical for 2 users)
    ├── Backup Size: Same (copy entire file)
    ├── Backup Time: < 1 second
    └── Restore Time: < 1 second
```

---

## Deployment Process

### Build Process

```
1. git clone repo
        ↓
2. docker-compose build
        ↓
   ┌─────────────────────────┐
   │  Docker Build (Multi-stage)
   ├─────────────────────────┤
   │                          │
   │ Stage 1: Node (Frontend)│
   │ ├─ FROM node:18-slim    │
   │ ├─ npm install          │
   │ ├─ npm run build        │
   │ └─ Output: /dist        │
   │       ↓                  │
   │ Stage 2: Python (Backend)
   │ ├─ FROM python:3.11-slim│
   │ ├─ pip install -r req   │
   │ ├─ Copy backend code    │
   │ ├─ Copy /dist from S1   │
   │ └─ Setup healthcheck    │
   └─────────────────────────┘
        ↓
3. Image created: ~400MB
        ↓
4. docker-compose up -d
        ↓
5. Container starts
        ↓
6. Database initialized
        ↓
7. Health check passes
        ↓
✅ Ready for traffic
```

### Deployment on VPS

```
Time  Action
────  ─────────────────────────────────────────
T+0s  $ /opt/mudra/scripts/deploy.sh
      ├─ Database backed up
      ├─ New code pulled
      ├─ Image rebuilt
      └─ Wait...
      
T+3m  Image build completes (~3 min for Node/Python)
      
T+3m  $ docker-compose down
      ├─ Old container stops
      └─ Wait 5 seconds
      
T+3m  $ docker-compose up -d
      └─ New container starts
      
T+3m10s  Health check begins (interval: 30s)
      
T+3m40s  ✅ Container marked healthy
      ├─ Nginx automatically serves new version
      └─ Users see updated app
      
Total: ~4 minutes (most of it is Docker build)
```

---

## Monitoring & Observability

### Health Monitoring

```
Real-time Checks (Every 30 seconds inside container)
├─ Container health check
│  ├─ Command: curl http://localhost:8000/health
│  ├─ Expected: {"status":"ok"}
│  ├─ Timeout: 10 seconds
│  └─ Action: Auto-restart if fails 3x
│
Cron Job (Every 5 minutes on host)
├─ /opt/mudra/scripts/monitor.sh
│  ├─ Container running?
│  ├─ API responding?
│  ├─ Disk usage < 90%?
│  ├─ Memory usage < 90%?
│  └─ Optional: Ping webhook (Healthchecks.io)
│
Daily Jobs
├─ Backup database
│  ├─ Time: 2:00 AM UTC
│  ├─ Script: /opt/mudra/scripts/backup.sh
│  ├─ Retention: 30 days
│  └─ Size: ~100KB per backup
│
Weekly Manual
├─ Check logs for errors
├─ Monitor disk growth
├─ Verify backups exist
└─ Performance review
```

### Log Files

```
/var/log/nginx/mudra_access.log
├─ Every HTTP request
├─ Format: IP timestamp method path status size
├─ Examples:
│  185.123.4.5 [30/May/2026:14:23:45] GET /api/trades 200 1024
│  185.123.4.5 [30/May/2026:14:23:46] GET /api/health 200 15
├─ Rotation: daily (handled by logrotate)
└─ Retention: 7 days

/var/log/nginx/mudra_error.log
├─ Errors, warnings, access denied
├─ Format: timestamp [level] message
├─ Examples:
│  2026/05/30 14:23:45 [error] 12345#0: backend error
│  2026/05/30 14:23:46 [warn] 12345#0: timeout
├─ Rotation: daily
└─ Retention: 7 days

docker-compose logs
├─ Application logs (FastAPI)
├─ Format: timestamp container_name message
├─ Examples:
│  app | 2026-05-30 14:23:45 INFO Started server
│  app | 2026-05-30 14:23:46 WARNING slow query: 500ms
├─ Retention: Latest 500 lines (in memory)
└─ Use: docker-compose logs -f (follow mode)

/var/log/mudra/monitor.log
├─ Health check results
├─ Format: timestamp [health_check] status message
├─ Examples:
│  2026-05-30 14:25:00 ✓ Container is running
│  2026-05-30 14:25:01 ✓ Health check passed
├─ Rotation: manual (monitor.sh manages)
└─ Retention: Last 100 lines
```

---

## Scalability Path

### Current Setup (2 Users)
```
VPS: 2GB RAM, 1 vCPU
├─ SQLite database
├─ ~300MB memory usage
├─ ~1% CPU (idle)
└─ Response time: 50-100ms
```

### Growth to 5 Users
```
VPS: 4GB RAM, 2 vCPU (+$7/mo)
├─ SQLite database (still fine)
├─ ~600MB memory usage
├─ ~5% CPU (idle)
└─ Response time: 50-100ms
```

### Growth to 20+ Users or 1M+ Trades
```
VPS: 8GB RAM, 4 vCPU (+$15/mo)
├─ PostgreSQL database (+$5/mo)
├─ Redis cache (+$3/mo)
├─ ~2GB memory usage
├─ ~10% CPU (idle)
└─ Response time: 20-50ms
Total: ~$35/month
```

### Growth to 100+ Users
```
Multiple VPS + Load Balancer (+$50+/mo)
├─ Frontend VPS
├─ Backend VPS
├─ Database VPS (PostgreSQL)
├─ Redis cache cluster
└─ Cloudflare CDN
```

---

## Disaster Recovery

### Backup Strategy

```
Location: /opt/mudra/backups/
├─ Daily at 2:00 AM UTC
├─ Format: mudra_YYYYMMDD_HHMMSS.db
├─ Retention: 30 days
├─ Size: ~100KB-500KB each
├─ Rotation: Auto-purge after 30 days
└─ Testing: Manual restore test monthly

Backup Timeline:
Day 1:   mudra_20260530_020000.db ← Latest
Day 2:   mudra_20260529_020000.db ← Can restore from here
...
Day 30:  mudra_20260501_020000.db ← Oldest
Day 31:  [Deleted by script]
```

### Recovery Procedure

```bash
# 1. Identify last good backup
ls -lh /opt/mudra/backups/ | tail -5

# 2. Stop application
docker-compose down

# 3. Restore database
cp /opt/mudra/backups/mudra_GOOD_DATE.db /opt/mudra/data/mudra.db

# 4. Restart
docker-compose up -d

# 5. Verify
curl https://yourdomain.com/api/health
# Should return {"status":"ok"}

# Recovery time: < 5 minutes
```

---

## Summary

| Layer | Technology | Details |
|-------|-----------|---------|
| **DNS** | Hostinger | A record: yourdomain.com → VPS IP |
| **SSL/TLS** | Let's Encrypt | Free, auto-renewing via Certbot |
| **Proxy** | Nginx | Reverse proxy, security headers, compression |
| **App Server** | Uvicorn/FastAPI | Python async framework |
| **Frontend** | React + Vite | Built as static files, served by FastAPI |
| **Database** | SQLite | Local file-based, daily backups |
| **Container** | Docker | Single container, multi-stage build |
| **Monitoring** | Systemd + Cron | Auto-restart, health checks, backup automation |
| **Infrastructure** | Hostinger VPS | 2GB RAM, Ubuntu 22.04, 50GB SSD |

**Total Cost:** $12-15/month  
**Setup Time:** 2-3 hours  
**Maintenance:** 30 min/week  
**Uptime Target:** 99%+  
**Scalable:** Yes (VPS upgrades available)

---

**Architecture Version:** 1.0  
**Last Updated:** 2026-05-30  
**For:** Mudra Trading App on Hostinger VPS  
**Status:** Production Ready ✅
