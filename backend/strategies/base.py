from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Literal
from backend.database import Candle

@dataclass
class StrategySignal:
    symbol: str
    side: Literal["LONG", "SHORT", "NEUTRAL"]
    confidence: float  # 0 to 1
    strategy_name: str

class BaseStrategy(ABC):
    """Base class for all trading strategies"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def analyze(self, candles: List[Candle]) -> Optional[StrategySignal]:
        """
        Analyze the list of candles and return a signal if one is generated.
        Args:
            candles: List of Candle objects in chronological order (oldest first)
        Returns:
            Optional[StrategySignal]: The generated signal or None if no clear signal
        """
        pass
