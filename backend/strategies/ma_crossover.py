import pandas as pd
from typing import List, Optional
from backend.database import Candle
from backend.strategies.base import BaseStrategy, StrategySignal

class MACrossoverStrategy(BaseStrategy):
    """
    Moving Average 9/21 crossover strategy.
    Signal: MA9 > MA21 -> LONG, MA9 < MA21 -> SHORT
    Confidence: Normalized distance between MAs
    """
    
    def __init__(self, fast_period: int = 9, slow_period: int = 21):
        super().__init__(name=f"MA_{fast_period}_{slow_period}")
        self.fast_period = fast_period
        self.slow_period = slow_period
    
    def analyze(self, candles: List[Candle]) -> Optional[StrategySignal]:
        if not candles or len(candles) < self.slow_period:
            return None
        
        # Convert candles to DataFrame
        df = pd.DataFrame([{
            'close': c.close,
            'symbol': c.symbol
        } for c in candles])
        
        # Calculate SMAs using pandas
        df['ma_fast'] = df['close'].rolling(window=self.fast_period).mean()
        df['ma_slow'] = df['close'].rolling(window=self.slow_period).mean()
        
        # Get the latest values
        latest = df.iloc[-1]
        ma_fast = latest['ma_fast']
        ma_slow = latest['ma_slow']
        
        if pd.isna(ma_fast) or pd.isna(ma_slow):
            return None
        
        symbol = latest['symbol']
        
        # Determine side
        if ma_fast > ma_slow:
            side = "LONG"
        elif ma_fast < ma_slow:
            side = "SHORT"
        else:
            side = "NEUTRAL"
            
        # Calculate confidence: normalized distance between MAs
        diff = abs(ma_fast - ma_slow)
        # Normalize diff. A 1% diff relative to slow MA is considered high confidence (1.0)
        dist_pct = diff / ma_slow
        confidence = min(dist_pct * 100, 1.0) # 1% diff = 1.0 confidence
        
        return StrategySignal(
            symbol=symbol,
            side=side,
            confidence=round(float(confidence), 2),
            strategy_name=self.name
        )
