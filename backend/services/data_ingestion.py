import asyncio
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import redis.asyncio as redis
from backend.feeds.binance import BinanceAdapter
from backend.feeds.zerodha import ZerodhaAdapter
from backend.config import Config
from backend.database import Candle

logger = logging.getLogger(__name__)

class DataIngestionService:
    def __init__(self, 
                 redis_client: redis.Redis, 
                 binance_adapter: Optional[BinanceAdapter] = None,
                 zerodha_adapter: Optional[ZerodhaAdapter] = None):
        self.redis = redis_client
        self.binance = binance_adapter
        self.zerodha = zerodha_adapter
        self.binance_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "DOGEUSDT"]
        self.zerodha_symbols = ["RELIANCE", "TCS", "INFY", "LT", "HDFC"]

    async def initialize_data(self, adapter: Any, symbol: str):
        """Fetch last 100 candles from REST and store in Redis"""
        try:
            logger.info(f"Initializing 1m data for {symbol}")
            candles = await adapter.get_candles(symbol, "1m", limit=100)
            if not candles:
                logger.warning(f"Could not fetch historical candles for {symbol}")
                return

            redis_key = f"market_data:1m:{symbol}"
            # Clear existing data and backfill
            await self.redis.delete(redis_key)
            
            # Use RPUSH for backfill to keep oldest -> newest order in the Redis list
            # So index 0 is oldest, index -1 is newest. 
            # WAIT: Professionals usually use LPUSH (index 0 is newest).
            # If we use LPUSH(1), LPUSH(2), LPUSH(3) -> [3, 2, 1]. Index 0 is newest.
            # To backfill [oldest...newest] so index 0 is newest: 
            # We should push them in order [oldest...newest] using LPUSH.
            # 1. LPUSH(oldest) -> [oldest]
            # 2. LPUSH(middle) -> [middle, oldest]
            # 3. LPUSH(newest) -> [newest, middle, oldest]
            # Yes, index 0 is newest.
            for candle in candles:
                await self.redis.lpush(redis_key, self._serialize_candle(candle))
            
            # Ensure we only keep 100
            await self.redis.ltrim(redis_key, 0, 99)
            
            logger.info(f"Stored {len(candles)} historical candles for {symbol}")
        except Exception as e:
            logger.error(f"Error initializing data for {symbol}: {e}")

    def _serialize_candle(self, candle: Candle) -> str:
        return json.dumps({
            "symbol": candle.symbol,
            "open": candle.open,
            "high": candle.high,
            "low": candle.low,
            "close": candle.close,
            "volume": candle.volume,
            "open_time": candle.open_time.isoformat(),
            "close_time": candle.close_time.isoformat()
        })

    async def handle_binance_kline(self, msg: Dict[str, Any]):
        """Callback for Binance WebSocket kline messages"""
        try:
            if msg.get("e") != "kline":
                return

            k = msg["k"]
            symbol = k["s"]
            is_closed = k["x"]

            if is_closed:
                candle_data = {
                    "symbol": symbol,
                    "open": float(k["o"]),
                    "high": float(k["h"]),
                    "low": float(k["l"]),
                    "close": float(k["c"]),
                    "volume": float(k["v"]),
                    "open_time": datetime.fromtimestamp(k["t"] / 1000).isoformat(),
                    "close_time": datetime.fromtimestamp(k["T"] / 1000).isoformat()
                }
                
                redis_key = f"market_data:1m:{symbol}"
                await self.redis.lpush(redis_key, json.dumps(candle_data))
                await self.redis.ltrim(redis_key, 0, 99)
                logger.debug(f"Stored closed 1m candle for {symbol}")
        except Exception as e:
            logger.error(f"Error handling kline message: {e}")

    async def connect_binance_stream(self, symbol: str, max_retries: int = 1000):
        retry_delay = 1
        for i in range(max_retries):
            try:
                await self.binance.start_kline_stream(symbol, "1m", self.handle_binance_kline)
                logger.warning(f"Binance stream for {symbol} closed. Retrying...")
            except Exception as e:
                logger.error(f"Error in Binance {symbol} stream: {e}. Retrying in {retry_delay}s...")
            
            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 60)

    async def run_zerodha_polling(self):
        """Zerodha doesn't have 1m WebSocket for historical candles easily, so we poll or wait for Phase 5"""
        while True:
            for symbol in self.zerodha_symbols:
                try:
                    # In a real system, we'd only fetch the LATEST closed candle
                    # For now, we reuse the initialize_data logic periodically
                    await self.initialize_data(self.zerodha, symbol)
                except Exception as e:
                    logger.error(f"Error polling Zerodha for {symbol}: {e}")
            await asyncio.sleep(60) # Poll every minute

    async def run(self):
        """Main entry point for the service"""
        tasks = []
        
        # Binance Setup
        if self.binance:
            if not self.binance.session:
                await self.binance.connect()
            for symbol in self.binance_symbols:
                await self.initialize_data(self.binance, symbol)
                tasks.append(asyncio.create_task(self.connect_binance_stream(symbol)))
        
        # Zerodha Setup
        if self.zerodha:
            # Note: Zerodha requires OAuth which is usually handled in routes.py
            # If session is active, we can run polling
            if self.zerodha.access_token:
                tasks.append(asyncio.create_task(self.run_zerodha_polling()))
        
        if tasks:
            await asyncio.gather(*tasks)
        else:
            logger.warning("No adapters configured for DataIngestionService")
