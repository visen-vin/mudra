# Mudra Screener v2.0 - Detailed Task Breakdown
## Based on PRD: 1-Minute Live Engine

**Document Purpose:** Actionable task list for implementation across 4 phases. Use for Jira/Trello/GitHub Projects.

---

## 🎯 PHASE 1: Infrastructure & Redis Setup (Backend)

### Phase 1 Epic: "Setup Redis & Data Ingestion Pipeline"

---

#### Task 1.1: Setup Redis Infrastructure
**Type:** Infrastructure Setup  
**Story Points:** 5  
**Priority:** P0 (Critical)  

**Acceptance Criteria:**
- [ ] Docker Compose includes Redis service (6.0+)
- [ ] Redis container persists data (volumes configured)
- [ ] Redis CLI accessible via `redis-cli` command
- [ ] Health check endpoint confirms Redis availability
- [ ] .env.example updated with REDIS_URL
- [ ] Local development setup documented in README

**Subtasks:**
- 1.1.1: Create redis service in docker-compose.yml
- 1.1.2: Configure Redis persistence (RDB snapshots)
- 1.1.3: Add Redis health check endpoint
- 1.1.4: Update environment variables

**Dependencies:** None

---

#### Task 1.2: Create Data Ingestion Service (Zerodha)
**Type:** Feature  
**Story Points:** 8  
**Priority:** P0 (Critical)  

**Acceptance Criteria:**
- [ ] Service fetches 1-minute OHLCV candles for 5 hardcoded symbols (e.g., RELIANCE, TCS, INFY, LT, HDFC)
- [ ] Candles are stored in Redis key: `market_data:1m:<SYMBOL>`
- [ ] Each Redis value contains last 100 candles (FIFO, oldest removed when > 100)
- [ ] Service runs continuously (separate thread/process)
- [ ] Graceful error handling (Zerodha API down → use cached data)
- [ ] Log file captures all ingestion events
- [ ] Configurable via environment variables (API key, symbols list)

**Subtasks:**
- 1.2.1: Extend backend/feeds/zerodha.py to support 1-minute candle fetching
- 1.2.2: Create backend/services/data_ingestion.py (main loop)
- 1.2.3: Implement Redis write logic (key structure, FIFO queue)
- 1.2.4: Add error handling & retry logic
- 1.2.5: Add logging for ingestion events

**Dependencies:** Task 1.1

---

#### Task 1.3: Create Data Ingestion Service (Binance)
**Type:** Feature  
**Story Points:** 8  
**Priority:** P0 (Critical)  

**Acceptance Criteria:**
- [ ] Service fetches 1-minute OHLCV candles for 5 hardcoded crypto symbols (e.g., BTCUSDT, ETHUSDT, BNBUSDT, ADAUSDT, DOGEUSDT)
- [ ] Uses existing backend/feeds/binance.py adapter
- [ ] Stores in Redis using same key structure: `market_data:1m:<SYMBOL>`
- [ ] Handles WebSocket connection management (auto-reconnect)
- [ ] Fallback to REST API if WebSocket unavailable
- [ ] Graceful shutdown on app stop (cleanup WebSocket)

**Subtasks:**
- 1.3.1: Extend backend/feeds/binance.py with 1-minute candle support
- 1.3.2: Implement WebSocket listener for tick data
- 1.3.3: Implement Redis write logic (matching Zerodha format)
- 1.3.4: Add reconnection logic with exponential backoff
- 1.3.5: Add logging for WebSocket events

**Dependencies:** Task 1.1, Task 1.2

---

#### Task 1.4: Test Data Ingestion (Standalone)
**Type:** Testing  
**Story Points:** 5  
**Priority:** P0 (Critical)  

**Acceptance Criteria:**
- [ ] Unit tests for Redis write operations (mock Redis)
- [ ] Integration tests confirm data appears in Redis after 30 seconds
- [ ] Test for error recovery (simulate API failure → check cached data)
- [ ] Performance test: 10 symbols ingesting in parallel → < 500ms per cycle
- [ ] All tests pass locally before moving to Phase 2

**Subtasks:**
- 1.4.1: Write unit tests for data_ingestion.py (mock APIs)
- 1.4.2: Write integration tests with real Redis
- 1.4.3: Write error recovery tests
- 1.4.4: Write performance/load tests

**Dependencies:** Task 1.2, Task 1.3

---

## 🔧 PHASE 2: Core Engine & Modularity (Backend)

### Phase 2 Epic: "Build 1-Minute Strategy Engine with APScheduler"

---

#### Task 2.1: Create BaseStrategy Abstract Class
**Type:** Architecture  
**Story Points:** 3  
**Priority:** P0 (Critical)  

**Acceptance Criteria:**
- [ ] Abstract class at `backend/strategies/base.py`
- [ ] Interface: `def analyze(candles: List[Candle]) -> Optional[StrategySignal]`
- [ ] StrategySignal dataclass: `{symbol, side ("LONG"/"SHORT"/"NEUTRAL"), confidence (0-1), strategy_name}`
- [ ] Documentation with example implementation
- [ ] Type hints throughout (mypy compatible)

**Subtasks:**
- 2.1.1: Design StrategySignal dataclass
- 2.1.2: Create BaseStrategy ABC with abstract methods
- 2.1.3: Add docstring examples
- 2.1.4: Add type hints validation tests

**Dependencies:** None

---

#### Task 2.2: Implement MA Crossover Strategy (PoC)
**Type:** Feature  
**Story Points:** 5  
**Priority:** P0 (Critical)  

**Acceptance Criteria:**
- [ ] Strategy: Moving Average 9/21 crossover on 1-minute timeframe
- [ ] Signal logic: MA9 > MA21 → LONG, MA9 < MA21 → SHORT, else NEUTRAL
- [ ] Confidence: Based on distance between MAs (normalized 0-1)
- [ ] File location: `backend/strategies/ma_crossover.py`
- [ ] Inherits from BaseStrategy
- [ ] Unit tests with mock candle data
- [ ] Performance: Analyzes 100 candles in < 10ms

**Subtasks:**
- 2.2.1: Implement MA crossover logic using pandas-ta
- 2.2.2: Calculate confidence score formula
- 2.2.3: Write unit tests (10+ test cases)
- 2.2.4: Add documentation

**Dependencies:** Task 2.1

---

#### Task 2.3: Create Strategy Registry & Loader
**Type:** Architecture  
**Story Points:** 4  
**Priority:** P0 (Critical)  

**Acceptance Criteria:**
- [ ] Registry file: `backend/strategies/registry.py`
- [ ] Dynamically loads all `.py` files from `backend/strategies/`
- [ ] Registry reads `ENABLED_STRATEGIES` from env var (comma-separated list)
- [ ] Can enable/disable strategies via database table `strategy_configs`
- [ ] Provides method: `get_active_strategies() -> List[Strategy]`
- [ ] Graceful error handling (bad strategy file → skip with warning)

**Subtasks:**
- 2.3.1: Implement strategy discovery mechanism
- 2.3.2: Create strategy_configs database table
- 2.3.3: Implement registry loader with env var support
- 2.3.4: Add logging for strategy loading/unloading
- 2.3.5: Write unit tests

**Dependencies:** Task 2.2

---

#### Task 2.4: Setup APScheduler (1-Minute Cron Job)
**Type:** Architecture  
**Story Points:** 5  
**Priority:** P0 (Critical)  

**Acceptance Criteria:**
- [ ] APScheduler configured in `backend/services/scheduler.py`
- [ ] Cron job triggers exactly at the `:01` second of every minute (e.g., 14:32:01, 14:33:01, etc.)
- [ ] Job triggers `screener_engine.run_scan()` function
- [ ] Logs each job execution (start time, duration, results)
- [ ] Graceful shutdown (completes current run before stopping)
- [ ] Health check endpoint: `/api/scheduler/status` returns last run time + next run time

**Subtasks:**
- 2.4.1: Install APScheduler and configure in main.py
- 2.4.2: Create scheduler.py with job definition
- 2.4.3: Implement scheduler start/stop logic
- 2.4.4: Add health check endpoint
- 2.4.5: Write tests (mock scheduler, verify job fires)

**Dependencies:** Task 2.1

---

#### Task 2.5: Create Screener Engine (Core Logic)
**Type:** Feature  
**Story Points:** 8  
**Priority:** P0 (Critical)  

**Acceptance Criteria:**
- [ ] Engine file: `backend/services/screener_engine.py`
- [ ] Main method: `async def run_scan()`
- [ ] Workflow:
  1. Get active symbols from Redis key `watchlist:active`
  2. For each symbol, fetch last 100 candles from Redis `market_data:1m:<SYMBOL>`
  3. Instantiate all active strategies from registry
  4. For each strategy: call `strategy.analyze(candles)`
  5. Aggregate signals (collect all strategy outputs for each symbol)
  6. Store aggregated result in Redis `screener_signals:latest` (overwrite, single JSON object)
- [ ] Execution must complete in < 3 seconds for 50 symbols × 3 strategies
- [ ] Parallel execution of strategies (asyncio or ThreadPool)
- [ ] Logs: Start time, symbol count, strategy count, duration, signal count
- [ ] Error handling: If strategy crashes, skip that strategy with warning

**Subtasks:**
- 2.5.1: Implement candle retrieval from Redis
- 2.5.2: Implement parallel strategy execution
- 2.5.3: Implement signal aggregation logic
- 2.5.4: Implement Redis write logic (`screener_signals:latest`)
- 2.5.5: Add comprehensive logging
- 2.5.6: Write tests (mock Redis, mock strategies)

**Dependencies:** Task 2.3, Task 2.4

---

#### Task 2.6: Create Watchlist Manager (Backend)
**Type:** Feature  
**Story Points:** 5  
**Priority:** P1 (High)  

**Acceptance Criteria:**
- [ ] Service: `backend/services/watchlist_manager.py`
- [ ] Stores active watchlist in Redis key `watchlist:active` (JSON array of symbols)
- [ ] Also stores in PostgreSQL table `watchlist` for persistence
- [ ] Methods:
  - `add_symbol(symbol, market)` → adds to active list + database
  - `remove_symbol(symbol)` → removes from active list + database
  - `get_active_watchlist()` → returns list of symbols
  - `sync_redis_from_db()` → restores Redis watchlist from database on startup
- [ ] Max 50 symbols in watchlist (config)
- [ ] Validation: Symbol exists in market data (Zerodha/Binance)

**Subtasks:**
- 2.6.1: Create watchlist PostgreSQL table
- 2.6.2: Implement WatchlistManager service
- 2.6.3: Add validation logic (symbol existence check)
- 2.6.4: Add startup sync from database → Redis
- 2.6.5: Write unit tests

**Dependencies:** Task 1.2, Task 1.3

---

#### Task 2.7: Test Engine Performance
**Type:** Testing  
**Story Points:** 5  
**Priority:** P0 (Critical)  

**Acceptance Criteria:**
- [ ] Load test: 50 symbols, 3 strategies, 100 candles each → completes in < 3 seconds
- [ ] Accuracy test: Known signal scenario (e.g., MA9=100, MA21=99) → correct signal generated
- [ ] Error resilience: 1 strategy crashes → others still execute
- [ ] Concurrency test: Multiple Redis reads/writes under load → no data corruption
- [ ] All tests pass before Phase 3

**Subtasks:**
- 2.7.1: Write load test script
- 2.7.2: Write accuracy tests
- 2.7.3: Write error resilience tests
- 2.7.4: Write concurrency tests

**Dependencies:** Task 2.5, Task 2.6

---

## 🎨 PHASE 3: API & Frontend Binding (Fullstack)

### Phase 3 Epic: "Build Screener API & React Dashboard"

---

#### Task 3.1: Create `/api/screener/latest` Endpoint
**Type:** Feature  
**Story Points:** 3  
**Priority:** P0 (Critical)  

**Acceptance Criteria:**
- [ ] Endpoint: `GET /api/screener/latest`
- [ ] Reads from Redis key `screener_signals:latest`
- [ ] Returns JSON:
  ```json
  {
    "timestamp": "2026-05-30T14:32:01Z",
    "signals": [
      {"symbol": "RELIANCE", "side": "LONG", "confidence": 0.85, "strategy": "MA_9_21"},
      {"symbol": "TCS", "side": "NEUTRAL", "confidence": 0.52, "strategy": "MA_9_21"}
    ],
    "scan_duration_ms": 245
  }
  ```
- [ ] Response time: < 50ms (cached in memory)
- [ ] Unit tests (mock Redis)

**Subtasks:**
- 3.1.1: Create endpoint in backend/api/routes.py
- 3.1.2: Add Redis read logic
- 3.1.3: Add response formatting
- 3.1.4: Write unit tests

**Dependencies:** Task 2.5

---

#### Task 3.2: Setup React Query (TanStack Query)
**Type:** Setup  
**Story Points:** 3  
**Priority:** P1 (High)  

**Acceptance Criteria:**
- [ ] TanStack Query installed (latest version)
- [ ] Query client configured in frontend/src/lib/queryClient.js
- [ ] useQuery hook setup for screener polling
- [ ] Polling interval: 60000ms (60 seconds)
- [ ] Stale time: 55000ms (refresh just before next poll)

**Subtasks:**
- 3.2.1: Install TanStack Query package
- 3.2.2: Configure QueryClient
- 3.2.3: Add QueryClientProvider to App.jsx
- 3.2.4: Create custom useScreenerQuery hook

**Dependencies:** None (Frontend)

---

#### Task 3.3: Build Screener UI Dashboard Component
**Type:** Feature  
**Story Points:** 8  
**Priority:** P0 (Critical)  

**Acceptance Criteria:**
- [ ] Component: `frontend/src/components/ScreenerDashboard.jsx`
- [ ] Displays data table with columns:
  - Symbol (left-aligned)
  - LTP (Last Traded Price) in ₹ or USDT
  - Signal (LONG / SHORT / NEUTRAL with color: green/red/gray)
  - Strategy Name
  - Last Update Timestamp (relative: "2 min ago")
- [ ] Data refreshes every 60 seconds without page reload/freeze
- [ ] Loading state: Skeleton loaders on initial load (no spinner)
- [ ] Empty state: "No signals yet" message with instructions
- [ ] Error state: Network error message with retry button
- [ ] Mobile responsive (Tailwind)
- [ ] Sorting: Click column header to sort
- [ ] Filtering: Filter by Signal type (LONG/SHORT/NEUTRAL)

**Subtasks:**
- 3.3.1: Create ScreenerDashboard component skeleton
- 3.3.2: Implement data table with react-table or simple HTML
- 3.3.3: Implement useScreenerQuery hook integration
- 3.3.4: Add loading/error/empty states
- 3.3.5: Add sorting and filtering
- 3.3.6: Style with Tailwind CSS
- 3.3.7: Add responsive design

**Dependencies:** Task 3.1, Task 3.2

---

#### Task 3.4: Add Screener Route to App.jsx
**Type:** Integration  
**Story Points:** 2  
**Priority:** P1 (High)  

**Acceptance Criteria:**
- [ ] New route: `/screener`
- [ ] Navigation link in header/sidebar
- [ ] Screener Dashboard component loads at `/screener`
- [ ] URL persists on page refresh
- [ ] Works with existing Dashboard, Positions, History routes

**Subtasks:**
- 3.4.1: Add route to React Router config
- 3.4.2: Add navigation link
- 3.4.3: Test navigation

**Dependencies:** Task 3.3

---

#### Task 3.5: Create `/api/strategies` Endpoint
**Type:** Feature  
**Story Points:** 3  
**Priority:** P1 (High)  

**Acceptance Criteria:**
- [ ] Endpoint: `GET /api/strategies`
- [ ] Returns list of available strategies with metadata:
  ```json
  {
    "strategies": [
      {"name": "MA_9_21", "enabled": true, "description": "MA Crossover 9/21"},
      {"name": "RSI", "enabled": false, "description": "RSI Strategy"}
    ]
  }
  ```
- [ ] Reads from registry (backend/strategies/registry.py)
- [ ] Unit tests

**Subtasks:**
- 3.5.1: Create endpoint in routes.py
- 3.5.2: Add registry integration
- 3.5.3: Write unit tests

**Dependencies:** Task 2.3

---

#### Task 3.6: Create `/api/strategies/toggle` Endpoint
**Type:** Feature  
**Story Points:** 3  
**Priority:** P1 (High)  

**Acceptance Criteria:**
- [ ] Endpoint: `POST /api/strategies/toggle`
- [ ] Request: `{"strategy_name": "MA_9_21", "enabled": true}`
- [ ] Updates strategy_configs table in database
- [ ] Triggers registry reload (strategies used in next scan)
- [ ] Response: Updated strategy list
- [ ] Unit tests

**Subtasks:**
- 3.6.1: Create endpoint in routes.py
- 3.6.2: Implement database update logic
- 3.6.3: Implement registry reload trigger
- 3.6.4: Write unit tests

**Dependencies:** Task 2.3, Task 3.5

---

#### Task 3.7: Build Strategies Config UI Component
**Type:** Feature  
**Story Points:** 5  
**Priority:** P2 (Medium)  

**Acceptance Criteria:**
- [ ] Component: `frontend/src/components/StrategiesConfig.jsx`
- [ ] List of all strategies with toggle switches
- [ ] Each toggle calls `/api/strategies/toggle`
- [ ] Loading state while toggle is processing
- [ ] Success/error toast notifications
- [ ] Mobile responsive

**Subtasks:**
- 3.7.1: Create component
- 3.7.2: Implement useQuery for strategies list
- 3.7.3: Implement toggle logic
- 3.7.4: Add toast notifications
- 3.7.5: Style with Tailwind

**Dependencies:** Task 3.5, Task 3.6

---

## 📋 PHASE 4: Dynamic Controls & Polish

### Phase 4 Epic: "Watchlist Management & UI Polish"

---

#### Task 4.1: Create `/api/watchlist` Endpoint
**Type:** Feature  
**Story Points:** 3  
**Priority:** P1 (High)  

**Acceptance Criteria:**
- [ ] Endpoint: `GET /api/watchlist`
- [ ] Returns current active watchlist:
  ```json
  {
    "symbols": ["RELIANCE", "TCS", "INFY", "LT", "HDFC"],
    "count": 5
  }
  ```
- [ ] Reads from Redis `watchlist:active`
- [ ] Unit tests

**Subtasks:**
- 4.1.1: Create endpoint
- 4.1.2: Implement Redis read logic
- 4.1.3: Write unit tests

**Dependencies:** Task 2.6

---

#### Task 4.2: Create `/api/watchlist/add` Endpoint
**Type:** Feature  
**Story Points:** 3  
**Priority:** P1 (High)  

**Acceptance Criteria:**
- [ ] Endpoint: `POST /api/watchlist/add`
- [ ] Request: `{"symbol": "HDFC", "market": "indian_equity"}`
- [ ] Calls WatchlistManager.add_symbol()
- [ ] Validates symbol exists
- [ ] Returns updated watchlist
- [ ] Error if symbol already in watchlist
- [ ] Error if max 50 symbols reached
- [ ] Unit tests

**Subtasks:**
- 4.2.1: Create endpoint
- 4.2.2: Implement validation
- 4.2.3: Implement error handling
- 4.2.4: Write unit tests

**Dependencies:** Task 2.6, Task 4.1

---

#### Task 4.3: Create `/api/watchlist/remove` Endpoint
**Type:** Feature  
**Story Points:** 2  
**Priority:** P1 (High)  

**Acceptance Criteria:**
- [ ] Endpoint: `DELETE /api/watchlist/{symbol}`
- [ ] Calls WatchlistManager.remove_symbol()
- [ ] Returns updated watchlist
- [ ] Error if symbol not in watchlist
- [ ] Unit tests

**Subtasks:**
- 4.3.1: Create endpoint
- 4.3.2: Implement removal logic
- 4.3.3: Write unit tests

**Dependencies:** Task 2.6, Task 4.1

---

#### Task 4.4: Build Watchlist Management UI
**Type:** Feature  
**Story Points:** 8  
**Priority:** P1 (High)  

**Acceptance Criteria:**
- [ ] Component: `frontend/src/components/WatchlistManager.jsx`
- [ ] Display current watchlist as list/chips
- [ ] Add new symbol:
  - Text input with autocomplete (suggest Zerodha/Binance symbols)
  - Button to add
  - Validation feedback
- [ ] Remove symbol:
  - Delete button on each chip/row
  - Confirmation dialog
- [ ] Loading states
- [ ] Error messages
- [ ] Mobile responsive
- [ ] Success toast on add/remove

**Subtasks:**
- 4.4.1: Create component structure
- 4.4.2: Implement useQuery for watchlist
- 4.4.3: Implement add symbol logic (mutation)
- 4.4.4: Implement remove symbol logic
- 4.4.5: Add autocomplete (symbol suggestions)
- 4.4.6: Add validation & error handling
- 4.4.7: Style with Tailwind

**Dependencies:** Task 4.1, Task 4.2, Task 4.3

---

#### Task 4.5: Integrate Screener into Main Dashboard
**Type:** Integration  
**Story Points:** 3  
**Priority:** P1 (High)  

**Acceptance Criteria:**
- [ ] Main Dashboard tabs:
  - Screener (new)
  - Positions (existing)
  - History (existing)
  - Strategies Config (new)
  - Watchlist (new)
- [ ] Smooth tab navigation
- [ ] Each tab independently loads data
- [ ] Tab persistence (URL reflects active tab)

**Subtasks:**
- 4.5.1: Refactor Dashboard.jsx to support tabs
- 4.5.2: Integrate ScreenerDashboard tab
- 4.5.3: Integrate WatchlistManager tab
- 4.5.4: Integrate StrategiesConfig tab
- 4.5.5: Test tab navigation

**Dependencies:** Task 3.3, Task 3.7, Task 4.4

---

#### Task 4.6: Optimize Frontend Performance
**Type:** Optimization  
**Story Points:** 5  
**Priority:** P2 (Medium)  

**Acceptance Criteria:**
- [ ] Lighthouse score: 85+ (Performance)
- [ ] No console warnings/errors
- [ ] Memoization: Screener table re-renders only when data changes (React.memo, useMemo)
- [ ] Code splitting: Lazy load ScreenerDashboard component
- [ ] Test: 100 re-renders in 1 second → <100ms DOM update

**Subtasks:**
- 4.6.1: Profile React app with DevTools
- 4.6.2: Implement memoization (React.memo, useMemo, useCallback)
- 4.6.3: Implement code splitting
- 4.6.4: Optimize table rendering
- 4.6.5: Write performance tests

**Dependencies:** Task 3.3, Task 4.5

---

#### Task 4.7: Add Search/Filter Features
**Type:** Feature  
**Story Points:** 5  
**Priority:** P2 (Medium)  

**Acceptance Criteria:**
- [ ] Filter by signal type: LONG / SHORT / NEUTRAL
- [ ] Search by symbol (real-time filter on client)
- [ ] Filter by market: Indian Equity / Crypto
- [ ] Persistence: Filters saved in URL params
- [ ] Mobile-friendly filter UI

**Subtasks:**
- 4.7.1: Add filter state to ScreenerDashboard
- 4.7.2: Implement signal type filter
- 4.7.3: Implement search filter
- 4.7.4: Implement market filter
- 4.7.5: Add URL param persistence

**Dependencies:** Task 3.3

---

## 🧪 CROSS-CUTTING TASKS

### Task C.1: Setup End-to-End (E2E) Tests
**Type:** Testing  
**Story Points:** 8  
**Priority:** P1 (High)  

**Acceptance Criteria:**
- [ ] E2E test framework: Playwright or Cypress
- [ ] Test scenarios:
  1. User loads dashboard → screener tab visible
  2. User adds symbol to watchlist → appears in table within 60 seconds
  3. User toggles strategy ON → signals update in next scan
  4. User removes symbol → disappears from table
- [ ] Tests run on CI (GitHub Actions)
- [ ] All tests pass before Phase 4 completion

**Subtasks:**
- C.1.1: Install & configure Playwright/Cypress
- C.1.2: Write test scenarios
- C.1.3: Setup CI workflow
- C.1.4: Run tests locally

**Dependencies:** Phase 3 completion

---

### Task C.2: Documentation & Runbook
**Type:** Documentation  
**Story Points:** 5  
**Priority:** P1 (High)  

**Acceptance Criteria:**
- [ ] README updated with screener setup instructions
- [ ] API documentation (Swagger/OpenAPI)
- [ ] Developer guide: How to add a new strategy
- [ ] Architecture diagram (1-minute engine flow)
- [ ] Troubleshooting guide

**Subtasks:**
- C.2.1: Update main README
- C.2.2: Generate OpenAPI docs
- C.2.3: Write strategy developer guide
- C.2.4: Create architecture diagram
- C.2.5: Write troubleshooting guide

**Dependencies:** All phases

---

### Task C.3: Docker & Deployment Readiness
**Type:** DevOps  
**Story Points:** 5  
**Priority:** P1 (High)  

**Acceptance Criteria:**
- [ ] Docker Compose includes Redis service
- [ ] Backend Dockerfile includes APScheduler + dependencies
- [ ] Frontend builds correctly in Docker
- [ ] .env.example includes all new env vars (REDIS_URL, ENABLED_STRATEGIES, etc.)
- [ ] docker-compose up → full app runs (backend + frontend + Redis)
- [ ] Health check endpoints respond correctly

**Subtasks:**
- C.3.1: Update docker-compose.yml
- C.3.2: Update Dockerfile for backend
- C.3.3: Test Docker Compose locally
- C.3.4: Update .env.example
- C.3.5: Document deployment steps

**Dependencies:** All phases

---

### Task C.4: Performance Benchmarking & Load Testing
**Type:** Testing  
**Story Points:** 5  
**Priority:** P2 (Medium)  

**Acceptance Criteria:**
- [ ] Load test: 50 symbols, 3 strategies → < 3 seconds scan
- [ ] Stress test: 100 symbols → measure time degradation
- [ ] API load test: 100 concurrent requests to `/api/screener/latest` → < 50ms response
- [ ] Frontend load test: Rapid tab switching → no memory leaks
- [ ] Report: Metrics & bottlenecks documented

**Subtasks:**
- C.4.1: Write load test script (Python/k6)
- C.4.2: Run load tests
- C.4.3: Document metrics
- C.4.4: Identify & fix bottlenecks
- C.4.5: Write performance report

**Dependencies:** Phase 2 completion

---

### Task C.5: Security Review & Hardening
**Type:** Security  
**Story Points:** 5  
**Priority:** P1 (High)  

**Acceptance Criteria:**
- [ ] API endpoints validated (no SQL injection, XSS)
- [ ] Redis credentials in .env (not hardcoded)
- [ ] CORS properly configured (not allow *)
- [ ] Input validation on all endpoints (symbol, market)
- [ ] Error messages don't leak sensitive info
- [ ] Security checklist reviewed

**Subtasks:**
- C.5.1: Audit API endpoints
- C.5.2: Check input validation
- C.5.3: Review CORS config
- C.5.4: Check environment variable handling
- C.5.5: Write security checklist document

**Dependencies:** Phase 3 completion

---

## 📊 TASK SUMMARY & METRICS

### By Phase:
| Phase | Tasks | Story Points | Priority | Duration (Est.) |
|-------|-------|--------------|----------|-----------------|
| **Phase 1** | 4 | 26 | P0 | 5-7 days |
| **Phase 2** | 7 | 40 | P0 | 7-10 days |
| **Phase 3** | 7 | 28 | P0/P1 | 5-7 days |
| **Phase 4** | 7 | 35 | P1/P2 | 5-7 days |
| **Cross-cutting** | 5 | 28 | P1/P2 | 5-7 days |
| **Total** | **30** | **157** | — | **27-38 days** |

### By Type:
- Feature: 18 tasks
- Testing: 6 tasks
- Infrastructure: 2 tasks
- Architecture: 2 tasks
- Documentation: 1 task
- DevOps: 1 task

### Critical Path (Blocking Tasks):
1. Task 1.1 → Task 1.2/1.3 → Task 2.1/2.3/2.4 → Task 2.5 → Task 3.1 → Task 3.3

---

## 🎯 ACCEPTANCE CRITERIA (PROJECT COMPLETION)

✅ **Phase 1 Complete When:**
- Redis running with data ingestion (Zerodha + Binance)
- 100 candles stored per symbol in Redis
- All Phase 1 tests passing

✅ **Phase 2 Complete When:**
- APScheduler runs 1-minute scan loop
- 3+ strategies available (MA, RSI, Volume, etc.)
- Signals calculated and stored in Redis < 3 seconds
- All Phase 2 tests passing

✅ **Phase 3 Complete When:**
- `/api/screener/latest` responds with signals
- React dashboard displays signals with 60-second polling
- No page freezes or janky re-renders
- All Phase 3 tests passing

✅ **Phase 4 Complete When:**
- Watchlist add/remove working
- Strategy toggle working
- Full dashboard integrated
- All Phase 4 tests passing

✅ **Overall Project Done When:**
- All 30 tasks completed & tested
- E2E tests passing
- Documentation complete
- Docker Compose working
- Performance benchmarks met
- Security review passed

---

## 📅 SUGGESTED SPRINT PLANNING

**Sprint 1 (5-7 days):** Phase 1 Tasks (1.1, 1.2, 1.3, 1.4)  
**Sprint 2 (7-10 days):** Phase 2 Tasks (2.1-2.7)  
**Sprint 3 (5-7 days):** Phase 3 Tasks (3.1-3.7)  
**Sprint 4 (5-7 days):** Phase 4 Tasks (4.1-4.7)  
**Sprint 5 (5-7 days):** Cross-Cutting Tasks (C.1-C.5) + Buffer for bugs/refinement  

---

**Document Version:** 1.0  
**Created:** 2026-05-30  
**Total Effort:** 157 story points (~4-5 weeks for 1 senior developer)  
**Next Action:** Start Phase 1 with Task 1.1 (Redis setup)
