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
