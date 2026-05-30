import asyncio
import json
import logging
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import redis.asyncio as redis
from backend.config import Config
from backend.database import Candle
from backend.strategies.registry import StrategyRegistry
from backend.strategies.base import StrategySignal

logger = logging.getLogger(__name__)

class ScreenerEngine:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.default_symbols = ["BTCUSDT", "ETHUSDT", "RELIANCE", "TCS", "INFY"]

    async def get_active_symbols(self) -> List[str]:
        """Fetch symbols from Redis watchlist:active or return defaults"""
        try:
            symbols_json = await self.redis.get("watchlist:active")
            if symbols_json:
                return json.loads(symbols_json)
        except Exception as e:
            logger.error(f"Error fetching watchlist: {e}")
        return self.default_symbols

    async def get_candles(self, symbol: str) -> List[Candle]:
        """Fetch last 100 candles from Redis market_data:1m:<SYMBOL>"""
        try:
            redis_key = f"market_data:1m:{symbol}"
            raw_candles = await self.redis.lrange(redis_key, 0, 99)
            
            candles = []
            for raw in raw_candles:
                data = json.loads(raw)
                # Convert back to Candle object
                candle = Candle(
                    symbol=data["symbol"],
                    open=data["open"],
                    high=data["high"],
                    low=data["low"],
                    close=data["close"],
                    volume=data["volume"],
                    open_time=datetime.fromisoformat(data["open_time"]),
                    close_time=datetime.fromisoformat(data["close_time"])
                )
                candles.append(candle)
            
            # The ingestion service uses LPUSH, so index 0 is newest.
            # BaseStrategy expects chronological order (oldest first).
            return candles[::-1]
        except Exception as e:
            logger.error(f"Error fetching candles for {symbol}: {e}")
            return []

    async def run_scan(self):
        """Main entry point to run the screening process"""
        start_time = time.time()
        logger.info("Starting screener scan...")
        
        try:
            symbols = await self.get_active_symbols()
            strategies = StrategyRegistry.get_active_strategies()
            
            all_signals = []
            
            async def scan_symbol(symbol: str):
                candles = await self.get_candles(symbol)
                if not candles:
                    return
                
                for strategy in strategies:
                    try:
                        signal = strategy.analyze(candles)
                        if signal:
                            all_signals.append(signal)
                    except Exception as e:
                        logger.error(f"Error running strategy {strategy.name} on {symbol}: {e}")

            # Run symbol scans in parallel
            await asyncio.gather(*(scan_symbol(s) for s in symbols))
            
            # Aggregate and store
            result = {
                "timestamp": datetime.utcnow().isoformat(),
                "scan_duration_ms": int((time.time() - start_time) * 1000),
                "signals": [
                    {
                        "symbol": s.symbol,
                        "side": s.side,
                        "confidence": s.confidence,
                        "strategy": s.strategy_name
                    } for s in all_signals
                ]
            }
            
            await self.redis.set("screener_signals:latest", json.dumps(result))
            logger.info(f"Scan complete. Found {len(all_signals)} signals in {result['scan_duration_ms']}ms")
            
        except Exception as e:
            logger.error(f"Critical error in screener engine: {e}")
