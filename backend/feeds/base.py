# backend/feeds/base.py
from abc import ABC, abstractmethod
from typing import Callable, List, Optional
from backend.database import Candle
from backend.schemas import Order, OrderResponse

class MarketAdapter(ABC):
    """Base class for market data adapters (Binance, Zerodha, etc.)"""

    @abstractmethod
    async def connect(self):
        """Establish connection to market data source"""
        raise NotImplementedError("Subclasses must implement connect()")

    @abstractmethod
    async def disconnect(self):
        """Close connection to market data source"""
        raise NotImplementedError("Subclasses must implement disconnect()")

    @abstractmethod
    async def get_price(self, symbol: str) -> Optional[float]:
        """Get current price for symbol"""
        raise NotImplementedError("Subclasses must implement get_price()")

    @abstractmethod
    async def get_candles(self, symbol: str, timeframe: str, limit: int = 100) -> List[Candle]:
        """Get historical candles"""
        raise NotImplementedError("Subclasses must implement get_candles()")

    @abstractmethod
    async def on_price_update(self, callback: Callable):
        """Register callback dict to fire on price ticks"""
        raise NotImplementedError("Subclasses must implement on_price_update()")

    @abstractmethod
    async def place_order(self, order: Order) -> OrderResponse:
        """Place market or limit order. Returns OrderResponse with id and status"""
        raise NotImplementedError("Subclasses must implement place_order()")
