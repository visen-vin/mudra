# backend/feeds/binance.py
import aiohttp
import asyncio
import json
from typing import Dict, List, Optional
from datetime import datetime
from backend.feeds.base import MarketAdapter
from backend.database import Candle
from backend.config import Config
import logging

logger = logging.getLogger(__name__)

class BinanceAdapter(MarketAdapter):
    """Binance WS + REST adapter for crypto trading"""

    BASE_URL = "https://api.binance.com/api/v3"
    WS_URL = "wss://stream.binance.com:9443/ws"

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.prices: Dict[str, float] = {}
        self.ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self.callbacks = {}  # symbol -> callback

    async def connect(self):
        """Establish connection to Binance APIs"""
        self.session = aiohttp.ClientSession()
        logger.info("Binance adapter connected")

    async def disconnect(self):
        """Close connection"""
        if self.session:
            await self.session.close()
        if self.ws:
            await self.ws.close()
        logger.info("Binance adapter disconnected")

    async def get_price(self, symbol: str) -> Optional[float]:
        """Get current price from cache or REST API"""
        if symbol in self.prices:
            return self.prices[symbol]

        # Fallback to REST API
        try:
            async with self.session.get(
                f"{self.BASE_URL}/ticker/price",
                params={"symbol": symbol},
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    price = float(data["price"])
                    self.prices[symbol] = price
                    return price
                else:
                    logger.warning(f"Failed to fetch price for {symbol}: HTTP {resp.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return None

    async def get_candles(self, symbol: str, timeframe: str, limit: int = 100) -> List[Candle]:
        """Fetch historical candles from Binance REST API"""
        try:
            async with self.session.get(
                f"{self.BASE_URL}/klines",
                params={
                    "symbol": symbol,
                    "interval": timeframe,
                    "limit": limit
                },
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                if resp.status != 200:
                    logger.warning(f"Failed to fetch candles for {symbol}: HTTP {resp.status}")
                    return []

                data = await resp.json()
        except Exception as e:
            logger.error(f"Error fetching candles for {symbol}: {e}")
            return []

        candles = []
        for row in data:
            try:
                candle = Candle(
                    symbol=symbol,
                    market="crypto",
                    timeframe=timeframe,
                    open_time=datetime.fromtimestamp(row[0] / 1000),
                    close_time=datetime.fromtimestamp(row[6] / 1000),
                    open=float(row[1]),
                    high=float(row[2]),
                    low=float(row[3]),
                    close=float(row[4]),
                    volume=float(row[7])
                )
                candles.append(candle)
            except (IndexError, ValueError, TypeError) as e:
                logger.warning(f"Error parsing candle row {row}: {e}")
                continue

        return candles

    async def on_price_update(self, symbol: str, price: float):
        """Update price cache and trigger callbacks"""
        self.prices[symbol] = price
        if symbol in self.callbacks:
            try:
                await self.callbacks[symbol](price)
            except Exception as e:
                logger.error(f"Error in price callback for {symbol}: {e}")

    async def place_order(self, symbol: str, side: str, qty: float, price: Optional[float] = None) -> Dict:
        """Place market or limit order on Binance (live mode only)"""
        if not Config.BINANCE_API_KEY:
            raise ValueError("BINANCE_API_KEY not configured")

        order_type = "LIMIT" if price else "MARKET"

        params = {
            "symbol": symbol,
            "side": side.upper(),
            "type": order_type,
            "quantity": qty,
            "timestamp": int(datetime.utcnow().timestamp() * 1000)
        }

        if price:
            params["price"] = price

        # Note: Full implementation requires request signing with BINANCE_API_SECRET
        # This is a placeholder that shows the structure
        logger.warning("place_order called but signing not yet implemented")

        return {
            "id": None,
            "status": "PENDING",
            "avg_price": price or 0
        }
