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
