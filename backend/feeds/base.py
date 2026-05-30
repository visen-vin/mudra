# backend/feeds/base.py
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from backend.database import Candle

class MarketAdapter(ABC):
    """Base class for market data adapters (Binance, Zerodha, etc.)"""

    @abstractmethod
    async def connect(self):
        """Establish connection to market data source"""
        pass

    @abstractmethod
    async def disconnect(self):
        """Close connection to market data source"""
        pass

    @abstractmethod
    async def get_price(self, symbol: str) -> float:
        """Get current price for symbol"""
        pass

    @abstractmethod
    async def get_candles(self, symbol: str, timeframe: str, limit: int = 100) -> List[Candle]:
        """Get historical candles"""
        pass

    @abstractmethod
    async def on_price_update(self, symbol: str, price: float):
        """Called when price updates"""
        pass

    @abstractmethod
    async def place_order(self, symbol: str, side: str, qty: float, price: Optional[float] = None) -> Dict:
        """Place market or limit order. Returns order dict with id, status, avg_price"""
        pass
