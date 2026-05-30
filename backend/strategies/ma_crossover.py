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
        closes = [c.close for c in recent]
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
