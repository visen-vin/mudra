# backend/feeds/binance.py
import aiohttp
import asyncio
import json
import hmac
import hashlib
import time
from typing import Callable, Dict, List, Optional
from datetime import datetime
from urllib.parse import urlencode
from backend.feeds.base import MarketAdapter
from backend.database import Candle
from backend.schemas import Order, OrderResponse
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
        self.callbacks: Dict[str, Callable] = {}  # symbol -> callback

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
        if not self.session:
            logger.error(f"Adapter not connected — call connect() first for {symbol}")
            return None

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
        if not self.session:
            logger.error(f"Adapter not connected — call connect() first for {symbol}")
            return []

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
                    volume=float(row[5])  # base asset volume (not quote asset volume)
                )
                candles.append(candle)
            except (IndexError, ValueError, TypeError) as e:
                logger.warning(f"Error parsing candle row {row}: {e}")
                continue

        return candles

    async def on_price_update(self, callback: Callable):
        """Register callback to be invoked on price updates"""
        # This is a placeholder implementation that stores the callback
        # In the full implementation, this would wire up the callback to price events
        pass

    async def place_order(self, order: Order) -> OrderResponse:
        """Place market or limit order on Binance (live mode only)"""
        if not Config.BINANCE_API_KEY or not Config.BINANCE_API_SECRET:
            logger.error("Binance API credentials missing")
            return OrderResponse(
                order_id="",
                status="ERROR: Missing API credentials"
            )

        if not self.session:
            await self.connect()

        endpoint = f"{self.BASE_URL}/order"
        
        # side: long -> BUY, short -> SELL
        side = "BUY" if order.side == "long" else "SELL"
        # type: if order.price exists -> LIMIT, else MARKET
        order_type = "LIMIT" if order.price else "MARKET"
        
        params = {
            "symbol": order.symbol,
            "side": side,
            "type": order_type,
            "quantity": order.qty,
            "timestamp": int(time.time() * 1000),
        }
        
        if order_type == "LIMIT":
            params["price"] = order.price
            params["timeInForce"] = "GTC"
        elif order_type == "MARKET":
            # Ensure timeInForce is NOT sent for MARKET orders
            if "timeInForce" in params:
                del params["timeInForce"]
            
        # Signature
        query_string = urlencode(params)
        signature = hmac.new(
            Config.BINANCE_API_SECRET.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        
        params["signature"] = signature
        
        headers = {
            "X-MBX-APIKEY": Config.BINANCE_API_KEY
        }
        
        try:
            async with self.session.post(endpoint, params=params, headers=headers) as resp:
                data = await resp.json()
                if resp.status == 200:
                    return OrderResponse(
                        order_id=str(data["orderId"]),
                        status=data["status"]
                    )
                else:
                    logger.error(f"Binance order failed: {data}")
                    return OrderResponse(
                        order_id="",
                        status=f"FAILED: {data.get('msg', 'Unknown error')}"
                    )
        except Exception as e:
            logger.error(f"Error placing Binance order: {e}")
            return OrderResponse(
                order_id="",
                status=f"ERROR: {str(e)}"
            )

