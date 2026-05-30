# Mudra Implementation — Remaining Tasks (5-12)

**Project:** Lightweight paper+live trading app (crypto + Indian equity)  
**Status:** Tasks 1-4 complete ✅ (Config, DB, Binance Feed, Trade Engine)  
**Next:** Tasks 5-12 (API Routes, Frontend, Strategies, Zerodha, Live Mode)

---

## ✅ COMPLETED TASKS

- **Task 1:** Project Setup & Config
- **Task 2:** Database Schema & Models
- **Task 3:** Binance Feed Service (Commit: 1c2864e)
- **Task 4:** Trade Engine & Position Monitor (Commit: b14b732) — All 17 tests passing

---

## REMAINING TASKS (5-12)

---

# Task 5: REST API Routes (Manual Trading)

**Files:**
- Create: `backend/api/routes.py`
- Modify: `backend/main.py`

## Step 1: Create REST routes

```python
# backend/api/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db, Position, SessionLocal
from backend.schemas import PositionCreate, PositionRead
from backend.engine.trade_engine import TradeEngine
from typing import List

router = APIRouter(prefix="/api", tags=["trading"])
engine = TradeEngine()

@router.get("/positions", response_model=List[PositionRead])
def get_positions(db: Session = Depends(get_db)):
    """Get all open positions"""
    return db.query(Position).filter(Position.status == "OPEN").all()

@router.get("/history", response_model=List[PositionRead])
def get_history(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    """Get closed trades (history)"""
    return db.query(Position).filter(Position.status == "CLOSED") \
        .order_by(Position.closed_at.desc()) \
        .offset(offset).limit(limit).all()

@router.post("/place-order", response_model=PositionRead)
def place_order(order: PositionCreate, db: Session = Depends(get_db)):
    """Place manual trade"""
    position = engine.open_position(
        symbol=order.symbol,
        market=order.market,
        side=order.side,
        qty=order.qty,
        entry_price=order.entry_price,
        sl=order.sl,
        tp=order.tp,
        mode=order.mode
    )
    db.refresh(position)
    return position

@router.post("/close-position/{position_id}", response_model=PositionRead)
def close_position(position_id: str, exit_price: float, db: Session = Depends(get_db)):
    """Manually close a position"""
    position = engine.close_position_manual(position_id, exit_price)
    db.refresh(position)
    return position

@router.get("/prices")
def get_prices(symbols: str):
    """Get current prices (mock for now)"""
    # Will be connected to feed service in Phase 2
    symbols_list = symbols.split(",")
    return {
        symbol: 0  # TODO: fetch from feed service
        for symbol in symbols_list
    }

@router.get("/settings")
def get_settings():
    """Get trading settings (paper/live mode)"""
    from backend.config import Config
    return {"mode": Config.DEFAULT_MODE}

@router.post("/settings")
def update_settings(mode: str):
    """Toggle paper/live mode"""
    # TODO: Persist settings to DB or config
    return {"mode": mode, "status": "updated"}
```

## Step 2: Update main.py to include routes

```python
# backend/main.py (updated)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import Config
from backend.database import init_db
from backend.api.routes import router

app = FastAPI(title="Mudra Trading", version="0.1.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# Include API routes
app.include_router(router)

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Step 3: Write test for API routes

```python
# tests/test_api_routes.py
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import init_db

client = TestClient(app)

def setup_function():
    init_db()

def test_get_positions():
    response = client.get("/api/positions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_place_order():
    response = client.post("/api/place-order", json={
        "symbol": "BTCUSDT",
        "market": "crypto",
        "side": "long",
        "qty": 1.0,
        "entry_price": 50000,
        "sl": 49000,
        "tp": 51000,
        "mode": "paper"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "BTCUSDT"
    assert data["status"] == "OPEN"

def test_get_history():
    response = client.get("/api/history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_settings():
    response = client.get("/api/settings")
    assert response.status_code == 200
    assert "mode" in response.json()
```

## Step 4: Run API tests

```bash
cd backend
python -m pytest tests/test_api_routes.py -v
```

Expected: All tests PASSED

## Step 5: Commit

```bash
git add backend/api/routes.py backend/main.py tests/test_api_routes.py
git commit -m "feat: REST API routes for manual trading"
```

---

# Task 6: Frontend Setup & Dashboard

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/tailwind.config.js`
- Create: `frontend/src/main.jsx`
- Create: `frontend/src/index.css`
- Create: `frontend/src/components/Dashboard.jsx`
- Create: `frontend/src/components/PriceBoard.jsx`
- Create: `frontend/src/lib/api.js`

## Step 1: Create package.json

```json
{
  "name": "mudra-frontend",
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "eslint src --ext js,jsx"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "swr": "^2.2.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.0",
    "vite": "^5.0.0",
    "tailwindcss": "^3.3.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0"
  }
}
```

## Step 2: Create vite.config.js

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
})
```

## Step 3: Create tailwind.config.js

```javascript
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

## Step 4: Create postcss.config.js

```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

## Step 5: Create src/main.jsx

```jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

## Step 6: Create src/index.css

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans',
    'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}
```

## Step 7: Create src/lib/api.js

```javascript
import axios from 'axios'

const API_BASE = '/api'

export const api = {
  positions: {
    list: () => axios.get(`${API_BASE}/positions`),
    close: (id, exitPrice) => axios.post(`${API_BASE}/close-position/${id}?exit_price=${exitPrice}`),
  },
  orders: {
    place: (order) => axios.post(`${API_BASE}/place-order`, order),
  },
  history: {
    list: (limit = 50, offset = 0) => axios.get(`${API_BASE}/history?limit=${limit}&offset=${offset}`),
  },
  prices: {
    get: (symbols) => axios.get(`${API_BASE}/prices?symbols=${symbols.join(',')}`),
  },
  settings: {
    get: () => axios.get(`${API_BASE}/settings`),
    update: (mode) => axios.post(`${API_BASE}/settings?mode=${mode}`),
  }
}
```

## Step 8: Create src/components/Dashboard.jsx

```jsx
import { useState, useEffect } from 'react'
import useSWR from 'swr'
import axios from 'axios'
import { api } from '../lib/api'

const fetcher = (url) => axios.get(url).then(res => res.data)

export default function Dashboard() {
  const { data: positions, error } = useSWR('/api/positions', fetcher)
  const { data: settings } = useSWR('/api/settings', fetcher)
  const [formData, setFormData] = useState({
    symbol: 'BTCUSDT',
    market: 'crypto',
    side: 'long',
    qty: 1.0,
    entry_price: 50000,
    sl: 49000,
    tp: 51000,
    mode: 'paper'
  })

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: ['qty', 'entry_price', 'sl', 'tp'].includes(name) ? parseFloat(value) : value
    }))
  }

  const handlePlaceOrder = async (e) => {
    e.preventDefault()
    try {
      await api.orders.place(formData)
      alert('Order placed successfully')
    } catch (error) {
      alert('Error placing order: ' + error.message)
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">Mudra Trading</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Open Positions */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-2xl font-bold mb-4">Open Positions</h2>
            {positions && positions.length > 0 ? (
              <div className="space-y-2">
                {positions.map(pos => (
                  <div key={pos.id} className="p-3 bg-gray-50 rounded">
                    <p className="font-mono text-sm">{pos.symbol} {pos.side.toUpperCase()}</p>
                    <p className="text-xs text-gray-600">Qty: {pos.qty} @ {pos.entry_price}</p>
                    <p className="text-xs">SL: {pos.sl} | TP: {pos.tp}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">No open positions</p>
            )}
          </div>

          {/* Place Order Form */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-2xl font-bold mb-4">Place Order</h2>
            <form onSubmit={handlePlaceOrder} className="space-y-3">
              <input
                type="text"
                name="symbol"
                value={formData.symbol}
                onChange={handleInputChange}
                placeholder="Symbol"
                className="w-full p-2 border rounded"
              />
              <select
                name="side"
                value={formData.side}
                onChange={handleInputChange}
                className="w-full p-2 border rounded"
              >
                <option value="long">Long</option>
                <option value="short">Short</option>
              </select>
              <input
                type="number"
                name="qty"
                value={formData.qty}
                onChange={handleInputChange}
                placeholder="Quantity"
                className="w-full p-2 border rounded"
              />
              <input
                type="number"
                name="entry_price"
                value={formData.entry_price}
                onChange={handleInputChange}
                placeholder="Entry Price"
                className="w-full p-2 border rounded"
              />
              <input
                type="number"
                name="sl"
                value={formData.sl}
                onChange={handleInputChange}
                placeholder="Stop Loss"
                className="w-full p-2 border rounded"
              />
              <input
                type="number"
                name="tp"
                value={formData.tp}
                onChange={handleInputChange}
                placeholder="Take Profit"
                className="w-full p-2 border rounded"
              />
              <button
                type="submit"
                className="w-full bg-blue-600 text-white p-2 rounded hover:bg-blue-700"
              >
                Place Order
              </button>
            </form>
          </div>
        </div>

        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <p className="text-sm text-gray-600">Mode: <span className="font-bold">{settings?.mode || 'paper'}</span></p>
        </div>
      </div>
    </div>
  )
}
```

## Step 9: Create src/App.jsx

```jsx
import Dashboard from './components/Dashboard'

function App() {
  return <Dashboard />
}

export default App
```

## Step 10: Create frontend/index.html

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Mudra Trading</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

## Step 11: Install dependencies and run dev server

```bash
cd frontend
npm install
npm run dev
```

Expected: Frontend runs on `http://localhost:5173`

## Step 12: Commit

```bash
git add frontend/
git commit -m "feat: frontend setup with React, Vite, TailwindCSS"
```

---

# Task 7: MA Crossover Strategy

**Files:**
- Create: `backend/strategies/base.py`
- Create: `backend/strategies/ma_crossover.py`
- Create: `tests/test_ma_strategy.py`

## Step 1: Create base strategy class

```python
# backend/strategies/base.py
from abc import ABC, abstractmethod
from typing import Optional, List
from backend.database import Candle

class Strategy(ABC):
    """Base class for trading strategies"""
    
    def __init__(self):
        self.last_signal = None
    
    @abstractmethod
    def analyze(self, candles: List[Candle]) -> Optional[dict]:
        """
        Analyze candles and return signal if generated.
        Returns: {"symbol": str, "side": "long"|"short", "confidence": float}
        """
        pass
```

## Step 2: Create MA crossover strategy

```python
# backend/strategies/ma_crossover.py
from typing import List, Optional
from backend.database import Candle
from backend.strategies.base import Strategy

class MACrossoverStrategy(Strategy):
    """MA 20/50 crossover strategy"""
    
    def __init__(self, fast_period: int = 20, slow_period: int = 50):
        super().__init__()
        self.fast_period = fast_period
        self.slow_period = slow_period
    
    def calculate_ma(self, candles: List[Candle], period: int) -> Optional[float]:
        """Calculate moving average"""
        if len(candles) < period:
            return None
        recent = candles[-period:]
        closes = [c.c for c in recent]
        return sum(closes) / period
    
    def analyze(self, candles: List[Candle]) -> Optional[dict]:
        """
        Generate signal when MA20 crosses MA50
        - Upward cross: long signal
        - Downward cross: short signal
        """
        if len(candles) < self.slow_period + 1:
            return None
        
        # Current candles
        ma20_current = self.calculate_ma(candles, self.fast_period)
        ma50_current = self.calculate_ma(candles, self.slow_period)
        
        # Previous candles
        ma20_prev = self.calculate_ma(candles[:-1], self.fast_period)
        ma50_prev = self.calculate_ma(candles[:-1], self.slow_period)
        
        if not all([ma20_current, ma50_current, ma20_prev, ma50_prev]):
            return None
        
        # Check crossover
        if ma20_prev <= ma50_prev and ma20_current > ma50_current:
            # Bullish crossover
            symbol = candles[-1].symbol
            return {
                "symbol": symbol,
                "side": "long",
                "confidence": 0.7,
                "reason": f"MA{self.fast_period} crossed above MA{self.slow_period}"
            }
        elif ma20_prev >= ma50_prev and ma20_current < ma50_current:
            # Bearish crossover
            symbol = candles[-1].symbol
            return {
                "symbol": symbol,
                "side": "short",
                "confidence": 0.7,
                "reason": f"MA{self.fast_period} crossed below MA{self.slow_period}"
            }
        
        return None
```

## Step 3: Write test for MA strategy

```python
# tests/test_ma_strategy.py
from backend.strategies.ma_crossover import MACrossoverStrategy
from backend.database import Candle
from datetime import datetime

def test_ma_bullish_crossover():
    """Test MA20 crossing above MA50"""
    strategy = MACrossoverStrategy()
    
    # Create candles with MA20 crossing above MA50
    candles = []
    for i in range(70):
        close = 100 + i if i < 35 else 100 + 35 + (i - 35) * 0.5  # Downtrend then uptrend
        candles.append(Candle(
            id=i,
            symbol="BTCUSDT",
            market="crypto",
            timeframe="1h",
            open_time=datetime.utcnow(),
            close_time=datetime.utcnow(),
            o=close - 1,
            h=close + 1,
            l=close - 2,
            c=close,
            v=1000
        ))
    
    signal = strategy.analyze(candles)
    
    assert signal is not None
    assert signal["side"] == "long"
    assert signal["confidence"] == 0.7

def test_ma_bearish_crossover():
    """Test MA20 crossing below MA50"""
    strategy = MACrossoverStrategy()
    
    # Create candles with MA20 crossing below MA50
    candles = []
    for i in range(70):
        close = 100 + (70 - i) * 0.5 if i < 35 else 100 + (35 - (i - 35)) * 0.5
        candles.append(Candle(
            id=i,
            symbol="ETHUSDT",
            market="crypto",
            timeframe="1h",
            open_time=datetime.utcnow(),
            close_time=datetime.utcnow(),
            o=close - 1,
            h=close + 1,
            l=close - 2,
            c=close,
            v=1000
        ))
    
    signal = strategy.analyze(candles)
    
    assert signal is not None
    assert signal["side"] == "short"
    assert signal["confidence"] == 0.7

def test_ma_no_signal():
    """Test no signal when MAs haven't crossed"""
    strategy = MACrossoverStrategy()
    
    # Create flat candles (no crossover)
    candles = []
    for i in range(70):
        candles.append(Candle(
            id=i,
            symbol="BTCUSDT",
            market="crypto",
            timeframe="1h",
            open_time=datetime.utcnow(),
            close_time=datetime.utcnow(),
            o=100,
            h=101,
            l=99,
            c=100,
            v=1000
        ))
    
    signal = strategy.analyze(candles)
    
    assert signal is None
```

## Step 4: Run strategy tests

```bash
cd backend
python -m pytest tests/test_ma_strategy.py -v
```

Expected: All tests PASSED

## Step 5: Commit

```bash
git add backend/strategies/ tests/test_ma_strategy.py
git commit -m "feat: MA 20/50 crossover strategy"
```

---

# Task 8: Zerodha Feed Adapter

**Files:**
- Create: `backend/feeds/zerodha.py`
- Create: `tests/test_zerodha_feed.py`

## Step 1: Create Zerodha adapter

```python
# backend/feeds/zerodha.py
from backend.feeds.base import MarketAdapter
from backend.database import Candle
from typing import Optional, List, Dict, Callable
import logging

logger = logging.getLogger(__name__)

class ZerodhaAdapter(MarketAdapter):
    """Zerodha Kite API adapter (OAuth-based)"""
    
    BASE_URL = "https://api.kite.trade"
    
    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token
        self.session = None
        self.prices: Dict[str, float] = {}
        self.callbacks: Dict[str, Callable] = {}
    
    async def connect(self):
        """Initialize Zerodha session (requires OAuth token)"""
        if not self.access_token:
            raise ValueError("Zerodha requires access_token via OAuth")
        logger.info("Zerodha adapter connected (OAuth)")
    
    async def disconnect(self):
        """Close Zerodha session"""
        logger.info("Zerodha adapter disconnected")
    
    async def get_price(self, symbol: str) -> Optional[float]:
        """Get current price from Zerodha"""
        if not self.access_token:
            logger.error("Zerodha: access_token not set")
            return None
        
        if symbol in self.prices:
            return self.prices[symbol]
        
        # TODO: Implement Zerodha REST API call
        # GET /quote/ohlc?instrument_tokens=...
        logger.warning(f"Zerodha: price not cached for {symbol}")
        return None
    
    async def get_candles(self, symbol: str, limit: int = 100) -> List[Candle]:
        """Get candles from Zerodha"""
        if not self.access_token:
            logger.error("Zerodha: access_token not set")
            return []
        
        # TODO: Implement Zerodha API call
        # GET /instruments/historical/...
        logger.warning(f"Zerodha: candles not implemented for {symbol}")
        return []
    
    async def on_price_update(self, callback: Callable):
        """Register callback for price updates (Phase 5: WebSocket)"""
        # TODO: Implement WebSocket subscription in Phase 5
        logger.warning("Zerodha: WebSocket not yet implemented")
    
    async def place_order(self, order: 'Order') -> 'OrderResponse':
        """Place order on Zerodha (Phase 5: Live Mode)"""
        raise NotImplementedError("Live Zerodha orders deferred to Phase 5")
```

## Step 2: Write test for Zerodha adapter

```python
# tests/test_zerodha_feed.py
import pytest
from backend.feeds.zerodha import ZerodhaAdapter

@pytest.mark.asyncio
async def test_zerodha_requires_token():
    """Test that Zerodha requires OAuth token"""
    adapter = ZerodhaAdapter()
    
    with pytest.raises(ValueError, match="requires access_token"):
        await adapter.connect()

@pytest.mark.asyncio
async def test_zerodha_get_price_no_token():
    """Test get_price returns None without token"""
    adapter = ZerodhaAdapter()
    price = await adapter.get_price("SBIN")
    
    assert price is None

@pytest.mark.asyncio
async def test_zerodha_place_order_not_implemented():
    """Test place_order raises NotImplementedError"""
    adapter = ZerodhaAdapter(access_token="mock_token")
    
    from backend.schemas import Order
    order = Order(symbol="SBIN", side="long", qty=1.0, price=500)
    
    with pytest.raises(NotImplementedError):
        await adapter.place_order(order)

def test_zerodha_connect_with_token():
    """Test Zerodha adapter initializes with token"""
    adapter = ZerodhaAdapter(access_token="test_token_xyz")
    assert adapter.access_token == "test_token_xyz"
```

## Step 3: Run Zerodha tests

```bash
cd backend
python -m pytest tests/test_zerodha_feed.py -v
```

Expected: All tests PASSED

## Step 4: Create Zerodha OAuth handler (placeholder for Phase 5)

```python
# backend/api/auth.py
from fastapi import APIRouter, HTTPException
from backend.feeds.zerodha import ZerodhaAdapter

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/zerodha/callback")
async def zerodha_oauth_callback(request_token: str):
    """
    Handle Zerodha OAuth callback (Phase 5)
    Converts request_token to access_token
    """
    # TODO: Exchange request_token for access_token
    # POST to https://api.kite.trade/session/token
    return {"status": "placeholder", "note": "Implement in Phase 5"}
```

## Step 5: Commit

```bash
git add backend/feeds/zerodha.py backend/api/auth.py tests/test_zerodha_feed.py
git commit -m "feat: Zerodha feed adapter (phase 5 placeholder)"
```

---

# Task 9: Signal Service & API Endpoints

**Files:**
- Create: `backend/services/signal_service.py`
- Modify: `backend/api/routes.py`

## Step 1: Create signal service

```python
# backend/services/signal_service.py
from backend.database import Signal, SessionLocal
from backend.schemas import SignalCreate
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

class SignalService:
    """Manages trading signals from strategies"""
    
    @staticmethod
    def create_signal(strategy: str, symbol: str, side: str, confidence: float, candle_close_time: datetime) -> Signal:
        """Persist signal to database"""
        db = SessionLocal()
        try:
            signal = Signal(
                signal_id=str(uuid.uuid4()),
                strategy=strategy,
                symbol=symbol,
                side=side,
                confidence=confidence,
                emitted_at=datetime.utcnow(),
                candle_close_time=candle_close_time
            )
            db.add(signal)
            db.commit()
            db.refresh(signal)
            
            logger.info(f"Signal created: {signal.signal_id} {strategy} {symbol} {side} @ {confidence}")
            return signal
        finally:
            db.close()
    
    @staticmethod
    def get_signals(limit: int = 100, offset: int = 0):
        """Retrieve recent signals"""
        db = SessionLocal()
        try:
            return db.query(Signal).order_by(Signal.emitted_at.desc()) \
                .offset(offset).limit(limit).all()
        finally:
            db.close()
    
    @staticmethod
    def get_signals_by_strategy(strategy: str, limit: int = 100):
        """Get signals from specific strategy"""
        db = SessionLocal()
        try:
            return db.query(Signal).filter(Signal.strategy == strategy) \
                .order_by(Signal.emitted_at.desc()).limit(limit).all()
        finally:
            db.close()
```

## Step 2: Update routes.py with signal endpoints

Add to `backend/api/routes.py`:

```python
from backend.services.signal_service import SignalService
from backend.schemas import SignalRead
from typing import List

@router.get("/signals", response_model=List[SignalRead])
def get_signals(strategy: str = None, limit: int = 100, offset: int = 0):
    """Get recent trading signals"""
    if strategy:
        signals = SignalService.get_signals_by_strategy(strategy, limit)
    else:
        signals = SignalService.get_signals(limit, offset)
    return signals

@router.post("/signals", response_model=SignalRead)
def create_signal(signal_data: dict):
    """Create new signal (from strategy)"""
    signal = SignalService.create_signal(
        strategy=signal_data["strategy"],
        symbol=signal_data["symbol"],
        side=signal_data["side"],
        confidence=signal_data["confidence"],
        candle_close_time=signal_data["candle_close_time"]
    )
    return signal
```

## Step 3: Write tests

```python
# tests/test_signal_service.py
from backend.services.signal_service import SignalService
from backend.database import init_db
from datetime import datetime

def setup_function():
    init_db()

def test_create_signal():
    signal = SignalService.create_signal(
        strategy="MA_CROSSOVER",
        symbol="BTCUSDT",
        side="long",
        confidence=0.75,
        candle_close_time=datetime.utcnow()
    )
    
    assert signal.signal_id is not None
    assert signal.strategy == "MA_CROSSOVER"
    assert signal.symbol == "BTCUSDT"

def test_get_signals():
    SignalService.create_signal(
        strategy="MA_CROSSOVER",
        symbol="ETHUSDT",
        side="short",
        confidence=0.65,
        candle_close_time=datetime.utcnow()
    )
    
    signals = SignalService.get_signals(limit=10)
    assert len(signals) >= 1
```

## Step 4: Run tests

```bash
cd backend
python -m pytest tests/test_signal_service.py -v
```

Expected: All tests PASSED

## Step 5: Commit

```bash
git add backend/services/ backend/api/routes.py tests/test_signal_service.py
git commit -m "feat: signal service and signal API endpoints"
```

---

# Task 10: Live Order Execution (Binance)

**Files:**
- Modify: `backend/feeds/binance.py` (implement place_order)
- Modify: `backend/engine/trade_engine.py`
- Create: `tests/test_live_orders.py`

## Steps

1. Implement `BinanceAdapter.place_order()` with actual order signing
2. Add live mode flag to TradeEngine
3. Route to paper or live execution based on position.mode
4. Tests for order signing and execution

**Note:** This task requires Binance API credentials and involves real order placement. Implement with caution for live mode.

---

# Task 11: Frontend Polish & Mobile Responsiveness

**Files:**
- Modify: `frontend/src/components/*`
- Create: `frontend/src/components/OpenPositions.jsx`
- Create: `frontend/src/components/ManualTradeForm.jsx`
- Create: `frontend/src/components/HistoryTable.jsx`
- Create: `frontend/src/hooks/useApi.js`

## Steps

1. Create separate components for positions, trade form, history
2. Add mobile-responsive grid layouts
3. Add real-time price updates via SWR polling
4. Add loading states and error handling
5. Add transaction history with sorting/filtering

---

# Task 12: Deployment & Documentation

**Files:**
- Create: `Dockerfile`
- Create: `docker-compose.yml`
- Create: `docs/SETUP.md`
- Create: `docs/API.md`

## Steps

1. Dockerize backend and frontend
2. Create docker-compose for local development
3. Write deployment guide (Heroku/Railway/Vercel)
4. Document API endpoints
5. Write user guide for paper/live trading

---

## QUICK REFERENCE

| Task | Status | Files | Tests |
|------|--------|-------|-------|
| 1. Config | ✅ | config.py, main.py | - |
| 2. Database | ✅ | database.py, schemas.py | test_models.py |
| 3. Binance | ✅ | feeds/binance.py | test_binance_feed.py |
| 4. Trade Engine | ✅ | engine/*.py | test_engine.py |
| 5. API Routes | 📋 | api/routes.py | test_api_routes.py |
| 6. Frontend | 📋 | frontend/src/* | - |
| 7. MA Strategy | 📋 | strategies/ma_crossover.py | test_ma_strategy.py |
| 8. Zerodha | 📋 | feeds/zerodha.py | test_zerodha_feed.py |
| 9. Signals | 📋 | services/signal_service.py | test_signal_service.py |
| 10. Live Orders | 📋 | feeds/binance.py | test_live_orders.py |
| 11. Frontend Polish | 📋 | frontend/src/* | - |
| 12. Deployment | 📋 | Dockerfile, docs/* | - |

---

## HOW TO CONTINUE FROM GEMINI CLI

```bash
cd /Users/vin/Projects/mudra

# Start Task 5
git checkout -b task-5-api-routes

# Implement following steps in TASKS_REMAINING.md

# Run tests frequently
python -m pytest tests/ -v

# Commit when task complete
git commit -m "feat: [task name]"
```

Use this file as your reference for each task. Each task has complete code, tests, and commit instructions.

